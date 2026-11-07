"""
api/route_report.py - Controller gửi và duyệt báo cáo ngập
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.repositories.db_connection import get_db
from app.services.report_service import ReportService
from app.services.auth_service import get_current_user, require_admin
from app.models.db_models.user import User
from app.models.schemas.report import (
    ReportCreateRequest, ReportReviewRequest,
    ReportResponse, ReportListResponse
)

router = APIRouter()


@router.post("/", response_model=ReportResponse, status_code=201)
async def submit_report(
    data: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Người dùng gửi báo cáo điểm ngập mới"""
    svc = ReportService(db)
    return await svc.submit_report(data, user_id=current_user.id)


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    status: Optional[str] = Query(None, description="pending | verified | rejected"),
    page:   int = Query(1, ge=1),
    limit:  int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),   # Chỉ Admin
):
    """Admin lấy danh sách báo cáo ngập"""
    svc = ReportService(db)
    return await svc.get_reports(status_filter=status, page=page, limit=limit)


@router.get("/my", response_model=list[ReportResponse])
async def my_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Người dùng xem báo cáo của mình"""
    svc = ReportService(db)
    return await svc.get_my_reports(current_user.id)


@router.get("/geojson")
async def reports_geojson(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Trả về báo cáo ngập dạng GeoJSON cho bản đồ"""
    from app.repositories.report_repo import ReportRepository
    from app.models.db_models.report import ReportStatus
    repo = ReportRepository(db)
    s = ReportStatus(status) if status else None
    return await repo.get_reports_geojson(status=s)


@router.patch("/{report_id}/review", response_model=ReportResponse)
async def review_report(
    report_id: int,
    data: ReportReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),   # Chỉ Admin
):
    """Admin duyệt hoặc từ chối báo cáo ngập"""
    svc = ReportService(db)
    return await svc.review_report(report_id, data, admin_id=current_user.id)

