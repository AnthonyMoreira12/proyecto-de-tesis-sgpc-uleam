<template>
  <Teleport to="body">
    <Transition name="avh-overlay">
      <div
        v-if="modelValue"
        ref="dialogRoot"
        class="avn-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="avn-overlay-title"
        tabindex="-1"
        @keydown="onDialogKeydown"
      >
        <h2
          id="avn-overlay-title"
          class="avn-sr-only"
        >
          Avisos institucionales del SGPC ULEAM
        </h2>

        <button
          class="avn-overlay__backdrop"
          type="button"
          tabindex="-1"
          aria-label="Cerrar avisos"
          @click="cerrarOverlay"
        ></button>

        <div
          ref="dialogShell"
          class="avn-shell"
          tabindex="-1"
        >
          <BannerPrincipal
            :key="`${version}:${initialManage ? 'manage' : 'view'}`"
            :user="user"
            :version="version"
            :initial-manage="initialManage"
            @continue="cerrarOverlay"
            @version-change="propagarCambioVersion"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import {
  nextTick,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";

import BannerPrincipal from "../banner-principal/BannerPrincipal.vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },

  user: {
    type: Object,
    default: null,
  },

  version: {
    type: String,
    default: "",
  },

  initialManage: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "continue",
  "version-change",
]);

const dialogRoot = ref(null);
const dialogShell = ref(null);

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

let previousBodyOverflow = "";
let previousBodyPaddingRight = "";
let previousFocusedElement = null;
let closing = false;
let bodyLocked = false;

const getFocusableElements = () => {
  const root = dialogRoot.value;

  if (!root) return [];

  return [
    ...root.querySelectorAll(
      FOCUSABLE_SELECTOR
    ),
  ].filter((element) => {
    const style =
      window.getComputedStyle(element);

    return (
      style.visibility !== "hidden" &&
      style.display !== "none"
    );
  });
};

const lockBodyScroll = () => {
  if (bodyLocked) return;

  const scrollbarWidth =
    window.innerWidth -
    document.documentElement.clientWidth;

  previousBodyOverflow =
    document.body.style.overflow;

  previousBodyPaddingRight =
    document.body.style.paddingRight;

  document.body.style.overflow = "hidden";

  if (scrollbarWidth > 0) {
    document.body.style.paddingRight =
      `${scrollbarWidth}px`;
  }

  bodyLocked = true;
};

const unlockBodyScroll = () => {
  if (!bodyLocked) return;

  document.body.style.overflow =
    previousBodyOverflow;

  document.body.style.paddingRight =
    previousBodyPaddingRight;

  bodyLocked = false;
};

const focusDialog = async () => {
  await nextTick();

  const focusable =
    getFocusableElements();

  const preferred = focusable.find(
    (element) =>
      element.getAttribute(
        "data-autofocus"
      ) === "true"
  );

  const target =
    preferred ||
    focusable[0] ||
    dialogShell.value ||
    dialogRoot.value;

  target?.focus?.();
};

const cerrarOverlay = () => {
  if (closing) return;

  closing = true;

  emit("update:modelValue", false);
  emit("continue");

  queueMicrotask(() => {
    closing = false;
  });
};

const propagarCambioVersion = (
  nextVersion
) => {
  emit("version-change", nextVersion);
};

const trapFocus = (event) => {
  if (event.key !== "Tab") return;

  const focusable =
    getFocusableElements();

  if (!focusable.length) {
    event.preventDefault();
    dialogShell.value?.focus?.();
    return;
  }

  const first = focusable[0];
  const last =
    focusable[focusable.length - 1];

  const active =
    document.activeElement;

  const focusOutsideDialog =
    !dialogRoot.value?.contains(active);

  if (
    event.shiftKey &&
    (active === first ||
      focusOutsideDialog)
  ) {
    event.preventDefault();
    last.focus();
    return;
  }

  if (
    !event.shiftKey &&
    active === last
  ) {
    event.preventDefault();
    first.focus();
  }
};

const onDialogKeydown = (event) => {
  if (!props.modelValue) return;

  if (event.key === "Escape") {
    event.preventDefault();
    cerrarOverlay();
    return;
  }

  trapFocus(event);
};

watch(
  () => props.modelValue,
  async (visible) => {
    if (visible) {
      previousFocusedElement =
        document.activeElement instanceof
        HTMLElement
          ? document.activeElement
          : null;

      lockBodyScroll();
      await focusDialog();

      return;
    }

    unlockBodyScroll();

    await nextTick();

    previousFocusedElement?.focus?.();
    previousFocusedElement = null;
  },
  {
    immediate: true,
  }
);

onBeforeUnmount(() => {
  unlockBodyScroll();

  previousFocusedElement?.focus?.();
  previousFocusedElement = null;
});
</script>

<style
  scoped
  src="./avisos-home-overlay.css"
></style>