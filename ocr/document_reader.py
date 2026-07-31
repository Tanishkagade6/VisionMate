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
        """Original console version — untouched, kept for reference."""

        self.speaker.speak("Hold the document steady.")
        time.sleep(3)

        cap = None

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

        ret = False
        frame = None

        for _ in range(30):
            ret, frame = cap.read()
            time.sleep(0.03)

        cap.release()

        if not ret or frame is None:
            self.speaker.speak("Unable to capture image.")
            return

        self.speaker.speak_async("Reading text.")

        texts = self.reader.read_text(frame)

        if not texts:
            self.speaker.speak("No text detected. Please move closer and try again.")
            return

        paragraph = " ".join(texts)
        self.speak_long_text(paragraph)

    def capture_and_read(self, stop_event=None, on_frame=None):
        """
        Streamlit version — returns (frame, texts) instead of only
        speaking, reports each warm-up frame via on_frame() for a live
        camera preview, and checks stop_event so "stop reading" can
        cut off mid-sentence.
        """

        self.speaker.speak("Hold the document steady.")
        time.sleep(2)

        cap = None
        for _ in range(5):
            cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
            if cap.isOpened():
                break
            time.sleep(1)

        if cap is None or not cap.isOpened():
            self.speaker.speak("Unable to open camera.")
            return None, []

        ret = False
        frame = None

        # Allow camera to autofocus — stream each frame for a live preview
        for _ in range(10):
            ret, frame = cap.read()
            if ret and frame is not None and on_frame:
                on_frame(frame)

        cap.release()

        if not ret or frame is None:
            self.speaker.speak("Unable to capture image.")
            return None, []

        if on_frame:
            on_frame(frame)  # show the final captured frame too

        if stop_event and stop_event.is_set():
            return frame, []

        self.speaker.speak_async("Reading text.")
        texts = self.reader.read_text(frame)

        if texts:
            self.speak_long_text(" ".join(texts), stop_event=stop_event)
        else:
            self.speaker.speak("No text detected. Please move closer and try again.")

        return frame, texts

    def speak_long_text(self, text, stop_event=None):

        if not text:
            return

        sentences = re.split(r'(?<=[.!?])\s+', text)

        if len(sentences) == 1:
            chunk_size = 180
            sentences = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for sentence in sentences:

            if stop_event and stop_event.is_set():
                self.speaker.stop()
                return

            sentence = sentence.strip()
            if sentence:
                self.speaker.speak(sentence)
