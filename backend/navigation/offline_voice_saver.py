import json
import os
from datetime import datetime

import speech_recognition as sr
import pyttsx3


class OfflineVoiceLocation:
    def __init__(self, file="navigation/saved_locations.json"):
        self.file = file
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.tts = pyttsx3.init()
        self.locations = self._load_locations()

    # -------------------- Storage --------------------

    def _load_locations(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                return json.load(f)
        return {}

    def _save_locations(self):
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, "w") as f:
            json.dump(self.locations, f, indent=2)

    # -------------------- Voice --------------------

    def speak(self, text):
        print("🔊", text)
        self.tts.say(text)
        self.tts.runAndWait()

    def listen(self, prompt):
        self.speak(prompt)

        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, 1)
            
        try:
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=5)
            
            # Try offline first
            try:
                text = self.recognizer.recognize_sphinx(audio)
                print("You said (offline):", text)
                return text.lower().strip()
            except:
                # Fallback to online if needed
                try:
                    text = self.recognizer.recognize_google(audio)
                    print("You said (online):", text)
                    return text.lower().strip()
                except:
                    self.speak("Sorry, I did not understand.")
                    return None
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything.")
            return None
        except:
            self.speak("Microphone error.")
            return None

    # -------------------- Location Input --------------------

    def get_coordinates(self):
        self.speak("Please enter coordinates.")
        try:
            lat = float(input("Latitude: "))
            lon = float(input("Longitude: "))
            return lat, lon
        except:
            self.speak("Invalid coordinates.")
            return None, None

    # -------------------- Core Actions --------------------

    def save_location(self):
        name = self.listen("Say location name, like home or bus stop.")
        if not name:
            return

        lat, lon = self.get_coordinates()
        if lat is None:
            return

        key = name.replace(" ", "_")

        self.locations[key] = {
            "lat": lat,
            "lon": lon,
            "description": name,
            "saved_at": datetime.now().isoformat()
        }

        self._save_locations()
        self.speak(f"{name} saved successfully.")

    def list_locations(self):
        if not self.locations:
            self.speak("No saved locations.")
            return

        self.speak("Here are your saved locations.")
        for data in self.locations.values():
            print(f"- {data['description']} → {data['lat']:.5f}, {data['lon']:.5f}")

    def delete_location(self):
        name = self.listen("Say the location name to delete.")
        if not name:
            return

        key = name.replace(" ", "_")
        if key in self.locations:
            del self.locations[key]
            self._save_locations()
            self.speak(f"{name} deleted.")
        else:
            self.speak(f"{name} not found.")

    def get_location_coords(self, location_name: str):
        """Get coordinates for a saved location (for navigation integration)"""
        location_name = location_name.lower().strip()
        
        # Try exact match first
        key = location_name.replace(" ", "_")
        if key in self.locations:
            loc = self.locations[key]
            return (loc['lat'], loc['lon'])
        
        # Try partial match
        for name, data in self.locations.items():
            if location_name in name.lower() or name.lower() in location_name:
                return (data['lat'], data['lon'])
        
        return None

    # -------------------- Simple Loop --------------------

    def run(self):
        self.speak("Voice location manager started.")

        while True:
            command = self.listen(
                "Say save location, list locations, delete location, or exit."
            )

            if not command:
                continue

            if "save" in command:
                self.save_location()
            elif "list" in command:
                self.list_locations()
            elif "delete" in command:
                self.delete_location()
            elif "exit" in command:
                self.speak("Goodbye.")
                break
