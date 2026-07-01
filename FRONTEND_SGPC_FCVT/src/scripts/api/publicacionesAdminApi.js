import api from "./axios";

/**
 * API administrativa de publicaciones.
 * Opera sobre /api/admin/publicaciones/ y sus acciones de creación delegada.
 */

const ADMIN_PUBLICACIONES_BASE = "admin/publicaciones/";

function esValorVacio(value) {
  return (
    value === undefined ||
    value === null ||
    value === "" ||
    value === "null" ||
    value === "undefined"
  );
}

function normalizarBoolean(value) {
  if (value === true || value === false) return value;
  if (esValorVacio(value)) return undefined;

  const s = String(value).trim().toLowerCase();

  if (["1", "true", "yes", "y", "on"].includes(s)) return true;
  if (["0", "false", "no", "n", "off"].includes(s)) return false;

  return undefined;
}

function appendFormValue(formData, key, value) {
  if (esValorVacio(value)) return;

  if (value instanceof File || value instanceof Blob) {
    formData.append(key, value);
    return;
  }

  if (value instanceof Date) {
    formData.append(key, value.toISOString().slice(0, 10));
    return;
  }

  if (Array.isArray(value)) {
    value.forEach((item) => {
      if (!esValorVacio(item)) {
        formData.append(key, item);
      }
    });
    return;
  }

  if (typeof value === "boolean") {
    formData.append(key, value ? "true" : "false");
    return;
  }

  formData.append(key, value);
}

function buildParams(filters = {}) {
  const params = {};

  const allowedKeys = [
    "q",
    "tipo",
    "tipo_publicacion_final",
    "usuario_objetivo_id",
    "usuario_id",
    "autor_objetivo_id",
    "autor_id",
    "admin_registrador_id",
    "facultad_id",
    "carrera_id",
    "anio",
    "solo_delegadas",
    "solo_con_pdf",
    "solo_con_adjuntos",
    "ordering",
    "page",
    "page_size",
  ];

  allowedKeys.forEach((key) => {
    const value = filters[key];
    if (esValorVacio(value)) return;

    if (
      key === "solo_delegadas" ||
      key === "solo_con_pdf" ||
      key === "solo_con_adjuntos"
    ) {
      const boolValue = normalizarBoolean(value);
      if (typeof boolValue === "boolean") {
        params[key] = boolValue ? "true" : "false";
      }
      return;
    }

    params[key] = value;
  });

  return params;
}

function normalizeListResponse(responseData) {
  if (Array.isArray(responseData)) {
    return {
      count: responseData.length,
      next: null,
      previous: null,
      results: responseData,
    };
  }

  if (responseData && Array.isArray(responseData.results)) {
    return {
      count: Number(responseData.count || 0),
      next: responseData.next || null,
      previous: responseData.previous || null,
      results: responseData.results,
    };
  }

  return {
    count: 0,
    next: null,
    previous: null,
    results: [],
  };
}

function normalizeFileItem(item, index) {
  if (!item) return null;

  if (item instanceof File || item instanceof Blob) {
    return {
      file: item,
      nombre: item?.name ? String(item.name).replace(/\.[^/.]+$/, "") : "",
      orden: index + 1,
    };
  }

  const file =
    item.file ||
    item.archivo ||
    item.uploadedFile ||
    item.rawFile ||
    item.pdf ||
    null;

  if (!(file instanceof File || file instanceof Blob)) {
    return null;
  }

  return {
    file,
    nombre: String(item.nombre || item.name || "").trim(),
    orden: Number(item.orden || index + 1),
  };
}

function normalizeFilesList(payload = {}) {
  const rawList = Array.isArray(payload.files)
    ? payload.files
    : Array.isArray(payload.archivos)
      ? payload.archivos
      : Array.isArray(payload.adjuntos)
        ? payload.adjuntos
        : [];

  return rawList
    .map((item, index) => normalizeFileItem(item, index))
    .filter(Boolean)
    .map((item, index) => ({
      ...item,
      nombre:
        String(item.nombre || "").trim() ||
        (item.file?.name
          ? String(item.file.name).replace(/\.[^/.]+$/, "")
          : `Archivo ${index + 1}`),
      orden: Number(item.orden || index + 1),
    }));
}

function buildAdjuntosMetaFromFiles(normalizedFiles = []) {
  if (!Array.isArray(normalizedFiles) || !normalizedFiles.length) return "";

  return JSON.stringify(
    normalizedFiles.map((item, index) => ({
      nombre:
        String(item?.nombre || "").trim() ||
        (item?.file?.name
          ? String(item.file.name).replace(/\.[^/.]+$/, "")
          : `Archivo ${index + 1}`),
      orden: Number(item?.orden || index + 1),
    }))
  );
}

function normalizeMetaValue(metaValue, fallbackFiles = []) {
  if (esValorVacio(metaValue)) {
    return buildAdjuntosMetaFromFiles(fallbackFiles);
  }

  if (typeof metaValue === "string") {
    const raw = metaValue.trim();
    return raw || buildAdjuntosMetaFromFiles(fallbackFiles);
  }

  if (Array.isArray(metaValue)) {
    return JSON.stringify(
      metaValue.map((item, index) => ({
        nombre: String(item?.nombre || "").trim(),
        orden: Number(item?.orden || index + 1),
      }))
    );
  }

  return buildAdjuntosMetaFromFiles(fallbackFiles);
}

function buildAutoresJson(autores = []) {
  if (!Array.isArray(autores)) return "[]";

  const normalized = autores
    .map((item, index) => {
      const autorId = Number(item?.autor_id || item?.autor || item?.id || 0);

      if (!Number.isFinite(autorId) || autorId <= 0) {
        return null;
      }

      const orden = Number(item?.orden || index + 1);
      const rol = String(item?.rol_autoria || "").trim().toLowerCase();

      return {
        autor_id: autorId,
        orden: Number.isFinite(orden) && orden > 0 ? orden : index + 1,
        ...(rol ? { rol_autoria: rol } : {}),
      };
    })
    .filter(Boolean);

  return JSON.stringify(normalized);
}

function buildDelegatedCreateFormData(payload = {}) {
  const formData = new FormData();

  const {
    autores,
    files,
    archivos,
    adjuntos,
    meta,
    archivos_meta,
    ...rest
  } = payload;

  Object.entries(rest).forEach(([key, value]) => {
    appendFormValue(formData, key, value);
  });

  formData.append("autores", buildAutoresJson(autores || []));

  const normalizedFiles = normalizeFilesList({
    files,
    archivos,
    adjuntos,
  });

  normalizedFiles.forEach((item) => {
    formData.append("files", item.file);
  });

  const metaValue = normalizeMetaValue(meta || archivos_meta, normalizedFiles);

  if (metaValue) {
    formData.append("meta", metaValue);
  }

  return formData;
}

function buildUpdatePayload(payload = {}) {
  const mustUseFormData = Object.values(payload).some((value) => {
    if (value instanceof File || value instanceof Blob) return true;

    if (Array.isArray(value)) {
      return value.some((item) => item instanceof File || item instanceof Blob);
    }

    return false;
  });

  if (!mustUseFormData) {
    return payload;
  }

  const formData = new FormData();

  Object.entries(payload).forEach(([key, value]) => {
    if (key === "autores") {
      formData.append("autores", buildAutoresJson(value || []));
      return;
    }

    appendFormValue(formData, key, value);
  });

  return formData;
}

export async function listarAdminPublicaciones(filters = {}) {
  const { data } = await api.get(ADMIN_PUBLICACIONES_BASE, {
    params: buildParams(filters),
  });

  return normalizeListResponse(data);
}

export async function obtenerAdminPublicacion(publicacionId) {
  const { data } = await api.get(
    `${ADMIN_PUBLICACIONES_BASE}${publicacionId}/`
  );

  return data;
}

export async function actualizarAdminPublicacion(
  publicacionId,
  payload = {},
  { partial = true } = {}
) {
  const body = buildUpdatePayload(payload);
  const method = partial ? "patch" : "put";

  const config =
    body instanceof FormData
      ? {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      : undefined;

  const { data } = await api[method](
    `${ADMIN_PUBLICACIONES_BASE}${publicacionId}/`,
    body,
    config
  );

  return data;
}

export async function eliminarAdminPublicacion(publicacionId) {
  const { data } = await api.delete(
    `${ADMIN_PUBLICACIONES_BASE}${publicacionId}/`
  );

  return data;
}

export async function crearAdminArticuloDelegado(payload = {}) {
  const body = buildDelegatedCreateFormData(payload);

  const { data } = await api.post(
    `${ADMIN_PUBLICACIONES_BASE}articulos/crear/`,
    body,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return data;
}

export async function crearAdminLibroDelegado(payload = {}) {
  const body = buildDelegatedCreateFormData(payload);

  const { data } = await api.post(
    `${ADMIN_PUBLICACIONES_BASE}libros/crear/`,
    body,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return data;
}

export async function crearAdminCapituloDelegado(payload = {}) {
  const body = buildDelegatedCreateFormData(payload);

  const { data } = await api.post(
    `${ADMIN_PUBLICACIONES_BASE}capitulos/crear/`,
    body,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return data;
}

export async function crearAdminPonenciaDelegada(payload = {}) {
  const body = buildDelegatedCreateFormData(payload);

  const { data } = await api.post(
    `${ADMIN_PUBLICACIONES_BASE}ponencias/crear/`,
    body,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return data;
}

export async function crearAdminPublicacionDelegada(tipo, payload = {}) {
  const normalized = String(tipo || "").trim().toLowerCase();

  if (
    normalized === "articulo" ||
    normalized === "articulo_alto_impacto" ||
    normalized === "articulo_regional" ||
    normalized === "alto_impacto" ||
    normalized === "regional" ||
    normalized === "aai" ||
    normalized === "ar"
  ) {
    return crearAdminArticuloDelegado(payload);
  }

  if (normalized === "libro" || normalized === "lib") {
    return crearAdminLibroDelegado(payload);
  }

  if (
    normalized === "capitulo" ||
    normalized === "capitulo_libro" ||
    normalized === "capítulo" ||
    normalized === "cap" 
  ) {
    return crearAdminCapituloDelegado(payload);
  }

  if (normalized === "ponencia" || normalized === "pon") {
    return crearAdminPonenciaDelegada(payload);
  }

  throw new Error("Tipo de creación delegada no soportado.");
}

export default {
  listarAdminPublicaciones,
  obtenerAdminPublicacion,
  actualizarAdminPublicacion,
  eliminarAdminPublicacion,
  crearAdminArticuloDelegado,
  crearAdminLibroDelegado,
  crearAdminCapituloDelegado,
  crearAdminPonenciaDelegada,
  crearAdminPublicacionDelegada,
};