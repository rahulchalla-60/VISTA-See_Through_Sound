import requests
import math
from typing import Tuple, List

def get_route(start: Tuple[float, float], end: Tuple[float, float]) -> dict:
    """Get route from OSRM server"""
    lat1, lon1 = start
    lat2, lon2 = end
    
    url = f"http://localhost:5000/route/v1/foot/{lon1},{lat1};{lon2},{lat2}?steps=true"
    
    try:
        response = requests.get(url)
        return response.json()
    except:
        return {}

def get_instructions(start: Tuple[float, float], end: Tuple[float, float]) -> List[str]:
    """Get turn-by-turn navigation instructions"""
    data = get_route(start, end)
    
    if not data or "routes" not in data:
        return ["No route found"]
    
    try:
        steps = data["routes"][0]["legs"][0]["steps"]
        return [step["maneuver"]["instruction"] for step in steps]
    except:
        return ["Error getting instructions"]

def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate distance between two GPS points in meters"""
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    
    # Simple distance calculation
    R = 6371000  # Earth radius in meters
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
    
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def navigate(start: Tuple[float, float], end: Tuple[float, float]):
    """Simple navigation function"""
    instructions = get_instructions(start, end)
    
    print(f"Navigation from {start} to {end}")
    print(f"Distance: {calculate_distance(start, end):.0f} meters")
    print("\nInstructions:")
    
    for i, instruction in enumerate(instructions, 1):
        print(f"{i}. {instruction}")
    
    return instructions

# Example usage
if __name__ == "__main__":
    start = (37.7749, -122.4194)  # San Francisco
    end = (37.7849, -122.4094)    # Nearby location
    
    navigate(start, end)
