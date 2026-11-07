"""
schemas/report.py - Pydantic schemas cho FloodReport
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ReportStatus(str, Enum):
    PENDING  = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ---------- Request schemas ---------- #

class ReportCreateRequest(BaseModel):
    longitude:   float
    latitude:    float
    description: Optional[str] = None
    image_url:   Optional[str] = None


class ReportReviewRequest(BaseModel):
    status:      ReportStatus
    review_note: Optional[str] = None


# ---------- Response schemas ---------- #

class ReportResponse(BaseModel):
    id:           int
    longitude:    float
    latitude:     float
    description:  Optional[str]
    image_url:    Optional[str]
    status:       ReportStatus
    reporter_id:  Optional[int]
    reviewed_by:  Optional[int]
    review_note:  Optional[str]
    created_at:   datetime
    reviewed_at:  Optional[datetime]

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    total:   int
    page:    int
    limit:   int
    reports: list[ReportResponse]

