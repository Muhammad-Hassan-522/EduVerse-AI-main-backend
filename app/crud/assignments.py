# from fastapi import HTTPException
# from app.db.database import db
# from datetime import datetime
# from bson import ObjectId
# from bson.errors import InvalidId

# def serialize_assignment(a):

#     def fix_date(value):
#         if not value:
#             return None
#         if isinstance(value, datetime):
#             return value
#         if hasattr(value, "as_datetime"):
#             return value.as_datetime()
#         try:
#             return datetime.fromisoformat(value)
#         except:
#             return value


#     return {
#         "id": str(a["_id"]),
#         "courseId": str(a["courseId"]),
#         "teacherId": str(a["teacherId"]),
#         "tenantId": str(a["tenantId"]),
#         "title": a["title"],
#         "description": a.get("description"),
#         "dueDate": fix_date(a.get("dueDate")),
#         "dueTime": fix_date(a.get("dueTime")),
#         "uploadedAt": fix_date(a.get("uploadedAt")),
#         "updatedAt": fix_date(a.get("updatedAt")),
#         "totalMarks": a.get("totalMarks"),
#         "passingMarks": a.get("passingMarks"),
#         "status": a.get("status"),
#         "fileUrl": a.get("fileUrl"),
#         "allowedFormats": a.get("allowedFormats", [])
#     }

# def to_oid(id_str, field):
#     try:
#         return ObjectId(id_str)
#     except InvalidId:
#         raise HTTPException(400, f"Invalid {field}")



# async def create_assignment(data):
#     d = data.dict()
#     d.update({
       
#         "courseId": ObjectId(d["courseId"]),
#         "teacherId": ObjectId(d["teacherId"]),
#         "tenantId": ObjectId(d["tenantId"]),
#         "uploadedAt": datetime.utcnow(),
#         "updatedAt": datetime.utcnow()
#     })

#     result = await db.assignments.insert_one(d)
#     new_assignment = await db.assignments.find_one({"_id": result.inserted_id})
#     return serialize_assignment(new_assignment)

# async def get_all_assignments(
#     search: str = None,
#     tenant_id: str = None,
#     teacher_id: str = None,
#     course_id: str = None,
#     status: str = None,
#     from_date: datetime = None,
#     to_date: datetime = None,
#     sort_by: str = "uploadedAt",
#     order: int = -1,
#     page: int = 1,
#     limit: int = 10
# ):
#     query = {}

#     # Search filter
#     if search:
#         query["$or"] = [
#             {"title": {"$regex": search, "$options": "i"}},
#             {"description": {"$regex": search, "$options": "i"}},
#             {"status": {"$regex": search, "$options": "i"}},
#         ]

#     # Standard filters
#     if tenant_id:
#         query["tenantId"] = to_oid(tenant_id, "tenantId")
#     if teacher_id:
#         query["teacherId"] = ObjectId(teacher_id)
#     if course_id:
#         query["courseId"] = ObjectId(course_id)
#     if status:
#         query["status"] = status

#     # Date range
#     if from_date or to_date:
#         query["uploadedAt"] = {}
#         if from_date:
#             query["uploadedAt"]["$gte"] = from_date
#         if to_date:
#             query["uploadedAt"]["$lte"] = to_date

#     # Pagination
#     skip = (page - 1) * limit

#     cursor = (
#         db.assignments.find(query)
#         .sort(sort_by, order)
#         .skip(skip)
#         .limit(limit)
#     )

#     results = [serialize_assignment(a) async for a in cursor]

#     total = await db.assignments.count_documents(query)

#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "totalPages": (total + limit - 1) // limit,
#         "results": results
#     }

# async def get_all_assignments_by_tenant(tenant_id: str):
#     tenant_oid = ObjectId(tenant_id)
#     cursor = db.assignments.find({"tenantId": tenant_oid})
#     return [serialize_assignment(a) async for a in cursor]


# async def get_assignment(id: str):
#     assignment = await db.assignments.find_one({"_id": ObjectId(id)})
#     return serialize_assignment(assignment) if assignment else None


# async def get_assignments_by_teacher(teacher_id: str):
#     teacher_oid = ObjectId(teacher_id)
#     cursor = db.assignments.find({
#         "$or": [
#             {"teacherId": teacher_oid},
#             {"teacherId": teacher_id}
#         ]
#     })
#     return [serialize_assignment(a) async for a in cursor]


# async def get_assignments_by_course(course_id: str):
#     cursor = db.assignments.find({"courseId": ObjectId(course_id)})
#     return [serialize_assignment(a) async for a in cursor]


# async def update_assignment(id: str, teacher_id: str, updates: dict):
#     assignment = await db.assignments.find_one({"_id": ObjectId(id)})
#     if not assignment:
#         return None

#     if str(assignment["teacherId"]) != teacher_id:
#         return "UNAUTHORIZED"

#     updates["updatedAt"] = datetime.utcnow()

#     await db.assignments.update_one(
#         {"_id": ObjectId(id)},
#         {"$set": updates}
#     )

#     new_data = await db.assignments.find_one({"_id": ObjectId(id)})
#     return serialize_assignment(new_data)


# async def delete_assignment(id: str, teacher_id: str):
#     assignment = await db.assignments.find_one({"_id": ObjectId(id)})
#     if not assignment:
#         return None

#     if str(assignment["teacherId"]) != teacher_id:
#         return "UNAUTHORIZED"

#     await db.assignments.delete_one({"_id": ObjectId(id)})
#     return True




from fastapi import HTTPException
from app.db.database import db
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

def serialize_assignment(a: dict) -> dict:
    """Serialize MongoDB assignment document into API-friendly format."""
    def fix_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if hasattr(value, "as_datetime"):
            return value.as_datetime()
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return value

    return {
        "id": str(a["_id"]),
        "courseId": str(a["courseId"]),
        "teacherId": str(a["teacherId"]),
        "tenantId": str(a["tenantId"]),
        "title": a["title"],
        "description": a.get("description"),
        "dueDate": fix_date(a.get("dueDate")),
        "dueTime": fix_date(a.get("dueTime")),
        "uploadedAt": fix_date(a.get("uploadedAt")),
        "updatedAt": fix_date(a.get("updatedAt")),
        "totalMarks": a.get("totalMarks"),
        "passingMarks": a.get("passingMarks"),
        "status": a.get("status"),
        "fileUrl": a.get("fileUrl"),
        "allowedFormats": a.get("allowedFormats", [])
    }


def to_oid(id_str: str, field: str) -> ObjectId:
    """Validate and convert string to Mongo ObjectId."""
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(400, f"Invalid {field}")


async def create_assignment(data) -> dict:
    d = data.dict()
    d.update({
        "courseId": to_oid(d["courseId"], "courseId"),
        "teacherId": to_oid(d["teacherId"], "teacherId"),
        "tenantId": to_oid(d["tenantId"], "tenantId"),
        "uploadedAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    result = await db.assignments.insert_one(d)
    new_assignment = await db.assignments.find_one({"_id": result.inserted_id})
    return serialize_assignment(new_assignment)


async def get_all_assignments(
    search: str = None,
    tenant_id: str = None,
    teacher_id: str = None,
    course_id: str = None,
    status: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    sort_by: str = "uploadedAt",
    order: int = -1,
    page: int = 1,
    limit: int = 10
):
    query = {}

    # Search filter
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"status": {"$regex": search, "$options": "i"}}
        ]

    # Standard filters
    if tenant_id:
        query["tenantId"] = to_oid(tenant_id, "tenantId")
    if teacher_id:
        query["teacherId"] = to_oid(teacher_id, "teacherId")
    if course_id:
        query["courseId"] = to_oid(course_id, "courseId")
    if status:
        query["status"] = status

    # Date range
    if from_date or to_date:
        query["uploadedAt"] = {}
        if from_date:
            query["uploadedAt"]["$gte"] = from_date
        if to_date:
            query["uploadedAt"]["$lte"] = to_date

    # Pagination
    skip = (page - 1) * limit
    cursor = (
        db.assignments.find(query)
        .sort(sort_by, order)
        .skip(skip)
        .limit(limit)
    )

    results = [serialize_assignment(a) async for a in cursor]
    total = await db.assignments.count_documents(query)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit,
        "results": results
    }

async def get_assignment(id: str):
    assignment = await db.assignments.find_one({"_id": to_oid(id, "assignmentId")})
    return serialize_assignment(assignment) if assignment else None


# async def get_all_assignments_by_tenant(tenant_id: str):
#     tenant_oid = to_oid(tenant_id, "tenantId")
#     cursor = db.assignments.find({"tenantId": tenant_oid})
#     return [serialize_assignment(a) async for a in cursor]


# async def get_assignments_by_teacher(teacher_id: str):
#     teacher_oid = to_oid(teacher_id, "teacherId")
#     cursor = db.assignments.find({
#         "$or": [
#             {"teacherId": teacher_oid},
#             {"teacherId": teacher_id}
#         ]
#     })
#     return [serialize_assignment(a) async for a in cursor]


# async def get_assignments_by_course(course_id: str):
#     course_oid = to_oid(course_id, "courseId")
#     cursor = db.assignments.find({"courseId": course_oid})
#     return [serialize_assignment(a) async for a in cursor]


async def update_assignment(id: str, teacher_id: str, updates: dict):
    assignment = await db.assignments.find_one({"_id": to_oid(id, "assignmentId")})
    if not assignment:
        return None

    if str(assignment["teacherId"]) != teacher_id:
        return "UNAUTHORIZED"

    # Only update fields that exist
    updates_to_set = {k: v for k, v in updates.items() if v is not None}
    updates_to_set["updatedAt"] = datetime.utcnow()

    await db.assignments.update_one({"_id": ObjectId(id)}, {"$set": updates_to_set})
    updated_assignment = await db.assignments.find_one({"_id": ObjectId(id)})
    return serialize_assignment(updated_assignment)


async def delete_assignment(id: str, teacher_id: str):
    assignment = await db.assignments.find_one({"_id": to_oid(id, "assignmentId")})
    if not assignment:
        return None

    if str(assignment["teacherId"]) != teacher_id:
        return "UNAUTHORIZED"

    await db.assignments.delete_one({"_id": ObjectId(id)})
    return True

