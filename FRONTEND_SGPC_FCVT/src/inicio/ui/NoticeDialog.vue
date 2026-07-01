<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="isOpen"
        class="notice-shell"
        role="presentation"
      >
        <div
          class="notice-backdrop"
          aria-hidden="true"
          @click="tryClose"
        ></div>

        <div
          ref="dialogRef"
          class="notice"
          :class="[
            `notice--${variant}`,
            { 'notice--confirm': !!modelValue?.confirm }
          ]"
          role="dialog"
          aria-modal="true"
          aria-labelledby="notice-title"
          aria-describedby="notice-body"
          tabindex="-1"
        >
          <div class="notice-accent" aria-hidden="true"></div>

          <div class="notice-header">
            <div class="notice-headcopy">
              <div class="notice-eyebrowrow">
                <div class="notice-icon" :class="`notice-icon--${variant}`" aria-hidden="true">
                  <span v-if="variant === 'danger'">!</span>
                  <span v-else-if="variant === 'warning'">!</span>
                  <span v-else>i</span>
                </div>

                <div class="notice-kicker" :class="`notice-kicker--${variant}`">
                  {{ kickerLabel }}
                </div>
              </div>

              <h3 id="notice-title" class="notice-title">
                {{ modelValue.title || "Aviso" }}
              </h3>
            </div>

            <button
              ref="closeBtnRef"
              class="notice-close"
              type="button"
              @click="tryClose"
              :disabled="busy"
              aria-label="Cerrar"
              title="Cerrar"
            >
              <span aria-hidden="true">✕</span>
            </button>
          </div>

          <div class="notice-content">
            <p id="notice-body" class="notice-body">
              {{ modelValue.message || "" }}
            </p>
          </div>

          <div class="notice-actions">
            <template v-if="modelValue.confirm">
              <button
                class="notice-btn notice-btn--ghost"
                type="button"
                @click="handleCancel"
                :disabled="busy"
              >
                {{ busy ? "..." : (modelValue.cancelText || "Cancelar") }}
              </button>

              <button
                class="notice-btn"
                :class="confirmBtnClass"
                type="button"
                @click="handleConfirm"
                :disabled="busy"
              >
                {{ busy ? "Procesando..." : (modelValue.confirmText || "Confirmar") }}
              </button>
            </template>

            <template v-else>
              <button
                class="notice-btn notice-btn--primary"
                type="button"
                @click="tryClose"
                :disabled="busy"
              >
                Entendido
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import {
  ref,
  Teleport,
  Transition,
  computed,
  watch,
  nextTick,
  onMounted,
  onBeforeUnmount,
} from "vue";

const props = defineProps({
  modelValue: { type: Object, required: true },
});

const emit = defineEmits(["close"]);

const busy = ref(false);
const dialogRef = ref(null);
const closeBtnRef = ref(null);

const isOpen = computed(() => !!props.modelValue?.open);

const normalize = (v) =>
  String(v || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();

const combinedText = computed(() => {
  const title = normalize(props.modelValue?.title);
  const message = normalize(props.modelValue?.message);
  return `${title} ${message}`.trim();
});

const variant = computed(() => {
  const text = combinedText.value;

  if (
    text.includes("eliminar") ||
    text.includes("borrar") ||
    text.includes("desactivar") ||
    text.includes("revocar") ||
    text.includes("bloquear")
  ) {
    return "danger";
  }

  if (
    text.includes("advertencia") ||
    text.includes("pendiente") ||
    text.includes("activar") ||
    text.includes("atencion")
  ) {
    return "warning";
  }

  return "info";
});

const kickerLabel = computed(() => {
  if (variant.value === "danger") return "Acción sensible";
  if (variant.value === "warning") return "Confirmación";
  return "Aviso del sistema";
});

const confirmBtnClass = computed(() => {
  if (variant.value === "danger") return "notice-btn--danger";
  if (variant.value === "warning") return "notice-btn--warning";
  return "notice-btn--primary";
});

const focusDialog = async () => {
  await nextTick();
  closeBtnRef.value?.focus?.();
};

const lockScroll = (locked) => {
  if (typeof document === "undefined") return;
  document.body.style.overflow = locked ? "hidden" : "";
};

const tryClose = () => {
  if (busy.value) return;
  emit("close");
};

const handleCancel = async () => {
  if (busy.value) return;

  try {
    busy.value = true;
    const fn = props.modelValue?.onCancel;
    if (typeof fn === "function") await fn();
  } finally {
    busy.value = false;
    emit("close");
  }
};

const handleConfirm = async () => {
  if (busy.value) return;

  try {
    busy.value = true;
    const fn = props.modelValue?.onConfirm;
    if (typeof fn === "function") await fn();
  } finally {
    busy.value = false;
    emit("close");
  }
};

const onKeyDown = (event) => {
  if (!isOpen.value) return;
  if (event.key !== "Escape") return;
  if (busy.value) return;
  tryClose();
};

watch(
  () => isOpen.value,
  async (open) => {
    lockScroll(open);
    if (open) {
      await focusDialog();
    }
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener("keydown", onKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeyDown);
  lockScroll(false);
});
</script>

<style scoped>
.notice-shell {
  --no-card: var(--bg-card, #ffffff);
  --no-surface: var(--bg-elevated, var(--bg-card, #ffffff));
  --no-soft: color-mix(in srgb, var(--bg-elevated, var(--bg-card, #ffffff)) 86%, transparent);
  --no-text: var(--text-primary, #111111);
  --no-muted: var(--text-secondary, #5f5a53);
  --no-line: color-mix(in srgb, var(--border-color, rgba(17, 17, 17, 0.1)) 92%, transparent);
  --no-line-strong: color-mix(
    in srgb,
    var(--border-strong, rgba(17, 17, 17, 0.14)) 92%,
    transparent
  );

  --no-primary: var(--color-primary, #111111);
  --no-warning: var(--warning, #8a6d33);
  --no-danger: var(--danger, #8f4740);

  --no-shadow: var(--shadow-strong, 0 18px 42px rgba(17, 17, 17, 0.07));

  position: fixed;
  inset: 0;
  z-index: 340;
  display: grid;
  place-items: center;
  padding: clamp(14px, 2vw, 24px);
  overflow: auto;
}

.notice-backdrop {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--overlay, rgba(17, 17, 17, 0.34)) 92%, transparent),
      color-mix(in srgb, var(--overlay, rgba(17, 17, 17, 0.34)) 100%, transparent)
    );
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.notice {
  position: relative;
  z-index: 1;
  width: min(560px, 100%);
  max-width: 100%;
  max-height: min(84vh, 720px);
  overflow: auto;
  margin: auto;
  border-radius: 24px;
  border: 1px solid var(--no-line);
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--no-surface) 96%, transparent),
      color-mix(in srgb, var(--no-card) 100%, transparent)
    );
  color: var(--no-text);
  box-shadow: var(--no-shadow);
  padding: 0;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  filter: none !important;
  opacity: 1 !important;
}

.notice-accent {
  height: 2px;
  width: 100%;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--no-primary) 42%, transparent),
    color-mix(in srgb, var(--no-primary) 8%, transparent)
  );
  border-radius: 24px 24px 0 0;
}

.notice--danger .notice-accent {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--no-danger) 52%, transparent),
    color-mix(in srgb, var(--no-danger) 10%, transparent)
  );
}

.notice--warning .notice-accent {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--no-warning) 52%, transparent),
    color-mix(in srgb, var(--no-warning) 10%, transparent)
  );
}

.notice-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 18px 20px 14px;
}

.notice-headcopy {
  min-width: 0;
  display: grid;
  gap: 10px;
}

.notice-eyebrowrow {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.notice-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 900;
  border: 1px solid transparent;
}

.notice-icon--info {
  color: color-mix(in srgb, var(--no-text) 88%, var(--no-primary));
  background: color-mix(in srgb, var(--no-primary) 8%, transparent);
  border-color: color-mix(in srgb, var(--no-primary) 16%, transparent);
}

.notice-icon--warning {
  color: color-mix(in srgb, var(--no-text) 88%, var(--no-warning));
  background: color-mix(in srgb, var(--no-warning) 10%, transparent);
  border-color: color-mix(in srgb, var(--no-warning) 18%, transparent);
}

.notice-icon--danger {
  color: color-mix(in srgb, var(--no-text) 88%, var(--no-danger));
  background: color-mix(in srgb, var(--no-danger) 9%, transparent);
  border-color: color-mix(in srgb, var(--no-danger) 18%, transparent);
}

.notice-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 11.4px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 1px solid transparent;
}

.notice-kicker--info {
  color: var(--no-muted);
  background: color-mix(in srgb, var(--no-primary) 6%, transparent);
  border-color: color-mix(in srgb, var(--no-primary) 14%, transparent);
}

.notice-kicker--warning {
  color: color-mix(in srgb, var(--no-text) 86%, var(--no-warning));
  background: color-mix(in srgb, var(--no-warning) 8%, transparent);
  border-color: color-mix(in srgb, var(--no-warning) 18%, transparent);
}

.notice-kicker--danger {
  color: color-mix(in srgb, var(--no-text) 86%, var(--no-danger));
  background: color-mix(in srgb, var(--no-danger) 8%, transparent);
  border-color: color-mix(in srgb, var(--no-danger) 18%, transparent);
}

.notice-title {
  margin: 0;
  color: var(--no-text);
  font-family: var(--font-serif, var(--font-sans));
  font-size: clamp(1.08rem, 0.98rem + 0.3vw, 1.24rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.14;
}

.notice-close {
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--no-line) 92%, transparent);
  background: color-mix(in srgb, var(--no-soft) 94%, var(--no-card));
  color: var(--no-text);
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  transition:
    transform var(--t-fast, 0.18s ease),
    box-shadow var(--t-fast, 0.18s ease),
    border-color var(--t-fast, 0.18s ease),
    background var(--t-fast, 0.18s ease),
    color var(--t-fast, 0.18s ease);
}

.notice-close:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--no-primary) 16%, var(--no-line));
  box-shadow: 0 8px 18px rgba(17, 17, 17, 0.08);
}

.notice-close:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.notice-close:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px var(--focus-ring, rgba(17, 17, 17, 0.14));
}

.notice-content {
  padding: 0 20px;
}

.notice-body {
  margin: 0;
  padding: 16px 0 0;
  border-top: 1px solid color-mix(in srgb, var(--no-line) 74%, transparent);
  color: var(--no-muted);
  line-height: 1.68;
  white-space: pre-line;
  font-size: 0.97rem;
}

.notice-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 18px 20px 20px;
  margin-top: 16px;
  border-top: 1px solid color-mix(in srgb, var(--no-line) 74%, transparent);
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--no-card) 88%, transparent),
      color-mix(in srgb, var(--no-card) 96%, transparent)
    );
}

.notice-btn {
  min-width: 142px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 800;
  transition:
    transform var(--t-fast, 0.18s ease),
    box-shadow var(--t-fast, 0.18s ease),
    border-color var(--t-fast, 0.18s ease),
    background var(--t-fast, 0.18s ease),
    filter var(--t-fast, 0.18s ease);
}

.notice-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.notice-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px var(--focus-ring, rgba(17, 17, 17, 0.14));
}

.notice-btn--ghost {
  border: 1px solid color-mix(in srgb, var(--no-line) 90%, transparent);
  background: var(--no-soft);
  color: var(--no-text);
}

.notice-btn--ghost:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--no-primary) 16%, var(--no-line));
  box-shadow: 0 8px 18px rgba(17, 17, 17, 0.08);
}

.notice-btn--primary {
  border: 1px solid color-mix(in srgb, var(--no-primary) 18%, transparent);
  background: var(--button-bg, #000000);
  color: var(--button-text, #ffffff);
  box-shadow: 0 10px 22px rgba(17, 17, 17, 0.12);
}

.notice-btn--primary:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.03);
}

.notice-btn--warning {
  border: 1px solid color-mix(in srgb, var(--no-warning) 20%, transparent);
  background: color-mix(in srgb, var(--no-warning) 90%, #000 10%);
  color: #ffffff;
  box-shadow: 0 10px 22px color-mix(in srgb, var(--no-warning) 16%, transparent);
}

.notice-btn--warning:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.03);
}

.notice-btn--danger {
  border: 1px solid color-mix(in srgb, var(--no-danger) 20%, transparent);
  background: color-mix(in srgb, var(--no-danger) 92%, #000 8%);
  color: #ffffff;
  box-shadow: 0 10px 22px color-mix(in srgb, var(--no-danger) 16%, transparent);
}

.notice-btn--danger:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.03);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition:
    opacity var(--t-fast, 0.18s ease),
    transform var(--t-fast, 0.18s ease);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

:global(.dark) .notice,
:global(html.dark) .notice,
:global([data-theme="dark"]) .notice {
  border-color: rgba(255, 255, 255, 0.1);
}

:global(.dark) .notice-actions,
:global(html.dark) .notice-actions,
:global([data-theme="dark"]) .notice-actions {
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--bg-card, #26221f) 88%, transparent),
      color-mix(in srgb, var(--bg-card, #26221f) 96%, transparent)
    );
}

@media (max-width: 640px) {
  .notice-shell {
    padding: 14px;
  }

  .notice {
    width: 100%;
    border-radius: 20px;
  }

  .notice-accent {
    border-radius: 20px 20px 0 0;
  }

  .notice-header {
    padding: 16px 16px 12px;
    gap: 10px;
  }

  .notice-content {
    padding: 0 16px;
  }

  .notice-actions {
    padding: 16px;
    flex-direction: column-reverse;
  }

  .notice-btn {
    width: 100%;
    min-width: 0;
  }

  .notice-close {
    width: 42px;
    height: 42px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .notice,
  .notice-close,
  .notice-btn,
  .modal-fade-enter-active,
  .modal-fade-leave-active {
    transition: none !important;
  }
}
</style>