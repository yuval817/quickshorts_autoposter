import os
from gtts import gTTS

def synthesize_tts(text: str, lang: str = "en", outfile: str = "voice.mp3"):
    """
    Create a voice-over mp3 from `text` using gTTS.
    Returns the path to the saved mp3.
    """
    # make the text TTS-friendly
    clean = " ".join(text.replace("\n", ". ").split())
    tts = gTTS(clean, lang=lang)
    tts.save(outfile)
    return outfile
