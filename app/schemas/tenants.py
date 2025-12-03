from typing import Optional
from datetime import datetime
from pydantic import EmailStr, BaseModel, Field, HttpUrl

# -------------------------
# Schema: Used when creating a tenant
# -------------------------
class TenantCreate(BaseModel):
    # Name of the tenant (e.g., school name)
    tenantName: str = Field(
        ..., min_length=2, max_length=100,
        json_schema_extra={"example": "EduVerse School"}
    )

    # Optional logo URL for the tenant
    tenantLogoUrl: Optional[HttpUrl] = Field(
        None,
        json_schema_extra={"example": "https://example.com/logo.png"}
    )

    # Email of the admin user
    adminEmail: EmailStr = Field(
        ..., json_schema_extra={"example": "admin@example.com"}
    )

    # Subscription ID stored in MongoDB (must be a valid ObjectId)
    subscriptionId: str = Field(
        ..., json_schema_extra={"example": "64a7c9e12f3d2a001f2d4b2f"}
    )


# -------------------------
# Schema: Used when updating tenant information
# -------------------------
class TenantUpdate(BaseModel):
    tenantName: Optional[str] = Field(
        None, min_length=2, max_length=100,
        json_schema_extra={"example": "New School Name"}
    )

    tenantLogoUrl: Optional[HttpUrl] = Field(
        None,
        json_schema_extra={"example": "https://example.com/newlogo.png"}
    )

    # Changing status (active / inactive / suspended)
    status: Optional[str] = Field(
        None,
        json_schema_extra={"example": "inactive"}
    )


# -------------------------
# Schema: Response object returned to the frontend
# -------------------------
class TenantResponse(BaseModel):
    id: str
    tenantName: str
    tenantLogoUrl: Optional[HttpUrl] = None
    adminEmail: EmailStr
    status: str
    subscriptionId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
