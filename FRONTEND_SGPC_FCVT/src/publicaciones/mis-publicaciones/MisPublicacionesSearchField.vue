<template>
  <div
    class="sgpc-mispub-search"
    role="search"
  >
    <span
      class="sgpc-mispub-search__icon"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M10.5 18a7.5 7.5 0 1 1 5.15-2.05L20.7 21l-1.4 1.4-5.05-5.05A7.47 7.47 0 0 1 10.5 18Zm0-2a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11Z"
        />
      </svg>
    </span>

    <input
      ref="inputEl"
      :value="modelValue"
      class="sgpc-mispub-search__input"
      type="text"
      inputmode="search"
      autocomplete="off"
      :placeholder="placeholder"
      aria-label="Buscar publicaciones"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <button
      v-if="modelValue"
      type="button"
      class="sgpc-mispub-search__clear"
      aria-label="Limpiar búsqueda"
      title="Limpiar búsqueda"
      @click="clear"
    >
      <span aria-hidden="true">
        ×
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  modelValue: {
    type: String,
    default: "",
  },

  placeholder: {
    type: String,
    default: "Buscar publicaciones",
  },
});

const emit = defineEmits([
  "update:modelValue",
]);

const inputEl = ref(null);

function focus() {
  inputEl.value?.focus();
}

function clear() {
  emit(
    "update:modelValue",
    ""
  );

  focus();
}

defineExpose({
  focus,
});
</script>

<style scoped>
.sgpc-mispub-search,
.sgpc-mispub-search * {
  box-sizing: border-box;
}

.sgpc-mispub-search {
  position: relative;

  width: 100%;
  min-width: 0;
  min-height: 46px;

  display: grid;
  grid-template-columns:
    19px
    minmax(0, 1fr)
    auto;

  align-items: center;
  gap: 9px;

  padding:
    0
    10px
    0
    13px;

  border:
    1px solid
    var(--border-color, #d8e1ec);

  border-radius: 10px;

  background:
    var(--bg-input, var(--bg-card, #ffffff));

  color:
    var(--text-secondary, #667085);

  box-shadow: none;

  transition:
    border-color 150ms ease,
    background 150ms ease,
    box-shadow 150ms ease;
}

.sgpc-mispub-search:hover {
  border-color:
    var(--border-strong, #bcc8d7);
}

.sgpc-mispub-search:focus-within {
  border-color:
    var(
      --color-primary-effective,
      var(--color-primary, #245f98)
    );

  box-shadow:
    0 0 0 3px
    color-mix(
      in srgb,
      var(--color-primary, #245f98) 11%,
      transparent
    );
}

.sgpc-mispub-search__icon {
  width: 19px;
  height: 19px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  color:
    var(--text-secondary, #667085);
}

.sgpc-mispub-search__icon svg {
  width: 19px;
  height: 19px;

  display: block;
}

.sgpc-mispub-search__input {
  all: unset;

  box-sizing: border-box;

  width: 100%;
  min-width: 0;
  height: 44px;

  display: block;

  color:
    var(--text-primary, #172033);

  font-family:
    var(--font-body, system-ui, sans-serif);

  font-size: 0.82rem;
  font-weight: 540;
  line-height: 1.3;

  cursor: text;
}

.sgpc-mispub-search__input::placeholder {
  color:
    var(--text-disabled, #98a2b3);

  opacity: 1;
}

.sgpc-mispub-search__clear {
  all: unset;

  box-sizing: border-box;

  width: 30px;
  height: 30px;

  display: inline-grid;
  place-items: center;

  border-radius: 8px;

  color:
    var(--text-secondary, #667085);

  font-family:
    var(--font-body, system-ui, sans-serif);

  font-size: 1.05rem;
  line-height: 1;

  cursor: pointer;

  transition:
    background 150ms ease,
    color 150ms ease;
}

.sgpc-mispub-search__clear:hover {
  background:
    var(--bg-elevated, #f4f7fb);

  color:
    var(--text-primary, #172033);
}

.sgpc-mispub-search__clear:focus-visible {
  outline:
    2px solid
    var(
      --color-primary-effective,
      var(--color-primary, #245f98)
    );

  outline-offset: 2px;
}

@media (max-width: 680px) {
  .sgpc-mispub-search {
    min-height: 44px;

    padding-left: 11px;
  }

  .sgpc-mispub-search__input {
    height: 42px;

    font-size: 0.8rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sgpc-mispub-search,
  .sgpc-mispub-search * {
    transition: none !important;
  }
}

</style>
