#!/usr/bin/env python3
"""
Test script for the new detection_node with object tracking
Press 'q' to quit the detection stream
"""

import sys
import os

# Add the nodes directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nodes'))

def test_detection():
    print("Testing YOLO Detection with Object Tracking...")
    print("Features:")
    print("- Object tracking with unique IDs")
    print("- 'Speak once' per object detection")
    print("- Press 'q' to quit")
    print()
    print("Make sure you have:")
    print("- ultralytics installed: pip install ultralytics")
    print("- opencv-python installed: pip install opencv-python")
    print()
    
    try:
        # Import and run the detection node
        import detection_node
        print("Detection started! Move objects in/out of view to test tracking.")
        
    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install required packages: pip install ultralytics opencv-python")
        print("2. Make sure your camera is not being used by another application")
        print("3. Check if your camera index is correct")

if __name__ == "__main__":
    test_detection()