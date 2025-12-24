import json
import os
from datetime import datetime
import speech_recognition as sr
import pyttsx3

class OfflineVoiceLocationSaver:
    def __init__(self, file="navigation/saved_locations.json"):
        self.file = file
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.tts = pyttsx3.init()
        self.locations = self._load()

    # ---------- STORAGE ----------
    def _load(self):
        """Load locations in format compatible with offline_navigation.py"""
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                data = json.load(f)
                # Convert from list format to dict format if needed
                if isinstance(data, list):
                    return self._convert_list_to_dict(data)
                return data
        return {}

    def _convert_list_to_dict(self, location_list):
        """Convert old list format to new dict format"""
        result = {}
        for item in location_list:
            name = item['name'].lower().replace(' ', '_')
            result[name] = {
                "lat": item['latitude'],
                "lon": item['longitude'],
                "description": item['name'],
                "saved_at": item.get('saved_at', datetime.now().isoformat())
            }
        return result

    def _save(self):
        """Save locations"""
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, "w") as f:
            json.dump(self.locations, f, indent=2)

    # ---------- VOICE (OFFLINE) ----------
    def speak(self, text):
        """Text-to-speech (offline)"""
        print(f"🔊 {text}")
        self.tts.say(text)
        self.tts.runAndWait()

    def listen_offline(self, prompt):
        """Listen using offline speech recognition"""
        self.speak(prompt)
        
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, 1)
            
        try:
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            # Try offline recognition first (if available)
            try:
                # Sphinx works offline but has limited accuracy
                text = self.recognizer.recognize_sphinx(audio)
                print(f"You said (offline): {text}")
                return text.strip()
            except:
                # Fallback to online if absolutely necessary
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"You said (online): {text}")
                    return text.strip()
                except:
                    self.speak("Could not understand. Please try again.")
                    return None
                    
        except sr.WaitTimeoutError:
            self.speak("No speech detected. Please try again.")
            return None
        except Exception as e:
            self.speak("Error with microphone.")
            return None

    # ---------- GPS (OFFLINE METHODS) ----------
    def get_location_manual(self):
        """Manual coordinate input"""
        self.speak("GPS not available. Please provide coordinates manually.")
        
        try:
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            return lat, lon
        except ValueError:
            self.speak("Invalid coordinates.")
            return None, None

    def get_location_from_saved(self):
        """Select from existing saved locations"""
        if not self.locations:
            self.speak("No saved locations available.")
            return None, None
            
        self.speak("Choose from existing locations:")
        location_names = list(self.locations.keys())
        
        for i, name in enumerate(location_names, 1):
            desc = self.locations[name].get('description', name)
            print(f"{i}. {desc}")
        
        try:
            choice = int(input("Enter number: ")) - 1
            if 0 <= choice < len(location_names):
                selected = self.locations[location_names[choice]]
                return selected['lat'], selected['lon']
        except:
            pass
            
        return None, None

    def get_location_gps(self):
        """Try to get GPS location (offline methods only)"""
        # Try GPSD (Linux/Android GPS daemon)
        try:
            import gpsd
            gpsd.connect()
            packet = gpsd.get_current()
            if packet.mode >= 2:  # 2D fix or better
                self.speak(f"GPS location acquired: {packet.lat:.6f}, {packet.lon:.6f}")
                return packet.lat, packet.lon
        except:
            pass

        # Try Android GPS (if running on Android with appropriate libraries)
        try:
            from plyer import gps
            gps.configure(on_location=self._on_gps_location)
            gps.start(minTime=1000, minDistance=1)
            # This would need a callback system for real implementation
        except:
            pass

        return None, None

    def get_location(self):
        """Get location using available offline methods"""
        self.speak("Getting your location...")
        
        # Try GPS first
        lat, lon = self.get_location_gps()
        if lat and lon:
            return lat, lon
        
        # Ask user for method
        self.speak("GPS not available. Choose input method:")
        print("1. Manual coordinates")
        print("2. Select from saved locations")
        
        choice = input("Choose (1-2): ").strip()
        
        if choice == "1":
            return self.get_location_manual()
        elif choice == "2":
            return self.get_location_from_saved()
        else:
            self.speak("Invalid choice.")
            return None, None

    # ---------- MAIN FUNCTIONS ----------
    def save_current_location(self):
        """Save current location with voice input"""
        self.speak("Let's save your current location.")
        
        # Get location name via voice
        name = self.listen_offline("Say the location name, like Home, Work, or Bus Stop")
        if not name:
            self.speak("No location name provided. Cancelled.")
            return False

        # Get coordinates
        lat, lon = self.get_location()
        if lat is None or lon is None:
            self.speak("Could not get location coordinates. Cancelled.")
            return False

        # Save location
        key = name.lower().replace(' ', '_')
        self.locations[key] = {
            "lat": lat,
            "lon": lon,
            "description": name,
            "saved_at": datetime.now().isoformat()
        }

        self._save()
        self.speak(f"Successfully saved {name} at coordinates {lat:.6f}, {lon:.6f}")
        return True

    def list_locations(self):
        """List all saved locations"""
        if not self.locations:
            self.speak("No saved locations.")
            return

        self.speak("Here are your saved locations:")
        print("\n📍 Saved Locations:")
        
        for key, data in self.locations.items():
            desc = data.get('description', key)
            lat, lon = data['lat'], data['lon']
            saved_at = data.get('saved_at', 'Unknown')
            print(f"• {desc}: {lat:.6f}, {lon:.6f} (saved: {saved_at[:10]})")

    def delete_location(self):
        """Delete a saved location"""
        if not self.locations:
            self.speak("No locations to delete.")
            return

        self.list_locations()
        name = self.listen_offline("Say the name of the location to delete")
        
        if not name:
            return

        key = name.lower().replace(' ', '_')
        
        # Try exact match first
        if key in self.locations:
            del self.locations[key]
            self._save()
            self.speak(f"Deleted {name}")
            return
        
        # Try partial match
        for existing_key in list(self.locations.keys()):
            if key in existing_key or existing_key in key:
                desc = self.locations[existing_key].get('description', existing_key)
                confirm = input(f"Delete '{desc}'? (y/n): ").lower()
                if confirm == 'y':
                    del self.locations[existing_key]
                    self._save()
                    self.speak(f"Deleted {desc}")
                return
        
        self.speak(f"Location {name} not found.")

    def interactive_mode(self):
        """Interactive voice-controlled location management"""
        self.speak("Welcome to Voice Location Saver")
        
        while True:
            self.speak("What would you like to do?")
            print("\nOptions:")
            print("1. Save current location")
            print("2. List saved locations") 
            print("3. Delete a location")
            print("4. Exit")
            
            choice = input("Choose (1-4) or say your choice: ").strip()
            
            if choice == "1":
                self.save_current_location()
            elif choice == "2":
                self.list_locations()
            elif choice == "3":
                self.delete_location()
            elif choice == "4":
                self.speak("Goodbye!")
                break
            else:
                # Try voice command
                command = self.listen_offline("Say: save location, list locations, delete location, or exit")
                if command:
                    if "save" in command.lower():
                        self.save_current_location()
                    elif "list" in command.lower():
                        self.list_locations()
                    elif "delete" in command.lower():
                        self.delete_location()
                    elif "exit" in command.lower():
                        self.speak("Goodbye!")
                        break

if __name__ == "__main__":
    saver = OfflineVoiceLocationSaver()
    saver.interactive_mode()