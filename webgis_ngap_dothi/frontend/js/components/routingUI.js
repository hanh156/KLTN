/**
 * components/routingUI.js - Chọn điểm đầu/cuối và vẽ tuyến đường tránh ngập
 */

import { getMap, flyTo }    from "../map/mapCore.js";
import ApiClient             from "../api/apiClient.js";
import Notify                from "../utils/notify.js";
import { formatDistance, formatDuration } from "../utils/helpers.js";

let _startMarker = null;
let _endMarker   = null;
let _routeLine   = null;
let _selectMode  = null;   // "start" | "end"

// Icon điểm đầu / cuối
const startIcon = L.icon({
  iconUrl:    "/frontend/assets/markers/marker_start.png",
  iconSize:   [32, 32], iconAnchor: [16, 32],
});
const endIcon = L.icon({
  iconUrl:    "/frontend/assets/markers/marker_end.png",
  iconSize:   [32, 32], iconAnchor: [16, 32],
});

// ------------------------------------------------------------------ //
//  Khởi tạo — gắn event listener cho nút chọn điểm
// ------------------------------------------------------------------ //
export function initRoutingUI() {
  const map = getMap();
  if (!map) return;

  document.getElementById("btn-select-start")?.addEventListener("click", () => {
    _selectMode = "start";
    Notify.info("Nhấn vào bản đồ để chọn điểm xuất phát");
    map.getContainer().style.cursor = "crosshair";
  });

  document.getElementById("btn-select-end")?.addEventListener("click", () => {
    _selectMode = "end";
    Notify.info("Nhấn vào bản đồ để chọn điểm đích");
    map.getContainer().style.cursor = "crosshair";
  });

  document.getElementById("btn-find-route")?.addEventListener("click", findRoute);
  document.getElementById("btn-clear-route")?.addEventListener("click", clearRoute);

  map.on("click", onMapClick);
}

function onMapClick(e) {
  if (!_selectMode) return;
  const { lat, lng } = e.latlng;

  if (_selectMode === "start") {
    setStartPoint(lat, lng);
  } else {
    setEndPoint(lat, lng);
  }

  _selectMode = null;
  getMap().getContainer().style.cursor = "";
}

function setStartPoint(lat, lng) {
  const map = getMap();
  if (_startMarker) map.removeLayer(_startMarker);
  _startMarker = L.marker([lat, lng], { icon: startIcon, draggable: true })
    .addTo(map)
    .bindPopup(`<b>📍 Điểm xuất phát</b><br>${lat.toFixed(5)}, ${lng.toFixed(5)}`);

  _startMarker.on("dragend", (e) => {
    const pos = e.target.getLatLng();
    updateCoordDisplay("start", pos.lat, pos.lng);
  });

  updateCoordDisplay("start", lat, lng);
}

function setEndPoint(lat, lng) {
  const map = getMap();
  if (_endMarker) map.removeLayer(_endMarker);
  _endMarker = L.marker([lat, lng], { icon: endIcon, draggable: true })
    .addTo(map)
    .bindPopup(`<b>🏁 Điểm đích</b><br>${lat.toFixed(5)}, ${lng.toFixed(5)}`);

  _endMarker.on("dragend", (e) => {
    const pos = e.target.getLatLng();
    updateCoordDisplay("end", pos.lat, pos.lng);
  });

  updateCoordDisplay("end", lat, lng);
}

function updateCoordDisplay(type, lat, lng) {
  const el = document.getElementById(`${type}-coord`);
  if (el) el.textContent = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
}

// ------------------------------------------------------------------ //
//  Tìm đường
// ------------------------------------------------------------------ //
async function findRoute() {
  if (!_startMarker || !_endMarker) {
    Notify.warning("Vui lòng chọn cả điểm xuất phát và điểm đích");
    return;
  }

  const start    = _startMarker.getLatLng();
  const end      = _endMarker.getLatLng();
  const scenario = document.getElementById("scenario-select")?.value || 100;
  const maxDepth = parseFloat(document.getElementById("max-depth")?.value || 0.3);

  Notify.loading("Đang tìm đường tránh ngập...");

  try {
    const result = await ApiClient.routing.findPath(
      start.lng, start.lat, end.lng, end.lat,
      { avoidFlood: true, scenarioMm: parseInt(scenario), maxDepthM: maxDepth }
    );

    Notify.dismissLoading();

    if (!result.found) {
      Notify.error("Không tìm được tuyến đường — toàn bộ đường có thể bị ngập");
      return;
    }

    drawRoute(result);
    showRouteInfo(result);
    Notify.success("Đã tìm được tuyến đường!");

  } catch (err) {
    Notify.dismissLoading();
    Notify.error("Lỗi tìm đường: " + err.message);
  }
}

function drawRoute(result) {
  const map = getMap();
  if (_routeLine) map.removeLayer(_routeLine);

  const coords = result.geojson?.coordinates?.map(([lng, lat]) => [lat, lng]) || [];
  if (!coords.length) return;

  _routeLine = L.polyline(coords, {
    color:  result.flood_avoided ? "#e67e22" : "#2980b9",
    weight: 5,
    opacity: 0.85,
    dashArray: result.flood_avoided ? "10, 5" : null,
  }).addTo(map);

  map.fitBounds(_routeLine.getBounds(), { padding: [40, 40] });
}

function showRouteInfo(result) {
  const panel = document.getElementById("route-result-panel");
  if (!panel) return;
  panel.style.display = "block";
  panel.innerHTML = `
    <h4>🗺️ Kết quả tuyến đường</h4>
    <p>📏 Khoảng cách: <b>${formatDistance(result.total_distance_m)}</b></p>
    <p>⏱️ Thời gian ước tính: <b>${formatDuration(result.total_time_min)}</b></p>
    <p>🌊 Tránh ngập: <b>${result.flood_avoided ? "Có" : "Không"}</b></p>
    ${result.warnings.length ? `<p>⚠️ ${result.warnings.join("<br>")}</p>` : ""}
  `;
}

function clearRoute() {
  const map = getMap();
  if (_routeLine)   { map.removeLayer(_routeLine);   _routeLine   = null; }
  if (_startMarker) { map.removeLayer(_startMarker); _startMarker = null; }
  if (_endMarker)   { map.removeLayer(_endMarker);   _endMarker   = null; }

  const panel = document.getElementById("route-result-panel");
  if (panel) panel.style.display = "none";

  ["start-coord", "end-coord"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = "Chưa chọn";
  });
}

export default { initRoutingUI };

