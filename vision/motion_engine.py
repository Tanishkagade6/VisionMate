class MotionEngine:

    def analyze(self, previous, current_center_x, current_box_height):

        if previous is None:
            return "Unknown"

        dx = current_center_x - previous["center_x"]
        dh = current_box_height - previous["box_height"]

        # Horizontal movement
        if dx > 20:
            horizontal = "Moving Right"
        elif dx < -20:
            horizontal = "Moving Left"
        else:
            horizontal = "Stationary"

        # Distance movement
        if dh > 20:
            depth = "Approaching"
        elif dh < -20:
            depth = "Moving Away"
        else:
            depth = "Stable"

        return {
            "horizontal": horizontal,
            "depth": depth
        }