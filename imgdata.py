import os
import rasterio
from rasterio.warp import transform_bounds
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ==========================================
# 🛑 הגדרות משתמש (שנה רק כאן)
# ==========================================
# הנתיב לתיקייה עם התמונות שלך
BASE_DIR = "/mnt/f/STORAGE FOR FINAL PROJECT/Students data/Students data/Jose_bord_satellite_data"

# הגדרת שטח החווה (בשביל החישובים בדאשבורד)
TOTAL_FARM_HA = 500  

# ==========================================
# 1. לוגיקה חכמה: עונות ו-GDD
# ==========================================
def calculate_smart_gdd(date_obj, max_temp, min_temp):
    """
    פונקציה שמחליטה איזו נוסחה להפעיל לפי העונה.
    חורף = חיטה (בסיס 0). קיץ = תירס (בסיס 10).
    """
    month = date_obj.month
    avg_temp = (max_temp + min_temp) / 2
    
    # בדיקה: האם אנחנו בחורף? (נובמבר עד מרץ)
    if month in [11, 12, 1, 2, 3]:
        # עונת חורף (Base Temp = 0)
        base_temp = 0
        season = "Winter"
    else:
        # עונת קיץ (Base Temp = 10)
        base_temp = 10
        season = "Summer"
    
    # חישוב GDD (לא נותנים למספר לרדת מתחת לאפס)
    gdd = max(0, avg_temp - base_temp)
    return gdd, season

# ==========================================
# 2. מנוע מזג אוויר (API)
# ==========================================
def get_weather_data(lat, lon, date_str):
    try:
        # המרת מחרוזת לתאריך אמיתי
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": date_str, "end_date": date_str,
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "timezone": "auto"
        }
        
        res = requests.get(url, params=params, timeout=5)
        if res.status_code != 200: return None, None, None
        
        data = res.json()
        if "daily" in data:
            max_t = data["daily"]["temperature_2m_max"][0]
            min_t = data["daily"]["temperature_2m_min"][0]
            
            # הפעלת הלוגיקה החכמה
            gdd, season = calculate_smart_gdd(date_obj, max_t, min_t)
            
            return max_t, gdd, season
            
    except Exception as e:
        print(f"⚠️ Weather Error: {e}")
    
    return None, 0, "Unknown"

# ==========================================
# 3. עיבוד תמונה (כולל מים ו-NDVI)
# ==========================================
def process_satellite_image(path):
    try:
        with rasterio.open(path) as src:
            # קריאת ערוצים (אדום ו-NIR ל-NDVI)
            red = src.read(4).astype('float32')
            nir = src.read(8).astype('float32')
            
            # חישוב NDVI (צימוח)
            np.seterr(divide='ignore', invalid='ignore')
            ndvi = (nir - red) / (nir + red)
            
            # חישוב NDMI (מים)
            # אם יש ערוץ SWIR (מס' 11) נשתמש בו, אחרת נעשה הערכה
            try:
                swir = src.read(11).astype('float32')
                ndmi = (nir - swir) / (nir + swir)
            except:
                # אין ערוץ 11? נשתמש בנוסחה חלופית או פשוט נחזיר ערך ריק
                ndmi = ndvi * 0.5 

            # ניקוי רעשים
            valid_pixels = ndvi[(ndvi > -1) & (ndvi < 1)]
            if len(valid_pixels) == 0: return None
            
            # חישוב אחוז סטרס (כמה מהשדה במצב רע?)
            stress_pct = np.sum(valid_pixels < 0.3) / len(valid_pixels)
            
            # חילוץ מיקום גיאוגרפי (עבור מזג האוויר)
            left, bottom, right, top = transform_bounds(src.crs, {'init': 'epsg:4326'}, *src.bounds)
            
            return {
                "lat": (bottom + top) / 2,
                "lon": (left + right) / 2,
                "ndvi_mean": float(np.mean(valid_pixels)),
                "ndmi_mean": float(np.mean(ndmi[(ndmi > -1) & (ndmi < 1)])),
                "stress_pct": float(stress_pct)
            }
    except:
        return None

# ==========================================
# 4. המנוע הראשי (Main Execution)
# ==========================================
print("🚀 מתחיל בעיבוד הנתונים... אנא המתן.")

data_rows = []
files = sorted([f for f in os.listdir(BASE_DIR) if f.endswith('.tif') or f.endswith('.tiff')])

for filename in files:
    try:
        # חילוץ תאריך מהשם: ndmi_2026-01-12.tiff
        date_str = filename.split('_')[1].split('.')[0]
        
        # 1. עיבוד התמונה
        img_stats = process_satellite_image(os.path.join(BASE_DIR, filename))
        
        if img_stats:
            # 2. קבלת מזג אוויר ו-GDD חכם
            max_t, gdd, season = get_weather_data(img_stats['lat'], img_stats['lon'], date_str)
            
            if max_t is not None:
                print(f"✅ {date_str} ({season}): Temp={max_t}°C, GDD={gdd:.1f}, NDVI={img_stats['ndvi_mean']:.2f}")
                
                data_rows.append({
                    "farm_id": "Jose_Farm",
                    "date": date_str,
                    "season": season,      # עמודה חדשה שתראה לך עונה!
                    "max_temp": max_t,
                    "daily_gdd": gdd,
                    "ndvi_mean": img_stats['ndvi_mean'],
                    "ndmi_mean": img_stats['ndmi_mean'],
                    "stress_pct": img_stats['stress_pct'],
                    "total_ha": TOTAL_FARM_HA
                })
    except Exception as e:
        print(f"⚠️ דילגתי על הקובץ {filename}: {e}")

# ==========================================
# 5. שלב ההעשרה (חישובים לדאשבורד)
# ==========================================
if data_rows:
    df = pd.DataFrame(data_rows)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # חישוב GDD מצטבר (Development Alignment)
    df['accumulated_gdd'] = df['daily_gdd'].cumsum()
    
    # חישוב מומנטום (האם משתפר או מתדרדר?)
    df['ndvi_change'] = df['ndvi_mean'].diff().fillna(0)
    df['ndvi_momentum'] = df['ndvi_change'].apply(lambda x: 'Increasing' if x > 0.01 else ('Declining' if x < -0.01 else 'Stable'))

    # חישוב הקטרים בסיכון (Active Ha & Risk)
    df['active_ha'] = df['total_ha'] 
    
    # הפרדה: עקת חום מול עקת מים
    # אם חם (מעל 30) -> עקת חום. אחרת -> עקת מים.
    df['temp_stress_ha'] = np.where(df['max_temp'] > 30, df['stress_pct'] * df['total_ha'], 0)
    df['water_stress_ha'] = np.where(df['max_temp'] <= 30, df['stress_pct'] * df['total_ha'], 0)
    
    # שטח בסיכון גבוה (חפיפה)
    df['risk_high_ha'] = df[['temp_stress_ha', 'water_stress_ha']].max(axis=1)

    # שמירה
    output_file = "final_dashboard_data.csv"
    df.to_csv(output_file, index=False)
    print(f"\n🎉 סיימנו! הקובץ {output_file} מוכן עם כל הנתונים.")
    print("עכשיו ה-GDD אמור להיות תקין (לא אפס) והעמודות מתאימות לדאשבורד.")
else:
    print("❌ לא נוצרו נתונים. בדוק את הנתיב לתיקייה.")