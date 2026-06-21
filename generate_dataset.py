import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import rasterio
from rasterio.transform import from_origin

def generate_professional_dataset():
    output_dir = "Simulated_Farm_Data"
    os.makedirs(output_dir, exist_ok=True)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    dates = []
    temps = []
    ndvis = []

    current_date = start_date
    print("🌱 מייצר נתונים היסטוריים (טמפרטורה + NDVI) עם סטיית תקן (STD)...")

    while current_date <= end_date:
        doy = current_date.timetuple().tm_yday # היום בשנה (1-365)

        # 1. יצירת טמפרטורה: כמו בקובץ שלך (חורף קר, קיץ חם)
        # שיא הקור בינואר (יום 20), שיא החום ביולי-אוגוסט
        temp_mean = 22.5 - 10.5 * np.cos(2 * np.pi * (doy - 20) / 365)
        temp_std = 2.0 # סטיית תקן של 2 מעלות
        final_temp = np.random.normal(temp_mean, temp_std)
        final_temp = round(final_temp, 1)

        # 2. יצירת NDVI עונתי הגיוני: ירוק באביב (אזור יום 80), יבש בסוף הקיץ
        ndvi_mean = 0.5 + 0.3 * np.cos(2 * np.pi * (doy - 80) / 365)
        ndvi_std = 0.05 # סטיית תקן מציאותית ללוויינים
        final_ndvi = np.random.normal(ndvi_mean, ndvi_std)
        # חותכים את הערך כדי שלא יעבור את גבולות ה-NDVI האפשריים (0 עד 1)
        final_ndvi = round(np.clip(final_ndvi, 0.1, 0.95), 3)

        date_str = current_date.strftime("%Y-%m-%d")

        dates.append(date_str)
        temps.append(final_temp)
        ndvis.append(final_ndvi)

        # 3. יצירת תמונת ה-TIFF עבור המודל (מבוסס על ה-NDVI שיצרנו)
        filename = os.path.join(output_dir, f"ndvi_{date_str}.tiff")
        
        # התמונה עצמה גם תקבל קצת רעש טבעי בין הפיקסלים (STD של 0.08)
        img_data = np.random.normal(final_ndvi, 0.08, (64, 64)).astype(np.float32)
        img_data = np.clip(img_data, 0.0, 1.0) 

        transform = from_origin(34.0, 32.0, 10, 10)
        with rasterio.open(
            filename, 'w', driver='GTiff',
            height=64, width=64, count=1, dtype=str(img_data.dtype),
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(img_data, 1)

        # קפיצה של 4 או 5 ימים קדימה (אינטרוול רנדומלי כמו שביקשת)
        jump_days = int(np.random.choice([4, 5]))
        current_date += timedelta(days=jump_days)

    # 4. שמירת הנתונים ל-CSV
    df = pd.DataFrame({
        "Date": dates,
        "Temperature": temps,
        "NDVI": ndvis
    })
    csv_filename = "realistic_farm_data.csv"
    df.to_csv(csv_filename, index=False)

    print(f"✅ סיימתי! נוצרו {len(dates)} רשומות/תמונות.")
    print(f"📁 התמונות נשמרו בתיקייה: {output_dir}")
    print(f"📄 קובץ הנתונים נשמר בשם: {csv_filename}")

if __name__ == "__main__":
    generate_professional_dataset()