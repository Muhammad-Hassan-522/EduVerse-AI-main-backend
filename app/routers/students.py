from fastapi import APIRouter, HTTPException, status
from app.schemas.student import (
    StudentCreate,
    StudentLogin,
    StudentUpdate,
    StudentResponse,
)
from app.crud import student as crud_student

router = APIRouter(prefix="/students", tags=["Students"])


# ------------------- CREATE STUDENT -------------------
@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    new_student = await crud_student.create_student(student)

    # Convert _id -> id
    new_student["id"] = new_student["_id"]
    del new_student["_id"]

    return StudentResponse(**new_student)


# ------------------- LOGIN STUDENT -------------------
@router.post("/login", response_model=StudentResponse)
async def login_student(payload: StudentLogin):
    db_student = await crud_student.get_student_by_email(payload.email)

    if not db_student:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if payload.password != db_student["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Convert _id -> id
    db_student["id"] = db_student["_id"]
    del db_student["_id"]

    return StudentResponse(**db_student)


# ------------------- GET ALL STUDENTS -------------------
@router.get("/", response_model=list[StudentResponse])
async def get_all_students():
    students = await crud_student.list_students()

    clean_students = []
    for s in students:
        s["id"] = s["_id"]
        del s["_id"]
        clean_students.append(StudentResponse(**s))

    return clean_students


# ------------------- GET SINGLE STUDENT -------------------
@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    student = await crud_student.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Convert _id -> id
    student["id"] = student["_id"]
    del student["_id"]

    return StudentResponse(**student)


# ------------------- UPDATE STUDENT -------------------
@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, update: StudentUpdate):
    updated = await crud_student.update_student(student_id, update)

    # Convert _id -> id
    updated["id"] = updated["_id"]
    del updated["_id"]

    return StudentResponse(**updated)
