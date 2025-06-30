# create_meeting_app/management/commands/transcribe_meeting.py

from django.core.management.base import BaseCommand
from create_meeting_app.models import Meeting, Transcript
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage

GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

speech_client = speech.SpeechClient.from_service_account_file(KEY_PATH)
storage_client = storage.Client.from_service_account_json(KEY_PATH)

class Command(BaseCommand):
    help = "Transcribe WAV files in single‑speaker, multilingual mode"

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

                # 2) Recognition config: multilingual, single speaker
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="bn-BD",                  # primary Bangla
                    alternative_language_codes=["en-US"],   # also support English
                    enable_automatic_punctuation=True,
                    model="default"
                    # no diarization flags here
                )
                audio = speech.RecognitionAudio(uri=gcs_uri)

                # 3) Transcribe
                operation = speech_client.long_running_recognize(
                    config=config, audio=audio
                )
                response = operation.result(timeout=600)

                # 4) Concatenate all result transcripts
                full_text = "\n\n".join(
                    result.alternatives[0].transcript.strip()
                    for result in response.results
                )

                # 5) Save to DB once
                Transcript.objects.create(
                    meeting=meeting,
                    text=full_text
                )

                # 6) Cleanup
                os.remove(path)
                blob.delete()
                self.stdout.write("✅ Transcription complete and cleaned up.")

            except Exception as e:
                self.stderr.write(f"⚠️ Error: {e}")
