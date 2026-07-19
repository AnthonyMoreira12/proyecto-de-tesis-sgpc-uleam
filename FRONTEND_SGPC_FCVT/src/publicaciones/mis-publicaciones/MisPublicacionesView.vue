<template>
  <div class="mispub" :data-tipo="tipoThemeCode">
    <div class="mispub__wrap">
      <!-- =====================================================
        ENCABEZADO
      ====================================================== -->
      <header
        class="mispub__hero page-stage page-stage-1"
        aria-label="Mis publicaciones"
      >
        <div class="hero__copy">
          <span class="hero__eyebrow">
            Producción científica
          </span>

          <h1 class="hero__title">
            Mis publicaciones
          </h1>

          <p class="hero__subtitle">
            Consulte y filtre las publicaciones científicas vinculadas a su
            perfil académico.
          </p>

          <div
            class="hero__pills"
            aria-label="Resumen de publicaciones"
          >
            <span class="pill">
              Total:
              <strong>{{ publicaciones.length }}</strong>
            </span>

            <span class="pill">
              Resultados:
              <strong>{{ publicacionesFiltradas.length }}</strong>
            </span>

            <span
              v-if="activeFiltersCount"
              class="pill pill--active"
            >
              Filtros:
              <strong>{{ activeFiltersCount }}</strong>
            </span>
          </div>
        </div>

        <div
          class="hero__tools"
          aria-label="Herramientas de consulta"
        >
          <label
            class="search search--navbar"
            aria-label="Buscar publicación"
          >
            <span
              class="search__lead"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                class="search__svg"
                aria-hidden="true"
              >
                <path
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 0 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </span>

            <input
              ref="searchEl"
              v-model="q"
              class="search__input"
              type="search"
              inputmode="search"
              autocomplete="off"
              placeholder="Buscar por título, tipo, proyecto, facultad o carrera…"
            />

            <button
              type="button"
              class="search__action"
              :aria-label="q ? 'Limpiar búsqueda' : 'Enfocar búsqueda'"
              @click="handleSearchAction"
            >
              <span
                v-if="q"
                class="search__x"
                aria-hidden="true"
              >
                ×
              </span>

              <svg
                v-else
                viewBox="0 0 24 24"
                class="search__svg"
                aria-hidden="true"
              >
                <path
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 1 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </label>

          <div
            class="view__switch"
            role="tablist"
            aria-label="Vista de resultados"
          >
            <button
              type="button"
              class="view__btn"
              :class="{ activo: vista === 'cards' }"
              role="tab"
              :aria-selected="vista === 'cards'"
              @click="vista = 'cards'"
            >
              Tarjetas
            </button>

            <button
              type="button"
              class="view__btn"
              :class="{ activo: vista === 'tabla' }"
              role="tab"
              :aria-selected="vista === 'tabla'"
              @click="vista = 'tabla'"
            >
              Tabla
            </button>
          </div>
        </div>
      </header>

      <!-- =====================================================
        FILTROS
      ====================================================== -->
      <section
        class="mispub__filters page-stage page-stage-2"
        aria-label="Filtros de publicaciones"
      >
        <div class="filters__head">
          <div class="filters__titlewrap">
            <h2 class="filters__title">
              Filtros
            </h2>
          </div>

          <button
            type="button"
            class="filters__clear"
            :class="{ 'is-hidden': !canClearFilters }"
            :disabled="!canClearFilters"
            @click="clearAllFilters"
          >
            Limpiar filtros
          </button>
        </div>

        <!-- Tipos de publicación -->
        <div
          class="filters__row"
          aria-label="Filtrar por tipo de publicación"
        >
          <button
            v-for="tipo in TIPOS_LIST"
            :key="tipo.value"
            type="button"
            class="chip"
            :class="{ activo: filtro.value === tipo.value }"
            :aria-pressed="filtro.value === tipo.value"
            @click="cambiarFiltro(tipo)"
          >
            <span
              class="chip__dot"
              :data-tipo="tipo.value"
              aria-hidden="true"
            ></span>

            <span class="chip__label">
              {{ tipo.label }}
            </span>

            <span
              class="chip__count"
              aria-label="Cantidad"
            >
              {{ countByType(tipo.value) }}
            </span>
          </button>
        </div>

        <!-- Filtros de año -->
        <div class="filters__dateGrid">
          <div class="filter-field filter-field--full">
            <label
              class="filter-label"
              for="mispub-anio"
            >
              Año exacto
            </label>

            <select
              id="mispub-anio"
              v-model="filtroAnio"
              class="filter-select"
              :disabled="Boolean(filtroAnioDesde || filtroAnioHasta)"
            >
              <option value="">
                Todos los años
              </option>

              <option
                v-for="anio in añosDisponibles"
                :key="`exact-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>

          <div class="filter-field">
            <label
              class="filter-label"
              for="mispub-anio-desde"
            >
              Desde
            </label>

            <select
              id="mispub-anio-desde"
              v-model="filtroAnioDesde"
              class="filter-select"
              :disabled="Boolean(filtroAnio)"
            >
              <option value="">
                Sin mínimo
              </option>

              <option
                v-for="anio in añosDisponibles"
                :key="`desde-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>

          <div class="filter-field">
            <label
              class="filter-label"
              for="mispub-anio-hasta"
            >
              Hasta
            </label>

            <select
              id="mispub-anio-hasta"
              v-model="filtroAnioHasta"
              class="filter-select"
              :disabled="Boolean(filtroAnio)"
            >
              <option value="">
                Actual
              </option>

              <option
                v-for="anio in añosDisponibles"
                :key="`hasta-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>
        </div>
      </section>

      <!-- =====================================================
        ESTADOS
      ====================================================== -->
      <section
        class="mispub__state page-stage page-stage-3"
        aria-live="polite"
        aria-atomic="true"
      >
        <div
          v-if="loading"
          class="state state--loading"
        >
          <span
            class="dot"
            aria-hidden="true"
          ></span>

          <span>
            Cargando publicaciones…
          </span>
        </div>

        <div
          v-else-if="publicacionesFiltradas.length === 0"
          class="state state--empty"
          :class="{ 'state--error': Boolean(errorMsg) }"
          :role="errorMsg ? 'alert' : 'status'"
        >
          {{ emptyMessage }}
        </div>
      </section>

      <!-- =====================================================
        RESULTADOS
      ====================================================== -->
      <section
        v-if="!loading && publicacionesFiltradas.length > 0"
        class="mispub__results page-stage page-stage-3"
        aria-label="Resultados de publicaciones"
      >
        <!-- Vista de tarjetas -->
        <div
          v-if="vista === 'cards'"
          class="cards page-stagger page-stagger--mid"
        >
          <article
            v-for="pub in publicacionesFiltradas"
            :key="pub.id"
            class="card"
            :data-tipo="resolveType(pub)"
            tabindex="0"
            role="button"
            :aria-label="`Ver detalle de ${pub.titulo || 'publicación'}`"
            @click="verDetalles(pub.id)"
            @keydown.enter.prevent="verDetalles(pub.id)"
            @keydown.space.prevent="verDetalles(pub.id)"
          >
            <div class="card__head">
              <span
                class="type__badge"
                :data-tipo="resolveType(pub)"
              >
                {{ resolveLabel(pub) }}
              </span>

              <time
                class="date"
                :datetime="pub.fecha_publicacion || ''"
              >
                {{ formatFecha(pub.fecha_publicacion) }}
              </time>
            </div>

            <div class="card__body">
              <h3
                class="card__title"
                :title="pub.titulo || 'Sin título'"
              >
                {{ pub.titulo || "Sin título" }}
              </h3>

              <p
                v-if="pub.autor"
                class="card__meta card__meta--soft"
                :title="pub.autor"
              >
                {{ pub.autor }}
              </p>

              <p
                v-if="pub.proyecto"
                class="card__meta"
                :title="pub.proyecto"
              >
                {{ pub.proyecto }}
              </p>

              <p
                class="card__meta"
                :title="buildAcademicMeta(pub)"
              >
                {{ buildAcademicMeta(pub) }}
              </p>
            </div>

            <div class="card__footer">
              <span class="card__action">
                Ver detalle
              </span>
            </div>
          </article>
        </div>

        <!-- Vista de tabla -->
        <div
          v-else
          class="table-wrap"
          role="region"
          aria-label="Tabla detallada de publicaciones"
          tabindex="0"
        >
          <table class="table">
            <thead>
              <tr>
                <th scope="col">
                  Tipo
                </th>

                <th scope="col">
                  Título
                </th>

                <th scope="col">
                  Proyecto
                </th>

                <th scope="col">
                  Fecha
                </th>

                <th scope="col">
                  Facultad
                </th>

                <th scope="col">
                  Carrera
                </th>

                <th
                  scope="col"
                  class="th-actions"
                >
                  Opciones
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="pub in publicacionesFiltradas"
                :key="pub.id"
              >
                <td class="td-strong">
                  <span
                    class="mini-badge"
                    :data-tipo="resolveType(pub)"
                  >
                    {{ resolveLabel(pub) }}
                  </span>
                </td>

                <td
                  class="td-title"
                  :title="pub.titulo || 'Sin título'"
                >
                  {{ pub.titulo || "Sin título" }}
                </td>

                <td :title="pub.proyecto || 'Sin proyecto'">
                  {{ pub.proyecto || "—" }}
                </td>

                <td>
                  {{ formatFecha(pub.fecha_publicacion) }}
                </td>

                <td :title="pub.facultad || 'Sin facultad'">
                  {{ pub.facultad || "—" }}
                </td>

                <td :title="pub.carrera || 'Sin carrera'">
                  {{ pub.carrera || "—" }}
                </td>

                <td class="td-actions">
                  <button
                    class="btn-mini"
                    type="button"
                    :aria-label="`Ver detalle de ${pub.titulo || 'publicación'}`"
                    @click="verDetalles(pub.id)"
                  >
                    Ver
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { useRouter } from "vue-router";

import api from "../../scripts/api/axios";

import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

/* ============================================================
  NAVEGACIÓN
============================================================ */

const router = useRouter();

/* ============================================================
  TIPOS DE PUBLICACIÓN
============================================================ */

const TIPOS = {
  ALL: {
    label: "Todos",
    value: "ALL",
  },

  AAI: {
    label: PUBLICACION_TIPOS.AAI.label,
    value: PUBLICACION_TIPOS.AAI.codigo,
  },

  AR: {
    label: PUBLICACION_TIPOS.AR.label,
    value: PUBLICACION_TIPOS.AR.codigo,
  },

  PON: {
    label: PUBLICACION_TIPOS.PON.label,
    value: PUBLICACION_TIPOS.PON.codigo,
  },

  CAP: {
    label: PUBLICACION_TIPOS.CAP.label,
    value: PUBLICACION_TIPOS.CAP.codigo,
  },

  LIB: {
    label: PUBLICACION_TIPOS.LIB.label,
    value: PUBLICACION_TIPOS.LIB.codigo,
  },
};

const TIPOS_LIST = [
  TIPOS.ALL,
  TIPOS.AAI,
  TIPOS.AR,
  TIPOS.PON,
  TIPOS.CAP,
  TIPOS.LIB,
];

/* ============================================================
  ESTADO PRINCIPAL
============================================================ */

const publicaciones = ref([]);
const loading = ref(true);
const errorMsg = ref("");

/* ============================================================
  ESTADO DE LA INTERFAZ
============================================================ */

const vista = ref("cards");

const q = ref("");
const searchEl = ref(null);

const filtro = ref(TIPOS.ALL);

const filtroAnio = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");

/* ============================================================
  NORMALIZACIÓN DE RESPUESTAS
============================================================ */

function extractArray(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  if (Array.isArray(payload?.publicaciones)) {
    return payload.publicaciones;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  return [];
}

function extractErrorMessage(
  error,
  fallback = "No se pudieron cargar las publicaciones."
) {
  const responseData = error?.response?.data;

  const detail =
    responseData?.detail ||
    responseData?.message ||
    responseData?.error ||
    error?.message;

  if (Array.isArray(detail)) {
    return detail.join(", ");
  }

  if (detail && typeof detail === "object") {
    return Object.values(detail)
      .flat()
      .map((value) => String(value))
      .join(" ");
  }

  return String(detail || fallback);
}

/* ============================================================
  NORMALIZACIÓN DE TEXTO Y FECHA
============================================================ */

function normalizeText(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function extractYear(fecha) {
  const raw = String(fecha || "").substring(0, 4);

  return /^\d{4}$/.test(raw)
    ? Number(raw)
    : null;
}

function formatFecha(fecha) {
  if (!fecha) {
    return "Sin fecha";
  }

  const normalized = String(fecha).slice(0, 10);
  const date = new Date(`${normalized}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return "Sin fecha";
  }

  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

/* ============================================================
  METADATOS DE PUBLICACIÓN
============================================================ */

function getResolvedMeta(item) {
  return (
    item?.__tipoMeta ||
    getTipoPublicacionMetaFromItem(item)
  );
}

function resolveType(item) {
  const meta = getResolvedMeta(item);

  return meta?.codigo || "OTRO";
}

function resolveLabel(item) {
  const meta = getResolvedMeta(item);

  if (meta?.codigo && meta.codigo !== "OTRO") {
    return meta.label;
  }

  return (
    String(
      item?.tipo_publicacion_final_label ||
        item?.tipo_publicacion_final ||
        item?.tipo ||
        "Publicación"
    ).trim() || "Publicación"
  );
}

function buildAcademicMeta(pub) {
  const facultad = String(pub?.facultad || "").trim();
  const carrera = String(pub?.carrera || "").trim();

  if (facultad && carrera) {
    return `${facultad} · ${carrera}`;
  }

  if (facultad) {
    return facultad;
  }

  if (carrera) {
    return carrera;
  }

  return "Sin ubicación académica";
}

/* ============================================================
  COMPUTEDS
============================================================ */

const añosDisponibles = computed(() => {
  const years = publicaciones.value
    .map((item) => extractYear(item?.fecha_publicacion))
    .filter((value) => Number.isInteger(value));

  return [...new Set(years)].sort((a, b) => b - a);
});

const tipoThemeCode = computed(() => {
  return filtro.value?.value || "ALL";
});

const activeFiltersCount = computed(() => {
  let total = 0;

  if (filtro.value?.value !== "ALL") {
    total += 1;
  }

  if (normalizeText(q.value)) {
    total += 1;
  }

  if (filtroAnio.value) {
    total += 1;
  }

  if (filtroAnioDesde.value) {
    total += 1;
  }

  if (filtroAnioHasta.value) {
    total += 1;
  }

  return total;
});

const canClearFilters = computed(() => {
  return (
    filtro.value?.value !== "ALL" ||
    normalizeText(q.value).length > 0 ||
    Boolean(filtroAnio.value) ||
    Boolean(filtroAnioDesde.value) ||
    Boolean(filtroAnioHasta.value)
  );
});

const publicacionesFiltradas = computed(() => {
  const tipoSeleccionado = filtro.value?.value || "ALL";

  const base =
    tipoSeleccionado === "ALL"
      ? publicaciones.value
      : publicaciones.value.filter(
          (item) => resolveType(item) === tipoSeleccionado
        );

  const term = normalizeText(q.value);

  const anioExacto = filtroAnio.value
    ? Number(filtroAnio.value)
    : null;

  const anioDesde = filtroAnioDesde.value
    ? Number(filtroAnioDesde.value)
    : null;

  const anioHasta = filtroAnioHasta.value
    ? Number(filtroAnioHasta.value)
    : null;

  const minYear =
    !anioExacto && anioDesde && anioHasta
      ? Math.min(anioDesde, anioHasta)
      : anioDesde;

  const maxYear =
    !anioExacto && anioDesde && anioHasta
      ? Math.max(anioDesde, anioHasta)
      : anioHasta;

  return base.filter((item) => {
    const haystack = [
      item?.titulo,
      item?.tipo,
      item?.tipo_codigo,
      item?.tipo_publicacion_final,
      item?.tipo_publicacion_final_label,
      item?.proyecto,
      item?.facultad,
      item?.carrera,
      item?.fecha_publicacion,
      item?.autor,
      resolveLabel(item),
      resolveType(item),
      buildAcademicMeta(item),
    ]
      .map((entry) => normalizeText(entry))
      .join(" ");

    const cumpleTexto = term
      ? haystack.includes(term)
      : true;

    const year = extractYear(item?.fecha_publicacion);

    let cumpleFecha = true;

    if (anioExacto) {
      cumpleFecha = year === anioExacto;
    } else {
      if (minYear && (!year || year < minYear)) {
        cumpleFecha = false;
      }

      if (maxYear && (!year || year > maxYear)) {
        cumpleFecha = false;
      }
    }

    return cumpleTexto && cumpleFecha;
  });
});

const emptyMessage = computed(() => {
  if (errorMsg.value) {
    return errorMsg.value;
  }

  const hasSearch = normalizeText(q.value).length > 0;

  const hasFilter =
    filtro.value?.value !== "ALL" ||
    Boolean(filtroAnio.value) ||
    Boolean(filtroAnioDesde.value) ||
    Boolean(filtroAnioHasta.value);

  if (hasSearch && hasFilter) {
    return "No se encontraron publicaciones con la búsqueda y los filtros seleccionados.";
  }

  if (hasSearch) {
    return "No se encontraron publicaciones para la búsqueda ingresada.";
  }

  if (hasFilter) {
    return "No hay publicaciones para los filtros seleccionados.";
  }

  return "Aún no tienes publicaciones registradas.";
});

/* ============================================================
  FILTROS
============================================================ */

function cambiarFiltro(tipo) {
  filtro.value = tipo;
}

function clearAllFilters() {
  filtro.value = TIPOS.ALL;
  q.value = "";
  filtroAnio.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";
}

function countByType(typeValue) {
  if (typeValue === "ALL") {
    return publicaciones.value.length;
  }

  return publicaciones.value.filter(
    (item) => resolveType(item) === typeValue
  ).length;
}

/* ============================================================
  BUSCADOR
============================================================ */

function handleSearchAction() {
  if (q.value) {
    q.value = "";
    searchEl.value?.focus();
    return;
  }

  searchEl.value?.focus();
}

/* ============================================================
  NAVEGACIÓN
============================================================ */

function verDetalles(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}`,
  });
}

/* ============================================================
  ATAJOS DE TECLADO
============================================================ */

function onKey(event) {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform.toLowerCase().includes("mac");

  const key = String(event.key || "").toLowerCase();

  const shortcutSearch =
    (isMac && event.metaKey && key === "k") ||
    (!isMac && event.ctrlKey && key === "k");

  if (shortcutSearch) {
    event.preventDefault();
    searchEl.value?.focus();
  }

  if (event.key === "Escape" && q.value) {
    q.value = "";
  }
}

/* ============================================================
  WATCHERS
============================================================ */

watch(filtroAnio, (value) => {
  if (!value) {
    return;
  }

  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";
});

watch(
  [filtroAnioDesde, filtroAnioHasta],
  ([desde, hasta]) => {
    if (desde || hasta) {
      filtroAnio.value = "";
    }
  }
);

/* ============================================================
  CARGA DE PUBLICACIONES
============================================================ */

async function cargarPublicaciones() {
  loading.value = true;
  errorMsg.value = "";

  try {
    const response = await api.get("/publicaciones/mias/");

    publicaciones.value = extractArray(response.data).map((item) => ({
      ...item,
      __tipoMeta: getTipoPublicacionMetaFromItem(item),
    }));
  } catch (error) {
    console.error("Error cargando publicaciones:", error);

    publicaciones.value = [];

    errorMsg.value = extractErrorMessage(
      error,
      "No se pudieron cargar tus publicaciones."
    );
  } finally {
    loading.value = false;
  }
}

/* ============================================================
  CICLO DE VIDA
============================================================ */

onMounted(async () => {
  window.addEventListener("keydown", onKey);

  await cargarPublicaciones();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKey);
});
</script>

<style src="../listado-publicaciones/sgpc-listados-base.css"></style>
<style src="./mis-publicaciones.css"></style>