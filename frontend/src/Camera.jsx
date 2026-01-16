import { useRef, useState } from "react";

const Camera = ({ onCameraReady }) => {
  const videoRef = useRef(null);
  const [started, setStarted] = useState(false);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStarted(true);

        // Notify parent that camera is ready
        if (onCameraReady) {
          onCameraReady(videoRef.current);
        }
      }
    } catch (err) {
      console.error("Camera access denied:", err);
    }
  };

  return (
    <div style={styles.container}>
      {!started && (
        <button onClick={startCamera} style={styles.button}>
          Start Camera
        </button>
      )}

      <video
        ref={videoRef}
        playsInline
        muted
        style={{
          ...styles.video,
          display: started ? "block" : "none"
        }}
      />
    </div>
  );
};

export default Camera;

const styles = {
  container: {
    width: "100vw",
    height: "100vh",
    backgroundColor: "black",
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
  },
  video: {
    width: "100%",
    height: "100%",
    objectFit: "cover"
  },
  button: {
    fontSize: "24px",
    padding: "20px 40px",
    borderRadius: "10px",
    border: "none",
    cursor: "pointer"
  }
};
