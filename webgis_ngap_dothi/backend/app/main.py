"""
main.py - Điểm khởi chạy ứng dụng FastAPI
Đăng ký tất cả router, cấu hình CORS, middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.route_map import router as map_router
from app.api.route_routing import router as routing_router
from app.api.route_report import router as report_router
from app.api.route_auth import router as auth_router

# ------------------------------------------------------------------ #
#  Khởi tạo ứng dụng
# ------------------------------------------------------------------ #
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="WebGIS hỗ trợ cảnh báo ngập đô thị và tìm đường tránh ngập",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ------------------------------------------------------------------ #
#  CORS — cho phép frontend gọi backend
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
#  Đăng ký Router
# ------------------------------------------------------------------ #
app.include_router(auth_router,    prefix="/api/auth",    tags=["Authentication"])
app.include_router(map_router,     prefix="/api/map",     tags=["Map & Flood Layers"])
app.include_router(routing_router, prefix="/api/routing", tags=["Routing"])
app.include_router(report_router,  prefix="/api/reports", tags=["Flood Reports"])


# ------------------------------------------------------------------ #
#  Health check
# ------------------------------------------------------------------ #
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

