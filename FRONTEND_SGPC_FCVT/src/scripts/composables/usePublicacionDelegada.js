import { computed, ref } from "vue";

import {
  actualizarAdminPublicacion,
  aprobarAdminPublicacion,
  crearAdminPublicacionDelegada,
  eliminarAdminPublicacion,
  listarAdminPublicaciones,
  observarAdminPublicacion,
  obtenerAdminPublicacion,
  obtenerAdminPublicacionHistorial,
  rechazarAdminPublicacion,
} from "../api/publicacionesAdminApi";

import {
  enviarPublicacionRevision,
  reenviarPublicacionRevision,
} from "../api/publicacionesApi";

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

    sede_id:
      Number(
        usuario.sede_id ||
        usuario.sede?.id ||
        usuario.sede ||
        0
      ) || null,

    sede_nombre: toText(
      usuario.sede_nombre ||
      usuario.sede?.nombre ||
      (typeof usuario.sede === "string"
        ? usuario.sede
        : "")
    ),

    carrera_id:
      Number(
        usuario.carrera_id ||
        usuario.carrera?.id ||
        usuario.carrera ||
        0
      ) || null,

    carrera_nombre: toText(
      usuario.carrera_nombre ||
      usuario.carrera?.nombre ||
      (typeof usuario.carrera === "string"
        ? usuario.carrera
        : "")
    ),

    facultad_id:
      Number(
        usuario.facultad_id ||
        usuario.facultad?.id ||
        usuario.facultad ||
        0
      ) || null,

    facultad_nombre: toText(
      usuario.facultad_nombre ||
      usuario.facultad?.nombre ||
      (typeof usuario.facultad === "string"
        ? usuario.facultad
        : "")
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

function extraerPublicacionRespuesta(response) {
  return (
    response?.publicacion ||
    response?.data?.publicacion ||
    (response?.id ? response : null)
  );
}

function actualizarPublicacionEnLista(
  list,
  publicacion
) {
  if (!publicacion?.id) {
    return Array.isArray(list)
      ? list
      : [];
  }

  const current = Array.isArray(list)
    ? list
    : [];

  return current.map((item) =>
    Number(item?.id) ===
    Number(publicacion.id)
      ? {
          ...item,
          ...publicacion,
        }
      : item
  );
}

export function usePublicacionDelegada() {
  const usuarioObjetivo = ref(null);

  const items = ref([]);
  const total = ref(0);
  const next = ref(null);
  const previous = ref(null);
  const detalle = ref(null);
  const historial = ref([]);

  const loading = ref(false);
  const loadingDetalle = ref(false);
  const loadingHistorial = ref(false);
  const saving = ref(false);
  const deleting = ref(false);
  const workflowLoading = ref(false);

  const error = ref("");
  const validationErrors = ref(null);

  const filtros = ref({
    q: "",
    tipo: "",
    estado: "",
    sede_id: "",
    facultad_id: "",
    carrera_id: "",
    anio: "",
    mes: "",
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
    const nextUser =
      normalizarUsuarioObjetivo(
        usuario
      );

    const changed =
      Number(usuarioObjetivo.value?.id || 0) !==
      Number(nextUser?.id || 0);

    usuarioObjetivo.value = nextUser;

    if (changed) {
      detalle.value = null;
      historial.value = [];
      resetListado();
    }
  }

  function clearUsuarioObjetivo() {
    usuarioObjetivo.value = null;
    detalle.value = null;
    historial.value = [];
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
      estado: "",
      sede_id: "",
      facultad_id: "",
      carrera_id: "",
      anio: "",
      mes: "",
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

      if (
        Number(detalle.value?.id) !==
        Number(response?.id)
      ) {
        historial.value = [];
      }

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

  async function cargarHistorial(
    publicacionId
  ) {
    limpiarEstados();
    loadingHistorial.value = true;

    try {
      const response =
        await obtenerAdminPublicacionHistorial(
          publicacionId
        );

      historial.value = Array.isArray(
        response?.items
      )
        ? response.items
        : [];

      return response;
    } catch (err) {
      historial.value = [];

      error.value = normalizarError(
        err,
        "No se pudo cargar el historial de la publicación."
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      loadingHistorial.value = false;
    }
  }

  function aplicarRespuestaWorkflow(
    publicacionId,
    response
  ) {
    const publicacion =
      extraerPublicacionRespuesta(
        response
      );

    if (publicacion?.id) {
      items.value =
        actualizarPublicacionEnLista(
          items.value,
          publicacion
        );

      if (
        Number(detalle.value?.id) ===
        Number(publicacion.id)
      ) {
        detalle.value = {
          ...detalle.value,
          ...publicacion,
        };
      }
    } else {
      const nextState = toText(
        response?.estado
      );

      if (nextState) {
        items.value = items.value.map(
          (item) =>
            Number(item?.id) ===
            Number(publicacionId)
              ? {
                  ...item,
                  estado: nextState,
                  estado_label:
                    response?.estado_label ||
                    item?.estado_label,
                }
              : item
        );

        if (
          Number(detalle.value?.id) ===
          Number(publicacionId)
        ) {
          detalle.value = {
            ...detalle.value,
            estado: nextState,
            estado_label:
              response?.estado_label ||
              detalle.value?.estado_label,
          };
        }
      }
    }

    return publicacion;
  }

  async function ejecutarWorkflow(
    publicacionId,
    operation,
    fallback
  ) {
    limpiarEstados();
    workflowLoading.value = true;

    try {
      const response =
        await operation();

      aplicarRespuestaWorkflow(
        publicacionId,
        response
      );

      if (
        Number(detalle.value?.id) ===
        Number(publicacionId)
      ) {
        try {
          await cargarHistorial(
            publicacionId
          );
        } catch (historyError) {
          console.warn(
            "El estado cambió, pero no se pudo refrescar el historial.",
            historyError
          );
        }
      }

      return response;
    } catch (err) {
      error.value = normalizarError(
        err,
        fallback
      );

      validationErrors.value =
        extraerErroresValidacion(err);

      throw err;
    } finally {
      workflowLoading.value = false;
    }
  }

  async function enviarARevision(
    publicacionId
  ) {
    return ejecutarWorkflow(
      publicacionId,
      () => enviarPublicacionRevision(
        publicacionId
      ),
      "No se pudo enviar la publicación a revisión."
    );
  }

  async function reenviarARevision(
    publicacionId
  ) {
    return ejecutarWorkflow(
      publicacionId,
      () => reenviarPublicacionRevision(
        publicacionId
      ),
      "No se pudo reenviar la publicación a revisión."
    );
  }

  async function aprobarPublicacion(
    publicacionId,
    comentario = ""
  ) {
    return ejecutarWorkflow(
      publicacionId,
      () => aprobarAdminPublicacion(
        publicacionId,
        comentario
      ),
      "No se pudo aprobar la publicación."
    );
  }

  async function observarPublicacion(
    publicacionId,
    comentario
  ) {
    return ejecutarWorkflow(
      publicacionId,
      () => observarAdminPublicacion(
        publicacionId,
        comentario
      ),
      "No se pudo observar la publicación."
    );
  }

  async function rechazarPublicacion(
    publicacionId,
    comentario
  ) {
    return ejecutarWorkflow(
      publicacionId,
      () => rechazarAdminPublicacion(
        publicacionId,
        comentario
      ),
      "No se pudo rechazar la publicación."
    );
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
        historial.value = [];
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
    historial,

    filtros,
    loading,
    loadingDetalle,
    loadingHistorial,
    saving,
    deleting,
    workflowLoading,
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
    cargarHistorial,
    enviarARevision,
    reenviarARevision,
    aprobarPublicacion,
    observarPublicacion,
    rechazarPublicacion,
    crearPublicacionDelegada,
    actualizarPublicacion,
    eliminarPublicacion,
  };
}
