from emergency.sos import SOS

class Emergency:

    def __init__(self):
        self.sos = SOS()

    def activate(self):
        self.sos.activate()