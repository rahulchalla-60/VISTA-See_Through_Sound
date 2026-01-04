import socketio
import cv2
import numpy as np
from ultralytics import YOLO
from yolox.tracker.byte_tracker import BYTETracker

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = socketio.ASGIApp(sio)

model = YOLO("yolo11n.pt")

tracker = BYTETracker(
    track_thresh=0.5,
    match_thresh=0.8,
    track_buffer=30
)

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def frame(sid, data):
    # Convert blob → image
    np_img = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # YOLO detection
    results = model(frame, conf=0.5, verbose=False)[0]

    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        detections.append([x1, y1, x2 - x1, y2 - y1, conf, cls])

    # ByteTrack expects numpy array
    dets = np.array(detections) if detections else np.empty((0, 6))

    tracks = tracker.update(
        dets[:, :5] if len(dets) else np.empty((0, 5)),
        frame.shape[:2],
        frame.shape[:2]
    )

    tracked_objects = []
    for t in tracks:
        tracked_objects.append({
            "track_id": int(t.track_id),
            "bbox": list(map(int, t.tlbr)),
        })

    await sio.emit("detections", tracked_objects)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
