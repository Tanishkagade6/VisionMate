import requests
from core.speaker_manager import speaker
from emergency.contacts import EMERGENCY_CONTACTS
from config import EMERGENCY_URL
import config

class SOS:

    def __init__(self):
        self.speaker = speaker

    def activate(self):

        self.speaker.speak_async("Emergency detected. Contacting emergency contact.")

        print("EMERGENCY_URL =", EMERGENCY_URL)

        try:
            response = requests.get(EMERGENCY_URL, timeout=5)
            print("Status Code:", response.status_code)
            print("Response:", response.text)
            return True, f"Emergency signal sent. Status {response.status_code}."

        except Exception as e:
            print("ERROR:", e)
            return False, f"Could not reach emergency device: {e}"