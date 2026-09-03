<template>
  <Teleport to="body">
    <Transition name="notice-fade">
      <div
        v-if="modelValue?.open"
        class="notice-overlay"
        @click.self="handleBackdropClick"
      >
        <div
          ref="dialogRef"
          class="notice"
          :class="[
            `notice--${variant}`,
            { 'notice--confirm': !!modelValue?.confirm },
          ]"
          :role="modelValue?.confirm ? 'alertdialog' : 'dialog'"
          aria-modal="true"
          aria-labelledby="notice-title"
          :aria-describedby="
            modelValue?.details
              ? 'notice-body notice-details'
              : 'notice-body'
          "
          :aria-busy="busy ? 'true' : 'false'"
          tabindex="-1"
          @keydown="handleDialogKeydown"
        >
          <header class="notice-header">
            <div class="notice-headcopy">
              <span
                class="notice-icon"
                :class="`notice-icon--${variant}`"
                aria-hidden="true"
              >
                <span v-if="variant === 'success'">✓</span>
                <span v-else-if="variant === 'danger'">!</span>
                <span v-else-if="variant === 'warning'">!</span>
                <span v-else>i</span>
              </span>

              <div class="notice-heading">
                <h3 id="notice-title" class="notice-title">
                  {{ modelValue.title || defaultTitle }}
                </h3>
              </div>
            </div>

            <button
              v-if="!modelValue.confirm"
              class="notice-close"
              type="button"
              :disabled="busy"
              aria-label="Cerrar aviso"
              @click="tryClose"
            >
              <span aria-hidden="true">×</span>
            </button>
          </header>

          <div class="notice-content">
            <p id="notice-body" class="notice-body">
              {{ modelValue.message || "" }}
            </p>

            <p
              v-if="modelValue.details"
              id="notice-details"
              class="notice-details"
            >
              {{ modelValue.details }}
            </p>
          </div>

          <footer class="notice-actions">
            <template v-if="modelValue.confirm">
              <button
                ref="cancelButtonRef"
                class="notice-btn notice-btn--secondary"
                type="button"
                :disabled="busy"
                @click="handleCancel"
              >
                {{
                  busy
                    ? "Espere..."
                    : (modelValue.cancelText || "Cancelar")
                }}
              </button>

              <button
                class="notice-btn"
                :class="confirmBtnClass"
                type="button"
                :disabled="busy"
                @click="handleConfirm"
              >
                {{
                  busy
                    ? "Procesando..."
                    : (modelValue.confirmText || "Confirmar")
                }}
              </button>
            </template>

            <template v-else>
              <button
                ref="primaryButtonRef"
                class="notice-btn notice-btn--primary"
                type="button"
                :disabled="busy"
                @click="tryClose"
              >
                Cerrar
              </button>
            </template>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits([
  "close",
]);

const busy = ref(false);
const dialogRef = ref(null);
const cancelButtonRef = ref(null);
const primaryButtonRef = ref(null);

let previouslyFocusedElement = null;
let previousBodyOverflow = "";
let bodyLockedByNotice = false;

const normalize = (value) =>
  String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();

const combinedText = computed(() => {
  const title = normalize(
    props.modelValue?.title
  );

  const message = normalize(
    props.modelValue?.message
  );

  return `${title} ${message}`.trim();
});

const isErrorNotice = computed(() => {
  const text = combinedText.value;

  return (
    text.includes("no se pudo") ||
    text.includes("error") ||
    text.includes("fallo") ||
    text.includes("falló")
  );
});

const variant = computed(() => {
  const explicitVariant = normalize(
    props.modelValue?.variant ||
      props.modelValue?.tone
  );

  if (
    [
      "info",
      "success",
      "warning",
      "danger",
    ].includes(explicitVariant)
  ) {
    return explicitVariant;
  }

  const text = combinedText.value;

  if (
    isErrorNotice.value ||
    text.includes("eliminar") ||
    text.includes("borrar") ||
    text.includes("desactivar") ||
    text.includes("revocar") ||
    text.includes("bloquear") ||
    text.includes("rechazar")
  ) {
    return "danger";
  }

  if (
    text.includes("guardado") ||
    text.includes("guardada") ||
    text.includes("actualizado") ||
    text.includes("actualizada") ||
    text.includes("activado") ||
    text.includes("activada") ||
    text.includes("completado") ||
    text.includes("completada") ||
    text.includes("correctamente") ||
    text.includes("exito")
  ) {
    return "success";
  }

  if (
    text.includes("advertencia") ||
    text.includes("pendiente") ||
    text.includes("activar") ||
    text.includes("atencion") ||
    text.includes("correccion") ||
    text.includes("observacion")
  ) {
    return "warning";
  }

  return "info";
});

const defaultTitle = computed(() => {
  if (props.modelValue?.confirm) {
    return "Confirmar acción";
  }

  if (variant.value === "success") {
    return "Listo";
  }

  if (variant.value === "danger") {
    return isErrorNotice.value
      ? "No se pudo completar"
      : "Confirmación requerida";
  }

  if (variant.value === "warning") {
    return "Atención";
  }

  return "Aviso";
});

const confirmBtnClass = computed(() => {
  if (variant.value === "danger") {
    return "notice-btn--danger";
  }

  if (variant.value === "warning") {
    return "notice-btn--warning";
  }

  return "notice-btn--primary";
});

const getFocusableElements = () => {
  const dialog = dialogRef.value;

  if (!(dialog instanceof HTMLElement)) {
    return [];
  }

  return Array.from(
    dialog.querySelectorAll(
      [
        "button:not([disabled])",
        "[href]",
        "input:not([disabled])",
        "select:not([disabled])",
        "textarea:not([disabled])",
        '[tabindex]:not([tabindex="-1"])',
      ].join(",")
    )
  ).filter(
    (element) =>
      element instanceof HTMLElement &&
      element.getAttribute("aria-hidden") !== "true"
  );
};

const focusInitialControl = async () => {
  await nextTick();

  const preferredControl =
    props.modelValue?.confirm
      ? cancelButtonRef.value
      : primaryButtonRef.value;

  if (preferredControl instanceof HTMLElement) {
    preferredControl.focus();
    return;
  }

  dialogRef.value?.focus();
};

const lockBodyScroll = () => {
  if (
    typeof document === "undefined" ||
    bodyLockedByNotice
  ) {
    return;
  }

  previouslyFocusedElement =
    document.activeElement;

  previousBodyOverflow =
    document.body.style.overflow;

  document.body.style.overflow = "hidden";
  bodyLockedByNotice = true;
};

const restorePageState = async () => {
  if (
    typeof document === "undefined" ||
    !bodyLockedByNotice
  ) {
    return;
  }

  document.body.style.overflow =
    previousBodyOverflow;

  bodyLockedByNotice = false;

  await nextTick();

  if (
    previouslyFocusedElement instanceof HTMLElement &&
    previouslyFocusedElement.isConnected
  ) {
    previouslyFocusedElement.focus();
  }

  previouslyFocusedElement = null;
};

const tryClose = () => {
  if (busy.value) {
    return;
  }

  emit("close");
};

const handleCancel = async () => {
  if (busy.value) {
    return;
  }

  try {
    busy.value = true;

    const fn =
      props.modelValue?.onCancel;

    if (typeof fn === "function") {
      await fn();
    }
  } finally {
    busy.value = false;
    emit("close");
  }
};

const handleConfirm = async () => {
  if (busy.value) {
    return;
  }

  try {
    busy.value = true;

    const fn =
      props.modelValue?.onConfirm;

    if (typeof fn === "function") {
      await fn();
    }
  } finally {
    busy.value = false;
    emit("close");
  }
};

const handleBackdropClick = () => {
  if (props.modelValue?.confirm) {
    void handleCancel();
    return;
  }

  tryClose();
};

const handleDialogKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();

    if (props.modelValue?.confirm) {
      void handleCancel();
      return;
    }

    tryClose();
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getFocusableElements();

  if (!focusableElements.length) {
    event.preventDefault();
    dialogRef.value?.focus();
    return;
  }

  const firstElement =
    focusableElements[0];

  const lastElement =
    focusableElements[
      focusableElements.length - 1
    ];

  const activeElement =
    document.activeElement;

  if (
    event.shiftKey &&
    activeElement === firstElement
  ) {
    event.preventDefault();
    lastElement.focus();
    return;
  }

  if (
    !event.shiftKey &&
    activeElement === lastElement
  ) {
    event.preventDefault();
    firstElement.focus();
  }
};

watch(
  () => Boolean(
    props.modelValue?.open
  ),
  async (isOpen) => {
    busy.value = false;

    if (isOpen) {
      lockBodyScroll();
      await focusInitialControl();
      return;
    }

    await restorePageState();
  },
  {
    immediate: true,
  }
);

onBeforeUnmount(() => {
  if (
    typeof document !== "undefined" &&
    bodyLockedByNotice
  ) {
    document.body.style.overflow =
      previousBodyOverflow;

    if (
      previouslyFocusedElement instanceof HTMLElement &&
      previouslyFocusedElement.isConnected
    ) {
      previouslyFocusedElement.focus();
    }
  }
});
</script>

<style scoped>
.notice-overlay,
.notice-overlay * {
  box-sizing: border-box;
}

.notice-overlay {
  /* ========================================================
     Variables locales.
     El modal se teletransporta a body, por eso no depende de
     variables definidas en el contenedor visual de la página.
  ======================================================== */
  --notice-card:
    var(
      --bg-card,
      #ffffff
    );

  --notice-soft:
    var(
      --bg-elevated,
      #f6f8fb
    );

  --notice-line:
    var(
      --border-color,
      rgba(17, 24, 39, 0.12)
    );

  --notice-line-strong:
    var(
      --border-strong,
      rgba(17, 24, 39, 0.2)
    );

  --notice-text:
    var(
      --text-primary,
      #111827
    );

  --notice-muted:
    var(
      --text-secondary,
      #667085
    );

  --notice-primary:
    var(
      --color-primary,
      #2563eb
    );

  --notice-success:
    var(
      --success,
      #17803d
    );

  --notice-warning:
    var(
      --warning,
      #9a6700
    );

  --notice-danger:
    var(
      --danger,
      #b42318
    );

  --notice-on-primary:
    var(
      --text-on-primary,
      #ffffff
    );

  --notice-on-success:
    var(
      --success-contrast,
      #ffffff
    );

  --notice-on-warning:
    var(
      --warning-contrast,
      #ffffff
    );

  --notice-on-danger:
    var(
      --danger-contrast,
      #ffffff
    );

  position: fixed;
  inset: 0;

  z-index:
    var(
      --z-notice,
      1200
    );

  width: 100vw;
  height: 100dvh;
  min-height: 100dvh;

  display: grid;
  place-items: center;

  padding:
    clamp(
      14px,
      2.2vw,
      26px
    );

  overflow: auto;

  overscroll-behavior:
    contain;

  background:
    rgba(
      15,
      23,
      42,
      0.52
    );

  backdrop-filter:
    none;

  -webkit-backdrop-filter:
    none;
}

/* ============================================================
   MODAL
============================================================ */

.notice {
  position: relative;

  width:
    min(
      560px,
      100%
    );

  max-height:
    min(
      88dvh,
      720px
    );

  display: flex;
  flex-direction: column;

  margin: auto;

  overflow: hidden;

  border:
    1px solid
    var(--notice-line);

  border-radius:
    14px;

  outline: none;

  background:
    var(--notice-card);

  color:
    var(--notice-text);

  box-shadow:
    0
    18px
    52px
    rgba(
      15,
      23,
      42,
      0.18
    );
}

.notice:focus-visible {
  outline:
    2px solid
    var(--notice-primary);

  outline-offset:
    3px;
}

/* ============================================================
   CABECERA
============================================================ */

.notice-header {
  display: flex;

  align-items:
    flex-start;

  justify-content:
    space-between;

  gap:
    16px;

  padding:
    20px
    20px
    15px;
}

.notice-headcopy {
  min-width: 0;

  flex:
    1 1 auto;

  display: grid;

  grid-template-columns:
    40px
    minmax(0, 1fr);

  align-items:
    center;

  gap:
    12px;
}

.notice-heading {
  min-width: 0;
}

.notice-icon {
  width: 40px;
  height: 40px;

  display: inline-grid;
  place-items: center;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--notice-primary) 18%,
      var(--notice-line)
    );

  border-radius:
    10px;

  background:
    color-mix(
      in srgb,
      var(--notice-primary) 7%,
      var(--notice-card)
    );

  color:
    var(--notice-primary);

  font-size:
    0.9rem;

  font-weight:
    820;

  line-height:
    1;
}

.notice-icon--success {
  border-color:
    color-mix(
      in srgb,
      var(--notice-success) 20%,
      var(--notice-line)
    );

  background:
    color-mix(
      in srgb,
      var(--notice-success) 7%,
      var(--notice-card)
    );

  color:
    var(--notice-success);
}

.notice-icon--warning {
  border-color:
    color-mix(
      in srgb,
      var(--notice-warning) 20%,
      var(--notice-line)
    );

  background:
    color-mix(
      in srgb,
      var(--notice-warning) 7%,
      var(--notice-card)
    );

  color:
    var(--notice-warning);
}

.notice-icon--danger {
  border-color:
    color-mix(
      in srgb,
      var(--notice-danger) 20%,
      var(--notice-line)
    );

  background:
    color-mix(
      in srgb,
      var(--notice-danger) 7%,
      var(--notice-card)
    );

  color:
    var(--notice-danger);
}

.notice-title {
  margin: 0;

  color:
    var(--notice-text);

  font-family:
    var(
      --font-heading,
      inherit
    );

  font-size:
    clamp(
      1.08rem,
      1rem + 0.35vw,
      1.3rem
    );

  font-weight:
    760;

  line-height:
    1.24;

  letter-spacing:
    -0.02em;

  overflow-wrap:
    anywhere;
}

.notice-close {
  appearance: none;

  width: 38px;
  height: 38px;

  flex:
    0
    0
    38px;

  display: inline-grid;
  place-items: center;

  padding: 0;

  border:
    1px solid
    transparent;

  border-radius:
    9px;

  background:
    transparent;

  color:
    var(--notice-muted);

  font: inherit;

  font-size:
    1.3rem;

  line-height:
    1;

  cursor: pointer;

  transition:
    border-color
    130ms
    ease,
    background
    130ms
    ease,
    color
    130ms
    ease;
}

.notice-close:hover:not(:disabled) {
  border-color:
    var(--notice-line);

  background:
    var(--notice-soft);

  color:
    var(--notice-text);
}

.notice-close:focus-visible {
  outline:
    2px solid
    var(--notice-primary);

  outline-offset:
    2px;
}

.notice-close:disabled {
  opacity: 0.55;

  cursor:
    not-allowed;
}

/* ============================================================
   CONTENIDO
============================================================ */

.notice-content {
  min-height: 0;

  padding:
    0
    20px
    18px;

  overflow-y: auto;

  overscroll-behavior:
    contain;
}

.notice-body {
  margin: 0;

  padding-top:
    15px;

  border-top:
    1px solid
    var(--notice-line);

  color:
    var(--notice-muted);

  font-size:
    0.86rem;

  line-height:
    1.55;

  white-space:
    pre-line;

  overflow-wrap:
    anywhere;
}

.notice-body:empty {
  display: none;
}

.notice-details {
  margin:
    12px
    0
    0;

  padding:
    10px
    11px;

  border:
    1px solid
    var(--notice-line);

  border-radius:
    9px;

  background:
    var(--notice-soft);

  color:
    var(--notice-muted);

  font-size:
    0.78rem;

  line-height:
    1.5;

  white-space:
    pre-line;

  overflow-wrap:
    anywhere;
}

/* ============================================================
   ACCIONES
============================================================ */

.notice-actions {
  display: flex;

  flex:
    0
    0
    auto;

  align-items:
    center;

  justify-content:
    flex-end;

  gap:
    8px;

  padding:
    13px
    20px
    17px;

  border-top:
    1px solid
    var(--notice-line);

  background:
    var(--notice-card);
}

.notice--confirm
  .notice-actions {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
}

.notice-btn {
  min-height:
    42px;

  padding:
    0
    14px;

  border:
    1px solid
    transparent;

  border-radius:
    9px;

  font: inherit;

  font-size:
    0.76rem;

  font-weight:
    730;

  line-height:
    1.2;

  cursor: pointer;

  transition:
    border-color
    130ms
    ease,
    background
    130ms
    ease,
    color
    130ms
    ease;
}

.notice-btn:focus-visible {
  outline:
    2px solid
    currentColor;

  outline-offset:
    2px;
}

.notice-btn:disabled {
  opacity:
    0.58;

  cursor:
    not-allowed;
}

.notice-btn--secondary {
  border-color:
    var(--notice-line);

  background:
    var(--notice-card);

  color:
    var(--notice-text);
}

.notice-btn--secondary:hover:not(:disabled) {
  border-color:
    var(--notice-line-strong);

  background:
    var(--notice-soft);
}

.notice-btn--primary {
  border-color:
    var(--notice-primary);

  background:
    var(--notice-primary);

  color:
    var(--notice-on-primary);
}

.notice-btn--warning {
  border-color:
    var(--notice-warning);

  background:
    var(--notice-warning);

  color:
    var(--notice-on-warning);
}

.notice-btn--danger {
  border-color:
    var(--notice-danger);

  background:
    var(--notice-danger);

  color:
    var(--notice-on-danger);
}

.notice-btn--primary:hover:not(:disabled),
.notice-btn--warning:hover:not(:disabled),
.notice-btn--danger:hover:not(:disabled) {
  filter:
    brightness(0.96);
}

/* ============================================================
   TRANSICIÓN
============================================================ */

.notice-fade-enter-active,
.notice-fade-leave-active {
  transition:
    opacity
    calc(
      140ms
      * var(
        --animate-speed,
        1
      )
    )
    ease;
}

.notice-fade-enter-active
  .notice,
.notice-fade-leave-active
  .notice {
  transition:
    transform
    calc(
      140ms
      * var(
        --animate-speed,
        1
      )
    )
    ease,
    opacity
    calc(
      140ms
      * var(
        --animate-speed,
        1
      )
    )
    ease;
}

.notice-fade-enter-from,
.notice-fade-leave-to {
  opacity: 0;
}

.notice-fade-enter-from
  .notice,
.notice-fade-leave-to
  .notice {
  opacity: 0;

  transform:
    translateY(4px);
}

/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 560px) {
  .notice-overlay {
    padding-top:
      max(
        10px,
        env(
          safe-area-inset-top,
          0px
        )
      );

    padding-right:
      max(
        10px,
        env(
          safe-area-inset-right,
          0px
        )
      );

    padding-bottom:
      max(
        10px,
        env(
          safe-area-inset-bottom,
          0px
        )
      );

    padding-left:
      max(
        10px,
        env(
          safe-area-inset-left,
          0px
        )
      );
  }

  .notice {
    width: 100%;

    max-height:
      calc(
        100dvh
        - 20px
      );
  }

  .notice-header {
    padding:
      16px
      16px
      12px;
  }

  .notice-headcopy {
    grid-template-columns:
      36px
      minmax(0, 1fr);

    gap:
      10px;
  }

  .notice-icon {
    width: 36px;
    height: 36px;

    border-radius:
      9px;
  }

  .notice-content {
    padding:
      0
      16px
      16px;
  }

  .notice-actions,
  .notice--confirm
    .notice-actions {
    display: grid;

    grid-template-columns:
      minmax(0, 1fr);

    padding:
      12px
      16px
      16px;
  }

  .notice--confirm
    .notice-btn--secondary {
    order: 2;
  }

  .notice--confirm
    .notice-btn:not(
      .notice-btn--secondary
    ) {
    order: 1;
  }

  .notice-btn {
    width: 100%;
  }
}

@media (pointer: coarse) {
  .notice-close,
  .notice-btn {
    min-height:
      44px;
  }

  .notice-close {
    width: 44px;
    height: 44px;

    flex-basis:
      44px;
  }
}

@media (prefers-contrast: more) {
  .notice {
    border-color:
      var(--notice-line-strong);
  }

  .notice-close:focus-visible,
  .notice-btn:focus-visible {
    outline:
      3px solid
      currentColor;

    outline-offset:
      2px;
  }
}

@media (forced-colors: active) {
  .notice-overlay {
    background:
      rgba(
        0,
        0,
        0,
        0.72
      );
  }
}

@media (prefers-reduced-motion: reduce) {
  .notice,
  .notice-close,
  .notice-btn,
  .notice-fade-enter-active,
  .notice-fade-leave-active,
  .notice-fade-enter-active
    .notice,
  .notice-fade-leave-active
    .notice {
    transition:
      none !important;
  }
}
</style>
