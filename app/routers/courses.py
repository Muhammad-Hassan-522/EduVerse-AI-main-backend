from fastapi import APIRouter, HTTPException
from app.schemas.course import CourseResponse
from app.crud import course as crud_course

router = APIRouter(prefix="/courses", tags=["Courses"])


# --------- Get all active courses ----------
@router.get("/", response_model=list[CourseResponse])
async def get_all_courses():
    courses = await crud_course.get_all_active_courses()
    result = []
    for c in courses:
        c["id"] = c["_id"]
        del c["_id"]
        result.append(CourseResponse(**c))
    return result


# --------- Get single course by id ----------
@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str):
    course = await crud_course.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course["id"] = course["_id"]
    del course["_id"]
    return CourseResponse(**course)
