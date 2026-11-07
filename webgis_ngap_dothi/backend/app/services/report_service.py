"""
services/report_service.py - Logic nghiệp vụ duyệt báo cáo ngập
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repo import ReportRepository
from app.repositories.flood_repo import FloodRepository
from app.models.db_models.report import ReportStatus
from app.models.schemas.report import ReportCreateRequest, ReportReviewRequest, ReportResponse, ReportListResponse


class ReportService:

    def __init__(self, db: AsyncSession):
        self.report_repo = ReportRepository(db)
        self.flood_repo  = FloodRepository(db)

    async def submit_report(self, data: ReportCreateRequest,
                             user_id: int = None) -> ReportResponse:
        """Người dùng gửi báo cáo điểm ngập"""
        report = await self.report_repo.create(
            lng=data.longitude,
            lat=data.latitude,
            description=data.description,
            image_url=data.image_url,
            reporter_id=user_id,
        )
        return ReportResponse.model_validate(report)

    async def get_reports(self, status_filter: str = None,
                           page: int = 1, limit: int = 20) -> ReportListResponse:
        """Admin lấy danh sách báo cáo"""
        status = ReportStatus(status_filter) if status_filter else None
        reports, total = await self.report_repo.get_all(status=status, page=page, limit=limit)
        return ReportListResponse(
            total=total, page=page, limit=limit,
            reports=[ReportResponse.model_validate(r) for r in reports],
        )

    async def review_report(self, report_id: int, data: ReportReviewRequest,
                             admin_id: int) -> ReportResponse:
        """
        Admin duyệt hoặc từ chối báo cáo.
        Nếu VERIFIED → tự động tạo FloodPoint từ tọa độ báo cáo.
        """
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Báo cáo không tồn tại")
        if report.status != ReportStatus.PENDING:
            raise HTTPException(status_code=400, detail="Báo cáo đã được xử lý trước đó")

        updated = await self.report_repo.update_status(
            report_id=report_id,
            status=data.status,
            reviewed_by=admin_id,
            review_note=data.review_note,
        )

        # Nếu xác minh → tạo FloodPoint chính thức
        if data.status == ReportStatus.VERIFIED:
            from sqlalchemy import text
            coords = await self.report_repo.db.execute(
                text("SELECT ST_X(geom) AS lng, ST_Y(geom) AS lat FROM flood_reports WHERE id = :id"),
                {"id": report_id}
            )
            row = coords.fetchone()
            if row:
                await self.flood_repo.create_flood_point(
                    lng=row.lng, lat=row.lat,
                    depth_m=0.3, severity="medium",
                    source="report",
                )

        return ReportResponse.model_validate(updated)

    async def get_my_reports(self, user_id: int) -> list[ReportResponse]:
        """Người dùng xem báo cáo của mình"""
        reports = await self.report_repo.get_by_user(user_id)
        return [ReportResponse.model_validate(r) for r in reports]

