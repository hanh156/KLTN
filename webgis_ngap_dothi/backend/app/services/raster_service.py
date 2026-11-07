"""
services/raster_service.py - Đọc và xử lý dữ liệu DEM/GeoTIFF
"""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional

try:
    import rasterio
    from rasterio.mask import mask as raster_mask
    from rasterio.warp import transform_bounds
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

from app.core.config import settings


class RasterService:

    def __init__(self):
        self.dem_path = Path(settings.DEM_FILE)

    def _check_rasterio(self):
        if not RASTERIO_AVAILABLE:
            raise RuntimeError("Thư viện rasterio chưa được cài đặt: pip install rasterio")

    def get_dem_info(self) -> dict:
        """Lấy thông tin metadata của file DEM"""
        self._check_rasterio()
        if not self.dem_path.exists():
            raise FileNotFoundError(f"Không tìm thấy DEM: {self.dem_path}")

        with rasterio.open(self.dem_path) as src:
            bounds = src.bounds
            return {
                "crs":        src.crs.to_string(),
                "width":      src.width,
                "height":     src.height,
                "resolution": src.res,
                "bounds": {
                    "west":  bounds.left,
                    "south": bounds.bottom,
                    "east":  bounds.right,
                    "north": bounds.top,
                },
                "nodata": src.nodata,
            }

    def read_elevation_array(self) -> Tuple[np.ndarray, dict]:
        """
        Đọc mảng độ cao từ DEM.
        Returns:
            elevation: numpy array 2D độ cao (mét)
            transform: affine transform để chuyển pixel → tọa độ
        """
        self._check_rasterio()
        with rasterio.open(self.dem_path) as src:
            elevation = src.read(1).astype(np.float32)
            nodata    = src.nodata
            if nodata is not None:
                elevation[elevation == nodata] = np.nan
            return elevation, src.transform, src.crs

    def get_elevation_at_point(self, lng: float, lat: float) -> Optional[float]:
        """Lấy độ cao tại một điểm tọa độ"""
        self._check_rasterio()
        with rasterio.open(self.dem_path) as src:
            # Chuyển tọa độ địa lý → pixel
            row, col = src.index(lng, lat)
            if 0 <= row < src.height and 0 <= col < src.width:
                value = src.read(1)[row, col]
                return float(value) if value != src.nodata else None
            return None

    def compute_flood_mask(self, water_level_m: float) -> np.ndarray:
        """
        Tạo mask vùng ngập: pixel nào có độ cao < water_level_m → ngập.

        Args:
            water_level_m: Mực nước dâng (mét so với mặt biển)

        Returns:
            Boolean array: True = ngập, False = không ngập
        """
        elevation, transform, crs = self.read_elevation_array()
        flood_mask = elevation < water_level_m
        return flood_mask, transform, crs

