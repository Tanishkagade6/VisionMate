from collections import Counter

class DecisionEngine:
    
    PEOPLE = {"person"}
    ANIMALS = {"dog","cat","bird","horse","sheep","cow","elephant","bear","zebra","giraffe"}
    VEHICLES = {"car","bus","truck","motorcycle","bicycle","train"}
    OBJECTS = {"chair","bench","table","bottle","cup","backpack","suitcase","tv","laptop"}
    
    HAZARD_WEIGHTS = {
    "person": 6,
    "animal": 5,
    "vehicle": 10,
    "object": 2
    }
    
    def summarize_objects(self, detected_objects):

        names = [obj["name"].lower() for obj in detected_objects]
        counts = Counter(names)

        summary = []

        for name, count in counts.items():

            if count == 1:
                summary.append(f"1 {name}")

            else:
                if name == "person":
                    summary.append(f"{count} people")
                else:
                    summary.append(f"{count} {name}s")
                
        return summary
    
    def analyze_scene_layout(self, detected_objects):
        
        layout = {
            "left": [],
            "center": [],
            "right": []
        }

        for obj in detected_objects:

            direction = obj["direction"].lower().strip()

            if direction in layout:
                layout[direction].append(obj["name"])

        return layout
    
    def find_safe_direction(self, scene_layout):

            left_count = len(scene_layout["left"])
            center_count = len(scene_layout["center"])
            right_count = len(scene_layout["right"])

            print("\nObject Count")
            print(f"Left   : {left_count}")
            print(f"Center : {center_count}")
            print(f"Right  : {right_count}")

            counts = {
                "left": left_count,
                "center": center_count,
                "right": right_count
            }

            safe_direction = min(counts, key=counts.get)

            return safe_direction
        
    def calculate_hazard_score(self, decisions):
        scores = {
            "left": 0,
            "center": 0,
            "right": 0
        }

        for decision in decisions:

            category = decision["category"]
            
            obj_id = decision["id"]

            weight = self.HAZARD_WEIGHTS.get(category, 1)
            
            motion_bonus = 0

            for obj in self.current_objects:

                if obj["id"] == obj_id:

                    motion = obj.get("motion", {})

                    if isinstance(motion, dict):
                        depth = motion.get("depth", "Stable")
                        motion_bonus = self.get_motion_bonus(depth)

                    break

            weight += motion_bonus
            
            print(f"{obj['name']} | Base:{self.HAZARD_WEIGHTS.get(category,1)} | "
                  f"Motion:{motion_bonus} | Final:{weight}")

            for obj in self.current_objects:

                if obj["id"] == obj_id:

                    direction = obj["direction"].lower()

                    if direction in scores:
                        scores[direction] += weight

                    break

        return scores
    
    def get_motion_bonus(self, depth):

        depth = depth.lower()

        if depth == "approaching":
            return 3

        elif depth == "moving away":
            return -2

        return 0
    
    def get_safest_direction(self, hazard_scores):

        safest_direction = min(hazard_scores, key=hazard_scores.get)

        return safest_direction
    
    def generate_navigation_instruction(self, hazard_scores):

        path_status = self.get_path_status(hazard_scores)

        center = path_status["center"]
        left = path_status["left"]
        right = path_status["right"]

        # Center is completely safe
        if center == "Clear":
            return "Path ahead is clear. Continue straight."

        # Center has a small obstacle
        elif center == "Caution":

            if left == "Clear":
                return "Person ahead. Move slightly left."

            elif right == "Clear":
                return "Person ahead. Move slightly right."

            else:
                return "Proceed carefully."

        # Center is blocked
        elif center == "Blocked":

            if left == "Clear":
                return "Center path blocked. Move left."

            elif right == "Clear":
                return "Center path blocked. Move right."

            elif left == "Caution":
                return "Center blocked. Carefully move left."

            elif right == "Caution":
                return "Center blocked. Carefully move right."

            else:
                return "Stop. No safe path detected."

        return "Proceed carefully."
    
    def get_path_status(self, hazard_scores):

        status = {}

        for direction, score in hazard_scores.items():

            if score == 0:
                status[direction] = "Clear"

            elif score <= 3:
                status[direction] = "Caution"

            else:
                status[direction] = "Blocked"

        return status
        
    def summarize_categories(self, decisions):

        summary = {}

        for decision in decisions:

            category = decision["category"]

            if category not in summary:
                summary[category] = 0

            summary[category] += 1

        return summary
        
    def analyze(self, detected_objects):
        
        self.current_objects = detected_objects
        
        scene_summary = self.summarize_objects(detected_objects)

        print("\nScene Summary")
        print(scene_summary)

        decisions = []

        for obj in detected_objects:

            message = "No Action"
            priority = 0
            
            print(obj)
            
            name = obj["name"].lower()
            display_name = obj["name"].capitalize()
            
            if name in self.PEOPLE:
                category = "person"

            elif name in self.ANIMALS:
                category = "animal"

            elif name in self.VEHICLES:
                category = "vehicle"

            else:
                category = "object"

            direction = obj["direction"].strip().lower()
            distance = obj["distance"].strip().lower()
            motion = obj["motion"]

            horizontal = "unknown"
            depth = "unknown"

            if isinstance(motion, dict):
                horizontal = motion.get("horizontal", "").strip().lower()
                depth = motion.get("depth", "").strip().lower()

            print(f"Direction : {direction}")
            print(f"Distance  : {distance}")
            print(f"Horizontal: {horizontal}")
            print(f"Depth     : {depth}")
            print(f"Category  : {category}")

            print(repr(direction))
            print(repr(distance))

            # Rule 1
            if direction == "center" and distance == "very near":
                
                if depth == "approaching":
                    message = f"{display_name} rapidly approaching ahead."
                    priority = 15
                    
                elif depth == "moving away":
                    message = f"{display_name} moving away."
                    priority = 5

                else:
                    message = f"{display_name} blocking your path."
                    priority = 10

            # Rule 2
            elif direction == "center" and distance == "near":
                
                if depth == "approaching":
                    message = f"{display_name} approaching ahead."
                    priority = 9
                    
                elif depth == "moving away":
                    message = f"{display_name} moving away."
                    priority = 4    

                else:
                    message = f"{display_name} ahead."
                    priority = 8
            
            # Rule 3
            elif direction == "left" and distance == "very near":

                if depth == "approaching":
                    message = f"{display_name} approaching from your left."
                    priority = 7
                    
                elif depth == "moving away":
                    message = f"{display_name} moving away on your left."
                    priority = 3

                else:
                    message = f"{display_name} very close on your left."
                    priority = 6


            # Rule 4
            elif direction == "right" and distance == "very near":

                if depth == "approaching":
                    message = f"{display_name} approaching from your right."
                    priority = 7
                    
                elif depth == "moving away":
                    message = f"{display_name} moving away on your right."
                    priority = 3

                else:
                    message = f"{display_name} very close on your right."
                    priority = 6
                    
            decisions.append({
                "id": obj["id"],
                "name": obj["name"],
                "category": category,
                "message": message,
                "priority": priority
            })

        # Select the highest priority decision
        if len(decisions) == 0:
            return None
        
        print("\n===== ALL DECISIONS =====")
        
        for d in decisions:
            print(d)
            
        print("=========================\n")
        
        category_summary = self.summarize_categories(decisions)
        print("Category Summary")
        print(category_summary)
        
        scene_layout = self.analyze_scene_layout(detected_objects)
        print("\nScene Layout")
        print(scene_layout)
        
        safe_direction = self.find_safe_direction(scene_layout)

        hazard_scores = self.calculate_hazard_score(decisions)
        print("\nHazard Scores")
        print(hazard_scores)

        instruction = self.generate_navigation_instruction(hazard_scores)
        print("\nNavigation Instruction")
        print(instruction)
        
        path_status = self.get_path_status(hazard_scores)
        print("\nPath Status")
        print(path_status)

        safe_direction = self.get_safest_direction(hazard_scores)
        print(f"\nSafest Direction (Hazard Based): {safe_direction.capitalize()}")
        
        best_decision = max(decisions, key=lambda x: x["priority"])
        
        best_decision["hazard_scores"] = hazard_scores
        best_decision["path_status"] = path_status
        best_decision["navigation"] = instruction
        best_decision["scene_summary"] = scene_summary
        best_decision["scene_layout"] = scene_layout
        best_decision["category_summary"] = category_summary
        
        return best_decision
