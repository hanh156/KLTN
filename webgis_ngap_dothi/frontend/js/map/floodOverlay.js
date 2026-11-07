/**
 * floodOverlay.js - Render vùng ngập và điểm ngập lên bản đồ Leaflet
 */

import { getMap }  from "./mapCore.js";
import ApiClient   from "../api/apiClient.js";
import Notify      from "../utils/notify.js";

// Màu sắc theo mức độ ngập
const FLOOD_COLORS = {
  low:    { fill: "#ffd700", border: "#cc9900" },   // Vàng
  medium: { fill: "#ff6b35", border: "#cc4400" },   // Cam
  high:   { fill: "#c0392b", border: "#8e1a12" },   // Đỏ
};

// Lưu tham chiếu các layer để có thể xóa/cập nhật
let _floodZoneLayer  = null;
let _floodPointLayer = null;
let _reportLayer     = null;

// ------------------------------------------------------------------ //
//  Vùng ngập (Polygon) theo kịch bản
// ------------------------------------------------------------------ //
export async function renderFloodZones(scenarioMm) {
  const map = getMap();
  if (!map) return;

  // Xóa layer cũ
  if (_floodZoneLayer) { map.removeLayer(_floodZoneLayer); _floodZoneLayer = null; }

  try {
    Notify.loading("Đang tải dữ liệu vùng ngập...");
    const geojson = await ApiClient.map.getFloodLayer(scenarioMm);

    _floodZoneLayer = L.geoJSON(geojson, {
      style: (feature) => ({
        color:       "#c0392b",
        weight:      1,
        opacity:     0.8,
        fillColor:   "#e74c3c",
        fillOpacity: 0.4,
      }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <b>🌊 Vùng ngập</b><br>
          Kịch bản: ${p.scenario_mm ?? scenarioMm} mm mưa<br>
          Độ sâu TB: ${p.avg_depth_m ? p.avg_depth_m.toFixed(2) + " m" : "N/A"}
        `);
      },
    }).addTo(map);

    Notify.success(`Đã tải vùng ngập kịch bản ${scenarioMm}mm`);
  } catch (err) {
    Notify.error("Không tải được lớp ngập: " + err.message);
  }
}

// ------------------------------------------------------------------ //
//  Điểm ngập (Marker)
// ------------------------------------------------------------------ //
const floodIcon = (severity) => L.divIcon({
  className: "",
  html: `<div class="flood-marker severity-${severity}">💧</div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

export async function renderFloodPoints(scenarioMm = null) {
  const map = getMap();
  if (!map) return;

  if (_floodPointLayer) { map.removeLayer(_floodPointLayer); _floodPointLayer = null; }

  try {
    const geojson = await ApiClient.map.getFloodPoints(scenarioMm);

    _floodPointLayer = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) =>
        L.marker(latlng, { icon: floodIcon(feature.properties.severity) }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <b>📍 Điểm ngập</b><br>
          Độ sâu: ${p.depth_m} m<br>
          Mức độ: ${p.severity}<br>
          Nguồn: ${p.source}<br>
          <small>${new Date(p.recorded_at).toLocaleString("vi-VN")}</small>
        `);
      },
    }).addTo(map);
  } catch (err) {
    console.warn("[FloodOverlay] Không tải được điểm ngập:", err.message);
  }
}

// ------------------------------------------------------------------ //
//  Báo cáo người dùng (Marker)
// ------------------------------------------------------------------ //
export async function renderReports(status = "verified") {
  const map = getMap();
  if (!map) return;

  if (_reportLayer) { map.removeLayer(_reportLayer); _reportLayer = null; }

  try {
    const geojson = await ApiClient.reports.getGeoJson(status);

    _reportLayer = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) =>
        L.marker(latlng, {
          icon: L.icon({
            iconUrl:    "/frontend/assets/markers/marker_verified.png",
            iconSize:   [28, 28],
            iconAnchor: [14, 28],
          }),
        }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <b>🚩 Báo cáo ngập</b><br>
          ${p.description || "Không có mô tả"}<br>
          Trạng thái: <b>${p.status}</b><br>
          <small>${new Date(p.created_at).toLocaleString("vi-VN")}</small>
        `);
      },
    }).addTo(map);
  } catch (err) {
    console.warn("[FloodOverlay] Không tải được báo cáo:", err.message);
  }
}

export function clearAllLayers() {
  const map = getMap();
  if (!map) return;
  [_floodZoneLayer, _floodPointLayer, _reportLayer].forEach(l => {
    if (l) map.removeLayer(l);
  });
  _floodZoneLayer = _floodPointLayer = _reportLayer = null;
}

export default { renderFloodZones, renderFloodPoints, renderReports, clearAllLayers };

