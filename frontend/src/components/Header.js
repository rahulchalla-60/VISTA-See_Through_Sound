import React from 'react';

const Header = () => {
  return (
    <>
      <h1>🎯 VISTA - Vision Assistant</h1>
      <p className="subtitle">Accessible Navigation for Blind Users</p>

      {/* Keyboard shortcuts info */}
      <div
        className="shortcuts-info"
        role="region"
        aria-labelledby="shortcuts-heading"
      >
        <h2 id="shortcuts-heading" className="sr-only">
          Keyboard Shortcuts
        </h2>
        <p className="shortcuts-text">
          Ctrl+V: Toggle Vision | Ctrl+N: Navigation | Ctrl+S: Save Location
        </p>
      </div>
    </>
  );
};

export default Header;