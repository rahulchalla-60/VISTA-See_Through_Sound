import { useRef, useState } from "react";
import Camera from "./Camera";
import WebSocketService from "./WebSocket";
import OverlayCanvas from "./OverlayCanvas";

const WS_URL = "ws://localhost:8000/ws";

function App() {
  const wsRef = useRef(null);
  const videoRef = useRef(null);
  const [detections, setDetections] = useState([]);

  const handleCameraReady = (videoEl) => {
    videoRef.current = videoEl;
    wsRef.current = new WebSocketService(WS_URL);
    wsRef.current.connect();

    wsRef.current.onMessage((data) => {
      setDetections(data.objects);
    });

    // Send frames to backend
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    const sendFrame = () => {
      if (videoEl.videoWidth > 0) {
        canvas.width = videoEl.videoWidth;
        canvas.height = videoEl.videoHeight;
        ctx.drawImage(videoEl, 0, 0);

        canvas.toBlob((blob) => {
          if (blob && wsRef.current) {
            wsRef.current.send(blob);
          }
        }, "image/jpeg", 0.8);
      }

      setTimeout(sendFrame, 100); // ~10 FPS
    };

    sendFrame();
  };

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <Camera onCameraReady={handleCameraReady} />
      <OverlayCanvas videoRef={videoRef} detections={detections} />
    </div>
  );
}

export default App;
