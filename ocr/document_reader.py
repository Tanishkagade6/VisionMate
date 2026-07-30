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
        time.sleep(3)

        cap = None

        # Retry opening camera
        for _ in range(5):

            cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            if cap.isOpened():
                break

            time.sleep(1)

        if cap is None or not cap.isOpened():
            self.speaker.speak("Unable to open camera.")
            return

        # -----------------------------
        # Warm up camera and autofocus
        # -----------------------------
        ret = False
        frame = None

        for _ in range(30):
            ret, frame = cap.read()
            time.sleep(0.03)

        cap.release()

        if not ret or frame is None:
            self.speaker.speak("Unable to capture image.")
            return

        # Speak while OCR starts
        self.speaker.speak_async("Reading text.")
        
        print("Captured Frame Shape:", frame.shape)

        texts = self.reader.read_text(frame)

        print("OCR Output:", texts)

        if not texts:
            self.speaker.speak("No text detected. Please move closer and try again.")
            return

        paragraph = " ".join(texts)

        print("\nFinal Text:\n")
        print(paragraph)

        self.speak_long_text(paragraph)

    def speak_long_text(self, text):

        if not text:
            return

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # If OCR returns one long sentence,
        # split into chunks.
        if len(sentences) == 1:
            chunk_size = 180
            sentences = [
                text[i:i + chunk_size]
                for i in range(0, len(text), chunk_size)
            ]

        for sentence in sentences:

            sentence = sentence.strip()

            if sentence:
                self.speaker.speak(sentence)