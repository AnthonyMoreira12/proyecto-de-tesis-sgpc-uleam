import axios from "axios";
import {
  clearAuthStorage,
  getAccessToken,
  getRefreshToken,
  isAccessTokenExpired,
  isRefreshTokenExpired,
  setAccessToken,
  setRefreshToken,
} from "../utils/authStorage";

/**
 * BaseURL robusto:
 * - VITE_API_URL = http://localhost:8000      -> http://localhost:8000/api
 * - VITE_API_URL = http://localhost:8000/api  -> http://localhost:8000/api
 * - Evita duplicados /api/api y elimina "/" final
 */
function buildBaseURL() {
  const raw = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const clean = String(raw).replace(/\/+$/, "");
  return clean.endsWith("/api") ? clean : `${clean}/api`;
}

const api = axios.create({
  baseURL: buildBaseURL(),
  withCredentials: true, 
});

const AUTH_ROUTES = [
  "auth/login/",
  "auth/register/",
  "auth/microsoft/login/",
  "auth/microsoft/callback/",
  "auth/microsoft/exchange/",
  "auth/password-reset/request/",
  "auth/password-reset/confirm/",
];

const REFRESH_ROUTE = "auth/refresh/";

function getRequestUrl(configOrUrl) {
  const raw =
    typeof configOrUrl === "string" ? configOrUrl : configOrUrl?.url || "";

  return String(raw)
    .replace(/^https?:\/\/[^/]+/i, "")
    .replace(/^\/+/, "");
}

function isAuthRoute(url) {
  const normalized = getRequestUrl(url);
  return AUTH_ROUTES.some((route) => normalized.includes(route));
}

function isRefreshRoute(url) {
  const normalized = getRequestUrl(url);
  return normalized.includes(REFRESH_ROUTE);
}

function ensurePlainHeaders(config) {
  config.headers = { ...(config.headers || {}) };
  return config;
}

function normalizeContentType(config) {
  config.headers = config.headers || {};

  const method = String(config.method || "get").toLowerCase();
  const methodsWithBody = ["post", "put", "patch"];
  const hasBodyMethod = methodsWithBody.includes(method);

  const isFormData =
    typeof FormData !== "undefined" && config.data instanceof FormData;

  const removeContentType = (obj) => {
    if (!obj) return;
    delete obj["Content-Type"];
    delete obj["content-type"];
  };

  if (isFormData) {
    removeContentType(config.headers);
    removeContentType(config.headers?.common);
    return config;
  }

  if (
    hasBodyMethod &&
    !config.headers["Content-Type"] &&
    !config.headers["content-type"]
  ) {
    config.headers["Content-Type"] = "application/json";
  }

  return config;
}

async function forceLogout() {
  clearAuthStorage();

  try {
    const mod = await import("../../router/index.js");
    const router = mod?.default;

    if (router) {
      await router.replace("/login");
      return;
    }
  } catch {
    // fallback abajo
  }

  window.location.href = "/login";
}

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach((item) => {
    if (token) item.resolve(token);
    else item.reject(error);
  });

  failedQueue = [];
}

async function refreshAccessToken() {
  const refresh = getRefreshToken();

  if (!refresh || isRefreshTokenExpired(30_000)) {
    throw new Error("La sesión ha vencido.");
  }

  const { data } = await api.post(
    REFRESH_ROUTE,
    { refresh },
    { withCredentials: false }
  );

  const newAccess = data?.access;
  const newRefresh = data?.refresh;

  if (!newAccess) {
    throw new Error("No llegó access en refresh.");
  }

  setAccessToken(newAccess);

  if (newRefresh) {
    setRefreshToken(newRefresh);
  }

  return newAccess;
}

api.interceptors.request.use(
  async (config) => {
    ensurePlainHeaders(config);

    config.withCredentials = false;

    if (isAuthRoute(config) || isRefreshRoute(config)) {
      return normalizeContentType(config);
    }

    const access = getAccessToken();
    const refresh = getRefreshToken();

    if (!access || !refresh) {
      return normalizeContentType(config);
    }

    if (isRefreshTokenExpired(30_000)) {
      await forceLogout();
      return Promise.reject(new Error("La sesión ha vencido."));
    }

    if (isAccessTokenExpired(30_000)) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          ensurePlainHeaders(config);
          config.withCredentials = false;
          config.headers.Authorization = `Bearer ${newToken}`;
          return normalizeContentType(config);
        });
      }

      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();

        isRefreshing = false;
        processQueue(null, newToken);

        config.headers.Authorization = `Bearer ${newToken}`;
        return normalizeContentType(config);
      } catch (error) {
        isRefreshing = false;
        processQueue(error, null);
        await forceLogout();
        return Promise.reject(error);
      }
    }

    if (!config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${access}`;
    }

    return normalizeContentType(config);
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    if (axios.isCancel?.(error) || error?.code === "ERR_CANCELED") {
      return Promise.reject(error);
    }

    if (!error?.response) {
      return Promise.reject(error);
    }

    const status = Number(error.response.status);

    const invalidToken =
      error.response?.data?.code === "token_not_valid" ||
      (typeof error.response?.data?.detail === "string" &&
        error.response.data.detail.toLowerCase().includes("token"));

    if (isAuthRoute(originalRequest)) {
      return Promise.reject(error);
    }

    if (isRefreshRoute(originalRequest)) {
      await forceLogout();
      return Promise.reject(error);
    }

    if ((status === 401 || invalidToken) && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh = getRefreshToken();

      if (!refresh || isRefreshTokenExpired(30_000)) {
        await forceLogout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          ensurePlainHeaders(originalRequest);
          originalRequest.withCredentials = false;
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          normalizeContentType(originalRequest);
          return api(originalRequest);
        });
      }

      isRefreshing = true;

      try {
        const newAccess = await refreshAccessToken();

        isRefreshing = false;
        processQueue(null, newAccess);

        ensurePlainHeaders(originalRequest);
        originalRequest.withCredentials = false;
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        normalizeContentType(originalRequest);

        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        processQueue(refreshError, null);
        await forceLogout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;