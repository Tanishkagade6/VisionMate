class ObjectFilter:
    
    MIN_CONFIDENCE = 0.50

    CRITICAL_OBJECTS = {
        "person",
        "bicycle",
        "motorcycle",
        "car",
        "bus",
        "truck",
        "train"
    }

    OBSTACLE_OBJECTS = {
        "chair",
        "bench",
        "couch",
        "bed",
        "dining table",
        "potted plant",
        "backpack",
        "suitcase",
        "tv",
        "refrigerator",
        "oven",
        "microwave",
        "sink",
        "toilet"
    }

    OPTIONAL_OBJECTS = {
        "bottle",
        "cup",
        "cell phone",
        "laptop",
        "book",
        "remote",
        "keyboard",
        "mouse",
        "umbrella",
        "handbag",
        "clock",
        "vase"
    }

    def filter_objects(self, detected_objects):
        """
        Categorizes detected objects into:
        - critical
        - obstacles
        - optional
        - unknown
        """

        categorized_objects = {
            "critical": [],
            "obstacles": [],
            "optional": [],
            "unknown": []
        }

        for obj in detected_objects:

            # Ignore low-confidence detections
            if obj["confidence"] < self.MIN_CONFIDENCE:
                continue

            object_name = obj["name"].lower()

            if object_name in self.CRITICAL_OBJECTS:
                categorized_objects["critical"].append(obj)

            elif object_name in self.OBSTACLE_OBJECTS:
                categorized_objects["obstacles"].append(obj)

            elif object_name in self.OPTIONAL_OBJECTS:
                categorized_objects["optional"].append(obj)

            else:
                categorized_objects["unknown"].append(obj)

        return categorized_objects