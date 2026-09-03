<template>
  <div class="admin-error-state" role="alert">
    <div class="admin-error-state__copy">
      <strong>{{ title }}</strong>
      <span v-if="message">{{ message }}</span>
    </div>

    <button
      v-if="retryLabel"
      type="button"
      class="admin-error-state__action"
      :disabled="retrying"
      @click="$emit('retry')"
    >
      {{ retrying ? "Reintentando…" : retryLabel }}
    </button>
  </div>
</template>

<script setup>
defineEmits(["retry"]);

defineProps({
  title: {
    type: String,
    default: "No pudimos cargar la información.",
  },
  message: {
    type: String,
    default: "",
  },
  retryLabel: {
    type: String,
    default: "Reintentar",
  },
  retrying: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.admin-error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  padding: 1rem 1.1rem;
  border: 1px solid rgba(185, 28, 28, 0.22);
  border-radius: 12px;
  background: rgba(185, 28, 28, 0.06);
}

.admin-error-state__copy {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.admin-error-state__copy strong { font-size: 0.9rem; }
.admin-error-state__copy span { font-size: 0.82rem; opacity: 0.78; }

.admin-error-state__action {
  flex: 0 0 auto;
  min-height: 2.2rem;
  padding: 0.45rem 0.8rem;
  border: 1px solid currentColor;
  border-radius: 9px;
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 650;
  cursor: pointer;
}

.admin-error-state__action:disabled {
  cursor: default;
  opacity: 0.55;
}

@media (max-width: 640px) {
  .admin-error-state { align-items: stretch; flex-direction: column; }
  .admin-error-state__action { align-self: flex-start; }
}
</style>
