import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'machinlearningFILE')
FEATURES   = ['ndvi', 'evi', 'ndwi', 'nri', 'dswi']

try:
    scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler_corn.pkl'))
    rfc = joblib.load(os.path.join(MODELS_DIR, 'rfc_corn.pkl'))
    kmeans= joblib.load(os.path.join(MODELS_DIR, 'kmeans_corn.pkl'))

    centers = kmeans.cluster_centers_
    sorted_ids = np.argsort(centers.sum(axis=1))

    optimal_cluster_id = sorted_ids[-1]
    warning_centroid   = centers[sorted_ids[-2]] 

except Exception:
    scaler = rfc = kmeans = warning_centroid = None
    optimal_cluster_id = -1

ALERTS = {
    'ndvi': "בריאות היבול נמוכה ",
    'evi':  "בריאות היבול נמוכה יש לבדוק אזורי יבול צפופים ",
    'ndwi': "חוסר מים ביבול מומלץ להגביר השקיה ולבדוק את לחות הקרקע",
    'nri':  "חסר חנקן בצמחים מומלץ להוסיף דשן",
    'dswi': "תכולת המים בעלים נמוכה יש לבדוק למזיקים או להוסיף מים",
}

def give_insights(indexes: dict, crop_type: str = "corn") -> dict:

    if crop_type.lower() != "corn" or not rfc:
        return { "message": "uvailaible",  "alerts": []}

    try:
        df   = pd.DataFrame([[indexes.get(f, 0.0) for f in FEATURES]], columns=FEATURES)
        scaled= scaler.transform(df)
        cluster = int(rfc.predict(scaled)[0])

        if cluster == optimal_cluster_id:
            return { "message": " all good",  "alerts": []}
        
        alerts = [ALERTS[f] for i, f in enumerate(FEATURES) if scaled[0][i] < warning_centroid[i]]
        
        return {
            
            "message": "we can see a few bad apples",  
            "alerts": alerts or [" general stress"]
        }

    except Exception:
        return { "message": "prediction failed", "alerts": []}



