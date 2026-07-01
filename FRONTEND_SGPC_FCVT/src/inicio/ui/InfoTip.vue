<template>
  <span class="infotip" ref="root">
    <button
      class="infotip__btn"
      type="button"
      :aria-label="label || 'Información'"
      :title="label || 'Información'"
      :aria-expanded="open ? 'true' : 'false'"
      :aria-controls="panelId"
      @click="toggle"
      @keydown.esc.stop.prevent="close"
    >
      <span class="infotip__btn-text" aria-hidden="true">i</span>
    </button>

    <Transition name="infotip-fade">
      <div
        v-if="open"
        :id="panelId"
        class="infotip__panel"
        role="dialog"
        aria-live="polite"
      >
        <div class="infotip__title" v-if="title">{{ title }}</div>

        <div class="infotip__text">
          <slot />
        </div>
      </div>
    </Transition>
  </span>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

defineProps({
  title: { type: String, default: "" },
  label: { type: String, default: "" },
});

const open = ref(false);
const root = ref(null);
const panelId = `infotip-panel-${Math.random().toString(36).slice(2, 10)}`;

const close = () => {
  open.value = false;
};

const toggle = () => {
  open.value = !open.value;
};

const onDocClick = (e) => {
  if (!open.value || !root.value) return;
  if (!root.value.contains(e.target)) close();
};

const onDocKeydown = (e) => {
  if (e.key === "Escape") close();
};

onMounted(() => {
  document.addEventListener("click", onDocClick, true);
  document.addEventListener("keydown", onDocKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick, true);
  document.removeEventListener("keydown", onDocKeydown);
});
</script>

<style scoped>
.infotip {
  --it-bg: var(--bg-card, #ffffff);
  --it-surface: var(--bg-elevated, var(--bg-card, #ffffff));
  --it-text: var(--text-primary, #111111);
  --it-muted: var(--text-secondary, #5f5a53);
  --it-line: color-mix(in srgb, var(--border-color, rgba(17, 17, 17, 0.1)) 92%, transparent);
  --it-line-strong: color-mix(
    in srgb,
    var(--border-strong, rgba(17, 17, 17, 0.14)) 92%,
    transparent
  );
  --it-accent: var(--color-primary, #111111);
  --it-shadow: var(--shadow-strong, 0 18px 50px rgba(0, 0, 0, 0.16));

  position: relative;
  display: inline-flex;
  align-items: center;
}

.infotip__btn {
  width: 24px;
  height: 24px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid var(--it-line);
  background: color-mix(in srgb, var(--it-bg) 94%, transparent);
  color: var(--it-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  cursor: pointer;
  transition:
    transform var(--t-fast, 0.18s ease),
    box-shadow var(--t-fast, 0.18s ease),
    border-color var(--t-fast, 0.18s ease),
    background var(--t-fast, 0.18s ease),
    color var(--t-fast, 0.18s ease);
}

.infotip__btn:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--it-accent) 18%, var(--it-line-strong));
  background: color-mix(in srgb, var(--it-accent) 6%, var(--it-bg));
  color: var(--it-text);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.infotip__btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px var(--focus-ring, rgba(17, 17, 17, 0.14));
}

.infotip__btn-text {
  font-size: 12px;
  font-weight: 900;
  transform: translateY(-0.5px);
}

.infotip__panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: min(360px, 84vw);
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--it-line);
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--it-surface) 96%, transparent),
      color-mix(in srgb, var(--it-bg) 100%, transparent)
    );
  box-shadow: var(--it-shadow);
  z-index: 999;
}

.infotip__panel::before {
  content: "";
  position: absolute;
  top: -1px;
  left: 0;
  width: 100%;
  height: 2px;
  border-radius: 16px 16px 0 0;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--it-accent) 36%, transparent),
    color-mix(in srgb, var(--it-accent) 10%, transparent)
  );
}

.infotip__title {
  margin: 0 0 6px;
  color: var(--it-text);
  font-family: var(--font-serif, var(--font-sans));
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.infotip__text {
  color: var(--it-muted);
  font-size: 0.88rem;
  line-height: 1.58;
}

.infotip-fade-enter-active,
.infotip-fade-leave-active {
  transition:
    opacity var(--t-fast, 0.18s ease),
    transform var(--t-fast, 0.18s ease);
}

.infotip-fade-enter-from,
.infotip-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

:global(html.dark) .infotip,
:global(.dark) .infotip,
:global([data-theme="dark"]) .infotip {
  --it-shadow: 0 22px 70px rgba(0, 0, 0, 0.42);
}

:global(html.dark) .infotip__panel,
:global(.dark) .infotip__panel,
:global([data-theme="dark"]) .infotip__panel {
  border-color: rgba(255, 255, 255, 0.1);
}

@media (prefers-reduced-motion: reduce) {
  .infotip__btn,
  .infotip-fade-enter-active,
  .infotip-fade-leave-active {
    transition: none !important;
  }
}
</style>