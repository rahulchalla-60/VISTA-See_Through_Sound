import React from 'react';

const StatusSection = ({ isRunning, status }) => {
  return (
    <section className="status-section" aria-labelledby="status-heading">
      <h2 id="status-heading">System Status</h2>
      <div className="status-container">
        <div
          className={`status-indicator ${isRunning ? "running" : "stopped"}`}
          role="status"
          aria-label={isRunning ? "System running" : "System stopped"}
        >
          {isRunning ? "🟢" : "🔴"}
        </div>
        <p className="status-text" aria-live="polite">
          {status}
        </p>
      </div>
    </section>
  );
};

export default StatusSection;