import { computed, ref } from "vue";

import {
  actualizarAdminPublicacion,
  crearAdminPublicacionDelegada,
  eliminarAdminPublicacion,
  listarAdminPublicaciones,
  obtenerAdminPublicacion,
} from "../api/publicacionesAdminApi";

/**
 * Composable para gestionar publicaciones administrativas
 * ligadas a un usuario/autor objetivo.
 *
 * Flujo esperado:
 * - setUsuarioObjetivo(...)
 * - cargarPublicaciones()
 * - crear / actualizar / eliminar
 */

function toText(value) {
  return String(value ?? "").trim();
}

function firstErrorMessage(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return toText(value);
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message =
        firstErrorMessage(item);

      if (message) {
        return message;
      }
    }

    return "";
  }

  if (typeof value === "object") {
    const preferredKeys = [
      "detail",
      "message",
      "non_field_errors",
      "usuario_objetivo_id",
      "autor_objetivo_id",
    ];

    for (const key of preferredKeys) {
      if (
        Object.prototype.hasOwnProperty.call(
          value,
          key
        )
      ) {
        const message =
          firstErrorMessage(value[key]);

        if (message) {
          return message;
        }
      }
    }

    for (const child of Object.values(value)) {
      const message =
        firstErrorMessage(child);

      if (message) {
        return message;
      }
    }
  }

  return "";
}

function normalizarError(
  error,
  fallback = "Ocurrió un error inesperado."
) {
  const payload =
    error?.response?.data ??
    error?.data ??
    null;

  return (
    firstErrorMessage(payload) ||
    toText(error?.message) ||
    fallback
  );
}

function extraerErroresValidacion(
  error
) {
  const data =
    error?.response?.data;

  if (
    !data ||
    typeof data !== "object"
  ) {
    return null;
  }

  return data;
}

function normalizeBoolean(value) {
  if (typeof value === "boolean") {
    return value;
  }

  const normalized =
    toText(value).toLowerCase();

  if (
    [
      "1",
      "true",
      "yes",
      "si",
      "sí",
    ].includes(normalized)
  ) {
    return true;
  }

  if (
    [
      "0",
      "false",
      "no",
    ].includes(normalized)
  ) {
    return false;
  }

  return null;
}

function normalizarUsuarioObjetivo(
  usuario = null
) {
  if (!usuario) {
    return null;
  }

  const isActive = normalizeBoolean(
    usuario.is_active ??
    usuario.usuario_activo
  );

  const isPending = normalizeBoolean(
    usuario.es_pendiente
  );

  return {
    id:
      Number(
        usuario.id ||
        usuario.usuario_id ||
        0
      ) || null,

    autor_id:
      Number(
        usuario.autor_id ||
        usuario.autor?.id ||
        usuario.autor_objetivo_id ||
        0
      ) || null,

    email: toText(
      usuario.email ||
      usuario.usuario_email
    ),

    nombres: toText(
      usuario.nombres
    ),

    apellidos: toText(
      usuario.apellidos
    ),

    nombre:
      toText(usuario.nombre) ||
      toText(usuario.autor_nombre) ||
      `${toText(usuario.nombres)} ${toText(
        usuario.apellidos
      )}`.trim(),

    is_active: isActive,
    es_pendiente: isPending,
    es_institucional:
      normalizeBoolean(
        usuario.es_institucional
      ),
    es_externo:
      normalizeBoolean(
        usuario.es_externo
      ),
  };
}

function mergeCreatedPublication(
  list,
  response
) {
  const publication =
    response?.publicacion ||
    response?.data?.publicacion ||
    null;

  const publicationId = Number(
    publication?.id ||
    publication?.publicacion_id ||
    0
  );

  if (!publicationId) {
    return {
      items: list,
      inserted: false,
      publication: null,
    };
  }

  const current = Array.isArray(list)
    ? list
    : [];

  return {
    items: [
      publication,
      ...current.filter(
        (item) =>
          Number(item?.id) !==
          publicationId
      ),
    ],
    inserted: !current.some(
      (item) =>
        Number(item?.id) ===
        publicationId
    ),
    publication,
  };
}

export function usePublicacionDelegada() {
  const usuarioObjetivo = ref(null);

  const items = ref([]);
  const total = ref(0);
  const next = ref(null);
  const previous = ref(null);
  const detalle = ref(null);

  const loading = ref(false);
  const loadingDetalle = ref(false);
  const saving = ref(false);
  const deleting = ref(false);

  const error = ref("");
  const validationErrors = ref(null);

  const filtros = ref({
    q: "",
    tipo: "",
    facultad_id: "",
    carrera_id: "",
    anio: "",
    solo_delegadas: "",
    solo_con_pdf: "",
    solo_con_adjuntos: "",
    ordering: "updated_desc",
    page: 1,
    page_size: 20,
  });

  const hasUsuarioObjetivo = computed(
    () => Boolean(
      usuarioObjetivo.value?.id
    )
  );

  const usuarioObjetivoLabel = computed(
    () => {
      const user =
        usuarioObjetivo.value;

      if (!user) {
        return "Sin usuario objetivo";
      }

      return (
        user.nombre ||
        user.email ||
        (
          user.id
            ? `Usuario #${user.id}`
            : "Usuario objetivo"
        )
      );
    }
  );

  function limpiarEstados() {
    error.value = "";
    validationErrors.value = null;
  }

  function resetListado() {
    items.value = [];
    total.value = 0;
    next.value = null;
    previous.value = null;
  }

  function setUsuarioObjetivo(
    usuario
  ) {
    usuarioObjetivo.value =
      normalizarUsuarioObjetivo(
        usuario
      );
  }

  function clearUsuarioObjetivo() {
    usuarioObjetivo.value = null;
    detalle.value = null;
    resetListado();
  }

  function setFiltros(
    parciales = {}
  ) {
    filtros.value = {
      ...filtros.value,
      ...parciales,
    };
  }

  function limpiarFiltros() {
    filtros.value = {
      q: "",
      tipo: "",
      facultad_id: "",
      carrera_id: "",
      anio: "",
      solo_delegadas: "",
      solo_con_pdf: "",
      solo_con_adjuntos: "",
      ordering: "updated_desc",
      page: 1,
      page_size: 20,
    };
  }

  function buildTargetFilters(
    extra = {}
  ) {
    const target =
      usuarioObjetivo.value || {};

    return {
      ...filtros.value,
      ...extra,
      usuario_objetivo_id:
        target.id || undefined,
      autor_objetivo_id:
        target.autor_id || undefined,
    };
  }

  function applyListResponse(response) {
    items.value = Array.isArray(
      response?.results
    )
      ? response.results
      : [];

    total.value = Number(
      response?.count || 0
    );

    next.value =
      response?.next || null;

    previous.value =
      response?.previous || null;
  }

  async function cargarPublicaciones(
    extraFilters = {}
  ) {
    limpiarEstados();

    if (!hasUsuarioObjetivo.value) {
      resetListado();

      error.value =
        "Debe seleccionar un usuario objetivo.";

      return {
        count: 0,
        results: [],
      };
    }

    loading.value = true;

    try {
      const response =
        await listarAdminPublicaciones(
          buildTargetFilters(
            extraFilters
          )
        );

      applyListResponse(response);

      return response;
    } catch (err) {
      resetListado();

      error.value = normalizarError(
        err,
        "No se pudieron cargar las publicaciones administrativas."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function cargarDetalle(
    publicacionId
  ) {
    limpiarEstados();
    loadingDetalle.value = true;

    try {
      const response =
        await obtenerAdminPublicacion(
          publicacionId
        );

      detalle.value = response;

      return response;
    } catch (err) {
      detalle.value = null;

      error.value = normalizarError(
        err,
        "No se pudo cargar el detalle de la publicación."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      loadingDetalle.value = false;
    }
  }

  function buildDelegatedPayload(
    payload = {}
  ) {
    const target =
      usuarioObjetivo.value || {};

    return {
      ...payload,

      usuario_objetivo_id:
        payload.usuario_objetivo_id ||
        payload.usuario_id ||
        target.id ||
        undefined,

      autor_objetivo_id:
        payload.autor_objetivo_id ||
        payload.autor_id ||
        target.autor_id ||
        undefined,
    };
  }

  async function crearPublicacionDelegada(
    tipo,
    payload = {}
  ) {
    limpiarEstados();

    if (!hasUsuarioObjetivo.value) {
      const message =
        "Debe seleccionar un usuario objetivo antes de crear.";

      error.value = message;

      throw new Error(message);
    }

    saving.value = true;

    try {
      const response =
        await crearAdminPublicacionDelegada(
          tipo,
          buildDelegatedPayload(
            payload
          )
        );

      const merged =
        mergeCreatedPublication(
          items.value,
          response
        );

      items.value = merged.items;

      if (merged.inserted) {
        total.value =
          Number(total.value || 0) + 1;
      }

      if (merged.publication) {
        detalle.value =
          merged.publication;
      }

      try {
        const refreshed =
          await listarAdminPublicaciones(
            buildTargetFilters()
          );

        applyListResponse(refreshed);
      } catch (refreshError) {
        /*
         * La creación ya fue confirmada por el backend.
         * Un fallo al refrescar el listado no debe convertir
         * una operación exitosa en un error de creación.
         */
        console.warn(
          "La publicación fue creada, pero no se pudo actualizar el listado.",
          refreshError
        );
      }

      return response;
    } catch (err) {
      error.value = normalizarError(
        err,
        "No se pudo crear la publicación delegada."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      saving.value = false;
    }
  }

  async function actualizarPublicacion(
    publicacionId,
    payload = {},
    options = {}
  ) {
    limpiarEstados();
    saving.value = true;

    try {
      const response =
        await actualizarAdminPublicacion(
          publicacionId,
          payload,
          options
        );

      const index =
        items.value.findIndex(
          (item) =>
            Number(item.id) ===
            Number(publicacionId)
        );

      if (index >= 0) {
        items.value[index] = {
          ...items.value[index],
          ...response,
        };
      }

      if (
        Number(detalle.value?.id) ===
        Number(publicacionId)
      ) {
        detalle.value = response;
      }

      return response;
    } catch (err) {
      error.value = normalizarError(
        err,
        "No se pudo actualizar la publicación."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      saving.value = false;
    }
  }

  async function eliminarPublicacion(
    publicacionId
  ) {
    limpiarEstados();
    deleting.value = true;

    try {
      const response =
        await eliminarAdminPublicacion(
          publicacionId
        );

      items.value = items.value.filter(
        (item) =>
          Number(item.id) !==
          Number(publicacionId)
      );

      total.value = Math.max(
        0,
        Number(total.value || 0) - 1
      );

      if (
        Number(detalle.value?.id) ===
        Number(publicacionId)
      ) {
        detalle.value = null;
      }

      return response;
    } catch (err) {
      error.value = normalizarError(
        err,
        "No se pudo eliminar la publicación."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      deleting.value = false;
    }
  }

  return {
    usuarioObjetivo,
    usuarioObjetivoLabel,
    hasUsuarioObjetivo,

    items,
    total,
    next,
    previous,
    detalle,

    filtros,
    loading,
    loadingDetalle,
    saving,
    deleting,
    error,
    validationErrors,

    setUsuarioObjetivo,
    clearUsuarioObjetivo,
    setFiltros,
    limpiarFiltros,
    limpiarEstados,
    resetListado,

    cargarPublicaciones,
    cargarDetalle,
    crearPublicacionDelegada,
    actualizarPublicacion,
    eliminarPublicacion,
  };
}
