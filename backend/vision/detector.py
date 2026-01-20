import cv2
import numpy as np
from ultralytics import YOLO
import base64
from io import BytesIO
from PIL import Image
import os

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        """Initialize the YOLO object detector"""
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the YOLO model"""
        try:
            # Check if model exists in current directory or backend directory
            if os.path.exists(self.model_path):
                model_file = self.model_path
            elif os.path.exists(f"../{self.model_path}"):
                model_file = f"../{self.model_path}"
            else:
                # If model doesn't exist, YOLO will download it
                model_file = self.model_path
            
            self.model = YOLO(model_file)
            print(f"YOLO model loaded successfully from {model_file}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise e
    
    def decode_base64_image(self, base64_string):
        """Decode base64 string to OpenCV image"""
        try:
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(BytesIO(image_data))
            
            # Convert PIL to OpenCV format (BGR)
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
        except Exception as e:
            print(f"Error decoding base64 image: {e}")
            return None
    
    def detect_objects(self, base64_image):
        """Detect objects in base64 encoded image"""
        if not self.model:
            return {"error": "Model not loaded"}
        
        # Decode base64 image
        image = self.decode_base64_image(base64_image)
        if image is None:
            return {"error": "Failed to decode image"}
        
        try:
            # Run YOLO detection
            results = self.model(image)
            
            # Process results
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        # Only include detections with confidence > 0.5
                        if confidence > 0.5:
                            detection = {
                                "class": class_name,
                                "confidence": round(confidence, 3),
                                "bbox": {
                                    "x1": int(x1),
                                    "y1": int(y1),
                                    "x2": int(x2),
                                    "y2": int(y2)
                                }
                            }
                            detections.append(detection)
            
            return {
                "success": True,
                "detections": detections,
                "count": len(detections)
            }
            
        except Exception as e:
            print(f"Error during object detection: {e}")
            return {"error": f"Detection failed: {str(e)}"}
    
    def get_detection_summary(self, detections):
        """Generate a summary of detected objects"""
        if not detections:
            return "No objects detected"
        
        # Count objects by class
        object_counts = {}
        for detection in detections:
            class_name = detection["class"]
            object_counts[class_name] = object_counts.get(class_name, 0) + 1
        
        # Create summary
        summary_parts = []
        for obj_class, count in object_counts.items():
            if count == 1:
                summary_parts.append(f"1 {obj_class}")
            else:
                summary_parts.append(f"{count} {obj_class}s")
        
        return f"Detected: {', '.join(summary_parts)}"