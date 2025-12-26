import { useEffect, useCallback } from 'react';

export const useKeyboardShortcuts = (
  isRunning,
  navigationActive,
  handleToggleVision,
  handleStopNavigation,
  handleSaveLocation
) => {
  const handleKeyDown = useCallback(
    (event) => {
      switch (event.key) {
        case "v":
        case "V":
          if (event.ctrlKey) {
            event.preventDefault();
            handleToggleVision();
          }
          break;
        case "n":
        case "N":
          if (event.ctrlKey && isRunning) {
            event.preventDefault();
            if (navigationActive) {
              handleStopNavigation();
            } else {
              // Focus on navigation section
              document.getElementById("navigation-section")?.focus();
            }
          }
          break;
        case "s":
        case "S":
          if (event.ctrlKey) {
            event.preventDefault();
            handleSaveLocation();
          }
          break;
        default:
          break;
      }
    },
    [isRunning, navigationActive, handleToggleVision, handleStopNavigation, handleSaveLocation]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
};