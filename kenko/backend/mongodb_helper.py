from pymongo import MongoClient

MONGODB_URI = ""

client = MongoClient(MONGODB_URI)
db = client["la_sim_db"]

def insert_patient_info(info):
    # Getting the collection by name will automatically create it on first insert if it doesn't exist.
    collection = db["patient_info"]
    return collection.insert_one(info)

def get_patient_info():
    collection = db["patient_info"]
    # This returns an empty list if there are no documents.
    return list(collection.find({}, {"_id": 0}))
