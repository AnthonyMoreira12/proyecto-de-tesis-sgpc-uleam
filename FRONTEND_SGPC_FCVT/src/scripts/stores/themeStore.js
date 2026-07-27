import { defineStore } from "pinia";
import {
  TRANSICIONES_RUTA,
  TRANSICION_RUTA_DEFAULT,
  getRouteTransitionPreset,
  normalizeRouteTransition,
} from "../utils/transicionesRuta";

/* ============================================================
   SGPC ULEAM — STORE GLOBAL DE APARIENCIA
============================================================ */

const STORAGE = Object.freeze({
  theme: "sgpc-theme",
  darkVariant: "sgpc-dark-variant",
  fontSize: "sgpc-fontSize",
  animations: "sgpc-animations",
  routeTransition: "sgpc-route-transition",
  surfaceLight: "sgpc-surface-light",
  surfaceDark: "sgpc-surface-dark",
  themeProfile: "sgpc-theme-profile",
  oldColor: "sgpc-color",
});

const LEGACY_STORAGE = Object.freeze([
  "darkMode",
  "themeColor",
  "fontSize",
  "animations",
  "sgpc-mono-dark",
]);

const DEFAULT_THEME = "light";
const DEFAULT_DARK_VARIANT = "black-white";
const DEFAULT_FONT_SIZE = "16px";
const DEFAULT_THEME_PROFILE = "institutional";
const DEFAULT_LIGHT_SURFACE = "standard-light";

const FONT_SIZES = Object.freeze([
  "15px",
  "16px",
  "18px",
  "20px",
]);

const DARK_VARIANTS = Object.freeze([
  "black-white",
  "dark-gray",
  "electric-blue",
  "institutional-blue",
  "crimson-black",
]);

const DARK_VARIANT_CLASSES = Object.freeze([
  "dark-black-white",
  "dark-dark-gray",
  "dark-electric-blue",
  "dark-institutional-blue",
  "dark-crimson-black",

  /* Compatibilidad con clases antiguas. */
  "dark-obsidian",
  "dark-slate-pro",
  "dark-midnight-blue",
  "dark-graphite",
  "dark-neon-noir",
  "dark-oled-black",
  "dark-plum-night",
  "dark-forest-night",
  "mono-dark",
]);

const CSS_VARIABLE_MAP = Object.freeze({
  accent: "--color-primary-default",
  accentContrast: "--accent-contrast",

  bgMain: "--bg-main",
  bgCard: "--bg-card",
  bgNavbar: "--bg-navbar",
  bgInput: "--bg-input",
  bgElevated: "--bg-elevated",
  bgSoft: "--bg-soft",
  overlay: "--overlay",
  cardHoverBg: "--card-hover-bg",

  textPrimary: "--text-primary",
  textSecondary: "--text-secondary",
  textInverse: "--text-inverse",
  textDisabled: "--text-disabled",

  borderColor: "--border-color",
  borderStrong: "--border-strong",
  lineSoft: "--line-soft",

  shadowSoft: "--shadow-soft",
  shadowStrong: "--shadow-strong",
  shadowHover: "--shadow-hover",

  hover: "--hover",
  active: "--active",

  focusOutline: "--focus-outline",
  focusRing: "--focus-ring",

  footerBg: "--footer-bg",
  footerText: "--footer-text",
  footerMuted: "--footer-muted",
});

function createPreset({
  value,
  label,
  desc,
  mode,
  variant,
  accent,
  accentContrast,
  preview,
  palette,
}) {
  const surface =
    mode === "light"
      ? DEFAULT_LIGHT_SURFACE
      : `${variant}-surface`;

  return Object.freeze({
    value,
    label,
    desc,
    mode,
    variant,
    surface,
    accent,
    accentContrast,
    accentLabel: label,

    preview: Object.freeze(preview),

    palette: Object.freeze({
      ...palette,
      accent,
      accentContrast,
    }),

    vars: Object.freeze({
      bgMain: palette.bgMain,
      bgCard: palette.bgCard,
      bgNavbar: palette.bgNavbar,
      bgInput: palette.bgInput,
      bgElevated: palette.bgElevated,
      bgSoft: palette.bgSoft,
      overlay: palette.overlay,
      cardHoverBg: palette.cardHoverBg,
    }),

    profile: Object.freeze({
      colorPrimaryDefault: accent,
      textPrimary: palette.textPrimary,
      textSecondary: palette.textSecondary,
      textInverse: palette.textInverse,
      textDisabled: palette.textDisabled,
      borderColor: palette.borderColor,
      borderStrong: palette.borderStrong,
      lineSoft: palette.lineSoft,
      shadowSoft: palette.shadowSoft,
      shadowStrong: palette.shadowStrong,
      shadowHover: palette.shadowHover,
      hover: palette.hover,
      active: palette.active,
      footerBg: palette.footerBg,
      footerText: palette.footerText,
      footerMuted: palette.footerMuted,
    }),
  });
}

/* ============================================================
   TEMA CLARO
============================================================ */

const LIGHT_PRESET = createPreset({
  value: "light",
  label: "Claro estándar",
  desc: "Blanco, gris claro y azul institucional",
  mode: "light",
  variant: null,

  accent: "#1d4ed8",
  accentContrast: "#ffffff",

  preview: {
    bg: "#f4f6f8",
    card: "#ffffff",
    line: "#d9e0e8",
    text: "#111827",
    muted: "#5f6b7a",
    accent: "#1d4ed8",
  },

  palette: {
    bgMain: "#f4f6f8",
    bgCard: "#ffffff",
    bgNavbar: "#ffffff",
    bgInput: "#ffffff",
    bgElevated: "#ffffff",
    bgSoft: "#eef2f6",
    overlay: "rgba(15, 23, 42, 0.55)",
    cardHoverBg: "#ffffff",

    textPrimary: "#111827",
    textSecondary: "#5f6b7a",
    textInverse: "#ffffff",
    textDisabled: "#9aa3af",

    borderColor: "#d9e0e8",
    borderStrong: "#bdc8d5",
    lineSoft: "#e8edf2",

    shadowSoft:
      "0 6px 18px rgba(15, 23, 42, 0.06)",

    shadowStrong:
      "0 18px 40px rgba(15, 23, 42, 0.12)",

    shadowHover:
      "0 10px 24px rgba(15, 23, 42, 0.09)",

    hover: "#f1f5f9",
    active: "#e7eef8",

    focusOutline: "#1d4ed8",
    focusRing: "rgba(29, 78, 216, 0.18)",

    footerBg: "#12233d",
    footerText: "#ffffff",
    footerMuted: "#c5d0df",
  },
});

/* ============================================================
   TEMAS OSCUROS
============================================================ */

const DARK_PRESETS = Object.freeze([
  createPreset({
    value: "black-white",
    label: "Negro y blanco",
    desc: "Negro absoluto, blanco puro y grises neutros",
    mode: "dark",
    variant: "black-white",

    accent: "#ffffff",
    accentContrast: "#000000",

    preview: {
      bg: "#000000",
      card: "#0b0b0b",
      line: "#292929",
      text: "#ffffff",
      muted: "#b8b8b8",
      accent: "#ffffff",
    },

    palette: {
      bgMain: "#000000",
      bgCard: "#0b0b0b",
      bgNavbar: "#000000",
      bgInput: "#161616",
      bgElevated: "#111111",
      bgSoft: "#151515",
      overlay: "rgba(0, 0, 0, 0.82)",
      cardHoverBg: "#111111",

      textPrimary: "#ffffff",
      textSecondary: "#b8b8b8",
      textInverse: "#000000",
      textDisabled: "#737373",

      borderColor: "#292929",
      borderStrong: "#444444",
      lineSoft: "#1d1d1d",

      shadowSoft: "none",

      shadowStrong:
        "0 18px 42px rgba(0, 0, 0, 0.80)",

      shadowHover: "none",

      hover: "#151515",
      active: "#242424",

      focusOutline: "#ffffff",
      focusRing: "rgba(255, 255, 255, 0.20)",

      footerBg: "#000000",
      footerText: "#ffffff",
      footerMuted: "#b8b8b8",
    },
  }),

  createPreset({
    value: "dark-gray",
    label: "Gris oscuro",
    desc: "Modo oscuro convencional y completamente neutro",
    mode: "dark",
    variant: "dark-gray",

    accent: "#ffffff",
    accentContrast: "#111111",

    preview: {
      bg: "#121212",
      card: "#1b1b1b",
      line: "#373737",
      text: "#ffffff",
      muted: "#bdbdbd",
      accent: "#ffffff",
    },

    palette: {
      bgMain: "#121212",
      bgCard: "#1b1b1b",
      bgNavbar: "#171717",
      bgInput: "#242424",
      bgElevated: "#202020",
      bgSoft: "#252525",
      overlay: "rgba(0, 0, 0, 0.76)",
      cardHoverBg: "#202020",

      textPrimary: "#ffffff",
      textSecondary: "#bdbdbd",
      textInverse: "#111111",
      textDisabled: "#777777",

      borderColor: "#373737",
      borderStrong: "#505050",
      lineSoft: "#2a2a2a",

      shadowSoft: "none",

      shadowStrong:
        "0 18px 42px rgba(0, 0, 0, 0.62)",

      shadowHover: "none",

      hover: "#292929",
      active: "#343434",

      focusOutline: "#ffffff",
      focusRing: "rgba(255, 255, 255, 0.18)",

      footerBg: "#0d0d0d",
      footerText: "#ffffff",
      footerMuted: "#bdbdbd",
    },
  }),

  createPreset({
    value: "electric-blue",
    label: "Azul eléctrico",
    desc: "Negro neutro con azul eléctrico y texto blanco",
    mode: "dark",
    variant: "electric-blue",

    accent: "#0066ff",
    accentContrast: "#ffffff",

    preview: {
      bg: "#000000",
      card: "#0d0d0d",
      line: "#2d2d2d",
      text: "#ffffff",
      muted: "#b8b8b8",
      accent: "#0066ff",
    },

    palette: {
      bgMain: "#000000",
      bgCard: "#0d0d0d",
      bgNavbar: "#000000",
      bgInput: "#171717",
      bgElevated: "#121212",
      bgSoft: "#151515",
      overlay: "rgba(0, 0, 0, 0.82)",
      cardHoverBg: "#121212",

      textPrimary: "#ffffff",
      textSecondary: "#b8b8b8",
      textInverse: "#ffffff",
      textDisabled: "#737373",

      borderColor: "#2d2d2d",
      borderStrong: "#484848",
      lineSoft: "#1d1d1d",

      shadowSoft: "none",

      shadowStrong:
        "0 18px 42px rgba(0, 0, 0, 0.80)",

      shadowHover: "none",

      hover: "#101722",
      active: "#112440",

      focusOutline: "#0066ff",
      focusRing: "rgba(0, 102, 255, 0.25)",

      footerBg: "#000000",
      footerText: "#ffffff",
      footerMuted: "#b8b8b8",
    },
  }),

  createPreset({
    value: "institutional-blue",
    label: "Azul institucional",
    desc: "Azul oscuro sólido con acento azul brillante",
    mode: "dark",
    variant: "institutional-blue",

    accent: "#1683ff",
    accentContrast: "#ffffff",

    preview: {
      bg: "#07111f",
      card: "#0d1a2b",
      line: "#29405f",
      text: "#ffffff",
      muted: "#b9c5d6",
      accent: "#1683ff",
    },

    palette: {
      bgMain: "#07111f",
      bgCard: "#0d1a2b",
      bgNavbar: "#091525",
      bgInput: "#132238",
      bgElevated: "#102038",
      bgSoft: "#102038",
      overlay: "rgba(0, 5, 14, 0.82)",
      cardHoverBg: "#102038",

      textPrimary: "#ffffff",
      textSecondary: "#b9c5d6",
      textInverse: "#ffffff",
      textDisabled: "#73829a",

      borderColor: "#29405f",
      borderStrong: "#3c5d87",
      lineSoft: "#1a2d48",

      shadowSoft: "none",

      shadowStrong:
        "0 18px 42px rgba(0, 5, 14, 0.66)",

      shadowHover: "none",

      hover: "#10233c",
      active: "#153052",

      focusOutline: "#1683ff",
      focusRing: "rgba(22, 131, 255, 0.26)",

      footerBg: "#030a13",
      footerText: "#ffffff",
      footerMuted: "#b9c5d6",
    },
  }),

  createPreset({
    value: "crimson-black",
    label: "Negro y rojo intenso",
    desc: "Negro absoluto con rojo sólido e intenso",
    mode: "dark",
    variant: "crimson-black",

    accent: "#ff1744",
    accentContrast: "#ffffff",

    preview: {
      bg: "#000000",
      card: "#080808",
      line: "#7a0018",
      text: "#ffffff",
      muted: "#c8c8c8",
      accent: "#ff1744",
    },

    palette: {
      bgMain: "#000000",
      bgCard: "#080808",
      bgNavbar: "#000000",
      bgInput: "#111111",
      bgElevated: "#0d0d0d",
      bgSoft: "#151515",
      overlay: "rgba(0, 0, 0, 0.86)",
      cardHoverBg: "#101010",

      textPrimary: "#ffffff",
      textSecondary: "#c8c8c8",
      textInverse: "#ffffff",
      textDisabled: "#777777",

      borderColor: "#7a0018",
      borderStrong: "#c4002f",
      lineSoft: "#2b0009",

      shadowSoft: "none",

      shadowStrong:
        "0 18px 42px rgba(0, 0, 0, 0.84)",

      shadowHover: "none",

      hover: "#190006",
      active: "#ff1744",

      focusOutline: "#ff3159",
      focusRing: "rgba(255, 23, 68, 0.34)",

      footerBg: "#000000",
      footerText: "#ffffff",
      footerMuted: "#c8c8c8",
    },
  }),
]);

/* ============================================================
   EXPORTACIONES PARA PREFERENCIAS
============================================================ */

export const SURFACE_PRESETS_LIGHT = Object.freeze([
  {
    value: DEFAULT_LIGHT_SURFACE,
    label: LIGHT_PRESET.label,
    desc: LIGHT_PRESET.desc,
    preview: LIGHT_PRESET.preview,
    vars: LIGHT_PRESET.vars,
  },
]);

export const SURFACE_PRESETS_DARK = Object.freeze(
  DARK_PRESETS.map((preset) => ({
    value: preset.surface,
    label: preset.label,
    desc: preset.desc,
    preview: preset.preview,
    vars: preset.vars,
  }))
);

export const UNIFIED_DARK_STYLE_PRESETS =
  DARK_PRESETS;

export const APPEARANCE_PRESETS = Object.freeze([
  LIGHT_PRESET,
  ...DARK_PRESETS,
]);

/* ============================================================
   UTILIDADES
============================================================ */

function getStorage(key, fallback = null) {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

function setStorage(key, value) {
  try {
    localStorage.setItem(key, String(value));
  } catch {
    // El navegador puede bloquear localStorage.
  }
}

function removeStorage(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    // Sin acción.
  }
}

function getRoot() {
  return typeof document === "undefined"
    ? null
    : document.documentElement;
}

function normalizeFontSize(value) {
  return FONT_SIZES.includes(value)
    ? value
    : DEFAULT_FONT_SIZE;
}

function normalizeDarkVariant(value) {
  const aliases = {
    obsidian: "black-white",
    "oled-black": "black-white",
    "oled-black-surface": "black-white",

    graphite: "dark-gray",
    "slate-pro": "dark-gray",

    ocean: "institutional-blue",
    "deep-ocean-night": "institutional-blue",
    "midnight-blue": "institutional-blue",

    neon: "electric-blue",

    crimson: "crimson-black",
    wine: "crimson-black",
    "red-black": "crimson-black",
    "dark-red": "crimson-black",
  };

  const raw = String(value ?? "")
    .replace(/-surface$/, "");

  const normalized = aliases[raw] ?? raw;

  return DARK_VARIANTS.includes(normalized)
    ? normalized
    : DEFAULT_DARK_VARIANT;
}

function getDarkPreset(value) {
  const normalized = normalizeDarkVariant(value);

  return (
    DARK_PRESETS.find(
      (preset) => preset.variant === normalized
    ) ?? DARK_PRESETS[0]
  );
}

function getCurrentPreset(store) {
  return store.darkMode
    ? getDarkPreset(store.darkVariant)
    : LIGHT_PRESET;
}

function removeDarkClasses(root) {
  DARK_VARIANT_CLASSES.forEach((className) => {
    root.classList.remove(className);
  });
}

function applyPresetVariables(root, preset) {
  Object.entries(CSS_VARIABLE_MAP).forEach(
    ([key, cssName]) => {
      const value =
        key === "accent" ||
        key === "accentContrast"
          ? preset[key]
          : preset.palette[key];

      if (value != null) {
        root.style.setProperty(cssName, value);
      }
    }
  );

  root.style.setProperty(
    "--color-primary",
    preset.accent
  );

  root.style.setProperty(
    "--color-primary-effective",
    preset.accent
  );

  root.style.setProperty(
    "--accent-user",
    preset.accent
  );

  root.style.setProperty(
    "--bg-elev",
    preset.palette.bgElevated
  );

  root.style.setProperty(
    "--ring-primary",
    `0 0 0 3px ${preset.palette.focusRing}`
  );

  /* Alias utilizados por estilos anteriores. */
  root.style.setProperty(
    "--background",
    preset.palette.bgMain
  );

  root.style.setProperty(
    "--surface",
    preset.palette.bgCard
  );

  root.style.setProperty(
    "--surface-card",
    preset.palette.bgCard
  );

  root.style.setProperty(
    "--surface-panel",
    preset.palette.bgElevated
  );

  root.style.setProperty(
    "--panel-bg",
    preset.palette.bgCard
  );

  root.style.setProperty(
    "--sidebar-bg",
    preset.palette.bgNavbar
  );

  root.style.setProperty(
    "--topbar-bg",
    preset.palette.bgNavbar
  );

  root.style.setProperty(
    "--input-bg",
    preset.palette.bgInput
  );

  root.style.setProperty(
    "--text-color",
    preset.palette.textPrimary
  );

  root.style.setProperty(
    "--muted-color",
    preset.palette.textSecondary
  );

  root.style.setProperty(
    "--border",
    preset.palette.borderColor
  );

  root.style.setProperty(
    "--primary",
    preset.accent
  );
}

function migrateLegacySettings() {
  const oldDark = getStorage("darkMode");
  const oldFont = getStorage("fontSize");
  const oldAnimations = getStorage("animations");
  const oldMono = getStorage("sgpc-mono-dark");

  if (
    getStorage(STORAGE.theme) === null &&
    oldDark !== null
  ) {
    setStorage(
      STORAGE.theme,
      oldDark === "true" ? "dark" : "light"
    );
  }

  if (
    getStorage(STORAGE.fontSize) === null &&
    oldFont !== null
  ) {
    setStorage(
      STORAGE.fontSize,
      normalizeFontSize(oldFont)
    );
  }

  if (
    getStorage(STORAGE.animations) === null &&
    oldAnimations !== null
  ) {
    setStorage(
      STORAGE.animations,
      oldAnimations === "false"
        ? "false"
        : "true"
    );
  }

  if (
    getStorage(STORAGE.darkVariant) === null &&
    oldMono === "true"
  ) {
    setStorage(
      STORAGE.darkVariant,
      "black-white"
    );
  }

  LEGACY_STORAGE.forEach(removeStorage);
  removeStorage(STORAGE.oldColor);
}

/* ============================================================
   STORE
============================================================ */

export const useThemeStore = defineStore(
  "theme",
  {
    state: () => {
      const darkMode =
        getStorage(
          STORAGE.theme,
          DEFAULT_THEME
        ) === "dark";

      const preset = getDarkPreset(
        getStorage(
          STORAGE.darkVariant,
          DEFAULT_DARK_VARIANT
        )
      );

      return {
        darkMode,
        darkVariant: preset.variant,

        themeProfile:
          DEFAULT_THEME_PROFILE,

        routeTransition:
          normalizeRouteTransition(
            getStorage(
              STORAGE.routeTransition,
              TRANSICION_RUTA_DEFAULT
            )
          ),

        hasCustomPrimary: false,

        primaryColor: darkMode
          ? preset.accent
          : LIGHT_PRESET.accent,

        fontSize: normalizeFontSize(
          getStorage(
            STORAGE.fontSize,
            DEFAULT_FONT_SIZE
          )
        ),

        animations:
          getStorage(
            STORAGE.animations,
            "true"
          ) !== "false",

        surfacePresetLight:
          DEFAULT_LIGHT_SURFACE,

        surfacePresetDark:
          preset.surface,

        ready: false,
      };
    },

    getters: {
      currentSurfacePreset(state) {
        return state.darkMode
          ? state.surfacePresetDark
          : state.surfacePresetLight;
      },

      currentSurfaceMeta(state) {
        if (!state.darkMode) {
          return SURFACE_PRESETS_LIGHT[0];
        }

        const preset = getDarkPreset(
          state.darkVariant
        );

        return SURFACE_PRESETS_DARK.find(
          (item) =>
            item.value === preset.surface
        );
      },

      isInstitutionalTheme() {
        return true;
      },

      currentUnifiedDarkStyleMeta(state) {
        return getDarkPreset(
          state.darkVariant
        );
      },

      currentUnifiedDarkStyle(state) {
        return getDarkPreset(
          state.darkVariant
        ).value;
      },

      currentAppearance(state) {
        return state.darkMode
          ? getDarkPreset(
              state.darkVariant
            ).value
          : "light";
      },
    },

    actions: {
      init() {
        migrateLegacySettings();

        this.darkMode =
          getStorage(
            STORAGE.theme,
            DEFAULT_THEME
          ) === "dark";

        this.darkVariant =
          normalizeDarkVariant(
            getStorage(
              STORAGE.darkVariant,
              DEFAULT_DARK_VARIANT
            )
          );

        this.surfacePresetDark =
          `${this.darkVariant}-surface`;

        this.surfacePresetLight =
          DEFAULT_LIGHT_SURFACE;

        this.themeProfile =
          DEFAULT_THEME_PROFILE;

        this.fontSize =
          normalizeFontSize(
            getStorage(
              STORAGE.fontSize,
              DEFAULT_FONT_SIZE
            )
          );

        this.animations =
          getStorage(
            STORAGE.animations,
            "true"
          ) !== "false";

        this.routeTransition =
          normalizeRouteTransition(
            getStorage(
              STORAGE.routeTransition,
              TRANSICION_RUTA_DEFAULT
            )
          );

        this.primaryColor =
          getCurrentPreset(this).accent;

        this.hasCustomPrimary = false;

        this.persist();
        this.applyAll();

        this.ready = true;
      },

      persist() {
        setStorage(
          STORAGE.theme,
          this.darkMode
            ? "dark"
            : "light"
        );

        setStorage(
          STORAGE.darkVariant,
          this.darkVariant
        );

        setStorage(
          STORAGE.fontSize,
          this.fontSize
        );

        setStorage(
          STORAGE.animations,
          this.animations
            ? "true"
            : "false"
        );

        setStorage(
          STORAGE.routeTransition,
          this.routeTransition
        );

        setStorage(
          STORAGE.surfaceLight,
          DEFAULT_LIGHT_SURFACE
        );

        setStorage(
          STORAGE.surfaceDark,
          `${this.darkVariant}-surface`
        );

        setStorage(
          STORAGE.themeProfile,
          DEFAULT_THEME_PROFILE
        );
      },

      applyAll() {
        this.applyTheme();
        this.applySurfacePalette();
        this.applyRouteTransition();
        this.applyFontSize();
        this.applyAnimations();
      },

      setAppearance(value) {
        if (value === "light") {
          this.darkMode = false;

          this.primaryColor =
            LIGHT_PRESET.accent;
        } else {
          const preset =
            getDarkPreset(value);

          this.darkMode = true;
          this.darkVariant =
            preset.variant;

          this.surfacePresetDark =
            preset.surface;

          this.primaryColor =
            preset.accent;
        }

        this.hasCustomPrimary = false;

        this.persist();
        this.applyTheme();
        this.applySurfacePalette();
      },

      setDark(value) {
        this.setAppearance(
          value
            ? this.darkVariant ||
                DEFAULT_DARK_VARIANT
            : "light"
        );
      },

      toggleTheme() {
        this.setDark(!this.darkMode);
      },

      setThemeProfile() {
        this.themeProfile =
          DEFAULT_THEME_PROFILE;

        this.hasCustomPrimary = false;

        this.persist();
        this.applyAll();
      },

      setDarkVariant(value) {
        this.setAppearance(
          normalizeDarkVariant(value)
        );
      },

      setUnifiedDarkStyle(value) {
        this.setAppearance(value);
      },

      applyTheme() {
        const root = getRoot();

        if (!root) return;

        root.classList.toggle(
          "dark",
          this.darkMode
        );

        removeDarkClasses(root);

        root.dataset.theme =
          this.darkMode
            ? "dark"
            : "light";

        root.dataset.themeProfile =
          DEFAULT_THEME_PROFILE;

        if (this.darkMode) {
          root.classList.add(
            `dark-${this.darkVariant}`
          );

          root.dataset.darkVariant =
            this.darkVariant;
        } else {
          delete root.dataset.darkVariant;
        }
      },

      setRouteTransition(value) {
        this.routeTransition =
          normalizeRouteTransition(value);

        this.persist();
        this.applyRouteTransition();
      },

      applyRouteTransition() {
        const root = getRoot();

        if (!root) return;

        const preset =
          getRouteTransitionPreset(
            this.routeTransition
          );

        Object.entries(
          preset.vars
        ).forEach(([name, value]) => {
          root.style.setProperty(
            name,
            value
          );
        });
      },

      setPrimaryColor() {
        this.hasCustomPrimary = false;

        removeStorage(
          STORAGE.oldColor
        );

        this.applyPrimaryColor();
      },

      clearPrimaryColor() {
        this.hasCustomPrimary = false;

        removeStorage(
          STORAGE.oldColor
        );

        this.applyPrimaryColor();
      },

      applyPrimaryColor() {
        const root = getRoot();

        if (!root) return;

        const preset =
          getCurrentPreset(this);

        this.primaryColor =
          preset.accent;

        root.style.setProperty(
          "--accent-user",
          preset.accent
        );

        root.style.setProperty(
          "--accent-contrast",
          preset.accentContrast
        );

        root.style.setProperty(
          "--color-primary-effective",
          preset.accent
        );
      },

      setFontSize(value) {
        this.fontSize =
          normalizeFontSize(value);

        this.persist();
        this.applyFontSize();
      },

      applyFontSize() {
        const root = getRoot();

        if (!root) return;

        /*
         * La escala tipográfica global se controla únicamente
         * mediante --font-base. theme.css aplica esa variable
         * al elemento <html>.
         *
         * No dejamos un font-size inline en <html>, porque sería
         * una segunda fuente de verdad y complica la adaptación
         * de las vistas.
         */
        root.style.setProperty(
          "--font-base",
          this.fontSize
        );

        root.dataset.fontSize =
          String(this.fontSize)
            .replace("px", "")
            .trim();

        /* Limpia el valor inline creado por versiones anteriores. */
        root.style.removeProperty(
          "font-size"
        );
      },

      setAnimations(value) {
        this.animations =
          Boolean(value);

        this.persist();
        this.applyAnimations();
      },

      applyAnimations() {
        const root = getRoot();

        if (!root) return;

        root.style.setProperty(
          "--animate-speed",
          this.animations
            ? "1"
            : "0"
        );

        root.classList.toggle(
          "reduced-motion",
          !this.animations
        );
      },

      setSurfacePreset(value) {
        if (!this.darkMode) {
          this.surfacePresetLight =
            DEFAULT_LIGHT_SURFACE;

          this.persist();
          this.applySurfacePalette();

          return;
        }

        this.setAppearance(
          String(value ?? "")
            .replace(/-surface$/, "")
        );
      },

      applySurfacePalette() {
        const root = getRoot();

        if (!root) return;

        const preset =
          getCurrentPreset(this);

        this.primaryColor =
          preset.accent;

        applyPresetVariables(
          root,
          preset
        );
      },

      reset() {
        Object.values(
          STORAGE
        ).forEach(removeStorage);

        LEGACY_STORAGE.forEach(
          removeStorage
        );

        this.darkMode = false;

        this.darkVariant =
          DEFAULT_DARK_VARIANT;

        this.themeProfile =
          DEFAULT_THEME_PROFILE;

        this.routeTransition =
          TRANSICION_RUTA_DEFAULT;

        this.hasCustomPrimary = false;

        this.primaryColor =
          LIGHT_PRESET.accent;

        this.fontSize =
          DEFAULT_FONT_SIZE;

        this.animations = true;

        this.surfacePresetLight =
          DEFAULT_LIGHT_SURFACE;

        this.surfacePresetDark =
          `${DEFAULT_DARK_VARIANT}-surface`;

        this.persist();
        this.applyAll();
      },
    },
  }
);

export { TRANSICIONES_RUTA };
