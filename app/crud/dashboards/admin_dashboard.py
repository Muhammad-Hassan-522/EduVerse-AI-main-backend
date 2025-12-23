from bson import ObjectId
from app.db.database import db
from app.crud.users import serialize_user
from app.crud.students import serialize_student
from app.crud.teachers import serialize_teacher
from app.crud.courses import serialize_course


async def get_all_students(tenant_id: str):
    students = []

    async for s in db.students.find({"tenantId": ObjectId(tenant_id)}):
        user = await db.users.find_one(
            {"_id": s["userId"], "tenantId": ObjectId(tenant_id)}
        )

        if not user:
            continue

        students.append({**serialize_student(s), "user": serialize_user(user)})

    return students


async def get_all_teachers(tenant_id: str):
    teachers = []

    async for t in db.teachers.find({"tenantId": ObjectId(tenant_id)}):
        user = await db.users.find_one(
            {"_id": t["userId"], "tenantId": ObjectId(tenant_id)}
        )

        if not user:
            continue

        teachers.append({**serialize_teacher(t), "user": serialize_user(user)})

    return teachers


async def get_all_courses(tenant_id: str):
    courses = []

    async for c in db.courses.find({"tenantId": ObjectId(tenant_id)}):
        courses.append(serialize_course(c))

    return courses
