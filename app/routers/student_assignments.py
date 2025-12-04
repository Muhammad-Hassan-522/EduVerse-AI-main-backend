from fastapi import APIRouter, HTTPException
from bson import ObjectId

from app.db.database import students_collection
from app.schemas.assignment import (
    AssignmentResponse,
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse,
)
from app.crud import assignment as crud_assignment

router = APIRouter(prefix="/students", tags=["Student Assignments"])


# ---------- Get assignments for a specific course ----------
@router.get("/{student_id}/courses/{course_id}/assignments", response_model=list[AssignmentResponse])
async def get_course_assignments_for_student(student_id: str, course_id: str):
    # Optional: verify student exists
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    assignments = await crud_assignment.get_assignments_by_course(course_id)

    result = []
    for a in assignments:
        a["id"] = a["_id"]
        del a["_id"]
        result.append(AssignmentResponse(**a))

    return result


# ---------- Get ALL assignments for a student (all enrolled courses) ----------
@router.get("/{student_id}/assignments", response_model=list[AssignmentResponse])
async def get_all_assignments_for_student(student_id: str):
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    assignments = await crud_assignment.get_assignments_for_student(student_id)

    result = []
    for a in assignments:
        a["id"] = a["_id"]
        del a["_id"]
        result.append(AssignmentResponse(**a))

    return result


# ---------- Submit assignment ----------
@router.post("/{student_id}/assignments/{assignment_id}/submit", response_model=AssignmentSubmissionResponse)
async def submit_assignment(
    student_id: str,
    assignment_id: str,
    payload: AssignmentSubmissionCreate,
):
    # Check student exists
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    submission = await crud_assignment.create_assignment_submission(
        student_id, assignment_id, payload.dict()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Assignment not found")

    submission["id"] = submission["_id"]
    del submission["_id"]

    return AssignmentSubmissionResponse(**submission)
