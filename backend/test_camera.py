#!/usr/bin/env python3

import cv2
import sys
import os

# Add the current directory to Python path so we can import from nodes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.camera_node import CameraNode

def test_camera():
    print("Testing Camera Node...")
    print("Press 'q' to quit")
    
    try:
        # Initialize camera node
        camera = CameraNode(cam_index=0)
        
        # Test the stream
        for frame_data in camera.stream():
            frame = frame_data["frame"]
            
            # Display the frame
            cv2.imshow('Camera Test - Press q to quit', frame)
            
            # The quit logic is handled inside the stream() method
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a camera connected and opencv-python installed")
    
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()