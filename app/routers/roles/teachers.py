from fastapi import APIRouter, Depends, HTTPException
from app.schemas.teachers import TeacherUpdate, TeacherResponse
from app.crud import teachers as crud_teacher
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"],
    dependencies=[Depends(require_role("teacher"))],
)


@router.get("/me", response_model=TeacherResponse)
async def get_my_profile(
    current_user=Depends(get_current_user),
):
    teacher = await crud_teacher.get_teacher_by_user(current_user["user_id"])
    if not teacher:
        raise HTTPException(404, "Teacher profile not found")

    return teacher


@router.patch("/me", response_model=TeacherResponse)
async def update_my_profile(
    update: TeacherUpdate,
    current_user=Depends(get_current_user),
):
    updated_teacher = await crud_teacher.update_teacher_profile(
        current_user["user_id"],
        update.dict(exclude_unset=True),
    )

    if not updated_teacher:
        raise HTTPException(404, "Teacher profile not found")

    return updated_teacher
