<template>
  <div
    v-if="message"
    class="admin-action-feedback"
    :data-status="status"
    :role="status === 'error' ? 'alert' : 'status'"
    aria-live="polite"
  >
    <span
      v-if="status === 'loading'"
      class="admin-action-feedback__spinner"
      aria-hidden="true"
    ></span>
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
defineProps({
  status: {
    type: String,
    default: "idle",
    validator: (value) => ["idle", "loading", "success", "error", "info"].includes(value),
  },
  message: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.admin-action-feedback {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2rem;
  padding: 0.45rem 0.7rem;
  border-radius: 9px;
  font-size: 0.82rem;
  font-weight: 600;
  background: color-mix(in srgb, currentColor 6%, transparent);
}

.admin-action-feedback[data-status="success"] { color: var(--sgpc-success, #166534); }
.admin-action-feedback[data-status="error"] { color: var(--sgpc-danger, #991b1b); }
.admin-action-feedback[data-status="loading"] { opacity: 0.78; }

.admin-action-feedback__spinner {
  width: 0.85rem;
  height: 0.85rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 999px;
  animation: admin-action-spin 0.75s linear infinite;
}

@keyframes admin-action-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .admin-action-feedback__spinner { animation: none; }
}
</style>
