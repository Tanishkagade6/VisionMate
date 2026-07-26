import threading
from vision.detector import VisionDetector

class Navigation:

    def __init__(self):
        self.detector = VisionDetector()
        self.thread = None

    def start(self):

        # Prevent multiple navigation threads
        if self.thread and self.thread.is_alive():
            print("[INFO] Navigation is already running.")
            return

        print("[INFO] Starting Navigation...")

        self.thread = threading.Thread(
            target=self.detector.start_camera,
            daemon=True)

        self.thread.start()

    def stop(self):

        print("[INFO] Stopping Navigation...")

        self.detector.stop_camera()

        if self.thread:
            self.thread.join(timeout=2)