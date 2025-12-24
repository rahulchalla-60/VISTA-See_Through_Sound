import subprocess
import os

def build_osrm(map_file="maps/city.osm.pbf"):
    """Build OSRM routing data"""
    
    if not os.path.exists(map_file):
        print(f"Map file {map_file} not found!")
        return
    
    print(f"Building OSRM for {map_file}...")
    
    # Get filename without .osm.pbf
    base_name = map_file.replace('.osm.pbf', '')
    
    # Run the three OSRM steps
    subprocess.run(["osrm-extract", "-p", "/usr/share/osrm-backend/profiles/foot.lua", map_file])
    subprocess.run(["osrm-partition", f"{base_name}.osrm"])
    subprocess.run(["osrm-customize", f"{base_name}.osrm"])
    
    print("Done!")

# Example usage:
# from download_map import download_map
# map_path = download_map("north-america/us/california")
# build_osrm(map_path)

if __name__ == "__main__":
    build_osrm()