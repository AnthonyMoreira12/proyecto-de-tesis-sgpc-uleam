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
]);

const CHECK_INTERVAL_MS = 45000;

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
  if (isAvisosDisabledRoute()) return false;
  if (!getAccessToken()) return false;
  return true;
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
    return null;
  }
};

const checkAvisos = async ({ force = false } = {}) => {
  if (checking) return;
  if (overlayVisible.value && !force) return;
  if (!canCheckAvisos()) return;

  checking = true;

  try {
    if (!user.value) {
      await loadProfile();
    }

    const status = await getAvisosStatus();
    const nextVersion = status.notifyVersion || status.version || "";

    currentVersion.value = nextVersion;

    const mustOpen = await shouldOpenAvisos(user.value, status);

    if (mustOpen) {
      openInManageMode.value = false;
      overlayVisible.value = true;
    }
  } catch (error) {
    const statusCode = Number(error?.response?.status || 0);

    if (statusCode !== 401) {
      console.error(error);
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
  const mode = event?.detail?.mode || event?.detail?.tipo || "";

  if (mode === "manage" || mode === "admin" || event?.detail?.manage === true) {
    await openAvisosManager();
    return;
  }

  await openAvisosViewer();
};

const handleOverlayClosed = () => {
  markAvisosAsSeen(user.value, currentVersion.value);
  openInManageMode.value = false;
};

const handleVersionChange = (nextVersion) => {
  currentVersion.value = String(nextVersion || "");
};

const scheduleRouteCheck = () => {
  if (routeCheckTimer) {
    window.clearTimeout(routeCheckTimer);
    routeCheckTimer = null;
  }

  routeCheckTimer = window.setTimeout(async () => {
    if (!canCheckAvisos()) return;

    await loadProfile();
    await checkAvisos();
  }, 350);
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
      overlayVisible.value = false;
      openInManageMode.value = false;
      return;
    }

    scheduleRouteCheck();
  }
);

onMounted(async () => {
  window.addEventListener("sgpc:open-avisos", handleExternalOpen);

  await nextTick();

  if (canCheckAvisos()) {
    await loadProfile();
    await checkAvisos();
  }

  startInterval();
});

onBeforeUnmount(() => {
  window.removeEventListener("sgpc:open-avisos", handleExternalOpen);

  stopInterval();

  if (routeCheckTimer) {
    window.clearTimeout(routeCheckTimer);
    routeCheckTimer = null;
  }
});
</script>