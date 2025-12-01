from fastapi import FastAPI
from app.routers import students
from app.routers import student_performance
from app.routers import  courses
from app.routers import  student_courses
from app.routers import  student_assignments
from app.routers import  student_quizzes

app = FastAPI(title="EduVerse AI Backend")

@app.get("/")
def root():
    return {"message" : "Success !"}

app.include_router(students.router)
app.include_router(student_performance.router)
app.include_router(courses.router)          
app.include_router(student_courses.router) 
app.include_router(student_assignments.router)
app.include_router(student_quizzes.router)