/**
 * components/reportFormUI.js - Gửi báo cáo điểm ngập có tọa độ GPS
 */

import { getMap }      from "../map/mapCore.js";
import ApiClient        from "../api/apiClient.js";
import Notify           from "../utils/notify.js";
import Auth             from "../utils/auth.js";

let _tempMarker = null;

export function initReportFormUI() {
  if (!Auth.requireAuth()) return;

  const map = getMap();

  // Chọn tọa độ bằng cách nhấn bản đồ
  if (map) {
    map.on("click", (e) => {
      const { lat, lng } = e.latlng;
      setReportLocation(lat, lng);
    });
  }

  // Nút lấy GPS hiện tại
  document.getElementById("btn-get-gps")?.addEventListener("click", getCurrentLocation);

  // Submit form
  document.getElementById("report-form")?.addEventListener("submit", submitReport);
}

function setReportLocation(lat, lng) {
  const map = getMap();

  if (_tempMarker) map?.removeLayer(_tempMarker);

  if (map) {
    _tempMarker = L.marker([lat, lng], {
      icon: L.icon({
        iconUrl:    "/frontend/assets/markers/marker_flood.png",
        iconSize:   [28, 28],
        iconAnchor: [14, 28],
      }),
    }).addTo(map).bindPopup("📍 Vị trí báo cáo").openPopup();
  }

  // Điền tọa độ vào form
  const lngInput = document.getElementById("report-lng");
  const latInput = document.getElementById("report-lat");
  const dispEl   = document.getElementById("selected-location");

  if (lngInput) lngInput.value = lng.toFixed(6);
  if (latInput) latInput.value = lat.toFixed(6);
  if (dispEl)   dispEl.textContent = `${lat.toFixed(5)}°N, ${lng.toFixed(5)}°E`;
}

function getCurrentLocation() {
  if (!navigator.geolocation) {
    Notify.warning("Trình duyệt không hỗ trợ GPS");
    return;
  }
  Notify.loading("Đang lấy vị trí...");
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      Notify.dismissLoading();
      setReportLocation(pos.coords.latitude, pos.coords.longitude);
      getMap()?.flyTo([pos.coords.latitude, pos.coords.longitude], 16);
    },
    (err) => {
      Notify.dismissLoading();
      Notify.error("Không lấy được GPS: " + err.message);
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

async function submitReport(e) {
  e.preventDefault();

  const lng  = parseFloat(document.getElementById("report-lng")?.value);
  const lat  = parseFloat(document.getElementById("report-lat")?.value);
  const desc = document.getElementById("report-desc")?.value?.trim();

  if (!lng || !lat) {
    Notify.warning("Vui lòng chọn vị trí trên bản đồ hoặc dùng GPS");
    return;
  }

  Notify.loading("Đang gửi báo cáo...");

  try {
    await ApiClient.reports.submit(lng, lat, desc, null);
    Notify.dismissLoading();
    Notify.success("Báo cáo đã được gửi! Chờ Admin xác minh.");

    // Reset form
    e.target.reset();
    if (_tempMarker) { getMap()?.removeLayer(_tempMarker); _tempMarker = null; }
    const dispEl = document.getElementById("selected-location");
    if (dispEl) dispEl.textContent = "Chưa chọn vị trí";

  } catch (err) {
    Notify.dismissLoading();
    Notify.error("Gửi báo cáo thất bại: " + err.message);
  }
}

export default { initReportFormUI };

