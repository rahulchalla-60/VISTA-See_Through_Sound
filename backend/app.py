import cv2
import numpy as np
import socketio
import uvicorn
from Detection.Detection import VisionDetector

class VisionAssistantServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(cors_allowed_origins="*")
        self.app = socketio.ASGIApp(self.sio)
        self.detector = VisionDetector()

        self._register_events()

    def _register_events(self):

        @self.sio.event
        async def connect(sid, environ):
            print("🌐 Client connected")

        @self.sio.event
        async def frame(sid, data):
            frame = self._decode(data)
            if frame is None:
                return

            results = self.detector.process(frame)
            await self.sio.emit("detections", results)

    def _decode(self, data):
        np_img = np.frombuffer(data, np.uint8)
        return cv2.imdecode(np_img, cv2.IMREAD_COLOR)


def main():
    server = VisionAssistantServer()
    print("🚀 Vision Assistant running at http://localhost:8000")
    uvicorn.run(server.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
