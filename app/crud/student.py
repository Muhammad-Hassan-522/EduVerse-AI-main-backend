

from app.db.database import db
from datetime import datetime
from app.schemas.student import StudentCreate
from bson import ObjectId


async def create_student(student: StudentCreate, tenantId: str):
    """Create a new student with proper tenantId handling"""
    student_dict = student.dict()
    
    # Use the passed tenantId (from database lookup)
    student_dict["tenantId"] = tenantId
    
    student_dict.update({
        "enrolledCourses": [],
        "completedCourses": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    result = await db.students.insert_one(student_dict)
    new_student = await db.students.find_one({"_id": result.inserted_id})
    
    # Convert _id to string for response
    new_student["id"] = str(new_student["_id"])
    # tenantId is already a string
    
    return new_student