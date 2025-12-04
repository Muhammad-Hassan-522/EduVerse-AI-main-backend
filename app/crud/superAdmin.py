from app.db.database import db
from datetime import datetime

def serialize_admin(a):
    return {
        "id": str(a["_id"]),
        "email": a["email"],
        "fullName": a["fullName"],
        "profileImageURL": a.get("profileImageURL", None),
        "role": a.get("role", "super_admin"),
        "createdAt": a.get("createdAt"),
        "lastLogin": a.get("lastLogin")
    }

async def login_super_admin(email: str, password: str):
    admin = await db.superAdmin.find_one({"email": email})

    if not admin:
        return "NOT_FOUND"

    if password != admin["password"]:  
        return "WRONG_PASSWORD"

    new_login_time = datetime.utcnow()
    await db.superAdmin.update_one(
        {"_id": admin["_id"]},
        {"$set": {"lastLogin": new_login_time}}
    )

    admin["lastLogin"] = new_login_time
    return serialize_admin(admin)
