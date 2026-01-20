#!/usr/bin/env python3
"""
Vision Assistant API Server
Runs the Flask server for object detection
"""

import os
import sys
from api import app, detector

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import cv2
        import numpy as np
        from ultralytics import YOLO
        from flask import Flask
        from flask_cors import CORS
        from PIL import Image
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install requirements: pip install -r ../requirements.txt")
        return False

def check_model():
    """Check if YOLO model is available"""
    model_paths = ["yolov8n.pt", "../yolov8n.pt"]
    
    for path in model_paths:
        if os.path.exists(path):
            print(f"✓ YOLO model found at: {path}")
            return True
    
    print("⚠ YOLO model not found locally, will download automatically")
    return True

def main():
    """Main function to start the server"""
    print("=" * 50)
    print("Vision Assistant API Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check model
    check_model()
    
    # Check if detector is loaded
    if detector.model is None:
        print("✗ Failed to load YOLO model")
        sys.exit(1)
    else:
        print("✓ YOLO model loaded successfully")
    
    print("\nStarting server...")
    print("API Endpoints:")
    print("  POST /detect - Object detection")
    print("  GET /health - Health check")
    print("  GET /model-info - Model information")
    print("\nServer will run on: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Flask server
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=False,  # Set to False for production
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")

if __name__ == "__main__":
    main()