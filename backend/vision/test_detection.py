import cv2
import base64
from detector import ObjectDetector
import json

def test_with_webcam():
    """Test object detection with webcam"""
    print("Testing object detection with webcam...")
    
    # Initialize detector
    detector = ObjectDetector()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Press 'q' to quit, 'space' to detect objects")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display frame
        cv2.imshow('Webcam - Press SPACE to detect', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):  # Space key
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            # Detect objects
            result = detector.detect_objects(base64_image)
            
            if result.get("success"):
                print(f"\nDetection Results:")
                print(f"Objects found: {result['count']}")
                print(f"Summary: {result.get('summary', 'No summary')}")
                
                for i, detection in enumerate(result['detections']):
                    print(f"  {i+1}. {detection['class']} (confidence: {detection['confidence']})")
            else:
                print(f"Detection failed: {result.get('error', 'Unknown error')}")
    
    cap.release()
    cv2.destroyAllWindows()

def test_with_image_file(image_path):
    """Test object detection with image file"""
    print(f"Testing object detection with image: {image_path}")
    
    # Initialize detector
    detector = ObjectDetector()
    
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image {image_path}")
            return
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', image)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        # Detect objects
        result = detector.detect_objects(base64_image)
        
        if result.get("success"):
            print(f"\nDetection Results:")
            print(f"Objects found: {result['count']}")
            print(f"Summary: {result.get('summary', 'No summary')}")
            
            for i, detection in enumerate(result['detections']):
                print(f"  {i+1}. {detection['class']} (confidence: {detection['confidence']})")
                bbox = detection['bbox']
                print(f"      Location: ({bbox['x1']}, {bbox['y1']}) to ({bbox['x2']}, {bbox['y2']})")
        else:
            print(f"Detection failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Vision Assistant - Object Detection Test")
    print("1. Test with webcam")
    print("2. Test with image file")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_webcam()
    elif choice == "2":
        image_path = input("Enter image file path: ").strip()
        test_with_image_file(image_path)
    else:
        print("Invalid choice")