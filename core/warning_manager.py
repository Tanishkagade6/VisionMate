import time

class WarningManager:
    """
    Prevents VisionMate from repeating the same warning continuously.
    """

    COOLDOWN = 3  # seconds

    def __init__(self):
        self.last_warning = None
        self.last_time = 0

    def get_warning(self, warnings):

        if not warnings:
            self.last_warning = None
            self.last_time = 0
            return None

        highest_priority_warning = warnings[0]
        current_warning = highest_priority_warning["message"]

        current_time = time.time()

        if current_warning == self.last_warning:

            if current_time - self.last_time < self.COOLDOWN:
                return None

        self.last_warning = current_warning
        self.last_time = current_time

        return highest_priority_warning