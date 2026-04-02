import sounddevice as sd
import numpy as np
import wavio
import speech_recognition as sr

def get_voice_input(duration=5, fs=44100):
    """
    Records voice for `duration` seconds and returns recognized text.
    """
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wavio.write("temp.wav", recording, fs, sampwidth=2)  # save recording

    r = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service error."