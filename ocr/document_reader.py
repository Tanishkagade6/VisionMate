import cv2
import time

from config import VIDEO_URL
from ocr.reader import OCRReader
from voice.speaker import Speaker

class DocumentReader:

    def __init__(self):
        self.reader = OCRReader()
        self.speaker = Speaker()

    def start(self):

        self.speaker.speak("Hold the document steady.")
        time.sleep(2)

        cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            self.speaker.speak("Unable to open camera.")
            return
        
        ret, frame = cap.read()

        cap.release()

        if not ret:
            self.speaker.speak("Unable to capture image.")
            return
        
        self.speaker.speak("Reading text.")
        
        text = self.reader.read_text(frame)
    
        if text:
            self.speaker.speak(text)
        else:
            self.speaker.speak(
                "No text detected. Please move closer and try again.")