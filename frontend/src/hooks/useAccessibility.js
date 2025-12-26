import { useState, useRef, useEffect } from 'react';

export const useAccessibility = () => {
  const [announcements, setAnnouncements] = useState([]);
  const announcementRef = useRef(null);

  const speak = (text) => {
    // Add to announcements for screen readers
    setAnnouncements((prev) => [...prev.slice(-4), text]); // Keep last 5 announcements

    // Use Web Speech API for immediate audio feedback
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.volume = 1.0;
      speechSynthesis.speak(utterance);
    }
  };

  // Focus management for accessibility
  useEffect(() => {
    if (announcementRef.current) {
      announcementRef.current.focus();
    }
  }, [announcements]);

  return {
    announcements,
    announcementRef,
    speak
  };
};