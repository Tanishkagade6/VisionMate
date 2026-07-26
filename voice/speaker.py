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

        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pythoncom = None
 
        try:
            with self.lock:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"[Speaker Error] {e}")
        finally:
            if pythoncom:
                pythoncom.CoUninitialize()

    def speak_async(self, text):
        print("SPEAK:", text)
        self.speak(text)

    def stop(self):

        with self.lock:
            self.engine.stop()