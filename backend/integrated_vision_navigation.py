"""
Integrated Vision + Navigation System
Combines YOLO detection with offline navigation, prioritizing obstacle safety.
"""

import time
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import existing components
from nodes.detection_node import DetectionNode
from nodes.spatial_analysis_node import SpatialAnalysisNode
from navigation.voice_navigation import VoiceNavigator
from navigation.navigate import get_instructions, calculate_distance
import pyttsx3


# Configuration Constants
DANGER_THRESHOLD = 3.0  # meters - configurable obstacle danger distance
NAVIGATION_INTERVAL = 5.0  # seconds between navigation instructions
OBSTACLE_CHECK_INTERVAL = 0.5  # seconds between obstacle checks


class InstructionType(Enum):
    OBSTACLE = "obstacle"
    NAVIGATION = "navigation"
    NONE = "none"


@dataclass
class SystemState:
    """Tracks the current state of spoken instructions"""
    last_obstacle_instruction: Optional[str] = None
    last_navigation_instruction: Optional[str] = None
    obstacle_active: bool = False
    navigation_active: bool = False
    last_obstacle_time: float = 0.0
    last_navigation_time: float = 0.0


class ObstacleDecisionEngine:
    """
    Analyzes detections and decides on obstacle avoidance instructions.
    PRIORITY: Obstacle safety always overrides navigation.
    """
    
    def __init__(self, danger_threshold: float = DANGER_THRESHOLD):
        self.danger_threshold = danger_threshold
        
    def analyze_obstacles(self, detections: List[Dict]) -> Optional[str]:
        """
        Analyze detections and return obstacle instruction if needed.
        
        Args:
            detections: List of detection dicts with spatial analysis
            
        Returns:
            Obstacle instruction string or None if safe
        """
        if not detections:
            return None
            
        # Find center obstacles within danger threshold
        center_obstacles = []
        left_clear = True
        right_clear = True
        
        for detection in detections:
            position = detection.get('position', 'unknown')
            distance = detection.get('distance', float('inf'))
            
            # Check if obstacle is dangerous
            if distance < self.danger_threshold:
                if position == 'center':
                    center_obstacles.append(detection)
                elif position == 'left':
                    left_clear = False
                elif position == 'right':
                    right_clear = False
        
        # If no center obstacles, path is clear
        if not center_obstacles:
            return None
            
        # 🔴 PRIORITY RULE: Center obstacle detected - decide avoidance
        if left_clear and right_clear:
            # Both sides clear - prefer right (standard traffic rule)
            return "Obstacle ahead. Move right."
        elif left_clear:
            return "Obstacle ahead. Move left."
        elif right_clear:
            return "Obstacle ahead. Move right."
        else:
            return "Obstacle ahead. Stop."


class NavigationController:
    """
    Manages OSRM navigation steps and timing.
    Only provides instructions when safe (no active obstacles).
    """
    
    def __init__(self, voice_navigator: VoiceNavigator):
        self.voice_nav = voice_navigator
        self.current_instructions = []
        self.instruction_index = 0
        self.destination_coords = None
        self.start_coords = None
        
    def start_navigation(self, start_coords: Tuple[float, float], 
                        end_coords: Tuple[float, float]):
        """Start navigation between coordinates"""
        self.start_coords = start_coords
        self.destination_coords = end_coords
        self.instruction_index = 0
        
        # Get navigation instructions from OSRM
        self.current_instructions = get_instructions(start_coords, end_coords)
        
        if not self.current_instructions or self.current_instructions[0] == "No route found":
            return False
            
        return True
        
    def next_instruction(self) -> Optional[str]:
        """Get next navigation instruction if available"""
        if not self.current_instructions:
            return None
            
        if self.instruction_index >= len(self.current_instructions):
            return "You have arrived at your destination."
            
        instruction = self.current_instructions[self.instruction_index]
        self.instruction_index += 1
        return instruction
        
    def has_more_instructions(self) -> bool:
        """Check if there are more navigation instructions"""
        return (self.current_instructions and 
                self.instruction_index < len(self.current_instructions))


class IntegratedVisionNavigation:
    """
    Main integration class combining vision detection with navigation.
    Implements safety-first speech control with obstacle priority.
    """
    
    def __init__(self):
        # Initialize existing components
        self.detection_node = DetectionNode()
        self.spatial_analysis = SpatialAnalysisNode()
        self.voice_nav = VoiceNavigator()
        
        # Initialize new components
        self.obstacle_engine = ObstacleDecisionEngine(DANGER_THRESHOLD)
        self.nav_controller = NavigationController(self.voice_nav)
        self.system_state = SystemState()
        
        # Speech control
        self.tts = pyttsx3.init()
        self.speech_lock = threading.Lock()
        self._setup_voice()
        
        # Control flags
        self.running = False
        self.navigation_thread = None
        
    def _setup_voice(self):
        """Configure TTS for clear obstacle warnings"""
        self.tts.setProperty("rate", 160)  # Slightly faster for urgency
        self.tts.setProperty("volume", 1.0)  # Maximum volume for safety
        
    def speak_priority(self, text: str, instruction_type: InstructionType):
        """
        🔊 SPEECH CONTROL: Speak with priority and suppression logic
        """
        current_time = time.time()
        
        with self.speech_lock:
            # Check if we should suppress this instruction
            if instruction_type == InstructionType.OBSTACLE:
                if text == self.system_state.last_obstacle_instruction:
                    # Don't repeat same obstacle warning
                    return
                    
                # Update state
                self.system_state.last_obstacle_instruction = text
                self.system_state.obstacle_active = True
                self.system_state.last_obstacle_time = current_time
                
            elif instruction_type == InstructionType.NAVIGATION:
                # Don't speak navigation if obstacle is active
                if self.system_state.obstacle_active:
                    return
                    
                if text == self.system_state.last_navigation_instruction:
                    # Don't repeat same navigation instruction
                    return
                    
                # Update state
                self.system_state.last_navigation_instruction = text
                self.system_state.navigation_active = True
                self.system_state.last_navigation_time = current_time
            
            # Speak the instruction
            print(f"🔊 [{instruction_type.value.upper()}] {text}")
            self.tts.say(text)
            self.tts.runAndWait()
    
    def process_frame(self, frame):
        """
        Process single frame: detection → spatial analysis → decision
        """
        # Get detections from YOLO + ByteTrack
        detections = self.detection_node.detect(frame)
        
        # Enrich detections with spatial analysis
        enriched_detections = []
        frame_height, frame_width = frame.shape[:2]
        
        for detection in detections:
            # Add spatial analysis
            box = detection['box']
            position = self.spatial_analysis.classify_position(box, frame_width)
            distance = self.spatial_analysis.estimate_distance(box)
            
            enriched_detection = detection.copy()
            enriched_detection['position'] = position
            enriched_detection['distance'] = distance
            
            enriched_detections.append(enriched_detection)
        
        return enriched_detections
    
    def obstacle_safety_check(self, detections: List[Dict]):
        """
        🔴 PRIORITY RULE: Check obstacles first, speak if dangerous
        """
        obstacle_instruction = self.obstacle_engine.analyze_obstacles(detections)
        
        if obstacle_instruction:
            # Obstacle detected - speak warning
            self.speak_priority(obstacle_instruction, InstructionType.OBSTACLE)
        else:
            # No obstacles - clear obstacle state
            if self.system_state.obstacle_active:
                self.system_state.obstacle_active = False
                self.system_state.last_obstacle_instruction = None
    
    def navigation_guidance(self):
        """
        🗺️ NAVIGATION LOGIC: Provide navigation instructions when safe
        """
        current_time = time.time()
        
        # Only speak navigation if no active obstacles
        if self.system_state.obstacle_active:
            return
            
        # Check if enough time has passed since last navigation instruction
        if (current_time - self.system_state.last_navigation_time) < NAVIGATION_INTERVAL:
            return
            
        # Get next navigation instruction
        if self.nav_controller.has_more_instructions():
            instruction = self.nav_controller.next_instruction()
            if instruction:
                self.speak_priority(instruction, InstructionType.NAVIGATION)
    
    def start_integrated_navigation(self, start_coords: Tuple[float, float], 
                                  end_coords: Tuple[float, float]):
        """
        Start integrated vision + navigation system
        """
        print("🚀 Starting Integrated Vision + Navigation System")
        
        # Initialize navigation
        if not self.nav_controller.start_navigation(start_coords, end_coords):
            print("❌ Failed to start navigation")
            return False
            
        # Calculate and announce route
        distance = calculate_distance(start_coords, end_coords)
        self.speak_priority(f"Navigation started. Destination is {distance:.0f} meters away.", 
                          InstructionType.NAVIGATION)
        
        self.running = True
        
        # Start navigation instruction thread
        self.navigation_thread = threading.Thread(target=self._navigation_loop)
        self.navigation_thread.daemon = True
        self.navigation_thread.start()
        
        return True
    
    def _navigation_loop(self):
        """
        Background thread for navigation instructions
        """
        while self.running:
            try:
                self.navigation_guidance()
                time.sleep(NAVIGATION_INTERVAL)
            except Exception as e:
                print(f"Navigation loop error: {e}")
                time.sleep(1)
    
    def process_vision_frame(self, frame):
        """
        🧩 MAIN INTEGRATION LOOP: Process frame with safety priority
        """
        try:
            # 1. Get enriched detections
            detections = self.process_frame(frame)
            
            # 2. 🔴 PRIORITY: Check obstacles first
            self.obstacle_safety_check(detections)
            
            # 3. Navigation guidance (only if safe)
            # This is handled by the background thread
            
            return detections
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return []
    
    def stop_navigation(self):
        """Stop the integrated navigation system"""
        self.running = False
        if self.navigation_thread:
            self.navigation_thread.join(timeout=2)
        
        self.speak_priority("Navigation stopped.", InstructionType.NAVIGATION)
        print("🛑 Integrated navigation stopped")


# Convenience functions for easy integration
def start_vision_navigation(start_coords: Tuple[float, float], 
                          end_coords: Tuple[float, float]):
    """
    Quick start function for integrated vision + navigation
    """
    system = IntegratedVisionNavigation()
    return system.start_integrated_navigation(start_coords, end_coords)


if __name__ == "__main__":
    # Example usage
    print("🧪 Testing Integrated Vision + Navigation System")
    
    # Test coordinates (San Francisco area)
    start = (37.7749, -122.4194)
    end = (37.7849, -122.4094)
    
    # Create integrated system
    system = IntegratedVisionNavigation()
    
    # Start navigation
    if system.start_integrated_navigation(start, end):
        print("✅ System started successfully")
        print("🎯 Expected behavior:")
        print("   - Obstacle warnings override navigation")
        print("   - No repeated instructions")
        print("   - Safety-first speech control")
        
        # Simulate running (in real app, this would be your camera loop)
        try:
            time.sleep(10)  # Run for 10 seconds
        except KeyboardInterrupt:
            pass
        finally:
            system.stop_navigation()
    else:
        print("❌ Failed to start system")