from django.core.management.base import BaseCommand
from create_meeting_app.models import Meeting, Transcript, TranscriptSegment
import os
import datetime
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from deepmultilingualpunctuation import PunctuationModel
from create_meeting_app.utils.tts import generate_tts_and_save
import requests
from django.conf import settings

# NEW: Import for Bangla sentence splitting
try:
    from bnlp import NLTKTokenizer
    bnlp_available = True
except ImportError:
    bnlp_available = False

GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

speech_client = speech.SpeechClient.from_service_account_file(KEY_PATH)
storage_client = storage.Client.from_service_account_json(KEY_PATH)

ENGLISH_WORDS = {
    # ... (your existing dictionary, unchanged)
}

def restore_english_words(text):
    for bn, en in ENGLISH_WORDS.items():
        text = text.replace(bn, en)
    return text

def get_seconds(d):
    if hasattr(d, 'nanos'):
        return d.seconds + d.nanos / 1e9
    else:
        return d.total_seconds()

def detect_hate_speech(text):
    prompt = f"""
You are an expert at detecting hate speech in Bangla text.

Hate speech is language that expresses discrimination, hostility, or violence against individuals or groups based on attributes like race, religion, ethnicity, nationality, gender, sexual orientation, political affiliation, origin, body shaming, or disability. Key indicators include dehumanizing language, calls for violence, discriminatory slurs, stereotyping, promoting supremacy, or personal offenses. Consider cultural context, dialects, and code-mixing in Bangla.

Classify the following Bangla text as hate speech.
Respond only with 'hate' or 'safe'.

Text: {text}
""".strip()

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 10,
            },
            timeout=30,
        )
        resp.raise_for_status()
        classification = resp.json()["choices"][0]["message"]["content"].strip().lower()
        return 'hate' in classification
    except Exception as e:
        print(f"⚠️ Error in hate detection: {e}")
        return False  # Assume safe if error

class Command(BaseCommand):
    help = "Transcribe WAV files in Bangla with smart punctuation & pause-based segments"

    def add_arguments(self, parser):
        parser.add_argument('meeting_id', type=int)

    def handle(self, *args, **options):
        mid = options['meeting_id']
        meeting = Meeting.objects.filter(id=mid).first()
        if not meeting:
            return self.stderr.write("❌ Meeting not found.")

        recordings = sorted(f for f in os.listdir("media/recordings")
                           if f.endswith('.wav') and f"_{mid}_" in f)
        if not recordings:
            return self.stdout.write("📭 No recordings found.")

        punctuator = PunctuationModel()

        for wav in recordings:
            path = os.path.join("media/recordings", wav)
            gcs_uri = f"gs://{GCS_BUCKET}/{wav}"
            self.stdout.write(f"🗣 Transcribing {wav}…")

            try:
                # Upload
                bucket = storage_client.bucket(GCS_BUCKET)
                blob = bucket.blob(wav)
                blob.upload_from_filename(path)

                # Recognize
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code='bn-BD',
                    alternative_language_codes=['en-US'],
                    enable_word_time_offsets=True,
                    enable_automatic_punctuation=True,
                    model='latest_long'
                )
                audio = speech.RecognitionAudio(uri=gcs_uri)
                op = speech_client.long_running_recognize(config=config, audio=audio)
                resp = op.result(timeout=600)

                # Build transcript
                raw = "\n\n".join(r.alternatives[0].transcript.strip() for r in resp.results)
                punct = punctuator.restore_punctuation(raw).replace('.', '।')
                final_text = restore_english_words(punct)

                # NEW: Filter for hate speech (sentence-level)
                if bnlp_available:
                    bnltk = NLTKTokenizer()
                    sentences = bnltk.sentence_tokenization(final_text)
                else:
                    # Fallback: Split on Bangla full stop
                    sentences = [s.strip() for s in final_text.split('।') if s.strip()]

                clean_sentences = []
                hateful_sentences = []
                for sentence in sentences:
                    if ': ' in sentence:
                        speaker, text = sentence.split(': ', 1)
                        if detect_hate_speech(text):
                            hateful_sentences.append(sentence)
                        else:
                            clean_sentences.append(sentence)
                    else:
                        if detect_hate_speech(sentence):
                            hateful_sentences.append(sentence)
                        else:
                            clean_sentences.append(sentence)

                transcript = Transcript.objects.create(
                    meeting=meeting,
                    raw_text=raw,
                    text='। '.join(clean_sentences),  # Join with Bangla full stop
                    hateful_text='। '.join(hateful_sentences) if hateful_sentences else ''
                )

                # Generate TTS for cleaned text only
                if transcript.text:
                    generate_tts_and_save(transcript.text, 'bn', transcript.transcript_audio, transcript, f"transcript_{mid}.mp3")

                # If summary already exists, generate summary audio
                if transcript.summary:
                    generate_tts_and_save(transcript.summary, 'bn', transcript.summary_audio, transcript, f"summary_{mid}.mp3")

                transcript.save()

                # Segment by pauses
                for result in resp.results:
                    words = result.alternatives[0].words
                    buffer = ""
                    start_time_proto = None
                    prev_end_sec = None

                    for idx, w in enumerate(words):
                        sec_start = get_seconds(w.start_time)
                        sec_end = get_seconds(w.end_time)

                        if start_time_proto is None:
                            start_time_proto = w.start_time
                        buffer += w.word + " "

                        pause = sec_start - prev_end_sec if prev_end_sec is not None else 0
                        end_of_audio = (idx == len(words) - 1)

                        if pause > 0.8 or end_of_audio:
                            tot_start = get_seconds(start_time_proto)
                            tot_end = sec_end

                            start_td = datetime.timedelta(seconds=tot_start)
                            end_td = datetime.timedelta(seconds=tot_end)

                            TranscriptSegment.objects.create(
                                transcript=transcript,
                                text=buffer.strip(),
                                start_time=start_td,
                                end_time=end_td
                            )
                            buffer = ""
                            start_time_proto = None

                        prev_end_sec = sec_end

                # Cleanup
                os.remove(path)
                blob.delete()
                self.stdout.write("✅ Transcription & segmentation complete.")

            except Exception as e:
                self.stderr.write(f"⚠️ Error: {e}")