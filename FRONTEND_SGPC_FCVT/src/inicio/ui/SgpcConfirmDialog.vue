<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="sgpc-modal-overlay sgpc-confirm-overlay"
      role="presentation"
      @click.self="cancel"
    >
      <section
        class="sgpc-modal-card sgpc-confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="messageId"
      >
        <header class="sgpc-confirm-dialog__header">
          <div>
            <span v-if="eyebrow" class="sgpc-confirm-dialog__eyebrow">{{ eyebrow }}</span>
            <h2 :id="titleId">{{ title }}</h2>
          </div>
          <button
            class="sgpc-confirm-dialog__close"
            type="button"
            aria-label="Cerrar"
            :disabled="busy"
            @click="cancel"
          >
            ×
          </button>
        </header>

        <div class="sgpc-confirm-dialog__body">
          <p :id="messageId">{{ message }}</p>
          <slot />
        </div>

        <footer class="sgpc-confirm-dialog__footer">
          <button
            type="button"
            class="sgpc-confirm-dialog__button sgpc-confirm-dialog__button--secondary"
            :disabled="busy"
            @click="cancel"
          >
            {{ cancelLabel }}
          </button>
          <button
            ref="confirmButton"
            type="button"
            class="sgpc-confirm-dialog__button"
            :class="`sgpc-confirm-dialog__button--${tone}`"
            :disabled="busy"
            @click="accept"
          >
            {{ busy ? busyLabel : confirmLabel }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useModalLayer } from "../../scripts/composables/useModalLayer";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: "Confirmar acción" },
  message: { type: String, default: "¿Desea continuar?" },
  eyebrow: { type: String, default: "" },
  confirmLabel: { type: String, default: "Confirmar" },
  cancelLabel: { type: String, default: "Cancelar" },
  busyLabel: { type: String, default: "Procesando…" },
  tone: {
    type: String,
    default: "primary",
    validator: (value) => ["primary", "danger", "warning"].includes(value),
  },
  busy: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "confirm", "cancel"]);
const confirmButton = ref(null);
const isOpen = computed(() => props.modelValue);
const uid = Math.random().toString(36).slice(2, 9);
const titleId = `sgpc-confirm-title-${uid}`;
const messageId = `sgpc-confirm-message-${uid}`;

useModalLayer(isOpen);

function close() {
  emit("update:modelValue", false);
}

function cancel() {
  if (props.busy) return;
  close();
  emit("cancel");
}

function accept() {
  if (props.busy) return;
  close();
  emit("confirm");
}

function onKeydown(event) {
  if (!props.modelValue || props.busy) return;
  if (event.key === "Escape") {
    event.preventDefault();
    cancel();
  }
}

watch(
  () => props.modelValue,
  async (open) => {
    if (!open) return;
    await nextTick();
    confirmButton.value?.focus();
  },
);

onMounted(() => window.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", onKeydown));
</script>

<style src="./sgpc-confirm-dialog.css"></style>
