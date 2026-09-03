/*
 * Utilidades para clasificación y permisos de usuarios.
 *
 * Reglas del SGPC ULEAM:
 *
 * - Administrador:
 *     is_staff = true
 *     o
 *     is_superuser = true
 *
 * - Usuario institucional:
 *     rol = autor
 *     auth_source = microsoft
 *
 * - Usuario externo:
 *     rol = autor_externo
 *     auth_source = local
 *
 * Los permisos administrativos son independientes del tipo
 * de cuenta.
 */

const ROLE_INSTITUTIONAL = "autor";
const ROLE_EXTERNAL = "autor_externo";

const AUTH_SOURCE_LOCAL = "local";
const AUTH_SOURCE_MICROSOFT = "microsoft";


/* ============================================================
   NORMALIZACIÓN
============================================================ */

export const normalizeAuthText = (value) => {
  return String(value ?? "")
    .trim()
    .toLowerCase();
};


export const normalizeAuthBoolean = (
  value,
  fallback = false
) => {
  if (value === true || value === 1) {
    return true;
  }

  if (value === false || value === 0) {
    return false;
  }

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return Boolean(fallback);
  }

  const normalized =
    normalizeAuthText(value);

  if (
    normalized === "1" ||
    normalized === "true" ||
    normalized === "yes" ||
    normalized === "y" ||
    normalized === "on" ||
    normalized === "si" ||
    normalized === "sí"
  ) {
    return true;
  }

  if (
    normalized === "0" ||
    normalized === "false" ||
    normalized === "no" ||
    normalized === "n" ||
    normalized === "off"
  ) {
    return false;
  }

  return Boolean(fallback);
};


/* ============================================================
   PERMISOS ADMINISTRATIVOS
============================================================ */

export const isAdminUser = (user) => {
  if (
    !user ||
    typeof user !== "object" ||
    Array.isArray(user)
  ) {
    return false;
  }

  /*
   * Los únicos campos autorizados para determinar el acceso
   * administrativo son los campos canónicos del modelo Django.
   *
   * No se confía en:
   *
   * - rol = admin
   * - rol = administrador
   * - roles = [...]
   * - es_admin almacenado previamente
   * - is_admin almacenado previamente
   */
  return Boolean(
    normalizeAuthBoolean(
      user.is_staff,
      false
    ) ||
    normalizeAuthBoolean(
      user.is_superuser,
      false
    )
  );
};


/* ============================================================
   CLASIFICACIÓN DE CUENTAS
============================================================ */

export const isInstitutionalUser = (user) => {
  if (
    !user ||
    typeof user !== "object" ||
    Array.isArray(user)
  ) {
    return false;
  }

  const role = normalizeAuthText(
    user.rol ?? user.role
  );

  const authSource = normalizeAuthText(
    user.auth_source
  );

  return Boolean(
    role === ROLE_INSTITUTIONAL &&
    authSource === AUTH_SOURCE_MICROSOFT
  );
};


export const isExternalUser = (user) => {
  if (
    !user ||
    typeof user !== "object" ||
    Array.isArray(user)
  ) {
    return false;
  }

  const role = normalizeAuthText(
    user.rol ?? user.role
  );

  const authSource = normalizeAuthText(
    user.auth_source
  );

  return Boolean(
    role === ROLE_EXTERNAL &&
    authSource === AUTH_SOURCE_LOCAL
  );
};


export const hasValidAccountClassification = (
  user
) => {
  return Boolean(
    isInstitutionalUser(user) ||
    isExternalUser(user)
  );
};


/* ============================================================
   ETIQUETAS
============================================================ */

export const getAccountTypeLabel = (user) => {
  if (isInstitutionalUser(user)) {
    return "Cuenta institucional";
  }

  if (isExternalUser(user)) {
    return "Cuenta externa";
  }

  return "Cuenta sin clasificación válida";
};


export const getAuthSourceLabel = (user) => {
  const authSource = normalizeAuthText(
    user?.auth_source
  );

  if (authSource === AUTH_SOURCE_MICROSOFT) {
    return "Microsoft 365";
  }

  if (authSource === AUTH_SOURCE_LOCAL) {
    return "Cuenta local";
  }

  return "Origen de autenticación no definido";
};


export const getUserRoleLabel = (user) => {
  if (isInstitutionalUser(user)) {
    return "Autor institucional";
  }

  if (isExternalUser(user)) {
    return "Autor externo";
  }

  const role = normalizeAuthText(
    user?.rol ?? user?.role
  );

  if (role === ROLE_INSTITUTIONAL) {
    return "Autor";
  }

  if (role === ROLE_EXTERNAL) {
    return "Autor externo";
  }

  return "Usuario";
};


/* ============================================================
   ESTADO DE CUENTA
============================================================ */

export const isActiveUser = (user) => {
  if (
    !user ||
    typeof user !== "object" ||
    Array.isArray(user)
  ) {
    return false;
  }

  return normalizeAuthBoolean(
    user.is_active,
    false
  );
};


export const isPendingExternalUser = (user) => {
  return Boolean(
    isExternalUser(user) &&
    !isActiveUser(user)
  );
};


/* ============================================================
   CÉDULA Y PERFIL
============================================================ */

export const hasValidCedula = (user) => {
  const cedula = String(
    user?.identificacion ?? ""
  ).trim();

  return /^\d{10}$/.test(cedula);
};


export const hasInstitutionalSite = (user) => {
  if (!isInstitutionalUser(user)) {
    return false;
  }

  const siteId =
    user?.sede_id ??
    (
      typeof user?.sede === "object"
        ? user.sede?.id
        : user?.sede
    );

  return Boolean(siteId);
};


export const hasInstitutionalCareer = (user) => {
  if (!isInstitutionalUser(user)) {
    return false;
  }

  const careerId =
    user?.carrera_id ??
    (
      typeof user?.carrera === "object"
        ? user.carrera?.id
        : user?.carrera
    );

  return Boolean(careerId);
};


export const calculateProfileComplete = (
  user
) => {
  /*
   * Regla vigente del backend:
   *
   * - una cuenta externa local puede tener el perfil completo
   *   sin cédula y nunca posee Sede/Carrera institucional;
   * - una cuenta institucional Microsoft requiere cédula válida,
   *   Sede y Carrera. La coherencia Sede-Carrera la valida el
   *   backend mediante CarreraSede activa.
   */
  if (isExternalUser(user)) {
    return true;
  }

  if (isInstitutionalUser(user)) {
    return Boolean(
      hasValidCedula(user) &&
      hasInstitutionalSite(user) &&
      hasInstitutionalCareer(user)
    );
  }

  return false;
};


/* ============================================================
   EXPORTACIÓN PREDETERMINADA
============================================================ */

export default {
  normalizeAuthText,
  normalizeAuthBoolean,

  isAdminUser,
  isInstitutionalUser,
  isExternalUser,
  hasValidAccountClassification,

  getAccountTypeLabel,
  getAuthSourceLabel,
  getUserRoleLabel,

  isActiveUser,
  isPendingExternalUser,

  hasValidCedula,
  hasInstitutionalSite,
  hasInstitutionalCareer,
  calculateProfileComplete,
};
