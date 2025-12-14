import cv2
from ultralytics import YOLO

class DetectionNode:
    def __init__(self, model="yolov8n.pt", conf=0.5):
        """
        Initialize YOLO detection with object tracking
        """
        print("Loading YOLO model...")
        self.model = YOLO(model)
        self.conf = conf
        print("YOLO model loaded successfully!")
    
    def detect(self, frame):
        """
        Detect objects in frame and return detection data
        Returns list of detections with format expected by app.py
        """
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=self.conf
        )
        
        detections = []
        
        for r in results:
            if r.boxes is None or r.boxes.id is None:
                continue
                
            boxes = r.boxes.xyxy.cpu().numpy()
            ids = r.boxes.id.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()
            confidences = r.boxes.conf.cpu().numpy()
            
            for box, track_id, cls, conf in zip(boxes, ids, classes, confidences):
                x1, y1, x2, y2 = map(int, box)
                label = self.model.names[int(cls)]
                
                detection = {
                    "label": label,
                    "conf": float(conf),
                    "box": (x1, y1, x2, y2),
                    "id": int(track_id)
                }
                
                detections.append(detection)
        
        return detections

# Standalone script functionality (for testing)
if __name__ == "__main__":
    from camera_node import CameraNode
    
    print("Testing DetectionNode as standalone script...")
    print("Press 'q' to quit")
    
    camera = CameraNode()
    detector = DetectionNode()
    spoken_ids = set()
    
    for frame_data in camera.stream():
        frame = frame_data["frame"]
        
        # Get detections
        detections = detector.detect(frame)
        
        # Process detections
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = det["label"]
            track_id = det["id"]
            conf = det["conf"]
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated_frame,
                f"{label} ID:{track_id} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            # Speak only once per object
            if track_id not in spoken_ids:
                print(f"SPEAK: {label} detected")
                spoken_ids.add(track_id)
        
        cv2.imshow("YOLO Detection Test - Press 'q' to quit", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
