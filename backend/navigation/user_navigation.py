import gpsd  # GPS daemon library
# or
from geopy import geocoders  # For address lookup

def get_current_gps():
    """Get current GPS coordinates automatically"""
    try:
        # Connect to GPS daemon (Linux/Android)
        gpsd.connect()
        packet = gpsd.get_current()
        return (packet.lat, packet.lon)
    except:
        return None
