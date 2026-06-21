import os
import asyncio
import numpy as np
import pandas as pd
from keras.models import Sequential, load_model
from keras.layers import Dense
from database import fields_collection

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "farm_ndvi_model.keras")
CSV_PATH   = os.path.join(BASE_DIR, "csvuploads", "agrodata.csv")


async def collect_training_data():
    temps=[] 
    ndvis =  []

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        temps.extend(df['Temperature'].values / 50.0)
        ndvis.extend(df['NDVI'].values)


    try:
        fields = await fields_collection.find({}).to_list(length=None)
        for f in fields:
            if (f.get("crop_type", "").lower() != "corn"):
                continue

            ndvi = f.get("current_status", {}).get("ndvi", 0)
            weather = f.get("recent_weather", [])
            if ndvi > 0 and weather:

                last = weather[-1]

                if last.get("temperatureAVG") is not None :

                    t=max(0.0, last.get("temperatureAVG"))

                    temps.append(t / 50.0)
                    ndvis.append(ndvi)

    except Exception as e:
        print(f"error with data {e}")


    return np.array(temps).reshape(-1, 1), np.array(ndvis)


async def train_model():
    temps, ndvis = await collect_training_data()



    if len(temps) == 0:
        print("No data to train on.")
        return

    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        epochs = 50
    else:
        model = Sequential([
            Dense(16, activation='relu', input_shape=(1,)),
            Dense(16, activation='relu'),
            Dense(16,  activation='relu'),
            Dense(1,  activation='sigmoid'),
        ])
        model.compile(optimizer='adam', loss='mse')
        epochs = 100

    model.fit(temps, ndvis, epochs=epochs, batch_size=16)
    model.save(MODEL_PATH)

#חדש

    print("\nPredictions Test")
    
    test_temps = temps[:10]
    actual_ndvis = ndvis[:10]
    
    predicted_ndvis = model.predict(test_temps, verbose=0).flatten()
    
    for i in range(10):
        temp_celsius = test_temps[i][0] * 50.0 
        print(f"Temp: {temp_celsius:.1f}C | Actual NDVI: {actual_ndvis[i]:.2f} | Predicted NDVI: {predicted_ndvis[i]:.2f}")

#
def get_ml_ndvi_predictions(temps: list) -> list:

    if not os.path.exists(MODEL_PATH):
        return [0.5] * len(temps)

    try:
        model = load_model(MODEL_PATH)

    except Exception:
        return [0.5] * len(temps)

    arr = (np.array(temps) / 50.0).reshape(-1, 1)

    predictions = model.predict(arr, verbose=0).flatten()

    result = []
    for p in predictions:

        ndvi = float(p)
        result.append(round(max(0.01, min(1.0, ndvi)), 2))

    return result


if __name__ == "__main__":
    asyncio.run(train_model())