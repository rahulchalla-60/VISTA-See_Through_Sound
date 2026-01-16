import numpy as np
from supervision.tracker.byte_tracker import ByteTracker
from supervision.detection.core import Detections


class ObjectTracker:
    def __init__(self):
        """
        Initializes ByteTrack tracker.
        """
        self.tracker = ByteTracker(
            track_thresh=0.25,
            track_buffer=30,
            match_thresh=0.8,
            frame_rate=30
        )

    def update(self, detections: list):
        """
        Converts YOLO detections to ByteTrack format and assigns IDs.

        Args:
            detections (list): Output from YOLODetector.detect()

        Returns:
            List[dict]: tracked objects with unique IDs
        """

        if len(detections) == 0:
            return []

        boxes = []
        scores = []
        class_ids = []

        for det in detections:
            boxes.append(det["bbox"])
            scores.append(det["confidence"])
            class_ids.append(det["class_id"])

        boxes = np.array(boxes, dtype=np.float32)
        scores = np.array(scores, dtype=np.float32)
        class_ids = np.array(class_ids, dtype=np.int32)

        # Create Supervision Detections object
        sv_detections = Detections(
            xyxy=boxes,
            confidence=scores,
            class_id=class_ids
        )

        # Run ByteTrack
        tracked = self.tracker.update_with_detections(sv_detections)

        tracked_objects = []

        for i in range(len(tracked)):
            track_id = int(tracked.tracker_id[i])

            x1, y1, x2, y2 = map(int, tracked.xyxy[i])

            # Get label from original detections
            class_id = int(tracked.class_id[i])
            label = next((det["label"] for det in detections if det["class_id"] == class_id), None)

            tracked_objects.append({
                "track_id": track_id,
                "bbox": [x1, y1, x2, y2],
                "class_id": class_id,
                "label": label
            })

        return tracked_objects
