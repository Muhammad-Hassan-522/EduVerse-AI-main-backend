from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.auth.dependencies import require_role
from app.schemas.assignment_submissions import (
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse,
)
from app.crud.assignment_submissions import (
    create_submission,
    get_all_submissions,
    get_submissions_by_student,
    get_submissions_by_assignment,
    grade_submission,
    delete_submission,
)

router = APIRouter(
    prefix="/assignment-submissions",
    tags=["Assignment Submissions"],
)


def validate_object_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")


# ===============================
# STUDENT: CREATE SUBMISSION
# ===============================
@router.post("/", response_model=AssignmentSubmissionResponse)
async def create_submission_route(
    data: AssignmentSubmissionCreate,
    current_user=Depends(require_role("student")),
):
    validate_object_id(data.assignmentId)
    validate_object_id(data.courseId)

    submission = await create_submission(
        data=data,
        student_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
    )

    return submission


# ===============================
# ADMIN / TEACHER: ALL SUBMISSIONS
# ===============================
@router.get("/", response_model=List[AssignmentSubmissionResponse])
async def get_all_submissions_route(
    current_user=Depends(require_role("admin", "teacher")),
):
    return await get_all_submissions(current_user["tenant_id"])


# ===============================
# STUDENT / TEACHER: BY STUDENT
# ===============================
@router.get("/me", response_model=List[AssignmentSubmissionResponse])
async def get_my_submissions(
    current_user=Depends(require_role("student")),
):
    return await get_submissions_by_student(
        student_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
    )


# ===============================
# TEACHER / ADMIN: BY ASSIGNMENT
# ===============================
@router.get(
    "/assignment/{assignment_id}",
    response_model=List[AssignmentSubmissionResponse],
)
async def get_by_assignment(
    assignment_id: str,
    current_user=Depends(require_role("teacher", "admin")),
):
    validate_object_id(assignment_id)

    return await get_submissions_by_assignment(
        assignment_id=assignment_id,
        tenant_id=current_user["tenant_id"],
    )


# ===============================
# TEACHER / ADMIN: GRADE
# ===============================
@router.put("/{submission_id}", response_model=AssignmentSubmissionResponse)
async def grade_submission_route(
    submission_id: str,
    update,
    current_user=Depends(require_role("teacher", "admin")),
):
    validate_object_id(submission_id)

    return await grade_submission(
        submission_id=submission_id,
        tenant_id=current_user["tenant_id"],
        marks=update.obtainedMarks,
        feedback=update.feedback,
    )


# ===============================
# ADMIN ONLY: DELETE
# ===============================
@router.delete("/{submission_id}")
async def delete_submission_route(
    submission_id: str,
    current_user=Depends(require_role("admin")),
):
    validate_object_id(submission_id)

    success = await delete_submission(
        submission_id=submission_id,
        tenant_id=current_user["tenant_id"],
    )
    if not success:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {"message": "Submission deleted successfully"}
