import api from "./axios";

const USER_BASE = "solicitudes-modificacion-publicaciones";
const ADMIN_BASE = "admin/solicitudes-modificacion-publicaciones";
const data = (response) => response?.data ?? response ?? null;

export const configuracionSolicitudModificacion = async (publicacionId) =>
  data(await api.get(`${USER_BASE}/configuracion/`, { params: { publicacion_id: publicacionId } }));

export const crearSolicitudModificacion = async (payload) =>
  data(await api.post(`${USER_BASE}/`, payload));

export const listarMisSolicitudesModificacion = async (params = {}) =>
  data(await api.get(`${USER_BASE}/`, { params }));

export const cancelarSolicitudModificacion = async (id) =>
  data(await api.post(`${USER_BASE}/${id}/cancelar/`));

export const listarSolicitudesModificacionAdmin = async (params = {}) =>
  data(await api.get(`${ADMIN_BASE}/`, { params }));

export const aprobarSolicitudModificacion = async (id, comentario = "") =>
  data(await api.post(`${ADMIN_BASE}/${id}/aprobar/`, { comentario }));

export const rechazarSolicitudModificacion = async (id, comentario) =>
  data(await api.post(`${ADMIN_BASE}/${id}/rechazar/`, { comentario }));
