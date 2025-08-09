import os
from gtts import gTTS

def synthesize_tts(text: str, lang: str = "en", outfile: str = "voice.mp3", slow: bool = True):
    """
    Create a voice-over mp3 from `text` using gTTS.
    """
    clean = " ".join(text.replace("\n", ". ").split())
    # slow=True gives a calmer, clearer delivery
    gTTS(clean, lang=lang, slow=slow).save(outfile)
    return outfile
