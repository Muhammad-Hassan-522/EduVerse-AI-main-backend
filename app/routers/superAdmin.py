from fastapi import APIRouter, HTTPException
from app.schemas.superAdmin import SuperAdminLogin, SuperAdminResponse
from app.crud.superAdmin import login_super_admin

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])


@router.post("/login", response_model=SuperAdminResponse)
async def super_admin_login_route(data: SuperAdminLogin):
    result = await login_super_admin(data.email, data.password)

    if result == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Super admin not found")

    if result == "WRONG_PASSWORD":
        raise HTTPException(status_code=401, detail="Incorrect password")

    return result
