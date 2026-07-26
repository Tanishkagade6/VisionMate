from paddleocr import PaddleOCR
import cv2
from config import OCR_CONFIDENCE, OCR_SCALE

class OCRReader:

    def __init__(self):

        print("Loading PaddleOCR...")

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en")

        print("PaddleOCR Ready!")

    def read_text(self, frame):

        if frame is None:
            return ""

        # Upscale image for better OCR
        frame = cv2.resize(
            frame,
            None,
            fx=OCR_SCALE,
            fy=OCR_SCALE,
            interpolation=cv2.INTER_CUBIC
        )

        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Increase contrast
        gray = cv2.equalizeHist(gray)

        # OCR
        result = self.ocr.ocr(gray, cls=True)

        if not result or result[0] is None:
            return ""

        texts = []

        print("\nDetected Text:\n")

        for line in result[0]:

            text = line[1][0].strip()
            confidence = line[1][1]

            if confidence >= OCR_CONFIDENCE:
                print(f"{text} --> {confidence:.2f}")
                texts.append(text)

        return texts