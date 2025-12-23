from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.roles import admins, students, super_admin, teachers
from app.routers.dashboards import admin_dashboard
from app.routers import (
    assignment_submissions,
    assignments,
    courses,
    quiz_submissions,
    quizzes,
    student_performance,
    subscription,
    tenants,
)
from app.routers.auth import admin_auth, student_auth, teacher_auth, login

app = FastAPI(
    title="EduVerse AI Backend",
    description="Multi-Tenant E-Learning Platform API",
    version="1.0.0",
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
        "status": "operational",
    }


# Include routers

app.include_router(admin_auth.router)
app.include_router(student_auth.router)
app.include_router(teacher_auth.router)
# app.include_router(admin_dashboard.router)

app.include_router(login.router)

app.include_router(super_admin.router)
app.include_router(admins.router)
app.include_router(students.router)
app.include_router(teachers.router)

# Eman
app.include_router(student_performance.router)

# Tayyaba
app.include_router(courses.router)

# Ayesha
app.include_router(assignments.router)
app.include_router(assignment_submissions.router)


# Hassan
app.include_router(tenants.router)
app.include_router(quizzes.router)
app.include_router(quiz_submissions.router)

# Manahil
app.include_router(subscription.router)
