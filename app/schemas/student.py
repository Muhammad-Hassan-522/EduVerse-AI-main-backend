from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class StudentCreate(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    profileImageURL: Optional[str] = ""
    contactNo: Optional[str] = None
    country: Optional[str] = None

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentUpdate(BaseModel):
    fullName: Optional[str] = None
    profileImageURL: Optional[str] = None
    contactNo: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    fullName: str
    email: EmailStr
    profileImageURL: Optional[str]
    contactNo: Optional[str]
    country: Optional[str]
    status: Optional[str]
    role: str
    tenant_id: str
    enrolledCourses: List[str]
    completedCourses: List[str]
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime]

    class Config:
        from_attributes = True
