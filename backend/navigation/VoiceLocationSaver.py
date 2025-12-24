import json
import os
from datetime import datetime
import speech_recognition as sr


class VoiceLocationSaver:
    def __init__(self, file="saved_locations.json"):
        self.file = file
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.locations = self._load()

    # ---------- STORAGE ----------
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.file, "w") as f:
            json.dump(self.locations, f, indent=2)

    # ---------- VOICE ----------
    def listen(self, prompt):
        print(f"\n🎤 {prompt}")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, 1)
            audio = self.recognizer.listen(source, timeout=5)

        try:
            text = self.recognizer.recognize_google(audio)
            print("You said:", text)
            return text.strip()
        except:
            print("Could not understand.")
            return None

    # ---------- GPS ----------
    def get_location(self):
        # Try GPSD (best)
        try:
            import gpsd
            gpsd.connect()
            p = gpsd.get_current()
            return p.lat, p.lon
        except:
            pass

        # Try IP location
        try:
            import geocoder
            g = geocoder.ip("me")
            if g.ok:
                return g.latlng
        except:
            pass

        # Manual fallback
        lat = float(input("Latitude: "))
        lon = float(input("Longitude: "))
        return lat, lon

    # ---------- MAIN ----------
    def save_current_location(self):
        name = self.listen("Say location name (Home, Bus Stop, etc)")
        if not name:
            return

        lat, lon = self.get_location()

        entry = {
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "saved_at": datetime.now().isoformat()
        }

        self.locations.append(entry)
        self._save()

        print(f"✅ Saved {name} @ {lat:.6f}, {lon:.6f}")

    def list_locations(self):
        if not self.locations:
            print("No saved locations.")
            return

        print("\n📍 Saved Locations:")
        for i, l in enumerate(self.locations, 1):
            print(f"{i}. {l['name']} → {l['latitude']:.6f}, {l['longitude']:.6f}")
