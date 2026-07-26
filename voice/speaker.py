import pyttsx3
import threading


class Speaker:

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)

        self.lock = threading.Lock()

    def speak(self, text):

        if not text:
            return

        with self.lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[Speaker Error] {e}")

    def speak_async(self, text):

        threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True
        ).start()

    def stop(self):

        with self.lock:
            self.engine.stop()