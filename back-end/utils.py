from weather_service import history_weather_from_dateofsowing, weather_future_7days
from datetime import timedelta, date, datetime
from database import fields_collection
from agromonitoring import *

CROP_STRESS_LEGEND = {
    "corn": {"minTemp": 10, "maxTemp": 30},
    "wheat": {"minTemp": 5, "maxTemp": 25},
    "rice": {"minTemp": 15, "maxTemp": 35},
    "soybeans": {"minTemp": 10, "maxTemp": 30},
    "cotton": {"minTemp": 15, "maxTemp": 38},
    "tomato": {"minTemp": 10, "maxTemp": 32},
    "potato": {"minTemp": 5, "maxTemp": 25},
    "apple": {"minTemp": -2, "maxTemp": 30},
    "grape": {"minTemp": 5, "maxTemp": 35},
    "lettuce": {"minTemp": 5, "maxTemp": 25}
}

ALL_GROWTH_STAGES = [
    "VE",
    "V1-V5",
    "V6-V7",
    "V8-Vn",
    "VT (Tassel)",
    "R1 (Silk)",
    "R2 (Blister)",
    "R3 (Milk)",
    "R4 (Dough)",
    "R5 (Dent)",
    "R6 (Maturity)"
]


CORN_GDD_STAGES = [
    ("VE", 80),
    ("V1-V5", 310),
    ("V6-V7", 400),
    ("V8-Vn", 570),
    ("VT (Tassel)", 749),
    ("R1 (Silk)", 810),
    ("R2 (Blister)", 950),
    ("R3 (Milk)", 1070),
    ("R4 (Dough)", 1200),
    ("R5 (Dent)", 1450),
    ("R6 (Maturity)", 1750)
]


def calc_daily_gdd_corn(maxitemp: float, minitemp: float) -> float:
    if maxitemp is None or minitemp is None:
        return 0.0
        
    maxitemp = min(maxitemp, 30.0) 
    minitemp = max(minitemp, 10.0)
    
    avg = (maxitemp + minitemp) / 2
    gdd = avg - 10.0  
    
    
    return max(0.0, gdd)


def calculate_current_growth_stage(weather_history: list, crop_type: str) -> tuple[str, float]:
    if crop_type.lower() != "corn":
        return "Unknown", 0.0 
        
    accugdd = 0.0
    
    for day in weather_history:
        maxitemp = day.get("max_temp")
        minitemp = day.get("min_temp")
        accugdd += calc_daily_gdd_corn(maxitemp, minitemp)
        
    current_stage = "VE"
    for stage, max_gdd in CORN_GDD_STAGES:
        if accugdd <= max_gdd:
            current_stage = stage
            break
            
    if accugdd > 1750:
        current_stage = "R6 (Maturity)"
        
    return current_stage, round(accugdd, 2)


async def update_growth_metrics(field: dict) -> tuple[str, float]:
    today_str = date.today().strftime("%Y-%m-%d")
    
    weather_history = [day for day in field.get("recent_weather", []) if day.get("date", "") <= today_str]

    crop_type = field.get("crop_type", "unknown")
    
    real_growth_stage, accumulated_gdd = calculate_current_growth_stage(weather_history, crop_type)
    
    if "_id" in field:
        await fields_collection.update_one(
            {"_id": field["_id"]},
            {"$set": {
                "current_status.growth_stage": real_growth_stage,
                "current_status.accumulated_gdd": accumulated_gdd
            }}
        )
        
    return real_growth_stage, accumulated_gdd

async def get_cached_weather(field: dict) -> list:
    today_str = date.today().strftime("%Y-%m-%d")
    
    last_update = field.get("last_weather_update", "1900-01-01")
    
    if last_update == today_str:
        return field.get("recent_weather", [])
        
    existing_weather = field.get("recent_weather", [])
    

    historical_db = [day for day in existing_weather if day["date"] < last_update]
    
    fresh_data = await history_weather_from_dateofsowing(
        field.get("latitude"), 
        field.get("longitude"), 
        field.get("sowing_date")
    ) or []
    
    if fresh_data:
        last_saved_date = historical_db[-1]["date"] if historical_db else "1900-01-01"
        
  
        new_days = [day for day in fresh_data if last_saved_date < day["date"] <= today_str]
        
        updated_weather = historical_db + new_days

        
        field["last_weather_update"] = today_str
        field["recent_weather"] = updated_weather
        
        if "_id" in field:
            await fields_collection.update_one(
                {"_id": field["_id"]},
                {"$set": {
                    "recent_weather": updated_weather,
                    "last_weather_update": today_str
                }}
            )
        return updated_weather
        
    return existing_weather




async def get_cached_ndvi(field: dict) -> dict:
    current_status = field.get("current_status", {})
    last_update_str = current_status.get("last_indexes_update") 
    today_str = date.today().strftime("%Y-%m-%d")
    
    if last_update_str:
        last_update = datetime.strptime(last_update_str, "%Y-%m-%d")
        if (datetime.now() - last_update).days < 8 and current_status.get("ndvi_trend") != "Unknown":
            return {
                "ndvi_trend": current_status.get("ndvi_trend", "Stable"),
                "ndvi": current_status.get("ndvi", 0.0) 
            }

    polyid = field.get("polyid")
    if not polyid:
        return {"ndvi_trend": "Stable", "ndvi": 0.0}
        
    satellite_data = await get_all_satellite_data(polyid, current_status.get("ndvi", 0.0)) 
    
    new_trend = satellite_data.get("trend", "Stable")
    new_indexes = satellite_data.get("indexes", {})
    new_ndvi = new_indexes.get("ndvi", 0.0)
    

    if "_id" in field and new_ndvi > 0:
        await fields_collection.update_one(
            {
                "_id": field["_id"],
                "current_status.last_indexes_update": {"$ne": today_str}
            },
            {
                "$set": {
                    "current_status.ndvi_trend": new_trend,
                    "current_status.ndvi": new_ndvi,
                    "current_status.last_indexes_update": today_str
                },
                "$push": {
                    "recent_indexes": {
                        "date": today_str, 
                        "trend": new_trend, 
                        "indexes": new_indexes
                    }
                }
            }
        )
        return {"ndvi_trend": new_trend, "ndvi": new_ndvi}
    
    return {
        "ndvi_trend": current_status.get("ndvi_trend", "Stable"),
        "ndvi": current_status.get("ndvi", 0.0)
    }


def calc_farm_area(fields):
    total_area = 0
    for f in fields:
        total_area += f.get("area_size_hectares", 0)
    return total_area

async def amount_of_stress_days(field: dict) -> int:

    crop_type = (field.get("crop_type") or "").lower()
    limits    = CROP_STRESS_LEGEND.get(crop_type)
    lat       = field.get("latitude")
    lon       = field.get("longitude")

    if not limits or not lat or not lon:
        return 0

    weather_data = await get_cached_weather(field) or []
    today_str    = date.today().strftime("%Y-%m-%d")

    stress_days = 0

    for day in weather_data:
        date_str = day.get("date")
        maxtemp   = day.get("max_temp")
        mintemp= day.get("min_temp")

        if not date_str or date_str > today_str or maxtemp is None or mintemp is None:
            continue

        if maxtemp > limits["maxTemp"] or mintemp < limits["minTemp"]:
            stress_days += 1

    return stress_days

# הוראות לגבי ניקוד מטעם החברה לגבי כל חישוב הציון לא החלטה שלי 

def score_on_stressdays_alone_field(stressdays):
    if stressdays == 0:
        return 1
    elif stressdays > 0 and stressdays <= 30:
        return 0.75
    elif stressdays > 30 and stressdays <= 50:
        return 0.5
    elif stressdays > 50 and stressdays <= 80:
        return 0.25
    else:       
        return 0

def score_on_growthstage_and_ndviTREND_field(trend, stage):
    if stage in ["VE", "V1-V5"]:
        if trend == "Up": return 1
        elif trend == "Stable": return 0.5
        return 0
    elif stage in ["V6-V7", "V8-Vn", "VT (Tassel)"]:
        if trend == "Up": return 1
        elif trend == "Stable": return 0.5    
        return 0
    elif stage in [ "R1 (Silk)","R2 (Blister)"]:
        if trend == "Up": return 1
        elif trend == "Stable": return 0.5
        return 0
    else:  
        if trend == "Up": return 0.5
        elif trend == "Stable": return 0.5
        return 0

def score_on_hectares_and_growthstage_field(stagefiled, majority_stage):
    if stagefiled not in ALL_GROWTH_STAGES or majority_stage not in ALL_GROWTH_STAGES:
        return 0

    field_index = ALL_GROWTH_STAGES.index(stagefiled)
    majority_index = ALL_GROWTH_STAGES.index(majority_stage)
    
    distance = abs(majority_index - field_index)
    
    if distance == 0:
        return 1
    elif distance == 1:
        return 0.5
    return 0

def get_majority_stage(fields: list) -> str:
    stage_hectares = {}
    for f in fields:
        stage  = f.get("current_status", {}).get("growth_stage", "Unknown")
        
        if stage != "Unknown":
            stage_hectares[stage] = stage_hectares.get(stage, 0) + f.get("area_size_hectares", 0)


            
    return max(stage_hectares, key=stage_hectares.get) if stage_hectares else "Unknown"















