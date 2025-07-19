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

# Your custom English words dictionary (Bangla phonetic to English)
ENGLISH_WORDS = {
    "সিরিয়াসলি": "seriously",
    "হোমওয়ার্ক": "homework",
    "হাই": "hi",
    "হ্যালো": "hello",
    "হ্যালো এভরিওয়ান": "hello everyone",
    "এভরিওয়ান":"everyone",
    "গুড মর্নিং": "good morning",
    "গুড নাইট": "good night",
    "গুড ইভিনিং": "good evening",
    "টেনশন": "tension",
    "মিড": "mid",
    "মিডটার্ম": "midterm",
    "এক্সাম": "exam",
    "ফাইনাল": "final",
    "কুইজ": "quiz",
    "অ্যাসাইনমেন্ট": "assignment",
    "প্রেজেন্টেশন": "presentation",
    "সাবমিট": "submit",
    "সাবমিশন": "submission",
    "ডেডলাইন": "deadline",
    "ল্যাব": "lab",
    "প্রজেক্ট": "project",
    "প্রজেক্ট ওয়ার্ক": "project work",
    "ক্লাস": "class",
    "লেকচার": "lecture",
    "রিসার্চ": "research",
    "থিসিস": "thesis",
    "জিপিএ": "GPA",
    "ক্রেডিট": "credit",
    "সেমিস্টার": "semester",
    "রেজাল্ট": "result",
    "রেজাল্টেড": "resulted",
    "শর্ট": "short",
    "মার্কস": "marks",
    "নম্বর": "marks",
    "পারসেন্টেজ": "percentage",
    "রোল": "roll",
    "রেজিস্ট্রেশন": "registration",
    "আটেন্ডেন্স": "attendance",
    "টিচার": "teacher",
    "স্যার": "sir",
    "ম্যাডাম": "madam",
    "কনফারেন্স": "conference",
    "ইন্টার্ন": "intern",
    "ইন্টার্নশিপ": "internship",
    "ড্রপ": "drop",
    "ইমপ্রুভ": "improve",
    "মডারেশন": "moderation",
    "গ্রেড": "grade",
    "টার্ম": "term",
    "ইউনিভার্সিটি": "university",
    "ক্যাম্পাস": "campus",
    "রেগুলার": "regular",
    "ইয়ার": "year",
    "ব্রেক": "break",
    "ভ্যাকেশন": "vacation",
    "ম্যাথ": "math",
    "ফিজিক্স": "physics",
    "কেমিস্ট্রি": "chemistry",
    "বায়ো": "biology",
    "কম্পিউটার": "computer",
    "প্র্যাকটিকাল": "practical",
    "ফর্ম": "form",
    "নোটিস": "notice",
    "ভাইভা": "viva",
    "অফিস": "office",
    "ডিপার্টমেন্ট": "department",
    "ফ্যাকাল্টি": "faculty",
    "সিভি": "CV",
    "সার্টিফিকেট": "certificate",
    "আইডি": "ID",
    "শিফট": "shift",
    "অনলাইন": "online",
    "অফলাইন": "offline",
    "জুম": "Zoom",
    "মিট": "Meet",
    "গুগল মিট": "Google Meet",
    "প্রজেক্টর": "projector",
    "স্লাইড": "slide",
    "গুগল": "Google",
    "ড্রাইভ": "Drive",
    "ফাইল": "file",
    "ফোল্ডার": "folder",
    "পিডিএফ": "PDF",
    "ওয়ার্ড": "Word",
    "পাওয়ারপয়েন্ট": "PowerPoint",
    "নোট": "note",
    "নোটস": "notes",
    "ক্যালকুলেশন": "calculation",
    "সিলেবাস": "syllabus",
    "কোর্স": "course",
    "সাজেশন": "suggestion",
    "স্টাডি": "study",
    "পড়াশোনা": "study",
    "প্রিপারেশন": "preparation",
    "রিভিশন": "revision",
    "গ্রুপস্টাডি": "group study",
    "ডিউ": "due",
    "রিমাইন্ডার": "reminder",
    "টাস্ক": "task",
    "কনসাল্ট": "consult",
    "আফটারক্লাস": "after class",
    "এক্সট্রা": "extra",
    "ক্লাসটেস্ট": "class test",
    "মডেলটেস্ট": "model test",
    "রেজিস্ট্রার": "registrar",
    "ডিন": "dean",
    "কনফার্ম": "confirm",
    "চেক": "check",
    "কমপ্লিট": "complete",
    "অ্যাপ্লিকেশন": "application",
    "এপ্লিকেশন": "application",
    "এপ্লাই": "apply",
    "ডকুমেন্ট": "document",
    "লগইন": "login",
    "সাইনআপ": "signup",
    "ইমেইল": "email",
    "লিঙ্কডইন": "LinkedIn",
    "ম্যাসেজ": "message",
    "গ্রুপচ্যাট": "group chat",
    "নোটিফিকেশন": "notification",
    "অ্যাপ": "app",
    "ডাউনলোড": "download",
    "আপলোড": "upload",
    "জার্নাল": "journal",
    "রেফারেন্স": "reference",
    "রিপোর্ট": "report",
    "ফিডব্যাক": "feedback",
    "পারফরমেন্স": "performance",
    "কোঅর্ডিনেট": "coordinate",
    "মিটিং": "meeting",
    "ডিসকাশন": "discussion",
    "পারসোনাল": "personal",
    "অফিশিয়াল": "official",
    "ওয়ান্স": "once",
    "টাইম": "time",
    "ডেট": "date",
    "প্ল্যান": "plan",
    "রিল্যাক্স": "relax",
    "বিজি": "busy",
    "ক্যাজুয়াল": "casual",
    "ইম্পরট্যান্ট": "important",
    "ইমিডিয়েটলি": "immediately",
    "ফাইনালি": "finally",
    "ইনশাআল্লাহ": "InshaAllah",
    "আলহামদুলিল্লাহ": "Alhamdulillah",
    "সাবানআল্লাহ": "SubhanAllah",
    "ইয়েস": "yes",
    "নো": "no",
    "ওকে": "okay",
    "ভেরি গুড": "very good",
    "থ্যাঙ্ক ইউ": "thank you",
    "ওয়েল ডান": "well done",
    "কনগ্র্যাচুলেশনস": "congratulations",
    "বেস্ট অফ লাক": "best of luck"
}


def restore_english_words(text):
    for bangla_word, english_word in ENGLISH_WORDS.items():
        text = text.replace(bangla_word, english_word)
    return text

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

                # 5.1) Restore English words from your custom dictionary
                final_text = restore_english_words(punctuated_bangla)

                # 6) Save to DB
                Transcript.objects.create(
                    meeting=meeting,
                    text=final_text
                )

                # 7) Clean up
                os.remove(path)
                blob.delete()
                self.stdout.write("✅ Transcription complete and cleaned up.")

            except Exception as e:
                self.stderr.write(f"⚠️ Error: {e}")
