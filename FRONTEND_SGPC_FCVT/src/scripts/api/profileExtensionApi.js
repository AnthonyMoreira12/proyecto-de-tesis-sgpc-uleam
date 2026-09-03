import api from "./axios";


/* ==========================================================
   CONFIGURACIÓN
========================================================== */

const PROFILE_EXTENSION_REQUESTS_URL =
  "/admin/profile-extension-requests";


/* ==========================================================
   UTILIDADES
========================================================== */

const toStr = (value) => {
  return value == null
    ? ""
    : String(value).trim();
};


const ensurePositiveInteger = (
  value,
  fieldName = "id"
) => {
  if (typeof value === "boolean") {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  const parsed = Number.parseInt(
    String(value ?? ""),
    10
  );

  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  return parsed;
};


const cleanParams = (params = {}) => {
  const cleaned = {};

  Object.entries(params).forEach(
    ([key, value]) => {
      if (value == null) {
        return;
      }

      if (typeof value === "string") {
        const normalized = value.trim();

        if (!normalized) {
          return;
        }

        cleaned[key] = normalized;
        return;
      }

      cleaned[key] = value;
    }
  );

  return cleaned;
};


const unwrap = (response) => (
  response?.data ??
  response ??
  null
);


/* ==========================================================
   SOLICITUDES DE EXTENSIÓN DE PERFIL
========================================================== */

export async function listarSolicitudesExtensionPerfil(
  params = {},
  { signal } = {}
) {
  const response = await api.get(
    `${PROFILE_EXTENSION_REQUESTS_URL}/`,
    {
      params: cleanParams(params),
      ...(signal ? { signal } : {}),
    }
  );

  return (
    unwrap(response) ||
    {
      count: 0,
      results: [],
    }
  );
}


export async function obtenerSolicitudExtensionPerfil(
  solicitudId,
  { signal } = {}
) {
  const id = ensurePositiveInteger(
    solicitudId,
    "solicitudId"
  );

  const response = await api.get(
    `${PROFILE_EXTENSION_REQUESTS_URL}/${id}/`,
    {
      ...(signal ? { signal } : {}),
    }
  );

  return unwrap(response);
}


export async function resolverSolicitudExtensionPerfil(
  solicitudId,
  payload = {},
  { signal } = {}
) {
  const id = ensurePositiveInteger(
    solicitudId,
    "solicitudId"
  );

  const response = await api.patch(
    `${PROFILE_EXTENSION_REQUESTS_URL}/${id}/`,
    {
      decision: toStr(payload?.decision),
      motivo_resolucion:
        toStr(payload?.motivo_resolucion),
      horas_aprobadas:
        payload?.horas_aprobadas == null ||
        payload?.horas_aprobadas === ""
          ? null
          : Number(payload.horas_aprobadas),
    },
    {
      ...(signal ? { signal } : {}),
    }
  );

  return unwrap(response);
}


export const profileExtensionApi = {
  listar: listarSolicitudesExtensionPerfil,
  obtener: obtenerSolicitudExtensionPerfil,
  resolver: resolverSolicitudExtensionPerfil,
};


export default profileExtensionApi;
