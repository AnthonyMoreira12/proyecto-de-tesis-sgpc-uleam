<template>
  <div class="sgpc-config-page">
    <div class="config-shell">
      <header class="config-hero page-stage page-hero page-stage-1">
        <div class="config-hero__top">
          <span class="config-kicker">Preferencias</span>
          <h1 class="config-title">Preferencias de interfaz</h1>
          <p class="config-lead">
            Ajuste apariencia, lectura y movimiento desde una sola vista.
          </p>
        </div>

        <div class="config-hero__meta" aria-label="Resumen actual">
          <span class="config-chip">{{ uiDarkMode ? "Oscuro" : "Claro" }}</span>
          <span class="config-chip">{{ currentProfileLabel }}</span>
          <span class="config-chip">
            {{ showUnifiedDarkStyles ? currentUnifiedDarkStyleLabel : currentSurfaceLabel }}
          </span>
          <span class="config-chip">{{ currentColorLabel }}</span>
          <span class="config-chip">{{ currentFontLabel }}</span>
          <span class="config-chip">{{ currentAnimationsLabel }}</span>
        </div>
      </header>

      <main class="config-layout page-stage page-content page-stage-2">
        <section
          class="config-primary page-stage page-main page-stage-3"
          aria-label="Preferencias de interfaz"
        >
          <article class="config-card config-card--appearance">
            <div class="section-head">
              <div class="section-head__copy">
                <span class="section-label">Apariencia</span>
                <h2 class="card-title">Tema, estilo y acento</h2>
              </div>

              <span class="section-note">
                {{ uiDarkMode ? "Modo oscuro" : "Modo claro" }}
              </span>
            </div>

            <div class="appearance-grid">
              <section class="editor-block">
                <div class="editor-block__head">
                  <h3 class="editor-block__title">Perfil visual</h3>
                </div>

                <div class="profile-options" role="list">
                  <button
                    v-for="profile in visualProfiles"
                    :key="profile.value"
                    class="profile-option"
                    :class="[
                      `profile-option--${profile.value}`,
                      { active: uiThemeProfile === profile.value }
                    ]"
                    type="button"
                    role="listitem"
                    @click="uiThemeProfile = profile.value"
                    :aria-label="`Seleccionar perfil ${profile.label}`"
                  >
                    <span class="profile-option__preview" aria-hidden="true">
                      <span class="profile-option__preview-top"></span>
                      <span class="profile-option__preview-body">
                        <span></span>
                        <span></span>
                        <span></span>
                      </span>
                    </span>

                    <span class="profile-option__copy">
                      <span class="profile-option__title">{{ profile.label }}</span>
                      <span class="profile-option__desc">{{ profile.desc }}</span>
                    </span>
                  </button>
                </div>
              </section>

              <section class="editor-block">
                <div class="editor-block__head">
                  <h3 class="editor-block__title">Modo base</h3>
                </div>

                <div class="mode-row">
                  <div class="mode-state">
                    <strong>{{ uiDarkMode ? "Oscuro" : "Claro" }}</strong>
                    <span>{{ currentModeDetail }}</span>
                  </div>

                  <label class="toggle toggle--large" aria-label="Modo oscuro">
                    <input type="checkbox" v-model="uiDarkMode" />
                    <span class="track" aria-hidden="true">
                      <span class="thumb" />
                    </span>
                  </label>
                </div>
              </section>

              <template v-if="isEditorialProfile">
                <section v-if="!uiDarkMode" class="editor-block">
                  <div class="editor-block__head">
                    <h3 class="editor-block__title">Superficies claras</h3>
                  </div>

                  <div class="surface-options" role="list">
                    <button
                      v-for="surface in surfaceOptions"
                      :key="surface.value"
                      class="surface-option"
                      type="button"
                      role="listitem"
                      :class="{ active: uiSurfacePreset === surface.value }"
                      :style="{
                        '--surface-bg': surface.preview.bg,
                        '--surface-card': surface.preview.card,
                        '--surface-line': surface.preview.line
                      }"
                      @click="changeSurfacePreset(surface.value)"
                      :aria-label="`Seleccionar superficie ${surface.label}`"
                    >
                      <span class="surface-option__preview" aria-hidden="true">
                        <span class="surface-option__preview-shell">
                          <span
                            class="surface-option__preview-card surface-option__preview-card--lg"
                          ></span>
                          <span class="surface-option__preview-row">
                            <span class="surface-option__preview-card"></span>
                            <span class="surface-option__preview-card"></span>
                          </span>
                        </span>
                      </span>

                      <span class="surface-option__copy">
                        <span class="surface-option__title">{{ surface.label }}</span>
                        <span class="surface-option__desc">{{ surface.desc }}</span>
                      </span>
                    </button>
                  </div>
                </section>

                <section v-else class="editor-block">
                  <div class="editor-block__head">
                    <h3 class="editor-block__title">Combinaciones oscuras</h3>
                  </div>

                  <div class="surface-options" role="list">
                    <button
                      v-for="style in unifiedDarkStyleOptions"
                      :key="style.value"
                      class="surface-option"
                      type="button"
                      role="listitem"
                      :class="{ active: currentUnifiedDarkStyle === style.value }"
                      :style="{
                        '--surface-bg': style.preview.bg,
                        '--surface-card': style.preview.card,
                        '--surface-line': style.preview.line
                      }"
                      @click="changeUnifiedDarkStyle(style.value)"
                      :aria-label="`Seleccionar combinación ${style.label}`"
                    >
                      <span class="surface-option__preview" aria-hidden="true">
                        <span class="surface-option__preview-shell">
                          <span
                            class="surface-option__preview-card surface-option__preview-card--lg"
                          ></span>
                          <span class="surface-option__preview-row">
                            <span class="surface-option__preview-card"></span>
                            <span class="surface-option__preview-card"></span>
                          </span>
                        </span>
                      </span>

                      <span class="surface-option__copy">
                        <span class="surface-option__title">{{ style.label }}</span>
                        <span class="surface-option__desc">{{ style.desc }}</span>
                      </span>
                    </button>
                  </div>
                </section>

                <section class="editor-block">
                  <div class="editor-block__head">
                    <h3 class="editor-block__title">Acento editorial</h3>
                  </div>

                  <div class="color-options" role="list">
                    <button
                      v-for="color in editorialAccentOptions"
                      :key="color.value"
                      class="color-option"
                      type="button"
                      role="listitem"
                      :class="{ active: isEditorialAccentActive }"
                      :style="{ '--chip-color': color.value }"
                      @click="changeTheme(color.value)"
                      :aria-label="`Seleccionar acento ${color.label}`"
                    >
                      <span class="color-option__left">
                        <span class="color-option__swatch" aria-hidden="true"></span>

                        <span class="color-option__copy">
                          <span class="color-option__title">{{ color.label }}</span>
                          <span class="color-option__desc">{{ color.desc }}</span>
                        </span>
                      </span>
                    </button>
                  </div>
                </section>
              </template>

              <template v-else>
                <section class="editor-block">
                  <div class="editor-block__head">
                    <h3 class="editor-block__title">Perfil estándar</h3>
                  </div>

                  <div class="institutional-mode">
                    <span class="institutional-mode__preview" aria-hidden="true">
                      <span class="institutional-mode__preview-top"></span>
                      <span class="institutional-mode__preview-body">
                        <span></span>
                        <span></span>
                        <span></span>
                      </span>
                    </span>

                    <div class="institutional-mode__copy">
                      <strong>
                        {{ uiDarkMode ? "Oscuro institucional" : "Claro institucional" }}
                      </strong>
                      <span>
                        {{
                          uiDarkMode
                            ? "Usa la base institucional oscura con acento azul estándar."
                            : "Usa la base institucional clara con acento azul estándar."
                        }}
                      </span>
                    </div>
                  </div>
                </section>
              </template>
            </div>
          </article>

          <article class="config-card config-card--reading">
            <div class="section-head">
              <div class="section-head__copy">
                <span class="section-label">Lectura</span>
                <h2 class="card-title">Fuente y movimiento</h2>
              </div>

              <span class="section-note">{{ currentFontLabel }}</span>
            </div>

            <div class="reading-grid">
              <section class="editor-block">
                <div class="editor-block__head">
                  <h3 class="editor-block__title">Tamaño tipográfico</h3>
                </div>

                <div class="font-options" role="list">
                  <button
                    v-for="option in fontOptions"
                    :key="option.value"
                    type="button"
                    role="listitem"
                    class="font-option"
                    :class="{ active: uiFontSize === option.value }"
                    @click="uiFontSize = option.value"
                    :aria-label="`Seleccionar tamaño ${option.label}`"
                  >
                    <span class="font-option__label">{{ option.label }}</span>
                    <span class="font-option__value">{{ option.value }}</span>
                  </button>
                </div>
              </section>

              <section class="editor-block">
                <div class="motion-row">
                  <div class="motion-row__copy">
                    <h3 class="editor-block__title">Movimiento</h3>
                  </div>

                  <div class="motion-row__action">
                    <span class="motion-row__state">{{ currentAnimationsLabel }}</span>

                    <label class="toggle" aria-label="Animaciones">
                      <input type="checkbox" v-model="uiAnimations" />
                      <span class="track" aria-hidden="true">
                        <span class="thumb" />
                      </span>
                    </label>
                  </div>
                </div>
              </section>
            </div>
          </article>
        </section>

        <aside
          class="config-sidebar page-stage page-sidebar page-stage-4"
          aria-label="Estado actual"
        >
          <article class="config-card config-card--summary">
            <div class="section-head">
              <div class="section-head__copy">
                <span class="section-label">Estado actual</span>
                <h2 class="card-title">Resumen</h2>
              </div>
            </div>

            <dl class="config-review__list">
              <div>
                <dt>Perfil</dt>
                <dd>{{ currentProfileLabel }}</dd>
              </div>

              <div>
                <dt>Tema</dt>
                <dd>{{ uiDarkMode ? "Oscuro" : "Claro" }}</dd>
              </div>

              <div v-if="showUnifiedDarkStyles">
                <dt>Combinación</dt>
                <dd>{{ currentUnifiedDarkStyleLabel }}</dd>
              </div>

              <template v-else>
                <div>
                  <dt>Superficie</dt>
                  <dd>{{ currentSurfaceLabel }}</dd>
                </div>

                <div>
                  <dt>Estilo</dt>
                  <dd>{{ currentModeDetail }}</dd>
                </div>
              </template>

              <div>
                <dt>Acento</dt>
                <dd>{{ currentColorLabel }}</dd>
              </div>

              <div>
                <dt>Fuente</dt>
                <dd>{{ currentFontLabel }}</dd>
              </div>

              <div>
                <dt>Movimiento</dt>
                <dd>{{ currentAnimationsLabel }}</dd>
              </div>
            </dl>
          </article>

          <article class="config-card config-card--reset">
            <div class="section-head">
              <div class="section-head__copy">
                <span class="section-label">Preferencias</span>
                <h2 class="card-title">Restablecer</h2>
              </div>
            </div>

            <button class="btn-reset" type="button" @click="resetConfig">
              Restaurar preferencias iniciales
            </button>
          </article>
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
  hasCustomPrimary,
  surfacePresetLight,
} = storeToRefs(themeStore);

const visualProfiles = [
  {
    value: "institutional",
    label: "Institucional",
    desc: "Base sobria con acento azul estándar",
  },
  {
    value: "editorial",
    label: "Editorial",
    desc: "Modo claro sobrio y combinaciones oscuras definidas",
  },
];

const fontOptions = [
  { value: "16px", label: "Estándar" },
  { value: "17px", label: "Cómoda" },
  { value: "18px", label: "Amplia" },
  { value: "20px", label: "Lectura" },
  { value: "22px", label: "Visible" },
  { value: "24px", label: "Extra visible" },
];

const uiDarkMode = computed({
  get: () => darkMode.value,
  set: (v) => themeStore.setDark(v),
});

const uiThemeProfile = computed({
  get: () => themeProfile.value,
  set: (v) => themeStore.setThemeProfile(v),
});

const uiSurfacePreset = computed({
  get: () => surfacePresetLight.value,
  set: (v) => themeStore.setSurfacePreset(v),
});

const uiFontSize = computed({
  get: () => fontSize.value,
  set: (v) => themeStore.setFontSize(v),
});

const uiAnimations = computed({
  get: () => animations.value,
  set: (v) => themeStore.setAnimations(v),
});

const isInstitutionalProfile = computed(() => uiThemeProfile.value === "institutional");
const isEditorialProfile = computed(() => uiThemeProfile.value === "editorial");
const showUnifiedDarkStyles = computed(() => isEditorialProfile.value && uiDarkMode.value);

const surfaceOptions = computed(() => SURFACE_PRESETS_LIGHT);
const unifiedDarkStyleOptions = computed(() => UNIFIED_DARK_STYLE_PRESETS);

const currentUnifiedDarkStyle = computed(() => themeStore.currentUnifiedDarkStyle);

const currentUnifiedDarkStyleMeta = computed(() => {
  return (
    unifiedDarkStyleOptions.value.find(
      (item) => item.value === currentUnifiedDarkStyle.value
    ) || unifiedDarkStyleOptions.value[0]
  );
});

const currentUnifiedDarkStyleLabel = computed(() => {
  return currentUnifiedDarkStyleMeta.value?.label || "Obsidian + Sage";
});

const currentProfileLabel = computed(() => {
  return isInstitutionalProfile.value ? "Institucional" : "Editorial";
});

const currentSurfaceLabel = computed(() => {
  if (isInstitutionalProfile.value) {
    return uiDarkMode.value ? "Institucional oscura" : "Institucional clara";
  }

  return (
    surfaceOptions.value.find((item) => item.value === uiSurfacePreset.value)?.label ||
    "Editorial"
  );
});

const currentModeDetail = computed(() => {
  if (isInstitutionalProfile.value) {
    return uiDarkMode.value ? "Oscuro institucional" : "Claro institucional";
  }

  if (uiDarkMode.value) {
    return currentUnifiedDarkStyleLabel.value;
  }

  return "Base clara editorial";
});

const editorialAccentValue = computed(() => "#111111");

const editorialAccentOptions = computed(() => [
  {
    value: editorialAccentValue.value,
    label: "Editorial",
    desc: "Negro sobrio combinable con cualquier modo",
  },
]);

const themeColor = computed(() => String(primaryColor.value || "").toLowerCase());

const isEditorialAccentActive = computed(() => {
  if (!isEditorialProfile.value) return false;

  if (!uiDarkMode.value && !hasCustomPrimary.value) {
    return true;
  }

  return hasCustomPrimary.value && themeColor.value === editorialAccentValue.value;
});

const currentColorLabel = computed(() => {
  if (isInstitutionalProfile.value) {
    return "Azul institucional";
  }

  if (uiDarkMode.value) {
    return hasCustomPrimary.value
      ? "Editorial"
      : currentUnifiedDarkStyleMeta.value?.accentLabel || "Sage";
  }

  return "Editorial";
});

const currentFontLabel = computed(() => {
  return fontOptions.find((option) => option.value === uiFontSize.value)?.label || "Cómoda";
});

const currentAnimationsLabel = computed(() => {
  return uiAnimations.value ? "Activo" : "Reducido";
});

const changeTheme = (color) => themeStore.setPrimaryColor(color);
const changeSurfacePreset = (value) => themeStore.setSurfacePreset(value);
const changeUnifiedDarkStyle = (value) => themeStore.setUnifiedDarkStyle(value);
const resetConfig = () => themeStore.reset();
</script>

<style scoped src="./preferencias-interfaz.css"></style>