<template>
  <div class="admin-user-edit-route">
    <!-- =====================================================
         CARGA
    ====================================================== -->
    <Teleport
      v-if="loading && !usuario"
      to="body"
    >
      <div class="admin-user-route-overlay">
        <section
          class="admin-user-route-state"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <span
            class="admin-user-route-spinner"
            aria-hidden="true"
          ></span>

          <strong>Cargando información…</strong>
        </section>
      </div>
    </Teleport>

    <!-- =====================================================
         ERROR
    ====================================================== -->
    <Teleport
      v-else-if="errorMessage"
      to="body"
    >
      <div
        class="admin-user-route-overlay"
        @click.self="closeEdit"
      >
        <section
          class="
            admin-user-route-state
            admin-user-route-state--error
          "
          role="alert"
        >
          <div>
            <strong>No se pudo cargar el usuario.</strong>
            <span>{{ errorMessage }}</span>
          </div>

          <div class="admin-user-route-state__actions">
            <button
              class="admin-user-route-button"
              type="button"
              :disabled="loading"
              @click="loadUser"
            >
              {{ loading ? "Reintentando…" : "Reintentar" }}
            </button>

            <button
              class="
                admin-user-route-button
                admin-user-route-button--primary
              "
              type="button"
              @click="closeEdit"
            >
              Cerrar
            </button>
          </div>
        </section>
      </div>
    </Teleport>

    <!-- =====================================================
         EDICIÓN MODAL
    ====================================================== -->
    <UsuarioModal
      v-else-if="usuario"
      mode="edit"
      :usuario="usuario"
      :extension-request="extensionRequest"
      :extension-request-required="extensionRequestRequired"
      :extension-request-id="extensionRequestId"
      :extension-request-load-error="extensionRequestLoadError"
      :focus-profile-edit="extensionRequestRequired"
      :initial-extend-hours="initialExtendHours"
      @close="closeEdit"
      @done="handleDone"
      @extension-resolved="handleExtensionResolved"
      @open-extension-request="openExtensionRequestQueue"
    />
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import { adminApi } from "../../scripts/api/adminApi";
import {
  listarSolicitudesExtensionPerfil,
  obtenerSolicitudExtensionPerfil,
} from "../../scripts/api/profileExtensionApi";

import UsuarioModal from "./UsuarioModal.vue";

const route = useRoute();
const router = useRouter();

const usuario = ref(null);
const loading = ref(false);
const errorMessage = ref("");

const extensionRequest = ref(null);
const extensionRequestLoadError = ref("");
const initialExtendHours = ref(24);

let requestSerial = 0;

const userId = computed(() =>
  String(route.params.id || "").trim()
);

const extensionRequestId = computed(() => {
  const value = Number(
    route.query?.solicitud
  );

  return (
    Number.isInteger(value) &&
    value > 0
  )
    ? value
    : null;
});

const extensionRequestRequired = computed(() =>
  String(
    route.query?.accion || ""
  )
    .trim()
    .toLowerCase() ===
    "extension-perfil"
);

const normalizeHours = (value) => {
  const hours = Number(value);

  return [6, 12, 24, 48, 72].includes(
    hours
  )
    ? hours
    : 24;
};

const normalizeLoadError = (error) => {
  const status = Number(
    error?.response?.status || 0
  );

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para editar este usuario.";
  }

  if (status === 404) {
    return "El usuario solicitado no existe o ya no está disponible.";
  }

  return "No se pudo cargar la información del usuario.";
};

const loadExtensionRequest = async () => {
  extensionRequest.value = null;
  extensionRequestLoadError.value = "";

  initialExtendHours.value = normalizeHours(
    route.query?.horas
  );

  try {
    if (extensionRequestRequired.value) {
      const requestId = extensionRequestId.value;

      if (!requestId) {
        extensionRequestLoadError.value =
          "La solicitud no contiene un identificador válido.";
        return;
      }

      const request =
        await obtenerSolicitudExtensionPerfil(
          requestId
        );

      const requestUserId = Number(
        request?.usuario_id
      );

      if (
        !Number.isInteger(requestUserId) ||
        requestUserId < 1
      ) {
        throw new Error(
          "La solicitud no contiene un usuario válido."
        );
      }

      if (
        requestUserId !==
        Number(userId.value)
      ) {
        throw new Error(
          "La solicitud no corresponde a este usuario."
        );
      }

      extensionRequest.value = {
        ...request,
      };

      initialExtendHours.value =
        normalizeHours(
          request?.horas_solicitadas ??
          route.query?.horas
        );
      return;
    }

    /*
     * Incluso al abrir el editor desde la lista general verificamos si
     * existe una solicitud pendiente. Así las acciones manuales sobre el
     * permiso del perfil no pueden saltarse el flujo de revisión.
     */
    const payload =
      await listarSolicitudesExtensionPerfil({
        estado: "pendiente",
        usuario_id: Number(userId.value),
        limit: 1,
      });

    const pending = Array.isArray(payload?.results)
      ? payload.results[0] || null
      : null;

    extensionRequest.value = pending
      ? { ...pending }
      : null;

    if (pending) {
      initialExtendHours.value =
        normalizeHours(
          pending?.horas_solicitadas
        );
    }
  } catch (error) {
    extensionRequest.value = null;

    extensionRequestLoadError.value =
      String(
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        "No se pudo verificar si existe una solicitud pendiente."
      ).trim();
  }
};


const loadUser = async () => {
  const id = userId.value;

  if (!id) {
    usuario.value = null;
    errorMessage.value =
      "No se recibió un identificador de usuario válido.";
    return;
  }

  const serial = ++requestSerial;

  loading.value = true;
  errorMessage.value = "";

  try {
    const payload =
      await adminApi.obtenerUsuario(id);

    if (serial !== requestSerial) {
      return;
    }

    usuario.value = payload || null;

    if (!usuario.value) {
      errorMessage.value =
        "No se pudo cargar la información del usuario.";
      return;
    }

    await loadExtensionRequest();
  } catch (error) {
    if (serial !== requestSerial) {
      return;
    }

    console.error(
      "Error cargando edición de usuario:",
      error
    );

    usuario.value = null;
    errorMessage.value =
      normalizeLoadError(error);
  } finally {
    if (serial === requestSerial) {
      loading.value = false;
    }
  }
};

const clearExtensionContext = async () => {
  if (!extensionRequestRequired.value) {
    return;
  }

  const query = {
    ...route.query,
  };

  delete query.accion;
  delete query.solicitud;
  delete query.horas;
  delete query.usuario;

  try {
    await router.replace({
      name: "AdminUsuarioEditar",
      params: {
        id: userId.value,
      },
      query,
    });
  } catch (error) {
    console.warn(
      "No fue posible limpiar el contexto de la solicitud.",
      error
    );
  }
};


const handleExtensionResolved = async (
  payload
) => {
  const solicitud =
    payload?.solicitud ||
    extensionRequest.value ||
    null;

  if (solicitud) {
    extensionRequest.value = {
      ...solicitud,
    };
  }

  /*
   * Una solicitud resuelta ya no pertenece a la cola
   * "Solicitudes de edición". Regresamos inmediatamente al
   * listado y enviamos el ID como señal efímera para que la vista
   * la retire del estado local antes de volver a consultar el backend.
   */
  const resolvedRequestId = Number(
    solicitud?.id ||
    extensionRequestId.value
  );

  const query = {
    tab: "solicitudes",
  };

  if (
    Number.isInteger(resolvedRequestId) &&
    resolvedRequestId > 0
  ) {
    query.solicitud_resuelta =
      String(resolvedRequestId);
  }

  const decision = String(
    payload?.decision || ""
  ).trim();

  if (decision) {
    query.decision = decision;
  }

  await router.replace({
    name: "AdminUsuarios",
    query,
  });
};


const openExtensionRequestQueue = async (request) => {
  const requestId = Number(
    request?.id ||
    extensionRequest.value?.id
  );

  if (!Number.isInteger(requestId) || requestId < 1) {
    return;
  }

  await router.push({
    name: "AdminUsuarios",
    query: {
      tab: "solicitudes",
      solicitud: String(requestId),
    },
  });
};


const closeEdit = () => {
  const origin = String(
    route.query?.origen || ""
  )
    .trim()
    .toLowerCase();

  if (
    origin === "detalle" &&
    userId.value
  ) {
    router.push({
      name: "AdminUsuarioDetalle",
      params: {
        id: userId.value,
      },
      query: {
        origen: "usuarios",
      },
    });
    return;
  }

  const returnTab = String(
    route.query?.tab || ""
  ).trim();

  router.push({
    name: "AdminUsuarios",
    query:
      returnTab
        ? { tab: returnTab }
        : {},
  });
};

const handleDone = () => {
  router.push({
    name: "AdminUsuarioDetalle",
    params: {
      id: userId.value,
    },
    query: {
      actualizado: "1",
      origen: "usuarios",
    },
  });
};

watch(
  userId,
  (nextId, previousId) => {
    if (nextId === previousId) {
      return;
    }

    usuario.value = null;
    errorMessage.value = "";
    extensionRequest.value = null;
    extensionRequestLoadError.value = "";
    loadUser();
  }
);

watch(
  () => [
    route.query?.accion,
    route.query?.solicitud,
    route.query?.horas,
  ],
  () => {
    if (usuario.value) {
      void loadExtensionRequest();
    }
  }
);

onMounted(loadUser);

onBeforeUnmount(() => {
  requestSerial += 1;
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-usuario-editar.css"></style>
