import cv2
import time
import re

from config import VIDEO_URL
from ocr.reader import OCRReader
from core.speaker_manager import speaker


class DocumentReader:

    def __init__(self):
        self.reader = OCRReader()
        self.speaker = speaker

    def start(self):

        self.speaker.speak("Hold the document steady.")
        time.sleep(2)

        cap = None

        # Retry opening the camera
        for _ in range(5):
            cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)

            if cap.isOpened():
                break

            time.sleep(1)

        if cap is None or not cap.isOpened():
            self.speaker.speak("Unable to open camera.")
            return

        # Allow camera to autofocus
        for _ in range(10):
            ret, frame = cap.read()

        cap.release()

        if not ret:
            self.speaker.speak("Unable to capture image.")
            return

        cv2.imwrite("captured_document.jpg", frame)

        self.speaker.speak("Reading text.")
        
        texts = self.reader.read_text(frame)

        if texts:
            chunk = ""
            
            for line in texts:
                chunk += line + " "
                
                # Speak after approximately 250 characters
                if len(chunk) > 250:
                    self.speaker.speak(chunk.strip())
                    chunk = ""

            # Speak any remaining text
            if chunk:
                self.speaker.speak(chunk.strip())
                
            else:
                self.speaker.speak("No text detected. Please move closer and try again.")
    
    def speak_long_text(self, text):

        if not text:
            return

        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # If OCR returns one very long sentence,
        # split it into smaller chunks.
        if len(sentences) == 1:
            chunk_size = 200
            sentences = [
                text[i:i + chunk_size]
                for i in range(0, len(text), chunk_size)
            ]

        for sentence in sentences:

            sentence = sentence.strip()

            if sentence:
                self.speaker.speak_async(sentence) 