<template>
  <div class="home-with-avisos">
    <InicioView />

    <AvisosHomeOverlay
      v-if="overlayOpen"
      :key="overlayRenderKey"
      v-model="overlayOpen"
      :user="usuario"
      :version="currentVersion"
      @continue="registrarVisualizacionAvisos"
      @version-change="handleAvisosVersionChange"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import InicioView from "../inicio-view/InicioView.vue";
import AvisosHomeOverlay from "../avisos-home-overlay/AvisosHomeOverlay.vue";
import {
  getAvisosStatus,
  markAvisosAsSeen,
  shouldOpenAvisos,
} from "../../scripts/utils/avisosGate";
import { useUserStore } from "../../scripts/stores/userStore";

const POLLING_INTERVAL_MS = 30000;

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

userStore.hydrate?.();

const overlayOpen = ref(false);
const checkingGate = ref(false);
const gateResolved = ref(false);
const currentVersion = ref("");
const overlayRefreshKey = ref(0);

let statusInterval = null;

const parseStoredUser = () => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

const usuario = computed(() => userStore.user || parseStoredUser() || null);

const identityKey = computed(() => {
  const user = usuario.value;

  if (user?.id) return `id:${String(user.id)}`;
  if (user?.email) return `email:${String(user.email).toLowerCase()}`;

  return "";
});

const overlayRenderKey = computed(() => {
  return `${identityKey.value || "anon"}:${overlayRefreshKey.value}:${currentVersion.value}`;
});

const manualAvisosRequested = computed(() => {
  return String(route.query?.modal || "").trim().toLowerCase() === "avisos";
});

const manualAvisosRequestKey = computed(() => {
  if (!manualAvisosRequested.value) return "";
  return `${route.path}:${String(route.query?.ts || "")}`;
});

const revisarAvisosAutomaticos = async () => {
  if (
    !identityKey.value ||
    checkingGate.value ||
    gateResolved.value ||
    manualAvisosRequested.value
  ) {
    return;
  }

  checkingGate.value = true;

  try {
    const status = await getAvisosStatus();
    currentVersion.value = status?.version || "";
    overlayOpen.value = await shouldOpenAvisos(usuario.value, status);
  } catch (error) {
    console.error(error);
    overlayOpen.value = false;
  } finally {
    checkingGate.value = false;
    gateResolved.value = true;
  }
};

const revisarCambiosEnCaliente = async () => {
  if (!identityKey.value || checkingGate.value) return;

  try {
    const status = await getAvisosStatus();
    const nextVersion = String(status?.version || "");
    const versionChanged = nextVersion !== currentVersion.value;

    if (versionChanged) {
      currentVersion.value = nextVersion;
      overlayRefreshKey.value += 1;

      const debeAbrir = await shouldOpenAvisos(usuario.value, status);
      if (debeAbrir) {
        overlayOpen.value = true;
      }
      return;
    }

    if (!overlayOpen.value) {
      const debeAbrir = await shouldOpenAvisos(usuario.value, status);
      if (debeAbrir) {
        currentVersion.value = nextVersion;
        overlayOpen.value = true;
      }
    }
  } catch (error) {
    console.error(error);
  }
};

const abrirAvisosManual = async () => {
  if (checkingGate.value) return;

  checkingGate.value = true;

  try {
    const status = await getAvisosStatus().catch(() => null);
    currentVersion.value = status?.version || "";
    overlayRefreshKey.value += 1;
    overlayOpen.value = true;
  } finally {
    checkingGate.value = false;
  }
};

const registrarVisualizacionAvisos = () => {
  if (!usuario.value) return;
  markAvisosAsSeen(usuario.value, currentVersion.value);
};

const handleAvisosVersionChange = (nextVersion) => {
  currentVersion.value = String(nextVersion || "");
};

const limpiarQueryAvisos = async () => {
  const nextQuery = { ...route.query };
  delete nextQuery.modal;
  delete nextQuery.ts;

  try {
    await router.replace({
      path: route.path,
      query: nextQuery,
    });
  } catch {
    //
  }
};

const onVisibilityChange = () => {
  if (!document.hidden) {
    revisarCambiosEnCaliente();
  }
};

const startPolling = () => {
  if (statusInterval) return;

  statusInterval = window.setInterval(() => {
    revisarCambiosEnCaliente();
  }, POLLING_INTERVAL_MS);
};

const stopPolling = () => {
  if (!statusInterval) return;

  clearInterval(statusInterval);
  statusInterval = null;
};

watch(
  () => identityKey.value,
  async (identity) => {
    gateResolved.value = false;
    overlayRefreshKey.value = 0;

    if (!identity) {
      overlayOpen.value = false;
      currentVersion.value = "";
      return;
    }

    await revisarAvisosAutomaticos();
  },
  { immediate: true }
);

watch(
  () => manualAvisosRequestKey.value,
  (key) => {
    if (!key) return;
    abrirAvisosManual();
  },
  { immediate: true }
);

watch(
  () => overlayOpen.value,
  async (visible) => {
    if (!visible && manualAvisosRequested.value) {
      await limpiarQueryAvisos();
    }
  }
);

onMounted(() => {
  startPolling();
  document.addEventListener("visibilitychange", onVisibilityChange);
});

onUnmounted(() => {
  stopPolling();
  document.removeEventListener("visibilitychange", onVisibilityChange);
});
</script>