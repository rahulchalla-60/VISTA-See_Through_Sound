import cv2
import pyttsx3
import time
import threading
from queue import Queue
import socketio
import numpy as np
from ultralytics import YOLO
from yolox.tracker.byte_tracker import BYTETracker
import uvicorn
import asyncio

class VisionAssistant:
    def __init__(self):
        # Socket.IO Detection System
        self.sio = socketio.AsyncServer(cors_allowed_origins="*")
        self.app = socketio.ASGIApp(self.sio)
        self.detection_model = YOLO("yolo11n.pt")
        self.tracker = BYTETracker(
            track_thresh=0.5,
            match_thresh=0.8,
            track_buffer=30
        )
        
        # TTS for voice announcements
        self.engine = None
        self.speech_queue = Queue()
        self.is_speaking = False
        self.spoken_ids = set()
        
        # Control flags
        self.running = False
        self.web_mode = False  # Flag for web interface mode
        
        self._setup_tts()
        self._start_speech_worker()
        self._setup_socketio_handlers()
    
    def _setup_socketio_handlers(self):
        """Setup Socket.IO event handlers for web interface"""
        
        @self.sio.event
        async def connect(sid, environ):
            print(f"🌐 Web client connected: {sid}")
            self.web_mode = True
        
        @self.sio.event
        async def disconnect(sid):
            print(f"🌐 Web client disconnected: {sid}")
            self.web_mode = False
        
        @self.sio.event
        async def frame(sid, data):
            """Process frame from web interface"""
            try:
                # Convert blob → image
                np_img = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                
                if frame is None:
                    return
                
                # YOLO detection
                results = self.detection_model(frame, conf=0.5, verbose=False)[0]
                
                detections = []
                class_names = []
                
                for box in results.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = results.names.get(cls, "unknown")
                    
                    detections.append([x1, y1, x2 - x1, y2 - y1, conf, cls])
                    class_names.append(class_name)
                
                # ByteTrack expects numpy array
                dets = np.array(detections) if detections else np.empty((0, 6))
                
                tracks = self.tracker.update(
                    dets[:, :5] if len(dets) else np.empty((0, 5)),
                    frame.shape[:2],
                    frame.shape[:2]
                )
                
                tracked_objects = []
                for i, t in enumerate(tracks):
                    x1, y1, x2, y2 = map(int, t.tlbr)
                    
                    # Match track with detection to get class name
                    class_name = "unknown"
                    confidence = 0.0
                    
                    if i < len(class_names):
                        class_name = class_names[i]
                    if i < len(detections):
                        confidence = detections[i][4]
                    
                    tracked_objects.append({
                        "track_id": int(t.track_id),
                        "bbox": [x1, y1, x2, y2],
                        "class_name": class_name,
                        "confidence": confidence
                    })
                
                # Send detections to frontend
                await self.sio.emit("detections", tracked_objects)
                
                # Optional: Announce objects for accessibility
                if tracked_objects and not self.is_speaking:
                    self._announce_web_detections(tracked_objects, frame.shape)
                
            except Exception as e:
                print(f"❌ Error processing web frame: {e}")
    
    def _announce_web_detections(self, tracked_objects, frame_shape):
        """Announce detected objects for web interface accessibility"""
        frame_height, frame_width = frame_shape[:2]
        
        for obj in tracked_objects:
            track_id = obj["track_id"]
            class_name = obj["class_name"]
            bbox = obj["bbox"]
            
            # Skip if already announced
            if track_id in self.spoken_ids:
                continue
            
            # Determine position
            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) / 2
            
            if center_x < frame_width * 0.33:
                position = "left"
            elif center_x > frame_width * 0.66:
                position = "right"
            else:
                position = "center"
            
            # Estimate distance (simple heuristic)
            box_height = y2 - y1
            distance = max(1.0, 100.0 / (box_height + 1))  # Simple distance estimation
            
            announcement = f"{class_name} detected on your {position}, approximately {distance:.1f} meters away"
            
            if not self.speech_queue.full():
                self.speech_queue.put(announcement)
                self.spoken_ids.add(track_id)
    
    def _setup_tts(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            print("✅ TTS engine initialized")
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
    
    def _start_speech_worker(self):
        """Start background speech worker"""
        speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        speech_thread.start()
    
    def _speech_worker(self):
        """Background thread for speech queue"""
        while True:
            try:
                announcement = self.speech_queue.get(timeout=1)
                if announcement is None:
                    break
                
                self.is_speaking = True
                print(f"🔊 Speech: {announcement}")
                
                # Use Windows SAPI for compatibility
                import os
                clean_announcement = announcement.replace("'", "''")
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 0; $synth.Volume = 100; $synth.Speak(\'{clean_announcement}\')"'
                os.system(cmd)
                
                self.is_speaking = False
                self.speech_queue.task_done()
                
            except:
                self.is_speaking = False
                continue
    
    def run_web_server(self, host="0.0.0.0", port=8000):
        """Run web server for frontend connection"""
        print(f"🌐 Starting Vision Assistant Web Server on {host}:{port}")
        print("🔗 Connect your frontend to this server")
        print("Press Ctrl+C to stop")
        
        try:
            uvicorn.run(self.app, host=host, port=port, log_level="info")
        except KeyboardInterrupt:
            print("\n🛑 Web server stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the vision assistant"""
        self.running = False
        
        # Stop speech thread
        self.speech_queue.put(None)
        
        print("✅ Vision Assistant stopped")


def main():
    """Main function for Vision Assistant"""
    import sys
    
    assistant = VisionAssistant()
    
    # Run web server mode for frontend connection
    try:
        assistant.run_web_server()
    except KeyboardInterrupt:
        print("\n🛑 Web server interrupted by user")
        assistant.stop()


if __name__ == "__main__":
    main()
