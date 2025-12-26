import React from 'react';

const NavigationSection = ({
  isRunning,
  navigationActive,
  startLocation,
  setStartLocation,
  destination,
  setDestination,
  savedLocations,
  loading,
  handleStartNavigation,
  handleStopNavigation,
  handleSaveLocation
}) => {
  if (!isRunning) return null;

  return (
    <section
      id="navigation-section"
      className="navigation-section"
      aria-labelledby="navigation-heading"
      tabIndex="-1"
    >
      <h2 id="navigation-heading">Navigation with Obstacle Detection</h2>

      {!navigationActive ? (
        <div className="navigation-setup">
          <div className="location-inputs">
            <div className="input-group">
              <label htmlFor="start-location">Start Location:</label>
              <select
                id="start-location"
                value={startLocation}
                onChange={(e) => setStartLocation(e.target.value)}
                aria-describedby="start-location-desc"
              >
                <option value="">Select start location</option>
                {savedLocations.map((location, index) => (
                  <option key={index} value={location.name}>
                    {location.description || location.name}
                  </option>
                ))}
              </select>
              <p id="start-location-desc" className="input-description">
                Choose your starting point from saved locations
              </p>
            </div>

            <div className="input-group">
              <label htmlFor="destination">Destination:</label>
              <select
                id="destination"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                aria-describedby="destination-desc"
              >
                <option value="">Select destination</option>
                {savedLocations.map((location, index) => (
                  <option key={index} value={location.name}>
                    {location.description || location.name}
                  </option>
                ))}
              </select>
              <p id="destination-desc" className="input-description">
                Choose your destination from saved locations
              </p>
            </div>
          </div>

          <button
            className="navigation-button start-nav"
            onClick={handleStartNavigation}
            disabled={!startLocation || !destination || loading}
            aria-describedby="start-nav-desc"
          >
            🧭 START NAVIGATION
          </button>
          <p id="start-nav-desc" className="button-description">
            Begin turn-by-turn navigation with obstacle detection
          </p>

          <button
            className="location-button"
            onClick={handleSaveLocation}
            aria-describedby="save-location-desc"
          >
            📍 SAVE CURRENT LOCATION
          </button>
          <p id="save-location-desc" className="button-description">
            Use voice commands to save your current location
          </p>
        </div>
      ) : (
        <div className="navigation-active">
          <p className="navigation-status" aria-live="polite">
            🧭 Navigation Active: {startLocation} → {destination}
          </p>
          <p className="safety-notice">
            🔴 Safety Priority: Obstacle warnings will override navigation
            instructions
          </p>

          <button
            className="navigation-button stop-nav"
            onClick={handleStopNavigation}
            disabled={loading}
            aria-describedby="stop-nav-desc"
          >
            🛑 STOP NAVIGATION
          </button>
          <p id="stop-nav-desc" className="button-description">
            Stop navigation but keep vision assistant active
          </p>
        </div>
      )}
    </section>
  );
};

export default NavigationSection;