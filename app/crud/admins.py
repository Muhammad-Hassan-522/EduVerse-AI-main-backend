from bson import ObjectId
from datetime import datetime
from app.db.database import db
from app.crud.users import serialize_user


def serialize_admin(a, user):

    return {
        "id": str(a["_id"]),
        "userId": str(a["userId"]),
        "user": serialize_user(user),
        "permissions": a.get("permissions", []),
        "status": a.get("status"),
        "createdAt": a.get("createdAt"),
        "updatedAt": a.get("updatedAt"),
    }


async def create_admin(user_id: str, permissions: list = None, status: str = "active"):

    if permissions is None:
        permissions = []

    data = {
        "userId": ObjectId(user_id),
        "permissions": permissions,
        "status": status,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }

    result = await db.admins.insert_one(data)
    admin = await db.admins.find_one({"_id": result.inserted_id})
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_admin(admin, user)


async def get_admin_by_user(user_id: str):

    admin = await db.admins.find_one({"userId": ObjectId(user_id)})
    if not admin:
        return None

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_admin(admin, user)


async def update_admin_profile(user_id: str, updates: dict):

    admin_fields = {}
    user_fields = {}

    # --- admin-specific fields ---
    for field in ["permissions", "status"]:
        if field in updates:
            admin_fields[field] = updates[field]

    # --- user-specific fields ---
    for field in ["fullName", "profileImageURL", "contactNo", "country"]:
        if field in updates:
            user_fields[field] = updates[field]

    if admin_fields:
        admin_fields["updatedAt"] = datetime.utcnow()
        await db.admins.update_one(
            {"userId": ObjectId(user_id)}, {"$set": admin_fields}
        )

    if user_fields:
        user_fields["updatedAt"] = datetime.utcnow()
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_fields})

    # --- fetch updated documents ---
    admin = await db.admins.find_one({"userId": ObjectId(user_id)})
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not admin or not user:
        return None

    return serialize_admin(admin, user)


async def get_all_admins(tenant_id: str | None = None):

    query = {}
    if tenant_id:
        query["tenantId"] = ObjectId(tenant_id)

    admins = await db.admins.find(query).to_list(length=None)
    result = []
    for a in admins:
        user = await db.users.find_one({"_id": ObjectId(a["userId"])})
        result.append(serialize_admin(a, user))
    return result
