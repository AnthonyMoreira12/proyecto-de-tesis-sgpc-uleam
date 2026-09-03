import api from "./axios";

const data = (response) => response?.data ?? response ?? null;

export const diagnosticarPreparacionProduccion = async () =>
  data(await api.get("admin/preparacion-produccion/diagnostico/"));

export const normalizarPreparacionProduccion = async (payload = {}) =>
  data(await api.post("admin/preparacion-produccion/normalizar/", payload));

export const verificarPreparacionProduccion = async (snapshotAntes = {}) =>
  data(
    await api.post("admin/preparacion-produccion/verificar/", {
      snapshot_antes: snapshotAntes,
    })
  );
