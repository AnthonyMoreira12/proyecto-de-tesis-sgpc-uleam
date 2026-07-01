import { defineStore } from "pinia";
import {
  TRANSICIONES_RUTA,
  TRANSICION_RUTA_DEFAULT,
  getRouteTransitionPreset,
  normalizeRouteTransition,
} from "../utils/transicionesRuta";

const LS = {
  theme: "sgpc-theme",
  color: "sgpc-color",
  font: "sgpc-fontSize",
  anim: "sgpc-animations",
  darkVariant: "sgpc-dark-variant",
  routeTransition: "sgpc-route-transition",
  surfaceLight: "sgpc-surface-light",
  surfaceDark: "sgpc-surface-dark",
  themeProfile: "sgpc-theme-profile",
};

const LEGACY = {
  dark: "darkMode",
  color: "themeColor",
  font: "fontSize",
  anim: "animations",
};

const DARK_VARIANTS = ["obsidian", "slate-pro", "oled-black"];

const THEME_PROFILES = ["editorial", "institutional"];
const DEFAULT_THEME_PROFILE = "institutional";

const DEFAULT_PRIMARY_LIGHT = "#111111";
const DEFAULT_PRIMARY_DARK = "#111111";
const LEGACY_EDITORIAL_DARK = "#f3ede5";
const DEFAULT_FONT_SIZE = "17px";

const DEFAULT_SURFACE_LIGHT = "editorial-paper";
const DEFAULT_SURFACE_DARK = "obsidian-warm";

const INSTITUTIONAL_PRIMARY_LIGHT = "#1d4ed8";
const INSTITUTIONAL_PRIMARY_DARK = "#8ab4ff";

const ACCENT_CRIMSON = "#7d2230";
const ACCENT_SAGE = "#4f6b52";
const ACCENT_TEAL = "#0f766e";

const SURFACE_STYLE_VAR_MAP = Object.freeze({
  bgMain: "--bg-main",
  bgCard: "--bg-card",
  bgNavbar: "--bg-navbar",
  bgInput: "--bg-input",
  bgElevated: "--bg-elevated",
  bgSoft: "--bg-soft",
  overlay: "--overlay",
  cardHoverBg: "--card-hover-bg",
});

const INSTITUTIONAL_PROFILE_VAR_MAP = Object.freeze({
  colorPrimaryDefault: "--color-primary-default",
  textPrimary: "--text-primary",
  textSecondary: "--text-secondary",
  textInverse: "--text-inverse",
  textDisabled: "--text-disabled",
  borderColor: "--border-color",
  borderStrong: "--border-strong",
  shadowSoft: "--shadow-soft",
  shadowStrong: "--shadow-strong",
  shadowHover: "--shadow-hover",
  hover: "--hover",
  active: "--active",
  footerBg: "--footer-bg",
  footerText: "--footer-text",
  footerMuted: "--footer-muted",
});

const INSTITUTIONAL_PROFILE_VAR_KEYS = Object.freeze(
  Object.values(INSTITUTIONAL_PROFILE_VAR_MAP)
);

const INSTITUTIONAL_THEME_LIGHT = Object.freeze({
  colorPrimaryDefault: INSTITUTIONAL_PRIMARY_LIGHT,
  bgMain: "#ffffff",
  bgCard: "#ffffff",
  bgNavbar: "rgba(255, 255, 255, 0.98)",
  bgInput: "#ffffff",
  bgElevated: "#ffffff",
  bgSoft: "rgba(29, 78, 216, 0.035)",
  overlay: "rgba(17, 17, 17, 0.42)",
  cardHoverBg: "#ffffff",
  textPrimary: "#111111",
  textSecondary: "#4b5563",
  textInverse: "#ffffff",
  textDisabled: "rgba(17, 17, 17, 0.42)",
  borderColor: "rgba(17, 17, 17, 0.10)",
  borderStrong: "rgba(17, 17, 17, 0.18)",
  shadowSoft: "0 8px 22px rgba(17, 17, 17, 0.04)",
  shadowStrong: "0 18px 42px rgba(17, 17, 17, 0.08)",
  shadowHover: "0 14px 32px rgba(17, 17, 17, 0.07)",
  hover: "rgba(17, 17, 17, 0.035)",
  active: "rgba(17, 17, 17, 0.06)",
  footerBg: "#0f3d91",
  footerText: "#ffffff",
  footerMuted: "rgba(255, 255, 255, 0.82)",
});

const INSTITUTIONAL_THEME_DARK = Object.freeze({
  colorPrimaryDefault: INSTITUTIONAL_PRIMARY_DARK,
  bgMain: "#0f172a",
  bgCard: "#172033",
  bgNavbar: "rgba(15, 23, 42, 0.96)",
  bgInput: "#1d2940",
  bgElevated: "#1a2438",
  bgSoft: "rgba(255, 255, 255, 0.045)",
  overlay: "rgba(0, 0, 0, 0.68)",
  cardHoverBg: "#172033",
  textPrimary: "#f8fafc",
  textSecondary: "#dbe4f3",
  textInverse: "#111111",
  textDisabled: "rgba(248, 250, 252, 0.42)",
  borderColor: "rgba(255, 255, 255, 0.10)",
  borderStrong: "rgba(255, 255, 255, 0.18)",
  shadowSoft: "0 12px 30px rgba(0, 0, 0, 0.34)",
  shadowStrong: "0 18px 44px rgba(0, 0, 0, 0.46)",
  shadowHover: "0 16px 34px rgba(0, 0, 0, 0.34)",
  hover: "rgba(255, 255, 255, 0.045)",
  active: "rgba(255, 255, 255, 0.08)",
  footerBg: "#0b1120",
  footerText: "#ffffff",
  footerMuted: "rgba(255, 255, 255, 0.82)",
});

export const SURFACE_PRESETS_LIGHT = Object.freeze([
  {
    value: "editorial-paper",
    label: "Editorial",
    desc: "Marfil sobrio",
    preview: {
      bg: "#f4f2ed",
      card: "#ffffff",
      line: "rgba(17,17,17,0.10)",
    },
    vars: {
      bgMain: "#f4f2ed",
      bgCard: "#ffffff",
      bgNavbar: "rgba(255, 255, 255, 0.98)",
      bgInput: "#ffffff",
      bgElevated: "#ffffff",
      bgSoft: "rgba(17, 17, 17, 0.028)",
      overlay: "rgba(17, 17, 17, 0.34)",
      cardHoverBg: "#ffffff",
    },
  },
  {
    value: "sage-paper",
    label: "Sage",
    desc: "Verde papel",
    preview: {
      bg: "#edf1eb",
      card: "#fbfdf9",
      line: "rgba(20,35,22,0.10)",
    },
    vars: {
      bgMain: "#edf1eb",
      bgCard: "#fbfdf9",
      bgNavbar: "rgba(251, 253, 249, 0.98)",
      bgInput: "#fbfdf9",
      bgElevated: "#fbfdf9",
      bgSoft: "rgba(17, 35, 20, 0.03)",
      overlay: "rgba(17, 17, 17, 0.34)",
      cardHoverBg: "#fbfdf9",
    },
  },
  {
    value: "mist-paper",
    label: "Mist",
    desc: "Azul grisáceo",
    preview: {
      bg: "#eef2f7",
      card: "#fcfdff",
      line: "rgba(20,30,45,0.10)",
    },
    vars: {
      bgMain: "#eef2f7",
      bgCard: "#fcfdff",
      bgNavbar: "rgba(252, 253, 255, 0.98)",
      bgInput: "#fcfdff",
      bgElevated: "#fcfdff",
      bgSoft: "rgba(20, 30, 45, 0.03)",
      overlay: "rgba(17, 17, 17, 0.34)",
      cardHoverBg: "#fcfdff",
    },
  },
  {
    value: "rose-paper",
    label: "Rose",
    desc: "Rosa muy suave",
    preview: {
      bg: "#f5edef",
      card: "#fffafb",
      line: "rgba(45,20,24,0.09)",
    },
    vars: {
      bgMain: "#f5edef",
      bgCard: "#fffafb",
      bgNavbar: "rgba(255, 250, 251, 0.98)",
      bgInput: "#fffafb",
      bgElevated: "#fffafb",
      bgSoft: "rgba(45, 20, 24, 0.03)",
      overlay: "rgba(17, 17, 17, 0.34)",
      cardHoverBg: "#fffafb",
    },
  },
]);

export const SURFACE_PRESETS_DARK = Object.freeze([
  {
    value: "obsidian-warm",
    label: "Obsidian",
    desc: "Oscuro editorial",
    preview: {
      bg: "#1c1917",
      card: "#26221f",
      line: "rgba(255,255,255,0.10)",
    },
    vars: {
      bgMain: "#1c1917",
      bgCard: "#26221f",
      bgNavbar: "rgba(33, 29, 27, 0.97)",
      bgInput: "#2e2926",
      bgElevated: "#2a2522",
      bgSoft: "rgba(255, 255, 255, 0.045)",
      overlay: "rgba(0, 0, 0, 0.58)",
      cardHoverBg: "#26221f",
    },
  },
  {
    value: "deep-ocean-night",
    label: "Ocean",
    desc: "Azul profundo",
    preview: {
      bg: "#101820",
      card: "#182330",
      line: "rgba(255,255,255,0.10)",
    },
    vars: {
      bgMain: "#101820",
      bgCard: "#182330",
      bgNavbar: "rgba(19, 29, 40, 0.97)",
      bgInput: "#202c39",
      bgElevated: "#1c2834",
      bgSoft: "rgba(255, 255, 255, 0.04)",
      overlay: "rgba(0, 0, 0, 0.72)",
      cardHoverBg: "#182330",
    },
  },
  {
    value: "oled-black-surface",
    label: "OLED Black",
    desc: "Negro profundo",
    preview: {
      bg: "#0a0a0a",
      card: "#141414",
      line: "rgba(255,255,255,0.10)",
    },
    vars: {
      bgMain: "#0a0a0a",
      bgCard: "#141414",
      bgNavbar: "rgba(10, 10, 10, 0.97)",
      bgInput: "#1d1d1d",
      bgElevated: "#181818",
      bgSoft: "rgba(255, 255, 255, 0.04)",
      overlay: "rgba(0, 0, 0, 0.76)",
      cardHoverBg: "#141414",
    },
  },
]);

export const UNIFIED_DARK_STYLE_PRESETS = Object.freeze([
  {
    value: "obsidian",
    label: "Obsidian + Sage",
    desc: "Sage por defecto",
    surface: "obsidian-warm",
    variant: "obsidian",
    accent: ACCENT_SAGE,
    accentLabel: "Sage",
    preview: {
      bg: "#1c1917",
      card: "#26221f",
      line: "rgba(255,255,255,0.10)",
    },
  },
  {
    value: "ocean",
    label: "Ocean + Carmesí",
    desc: "Carmesí por defecto",
    surface: "deep-ocean-night",
    variant: "slate-pro",
    accent: ACCENT_CRIMSON,
    accentLabel: "Carmesí",
    preview: {
      bg: "#101820",
      card: "#182330",
      line: "rgba(255,255,255,0.10)",
    },
  },
  {
    value: "oled-black",
    label: "OLED Black + Teal",
    desc: "Teal por defecto",
    surface: "oled-black-surface",
    variant: "oled-black",
    accent: ACCENT_TEAL,
    accentLabel: "Teal",
    preview: {
      bg: "#0a0a0a",
      card: "#141414",
      line: "rgba(255,255,255,0.10)",
    },
  },
]);

function getLS(key, fallback = null) {
  try {
    const value = localStorage.getItem(key);
    return value ?? fallback;
  } catch {
    return fallback;
  }
}

function setLS(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // noop
  }
}

function removeLS(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    // noop
  }
}

function normalizeHexColor(value, fallback) {
  const raw = String(value ?? "").trim();
  if (!raw) return fallback;

  if (/^#([0-9a-fA-F]{3}){1,2}$/.test(raw)) {
    if (raw.length === 4) {
      const expanded = raw
        .slice(1)
        .split("")
        .map((char) => char + char)
        .join("");
      return `#${expanded}`.toLowerCase();
    }

    return raw.toLowerCase();
  }

  return fallback;
}

function isEditorialAccent(value) {
  const normalized = normalizeHexColor(value, null);

  return (
    normalized === DEFAULT_PRIMARY_LIGHT ||
    normalized === DEFAULT_PRIMARY_DARK ||
    normalized === LEGACY_EDITORIAL_DARK
  );
}

function getStoredEditorialAccent(value) {
  const normalized = normalizeHexColor(value, null);

  if (!isEditorialAccent(normalized)) {
    return null;
  }

  return DEFAULT_PRIMARY_LIGHT;
}

function hexToRgb(hex) {
  const normalized = normalizeHexColor(hex, null);
  if (!normalized) return null;

  const value = normalized.replace("#", "");
  const r = parseInt(value.slice(0, 2), 16);
  const g = parseInt(value.slice(2, 4), 16);
  const b = parseInt(value.slice(4, 6), 16);

  if ([r, g, b].some((channel) => Number.isNaN(channel))) {
    return null;
  }

  return { r, g, b };
}

function getRelativeLuminance({ r, g, b }) {
  const normalize = (channel) => {
    const c = channel / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };

  const R = normalize(r);
  const G = normalize(g);
  const B = normalize(b);

  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

function getContrastText(hex, fallback = "#ffffff") {
  const rgb = hexToRgb(hex);
  if (!rgb) return fallback;

  return getRelativeLuminance(rgb) > 0.5 ? "#111111" : "#ffffff";
}

function normalizeDarkVariant(value) {
  if (value === "base") return "obsidian";
  if (value === "soft") return "slate-pro";
  if (value === "deep") return "obsidian";
  if (value === "contrast") return "obsidian";
  if (value === "graphite") return "oled-black";
  if (value === "midnight-blue" || value === "neon-noir") return "obsidian";

  return DARK_VARIANTS.includes(value) ? value : "obsidian";
}

function normalizeThemeProfile(value) {
  if (value === "generic") return "institutional";
  return THEME_PROFILES.includes(value) ? value : DEFAULT_THEME_PROFILE;
}

function getDarkVariantClass(variant) {
  switch (variant) {
    case "obsidian":
      return "dark-obsidian";
    case "slate-pro":
      return "dark-slate-pro";
    case "oled-black":
      return "dark-oled-black";
    default:
      return "dark-obsidian";
  }
}

function removeDarkVariantClasses(root) {
  root.classList.remove(
    "dark-obsidian",
    "dark-slate-pro",
    "dark-midnight-blue",
    "dark-graphite",
    "dark-neon-noir",
    "dark-oled-black",
    "dark-plum-night",
    "dark-forest-night",
    "mono-dark"
  );
}

function applyCssVars(root, map, vars) {
  Object.entries(map).forEach(([key, cssVar]) => {
    const value = vars?.[key];

    if (value === undefined || value === null || value === "") {
      root.style.removeProperty(cssVar);
    } else {
      root.style.setProperty(cssVar, value);
    }
  });
}

function clearCssVars(root, cssVars) {
  cssVars.forEach((cssVar) => root.style.removeProperty(cssVar));
}

function getInstitutionalThemeTokens(isDark) {
  return isDark ? INSTITUTIONAL_THEME_DARK : INSTITUTIONAL_THEME_LIGHT;
}

function getSurfaceCatalog(isDark) {
  return isDark ? SURFACE_PRESETS_DARK : SURFACE_PRESETS_LIGHT;
}

function getDefaultSurfacePreset(isDark) {
  return isDark ? DEFAULT_SURFACE_DARK : DEFAULT_SURFACE_LIGHT;
}

function normalizeSurfacePreset(value, isDark) {
  const catalog = getSurfaceCatalog(isDark);

  return catalog.some((item) => item.value === value)
    ? value
    : getDefaultSurfacePreset(isDark);
}

function getSurfacePresetMeta(value, isDark) {
  const normalized = normalizeSurfacePreset(value, isDark);

  return (
    getSurfaceCatalog(isDark).find((item) => item.value === normalized) ||
    getSurfaceCatalog(isDark)[0]
  );
}

function findUnifiedDarkStyleByValue(value) {
  return UNIFIED_DARK_STYLE_PRESETS.find((item) => item.value === value) || null;
}

function resolveUnifiedDarkStyle(surface, variant) {
  const exact = UNIFIED_DARK_STYLE_PRESETS.find(
    (item) => item.surface === surface && item.variant === variant
  );
  if (exact) return exact;

  const bySurface = UNIFIED_DARK_STYLE_PRESETS.find((item) => item.surface === surface);
  if (bySurface) return bySurface;

  const byVariant = UNIFIED_DARK_STYLE_PRESETS.find((item) => item.variant === variant);
  if (byVariant) return byVariant;

  return UNIFIED_DARK_STYLE_PRESETS[0];
}

function getDefaultPrimaryForContext(isDark, profile, surfaceDark, darkVariant) {
  if (profile === "institutional") {
    return isDark ? INSTITUTIONAL_PRIMARY_DARK : INSTITUTIONAL_PRIMARY_LIGHT;
  }

  if (isDark) {
    return resolveUnifiedDarkStyle(surfaceDark, darkVariant).accent;
  }

  return DEFAULT_PRIMARY_LIGHT;
}

export const useThemeStore = defineStore("theme", {
  state: () => {
    const storedTheme = getLS(LS.theme);
    const initialDark = storedTheme === "dark";

    const initialThemeProfile = normalizeThemeProfile(
      getLS(LS.themeProfile, DEFAULT_THEME_PROFILE)
    );

    const initialDarkVariant = normalizeDarkVariant(getLS(LS.darkVariant, "obsidian"));

    const initialSurfaceDark = normalizeSurfacePreset(
      getLS(LS.surfaceDark, DEFAULT_SURFACE_DARK),
      true
    );

    const initialSurfaceLight = normalizeSurfacePreset(
      getLS(LS.surfaceLight, DEFAULT_SURFACE_LIGHT),
      false
    );

    const storedEditorialAccent = getStoredEditorialAccent(getLS(LS.color, null));

    return {
      darkMode: initialDark,
      darkVariant: initialDarkVariant,
      themeProfile: initialThemeProfile,
      routeTransition: normalizeRouteTransition(
        getLS(LS.routeTransition, TRANSICION_RUTA_DEFAULT)
      ),
      hasCustomPrimary:
        initialThemeProfile === "editorial" && storedEditorialAccent !== null,
      primaryColor:
        initialThemeProfile === "editorial" && storedEditorialAccent !== null
          ? storedEditorialAccent
          : getDefaultPrimaryForContext(
              initialDark,
              initialThemeProfile,
              initialSurfaceDark,
              initialDarkVariant
            ),
      fontSize: getLS(LS.font, DEFAULT_FONT_SIZE),
      animations: getLS(LS.anim, "true") !== "false",
      surfacePresetLight: initialSurfaceLight,
      surfacePresetDark: initialSurfaceDark,
      ready: false,
    };
  },

  getters: {
    currentSurfacePreset(state) {
      return state.darkMode ? state.surfacePresetDark : state.surfacePresetLight;
    },

    currentSurfaceMeta(state) {
      return getSurfacePresetMeta(
        state.darkMode ? state.surfacePresetDark : state.surfacePresetLight,
        state.darkMode
      );
    },

    isInstitutionalTheme(state) {
      return state.themeProfile === "institutional";
    },

    currentUnifiedDarkStyleMeta(state) {
      return resolveUnifiedDarkStyle(state.surfacePresetDark, state.darkVariant);
    },

    currentUnifiedDarkStyle(state) {
      return resolveUnifiedDarkStyle(state.surfacePresetDark, state.darkVariant).value;
    },
  },

  actions: {
    init() {
      const legacyDark = getLS(LEGACY.dark);
      const legacyColor = getLS(LEGACY.color);
      const legacyFont = getLS(LEGACY.font);
      const legacyAnim = getLS(LEGACY.anim);

      if (
        legacyDark !== null ||
        legacyColor !== null ||
        legacyFont !== null ||
        legacyAnim !== null
      ) {
        if (legacyDark !== null && !getLS(LS.theme)) {
          const isDark = legacyDark === "true";
          setLS(LS.theme, isDark ? "dark" : "light");
        }

        if (legacyColor !== null && !getLS(LS.color)) {
          const normalized = normalizeHexColor(legacyColor, null);
          if (isEditorialAccent(normalized)) {
            setLS(LS.color, DEFAULT_PRIMARY_LIGHT);
          }
        }

        if (legacyFont !== null && !getLS(LS.font)) {
          setLS(LS.font, legacyFont);
        }

        if (legacyAnim !== null && !getLS(LS.anim)) {
          setLS(LS.anim, legacyAnim === "true" ? "true" : "false");
        }

        removeLS(LEGACY.dark);
        removeLS(LEGACY.color);
        removeLS(LEGACY.font);
        removeLS(LEGACY.anim);
      }

      const legacyMonoDark = getLS("sgpc-mono-dark");
      if (legacyMonoDark === "true" && !getLS(LS.darkVariant)) {
        setLS(LS.darkVariant, "oled-black");
      }
      removeLS("sgpc-mono-dark");

      if (!getLS(LS.theme)) {
        const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)")?.matches;
        this.darkMode = !!prefersDark;
        setLS(LS.theme, this.darkMode ? "dark" : "light");
      } else {
        this.darkMode = getLS(LS.theme) === "dark";
      }

      this.darkVariant = normalizeDarkVariant(getLS(LS.darkVariant, "obsidian"));

      this.themeProfile = normalizeThemeProfile(
        getLS(LS.themeProfile, DEFAULT_THEME_PROFILE)
      );

      this.routeTransition = normalizeRouteTransition(
        getLS(LS.routeTransition, TRANSICION_RUTA_DEFAULT)
      );

      this.fontSize = getLS(LS.font, DEFAULT_FONT_SIZE);
      this.animations = getLS(LS.anim, "true") !== "false";

      this.surfacePresetLight = normalizeSurfacePreset(
        getLS(LS.surfaceLight, DEFAULT_SURFACE_LIGHT),
        false
      );

      this.surfacePresetDark = normalizeSurfacePreset(
        getLS(LS.surfaceDark, DEFAULT_SURFACE_DARK),
        true
      );

      const resolvedStyle = resolveUnifiedDarkStyle(
        this.surfacePresetDark,
        this.darkVariant
      );

      this.surfacePresetDark = resolvedStyle.surface;
      this.darkVariant = resolvedStyle.variant;

      const storedColor = getLS(LS.color, null);
      const storedEditorialAccent = getStoredEditorialAccent(storedColor);

      if (storedColor !== null && storedEditorialAccent === null) {
        removeLS(LS.color);
      }

      if (this.themeProfile === "institutional") {
        this.hasCustomPrimary = false;
        removeLS(LS.color);
      } else {
        this.hasCustomPrimary = storedEditorialAccent !== null;
      }

      this.primaryColor = this.hasCustomPrimary
        ? DEFAULT_PRIMARY_LIGHT
        : getDefaultPrimaryForContext(
            this.darkMode,
            this.themeProfile,
            this.surfacePresetDark,
            this.darkVariant
          );

      setLS(LS.darkVariant, this.darkVariant);
      setLS(LS.themeProfile, this.themeProfile);
      setLS(LS.routeTransition, this.routeTransition);
      setLS(LS.surfaceLight, this.surfacePresetLight);
      setLS(LS.surfaceDark, this.surfacePresetDark);

      this.applyAll();
      this.ready = true;
    },

    applyAll() {
      this.applyTheme();
      this.applyRouteTransition();
      this.applyPrimaryColor();
      this.applyFontSize();
      this.applyAnimations();
      this.applySurfacePalette();
    },

    setDark(value) {
      this.darkMode = !!value;
      setLS(LS.theme, this.darkMode ? "dark" : "light");

      if (this.themeProfile !== "institutional") {
        if (this.hasCustomPrimary) {
          this.primaryColor = DEFAULT_PRIMARY_LIGHT;
          setLS(LS.color, DEFAULT_PRIMARY_LIGHT);
        } else {
          this.primaryColor = getDefaultPrimaryForContext(
            this.darkMode,
            this.themeProfile,
            this.surfacePresetDark,
            this.darkVariant
          );
        }
      }

      this.applyTheme();
      this.applyPrimaryColor();
      this.applySurfacePalette();
    },

    toggleTheme() {
      this.setDark(!this.darkMode);
    },

    setThemeProfile(profile) {
      this.themeProfile = normalizeThemeProfile(profile);
      setLS(LS.themeProfile, this.themeProfile);

      if (this.themeProfile === "institutional") {
        this.hasCustomPrimary = false;
        removeLS(LS.color);
      }

      this.primaryColor = this.hasCustomPrimary
        ? DEFAULT_PRIMARY_LIGHT
        : getDefaultPrimaryForContext(
            this.darkMode,
            this.themeProfile,
            this.surfacePresetDark,
            this.darkVariant
          );

      this.applyAll();
    },

    setDarkVariant(variant) {
      this.darkVariant = normalizeDarkVariant(variant);

      const resolvedStyle = resolveUnifiedDarkStyle(
        this.surfacePresetDark,
        this.darkVariant
      );

      this.surfacePresetDark = resolvedStyle.surface;
      this.darkVariant = resolvedStyle.variant;
      this.hasCustomPrimary = false;
      this.primaryColor = resolvedStyle.accent;

      removeLS(LS.color);
      setLS(LS.surfaceDark, this.surfacePresetDark);
      setLS(LS.darkVariant, this.darkVariant);

      this.applyTheme();
      this.applyPrimaryColor();
      this.applySurfacePalette();
    },

    setUnifiedDarkStyle(styleValue) {
      const preset = findUnifiedDarkStyleByValue(styleValue);
      if (!preset) return;

      this.surfacePresetDark = normalizeSurfacePreset(preset.surface, true);
      this.darkVariant = normalizeDarkVariant(preset.variant);

      this.hasCustomPrimary = false;
      this.primaryColor = preset.accent;

      removeLS(LS.color);
      setLS(LS.surfaceDark, this.surfacePresetDark);
      setLS(LS.darkVariant, this.darkVariant);

      this.applyTheme();
      this.applyPrimaryColor();
      this.applySurfacePalette();
    },

    applyTheme() {
      const root = document.documentElement;

      root.classList.toggle("dark", this.darkMode);
      removeDarkVariantClasses(root);

      root.dataset.theme = this.darkMode ? "dark" : "light";
      root.dataset.themeProfile = this.themeProfile;

      if (this.darkMode && this.themeProfile !== "institutional") {
        const variantClass = getDarkVariantClass(this.darkVariant);
        if (variantClass) {
          root.classList.add(variantClass);
        }
        root.dataset.darkVariant = this.darkVariant;
      } else {
        delete root.dataset.darkVariant;
      }
    },

    setRouteTransition(value) {
      this.routeTransition = normalizeRouteTransition(value);
      setLS(LS.routeTransition, this.routeTransition);
      this.applyRouteTransition();
    },

    applyRouteTransition() {
      const root = document.documentElement;
      const preset = getRouteTransitionPreset(this.routeTransition);

      Object.entries(preset.vars).forEach(([key, value]) => {
        root.style.setProperty(key, value);
      });
    },

    setPrimaryColor(color) {
      if (this.themeProfile === "institutional") return;

      const normalized = normalizeHexColor(color, DEFAULT_PRIMARY_LIGHT);

      if (!isEditorialAccent(normalized)) {
        this.clearPrimaryColor();
        return;
      }

      this.primaryColor = DEFAULT_PRIMARY_LIGHT;
      this.hasCustomPrimary = true;

      setLS(LS.color, DEFAULT_PRIMARY_LIGHT);
      this.applyPrimaryColor();
    },

    clearPrimaryColor() {
      this.hasCustomPrimary = false;
      removeLS(LS.color);

      this.primaryColor = getDefaultPrimaryForContext(
        this.darkMode,
        this.themeProfile,
        this.surfacePresetDark,
        this.darkVariant
      );

      this.applyPrimaryColor();
    },

    applyPrimaryColor() {
      const root = document.documentElement;

      let effectiveColor = getDefaultPrimaryForContext(
        this.darkMode,
        this.themeProfile,
        this.surfacePresetDark,
        this.darkVariant
      );

      if (this.themeProfile === "institutional") {
        effectiveColor = this.darkMode
          ? INSTITUTIONAL_PRIMARY_DARK
          : INSTITUTIONAL_PRIMARY_LIGHT;
      } else if (this.hasCustomPrimary) {
        effectiveColor = DEFAULT_PRIMARY_LIGHT;
        this.primaryColor = DEFAULT_PRIMARY_LIGHT;
      } else {
        this.primaryColor = effectiveColor;
      }

      root.style.removeProperty("--accent-user");

      if (this.themeProfile !== "institutional") {
        root.style.setProperty("--accent-user", effectiveColor);
      }

      root.style.setProperty("--accent-contrast", getContrastText(effectiveColor));
      root.style.setProperty("--color-primary-effective", effectiveColor);
    },

    setFontSize(size) {
      this.fontSize = size || DEFAULT_FONT_SIZE;
      setLS(LS.font, this.fontSize);
      this.applyFontSize();
    },

    applyFontSize() {
      document.documentElement.style.setProperty("--font-base", this.fontSize);
    },

    setAnimations(value) {
      this.animations = !!value;
      setLS(LS.anim, this.animations ? "true" : "false");
      this.applyAnimations();
    },

    applyAnimations() {
      const root = document.documentElement;
      root.style.setProperty("--animate-speed", this.animations ? "1" : "0");
      root.classList.toggle("reduced-motion", !this.animations);
    },

    setSurfacePreset(value) {
      if (this.darkMode) {
        this.surfacePresetDark = normalizeSurfacePreset(value, true);
        setLS(LS.surfaceDark, this.surfacePresetDark);

        const resolvedStyle = resolveUnifiedDarkStyle(
          this.surfacePresetDark,
          this.darkVariant
        );

        this.surfacePresetDark = resolvedStyle.surface;
        this.darkVariant = resolvedStyle.variant;
        this.hasCustomPrimary = false;
        this.primaryColor = resolvedStyle.accent;

        removeLS(LS.color);
        setLS(LS.surfaceDark, this.surfacePresetDark);
        setLS(LS.darkVariant, this.darkVariant);
      } else {
        this.surfacePresetLight = normalizeSurfacePreset(value, false);
        setLS(LS.surfaceLight, this.surfacePresetLight);
      }

      this.applyTheme();
      this.applyPrimaryColor();
      this.applySurfacePalette();
    },

    applySurfacePalette() {
      const root = document.documentElement;

      if (this.themeProfile === "institutional") {
        const institutionalTokens = getInstitutionalThemeTokens(this.darkMode);
        applyCssVars(root, SURFACE_STYLE_VAR_MAP, institutionalTokens);
        applyCssVars(root, INSTITUTIONAL_PROFILE_VAR_MAP, institutionalTokens);
        return;
      }

      const preset = this.darkMode
        ? getSurfacePresetMeta(this.surfacePresetDark, true)
        : getSurfacePresetMeta(this.surfacePresetLight, false);

      applyCssVars(root, SURFACE_STYLE_VAR_MAP, preset.vars);
      clearCssVars(root, INSTITUTIONAL_PROFILE_VAR_KEYS);
    },

    reset() {
      removeLS(LS.theme);
      removeLS(LS.color);
      removeLS(LS.font);
      removeLS(LS.anim);
      removeLS(LS.darkVariant);
      removeLS(LS.routeTransition);
      removeLS(LS.surfaceLight);
      removeLS(LS.surfaceDark);
      removeLS(LS.themeProfile);
      removeLS("sgpc-mono-dark");

      this.darkMode = false;
      this.darkVariant = "obsidian";
      this.themeProfile = DEFAULT_THEME_PROFILE;
      this.routeTransition = TRANSICION_RUTA_DEFAULT;
      this.hasCustomPrimary = false;
      this.primaryColor = DEFAULT_PRIMARY_LIGHT;
      this.fontSize = DEFAULT_FONT_SIZE;
      this.animations = true;
      this.surfacePresetLight = DEFAULT_SURFACE_LIGHT;
      this.surfacePresetDark = DEFAULT_SURFACE_DARK;

      setLS(LS.theme, "light");
      setLS(LS.darkVariant, "obsidian");
      setLS(LS.themeProfile, DEFAULT_THEME_PROFILE);
      setLS(LS.routeTransition, TRANSICION_RUTA_DEFAULT);
      setLS(LS.font, DEFAULT_FONT_SIZE);
      setLS(LS.anim, "true");
      setLS(LS.surfaceLight, DEFAULT_SURFACE_LIGHT);
      setLS(LS.surfaceDark, DEFAULT_SURFACE_DARK);

      this.applyAll();
    },
  },
});

export { TRANSICIONES_RUTA };