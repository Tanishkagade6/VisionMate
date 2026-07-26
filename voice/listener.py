import json     #converts text into python
import queue
import sounddevice as sd
from config import VOSK_MODEL_PATH
from vosk import Model, KaldiRecognizer

class VoiceListener:

    def __init__(self):
        self.model = Model(VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, 16000)     #16000 samples every second.

        self.audio_queue = queue.Queue()

    def callback(self, indata, frames, time, status):
        if status:
            print(status)

        self.audio_queue.put(bytes(indata))

    def listen(self):

        print("\n🎤 Listening...")

        with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                device=1,          # Realtek Microphone
                callback=self.callback):

            while True:

                data = self.audio_queue.get()

                if self.recognizer.AcceptWaveform(data):

                    result = json.loads(self.recognizer.Result())

                    text = result.get("text", "").strip().lower()

                    if text:
                        print(f"✅ You said: {text}")
                        return text