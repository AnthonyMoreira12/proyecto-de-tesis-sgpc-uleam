<template>
  <div
    class="admin-loading-state"
    role="status"
    aria-live="polite"
    :aria-label="message"
  >
    <span class="admin-loading-state__spinner" aria-hidden="true"></span>

    <div class="admin-loading-state__copy">
      <strong>{{ message }}</strong>
      <span v-if="description">{{ description }}</span>
    </div>

    <div
      v-if="skeleton"
      class="admin-loading-state__skeleton"
      aria-hidden="true"
    >
      <span v-for="row in rows" :key="row"></span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  message: {
    type: String,
    default: "Cargando información…",
  },
  description: {
    type: String,
    default: "",
  },
  skeleton: {
    type: Boolean,
    default: true,
  },
  skeletonRows: {
    type: Number,
    default: 4,
  },
});

const rows = computed(() => {
  const count = Number(props.skeletonRows);
  return Number.isFinite(count) && count > 0
    ? Math.min(Math.trunc(count), 8)
    : 4;
});
</script>

<style scoped>
.admin-loading-state {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.85rem 1rem;
  align-items: center;
  width: 100%;
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--sgpc-border, rgba(15, 23, 42, 0.12));
  border-radius: 14px;
  background: var(--sgpc-surface, #fff);
}

.admin-loading-state__spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 999px;
  opacity: 0.72;
  animation: admin-loading-spin 0.75s linear infinite;
}

.admin-loading-state__copy {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.admin-loading-state__copy strong {
  font-size: 0.95rem;
  font-weight: 650;
}

.admin-loading-state__copy span {
  font-size: 0.84rem;
  opacity: 0.7;
}

.admin-loading-state__skeleton {
  grid-column: 1 / -1;
  display: grid;
  gap: 0.55rem;
  margin-top: 0.2rem;
}

.admin-loading-state__skeleton span {
  display: block;
  height: 0.72rem;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    rgba(148, 163, 184, 0.14),
    rgba(148, 163, 184, 0.28),
    rgba(148, 163, 184, 0.14)
  );
  background-size: 220% 100%;
  animation: admin-loading-shimmer 1.35s ease-in-out infinite;
}

.admin-loading-state__skeleton span:nth-child(2n) {
  width: 82%;
}

.admin-loading-state__skeleton span:nth-child(3n) {
  width: 64%;
}

@keyframes admin-loading-spin {
  to { transform: rotate(360deg); }
}

@keyframes admin-loading-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .admin-loading-state__spinner,
  .admin-loading-state__skeleton span {
    animation: none;
  }
}
</style>
