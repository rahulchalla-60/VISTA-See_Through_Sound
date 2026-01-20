import cv2
import base64
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import numpy as np

class ObjectDetector:
    def __init__(self):
        print("Loading YOLO AI model...")
        self.model = YOLO('yolov8n.pt')  # This will download if not present
        print("AI model loaded!")
    
    def detect_objects(self, base64_image):
        # Convert base64 to image
        image = self._base64_to_image(base64_image)
        if image is None:
            return {"error": "Could not read image"}
        
        # Find objects using AI
        results = self.model(image)
        
        # Get the objects we found
        objects_found = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    # Get object info
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    object_name = self.model.names[class_id]
                    
                    # Only keep objects we're confident about
                    if confidence > 0.5:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        objects_found.append({
                            "name": object_name,
                            "confidence": round(confidence, 2),
                            "location": {
                                "x1": int(x1), "y1": int(y1),
                                "x2": int(x2), "y2": int(y2)
                            }
                        })
        
        return {
            "success": True,
            "objects": objects_found,
            "count": len(objects_found)
        }
    
    def _base64_to_image(self, base64_string):
        try:
            # Decode the base64 string
            image_data = base64.b64decode(base64_string)
            pil_image = Image.open(BytesIO(image_data))
            # Convert to format OpenCV can use
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return opencv_image
        except:
            return None
    
    def get_summary(self, objects):
        if not objects:
            return "No objects detected"
        
        # Count each type of object
        counts = {}
        for obj in objects:
            name = obj["name"]
            counts[name] = counts.get(name, 0) + 1
        
        # Make a simple sentence
        parts = []
        for name, count in counts.items():
            if count == 1:
                parts.append(f"1 {name}")
            else:
                parts.append(f"{count} {name}s")
        
        return f"I see: {', '.join(parts)}"