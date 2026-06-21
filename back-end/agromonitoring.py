

import asyncio
import math
import time
from datetime import datetime, timedelta



import httpx


AGRO_API_KEY  = "839539276588513b1c5a2595bdbf00e8"
AGRO_BASE     = "http://api.agromonitoring.com/agro/1.0"

MAX_NDVI_RETRIES     = 6      
NDVI_RETRY_DELAY     = 2     
NDVI_CHANGE_THRESHOLD = 0.03


def build_polygon_coords(lat: float, lon: float, hectares: float) -> list:
    area_m2 = hectares * 10_000

    radius = math.sqrt(area_m2 / math.pi)

    lat_offset = radius / 111_320.0
    lon_offset = radius / (111_320.0 * math.cos(math.radians(lat)))

    return [
        [lon - lon_offset, lat + lat_offset],
        [lon + lon_offset, lat + lat_offset],
        [lon + lon_offset, lat - lat_offset],
        [lon - lon_offset, lat - lat_offset],
        [lon - lon_offset, lat + lat_offset],
    ]







async def create_agro_polygon(name: str, lat: float, lon: float, hectares: float):

    payload = {
        "name": name,
        "geo_json": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [build_polygon_coords(lat, lon, hectares)]
            }
        }
    }

    async with httpx.AsyncClient() as client:
        
        response = await client.post(f"{AGRO_BASE}/polygons?appid={AGRO_API_KEY}",json=payload)
        if response.status_code in (200, 201):
             poly_id = response.json().get("id")
             return poly_id



    return None


async def fetch_mean_indexes(client: httpx.AsyncClient, stats_url: str) -> float:

    for nothin in range( MAX_NDVI_RETRIES ):
        response = await client.get(stats_url)

        if response.status_code == 200:
            return response.json().get("mean", 0.0)

        if response.status_code == 202:
            await asyncio.sleep(NDVI_RETRY_DELAY)
            continue

        break

    return 0.0





async def fetch_images(client: httpx.AsyncClient, polyid: str) -> list:

    start = int((datetime.now() - timedelta(days=7)).timestamp())
    end   = int(time.time()) -300

    url      = f"{AGRO_BASE}/image/search?start={start}&end={end}&polyid={polyid}&appid={AGRO_API_KEY}"
    response = await client.get(url)
    images = response.json()

    if not isinstance(images, list):
        return []



        
    return sorted(images, key=lambda img: img["dt"])





async def get_all_satellite_data(polyid: str, last_saved_ndvi: float = 0.0) -> dict:

    if not polyid:
        return {"trend": "Stable", "indexes": {}}

    async with httpx.AsyncClient() as client:
        try:
            images = await fetch_images(client, polyid)

            if not images:
                return {"trend": "Stable", "indexes": {}}

            cleanest = sorted(images, key=lambda img: img.get("cl", 100))[0]

            stats = cleanest.get("stats", {})
            
            tasks = {}
            for index_name, url in stats.items():
                tasks[index_name] = fetch_mean_indexes(client, url)

            keys = list(tasks.keys())
            results = await asyncio.gather(*[tasks[k] for k in keys])
            
            resolved_stats = {keys[i]: round(results[i], 3) for i in range(len(keys))}

            new_ndvi = resolved_stats.get("ndvi", 0.0)
            
            trend = "Stable"
            if last_saved_ndvi > 0:
                diff = new_ndvi - last_saved_ndvi
                if diff > NDVI_CHANGE_THRESHOLD: trend = "Up"
                elif diff < -NDVI_CHANGE_THRESHOLD: trend = "Down"

            return {
                "trend": trend,
                "indexes": resolved_stats 
            }

        except Exception :
            return {"trend": "Stable", "indexes": {}}
        


