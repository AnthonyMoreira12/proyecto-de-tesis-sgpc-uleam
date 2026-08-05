<template>
  <div class="preferences-page">
    <div class="preferences-shell">
      <header
        class="preferences-hero"
        aria-labelledby="preferences-title"
      >
        <div class="preferences-hero__identity">
          <span
            class="preferences-hero__icon"
            aria-hidden="true"
          >
            <svg
              viewBox="0 0 24 24"
              focusable="false"
            >
              <path
                d="M12 3.5a2.2 2.2 0 0 1 2.1 1.5l.2.7a2.2 2.2 0 0 0 2.7 1.4l.7-.2a2.2 2.2 0 0 1 2.5 1.1 2.2 2.2 0 0 1-.4 2.7l-.5.5a2.2 2.2 0 0 0 0 3.1l.5.5a2.2 2.2 0 0 1 .4 2.7 2.2 2.2 0 0 1-2.5 1.1l-.7-.2a2.2 2.2 0 0 0-2.7 1.4l-.2.7a2.2 2.2 0 0 1-4.2 0l-.2-.7A2.2 2.2 0 0 0 7 18.3l-.7.2a2.2 2.2 0 0 1-2.5-1.1 2.2 2.2 0 0 1 .4-2.7l.5-.5a2.2 2.2 0 0 0 0-3.1l-.5-.5A2.2 2.2 0 0 1 3.8 8a2.2 2.2 0 0 1 2.5-1.1l.7.2a2.2 2.2 0 0 0 2.7-1.4l.2-.7A2.2 2.2 0 0 1 12 3.5Z"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linecap="round"
                stroke-linejoin="round"
              />

              <circle
                cx="12"
                cy="12"
                r="3"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
              />
            </svg>
          </span>

          <div class="preferences-hero__copy">
            <span class="preferences-eyebrow">
              Configuración personal
            </span>

            <h1
              id="preferences-title"
              class="preferences-title"
            >
              Preferencias de interfaz
            </h1>

            <p class="preferences-lead">
              Ajuste la apariencia, la legibilidad y el movimiento del sistema.
            </p>
          </div>
        </div>

        <div
          class="autosave-status"
          role="status"
          aria-label="Los cambios se guardan automáticamente"
        >
          <span
            class="autosave-status__dot"
            aria-hidden="true"
          ></span>

          <span>Guardado automático</span>
        </div>
      </header>

      <main class="preferences-layout">
        <div class="preferences-main">
          <!-- APARIENCIA -->
          <section
            class="settings-card settings-card--appearance"
            aria-labelledby="appearance-title"
          >
            <header class="settings-card__header">
              <div class="settings-card__heading">
                <span
                  class="settings-card__icon"
                  aria-hidden="true"
                >
                  <svg
                    viewBox="0 0 24 24"
                    focusable="false"
                  >
                    <path
                      d="M12 3a9 9 0 1 0 0 18h1.2a1.8 1.8 0 0 0 .4-3.5l-.9-.2a1.6 1.6 0 0 1 .4-3.1h2.5A5.4 5.4 0 0 0 21 8.8C21 5.6 17 3 12 3Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />

                    <circle
                      cx="7.5"
                      cy="10"
                      r="1"
                      fill="currentColor"
                    />

                    <circle
                      cx="10"
                      cy="6.8"
                      r="1"
                      fill="currentColor"
                    />

                    <circle
                      cx="14"
                      cy="6.5"
                      r="1"
                      fill="currentColor"
                    />

                    <circle
                      cx="17"
                      cy="9"
                      r="1"
                      fill="currentColor"
                    />
                  </svg>
                </span>

                <div>
                  <span class="section-kicker">
                    Apariencia
                  </span>

                  <h2 id="appearance-title">
                    Seleccione un tema
                  </h2>

                  <p>
                    Cada opción utiliza colores sólidos, sin degradados ni
                    superficies difuminadas.
                  </p>
                </div>
              </div>

              <span class="current-setting">
                {{ currentAppearance.label }}
              </span>
            </header>

            <div
              class="appearance-grid"
              role="radiogroup"
              aria-label="Temas disponibles"
            >
              <button
                v-for="option in appearanceOptions"
                :key="option.value"
                class="appearance-option"
                :class="{
                  'is-selected': selectedAppearance === option.value,
                  'is-dark-option': option.mode === 'dark',
                }"
                type="button"
                role="radio"
                :aria-checked="selectedAppearance === option.value"
                :style="getOptionStyle(option)"
                @click="selectAppearance(option.value)"
              >
                <span
                  class="appearance-option__preview"
                  aria-hidden="true"
                >
                  <span class="theme-preview">
                    <span class="theme-preview__sidebar">
                      <span class="theme-preview__brand"></span>
                      <span class="theme-preview__nav is-active"></span>
                      <span class="theme-preview__nav"></span>
                      <span class="theme-preview__nav"></span>
                    </span>

                    <span class="theme-preview__content">
                      <span class="theme-preview__topbar">
                        <span></span>
                        <span></span>
                      </span>

                      <span class="theme-preview__body">
                        <span class="theme-preview__headline"></span>

                        <span class="theme-preview__metrics">
                          <span></span>
                          <span></span>
                          <span></span>
                        </span>

                        <span class="theme-preview__panel">
                          <span></span>
                          <span></span>
                        </span>
                      </span>
                    </span>
                  </span>
                </span>

                <span class="appearance-option__footer">
                  <span class="appearance-option__copy">
                    <strong>{{ option.label }}</strong>
                    <span>{{ option.desc }}</span>
                  </span>

                  <span
                    class="appearance-option__check"
                    aria-hidden="true"
                  >
                    <svg
                      viewBox="0 0 20 20"
                      focusable="false"
                    >
                      <path
                        d="m5 10.3 3 3 7-7"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.1"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>
                </span>
              </button>
            </div>
          </section>

          <!-- LEGIBILIDAD -->
          <section
            class="settings-card"
            aria-labelledby="readability-title"
          >
            <header class="settings-card__header">
              <div class="settings-card__heading">
                <span
                  class="settings-card__icon"
                  aria-hidden="true"
                >
                  <svg
                    viewBox="0 0 24 24"
                    focusable="false"
                  >
                    <path
                      d="M4 6.5h16M8 6.5v11M5.5 17.5h5M15 10.5h4M17 10.5v7M14.5 17.5h5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>

                <div>
                  <span class="section-kicker">
                    Legibilidad
                  </span>

                  <h2 id="readability-title">
                    Tamaño del texto
                  </h2>

                  <p>
                    Cambia el tamaño base de la tipografía en toda la aplicación.
                  </p>
                </div>
              </div>

              <span class="current-setting">
                {{ currentFont.label }}
              </span>
            </header>

            <div
              class="font-size-grid"
              role="radiogroup"
              aria-label="Tamaño del texto"
            >
              <button
                v-for="option in fontOptions"
                :key="option.value"
                class="font-size-option"
                :class="{
                  'is-selected': uiFontSize === option.value,
                }"
                type="button"
                role="radio"
                :aria-checked="uiFontSize === option.value"
                @click="uiFontSize = option.value"
              >
                <span
                  class="font-size-option__sample"
                  :style="{ fontSize: option.sampleSize }"
                  aria-hidden="true"
                >
                  Aa
                </span>

                <span class="font-size-option__copy">
                  <strong>{{ option.label }}</strong>
                  <span>{{ option.detail }}</span>
                </span>
              </button>
            </div>
          </section>

          <!-- MOVIMIENTO -->
          <section
            class="settings-card"
            aria-labelledby="motion-title"
          >
            <header class="settings-card__header settings-card__header--compact">
              <div class="settings-card__heading">
                <span
                  class="settings-card__icon"
                  aria-hidden="true"
                >
                  <svg
                    viewBox="0 0 24 24"
                    focusable="false"
                  >
                    <path
                      d="M4 12h3l2.2-5 4.1 10 2.2-5H20"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div>
                  <span class="section-kicker">
                    Movimiento
                  </span>

                  <h2 id="motion-title">
                    Animaciones de interfaz
                  </h2>

                  <p>
                    Mantenga transiciones breves o desactívelas para una
                    navegación inmediata.
                  </p>
                </div>
              </div>

              <label class="switch-control">
                <span class="sr-only">
                  Activar animaciones de interfaz
                </span>

                <input
                  v-model="uiAnimations"
                  type="checkbox"
                />

                <span
                  class="switch-control__track"
                  aria-hidden="true"
                >
                  <span class="switch-control__thumb"></span>
                </span>
              </label>
            </header>

            <div class="motion-state">
              <span
                class="motion-state__indicator"
                :class="{
                  'is-enabled': uiAnimations,
                }"
                aria-hidden="true"
              ></span>

              <span>
                <strong>
                  {{
                    uiAnimations
                      ? "Animaciones activas"
                      : "Movimiento reducido"
                  }}
                </strong>

                <small>
                  {{
                    uiAnimations
                      ? "Se aplican transiciones cortas y discretas."
                      : "Los cambios de pantalla se muestran sin animación."
                  }}
                </small>
              </span>
            </div>
          </section>
        </div>

        <!-- VISTA PREVIA -->
        <aside class="preferences-sidebar">
          <section
            class="preview-card"
            aria-labelledby="preview-title"
          >
            <header class="preview-card__header">
              <div>
                <span class="section-kicker">
                  Vista previa
                </span>

                <h2 id="preview-title">
                  Resultado actual
                </h2>
              </div>

              <span
                class="preview-live"
                aria-label="Vista previa actualizada"
              >
                <span aria-hidden="true"></span>
                En vivo
              </span>
            </header>

            <div
              class="interface-preview"
              :class="{
                'is-dark': currentAppearance.mode === 'dark',
              }"
              :style="previewStyle"
              aria-hidden="true"
            >
              <div class="preview-dashboard">
                <aside class="preview-dashboard__sidebar">
                  <div class="preview-dashboard__logo">
                    <span>S</span>
                    <strong>SGPC</strong>
                  </div>

                  <nav class="preview-dashboard__nav">
                    <span class="is-active">
                      <i></i>
                      <b></b>
                    </span>

                    <span>
                      <i></i>
                      <b></b>
                    </span>

                    <span>
                      <i></i>
                      <b></b>
                    </span>

                    <span>
                      <i></i>
                      <b></b>
                    </span>
                  </nav>
                </aside>

                <div class="preview-dashboard__main">
                  <header class="preview-dashboard__topbar">
                    <div>
                      <strong>Dashboard</strong>
                      <span>Panel institucional</span>
                    </div>

                    <span class="preview-dashboard__avatar"></span>
                  </header>

                  <div class="preview-dashboard__content">
                    <div class="preview-dashboard__welcome">
                      <div>
                        <span>Resumen institucional</span>
                        <strong>Producción científica</strong>
                      </div>

                      <button
                        type="button"
                        tabindex="-1"
                      >
                        Reporte
                      </button>
                    </div>

                    <div class="preview-dashboard__stats">
                      <article>
                        <span>Publicaciones</span>
                        <strong>128</strong>
                      </article>

                      <article>
                        <span>Autores</span>
                        <strong>64</strong>
                      </article>

                      <article>
                        <span>Proyectos</span>
                        <strong>24</strong>
                      </article>
                    </div>

                    <div class="preview-dashboard__chart">
                      <div class="preview-dashboard__chart-head">
                        <span></span>
                        <span></span>
                      </div>

                      <div class="preview-dashboard__bars">
                        <i></i>
                        <i></i>
                        <i></i>
                        <i></i>
                        <i></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <dl class="current-summary">
              <div>
                <dt>Tema</dt>
                <dd>{{ currentAppearance.label }}</dd>
              </div>

              <div>
                <dt>Texto</dt>
                <dd>{{ currentFont.label }}</dd>
              </div>

              <div>
                <dt>Movimiento</dt>
                <dd>
                  {{ uiAnimations ? "Activo" : "Reducido" }}
                </dd>
              </div>
            </dl>
          </section>

          <!-- RESTAURAR -->
          <section
            class="reset-card"
            aria-labelledby="reset-title"
          >
            <div class="reset-card__copy">
              <span
                class="reset-card__icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                >
                  <path
                    d="M4 4v6h6M4.8 9.4A8 8 0 1 1 6.2 17"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <div>
                <h2 id="reset-title">
                  Restaurar preferencias
                </h2>

                <p>
                  Recupera el tema claro, el texto estándar y las animaciones.
                </p>
              </div>
            </div>

            <button
              ref="resetTrigger"
              class="reset-button"
              type="button"
              @click="openResetConfirm"
            >
              Restaurar valores iniciales
            </button>
          </section>
        </aside>
      </main>
    </div>

    <!-- MODAL PERSONALIZADO -->
    <Teleport to="body">
      <Transition name="confirm-modal">
        <div
          v-if="showResetConfirm"
          class="confirm-modal-backdrop"
          role="presentation"
          @click.self="closeResetConfirm"
        >
          <section
            ref="resetDialog"
            class="confirm-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="reset-dialog-title"
            aria-describedby="reset-dialog-description"
            tabindex="-1"
            @keydown="handleDialogKeydown"
          >
            <header class="confirm-dialog__header">
              <span
                class="confirm-dialog__icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                >
                  <path
                    d="M4 4v6h6M4.8 9.4A8 8 0 1 1 6.2 17"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.9"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <div class="confirm-dialog__heading">
                <span class="confirm-dialog__eyebrow">
                  Confirmación
                </span>

                <h2 id="reset-dialog-title">
                  Restaurar preferencias
                </h2>
              </div>

              <button
                class="confirm-dialog__close"
                type="button"
                aria-label="Cerrar ventana"
                @click="closeResetConfirm"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                  aria-hidden="true"
                >
                  <path
                    d="m7 7 10 10M17 7 7 17"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.9"
                    stroke-linecap="round"
                  />
                </svg>
              </button>
            </header>

            <div class="confirm-dialog__body">
              <p id="reset-dialog-description">
                Se aplicará nuevamente la configuración inicial de la interfaz.
              </p>

              <ul class="confirm-dialog__changes">
                <li>Tema claro estándar</li>
                <li>Tamaño de texto estándar</li>
                <li>Animaciones activadas</li>
              </ul>

              <p class="confirm-dialog__note">
                El cambio se aplicará inmediatamente. Después podrá volver a
                personalizar estas opciones.
              </p>
            </div>

            <footer class="confirm-dialog__actions">
              <button
                ref="cancelResetButton"
                class="confirm-dialog__button confirm-dialog__button--secondary"
                type="button"
                @click="closeResetConfirm"
              >
                Cancelar
              </button>

              <button
                class="confirm-dialog__button confirm-dialog__button--danger"
                type="button"
                @click="confirmReset"
              >
                Restaurar preferencias
              </button>
            </footer>
          </section>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  ref,
} from "vue";

import { storeToRefs } from "pinia";

import {
  APPEARANCE_PRESETS,
  useThemeStore,
} from "../../scripts/stores/themeStore";

const themeStore = useThemeStore();

const {
  darkMode,
  fontSize,
  animations,
} = storeToRefs(themeStore);

const showResetConfirm = ref(false);
const resetDialog = ref(null);
const resetTrigger = ref(null);
const cancelResetButton = ref(null);

let previousBodyOverflow = "";

const appearanceOptions = APPEARANCE_PRESETS;

const fontOptions = Object.freeze([
  {
    value: "15px",
    label: "Compacto",
    detail: "Más contenido visible",
    sampleSize: "1.15rem",
  },
  {
    value: "16px",
    label: "Estándar",
    detail: "Equilibrio recomendado",
    sampleSize: "1.3rem",
  },
  {
    value: "18px",
    label: "Cómodo",
    detail: "Lectura más amplia",
    sampleSize: "1.5rem",
  },
  {
    value: "20px",
    label: "Grande",
    detail: "Máxima legibilidad",
    sampleSize: "1.7rem",
  },
]);

const selectedAppearance = computed(() => {
  return darkMode.value
    ? themeStore.currentUnifiedDarkStyle
    : "light";
});

const currentAppearance = computed(() => {
  return (
    appearanceOptions.find(
      (option) => option.value === selectedAppearance.value
    ) || appearanceOptions[0]
  );
});

const currentFont = computed(() => {
  return (
    fontOptions.find(
      (option) => option.value === fontSize.value
    ) || fontOptions[1]
  );
});

const uiFontSize = computed({
  get: () => fontSize.value,

  set: (value) => {
    themeStore.setFontSize(value);
  },
});

const uiAnimations = computed({
  get: () => animations.value,

  set: (value) => {
    themeStore.setAnimations(value);
  },
});

const previewStyle = computed(() => {
  const preview = currentAppearance.value.preview;

  return {
    "--preview-bg": preview.bg,
    "--preview-card": preview.card,
    "--preview-line": preview.line,
    "--preview-text": preview.text,
    "--preview-muted": preview.muted,
    "--preview-accent": preview.accent,
    "--preview-font-size": uiFontSize.value,
  };
});

const getOptionStyle = (option) => {
  return {
    "--option-bg": option.preview.bg,
    "--option-card": option.preview.card,
    "--option-line": option.preview.line,
    "--option-text": option.preview.text,
    "--option-muted": option.preview.muted,
    "--option-accent": option.preview.accent,
  };
};

const selectAppearance = (value) => {
  themeStore.setAppearance(value);
};

const lockPageScroll = () => {
  if (typeof document === "undefined") return;

  previousBodyOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";
};

const unlockPageScroll = () => {
  if (typeof document === "undefined") return;

  document.body.style.overflow = previousBodyOverflow;
};

const openResetConfirm = async () => {
  if (showResetConfirm.value) return;

  showResetConfirm.value = true;
  lockPageScroll();

  await nextTick();

  cancelResetButton.value?.focus();
};

const closeResetConfirm = async () => {
  if (!showResetConfirm.value) return;

  showResetConfirm.value = false;
  unlockPageScroll();

  await nextTick();

  resetTrigger.value?.focus();
};

const confirmReset = () => {
  themeStore.reset();
  closeResetConfirm();
};

const handleDialogKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeResetConfirm();
    return;
  }

  if (event.key !== "Tab") return;

  const dialog = resetDialog.value;

  if (!dialog) return;

  const focusableElements = Array.from(
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
  );

  if (!focusableElements.length) {
    event.preventDefault();
    dialog.focus();
    return;
  }

  const firstElement = focusableElements[0];
  const lastElement =
    focusableElements[focusableElements.length - 1];

  const activeElement = document.activeElement;

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

onBeforeUnmount(() => {
  unlockPageScroll();
});
</script>

<style
  scoped
  src="./preferencias-interfaz.css"
></style>
