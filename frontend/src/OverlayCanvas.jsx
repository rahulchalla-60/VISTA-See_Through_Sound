import { useEffect, useRef } from "react";

const OverlayCanvas = ({ videoRef, detections }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!videoRef?.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const draw = () => {
      if (!videoRef.current.videoWidth) {
        requestAnimationFrame(draw);
        return;
      }

      // Match canvas to video size
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;

      // Clear previous frame
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      detections.forEach((obj) => {
        const [x1, y1, x2, y2] = obj.bbox;
        const width = x2 - x1;
        const height = y2 - y1;

        // 🔲 Bounding box
        ctx.strokeStyle = "#00FF00"; // high-contrast green
        ctx.lineWidth = 4;
        ctx.strokeRect(x1, y1, width, height);

        // 🏷️ Text label
        ctx.fillStyle = "#00FF00";
        ctx.font = "20px Arial";
        ctx.textBaseline = "top";

        const labelText = `ID ${obj.id} | ${obj.label}`;
        const infoText = `${obj.position}, ${obj.distance}`;

        // Background for readability
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(x1, y1 - 44, ctx.measureText(labelText).width + 10, 44);

        ctx.fillStyle = "#00FF00";
        ctx.fillText(labelText, x1 + 5, y1 - 40);
        ctx.fillText(infoText, x1 + 5, y1 - 20);
      });

      requestAnimationFrame(draw);
    };

    draw();
  }, [detections, videoRef]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        zIndex: 10,
        width: "100%",
        height: "100%",
        pointerEvents: "none"
      }}
    />
  );
};

export default OverlayCanvas;
