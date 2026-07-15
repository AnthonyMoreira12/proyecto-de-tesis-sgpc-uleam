// src/scripts/api/adminApi.js
import api from "./axios";

const trimText = (value) => String(value ?? "").trim();

const ensureId = (id, label = "id") => {
  const value = trimText(id);

  if (!value) {
    throw new Error(`El ${label} es obligatorio.`);
  }

  return value;
};

const buildOptionalParams = (base = {}) => {
  const params = { ...base };

  Object.keys(params).forEach((key) => {
    const value = params[key];

    if (value === "" || value == null) {
      delete params[key];
    }
  });

  return params;
};

const withQuery = (q = "", paramsExtra = {}) => {
  const query = trimText(q);

  return buildOptionalParams({
    ...paramsExtra,
    q: query || undefined,
  });
};

const getData = async (request) => {
  const { data } = await request;
  return data;
};

const postNoBody = async (url, payload = {}) => {
  return getData(api.post(url, payload));
};

const patchById = async (baseUrl, id, payload = {}) => {
  return getData(
    api.patch(
      `${baseUrl}/${ensureId(id)}/`,
      payload
    )
  );
};

const deleteById = async (baseUrl, id) => {
  return getData(
    api.delete(
      `${baseUrl}/${ensureId(id)}/`
    )
  );
};

export const adminApi = {
  /* ============================================================
     USUARIOS
     Base: /admin/usuarios/
  ============================================================ */

  /**
   * Lista o busca usuarios administrativos.
   *
   * @param {string} q Texto de búsqueda.
   * @param {object} paramsExtra Parámetros adicionales.
   * @returns {Promise<object|Array>}
   */
  usuarios: async (q = "", paramsExtra = {}) => {
    return getData(
      api.get("admin/usuarios/", {
        params: withQuery(q, paramsExtra),
      })
    );
  },

  /**
   * Recupera un usuario específico por su identificador.
   *
   * Esta función es utilizada por
   * AdminPublicacionesDelegadasView.vue cuando la ruta contiene
   * el parámetro usuarioId.
   *
   * Endpoint:
   * GET /api/admin/usuarios/:id/
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  obtenerUsuario: async (id) => {
    const usuarioId = ensureId(id, "usuarioId");

    return getData(
      api.get(`admin/usuarios/${usuarioId}/`)
    );
  },

  /**
   * Crea un usuario.
   *
   * @param {object} payload Datos del usuario.
   * @returns {Promise<object>}
   */
  crearUsuario: async (payload) => {
    return getData(
      api.post("admin/usuarios/", payload)
    );
  },

  /**
   * Actualiza parcialmente un usuario.
   *
   * @param {number|string} id Identificador del usuario.
   * @param {object} payload Campos que se actualizarán.
   * @returns {Promise<object>}
   */
  editarUsuario: async (id, payload) => {
    return patchById(
      "admin/usuarios",
      id,
      payload
    );
  },

  /**
   * Elimina un usuario.
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  eliminarUsuario: async (id) => {
    return deleteById(
      "admin/usuarios",
      id
    );
  },

  /**
   * Alterna el estado activo del usuario.
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  toggleActivo: async (id) => {
    const usuarioId = ensureId(id, "usuarioId");

    return postNoBody(
      `admin/usuarios/${usuarioId}/toggle-activo/`
    );
  },

  /**
   * Activa un usuario.
   *
   * @param {number|string} id Identificador del usuario.
   * @param {object} payload Información necesaria para activarlo.
   * @returns {Promise<object>}
   */
  activarUsuario: async (id, payload = {}) => {
    const usuarioId = ensureId(id, "usuarioId");

    return getData(
      api.post(
        `admin/usuarios/${usuarioId}/activar/`,
        payload
      )
    );
  },

  /**
   * Habilita temporalmente la edición del perfil.
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  habilitarEdicionPerfil: async (id) => {
    const usuarioId = ensureId(id, "usuarioId");

    return postNoBody(
      `admin/usuarios/${usuarioId}/habilitar-edicion-perfil/`
    );
  },

  /**
   * Extiende el período de edición del perfil.
   *
   * @param {number|string} id Identificador del usuario.
   * @param {number} horas Número de horas.
   * @returns {Promise<object>}
   */
  extenderEdicionPerfil: async (id, horas = 24) => {
    const usuarioId = ensureId(id, "usuarioId");

    return getData(
      api.post(
        `admin/usuarios/${usuarioId}/extender-edicion-perfil/`,
        {
          horas,
        }
      )
    );
  },

  /**
   * Bloquea la edición del perfil.
   *
   * @param {number|string} id Identificador del usuario.
   * @param {string} reason Motivo del bloqueo.
   * @returns {Promise<object>}
   */
  bloquearEdicionPerfil: async (id, reason = "") => {
    const usuarioId = ensureId(id, "usuarioId");
    const motivo = trimText(reason);
    const payload = motivo
      ? { reason: motivo }
      : {};

    return getData(
      api.post(
        `admin/usuarios/${usuarioId}/bloquear-edicion-perfil/`,
        payload
      )
    );
  },

  /**
   * Promueve un usuario al rol administrativo.
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  promoverAdmin: async (id) => {
    const usuarioId = ensureId(id, "usuarioId");

    return postNoBody(
      `admin/usuarios/${usuarioId}/promover-admin/`
    );
  },

  /**
   * Revoca el rol administrativo.
   *
   * @param {number|string} id Identificador del usuario.
   * @returns {Promise<object>}
   */
  revocarAdmin: async (id) => {
    const usuarioId = ensureId(id, "usuarioId");

    return postNoBody(
      `admin/usuarios/${usuarioId}/revocar-admin/`
    );
  },

  /* ============================================================
     SELECTS
  ============================================================ */

  /**
   * Obtiene las facultades disponibles para selectores.
   *
   * @returns {Promise<object|Array>}
   */
  selectsFacultades: async () => {
    return getData(
      api.get("selects/facultades/")
    );
  },

  /**
   * Obtiene las carreras pertenecientes a una facultad.
   *
   * @param {number|string} facultadId Identificador de la facultad.
   * @returns {Promise<object|Array>}
   */
  selectsCarrerasByFacultad: async (facultadId) => {
    const id = ensureId(
      facultadId,
      "facultadId"
    );

    return getData(
      api.get(`selects/carreras/${id}/`)
    );
  },

  /* ============================================================
     FACULTADES
     Base: /admin/facultades/
  ============================================================ */

  /**
   * Lista facultades administrativas.
   *
   * @param {object} params Parámetros de consulta.
   * @returns {Promise<object|Array>}
   */
  adminFacultades: async (params = {}) => {
    return getData(
      api.get("admin/facultades/", {
        params: buildOptionalParams(params),
      })
    );
  },

  /**
   * Crea una facultad.
   *
   * @param {object} payload Datos de la facultad.
   * @returns {Promise<object>}
   */
  crearFacultad: async (payload) => {
    return getData(
      api.post("admin/facultades/", payload)
    );
  },

  /**
   * Actualiza una facultad.
   *
   * @param {number|string} id Identificador de la facultad.
   * @param {object} payload Campos que se actualizarán.
   * @returns {Promise<object>}
   */
  editarFacultad: async (id, payload) => {
    return patchById(
      "admin/facultades",
      id,
      payload
    );
  },

  /**
   * Elimina una facultad.
   *
   * @param {number|string} id Identificador de la facultad.
   * @returns {Promise<object>}
   */
  eliminarFacultad: async (id) => {
    return deleteById(
      "admin/facultades",
      id
    );
  },

  /* ============================================================
     CARRERAS
     Base: /admin/carreras/
  ============================================================ */

  /**
   * Lista carreras administrativas.
   *
   * @param {object} params Parámetros de consulta.
   * @returns {Promise<object|Array>}
   */
  adminCarreras: async (params = {}) => {
    return getData(
      api.get("admin/carreras/", {
        params: buildOptionalParams(params),
      })
    );
  },

  /**
   * Crea una carrera.
   *
   * @param {object} payload Datos de la carrera.
   * @returns {Promise<object>}
   */
  crearCarrera: async (payload) => {
    return getData(
      api.post("admin/carreras/", payload)
    );
  },

  /**
   * Actualiza una carrera.
   *
   * @param {number|string} id Identificador de la carrera.
   * @param {object} payload Campos que se actualizarán.
   * @returns {Promise<object>}
   */
  editarCarrera: async (id, payload) => {
    return patchById(
      "admin/carreras",
      id,
      payload
    );
  },

  /**
   * Elimina una carrera.
   *
   * @param {number|string} id Identificador de la carrera.
   * @returns {Promise<object>}
   */
  eliminarCarrera: async (id) => {
    return deleteById(
      "admin/carreras",
      id
    );
  },
};

export default adminApi;