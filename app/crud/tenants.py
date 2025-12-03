from fastapi import HTTPException, status
from app.db.database import db
from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any


# -------------------------
# Convert MongoDB document → API format (Python dict)
# -------------------------
def serialize_tenant(tenant):
    return {
        "id": str(tenant["_id"]),                     # convert ObjectId -> string
        "tenantName": tenant["tenantName"],
        "tenantLogoUrl": tenant.get("tenantLogoUrl"),
        "adminEmail": tenant["adminEmail"],
        "status": tenant.get("status", "active"),
        "subscriptionId": str(tenant["subscriptionId"]),
        "createdAt": tenant["createdAt"],              # datetime object
        "updatedAt": tenant.get("updatedAt")
    }


# -------------------------
# Create a new tenant
# -------------------------
async def create_tenant(request):
    # Convert Pydantic model to dictionary
    data = request.dict()

    # Ensure unique tenantName
    if await db.tenants.find_one({"tenantName": data["tenantName"], "isDeleted": False}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant name already exists")

    data.update({
        "subscriptionId": ObjectId(data["subscriptionId"]),  # convert to ObjectId
        "createdAt": datetime.utcnow(),                      # timestamp
        "status": "active",                                   # default status
        "updatedAt": None,
        "isDeleted": False
    })

    # Insert into MongoDB
    result = await db.tenants.insert_one(data)

    # Fetch the created tenant
    new_tenant = await db.tenants.find_one({"_id": result.inserted_id})

    return serialize_tenant(new_tenant)

# -------------------------
# Get all tenants (filter, search, sort, pagination)
# -------------------------
async def get_all_tenants(
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None
):

    query: Dict[str, Any] = {"isDeleted": False}

    # Filter by status
    if status:
        query["status"] = status

    # Case-insensitive search on tenantName & adminEmail
    if search:
        query["$or"] = [
            {"tenantName": {"$regex": search, "$options": "i"}},
            {"adminEmail": {"$regex": search, "$options": "i"}},
        ]

    cursor = db.tenants.find(query)

    # Sorting logic
    if sort:
        direction = -1 if sort.startswith("-") else 1
        field = sort.lstrip("-")
        cursor = cursor.sort(field, direction)

    # Pagination
    tenants = await cursor.skip(skip).limit(limit).to_list(length=limit)

    return [serialize_tenant(t) for t in tenants]


# -------------------------
# Get a single tenant by id
# -------------------------
async def get_tenant(_id):
    tenant = await db.tenants.find_one({"_id": ObjectId(_id), "isDeleted": False})
    return serialize_tenant(tenant) if tenant else None


# -------------------------
# Update tenant by id
# -------------------------
async def update_tenant(_id, updates):

    if not updates:
        return None

    # Convert subscriptionId to ObjectId if included
    if "subscriptionId" in updates:
        updates["subscriptionId"] = ObjectId(updates["subscriptionId"])

    updates["updatedAt"] = datetime.utcnow()

    await db.tenants.update_one(
        {"_id": ObjectId(_id), "isDeleted": False},
        {"$set": updates}
    )

    tenant = await db.tenants.find_one({"_id": ObjectId(_id), "isDeleted": False})
    return serialize_tenant(tenant) if tenant else None


# -------------------------
# Delete tenant by id
# -------------------------
async def delete_tenant(_id):
    result = await db.tenants.delete_one(
        {"_id": ObjectId(_id)},
        {"$set": {"isDeleted": True}}
    )
    return result.modified_count > 0
