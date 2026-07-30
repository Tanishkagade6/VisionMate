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
            response = requests.get(EMERGENCY_URL,
                timeout=5
            )

            print("Status Code:", response.status_code)
            print("Response:", response.text)

        except Exception as e:
            print("ERROR:", e)

        # try:
        #     response = requests.get(EMERGENCY_URL,timeout=5)

        #     if response.status_code == 200:
        #         print("Emergency trigger sent successfully.")

        #         for contact in EMERGENCY_CONTACTS:
        #             print(f"Notified {contact['name']} ({contact['phone']})")

        #         self.speaker.speak("Emergency contact has been notified.")

        #     else:
        #         self.speaker.speak("Failed to trigger emergency.")

        # except Exception as e:
        #     print(e)
        #     self.speaker.speak("Unable to connect to your phone.")