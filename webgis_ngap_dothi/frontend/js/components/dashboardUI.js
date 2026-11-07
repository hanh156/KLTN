/**
 * components/dashboardUI.js - Thống kê tổng quan cho Admin Dashboard
 * Dùng Chart.js để vẽ biểu đồ
 */

import ApiClient from "../api/apiClient.js";
import Notify    from "../utils/notify.js";
import Auth      from "../utils/auth.js";
import { formatArea } from "../utils/helpers.js";

export async function initDashboardUI() {
  if (!Auth.requireAdminAuth()) return;

  Notify.loading("Đang tải thống kê...");

  try {
    // Tải thống kê song song cho cả 3 kịch bản
    const [stat100, stat200, stat300] = await Promise.all([
      ApiClient.map.getStatistics(100),
      ApiClient.map.getStatistics(200),
      ApiClient.map.getStatistics(300),
    ]);

    Notify.dismissLoading();

    // Render số liệu tổng quan
    renderStatCards(stat100, stat200, stat300);

    // Vẽ biểu đồ mức độ ngập
    renderSeverityChart(stat100);

    // Vẽ biểu đồ so sánh kịch bản
    renderScenarioChart(stat100, stat200, stat300);

  } catch (err) {
    Notify.dismissLoading();
    Notify.error("Không tải được thống kê: " + err.message);
  }
}

function renderStatCards(s100, s200, s300) {
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl("stat-points-100",  s100.total_points);
  setEl("stat-points-200",  s200.total_points);
  setEl("stat-points-300",  s300.total_points);
  setEl("stat-high-100",    s100.severity_count?.high || 0);
  setEl("stat-high-200",    s200.severity_count?.high || 0);
  setEl("stat-high-300",    s300.severity_count?.high || 0);
}

function renderSeverityChart(stats) {
  const ctx = document.getElementById("severity-chart");
  if (!ctx || typeof Chart === "undefined") return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Nhẹ", "Trung bình", "Nặng"],
      datasets: [{
        data: [
          stats.severity_count?.low    || 0,
          stats.severity_count?.medium || 0,
          stats.severity_count?.high   || 0,
        ],
        backgroundColor: ["#ffd700", "#ff6b35", "#c0392b"],
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        title: { display: true, text: "Phân bố mức độ ngập (kịch bản 100mm)" },
      },
    },
  });
}

function renderScenarioChart(s100, s200, s300) {
  const ctx = document.getElementById("scenario-chart");
  if (!ctx || typeof Chart === "undefined") return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["100mm", "200mm", "300mm"],
      datasets: [
        {
          label: "Tổng điểm ngập",
          data: [s100.total_points, s200.total_points, s300.total_points],
          backgroundColor: ["#3498db", "#e67e22", "#e74c3c"],
        },
        {
          label: "Điểm ngập nặng",
          data: [
            s100.severity_count?.high || 0,
            s200.severity_count?.high || 0,
            s300.severity_count?.high || 0,
          ],
          backgroundColor: ["#85c1e9", "#f0a500", "#c0392b"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "So sánh theo kịch bản mưa" } },
      scales: { y: { beginAtZero: true, title: { display: true, text: "Số điểm" } } },
    },
  });
}

export default { initDashboardUI };

