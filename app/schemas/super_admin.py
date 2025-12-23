from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.users import UserResponse


class SuperAdminCreate(BaseModel):
    userId: str


class SuperAdminUpdate(BaseModel):
    # ---- user fields ----
    fullName: Optional[str] = None
    profileImageURL: Optional[str] = None
    contactNo: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}


class SuperAdminResponse(BaseModel):
    id: str
    userId: str
    user: UserResponse  # NESTED USER
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}
