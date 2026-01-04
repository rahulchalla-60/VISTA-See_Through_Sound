import numpy as np
from ultralytics import YOLO
from yolox.tracker.byte_tracker import BYTETracker


class VisionDetector:
    def __init__(self, model_path="yolo11n.pt"):
        self.model = YOLO(model_path)
        self.tracker = BYTETracker(
            track_thresh=0.5,
            match_thresh=0.8,
            track_buffer=30
        )

    def process(self, frame):
        detections = self._detect(frame)
        tracks = self._track(detections)
        return tracks

    def _detect(self, frame):
        results = self.model(frame, conf=0.5, verbose=False)[0]

        output = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            output.append({
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "confidence": conf,
                "class": results.names.get(cls, "unknown")
            })
        return output

    def _track(self, detections):
        if not detections:
            return []

        det_array = np.array([
            d["bbox"] + [d["confidence"]]
            for d in detections
        ])

        tracks = self.tracker.update(det_array)

        tracked = []
        for track, det in zip(tracks, detections):
            x, y, w, h = map(int, track.tlwh)
            tracked.append({
                "id": track.track_id,
                "bbox": [x, y, x + w, y + h],  # [x1, y1, x2, y2] format for frontend
                "class": det["class"],
                "confidence": det["confidence"]
            })
        return tracked
