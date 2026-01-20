from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add vision folder to path so we can import detector
sys.path.append(os.path.join(os.path.dirname(__file__), 'vision'))
from detector import ObjectDetector

# Create FastAPI app
app = FastAPI(title="Vision Assistant", description="AI Object Detection for Blind Assistance")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the AI model
print("Loading AI model...")
detector = ObjectDetector()
print("AI model ready!")

# Request model for image data
class ImageRequest(BaseModel):
    image: str

@app.post("/detect")
async def detect_objects(request: ImageRequest):
    """Find objects in the image using AI"""
    
    # Find objects in the image
    result = detector.detect_objects(request.image)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Create a simple summary
    summary = detector.get_summary(result["objects"])
    result["summary"] = summary
    
    # Show what we found
    print(f"Found {result['count']} objects: {summary}")
    
    return result

@app.get("/health")
async def health_check():
    """Check if the AI is working"""
    return {"status": "working", "ai_ready": detector.model is not None}

@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "Vision Assistant AI is running!",
        "endpoints": {
            "/detect": "Send image to detect objects",
            "/health": "Check if AI is working"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Vision Assistant Server...")
    print("Server will run on: http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)