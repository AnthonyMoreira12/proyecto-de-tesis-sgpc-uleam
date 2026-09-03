<template>
  <div class="sgpc-period-picker">
    <div class="sgpc-period-picker__field">
      <span>Desde</span>
      <button
        ref="fromTrigger"
        type="button"
        class="sgpc-period-picker__trigger"
        :class="{ 'has-value': from }"
        :aria-expanded="picker.open && picker.target === 'from'"
        aria-haspopup="dialog"
        @click.stop="toggle('from')"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 2v3M17 2v3M3.5 9h17M5.5 4.5h13a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2Z" />
        </svg>
        <span>{{ formatPeriod(from) || "Mes inicial" }}</span>
        <span aria-hidden="true">▾</span>
      </button>
    </div>

    <div class="sgpc-period-picker__field">
      <span>Hasta</span>
      <button
        ref="toTrigger"
        type="button"
        class="sgpc-period-picker__trigger"
        :class="{ 'has-value': to }"
        :aria-expanded="picker.open && picker.target === 'to'"
        aria-haspopup="dialog"
        @click.stop="toggle('to')"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 2v3M17 2v3M3.5 9h17M5.5 4.5h13a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2Z" />
        </svg>
        <span>{{ formatPeriod(to) || "Mes final" }}</span>
        <span aria-hidden="true">▾</span>
      </button>
    </div>

    <Teleport to="body">
      <Transition name="sgpc-period-popover">
        <section
          v-if="picker.open"
          ref="popoverRef"
          class="sgpc-period-picker__popover"
          :class="{ 'is-up': popover.opensUp }"
          :style="popoverStyle"
          role="dialog"
          aria-label="Seleccionar mes y año"
          @click.stop
        >
          <header class="sgpc-period-picker__nav">
            <button
              type="button"
              aria-label="Año anterior"
              :disabled="!canMove(-1)"
              @click="move(-1)"
            >
              ‹
            </button>

            <select v-model.number="picker.year" aria-label="Año">
              <option
                v-for="year in years"
                :key="year.value"
                :value="Number(year.value)"
              >
                {{ year.label }}
              </option>
            </select>

            <button
              type="button"
              aria-label="Año siguiente"
              :disabled="!canMove(1)"
              @click="move(1)"
            >
              ›
            </button>
          </header>

          <div class="sgpc-period-picker__months">
            <button
              v-for="month in months"
              :key="`${picker.year}-${month.value}`"
              type="button"
              :class="{ 'is-selected': isSelected(month.value) }"
              :disabled="!monthAllowed(month.value)"
              @click="selectMonth(month.value)"
            >
              {{ month.short_label || month.label }}
            </button>
          </div>

          <footer class="sgpc-period-picker__footer">
            <span>{{ rangeLabel }}</span>
            <button type="button" @click="clearTarget">
              Quitar selección
            </button>
          </footer>
        </section>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

const props = defineProps({
  from: { type: String, default: "" },
  to: { type: String, default: "" },
  period: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["update:from", "update:to"]);

const FALLBACK_MONTHS = Object.freeze([
  { value: 1, label: "Enero", short_label: "Ene" },
  { value: 2, label: "Febrero", short_label: "Feb" },
  { value: 3, label: "Marzo", short_label: "Mar" },
  { value: 4, label: "Abril", short_label: "Abr" },
  { value: 5, label: "Mayo", short_label: "May" },
  { value: 6, label: "Junio", short_label: "Jun" },
  { value: 7, label: "Julio", short_label: "Jul" },
  { value: 8, label: "Agosto", short_label: "Ago" },
  { value: 9, label: "Septiembre", short_label: "Sep" },
  { value: 10, label: "Octubre", short_label: "Oct" },
  { value: 11, label: "Noviembre", short_label: "Nov" },
  { value: 12, label: "Diciembre", short_label: "Dic" },
]);

const fromTrigger = ref(null);
const toTrigger = ref(null);
const popoverRef = ref(null);

const picker = reactive({
  open: false,
  target: "from",
  year: null,
});

const popover = reactive({
  top: 0,
  left: 0,
  width: 360,
  maxHeight: 420,
  opensUp: false,
});

const popoverStyle = computed(() => ({
  top: `${popover.top}px`,
  left: `${popover.left}px`,
  width: `${popover.width}px`,
  maxHeight: `${popover.maxHeight}px`,
}));

const years = computed(() => {
  const values = Array.isArray(props.period?.anios)
    ? props.period.anios
    : [];

  if (values.length) return values;

  const current = new Date().getFullYear();
  return [{ value: current, label: String(current) }];
});

const months = computed(() => {
  const values = Array.isArray(props.period?.meses)
    ? props.period.meses
    : [];

  return values.length ? values : FALLBACK_MONTHS;
});

const minPeriod = computed(() => normalize(props.period?.mes_min));
const maxPeriod = computed(() => normalize(props.period?.mes_max));

const rangeLabel = computed(() => {
  const fromLabel = formatPeriod(minPeriod.value);
  const toLabel = formatPeriod(maxPeriod.value);

  return fromLabel && toLabel
    ? `Período disponible: ${fromLabel} — ${toLabel}`
    : "Seleccione el mes que desea consultar";
});

watch(
  () => props.period,
  () => ensureYear(),
  { deep: true }
);

watch(
  () => picker.year,
  () => {
    if (picker.open) nextTick(updatePopoverPosition);
  }
);

function normalize(value) {
  const text = String(value || "").trim();
  return /^\d{4}-(0[1-9]|1[0-2])$/.test(text) ? text : "";
}

function parse(value) {
  const normalized = normalize(value);
  if (!normalized) return null;
  const [year, month] = normalized.split("-").map(Number);
  return { year, month };
}

function formatPeriod(value) {
  const parsed = parse(value);
  if (!parsed) return "";

  const text = new Intl.DateTimeFormat("es-EC", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(parsed.year, parsed.month - 1, 1)));

  return text.charAt(0).toUpperCase() + text.slice(1);
}

function ensureYear() {
  const available = years.value.map((item) => Number(item.value));
  if (!available.length) return;

  if (!available.includes(Number(picker.year))) {
    picker.year = available[0];
  }
}

function activeTrigger() {
  return picker.target === "from" ? fromTrigger.value : toTrigger.value;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function updatePopoverPosition() {
  if (!picker.open || typeof window === "undefined") return;

  const trigger = activeTrigger();
  if (!trigger) return;

  const rect = trigger.getBoundingClientRect();
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  const margin = 8;
  const gap = 6;
  const desiredWidth = 360;
  const width = Math.max(260, Math.min(desiredWidth, viewportWidth - margin * 2));
  const left = clamp(rect.left, margin, Math.max(margin, viewportWidth - width - margin));

  const spaceBelow = Math.max(0, viewportHeight - rect.bottom - gap - margin);
  const spaceAbove = Math.max(0, rect.top - gap - margin);
  const opensUp = spaceBelow < 280 && spaceAbove > spaceBelow;
  const availableHeight = opensUp ? spaceAbove : spaceBelow;
  const maxHeight = Math.max(180, Math.min(420, availableHeight || 420));

  popover.width = width;
  popover.left = left;
  popover.maxHeight = maxHeight;
  popover.opensUp = opensUp;
  popover.top = opensUp
    ? Math.max(margin, rect.top - gap - maxHeight)
    : Math.min(viewportHeight - margin, rect.bottom + gap);

  const element = popoverRef.value;
  if (!element) return;

  const renderedHeight = Math.min(element.offsetHeight || maxHeight, maxHeight);
  popover.top = opensUp
    ? Math.max(margin, rect.top - gap - renderedHeight)
    : clamp(rect.bottom + gap, margin, Math.max(margin, viewportHeight - renderedHeight - margin));
}

async function toggle(target) {
  if (picker.open && picker.target === target) {
    close();
    return;
  }

  picker.target = target;
  const source = target === "from" ? props.from : props.to;
  const reference = parse(source || props.period?.mes_actual || maxPeriod.value);
  picker.year = reference?.year || Number(years.value[0]?.value);
  ensureYear();
  picker.open = true;

  await nextTick();
  updatePopoverPosition();
  window.requestAnimationFrame(updatePopoverPosition);
}

function close() {
  picker.open = false;
}

function canMove(direction) {
  const available = years.value.map((item) => Number(item.value));
  const index = available.indexOf(Number(picker.year));
  if (index < 0) return false;

  const target = direction < 0 ? index + 1 : index - 1;
  return target >= 0 && target < available.length;
}

function move(direction) {
  if (!canMove(direction)) return;
  const available = years.value.map((item) => Number(item.value));
  const index = available.indexOf(Number(picker.year));
  picker.year = available[direction < 0 ? index + 1 : index - 1];
}

function valueFor(month) {
  return `${Number(picker.year)}-${String(Number(month)).padStart(2, "0")}`;
}

function monthAllowed(month) {
  const value = valueFor(month);
  if (minPeriod.value && value < minPeriod.value) return false;
  if (maxPeriod.value && value > maxPeriod.value) return false;
  return true;
}

function isSelected(month) {
  const current = picker.target === "from" ? props.from : props.to;
  return normalize(current) === valueFor(month);
}

function selectMonth(month) {
  if (!monthAllowed(month)) return;

  const selected = valueFor(month);
  let nextFrom = normalize(props.from);
  let nextTo = normalize(props.to);

  if (picker.target === "from") {
    nextFrom = selected;
    if (nextTo && nextFrom > nextTo) nextTo = nextFrom;
  } else {
    nextTo = selected;
    if (nextFrom && nextTo < nextFrom) nextFrom = nextTo;
  }

  emit("update:from", nextFrom);
  emit("update:to", nextTo);
  close();
}

function clearTarget() {
  emit(picker.target === "from" ? "update:from" : "update:to", "");
  close();
}

function documentClick(event) {
  if (!picker.open) return;

  const target = event.target;
  const trigger = activeTrigger();

  if (trigger?.contains?.(target) || popoverRef.value?.contains?.(target)) return;
  close();
}

function documentKeydown(event) {
  if (event.key !== "Escape" || !picker.open) return;
  const trigger = activeTrigger();
  close();
  trigger?.focus?.();
}

onMounted(() => {
  ensureYear();
  document.addEventListener("click", documentClick);
  document.addEventListener("keydown", documentKeydown);
  window.addEventListener("resize", updatePopoverPosition, { passive: true });
  window.addEventListener("scroll", updatePopoverPosition, true);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", documentClick);
  document.removeEventListener("keydown", documentKeydown);
  window.removeEventListener("resize", updatePopoverPosition);
  window.removeEventListener("scroll", updatePopoverPosition, true);
});
</script>

<style scoped>
.sgpc-period-picker,
.sgpc-period-picker__popover {
  --period-card: var(--report-card, var(--my-card, var(--bg-card, #ffffff)));
  --period-soft: var(--report-soft, var(--my-soft, var(--bg-elevated, #f5f7fb)));
  --period-input: var(--report-input, var(--my-input, var(--bg-input, #ffffff)));
  --period-text: var(--report-text, var(--my-text, var(--text-primary, #172033)));
  --period-muted: var(--report-muted, var(--my-muted, var(--text-secondary, #667085)));
  --period-line: var(--report-line, var(--my-line, var(--border-color, #d9e0e8)));
  --period-line-strong: var(--report-line-strong, var(--my-line-strong, var(--border-strong, #bdc8d5)));
  --period-primary: var(--report-primary, var(--my-primary, var(--color-primary, #315fcb)));
  --period-primary-soft: var(--report-primary-soft, var(--my-primary-soft, var(--primary-soft, #edf3ff)));
  --period-ring: var(--adm-ring, var(--my-ring, var(--ring-primary, 0 0 0 3px rgba(49, 95, 203, 0.16))));
}

.sgpc-period-picker {
  position: relative;
  min-width: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.sgpc-period-picker,
.sgpc-period-picker *,
.sgpc-period-picker__popover,
.sgpc-period-picker__popover * {
  box-sizing: border-box;
}

.sgpc-period-picker__field {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.sgpc-period-picker__field > span {
  color: var(--period-muted);
  font-size: 0.63rem;
  font-weight: 690;
}

.sgpc-period-picker__trigger {
  width: 100%;
  min-width: 0;
  min-height: 40px;
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr) auto;
  align-items: center;
  gap: 7px;
  padding: 0 9px;
  border: 1px solid var(--period-line);
  border-radius: var(--radius-sm, 8px);
  background: var(--period-input);
  color: var(--period-muted);
  box-shadow: none;
  font: inherit;
  font-size: 0.69rem;
  text-align: left;
  cursor: pointer;
}

.sgpc-period-picker__trigger:hover {
  border-color: var(--period-line-strong);
}

.sgpc-period-picker__trigger.has-value {
  color: var(--period-text);
}

.sgpc-period-picker__trigger:focus-visible {
  outline: none;
  border-color: var(--period-primary);
  box-shadow: var(--period-ring);
}

.sgpc-period-picker__trigger svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sgpc-period-picker__popover {
  position: fixed;
  z-index: var(--z-modal, 100);
  display: grid;
  gap: 8px;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 10px;
  border: 1px solid var(--period-line);
  border-radius: var(--radius-lg, 12px);
  background: var(--period-card);
  color: var(--period-text);
  box-shadow: var(--shadow-strong, 0 14px 38px rgba(15, 23, 42, 0.18));
}

.sgpc-period-picker__nav {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) 36px;
  align-items: center;
  gap: 6px;
}

.sgpc-period-picker__nav button,
.sgpc-period-picker__nav select,
.sgpc-period-picker__footer button {
  min-height: 36px;
  border: 1px solid var(--period-line);
  border-radius: var(--radius-sm, 8px);
  background: var(--period-input);
  color: var(--period-text);
  box-shadow: none;
  font: inherit;
  font-size: 0.68rem;
}

.sgpc-period-picker__nav button,
.sgpc-period-picker__footer button {
  cursor: pointer;
}

.sgpc-period-picker__nav button:hover:not(:disabled),
.sgpc-period-picker__footer button:hover:not(:disabled) {
  border-color: var(--period-line-strong);
  background: var(--period-soft);
}

.sgpc-period-picker__nav button:focus-visible,
.sgpc-period-picker__nav select:focus-visible,
.sgpc-period-picker__footer button:focus-visible,
.sgpc-period-picker__months button:focus-visible {
  outline: none;
  border-color: var(--period-primary);
  box-shadow: var(--period-ring);
}

.sgpc-period-picker__nav button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.sgpc-period-picker__months {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 5px;
}

.sgpc-period-picker__months button {
  min-width: 0;
  min-height: 42px;
  display: grid;
  place-content: center;
  padding: 5px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm, 8px);
  background: transparent;
  color: var(--period-text);
  font: inherit;
  font-size: 0.69rem;
  font-weight: 720;
  cursor: pointer;
}

.sgpc-period-picker__months button:hover:not(:disabled) {
  border-color: var(--period-line);
  background: var(--period-soft);
}

.sgpc-period-picker__months button.is-selected {
  border-color: color-mix(in srgb, var(--period-primary) 38%, var(--period-line));
  background: var(--period-primary-soft);
  color: var(--period-primary);
}

.sgpc-period-picker__months button:disabled {
  opacity: 0.34;
  cursor: not-allowed;
}

.sgpc-period-picker__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--period-line);
  color: var(--period-muted);
  font-size: 0.59rem;
}

.sgpc-period-picker__footer span {
  min-width: 0;
  line-height: 1.35;
}

.sgpc-period-picker__footer button {
  flex: 0 0 auto;
  min-height: 30px;
  padding: 0 7px;
  border-color: transparent;
  background: transparent;
  color: var(--period-primary);
  font-weight: 700;
  white-space: nowrap;
}

.sgpc-period-popover-enter-active,
.sgpc-period-popover-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}

.sgpc-period-popover-enter-from,
.sgpc-period-popover-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

.sgpc-period-picker__popover.is-up.sgpc-period-popover-enter-from,
.sgpc-period-picker__popover.is-up.sgpc-period-popover-leave-to {
  transform: translateY(3px);
}

@media (pointer: coarse) {
  .sgpc-period-picker button,
  .sgpc-period-picker select,
  .sgpc-period-picker__popover button,
  .sgpc-period-picker__popover select {
    min-height: 44px;
  }
}

@media (max-width: 640px) {
  .sgpc-period-picker {
    grid-template-columns: 1fr;
  }

  .sgpc-period-picker select,
  .sgpc-period-picker__popover select {
    font-size: 16px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sgpc-period-popover-enter-active,
  .sgpc-period-popover-leave-active {
    transition: none;
  }
}
</style>
