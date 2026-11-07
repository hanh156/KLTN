/**
 * layerControl.js - Bật/tắt các lớp GeoJSON, WMS, tile layer trên bản đồ
 */

import { getMap, fitToLayer } from "./mapCore.js";

const _layers = {};  // Lưu trữ tất cả layer theo tên

/**
 * Thêm lớp GeoJSON vào bản đồ và quản lý theo tên
 */
export function addGeoJsonLayer(name, geojsonData, styleOptions = {}, popupFn = null) {
  const map = getMap();
  if (!map) return;

  removeLayer(name);  // Xóa layer cũ cùng tên nếu có

  const defaultStyle = {
    color: "#2980b9", weight: 2, opacity: 0.8,
    fillColor: "#3498db", fillOpacity: 0.3,
    ...styleOptions,
  };

  const layer = L.geoJSON(geojsonData, {
    style: defaultStyle,
    onEachFeature: popupFn ? (feature, l) => l.bindPopup(popupFn(feature)) : undefined,
  }).addTo(map);

  _layers[name] = layer;
  return layer;
}

/**
 * Bật/tắt lớp theo tên
 */
export function toggleLayer(name) {
  const map = getMap();
  const layer = _layers[name];
  if (!map || !layer) return;

  if (map.hasLayer(layer)) {
    map.removeLayer(layer);
  } else {
    map.addLayer(layer);
  }
}

/**
 * Xóa lớp khỏi bản đồ
 */
export function removeLayer(name) {
  const map = getMap();
  if (_layers[name]) {
    if (map) map.removeLayer(_layers[name]);
    delete _layers[name];
  }
}

/**
 * Zoom đến extent của layer
 */
export function zoomToLayer(name) {
  const layer = _layers[name];
  if (layer) fitToLayer(layer);
}

/**
 * Lấy danh sách tên các layer đang hiển thị
 */
export function getActiveLayers() {
  const map = getMap();
  return Object.entries(_layers)
    .filter(([, layer]) => map && map.hasLayer(layer))
    .map(([name]) => name);
}

export default { addGeoJsonLayer, toggleLayer, removeLayer, zoomToLayer, getActiveLayers };

