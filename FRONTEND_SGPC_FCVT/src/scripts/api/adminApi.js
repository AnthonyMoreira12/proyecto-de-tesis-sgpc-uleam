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
    if (value === "" || value == null) delete params[key];
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
  return getData(api.patch(`${baseUrl}/${ensureId(id)}/`, payload));
};

const deleteById = async (baseUrl, id) => {
  return getData(api.delete(`${baseUrl}/${ensureId(id)}/`));
};

export const adminApi = {
  /* ============================================================
     USUARIOS
     Base: /admin/usuarios/
  ============================================================ */
  usuarios: async (q = "", paramsExtra = {}) => {
    return getData(
      api.get("admin/usuarios/", {
        params: withQuery(q, paramsExtra),
      })
    );
  },

  crearUsuario: async (payload) => {
    return getData(api.post("admin/usuarios/", payload));
  },

  editarUsuario: async (id, payload) => {
    return patchById("admin/usuarios", id, payload);
  },

  eliminarUsuario: async (id) => {
    return deleteById("admin/usuarios", id);
  },

  toggleActivo: async (id) => {
    return postNoBody(`admin/usuarios/${ensureId(id)}/toggle-activo/`);
  },

  activarUsuario: async (id, payload) => {
    return getData(api.post(`admin/usuarios/${ensureId(id)}/activar/`, payload));
  },

  habilitarEdicionPerfil: async (id) => {
    return postNoBody(`admin/usuarios/${ensureId(id)}/habilitar-edicion-perfil/`);
  },

  extenderEdicionPerfil: async (id, horas = 24) => {
    return getData(
      api.post(`admin/usuarios/${ensureId(id)}/extender-edicion-perfil/`, {
        horas,
      })
    );
  },

  bloquearEdicionPerfil: async (id, reason = "") => {
    const motivo = trimText(reason);
    const payload = motivo ? { reason: motivo } : {};

    return getData(
      api.post(`admin/usuarios/${ensureId(id)}/bloquear-edicion-perfil/`, payload)
    );
  },

  promoverAdmin: async (id) => {
    return postNoBody(`admin/usuarios/${ensureId(id)}/promover-admin/`);
  },

  revocarAdmin: async (id) => {
    return postNoBody(`admin/usuarios/${ensureId(id)}/revocar-admin/`);
  },

  /* ============================================================
     SELECTS
  ============================================================ */
  selectsFacultades: async () => {
    return getData(api.get("selects/facultades/"));
  },

  selectsCarrerasByFacultad: async (facultadId) => {
    return getData(
      api.get(`selects/carreras/${ensureId(facultadId, "facultadId")}/`)
    );
  },

  /* ============================================================
     FACULTADES
     Base: /admin/facultades/
  ============================================================ */
  adminFacultades: async (params = {}) => {
    return getData(
      api.get("admin/facultades/", {
        params: buildOptionalParams(params),
      })
    );
  },

  crearFacultad: async (payload) => {
    return getData(api.post("admin/facultades/", payload));
  },

  editarFacultad: async (id, payload) => {
    return patchById("admin/facultades", id, payload);
  },

  eliminarFacultad: async (id) => {
    return deleteById("admin/facultades", id);
  },

  /* ============================================================
     CARRERAS
     Base: /admin/carreras/
  ============================================================ */
  adminCarreras: async (params = {}) => {
    return getData(
      api.get("admin/carreras/", {
        params: buildOptionalParams(params),
      })
    );
  },

  crearCarrera: async (payload) => {
    return getData(api.post("admin/carreras/", payload));
  },

  editarCarrera: async (id, payload) => {
    return patchById("admin/carreras", id, payload);
  },

  eliminarCarrera: async (id) => {
    return deleteById("admin/carreras", id);
  },
};

export default adminApi;