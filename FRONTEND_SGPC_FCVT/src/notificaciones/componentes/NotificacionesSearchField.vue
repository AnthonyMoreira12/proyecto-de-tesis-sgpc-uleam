<template>
  <div
    class="sgpc-ntf-search"
    role="search"
    aria-label="Buscar notificaciones"
  >
    <div class="sgpc-ntf-search__field">
      <span
        class="sgpc-ntf-search__icon"
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
        class="sgpc-ntf-search__input"
        type="text"
        inputmode="search"
        autocomplete="off"
        spellcheck="false"
        :value="modelValue"
        :placeholder="placeholder"
        aria-label="Buscar notificaciones"
        @input="onInput"
        @keydown.esc="clearSearch"
      />

      <button
        v-if="modelValue"
        class="sgpc-ntf-search__clear"
        type="button"
        aria-label="Limpiar búsqueda"
        title="Limpiar búsqueda"
        @click="clearSearch"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M18.3 5.71 12 12l6.3 6.29-1.41 1.42L10.59 13.4 4.29 19.71 2.88 18.3 9.17 12 2.88 5.71 4.29 4.29l6.3 6.3 6.3-6.3 1.41 1.42Z"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },

  placeholder: {
    type: String,
    default: "Buscar notificaciones",
  },
});

const emit = defineEmits([
  "update:modelValue",
]);

const onInput = (event) => {
  emit(
    "update:modelValue",
    event?.target?.value ?? ""
  );
};

const clearSearch = () => {
  emit("update:modelValue", "");
};
</script>

<style scoped>
/* Aislado para evitar reglas globales heredadas sobre inputs. */
.sgpc-ntf-search,
.sgpc-ntf-search *,
.sgpc-ntf-search *::before,
.sgpc-ntf-search *::after {
  box-sizing: border-box;
}

.sgpc-ntf-search {
  all: initial;

  width: 100%;
  min-width: 0;

  display: block;

  color: var(--text-primary, #172033);

  font-family:
    var(
      --font-body,
      Inter,
      ui-sans-serif,
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      sans-serif
    );
}

.sgpc-ntf-search__field {
  position: relative;

  width: 100%;
  height: 44px;
  min-width: 0;

  display: flex;
  align-items: center;
  gap: 9px;

  padding: 0 8px 0 12px;

  overflow: hidden;

  border:
    1px solid
    var(--border-color, #d9e0e8);

  border-radius: 11px;

  background:
    var(
      --bg-input,
      var(--bg-card, #ffffff)
    );

  box-shadow: none;

  transition:
    border-color 150ms ease,
    background 150ms ease,
    box-shadow 150ms ease;
}

.sgpc-ntf-search__field:hover {
  border-color:
    var(--border-strong, #bdc8d5);
}

.sgpc-ntf-search__field:focus-within {
  border-color:
    var(
      --color-primary-effective,
      var(--color-primary, #1d4ed8)
    );

  background: var(--bg-card, #ffffff);

  box-shadow:
    0 0 0 3px
    color-mix(
      in srgb,
      var(--color-primary, #1d4ed8) 11%,
      transparent
    );
}

.sgpc-ntf-search__icon {
  all: unset;

  flex: 0 0 18px;

  width: 18px;
  height: 18px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  color: var(--text-secondary, #667085);

  pointer-events: none;
}

.sgpc-ntf-search__field:focus-within
  .sgpc-ntf-search__icon {
  color:
    var(
      --color-primary-effective,
      var(--color-primary, #1d4ed8)
    );
}

.sgpc-ntf-search__icon svg {
  all: unset;

  width: 17px;
  height: 17px;

  display: block;
}

.sgpc-ntf-search__input {
  all: unset !important;

  box-sizing: border-box !important;

  flex: 1 1 auto !important;

  width: auto !important;
  min-width: 0 !important;
  height: 42px !important;

  display: block !important;

  margin: 0 !important;
  padding: 0 !important;

  border: 0 !important;
  border-radius: 0 !important;
  outline: 0 !important;

  background: transparent !important;
  box-shadow: none !important;

  color: var(--text-primary, #172033) !important;

  font-family: inherit !important;
  font-size: 0.77rem !important;
  font-style: normal !important;
  font-weight: 520 !important;
  line-height: 1.2 !important;
  letter-spacing: 0 !important;

  text-align: left !important;

  appearance: none !important;
  -webkit-appearance: none !important;

  opacity: 1 !important;
  transform: none !important;
}

.sgpc-ntf-search__input::placeholder {
  color: var(--text-disabled, #98a2b3) !important;
  opacity: 1 !important;
}

.sgpc-ntf-search__clear {
  all: unset !important;

  box-sizing: border-box !important;

  flex: 0 0 28px !important;

  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;

  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;

  margin: 0 !important;
  padding: 0 !important;

  border: 0 !important;
  border-radius: 8px !important;

  background: transparent !important;

  color: var(--text-secondary, #667085) !important;

  cursor: pointer !important;

  transition:
    background 150ms ease,
    color 150ms ease !important;
}

.sgpc-ntf-search__clear:hover {
  background: var(--bg-soft, #f5f7fb) !important;
  color: var(--text-primary, #172033) !important;
}

.sgpc-ntf-search__clear:focus-visible {
  outline:
    2px solid
    var(--focus-outline, #1d4ed8) !important;

  outline-offset: 1px !important;
}

.sgpc-ntf-search__clear svg {
  all: unset;

  width: 13px;
  height: 13px;

  display: block;
}

@media (pointer: coarse) {
  .sgpc-ntf-search__field {
    height: 46px;
  }

  .sgpc-ntf-search__input {
    height: 44px !important;
  }

  .sgpc-ntf-search__clear {
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sgpc-ntf-search__field,
  .sgpc-ntf-search__clear {
    transition: none !important;
  }
}
</style>
