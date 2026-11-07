"""
repositories/report_repo.py - SQL truy vấn báo cáo ngập người dùng
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional

from app.models.db_models.report import FloodReport, ReportStatus


class ReportRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lng: float, lat: float, description: str = None,
                     image_url: str = None, reporter_id: int = None) -> FloodReport:
        """Tạo báo cáo ngập mới"""
        report = FloodReport(
            geom=f"SRID=4326;POINT({lng} {lat})",
            description=description,
            image_url=image_url,
            reporter_id=reporter_id,
            status=ReportStatus.PENDING,
        )
        self.db.add(report)
        await self.db.flush()
        return report

    async def get_by_id(self, report_id: int) -> Optional[FloodReport]:
        result = await self.db.execute(
            select(FloodReport).where(FloodReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, status: Optional[ReportStatus] = None,
                      page: int = 1, limit: int = 20) -> Tuple[List[FloodReport], int]:
        """Lấy danh sách báo cáo có phân trang"""
        stmt = select(FloodReport)
        count_stmt = select(func.count(FloodReport.id))

        if status:
            stmt = stmt.where(FloodReport.status == status)
            count_stmt = count_stmt.where(FloodReport.status == status)

        total = (await self.db.execute(count_stmt)).scalar()
        stmt = stmt.offset((page - 1) * limit).limit(limit).order_by(FloodReport.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def get_by_user(self, user_id: int) -> List[FloodReport]:
        """Lấy báo cáo của một người dùng"""
        result = await self.db.execute(
            select(FloodReport)
            .where(FloodReport.reporter_id == user_id)
            .order_by(FloodReport.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(self, report_id: int, status: ReportStatus,
                             reviewed_by: int, review_note: str = None) -> Optional[FloodReport]:
        """Admin duyệt hoặc từ chối báo cáo"""
        from datetime import datetime, timezone
        stmt = (
            update(FloodReport)
            .where(FloodReport.id == report_id)
            .values(
                status=status,
                reviewed_by=reviewed_by,
                review_note=review_note,
                reviewed_at=datetime.now(timezone.utc),
            )
            .returning(FloodReport)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_reports_geojson(self, status: Optional[ReportStatus] = None) -> dict:
        """Trả về báo cáo ngập dạng GeoJSON"""
        from sqlalchemy import text
        where = f"WHERE status = '{status.value}'" if status else ""
        sql = text(f"""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', COALESCE(json_agg(
                    json_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(geom)::json,
                        'properties', json_build_object(
                            'id', id,
                            'description', description,
                            'status', status,
                            'created_at', created_at
                        )
                    )
                ), '[]'::json)
            ) AS geojson
            FROM flood_reports {where}
        """)
        result = await self.db.execute(sql)
        row = result.fetchone()
        return row.geojson if row else {"type": "FeatureCollection", "features": []}

