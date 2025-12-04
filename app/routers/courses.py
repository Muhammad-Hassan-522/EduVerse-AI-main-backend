
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.schemas.courses import (
    CourseCreate, 
    CourseUpdate, 
    CourseResponse, 
    CourseEnrollment
)
from app.crud.courses import course_crud
from app.db.database import db

router = APIRouter(prefix="/courses", tags=["courses"])


# Dependency: Get Tenant ID

async def get_current_tenant_id() -> str:
    """
    Fetch the current tenant ID from the database.
    
    This ensures all operations are scoped to the correct organization.
    TODO: i will Replace with JWT token extraction when authentication is implemented.
    """
    tenant = await db.tenants.find_one({})
    
    if not tenant:
        raise HTTPException(
            status_code=500, 
            detail="No tenant found in database. Please create a tenant first."
        )
    
    return str(tenant["_id"])


# Course CRUD Endpoints


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(
    course: CourseCreate,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Create a new course.
    
    The tenant ID is automatically injected from the database.
    Teacher ID must be provided in the request body.
    """
    # Set tenant ID before creating the course
    course.tenantId = tenantId
    
    created_course = await course_crud.create_course(course)
    return created_course


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    tenantId: str = Depends(get_current_tenant_id),
    teacher_id: Optional[str] = Query(None, description="Filter by teacher ID"),
    status: Optional[str] = Query(None, description="Filter by status (Active, Inactive, Upcoming, Completed)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    skip: int = Query(0, ge=0, description="Number of courses to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum courses to return")
):
    """
    Get all courses with optional filters.
    
    Supports filtering by teacher, status, category, and text search.
    Results are automatically scoped to the current tenant.
    """
    courses = await course_crud.get_all_courses(
        tenantId=tenantId,
        teacher_id=teacher_id,
        status=status,
        category=category,
        search=search,
        skip=skip,
        limit=limit
    )
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Get a single course by its ID.
    
    Returns 404 if course doesn't exist or belongs to a different tenant.
    """
    course = await course_crud.get_course_by_id(course_id, tenantId)
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Update a course's information.
    
    Only provided fields will be updated. Empty or placeholder values are ignored.
    Returns 404 if course doesn't exist or belongs to a different tenant.
    """
    updated_course = await course_crud.update_course(course_id, tenantId, course_update)
    
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return updated_course


@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: str,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Delete a course permanently.
    
    Returns 404 if course doesn't exist or belongs to a different tenant.
    Returns 204 (No Content) on successful deletion.
    """
    deleted = await course_crud.delete_course(course_id, tenantId)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return None



# Enrollment Endpoints


@router.post("/enroll", status_code=200)
async def enroll_in_course(
    enrollment: CourseEnrollment,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Enroll a student in a course.
    
    Validates that both student and course exist and belong to the same tenant.
    Prevents duplicate enrollments.
    """
    result = await course_crud.enroll_student(
        enrollment.courseId, 
        enrollment.studentId, 
        tenantId
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/unenroll", status_code=200)
async def unenroll_from_course(
    enrollment: CourseEnrollment,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Remove a student from a course.
    
    Validates that the student is actually enrolled before removing them.
    """
    result = await course_crud.unenroll_student(
        enrollment.courseId, 
        enrollment.studentId, 
        tenantId
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/student/{student_id}", response_model=List[CourseResponse])
async def get_student_courses(
    student_id: str,
    tenantId: str = Depends(get_current_tenant_id)
):
    """
    Get all courses a student is enrolled in.
    
    Returns an empty list if student has no enrollments.
    """
    courses = await course_crud.get_student_courses(student_id, tenantId)
    return courses