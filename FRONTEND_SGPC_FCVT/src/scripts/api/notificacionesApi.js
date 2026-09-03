import api from "./axios";


/* ==========================================================
   CONFIGURACIÓN
========================================================== */

const NOTIFICATIONS_BASE_URL =
  "/notificaciones";

const PROFILE_EXTENSION_REQUESTS_URL =
  "/admin/profile-extension-requests";


/* ==========================================================
   UTILIDADES
========================================================== */

const toStr = (
  value
) => (
  value == null
    ? ""
    : String(value).trim()
);


const ensurePositiveInteger = (
  value,
  fieldName = "id"
) => {
  if (
    typeof value === "boolean"
  ) {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  const parsedValue =
    Number.parseInt(
      String(value ?? ""),
      10
    );

  if (
    !Number.isInteger(
      parsedValue
    ) ||
    parsedValue < 1
  ) {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  return parsedValue;
};


const cleanParams = (
  params = {}
) => {
  const cleaned = {};

  Object.entries(
    params
  ).forEach(
    ([
      key,
      value,
    ]) => {
      if (
        value == null
      ) {
        return;
      }

      if (
        typeof value ===
        "string"
      ) {
        const normalized =
          value.trim();

        if (
          !normalized
        ) {
          return;
        }

        cleaned[key] =
          normalized;

        return;
      }

      cleaned[key] =
        value;
    }
  );

  return cleaned;
};


const unwrap = (
  response
) => (
  response?.data ??
  response ??
  null
);


/* ==========================================================
   LISTADO DE NOTIFICACIONES
========================================================== */

export async function listarNotificaciones(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${NOTIFICATIONS_BASE_URL}/`,
      {
        params:
          cleanParams(
            params
          ),

        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   DETALLE DE NOTIFICACIÓN
========================================================== */

export async function obtenerNotificacion(
  notificacionId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      notificacionId,
      "notificacionId"
    );

  const response =
    await api.get(
      `${NOTIFICATIONS_BASE_URL}/${id}/`,
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   RESUMEN
========================================================== */

export async function obtenerResumenNotificaciones(
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${NOTIFICATIONS_BASE_URL}/resumen/`,
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  const data =
    unwrap(
      response
    ) || {};

  return {
    total:
      Number(
        data?.total || 0
      ),

    no_leidas:
      Number(
        data?.no_leidas || 0
      ),
  };
}


/* ==========================================================
   MARCAR COMO LEÍDA
========================================================== */

export async function marcarNotificacionLeida(
  notificacionId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      notificacionId,
      "notificacionId"
    );

  const response =
    await api.post(
      `${NOTIFICATIONS_BASE_URL}/${id}/leer/`,
      {},
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   MARCAR TODAS COMO LEÍDAS
========================================================== */

export async function marcarTodasNotificacionesLeidas(
  {
    signal,
  } = {}
) {
  const response =
    await api.post(
      `${NOTIFICATIONS_BASE_URL}/marcar-todas-leidas/`,
      {},
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   SOLICITUDES DE EXTENSIÓN DE PERFIL
========================================================== */

export async function listarSolicitudesExtensionPerfil(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${PROFILE_EXTENSION_REQUESTS_URL}/`,
      {
        params:
          cleanParams(
            params
          ),

        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return (
    unwrap(
      response
    ) || {
      count: 0,
      results: [],
    }
  );
}


export async function obtenerSolicitudExtensionPerfil(
  solicitudId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      solicitudId,
      "solicitudId"
    );

  const response =
    await api.get(
      `${PROFILE_EXTENSION_REQUESTS_URL}/${id}/`,
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


export async function resolverSolicitudExtensionPerfil(
  solicitudId,
  payload = {},
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      solicitudId,
      "solicitudId"
    );

  const horasAprobadas =
    payload?.horas_aprobadas;

  const response =
    await api.patch(
      `${PROFILE_EXTENSION_REQUESTS_URL}/${id}/`,
      {
        decision:
          toStr(
            payload?.decision
          ),

        motivo_resolucion:
          toStr(
            payload?.motivo_resolucion
          ),

        horas_aprobadas:
          horasAprobadas == null ||
          horasAprobadas === ""
            ? null
            : Number(
                horasAprobadas
              ),
      },
      {
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   TIPOS DE NOTIFICACIÓN
========================================================== */

export const TIPOS_NOTIFICACION =
  Object.freeze({
    PUBLICACION_ENVIADA:
      "publicacion_enviada",

    PUBLICACION_OBSERVADA:
      "publicacion_observada",

    PUBLICACION_APROBADA:
      "publicacion_aprobada",

    PUBLICACION_RECHAZADA:
      "publicacion_rechazada",

    NUEVA_PUBLICACION_REVISION:
      "nueva_publicacion_revision",

    PUBLICACION_REENVIADA:
      "publicacion_reenviada",

    SOLICITUD_EXTENSION_PERFIL:
      "solicitud_extension_perfil",

    EXTENSION_PERFIL_APROBADA:
      "extension_perfil_aprobada",

    EXTENSION_PERFIL_RECHAZADA:
      "extension_perfil_rechazada",

    CAMPANIA_ACTUALIZACION:
      "campania_actualizacion",

    RECORDATORIO_ACTUALIZACION:
      "recordatorio_actualizacion",

    SOLICITUD_MODIFICACION_PUBLICACION:
      "solicitud_modificacion_publicacion",

    MODIFICACION_PUBLICACION_APROBADA:
      "modificacion_publicacion_aprobada",

    MODIFICACION_PUBLICACION_RECHAZADA:
      "modificacion_publicacion_rechazada",
  });


export function tipoNotificacionLabel(
  value
) {
  const normalized =
    toStr(
      value
    ).toLowerCase();

  const labels = {
    publicacion_enviada:
      "Publicación enviada",

    publicacion_observada:
      "Publicación observada",

    publicacion_aprobada:
      "Publicación aprobada",

    publicacion_rechazada:
      "Publicación rechazada",

    nueva_publicacion_revision:
      "Nueva publicación para revisar",

    publicacion_reenviada:
      "Publicación corregida y reenviada",

    solicitud_extension_perfil:
      "Solicitud de extensión de perfil",

    extension_perfil_aprobada:
      "Extensión de perfil aprobada",

    extension_perfil_rechazada:
      "Extensión de perfil rechazada",

    campania_actualizacion:
      "Actualización de información requerida",

    recordatorio_actualizacion:
      "Recordatorio de actualización",

    solicitud_modificacion_publicacion:
      "Solicitud de modificación de publicación",

    modificacion_publicacion_aprobada:
      "Modificación de publicación aprobada",

    modificacion_publicacion_rechazada:
      "Modificación de publicación rechazada",
  };

  return (
    labels[
      normalized
    ] ||
    "Notificación"
  );
}


/* ==========================================================
   OBJETO COMPATIBLE
========================================================== */

export const notificacionesApi = {
  listar:
    listarNotificaciones,

  obtener:
    obtenerNotificacion,

  resumen:
    obtenerResumenNotificaciones,

  marcarLeida:
    marcarNotificacionLeida,

  marcarTodasLeidas:
    marcarTodasNotificacionesLeidas,

  listarSolicitudesExtensionPerfil:
    listarSolicitudesExtensionPerfil,

  obtenerSolicitudExtensionPerfil:
    obtenerSolicitudExtensionPerfil,

  resolverSolicitudExtensionPerfil:
    resolverSolicitudExtensionPerfil,

  tipos:
    TIPOS_NOTIFICACION,

  tipoLabel:
    tipoNotificacionLabel,
};


export default notificacionesApi;