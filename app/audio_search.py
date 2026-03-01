import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHUNK_SECONDS = 4

model = WhisperModel("base", device="cpu")

def listen_once():
    print("Speak your query...")

    audio = sd.rec(
        int(SAMPLE_RATE * CHUNK_SECONDS),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    audio = audio.flatten()

    segments, _ = model.transcribe(audio, language="en")
    text = " ".join([seg.text for seg in segments]).strip()

    return text