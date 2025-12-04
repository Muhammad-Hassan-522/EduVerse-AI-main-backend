# app/routers/student_performance.py
from fastapi import APIRouter, HTTPException

from app.schemas.student_performance import (
    StudentPerformanceResponse,
    AddPointsRequest,
    WeeklyTimeRequest,
    BadgeRequest,
    CertificateRequest,
    CourseProgressRequest
)
from app.crud.student_performance import StudentPerformanceCRUD

router = APIRouter(
    prefix="/studentPerformance",
    tags=["Student Performance / Leaderboard"],
)


@router.get("/leaderboard/{tenantId}", response_model=StudentPerformanceResponse)
async def get_leaderboard(tenantId: str):
    doc = await StudentPerformanceCRUD.get_by_tenant(tenantId)
    if not doc:
        raise HTTPException(status_code=404, detail="Student performance not found")
    return doc


@router.patch("/leaderboard/{tenantId}/add-points", response_model=StudentPerformanceResponse)
async def add_points(tenantId: str, body: AddPointsRequest):
    return await StudentPerformanceCRUD.add_points(tenantId, body.points)


@router.patch("/leaderboard/{tenantId}/weekly-time", response_model=StudentPerformanceResponse)
async def weekly_time(tenantId: str, body: WeeklyTimeRequest):
    return await StudentPerformanceCRUD.add_weekly_time(tenantId, body.weekStart, body.minutes)


@router.patch("/leaderboard/{tenantId}/add-badge", response_model=StudentPerformanceResponse)
async def add_badge(tenantId: str, body: BadgeRequest):
    return await StudentPerformanceCRUD.add_badge(tenantId, body.dict())


@router.delete("/leaderboard/{tenantId}/remove-badge/{title}", response_model=StudentPerformanceResponse)
async def remove_badge(tenantId: str, title: str):
    return await StudentPerformanceCRUD.remove_badge(tenantId, title)


@router.patch("/leaderboard/{tenantId}/add-certificate", response_model=StudentPerformanceResponse)
async def add_certificate(tenantId: str, body: CertificateRequest):
    return await StudentPerformanceCRUD.add_certificate(tenantId, body.dict())


@router.delete("/leaderboard/{tenantId}/remove-certificate/{title}", response_model=StudentPerformanceResponse)
async def remove_certificate(tenantId: str, title: str):
    return await StudentPerformanceCRUD.remove_certificate(tenantId, title)

@router.get(
    "/studentPerformance/leaderboard-full",
    summary="Get Full Leaderboard (sorted + ranked)",
    tags=["Student Performance / Leaderboard"],
)
async def get_full_leaderboard():
    """
    Returns **all** studentPerformance documents,
    sorted by totalPoints, xp, level and with a `rank` field added.
    """
    data = await StudentPerformanceCRUD.get_full_leaderboard()   # <-- IMPORTANT: await
    return data     

@router.get("/studentPerformance/leaderboard/top5")
async def get_top5_leaderboard():
    return await StudentPerformanceCRUD.get_top5_leaderboard()

@router.patch("/leaderboard/{tenantId}/course-progress")
async def update_course_progress(tenantId: str, body: CourseProgressRequest):
    return await StudentPerformanceCRUD.update_course_progress(
        tenantId, 
        body.courseId, 
        body.completionPercentage, 
        body.lastActive
    )

@router.get("/leaderboard/{tenantId}/course-stats")
async def get_course_stats(tenantId: str):
    return await StudentPerformanceCRUD.get_course_stats(tenantId)
