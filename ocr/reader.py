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
            return ""

        # Resize for better OCR
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

        # Improve contrast
        gray = cv2.equalizeHist(gray)

        # Save processed image (optional)
        cv2.imwrite("processed_document.jpg", gray)

        result = self.ocr.readtext(
            gray,
            detail=1,
            paragraph=False,
            decoder="greedy",
            batch_size=1
        )

        if not result:
            return []

        texts = []

        print("\n========== OCR OUTPUT ==========\n")

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

        print("\n===============================\n")

        return texts