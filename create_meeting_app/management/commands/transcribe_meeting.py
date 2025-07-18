from django.core.management.base import BaseCommand
from create_meeting_app.models import Meeting, Transcript
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from deepmultilingualpunctuation import PunctuationModel

# Load env vars
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Initialize clients
speech_client = speech.SpeechClient.from_service_account_file(KEY_PATH)
storage_client = storage.Client.from_service_account_json(KEY_PATH)

class Command(BaseCommand):
    help = "Transcribe WAV files in Bangla with smart punctuation"

    def add_arguments(self, parser):
        parser.add_argument('meeting_id', type=int)

    def handle(self, *args, **options):
        meeting_id = options['meeting_id']
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if not meeting:
            return self.stderr.write("❌ Meeting not found.")

        recordings = sorted(
            f for f in os.listdir("media/recordings")
            if f.endswith(".wav") and f"_{meeting_id}_" in f
        )
        if not recordings:
            return self.stdout.write("📭 No recordings found.")

        # Load punctuation model once
        punctuator = PunctuationModel()

        for wav_file in recordings:
            path = os.path.join("media/recordings", wav_file)
            gcs_uri = f"gs://{GCS_BUCKET}/{wav_file}"
            self.stdout.write(f"🗣 Transcribing {wav_file}…")

            try:
                # 1) Upload WAV to GCS
                bucket = storage_client.bucket(GCS_BUCKET)
                blob = bucket.blob(wav_file)
                blob.upload_from_filename(path)
                self.stdout.write(f"☁️ Uploaded to {gcs_uri}")

                # 2) Transcription config
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="bn-BD",
                    alternative_language_codes=["en-US"],
                    enable_automatic_punctuation=True,
                    model="latest_long"
                )
                audio = speech.RecognitionAudio(uri=gcs_uri)

                # 3) Transcribe
                operation = speech_client.long_running_recognize(config=config, audio=audio)
                response = operation.result(timeout=600)

                # 4) Join raw transcripts
                raw_text = "\n\n".join(
                    result.alternatives[0].transcript.strip()
                    for result in response.results
                )

                # 5) Punctuate and convert full stops to Bangla danda
                punctuated = punctuator.restore_punctuation(raw_text)
                punctuated_bangla = punctuated.replace('.', '।')

                # 6) Save to DB
                Transcript.objects.create(
                    meeting=meeting,
                    text=punctuated_bangla
                )

                # 7) Clean up
                os.remove(path)
                blob.delete()
                self.stdout.write("✅ Transcription complete and cleaned up.")

            except Exception as e:
                self.stderr.write(f"⚠️ Error: {e}")
