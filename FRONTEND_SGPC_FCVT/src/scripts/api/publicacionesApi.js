import api from "./axios";

/* =========================================================
   PUBLICACIONES API · SGPC ULEAM
   Contrato alineado con backend DRF:
   - /publicaciones/
   - /publicaciones/mias/
   - /publicaciones/<id>/
   - /publicaciones/articulos/crear/
   - /publicaciones/prevalidar/
   - /publicaciones/validar-duplicados/
   - /publicaciones/<id>/enviar-revision/
   - /publicaciones/<id>/reenviar-revision/
   - /archivos-publicacion/
   - /archivos-publicacion/bulk-upload/
   - /reportes/publicaciones/excel/
========================================================= */

export const PUBLICACION_ENDPOINTS = Object.freeze({
  publicaciones: "/publicaciones/",
  publicacionesMias: "/publicaciones/mias/",
  articuloCrear: "/publicaciones/articulos/crear/",
  prevalidar: "/publicaciones/prevalidar/",
  validarDuplicados: "/publicaciones/validar-duplicados/",
  archivos: "/archivos-publicacion/",
  archivosBulk: "/archivos-publicacion/bulk-upload/",
  excel: "/reportes/publicaciones/excel/",
});

const ENDPOINTS = PUBLICACION_ENDPOINTS;

const ARTICULO_REGIONAL = "articulo_regional";
const ARTICULO_ALTO_IMPACTO = "articulo_alto_impacto";

const CAMPOS_ARTICULO_BASE = [
  "tipo_codigo",
  "sede",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "pais",
  "ciudad",
  "origen_tipo",
  "origen_grado",
  "anio_publicacion",
  "mes_publicacion",
  "archivo_pdf",
  "nombre_articulo",
  "codigo_doi",
  "codigo_issn",
  "nombre_revista",
  "numero_revista",
  "link_revista",
  "link_publicacion",
  "autores",
];

const CAMPOS_ARTICULO_REGIONAL = [
  "base_datos_indexada",
  "base_datos_otra",
];

const CAMPOS_ARTICULO_ALTO_IMPACTO = [
  "factor_impacto",
  "cuartil",
  "sjr",
];

function isBlobLike(value) {
  const isBlob =
    typeof Blob !== "undefined" &&
    value instanceof Blob;

  const isFile =
    typeof File !== "undefined" &&
    value instanceof File;

  return isBlob || isFile;
}

function isNil(value) {
  return value === null || value === undefined;
}

function isEmptyString(value) {
  return (
    typeof value === "string" &&
    value.trim() === ""
  );
}

function normalizeId(value) {
  if (isNil(value) || value === "") {
    return "";
  }

  if (typeof value === "object") {
    return value.id ?? value.value ?? "";
  }

  return value;
}

function normalizeText(value) {
  if (isNil(value)) {
    return "";
  }

  return String(value).trim();
}

function resolveUploadedFile(value) {
  if (isBlobLike(value)) {
    return value;
  }

  if (!value || typeof value !== "object") {
    return null;
  }

  const candidates = [
    value.file,
    value.archivo,
    value.uploadedFile,
    value.rawFile,
    value.pdf,
  ];

  return (
    candidates.find(isBlobLike) ||
    null
  );
}

function normalizeAttachmentItems(rawItems) {
  if (!Array.isArray(rawItems)) {
    return [];
  }

  return rawItems
    .map((item, index) => {
      const file = resolveUploadedFile(item);

      if (!file) {
        return null;
      }

      const rawOrder = Number(
        item?.orden ?? index + 1
      );

      return {
        file,
        nombre:
          normalizeText(item?.nombre) ||
          normalizeText(item?.name) ||
          normalizeText(file.name) ||
          `Adjunto ${index + 1}`,
        orden:
          Number.isInteger(rawOrder) &&
          rawOrder > 0
            ? rawOrder
            : index + 1,
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) =>
        a.orden - b.orden
    )
    .map((item, index) => ({
      ...item,
      orden: index + 1,
    }));
}

function normalizeTipoCodigo(payload = {}) {
  const tipo = normalizeText(
    payload.tipo_codigo ||
      payload.tipoArticulo ||
      payload.tipo_articulo_codigo
  ).toLowerCase();

  if (
    tipo === ARTICULO_REGIONAL ||
    tipo === "regional"
  ) {
    return ARTICULO_REGIONAL;
  }

  if (
    tipo === ARTICULO_ALTO_IMPACTO ||
    tipo === "alto_impacto" ||
    tipo === "alto-impacto"
  ) {
    return ARTICULO_ALTO_IMPACTO;
  }

  return tipo;
}

function normalizeAutores(autores) {
  if (!Array.isArray(autores)) {
    return [];
  }

  return autores
    .map((item, index) => {
      const autorId =
        item?.autor_id ??
        item?.autor?.id ??
        item?.id ??
        item?.value;

      const parsedId = Number(autorId);
      const parsedOrder = Number(
        item?.orden || index + 1
      );

      if (
        !Number.isFinite(parsedId) ||
        parsedId <= 0
      ) {
        return null;
      }

      return {
        autor_id: parsedId,
        orden:
          Number.isFinite(parsedOrder) &&
          parsedOrder > 0
            ? parsedOrder
            : index + 1,
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) =>
        a.orden - b.orden
    )
    .map((item, index) => ({
      autor_id: item.autor_id,
      orden: index + 1,
    }));
}

function appendValue(
  formData,
  key,
  value
) {
  if (isNil(value)) {
    return;
  }

  if (isEmptyString(value)) {
    return;
  }

  if (isBlobLike(value)) {
    formData.append(key, value);
    return;
  }

  if (
    Array.isArray(value) ||
    typeof value === "object"
  ) {
    formData.append(
      key,
      JSON.stringify(value)
    );
    return;
  }

  formData.append(key, value);
}

function normalizePublicationPeriod(
  rawPayload = {}
) {
  const payload = {
    ...(rawPayload || {}),
  };

  let year =
    payload.anio_publicacion ??
    payload.anio ??
    null;

  let month =
    payload.mes_publicacion ??
    payload.mes ??
    null;

  const legacyDate = normalizeText(
    payload.fecha_publicacion
  );

  if (legacyDate) {
    const match = legacyDate.match(
      /^(\d{4})-(\d{1,2})(?:-\d{1,2})?$/
    );

    if (match) {
      if (isNil(year) || year === "") {
        year = Number(match[1]);
      }

      if (isNil(month) || month === "") {
        month = Number(match[2]);
      }
    }
  }

  if (!isNil(year) && year !== "") {
    const parsedYear = Number(year);
    payload.anio_publicacion =
      Number.isInteger(parsedYear)
        ? parsedYear
        : year;
  }

  if (!isNil(month) && month !== "") {
    const parsedMonth = Number(month);
    payload.mes_publicacion =
      Number.isInteger(parsedMonth)
        ? parsedMonth
        : month;
  }

  /*
   * fecha_publicacion, anio y mes pertenecen al contrato anterior.
   * Se aceptan como entrada de compatibilidad, pero el backend actual
   * recibe anio_publicacion y mes_publicacion.
   */
  delete payload.fecha_publicacion;
  delete payload.anio;
  delete payload.mes;

  return payload;
}

function limpiarPayloadArticulo(
  rawPayload = {}
) {
  const payload =
    normalizePublicationPeriod(
      rawPayload
    );

  const tipoCodigo =
    normalizeTipoCodigo(payload);

  payload.tipo_codigo = tipoCodigo;

  payload.sede = normalizeId(
    payload.sede
  );

  payload.facultad = normalizeId(
    payload.facultad
  );

  payload.carrera = normalizeId(
    payload.carrera
  );

  payload.proyecto = normalizeId(
    payload.proyecto
  );

  payload.area = normalizeId(
    payload.area
  );

  payload.subarea = normalizeId(
    payload.subarea
  );

  payload.pais = normalizeId(
    payload.pais
  );

  payload.ciudad = normalizeId(
    payload.ciudad
  );

  payload.archivo_pdf =
    resolveUploadedFile(
      payload.archivo_pdf
    );

  payload.autores = normalizeAutores(
    payload.autores
  );

  payload.nombre_articulo =
    normalizeText(
      payload.nombre_articulo
    );

  payload.codigo_doi = normalizeText(
    payload.codigo_doi
  );

  payload.codigo_issn = normalizeText(
    payload.codigo_issn
  );

  payload.nombre_revista =
    normalizeText(
      payload.nombre_revista
    );

  payload.link_revista = normalizeText(
    payload.link_revista
  );

  payload.link_publicacion =
    normalizeText(
      payload.link_publicacion
    );

  payload.base_datos_indexada =
    normalizeText(
      payload.base_datos_indexada
    ).toLowerCase();

  payload.base_datos_otra =
    normalizeText(
      payload.base_datos_otra
    );

  payload.factor_impacto =
    normalizeText(
      payload.factor_impacto
    ).toLowerCase();

  payload.cuartil = normalizeText(
    payload.cuartil
  ).toLowerCase();

  payload.sjr = normalizeText(
    payload.sjr
  );

  if (
    tipoCodigo ===
    ARTICULO_REGIONAL
  ) {
    payload.factor_impacto = "";
    payload.cuartil = "";
    payload.sjr = "";

    if (
      payload.base_datos_indexada !==
      "otra"
    ) {
      payload.base_datos_otra = "";
    }
  }

  if (
    tipoCodigo ===
    ARTICULO_ALTO_IMPACTO
  ) {
    payload.base_datos_indexada = "";
    payload.base_datos_otra = "";
  }

  return payload;
}

function buildArticuloFormData(
  rawPayload = {}
) {
  const payload =
    limpiarPayloadArticulo(
      rawPayload
    );

  const formData = new FormData();
  const tipoCodigo =
    payload.tipo_codigo;

  CAMPOS_ARTICULO_BASE.forEach(
    (key) => {
      appendValue(
        formData,
        key,
        payload[key]
      );
    }
  );

  if (
    tipoCodigo ===
    ARTICULO_REGIONAL
  ) {
    CAMPOS_ARTICULO_REGIONAL.forEach(
      (key) => {
        appendValue(
          formData,
          key,
          payload[key]
        );
      }
    );
  }

  if (
    tipoCodigo ===
    ARTICULO_ALTO_IMPACTO
  ) {
    CAMPOS_ARTICULO_ALTO_IMPACTO.forEach(
      (key) => {
        appendValue(
          formData,
          key,
          payload[key]
        );
      }
    );
  }

  const rawAttachments =
    Array.isArray(payload.archivos)
      ? payload.archivos
      : Array.isArray(payload.files)
        ? payload.files
        : Array.isArray(payload.adjuntos)
          ? payload.adjuntos
          : [];

  const attachments =
    normalizeAttachmentItems(
      rawAttachments
    );

  attachments.forEach(
    (item) => {
      formData.append(
        "files",
        item.file
      );
    }
  );

  if (attachments.length) {
    formData.append(
      "meta",
      JSON.stringify(
        attachments.map(
          ({ nombre, orden }) => ({
            nombre,
            orden,
          })
        )
      )
    );
  }

  return formData;
}

function buildUpdateFormData(
  rawPayload = {}
) {
  const payload =
    normalizePublicationPeriod(
      rawPayload
    );

  const formData = new FormData();

  Object.entries(payload).forEach(
    ([key, value]) => {
      if (
        key === "archivos" ||
        key === "files" ||
        key === "adjuntos"
      ) {
        return;
      }

      if (key === "autores") {
        appendValue(
          formData,
          key,
          normalizeAutores(value)
        );
        return;
      }

      if (
        key === "sede" ||
        key === "facultad" ||
        key === "carrera" ||
        key === "proyecto" ||
        key === "area" ||
        key === "subarea" ||
        key === "pais" ||
        key === "ciudad"
      ) {
        appendValue(
          formData,
          key,
          normalizeId(value)
        );
        return;
      }

      if (key === "archivo_pdf") {
        const file =
          resolveUploadedFile(value);

        if (file) {
          formData.append(
            key,
            file
          );
        }

        return;
      }

      appendValue(
        formData,
        key,
        value
      );
    }
  );

  return formData;
}

function buildQueryParams(
  params = {}
) {
  const output = {};

  Object.entries(params || {}).forEach(
    ([key, value]) => {
      if (isNil(value)) {
        return;
      }

      if (isEmptyString(value)) {
        return;
      }

      if (
        typeof value === "object" &&
        !Array.isArray(value)
      ) {
        const normalized =
          normalizeId(value);

        if (
          !isNil(normalized) &&
          normalized !== ""
        ) {
          output[key] = normalized;
        }

        return;
      }

      output[key] = value;
    }
  );

  return output;
}

/* =========================================================
   Listados
========================================================= */

export async function obtenerPublicaciones(
  params = {}
) {
  const response = await api.get(
    ENDPOINTS.publicaciones,
    {
      params: buildQueryParams(
        params
      ),
    }
  );

  return response.data;
}

export async function obtenerMisPublicaciones(
  params = {}
) {
  const response = await api.get(
    ENDPOINTS.publicacionesMias,
    {
      params: buildQueryParams(
        params
      ),
    }
  );

  return response.data;
}

export async function obtenerPublicacionDetalle(
  id
) {
  const response = await api.get(
    `${ENDPOINTS.publicaciones}${id}/`
  );

  return response.data;
}

/* =========================================================
   Creación / actualización
========================================================= */

export async function crearArticulo(
  payload = {}
) {
  const formData =
    buildArticuloFormData(payload);

  const response = await api.post(
    ENDPOINTS.articuloCrear,
    formData
  );

  return response.data;
}

export async function actualizarPublicacion(
  id,
  payload = {}
) {
  const formData =
    buildUpdateFormData(payload);

  const response = await api.patch(
    `${ENDPOINTS.publicaciones}${id}/`,
    formData
  );

  return response.data;
}

export async function reemplazarPublicacion(
  id,
  payload = {}
) {
  const formData =
    buildUpdateFormData(payload);

  const response = await api.put(
    `${ENDPOINTS.publicaciones}${id}/`,
    formData
  );

  return response.data;
}

/* =========================================================
   Prevalidación, duplicados y flujo de revisión
========================================================= */

function buildCandidateValidationPayload(
  rawPayload = {}
) {
  const payload =
    normalizePublicationPeriod(
      rawPayload
    );

  if (Array.isArray(payload.autores)) {
    payload.autores = normalizeAutores(
      payload.autores
    );
  }

  return buildUpdateFormData(payload);
}

export async function prevalidarPublicacion(
  payload = {}
) {
  const body =
    buildCandidateValidationPayload(
      payload
    );

  const response = await api.post(
    ENDPOINTS.prevalidar,
    body
  );

  return response.data;
}

export async function validarDuplicadosPublicacion(
  payload = {}
) {
  const body =
    buildCandidateValidationPayload(
      payload
    );

  const response = await api.post(
    ENDPOINTS.validarDuplicados,
    body
  );

  return response.data;
}

export function normalizarPublicacionId(value) {
  const id = Number(
    value?.publicacion_id ??
    value?.id ??
    value
  );

  if (
    !Number.isInteger(id) ||
    id <= 0
  ) {
    throw new Error(
      "El identificador de la publicación no es válido."
    );
  }

  return id;
}

export async function enviarPublicacionRevision(
  publicacionId
) {
  const id =
    normalizarPublicacionId(
      publicacionId
    );

  const response = await api.post(
    `/publicaciones/${id}/enviar-revision/`,
    {}
  );

  return response.data;
}

export async function reenviarPublicacionRevision(
  publicacionId
) {
  const id =
    normalizarPublicacionId(
      publicacionId
    );

  const response = await api.post(
    `/publicaciones/${id}/reenviar-revision/`,
    {}
  );

  return response.data;
}

/* =========================================================
   Adjuntos
========================================================= */

export async function obtenerArchivosPublicacion(
  publicacionId
) {
  const response = await api.get(
    ENDPOINTS.archivos,
    {
      params: {
        publicacion_id:
          normalizeId(
            publicacionId
          ),
      },
    }
  );

  return response.data;
}

export async function subirArchivoPublicacion(
  payload = {}
) {
  const formData = new FormData();

  appendValue(
    formData,
    "publicacion",
    normalizeId(
      payload.publicacion ||
      payload.publicacion_id
    )
  );

  appendValue(
    formData,
    "nombre",
    payload.nombre
  );

  const file = resolveUploadedFile(
    payload.archivo ||
    payload.file ||
    payload
  );

  if (file) {
    formData.append(
      "archivo",
      file
    );
  }

  appendValue(
    formData,
    "orden",
    payload.orden
  );

  const response = await api.post(
    ENDPOINTS.archivos,
    formData
  );

  return response.data;
}

export async function subirArchivosPublicacion(
  payload = {}
) {
  const publicacionId = normalizeId(
    payload.publicacion ||
    payload.publicacion_id
  );

  const rawAttachments =
    Array.isArray(payload.archivos)
      ? payload.archivos
      : Array.isArray(payload.files)
        ? payload.files
        : Array.isArray(payload.adjuntos)
          ? payload.adjuntos
          : [];

  const attachments =
    normalizeAttachmentItems(
      rawAttachments
    );

  const formData = new FormData();

  appendValue(
    formData,
    "publicacion_id",
    publicacionId
  );

  attachments.forEach(
    (item) => {
      formData.append(
        "files",
        item.file
      );
    }
  );

  formData.append(
    "meta",
    JSON.stringify(
      attachments.map(
        ({ nombre, orden }) => ({
          nombre,
          orden,
        })
      )
    )
  );

  const response = await api.post(
    ENDPOINTS.archivosBulk,
    formData
  );

  return response.data;
}

export async function eliminarArchivoPublicacion(
  id
) {
  const response = await api.delete(
    `${ENDPOINTS.archivos}${id}/`
  );

  return response.data;
}

/* =========================================================
   Reportes
========================================================= */

export async function descargarPublicacionesExcel(
  params = {}
) {
  const response = await api.get(
    ENDPOINTS.excel,
    {
      params: buildQueryParams(
        params
      ),
      responseType: "blob",
    }
  );

  return response.data;
}

/* =========================================================
   Aliases compatibles
========================================================= */

export const listarPublicaciones =
  obtenerPublicaciones;

export const listarMisPublicaciones =
  obtenerMisPublicaciones;

export const getPublicaciones =
  obtenerPublicaciones;

export const getMisPublicaciones =
  obtenerMisPublicaciones;

export const getPublicacionDetalle =
  obtenerPublicacionDetalle;

export const registrarArticulo =
  crearArticulo;

export const crearArticuloPublicacion =
  crearArticulo;

export const updatePublicacion =
  actualizarPublicacion;

export const prevalidar =
  prevalidarPublicacion;

export const validarDuplicados =
  validarDuplicadosPublicacion;

export const enviarARevision =
  enviarPublicacionRevision;

export const reenviarARevision =
  reenviarPublicacionRevision;

export default {
  obtenerPublicaciones,
  obtenerMisPublicaciones,
  obtenerPublicacionDetalle,
  crearArticulo,
  actualizarPublicacion,
  reemplazarPublicacion,
  prevalidarPublicacion,
  validarDuplicadosPublicacion,
  enviarPublicacionRevision,
  reenviarPublicacionRevision,
  normalizarPublicacionId,
  obtenerArchivosPublicacion,
  subirArchivoPublicacion,
  subirArchivosPublicacion,
  eliminarArchivoPublicacion,
  descargarPublicacionesExcel,

  listarPublicaciones,
  listarMisPublicaciones,
  getPublicaciones,
  getMisPublicaciones,
  getPublicacionDetalle,
  registrarArticulo,
  crearArticuloPublicacion,
  updatePublicacion,
  prevalidar,
  validarDuplicados,
  enviarARevision,
  reenviarARevision,
};
