<template>
  <div class="ivbi-period-range">
    <div class="ivbi-field ivbi-field--period">
      <span>Desde</span>

      <button
        type="button"
        class="ivbi-period-trigger"
        :class="{ 'has-value': from }"
        aria-label="Seleccionar mes inicial"
        :aria-expanded="picker.open && picker.target === 'from'"
        @click.stop="togglePicker('from')"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 2v3M17 2v3M3.5 9h17M5.5 4.5h13a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2Z" />
        </svg>

        <span class="ivbi-period-trigger__value">
          {{ formatPeriod(from) || "Mes inicial" }}
        </span>

        <svg class="ivbi-period-trigger__chevron" viewBox="0 0 24 24" aria-hidden="true">
          <path d="m7 10 5 5 5-5" />
        </svg>
      </button>
    </div>

    <div class="ivbi-field ivbi-field--period">
      <span>Hasta</span>

      <button
        type="button"
        class="ivbi-period-trigger"
        :class="{ 'has-value': to }"
        aria-label="Seleccionar mes final"
        :aria-expanded="picker.open && picker.target === 'to'"
        @click.stop="togglePicker('to')"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 2v3M17 2v3M3.5 9h17M5.5 4.5h13a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2Z" />
        </svg>

        <span class="ivbi-period-trigger__value">
          {{ formatPeriod(to) || "Mes final" }}
        </span>

        <svg class="ivbi-period-trigger__chevron" viewBox="0 0 24 24" aria-hidden="true">
          <path d="m7 10 5 5 5-5" />
        </svg>
      </button>
    </div>

    <Transition name="ivbi-period-popover">
      <section
        v-if="picker.open"
        class="ivbi-period-popover"
        :class="{ 'is-to': picker.target === 'to' }"
        role="dialog"
        aria-label="Selector de período por mes y año"
        @click.stop
      >
        <div class="ivbi-period-popover__presets" aria-label="Períodos rápidos">
          <button type="button" @click="applyPreset('current-year')">
            Este año
          </button>
          <button
            type="button"
            :disabled="!canUsePreviousYear"
            @click="applyPreset('previous-year')"
          >
            Año anterior
          </button>
          <button type="button" @click="applyPreset('last-12')">
            12 meses
          </button>
          <button type="button" @click="applyPreset('historical')">
            Histórico
          </button>
        </div>

        <div class="ivbi-period-popover__nav">
          <button
            type="button"
            class="ivbi-period-nav-btn"
            aria-label="Año anterior"
            :disabled="!canMoveYear(-1)"
            @click="moveYear(-1)"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m15 18-6-6 6-6" />
            </svg>
          </button>

          <label class="ivbi-period-year-select">
            <span class="sr-only">Año</span>
            <select v-model.number="picker.year" aria-label="Año del período">
              <option
                v-for="year in yearOptions"
                :key="`period-year-${year.value}`"
                :value="Number(year.value)"
              >
                {{ year.label }}
              </option>
            </select>
          </label>

          <button
            type="button"
            class="ivbi-period-nav-btn"
            aria-label="Año siguiente"
            :disabled="!canMoveYear(1)"
            @click="moveYear(1)"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m9 18 6-6-6-6" />
            </svg>
          </button>
        </div>

        <div class="ivbi-period-months" role="grid" :aria-label="`Meses de ${picker.year}`">
          <button
            v-for="month in monthOptions"
            :key="`period-month-${picker.year}-${month.value}`"
            type="button"
            class="ivbi-period-month"
            :class="{
              'is-selected': isSelectedMonth(month.value),
              'has-data': monthCount(month.value) > 0,
            }"
            :disabled="!isMonthAllowed(month.value)"
            :aria-label="monthAriaLabel(month)"
            @click="selectMonth(month.value)"
          >
            <span>{{ month.short_label || month.label }}</span>
            <small v-if="monthCount(month.value) > 0">
              {{ monthCount(month.value) }}
            </small>
            <small v-else aria-hidden="true">—</small>
          </button>
        </div>

        <div class="ivbi-period-popover__summary">
          <div>
            <strong>{{ pickerYearTotal }}</strong>
            <span> publicaciones con mes en {{ picker.year }}</span>
          </div>

          <button
            type="button"
            class="ivbi-period-clear"
            @click="clearCurrentTarget"
          >
            Limpiar {{ picker.target === "from" ? "desde" : "hasta" }}
          </button>
        </div>

        <div class="ivbi-period-popover__foot">
          <span>{{ availableRangeLabel }}</span>
          <span v-if="lastDataLabel">Último dato: {{ lastDataLabel }}</span>
        </div>
      </section>
    </Transition>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  watch,
} from "vue";

const props = defineProps({
  from: {
    type: String,
    default: "",
  },
  to: {
    type: String,
    default: "",
  },
  period: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits([
  "update:from",
  "update:to",
]);

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

const picker = reactive({
  open: false,
  target: "from",
  year: null,
});

const yearOptions = computed(() => {
  const fromBackend = Array.isArray(props.period?.anios)
    ? props.period.anios
    : [];

  if (fromBackend.length) {
    return fromBackend;
  }

  const currentYear = new Date().getFullYear();

  return [
    {
      value: currentYear,
      label: String(currentYear),
    },
  ];
});

const monthOptions = computed(() => {
  const fromBackend = Array.isArray(props.period?.meses)
    ? props.period.meses
    : [];

  return fromBackend.length
    ? fromBackend
    : FALLBACK_MONTHS;
});

const minPeriod = computed(() => normalizePeriod(props.period?.mes_min));
const maxPeriod = computed(() => normalizePeriod(props.period?.mes_max));
const currentPeriod = computed(() => {
  return (
    normalizePeriod(props.period?.mes_actual) ||
    maxPeriod.value ||
    currentCalendarMonth()
  );
});

const lastDataLabel = computed(() => {
  return formatPeriod(props.period?.ultimo_mes_con_datos);
});

const availableRangeLabel = computed(() => {
  const minLabel = formatPeriod(minPeriod.value);
  const maxLabel = formatPeriod(maxPeriod.value);

  if (minLabel && maxLabel) {
    return `Rango consultable: ${minLabel} — ${maxLabel}`;
  }

  return "Rango temporal definido por el servidor";
});

const pickerYearTotal = computed(() => {
  return monthOptions.value.reduce(
    (total, month) => total + monthCount(month.value),
    0
  );
});

const canUsePreviousYear = computed(() => {
  const reference = parsePeriod(currentPeriod.value);

  if (!reference) {
    return false;
  }

  const previousStart = `${reference.year - 1}-01`;
  const previousEnd = `${reference.year - 1}-12`;

  return rangeOverlapsAvailable(previousStart, previousEnd);
});

watch(
  () => props.period,
  () => {
    ensurePickerYear();
  },
  { deep: true }
);

function normalizePeriod(value) {
  const text = String(value || "").trim();

  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(text)) {
    return "";
  }

  return text;
}

function parsePeriod(value) {
  const normalized = normalizePeriod(value);

  if (!normalized) {
    return null;
  }

  const [year, month] = normalized.split("-").map(Number);

  return { year, month };
}

function currentCalendarMonth() {
  const now = new Date();

  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

function formatPeriod(value) {
  const parsed = parsePeriod(value);

  if (!parsed) {
    return "";
  }

  const date = new Date(Date.UTC(parsed.year, parsed.month - 1, 1));

  const text = new Intl.DateTimeFormat("es-EC", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);

  return text.charAt(0).toUpperCase() + text.slice(1);
}

function monthOrdinal(value) {
  const parsed = parsePeriod(value);

  if (!parsed) {
    return null;
  }

  return parsed.year * 12 + (parsed.month - 1);
}

function ordinalToPeriod(ordinal) {
  const year = Math.floor(ordinal / 12);
  const month = (ordinal % 12) + 1;

  return `${year}-${String(month).padStart(2, "0")}`;
}

function clampPeriod(value) {
  const normalized = normalizePeriod(value);

  if (!normalized) {
    return "";
  }

  if (minPeriod.value && normalized < minPeriod.value) {
    return minPeriod.value;
  }

  if (maxPeriod.value && normalized > maxPeriod.value) {
    return maxPeriod.value;
  }

  return normalized;
}

function rangeOverlapsAvailable(start, end) {
  const normalizedStart = normalizePeriod(start);
  const normalizedEnd = normalizePeriod(end);

  if (!normalizedStart || !normalizedEnd) {
    return false;
  }

  if (maxPeriod.value && normalizedStart > maxPeriod.value) {
    return false;
  }

  if (minPeriod.value && normalizedEnd < minPeriod.value) {
    return false;
  }

  return true;
}

function emitRange(fromValue, toValue) {
  emit("update:from", fromValue);
  emit("update:to", toValue);
}

function ensurePickerYear() {
  const years = yearOptions.value.map((item) => Number(item.value));

  if (!years.length) {
    picker.year = new Date().getFullYear();
    return;
  }

  if (!years.includes(Number(picker.year))) {
    picker.year = years[0];
  }
}

function togglePicker(target) {
  if (picker.open && picker.target === target) {
    picker.open = false;
    return;
  }

  picker.target = target;

  const sourceValue = target === "from" ? props.from : props.to;
  const parsed = parsePeriod(sourceValue || currentPeriod.value || maxPeriod.value);

  picker.year = parsed?.year || Number(yearOptions.value[0]?.value);
  ensurePickerYear();
  picker.open = true;
}

function closePicker() {
  picker.open = false;
}

function canMoveYear(direction) {
  const years = yearOptions.value.map((item) => Number(item.value));
  const index = years.indexOf(Number(picker.year));

  if (index < 0) {
    return false;
  }

  const nextIndex = direction < 0 ? index + 1 : index - 1;

  return nextIndex >= 0 && nextIndex < years.length;
}

function moveYear(direction) {
  if (!canMoveYear(direction)) {
    return;
  }

  const years = yearOptions.value.map((item) => Number(item.value));
  const index = years.indexOf(Number(picker.year));
  const nextIndex = direction < 0 ? index + 1 : index - 1;

  picker.year = years[nextIndex];
}

function periodForMonth(month) {
  return `${Number(picker.year)}-${String(Number(month)).padStart(2, "0")}`;
}

function isMonthAllowed(month) {
  const value = periodForMonth(month);

  if (minPeriod.value && value < minPeriod.value) {
    return false;
  }

  if (maxPeriod.value && value > maxPeriod.value) {
    return false;
  }

  return true;
}

function monthCount(month) {
  const yearBucket = props.period?.meses_con_datos?.[String(picker.year)] || {};

  return Number(yearBucket?.[String(Number(month))] || 0);
}

function isSelectedMonth(month) {
  const selected = picker.target === "from" ? props.from : props.to;

  return normalizePeriod(selected) === periodForMonth(month);
}

function monthAriaLabel(month) {
  const count = monthCount(month.value);
  const suffix = count === 1 ? "publicación" : "publicaciones";

  return `${month.label} ${picker.year}, ${count} ${suffix}`;
}

function selectMonth(month) {
  if (!isMonthAllowed(month)) {
    return;
  }

  const selected = periodForMonth(month);
  let nextFrom = normalizePeriod(props.from);
  let nextTo = normalizePeriod(props.to);

  if (picker.target === "from") {
    nextFrom = selected;

    if (nextTo && nextFrom > nextTo) {
      nextTo = nextFrom;
    }
  } else {
    nextTo = selected;

    if (nextFrom && nextTo < nextFrom) {
      nextFrom = nextTo;
    }
  }

  emitRange(nextFrom, nextTo);
  closePicker();
}

function clearCurrentTarget() {
  if (picker.target === "from") {
    emit("update:from", "");
  } else {
    emit("update:to", "");
  }

  closePicker();
}

function applyPreset(preset) {
  if (preset === "historical") {
    emitRange("", "");
    closePicker();
    return;
  }

  const reference = parsePeriod(currentPeriod.value);

  if (!reference) {
    return;
  }

  let start = "";
  let end = "";

  if (preset === "current-year") {
    start = `${reference.year}-01`;
    end = currentPeriod.value;
  }

  if (preset === "previous-year") {
    start = `${reference.year - 1}-01`;
    end = `${reference.year - 1}-12`;
  }

  if (preset === "last-12") {
    const referenceOrdinal = monthOrdinal(currentPeriod.value);

    if (referenceOrdinal === null) {
      return;
    }

    start = ordinalToPeriod(referenceOrdinal - 11);
    end = currentPeriod.value;
  }

  if (!rangeOverlapsAvailable(start, end)) {
    return;
  }

  start = clampPeriod(start);
  end = clampPeriod(end);

  emitRange(start, end);
  closePicker();
}

function handleDocumentClick(event) {
  if (!picker.open) {
    return;
  }

  if (event.target?.closest?.(".ivbi-period-range")) {
    return;
  }

  closePicker();
}

function handleDocumentKeydown(event) {
  if (event.key === "Escape") {
    closePicker();
  }
}

onMounted(() => {
  ensurePickerYear();
  document.addEventListener("click", handleDocumentClick);
  document.addEventListener("keydown", handleDocumentKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleDocumentClick);
  document.removeEventListener("keydown", handleDocumentKeydown);
});
</script>

<style scoped>
.ivbi-period-range {
  position: relative;
  min-width: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.4375rem;
  grid-column: span 2;
}

.ivbi-field--period {
  min-width: 0;
  display: grid;
  gap: 0.25rem;
}

.ivbi-field--period > span {
  color: var(--ivbi-text-soft);
  font-family: var(--font-label);
  font-size: 0.58rem;
  line-height: 1;
  font-weight: 600;
}

.ivbi-period-trigger {
  width: 100%;
  height: var(--ivbi-control-sm);
  min-height: var(--ivbi-control-sm);
  min-width: 0;
  display: grid;
  grid-template-columns: 0.9rem minmax(0, 1fr) 0.8rem;
  align-items: center;
  gap: 0.4rem;
  padding: 0 0.55rem;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--input-radius);
  outline: none;
  background: var(--ivbi-input);
  color: var(--ivbi-text-muted);
  font-family: var(--font-control);
  font-size: 0.67rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: border-color var(--ivbi-transition-med), box-shadow var(--ivbi-transition-med), color var(--ivbi-transition-med);
}

.ivbi-period-trigger:hover {
  border-color: var(--ivbi-line-strong);
}

.ivbi-period-trigger:focus-visible,
.ivbi-period-trigger[aria-expanded="true"] {
  border-color: var(--ivbi-accent);
  box-shadow: var(--ring-primary);
}

.ivbi-period-trigger.has-value {
  color: var(--ivbi-text);
}

.ivbi-period-trigger svg {
  width: 0.88rem;
  height: 0.88rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.ivbi-period-trigger__value {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ivbi-period-trigger__chevron {
  justify-self: end;
}

.ivbi-period-popover {
  position: absolute;
  z-index: 80;
  top: calc(100% + 0.5rem);
  left: 0;
  width: min(21rem, calc(100vw - 2rem));
  padding: 0.75rem;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--radius-md);
  background: var(--ivbi-surface);
  box-shadow: var(--shadow-strong);
}

.ivbi-period-popover.is-to {
  left: auto;
  right: 0;
}

.ivbi-period-popover__presets {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.3rem;
  margin-bottom: 0.65rem;
}

.ivbi-period-popover__presets button,
.ivbi-period-clear {
  min-height: 1.9rem;
  padding: 0.3rem 0.4rem;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--ivbi-text-soft);
  font: inherit;
  font-size: 0.59rem;
  font-weight: 650;
  cursor: pointer;
}

.ivbi-period-popover__presets button:hover:not(:disabled),
.ivbi-period-clear:hover:not(:disabled) {
  border-color: var(--ivbi-accent);
  color: var(--ivbi-accent);
}

.ivbi-period-popover__presets button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.ivbi-period-popover__nav {
  display: grid;
  grid-template-columns: 2rem minmax(0, 1fr) 2rem;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.55rem;
}

.ivbi-period-nav-btn {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--radius-sm);
  background: var(--ivbi-input);
  color: var(--ivbi-text);
  cursor: pointer;
}

.ivbi-period-nav-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.ivbi-period-nav-btn svg {
  width: 0.9rem;
  height: 0.9rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.ivbi-period-year-select select {
  width: 100%;
  height: 2rem;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--radius-sm);
  background: var(--ivbi-input);
  color: var(--ivbi-text);
  font: inherit;
  font-size: 0.72rem;
  font-weight: 700;
  text-align: center;
}

.ivbi-period-months {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.35rem;
}

.ivbi-period-month {
  min-height: 2.65rem;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 0.08rem;
  padding: 0.3rem;
  border: 1px solid var(--ivbi-line);
  border-radius: var(--radius-sm);
  background: var(--ivbi-input);
  color: var(--ivbi-text-soft);
  font: inherit;
  cursor: pointer;
}

.ivbi-period-month span {
  font-size: 0.64rem;
  font-weight: 700;
}

.ivbi-period-month small {
  min-height: 0.65rem;
  color: var(--ivbi-text-muted);
  font-size: 0.52rem;
  line-height: 1;
}

.ivbi-period-month.has-data {
  color: var(--ivbi-text);
}

.ivbi-period-month:hover:not(:disabled) {
  border-color: var(--ivbi-accent);
}

.ivbi-period-month.is-selected {
  border-color: var(--ivbi-accent);
  background: var(--primary-soft);
  color: var(--ivbi-accent);
}

.ivbi-period-month:disabled {
  cursor: not-allowed;
  opacity: 0.35;
}

.ivbi-period-popover__summary {
  margin-top: 0.65rem;
  padding-top: 0.6rem;
  border-top: 1px solid var(--ivbi-line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--ivbi-text-muted);
  font-size: 0.58rem;
}

.ivbi-period-popover__summary strong {
  color: var(--ivbi-text);
}

.ivbi-period-clear {
  flex: 0 0 auto;
}

.ivbi-period-popover__foot {
  margin-top: 0.5rem;
  display: grid;
  gap: 0.12rem;
  color: var(--ivbi-text-muted);
  font-size: 0.54rem;
  line-height: 1.3;
}

.ivbi-period-popover-enter-active,
.ivbi-period-popover-leave-active {
  transition: opacity 0.14s ease, transform 0.14s ease;
}

.ivbi-period-popover-enter-from,
.ivbi-period-popover-leave-to {
  opacity: 0;
  transform: translateY(-0.2rem);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 640px) {
  .ivbi-period-range {
    grid-template-columns: 1fr;
    grid-column: 1 / -1;
  }

  .ivbi-period-popover,
  .ivbi-period-popover.is-to {
    left: 0;
    right: auto;
    width: 100%;
  }

  .ivbi-period-popover__presets {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
