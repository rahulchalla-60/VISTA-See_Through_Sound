import subprocess
import os

def start_server(osrm_file="maps/city.osrm"):
    """Start OSRM routing server"""
    
    if not os.path.exists(osrm_file):
        print(f"OSRM file {osrm_file} not found!")
        return
    
    print(f"Starting OSRM server with {osrm_file}...")
    
    subprocess.run([
        "osrm-routed",
        "--algorithm", "mld",
        osrm_file
    ])

# Example usage:
# from download_map import download_map
# from build_osrm import build_osrm
# 
# map_path = download_map("north-america/us/california")
# build_osrm(map_path)
# osrm_path = map_path.replace('.osm.pbf', '.osrm')
# start_server(osrm_path)

if __name__ == "__main__":
    start_server()
