import { onBeforeUnmount, watch } from "vue";

/**
 * Ejecuta una consulta automáticamente cuando cambian los filtros.
 * Se usa debounce para evitar una petición por cada pulsación al escribir.
 */
export function useAutoFilters(source, callback, options = {}) {
  const delay = Number(options.delay ?? 300);
  let timer = null;

  const stop = watch(
    source,
    () => {
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        timer = null;
        callback();
      }, delay);
    },
    {
      deep: true,
      flush: "post",
    },
  );

  onBeforeUnmount(() => {
    stop();
    if (timer) window.clearTimeout(timer);
  });
}
