
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}

# Module Schema
class ModuleSchema(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    order: int = 0

# Base Course Schema
class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: str
    status: str = "Active"  # Active, Inactive, Upcoming, Completed
    courseCode: Optional[str] = None
    duration: Optional[str] = None
    thumbnailUrl: Optional[str] = ""
    modules: List[ModuleSchema] = []

# Create Course Request
class CourseCreate(CourseBase):
    teacherId: str  #  Required - client must provide this
    tenantId: Optional[str] = None  #  Optional - will be set by router from DB
    enrolledStudents: int = 0

# Update Course Request - ALL fields from CourseBase should be optional
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    courseCode: Optional[str] = None  
    duration: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    modules: Optional[List[ModuleSchema]] = None
    
    

# Course Response
class CourseResponse(CourseBase):
    id: str = Field(alias="_id")
    teacherId: str
    tenantId: str
    enrolledStudents: int = 0
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        #  - allows using both 'id' and '_id' field names
        allow_population_by_field_name = True
        # Alternative for newer Pydantic versions (if above doesn't work):
        # from_attributes = True

# Course Enrollment Request
class CourseEnrollment(BaseModel):
    studentId: str
    courseId: str

# Course with Progress (for students)
class CourseWithProgress(CourseResponse):
    progress: Optional[int] = 0  # 0-100
    lessonsCompleted: Optional[int] = 0
    totalLessons: Optional[int] = 0
    nextLesson: Optional[str] = None