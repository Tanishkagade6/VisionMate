from collections import defaultdict

class SceneDescriber:

    def __init__(self):
        # Higher priority objects are described first
        self.priority = {
            "person": 1,
            "car": 2,
            "bus": 2,
            "truck": 2,
            "motorcycle": 2,
            "bicycle": 2,
            "dog": 3,
            "cat": 3,
            "chair": 4,
            "table": 4,
            "bench": 4,
            "bottle": 5,
            "cup": 5,
            "book": 5,
            "cell phone": 5
        }

    def describe_scene(self, detected_objects):

        if not detected_objects:
            return "The area around you appears clear."

        # Sort important objects first
        detected_objects = sorted(
            detected_objects,
            key=lambda x: self.priority.get(x["name"], 100)
        )

        grouped = defaultdict(list)

        for obj in detected_objects:
            grouped[obj["name"]].append(obj)

        sentences = []

        for name, objs in grouped.items():

            count = len(objs)

            if count == 1:

                obj = objs[0]

                direction = self.get_direction(obj["direction"])
                distance = self.get_distance(obj["distance"])

                sentences.append(
                    f"There is a {name} {direction}{distance}."
                )

            else:

                directions = defaultdict(int)

                for obj in objs:
                    directions[obj["direction"]] += 1

                parts = []

                for direction, num in directions.items():

                    if num == 1:
                        parts.append(f"one {self.get_direction(direction)}")
                    else:
                        parts.append(f"{num} {self.get_direction(direction)}")

                if name == "person":
                    name_text = "people"
                else:
                    name_text = name + "s"

                sentences.append(
                    f"There are {count} {name_text}: {', '.join(parts)}."
                )

        return " ".join(sentences)

    def get_direction(self, direction):

        mapping = {
            "left": "on your left",
            "right": "on your right",
            "center": "ahead"
        }

        return mapping.get(direction, "nearby")

    def get_distance(self, distance):

        mapping = {
            "very near": ", very close to you",
            "near": ", nearby",
            "medium": ", a short distance away",
            "far": ", farther away"
        }

        return mapping.get(distance, "")