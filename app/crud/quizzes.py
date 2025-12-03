from bson import ObjectId
from datetime import datetime
from app.db.database import db

def serialize_quiz(quiz):
    """
    Convert MongoDB quiz document into a JSON serializable dictionary.
    - Converts ObjectId fields to strings.
    - Ensures default values exist (status, aiGenerated).
    """
    return {
        "id": str(quiz["_id"]),
        "courseId": str(quiz["courseId"]),
        "teacherId": str(quiz["teacherId"]),
        "tenantId": str(quiz["tenantId"]),
        "quizNumber": quiz["quizNumber"],
        "description": quiz.get("description"),
        "dueDate": quiz["dueDate"],    # Already a datetime object
        "questions": quiz["questions"], # Stored as list of dicts
        "timeLimitMinutes": quiz.get("timeLimitMinutes"),
        "totalMarks": quiz["totalMarks"],
        "aiGenerated": quiz.get("aiGenerated", False),
        "status": quiz.get("status", "active"),
        "createdAt": quiz["createdAt"],
        "updatedAt": quiz["updatedAt"],
    }


async def create_quiz(request):
    """Insert a new quiz into MongoDB."""

    # Convert Pydantic model → Python dict
    data = request.dict()
    
    # Convert string IDs to ObjectId & add metadata
    data.update({
        "courseId": ObjectId(data["courseId"]),
        "teacherId": ObjectId(data["teacherId"]),
        "tenantId": ObjectId(data["tenantId"]),
        "status": "active",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    })

    # Insert into MongoDB
    res = await db.quizzes.insert_one(data)

    # Fetch inserted document
    new_quiz = await db.quizzes.find_one({"_id": res.inserted_id})

    return serialize_quiz(new_quiz)


async def get_quiz(_id):
    """Fetch a single quiz using its ObjectId."""

    quiz = await db.quizzes.find_one({"_id": ObjectId(_id)})
    return serialize_quiz(quiz) if quiz else None


async def get_quizzes_filtered(
    tenantId=None, teacherId=None, courseId=None,
    search=None, sort="createdAt", page=1, limit=10
):
    """
    Fetch quizzes with:
    - Filtering by tenant / teacher / course
    - Text search on description
    - Sorting (ASC / DESC)
    - Pagination
    """

    query = {}

    # Add filtering conditions if provided
    if tenantId:
        query["tenantId"] = ObjectId(tenantId)

    if teacherId:
        query["teacherId"] = ObjectId(teacherId)

    if courseId:
        query["courseId"] = ObjectId(courseId)

    # Enables text search in description field
    if search:
        query["description"] = {"$regex": search, "$options": "i"}

    # Determine sorting direction
    sort_dir = -1 if sort.startswith("-") else 1
    sort_field = sort.lstrip("-")

    # Apply filtering, sorting, pagination
    cursor = (
        db.quizzes.find(query)
        .sort(sort_field, sort_dir)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    # Convert to list of serialized quizzes
    return [serialize_quiz(q) async for q in cursor]

async def update_quiz(_id, teacherId, updates):
    """Update a quiz only if the teacher is the owner."""

    quiz = await db.quizzes.find_one({"_id": ObjectId(_id)})
    if not quiz:
        return None

    # Permission check
    if str(quiz["teacherId"]) != str(teacherId):
        return "Unauthorized"

    # Update timestamp
    updates["updatedAt"] = datetime.utcnow()

    # Apply updates
    await db.quizzes.update_one({"_id": ObjectId(_id)}, {"$set": updates})

    # Fetch updated quiz
    updated_quiz = await db.quizzes.find_one({"_id": ObjectId(_id)})

    return serialize_quiz(updated_quiz)


async def delete_quiz(_id, teacherId):
    """ Delete quiz only if teacher owns it. """

    quiz = await db.quizzes.find_one({"_id": ObjectId(_id)})
    if not quiz:
        return None

    # Permission check
    if str(quiz["teacherId"]) != str(teacherId):
        return "Unauthorized"

    # Delete document
    await db.quizzes.delete_one({"_id": ObjectId(_id)})

    return True
