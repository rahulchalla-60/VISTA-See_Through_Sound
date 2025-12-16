import cv2
import pyttsx3
import time
import threading
from queue import Queue

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
    
    # Initialize text-to-speech engine with better settings
    try:
        engine = pyttsx3.init()
        # Set speech rate (slower = more clear)
        engine.setProperty('rate', 150)
        # Set volume (0.0 to 1.0)
        engine.setProperty('volume', 0.9)
        print("TTS engine initialized successfully")
    except Exception as e:
        print(f"TTS initialization failed: {e}")
        engine = None
    
    spoken_ids = set()  # to avoid repeated announcements
    
    # Speech queue system to prevent overlapping
    speech_queue = Queue()
    is_speaking = False
    
    def speech_worker():
        """Background thread to handle speech queue"""
        nonlocal is_speaking
        while True:
            try:
                announcement = speech_queue.get(timeout=1)
                if announcement is None:  # Shutdown signal
                    break
                    
                is_speaking = True
                print(f"🔊 Speaking: {announcement}")
                
                # Use Windows SAPI TTS (synchronous to prevent overlap)
                import os
                clean_announcement = announcement.replace("'", "''")
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 0; $synth.Volume = 100; $synth.Speak(\'{clean_announcement}\')"'
                os.system(cmd)
                
                is_speaking = False
                print("✅ Speech completed")
                speech_queue.task_done()
                
            except:
                is_speaking = False
                continue
    
    # Start speech worker thread
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()

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

            #  Announce only once per unique object
            if track_id not in spoken_ids:
                # Create full announcement with spatial information
                announcement = f"{label} on your {position}"
                if distance:
                    announcement += f", distance {distance} units"
                
                print(f"QUEUING: {announcement}")  # Debug print
                
                # Add to speech queue (prevents overlapping)
                if not speech_queue.full():
                    speech_queue.put(announcement)
                    print("📝 Added to speech queue")
                else:
                    print("⚠️ Speech queue full, skipping")
                
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

        # Show video frame (MOVED OUTSIDE the detection loop)
        cv2.imshow("Vision Assistant - Press 'q' to quit", annotated_frame)

        # Check for quit key (MOVED OUTSIDE the detection loop)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Vision Assistant stopped by user")
            break

    # Cleanup
    speech_queue.put(None)  # Signal speech thread to stop
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
