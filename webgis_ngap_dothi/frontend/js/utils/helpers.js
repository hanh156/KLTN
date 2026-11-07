/**
 * utils/helpers.js - Các hàm tiện ích dùng chung toàn hệ thống
 */

// ------------------------------------------------------------------ //
//  Format tọa độ
// ------------------------------------------------------------------ //
export function formatCoord(value, type = "lng") {
  const dir = type === "lat"
    ? (value >= 0 ? "N" : "S")
    : (value >= 0 ? "E" : "W");
  return `${Math.abs(value).toFixed(5)}°${dir}`;
}

// ------------------------------------------------------------------ //
//  Format ngày giờ tiếng Việt
// ------------------------------------------------------------------ //
export function formatDate(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleDateString("vi-VN", {
    day: "2-digit", month: "2-digit", year: "numeric",
  });
}

export function formatDateTime(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleString("vi-VN", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

// ------------------------------------------------------------------ //
//  Format số
// ------------------------------------------------------------------ //
export function formatDistance(meters) {
  if (meters < 1000) return `${Math.round(meters)} m`;
  return `${(meters / 1000).toFixed(1)} km`;
}

export function formatArea(sqm) {
  if (sqm < 10000) return `${Math.round(sqm).toLocaleString("vi-VN")} m²`;
  return `${(sqm / 10000).toFixed(2)} ha`;
}

export function formatDuration(minutes) {
  if (minutes < 60) return `${Math.round(minutes)} phút`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return `${h} giờ ${m > 0 ? m + " phút" : ""}`.trim();
}

// ------------------------------------------------------------------ //
//  Màu sắc theo mức độ ngập
// ------------------------------------------------------------------ //
export function getSeverityLabel(severity) {
  const map = { low: "Nhẹ", medium: "Trung bình", high: "Nặng" };
  return map[severity] || severity;
}

export function getSeverityColor(severity) {
  const map = { low: "#ffd700", medium: "#ff6b35", high: "#c0392b" };
  return map[severity] || "#999";
}

// ------------------------------------------------------------------ //
//  Nhãn trạng thái báo cáo
// ------------------------------------------------------------------ //
export function getStatusLabel(status) {
  const map = { pending: "Chờ duyệt", verified: "Đã xác minh", rejected: "Từ chối" };
  return map[status] || status;
}

export function getStatusBadgeClass(status) {
  const map = { pending: "badge-warning", verified: "badge-success", rejected: "badge-danger" };
  return map[status] || "badge-secondary";
}

// ------------------------------------------------------------------ //
//  Tiện ích DOM
// ------------------------------------------------------------------ //
export function $(selector, parent = document) {
  return parent.querySelector(selector);
}

export function $$(selector, parent = document) {
  return [...parent.querySelectorAll(selector)];
}

export function showElement(el)  { if (el) el.style.display = ""; }
export function hideElement(el)  { if (el) el.style.display = "none"; }
export function toggleElement(el) {
  if (el) el.style.display = el.style.display === "none" ? "" : "none";
}

// ------------------------------------------------------------------ //
//  Debounce (tránh gọi hàm quá nhiều lần)
// ------------------------------------------------------------------ //
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

