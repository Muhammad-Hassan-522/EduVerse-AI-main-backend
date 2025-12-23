from fastapi import Depends
from app.auth.router import oauth2_scheme
from app.db.database import db
from app.utils.security import decode_token
from bson import ObjectId
from fastapi import HTTPException


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    user = await db.users.find_one(
        {"_id": ObjectId(payload["user_id"]), "status": "active"}
    )
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "user_id": str(user["_id"]),
        "role": user["role"],
        "tenant_id": str(user["tenantId"]),
    }


def require_role(*allowed_roles: str):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient Role")
        return current_user

    return role_checker
