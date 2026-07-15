const STORAGE_KEYS =
  Object.freeze({
    access: Object.freeze([
      "access_token",
      "access",
    ]),

    accessCanonical:
      "access_token",

    user: "user",
    nombres: "nombres",
    apellidos: "apellidos",
    avatar: "avatar_url",
    rol: "rol",
    email: "email",
    autorId: "autor_id",
  });

const LEGACY_REFRESH_KEYS =
  Object.freeze([
    "refresh_token",
    "refresh",
  ]);

/**
 * Marcador de compatibilidad.
 *
 * El refresh token real no está disponible para JavaScript:
 * el backend debe administrarlo mediante una cookie HttpOnly.
 */
export const REFRESH_COOKIE_MARKER =
  "cookie-managed";

export const AUTH_STORAGE_KEYS =
  STORAGE_KEYS;

const normalizeStoredString = (
  value
) => String(value ?? "").trim();

export const getStorageValue = (
  key,
  fallback = ""
) => {
  try {
    const value =
      localStorage.getItem(key);

    return value ?? fallback;
  } catch {
    return fallback;
  }
};

export const setStorageValue = (
  key,
  value
) => {
  try {
    localStorage.setItem(
      key,
      String(value ?? "")
    );
  } catch {
    /*
     * El almacenamiento puede estar bloqueado por el navegador.
     */
  }
};

export const removeStorageValue = (
  key
) => {
  try {
    localStorage.removeItem(key);
  } catch {
    /*
     * El almacenamiento puede estar bloqueado por el navegador.
     */
  }
};

export const readFirstStorageValue = (
  keys = []
) => {
  const normalizedKeys =
    Array.isArray(keys)
      ? keys
      : [keys];

  for (const key of normalizedKeys) {
    const value =
      normalizeStoredString(
        getStorageValue(
          key,
          ""
        )
      );

    if (value) {
      return value;
    }
  }

  return "";
};

export const getAccessToken = () =>
  readFirstStorageValue(
    STORAGE_KEYS.access
  );

/**
 * Se conserva por compatibilidad con código existente.
 *
 * Nunca devuelve el refresh real y no debe enviarse en el body
 * de /auth/refresh/. Axios debe usar withCredentials: true.
 */
export const getRefreshToken = () =>
  REFRESH_COOKIE_MARKER;

export const setAccessToken = (
  value
) => {
  const token =
    normalizeStoredString(value);

  if (token) {
    setStorageValue(
      STORAGE_KEYS.accessCanonical,
      token
    );
  } else {
    removeStorageValue(
      STORAGE_KEYS.accessCanonical
    );
  }

  /*
   * Se elimina la antigua clave alternativa para mantener
   * una sola fuente de verdad.
   */
  removeStorageValue("access");

  return token;
};

/**
 * El refresh token se administra mediante cookie HttpOnly.
 * Esta función no guarda el valor recibido.
 */
export const setRefreshToken = (
  _value
) => REFRESH_COOKIE_MARKER;

export const setAuthTokens = ({
  access = "",
  refresh = "",
} = {}) => {
  const savedAccess =
    setAccessToken(access);

  /*
   * Se mantiene por compatibilidad, aunque no persiste
   * el refresh token.
   */
  setRefreshToken(refresh);

  return {
    access: savedAccess,
    refresh:
      REFRESH_COOKIE_MARKER,
  };
};

export const getStoredUser = (
  fallback = null
) => {
  try {
    const raw =
      getStorageValue(
        STORAGE_KEYS.user,
        ""
      );

    return raw
      ? JSON.parse(raw)
      : fallback;
  } catch {
    return fallback;
  }
};

export const setStoredUser = (
  value
) => {
  if (
    !value ||
    typeof value !== "object"
  ) {
    removeStorageValue(
      STORAGE_KEYS.user
    );

    return null;
  }

  try {
    localStorage.setItem(
      STORAGE_KEYS.user,
      JSON.stringify(value)
    );

    return value;
  } catch {
    return null;
  }
};

export const clearPersistedProfileFields =
  () => {
    [
      STORAGE_KEYS.user,
      STORAGE_KEYS.nombres,
      STORAGE_KEYS.apellidos,
      STORAGE_KEYS.avatar,
      STORAGE_KEYS.rol,
      STORAGE_KEYS.email,
      STORAGE_KEYS.autorId,
    ].forEach(removeStorageValue);
  };

export const clearAuthStorage =
  () => {
    [
      STORAGE_KEYS.accessCanonical,
      "access",

      ...LEGACY_REFRESH_KEYS,

      STORAGE_KEYS.user,
      STORAGE_KEYS.nombres,
      STORAGE_KEYS.apellidos,
      STORAGE_KEYS.avatar,
      STORAGE_KEYS.rol,
      STORAGE_KEYS.email,
      STORAGE_KEYS.autorId,
    ].forEach(removeStorageValue);
  };

/* ============================================================
   JWT EXPIRATION HELPERS
============================================================ */

export const decodeJwtPayload = (
  token = ""
) => {
  const normalized =
    normalizeStoredString(token);

  if (
    !normalized ||
    normalized ===
      REFRESH_COOKIE_MARKER
  ) {
    return null;
  }

  const parts =
    normalized.split(".");

  if (parts.length !== 3) {
    return null;
  }

  try {
    const base64Url =
      parts[1];

    const base64 =
      base64Url
        .replace(/-/g, "+")
        .replace(/_/g, "/");

    const padded =
      base64.padEnd(
        base64.length +
          (
            (
              4 -
              (
                base64.length %
                4
              )
            ) %
            4
          ),
        "="
      );

    const binary =
      atob(padded);

    const bytes =
      Uint8Array.from(
        binary,
        (character) =>
          character.charCodeAt(0)
      );

    const json =
      new TextDecoder().decode(
        bytes
      );

    return JSON.parse(json);
  } catch {
    return null;
  }
};

export const getTokenExpirationMs = (
  token = ""
) => {
  const payload =
    decodeJwtPayload(token);

  const exp =
    Number(payload?.exp || 0);

  if (
    !Number.isFinite(exp) ||
    exp <= 0
  ) {
    return 0;
  }

  return exp * 1000;
};

export const isTokenExpired = (
  token = "",
  skewMs = 30_000
) => {
  if (
    token ===
    REFRESH_COOKIE_MARKER
  ) {
    /*
     * JavaScript no puede inspeccionar una cookie HttpOnly.
     */
    return false;
  }

  const expMs =
    getTokenExpirationMs(token);

  if (!expMs) {
    return true;
  }

  return (
    Date.now() +
      Number(skewMs || 0) >=
    expMs
  );
};

export const getAccessTokenExpirationMs =
  () =>
    getTokenExpirationMs(
      getAccessToken()
    );

export const isAccessTokenExpired = (
  skewMs = 30_000
) =>
  isTokenExpired(
    getAccessToken(),
    skewMs
  );

/**
 * La vigencia real de la cookie solo puede determinarla
 * el backend mediante una solicitud a /auth/refresh/.
 */
export const isRefreshTokenExpired = (
  _skewMs = 30_000
) => false;

/**
 * Un access vencido todavía permite intentar una renovación
 * mediante la cookie HttpOnly.
 */
export const hasUsableSession = () =>
  Boolean(getAccessToken());