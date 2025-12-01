from fastapi import APIRouter, HTTPException
from bson import ObjectId

from app.db.database import students_collection, courses_collection
from app.utils.mongo import fix_object_ids
from app.schemas.course import CourseResponse

router = APIRouter(prefix="/students", tags=["Student Courses"])


# ---------- Enroll a student in a course ----------
@router.post("/{student_id}/enroll/{course_id}")
async def enroll_in_course(student_id: str, course_id: str):
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = await courses_collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # add courseId as string to enrolledCourses[]
    await students_collection.update_one(
        {"_id": ObjectId(student_id)},
        {"$addToSet": {"enrolledCourses": course_id}},
    )

    # increment enrolledStudents counter in course
    await courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$inc": {"enrolledStudents": 1}},
    )

    return {"message": "Enrolled successfully"}


# ---------- Get all courses of a student ----------
@router.get("/{student_id}/courses", response_model=list[CourseResponse])
async def get_student_courses(student_id: str):
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrolled_ids = student.get("enrolledCourses", [])
    if not enrolled_ids:
        return []

    object_ids = [ObjectId(cid) for cid in enrolled_ids]

    cursor = courses_collection.find({"_id": {"$in": object_ids}})
    courses = await cursor.to_list(length=None)
    courses = fix_object_ids(courses)

    result = []
    for c in courses:
        c["id"] = c["_id"]
        del c["_id"]
        result.append(CourseResponse(**c))

    return result
