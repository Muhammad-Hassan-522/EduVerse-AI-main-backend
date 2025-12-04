from pydantic import BaseModel
from datetime import datetime

class QuizSubmitRequest(BaseModel):
    answers: dict   # { "questionIndex": "selected_answer" }

class QuizSubmissionResponse(BaseModel):
    id: str
    studentId: str
    quizId: str
    courseId: str
    submittedAt: datetime
    obtainedMarks: int
    percentage: float
    status: str
    tenantId: str
