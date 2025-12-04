from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    status: str
    courseCode: str
    duration: str
    thumbnailUrl: str
    modules: List[Any]
    teacherId: str
    tenantId: str
    enrolledStudents: int
    createdAt: datetime
    updatedAt: datetime
