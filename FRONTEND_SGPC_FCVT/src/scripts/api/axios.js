import axios from "axios";

import {
  clearAuthStorage,
  getAccessToken,
  isAccessTokenExpired,
  setAccessToken,
  setRefreshToken,
} from "../utils/authStorage";

/**
 * BaseURL robusto:
 *
 * VITE_API_URL = http://localhost:8000
 * Resultado      http://localhost:8000/api
 *
 * VITE_API_URL = http://localhost:8000/api
 * Resultado      http://localhost:8000/api
 */
function buildBaseURL() {
  const raw =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const clean = String(raw)
    .trim()
    .replace(/\/+$/, "");

  return clean.endsWith("/api")
    ? clean
    : `${clean}/api`;
}

const baseURL = buildBaseURL();

/**
 * Cliente principal.
 *
 * withCredentials debe permanecer activo porque el refresh
 * token se administra mediante una cookie HttpOnly.
 */
const api = axios.create({
  baseURL,
  withCredentials: true,
});

/**
 * Cliente independiente para la renovación.
 *
 * No utiliza los interceptores del cliente principal, por lo
 * que evita recursión y bucles sobre /auth/refresh/.
 */
const refreshClient = axios.create({
  baseURL,
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

const REFRESH_ROUTE =
  "auth/refresh/";

const PUBLIC_FRONTEND_PATHS =
  new Set([
    "/login",
    "/recuperar-contrasena",
    "/restablecer-contrasena",
    "/reset-password",
  ]);

function getRequestUrl(configOrUrl) {
  const raw =
    typeof configOrUrl === "string"
      ? configOrUrl
      : configOrUrl?.url || "";

  return String(raw)
    .replace(
      /^https?:\/\/[^/]+/i,
      ""
    )
    .replace(/^\/+/, "");
}

function isAuthRoute(configOrUrl) {
  const normalized =
    getRequestUrl(configOrUrl);

  return AUTH_ROUTES.some(
    (route) =>
      normalized.includes(route)
  );
}

function isRefreshRoute(
  configOrUrl
) {
  const normalized =
    getRequestUrl(configOrUrl);

  return normalized.includes(
    REFRESH_ROUTE
  );
}

function ensureHeaders(config) {
  if (!config.headers) {
    config.headers = {};
  }

  return config.headers;
}

function hasHeader(headers, name) {
  if (!headers) {
    return false;
  }

  if (
    typeof headers.has ===
    "function"
  ) {
    return headers.has(name);
  }

  const normalizedName =
    String(name).toLowerCase();

  return Object.keys(headers).some(
    (key) =>
      String(key).toLowerCase() ===
      normalizedName
  );
}

function setHeader(
  headers,
  name,
  value
) {
  if (!headers) {
    return;
  }

  if (
    typeof headers.set ===
    "function"
  ) {
    headers.set(name, value);
    return;
  }

  headers[name] = value;
}

function removeHeader(
  headers,
  name
) {
  if (!headers) {
    return;
  }

  if (
    typeof headers.delete ===
    "function"
  ) {
    headers.delete(name);
    return;
  }

  const normalizedName =
    String(name).toLowerCase();

  Object.keys(headers).forEach(
    (key) => {
      if (
        String(key).toLowerCase() ===
        normalizedName
      ) {
        delete headers[key];
      }
    }
  );
}

function normalizeContentType(config) {
  const headers =
    ensureHeaders(config);

  const method = String(
    config.method || "get"
  ).toLowerCase();

  const hasBodyMethod = [
    "post",
    "put",
    "patch",
  ].includes(method);

  const isFormData =
    typeof FormData !==
      "undefined" &&
    config.data instanceof
      FormData;

  if (isFormData) {
    /*
     * El navegador genera automáticamente el boundary
     * correcto para multipart/form-data.
     */
    removeHeader(
      headers,
      "Content-Type"
    );

    return config;
  }

  if (
    hasBodyMethod &&
    !hasHeader(
      headers,
      "Content-Type"
    )
  ) {
    setHeader(
      headers,
      "Content-Type",
      "application/json"
    );
  }

  return config;
}

function removeAuthorization(config) {
  const headers =
    ensureHeaders(config);

  removeHeader(
    headers,
    "Authorization"
  );

  return config;
}

function applyAccessToken(
  config,
  token
) {
  const headers =
    ensureHeaders(config);

  setHeader(
    headers,
    "Authorization",
    `Bearer ${token}`
  );

  return config;
}

function createSessionExpiredError(
  cause = null
) {
  const error =
    new Error(
      "La sesión ha vencido."
    );

  error.name =
    "SessionExpiredError";

  if (cause) {
    error.cause = cause;
  }

  return error;
}

function getLoginRedirectUrl() {
  if (
    typeof window ===
    "undefined"
  ) {
    return "/login";
  }

  const currentPath =
    window.location.pathname ||
    "/";

  if (
    PUBLIC_FRONTEND_PATHS.has(
      currentPath
    )
  ) {
    return "/login";
  }

  const currentLocation =
    `${currentPath}` +
    `${window.location.search || ""}` +
    `${window.location.hash || ""}`;

  return (
    "/login?redirect=" +
    encodeURIComponent(
      currentLocation
    )
  );
}

/* =========================================================
   CIERRE DE SESIÓN FORZADO
========================================================= */

let logoutPromise = null;

async function forceLogout() {
  if (logoutPromise) {
    return logoutPromise;
  }

  logoutPromise =
    Promise.resolve().then(() => {
      clearAuthStorage();

      if (
        typeof window ===
        "undefined"
      ) {
        return;
      }

      window.dispatchEvent(
        new CustomEvent(
          "sgpc:auth-expired"
        )
      );

      const target =
        getLoginRedirectUrl();

      const current =
        `${window.location.pathname}` +
        `${window.location.search}`;

      if (current !== target) {
        /*
         * Se usa location.replace para reiniciar Pinia y evitar
         * que permanezca un estado autenticado obsoleto.
         */
        window.location.replace(
          target
        );
      }
    });

  return logoutPromise;
}

/* =========================================================
   COLA DE RENOVACIÓN
========================================================= */

let isRefreshing = false;
let failedQueue = [];

function processQueue(
  error,
  token = null
) {
  failedQueue.forEach(
    ({ resolve, reject }) => {
      if (token) {
        resolve(token);
      } else {
        reject(error);
      }
    }
  );

  failedQueue = [];
}

function waitForRefresh() {
  return new Promise(
    (resolve, reject) => {
      failedQueue.push({
        resolve,
        reject,
      });
    }
  );
}

/**
 * Renueva el access token mediante la cookie HttpOnly.
 *
 * No envía "cookie-managed" en el cuerpo. El navegador adjunta
 * la cookie porque withCredentials está habilitado.
 */
async function refreshAccessToken() {
  const { data } =
    await refreshClient.post(
      REFRESH_ROUTE,
      {},
      {
        withCredentials: true,
      }
    );

  const newAccess =
    data?.access ||
    data?.access_token ||
    "";

  const rotatedRefresh =
    data?.refresh ||
    data?.refresh_token ||
    "";

  if (!newAccess) {
    throw new Error(
      "El servidor no devolvió un nuevo access token."
    );
  }

  setAccessToken(newAccess);

  /*
   * En modo HttpOnly no se persiste el refresh en JavaScript.
   * Se conserva la llamada por compatibilidad.
   */
  if (rotatedRefresh) {
    setRefreshToken(
      rotatedRefresh
    );
  }

  return newAccess;
}

async function getRefreshedToken() {
  if (isRefreshing) {
    return waitForRefresh();
  }

  isRefreshing = true;

  try {
    const newAccess =
      await refreshAccessToken();

    processQueue(
      null,
      newAccess
    );

    return newAccess;
  } catch (error) {
    const sessionError =
      createSessionExpiredError(
        error
      );

    processQueue(
      sessionError,
      null
    );

    await forceLogout();

    throw sessionError;
  } finally {
    isRefreshing = false;
  }
}

/* =========================================================
   INTERCEPTOR DE SOLICITUD
========================================================= */

api.interceptors.request.use(
  async (config) => {
    /*
     * No debe establecerse en false. El login, Microsoft y
     * refresh pueden necesitar recibir o enviar cookies.
     */
    config.withCredentials = true;

    ensureHeaders(config);

    /*
     * Las rutas de autenticación no deben recibir un token
     * Authorization antiguo o vencido.
     */
    if (
      isAuthRoute(config) ||
      isRefreshRoute(config)
    ) {
      removeAuthorization(config);

      return normalizeContentType(
        config
      );
    }

    const access =
      getAccessToken();

    if (!access) {
      return normalizeContentType(
        config
      );
    }

    /*
     * Renovación preventiva antes de enviar una petición con
     * un access token próximo a vencer.
     */
    if (
      isAccessTokenExpired(
        30_000
      )
    ) {
      const newAccess =
        await getRefreshedToken();

      applyAccessToken(
        config,
        newAccess
      );

      return normalizeContentType(
        config
      );
    }

    if (
      !hasHeader(
        config.headers,
        "Authorization"
      )
    ) {
      applyAccessToken(
        config,
        access
      );
    }

    return normalizeContentType(
      config
    );
  },

  (error) =>
    Promise.reject(error)
);

/* =========================================================
   INTERCEPTOR DE RESPUESTA
========================================================= */

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest =
      error?.config;

    if (!originalRequest) {
      return Promise.reject(
        error
      );
    }

    if (
      axios.isCancel?.(error) ||
      error?.code ===
        "ERR_CANCELED"
    ) {
      return Promise.reject(
        error
      );
    }

    if (!error?.response) {
      return Promise.reject(
        error
      );
    }

    const status = Number(
      error.response.status
    );

    const detail =
      typeof error.response?.data
        ?.detail === "string"
        ? error.response.data.detail
            .toLowerCase()
        : "";

    const invalidToken =
      error.response?.data?.code ===
        "token_not_valid" ||
      detail.includes("token");

    /*
     * Los errores del login, Microsoft y recuperación deben
     * llegar al componente que realizó la solicitud.
     */
    if (
      isAuthRoute(
        originalRequest
      )
    ) {
      return Promise.reject(
        error
      );
    }

    /*
     * El refresh nunca debe intentar renovarse a sí mismo.
     */
    if (
      isRefreshRoute(
        originalRequest
      )
    ) {
      await forceLogout();

      return Promise.reject(
        createSessionExpiredError(
          error
        )
      );
    }

    const requiresRefresh =
      status === 401 ||
      invalidToken;

    if (!requiresRefresh) {
      return Promise.reject(
        error
      );
    }

    /*
     * Una petición solo se reintenta una vez.
     */
    if (
      originalRequest._retry
    ) {
      await forceLogout();

      return Promise.reject(
        createSessionExpiredError(
          error
        )
      );
    }

    originalRequest._retry = true;
    originalRequest.withCredentials =
      true;

    try {
      const newAccess =
        await getRefreshedToken();

      applyAccessToken(
        originalRequest,
        newAccess
      );

      normalizeContentType(
        originalRequest
      );

      return api(
        originalRequest
      );
    } catch (refreshError) {
      return Promise.reject(
        refreshError
      );
    }
  }
);

export default api;