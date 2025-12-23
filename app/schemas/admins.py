from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.users import UserResponse


class AdminCreate(BaseModel):
    userId: str
    permissions: List[str] = []


class AdminUpdateRequest(BaseModel):

    # ---- user fields ----
    fullName: Optional[str] = None
    profileImageURL: Optional[str] = None
    contactNo: Optional[str] = None
    country: Optional[str] = None

    # ---- admin fields ----
    permissions: Optional[List[str]] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminResponse(BaseModel):
    id: str
    userId: str
    permissions: List[str]
    status: str
    createdAt: datetime
    updatedAt: datetime

    user: UserResponse

    model_config = {"from_attributes": True}
