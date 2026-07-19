class DecisionEngine:

    def analyze(self, detected_objects):

        decisions = []

        for obj in detected_objects:

            message = "No Action"
            priority = 0
            
            print(obj)

            direction = obj["direction"].strip().lower()
            distance = obj["distance"].strip().lower()

            print(repr(direction))
            print(repr(distance))

            # Rule 1
            if direction == "center" and distance == "very near":
                message = "Obstacle blocking your path."
                priority = 10

            # Rule 2
            elif direction == "center" and distance == "near":
                message = "Obstacle ahead."
                priority = 8

            decisions.append({
                "id": obj["id"],
                "name": obj["name"],
                "message": message,
                "priority": priority
            })
            
        # Select the highest priority decision
        if len(decisions) == 0:
            return None

        best_decision = max(decisions, key=lambda x: x["priority"])

        return best_decision
