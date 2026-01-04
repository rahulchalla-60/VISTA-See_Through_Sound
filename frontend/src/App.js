import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import CameraFeed from "./CameraFeed.js";
import io from "socket.io-client";

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [detections, setDetections] = useState([]);
  const [status, setStatus] = useState("Disconnected");
  const socketRef = useRef(null);
  const announcementRef = useRef(null);

  useEffect(() => {
    // Connect to backend
    socketRef.current = io("http://localhost:8000");
    
    socketRef.current.on("connect", () => {
      setIsConnected(true);
      setStatus("Connected - Camera Active");
      speak("Vision assistant connected");
    });

    socketRef.current.on("disconnect", () => {
      setIsConnected(false);
      setStatus("Disconnected");
      speak("Vision assistant disconnected");
    });

    socketRef.current.on("detections", (detectedObjects) => {
      setDetections(detectedObjects);
      
      // Announce new detections
      if (detectedObjects.length > 0) {
        const announcement = `${detectedObjects.length} object${detectedObjects.length > 1 ? 's' : ''} detected`;
        speak(announcement);
      }
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const speak = (text) => {
    if (announcementRef.current) {
      announcementRef.current.textContent = text;
    }
    
    // Also use Web Speech API if available
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="App" role="main">
      {/* Screen reader announcements */}
      <div 
        ref={announcementRef}
        aria-live="polite" 
        aria-atomic="true"
        className="sr-only"
      />

      <header className="App-header">
        <h1>Vision Assistant for Blind People</h1>
        
        <div className="status-section">
          <h2>Status</h2>
          <p className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
            {status}
          </p>
        </div>

        <div className="camera-section">
          <h2>Camera Feed</h2>
          {isConnected ? (
            <CameraFeed />
          ) : (
            <div className="camera-placeholder">
              <p>Connecting to camera...</p>
            </div>
          )}
        </div>

        <div className="detections-section">
          <h2>Current Detections ({detections.length})</h2>
          {detections.length > 0 ? (
            <ul className="detections-list">
              {detections.map((detection) => (
                <li key={detection.track_id} className="detection-item">
                  <strong>{detection.class_name}</strong> 
                  <span className="detection-id"> (ID: {detection.track_id})</span>
                  <span className="detection-confidence">
                    {(detection.confidence * 100).toFixed(1)}% confidence
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p>No objects detected</p>
          )}
        </div>

        <div className="info-section">
          <h2>Instructions</h2>
          <ul>
            <li>Make sure your camera is enabled</li>
            <li>Point camera at objects to detect them</li>
            <li>Listen for voice announcements</li>
            <li>Check the detections list for current objects</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;