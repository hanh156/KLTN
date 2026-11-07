/**
 * apiClient.js
 * NƠI DUY NHẤT định nghĩa URL endpoint gọi về backend.
 * Mọi file JS khác chỉ được gọi API thông qua object này.
 */

const API_BASE_URL = "http://localhost:8000/api";

const ApiClient = {

  // ---------------------------------------------------------------- //
  //  Tiện ích gọi fetch có xử lý lỗi & token tự động
  // ---------------------------------------------------------------- //
  async _request(method, endpoint, body = null, requireAuth = false) {
    const headers = { "Content-Type": "application/json" };

    if (requireAuth) {
      const token = localStorage.getItem("access_token");
      if (!token) {
        window.location.href = "/frontend/pages/user/login_user.html";
        return;
      }
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/frontend/pages/user/login_user.html";
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (err) {
      console.error(`[ApiClient] ${method} ${endpoint} failed:`, err.message);
      throw err;
    }
  },

  // ================================================================ //
  //  AUTH
  // ================================================================ //
  auth: {
    login: (username, password) => {
      const form = new URLSearchParams({ username, password });
      return fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        body: form,
      }).then(r => r.json());
    },
    register: (data) => ApiClient._request("POST", "/auth/register", data),
    getMe:    ()     => ApiClient._request("GET",  "/auth/me", null, true),
  },

  // ================================================================ //
  //  MAP & FLOOD LAYERS
  // ================================================================ //
  map: {
    getFloodLayer:  (scenario) =>
      ApiClient._request("GET", `/map/flood-layer${scenario ? `?scenario=${scenario}` : ""}`),
    getFloodPoints: (scenario) =>
      ApiClient._request("GET", `/map/flood-points${scenario ? `?scenario=${scenario}` : ""}`),
    runScenario:    (mm)       =>
      ApiClient._request("GET", `/map/scenarios/${mm}`),
    getStatistics:  (scenario) =>
      ApiClient._request("GET", `/map/statistics?scenario=${scenario || 100}`),
    getDemInfo:     ()         =>
      ApiClient._request("GET", "/map/dem-info"),
    getElevation:   (lng, lat) =>
      ApiClient._request("GET", `/map/elevation?lng=${lng}&lat=${lat}`),
  },

  // ================================================================ //
  //  ROUTING (Tìm đường tránh ngập)
  // ================================================================ //
  routing: {
    findPath: (startLng, startLat, endLng, endLat, options = {}) =>
      ApiClient._request("POST", "/routing/find-path", {
        start: { longitude: startLng, latitude: startLat },
        end:   { longitude: endLng,   latitude: endLat   },
        avoid_flood:  options.avoidFlood  ?? true,
        scenario_mm:  options.scenarioMm  ?? 100,
        max_depth_m:  options.maxDepthM   ?? 0.3,
      }),
    getGraphInfo: () => ApiClient._request("GET", "/routing/graph-info"),
  },

  // ================================================================ //
  //  REPORTS (Báo cáo ngập)
  // ================================================================ //
  reports: {
    submit: (lng, lat, description, imageUrl) =>
      ApiClient._request("POST", "/reports/", {
        longitude: lng, latitude: lat, description, image_url: imageUrl,
      }, true),

    getAll: (status, page = 1, limit = 20) =>
      ApiClient._request(
        "GET",
        `/reports/?page=${page}&limit=${limit}${status ? `&status=${status}` : ""}`,
        null, true
      ),

    getMy: () => ApiClient._request("GET", "/reports/my", null, true),

    getGeoJson: (status) =>
      ApiClient._request("GET", `/reports/geojson${status ? `?status=${status}` : ""}`),

    review: (id, status, reviewNote) =>
      ApiClient._request("PATCH", `/reports/${id}/review`,
        { status, review_note: reviewNote }, true
      ),
  },
};

export default ApiClient;

