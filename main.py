from voice.listener import VoiceListener
from voice.commands import CommandHandler

class VisionMate:

    def __init__(self):

        print("=" * 50)
        print(" VisionMate Started ")
        print("=" * 50)

        self.listener = VoiceListener()
        self.handler = CommandHandler()

    def run(self):
        
        print("\n========== VisionMate ==========")
        print("Available Voice Commands:")
        print("🎤 Start Navigation")
        print("📄 Read Document")
        # print("🌄 Describe Scene")
        print("🚨 Emergency SOS")
        print("❌ Exit")
        print("=" * 33)

        self.handler.speaker.speak_async(
            "Welcome to VisionMate. How can I help you?"
        )

        running = True

        while running:

            command = self.listener.listen()

            if command:
                running = self.handler.execute(command)

        print("VisionMate Closed.")

if __name__ == "__main__":

    app = VisionMate()
    app.run()