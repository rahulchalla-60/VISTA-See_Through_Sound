import pyttsx3
import time
from typing import Tuple

from navigate import get_instructions, calculate_distance
from offline_navigation import OfflineNavigation


class VoiceNavigator:
    def __init__(self):
        self.tts = pyttsx3.init()
        self.nav = OfflineNavigation()
        self._setup_voice()

    def _setup_voice(self):
        """Make the voice calm and clear"""
        self.tts.setProperty("rate", 150)
        self.tts.setProperty("volume", 0.9)

        for voice in self.tts.getProperty("voices"):
            if "zira" in voice.name.lower() or "female" in voice.name.lower():
                self.tts.setProperty("voice", voice.id)
                break

    def speak(self, text: str, pause: float = 0.0):
        """Speak one sentence and optionally pause"""
        print("🔊", text)
        self.tts.say(text)
        self.tts.runAndWait()
        if pause > 0:
            time.sleep(pause)

    # --------------------------------------------------
    # CORE NAVIGATION
    # --------------------------------------------------

    def navigate(self, start: Tuple[float, float], end: Tuple[float, float]):
        """Speak turn-by-turn navigation"""
        self.speak("Getting directions.")

        distance = calculate_distance(start, end)
        self.speak(f"Your destination is about {distance:.0f} meters away.", 1)

        steps = get_instructions(start, end)

        if not steps:
            self.speak("Sorry. I could not find a route.")
            return

        self.speak("Navigation started.", 1)

        for step in steps:
            self.speak(step, 2)

        self.speak("You have arrived at your destination.")

    # --------------------------------------------------
    # SAVED LOCATIONS
    # --------------------------------------------------

    def navigate_to_saved_place(self, place_name: str, current_location: Tuple[float, float] = None):
        """Navigate to a saved location by name"""
        if current_location is None:
            current_location = self.get_current_location()
            
        destination = self.nav.get_location_coords(place_name)

        if not destination:
            self.speak(f"I could not find {place_name}.")
            self.list_saved_places()  # Help user see available options
            return

        self.speak(f"Navigating to {place_name}.", 1)
        self.navigate(current_location, destination)
    
    def get_current_location(self):
        """Get current GPS location (placeholder for GPS integration)"""
        # This would integrate with actual GPS when available
        # For now, could ask user or use a default
        return (37.7749, -122.4194)  # Default location
    
    def list_saved_places(self):
        """Speak available saved locations"""
        locations = list(self.nav.saved_locations.keys())
        if locations:
            places = ", ".join(locations)
            self.speak(f"Available locations are: {places}")
        else:
            self.speak("No saved locations available.")
