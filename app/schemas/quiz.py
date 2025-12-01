from pydantic import BaseModel
from typing import List
from datetime import datetime

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correctAnswer: str

class QuizCreate(BaseModel):
    courseId: str
    teacherId: str
    title: str
    description: str
    dueDate: datetime
    questions: List[QuizQuestion]
    timeLimitMinutes: int
    totalMarks: int

class QuizResponse(QuizCreate):
    id: str
    status: str
