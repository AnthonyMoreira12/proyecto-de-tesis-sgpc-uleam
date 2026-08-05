/* ============================================================
   SGPC ULEAM — TRANSICIONES DE RUTA
============================================================ */

/*
 * Transición seleccionada:
 *
 * REVEAL INSTITUCIONAL
 *
 * La interfaz nueva se muestra inmediatamente.
 *
 * El efecto visual se aplica únicamente mediante elementos
 * decorativos generados desde theme.css:
 *
 * - línea superior de acento;
 * - resplandor superficial muy tenue.
 *
 * No se transforma ni se oculta el contenido de la página.
 */

const INSTITUTIONAL_REVEAL_PRESET =
  Object.freeze({
    value: "institutional-reveal",

    label: "Reveal institucional",

    desc:
      "Entrada elegante con una línea de acento y un resplandor superficial discreto.",

    tier: "Premium",

    intensity: "2/5",

    bestFor:
      "Paneles, formularios, perfiles, listados y módulos administrativos",

    vars: Object.freeze({
      /* ======================================================
         DURACIÓN GENERAL
      ====================================================== */

      /*
       * Se conserva para compatibilidad con el sistema global.
       * La página completa no utiliza esta duración para moverse.
       */
      "--page-shell-enter-duration-base":
        "420ms",

      "--page-shell-leave-duration-base":
        "0ms",

      /* ======================================================
         CURVAS
      ====================================================== */

      "--page-shell-enter-ease":
        "cubic-bezier(0.16, 1, 0.3, 1)",

      "--page-shell-leave-ease":
        "linear",

      /* ======================================================
         ELEMENTOS DECORATIVOS
      ====================================================== */

      "--route-accent-duration":
        "420ms",

      "--route-glow-duration":
        "520ms",

      "--route-accent-height":
        "2px",

      "--route-accent-opacity":
        "0.95",

      "--route-glow-opacity":
        "0.28",

      /* ======================================================
         MOVIMIENTO DEL CONTENIDO DESACTIVADO
      ====================================================== */

      "--page-shell-enter-x":
        "0px",

      "--page-shell-enter-y":
        "0px",

      "--page-shell-leave-x":
        "0px",

      "--page-shell-leave-y":
        "0px",

      "--page-shell-enter-scale":
        "1",

      "--page-shell-leave-scale":
        "1",

      /* ======================================================
         ROTACIÓN Y DEFORMACIÓN DESACTIVADAS
      ====================================================== */

      "--page-shell-enter-rotate":
        "0deg",

      "--page-shell-leave-rotate":
        "0deg",

      "--page-shell-enter-rotate-x":
        "0deg",

      "--page-shell-leave-rotate-x":
        "0deg",

      "--page-shell-enter-rotate-y":
        "0deg",

      "--page-shell-leave-rotate-y":
        "0deg",

      "--page-shell-enter-skew-x":
        "0deg",

      "--page-shell-leave-skew-x":
        "0deg",

      "--page-shell-enter-skew-y":
        "0deg",

      "--page-shell-leave-skew-y":
        "0deg",

      /* ======================================================
         FILTROS DESACTIVADOS
      ====================================================== */

      "--page-shell-enter-blur":
        "0px",

      "--page-shell-leave-blur":
        "0px",

      "--page-shell-enter-saturate":
        "1",

      "--page-shell-leave-saturate":
        "1",

      "--page-shell-enter-brightness":
        "1",

      "--page-shell-leave-brightness":
        "1",

      "--page-shell-enter-clip-path":
        "none",

      "--page-shell-leave-clip-path":
        "none",

      /* ======================================================
         ANIMACIONES INTERNAS DESACTIVADAS
      ====================================================== */

      "--page-stage-duration-base":
        "0ms",

      "--page-stagger-step-base":
        "0ms",

      "--page-delay-1-base":
        "0ms",

      "--page-delay-2-base":
        "0ms",

      "--page-delay-3-base":
        "0ms",

      "--page-delay-4-base":
        "0ms",

      "--page-delay-5-base":
        "0ms",

      "--page-delay-6-base":
        "0ms",

      "--page-stage-x":
        "0px",

      "--page-stage-y":
        "0px",

      "--page-stage-scale":
        "1",

      "--page-stage-rotate":
        "0deg",

      "--page-stage-blur":
        "0px",

      "--page-stage-saturate":
        "1",

      "--page-stage-brightness":
        "1",
    }),
  });

/* ============================================================
   TRANSICIONES DISPONIBLES
============================================================ */

export const TRANSICIONES_RUTA =
  Object.freeze([
    INSTITUTIONAL_REVEAL_PRESET,
  ]);

/* ============================================================
   TRANSICIÓN PREDETERMINADA
============================================================ */

export const TRANSICION_RUTA_DEFAULT =
  "institutional-reveal";

/* ============================================================
   NORMALIZACIÓN
============================================================ */

/**
 * Devuelve una transición registrada.
 *
 * Los valores antiguos almacenados, como:
 *
 * - module-loading
 * - soft-rise
 * - institutional-indicator
 * - professional-fade
 *
 * se reemplazan automáticamente por institutional-reveal.
 */
export function normalizeRouteTransition(
  value
) {
  const requestedValue =
    String(value ?? "").trim();

  const exists =
    TRANSICIONES_RUTA.some(
      (preset) =>
        preset.value ===
        requestedValue
    );

  return exists
    ? requestedValue
    : TRANSICION_RUTA_DEFAULT;
}

/* ============================================================
   OBTENER PRESET
============================================================ */

export function getRouteTransitionPreset(
  value
) {
  const normalizedValue =
    normalizeRouteTransition(value);

  return (
    TRANSICIONES_RUTA.find(
      (preset) =>
        preset.value ===
        normalizedValue
    ) ??
    INSTITUTIONAL_REVEAL_PRESET
  );
}