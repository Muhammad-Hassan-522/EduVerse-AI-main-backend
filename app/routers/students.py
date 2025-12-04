# from fastapi import APIRouter
# from app.schemas.student import StudentCreate, StudentResponse
# from app.crud.student import create_student as crud_create_student

# router = APIRouter(prefix="/students", tags=["students"])

# @router.post("/", response_model=StudentResponse)
# async def create_student(student: StudentCreate):
#     new_student = await crud_create_student(student)
#     return StudentResponse(**new_student)



from fastapi import APIRouter, Depends, HTTPException
from app.schemas.student import StudentCreate, StudentResponse
from app.crud.student import create_student as crud_create_student
from app.db.database import db

router = APIRouter(prefix="/student", tags=["Students"])


# Helper function to get tenant ID from database
async def get_current_tenant_id() -> str:
    """Get tenant ID from database (first tenant for now)"""
    tenant = await db.tenants.find_one({})
    
    if not tenant:
        raise HTTPException(
            status_code=500, 
            detail="No tenant found in database. Please create a tenant first."
        )
    
    return str(tenant["_id"])

@router.post("/", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    tenantId: str = Depends(get_current_tenant_id)
):
    """Create a new student"""
    new_student = await crud_create_student(student, tenantId)
    return StudentResponse(**new_student)