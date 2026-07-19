import cv2

class VisionUI:

    def draw_warning_panel(self, frame, warning):

        if warning is None:
            return frame

        cv2.rectangle(
            frame,
            (10, 50),
            (340, 170),
            (40, 40, 40),
            -1
        )

        cv2.putText(
            frame,
            "CURRENT WARNING",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            warning["message"],
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Distance : {warning['distance']}",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 255, 200),
            1
        )

        cv2.putText(
            frame,
            f"Direction : {warning['direction']}",
            (20, 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 255, 200),
            1)
        
        return frame 
    
    def draw_object_labels(self, frame, detected_objects):

        for obj in detected_objects:

            x1 = obj["x1"]
            y1 = obj["y1"]

            # ---------- Label Text ----------
            title = obj["name"].capitalize()
            confidence = obj["confidence"]

            if confidence >= 0.85:
                confidence_color = (0, 255, 0)      # Green

            elif confidence >= 0.65:
                confidence_color = (0, 255, 255)    # Yellow

            elif confidence >= 0.50:
                confidence_color = (0, 165, 255)    # Orange

            else:
                confidence_color = (0, 0, 255)      # Red

            info = f"{obj['distance'].title()} • {obj['direction'].title()}"
            confidence_text = f"{int(confidence * 100)}%"   
                     
            critical = {
                "person",
                "bicycle",
                "motorcycle",
                "car",
                "bus",
                "truck",
                "train"
            }

            obstacles = {
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

            name = obj["name"].lower()

            if name in critical:
                border_color = (0, 0, 255)      # Red

            elif name in obstacles:
                border_color = (0, 165, 255)    # Orange

            else:
                border_color = (255, 0, 0)      # Blue

            # ---------- Box Size ----------
            box_width = 220
            box_height = 45

            # Draw above the object
            box_x = x1
            box_y = y1 - box_height - 5
            
            # Reserved area for warning panel
            WARNING_X = 10
            WARNING_Y = 50
            WARNING_WIDTH = 340
            WARNING_HEIGHT = 170

            label_right = box_x + box_width
            label_bottom = box_y + box_height

            overlaps_warning = (
                box_x < WARNING_X + WARNING_WIDTH and
                label_right > WARNING_X and
                box_y < WARNING_Y + WARNING_HEIGHT and
                label_bottom > WARNING_Y
            )

            # If label overlaps warning panel, move it below the object
            if overlaps_warning:
                box_x = WARNING_X + WARNING_WIDTH + 10

            # If object is near top, draw below it instead
            if box_y < 5:
                box_y = y1 + 5

            # ---------- Background ----------
            cv2.rectangle(
                frame,
                (box_x, box_y),
                (box_x + box_width, box_y + box_height),
                border_color,
                2
            )

            # ---------- Border ----------
            cv2.rectangle(
                frame,
                (box_x, box_y),
                (box_x + box_width, box_y + box_height),
                (255, 255, 255),
                1
            )

            # ---------- Object Name ----------
            cv2.putText(
                frame,
                title,
                (box_x + 8, box_y + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            # ---------- Information ----------
            cv2.putText(
                frame,
                info,
                (box_x + 8, box_y + 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (220, 220, 220),
                1
            )

            cv2.putText(
                frame,
                confidence_text,
                (box_x + 125, box_y + 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                confidence_color,
                1
            )

        return frame