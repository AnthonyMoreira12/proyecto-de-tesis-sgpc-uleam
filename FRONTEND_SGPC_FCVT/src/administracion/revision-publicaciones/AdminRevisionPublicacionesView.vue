<template>
  <div class="sgpc-admin-page adm-review-page">
    <main class="adm-review-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="adm-review-toolbar page-stage page-main">
        <div class="adm-review-toolbar__copy">
          <button
            class="adm-review-back"
            type="button"
            @click="goToPanel"
          >
            <span aria-hidden="true">←</span>
            Volver a administración
          </button>

          <div class="adm-review-toolbar__headline">
            <div>
              <h1>Revisión de publicaciones</h1>
              <p>
                Revise las publicaciones enviadas y decida si se aprueban,
                necesitan correcciones o deben rechazarse.
              </p>
            </div>
          </div>
        </div>

        <div class="adm-review-toolbar__actions">
          <button
            class="adm-review-button"
            type="button"
            :disabled="loading"
            @click="refreshAll"
          >
            <svg
              :class="{ 'adm-review-refresh-spin': loading }"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M12 4a8 8 0 0 1 7.45 5H17l3.5 3.5L24 9h-2.47A10 10 0 1 0 22 15h-2.1A8 8 0 1 1 12 4Z"
              />
            </svg>

            {{ loading ? "Actualizando…" : "Actualizar" }}
          </button>
        </div>
      </header>

      <!-- =====================================================
           ESTADOS + BÚSQUEDA
      ====================================================== -->
      <section class="adm-review-controls adm-review-local-surface page-stage page-main">
        <div
          class="adm-review-tabs"
          role="tablist"
          aria-label="Estados de revisión"
          @keydown="handleTabsKeydown"
        >
          <button
            v-for="tab in reviewTabs"
            :key="tab.value || 'all'"
            class="adm-review-tab"
            :class="{ 'is-active': filters.estado === tab.value }"
            type="button"
            role="tab"
            :id="`review-tab-${tab.value || 'all'}`"
            :aria-selected="filters.estado === tab.value ? 'true' : 'false'"
            aria-controls="adm-review-results-panel"
            :tabindex="filters.estado === tab.value ? 0 : -1"
            @click="setState(tab.value)"
          >
            <span>{{ tab.label }}</span>
            <strong>{{ numberLabel(stateCount(tab.value)) }}</strong>
          </button>
        </div>

        <form
          class="adm-review-search-row"
          @submit.prevent="applyFilters"
        >
          <label class="adm-review-searchbox">
            <span class="sr-only">Buscar publicaciones</span>

            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M10 18a8 8 0 1 1 5.29-14 8 8 0 0 1 .71 11.29L21 20.3 19.3 22l-5-5A7.96 7.96 0 0 1 10 18Zm0-2a6 6 0 1 0 0-12 6 6 0 0 0 0 12Z"
              />
            </svg>

            <input
              v-model.trim="filters.q"
              type="search"
              placeholder="Título, autor, proyecto, sede, facultad o carrera"
              autocomplete="off"
            />
          </label>

          <button
            class="adm-review-search-submit"
            type="submit"
            :disabled="loading"
          >
            Buscar
          </button>

          <button
            class="adm-review-filter-toggle"
            :class="{ 'is-active': showAdvancedFilters || hasNonStateFilters }"
            type="button"
            :aria-expanded="showAdvancedFilters ? 'true' : 'false'"
            @click="showAdvancedFilters = !showAdvancedFilters"
          >
            Más filtros

            <span
              v-if="activeAdvancedFilterCount"
              class="adm-review-filter-toggle__count"
              :aria-label="`${activeAdvancedFilterCount} filtros adicionales activos`"
            >
              {{ activeAdvancedFilterCount }}
            </span>
          </button>

          <button
            v-if="hasNonStateFilters"
            class="adm-review-textbutton"
            type="button"
            :disabled="loading"
            @click="resetFilters"
          >
            Limpiar
          </button>
        </form>

        <div
          v-if="showAdvancedFilters"
          class="adm-review-advanced"
        >
          <label class="adm-review-field">
            <span>Sede</span>
            <select
              v-model="filters.sede_id"
              :disabled="catalogLoading"
              @change="handleAcademicFilterChange"
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

          <label class="adm-review-field">
            <span>Facultad</span>
            <select
              v-model="filters.facultad_id"
              :disabled="catalogLoading"
              @change="handleAcademicFilterChange"
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

          <label class="adm-review-field">
            <span>Carrera</span>
            <select
              v-model="filters.carrera_id"
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

          <label class="adm-review-field">
            <span>Tipo</span>
            <select v-model="filters.tipo">
              <option
                v-for="item in typeOptions"
                :key="item.value || 'all-types'"
                :value="item.value"
              >
                {{ item.label }}
              </option>
            </select>
          </label>

          <label class="adm-review-field">
            <span>Año</span>
            <input
              v-model="filters.anio"
              type="number"
              min="1900"
              max="2100"
              step="1"
              placeholder="Todos"
            />
          </label>

          <label class="adm-review-check">
            <input
              v-model="filters.solo_con_pdf"
              type="checkbox"
            />
            <span>Solo con documento PDF</span>
          </label>

          <button
            class="adm-review-filter-submit"
            type="button"
            :disabled="loading"
            @click="applyFilters"
          >
            Aplicar
          </button>
        </div>
      </section>

      <!-- =====================================================
           MENSAJES
      ====================================================== -->
      <AdminErrorState
        v-if="errorMessage"
        class="adm-review-stage3-feedback"
        title="No se pudieron cargar las publicaciones"
        :message="errorMessage"
        retry-label="Reintentar"
        :retrying="loading"
        @retry="refreshAll"
      />

      <!-- =====================================================
           LISTADO
      ====================================================== -->
      <section
        id="adm-review-results-panel"
        class="adm-review-results page-stage page-main"
        role="tabpanel"
        :aria-labelledby="`review-tab-${filters.estado || 'all'}`"
        :aria-busy="loading ? 'true' : 'false'"
      >
        <header class="adm-review-results__head">
          <h2 class="sr-only">{{ currentStateTitle }}</h2>

          <span
            class="adm-review-results__count"
            aria-live="polite"
          >
            {{ resultsCountLabel }}
            <template v-if="hasNonStateFilters">
              · filtros aplicados
            </template>
          </span>
        </header>

        <AdminInlineLoader
          v-if="refreshing && loadingFeedbackVisible"
          class="adm-review-stage3-inline"
          message="Actualizando publicaciones…"
        />

        <div
          v-if="initialLoading"
          class="adm-review-stage3-loading-slot"
        >
          <AdminLoadingState
            v-if="loadingFeedbackVisible"
            class="adm-review-stage3-loading"
            message="Cargando publicaciones…"
            description="Estamos preparando la cola de revisión."
            :skeleton-rows="5"
          />
        </div>

        <div
          v-else-if="items.length"
          class="adm-review-list"
        >
          <article
            v-for="item in items"
            :key="publicationId(item)"
            class="adm-review-record adm-review-local-surface"
            :data-state="reviewStateTone(item)"
          >
            <div class="adm-review-record__main">
              <div class="adm-review-record__identity">
                <div class="adm-review-record__meta">
                  <span
                    v-if="!filters.estado"
                    class="adm-review-statechip"
                    :data-tone="reviewStateTone(item)"
                  >
                    {{ reviewStateLabel(item) }}
                  </span>

                  <span class="adm-review-type">
                    {{ reviewPublicationType(item) }}
                  </span>
                </div>

                <h3>{{ reviewTitle(item) }}</h3>

                <p class="adm-review-record__author">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z"
                    />
                  </svg>

                  {{ reviewAuthor(item) }}
                </p>
              </div>

              <div class="adm-review-record__context">
                <div class="adm-review-record__fact adm-review-record__fact--wide">
                  <span>Información académica</span>
                  <strong>{{ reviewAcademicContext(item) }}</strong>
                </div>

                <div class="adm-review-record__fact">
                  <span>Proyecto</span>
                  <strong>{{ reviewProject(item) }}</strong>
                </div>

                <div class="adm-review-record__fact">
                  <span>Período</span>
                  <strong>{{ reviewPeriod(item) }}</strong>
                </div>

                <div
                  v-if="!reviewHasPdf(item)"
                  class="adm-review-record__fact adm-review-record__fact--warning"
                >
                  <span>Documento</span>
                  <strong>Sin PDF</strong>
                </div>
              </div>

              <div class="adm-review-record__side">
                <time
                  class="adm-review-record__date"
                  :datetime="reviewUpdatedAt(item) || ''"
                >
                  Último cambio: {{ formatDateTime(reviewUpdatedAt(item)) }}
                </time>

                <button
                  class="adm-review-open"
                  :class="{
                    'is-action-required':
                      reviewState(item) === ESTADO_PUBLICACION.EN_REVISION,
                  }"
                  type="button"
                  @click="goToPublicationDetail(item)"
                >
                  {{ reviewActionLabel(item) }}
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            </div>
          </article>
        </div>

        <AdminEmptyState
          v-else
          class="adm-review-stage3-empty"
          :title="emptyTitle"
          :message="emptyHelp"
          :action-label="hasNonStateFilters ? 'Limpiar filtros' : ''"
          @action="resetFilters"
        />

        <nav
          v-if="pageCount > 1"
          class="adm-review-pagination adm-review-local-surface"
          aria-label="Paginación de publicaciones"
        >
          <button
            type="button"
            :disabled="currentPage <= 1 || loading"
            @click="changePage(currentPage - 1)"
          >
            ← Anterior
          </button>

          <span>
            Página <strong>{{ currentPage }}</strong> de
            <strong>{{ pageCount }}</strong>
          </span>

          <button
            type="button"
            :disabled="currentPage >= pageCount || loading"
            @click="changePage(currentPage + 1)"
          >
            Siguiente →
          </button>
        </nav>
      </section>
    </main>
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
import { useRoute, useRouter } from "vue-router";

import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminEmptyState from "../_shared/components/feedback/AdminEmptyState.vue";

import {
  getAdminCarreras,
  getAdminFacultades,
  getAdminSedes,
} from "../_shared/utils/adminCatalogCache";
import {
  listarAdminPublicaciones,
} from "../../scripts/api/publicacionesAdminApi";
import {
  obtenerDashboardGestion,
} from "../../scripts/api/gestionApi";
import {
  ESTADO_PUBLICACION,
  estadoPublicacionLabel,
  estadoPublicacionTone,
  normalizarEstadoPublicacion,
} from "../../scripts/utils/publicacion-estados";

const router = useRouter();
const route = useRoute();

const PAGE_SIZE = 20;

const VALID_REVIEW_STATES = new Set([
  "",
  ESTADO_PUBLICACION.EN_REVISION,
  ESTADO_PUBLICACION.OBSERVADA,
  ESTADO_PUBLICACION.APROBADA,
  ESTADO_PUBLICACION.RECHAZADA,
]);

const reviewTabs = Object.freeze([
  {
    value: ESTADO_PUBLICACION.EN_REVISION,
    label: "En revisión",
  },
  {
    value: ESTADO_PUBLICACION.OBSERVADA,
    label: "Observadas",
  },
  {
    value: ESTADO_PUBLICACION.APROBADA,
    label: "Aprobadas",
  },
  {
    value: ESTADO_PUBLICACION.RECHAZADA,
    label: "Rechazadas",
  },
  {
    value: "",
    label: "Todas",
  },
]);

const typeOptions = Object.freeze([
  { value: "", label: "Todos los tipos" },
  { value: "articulo_alto_impacto", label: "Artículo de alto impacto" },
  { value: "articulo_regional", label: "Artículo regional" },
  { value: "ponencia", label: "Ponencia" },
  { value: "libro", label: "Libro" },
  { value: "capitulo_libro", label: "Capítulo de libro" },
]);

const items = ref([]);
const total = ref(0);
const currentPage = ref(normalizePage(route.query?.pagina));
const loading = ref(false);
const hasLoaded = ref(false);
const loadingFeedbackVisible = ref(false);
const errorMessage = ref("");

let loadingFeedbackTimer = null;

const dashboard = ref(null);
const dashboardLoading = ref(false);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const catalogLoading = ref(false);
const carrerasLoading = ref(false);


let listRequestSerial = 0;
let dashboardController = null;
let careersController = null;

const filters = reactive({
  q: String(route.query?.q || "").trim(),
  estado: normalizeInitialState(route.query?.estado),
  sede_id: normalizeQueryId(route.query?.sede_id || route.query?.sede),
  facultad_id: normalizeQueryId(route.query?.facultad_id || route.query?.facultad),
  carrera_id: normalizeQueryId(route.query?.carrera_id || route.query?.carrera),
  tipo: String(route.query?.tipo || "").trim(),
  anio: normalizeYear(route.query?.anio),
  solo_con_pdf: normalizeQueryBoolean(route.query?.solo_con_pdf),
});

const showAdvancedFilters = ref(
  Boolean(
    route.query?.sede_id ||
      route.query?.sede ||
      route.query?.facultad_id ||
      route.query?.facultad ||
      route.query?.carrera_id ||
      route.query?.carrera ||
      route.query?.tipo ||
      route.query?.anio ||
      route.query?.solo_con_pdf
  )
);

const indicators = computed(() => dashboard.value?.indicadores || {});

const initialLoading = computed(() =>
  loading.value && !hasLoaded.value && !items.value.length
);

const refreshing = computed(() =>
  loading.value && hasLoaded.value && items.value.length > 0
);

const activeAdvancedFilterCount = computed(() =>
  [
    filters.sede_id,
    filters.facultad_id,
    filters.carrera_id,
    filters.tipo,
    filters.anio,
    filters.solo_con_pdf ? "1" : "",
  ].filter((value) => String(value || "").trim()).length
);


const pageCount = computed(() => {
  const value = Math.ceil(Number(total.value || 0) / PAGE_SIZE);
  return Math.max(1, value || 1);
});

const hasNonStateFilters = computed(() =>
  Boolean(
    String(filters.q || "").trim() ||
      String(filters.sede_id || "").trim() ||
      String(filters.facultad_id || "").trim() ||
      String(filters.carrera_id || "").trim() ||
      String(filters.tipo || "").trim() ||
      String(filters.anio || "").trim() ||
      filters.solo_con_pdf
  )
);

const currentStateTitle = computed(() => {
  const titles = {
    [ESTADO_PUBLICACION.EN_REVISION]: "Pendientes de revisión",
    [ESTADO_PUBLICACION.OBSERVADA]: "Publicaciones observadas",
    [ESTADO_PUBLICACION.APROBADA]: "Publicaciones aprobadas",
    [ESTADO_PUBLICACION.RECHAZADA]: "Publicaciones rechazadas",
  };

  return titles[filters.estado] || "Todas las publicaciones";
});

const currentStateHelp = computed(() => {
  const help = {
    [ESTADO_PUBLICACION.EN_REVISION]:
      "Publicaciones que esperan ser revisadas.",
    [ESTADO_PUBLICACION.OBSERVADA]:
      "Publicaciones devueltas al autor para que realice correcciones.",
    [ESTADO_PUBLICACION.APROBADA]:
      "Publicaciones que ya fueron aprobadas.",
    [ESTADO_PUBLICACION.RECHAZADA]:
      "Publicaciones que fueron rechazadas.",
  };

  return (
    help[filters.estado] ||
    "Consulte todas las publicaciones revisadas o pendientes de revisión."
  );
});

const resultsCountLabel = computed(() => {
  const value = Number(total.value || 0);

  if (value === 1) {
    return "1 publicación";
  }

  return `${numberLabel(value)} publicaciones`;
});

const emptyTitle = computed(() => {
  const titles = {
    [ESTADO_PUBLICACION.EN_REVISION]: "No hay publicaciones pendientes",
    [ESTADO_PUBLICACION.OBSERVADA]: "No hay publicaciones observadas",
    [ESTADO_PUBLICACION.APROBADA]: "No hay publicaciones aprobadas",
    [ESTADO_PUBLICACION.RECHAZADA]: "No hay publicaciones rechazadas",
  };

  return titles[filters.estado] || "No se encontraron publicaciones";
});

const emptyHelp = computed(() => {
  if (hasNonStateFilters.value) {
    return "No hay coincidencias con los filtros aplicados. Modifíquelos o límpielos para ampliar la consulta.";
  }

  if (filters.estado === ESTADO_PUBLICACION.EN_REVISION) {
    return "No hay publicaciones esperando revisión.";
  }

  return "No existen publicaciones registradas en este estado.";
});


function normalizeInitialState(value) {
  const raw = String(value ?? "").trim().toLowerCase();

  if (raw === "all" || raw === "todas" || raw === "todos") {
    return "";
  }

  const state = normalizarEstadoPublicacion(value);

  if (state && VALID_REVIEW_STATES.has(state)) {
    return state;
  }

  return ESTADO_PUBLICACION.EN_REVISION;
}

function normalizeQueryId(value) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? String(parsed) : "";
}

function normalizeYear(value) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed >= 1900 && parsed <= 2100
    ? String(parsed)
    : "";
}

function normalizePage(value) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

function normalizeQueryBoolean(value) {
  return [true, 1, "1", "true", "yes", "on"].includes(value);
}

function normalizeRows(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function selectorLabel(item) {
  return String(
    item?.nombre ||
      item?.name ||
      item?.label ||
      item?.descripcion ||
      `Registro ${item?.id || ""}`
  ).trim();
}

function numberLabel(value) {
  const parsed = Number(value || 0);
  return Number.isFinite(parsed)
    ? new Intl.NumberFormat("es-EC").format(parsed)
    : "0";
}

function stateCount(state) {
  if (!state) {
    return Number(indicators.value?.total_publicaciones || 0);
  }

  return Number(indicators.value?.[state] || 0);
}

function publicationId(item) {
  const parsed = Number(item?.id || item?.publicacion_id || 0);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 0;
}

function reviewState(item) {
  return normalizarEstadoPublicacion(item?.estado || item?.status || "");
}

function reviewStateLabel(item) {
  return (
    String(item?.estado_label || "").trim() ||
    estadoPublicacionLabel(reviewState(item)) ||
    "Sin estado"
  );
}

function reviewStateTone(item) {
  return estadoPublicacionTone(reviewState(item)) || "neutral";
}

function reviewActionLabel(item) {
  const state = reviewState(item);

  if (state === ESTADO_PUBLICACION.EN_REVISION) {
    return "Revisar";
  }

  if (state === ESTADO_PUBLICACION.OBSERVADA) {
    return "Ver correcciones";
  }

  return "Ver publicación";
}

function reviewTitle(item) {
  return String(
    item?.titulo ||
      item?.nombre ||
      item?.nombre_articulo ||
      item?.nombre_ponencia ||
      item?.nombre_libro ||
      item?.nombre_capitulo ||
      "Publicación sin título"
  ).trim();
}

function reviewPublicationType(item) {
  return String(
    item?.tipo_publicacion_final_label ||
      item?.tipo_label ||
      item?.tipo_nombre ||
      item?.tipo ||
      "Publicación"
  ).trim();
}

function reviewAuthor(item) {
  const firstAuthor = Array.isArray(item?.autores) ? item.autores[0] : null;

  return String(
    item?.autor_principal ||
      item?.autor_principal_nombre ||
      firstAuthor?.autor_nombre ||
      firstAuthor?.nombre_completo ||
      firstAuthor?.nombre ||
      item?.usuario_creador_nombre ||
      item?.usuario_creador_email ||
      "Autor no informado"
  ).trim();
}

function reviewAcademicContext(item) {
  const parts = [
    item?.sede || item?.sede_nombre,
    item?.facultad || item?.facultad_nombre,
    item?.carrera || item?.carrera_nombre,
  ]
    .map((value) => String(value || "").trim())
    .filter(Boolean);

  return parts.length ? parts.join(" · ") : "Información académica no registrada";
}

function reviewProject(item) {
  return String(
    item?.proyecto ||
      item?.proyecto_nombre ||
      "Sin proyecto"
  ).trim();
}

function reviewPeriod(item) {
  const year = Number(item?.anio_publicacion ?? item?.anio ?? 0);
  const month = Number(item?.mes_publicacion ?? item?.mes ?? 0);
  const monthLabel = String(item?.mes_publicacion_label || "").trim();

  const months = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
  };

  const resolvedMonth = monthLabel || months[month] || "";
  const hasYear = Number.isInteger(year) && year > 0;

  if (hasYear && resolvedMonth) return `${resolvedMonth} de ${year}`;
  if (hasYear) return String(year);
  if (resolvedMonth) return resolvedMonth;
  return "Sin período";
}

function reviewHasPdf(item) {
  return Boolean(
    item?.tiene_pdf ||
      item?.has_pdf ||
      item?.hasPdf ||
      item?.tiene_pdf_principal ||
      item?.archivo_pdf ||
      item?.pdf_url
  );
}

function reviewUpdatedAt(item) {
  return (
    item?.updated_at ||
    item?.fecha_actualizacion ||
    item?.created_at ||
    item?.fecha_creacion ||
    null
  );
}

function formatDateTime(value) {
  if (!value) return "Sin fecha";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sin fecha";

  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}


function normalizeError(
  error,
  fallback = "No se pudo completar la acción."
) {
  const status = Number(error?.response?.status || 0);
  const payload = error?.response?.data;

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para realizar esta acción.";
  }

  if (status === 404) {
    return "No se encontró la información solicitada.";
  }

  const direct =
    payload && typeof payload === "object"
      ? [
          payload.detail,
          payload.message,
          payload.mensaje,
          payload.error,
        ].find((value) => typeof value === "string" && value.trim())
      : "";

  const candidate = String(
    direct ||
      (typeof payload === "string" ? payload : "") ||
      ""
  ).trim();

  const technicalPattern =
    /(traceback|exception|database|sql|backend|endpoint|jwt|token|serializer|queryset|http\s*\d{3}|internal server|stack|foreign key|constraint)/i;

  if (candidate && !technicalPattern.test(candidate)) {
    return candidate;
  }

  return fallback;
}

function buildListParams(page = currentPage.value) {
  return {
    q: filters.q || undefined,
    estado: filters.estado || undefined,
    sede_id: filters.sede_id || undefined,
    facultad_id: filters.facultad_id || undefined,
    carrera_id: filters.carrera_id || undefined,
    tipo: filters.tipo || undefined,
    anio: filters.anio || undefined,
    solo_con_pdf: filters.solo_con_pdf ? true : undefined,
    ordering: "updated_desc",
    page,
    page_size: PAGE_SIZE,
  };
}

function buildDashboardParams() {
  return {
    sede: filters.sede_id || undefined,
    facultad: filters.facultad_id || undefined,
    carrera: filters.carrera_id || undefined,
    tipo: filters.tipo || undefined,
    anio: filters.anio || undefined,
    top: 5,
  };
}

async function syncRouteQuery() {
  const query = {
    ...route.query,
    estado: filters.estado || "all",
    q: filters.q || undefined,
    pagina: currentPage.value > 1 ? String(currentPage.value) : undefined,
    sede_id: filters.sede_id || undefined,
    facultad_id: filters.facultad_id || undefined,
    carrera_id: filters.carrera_id || undefined,
    tipo: filters.tipo || undefined,
    anio: filters.anio || undefined,
    solo_con_pdf: filters.solo_con_pdf ? "1" : undefined,
  };

  Object.keys(query).forEach((key) => {
    if (query[key] === undefined || query[key] === null || query[key] === "") {
      delete query[key];
    }
  });

  await router.replace({
    name: "AdminRevisionPublicaciones",
    query,
  });
}

async function loadCarreras() {
  careersController?.abort?.();
  const controller = new AbortController();
  careersController = controller;
  carrerasLoading.value = true;

  try {
    const data = await getAdminCarreras({
      sedeId: filters.sede_id || null,
      facultadId: filters.facultad_id || null,
    });

    if (careersController !== controller) return;

    carreras.value = normalizeRows(data);

    if (
      filters.carrera_id &&
      !carreras.value.some(
        (item) => Number(item?.id) === Number(filters.carrera_id)
      )
    ) {
      filters.carrera_id = "";
    }
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") {
      return;
    }

    console.error("Error cargando carreras de revisión:", error);
    carreras.value = [];
    filters.carrera_id = "";
  } finally {
    if (careersController === controller) {
      careersController = null;
      carrerasLoading.value = false;
    }
  }
}

async function loadCatalogs() {
  catalogLoading.value = true;

  try {
    const [sitesData, facultiesData] = await Promise.all([
      getAdminSedes(),
      getAdminFacultades(),
    ]);

    sedes.value = normalizeRows(sitesData);
    facultades.value = normalizeRows(facultiesData);

    await loadCarreras();
  } catch (error) {
    console.error("Error cargando catálogos de revisión:", error);
    sedes.value = [];
    facultades.value = [];
    carreras.value = [];
  } finally {
    catalogLoading.value = false;
  }
}

async function loadDashboardSummary() {
  dashboardController?.abort?.();
  const controller = new AbortController();
  dashboardController = controller;
  dashboardLoading.value = true;

  try {
    const data = await obtenerDashboardGestion(
      buildDashboardParams(),
      { signal: controller.signal }
    );

    if (dashboardController !== controller) return;
    dashboard.value = data || null;
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") {
      return;
    }

    console.error("Error cargando resumen de revisión:", error);
  } finally {
    if (dashboardController === controller) {
      dashboardController = null;
      dashboardLoading.value = false;
    }
  }
}

function scheduleLoadingFeedback() {
  if (loadingFeedbackTimer) {
    clearTimeout(loadingFeedbackTimer);
  }

  loadingFeedbackVisible.value = false;
  loadingFeedbackTimer = setTimeout(() => {
    if (loading.value) {
      loadingFeedbackVisible.value = true;
    }
  }, 220);
}

function clearLoadingFeedback() {
  if (loadingFeedbackTimer) {
    clearTimeout(loadingFeedbackTimer);
    loadingFeedbackTimer = null;
  }

  loadingFeedbackVisible.value = false;
}

async function loadItems(page = currentPage.value) {
  const requestId = ++listRequestSerial;
  const hadLoadedData = hasLoaded.value;

  loading.value = true;
  errorMessage.value = "";
  scheduleLoadingFeedback();

  try {
    const response = await listarAdminPublicaciones(buildListParams(page));

    if (requestId !== listRequestSerial) return;

    items.value = normalizeRows(response);
    total.value = Number(response?.count ?? items.value.length);
    currentPage.value = page;
    hasLoaded.value = true;
  } catch (error) {
    if (requestId !== listRequestSerial) return;

    console.error("Error cargando publicaciones para revisión:", error);

    if (!hadLoadedData) {
      items.value = [];
      total.value = 0;
    }

    errorMessage.value = normalizeError(
      error,
      hadLoadedData
        ? "No se pudo actualizar la lista. Se mantienen los últimos datos disponibles."
        : "No se pudieron cargar las publicaciones."
    );
  } finally {
    if (requestId === listRequestSerial) {
      loading.value = false;
      clearLoadingFeedback();
    }
  }
}

async function refreshAll() {

  await Promise.all([
    loadItems(currentPage.value),
    loadDashboardSummary(),
  ]);
}

async function applyFilters() {
  currentPage.value = 1;
  await syncRouteQuery();

  await Promise.all([
    loadItems(currentPage.value),
    loadDashboardSummary(),
  ]);
}

async function resetFilters() {
  filters.q = "";
  filters.sede_id = "";
  filters.facultad_id = "";
  filters.carrera_id = "";
  filters.tipo = "";
  filters.anio = "";
  filters.solo_con_pdf = false;
  currentPage.value = 1;

  await loadCarreras();
  await syncRouteQuery();

  await Promise.all([
    loadItems(1),
    loadDashboardSummary(),
  ]);
}

async function handleAcademicFilterChange() {
  filters.carrera_id = "";
  await loadCarreras();
}

async function setState(value) {
  if (!VALID_REVIEW_STATES.has(value)) return;

  filters.estado = value;
  currentPage.value = 1;
  errorMessage.value = "";

  await syncRouteQuery();
  await loadItems(1);
}

function handleTabsKeydown(event) {
  if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
    return;
  }

  const tablist = event.currentTarget;
  const current = event.target?.closest?.('[role="tab"]');

  if (!(tablist instanceof HTMLElement) || !(current instanceof HTMLElement)) {
    return;
  }

  const availableTabs = Array.from(
    tablist.querySelectorAll('[role="tab"]:not(:disabled)')
  );

  if (!availableTabs.length) return;

  const currentIndex = Math.max(0, availableTabs.indexOf(current));
  let targetIndex = currentIndex;

  if (event.key === "Home") {
    targetIndex = 0;
  } else if (event.key === "End") {
    targetIndex = availableTabs.length - 1;
  } else if (event.key === "ArrowRight") {
    targetIndex = (currentIndex + 1) % availableTabs.length;
  } else {
    targetIndex = (currentIndex - 1 + availableTabs.length) % availableTabs.length;
  }

  event.preventDefault();

  const target = availableTabs[targetIndex];
  target?.focus();
  target?.click();
}

async function changePage(page) {
  const target = Number(page);

  if (
    !Number.isInteger(target) ||
    target < 1 ||
    target > pageCount.value ||
    target === currentPage.value
  ) {
    return;
  }

  await loadItems(target);
  await syncRouteQuery();

  if (typeof window !== "undefined") {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function goToPanel() {
  router.push({ name: "AdminPanel" });
}

function goToPublicationDetail(item) {
  const id = publicationId(item);
  if (!id) return;

  const currentIndex = items.value.findIndex(
    (row) => publicationId(row) === id
  );

  const nextId =
    currentIndex >= 0 && currentIndex < items.value.length - 1
      ? publicationId(items.value[currentIndex + 1])
      : 0;

  router.push({
    name: "AdminRevisionDetalle",
    params: { id },
    query: {
      // Conservamos el contexto para volver a la misma consulta.
      estado: filters.estado || "all",
      sede_id: filters.sede_id || undefined,
      facultad_id: filters.facultad_id || undefined,
      carrera_id: filters.carrera_id || undefined,
      tipo: filters.tipo || undefined,
      anio: filters.anio || undefined,
      solo_con_pdf: filters.solo_con_pdf ? "1" : undefined,
      q: filters.q || undefined,
      pagina: currentPage.value > 1 ? String(currentPage.value) : undefined,
      next_id: nextId ? String(nextId) : undefined,
    },
  });
}


watch(
  () => route.query?.estado,
  async (value) => {
    const normalized = normalizeInitialState(value);

    if (normalized === filters.estado) return;

    filters.estado = normalized;
    currentPage.value = 1;
    await loadItems(1);
  }
);

onMounted(async () => {
  await loadCatalogs();

  await Promise.all([
    loadItems(1),
    loadDashboardSummary(),
  ]);
});

onBeforeUnmount(() => {
  listRequestSerial += 1;
  clearLoadingFeedback();
  dashboardController?.abort?.();
  careersController?.abort?.();
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-revision-publicaciones.css"></style>
<style src="./admin-revision-stage3.css"></style>
