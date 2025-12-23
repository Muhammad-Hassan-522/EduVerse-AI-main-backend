# from app.db.database import db
# from app.schemas.assignment_submissions import AssignmentSubmissionCreate
# from datetime import datetime
# from bson import ObjectId
# from typing import List, Optional

# def serialize_submission(sub):
#     def fix_date(value):
#         if isinstance(value, datetime):
#             return value
#         if value is None:
#             return None
#         if hasattr(value, "as_datetime"):
#             return value.as_datetime()
#         return None

#     return {
#         "id": str(sub["_id"]),
#         "studentId": str(sub["studentId"]),
#         "assignmentId": str(sub["assignmentId"]),
#         "submittedAt": fix_date(sub.get("submittedAt")),
#         "fileUrl": sub.get("fileUrl"),
#         "obtainedMarks": sub.get("obtainedMarks"),
#         "feedback": sub.get("feedback"),
#         "courseId": str(sub["courseId"]),
#         "tenantId": str(sub["tenantId"]),
#         "gradedAt": fix_date( sub.get("gradedAt")),
#     }

# async def create_submission(data: AssignmentSubmissionCreate):
#     submission_data = data.dict()
#     submission_data.update({
#         "studentId": ObjectId(submission_data["studentId"]),
#         "assignmentId": ObjectId(submission_data["assignmentId"]),
#         "courseId": ObjectId(submission_data["courseId"]),
#         "tenantId": ObjectId(submission_data["tenantId"]),
#         "submittedAt":datetime.utcnow(),
#         "obtainedMarks": None,
#         "feedback": None,
#         "gradedAt": None
#     })

#     result = await db.assignmentSubmissions.insert_one(submission_data)
#     new_submission = await db.assignmentSubmissions.find_one({"_id": result.inserted_id})
#     return serialize_submission(new_submission)


# async def get_all_submissions() -> List[dict]:
#     cursor = db.assignmentSubmissions.find().sort("submittedAt", -1)
#     submissions = [serialize_submission(s) async for s in cursor]
#     return submissions


# async def get_submissions_by_student(student_id: str) -> List[dict]:
#     cursor = db.assignmentSubmissions.find({"studentId": ObjectId(student_id)})
#     submissions = [serialize_submission(s) async for s in cursor]
#     return submissions


# async def get_submissions_by_assignment(assignment_id: str) -> List[dict]:
#     cursor = db.assignmentSubmissions.find({"assignmentId": ObjectId(assignment_id)})
#     submissions = [serialize_submission(s) async for s in cursor]
#     return submissions


# async def grade_submission(submission_id: str, marks: Optional[int] = None, feedback: Optional[str] = None):
#     updates = {"gradedAt": datetime.utcnow()}
#     if marks is not None:
#         updates["obtainedMarks"] = marks
#     if feedback is not None:
#         updates["feedback"] = feedback

#     await db.assignmentSubmissions.update_one(
#         {"_id": ObjectId(submission_id)},
#         {"$set": updates}
#     )
#     updated = await db.assignmentSubmissions.find_one({"_id": ObjectId(submission_id)})
#     return serialize_submission(updated)


# async def delete_submission(submission_id: str):
#     result = await db.assignmentSubmissions.delete_one({"_id": ObjectId(submission_id)})
#     return result.deleted_count > 0


from app.db.database import db
from datetime import datetime
from bson import ObjectId
from typing import List, Optional


def serialize_submission(sub):
    return {
        "id": str(sub["_id"]),
        "studentId": str(sub["studentId"]),
        "assignmentId": str(sub["assignmentId"]),
        "submittedAt": sub["submittedAt"],
        "fileUrl": sub["fileUrl"],
        "obtainedMarks": sub.get("obtainedMarks"),
        "feedback": sub.get("feedback"),
        "courseId": str(sub["courseId"]),
        "tenantId": str(sub["tenantId"]),
        "gradedAt": sub.get("gradedAt"),
    }


async def create_submission(data, student_id: str, tenant_id: str):
    submission = {
        "studentId": ObjectId(student_id),
        "assignmentId": ObjectId(data.assignmentId),
        "courseId": ObjectId(data.courseId),
        "tenantId": ObjectId(tenant_id),
        "fileUrl": data.fileUrl,
        "submittedAt": datetime.utcnow(),
        "obtainedMarks": None,
        "feedback": None,
        "gradedAt": None,
    }

    result = await db.assignmentSubmissions.insert_one(submission)
    doc = await db.assignmentSubmissions.find_one({"_id": result.inserted_id})
    return serialize_submission(doc)


async def get_all_submissions(tenant_id: str) -> List[dict]:
    cursor = db.assignmentSubmissions.find({"tenantId": ObjectId(tenant_id)}).sort(
        "submittedAt", -1
    )
    return [serialize_submission(s) async for s in cursor]


async def get_submissions_by_student(student_id: str, tenant_id: str):
    cursor = db.assignmentSubmissions.find(
        {
            "studentId": ObjectId(student_id),
            "tenantId": ObjectId(tenant_id),
        }
    )
    return [serialize_submission(s) async for s in cursor]


async def get_submissions_by_assignment(assignment_id: str, tenant_id: str):
    cursor = db.assignmentSubmissions.find(
        {
            "assignmentId": ObjectId(assignment_id),
            "tenantId": ObjectId(tenant_id),
        }
    )
    return [serialize_submission(s) async for s in cursor]


async def grade_submission(
    submission_id: str,
    tenant_id: str,
    marks: Optional[int],
    feedback: Optional[str],
):
    updates = {"gradedAt": datetime.utcnow()}
    if marks is not None:
        updates["obtainedMarks"] = marks
    if feedback is not None:
        updates["feedback"] = feedback

    await db.assignmentSubmissions.update_one(
        {
            "_id": ObjectId(submission_id),
            "tenantId": ObjectId(tenant_id),
        },
        {"$set": updates},
    )

    doc = await db.assignmentSubmissions.find_one(
        {
            "_id": ObjectId(submission_id),
            "tenantId": ObjectId(tenant_id),
        }
    )
    return serialize_submission(doc)


async def delete_submission(submission_id: str, tenant_id: str):
    result = await db.assignmentSubmissions.delete_one(
        {
            "_id": ObjectId(submission_id),
            "tenantId": ObjectId(tenant_id),
        }
    )
    return result.deleted_count > 0
