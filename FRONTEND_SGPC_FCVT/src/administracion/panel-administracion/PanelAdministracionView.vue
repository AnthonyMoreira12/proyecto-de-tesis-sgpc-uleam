<template>
  <div
    class="sgpc-admin-page adm-dashboard-page"
    :aria-busy="dashboardLoading ? 'true' : 'false'"
  >
    <div class="adm-dashboard-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="adm-dashboard-hero page-stage page-hero">
        <div class="adm-dashboard-hero__copy">
          <h1 class="adm-title">Administración</h1>

          <div
            v-if="hasFilters"
            class="adm-dashboard-hero__scope"
            aria-label="Filtros aplicados"
          >
            <span>{{ scopeLabel }}</span>
            <strong>Filtros aplicados</strong>
          </div>
        </div>

        <div class="adm-dashboard-hero__actions">
          <button
            class="adm-dashboard-button adm-dashboard-button--secondary"
            type="button"
            :disabled="dashboardLoading"
            @click="actualizarPanel"
          >
            <svg
              :class="{ 'is-spinning': dashboardLoading }"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M12 4a8 8 0 0 1 7.45 5H17l3.5 3.5L24 9h-2.47A10 10 0 1 0 22 15h-2.1A8 8 0 1 1 12 4Z"
              />
            </svg>
            {{ dashboardLoading ? "Actualizando…" : "Actualizar" }}
          </button>
        </div>
      </header>

      <!-- =====================================================
           GESTIÓN ADMINISTRATIVA · NAVEGACIÓN PRINCIPAL
      ====================================================== -->
      <section
        class="adm-dashboard-modules page-stage page-main"
        aria-labelledby="adm-dashboard-modules-title"
      >
        <header class="adm-dashboard-sectionhead adm-dashboard-sectionhead--simple">
          <div>
            <h2 id="adm-dashboard-modules-title">Gestión administrativa</h2>
          </div>
        </header>

        <div class="adm-dashboard-modulegrid">
          <button
            v-for="card in cards"
            :key="card.name"
            class="adm-dashboard-module adm-surface"
            type="button"
            @click="go(card.name, card.query)"
          >
            <span class="adm-dashboard-module__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" :d="card.iconPath" />
              </svg>
            </span>

            <span class="adm-dashboard-module__body">
              <span class="adm-dashboard-module__topline">
                <strong>{{ card.title }}</strong>
                <span
                  v-if="card.badge"
                  class="adm-dashboard-module__badge"
                  :data-tone="card.badgeTone || 'neutral'"
                >
                  {{ card.badge }}
                </span>
              </span>
            </span>
          </button>
        </div>
      </section>

      <!-- =====================================================
           ERROR / CARGA
      ====================================================== -->
      <AdminErrorState
        v-if="dashboardError"
        title="No se pudo actualizar la información."
        :message="dashboardError"
        :retrying="dashboardLoading"
        @retry="actualizarPanel"
      />

      <AdminLoadingState
        v-if="dashboardLoadingVisible && !dashboard"
        message="Cargando información administrativa…"
        description="Estamos preparando los indicadores y pendientes del panel."
        :skeleton-rows="4"
      />

      <AdminInlineLoader
        v-if="dashboardLoadingVisible && dashboard"
        class="adm-dashboard-refreshing"
        message="Actualizando información…"
      />

      <template v-if="dashboard">
        <!-- ===================================================
             ALCANCE DE LA INFORMACIÓN
        ==================================================== -->
        <section
          class="adm-dashboard-filterbar adm-surface page-stage page-main"
          aria-labelledby="adm-dashboard-filter-title"
        >
          <div class="adm-dashboard-filterbar__head">
            <div>
              <h2 id="adm-dashboard-filter-title">Alcance de la información</h2>
            </div>

            <div class="adm-dashboard-filterbar__actions">
              <button
                class="adm-dashboard-textbutton"
                type="button"
                :aria-expanded="advancedFiltersOpen || hasAdvancedFilters"
                aria-controls="adm-dashboard-advanced-filters"
                @click="advancedFiltersOpen = !advancedFiltersOpen"
              >
                {{ advancedFiltersOpen || hasAdvancedFilters ? "Ocultar filtros" : "Más filtros" }}
              </button>

              <button
                v-if="hasFilters"
                class="adm-dashboard-textbutton"
                type="button"
                :disabled="dashboardLoading"
                @click="limpiarFiltros"
              >
                Limpiar
              </button>
            </div>
          </div>

          <div
            class="adm-dashboard-filters adm-dashboard-filters--primary"
            role="search"
            aria-label="Filtros principales del panel"
          >
            <label class="adm-dashboard-field">
              <span>Sede</span>
              <select
                v-model="filtros.sede"
                :disabled="catalogLoading"
                @change="handleSedeChange"
              >
                <option value="">Todas las sedes</option>
                <option
                  v-for="item in sedes"
                  :key="`sede-${item.id}`"
                  :value="String(item.id)"
                >
                  {{ selectorLabel(item) }}
                </option>
              </select>
            </label>

            <label class="adm-dashboard-field">
              <span>Facultad</span>
              <select
                v-model="filtros.facultad"
                :disabled="catalogLoading"
                @change="handleFacultadChange"
              >
                <option value="">Todas las facultades</option>
                <option
                  v-for="item in facultades"
                  :key="`facultad-${item.id}`"
                  :value="String(item.id)"
                >
                  {{ selectorLabel(item) }}
                </option>
              </select>
            </label>

            <label class="adm-dashboard-field">
              <span>Carrera</span>
              <select
                v-model="filtros.carrera"
                :disabled="catalogLoading || carrerasLoading"
              >
                <option value="">
                  {{ carrerasLoading ? "Cargando…" : "Todas las carreras" }}
                </option>
                <option
                  v-for="item in carreras"
                  :key="`carrera-${item.id}`"
                  :value="String(item.id)"
                >
                  {{ selectorLabel(item) }}
                </option>
              </select>
            </label>

            <label class="adm-dashboard-field">
              <span>Año</span>
              <select v-model="filtros.anio">
                <option value="">Todos los años</option>
                <option
                  v-for="year in availableYears"
                  :key="`year-${year}`"
                  :value="String(year)"
                >
                  {{ year }}
                </option>
              </select>
            </label>
          </div>

          <div
            v-show="advancedFiltersOpen || hasAdvancedFilters"
            id="adm-dashboard-advanced-filters"
            class="adm-dashboard-filters adm-dashboard-filters--advanced"
          >
            <label class="adm-dashboard-field">
              <span>Estado de publicación</span>
              <select v-model="filtros.estado">
                <option value="">Todos los estados</option>
                <option
                  v-for="item in publicationStates"
                  :key="`publication-state-${item.value}`"
                  :value="item.value"
                >
                  {{ item.label }}
                </option>
              </select>
            </label>

            <label class="adm-dashboard-field">
              <span>Estado de proyecto</span>
              <select v-model="filtros.estado_proyecto">
                <option value="">Todos los estados</option>
                <option
                  v-for="item in projectStates"
                  :key="`project-state-${item.value}`"
                  :value="item.value"
                >
                  {{ item.label }}
                </option>
              </select>
            </label>
          </div>
        </section>

        <!-- ===================================================
             REQUIERE ATENCIÓN
        ==================================================== -->
        <section
          class="adm-dashboard-attention adm-surface page-stage page-main"
          aria-labelledby="adm-dashboard-attention-title"
        >
          <header class="adm-dashboard-sectionhead">
            <div>
              <h2 id="adm-dashboard-attention-title">Requiere atención</h2>
            </div>
          </header>

          <div class="adm-dashboard-attention-grid">
            <div class="adm-dashboard-reviewbox">
              <div class="adm-dashboard-reviewbox__head">
                <span class="adm-dashboard-reviewbox__label">Publicaciones por revisar</span>
                <strong>{{ numberLabel(alerts.publicaciones_en_revision) }}</strong>
              </div>

              <div v-if="reviewQueue.length" class="adm-dashboard-reviewlist">
                <button
                  v-for="item in reviewQueue.slice(0, 5)"
                  :key="`review-${item.publicacion_id}`"
                  class="adm-dashboard-reviewitem"
                  type="button"
                  @click="goPublication(item.publicacion_id)"
                >
                  <span class="adm-dashboard-reviewitem__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8M8 17h6"
                      />
                    </svg>
                  </span>

                  <span class="adm-dashboard-reviewitem__body">
                    <strong>{{ item.tipo || "Publicación" }}</strong>
                    <small>
                      {{ item.sede || "Sin sede" }} ·
                      {{ item.carrera || "Sin carrera" }}
                    </small>
                  </span>

                  <time :datetime="item.updated_at || ''">
                    {{ formatDateTime(item.updated_at) }}
                  </time>

                  <span class="adm-dashboard-reviewitem__arrow" aria-hidden="true">→</span>
                </button>
              </div>

              <div v-else class="adm-dashboard-empty adm-dashboard-empty--good">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="m9.2 16.2-4-4L3.8 13.6 9.2 19 20.6 7.6 19.2 6.2l-10 10Z"
                  />
                </svg>
                <strong>Sin publicaciones pendientes</strong>
              </div>
            </div>

            <aside class="adm-dashboard-attention__side" aria-label="Otros pendientes administrativos">
              <div class="adm-dashboard-pendingblock">
                <div class="adm-dashboard-pendingblock__head">
                  <strong>Otros pendientes</strong>
                </div>

                <div class="adm-dashboard-pendinglist">
                  <button
                    v-for="alert in secondaryAttentionCards"
                    :key="alert.key"
                    class="adm-dashboard-pendingitem"
                    :data-tone="alert.tone"
                    type="button"
                    @click="alert.action?.()"
                  >
                    <span class="adm-dashboard-pendingitem__body">
                      <strong>{{ alert.label }}</strong>
                      <small>{{ alert.help }}</small>
                    </span>
                    <span class="adm-dashboard-pendingitem__value">{{ alert.value }}</span>
                  </button>
                </div>
              </div>

              <div class="adm-dashboard-quality">
                <div class="adm-dashboard-quality__head">
                  <strong>Calidad de la información</strong>
                  <span>Aspectos que conviene completar</span>
                </div>

                <div class="adm-dashboard-quality__list">
                  <button
                    v-for="alert in qualityAlertCards"
                    :key="alert.key"
                    class="adm-dashboard-quality__item"
                    type="button"
                    @click="alert.action?.()"
                  >
                    <span>{{ alert.label }}</span>
                    <strong>{{ alert.value }}</strong>
                  </button>
                </div>
              </div>
            </aside>
          </div>
        </section>

        <!-- ===================================================
             RESUMEN GENERAL
        ==================================================== -->
        <section
          class="adm-dashboard-summary page-stage page-main"
          aria-labelledby="adm-dashboard-summary-title"
        >
          <header class="adm-dashboard-sectionhead adm-dashboard-sectionhead--simple">
            <div>
              <h2 id="adm-dashboard-summary-title">Resumen general</h2>
            </div>
          </header>

          <div class="adm-dashboard-kpis" aria-label="Indicadores principales">
            <article
              v-for="card in kpiCards"
              :key="card.key"
              class="adm-dashboard-kpi adm-surface"
              :data-tone="card.tone"
            >
              <span class="adm-dashboard-kpi__label">{{ card.label }}</span>
              <strong class="adm-dashboard-kpi__value">{{ card.value }}</strong>
              <span class="adm-dashboard-kpi__meta">{{ card.meta }}</span>
            </article>
          </div>
        </section>

        <!-- ===================================================
             ACTIVIDAD + REPORTES
        ==================================================== -->
        <div class="adm-dashboard-bottom-grid page-stage page-main">
          <section
            class="adm-dashboard-card adm-dashboard-activity adm-surface"
            aria-labelledby="adm-dashboard-activity-title"
          >
            <header class="adm-dashboard-card__head">
              <div>
                <h2 id="adm-dashboard-activity-title">Actividad reciente</h2>
              </div>
            </header>

            <div v-if="recentActivity.length" class="adm-dashboard-timeline">
              <button
                v-for="item in recentActivity.slice(0, 7)"
                :key="`activity-${item.id}`"
                class="adm-dashboard-timeline__item"
                type="button"
                @click="goPublication(item.publicacion_id)"
              >
                <span class="adm-dashboard-timeline__marker" aria-hidden="true"></span>
                <span class="adm-dashboard-timeline__body">
                  <strong>{{ item.evento_label || eventLabel(item.evento) }}</strong>
                  <small>
                    {{ item.actor_nombre || item.actor_email || "Sistema" }} ·
                    {{ transitionLabel(item) }}
                  </small>
                </span>
                <time :datetime="item.created_at || ''">
                  {{ formatDateTime(item.created_at) }}
                </time>
              </button>
            </div>

            <p v-else class="adm-dashboard-empty-copy">
              Sin actividad reciente.
            </p>
          </section>

          <section
            class="adm-dashboard-report adm-surface"
            aria-labelledby="adm-dashboard-report-title"
          >
            <div class="adm-dashboard-report__intro">
              <h2 id="adm-dashboard-report-title">Reportes</h2>
              <p>Genera un resumen o descarga la información con el alcance seleccionado.</p>
            </div>

            <div class="adm-dashboard-report__actions">
              <button
                class="adm-dashboard-button adm-dashboard-button--secondary"
                type="button"
                :disabled="reportPreviewLoading || reportDownloadLoading"
                @click="prepararVistaPreviaReporte"
              >
                {{ reportPreviewLoading ? "Preparando…" : "Ver resumen" }}
              </button>

              <button
                class="adm-dashboard-button adm-dashboard-button--primary"
                type="button"
                :disabled="reportPreviewLoading || reportDownloadLoading"
                @click="exportarReporteGestion"
              >
                {{ reportDownloadLoading ? "Preparando Excel…" : "Descargar Excel" }}
              </button>
            </div>

            <AdminActionFeedback
              v-if="reportPreviewLoading"
              status="loading"
              message="Preparando resumen del reporte…"
            />

            <AdminActionFeedback
              v-else-if="reportDownloadLoading"
              status="loading"
              message="Generando archivo Excel…"
            />

            <div v-if="reportFilterChips.length" class="adm-dashboard-report__chips">
              <span v-for="chip in reportFilterChips" :key="chip.key">
                <small>{{ chip.label }}</small>
                <strong>{{ chip.value }}</strong>
              </span>
            </div>

            <AdminActionFeedback
              v-if="reportError"
              status="error"
              :message="`No se pudo preparar el reporte. ${reportError}`"
            />

            <AdminActionFeedback
              v-if="reportSuccess"
              status="success"
              :message="reportSuccess"
            />

            <div v-if="reportPreview" class="adm-dashboard-report__preview">
              <article
                v-for="item in reportSummaryCards"
                :key="item.key"
                class="adm-dashboard-reportmetric"
                :data-tone="item.tone"
              >
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </article>
            </div>
          </section>
        </div>
      </template>
    </div>
  </div>
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
import { storeToRefs } from "pinia";
import { useRouter } from "vue-router";

import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import { useAsyncState } from "../_shared/composables/useAsyncState";

import {
  getAdminCarreras,
  getAdminFacultades,
  getAdminSedes,
} from "../_shared/utils/adminCatalogCache";
import { useAutoFilters } from "../../scripts/composables/useAutoFilters";
import {
  useNotificacionesStore,
} from "../../scripts/stores/notificacionesStore";
import {
  listarSolicitudesExtensionPerfil,
} from "../../scripts/api/profileExtensionApi";
import {
  descargarReporteGestionExcel as solicitarReporteGestionExcel,
  guardarBlobEnNavegador,
  obtenerDashboardGestion,
  obtenerVistaPreviaReporteGestion,
} from "../../scripts/api/gestionApi";

const router = useRouter();
const notificationsStore =
  useNotificacionesStore();

const {
  incomingSequence,
} = storeToRefs(
  notificationsStore
);

const dashboard = ref(null);
const dashboardRequestState = useAsyncState({ loadingDelay: 220 });
const dashboardLoading = computed(() => dashboardRequestState.pending.value);
const dashboardLoadingVisible = computed(
  () => dashboardRequestState.visibleLoading.value,
);
const dashboardError = ref("");
const reportPreview = ref(null);
const reportPreviewLoading = ref(false);
const reportDownloadLoading = ref(false);
const reportError = ref("");
const reportSuccess = ref("");
const advancedFiltersOpen = ref(false);
const catalogLoading = ref(false);
const carrerasLoading = ref(false);
const profileExtensionPendingCount = ref(0);
const profileExtensionCountLoading = ref(false);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);

let dashboardController = null;
let careersController = null;
let reportPreviewController = null;
let reportDownloadController = null;

const filtros = reactive({
  sede: "",
  facultad: "",
  carrera: "",
  anio: "",
  estado: "",
  estado_proyecto: "",
});

const indicators = computed(() => dashboard.value?.indicadores || {});
const alerts = computed(() => dashboard.value?.alertas || {});
const projectMetrics = computed(() => dashboard.value?.proyectos || {});


const cards = computed(() => [
  {
    name: "AdminRevisionPublicaciones",
    title: "Revisión de publicaciones",
    badge:
      dashboardLoading.value && !dashboard.value
        ? "Cargando…"
        : Number(alerts.value.publicaciones_en_revision || 0) > 0
          ? `${numberLabel(alerts.value.publicaciones_en_revision)} pendientes`
          : null,
    badgeTone:
      dashboardLoading.value && !dashboard.value
        ? "neutral"
        : "warning",
    iconPath:
      "M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h4m-4 4h3m5.2-4.7 1.4 1.4-4.6 4.6-2.3-2.3 1.4-1.4.9.9 3.2-3.2Z",
  },
  {
    name: "AdminUsuarios",
    title: "Usuarios",
    iconPath:
      "M12 12a4 4 0 1 0-4-4a4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z",
  },
  {
    name: "AdminPublicaciones",
    title: "Registrar para usuario",
    iconPath:
      "M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5M8 12h8M8 16h5m4-5v3m0 0v3m0-3h3m-3 0h-3",
  },
  {
    name: "AdminSolicitudesModificacion",
    title: "Solicitudes de modificación",
    iconPath:
      "M5 3h14v18H5V3Zm3 4h8v2H8V7Zm0 4h8v2H8v-2Zm0 4h5v2H8v-2Z",
  },
  {
    name: "GestionFacultadesCarreras",
    title: "Estructura académica",
    iconPath:
      "M3 3h8v8H3V3Zm10 0h8v8h-8V3ZM3 13h8v8H3v-8Zm10 0h8v8h-8v-8Z",
  },
  {
    name: "ProyectosListado",
    title: "Proyectos",
    iconPath:
      "M10 4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6Z",
  },
]);
const availableYears = computed(() => {
  const values = dashboard.value?.filtros_disponibles?.anios;
  return Array.isArray(values) ? values : [];
});

const publicationStates = computed(() => {
  const values = dashboard.value?.filtros_disponibles?.estados_publicacion;
  return Array.isArray(values) ? values : [];
});

const projectStates = computed(() => {
  const values = dashboard.value?.filtros_disponibles?.estados_proyecto;
  return Array.isArray(values) ? values : [];
});

const reviewQueue = computed(() =>
  Array.isArray(dashboard.value?.cola_revision)
    ? dashboard.value.cola_revision
    : []
);

const recentActivity = computed(() =>
  Array.isArray(dashboard.value?.actividad_reciente)
    ? dashboard.value.actividad_reciente
    : []
);

const reportIndicators = computed(() => reportPreview.value?.indicadores || {});
const reportAlerts = computed(() => reportPreview.value?.alertas || {});
const reportProjects = computed(() => reportPreview.value?.proyectos || {});

const reportIncludes = computed(() =>
  Array.isArray(reportPreview.value?.incluye) ? reportPreview.value.incluye : []
);

const reportSheetsEstimated = computed(() => {
  const value = Number(reportPreview.value?.hojas_estimadas || 0);
  return Number.isFinite(value) && value > 0 ? value : reportIncludes.value.length;
});

const reportAlertsTotal = computed(() =>
  Number(reportAlerts.value.publicaciones_en_revision || 0) +
  Number(reportAlerts.value.publicaciones_observadas || 0) +
  Number(reportAlerts.value.publicaciones_sin_pdf || 0) +
  Number(reportAlerts.value.publicaciones_sin_proyecto || 0) +
  Number(reportAlerts.value.proyectos_sin_produccion || 0)
);

const hasFilters = computed(() =>
  Object.values(filtros).some((value) => String(value || "").trim())
);

const hasAdvancedFilters = computed(() =>
  Boolean(filtros.estado || filtros.estado_proyecto)
);

const scopeLabel = computed(() => {
  const selectedSite = sedes.value.find(
    (item) => String(item?.id) === String(filtros.sede)
  );
  const selectedFaculty = facultades.value.find(
    (item) => String(item?.id) === String(filtros.facultad)
  );
  const selectedCareer = carreras.value.find(
    (item) => String(item?.id) === String(filtros.carrera)
  );

  if (selectedCareer) return selectorLabel(selectedCareer);
  if (selectedFaculty) return selectorLabel(selectedFaculty);
  if (selectedSite) return selectorLabel(selectedSite);
  return "Vista institucional";
});

const reportFilterChips = computed(() => {
  const chips = [];
  const selectedSite = sedes.value.find(
    (item) => String(item?.id) === String(filtros.sede)
  );
  const selectedFaculty = facultades.value.find(
    (item) => String(item?.id) === String(filtros.facultad)
  );
  const selectedCareer = carreras.value.find(
    (item) => String(item?.id) === String(filtros.carrera)
  );

  if (selectedSite) chips.push({ key: "sede", label: "Sede", value: selectorLabel(selectedSite) });
  if (selectedFaculty) chips.push({ key: "facultad", label: "Facultad", value: selectorLabel(selectedFaculty) });
  if (selectedCareer) chips.push({ key: "carrera", label: "Carrera", value: selectorLabel(selectedCareer) });
  if (filtros.anio) chips.push({ key: "anio", label: "Año", value: String(filtros.anio) });
  if (filtros.estado) chips.push({ key: "estado", label: "Estado publicación", value: stateLabel(filtros.estado) });
  if (filtros.estado_proyecto) {
    const projectState = projectStates.value.find((item) => item?.value === filtros.estado_proyecto);
    chips.push({
      key: "estado_proyecto",
      label: "Estado proyecto",
      value: projectState?.label || String(filtros.estado_proyecto).replaceAll("_", " "),
    });
  }

  return chips;
});

const reportSummaryCards = computed(() => [
  {
    key: "publications",
    label: "Publicaciones",
    value: numberLabel(reportIndicators.value.total_publicaciones),
    tone: "primary",
  },
  {
    key: "pending",
    label: "Pendientes",
    value: numberLabel(reportIndicators.value.pendientes_gestion),
    tone: "warning",
  },
  {
    key: "pdf",
    label: "Con documento PDF",
    value: formatPercent(reportIndicators.value.cobertura_pdf),
    tone: "info",
  },
  {
    key: "projects",
    label: "Proyectos",
    value: numberLabel(reportProjects.value.total_proyectos),
    tone: "success",
  },
]);
const kpiCards = computed(() => [
  {
    key: "total",
    label: "Publicaciones",
    value: numberLabel(indicators.value.total_publicaciones),
    meta: `${numberLabel(indicators.value.con_proyecto)} vinculadas a proyectos`,
    tone: "neutral",
  },
  {
    key: "approved",
    label: "Aprobadas",
    value: numberLabel(indicators.value.aprobada),
    meta: `${formatPercent(indicators.value.tasa_aprobacion_resueltas)} de las decisiones resueltas`,
    tone: "success",
  },
  {
    key: "pdf",
    label: "Con documento PDF",
    value: formatPercent(indicators.value.cobertura_pdf),
    meta: `${numberLabel(indicators.value.sin_pdf)} pendientes de documento`,
    tone: "info",
  },
  {
    key: "projects",
    label: "Proyectos",
    value: numberLabel(projectMetrics.value.total_proyectos),
    meta: `${numberLabel(alerts.value.proyectos_sin_produccion)} sin publicaciones asociadas`,
    tone: "primary",
  },
]);
const secondaryAttentionCards = computed(() => [
  {
    key: "profile-extension",
    label: "Solicitudes de perfil",
    value: numberLabel(profileExtensionPendingCount.value),
    help: "Solicitudes pendientes de autorización.",
    tone: profileExtensionPendingCount.value > 0 ? "warning" : "success",
    action: () =>
      router.push({
        name: "AdminUsuarios",
        query: {
          tab: "solicitudes",
        },
      }),
  },
  {
    key: "observed",
    label: "Publicaciones observadas",
    value: numberLabel(alerts.value.publicaciones_observadas),
    help: "Continúan dentro del ciclo de corrección.",
    tone: "info",
    action: () => goReview("observada"),
  },
]);

const qualityAlertCards = computed(() => [
  {
    key: "no-pdf",
    label: "Sin documento PDF",
    value: numberLabel(alerts.value.publicaciones_sin_pdf),
    action: () => go("AdminPublicaciones"),
  },
  {
    key: "no-project",
    label: "Sin proyecto",
    value: numberLabel(alerts.value.publicaciones_sin_proyecto),
    action: () => go("AdminPublicaciones"),
  },
  {
    key: "projects-empty",
    label: "Proyectos sin publicaciones",
    value: numberLabel(alerts.value.proyectos_sin_produccion),
    action: () => go("ProyectosListado"),
  },
]);


function selectorLabel(item) {
  return String(
    item?.nombre ||
      item?.name ||
      item?.label ||
      item?.descripcion ||
      `Registro ${item?.id || ""}`
  ).trim();
}

function normalizeSelectorPayload(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

function numberLabel(value) {
  const number = Number(value || 0);
  return Number.isFinite(number)
    ? new Intl.NumberFormat("es-EC").format(number)
    : "0";
}

function formatPercent(value) {
  const number = Number(value || 0);
  if (!Number.isFinite(number)) return "0%";
  return `${number.toLocaleString("es-EC", {
    minimumFractionDigits: number % 1 ? 1 : 0,
    maximumFractionDigits: 1,
  })}%`;
}

function formatDateTime(value) {
  if (!value) return "Sin fecha";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function eventLabel(value) {
  const labels = {
    creada: "Publicación creada",
    editada: "Publicación editada",
    enviada_revision: "Enviada a revisión",
    observada: "Publicación observada",
    aprobada: "Publicación aprobada",
    rechazada: "Publicación rechazada",
    reenviada_revision: "Reenviada a revisión",
  };
  return labels[String(value || "").trim().toLowerCase()] || "Actividad registrada";
}

function stateLabel(value) {
  const states = publicationStates.value;
  const match = states.find((item) => item?.value === value);
  return match?.label || String(value || "").replaceAll("_", " ") || "Sin estado";
}

function transitionLabel(item) {
  const before = item?.estado_anterior;
  const after = item?.estado_resultante;
  if (before && after && before !== after) {
    return `${stateLabel(before)} → ${stateLabel(after)}`;
  }
  if (after) return stateLabel(after);
  if (before) return stateLabel(before);
  return "Sin cambio de estado";
}

function buildDashboardParams() {
  return {
    sede: filtros.sede || undefined,
    facultad: filtros.facultad || undefined,
    carrera: filtros.carrera || undefined,
    anio: filtros.anio || undefined,
    estado: filtros.estado || undefined,
    estado_proyecto: filtros.estado_proyecto || undefined,
    top: 10,
  };
}

function buildReportParams() {
  return {
    sede: filtros.sede || undefined,
    facultad: filtros.facultad || undefined,
    carrera: filtros.carrera || undefined,
    anio: filtros.anio || undefined,
    estado: filtros.estado || undefined,
    estado_proyecto: filtros.estado_proyecto || undefined,
    top: 100,
  };
}

function limpiarVistaPreviaReporte() {
  reportPreviewController?.abort?.();
  reportPreviewController = null;
  reportPreview.value = null;
  reportPreviewLoading.value = false;
  reportError.value = "";
  reportSuccess.value = "";
}

function dashboardErrorMessage(error) {
  const payload = error?.response?.data || error?.data || error;
  if (typeof payload === "string" && payload.trim()) return payload.trim();
  if (payload?.detail) return String(payload.detail);
  if (payload && typeof payload === "object") {
    const messages = Object.entries(payload).flatMap(([key, value]) => {
      const list = Array.isArray(value) ? value : [value];
      return list
        .map((item) => String(item || "").trim())
        .filter(Boolean)
        .map((item) => `${key}: ${item}`);
    });
    if (messages.length) return messages.join(" · ");
  }
  return "Intente nuevamente.";
}

async function cargarCatalogos() {
  catalogLoading.value = true;
  try {
    const [sitesPayload, facultiesPayload] = await Promise.all([
      getAdminSedes(),
      getAdminFacultades(),
    ]);
    sedes.value = normalizeSelectorPayload(sitesPayload);
    facultades.value = normalizeSelectorPayload(facultiesPayload);
    await cargarCarreras();
  } catch (error) {
    console.error("Error cargando catálogos del dashboard:", error);
  } finally {
    catalogLoading.value = false;
  }
}

async function cargarCarreras() {
  careersController?.abort?.();
  const controller = new AbortController();
  careersController = controller;
  carrerasLoading.value = true;

  try {
    const payload = await getAdminCarreras({
      sedeId: filtros.sede || null,
      facultadId: filtros.facultad || null,
    });
    if (careersController !== controller) return;

    carreras.value = normalizeSelectorPayload(payload);

    if (
      filtros.carrera &&
      !carreras.value.some((item) => String(item?.id) === String(filtros.carrera))
    ) {
      filtros.carrera = "";
    }
  } catch (error) {
    if (error?.name !== "CanceledError" && error?.code !== "ERR_CANCELED") {
      console.error("Error cargando carreras del dashboard:", error);
      carreras.value = [];
    }
  } finally {
    if (careersController === controller) {
      careersController = null;
      carrerasLoading.value = false;
    }
  }
}

async function handleSedeChange() {
  filtros.carrera = "";
  await cargarCarreras();
}

async function handleFacultadChange() {
  filtros.carrera = "";
  await cargarCarreras();
}

async function cargarDashboard({ silent = false } = {}) {
  dashboardController?.abort?.();
  const controller = new AbortController();
  dashboardController = controller;

  dashboardRequestState.begin({ clearError: false });
  if (!silent) dashboardError.value = "";

  try {
    const payload = await obtenerDashboardGestion(buildDashboardParams(), {
      signal: controller.signal,
    });
    if (dashboardController !== controller) return;
    dashboard.value = payload || null;
    dashboardError.value = "";
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") return;
    console.error("Error cargando dashboard de gestión:", error);
    dashboardError.value = dashboardErrorMessage(error);
  } finally {
    if (dashboardController === controller) {
      dashboardRequestState.finish({ loaded: Boolean(dashboard.value) });
    }
  }
}

async function prepararVistaPreviaReporte() {
  reportPreviewController?.abort?.();
  const controller = new AbortController();
  reportPreviewController = controller;

  reportPreviewLoading.value = true;
  reportError.value = "";
  reportSuccess.value = "";

  try {
    const payload = await obtenerVistaPreviaReporteGestion(buildReportParams(), {
      signal: controller.signal,
    });
    if (reportPreviewController !== controller) return;
    reportPreview.value = payload || null;
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") return;
    console.error("Error cargando vista previa del reporte de gestión:", error);
    reportPreview.value = null;
    reportError.value = dashboardErrorMessage(error);
  } finally {
    if (reportPreviewController === controller) reportPreviewLoading.value = false;
  }
}

async function exportarReporteGestion() {
  reportDownloadController?.abort?.();
  const controller = new AbortController();
  reportDownloadController = controller;

  reportDownloadLoading.value = true;
  reportError.value = "";
  reportSuccess.value = "";

  try {
    const result = await solicitarReporteGestionExcel(buildReportParams(), {
      signal: controller.signal,
    });
    if (reportDownloadController !== controller) return;

    guardarBlobEnNavegador(result?.blob, result?.filename);
    reportSuccess.value = "Excel descargado.";

    if (!reportPreview.value) {
      await prepararVistaPreviaReporte();
    }
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") return;
    console.error("Error descargando reporte institucional:", error);
    reportError.value = dashboardErrorMessage(error);
  } finally {
    if (reportDownloadController === controller) reportDownloadLoading.value = false;
  }
}

async function limpiarFiltros() {
  limpiarVistaPreviaReporte();
  Object.assign(filtros, {
    sede: "",
    facultad: "",
    carrera: "",
    anio: "",
    estado: "",
    estado_proyecto: "",
  });
  advancedFiltersOpen.value = false;
  await cargarCarreras();
}

const go = (name, query = undefined) => {
  if (!name) return;

  router.push({
    name,
    ...(query ? { query } : {}),
  });
};

function goReview(estado = "") {
  router.push({
    name: "AdminRevisionPublicaciones",
    query: estado ? { estado } : {},
  });
}

function goPublication(publicationId) {
  const id = Number(publicationId);
  if (!Number.isInteger(id) || id < 1) return;
  router.push({
    name: "AdminRevisionDetalle",
    params: { id },
  });
}

watch(
  () => [
    filtros.sede,
    filtros.facultad,
    filtros.carrera,
    filtros.anio,
    filtros.estado,
    filtros.estado_proyecto,
  ],
  () => {
    if (reportPreview.value || reportError.value || reportSuccess.value) {
      limpiarVistaPreviaReporte();
    }
  }
);

useAutoFilters(
  filtros,
  () => cargarDashboard({ silent: false }),
  { delay: 320 },
);

const loadProfileExtensionRequests = async () => {
  if (profileExtensionCountLoading.value) {
    return;
  }

  profileExtensionCountLoading.value = true;

  try {
    const payload =
      await listarSolicitudesExtensionPerfil({
        estado: "pendiente",
        limit: 5,
      });

    const count = Number(
      payload?.count || 0
    );

    profileExtensionPendingCount.value =
      Number.isFinite(count) && count > 0
        ? count
        : 0;
  } catch (error) {
    /*
      Conservamos el último contador conocido. Un fallo temporal
      de red no debe convertir visualmente solicitudes pendientes
      en cero.
    */
    console.warn(
      "No se pudo consultar las solicitudes de extensión de perfil.",
      error
    );
  } finally {
    profileExtensionCountLoading.value = false;
  }
};

const actualizarPanel = async () => {
  await Promise.all([
    cargarDashboard({ silent: false }),
    loadProfileExtensionRequests(),
  ]);
};

const handleWindowFocus = () => {
  loadProfileExtensionRequests();
};

const handleVisibilityChange = () => {
  if (document.visibilityState === "visible") {
    loadProfileExtensionRequests();
  }
};

/*
  El host global ya detecta las notificaciones nuevas. Cuando llega
  una, reutilizamos esa señal para refrescar únicamente el contador
  administrativo, sin crear un segundo polling.
*/
watch(
  () => incomingSequence.value,
  () => {
    loadProfileExtensionRequests();
  }
);

onMounted(async () => {
  window.addEventListener(
    "focus",
    handleWindowFocus
  );

  document.addEventListener(
    "visibilitychange",
    handleVisibilityChange
  );

  await Promise.all([
    cargarCatalogos(),
    actualizarPanel(),
  ]);
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "focus",
    handleWindowFocus
  );

  document.removeEventListener(
    "visibilitychange",
    handleVisibilityChange
  );

  dashboardController?.abort?.();
  careersController?.abort?.();
  reportPreviewController?.abort?.();
  reportDownloadController?.abort?.();
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./panel-administracion.css"></style>
