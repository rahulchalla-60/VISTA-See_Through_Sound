import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';

export const useNavigation = (speak) => {
  const [navigationActive, setNavigationActive] = useState(false);
  const [startLocation, setStartLocation] = useState("");
  const [destination, setDestination] = useState("");
  const [savedLocations, setSavedLocations] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadSavedLocations = useCallback(async () => {
    try {
      const response = await axios.get("/api/locations");
      if (response.data.success) {
        setSavedLocations(response.data.locations || []);
      }
    } catch (error) {
      console.error("Error loading locations:", error);
    }
  }, []);

  const handleStartNavigation = useCallback(async () => {
    if (!startLocation || !destination) {
      const errorMsg = "Please select both start location and destination";
      speak(errorMsg);
      return;
    }

    setLoading(true);
    speak("Starting navigation with obstacle detection");

    try {
      const response = await axios.post("/api/navigation/start", {
        start: startLocation,
        destination: destination,
      });

      if (response.data.success) {
        setNavigationActive(true);
        speak(
          `Navigation started from ${startLocation} to ${destination}. Obstacle detection is active for your safety.`
        );
      } else {
        const errorMsg = "Navigation failed: " + response.data.message;
        speak(errorMsg);
      }
    } catch (error) {
      const errorMsg =
        "Navigation error: " + (error.response?.data?.message || error.message);
      speak(errorMsg);
    }

    setLoading(false);
  }, [startLocation, destination, speak]);

  const handleStopNavigation = useCallback(async () => {
    setLoading(true);
    speak("Stopping navigation");

    try {
      const response = await axios.post("/api/navigation/stop");

      if (response.data.success) {
        setNavigationActive(false);
        speak(
          "Navigation stopped. Vision assistant continues to detect objects."
        );
      }
    } catch (error) {
      const errorMsg = "Error stopping navigation: " + error.message;
      speak(errorMsg);
    }

    setLoading(false);
  }, [speak]);

  const handleSaveLocation = useCallback(async () => {
    speak(
      "Opening location saver. Please use voice commands to save your current location."
    );

    try {
      const response = await axios.post("/api/locations/save");
      if (response.data.success) {
        speak("Location saver activated. Say the location name when prompted.");
        loadSavedLocations(); // Refresh the list
      }
    } catch (error) {
      const errorMsg = "Error activating location saver: " + error.message;
      speak(errorMsg);
    }
  }, [speak, loadSavedLocations]);

  // Load saved locations on mount
  useEffect(() => {
    loadSavedLocations();
  }, [loadSavedLocations]);

  return {
    navigationActive,
    setNavigationActive,
    startLocation,
    setStartLocation,
    destination,
    setDestination,
    savedLocations,
    loading,
    handleStartNavigation,
    handleStopNavigation,
    handleSaveLocation
  };
};