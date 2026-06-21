import pymongo

    

if __name__ == "__main__":
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.farm_database
    fields_collection = db.get_collection("fields")
    users_collection = db.get_collection("users")


    fields_collection.delete_many({})
    users_collection.delete_many({})