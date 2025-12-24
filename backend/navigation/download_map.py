import requests, os

def download_map(region):
    url = f"https://download.geofabrik.de/{region}-latest.osm.pbf"
    os.makedirs("maps", exist_ok=True)
    safe_region = region.replace('/', '_').replace('\\', '_')
    path = f"maps/{safe_region}.osm.pbf"

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

    return path
