-- =============================================================
-- init_db.sql - Khởi tạo PostgreSQL + PostGIS cho WebGIS Ngập Đô Thị
-- Chạy 1 lần duy nhất trước khi dùng Alembic
-- =============================================================

-- 1. Bật extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Bảng users
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            VARCHAR(10)  NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

-- 3. Bảng điểm ngập
CREATE TABLE IF NOT EXISTS flood_points (
    id          SERIAL PRIMARY KEY,
    geom        GEOMETRY(POINT, 4326) NOT NULL,
    depth_m     FLOAT NOT NULL,
    severity    VARCHAR(10) NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    scenario    INTEGER,
    source      VARCHAR(50) DEFAULT 'manual',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_flood_points_geom ON flood_points USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_flood_points_scenario ON flood_points(scenario);

-- 4. Bảng vùng ngập (polygon kịch bản)
CREATE TABLE IF NOT EXISTS flood_zones (
    id          SERIAL PRIMARY KEY,
    geom        GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    scenario_mm INTEGER NOT NULL,
    avg_depth_m FLOAT,
    area_sqm    FLOAT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_flood_zones_geom     ON flood_zones USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_flood_zones_scenario ON flood_zones(scenario_mm);

-- 5. Bảng báo cáo ngập người dùng
CREATE TABLE IF NOT EXISTS flood_reports (
    id          SERIAL PRIMARY KEY,
    geom        GEOMETRY(POINT, 4326) NOT NULL,
    description TEXT,
    image_url   VARCHAR(500),
    status      VARCHAR(10) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'verified', 'rejected')),
    reporter_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    review_note TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_flood_reports_geom   ON flood_reports USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_flood_reports_status ON flood_reports(status);

-- 6. Bảng node giao thông
CREATE TABLE IF NOT EXISTS road_nodes (
    id      BIGSERIAL PRIMARY KEY,
    geom    GEOMETRY(POINT, 4326) NOT NULL,
    osm_id  BIGINT
);
CREATE INDEX IF NOT EXISTS idx_road_nodes_geom ON road_nodes USING GIST(geom);

-- 7. Bảng cạnh đường (edge)
CREATE TABLE IF NOT EXISTS road_edges (
    id            SERIAL PRIMARY KEY,
    source        BIGINT REFERENCES road_nodes(id),
    target        BIGINT REFERENCES road_nodes(id),
    geom          GEOMETRY(LINESTRING, 4326) NOT NULL,
    osm_id        BIGINT,
    name          VARCHAR(200),
    road_type     VARCHAR(50),
    length_m      FLOAT NOT NULL,
    max_speed     INTEGER DEFAULT 50,
    oneway        BOOLEAN DEFAULT FALSE,
    flood_depth_m FLOAT DEFAULT 0.0,
    is_blocked    BOOLEAN DEFAULT FALSE,
    cost_normal   FLOAT,
    cost_flooded  FLOAT
);
CREATE INDEX IF NOT EXISTS idx_road_edges_geom   ON road_edges USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_road_edges_source ON road_edges(source);
CREATE INDEX IF NOT EXISTS idx_road_edges_target ON road_edges(target);

-- 8. Tài khoản Admin mặc định (đổi mật khẩu sau khi deploy!)
-- Mật khẩu: admin123 (đã bcrypt hash)
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'admin',
    'admin@webgis.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBpj5GKi9M3Jqe',
    'Quản trị viên',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- =============================================================
-- Hoàn tất! Chạy tiếp: alembic upgrade head
-- =============================================================

