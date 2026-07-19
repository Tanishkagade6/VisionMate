class SafetyEngine:
    """
    Decides whether a detected object requires a warning.
    """

    def analyze(self, categorized_objects):

        warnings = []

        for obj in categorized_objects["critical"]:

            direction = obj["direction"]

            if direction == "center":
                priority = 2
                message = f"{obj['name'].capitalize()} ahead."
            else:
                priority = 1
                message = f"{obj['name'].capitalize()} on your {direction}."

            warnings.append({
                "priority": priority,
                "message": message,
                "object": obj["name"],
                "direction": direction,
                "distance": obj["distance"],
                "category": "critical"
            })

        for obj in categorized_objects["obstacles"]:

            direction = obj["direction"]
            distance = obj["distance"]

            priority = None
            message = None

            # Very Near
            if distance == "very near":

                if direction == "center":
                    priority = 5
                    message = f"Immediate obstacle ahead: {obj['name']}."

                else:
                    priority = 4
                    message = f"Immediate obstacle on your {direction}: {obj['name']}."

            elif distance == "near":

                if direction == "center":
                    priority = 4
                    message = f"Obstacle ahead: {obj['name']}."

                else:
                    priority = 3
                    message = f"Obstacle on your {direction}: {obj['name']}."

            elif distance == "medium":

                if direction == "center":
                    priority = 3
                    message = f"{obj['name'].capitalize()} ahead."

                else:
                    priority = 2
                    message = f"{obj['name'].capitalize()} on your {direction}."

            # Far → No warning
            if priority is not None:

                warnings.append({
                    "priority": priority,
                    "message": message,
                    "object": obj["name"],
                    "direction": direction,
                    "distance": distance,
                    "category": "obstacle"
                })

        warnings.sort(
            key=lambda warning: warning["priority"],
            reverse=True
        )

        return warnings