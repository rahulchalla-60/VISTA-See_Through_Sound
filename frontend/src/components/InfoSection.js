import React from 'react';

const InfoSection = () => {
  return (
    <>
      {/* Information Section */}
      <section className="info-section" aria-labelledby="info-heading">
        <h2 id="info-heading">How VISTA Works</h2>
        <ul>
          <li>🎥 Camera captures live video feed</li>
          <li>🤖 AI detects objects and obstacles in real-time</li>
          <li>📍 Provides spatial location (left, center, right)</li>
          <li>📏 Estimates distance to objects and obstacles</li>
          <li>🔊 Announces objects with clear text-to-speech</li>
          <li>🧭 Provides turn-by-turn navigation instructions</li>
          <li>🔴 Prioritizes obstacle warnings over navigation</li>
          <li>🎤 Voice-controlled location saving</li>
        </ul>
      </section>

      {/* Safety Information */}
      <section className="safety-section" aria-labelledby="safety-heading">
        <h2 id="safety-heading">Safety Features</h2>
        <ul>
          <li>🔴 Obstacle detection overrides navigation instructions</li>
          <li>🚨 Immediate audio warnings for center obstacles</li>
          <li>↔️ Left/right movement suggestions when blocked</li>
          <li>🛑 Stop commands when path is completely blocked</li>
          <li>🔊 No overlapping audio announcements</li>
          <li>⌨️ Full keyboard accessibility</li>
        </ul>
      </section>
    </>
  );
};

export default InfoSection;