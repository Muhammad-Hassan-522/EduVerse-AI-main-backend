from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["LMS"]
student_performance_collection = db["studentPerformance"]
students_collection = db["students"]
courses_collection = db["courses"]
assignments_collection = db["assignments"]              
assignment_submissions_collection = db["assignmentSubmissions"]
quizzes_collection = db["quizzes"]
quiz_submissions_collection = db["quizSubmissions"]


