import easyocr
import cv2

class OCRReader:

    def __init__(self):
        print("Loading EasyOCR model...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        print("OCR Ready!")

    def read_text(self, frame):

        if frame is None:
            return ""

        # # Convert to grayscale
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # # Increase contrast
        # gray = cv2.equalizeHist(gray)
        # # Remove slight noise
        # gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # # Sharpen text using thresholding
        # _, processed = cv2.threshold(
        #     gray,
        #     0,
        #     255,
        #     cv2.THRESH_BINARY + cv2.THRESH_OTSU
        # )

        results = self.reader.readtext(
            processed,
            detail=0,
            paragraph=True
        )

        return " ".join(results)