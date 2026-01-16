import cv2
import numpy as np
from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.4):
        """
        Loads YOLOv8 model.
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame: np.ndarray):
        """
        Runs YOLO inference on a frame.

        Args:
            frame (np.ndarray): BGR image (OpenCV frame)

        Returns:
            List[dict]: detections with bbox, label, confidence
        """

        # YOLO expects RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.model(rgb_frame, conf=self.conf_threshold, verbose=False)[0]

        detections = []

        if results.boxes is None:
            return detections

        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for box, score, cls_id in zip(boxes, scores, class_ids):
            x1, y1, x2, y2 = map(int, box)

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": float(score),
                "class_id": cls_id,
                "label": self.model.names[cls_id]
            })

        return detections
