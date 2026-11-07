/**
 * components/mapViewer.js - Điều phối hiển thị bản đồ chính (User)
 * Khởi tạo map và tải tất cả lớp dữ liệu cần thiết
 */

import { initMap }       from "../map/mapCore.js";
import FloodOverlay      from "../map/floodOverlay.js";
import { initRoutingUI } from "./routingUI.js";
import Notify            from "../utils/notify.js";

let _currentScenario = 100;

export async function initMapViewer() {
  // 1. Khởi tạo bản đồ
  const map = initMap("map", { center: [10.8231, 106.6297], zoom: 13 });

  // 2. Tải lớp dữ liệu mặc định
  await loadAllLayers(_currentScenario);

  // 3. Khởi tạo tìm đường
  initRoutingUI();

  // 4. Event: chuyển đổi kịch bản ngập
  document.getElementById("scenario-select")?.addEventListener("change", async (e) => {
    _currentScenario = parseInt(e.target.value);
    await loadAllLayers(_currentScenario);
  });

  // 5. Toggle bật/tắt lớp ngập
  document.getElementById("toggle-flood-zones")?.addEventListener("change", async (e) => {
    if (e.target.checked) {
      await FloodOverlay.renderFloodZones(_currentScenario);
    } else {
      FloodOverlay.clearAllLayers();
    }
  });

  document.getElementById("toggle-flood-points")?.addEventListener("change", async (e) => {
    if (e.target.checked) await FloodOverlay.renderFloodPoints(_currentScenario);
  });

  document.getElementById("toggle-reports")?.addEventListener("change", async (e) => {
    if (e.target.checked) await FloodOverlay.renderReports("verified");
  });
}

async function loadAllLayers(scenarioMm) {
  Notify.loading(`Đang tải kịch bản ${scenarioMm}mm...`);
  await Promise.allSettled([
    FloodOverlay.renderFloodZones(scenarioMm),
    FloodOverlay.renderFloodPoints(scenarioMm),
    FloodOverlay.renderReports("verified"),
  ]);
  Notify.dismissLoading();
}

export default { initMapViewer };

