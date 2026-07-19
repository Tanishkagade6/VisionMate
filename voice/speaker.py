import threading   #(camera capturing + speaking warnings)
import queue
import pyttsx3     # text-speech conversion library

class Speaker:
   
    SPEECH_RATE = 170

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.SPEECH_RATE)

        self.queue = queue.Queue()

        self.worker = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )
        self.worker.start()

    def _speech_worker(self):
        """Continuously speaks queued messages."""

        while True:
            message = self.queue.get()

            try:
                self.engine.say(message)
                self.engine.runAndWait()

            except Exception as e:
                print(f"Speech Error: {e}")

            self.queue.task_done()

    def speak_async(self, message):
        """Adds a message to the speech queue."""
        
        if not message:
            return

        if self.queue.empty():
            self.queue.put(message)