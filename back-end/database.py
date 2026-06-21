import motor.motor_asyncio

MONGO_DETAILS = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.farm_database 
users_collection = db.get_collection("users")

fields_collection = db.get_collection("fields")
