import cv2
from vision.detector import VisionDetector
from ocr.reader import OCRReader
from modules.emergency import Emergency
from core.speaker_manager import speaker
from config import VIDEO_URL

detector = VisionDetector()
ocr = OCRReader()
emergency = Emergency()

while True:

    print("\n========== VisionMate ==========")
    print("1. Navigation")
    print("2. Read Document")
    print("3. Emergency")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        detector.start_camera()

    elif choice == "2":
        cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not cap.isOpened():
            print("Could not open camera")
            continue

        print("\nPress SPACE to capture document")
        print("Press ESC to cancel")

        while True:

            ret, frame = cap.read()\
            
            cv2.imwrite("ocr_test.jpg", frame)

            if not ret:
                break

            cv2.imshow("Document Reader", frame)

            key = cv2.waitKey(1)

            # SPACE
            if key == 32:
                cv2.imwrite("ocr_test.jpg", frame)
                print("Saved ocr_test.jpg")                
                texts = ocr.read_text(frame)
                
                print("\n========== OCR RESULT ==========\n")

                for line in texts:
                    print(line)

                if texts:
                    speaker.speak_async(" ".join(texts))
                
                if texts:
                    speaker.speak_async(" ".join(texts))

                print("\n========== OCR RESULT ==========\n")

                if len(texts) == 0:
                    print("No text detected.")

                else:
                    for t in texts:
                        print(t)

                break

            # ESC
            elif key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()  

    elif choice == "3":
        emergency.activate()

    elif choice == "4":
        break

    else:
        print("Invalid choice")