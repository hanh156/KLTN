/**
 * utils/notify.js - Hệ thống thông báo toast toàn hệ thống
 * Dùng: Notify.success("Thành công!") | Notify.error("Lỗi!")
 */

const CONTAINER_ID = "notify-container";
const DURATION_MS  = 3500;

function getContainer() {
  let el = document.getElementById(CONTAINER_ID);
  if (!el) {
    el = document.createElement("div");
    el.id = CONTAINER_ID;
    el.style.cssText = `
      position: fixed; top: 20px; right: 20px; z-index: 99999;
      display: flex; flex-direction: column; gap: 8px;
      max-width: 360px;
    `;
    document.body.appendChild(el);
  }
  return el;
}

function show(message, type = "info", duration = DURATION_MS) {
  const colors = {
    success: { bg: "#27ae60", icon: "✅" },
    error:   { bg: "#e74c3c", icon: "❌" },
    warning: { bg: "#f39c12", icon: "⚠️" },
    info:    { bg: "#2980b9", icon: "ℹ️" },
    loading: { bg: "#7f8c8d", icon: "⏳" },
  };

  const { bg, icon } = colors[type] || colors.info;
  const container = getContainer();

  const toast = document.createElement("div");
  toast.style.cssText = `
    background: ${bg}; color: white; padding: 12px 16px;
    border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    display: flex; align-items: center; gap: 8px;
    font-size: 14px; font-family: sans-serif;
    animation: slideIn 0.3s ease;
    cursor: pointer;
  `;
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  toast.onclick = () => toast.remove();

  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  return toast;  // Trả về để có thể dismiss thủ công (dùng cho loading)
}

// Thêm CSS animation
const style = document.createElement("style");
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to   { transform: translateX(0);   opacity: 1; }
  }
`;
document.head?.appendChild(style);

let _loadingToast = null;

const Notify = {
  success: (msg, duration) => show(msg, "success", duration),
  error:   (msg, duration) => show(msg, "error", duration),
  warning: (msg, duration) => show(msg, "warning", duration),
  info:    (msg, duration) => show(msg, "info", duration),

  loading: (msg = "Đang tải...") => {
    if (_loadingToast) _loadingToast.remove();
    _loadingToast = show(msg, "loading", 0);  // Không tự đóng
    return _loadingToast;
  },

  dismissLoading: () => {
    if (_loadingToast) {
      _loadingToast.remove();
      _loadingToast = null;
    }
  },

  confirm: (message) => window.confirm(message),
};

export default Notify;

