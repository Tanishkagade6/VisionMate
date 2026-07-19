class TrackerMemory:

    def __init__(self):
        # Stores previous information for each tracked object
        self.memory = {}

    def update(self, track_id, center_x, box_height):

        previous = self.memory.get(track_id)

        self.memory[track_id] = {
            "center_x": center_x,
            "box_height": box_height
        }

        return previous