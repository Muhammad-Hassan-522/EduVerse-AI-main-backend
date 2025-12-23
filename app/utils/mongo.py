# app/utils/mongo.py
from bson import ObjectId

def fix_object_ids(data):
    
    if isinstance(data, ObjectId):
        return str(data)

    if isinstance(data, list):
        return [fix_object_ids(item) for item in data]

    if isinstance(data, dict):
        return {k: fix_object_ids(v) for k, v in data.items()}

    return data
