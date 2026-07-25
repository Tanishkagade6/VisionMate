import pyttsx3
import time

class Speaker:

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)

    def speak(self, text):
        if not text:
            return
        
        self.engine.say(text)
        self.engine.runAndWait()
 
        time.sleep(0.5)