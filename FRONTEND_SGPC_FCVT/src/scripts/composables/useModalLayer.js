import { onBeforeUnmount, watch } from "vue";

let openLayers = 0;

function syncDocumentLock() {
  if (typeof document === "undefined") return;

  const locked = openLayers > 0;
  document.documentElement.classList.toggle("sgpc-modal-open", locked);
  document.body?.classList.toggle("sgpc-modal-open", locked);
}

/**
 * Mantiene los modales de contenido coordinados con la navegación global.
 * - Bloquea el scroll de la página sin tocar el scroll interno del modal.
 * - Cierra drawer, búsqueda, cuenta y notificaciones al abrir un modal.
 * - Tolera más de un modal montado sin liberar el bloqueo antes de tiempo.
 */
export function useModalLayer(source) {
  let active = false;

  const stop = watch(
    source,
    (isOpen) => {
      const next = Boolean(isOpen);

      if (next && !active) {
        active = true;
        openLayers += 1;
        syncDocumentLock();

        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent("sgpc:modal-open"));
        }
        return;
      }

      if (!next && active) {
        active = false;
        openLayers = Math.max(0, openLayers - 1);
        syncDocumentLock();
      }
    },
    {
      immediate: true,
      flush: "post",
    },
  );

  onBeforeUnmount(() => {
    stop();
    if (active) {
      active = false;
      openLayers = Math.max(0, openLayers - 1);
      syncDocumentLock();
    }
  });
}
