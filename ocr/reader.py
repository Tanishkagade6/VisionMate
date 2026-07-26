import cv2
import easyocr
from config import OCR_CONFIDENCE, OCR_SCALE

class OCRReader:

    def __init__(self):
        print("Loading EasyOCR...")
        self.ocr = easyocr.Reader(["en"], gpu=False)
        print("EasyOCR Ready!")

    def read_text(self, frame):
        if frame is None:
            h, w = frame.shape[:2]

            frame = frame[
                int(h * 0.15):int(h * 0.85),
                int(w * 0.10):int(w * 0.90)
            ]
            
            return ""

        frame = cv2.resize(frame, None, fx=OCR_SCALE, fy=OCR_SCALE, interpolation=cv2.INTER_CUBIC)

        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # gray = cv2.equalizeHist(gray)

        # Reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Adaptive threshold
        gray = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15
        )

        result = self.ocr.readtext(
            gray,
            paragraph=False,
            detail=1,
            decoder="beamsearch",
            width_ths=0.7,
            batch_size=1
        )
        if not result:
            return ""

        texts = []
        print("\nDetected Text:\n")
        
        for item in result:

            if len(item) == 3:
                bbox, text, confidence = item

                text = text.strip()

                if confidence >= OCR_CONFIDENCE:
                    print(f"{text} --> {confidence:.2f}")
                    texts.append(text)

            elif len(item) == 2:
                bbox, text = item

                text = text.strip()

                print(text)
                texts.append(text)

        return texts
