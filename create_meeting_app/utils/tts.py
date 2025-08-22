import os
from gtts import gTTS
from django.core.files import File

def generate_tts_and_save(text, lang, file_field, instance, filename):
    if not text:
        return
    tts = gTTS(text=text, lang=lang)
    file_path = f"media/tts/{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    tts.save(file_path)

    with open(file_path, "rb") as f:
        file_field.save(filename, File(f), save=False)
