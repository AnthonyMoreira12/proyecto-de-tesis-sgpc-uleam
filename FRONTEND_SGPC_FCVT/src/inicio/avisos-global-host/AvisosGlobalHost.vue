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
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
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
const lastConfirmedVersion = ref("");

let checkTimer = null;
let routeCheckTimer = null;
let checking = false;
let closingOverlay = false;

const getAccessToken = () => {
  return localStorage.getItem("access_token") || "";
};

const hasUserIdentity = (value) => {
  return Boolean(
    value?.id ||
      String(value?.email || "").trim()
  );
};

const isAvisosDisabledRoute = () => {
  return AVISOS_DISABLED_PATHS.has(route.path);
};

const canCheckAvisos = () => {
  return (
    !isAvisosDisabledRoute() &&
    Boolean(getAccessToken())
  );
};

const getStatusVersion = (status) => {
  return String(
    status?.notifyVersion ||
      status?.version ||
      ""
  ).trim();
};

const loadProfile = async () => {
  if (!getAccessToken()) {
    user.value = null;
    return null;
  }

  try {
    const { data } = await api.get(
      "auth/profile/"
    );

    user.value = data;
    return data;
  } catch (error) {
    const statusCode = Number(
      error?.response?.status || 0
    );

    if (statusCode === 401) {
      user.value = null;
    }

    if (statusCode !== 401) {
      console.error(
        "No fue posible cargar el perfil para los avisos.",
        error
      );
    }

    return null;
  }
};

const ensureResolvedUser = async () => {
  if (hasUserIdentity(user.value)) {
    return user.value;
  }

  const loadedUser = await loadProfile();

  return hasUserIdentity(loadedUser)
    ? loadedUser
    : null;
};

const fetchConfirmedStatus = async () => {
  const status = await getAvisosStatus();
  const version = getStatusVersion(status);

  currentVersion.value = version;
  lastConfirmedVersion.value = version;

  return status;
};

const checkAvisos = async ({
  force = false,
} = {}) => {
  if (
    checking ||
    closingOverlay ||
    !canCheckAvisos()
  ) {
    return;
  }

  if (overlayVisible.value && !force) {
    return;
  }

  checking = true;

  try {
    const resolvedUser =
      await ensureResolvedUser();

    if (!resolvedUser) {
      return;
    }

    const status =
      await fetchConfirmedStatus();

    const mustOpen =
      await shouldOpenAvisos(
        resolvedUser,
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

const prepareManualOpen = async () => {
  if (!canCheckAvisos()) {
    return null;
  }

  const resolvedUser =
    await ensureResolvedUser();

  if (!resolvedUser) {
    return null;
  }

  try {
    await fetchConfirmedStatus();
  } catch (error) {
    const statusCode = Number(
      error?.response?.status || 0
    );

    if (statusCode !== 401) {
      console.error(
        "No fue posible sincronizar la versión de los avisos.",
        error
      );
    }
  }

  return resolvedUser;
};

const openAvisosViewer = async () => {
  const resolvedUser =
    await prepareManualOpen();

  if (!resolvedUser) {
    return;
  }

  openInManageMode.value = false;
  overlayVisible.value = true;
};

const openAvisosManager = async () => {
  const resolvedUser =
    await prepareManualOpen();

  if (!resolvedUser) {
    return;
  }

  const isAdmin = Boolean(
    resolvedUser?.is_staff ||
      resolvedUser?.is_superuser ||
      resolvedUser?.es_admin ||
      resolvedUser?.is_admin
  );

  if (!isAdmin) {
    return;
  }

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

const handleOverlayClosed = async () => {
  if (closingOverlay) {
    return;
  }

  closingOverlay = true;

  const wasManageMode =
    openInManageMode.value;

  openInManageMode.value = false;

  try {
    if (!canCheckAvisos()) {
      return;
    }

    const resolvedUser =
      await ensureResolvedUser();

    if (!resolvedUser) {
      return;
    }

    try {
      const status =
        await fetchConfirmedStatus();

      const confirmedVersion =
        getStatusVersion(status);

      if (
        status?.hasItems &&
        confirmedVersion
      ) {
        markAvisosAsSeen(
          resolvedUser,
          status
        );
      }

      return;
    } catch (error) {
      const statusCode = Number(
        error?.response?.status || 0
      );

      if (statusCode !== 401) {
        console.error(
          "No fue posible confirmar la versión al cerrar los avisos.",
          error
        );
      }
    }

    /*
     * Para una visualización normal puede utilizarse la última
     * versión confirmada obtenida al abrir el overlay.
     *
     * En modo administrador no se usa este respaldo porque el
     * contenido pudo cambiar durante la sesión de edición.
     */
    if (
      !wasManageMode &&
      lastConfirmedVersion.value
    ) {
      markAvisosAsSeen(
        resolvedUser,
        lastConfirmedVersion.value
      );
    }
  } finally {
    closingOverlay = false;
  }
};

const handleVersionChange = (
  nextVersion
) => {
  const normalizedVersion = String(
    nextVersion || ""
  ).trim();

  if (!normalizedVersion) {
    return;
  }

  currentVersion.value =
    normalizedVersion;
};

const clearRouteCheck = () => {
  if (!routeCheckTimer) {
    return;
  }

  window.clearTimeout(routeCheckTimer);
  routeCheckTimer = null;
};

const scheduleRouteCheck = () => {
  clearRouteCheck();

  routeCheckTimer = window.setTimeout(
    async () => {
      routeCheckTimer = null;

      if (!canCheckAvisos()) {
        return;
      }

      await checkAvisos();
    },
    ROUTE_CHECK_DELAY_MS
  );
};

const startInterval = () => {
  if (checkTimer) {
    return;
  }

  checkTimer = window.setInterval(
    () => {
      checkAvisos();
    },
    CHECK_INTERVAL_MS
  );
};

const stopInterval = () => {
  if (!checkTimer) {
    return;
  }

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
