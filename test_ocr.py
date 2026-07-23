import cv2
from ocr.reader import OCRReader

ocr = OCRReader()

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Width :", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:

    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("OCR Camera", frame)

    key = cv2.waitKey(1)

    if key == ord('r'):
        
        print("Hold still...")

        cv2.waitKey(2000)

        ret, frame = cap.read()

        text = ocr.read_text(frame)

        print("\n========== TEXT DETECTED ==========")

        if text:
            print(text)
        else:
            print("No text found.")

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()