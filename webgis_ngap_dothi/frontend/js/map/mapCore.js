/**
 * mapCore.js - Khởi tạo và quản lý Leaflet map instance
 * Là nơi duy nhất tạo map — các module khác nhận instance qua getMap()
 */

import { formatCoord } from "../utils/helpers.js";

let _map = null;

/**
 * Khởi tạo bản đồ Leaflet
 * @param {string} containerId - ID thẻ div chứa bản đồ
 * @param {Object} options     - Tùy chọn center, zoom
 * @returns {L.Map}
 */
export function initMap(containerId = "map", options = {}) {
  if (_map) return _map;

  const defaultCenter = options.center || [10.8231, 106.6297]; // TP.HCM
  const defaultZoom   = options.zoom   || 13;

  _map = L.map(containerId, {
    center:        defaultCenter,
    zoom:          defaultZoom,
    zoomControl:   true,
    attributionControl: true,
  });

  // --- Tile layer mặc định: OpenStreetMap ---
  const osmTile = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      maxZoom:     19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }
  ).addTo(_map);

  // --- Tile layer vệ tinh (tùy chọn) ---
  const satelliteTile = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { maxZoom: 19, attribution: "Esri World Imagery" }
  );

  // --- Layer Control ---
  L.control.layers(
    { "Bản đồ nền": osmTile, "Vệ tinh": satelliteTile },
    {},
    { position: "topright", collapsed: false }
  ).addTo(_map);

  // --- Scale bar ---
  L.control.scale({ imperial: false, metric: true }).addTo(_map);

  // --- Hiển thị tọa độ khi di chuột ---
  _map.on("mousemove", (e) => {
    const coordEl = document.getElementById("coord-display");
    if (coordEl) {
      coordEl.textContent =
        `${formatCoord(e.latlng.lat, "lat")} | ${formatCoord(e.latlng.lng, "lng")}`;
    }
  });

  console.log("[MapCore] Bản đồ đã khởi tạo thành công");
  return _map;
}

/**
 * Lấy map instance hiện tại
 * @returns {L.Map|null}
 */
export function getMap() {
  return _map;
}

/**
 * Di chuyển bản đồ đến tọa độ
 */
export function flyTo(lat, lng, zoom = 15) {
  if (_map) _map.flyTo([lat, lng], zoom);
}

/**
 * Fit bounds của bản đồ theo GeoJSON layer
 */
export function fitToLayer(layer) {
  if (_map && layer) {
    try {
      _map.fitBounds(layer.getBounds(), { padding: [30, 30] });
    } catch (e) {
      console.warn("[MapCore] Không thể fit bounds:", e.message);
    }
  }
}

export default { initMap, getMap, flyTo, fitToLayer };

