import api from "./axios";
const data = (response) => response?.data ?? response ?? null;

export const diagnosticoIntegridadDocumental = async () =>
  data(await api.get("admin/integridad-documental/diagnostico/"));

export const ejecutarBackfillIntegridadDocumental = async (payload = {}) =>
  data(await api.post("admin/integridad-documental/backfill/", payload));
