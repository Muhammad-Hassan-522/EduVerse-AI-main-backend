from fastapi import APIRouter
from app.schemas.student import StudentCreate, StudentResponse
from app.crud.student import create_student as crud_create_student

router = APIRouter(prefix="/student", tags=["Students"])


@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    new_student = await crud_create_student(student)
    return StudentResponse(**new_student)


