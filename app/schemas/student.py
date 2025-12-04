from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class StudentCreate(BaseModel):
    # tenant_id: str
    name: str
    email: EmailStr
    password: str
    profileImageURL: Optional[str] = None
    contactNo: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    tenantId: Optional[str] = None
    name: str
    email: EmailStr
    profileImageURL: Optional[str] = None
    enrolledCourses: List[str] = []
    completedCourses: List[str] = []
    contactNo: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
