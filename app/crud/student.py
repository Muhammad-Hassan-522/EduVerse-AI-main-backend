from app.db.database import db
from datetime import datetime
from app.schemas.student import StudentCreate, StudentUpdate
from bson import ObjectId
#from app.core.security import hash_password
from app.core.settings import TENANT_ID
from app.utils.mongo import fix_object_ids
from app.db.database import students_collection as COLLECTION
  # your student table is users collection


async def create_student(student: StudentCreate):
    data = student.dict()

    data.update({
        "tenant_id": ObjectId(TENANT_ID),
        "password": data["password"],
        "enrolledCourses": [],
        "completedCourses": [],
        "role": "student",
        "status": "active",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "lastLogin": None,
    })

    result = await COLLECTION.insert_one(data)
    new_student = await COLLECTION.find_one({"_id": result.inserted_id})
    return fix_object_ids(new_student)


async def get_student_by_email(email: str):
    student = await COLLECTION.find_one({"email": email})
    if not student:
        return None
    return fix_object_ids(student)


async def get_student_by_id(student_id: str):
    student = await COLLECTION.find_one({"_id": ObjectId(student_id)})
    if not student:
        return None
    return fix_object_ids(student)


async def list_students():
    cursor = COLLECTION.find({})
    students = await cursor.to_list(length=None)
    return fix_object_ids(students)


async def update_student(student_id: str, update: StudentUpdate):
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updatedAt"] = datetime.utcnow()

    await COLLECTION.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": update_data}
    )

    updated = await COLLECTION.find_one({"_id": ObjectId(student_id)})
    return fix_object_ids(updated)
