/**
 * components/verifyUI.js - Admin duyệt / từ chối báo cáo ngập
 */

import ApiClient from "../api/apiClient.js";
import Notify    from "../utils/notify.js";
import Auth      from "../utils/auth.js";
import { formatDateTime, getStatusBadgeClass, getStatusLabel } from "../utils/helpers.js";

let _currentPage   = 1;
const LIMIT        = 20;

export async function initVerifyUI() {
  if (!Auth.requireAdminAuth()) return;

  // Filter theo trạng thái
  document.getElementById("status-filter")?.addEventListener("change", () => {
    _currentPage = 1;
    loadReports();
  });

  document.getElementById("btn-prev")?.addEventListener("click", () => {
    if (_currentPage > 1) { _currentPage--; loadReports(); }
  });

  document.getElementById("btn-next")?.addEventListener("click", () => {
    _currentPage++;
    loadReports();
  });

  await loadReports();
}

async function loadReports() {
  const status   = document.getElementById("status-filter")?.value || "";
  const tbody    = document.getElementById("reports-tbody");
  const pageInfo = document.getElementById("page-info");

  if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center">Đang tải...</td></tr>`;

  try {
    const data = await ApiClient.reports.getAll(status || null, _currentPage, LIMIT);

    if (!data.reports?.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Không có báo cáo nào</td></tr>`;
      return;
    }

    tbody.innerHTML = data.reports.map(r => `
      <tr>
        <td>${r.id}</td>
        <td>${r.longitude?.toFixed(5)}, ${r.latitude?.toFixed(5)}</td>
        <td>${r.description || "—"}</td>
        <td><span class="badge ${getStatusBadgeClass(r.status)}">${getStatusLabel(r.status)}</span></td>
        <td>${formatDateTime(r.created_at)}</td>
        <td>
          ${r.status === "pending" ? `
            <button class="btn btn-sm btn-success me-1"
              onclick="approveReport(${r.id})">✅ Duyệt</button>
            <button class="btn btn-sm btn-danger"
              onclick="rejectReport(${r.id})">❌ Từ chối</button>
          ` : "—"}
        </td>
      </tr>
    `).join("");

    if (pageInfo) pageInfo.textContent = `Trang ${_currentPage} / Tổng ${data.total} báo cáo`;

  } catch (err) {
    Notify.error("Không tải được báo cáo: " + err.message);
  }
}

// Hàm global cho onclick trong HTML
window.approveReport = async (id) => {
  if (!Notify.confirm("Xác nhận duyệt báo cáo này?")) return;
  try {
    await ApiClient.reports.review(id, "verified", "Đã xác minh tại thực địa");
    Notify.success("Đã duyệt báo cáo");
    loadReports();
  } catch (err) { Notify.error(err.message); }
};

window.rejectReport = async (id) => {
  const note = prompt("Lý do từ chối:");
  if (note === null) return;
  try {
    await ApiClient.reports.review(id, "rejected", note);
    Notify.success("Đã từ chối báo cáo");
    loadReports();
  } catch (err) { Notify.error(err.message); }
};

export default { initVerifyUI };

