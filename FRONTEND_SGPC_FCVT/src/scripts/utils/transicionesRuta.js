const MODULE_LOADING_PRESET = {
  value: "module-loading",
  label: "Animación de carga de módulos",
  desc: "Carga progresiva por bloques.",
  tier: "Estándar",
  intensity: "3/5",
  bestFor: "Paneles y módulos",
  vars: {
    "--page-shell-enter-duration-base": "760ms",
    "--page-shell-leave-duration-base": "320ms",
    "--page-shell-enter-ease": "cubic-bezier(0.16, 0.9, 0.2, 1)",
    "--page-shell-leave-ease": "cubic-bezier(0.32, 0, 0.2, 1)",
    "--page-shell-enter-origin": "50% 60%",
    "--page-shell-leave-origin": "50% 40%",

    "--page-shell-enter-perspective": "1400px",
    "--page-shell-leave-perspective": "1400px",

    "--page-shell-enter-x": "0px",
    "--page-shell-enter-y": "18px",
    "--page-shell-leave-x": "0px",
    "--page-shell-leave-y": "-8px",

    "--page-shell-enter-scale": "0.985",
    "--page-shell-leave-scale": "1.002",

    "--page-shell-enter-rotate": "0deg",
    "--page-shell-leave-rotate": "0deg",
    "--page-shell-enter-rotate-x": "0deg",
    "--page-shell-leave-rotate-x": "0deg",
    "--page-shell-enter-rotate-y": "0deg",
    "--page-shell-leave-rotate-y": "0deg",
    "--page-shell-enter-skew-x": "0deg",
    "--page-shell-leave-skew-x": "0deg",
    "--page-shell-enter-skew-y": "0deg",
    "--page-shell-leave-skew-y": "0deg",

    "--page-shell-enter-blur": "8px",
    "--page-shell-leave-blur": "3px",
    "--page-shell-enter-saturate": "0.96",
    "--page-shell-leave-saturate": "0.99",
    "--page-shell-enter-brightness": "1",
    "--page-shell-leave-brightness": "1",
    "--page-shell-enter-clip-path": "polygon(0 0, 100% 0, 100% 100%, 0 100%)",
    "--page-shell-leave-clip-path": "polygon(0 0, 100% 0, 100% 100%, 0 100%)",

    "--page-stage-duration-base": "620ms",
    "--page-stagger-step-base": "96ms",
    "--page-delay-1-base": "95ms",
    "--page-delay-2-base": "190ms",
    "--page-delay-3-base": "285ms",
    "--page-delay-4-base": "380ms",
    "--page-delay-5-base": "475ms",
    "--page-delay-6-base": "570ms",
    "--page-stage-x": "0px",
    "--page-stage-y": "18px",
    "--page-stage-scale": "0.972",
    "--page-stage-rotate": "0deg",
    "--page-stage-blur": "6px",
    "--page-stage-saturate": "0.992",
    "--page-stage-brightness": "0.98",
  },
};

export const TRANSICIONES_RUTA = [MODULE_LOADING_PRESET];
export const TRANSICION_RUTA_DEFAULT = "module-loading";

export function normalizeRouteTransition() {
  return TRANSICION_RUTA_DEFAULT;
}

export function getRouteTransitionPreset() {
  return MODULE_LOADING_PRESET;
}