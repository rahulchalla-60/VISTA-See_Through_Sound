import { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

export default function CameraAssistant() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const socketRef = useRef(null);
  const [running, setRunning] = useState(false);
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    socketRef.current = io("http://localhost:8000");

    socketRef.current.on("detections", (data) => {
      setDetections(data);
      speak(data);
    });

    return () => socketRef.current.disconnect();
  }, []);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
    await videoRef.current.play();
    setRunning(true);
  };

  const stop = () => {
    videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    setRunning(false);
  };

  useEffect(() => {
    if (!running) return;
    
    const i = setInterval(() => {
      if (!running) return;
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (video.videoWidth === 0) return;

      const ctx = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(blob => {
        socketRef.current.emit("frame", blob);
      }, "image/jpeg", 0.6);
    }, 200);
    
    return () => clearInterval(i);
  }, [running]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw detections
    ctx.lineWidth = 2;
    ctx.strokeStyle = "lime";
    ctx.fillStyle = "lime";
    ctx.font = "16px Arial";

    detections.forEach(d => {
      const [x1, y1, x2, y2] = d.bbox;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      ctx.fillText(d.class, x1, y1 - 5);
    });
  }, [detections]);

  const speak = (objects) => {
    if (!window.speechSynthesis) return;
    objects.forEach(o => {
      const msg = new SpeechSynthesisUtterance(`${o.class} detected`);
      window.speechSynthesis.speak(msg);
    });
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h1>Vision Assistant</h1>

      {!running ? (
        <button onClick={start} style={btnStyle}>▶ START</button>
      ) : (
        <button onClick={stop} style={btnStyle}>⏹ STOP</button>
      )}

      <div style={{ position: "relative" }}>
        <video ref={videoRef} style={{ width: "640px" }} />
        <canvas
          ref={canvasRef}
          style={{ position: "absolute", top: 0, left: 0 }}
        />
      </div>
    </div>
  );
}

const btnStyle = {
  fontSize: "24px",
  padding: "15px 40px",
  margin: "20px",
  cursor: "pointer"
};
