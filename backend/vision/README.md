# Vision Module - Object Detection API

This module provides real-time object detection using YOLOv8 for the Vision Assistant application.

## Features

- Real-time object detection using YOLOv8n model
- REST API for frontend integration
- Base64 image processing
- Confidence-based filtering
- Object detection summaries
- Health check endpoints

## Files

- `detector.py` - Core object detection logic using YOLO
- `api.py` - Flask REST API server
- `run_server.py` - Server startup script with dependency checks
- `test_detection.py` - Testing utilities for webcam and image files

## API Endpoints

### POST /detect
Detect objects in a base64 encoded image.

**Request:**
```json
{
  "image": "base64_encoded_image_data"
}
```

**Response:**
```json
{
  "success": true,
  "detections": [
    {
      "class": "person",
      "confidence": 0.85,
      "bbox": {
        "x1": 100,
        "y1": 50,
        "x2": 200,
        "y2": 300
      }
    }
  ],
  "count": 1,
  "summary": "Detected: 1 person"
}
```

### GET /health
Check server health and model status.

### GET /model-info
Get information about the loaded YOLO model.

## Setup and Usage

1. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the Server:**
   ```bash
   cd backend/vision
   python run_server.py
   ```

3. **Test Detection:**
   ```bash
   python test_detection.py
   ```

## Model Information

- Uses YOLOv8n (nano) model for fast inference
- Automatically downloads model if not present
- Detects 80 different object classes
- Confidence threshold: 0.5

## Integration

The API is designed to work with the React frontend that sends video frames as base64 encoded images for real-time object detection.

## Error Handling

- Validates input data
- Handles model loading errors
- Provides detailed error messages
- Graceful fallbacks for missing dependencies