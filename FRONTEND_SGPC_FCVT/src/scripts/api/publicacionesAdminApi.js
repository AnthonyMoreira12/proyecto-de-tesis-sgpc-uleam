import api from "./axios";

/**
 * API administrativa de publicaciones.
 * Opera sobre /api/admin/publicaciones/, creación delegada,
 * auditoría y decisiones del flujo formal de revisión.
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

function normalizarId(value) {
  if (esValorVacio(value)) {
    return null;
  }

  if (
    typeof value === "object" &&
    !(value instanceof Date) &&
    !(typeof File !== "undefined" && value instanceof File) &&
    !(typeof Blob !== "undefined" && value instanceof Blob)
  ) {
    const candidate =
      value.id ??
      value.pk ??
      value.value;

    if (!esValorVacio(candidate)) {
      return normalizarId(candidate);
    }
  }

  const parsed = Number(value);

  return (
    Number.isInteger(parsed) &&
    parsed > 0
  )
    ? parsed
    : null;
}

function normalizarPeriodoPublicacion(
  payload = {}
) {
  const output = {
    ...(payload || {}),
  };

  let year =
    output.anio_publicacion ??
    output.anio ??
    null;

  let month =
    output.mes_publicacion ??
    output.mes ??
    null;

  const legacyDate = String(
    output.fecha_publicacion || ""
  ).trim();

  if (legacyDate) {
    const match = legacyDate.match(
      /^(\d{4})-(\d{1,2})(?:-\d{1,2})?$/
    );

    if (match) {
      if (esValorVacio(year)) {
        year = Number(match[1]);
      }

      if (esValorVacio(month)) {
        month = Number(match[2]);
      }
    }
  }

  if (!esValorVacio(year)) {
    const parsedYear = Number(year);
    output.anio_publicacion =
      Number.isInteger(parsedYear)
        ? parsedYear
        : year;
  }

  if (!esValorVacio(month)) {
    const parsedMonth = Number(month);
    output.mes_publicacion =
      Number.isInteger(parsedMonth)
        ? parsedMonth
        : month;
  }

  delete output.fecha_publicacion;
  delete output.anio;
  delete output.mes;

  return output;
}

function normalizarPublicacionId(value) {
  const id = normalizarId(value);

  if (!id) {
    throw new Error(
      "El identificador de la publicación no es válido."
    );
  }

  return id;
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
    "estado",
    "estado_publicacion",
    "status",
    "sede_id",
    "sede",
    "facultad_id",
    "carrera_id",
    "anio",
    "mes",
    "solo_delegadas",
    "solo_con_pdf",
    "solo_con_adjuntos",
    "ordering",
    "page",
    "page_size",
  ];

  const idFilterKeys = new Set([
    "usuario_objetivo_id",
    "usuario_id",
    "autor_objetivo_id",
    "autor_id",
    "admin_registrador_id",
    "sede_id",
    "sede",
    "facultad_id",
    "carrera_id",
  ]);

  allowedKeys.forEach((key) => {
    const value = filters[key];
    if (esValorVacio(value)) return;

    if (idFilterKeys.has(key)) {
      const id = normalizarId(value);

      if (id) {
        params[key] = id;
      }

      return;
    }

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
  if (!Array.isArray(autores)) {
    return "[]";
  }

  const normalized = autores
    .map((item, index) => {
      const autorId = normalizarId(
        item?.autor_id ??
        item?.autor ??
        item?.id
      );

      if (!autorId) {
        return null;
      }

      const rawOrder = Number(
        item?.orden || index + 1
      );

      return {
        autor_id: autorId,
        orden:
          Number.isFinite(rawOrder) &&
          rawOrder > 0
            ? rawOrder
            : index + 1,
      };
    })
    .filter(Boolean)
    .sort((left, right) =>
      left.orden - right.orden
    )
    .map((item, index) => ({
      autor_id: item.autor_id,
      orden: index + 1,
    }));

  return JSON.stringify(normalized);
}

function buildDelegatedCreateFormData(payload = {}) {
  const formData = new FormData();

  const normalizedPayload =
    normalizarPeriodoPublicacion(
      payload
    );

  const {
    autores,
    files,
    archivos,
    adjuntos,
    meta,
    archivos_meta,
    ...rest
  } = normalizedPayload;

  const relationFields = new Set([
    "sede",
    "facultad",
    "carrera",
    "proyecto",
    "area",
    "subarea",
    "pais",
    "ciudad",
    "usuario_objetivo_id",
    "usuario_id",
    "autor_objetivo_id",
    "autor_id",
  ]);

  Object.entries(rest).forEach(([key, value]) => {
    if (relationFields.has(key)) {
      appendFormValue(
        formData,
        key,
        normalizarId(value)
      );
      return;
    }

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
  const normalizedPayload =
    normalizarPeriodoPublicacion(
      payload
    );

  if (Array.isArray(normalizedPayload.autores)) {
    normalizedPayload.autores = JSON.parse(
      buildAutoresJson(
        normalizedPayload.autores
      )
    );
  }

  const relationFields = [
    "sede",
    "facultad",
    "carrera",
    "proyecto",
    "area",
    "subarea",
    "pais",
    "ciudad",
  ];

  relationFields.forEach((key) => {
    if (
      Object.prototype.hasOwnProperty.call(
        normalizedPayload,
        key
      )
    ) {
      normalizedPayload[key] =
        normalizarId(
          normalizedPayload[key]
        );
    }
  });

  const mustUseFormData = Object.values(
    normalizedPayload
  ).some((value) => {
    if (
      (typeof File !== "undefined" && value instanceof File) ||
      (typeof Blob !== "undefined" && value instanceof Blob)
    ) {
      return true;
    }

    if (Array.isArray(value)) {
      return value.some(
        (item) =>
          (typeof File !== "undefined" && item instanceof File) ||
          (typeof Blob !== "undefined" && item instanceof Blob)
      );
    }

    return false;
  });

  if (!mustUseFormData) {
    return normalizedPayload;
  }

  const formData = new FormData();

  Object.entries(
    normalizedPayload
  ).forEach(([key, value]) => {
    if (key === "autores") {
      formData.append(
        "autores",
        buildAutoresJson(value || [])
      );
      return;
    }

    appendFormValue(
      formData,
      key,
      value
    );
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
  const id = normalizarPublicacionId(
    publicacionId
  );

  const { data } = await api.get(
    `${ADMIN_PUBLICACIONES_BASE}${id}/`
  );

  return data;
}

export async function actualizarAdminPublicacion(
  publicacionId,
  payload = {},
  { partial = true } = {}
) {
  const id = normalizarPublicacionId(
    publicacionId
  );

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
    `${ADMIN_PUBLICACIONES_BASE}${id}/`,
    body,
    config
  );

  return data;
}

export async function eliminarAdminPublicacion(publicacionId) {
  const id = normalizarPublicacionId(
    publicacionId
  );

  const { data } = await api.delete(
    `${ADMIN_PUBLICACIONES_BASE}${id}/`
  );

  return data;
}

export async function obtenerAdminPublicacionHistorial(
  publicacionId
) {
  const id = normalizarPublicacionId(
    publicacionId
  );

  const { data } = await api.get(
    `${ADMIN_PUBLICACIONES_BASE}${id}/historial/`
  );

  return data;
}

async function resolverDecisionAdmin(
  publicacionId,
  accion,
  comentario = ""
) {
  const id = normalizarPublicacionId(
    publicacionId
  );

  const normalizedAction = String(
    accion || ""
  ).trim().toLowerCase();

  if (
    ![
      "aprobar",
      "observar",
      "rechazar",
    ].includes(normalizedAction)
  ) {
    throw new Error(
      "La decisión administrativa indicada no es válida."
    );
  }

  const body = {};
  const normalizedComment = String(
    comentario || ""
  ).trim();

  if (normalizedComment) {
    body.comentario = normalizedComment;
  }

  const { data } = await api.post(
    `${ADMIN_PUBLICACIONES_BASE}${id}/${normalizedAction}/`,
    body
  );

  return data;
}

export async function aprobarAdminPublicacion(
  publicacionId,
  comentario = ""
) {
  return resolverDecisionAdmin(
    publicacionId,
    "aprobar",
    comentario
  );
}

export async function observarAdminPublicacion(
  publicacionId,
  comentario
) {
  return resolverDecisionAdmin(
    publicacionId,
    "observar",
    comentario
  );
}

export async function rechazarAdminPublicacion(
  publicacionId,
  comentario
) {
  return resolverDecisionAdmin(
    publicacionId,
    "rechazar",
    comentario
  );
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
  obtenerAdminPublicacionHistorial,
  actualizarAdminPublicacion,
  eliminarAdminPublicacion,
  aprobarAdminPublicacion,
  observarAdminPublicacion,
  rechazarAdminPublicacion,
  crearAdminArticuloDelegado,
  crearAdminLibroDelegado,
  crearAdminCapituloDelegado,
  crearAdminPonenciaDelegada,
  crearAdminPublicacionDelegada,
};