from ultralytics import YOLO
import cv2
import time
from vision.direction import DirectionEngine
from vision.distance import DistanceEngine
from core.warning_manager import WarningManager
from voice.speaker import Speaker
from vision.object_filter import ObjectFilter
from core.safety_engine import SafetyEngine
from vision.ui import VisionUI
from vision.tracker_memory import TrackerMemory
from vision.motion_engine import MotionEngine
from core.decision_engine import DecisionEngine
from scene.describer import SceneDescriber

class VisionDetector:
  
    def __init__(self, model_name= "yolov8s.pt"):
        print("[INFO] Loading YOLO model...")
        
        self.model = YOLO(model_name)
        self.direction_engine = DirectionEngine()
        self.distance_engine = DistanceEngine()
        self.warning_manager = WarningManager()
        self.speaker = Speaker()
        self.object_filter = ObjectFilter()
        self.safety_engine = SafetyEngine()
        self.ui = VisionUI()
        self.tracker_memory = TrackerMemory()
        self.motion_engine = MotionEngine()
        self.decision_engine = DecisionEngine()
        self.scene_describer = SceneDescriber()
        
        self.last_warning = None
        self.last_warning_time = 0
        self.WARNING_DISPLAY_TIME = 1.0
        
        print("[SUCCESS] Vision Engine Ready!")
        
    def extract_objects(self, results):
            
        detected_objects = []

        for box in results[0].boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # Get tracking ID
            if box.id is not None:
                track_id = int(box.id[0])
            else:
                track_id = -1

            object_name = self.model.names[class_id]
            
            x1, y1, x2, y2 = map(float, box.xyxy[0])

            box_height = y2 - y1
            center_x = (x1 + x2) / 2
            frame_width = results[0].orig_shape[1]
            frame_height = results[0].orig_shape[0]

            direction = self.direction_engine.get_direction(center_x,frame_width)
            distance = self.distance_engine.estimate(box_height,frame_height)
            previous = self.tracker_memory.update(track_id,center_x,box_height)
            motion = self.motion_engine.analyze(previous,center_x,box_height)
            
            detected_objects.append({
                "id": track_id,
                "name": object_name,
                "confidence": round(confidence, 2),
                "motion": motion,
                "center_x": float(center_x),
                "direction": direction,
                "distance": distance,
                "box_height": float(box_height),
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                })

        for obj in detected_objects:
            print(f"ID:{obj['id']} | "
                f"{obj['name']} | "
                f"{obj['direction']} | "
                f"{obj['distance']} |"
                f"{obj['motion']} ")
                
        return detected_objects
    
    def process_frame(self, frame):
        
        try:
            start = time.time()
            
            results = self.model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                conf = 0.5,
                imgsz = 960,
                device=0,
                verbose=False
            )
            inference_time = (time.time() - start) * 1000
            print(f"Inference Time: {inference_time:.2f} ms")
            
        except Exception as e:
            print(e)
            return [], frame

        detected_objects = self.extract_objects(results)
        decision = self.decision_engine.analyze(detected_objects)
        scene_description = self.scene_describer.describe_scene(detected_objects)
        
        print("\n========== Scene Description ==========")
        print(scene_description)
        
        if decision:
            self.speaker.speak_async(decision["navigation"])
        
        annotated_frame = results[0].plot(labels=False)

        return detected_objects,decision,scene_description, annotated_frame
            
    def start_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return
        
        prev_time = time.time()
        while True:
            success, frame = cap.read()
            
            current_time = time.time()

            fps = 1 / (current_time - prev_time)

            prev_time = current_time
            
            if not success:
                break
            
            detected_objects,decision,scene_description, annotated_frame = self.process_frame(frame)
            
            print(decision)
            print(scene_description)

            categorized_objects = self.object_filter.filter_objects(detected_objects)

            warnings = self.safety_engine.analyze(categorized_objects)
            warning = self.warning_manager.get_warning(warnings)

            if warning:
                self.last_warning = warning
                self.last_warning_time = time.time()
                self.speaker.speak_async(warning["message"])
                
            if (self.last_warning is not None
                and time.time() - self.last_warning_time < self.WARNING_DISPLAY_TIME):
                
                annotated_frame = self.ui.draw_warning_panel(annotated_frame,self.last_warning)
                annotated_frame = self.ui.draw_object_labels(annotated_frame,detected_objects) 
                             
            cv2.imshow("VisionMate", annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows() 