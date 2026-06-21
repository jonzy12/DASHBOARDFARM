import httpx
from datetime import datetime, date


async def history_weather_from_dateofsowing(lat: float, lon: float, sowing_date_str: str = None):
    
    thingstoget_his = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "et0_fao_evapotranspiration", "precipitation_sum"], 
        "past_days": how_many_days_from_seeding(sowing_date_str), 
        "forecast_days": 1, 
        "timezone": "auto"
    }
    return await fetch_weather_from_api(thingstoget_his)


async def weather_future_7days(lat: float, lon: float):
    
    thingstoget_Fut = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "et0_fao_evapotranspiration", "precipitation_sum"], 
        "past_days": 0,      
        "forecast_days": 7,  
        "timezone": "auto"
    }
    return await fetch_weather_from_api(thingstoget_Fut)



async def fetch_weather_from_api(params: dict):
    url = "https://api.open-meteo.com/v1/forecast"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return format_weather_response(response.json())
            
            return None
                
        except Exception as e:
            return None
        


def how_many_days_from_seeding(sowing_date_str: str) -> int:
    if not sowing_date_str:
        return 0
    try:
        sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d").date()
        days_between = (date.today() - sowing_date).days
        return min(days_between, 90) 
    except Exception:
        return 0
    


def format_weather_response(data: dict) -> list:
    daily = data["daily"]
    return [
        {
            "date": daily["time"][i], 
            "date_str": datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%a, %d"), 
            "temperatureAVG": (daily["temperature_2m_max"][i] + daily["temperature_2m_min"][i]) / 2,
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i],
            "et0": daily["et0_fao_evapotranspiration"][i],
            "precip": daily["precipitation_sum"][i]
        }
        for i in range(len(daily["time"]))
    ]