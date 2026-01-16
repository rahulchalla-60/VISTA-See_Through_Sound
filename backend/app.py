import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from vision.detector import YOLODetector
from vision.tracker import ObjectTracker
from vision.position import get_object_position
from vision.distance import estimate_distance
from vision.tts import ObjectAnnouncer


# -------------------- FastAPI App --------------------
app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Load Vision Modules --------------------
detector = YOLODetector()
tracker = ObjectTracker()
announcer = ObjectAnnouncer()


# -------------------- Utility: Decode Image --------------------
def decode_frame(frame_bytes: bytes):
    """
    Decodes JPEG bytes into OpenCV frame.
    """
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame


# -------------------- WebSocket Endpoint --------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 WebSocket connected")

    try:
        while True:
            # 1️⃣ Receive frame from frontend
            frame_bytes = await websocket.receive_bytes()

            # 2️⃣ Decode frame
            frame = decode_frame(frame_bytes)
            if frame is None:
                continue

            frame_height, frame_width, _ = frame.shape

            # 3️⃣ YOLO Detection
            detections = detector.detect(frame)

            # 4️⃣ ByteTrack Tracking
            tracked_objects = tracker.update(detections)

            response_objects = []

            # 5️⃣ Position + Distance + TTS
            for obj in tracked_objects:
                bbox = obj["bbox"]
                track_id = obj["track_id"]
                label = obj["label"]

                position = get_object_position(bbox, frame_width)
                distance = estimate_distance(bbox, frame_height)

                # 🔊 Announce only once
                announcer.announce(
                    track_id=track_id,
                    label=label,
                    position=position,
                    distance=distance
                )

                response_objects.append({
                    "id": track_id,
                    "label": label,
                    "bbox": bbox,
                    "position": position,
                    "distance": distance
                })

            # 6️⃣ Send results to frontend
            await websocket.send_json({
                "objects": response_objects
            })

    except WebSocketDisconnect:
        print("❌ WebSocket disconnected")

    except WebSocketDisconnect:
        announcer.spoken_ids.clear()
        print("❌ WebSocket disconnected, TTS reset")

    except Exception as e:
        print("⚠️ Error:", e)
