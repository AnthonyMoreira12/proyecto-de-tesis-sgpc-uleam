<template>
  <main class="my-report">
    <header class="my-report__header">
      <div>
        <h1>Mi producción científica</h1>
        <p>
          Consulte sus publicaciones aprobadas, analice su evolución y descargue los resultados cuando los necesite.
        </p>
      </div>

      <div class="my-report__exports" aria-label="Descargar resultados">
        <button
          class="my-report__export my-report__export--excel"
          type="button"
          :disabled="loading || Boolean(downloadingFormat)"
          @click="downloadReport('excel')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M5 3h10l4 4v14H5V3Zm9 1.5V8h3.5L14 4.5ZM8 11l2 3-2 3h2.2l1-1.8 1 1.8h2.2l-2-3 2-3h-2.2l-1 1.8-1-1.8H8Z"
            />
          </svg>
          {{ downloadingFormat === "excel" ? "Preparando…" : "Descargar Excel" }}
        </button>

        <button
          class="my-report__export my-report__export--pdf"
          type="button"
          :disabled="loading || Boolean(downloadingFormat)"
          @click="downloadReport('pdf')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M6 2h9l5 5v15H6V2Zm8 1.5V8h4.5L14 3.5ZM8.5 12v6h1.6v-2h.9c1.7 0 2.8-.8 2.8-2s-1.1-2-2.8-2H8.5Zm1.6 1.3h.8c.8 0 1.2.2 1.2.7s-.4.7-1.2.7h-.8v-1.4Zm4.6-1.3v6h2.2c2 0 3.3-1.1 3.3-3s-1.3-3-3.3-3h-2.2Zm1.6 1.4h.5c1.1 0 1.7.5 1.7 1.6s-.6 1.6-1.7 1.6h-.5v-3.2Z"
            />
          </svg>
          {{ downloadingFormat === "pdf" ? "Preparando…" : "Descargar PDF" }}
        </button>
      </div>
    </header>

    <section
      class="my-report__filters"
      aria-labelledby="my-report-filters-title"
    >
      <header>
        <div>
          <h2 id="my-report-filters-title">Filtros</h2>
          <p>Seleccione solo los criterios que necesite.</p>
        </div>

        <div class="my-report__filter-actions">
          <span v-if="loading" class="my-report__filter-loading" role="status">
            <span aria-hidden="true"></span>
            Actualizando…
          </span>

          <button
            v-if="hasFilters"
            type="button"
            class="my-report__clear"
            :disabled="loading"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </header>

      <div class="my-report__filter-grid">
        <div class="my-report__filter-row my-report__filter-row--period">
          <label class="my-report__field my-report__field--period-mode">
            <span>Período</span>
            <select v-model="filters.periodo_modo" @change="handleModeChange">
              <option
                v-for="mode in periodModes"
                :key="mode.value"
                :value="mode.value"
              >
                {{ periodModeLabel(mode) }}
              </option>
            </select>
          </label>

          <label
            v-if="['trimestral', 'semestral', 'anual'].includes(filters.periodo_modo)"
            class="my-report__field my-report__field--year"
          >
            <span>Año</span>
            <select v-model="filters.anio">
              <option
                v-for="year in yearOptions"
                :key="year.value"
                :value="String(year.value)"
              >
                {{ year.label }}
              </option>
            </select>
          </label>

          <label
            v-if="filters.periodo_modo === 'trimestral'"
            class="my-report__field my-report__field--period-part"
          >
            <span>Trimestre</span>
            <select v-model="filters.trimestre">
              <option value="1">1.º · Enero — Marzo</option>
              <option value="2">2.º · Abril — Junio</option>
              <option value="3">3.º · Julio — Septiembre</option>
              <option value="4">4.º · Octubre — Diciembre</option>
            </select>
          </label>

          <label
            v-if="filters.periodo_modo === 'semestral'"
            class="my-report__field my-report__field--period-part"
          >
            <span>Semestre</span>
            <select v-model="filters.semestre">
              <option value="1">1.º · Enero — Junio</option>
              <option value="2">2.º · Julio — Diciembre</option>
            </select>
          </label>

          <div
            v-if="filters.periodo_modo === 'personalizado'"
            class="my-report__custom-period"
          >
            <ReportPeriodPicker
              :from="filters.mes_desde"
              :to="filters.mes_hasta"
              :period="periodCatalog"
              @update:from="filters.mes_desde = $event"
              @update:to="filters.mes_hasta = $event"
            />
          </div>
        </div>

        <div class="my-report__filter-row my-report__filter-row--scope">
          <label class="my-report__field my-report__field--type">
            <span>Tipo</span>
            <select v-model="filters.tipo">
              <option value="">Todos los tipos</option>
              <option
                v-for="item in catalogs.tipos"
                :key="`my-type-${item.id}`"
                :value="String(item.id)"
              >
                {{ optionLabel(item) }}
              </option>
            </select>
          </label>

          <label class="my-report__field my-report__field--project">
            <span>Proyecto</span>
            <select v-model="filters.proyecto">
              <option value="">Todos los proyectos</option>
              <option
                v-for="item in catalogs.proyectos"
                :key="`my-project-${item.id}`"
                :value="String(item.id)"
              >
                {{ optionLabel(item) }}
              </option>
            </select>
          </label>
        </div>
      </div>
    </section>

    <div v-if="errorMessage" class="my-report__message is-error" role="alert">
      <strong>No se pudo completar la solicitud.</strong>
      <span>{{ errorMessage }}</span>
    </div>

    <div v-if="successMessage" class="my-report__message is-success" role="status">
      {{ successMessage }}
    </div>

    <div v-if="loading && !report" class="my-report__loading" role="status">
      <span aria-hidden="true"></span>
      Cargando publicaciones…
    </div>

    <template v-if="report">
      <section class="my-report__stats" aria-label="Indicadores del reporte">
        <article>
          <span>Publicaciones</span>
          <strong>{{ numberLabel(summary.total_publicaciones) }}</strong>
          <small>Aprobadas con los filtros seleccionados</small>
        </article>
        <article>
          <span>Con documento PDF</span>
          <strong>{{ numberLabel(summary.con_pdf) }}</strong>
          <small>
            {{ percentLabel(summary.cobertura_pdf) }} del total
          </small>
        </article>
        <article>
          <span>Con proyecto</span>
          <strong>{{ numberLabel(summary.con_proyecto) }}</strong>
          <small>
            {{ percentLabel(summary.vinculacion_proyectos) }} del total
          </small>
        </article>
        <article>
          <span>Tipos de publicación</span>
          <strong>{{ numberLabel(summary.total_tipos) }}</strong>
          <small>Tipos presentes en los resultados</small>
        </article>
      </section>

      <section class="my-report__analysis" aria-label="Análisis gráfico de la producción">
        <article class="my-report__chart-card my-report__chart-card--wide">
          <header>
            <div>
              <h2>Evolución por año</h2>
              <p>Cantidad de publicaciones aprobadas registradas cada año.</p>
            </div>
          </header>

          <div v-if="yearChartDots.length >= 1" class="my-report__line-chart">
            <svg
              viewBox="0 0 1000 280"
              role="img"
              aria-label="Evolución de publicaciones aprobadas por año"
            >
              <line
                v-for="grid in chartGridLines"
                :key="`year-grid-${grid}`"
                x1="48"
                x2="970"
                :y1="grid"
                :y2="grid"
                class="my-report__chart-gridline"
              />

              <polyline
                :points="yearChartPoints"
                class="my-report__chart-line"
                fill="none"
              />

              <g
                v-for="point in yearChartDots"
                :key="`year-${point.label}`"
                class="my-report__chart-point"
              >
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="7"
                  class="my-report__chart-dot"
                >
                  <title>{{ point.label }}: {{ numberLabel(point.value) }} publicaciones</title>
                </circle>
                <text
                  :x="point.x"
                  :y="point.y - 15"
                  text-anchor="middle"
                  class="my-report__chart-value"
                >
                  {{ numberLabel(point.value) }}
                </text>
                <text
                  :x="point.x"
                  y="266"
                  text-anchor="middle"
                  class="my-report__chart-label"
                >
                  {{ point.shortLabel }}
                </text>
              </g>
            </svg>
          </div>
          <p v-else class="my-report__empty">No hay información por año.</p>
        </article>

        <article class="my-report__chart-card">
          <header>
            <div>
              <h2>Tipos de publicación</h2>
              <p>Cantidad y proporción de publicaciones por tipo.</p>
            </div>
          </header>

          <div v-if="showTypeDonut" class="my-report__donut-layout">
            <div class="my-report__donut" :style="typeDonutStyle" aria-hidden="true">
              <div>
                <strong>{{ numberLabel(summary.total_publicaciones) }}</strong>
                <span>publicaciones</span>
              </div>
            </div>

            <div class="my-report__legend">
              <div v-for="item in typeChartRows" :key="item.key">
                <span class="my-report__legend-dot" :style="{ background: item.color }"></span>
                <strong>{{ item.label }}</strong>
                <span>{{ numberLabel(item.total) }} · {{ percentLabel(item.percent) }}</span>
              </div>
            </div>
          </div>
          <p v-else class="my-report__empty">No hay información por tipo.</p>
        </article>

        <article class="my-report__chart-card">
          <header>
            <div>
              <h2>Proyectos</h2>
              <p>Proyectos con más publicaciones vinculadas.</p>
            </div>
          </header>

          <div v-if="showProjectBars" class="my-report__ranking-chart">
            <div v-for="(row, index) in projectChartRows" :key="row.proyecto_id || row.proyecto">
              <div class="my-report__ranking-chart-head">
                <span>{{ index + 1 }}</span>
                <strong :title="row.proyecto || 'Sin proyecto'">{{ row.proyecto || "Sin proyecto" }}</strong>
                <b>{{ numberLabel(row.total) }}</b>
              </div>
              <div class="my-report__ranking-track" aria-hidden="true">
                <span :style="{ width: barWidth(row.total, projectChartRows) }"></span>
              </div>
            </div>
          </div>
          <p v-else class="my-report__empty">No hay publicaciones vinculadas a proyectos.</p>
        </article>

        <article class="my-report__chart-card my-report__chart-card--wide">
          <header>
            <div>
              <h2>Evolución mensual<span v-if="monthChartContextLabel"> · {{ monthChartContextLabel }}</span></h2>
              <p>Cantidad de publicaciones por mes dentro de la selección.</p>
            </div>
          </header>

          <div v-if="monthChartDots.length >= 1" class="my-report__line-chart my-report__line-chart--area">
            <svg
              viewBox="0 0 1000 280"
              role="img"
              aria-label="Evolución mensual de publicaciones aprobadas"
            >
              <defs>
                <linearGradient id="my-report-area-gradient" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stop-color="currentColor" stop-opacity="0.22" />
                  <stop offset="100%" stop-color="currentColor" stop-opacity="0.03" />
                </linearGradient>
              </defs>

              <line
                v-for="grid in chartGridLines"
                :key="`month-grid-${grid}`"
                x1="48"
                x2="970"
                :y1="grid"
                :y2="grid"
                class="my-report__chart-gridline"
              />

              <polygon
                :points="monthAreaPoints"
                class="my-report__chart-area"
              />

              <polyline
                :points="monthChartPoints"
                class="my-report__chart-line"
                fill="none"
              />

              <g
                v-for="point in monthChartDots"
                :key="`month-${point.label}`"
                class="my-report__chart-point"
              >
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="6"
                  class="my-report__chart-dot"
                >
                  <title>{{ point.label }}: {{ numberLabel(point.value) }} publicaciones</title>
                </circle>
                <text
                  v-if="point.value"
                  :x="point.x"
                  :y="point.y - 14"
                  text-anchor="middle"
                  class="my-report__chart-value"
                >
                  {{ numberLabel(point.value) }}
                </text>
                <text
                  :x="point.x"
                  y="266"
                  text-anchor="middle"
                  class="my-report__chart-label"
                >
                  {{ point.shortLabel }}
                </text>
              </g>
            </svg>
          </div>
          <p v-else class="my-report__empty">{{ monthChartEmptyMessage }}</p>
        </article>
      </section>

      <section class="my-report__detail">
        <header>
          <div>
            <h2>Publicaciones incluidas</h2>
            <p v-if="report.detalle?.truncado">
              Mostrando {{ numberLabel(detailRows.length) }} de
              {{ numberLabel(report.detalle?.total) }} publicaciones. Los archivos
              descargados incluyen todas las publicaciones.
            </p>
            <p v-else>
              {{ numberLabel(report.detalle?.total) }} publicaciones aprobadas.
            </p>
          </div>
        </header>

        <div v-if="detailRows.length" class="my-report__table-wrap">
          <table>
            <thead>
              <tr>
                <th>Título</th>
                <th>Tipo</th>
                <th>Período</th>
                <th>Proyecto</th>
                <th>Autores</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in detailRows" :key="row.publicacion_id">
                <td data-label="Título"><strong>{{ row.titulo }}</strong></td>
                <td data-label="Tipo">{{ row.tipo || "—" }}</td>
                <td data-label="Período">{{ row.periodo || "—" }}</td>
                <td data-label="Proyecto">{{ row.proyecto || "Sin proyecto" }}</td>
                <td data-label="Autores">
                  <span :title="String(row.autores || '')">
                    {{ authorsPreview(row.autores) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="my-report__empty">No hay publicaciones que coincidan con estos filtros.</p>
      </section>
    </template>
  </main>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import ReportPeriodPicker from "../componentes/ReportPeriodPicker.vue";

import {
  descargarMiReporteProduccionExcel,
  descargarMiReporteProduccionPdf,
  guardarBlobEnNavegador,
  obtenerMiReporteProduccion,
} from "../../scripts/api/gestionApi";

const report = ref(null);
const loading = ref(false);
const downloadingFormat = ref("");
const errorMessage = ref("");
const successMessage = ref("");
const appliedParamsKey = ref("");

let reportController = null;
let downloadController = null;
let autoRefreshTimer = null;

const filters = reactive({
  tipo: "",
  proyecto: "",
  periodo_modo: "historico",
  mes_desde: "",
  mes_hasta: "",
  anio: "",
  trimestre: "1",
  semestre: "1",
});

const catalogs = computed(() => report.value?.filtros_disponibles || {
  tipos: [],
  proyectos: [],
  periodo: {},
});

const periodCatalog = computed(() => catalogs.value.periodo || {});

const periodModes = computed(() => {
  const modes = Array.isArray(periodCatalog.value?.modos)
    ? periodCatalog.value.modos
    : [];

  return modes.length ? modes : [
    { value: "historico", label: "Histórico" },
    { value: "personalizado", label: "Personalizado" },
    { value: "trimestral", label: "Trimestral" },
    { value: "semestral", label: "Semestral" },
    { value: "anual", label: "Anual" },
    { value: "ultimos_12_meses", label: "Últimos 12 meses" },
  ];
});

const PERIOD_MODE_LABELS = Object.freeze({
  historico: "Todo el historial",
  personalizado: "Elegir fechas",
  trimestral: "Por trimestre",
  semestral: "Por semestre",
  anual: "Por año",
  ultimos_12_meses: "Últimos 12 meses",
});

function periodModeLabel(mode) {
  const value =
    String(mode?.value || "")
      .trim()
      .toLowerCase();

  return (
    PERIOD_MODE_LABELS[value] ||
    String(mode?.label || "Período")
  );
}


const yearOptions = computed(() => {
  const years = Array.isArray(periodCatalog.value?.anios)
    ? periodCatalog.value.anios
    : [];

  if (years.length) return years;
  const current = new Date().getFullYear();
  return [{ value: current, label: String(current) }];
});

const summary = computed(() => report.value?.resumen || {});
const yearRows = computed(() => report.value?.distribuciones?.por_anio || []);
const monthRows = computed(() => report.value?.distribuciones?.por_mes || []);
const typeRows = computed(() => report.value?.distribuciones?.por_tipo || []);
const projectRows = computed(() => report.value?.distribuciones?.por_proyecto || []);
const detailRows = computed(() => report.value?.detalle?.items || []);
const appliedFilters = computed(() => report.value?.filtros_aplicados || {});

function monthOrdinal(year, month) {
  return Number(year) * 12 + (Number(month) - 1);
}

function monthFromOrdinal(ordinal) {
  const year = Math.floor(ordinal / 12);
  const month = (ordinal % 12) + 1;
  return { year, month };
}

function parseMonthKey(value) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})$/);
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (!year || month < 1 || month > 12) return null;
  return { year, month };
}

function denseMonthRows(rows, startKey, endKey) {
  const values = Array.isArray(rows) ? rows : [];
  const counts = new Map();

  values.forEach((row) => {
    const year = Number(row?.anio || 0);
    const month = Number(row?.mes || 0);
    if (!year || month < 1 || month > 12) return;
    counts.set(`${year}-${String(month).padStart(2, "0")}`, Number(row?.total || 0));
  });

  let start = parseMonthKey(startKey);
  let end = parseMonthKey(endKey);

  if (!start || !end) {
    const periods = values
      .map((row) => parseMonthKey(row?.periodo))
      .filter(Boolean)
      .map((item) => monthOrdinal(item.year, item.month));
    if (!periods.length) return [];
    const min = Math.min(...periods);
    const max = Math.max(...periods);
    start = monthFromOrdinal(min);
    end = monthFromOrdinal(max);
  }

  let from = monthOrdinal(start.year, start.month);
  let to = monthOrdinal(end.year, end.month);
  if (from > to) [from, to] = [to, from];

  const output = [];
  for (let ordinal = from; ordinal <= to; ordinal += 1) {
    const { year, month } = monthFromOrdinal(ordinal);
    const periodo = `${year}-${String(month).padStart(2, "0")}`;
    output.push({
      anio: year,
      mes: month,
      periodo,
      mes_label: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][month - 1],
      total: counts.get(periodo) || 0,
    });
  }
  return output;
}

const monthChartRows = computed(() => {
  const rows = monthRows.value;
  if (!rows.length) return [];

  const filtersApplied = appliedFilters.value;
  const mode = String(filtersApplied?.periodo_modo || "historico").toLowerCase();

  if (mode === "historico") {
    const years = [...new Set(
      rows.map((row) => Number(row?.anio || 0)).filter(Boolean)
    )].sort((a, b) => a - b);

    if (!years.length) return [];

    const latestYear = years[years.length - 1];
    return denseMonthRows(
      rows,
      `${latestYear}-01`,
      `${latestYear}-12`
    );
  }

  let from = filtersApplied?.mes_desde || "";
  let to = filtersApplied?.mes_hasta || "";

  if (mode === "anual" && filtersApplied?.anio) {
    const year = Number(filtersApplied.anio);
    from = `${year}-01`;
    to = `${year}-12`;
  }

  const dense = denseMonthRows(rows, from, to);
  return dense.length <= 18 ? dense : dense.slice(-12);
});

const monthChartEmptyMessage = computed(() =>
  "No hay información mensual para esta selección."
);

const monthChartContextLabel = computed(() => {
  const rows = monthChartRows.value;
  if (!rows.length) return "";

  const years = [...new Set(rows.map((row) => Number(row?.anio || 0)).filter(Boolean))];
  if (years.length === 1) return String(years[0]);

  const first = rows[0]?.periodo || "";
  const last = rows[rows.length - 1]?.periodo || "";
  return first && last ? `${first} — ${last}` : "";
});

const CHART_COLORS = Object.freeze([
  "#2f66e8",
  "#2f855a",
  "#7554b8",
  "#b85f2e",
  "#237b72",
  "#8a5d1e",
  "#5c6f82",
]);

const chartGridLines = Object.freeze([48, 98, 148, 198, 248]);

function buildLineDots(rows, labelKey, shortLabelKey = labelKey) {
  const values = Array.isArray(rows) ? rows : [];
  if (!values.length) return [];

  const max = Math.max(1, ...values.map((row) => Number(row?.total || 0)));
  const left = 58;
  const right = 958;
  const top = 40;
  const bottom = 238;
  const width = right - left;
  const height = bottom - top;

  return values.map((row, index) => {
    const denominator = Math.max(1, values.length - 1);
    const value = Math.max(0, Number(row?.total || 0));
    const x = values.length === 1
      ? left + width / 2
      : left + (width * index) / denominator;
    const y = bottom - (value / max) * height;

    return {
      x: Number(x.toFixed(2)),
      y: Number(y.toFixed(2)),
      value,
      label: String(row?.[labelKey] || ""),
      shortLabel: String(row?.[shortLabelKey] || row?.[labelKey] || ""),
    };
  });
}

const yearChartDots = computed(() =>
  buildLineDots(yearRows.value, "anio", "anio")
);

const yearChartPoints = computed(() =>
  yearChartDots.value.map((point) => `${point.x},${point.y}`).join(" ")
);

const monthChartDots = computed(() =>
  buildLineDots(
    monthChartRows.value,
    "periodo",
    "mes_label"
  ).map((point) => ({
    ...point,
    shortLabel: point.shortLabel.slice(0, 3),
  }))
);

const monthChartPoints = computed(() =>
  monthChartDots.value.map((point) => `${point.x},${point.y}`).join(" ")
);

const monthAreaPoints = computed(() => {
  const points = monthChartDots.value;
  if (!points.length) return "";
  return [
    `${points[0].x},238`,
    ...points.map((point) => `${point.x},${point.y}`),
    `${points[points.length - 1].x},238`,
  ].join(" ");
});

const typeChartRows = computed(() => {
  const rows = typeRows.value;
  const total = rows.reduce((sum, row) => sum + Number(row?.total || 0), 0);

  return rows.map((row, index) => ({
    key: row?.tipo_id || row?.tipo || index,
    label: row?.tipo || "Sin tipo",
    total: Number(row?.total || 0),
    percent: total ? (Number(row?.total || 0) / total) * 100 : 0,
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));
});

const showTypeDonut = computed(() => typeChartRows.value.length >= 1);

const typeDonutStyle = computed(() => {
  const rows = typeChartRows.value;
  if (!rows.length) return { background: "var(--my-soft-2)" };

  let start = 0;
  const stops = rows.map((row) => {
    const end = start + row.percent;
    const segment = `${row.color} ${start}% ${end}%`;
    start = end;
    return segment;
  });

  return { background: `conic-gradient(${stops.join(", ")})` };
});

const projectChartRows = computed(() =>
  [...projectRows.value]
    .sort((a, b) => Number(b?.total || 0) - Number(a?.total || 0))
    .slice(0, 8)
);
const showProjectBars = computed(() => projectChartRows.value.length >= 1);

const hasFilters = computed(() => Boolean(
  filters.tipo ||
  filters.proyecto ||
  filters.periodo_modo !== "historico" ||
  filters.mes_desde ||
  filters.mes_hasta
));

function numberLabel(value) {
  const number = Number(value || 0);
  return Number.isFinite(number) ? number.toLocaleString("es-EC") : "0";
}

function percentLabel(value) {
  const number = Number(value || 0);
  return Number.isFinite(number)
    ? `${number.toLocaleString("es-EC", { maximumFractionDigits: 1 })}%`
    : "0%";
}

function optionLabel(item) {
  return String(item?.label || "Sin nombre").trim();
}

function barWidth(value, rows) {
  const max = Math.max(1, ...rows.map((row) => Number(row?.total || 0)));
  const current = Math.max(0, Number(value || 0));
  return current ? `${Math.max(3, (current / max) * 100)}%` : "0%";
}

function authorsPreview(value) {
  const parts = Array.isArray(value)
    ? value
        .map((item) =>
          String(
            item?.nombre_completo ||
              item?.autor_nombre ||
              item?.nombre ||
              item ||
              ""
          ).trim()
        )
        .filter(Boolean)
    : String(value || "")
        .split(/\s*\|\s*/)
        .map((item) => item.trim())
        .filter(Boolean);

  if (!parts.length) return "—";
  if (parts.length <= 2) return parts.join(" · ");

  const remaining = parts.length - 2;
  return `${parts.slice(0, 2).join(" · ")} · +${remaining} ${
    remaining === 1 ? "autor" : "autores"
  }`;
}

function syncYear() {
  if (!yearOptions.value.some((item) => String(item.value) === String(filters.anio))) {
    filters.anio = String(yearOptions.value[0]?.value || new Date().getFullYear());
  }
}

function currentQuarter() {
  const month = new Date().getMonth() + 1;
  return String(Math.floor((month - 1) / 3) + 1);
}

function currentSemester() {
  return new Date().getMonth() + 1 <= 6 ? "1" : "2";
}

function handleModeChange() {
  successMessage.value = "";
  if (filters.periodo_modo !== "personalizado") {
    filters.mes_desde = "";
    filters.mes_hasta = "";
  }
  if (filters.periodo_modo === "trimestral") {
    filters.trimestre = currentQuarter();
  }
  if (filters.periodo_modo === "semestral") {
    filters.semestre = currentSemester();
  }
  syncYear();
}

function buildParams() {
  const params = {
    tipo: filters.tipo || undefined,
    proyecto: filters.proyecto || undefined,
    periodo_modo: filters.periodo_modo,
    detalle_limite: 100,
  };

  if (filters.periodo_modo === "personalizado") {
    params.mes_desde = filters.mes_desde || undefined;
    params.mes_hasta = filters.mes_hasta || undefined;
  }

  if (["trimestral", "semestral", "anual"].includes(filters.periodo_modo)) {
    params.anio = filters.anio || undefined;
  }

  if (filters.periodo_modo === "trimestral") params.trimestre = filters.trimestre;
  if (filters.periodo_modo === "semestral") params.semestre = filters.semestre;

  return params;
}

function paramsKey(params = buildParams()) {
  return JSON.stringify(params);
}

function normalizeError(error) {
  const status = Number(error?.response?.status || 0);
  const payload = error?.response?.data;

  if (status === 401) return "Su sesión ha vencido. Inicie sesión nuevamente.";

  if (payload && typeof payload === "object") {
    const direct = [payload.detail, payload.message, payload.error]
      .find((value) => typeof value === "string" && value.trim());
    if (direct) return direct;

    const fieldError = Object.values(payload).flat()
      .find((value) => typeof value === "string" && value.trim());
    if (fieldError) return fieldError;
  }

  return "Intente nuevamente en unos momentos.";
}

function scheduleReportRefresh(delay = 320) {
  window.clearTimeout(autoRefreshTimer);
  autoRefreshTimer = window.setTimeout(() => {
    loadReport();
  }, delay);
}

async function loadReport() {
  reportController?.abort?.();
  const controller = new AbortController();
  reportController = controller;

  const params = buildParams();
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const payload = await obtenerMiReporteProduccion(
      params,
      { signal: controller.signal }
    );

    if (reportController !== controller) return false;
    report.value = payload || null;
    syncYear();
    appliedParamsKey.value = paramsKey(params);
    return true;
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") return false;
    console.error("Error cargando reporte personal:", error);
    errorMessage.value = normalizeError(error);
    return false;
  } finally {
    if (reportController === controller) loading.value = false;
  }
}

async function downloadReport(format) {
  if (!["excel", "pdf"].includes(format)) return;

  downloadingFormat.value = format;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    if (paramsKey() !== appliedParamsKey.value) {
      const refreshed = await loadReport();
      if (!refreshed) return;
    }

    downloadController?.abort?.();
    const controller = new AbortController();
    downloadController = controller;
    const params = buildParams();

    const request = format === "pdf"
      ? descargarMiReporteProduccionPdf
      : descargarMiReporteProduccionExcel;

    const result = await request(
      params,
      { signal: controller.signal }
    );

    if (downloadController !== controller) return;
    guardarBlobEnNavegador(result?.blob, result?.filename);
    successMessage.value =
      `Archivo ${format === "pdf" ? "PDF" : "Excel"} descargado.`;
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") return;
    console.error(`Error descargando reporte ${format}:`, error);
    errorMessage.value = normalizeError(error);
  } finally {
    downloadingFormat.value = "";
  }
}

async function clearFilters() {
  Object.assign(filters, {
    tipo: "",
    proyecto: "",
    periodo_modo: "historico",
    mes_desde: "",
    mes_hasta: "",
    anio: "",
    trimestre: "1",
    semestre: "1",
  });

  window.clearTimeout(autoRefreshTimer);
  await loadReport();
}

watch(
  () => paramsKey(),
  (nextKey, previousKey) => {
    if (nextKey === previousKey) return;

    successMessage.value = "";

    if (
      filters.periodo_modo === "personalizado" &&
      (!filters.mes_desde || !filters.mes_hasta)
    ) {
      return;
    }

    scheduleReportRefresh();
  }
);

onMounted(loadReport);

onBeforeUnmount(() => {
  window.clearTimeout(autoRefreshTimer);
  reportController?.abort?.();
  downloadController?.abort?.();
});
</script>

<style scoped src="./mis-reportes.css"></style>
