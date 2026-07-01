<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="avn-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Avisos institucionales"
    >
      <div class="avn-overlay__backdrop" @click="cerrarOverlay"></div>

      <div class="avn-shell">
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
  </Teleport>
</template>

<script setup>
import { onBeforeUnmount, watch } from "vue";
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

const emit = defineEmits(["update:modelValue", "continue", "version-change"]);

let previousBodyOverflow = "";
let keyHandlerBound = false;

const cerrarOverlay = () => {
  emit("update:modelValue", false);
  emit("continue");
};

const propagarCambioVersion = (nextVersion) => {
  emit("version-change", nextVersion);
};

const onGlobalKeydown = (event) => {
  if (!props.modelValue) return;

  if (event.key === "Escape") {
    event.preventDefault();
    cerrarOverlay();
  }
};

const bindGlobal = () => {
  if (keyHandlerBound) return;

  previousBodyOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";

  window.addEventListener("keydown", onGlobalKeydown);
  keyHandlerBound = true;
};

const unbindGlobal = () => {
  if (!keyHandlerBound) return;

  window.removeEventListener("keydown", onGlobalKeydown);
  document.body.style.overflow = previousBodyOverflow;
  keyHandlerBound = false;
};

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      bindGlobal();
    } else {
      unbindGlobal();
    }
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  unbindGlobal();
});
</script>

<style scoped src="./avisos-home-overlay.css"></style>