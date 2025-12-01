from bson import ObjectId
from app.db.database import quizzes_collection
from app.utils.mongo import fix_object_ids

async def get_quiz_by_id(quiz_id: str):
    quiz = await quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
    return fix_object_ids(quiz)
