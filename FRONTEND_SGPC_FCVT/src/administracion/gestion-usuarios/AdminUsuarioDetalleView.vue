<template>
  <div class="admin-user-detail-route">
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
        @click.self="goBack"
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
              @click="goBack"
            >
              Cerrar
            </button>
          </div>
        </section>
      </div>
    </Teleport>

    <!-- =====================================================
         DETALLE MODAL
    ====================================================== -->
    <DetalleAutorUsuarioModal
      v-else-if="usuario"
      :usuario="usuario"
      show-edit-action
      @close="goBack"
      @edit="goEdit"
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
import DetalleAutorUsuarioModal from "./DetalleAutorUsuarioModal.vue";

const route = useRoute();
const router = useRouter();

const usuario = ref(null);
const loading = ref(false);
const errorMessage = ref("");

let requestSerial = 0;

const userId = computed(() =>
  String(route.params.id || "").trim()
);

const normalizeLoadError = (error) => {
  const status = Number(
    error?.response?.status || 0
  );

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para consultar este usuario.";
  }

  if (status === 404) {
    return "El usuario solicitado no existe o ya no está disponible.";
  }

  return "No se pudo cargar la información del usuario.";
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
    }
  } catch (error) {
    if (serial !== requestSerial) {
      return;
    }

    console.error(
      "Error cargando detalle de usuario:",
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

const goBack = () => {
  router.push({
    name: "AdminUsuarios",
  });
};

const goEdit = () => {
  if (!userId.value) {
    return;
  }

  router.push({
    name: "AdminUsuarioEditar",
    params: {
      id: userId.value,
    },
    query: {
      origen: "detalle",
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
    loadUser();
  }
);

onMounted(loadUser);

onBeforeUnmount(() => {
  requestSerial += 1;
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-usuario-detalle.css"></style>
