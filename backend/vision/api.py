from flask import Flask, request, jsonify
from flask_cors import CORS
from detector import ObjectDetector
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize object detector
detector = ObjectDetector()

@app.route('/detect', methods=['POST'])
def detect_objects():
    """API endpoint to detect objects in uploaded image"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                "error": "No image data provided",
                "success": False
            }), 400
        
        # Get base64 image data
        base64_image = data['image']
        
        # Perform object detection
        result = detector.detect_objects(base64_image)
        
        if "error" in result:
            return jsonify(result), 500
        
        # Generate summary for accessibility
        summary = detector.get_detection_summary(result["detections"])
        result["summary"] = summary
        
        # Log detection results
        print(f"Detection completed: {result['count']} objects found")
        print(f"Summary: {summary}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            "error": f"Server error: {str(e)}",
            "success": False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": detector.model is not None
    })

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if detector.model:
        return jsonify({
            "model_path": detector.model_path,
            "classes": list(detector.model.names.values()),
            "num_classes": len(detector.model.names)
        })
    else:
        return jsonify({"error": "Model not loaded"}), 500

if __name__ == '__main__':
    print("Starting Vision Assistant API Server...")
    print(f"Model loaded: {detector.model is not None}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )