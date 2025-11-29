# from fastapi import APIRouter, HTTPException
# from app.schemas.assignments import (
#     AssignmentCreate,
#     AssignmentUpdate,
#     AssignmentResponse
# )
# from app.crud.assignments import (
#     create_assignment,
#     get_all_assignments,
#     get_all_assignments_by_tenant,
#     get_assignment,
#     get_assignments_by_teacher,
#     get_assignments_by_course,
#     get_assignments_for_student,
#     update_assignment,
#     delete_assignment
# )

# router = APIRouter(prefix="/assignments", tags=["Assignments"])

# @router.post("/", response_model=AssignmentResponse)
# async def create_assignment_route(data: AssignmentCreate):
#     return await create_assignment(data)


# @router.get("/", response_model=list[AssignmentResponse])
# async def get_all_assignments_route():
#     return await get_all_assignments()


# @router.get("/tenant/{tenantId}", response_model=list[AssignmentResponse])
# async def get_all_by_tenant(tenantId: str):
#     return await get_all_assignments_by_tenant(tenantId)


# @router.get("/teacher/{teacherId}", response_model=list[AssignmentResponse])
# async def get_by_teacher(teacherId: str):
#     return await get_assignments_by_teacher(teacherId)


# @router.get("/course/{courseId}", response_model=list[AssignmentResponse])
# async def get_by_course(courseId: str):
#     return await get_assignments_by_course(courseId)


# @router.get("/student/{studentId}", response_model=list[AssignmentResponse])
# async def get_for_student(studentId: str):
#     return await get_assignments_for_student(studentId)


# @router.get("/{id}", response_model=AssignmentResponse)
# async def get_assignment_route(id: str):
#     assignment = await get_assignment(id)
#     if not assignment:
#         raise HTTPException(status_code=404, detail="Assignment not found")
#     return assignment


# @router.put("/{id}", response_model=AssignmentResponse)
# async def update_assignment_route(id: str, teacherId: str, updates: AssignmentUpdate):
#     result = await update_assignment(id, teacherId, updates.dict(exclude_unset=True))

#     if result == "UNAUTHORIZED":
#         raise HTTPException(status_code=403, detail="Not allowed to edit this assignment")
#     if not result:
#         raise HTTPException(status_code=404, detail="Assignment not found")

#     return result


# @router.delete("/{id}")
# async def delete_assignment_route(id: str, teacherId: str):
#     result = await delete_assignment(id, teacherId)

#     if result == "UNAUTHORIZED":
#         raise HTTPException(status_code=403, detail="Not allowed to delete this assignment")
#     if not result:
#         raise HTTPException(status_code=404, detail="Assignment not found")

#     return {"message": "Assignment deleted successfully"}


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
    get_all_assignments_by_tenant,
    get_assignment,
    get_assignments_by_teacher,
    get_assignments_by_course,
    update_assignment,
    delete_assignment
)

router = APIRouter(prefix="/assignments", tags=["Assignments"])


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


@router.get("/", response_model=list[AssignmentResponse])
async def get_all_assignments_route():
    return await get_all_assignments()



@router.get("/tenant/{tenantId}", response_model=list[AssignmentResponse])
async def get_all_by_tenant(tenantId: str):

    validate_object_id(tenantId, "tenantId")

    return await get_all_assignments_by_tenant(tenantId)



@router.get("/teacher/{teacherId}", response_model=list[AssignmentResponse])
async def get_by_teacher(teacherId: str):

    validate_object_id(teacherId, "teacherId")

    return await get_assignments_by_teacher(teacherId)


@router.get("/course/{courseId}", response_model=list[AssignmentResponse])
async def get_by_course(courseId: str):

    validate_object_id(courseId, "courseId")

    return await get_assignments_by_course(courseId)



# @router.get("/student/{studentId}", response_model=list[AssignmentResponse])
# async def get_for_student(studentId: str):

#     validate_object_id(studentId, "studentId")

#     return await get_assignments_for_student(studentId)


@router.get("/{id}", response_model=AssignmentResponse)
async def get_assignment_route(id: str):

    validate_object_id(id, "assignmentId")

    assignment = await get_assignment(id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    return assignment


@router.put("/{id}", response_model=AssignmentResponse)
async def update_assignment_route(id: str, teacherId: str, updates: AssignmentUpdate):

    validate_object_id(id, "assignmentId")
    validate_object_id(teacherId, "teacherId")

    result = await update_assignment(id, teacherId, updates.dict(exclude_unset=True))

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
