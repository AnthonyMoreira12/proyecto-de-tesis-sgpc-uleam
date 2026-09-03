import { computed, onBeforeUnmount, ref } from "vue";

/**
 * Estado reutilizable para cargas de pantalla y refrescos.
 * El loader visual puede retrasarse para evitar parpadeos en peticiones rápidas.
 */
export function useAsyncState({ loadingDelay = 220 } = {}) {
  const pending = ref(false);
  const visibleLoading = ref(false);
  const error = ref("");
  const hasLoaded = ref(false);

  let loadingTimer = null;

  const refreshing = computed(() => pending.value && hasLoaded.value);
  const initialLoading = computed(() => pending.value && !hasLoaded.value);

  function clearLoadingTimer() {
    if (loadingTimer) {
      clearTimeout(loadingTimer);
      loadingTimer = null;
    }
  }

  function begin({ clearError = true } = {}) {
    pending.value = true;
    if (clearError) error.value = "";

    clearLoadingTimer();
    loadingTimer = setTimeout(() => {
      if (pending.value) visibleLoading.value = true;
    }, Math.max(0, Number(loadingDelay) || 0));
  }

  function finish({ loaded = true } = {}) {
    pending.value = false;
    if (loaded) hasLoaded.value = true;
    clearLoadingTimer();
    visibleLoading.value = false;
  }

  function fail(message) {
    error.value = String(message || "No pudimos completar la operación.");
  }

  function resetError() {
    error.value = "";
  }

  onBeforeUnmount(clearLoadingTimer);

  return {
    pending,
    visibleLoading,
    error,
    hasLoaded,
    refreshing,
    initialLoading,
    begin,
    finish,
    fail,
    resetError,
  };
}
