import cv2

from nodes.camera_node import CameraNode
from nodes.detection_node import DetectionNode
from nodes.spatial_analysis_node import SpatialAnalysis

def main():
    print("Starting Vision Assistant System...")
    print("Press 'q' to quit")
    print("-" * 40)
    
    # Initialize components
    camera = CameraNode()
    detector = DetectionNode(model="yolov8n.pt", conf=0.5)
    spatial = SpatialAnalysis()
    
    spoken_ids = set()  # to avoid repeated announcements

    for frame_data in camera.stream():
        frame = frame_data["frame"]  # Extract frame from dictionary
        frame_height, frame_width = frame.shape[:2]

        # Get detections using the DetectionNode class
        detections = detector.detect(frame)

        annotated_frame = frame.copy()

        for det in detections:
            box = det["box"]
            label = det["label"]
            track_id = det["id"]
            conf = det["conf"]

            # Spatial analysis
            position = spatial.classify_position(box, frame_width)
            distance = spatial.estimate_distance(box)

            det["position"] = position
            det["distance"] = distance

            # 🔊 Announce only once per unique object
            if track_id not in spoken_ids:
                announcement = f"{label} on your {position}"
                if distance:
                    announcement += f", distance {distance} units"
                print(f"SPEAK: {announcement}")
                spoken_ids.add(track_id)

            # Draw bounding box and info
            x1, y1, x2, y2 = box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Create display text
            display_text = f"{label} ID:{track_id} {position}"
            if distance:
                display_text += f" {distance}"
            
            cv2.putText(
                annotated_frame,
                display_text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        cv2.imshow("Vision Assistant - Press 'q' to quit", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Vision Assistant stopped by user")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
