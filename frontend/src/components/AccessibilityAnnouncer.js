import React from 'react';

const AccessibilityAnnouncer = ({ announcements, announcementRef }) => {
  return (
    <div
      ref={announcementRef}
      className="sr-only"
      aria-live="polite"
      aria-atomic="true"
      tabIndex="-1"
    >
      {announcements.length > 0 && announcements[announcements.length - 1]}
    </div>
  );
};

export default AccessibilityAnnouncer;