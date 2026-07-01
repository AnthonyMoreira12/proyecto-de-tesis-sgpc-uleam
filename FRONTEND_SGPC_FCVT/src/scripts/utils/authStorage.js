const STORAGE_KEYS = Object.freeze({
  access: Object.freeze(["access_token", "access"]),
  accessCanonical: "access_token",
  user: "user",
  nombres: "nombres",
  apellidos: "apellidos",
  avatar: "avatar_url",
  rol: "rol",
  email: "email",
  autorId: "autor_id",
});

export const AUTH_STORAGE_KEYS = STORAGE_KEYS;

const normalizeStoredString = (value) => String(value ?? "").trim();

export const getStorageValue = (key, fallback = "") => {
  try {
    const value = localStorage.getItem(key);
    return value ?? fallback;
  } catch {
    return fallback;
  }
};

export const setStorageValue = (key, value) => {
  try {
    localStorage.setItem(key, String(value ?? ""));
  } catch { }
};

export const removeStorageValue = (key) => {
  try {
    localStorage.removeItem(key);
  } catch { }
};

export const readFirstStorageValue = (keys = []) => {
  const normalizedKeys = Array.isArray(keys) ? keys : [keys];
  for (const key of normalizedKeys) {
    const value = normalizeStoredString(getStorageValue(key, ""));
    if (value) return value;
  }
  return "";
};

export const getAccessToken = () => readFirstStorageValue(STORAGE_KEYS.access);

// 🔒 SEGURIDAD: Ya no leemos el refresh token de LocalStorage.
// Devolvemos un string genérico para que el sistema sepa que dependemos de la Cookie.
export const getRefreshToken = () => "cookie-managed";

export const setAccessToken = (value) => {
  const token = normalizeStoredString(value);
  if (token) {
    setStorageValue(STORAGE_KEYS.accessCanonical, token);
  } else {
    removeStorageValue(STORAGE_KEYS.accessCanonical);
  }
  removeStorageValue("access");
  return token;
};

// 🔒 SEGURIDAD: Ya no guardamos el refresh token. Lo ignoramos.
export const setRefreshToken = (value) => "cookie-managed";

export const setAuthTokens = ({ access = "", refresh = "" } = {}) => {
  const savedAccess = setAccessToken(access);
  return { access: savedAccess, refresh: "cookie-managed" };
};

export const getStoredUser = (fallback = null) => {
  try {
    const raw = getStorageValue(STORAGE_KEYS.user, "");
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
};

export const setStoredUser = (value) => {
  if (!value || typeof value !== "object") {
    removeStorageValue(STORAGE_KEYS.user);
    return null;
  }
  try {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(value));
    return value;
  } catch {
    return null;
  }
};

export const clearPersistedProfileFields = () => {
  [
    STORAGE_KEYS.user, STORAGE_KEYS.nombres, STORAGE_KEYS.apellidos,
    STORAGE_KEYS.avatar, STORAGE_KEYS.rol, STORAGE_KEYS.email, STORAGE_KEYS.autorId,
  ].forEach(removeStorageValue);
};

export const clearAuthStorage = () => {
  [
    STORAGE_KEYS.accessCanonical, "access",
    "refresh_token", "refresh", // Limpiamos los viejos por si acaso
    STORAGE_KEYS.user, STORAGE_KEYS.nombres, STORAGE_KEYS.apellidos,
    STORAGE_KEYS.avatar, STORAGE_KEYS.rol, STORAGE_KEYS.email, STORAGE_KEYS.autorId,
  ].forEach(removeStorageValue);
};

/* ============================================================
   JWT EXPIRATION HELPERS
============================================================ */

export const decodeJwtPayload = (token = "") => {
  const normalized = normalizeStoredString(token);
  if (!normalized || normalized === "cookie-managed") return null;

  const parts = normalized.split(".");
  if (parts.length !== 3) return null;

  try {
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    const json = decodeURIComponent(
      atob(padded).split("").map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`).join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
};

export const getTokenExpirationMs = (token = "") => {
  const payload = decodeJwtPayload(token);
  const exp = Number(payload?.exp || 0);
  return (!Number.isFinite(exp) || exp <= 0) ? 0 : exp * 1000;
};

export const isTokenExpired = (token = "", skewMs = 30_000) => {
  if (token === "cookie-managed") return false; // La cookie la maneja el backend
  const expMs = getTokenExpirationMs(token);
  return !expMs ? true : Date.now() + skewMs >= expMs;
};

export const getAccessTokenExpirationMs = () => getTokenExpirationMs(getAccessToken());

export const isAccessTokenExpired = (skewMs = 30_000) => isTokenExpired(getAccessToken(), skewMs);

// Como es una cookie, asumimos que siempre es válido hasta que el backend diga lo contrario con un error 401
export const isRefreshTokenExpired = (skewMs = 30_000) => false; 

export const hasUsableSession = () => {
  const access = getAccessToken();
  return !!access;
};