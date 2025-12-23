from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.users import UserResponse


class StudentCreate(BaseModel):
    userId: str


class StudentUpdate(BaseModel):
    # ---- user fields ----
    fullName: Optional[str] = None
    profileImageURL: Optional[str] = None
    contactNo: Optional[str] = None
    country: Optional[str] = None
    tenantId: Optional[str] = None

    # ---- student fields ----
    status: Optional[str] = None
    enrolledCourses: Optional[List[str]] = None
    completedCourses: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class StudentResponse(BaseModel):
    id: str
    userId: str
    tenantId: Optional[str] = None  # include in response
    user: UserResponse  # NESTED USER
    enrolledCourses: List[str] = []
    completedCourses: List[str] = []
    status: str
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}
