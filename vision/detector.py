from ultralytics import YOLO
import cv2
from vision.object_filter import ObjectFilter
from vision.direction import DirectionEngine
from core.safety_engine import SafetyEngine

class VisionDetector:
  
    def __init__(self, model_name= "yolov8n.pt"):
        print("[INFO] Loading YOLO model...")
        
        self.model = YOLO(model_name)
        self.object_filter = ObjectFilter()
        self.direction_engine = DirectionEngine()
        self.safety_engine = SafetyEngine()
        
        print("[SUCCESS] Vision Engine Ready!")
        
    def extract_objects(self, results):
            
        detected_objects = []

        for box in results[0].boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            object_name = self.model.names[class_id]
            
            x1, y1, x2, y2 = box.xyxy[0]
            center_x = (x1 + x2) / 2
            frame_width = 640

            direction = self.direction_engine.get_direction(center_x,frame_width)
            
            detected_objects.append({
                "name": object_name,
                "confidence": round(confidence, 2),
                "center_x": float(center_x),
                "direction": direction})

        return detected_objects
    
    def start_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return
        
        while True:
            success, frame = cap.read()
            
            if not success:
                break
            
            results = self.model(frame)
            
            detected_objects = self.extract_objects(results)
            categorized_objects = self.object_filter.filter_objects(detected_objects)
            
            warnings = self.safety_engine.analyze(categorized_objects)

            print("\n==============================")
            print("VisionMate Warnings")
            print("==============================")

            if warnings:
                for warning in warnings:
                    print("⚠️", warning["message"])
            else:
                print("✅ No immediate danger detected.")
            
            annotated_frame = results[0].plot()
            
            cv2.imshow("VisionMate", annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows() 
        
        
        
        