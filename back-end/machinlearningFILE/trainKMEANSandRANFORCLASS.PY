import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

#לבדיקות דיוק
from sklearn.metrics import confusion_matrix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

async def train_my_ai():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    collection = client["farm_database"]["fields"]

    fields = await collection.find({"crop_type": "corn"}).to_list(length=10000)
    
    data_rows = []
    for field in fields:
        for entry in field.get("recent_indexes", []):
            idx = entry.get("indexes", {})
            data_rows.append({
                "ndvi": idx.get("ndvi"),
                "evi": idx.get("evi"),
                "ndwi": idx.get("ndwi"),
                "nri": idx.get("nri"),
                "dswi": idx.get("dswi")
            })
            
    df = pd.DataFrame(data_rows)


    df = df.dropna() 
    

    scaler = StandardScaler()
    X_scaled= scaler.fit_transform(df)

    kmeans =KMeans(n_clusters=3, random_state=42)
    y_labels= kmeans.fit_predict(X_scaled) 

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_labels, test_size=0.2, random_state=42)

    rfc = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=20 ,)
    rfc.fit(X_train, y_train)

    predictions = rfc.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f" (Accuracy) {accuracy * 100:.2f}%\n")
    print(classification_report(y_test, predictions))
#חדש
    print("Classification Report")
    print(classification_report(y_test, predictions))
    
    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, predictions))
#

    joblib.dump(kmeans, os.path.join(BASE_DIR, 'kmeans_corn.pkl'))
    joblib.dump(rfc, os.path.join(BASE_DIR, 'rfc_corn.pkl'))
    joblib.dump(scaler, os.path.join(BASE_DIR, 'scaler_corn.pkl'))
    

if __name__ == "__main__":
    asyncio.run(train_my_ai())