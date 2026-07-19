class DistanceEngine:
    
    VERY_NEAR_THRESHOLD = 0.60
    NEAR_THRESHOLD = 0.40
    MEDIUM_THRESHOLD = 0.18

    def estimate(self, box_height, frame_height):
    
        height_ratio = box_height / frame_height

        if height_ratio > self.VERY_NEAR_THRESHOLD:
            return "very near"

        elif height_ratio > self.NEAR_THRESHOLD:
            return "near"

        elif height_ratio > self.MEDIUM_THRESHOLD:
            return "medium"

        return "far"