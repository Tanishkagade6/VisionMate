class DirectionEngine:
    
    def get_direction(self, center_x, frame_width):

        left_boundary = frame_width // 3
        right_boundary = (2 * frame_width) // 3

        if center_x < left_boundary:
            return "left"

        elif center_x < right_boundary:
            return "center"

        return "right"