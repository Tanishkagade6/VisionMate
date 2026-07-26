from core.speaker_manager import speaker
from modules.emergency import Emergency

class CommandHandler:

    def __init__(self):
        self.emergency_module = Emergency()
        self.navigation = None
        
        self.speaker = speaker
        self.document_reader = None

        self.commands = {
            "read document": self.read_document,
            "start navigation": self.start_navigation,
            "stop navigation": self.stop_navigation,
            "describe scene": self.describe_scene,
            "emergency": self.emergency,
            "exit": self.exit
        }

    def execute(self, command):

        action = self.commands.get(command)

        if action:
            return action()

        self.speaker.speak("Sorry, I didn't understand that command.")
        return True

    def read_document(self):

        if self.document_reader is None:
            from ocr.document_reader import DocumentReader
            self.document_reader = DocumentReader()

        self.document_reader.start()
        return True

    def start_navigation(self):
        
        if self.navigation is None:
            from modules.navigation import Navigation
            self.navigation = Navigation()
            
        self.speaker.speak_async("Starting navigation")
        self.navigation.start()
        return True

    def stop_navigation(self):
        if self.navigation is not None:
            self.navigation.stop()

        self.speaker.stop()
        self.speaker.speak_async("Navigation stopped.")

        return True

    def describe_scene(self):
        self.speaker.speak("Scene description module is under construction.")
        return True

    def emergency(self):
        self.emergency_module.activate()
        return True

    def exit(self):
        
        if self.navigation is not None:
            self.navigation.stop()
        
        self.speaker.stop()    
        self.speaker.speak("Goodbye.")
        return False