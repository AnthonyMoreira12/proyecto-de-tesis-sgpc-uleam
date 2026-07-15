<template>
  <div class="sgpc-config-page">
    <div class="config-shell">
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header
        class="config-hero page-stage page-hero page-stage-1"
        aria-labelledby="preferences-title"
      >
        <div class="config-hero__copy">
          <h1
            id="preferences-title"
            class="config-title"
          >
            Preferencias de interfaz
          </h1>

          <p class="config-lead">
            Personalice la apariencia, el tamaño del texto y el movimiento del
            sistema.
          </p>
        </div>

        <div
          class="config-autosave"
          role="status"
          aria-label="Los cambios se guardan automáticamente"
        >
          <span
            class="config-autosave__icon"
            aria-hidden="true"
          >
            <svg
              viewBox="0 0 24 24"
              focusable="false"
            >
              <path
                d="m7.5 12.5 3 3 6-7"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />

              <circle
                cx="12"
                cy="12"
                r="9"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
              />
            </svg>
          </span>

          <span>Guardado automático</span>
        </div>
      </header>

      <!-- =====================================================
           CONTENIDO
      ====================================================== -->
      <main class="config-layout page-stage page-content page-stage-2">
        <section
          class="config-primary page-stage page-main page-stage-3"
          aria-label="Configuración de la interfaz"
        >
          <!-- =================================================
               APARIENCIA
          ================================================== -->
          <article class="config-card config-card--appearance">
            <header class="section-head">
              <div class="section-head__copy">
                <span class="section-label">
                  Apariencia
                </span>

                <h2 class="card-title">
                  Estilo visual
                </h2>

                <p class="section-description">
                  Seleccione la identidad visual y el tema que desea utilizar.
                </p>
              </div>
            </header>

            <div class="config-sections">
              <!-- Perfil visual -->
              <section
                class="editor-block"
                aria-labelledby="profile-title"
              >
                <div class="editor-block__head">
                  <h3
                    id="profile-title"
                    class="editor-block__title"
                  >
                    Perfil
                  </h3>

                  <p class="editor-block__description">
                    Define el estilo general de la interfaz.
                  </p>
                </div>

                <div class="profile-options">
                  <button
                    v-for="profile in visualProfiles"
                    :key="profile.value"
                    class="profile-option"
                    :class="[
                      `profile-option--${profile.value}`,
                      {
                        active:
                          uiThemeProfile === profile.value,
                      },
                    ]"
                    type="button"
                    :aria-pressed="
                      uiThemeProfile === profile.value
                    "
                    @click="
                      uiThemeProfile = profile.value
                    "
                  >
                    <span
                      class="profile-option__preview"
                      aria-hidden="true"
                    >
                      <span class="profile-option__preview-top"></span>

                      <span class="profile-option__preview-layout">
                        <span class="profile-option__preview-sidebar"></span>

                        <span class="profile-option__preview-content">
                          <span></span>
                          <span></span>
                          <span></span>
                        </span>
                      </span>
                    </span>

                    <span class="profile-option__copy">
                      <span class="profile-option__title">
                        {{ profile.label }}
                      </span>

                      <span class="profile-option__desc">
                        {{ profile.desc }}
                      </span>
                    </span>

                    <span
                      class="option-check"
                      aria-hidden="true"
                    >
                      <svg
                        viewBox="0 0 20 20"
                        focusable="false"
                      >
                        <path
                          d="m5.5 10.2 2.8 2.8 6.2-6.2"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>
                  </button>
                </div>
              </section>

              <!-- Tema -->
              <section
                class="editor-block"
                aria-labelledby="theme-title"
              >
                <div class="editor-block__head">
                  <h3
                    id="theme-title"
                    class="editor-block__title"
                  >
                    Tema
                  </h3>

                  <p class="editor-block__description">
                    Cambie entre una interfaz clara u oscura.
                  </p>
                </div>

                <div class="mode-row">
                  <div class="mode-state">
                    <span
                      class="mode-state__icon"
                      aria-hidden="true"
                    >
                      <svg
                        v-if="uiDarkMode"
                        viewBox="0 0 24 24"
                        focusable="false"
                      >
                        <path
                          d="M20 15.4A8 8 0 0 1 8.6 4a8.2 8.2 0 1 0 11.4 11.4Z"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>

                      <svg
                        v-else
                        viewBox="0 0 24 24"
                        focusable="false"
                      >
                        <circle
                          cx="12"
                          cy="12"
                          r="4"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.8"
                        />

                        <path
                          d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                        />
                      </svg>
                    </span>

                    <span class="mode-state__copy">
                      <strong>
                        {{ currentModeLabel }}
                      </strong>

                      <span>
                        {{
                          uiDarkMode
                            ? "Reduce el brillo y utiliza superficies oscuras."
                            : "Utiliza fondos claros y mayor luminosidad."
                        }}
                      </span>
                    </span>
                  </div>

                  <label class="toggle toggle--large">
                    <span class="sr-only">
                      Activar modo oscuro
                    </span>

                    <input
                      v-model="uiDarkMode"
                      type="checkbox"
                    />

                    <span
                      class="track"
                      aria-hidden="true"
                    >
                      <span class="thumb"></span>
                    </span>
                  </label>
                </div>
              </section>

              <!-- Variante editorial -->
              <section
                v-if="isEditorialProfile"
                class="editor-block"
                aria-labelledby="variant-title"
              >
                <div class="editor-block__head">
                  <h3
                    id="variant-title"
                    class="editor-block__title"
                  >
                    Variante visual
                  </h3>

                  <p class="editor-block__description">
                    Seleccione la combinación de superficies que mejor se
                    adapte a su lectura.
                  </p>
                </div>

                <div class="surface-options">
                  <button
                    v-for="variant in variantOptions"
                    :key="variant.value"
                    class="surface-option"
                    type="button"
                    :class="{
                      active:
                        currentVariantValue === variant.value,
                    }"
                    :aria-pressed="
                      currentVariantValue === variant.value
                    "
                    :style="{
                      '--surface-bg': variant.preview.bg,
                      '--surface-card': variant.preview.card,
                      '--surface-line': variant.preview.line,
                    }"
                    @click="changeVariant(variant.value)"
                  >
                    <span
                      class="surface-option__preview"
                      aria-hidden="true"
                    >
                      <span class="surface-option__preview-shell">
                        <span class="surface-option__preview-top"></span>

                        <span class="surface-option__preview-layout">
                          <span class="surface-option__preview-sidebar"></span>

                          <span class="surface-option__preview-body">
                            <span class="surface-option__preview-card"></span>

                            <span class="surface-option__preview-row">
                              <span></span>
                              <span></span>
                            </span>
                          </span>
                        </span>
                      </span>
                    </span>

                    <span class="surface-option__copy">
                      <span class="surface-option__title">
                        {{ variant.label }}
                      </span>

                      <span class="surface-option__desc">
                        {{ variant.desc }}
                      </span>
                    </span>

                    <span
                      class="option-check"
                      aria-hidden="true"
                    >
                      <svg
                        viewBox="0 0 20 20"
                        focusable="false"
                      >
                        <path
                          d="m5.5 10.2 2.8 2.8 6.2-6.2"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>
                  </button>
                </div>
              </section>
            </div>
          </article>

          <!-- =================================================
               ACCESIBILIDAD
          ================================================== -->
          <article class="config-card config-card--accessibility">
            <header class="section-head">
              <div class="section-head__copy">
                <span class="section-label">
                  Accesibilidad
                </span>

                <h2 class="card-title">
                  Texto y movimiento
                </h2>

                <p class="section-description">
                  Ajuste la lectura y reduzca los efectos visuales cuando sea
                  necesario.
                </p>
              </div>
            </header>

            <div class="config-sections">
              <!-- Tamaño del texto -->
              <section
                class="editor-block"
                aria-labelledby="font-title"
              >
                <div class="editor-block__head">
                  <h3
                    id="font-title"
                    class="editor-block__title"
                  >
                    Tamaño del texto
                  </h3>

                  <p class="editor-block__description">
                    El cambio se aplicará en las principales interfaces del
                    sistema.
                  </p>
                </div>

                <div class="font-options">
                  <button
                    v-for="option in fontOptions"
                    :key="option.value"
                    type="button"
                    class="font-option"
                    :class="{
                      active:
                        uiFontSize === option.value,
                    }"
                    :aria-pressed="
                      uiFontSize === option.value
                    "
                    @click="
                      uiFontSize = option.value
                    "
                  >
                    <span class="font-option__sample">
                      Aa
                    </span>

                    <span class="font-option__copy">
                      <span class="font-option__label">
                        {{ option.label }}
                      </span>

                      <span class="font-option__value">
                        {{ option.value }}
                      </span>
                    </span>

                    <span
                      class="option-check"
                      aria-hidden="true"
                    >
                      <svg
                        viewBox="0 0 20 20"
                        focusable="false"
                      >
                        <path
                          d="m5.5 10.2 2.8 2.8 6.2-6.2"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>
                  </button>
                </div>
              </section>

              <!-- Movimiento -->
              <section
                class="editor-block"
                aria-labelledby="motion-title"
              >
                <div class="motion-row">
                  <div class="motion-row__content">
                    <span
                      class="motion-row__icon"
                      aria-hidden="true"
                    >
                      <svg
                        viewBox="0 0 24 24"
                        focusable="false"
                      >
                        <path
                          d="M4 12h16M15 7l5 5-5 5M9 17l-5-5 5-5"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>

                    <span class="motion-row__copy">
                      <h3
                        id="motion-title"
                        class="editor-block__title"
                      >
                        Reducir movimiento
                      </h3>

                      <span>
                        Limita animaciones y transiciones decorativas.
                      </span>
                    </span>
                  </div>

                  <div class="motion-row__action">
                    <span class="motion-row__state">
                      {{ currentMotionLabel }}
                    </span>

                    <label class="toggle">
                      <span class="sr-only">
                        Reducir movimiento
                      </span>

                      <input
                        v-model="uiReduceMotion"
                        type="checkbox"
                      />

                      <span
                        class="track"
                        aria-hidden="true"
                      >
                        <span class="thumb"></span>
                      </span>
                    </label>
                  </div>
                </div>
              </section>
            </div>
          </article>
        </section>

        <!-- =================================================
             VISTA PREVIA Y RESTABLECIMIENTO
        ================================================== -->
        <aside
          class="config-sidebar page-stage page-sidebar page-stage-4"
          aria-label="Vista previa de preferencias"
        >
          <article class="config-card config-card--preview">
            <header class="section-head">
              <div class="section-head__copy">
                <span class="section-label">
                  Vista previa
                </span>

                <h2 class="card-title">
                  Resultado aproximado
                </h2>
              </div>
            </header>

            <div
              class="interface-preview"
              :class="{
                'is-dark': uiDarkMode,
                'is-editorial': isEditorialProfile,
              }"
              :style="previewStyle"
              aria-hidden="true"
            >
              <div class="preview-app">
                <div class="preview-app__sidebar">
                  <div class="preview-app__brand">
                    <span></span>
                    <strong>SGPC</strong>
                  </div>

                  <div class="preview-app__menu">
                    <span class="is-active"></span>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>

                <div class="preview-app__main">
                  <div class="preview-app__topbar">
                    <span class="preview-app__topbar-title"></span>

                    <span class="preview-app__avatar"></span>
                  </div>

                  <div class="preview-app__content">
                    <div class="preview-app__heading">
                      <strong class="preview-app__title">
                        Producción científica
                      </strong>

                      <span class="preview-app__subtitle">
                        Resumen institucional
                      </span>
                    </div>

                    <div class="preview-app__cards">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                    <div class="preview-app__panel">
                      <span class="preview-app__panel-line"></span>
                      <span class="preview-app__panel-line is-short"></span>

                      <span class="preview-app__button">
                        Acción principal
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <p class="preview-help">
              La vista previa representa los cambios principales. Algunas
              pantallas pueden presentar variaciones.
            </p>

            <div class="preview-current">
              <span>
                {{ currentProfileLabel }}
              </span>

              <span aria-hidden="true">•</span>

              <span>
                {{ currentModeLabel }}
              </span>

              <span aria-hidden="true">•</span>

              <span>
                {{ currentFontLabel }}
              </span>
            </div>
          </article>

          <section
            class="config-reset-panel"
            aria-labelledby="reset-title"
          >
            <div class="config-reset-panel__copy">
              <h2 id="reset-title">
                Restaurar preferencias
              </h2>

              <p>
                Recupera la apariencia y configuración inicial del sistema.
              </p>
            </div>

            <button
              class="btn-reset"
              type="button"
              @click="resetConfig"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
                focusable="false"
              >
                <path
                  d="M4 4v6h6M4.7 9.5A8 8 0 1 1 6 17.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>

              <span>
                Restaurar valores predeterminados
              </span>
            </button>
          </section>
        </aside>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { storeToRefs } from "pinia";

import {
  useThemeStore,
  SURFACE_PRESETS_LIGHT,
  UNIFIED_DARK_STYLE_PRESETS,
} from "../../scripts/stores/themeStore";

const themeStore = useThemeStore();

const {
  darkMode,
  themeProfile,
  primaryColor,
  fontSize,
  animations,
  surfacePresetLight,
} = storeToRefs(themeStore);

/* =========================================================
   OPCIONES
========================================================= */

const visualProfiles = [
  {
    value: "institutional",
    label: "Institucional",
    desc: "Diseño administrativo con acento azul y alta claridad visual.",
  },
  {
    value: "editorial",
    label: "Editorial",
    desc: "Diseño sobrio con superficies suaves y mayor contraste tipográfico.",
  },
];

const fontOptions = [
  {
    value: "16px",
    label: "Compacto",
  },
  {
    value: "17px",
    label: "Estándar",
  },
  {
    value: "20px",
    label: "Grande",
  },
  {
    value: "22px",
    label: "Muy grande",
  },
];

/* =========================================================
   MODELOS
========================================================= */

const uiDarkMode = computed({
  get: () => darkMode.value,

  set: (value) => {
    themeStore.setDark(value);
  },
});

const uiThemeProfile = computed({
  get: () => themeProfile.value,

  set: (value) => {
    themeStore.setThemeProfile(value);
  },
});

const uiSurfacePreset = computed({
  get: () => surfacePresetLight.value,

  set: (value) => {
    themeStore.setSurfacePreset(value);
  },
});

const uiFontSize = computed({
  get: () => fontSize.value,

  set: (value) => {
    themeStore.setFontSize(value);
  },
});

const uiReduceMotion = computed({
  get: () => !animations.value,

  set: (value) => {
    themeStore.setAnimations(!value);
  },
});

/* =========================================================
   PERFIL Y VARIANTES
========================================================= */

const isInstitutionalProfile = computed(() => {
  return uiThemeProfile.value === "institutional";
});

const isEditorialProfile = computed(() => {
  return uiThemeProfile.value === "editorial";
});

const surfaceOptions = computed(() => {
  return SURFACE_PRESETS_LIGHT;
});

const unifiedDarkStyleOptions = computed(() => {
  return UNIFIED_DARK_STYLE_PRESETS;
});

const currentUnifiedDarkStyle = computed(() => {
  return themeStore.currentUnifiedDarkStyle;
});

const variantOptions = computed(() => {
  if (!isEditorialProfile.value) {
    return [];
  }

  return uiDarkMode.value
    ? unifiedDarkStyleOptions.value
    : surfaceOptions.value;
});

const currentVariantValue = computed(() => {
  if (uiDarkMode.value) {
    return currentUnifiedDarkStyle.value;
  }

  return uiSurfacePreset.value;
});

const currentVariantMeta = computed(() => {
  return (
    variantOptions.value.find(
      (item) =>
        item.value === currentVariantValue.value
    ) ||
    variantOptions.value[0] ||
    null
  );
});

const changeVariant = (value) => {
  if (uiDarkMode.value) {
    themeStore.setUnifiedDarkStyle(value);
    return;
  }

  themeStore.setSurfacePreset(value);
};

/* =========================================================
   ETIQUETAS
========================================================= */

const currentProfileLabel = computed(() => {
  return isInstitutionalProfile.value
    ? "Institucional"
    : "Editorial";
});

const currentModeLabel = computed(() => {
  return uiDarkMode.value
    ? "Modo oscuro"
    : "Modo claro";
});

const currentFontLabel = computed(() => {
  return (
    fontOptions.find(
      (option) =>
        option.value === uiFontSize.value
    )?.label ||
    "Personalizado"
  );
});

const currentMotionLabel = computed(() => {
  return uiReduceMotion.value
    ? "Reducido"
    : "Activo";
});

/* =========================================================
   VISTA PREVIA
========================================================= */

const previewAccent = computed(() => {
  const selectedColor = String(
    primaryColor.value || ""
  ).trim();

  if (selectedColor) {
    return selectedColor;
  }

  if (isInstitutionalProfile.value) {
    return "#315fcb";
  }

  return uiDarkMode.value
    ? "#98a98d"
    : "#111111";
});

const previewSurface = computed(() => {
  if (isInstitutionalProfile.value) {
    if (uiDarkMode.value) {
      return {
        bg: "#0f1728",
        card: "#18243a",
        line: "rgba(255, 255, 255, 0.12)",
      };
    }

    return {
      bg: "#f3f6fb",
      card: "#ffffff",
      line: "rgba(23, 32, 51, 0.12)",
    };
  }

  const preview =
    currentVariantMeta.value?.preview;

  if (preview) {
    return preview;
  }

  if (uiDarkMode.value) {
    return {
      bg: "#111827",
      card: "#1f2937",
      line: "rgba(255, 255, 255, 0.12)",
    };
  }

  return {
    bg: "#f4f2ed",
    card: "#ffffff",
    line: "rgba(17, 17, 17, 0.12)",
  };
});

const previewStyle = computed(() => {
  return {
    "--preview-bg":
      previewSurface.value.bg,

    "--preview-card":
      previewSurface.value.card,

    "--preview-line":
      previewSurface.value.line,

    "--preview-accent":
      previewAccent.value,

    "--preview-font-size":
      uiFontSize.value,

    "--preview-ink":
      uiDarkMode.value
        ? "#f4f7fc"
        : "#172033",

    "--preview-muted":
      uiDarkMode.value
        ? "#aeb8ca"
        : "#667085",
  };
});

/* =========================================================
   RESTABLECER
========================================================= */

const resetConfig = () => {
  const accepted =
    typeof window === "undefined" ||
    window.confirm(
      "¿Desea restaurar las preferencias iniciales de la interfaz?"
    );

  if (!accepted) {
    return;
  }

  themeStore.reset();
};
</script>

<style
  scoped
  src="./preferencias-interfaz.css"
></style>