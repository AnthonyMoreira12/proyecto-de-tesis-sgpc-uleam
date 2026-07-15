<template>
  <AvisosHomeOverlay
    v-model="overlayVisible"
    :user="user"
    :version="currentVersion"
    :initial-manage="openInManageMode"
    @continue="handleOverlayClosed"
    @version-change="handleVersionChange"
  />
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import api from "../../scripts/api/axios";
import AvisosHomeOverlay from "../avisos-home-overlay/AvisosHomeOverlay.vue";
import {
  getAvisosStatus,
  markAvisosAsSeen,
  shouldOpenAvisos,
} from "../../scripts/utils/avisosGate";

const route = useRoute();

const AVISOS_DISABLED_PATHS = new Set([
  "/login",
  "/reset-password",
  "/restablecer-contrasena",
]);

const CHECK_INTERVAL_MS = 45_000;
const ROUTE_CHECK_DELAY_MS = 350;

const user = ref(null);
const overlayVisible = ref(false);
const openInManageMode = ref(false);
const currentVersion = ref("");

let checkTimer = null;
let routeCheckTimer = null;
let checking = false;

const getAccessToken = () => {
  return localStorage.getItem("access_token") || "";
};

const isAvisosDisabledRoute = () => {
  return AVISOS_DISABLED_PATHS.has(route.path);
};

const canCheckAvisos = () => {
  return !isAvisosDisabledRoute() && Boolean(getAccessToken());
};

const loadProfile = async () => {
  if (!getAccessToken()) {
    user.value = null;
    return null;
  }

  try {
    const { data } = await api.get("auth/profile/");

    user.value = data;

    return data;
  } catch (error) {
    user.value = null;

    if (Number(error?.response?.status || 0) !== 401) {
      console.error(
        "No fue posible cargar el perfil para los avisos.",
        error
      );
    }

    return null;
  }
};

const checkAvisos = async ({ force = false } = {}) => {
  if (checking || !canCheckAvisos()) return;
  if (overlayVisible.value && !force) return;

  checking = true;

  try {
    if (!user.value) {
      await loadProfile();
    }

    const status = await getAvisosStatus();

    const nextVersion = String(
      status?.notifyVersion ||
        status?.version ||
        ""
    );

    currentVersion.value = nextVersion;

    const mustOpen = await shouldOpenAvisos(
      user.value,
      status
    );

    if (mustOpen) {
      openInManageMode.value = false;
      overlayVisible.value = true;
    }
  } catch (error) {
    const statusCode = Number(
      error?.response?.status || 0
    );

    if (statusCode !== 401) {
      console.error(
        "No fue posible comprobar los avisos institucionales.",
        error
      );
    }
  } finally {
    checking = false;
  }
};

const openAvisosViewer = async () => {
  if (!canCheckAvisos()) return;

  if (!user.value) {
    await loadProfile();
  }

  openInManageMode.value = false;
  overlayVisible.value = true;
};

const openAvisosManager = async () => {
  if (!canCheckAvisos()) return;

  if (!user.value) {
    await loadProfile();
  }

  const isAdmin = Boolean(
    user.value?.is_staff ||
      user.value?.is_superuser ||
      user.value?.es_admin ||
      user.value?.is_admin
  );

  if (!isAdmin) return;

  openInManageMode.value = true;
  overlayVisible.value = true;
};

const handleExternalOpen = async (event) => {
  const mode = String(
    event?.detail?.mode ||
      event?.detail?.tipo ||
      ""
  )
    .trim()
    .toLowerCase();

  const shouldManage =
    mode === "manage" ||
    mode === "admin" ||
    event?.detail?.manage === true;

  if (shouldManage) {
    await openAvisosManager();
    return;
  }

  await openAvisosViewer();
};

const handleOverlayClosed = () => {
  if (currentVersion.value) {
    markAvisosAsSeen(
      user.value,
      currentVersion.value
    );
  }

  openInManageMode.value = false;
};

const handleVersionChange = (nextVersion) => {
  currentVersion.value = String(
    nextVersion || ""
  );
};

const clearRouteCheck = () => {
  if (!routeCheckTimer) return;

  window.clearTimeout(routeCheckTimer);
  routeCheckTimer = null;
};

const scheduleRouteCheck = () => {
  clearRouteCheck();

  routeCheckTimer = window.setTimeout(
    async () => {
      routeCheckTimer = null;

      if (!canCheckAvisos()) return;

      await loadProfile();
      await checkAvisos();
    },
    ROUTE_CHECK_DELAY_MS
  );
};

const startInterval = () => {
  if (checkTimer) return;

  checkTimer = window.setInterval(() => {
    checkAvisos();
  }, CHECK_INTERVAL_MS);
};

const stopInterval = () => {
  if (!checkTimer) return;

  window.clearInterval(checkTimer);
  checkTimer = null;
};

watch(
  () => route.fullPath,
  () => {
    if (isAvisosDisabledRoute()) {
      clearRouteCheck();

      overlayVisible.value = false;
      openInManageMode.value = false;

      return;
    }

    scheduleRouteCheck();
  }
);

onMounted(async () => {
  window.addEventListener(
    "sgpc:open-avisos",
    handleExternalOpen
  );

  await nextTick();

  if (canCheckAvisos()) {
    await loadProfile();
    await checkAvisos();
  }

  startInterval();
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "sgpc:open-avisos",
    handleExternalOpen
  );

  stopInterval();
  clearRouteCheck();
});
</script>