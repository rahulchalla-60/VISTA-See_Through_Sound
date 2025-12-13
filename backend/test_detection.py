#!/usr/bin/env python3
"""
Test script for integrated camera + detection system
Press 'q' to quit the detection stream
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.detection_node import DetectionNode

def test_detection():
    print("Testing Camera + YOLO Detection Integration...")
    print("Make sure you have:")
    print("- A camera connected")
    print("- ultralytics installed: pip install ultralytics")
    print("- opencv-python installed: pip install opencv-python")
    print()
    
    try:
        # Initialize the integrated detection node
        detection_system = DetectionNode(
            cam_index=0,        # Use default camera
            model="yolov8n.pt", # Use nano model (fastest)
            conf=0.5            # 50% confidence threshold
        )
        
        # Run the detection stream
        detection_system.run_detection_stream()
        
    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install required packages: pip install ultralytics opencv-python")
        print("2. Make sure your camera is not being used by another application")
        print("3. Check if your camera index is correct (try cam_index=1 if 0 doesn't work)")

if __name__ == "__main__":
    test_detection()