import { useState, useCallback } from 'react';
import axios from 'axios';

export const useVisionAssistant = (speak) => {
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Vision Assistant Ready");

  const handleToggleVision = useCallback(async () => {
    setLoading(true);

    try {
      if (!isRunning) {
        setStatus("Starting vision assistant...");
        speak("Starting vision assistant");

        const response = await axios.post("/api/start");

        if (response.data.success) {
          setIsRunning(true);
          setStatus("Vision Assistant Active - Camera Running");
          speak(
            "Vision assistant started successfully. Camera is now active and detecting objects."
          );
        } else {
          const errorMsg = "Failed to start: " + response.data.message;
          setStatus(errorMsg);
          speak(errorMsg);
        }
      } else {
        setStatus("Stopping vision assistant...");
        speak("Stopping vision assistant");

        const response = await axios.post("/api/stop");

        if (response.data.success) {
          setIsRunning(false);
          setStatus("Vision Assistant Stopped");
          speak("Vision assistant stopped successfully.");
        } else {
          const errorMsg = "Failed to stop: " + response.data.message;
          setStatus(errorMsg);
          speak(errorMsg);
        }
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMsg =
        "Connection error: " + (error.response?.data?.message || error.message);
      setStatus(errorMsg);
      speak(errorMsg);
    }

    setLoading(false);
  }, [isRunning, speak]);

  return {
    isRunning,
    setIsRunning,
    loading,
    status,
    handleToggleVision
  };
};