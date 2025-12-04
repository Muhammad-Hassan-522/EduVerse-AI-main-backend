from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class AssignmentResponse(BaseModel):
    id: str
    courseId: str
    teacherId: str
    title: str
    description: str
    dueDate: datetime
    totalMarks: int
    passingMarks: int
    status: str
    fileUrl: str
    tenantId: str
    allowedFormats: List[str] = []
    uploadedAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class AssignmentSubmissionCreate(BaseModel):
    fileUrl: str  # e.g. link/path of uploaded file
    answerText: Optional[str] = None  # if you support text


class AssignmentSubmissionResponse(BaseModel):
    id: str
    studentId: str
    assignmentId: str
    courseId: str
    fileUrl: str
    answerText: Optional[str] = None
    submittedAt: datetime
    status: str
    obtainedMarks: Optional[float] = None
