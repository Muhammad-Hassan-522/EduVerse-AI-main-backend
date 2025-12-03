from fastapi import APIRouter, HTTPException, Query, status
from bson import ObjectId
from typing import Optional

from app.schemas.quizzes import QuizCreate, QuizUpdate, QuizResponse
from app.crud.quizzes import (
    create_quiz,
    get_quiz,
    get_quizzes_filtered,
    update_quiz,
    delete_quiz
)

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)

# ------------------ VALIDATION ------------------
def validate(_id: str):
    """Ensures that incoming IDs are valid MongoDB ObjectIds."""
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ObjectId")

# ------------------ CREATE QUIZ ------------------
@router.post("/", response_model=QuizResponse, summary="Create a new quiz")
async def create_quiz_route(data: QuizCreate):
    # Validate IDs coming from body
    validate(data.courseId)
    validate(data.teacherId)
    validate(data.tenantId)

    # Call CRUD function
    return await create_quiz(data)

# ------------------ GET QUIZ BY ID ------------------
@router.get("/{quiz_id}", response_model=QuizResponse, summary="Get quiz by ID")
async def get_one(quiz_id: str):
    validate(quiz_id)
    quiz = await get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz


# ------------------ LIST QUIZZES (FILTERING + SEARCH + PAGINATION) ------------------
@router.get("/", response_model=list[QuizResponse],
            summary="List quizzes with filtering, searching, sorting, pagination")
async def list_quizzes(
    tenant_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    course_id: Optional[str] = None,
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("createdAt"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):

    # Validate IDs only if provided
    if tenant_id: 
        validate(tenant_id)
    if teacher_id: 
        validate(teacher_id)
    if course_id: 
        validate(course_id)

    # Forward to CRUD function
    return await get_quizzes_filtered(
        tenant_id, teacher_id, course_id, search, sort, page, limit
    )

# ------------------ UPDATE QUIZ ------------------
@router.put("/{quiz_id}", response_model=QuizResponse, summary="Update quiz by ID")
async def update_quiz_route(quiz_id: str, teacher_id: str, updates: QuizUpdate):
    validate(quiz_id)
    validate(teacher_id)

    result = await update_quiz(quiz_id, teacher_id, updates.dict(exclude_unset=True))

    if result == "Unauthorized":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only the owner teacher can edit this quiz")

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    return result


# ------------------ DELETE QUIZ ------------------
@router.delete("/{quiz_id}", summary="Delete quiz by ID")
async def delete_quiz_route(quiz_id: str, teacher_id: str):
    validate(quiz_id)
    validate(teacher_id)

    result = await delete_quiz(quiz_id, teacher_id)

    if result == "Unauthorized":
        raise HTTPException(401, "Only the owner teacher can delete this quiz")

    if result is None:
        raise HTTPException(404, "Quiz not found")

    return {"message": "Quiz deleted successfully"}
