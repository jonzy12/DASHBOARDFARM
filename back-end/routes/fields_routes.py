from datetime import timedelta, date, datetime
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from models import FieldCreate
from security import get_current_user


from database import fields_collection
from weather_service import history_weather_from_dateofsowing, weather_future_7days
from agromonitoring import create_agro_polygon, get_all_satellite_data 
from neural_network_ndvi_temp import get_ml_ndvi_predictions

from utils import *

import asyncio 

from ml_service import give_insights




router = APIRouter()
#

@router.post("/add-field")
async def add_field(field: FieldCreate, current_user: str = Depends(get_current_user)):

    polyid = await create_agro_polygon(
        name=field.plot_name,
        lat=field.latitude,
        lon=field.longitude,
        hectares=field.area_size_hectares
    )

    recent_indexes_list = []
    detected_ndvi = 0.0
    detected_trend = "Stable"
    today_str = date.today().strftime("%Y-%m-%d")
    
    if polyid:
        await asyncio.sleep(3) 
        
        satellite_data = await get_all_satellite_data(polyid)
        
        if satellite_data and satellite_data.get("indexes"):
            detected_trend = satellite_data.get("trend", "Stable")
            indexes = satellite_data.get("indexes", {})
            detected_ndvi = indexes.get("ndvi", 0.0) 
            
            recent_indexes_list.append({
                "date": today_str,
                "trend": detected_trend,
                "indexes": indexes
            })
            

    sowing_str = field.sowing_date.strftime("%Y-%m-%d")

    field_dict = {
        "plot_name": field.plot_name,
        "crop_type": field.crop_type,
        "area_size_hectares": field.area_size_hectares,
        "latitude": field.latitude,
        "longitude": field.longitude,
        "owner_id": current_user,
        "sowing_date": sowing_str,
        "polyid": polyid,

        "current_status": {
            "growth_stage": "Unknown",
            "accumulated_gdd": 0.0,      
            "ndvi_trend": detected_trend, 
            "ndvi": detected_ndvi,  
            "last_indexes_update": today_str
        },
        
        "recent_indexes": recent_indexes_list,

        "last_weather_update": None,
        "recent_weather": []
    }

    result = await fields_collection.insert_one(field_dict)
    
    return {
        "message": "field added ", 
        "field_id": str(result.inserted_id), 
        "polyid_created": polyid
    }


@router.get("/fields")
async def get_my_fields(current_user: str = Depends(get_current_user)):


    fields=  await fields_collection.find({"owner_id": current_user}).to_list(length=100)

    
    for field in fields:
        field["_id"] = str(field["_id"])
        
    return fields






@router.get("/field/{field_id}/weather")
async def get_weather_for_field(field_id: str, current_user: str = Depends(get_current_user)):
    
    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID")
        
    field = await fields_collection.find_one({"_id": ObjectId(field_id), "owner_id": current_user})

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    forecast = await weather_future_7days(lat=field.get("latitude"), lon=field.get("longitude"))
    
    if not forecast:
        raise HTTPException(status_code=500, detail="Failed to fetch forecast data")
        

    future_temps=[]
    for day in forecast:
        future_temps.append(day.get("temperatureAVG", 20.0))

    mlpredictions = get_ml_ndvi_predictions(future_temps)
    
    for i in range(len(forecast)):

        if i < len(mlpredictions):
            forecast[i]["ndvi"] = round(mlpredictions[i], 2)
        else:
            forecast[i]["ndvi"] = 0.5 

        forecast[i]["temperatureAVG"] = round(forecast[i].get("temperatureAVG", 20.0), 1)
            
    return {
        "farm_name": field.get("plot_name"), 
        "coordinates": {"lat": field.get("latitude"), "lon": field.get("longitude")},
        "weather": forecast 
    }


#shows me the stress days in a graph with dates
@router.get("/farm/stress-graph")
async def get_farm_stress(current_user: str = Depends(get_current_user)):

    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    
    if not fields:
        return {"chartData": []}

    daily_stress = {} 
    today_str = date.today().strftime("%Y-%m-%d")

    for field in fields:
        
        limits = CROP_STRESS_LEGEND.get(field.get("crop_type", "").lower())
        if not limits:
            continue
            
        weather_data = await get_cached_weather(field)
        if not weather_data:
            continue
            
        for day in weather_data:
            date_str = day.get("date")
            
            if date_str > today_str:
                continue
                
            avgt = day.get("temperatureAVG")
            
            if avgt is not None:
                if avgt > limits["maxTemp"] or avgt < limits["minTemp"]:
                    
                    if date_str not in daily_stress:
                        daily_stress[date_str] = {"date_str": date_str, "high_stress": 0, "low_stress": 0}
                        
                    if avgt > limits["maxTemp"]:
                        daily_stress[date_str]["high_stress"] += 1
                    if avgt < limits["minTemp"]:
                        daily_stress[date_str]["low_stress"] += 1

    chart_data = list(daily_stress.values())        
    chart_data.sort(key=lambda x: x["date_str"]) 
    
    return {"chartData": chart_data}


@router.get("/farm/sum-of-area-hactares")
async def get_farm_area(current_user: str = Depends(get_current_user)):
    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    return {"totalAreaHectares": calc_farm_area(fields)}


@router.get("/farm/amount-of-stressdays")
async def get_farm_stressdays_total(current_user: str = Depends(get_current_user)):

    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    stressdates_no_doubles = set() 
    today_str = date.today().strftime("%Y-%m-%d") 
    
    for f in fields:

        limits = CROP_STRESS_LEGEND.get(f.get("crop_type", "").lower())
        if not limits: 
            continue
            
        weather_data = await get_cached_weather(f) or []
        
        for day in weather_data:
            date_str = day.get("date")
            avgt = day.get("temperatureAVG")
            
            if date_str > today_str or avgt is None:
                continue
                
            if avgt > limits["maxTemp"] or avgt < limits["minTemp"]:
                stressdates_no_doubles.add(date_str) 

    return {"stressdays": len(stressdates_no_doubles)}


@router.get("/farm/effected-hectares")
async def get_farm_effected_hectares(current_user: str = Depends(get_current_user)):
    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    
    effected_hectares = 0
    total_farm_area = calc_farm_area(fields)
    today_str = date.today().strftime("%Y-%m-%d")
    
    for f in fields:

        limits = CROP_STRESS_LEGEND.get(f.get("crop_type", "").lower())
        if not limits:
            continue
            
        weather_data = await get_cached_weather(f) or []
        
        for day in weather_data:
            date_str = day.get("date")
            avgt = day.get("temperatureAVG")
            
            if date_str > today_str or avgt is None:
                continue
                
            if avgt > limits["maxTemp"] or avgt < limits["minTemp"]:
                effected_hectares += f.get("area_size_hectares", 0)
                break 
                    
    return {
        "effected_hectares": round(effected_hectares, 2), 
        "effected_percentage": round((effected_hectares / total_farm_area) * 100, 1) if total_farm_area else 0 
    }

    

@router.get("/farm/ndvi-summary")
async def get_ndvi_summary(current_user: str = Depends(get_current_user)):
    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    
    total_up = 0
    total_stable = 0
    total_down = 0
    
    for field in fields:
        hectares = field.get("area_size_hectares", 0)
        
        status = await get_cached_ndvi(field)
        
        trend = status.get("ndvi_trend", "Stable")
            
        if trend == "Up":
            total_up += hectares
        elif trend == "Down":
            total_down += hectares
        else:
            total_stable += hectares
            
    return [
        {"name": "Up","area": total_up, "value":  total_up, "color": "#00ff00"}, 
        {"name": "Stable", "area": total_stable, "value": total_stable, "color": "#0000ff"}, 
        {"name": "Down", "area": total_down, "value": total_down, "color": "#ff0000"} 
    ]


@router.get("/farm/et0-summary")
async def get_et0_summary(current_user: str = Depends(get_current_user)):

    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    if len(fields) == 0: 
        return []
    


    arr={}   

    chart_data = []  



    for f in fields:


        weatherdata= await get_cached_weather(f) or []

        for day in weatherdata[-10:]:

            
            if day.get("date_str", "") not in arr:
                arr[day.get("date_str", "")] = {"et0": 0, "precip": 0}


            arr[day.get("date_str", "")]["et0"] += day.get("et0", 0)/len(fields)
            arr[day.get("date_str", "")]["precip"] += day.get("precip", 0)/len(fields)



    for day_str, values in arr.items():
        chart_data.append({
            "date_str": day_str,
            "et0": round(values["et0"], 2),     
             "precip": round(values["precip"], 2)
        })

    return chart_data

   


@router.get("/farm/growth-stage-summary")
async def get_growth_stage_summary(current_user: str = Depends(get_current_user)):
    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)
    
    stage_map = {stage: 0.0 for stage in ALL_GROWTH_STAGES}
    stage_map["Unknown"] = 0.0 
    
    for field in fields:
        try:

            stage, gdd= await update_growth_metrics(field) 
        except Exception:
            stage = "Unknown"
            
        if stage not in stage_map:

            stage = "Unknown"
            
        hectares = field.get("area_size_hectares", 0)
        stage_map[stage] += hectares
            
    chart_data = []
    for stage in ALL_GROWTH_STAGES:
        chart_data.append({
            "name": stage,
            "hectares": round(stage_map[stage], 2) 
        })
        
    if stage_map["Unknown"] > 0:
        chart_data.append({
            "name": "Unknown",
            "hectares": round(stage_map["Unknown"], 2)
        })
        
    return chart_data


@router.get("/field/{field_id}/score")
async def get_field_score(field_id: str, current_user: str = Depends(get_current_user)):

    field = await fields_collection.find_one({"_id": ObjectId(field_id), "owner_id": current_user})
    if not field:
        raise HTTPException(status_code=404, detail="Field not found or unauthorized")
    
    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)

    current_stage,gdd= await update_growth_metrics(field) 

    ndvi_trend = (await get_cached_ndvi(field)).get("ndvi_trend", "Stable")


    stress_days = await amount_of_stress_days(field)
    
    score1 = score_on_stressdays_alone_field(stress_days)
    score2 = score_on_growthstage_and_ndviTREND_field(ndvi_trend, current_stage)
    score3 = score_on_hectares_and_growthstage_field(current_stage, get_majority_stage(fields))
    
    return {"score": (score1 + score2 + score3)/3.0, "out_of_number": 1.0}


@router.get("/farm/score")
async def get_farm_score(current_user: str = Depends(get_current_user)):

    fields = await fields_collection.find({"owner_id": current_user}).to_list(length=100)

    if not fields:
        return {"score": 0, "out_of_number": 0}


    total_score = 0

    for field in fields:
        current_stage, gdd = await update_growth_metrics(field) 
        status = await get_cached_ndvi(field)                 
        ndvi_trend = status.get("ndvi_trend", "Stable")
        
        stress_days = await amount_of_stress_days(field)

        score1 = score_on_stressdays_alone_field(stress_days)
        score2 = score_on_growthstage_and_ndviTREND_field(ndvi_trend, current_stage)
        score3 = score_on_hectares_and_growthstage_field(current_stage, get_majority_stage(fields))

        total_score += score1 + score2 + score3

    total_score = total_score / len(fields)

    return {"score": total_score/3.0, "out_of_number": 1.0}




    
@router.get("/field/{field_id}/health")
async def get_field_ml_health(field_id: str, current_user: str = Depends(get_current_user)):

    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID")
    
    field = await fields_collection.find_one({"_id": ObjectId(field_id), "owner_id": current_user})
    if not field:
        raise HTTPException(status_code=404, detail=" no fields")

    recent_indexes = field.get("recent_indexes", [])
    if not recent_indexes:
        return { "message": "no data", "alerts": []}

    latest = recent_indexes[-1].get("indexes", {})
    return give_insights(indexes=latest, crop_type=field.get("crop_type", "unknown"))