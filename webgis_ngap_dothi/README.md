# WebGIS Ngập Đô Thị

> Hệ thống WebGIS hỗ trợ cảnh báo ngập đô thị và tìm đường tránh ngập sử dụng thuật toán Dijkstra/A* trên dữ liệu OpenStreetMap và DEM.

## Tính năng chính

- 🗺️ **Hiển thị bản đồ** vùng ngập theo kịch bản mưa (100mm / 200mm / 300mm)
- 🧭 **Tìm đường tránh ngập** sử dụng thuật toán A* với trọng số ngập
- 📢 **Báo cáo điểm ngập** từ người dùng với GPS
- ✅ **Xác minh báo cáo** bởi Admin
- 📊 **Dashboard thống kê** tổng quan tình trạng ngập

## Công nghệ

| Tầng      | Công nghệ                              |
|-----------|----------------------------------------|
| Backend   | FastAPI + Python                       |
| Database  | PostgreSQL + PostGIS                   |
| GIS       | GeoPandas, Rasterio, Shapely           |
| Routing   | NetworkX (Dijkstra / A*)               |
| Frontend  | HTML / CSS / JavaScript (Vanilla)      |
| Bản đồ   | Leaflet.js + OpenStreetMap             |

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/your-username/webgis_ngap_dothi.git
cd webgis_ngap_dothi
```

### 2. Cài đặt Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# Cài thư viện
pip install -r requirements.txt

# Cấu hình môi trường
copy .env.example .env
# Chỉnh sửa .env với thông tin DB của bạn
```

### 3. Khởi tạo Database

```bash
# Tạo database PostgreSQL
createdb webgis_ngap

# Chạy script khởi tạo PostGIS
psql -U postgres -d webgis_ngap -f scripts/init_db.sql

# Chạy migrations Alembic
alembic upgrade head
```

### 4. Chạy Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Docs: http://localhost:8000/api/docs

### 5. Chạy Frontend

Dùng Live Server (VS Code extension) hoặc:

```bash
cd frontend
python -m http.server 5500
```

Mở: http://localhost:5500/pages/user/index_map.html

## Cấu trúc dự án

```
webgis_ngap_dothi/
├── backend/          # FastAPI (Controller - Service - Repository)
├── frontend/         # HTML / CSS / JavaScript (Leaflet.js)
└── docs/             # Tài liệu kỹ thuật
```

## Tài liệu

- [Thiết kế Database](docs/database_design.md)
- [API Documentation](docs/api_documentation.md)
- [Kiến trúc hệ thống](docs/system_architecture.md)

## Chạy Tests

```bash
cd backend
pytest tests/ -v
```

## Tác giả

Luận văn tốt nghiệp — Hệ thống WebGIS hỗ trợ cảnh báo ngập đô thị

