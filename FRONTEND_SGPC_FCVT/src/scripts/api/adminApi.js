// src/scripts/api/adminApi.js
import api from "./axios";


/* ============================================================
   CONSTANTES
============================================================ */

const ADMIN_USERS_BASE_URL =
  "admin/usuarios";

const ADMIN_FACULTIES_BASE_URL =
  "admin/facultades";

const ADMIN_CAREERS_BASE_URL =
  "admin/carreras";


/* ============================================================
   NORMALIZACIÓN GENERAL
============================================================ */

const trimText = (value) => {
  return String(value ?? "").trim();
};


const normalizeEmail = (value) => {
  return trimText(value).toLowerCase();
};


const normalizeCedula = (value) => {
  const text = trimText(value);

  return text || null;
};


const normalizeBoolean = (
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
    trimText(value).toLowerCase();

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


const normalizePositiveInteger = (
  value,
  fallback = null
) => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return fallback;
  }

  if (typeof value === "boolean") {
    return fallback;
  }

  const parsed = Number(value);

  if (
    !Number.isInteger(parsed) ||
    parsed <= 0
  ) {
    return fallback;
  }

  return parsed;
};


/* ============================================================
   VALIDACIÓN DE IDENTIFICADORES
============================================================ */

const ensureId = (
  id,
  label = "id"
) => {
  const value = trimText(id);

  if (!value) {
    throw new Error(
      `El ${label} es obligatorio.`
    );
  }

  const numericValue = Number(value);

  if (
    !Number.isInteger(numericValue) ||
    numericValue <= 0
  ) {
    throw new Error(
      `El ${label} no es válido.`
    );
  }

  return String(numericValue);
};


/* ============================================================
   PARÁMETROS DE CONSULTA
============================================================ */

const buildOptionalParams = (
  base = {}
) => {
  const params = {
    ...base,
  };

  Object.keys(params).forEach(
    (key) => {
      const value = params[key];

      if (
        value === "" ||
        value === null ||
        value === undefined
      ) {
        delete params[key];
      }
    }
  );

  return params;
};


const withQuery = (
  q = "",
  paramsExtra = {}
) => {
  const query = trimText(q);

  return buildOptionalParams({
    ...paramsExtra,
    q: query || undefined,
  });
};


/* ============================================================
   RESPUESTAS
============================================================ */

const getData = async (request) => {
  const response = await request;

  /*
    DELETE puede responder 204 No Content. En ese caso Axios
    suele entregar una cadena vacía.
  */
  if (
    response?.status === 204 ||
    response?.data === ""
  ) {
    return null;
  }

  return response?.data;
};


/* ============================================================
   OPERACIONES HTTP GENERALES
============================================================ */

const postNoBody = async (
  url,
  payload = {}
) => {
  return getData(
    api.post(
      url,
      payload
    )
  );
};


const patchById = async (
  baseUrl,
  id,
  payload = {}
) => {
  const normalizedId = ensureId(
    id
  );

  return getData(
    api.patch(
      `${baseUrl}/${normalizedId}/`,
      payload
    )
  );
};


const deleteById = async (
  baseUrl,
  id
) => {
  const normalizedId = ensureId(
    id
  );

  return getData(
    api.delete(
      `${baseUrl}/${normalizedId}/`
    )
  );
};


/* ============================================================
   PAYLOAD DE CREACIÓN DE USUARIO
============================================================ */

const buildCreateUserPayload = (
  payload = {}
) => {
  const nombres = trimText(
    payload?.nombres
  );

  const apellidos = trimText(
    payload?.apellidos
  );

  const email = normalizeEmail(
    payload?.email
  );

  const identificacion =
    normalizeCedula(
      payload?.identificacion
    );

  if (!nombres) {
    throw new Error(
      "Los nombres son obligatorios."
    );
  }

  if (!apellidos) {
    throw new Error(
      "Los apellidos son obligatorios."
    );
  }

  if (!email) {
    throw new Error(
      "El correo electrónico es obligatorio."
    );
  }

  if (
    identificacion &&
    !/^\d{10}$/.test(
      identificacion
    )
  ) {
    throw new Error(
      "La cédula debe contener exactamente 10 dígitos numéricos cuando se proporciona."
    );
  }

  /*
    El backend controla automáticamente:

    - rol
    - auth_source
    - sede
    - carrera
    - is_active
    - is_staff
    - is_superuser
    - contraseña inicial
  */
  return {
    nombres,
    apellidos,
    email,
    identificacion,
  };
};


/* ============================================================
   PAYLOAD DE EDICIÓN DE USUARIO
============================================================ */

const buildEditUserPayload = (
  payload = {}
) => {
  const output = {};

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "nombres"
    )
  ) {
    output.nombres = trimText(
      payload.nombres
    );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "apellidos"
    )
  ) {
    output.apellidos = trimText(
      payload.apellidos
    );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "email"
    )
  ) {
    output.email = normalizeEmail(
      payload.email
    );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "identificacion"
    )
  ) {
    const identificacion =
      normalizeCedula(
        payload.identificacion
      );

    if (
      identificacion &&
      !/^\d{10}$/.test(
        identificacion
      )
    ) {
      throw new Error(
        "La cédula debe contener exactamente 10 dígitos numéricos cuando se proporciona."
      );
    }

    output.identificacion =
      identificacion;
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "is_active"
    )
  ) {
    output.is_active =
      normalizeBoolean(
        payload.is_active
      );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "is_staff"
    )
  ) {
    output.is_staff =
      normalizeBoolean(
        payload.is_staff
      );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "sede"
    )
  ) {
    output.sede =
      normalizePositiveInteger(
        payload.sede
      );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "facultad"
    )
  ) {
    output.facultad =
      normalizePositiveInteger(
        payload.facultad
      );
  }

  if (
    Object.prototype.hasOwnProperty.call(
      payload,
      "carrera"
    )
  ) {
    output.carrera =
      normalizePositiveInteger(
        payload.carrera
      );
  }

  /*
    No se envían campos sensibles que el backend no permite
    modificar desde este endpoint:

    - rol
    - auth_source
    - is_superuser
    - perfil_completo
    - es_admin
    - is_admin
    - is_staff_set
  */
  return output;
};


/* ============================================================
   API ADMINISTRATIVA
============================================================ */

export const adminApi = {
  /* ==========================================================
     USUARIOS
     Base: /api/admin/usuarios/
  ========================================================== */

  /**
   * Lista o busca usuarios.
   *
   * paramsExtra puede incluir:
   *
   * - scope
   * - incompletos
   */
  usuarios: async (
    q = "",
    paramsExtra = {}
  ) => {
    return getData(
      api.get(
        `${ADMIN_USERS_BASE_URL}/`,
        {
          params: withQuery(
            q,
            paramsExtra
          ),
        }
      )
    );
  },


  /**
   * Recupera el detalle de un usuario.
   */
  obtenerUsuario: async (id) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    return getData(
      api.get(
        `${ADMIN_USERS_BASE_URL}/${usuarioId}/`
      )
    );
  },


  /**
   * Crea una cuenta externa pendiente.
   *
   * El backend la crea:
   *
   * - inactiva;
   * - sin contraseña utilizable;
   * - sin Sede ni Carrera institucional;
   * - con identificación opcional;
   * - sin permisos administrativos.
   */
  crearUsuario: async (
    payload = {}
  ) => {
    const normalizedPayload =
      buildCreateUserPayload(
        payload
      );

    return getData(
      api.post(
        `${ADMIN_USERS_BASE_URL}/`,
        normalizedPayload
      )
    );
  },


  /**
   * Actualiza parcialmente un usuario.
   */
  editarUsuario: async (
    id,
    payload = {}
  ) => {
    const normalizedPayload =
      buildEditUserPayload(
        payload
      );

    return patchById(
      ADMIN_USERS_BASE_URL,
      id,
      normalizedPayload
    );
  },


  /**
   * Elimina un usuario.
   */
  eliminarUsuario: async (id) => {
    return deleteById(
      ADMIN_USERS_BASE_URL,
      id
    );
  },


  /**
   * Alterna el estado activo.
   *
   * Una cuenta externa pendiente sin contraseña debe utilizar
   * activarUsuario() y no esta operación.
   */
  toggleActivo: async (id) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    return postNoBody(
      `${ADMIN_USERS_BASE_URL}/${usuarioId}/toggle-activo/`
    );
  },


  /**
   * Activa una cuenta externa pendiente.
   */
  activarUsuario: async (
    id,
    payload = {}
  ) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    const email = normalizeEmail(
      payload?.email
    );

    /*
      No se usa trim() sobre la contraseña porque modificaría
      el valor escrito por el administrador.
    */
    const password = String(
      payload?.password ?? ""
    );

    if (!email) {
      throw new Error(
        "El correo electrónico es obligatorio."
      );
    }

    if (
      password.length < 8 ||
      password.length > 128 ||
      password.trim().length === 0
    ) {
      throw new Error(
        "La contraseña debe contener entre 8 y 128 caracteres."
      );
    }

    return getData(
      api.post(
        `${ADMIN_USERS_BASE_URL}/${usuarioId}/activar/`,
        {
          email,
          password,
        }
      )
    );
  },


  /**
   * Habilita temporalmente la edición del perfil.
   */
  habilitarEdicionPerfil: async (
    id,
    {
      horas = 48,
      intentos = 3,
    } = {}
  ) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    const normalizedHours =
      normalizePositiveInteger(
        horas,
        48
      );

    const normalizedAttempts =
      normalizePositiveInteger(
        intentos,
        3
      );

    return getData(
      api.post(
        `${ADMIN_USERS_BASE_URL}/${usuarioId}/habilitar-edicion-perfil/`,
        {
          horas: normalizedHours,
          intentos: normalizedAttempts,
        }
      )
    );
  },


  /**
   * Extiende el periodo de edición.
   */
  extenderEdicionPerfil: async (
    id,
    horas = 24
  ) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    const normalizedHours =
      normalizePositiveInteger(
        horas
      );

    if (!normalizedHours) {
      throw new Error(
        "El número de horas debe ser mayor que cero."
      );
    }

    return getData(
      api.post(
        `${ADMIN_USERS_BASE_URL}/${usuarioId}/extender-edicion-perfil/`,
        {
          horas: normalizedHours,
        }
      )
    );
  },


  /**
   * Bloquea la edición del perfil.
   */
  bloquearEdicionPerfil: async (
    id,
    reason = ""
  ) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    const motivo = trimText(
      reason
    );

    if (motivo.length > 255) {
      throw new Error(
        "El motivo no puede superar los 255 caracteres."
      );
    }

    return getData(
      api.post(
        `${ADMIN_USERS_BASE_URL}/${usuarioId}/bloquear-edicion-perfil/`,
        motivo
          ? {
              reason: motivo,
            }
          : {}
      )
    );
  },


  /**
   * Promueve un usuario como administrador.
   */
  promoverAdmin: async (id) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    return postNoBody(
      `${ADMIN_USERS_BASE_URL}/${usuarioId}/promover-admin/`
    );
  },


  /**
   * Revoca los permisos administrativos.
   */
  revocarAdmin: async (id) => {
    const usuarioId = ensureId(
      id,
      "usuarioId"
    );

    return postNoBody(
      `${ADMIN_USERS_BASE_URL}/${usuarioId}/revocar-admin/`
    );
  },


  /**
   * Busca usuarios institucionales Microsoft.
   */
  buscarMicrosoft: async (
    q = ""
  ) => {
    const query = trimText(q);

    return getData(
      api.get(
        `${ADMIN_USERS_BASE_URL}/buscar-microsoft/`,
        {
          params: buildOptionalParams({
            q: query || undefined,
          }),
        }
      )
    );
  },


  /* ==========================================================
     SELECTORES
  ========================================================== */

  /**
   * Obtiene las Sedes institucionales activas.
   */
  selectsSedes: async () => {
    return getData(
      api.get(
        "selects/sedes/"
      )
    );
  },


  /**
   * Obtiene Carreras filtradas por Sede.
   */
  selectsCarrerasBySede: async (
    sedeId
  ) => {
    const id = ensureId(
      sedeId,
      "sedeId"
    );

    return getData(
      api.get(
        `selects/carreras/sede/${id}/`
      )
    );
  },


  /**
   * Selector flexible de Carreras. El backend admite
   * sede_id, facultad_id o ambos filtros simultáneamente.
   */
  selectsCarreras: async ({
    sedeId = null,
    facultadId = null,
  } = {}) => {
    return getData(
      api.get(
        "selects/carreras/",
        {
          params: buildOptionalParams({
            sede_id:
              normalizePositiveInteger(
                sedeId
              ) || undefined,
            facultad_id:
              normalizePositiveInteger(
                facultadId
              ) || undefined,
          }),
        }
      )
    );
  },


  /**
   * Obtiene las Facultades disponibles.
   */
  selectsFacultades: async () => {
    return getData(
      api.get(
        "selects/facultades/"
      )
    );
  },


  /**
   * Obtiene las Carreras de una Facultad.
   */
  selectsCarrerasByFacultad: async (
    facultadId
  ) => {
    const id = ensureId(
      facultadId,
      "facultadId"
    );

    return getData(
      api.get(
        `selects/carreras/${id}/`
      )
    );
  },


  /* ==========================================================
     FACULTADES
     Base: /api/admin/facultades/
  ========================================================== */

  adminFacultades: async (
    params = {}
  ) => {
    return getData(
      api.get(
        `${ADMIN_FACULTIES_BASE_URL}/`,
        {
          params:
            buildOptionalParams(
              params
            ),
        }
      )
    );
  },


  crearFacultad: async (
    payload = {}
  ) => {
    return getData(
      api.post(
        `${ADMIN_FACULTIES_BASE_URL}/`,
        payload
      )
    );
  },


  editarFacultad: async (
    id,
    payload = {}
  ) => {
    return patchById(
      ADMIN_FACULTIES_BASE_URL,
      id,
      payload
    );
  },


  eliminarFacultad: async (id) => {
    return deleteById(
      ADMIN_FACULTIES_BASE_URL,
      id
    );
  },


  /* ==========================================================
     CARRERAS
     Base: /api/admin/carreras/
  ========================================================== */

  adminCarreras: async (
    params = {}
  ) => {
    return getData(
      api.get(
        `${ADMIN_CAREERS_BASE_URL}/`,
        {
          params:
            buildOptionalParams(
              params
            ),
        }
      )
    );
  },


  crearCarrera: async (
    payload = {}
  ) => {
    return getData(
      api.post(
        `${ADMIN_CAREERS_BASE_URL}/`,
        payload
      )
    );
  },


  editarCarrera: async (
    id,
    payload = {}
  ) => {
    return patchById(
      ADMIN_CAREERS_BASE_URL,
      id,
      payload
    );
  },


  eliminarCarrera: async (id) => {
    return deleteById(
      ADMIN_CAREERS_BASE_URL,
      id
    );
  },
};


export default adminApi;
