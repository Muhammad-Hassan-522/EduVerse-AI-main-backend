from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    courses, 
    students, 
    assignments, 
    assignment_submissions, 
    superAdmin, 
    tenants, 
    quizzes, 
    quiz_submissions, 
    admins, 
    teachers, 
    subscription, 
    student_performance, 
    student_courses, 
    student_assignments, 
    student_quizzes
)

app = FastAPI(
    title="EduVerse AI Backend",
    description="Multi-tenant e-learning platform API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ['http://localhost:4200'] for Angular dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "EduVerse AI Backend API",
        "version": "1.0.0",
        "status": "operational"
    }

# Include routers

# Eman
app.include_router(students.router)
app.include_router(student_performance.router)
app.include_router(student_courses.router) 
app.include_router(student_assignments.router)
app.include_router(student_quizzes.router)

# Tayyaba
app.include_router(courses.router)

# Ayesha
app.include_router(superAdmin.router)
app.include_router(assignments.router)
app.include_router(assignment_submissions.router)


# Hassan
app.include_router(tenants.router)
app.include_router(quizzes.router)
app.include_router(quiz_submissions.router)

# Manahil
app.include_router(admins.router)
app.include_router(subscription.router)
app.include_router(teachers.router)
