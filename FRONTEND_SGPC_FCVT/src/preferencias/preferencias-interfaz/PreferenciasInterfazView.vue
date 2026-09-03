<template>
  <div class="preferences-page">
    <div class="preferences-shell">
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header
        class="preferences-hero page-stage page-stage-1"
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
            <h1
              id="preferences-title"
              class="preferences-title"
            >
              Preferencias
            </h1>
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
          <span>Se guarda automáticamente</span>
        </div>
      </header>

      <!-- =====================================================
           CONTENIDO
      ====================================================== -->
      <main class="preferences-layout page-stage page-stage-2">
        <div class="preferences-main">
          <!-- =================================================
               APARIENCIA
          ================================================== -->
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
                    <circle cx="7.5" cy="10" r="1" fill="currentColor" />
                    <circle cx="10" cy="6.8" r="1" fill="currentColor" />
                    <circle cx="14" cy="6.5" r="1" fill="currentColor" />
                    <circle cx="17" cy="9" r="1" fill="currentColor" />
                  </svg>
                </span>

                <div>
                  <h2 id="appearance-title">
                    Tema
                  </h2>
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

          <!-- =================================================
               LEGIBILIDAD
          ================================================== -->
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
                  <h2 id="readability-title">
                    Tamaño del texto
                  </h2>
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
                </span>
              </button>
            </div>
          </section>

          <!-- =================================================
               MOVIMIENTO
          ================================================== -->
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
                  <h2 id="motion-title">
                    Animaciones
                  </h2>
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

            <div class="preference-inline-status">
              <span>Estado</span>
              <strong>
                {{ uiAnimations ? "Activadas" : "Desactivadas" }}
              </strong>
            </div>
          </section>

          <!-- =================================================
               NOTIFICACIONES
          ================================================== -->
          <section
            class="settings-card notification-settings-card"
            aria-labelledby="notification-sound-title"
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
                      d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-5v-5a7 7 0 0 0-5-6.71V4a2 2 0 1 0-4 0v1.29A7 7 0 0 0 5 12v5l-2 2h18l-2-2Zm-2 0H7v-5a5 5 0 0 1 10 0v5Z"
                      fill="currentColor"
                    />
                  </svg>
                </span>

                <div>
                  <h2 id="notification-sound-title">
                    Sonido de notificaciones
                  </h2>
                </div>
              </div>

              <label class="switch-control">
                <span class="sr-only">
                  Activar sonido de nuevas notificaciones
                </span>

                <input
                  v-model="notificationSoundEnabled"
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

            <div class="notification-sound-state">
              <div class="preference-inline-status notification-sound-state__status">
                <span>Estado</span>
                <strong>
                  {{ notificationSoundEnabled ? "Activado" : "Desactivado" }}
                </strong>
              </div>

              <div class="notification-volume-control">
                <label for="notification-volume">
                  <span>Volumen</span>
                  <strong>{{ notificationSoundVolume }}%</strong>
                </label>

                <input
                  id="notification-volume"
                  v-model.number="notificationSoundVolume"
                  class="notification-volume-control__range"
                  type="range"
                  min="25"
                  max="100"
                  step="5"
                  :disabled="!notificationSoundEnabled"
                  aria-label="Volumen del sonido de notificaciones"
                />
              </div>

              <button
                class="notification-sound-test"
                type="button"
                :disabled="!notificationSoundEnabled"
                @click="testNotificationSound"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M5 9v6h4l5 4V5L9 9H5Zm11.5 3a4.5 4.5 0 0 0-1.5-3.35v6.7A4.5 4.5 0 0 0 16.5 12Zm0-7.1v2.05a7 7 0 0 1 0 10.1v2.05a9 9 0 0 0 0-14.2Z"
                  />
                </svg>
                Probar sonido
              </button>
            </div>
          </section>
        </div>

        <!-- ===================================================
             VISTA PREVIA Y RESUMEN
        ==================================================== -->
        <aside class="preferences-sidebar">
          <section
            class="preview-card"
            aria-labelledby="preview-title"
          >
            <header class="preview-card__header">
              <div>
                <h2 id="preview-title">
                  Vista previa
                </h2>
              </div>
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
                      <strong>SGPC</strong>
                      
                    </div>

                    <span class="preview-dashboard__avatar"></span>
                  </header>

                  <div class="preview-dashboard__content">
                    <div class="preview-dashboard__welcome">
                      <div>
                        
                        <strong>Producción científica</strong>
                      </div>

                      <button type="button">
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
                <dd>{{ uiAnimations ? "Activo" : "Reducido" }}</dd>
              </div>
              <div>
                <dt>Notificaciones</dt>
                <dd>
                  {{
                    notificationSoundEnabled
                      ? `Activo · ${notificationSoundVolume}%`
                      : "Silenciado"
                  }}
                </dd>
              </div>
            </dl>
          </section>

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
                  Restaurar
                </h2>
              </div>
            </div>

            <button
              class="reset-button"
              type="button"
              @click="resetConfig"
            >
              Restaurar preferencias
            </button>
          </section>
        </aside>
      </main>
    </div>

    <NoticeDialog
      :modelValue="notice"
      @close="closeNotice"
    />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { storeToRefs } from "pinia";

import {
  APPEARANCE_PRESETS,
  useThemeStore,
} from "../../scripts/stores/themeStore";
import { useNotificacionesStore } from
  "../../scripts/stores/notificacionesStore";
import { useNotice } from "../../scripts/composables/useNotice";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";

const themeStore = useThemeStore();
const notificationsStore = useNotificacionesStore();

const {
  notice,
  openNotice,
  closeNotice,
} = useNotice();

const {
  darkMode,
  fontSize,
  animations,
} = storeToRefs(themeStore);

const {
  soundEnabled,
  soundVolume,
} = storeToRefs(
  notificationsStore
);

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

const uiFontSize = computed({
  get: () => fontSize.value,
  set: (value) => themeStore.setFontSize(value),
});

const uiAnimations = computed({
  get: () => animations.value,
  set: (value) => themeStore.setAnimations(value),
});

const notificationSoundEnabled = computed({
  get: () => soundEnabled.value,
  set: (value) =>
    notificationsStore.setSoundEnabled(value),
});

const notificationSoundVolume = computed({
  get: () => Math.max(
    25,
    Math.round(
      Number(soundVolume.value || 0) * 100
    )
  ),
  set: (value) => {
    const normalized = Math.min(
      100,
      Math.max(25, Number(value) || 25)
    );

    notificationsStore.setSoundVolume(
      normalized / 100
    );
  },
});

const testNotificationSound = async () => {
  if (!notificationSoundEnabled.value) {
    return;
  }

  await notificationsStore.testSound();
};

const currentFont = computed(() => {
  return (
    fontOptions.find(
      (option) => option.value === uiFontSize.value
    ) || fontOptions[1]
  );
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

const resetConfig = () => {
  openNotice({
    title: "Restaurar preferencias",
    message:
      "Se restaurarán todas las preferencias a sus valores iniciales.",
    confirm: true,
    confirmText: "Restaurar preferencias",
    cancelText: "Cancelar",
    onConfirm: () => {
      themeStore.reset();
      notificationsStore.resetPreferences();
    },
  });
};

</script>

<style
  scoped
  src="./preferencias-interfaz.css"
></style>
