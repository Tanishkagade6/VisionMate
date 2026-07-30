import pyttsx3
import threading
import queue


class Speaker:

    def __init__(self):
        self.queue = queue.Queue()

        self.worker_thread = threading.Thread(
            target=self.worker,
            daemon=True
        )
        self.worker_thread.start()

    def worker(self):

        # IMPORTANT:
        # Create the TTS engine INSIDE this thread.
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)

        while True:

            text = self.queue.get()

            if text is None:
                break

            try:
                print(f"SPEAK: {text}")

                engine.say(text)
                engine.runAndWait()

            except Exception as e:
                print(f"[Speaker Error] {e}")

            finally:
                self.queue.task_done()

        engine.stop()

    def speak_async(self, text):

        if not text:
            return

        self.queue.put(text)

    def speak(self, text):
        self.speak_async(text)

    def stop(self):

        # Stop current speech
        self.queue.put(None)

        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)