from gtts import gTTS
from io import BytesIO

def generate_audio(text, language):
    tts = gTTS(text=text, lang=language)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    return mp3_fp
