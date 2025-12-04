from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SuperAdminBase(BaseModel):
    email: EmailStr
    fullName: str

class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str

class SuperAdminResponse(SuperAdminBase):
    id: str
    profileImageURL: str | None = None
    role: str = "super_admin"
    createdAt: datetime
    lastLogin: Optional[datetime]= None

    model_config = {
        "from_attributes": True
    }
