from django.core.management.base import BaseCommand
from create_meeting_app.models import Meeting, Transcript, TranscriptSegment
import os
import datetime
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from deepmultilingualpunctuation import PunctuationModel

GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

speech_client = speech.SpeechClient.from_service_account_file(KEY_PATH)
storage_client = storage.Client.from_service_account_json(KEY_PATH)

ENGLISH_WORDS = {
    "সিরিয়াসলি": "seriously",
    "হোমওয়ার্ক": "homework",
    "হাই": "hi",
    "হ্যালো": "hello",
    "হ্যালো এভরিওয়ান": "hello everyone",
    "এভরিওয়ান": "everyone",
    "গুড মর্নিং": "good morning",
    "গুড নাইট": "good night",
    "গুড ইভিনিং": "good evening",
    "টেনশন": "tension",
    "মিডটার্ম": "midterm",
    "কুইজ": "quiz",
    "প্রেজেন্টেশন": "presentation",
    "ডেডলাইন": "deadline",
    "রেজাল্ট": "result",
    "অ্যাসাইনমেন্ট": "assignment",
    "মার্কস": "marks",
    "ক্লাস": "class",
    "প্রজেক্ট": "project",
    "ইউনিভার্সিটি": "university",
    "সেমিস্টার": "semester",
    "থিসিস": "thesis",
    "স্টাডি": "study",
    "ফাইনাল": "final",
    "আটেন্ডেন্স": "attendance",
    "লেকচার": "lecture",
    "গুগল": "Google",
    "মিট": "Meet",
    "পিডিএফ": "PDF",
    "নোট": "note",
    "রেজিস্ট্রেশন": "registration",
    "টিচার": "teacher",
    "স্যার": "sir",
    "ম্যাডাম": "madam"
    # You can keep adding more if needed
}

def restore_english_words(text):
    for bn, en in ENGLISH_WORDS.items():
        text = text.replace(bn, en)
    return text

def get_seconds(d):
    """
    Return total seconds of a protobuf Duration or a datetime.timedelta.
    """
    if hasattr(d, 'nanos'):
        return d.seconds + d.nanos / 1e9
    else:
        return d.total_seconds()

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

                transcript = Transcript.objects.create(
                    meeting=meeting,
                    raw_text=raw,
                    text=final_text
                )

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

                        # Compute pause from previous word
                        pause = sec_start - prev_end_sec if prev_end_sec is not None else 0
                        end_of_audio = (idx == len(words) - 1)

                        # Split if long pause or end of this result
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