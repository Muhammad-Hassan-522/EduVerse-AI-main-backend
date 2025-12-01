# app/utils/mongo.py
from bson import ObjectId

def fix_object_ids(data):
    """
    Recursively convert ALL ObjectId values to strings
    so FastAPI/JSON can encode them safely.
    """
    if isinstance(data, ObjectId):
        return str(data)

    if isinstance(data, list):
        return [fix_object_ids(item) for item in data]

    if isinstance(data, dict):
        return {k: fix_object_ids(v) for k, v in data.items()}

    return data
