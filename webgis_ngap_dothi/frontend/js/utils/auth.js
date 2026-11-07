/**
 * utils/auth.js - Quản lý JWT token, kiểm tra role, redirect
 */

const TOKEN_KEY   = "access_token";
const USER_KEY    = "current_user";

// ------------------------------------------------------------------ //
//  Lưu / đọc / xóa token
// ------------------------------------------------------------------ //
export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// ------------------------------------------------------------------ //
//  Lưu / đọc thông tin user
// ------------------------------------------------------------------ //
export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY));
  } catch {
    return null;
  }
}

// ------------------------------------------------------------------ //
//  Kiểm tra đăng nhập
// ------------------------------------------------------------------ //
export function isLoggedIn() {
  return !!getToken();
}

export function isAdmin() {
  const user = getUser();
  return user?.role === "admin";
}

// ------------------------------------------------------------------ //
//  Redirect guards
// ------------------------------------------------------------------ //
export function requireAuth(redirectTo = "/frontend/pages/user/login_user.html") {
  if (!isLoggedIn()) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

export function requireAdminAuth(redirectTo = "/frontend/pages/admin/login_admin.html") {
  if (!isLoggedIn() || !isAdmin()) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

// ------------------------------------------------------------------ //
//  Đăng xuất
// ------------------------------------------------------------------ //
export function logout(redirectTo = "/frontend/pages/user/login_user.html") {
  removeToken();
  window.location.href = redirectTo;
}

// ------------------------------------------------------------------ //
//  Xử lý sau đăng nhập thành công
// ------------------------------------------------------------------ //
export function handleLoginSuccess(tokenResponse) {
  saveToken(tokenResponse.access_token);
  saveUser(tokenResponse.user);

  // Redirect theo role
  if (tokenResponse.user.role === "admin") {
    window.location.href = "/frontend/pages/admin/dashboard.html";
  } else {
    window.location.href = "/frontend/pages/user/index_map.html";
  }
}

export default {
  saveToken, getToken, removeToken,
  saveUser, getUser,
  isLoggedIn, isAdmin,
  requireAuth, requireAdminAuth,
  logout, handleLoginSuccess,
};

