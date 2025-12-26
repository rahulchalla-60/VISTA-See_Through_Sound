import React from 'react';

const VisionControls = ({ isRunning, loading, handleToggleVision }) => {
  return (
    <section className="controls-section" aria-labelledby="controls-heading">
      <h2 id="controls-heading">Main Controls</h2>

      <button
        className={`main-button ${isRunning ? "stop" : "start"} ${
          loading ? "loading" : ""
        }`}
        onClick={handleToggleVision}
        disabled={loading}
        aria-describedby="vision-button-desc"
      >
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true"></span>
            <span>Processing...</span>
          </>
        ) : (
          <>{isRunning ? "⏹️ STOP VISION" : "▶️ START VISION"}</>
        )}
      </button>
      <p id="vision-button-desc" className="button-description">
        {isRunning
          ? "Stop camera and object detection"
          : "Start camera and object detection"}
      </p>
    </section>
  );
};

export default VisionControls;