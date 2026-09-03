<template>
  <div class="admin-empty-state" role="status">
    <strong>{{ title }}</strong>
    <span v-if="message">{{ message }}</span>
    <button
      v-if="actionLabel"
      type="button"
      class="admin-empty-state__action"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
defineEmits(["action"]);

defineProps({
  title: {
    type: String,
    default: "No hay información disponible",
  },
  message: {
    type: String,
    default: "",
  },
  actionLabel: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.admin-empty-state {
  display: grid;
  justify-items: start;
  gap: 0.35rem;
  width: 100%;
  padding: 1.25rem;
  border: 1px dashed var(--sgpc-border, rgba(15, 23, 42, 0.16));
  border-radius: 14px;
}

.admin-empty-state strong { font-size: 0.95rem; }
.admin-empty-state span { font-size: 0.85rem; opacity: 0.7; }

.admin-empty-state__action {
  margin-top: 0.4rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 650;
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
}
</style>
