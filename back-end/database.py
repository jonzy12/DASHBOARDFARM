import os
import motor.motor_asyncio
from dotenv import load_dotenv

# טעינת המשתנים מקובץ ה-.env (כדי לקחת את הכתובת המאובטחת)
load_dotenv()

# קריאת הכתובת מהסביבה, ואם היא לא קיימת - נשתמש בלוקאל הוסט כגיבוי
MONGO_DETAILS = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.farm_database 
users_collection = db.get_collection("users")
fields_collection = db.get_collection("fields")