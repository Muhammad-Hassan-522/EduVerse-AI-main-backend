
from app.db.database import db
from datetime import datetime
from app.schemas.student import StudentCreate
from bson import ObjectId


async def create_student(student: StudentCreate):
    student_dict = student.dict()

    if not student_dict.get("tenant_id"):
        student_dict["tenant_id"] = ObjectId()  

    student_dict.update({
        "enrolledCourses": [],
        "completedCourses": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    result = await db.students.insert_one(student_dict)
    new_student = await db.students.find_one({"_id": result.inserted_id})
    new_student["id"] = str(new_student["_id"])
    new_student["tenant_id"] = str(new_student["tenant_id"]) 
    return new_student



