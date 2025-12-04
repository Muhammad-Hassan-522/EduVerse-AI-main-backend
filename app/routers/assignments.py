from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from app.schemas.assignments import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse
)
from app.crud.assignments import (
    create_assignment,
    get_all_assignments,
   
    get_assignment,
   
    update_assignment,
    delete_assignment
)

router = APIRouter(prefix="/assignments", tags=["Assignments"])

def clean_updates(data: dict):
    cleaned = {}
    for k, v in data.items():
        if v in [None, "", [], {}]:
            continue 
        cleaned[k] = v
    return cleaned


def validate_object_id(id: str, name: str = "id"):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid ObjectId format for {name}"
        )

@router.post("/", response_model=AssignmentResponse)
async def create_assignment_route(data: AssignmentCreate):
    
    validate_object_id(data.courseId, "courseId")
    validate_object_id(data.teacherId, "teacherId")
    validate_object_id(data.tenantId, "tenantId")

    assignment = await create_assignment(data)

    if not assignment:
        raise HTTPException(500, "Failed to create assignment")

    return assignment


# @router.get("/", response_model=list[AssignmentResponse])
# async def get_all_assignments_route():
#     return await get_all_assignments()


@router.get("/", response_model=dict)
async def get_all_assignments_route(
    search: str = None,
    tenantId: str = None,
    teacherId: str = None,
    courseId: str = None,
    status: str = None,
    fromDate: datetime = None,
    toDate: datetime = None,
    sortBy: str = "uploadedAt",
    order: int = -1,
    page: int = 1,
    limit: int = 10,
):
    return await get_all_assignments(
        search,
        tenantId,
        teacherId,
        courseId,
        status,
        fromDate,
        toDate,
        sortBy,
        order,
        page,
        limit
    )



# @router.get("/tenant/{tenantId}", response_model=list[AssignmentResponse])
# async def get_all_by_tenant(tenantId: str):

#     validate_object_id(tenantId, "tenantId")

#     return await get_all_assignments_by_tenant(tenantId)



# @router.get("/teacher/{teacherId}", response_model=list[AssignmentResponse])
# async def get_by_teacher(teacherId: str):

#     validate_object_id(teacherId, "teacherId")

#     return await get_assignments_by_teacher(teacherId)


# @router.get("/course/{courseId}", response_model=list[AssignmentResponse])
# async def get_by_course(courseId: str):

#     validate_object_id(courseId, "courseId")

#     return await get_assignments_by_course(courseId)


@router.get("/{id}", response_model=AssignmentResponse)
async def get_assignment_route(id: str):

    validate_object_id(id, "assignmentId")

    assignment = await get_assignment(id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    return assignment;


@router.put("/{id}", response_model=AssignmentResponse)
async def update_assignment_route(id: str, teacherId: str, updates: Optional[AssignmentUpdate] = None):

    validate_object_id(id, "assignmentId")
    validate_object_id(teacherId, "teacherId")
    update_data = updates.dict(exclude_unset=True)

    # remove empty values so they don't override DB
    update_data = clean_updates(update_data)

    result = await update_assignment(id, teacherId, update_data)

    if result == "UNAUTHORIZED":
        raise HTTPException(403, "You are not allowed to edit this assignment")

    if not result:
        raise HTTPException(404, "Assignment not found")

    return result



@router.delete("/{id}")
async def delete_assignment_route(id: str, teacherId: str):

    validate_object_id(id, "assignmentId")
    validate_object_id(teacherId, "teacherId")

    result = await delete_assignment(id, teacherId)

    if result == "UNAUTHORIZED":
        raise HTTPException(403, "You are not allowed to delete this assignment")

    if not result:
        raise HTTPException(404, "Assignment not found")

    return {"message": "Assignment deleted successfully"}
