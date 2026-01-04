import { useEffect, useRef } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:8000");

export default function CameraFeed() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    async function startCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
      videoRef.current.srcObject = stream;
    }
    startCamera();
  }, []);

  const sendFrame = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      socket.emit("frame", blob);
    }, "image/jpeg");
  };

  useEffect(() => {
    const interval = setInterval(sendFrame, 200); // ~5 FPS
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <video ref={videoRef} autoPlay playsInline />
      <canvas ref={canvasRef} style={{ display: "none" }} />
    </>
  );
}
