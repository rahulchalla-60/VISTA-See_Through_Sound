import cv2
import time
from nodes.camera_node import CameraNode
from ultralytics import YOLO

class YoloDetector:
    def __init__(self, model="yolov8n.pt", conf=0.5):
        print("YOLO is loading...")
        self.model = YOLO(model)  # Actually load the YOLO model
        self.conf = conf
        print("YOLO loaded successfully!")
    def detect(self, frame):
        results = self.model(frame, conf=self.conf)
        detections = []
        annotated_frame = frame.copy()

        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = self.model.names[cls]

                    detections.append({
                        "label": label,
                        "conf": conf,
                        "box": (int(x1), int(y1), int(x2), int(y2))
                    })

                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f"{label} {conf:.2f}",
                                (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (0, 255, 0), 2)
        
        return annotated_frame, detections


class DetectionNode:
    """Integration class that connects camera and detection"""
    def __init__(self, cam_index=0, model="yolov8n.pt", conf=0.5, fps=5):
        self.camera = CameraNode(cam_index)
        self.detector = YoloDetector(model, conf)
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.previous_objects = set()  # Track previous detections
    
    def run_detection_stream(self):
        """Run live detection on camera stream"""
        print(f"Starting detection stream at {self.fps} FPS...")
        print("Press 'q' to quit")
        print("Will only print when objects appear/disappear")
        print("-" * 50)
        
        last_time = time.time()
        
        try:
            for frame_data in self.camera.stream():
                frame = frame_data["frame"]
                
                # Control frame rate
                current_time = time.time()
                if current_time - last_time < self.frame_delay:
                    continue
                last_time = current_time
                
                # Run detection on the frame
                annotated_frame, detections = self.detector.detect(frame)
                
                # Display results
                cv2.imshow('YOLO Detection - Press q to quit', annotated_frame)
                
                # Track object changes
                current_objects = set(det['label'] for det in detections)
                
                # Check for new objects
                new_objects = current_objects - self.previous_objects
                if new_objects:
                    print(f" NEW: {', '.join(new_objects)}")
                
                # Check for disappeared objects  
                disappeared_objects = self.previous_objects - current_objects
                if disappeared_objects:
                    print(f" GONE: {', '.join(disappeared_objects)}")
                
                # Show current count if objects present
                if detections and (new_objects or disappeared_objects):
                    print(f" Current: {len(detections)} objects - {', '.join(current_objects)}")
                    print("-" * 30)
                
                self.previous_objects = current_objects
                
        except Exception as e:
            print(f"Error during detection: {e}")
        finally:
            self.camera.release()
            cv2.destroyAllWindows()
