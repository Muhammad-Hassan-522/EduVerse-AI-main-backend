from bson import ObjectId
from datetime import datetime
from app.db.database import quiz_submissions_collection
from app.utils.mongo import fix_object_ids

async def save_submission(data: dict):
    data["submittedAt"] = datetime.utcnow()
    result = await quiz_submissions_collection.insert_one(data)
    saved = await quiz_submissions_collection.find_one({"_id": result.inserted_id})
    return fix_object_ids(saved)

# existing: save_submission(...)

async def get_submission_by_student_and_quiz(student_id: str, quiz_id: str):
    submission = await quiz_submissions_collection.find_one({
        "studentId": ObjectId(student_id),
        "quizId": ObjectId(quiz_id),
    })
    if not submission:
        return None
    return fix_object_ids(submission)


async def get_submissions_by_student(student_id: str):
    cursor = quiz_submissions_collection.find({
        "studentId": ObjectId(student_id)
    })
    submissions = [fix_object_ids(doc) async for doc in cursor]
    return submissions
