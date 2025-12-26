import React from "react";
import "./App.css";

// Custom Hooks
import {
  useAccessibility,
  useVisionAssistant,
  useNavigation,
  useKeyboardShortcuts
} from "./hooks";

// Components
import {
  AccessibilityAnnouncer,
  Header,
  StatusSection,
  VisionControls,
  NavigationSection,
  InfoSection
} from "./components";

function App() {
  // Custom hooks for functionality
  const { announcements, announcementRef, speak } = useAccessibility();
  
  const {
    isRunning,
    loading: visionLoading,
    status,
    handleToggleVision
  } = useVisionAssistant(speak);

  const {
    navigationActive,
    setNavigationActive,
    startLocation,
    setStartLocation,
    destination,
    setDestination,
    savedLocations,
    loading: navigationLoading,
    handleStartNavigation,
    handleStopNavigation,
    handleSaveLocation
  } = useNavigation(speak);

  // Handle vision stop to also stop navigation
  const handleVisionToggle = async () => {
    if (isRunning && navigationActive) {
      setNavigationActive(false);
    }
    await handleToggleVision();
  };

  // Keyboard shortcuts
  useKeyboardShortcuts(
    isRunning,
    navigationActive,
    handleVisionToggle,
    handleStopNavigation,
    handleSaveLocation
  );

  const loading = visionLoading || navigationLoading;

  return (
    <div className="App" role="main">
      <AccessibilityAnnouncer 
        announcements={announcements}
        announcementRef={announcementRef}
      />

      <header className="App-header">
        <Header />

        <StatusSection 
          isRunning={isRunning}
          status={status}
        />

        <VisionControls
          isRunning={isRunning}
          loading={loading}
          handleToggleVision={handleVisionToggle}
        />

        <NavigationSection
          isRunning={isRunning}
          navigationActive={navigationActive}
          startLocation={startLocation}
          setStartLocation={setStartLocation}
          destination={destination}
          setDestination={setDestination}
          savedLocations={savedLocations}
          loading={loading}
          handleStartNavigation={handleStartNavigation}
          handleStopNavigation={handleStopNavigation}
          handleSaveLocation={handleSaveLocation}
        />

        <InfoSection />
      </header>
    </div>
  );
}

export default App;