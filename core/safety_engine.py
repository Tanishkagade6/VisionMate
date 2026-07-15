class SafetyEngine:
    """
    Decides whether a detected object
    requires a warning.
    """

    def analyze(self, categorized_objects):

        warnings = []

        for obj in categorized_objects["critical"]:

           if obj["direction"] == "center":
               
               warnings.append({
                    "priority": 2,
                    "message": f"{obj['name'].capitalize()} ahead."
                })

           else:
               warnings.append({"priority": 1,
                    "message": f"{obj['name'].capitalize()} on your {obj['direction']}."
                    })

        for obj in categorized_objects["obstacles"]:

            if obj["direction"] == "center":

                warnings.append({
                    "priority": 3,
                    "message": f"Obstacle ahead: {obj['name']}."
                })
                
        warnings.sort(key=lambda warning: warning["priority"],reverse=True)
        
        return warnings