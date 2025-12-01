from bson import ObjectId
from app.db.database import assignments_collection, assignment_submissions_collection, students_collection
from app.utils.mongo import fix_object_ids
from app.core.settings import TENANT_ID
from datetime import datetime


async def get_assignments_by_course(course_id: str):
    # courseId in DB may be string or ObjectId, so we handle both
    query = {
        "tenantId": TENANT_ID,
        "status": "Active",
        "$or": [
            {"courseId": course_id},
            {"courseId": ObjectId(course_id)},
        ]
    }
    cursor = assignments_collection.find(query)
    docs = await cursor.to_list(length=None)
    return fix_object_ids(docs)


async def get_assignments_for_student(student_id: str):
    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        return []

    enrolled = student.get("enrolledCourses", [])
    if not enrolled:
        return []

    # assignments for all enrolled courses
    query = {
        "tenantId": TENANT_ID,
        "status": "Active",
        "courseId": {"$in": enrolled},
    }
    cursor = assignments_collection.find(query)
    docs = await cursor.to_list(length=None)
    return fix_object_ids(docs)


async def create_assignment_submission(student_id: str, assignment_id: str, payload: dict):
    # we expect payload already contains fileUrl, answerText (optional)
    now = datetime.utcnow()

    # first get assignment (also to know courseId)
    assignment = await assignments_collection.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        return None

    data = {
        "studentId": student_id,
        "assignmentId": assignment_id,
        "courseId": str(assignment.get("courseId")),
        "fileUrl": payload.get("fileUrl"),
        "answerText": payload.get("answerText"),
        "submittedAt": now,
        "status": "submitted",
        "obtainedMarks": None,
        "tenantId": TENANT_ID,
    }

    result = await assignment_submissions_collection.insert_one(data)
    new_doc = await assignment_submissions_collection.find_one({"_id": result.inserted_id})
    return fix_object_ids(new_doc)


async def get_submission_for_student_assignment(student_id: str, assignment_id: str):
    doc = await assignment_submissions_collection.find_one(
        {"studentId": student_id, "assignmentId": assignment_id}
    )
    if not doc:
        return None
    return fix_object_ids(doc)
