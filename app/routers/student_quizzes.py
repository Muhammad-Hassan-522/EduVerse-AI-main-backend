from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime

from app.db.database import students_collection, quizzes_collection, quiz_submissions_collection
from app.schemas.quiz_submission import QuizSubmitRequest, QuizSubmissionResponse
from app.utils.mongo import fix_object_ids
from app.crud import quiz_submission as crud_quiz_submission

router = APIRouter(prefix="/students", tags=["Student Quizzes"])


# ----------------- Get quizzes for a course -----------------
@router.get("/{student_id}/courses/{course_id}/quizzes")
async def get_quizzes_for_student(student_id: str, course_id: str):

    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(404, "Student not found")

    if course_id not in student.get("enrolledCourses", []):
        raise HTTPException(400, "Student is not enrolled in this course")

    quizzes = await quizzes_collection.find({"courseId": ObjectId(course_id)}).to_list(None)
    return fix_object_ids(quizzes)


# ----------------- Submit a quiz -----------------
@router.post("/{student_id}/quizzes/{quiz_id}/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(student_id: str, quiz_id: str, payload: QuizSubmitRequest):

    quiz = await quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    course_id = str(quiz["courseId"])

    student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(404, "Student not found")

    if course_id not in student.get("enrolledCourses", []):
        raise HTTPException(400, "Student not enrolled in this course")

    # Evaluate marks
    total = quiz["totalMarks"]
    questions = quiz["questions"]
    correct = 0

    for i, q in enumerate(questions):
        if str(i) in payload.answers and payload.answers[str(i)] == q["correctAnswer"]:
            correct += 1

    obtained = int((correct / len(questions)) * total)

    submission = {
        "studentId": ObjectId(student_id),
        "quizId": ObjectId(quiz_id),
        "courseId": ObjectId(course_id),
        "obtainedMarks": obtained,
        "percentage": (correct / len(questions)) * 100,
        "status": "submitted",
        "tenantId": student["tenantId"],
    }

    result = await quiz_submissions_collection.insert_one(submission)
    saved = await quiz_submissions_collection.find_one({"_id": result.inserted_id})

    return QuizSubmissionResponse(**fix_object_ids(saved))
# -------- Get result for a specific quiz for this student --------
@router.get("/{student_id}/quizzes/{quiz_id}/result", response_model=QuizSubmissionResponse)
async def get_quiz_result(student_id: str, quiz_id: str):

    submission = await crud_quiz_submission.get_submission_by_student_and_quiz(
        student_id, quiz_id
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Result not found for this quiz")

    # Convert ObjectId to string and rename _id → id
    submission["id"] = submission["_id"]
    del submission["_id"]

    return QuizSubmissionResponse(**submission)



# -------- Get all quiz results for this student --------
@router.get("/{student_id}/quiz-results", response_model=list[QuizSubmissionResponse])
async def get_all_quiz_results(student_id: str):

    submissions = await crud_quiz_submission.get_submissions_by_student(student_id)

    results = []
    for sub in submissions:
        sub["id"] = sub["_id"]
        del sub["_id"]
        results.append(QuizSubmissionResponse(**sub))

    return results


