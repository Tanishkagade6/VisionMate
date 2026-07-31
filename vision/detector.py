from ultralytics import YOLO
import cv2
import time
import torch
from config import VIDEO_URL
from vision.direction import DirectionEngine
from vision.distance import DistanceEngine
from core.warning_manager import WarningManager
from core.speaker_manager import speaker
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
        
        print("[INFO] Loading YOLO model...")

        self.model = YOLO(model_name)
        self.model.to("cuda")
        self.direction_engine = DirectionEngine()
        self.distance_engine = DistanceEngine()
        self.warning_manager = WarningManager()
        
        self.speaker = speaker
        self.object_filter = ObjectFilter()
        self.safety_engine = SafetyEngine()
        self.ui = VisionUI()
        self.tracker_memory = TrackerMemory()
        self.motion_engine = MotionEngine()
        self.decision_engine = DecisionEngine()
        self.scene_describer = SceneDescriber()
        
        self.last_navigation = ""
        self.last_navigation_time = 0
        
        self.last_scene_description = ""
        self.last_scene_time = 0

        self.SCENE_UPDATE_INTERVAL = 5
        
        # Navigation control
        self.running = False
        self.frame_callback = None
        self.camera = None
        
        self.last_warning = None
        self.last_warning_time = 0
        self.WARNING_DISPLAY_TIME = 1.0
        
        print("[SUCCESS] Vision Engine Ready!")
        
    def extract_objects(self, results):
            
        detected_objects = []

        for box in results[0].boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            if confidence < 0.60:
                continue

            # Get tracking ID
            if box.id is not None:
                track_id = int(box.id[0])
            else:
                track_id = -1

            object_name = self.model.names[class_id]
            if object_name == "dining table":
                object_name = "table"
                
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

        # for obj in detected_objects:
        #     print(f"ID:{obj['id']} | "
        #         f"{obj['name']} | "
        #         f"{obj['direction']} | "
        #         f"{obj['distance']} |"
        #         f"{obj['motion']} ")
                
        return detected_objects
    
    def process_frame(self, frame):

        try:
            start = time.time()
            
            # results = self.model(frame, conf=0.5)
            frame = cv2.resize(frame, (640,480))
            t1 = time.time()
            
            results = self.model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                conf=0.5,
                imgsz=416,
                device=0,
                verbose=False
            )
            t2 = time.time()
            
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls]

                if class_name == "dining table":
                    class_name = "table"
        
        except Exception as e:
            print(e)
            return [], None, "", frame

        detected_objects = self.extract_objects(results)
        t3 = time.time()
        
        # for obj in detected_objects:
            # print(obj["name"], obj["confidence"])

        # Decision Engine
        decision = self.decision_engine.analyze(detected_objects)
        t4 = time.time()

        # Update scene description only every 3 seconds
        current_time = time.time()

        if current_time - self.last_scene_time > self.SCENE_UPDATE_INTERVAL:
            self.last_scene_description = self.scene_describer.describe_scene(detected_objects)
            self.last_scene_time = current_time

        scene_description = self.last_scene_description

        # Speak only when navigation changes
        if decision:

            nav = decision["navigation"]

            current_time = time.time()

            if (nav != self.last_navigation or current_time - self.last_navigation_time > 8):
                self.speaker.speak_async(nav)
                self.last_navigation = nav
                self.last_navigation_time = current_time

        annotated_frame = results[0].plot(labels=False)
        t5 = time.time()
        
        end = time.time()

        return detected_objects, decision, scene_description, annotated_frame
    
    def reset(self):
        """Call when starting a fresh navigation session."""
        self.last_navigation = ""
        self.last_navigation_time = 0
        self.last_scene_description = ""
        self.last_scene_time = 0
        self.last_warning = None
        self.last_warning_time = 0
            
    def start_camera(self):
        
        if self.running:
            return

        self.camera = cv2.VideoCapture(VIDEO_URL)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        
        if not self.camera.isOpened():
            print("[ERROR] Could not open webcam.")
            return
        
        self.running = True
        
        print("[INFO] Camera Started")
        
        prev_time = time.time()
        
        cv2.namedWindow("VisionMate",cv2.WINDOW_NORMAL)

        cv2.resizeWindow("VisionMate",960,540)
        
        while self.running:
                        
            for _ in range(2):
                self.camera.grab()
                
            success, frame = self.camera.read()
            
            if not success:
                print("Failed to read frame")
                break
            
            current_time = time.time()

            fps = 1 / (current_time - prev_time)

            prev_time = current_time
            
            if not success:
                break
            
            detected_objects,decision,scene_description, annotated_frame = self.process_frame(frame)
           
            categorized_objects = self.object_filter.filter_objects(detected_objects)

            warnings = self.safety_engine.analyze(categorized_objects)
            warning = self.warning_manager.get_warning(warnings)

            if warning:
                self.last_warning = warning
                self.last_warning_time = time.time()
                # self.speaker.speak_async(warning["message"])
                
            if (self.last_warning is not None
                and time.time() - self.last_warning_time < self.WARNING_DISPLAY_TIME):
                
                annotated_frame = self.ui.draw_warning_panel(annotated_frame,self.last_warning)
                annotated_frame = self.ui.draw_object_labels(annotated_frame,detected_objects) 
            
            # import cv2 as cv  
            # cv2.namedWindow("VisionMate", cv2.WINDOW_NORMAL)
            # cv2.resizeWindow("VisionMate", 900, 500)
            
            display_frame = cv2.resize(annotated_frame, (960, 540))
            cv2.imshow("VisionMate", display_frame)
            # cv2.imshow("VisionMate", annotated_frame)          
                 
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_camera()
                break
            
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()

        self.running = False
            
    def stop_camera(self):

        print("[INFO] Stopping Navigation...")

        self.running = False

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()