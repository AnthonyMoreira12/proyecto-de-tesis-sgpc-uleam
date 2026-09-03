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
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";
import AvisosHomeOverlay from "../avisos-home-overlay/AvisosHomeOverlay.vue";
import {
  getAvisosStatus,
  markAvisosAsSeen,
  shouldOpenAvisos,
} from "../../scripts/utils/avisosGate";

const route = useRoute();
const router = useRouter();

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
let manualOpenInFlight = false;
let lastManualRequestKey = "";

const manualAvisosRequested = computed(() => {
  return (
    String(route.query?.modal || "")
      .trim()
      .toLowerCase() === "avisos"
  );
});

const manualAvisosRequestKey = computed(() => {
  if (!manualAvisosRequested.value) {
    return "";
  }

  return [
    route.path,
    String(route.query?.ts || ""),
  ].join(":");
});

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

const clearManualAvisosQuery = async () => {
  if (!manualAvisosRequested.value) {
    return;
  }

  const nextQuery = {
    ...route.query,
  };

  delete nextQuery.modal;
  delete nextQuery.ts;

  try {
    await router.replace({
      path: route.path,
      query: nextQuery,
      hash: route.hash,
    });
  } catch {
    // La navegación puede quedar cancelada si otra ruta ganó la carrera.
  }
};

const checkAvisos = async ({
  force = false,
} = {}) => {
  if (
    checking ||
    closingOverlay ||
    manualOpenInFlight ||
    !canCheckAvisos()
  ) {
    return;
  }

  if (manualAvisosRequested.value && !force) {
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

const openManualFromRoute = async () => {
  const requestKey =
    manualAvisosRequestKey.value;

  if (
    !requestKey ||
    manualOpenInFlight ||
    requestKey === lastManualRequestKey
  ) {
    return;
  }

  manualOpenInFlight = true;
  lastManualRequestKey = requestKey;

  try {
    await openAvisosViewer();
  } finally {
    manualOpenInFlight = false;
  }
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
  overlayVisible.value = false;

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

    /*
     * En una visualización normal se persiste inmediatamente la
     * última versión confirmada. Esto cierra la pequeña ventana de
     * carrera entre el clic de cerrar y la siguiente comprobación.
     * Luego se reconcilia con el backend.
     */
    if (!wasManageMode) {
      const optimisticVersion =
        currentVersion.value ||
        lastConfirmedVersion.value;

      if (optimisticVersion) {
        markAvisosAsSeen(
          resolvedUser,
          optimisticVersion
        );
      }
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

      /*
       * Si la red falla, la visualización normal ya quedó marcada
       * con la última versión válida. En modo administrador no se
       * adivina la versión porque pudo cambiar mientras editaba.
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
    }
  } finally {
    await clearManualAvisosQuery();
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
  lastConfirmedVersion.value =
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
  async () => {
    if (isAvisosDisabledRoute()) {
      clearRouteCheck();
      overlayVisible.value = false;
      openInManageMode.value = false;
      return;
    }

    if (manualAvisosRequested.value) {
      clearRouteCheck();
      await openManualFromRoute();
      return;
    }

    /*
     * Al desaparecer la query manual, una futura solicitud con un
     * nuevo `ts` debe poder volver a abrir el visor.
     */
    lastManualRequestKey = "";
    scheduleRouteCheck();
  }
);

onMounted(async () => {
  window.addEventListener(
    "sgpc:open-avisos",
    handleExternalOpen
  );

  await nextTick();

  if (manualAvisosRequested.value) {
    await openManualFromRoute();
  } else if (canCheckAvisos()) {
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
