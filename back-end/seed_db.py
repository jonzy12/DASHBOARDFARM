import pymongo
import os
from dotenv import load_dotenv

def migrate_local_to_cloud():
    # 1. טעינת הכתובת של הענן מקובץ ה-.env (שיצרנו בשלב הקודם)
    load_dotenv()
    CLOUD_MONGO_URI = os.getenv("MONGO_URI")

    if not CLOUD_MONGO_URI or CLOUD_MONGO_URI == "mongodb://localhost:27017":
        print("❌ Error: Please check your .env file. It seems MONGO_URI is missing or points to localhost.")
        return

    print("🔄 Connecting to databases...")
    
    # 2. התחברות למונגו הלוקאלי (ממנו נשאב את המידע)
    local_client = pymongo.MongoClient("mongodb://localhost:27017")
    local_db = local_client.farm_database

    # 3. התחברות למונגו בענן (אליו נזריק את המידע)
    cloud_client = pymongo.MongoClient(CLOUD_MONGO_URI)
    cloud_db = cloud_client.farm_database

    # האוספים שאנחנו רוצים להעביר
    collections_to_migrate = ["users", "fields"]

    for coll_name in collections_to_migrate:
        print(f"\n📂 Processing collection: '{coll_name}'...")
        
        local_collection = local_db.get_collection(coll_name)
        cloud_collection = cloud_db.get_collection(coll_name)

        # משיכת כל הנתונים מהמסד המקומי והפיכתם לרשימה
        local_data = list(local_collection.find())
        
        if len(local_data) > 0:
            print(f"   Found {len(local_data)} documents locally. Uploading to cloud...")
            
            # פעולת מניעה: מחיקת נתונים קיימים בענן באוסף הזה כדי למנוע כפילויות בהעברה
            cloud_collection.delete_many({})
            
            # הזרקת כל הנתונים לענן בבת אחת
            cloud_collection.insert_many(local_data)
            
            print(f"   ✅ Successfully migrated {len(local_data)} documents to '{coll_name}'.")
        else:
            print(f"   ⚠️ Collection '{coll_name}' is empty locally. Nothing to migrate.")

    print("\n🚀 Migration completed successfully! Your cloud database is ready.")

if __name__ == "__main__":
    migrate_local_to_cloud()