<template>
  <div class="admin-inline-loader" role="status" aria-live="polite">
    <span class="admin-inline-loader__spinner" aria-hidden="true"></span>
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: "Actualizando información…",
  },
});
</script>

<style scoped>
.admin-inline-loader {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2rem;
  padding: 0.4rem 0.65rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  background: color-mix(in srgb, currentColor 6%, transparent);
  opacity: 0.78;
}

.admin-inline-loader__spinner {
  width: 0.9rem;
  height: 0.9rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 999px;
  animation: admin-inline-spin 0.75s linear infinite;
}

@keyframes admin-inline-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .admin-inline-loader__spinner { animation: none; }
}
</style>
