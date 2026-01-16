import pyttsx3
import threading


class ObjectAnnouncer:
    def __init__(self):
        """
        Initializes TTS engine and spoken ID memory.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)   # speech speed
        self.engine.setProperty("volume", 1.0)

        self.spoken_ids = set()
        self.lock = threading.Lock()

    def announce(self, track_id, label, position, distance):
        """
        Announces object details only once per unique track_id.

        Args:
            track_id (int): Unique ByteTrack ID
            label (str): Object class name
            position (str): left / center / right
            distance (str): very near / near / far / very far
        """

        with self.lock:
            if track_id in self.spoken_ids:
                return

            self.spoken_ids.add(track_id)

        message = f"{label} on your {position}, {distance}"

        # Run TTS in background so video processing is not blocked
        threading.Thread(
            target=self._speak,
            args=(message,),
            daemon=True
        ).start()

    def _speak(self, text):
        """
        Speaks the given text.
        """
        self.engine.say(text)
        self.engine.runAndWait()
