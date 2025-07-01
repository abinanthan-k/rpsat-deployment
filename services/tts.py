from gtts import gTTS

def generate_audio(text, filename, language):
    tts = gTTS(text=text, lang=language)
    tts.save(filename)
