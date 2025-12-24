import cv2
import pyttsx3
import time
import threading
from queue import Queue

from nodes.camera_node import CameraNode
from integrated_vision_navigation import IntegratedVisionNavigation

class VisionAssistant:
    def __init__(self):
        # 🧩 NEW: Integrated vision + navigation system
        self.integrated_system = IntegratedVisionNavigation()
        self.camera = CameraNode()
        
        # Legacy TTS for compatibility
        self.engine = None
        self.speech_queue = Queue()
        self.is_speaking = False
        self.spoken_ids = set()
        
        # Control flags
        self.running = False
        self.navigation_active = False
        
        self._setup_tts()
        self._start_speech_worker()
    
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
        """Background thread for legacy speech queue"""
        while True:
            try:
                announcement = self.speech_queue.get(timeout=1)
                if announcement is None:
                    break
                
                self.is_speaking = True
                print(f"🔊 Legacy Speech: {announcement}")
                
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
    
    def start_navigation(self, start_coords, end_coords):
        """
        🗺️ Start integrated vision + navigation with obstacle detection
        """
        print(f"🚀 Starting INTEGRATED navigation from {start_coords} to {end_coords}")
        print("🔴 SAFETY MODE: Obstacle warnings will override navigation instructions")
        
        success = self.integrated_system.start_integrated_navigation(start_coords, end_coords)
        if success:
            self.navigation_active = True
            print("✅ Navigation started with obstacle detection")
        else:
            print("❌ Failed to start navigation")
        return success
    
    def stop_navigation(self):
        """Stop navigation system"""
        if self.navigation_active:
            self.integrated_system.stop_navigation()
            self.navigation_active = False
            print("🛑 Navigation stopped")
    
    def run(self):
        """
        🧩 MAIN INTEGRATION LOOP: Vision processing with safety priority
        """
        self.running = True
        print("=" * 60)
        print("🚀 VISION ASSISTANT WITH INTEGRATED NAVIGATION")
        print("=" * 60)
        print("🔴 SAFETY PRIORITY: Obstacle warnings override navigation")
        print("🗺️ Navigation: Provides turn-by-turn directions when safe")
        print("👁️ Vision: Detects and announces objects with spatial awareness")
        print("Press 'q' to quit, 'n' to toggle navigation mode")
        print("-" * 60)
        
        for frame_data in self.camera.stream():
            if not self.running:
                break
            
            frame = frame_data["frame"]
            
            if self.navigation_active:
                # 🧩 INTEGRATED MODE: Vision + Navigation with Safety Priority
                detections = self.integrated_system.process_vision_frame(frame)
                annotated_frame = self._draw_safety_detections(frame, detections)
                
                # Display mode indicator
                cv2.putText(annotated_frame, "NAVIGATION MODE - SAFETY PRIORITY", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
            else:
                # 🔍 DETECTION ONLY MODE: Legacy object detection
                detections = self.integrated_system.detection_node.detect(frame)
                annotated_frame = self._process_legacy_detections(frame, detections)
                
                # Display mode indicator
                cv2.putText(annotated_frame, "DETECTION ONLY MODE", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show frame
            cv2.imshow("Vision Assistant - 'q'=quit, 'n'=navigation", annotated_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Vision Assistant stopped by user")
                break
            elif key == ord('n'):
                self._toggle_navigation_mode()
        
        self.stop()
    
    def _toggle_navigation_mode(self):
        """Toggle between detection-only and navigation modes"""
        if self.navigation_active:
            self.stop_navigation()
        else:
            # Example coordinates - in real use, get from GPS or user input
            start_coords = (37.7749, -122.4194)  # San Francisco
            end_coords = (37.7849, -122.4094)    # Nearby location
            self.start_navigation(start_coords, end_coords)
    
    def _draw_safety_detections(self, frame, detections):
        """
        🔴 Draw detections with safety color coding for navigation mode
        """
        annotated_frame = frame.copy()
        
        for detection in detections:
            obj_id = detection['id']
            label = detection['label']
            box = detection['box']
            position = detection.get('position', 'unknown')
            distance = detection.get('distance', 0)
            
            # 🔴 SAFETY COLOR CODING
            if position == 'center' and distance < 3.0:  # DANGER_THRESHOLD
                color = (0, 0, 255)  # Red - DANGEROUS
                thickness = 4
                safety_status = "DANGER"
            elif distance < 3.0:
                color = (0, 255, 255)  # Yellow - CAUTION
                thickness = 3
                safety_status = "CAUTION"
            else:
                color = (0, 255, 0)  # Green - SAFE
                thickness = 2
                safety_status = "SAFE"
            
            # Draw detection box
            x1, y1, x2, y2 = box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Safety label
            safety_text = f"{label} ID:{obj_id} ({position}, {distance:.1f}m) [{safety_status}]"
            cv2.putText(annotated_frame, safety_text, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return annotated_frame
    
    def _process_legacy_detections(self, frame, detections):
        """
        👁️ Process detections in legacy mode (detection only, no navigation)
        """
        annotated_frame = frame.copy()
        frame_height, frame_width = frame.shape[:2]
        
        for detection in detections:
            obj_id = detection['id']
            label = detection['label']
            box = detection['box']
            conf = detection.get('conf', 0)
            
            # Spatial analysis
            position = self.integrated_system.spatial_analysis.classify_position(box, frame_width)
            distance = self.integrated_system.spatial_analysis.estimate_distance(box)
            
            # Announce only once per unique object (legacy behavior)
            if obj_id not in self.spoken_ids:
                announcement = f"{label} on your {position}"
                if distance:
                    announcement += f", distance {distance:.1f} meters"
                
                print(f"📝 QUEUING: {announcement}")
                
                if not self.speech_queue.full():
                    self.speech_queue.put(announcement)
                
                self.spoken_ids.add(obj_id)
            
            # Draw detection
            x1, y1, x2, y2 = box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            display_text = f"{label} ID:{obj_id} {position} {distance:.1f}m"
            cv2.putText(annotated_frame, display_text, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return annotated_frame
    
    def stop(self):
        """Stop the vision assistant"""
        self.running = False
        
        # Stop navigation if active
        if self.navigation_active:
            self.stop_navigation()
        
        # Stop speech thread
        self.speech_queue.put(None)
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        print("✅ Vision Assistant stopped")


def main():
    """Main function with integrated vision + navigation"""
    assistant = VisionAssistant()
    
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        assistant.stop()


if __name__ == "__main__":
    main()
