const normalizeBoolean = (value) => {
  return (
    value === true ||
    value === 1 ||
    value === "1" ||
    value === "true" ||
    value === "True"
  );
};

export const isAdminUser = (user) => {
  if (!user || typeof user !== "object") return false;

  const role = String(user?.rol ?? user?.role ?? "").trim().toLowerCase();
  const roles = Array.isArray(user?.roles)
    ? user.roles.map((item) => String(item ?? "").trim().toLowerCase())
    : [];

  return !!(
    normalizeBoolean(user?.is_staff) ||
    normalizeBoolean(user?.is_superuser) ||
    normalizeBoolean(user?.es_admin) ||
    normalizeBoolean(user?.is_admin) ||
    role === "admin" ||
    role === "administrador" ||
    roles.includes("admin") ||
    roles.includes("administrador")
  );
};