<template>
  <div
    class="mispub"
    :data-tipo="tipoThemeCode"
  >
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
            Consulte, filtre y gestione las publicaciones científicas
            vinculadas a su perfil académico.
          </p>

          <div
            class="hero__pills"
            aria-label="Resumen de publicaciones"
          >
            <span class="pill">
              Total:
              <strong>{{ totalPublicaciones }}</strong>
            </span>

            <span class="pill">
              Resultados:
              <strong>{{ totalResultados }}</strong>
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
              placeholder="Buscar por título, autor, tipo, proyecto, facultad o carrera…"
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
            role="group"
            aria-label="Vista de resultados"
          >
            <button
              type="button"
              class="view__btn"
              :class="{ activo: vista === 'cards' }"
              :aria-pressed="vista === 'cards'"
              @click="vista = 'cards'"
            >
              Tarjetas
            </button>

            <button
              type="button"
              class="view__btn"
              :class="{ activo: vista === 'tabla' }"
              :aria-pressed="vista === 'tabla'"
              @click="vista = 'tabla'"
            >
              Tabla
            </button>
          </div>
        </div>
      </header>

      <!-- =====================================================
        FILTROS COMPACTOS
      ====================================================== -->

      <section
        class="mispub__filters page-stage page-stage-2"
        aria-label="Filtros de publicaciones"
      >
        <div class="filters__head">
          <div class="filters__titlewrap">
            <div class="filters__titleLine">
              <h2 class="filters__title">
                Filtros y ordenamiento
              </h2>

              <span
                v-if="activeFiltersCount"
                class="filters__activeBadge"
              >
                {{ activeFiltersCount }}
                {{ activeFiltersCount === 1 ? "activo" : "activos" }}
              </span>
            </div>

            <p class="filters__description">
              Refine los resultados sin perder de vista sus publicaciones.
            </p>
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

        <!-- ===================================================
          TIPO DE PUBLICACIÓN
        ==================================================== -->

        <div class="filters__group filters__group--types">
          <div class="filters__groupHead">
            <h3 class="filters__groupTitle">
              Tipo de publicación
            </h3>
          </div>

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
        </div>

        <!-- ===================================================
          FILTROS PRINCIPALES
        ==================================================== -->

        <div class="filters__group filters__group--primary">
          <div class="filters__groupHead">
            <h3 class="filters__groupTitle">
              Filtros principales
            </h3>

            <span class="filters__groupHint">
              Carrera y proyecto dependen de la selección anterior.
            </span>
          </div>

          <div class="filters__primaryGrid">
            <div class="filter-field filter-field--faculty">
              <label
                class="filter-label"
                for="mispub-facultad"
              >
                Facultad
              </label>

              <select
                id="mispub-facultad"
                v-model="filtroFacultad"
                class="filter-select"
                @change="onMainFacultadChange"
              >
                <option value="">
                  Todas las facultades
                </option>

                <option
                  v-for="facultad in facultades"
                  :key="`facultad-${facultad.id}`"
                  :value="String(facultad.id)"
                >
                  {{ getCatalogLabel(facultad) }}
                </option>
              </select>
            </div>

            <div class="filter-field filter-field--career">
              <label
                class="filter-label"
                for="mispub-carrera"
              >
                Carrera
              </label>

              <select
                id="mispub-carrera"
                v-model="filtroCarrera"
                class="filter-select"
                :disabled="!filtroFacultad"
                @change="onMainCarreraChange"
              >
                <option value="">
                  Todas las carreras
                </option>

                <option
                  v-for="carrera in carreras"
                  :key="`carrera-${carrera.id}`"
                  :value="String(carrera.id)"
                >
                  {{ getCatalogLabel(carrera) }}
                </option>
              </select>
            </div>

            <div class="filter-field filter-field--project">
              <label
                class="filter-label"
                for="mispub-proyecto"
              >
                Proyecto
              </label>

              <select
                id="mispub-proyecto"
                v-model="filtroProyecto"
                class="filter-select"
                :disabled="!filtroCarrera"
              >
                <option value="">
                  Todos los proyectos
                </option>

                <option
                  v-for="proyecto in proyectos"
                  :key="`proyecto-${proyecto.id}`"
                  :value="String(proyecto.id)"
                >
                  {{ getCatalogLabel(proyecto) }}
                </option>
              </select>
            </div>

            <div class="filter-field filter-field--year">
              <label
                class="filter-label"
                for="mispub-anio"
              >
                Año
              </label>

              <select
                id="mispub-anio"
                v-model="filtroAnio"
                class="filter-select"
                :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnioDesde || filtroAnioHasta)"
              >
                <option value="">
                  {{
                    loadingAnios
                      ? "Cargando años…"
                      : añosDisponibles.length
                        ? "Todos"
                        : "Sin años disponibles"
                  }}
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

            <div class="filter-field filter-field--advancedAction">
              <span class="filter-label">
                Opciones
              </span>

              <button
                type="button"
                class="filters__advancedButton"
                :class="{
                  'is-open': filtrosAvanzadosAbiertos,
                  'has-active': advancedFiltersCount > 0,
                }"
                :aria-expanded="filtrosAvanzadosAbiertos"
                aria-controls="mispub-advanced-filters"
                @click="filtrosAvanzadosAbiertos = !filtrosAvanzadosAbiertos"
              >
                <svg
                  viewBox="0 0 24 24"
                  class="filters__advancedIcon"
                  aria-hidden="true"
                >
                  <path
                    d="M4 6h16M7 12h10M10 18h4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.9"
                    stroke-linecap="round"
                  />
                </svg>

                <span class="filters__advancedLabel">
                  Más filtros
                </span>

                <span
                  v-if="advancedFiltersCount"
                  class="filters__advancedCount"
                  aria-label="Filtros avanzados activos"
                >
                  {{ advancedFiltersCount }}
                </span>

                <svg
                  viewBox="0 0 24 24"
                  class="filters__advancedChevron"
                  aria-hidden="true"
                >
                  <path
                    d="m7 10 5 5 5-5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- ===================================================
          FILTROS AVANZADOS PLEGABLES
        ==================================================== -->

        <Transition name="filters-advanced">
          <div
            v-if="filtrosAvanzadosAbiertos"
            id="mispub-advanced-filters"
            class="filters__group filters__group--advanced"
          >
            <div class="filters__groupHead">
              <h3 class="filters__groupTitle">
                Filtros avanzados
              </h3>

              <span class="filters__groupHint">
                Para el periodo use un año exacto o un rango, no ambos.
              </span>
            </div>

            <div class="filters__advancedGrid">
              <div class="filter-field">
                <label
                  class="filter-label"
                  for="mispub-origen"
                >
                  Origen
                </label>

                <select
                  id="mispub-origen"
                  v-model="filtroOrigen"
                  class="filter-select"
                >
                  <option
                    v-for="origen in ORIGENES_LIST"
                    :key="origen.value"
                    :value="origen.value"
                  >
                    {{ origen.label }}
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
                  :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
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
                  :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
                >
                  <option value="">
                    Sin máximo
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

              <div class="filter-field">
                <label
                  class="filter-label"
                  for="mispub-orden"
                >
                  Ordenar por
                </label>

                <select
                  id="mispub-orden"
                  v-model="orden"
                  class="filter-select"
                >
                  <option
                    v-for="option in ORDENES"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div class="filter-field filter-field--toggle">
                <span class="filter-label">
                  Disponibilidad
                </span>

                <label
                  class="filter-toggle filter-toggle--compact"
                  for="mispub-solo-pdf"
                >
                  <input
                    id="mispub-solo-pdf"
                    v-model="soloConPdf"
                    class="filter-toggle__input"
                    type="checkbox"
                  />

                  <span
                    class="filter-toggle__control"
                    aria-hidden="true"
                  >
                    <span class="filter-toggle__thumb"></span>
                  </span>

                  <span class="filter-toggle__content">
                    <strong class="filter-toggle__title">
                      Solo con PDF
                    </strong>

                    <span class="filter-toggle__description">
                      Archivo disponible
                    </span>
                  </span>
                </label>
              </div>
            </div>
          </div>
        </Transition>
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
          <span>
            {{ emptyMessage }}
          </span>

          <button
            v-if="errorMsg"
            type="button"
            class="btn-mini"
            @click="cargarPublicaciones({ forceLoading: true })"
          >
            Reintentar
          </button>

          <button
            v-else-if="canClearFilters"
            type="button"
            class="btn-mini"
            @click="clearAllFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </section>

      <section
        v-if="pdfErrorMsg"
        class="mispub__state page-stage page-stage-3"
        aria-live="polite"
      >
        <div
          class="state state--error"
          role="alert"
        >
          <span>
            {{ pdfErrorMsg }}
          </span>

          <button
            type="button"
            class="btn-mini"
            @click="pdfErrorMsg = ''"
          >
            Cerrar
          </button>
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
              <RouterLink
                class="card__titleLink"
                :to="`/publicacion/${pub.id}`"
                :aria-label="`Ver detalle de ${pub.titulo || 'publicación'}`"
              >
                <h3
                  class="card__title"
                  :title="pub.titulo || 'Sin título'"
                >
                  {{ pub.titulo || "Sin título" }}
                </h3>
              </RouterLink>

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

              <p
                v-if="resolveOrigenResumen(pub)"
                class="card__origin"
                :title="resolveOrigenResumen(pub)"
              >
                <strong>
                  Origen:
                </strong>

                {{ resolveOrigenResumen(pub) }}
              </p>
            </div>

            <div class="card__footer card__footer--actions">
              <button
                type="button"
                class="btn-mini"
                @click="verDetalles(pub.id)"
              >
                Ver
              </button>

              <button
                v-if="pub.puede_editar"
                type="button"
                class="btn-mini"
                @click="editarPublicacion(pub.id)"
              >
                Editar
              </button>

              <button
                v-if="hasPdf(pub)"
                type="button"
                class="btn-mini"
                :disabled="openingPdfId !== null"
                @click="abrirPdf(pub)"
              >
                {{
                  openingPdfId === pub.id
                    ? "Abriendo…"
                    : "PDF"
                }}
              </button>
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
                  Origen
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
                  <RouterLink
                    class="table__titleLink"
                    :to="`/publicacion/${pub.id}`"
                  >
                    {{ pub.titulo || "Sin título" }}
                  </RouterLink>
                </td>

                <td
                  :title="resolveOrigenResumen(pub) || 'Sin origen específico'"
                >
                  {{ resolveOrigenResumen(pub) || "—" }}
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
                  <div class="table__actions">
                    <button
                      class="btn-mini"
                      type="button"
                      :aria-label="`Ver detalle de ${pub.titulo || 'publicación'}`"
                      @click="verDetalles(pub.id)"
                    >
                      Ver
                    </button>

                    <button
                      v-if="pub.puede_editar"
                      class="btn-mini"
                      type="button"
                      :aria-label="`Editar ${pub.titulo || 'publicación'}`"
                      @click="editarPublicacion(pub.id)"
                    >
                      Editar
                    </button>

                    <button
                      v-if="hasPdf(pub)"
                      class="btn-mini"
                      type="button"
                      :disabled="openingPdfId !== null"
                      :aria-label="`Abrir PDF de ${pub.titulo || 'publicación'}`"
                      @click="abrirPdf(pub)"
                    >
                      {{
                        openingPdfId === pub.id
                          ? "Abriendo…"
                          : "PDF"
                      }}
                    </button>
                  </div>
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

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";

import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

/* ============================================================
  CONFIGURACIÓN
============================================================ */

const LIST_ENDPOINT = "/publicaciones/mias/";
const YEARS_ENDPOINT = "/publicaciones/mias/anios-disponibles/";
const FACULTADES_ENDPOINT = "/selects/facultades/";

const FILTER_DEBOUNCE_MS = 350;
const ROUTE_SYNC_DEBOUNCE_MS = 180;
const PDF_URL_REVOKE_DELAY_MS = 60_000;

/* ============================================================
  NAVEGACIÓN
============================================================ */

const route = useRoute();
const router = useRouter();

/* ============================================================
  TIPOS DE PUBLICACIÓN
============================================================ */

const TIPOS = Object.freeze({
  ALL: Object.freeze({
    label: "Todos",
    value: "ALL",
    apiValue: "",
  }),

  AAI: Object.freeze({
    label: PUBLICACION_TIPOS.AAI.label,
    value: PUBLICACION_TIPOS.AAI.codigo,
    apiValue: PUBLICACION_TIPOS.AAI.apiCodigo,
  }),

  AR: Object.freeze({
    label: PUBLICACION_TIPOS.AR.label,
    value: PUBLICACION_TIPOS.AR.codigo,
    apiValue: PUBLICACION_TIPOS.AR.apiCodigo,
  }),

  PON: Object.freeze({
    label: PUBLICACION_TIPOS.PON.label,
    value: PUBLICACION_TIPOS.PON.codigo,
    apiValue: PUBLICACION_TIPOS.PON.apiCodigo,
  }),

  CAP: Object.freeze({
    label: PUBLICACION_TIPOS.CAP.label,
    value: PUBLICACION_TIPOS.CAP.codigo,
    apiValue: PUBLICACION_TIPOS.CAP.apiCodigo,
  }),

  LIB: Object.freeze({
    label: PUBLICACION_TIPOS.LIB.label,
    value: PUBLICACION_TIPOS.LIB.codigo,
    apiValue: PUBLICACION_TIPOS.LIB.apiCodigo,
  }),
});

const TIPOS_LIST = Object.freeze([
  TIPOS.ALL,
  TIPOS.AAI,
  TIPOS.AR,
  TIPOS.PON,
  TIPOS.CAP,
  TIPOS.LIB,
]);

/* ============================================================
  ORÍGENES
============================================================ */

const ORIGENES_LIST = Object.freeze([
  {
    label: "Todos los orígenes",
    value: "ALL",
  },
  {
    label: "Ninguno",
    value: "ninguno",
  },
  {
    label: "Trabajo de integración curricular",
    value: "tic",
  },
  {
    label: "Tesis de maestría",
    value: "maestria",
  },
  {
    label: "Tesis doctoral",
    value: "doctoral",
  },
  {
    label: "Otro",
    value: "otro",
  },
]);

const ORIGEN_LABELS = Object.freeze({
  ninguno: "Ninguno",
  tic: "Trabajo de integración curricular",
  maestria: "Tesis de maestría",
  doctoral: "Tesis doctoral",
  otro: "Otro",
});

/* ============================================================
  ORDENAMIENTO
============================================================ */

const ORDENES = Object.freeze([
  {
    label: "Más recientes",
    value: "recientes",
  },
  {
    label: "Más antiguas",
    value: "antiguas",
  },
  {
    label: "Título A–Z",
    value: "titulo_asc",
  },
  {
    label: "Título Z–A",
    value: "titulo_desc",
  },
  {
    label: "Tipo de publicación",
    value: "tipo",
  },
]);

/* ============================================================
  DATOS PRINCIPALES
============================================================ */

const publicaciones = ref([]);

const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);

const totalPublicaciones = ref(0);
const totalResultados = ref(0);
const añosDisponibles = ref([]);

const typeCounts = ref(
  Object.fromEntries(
    TIPOS_LIST.map((tipo) => [
      tipo.value,
      0,
    ])
  )
);

/* ============================================================
  ESTADOS
============================================================ */

const loading = ref(true);
const loadingAnios = ref(true);
const errorMsg = ref("");
const pdfErrorMsg = ref("");
const openingPdfId = ref(null);

/* ============================================================
  ESTADO DE LA INTERFAZ
============================================================ */

const vista = ref("cards");
const filtrosAvanzadosAbiertos = ref(false);

const q = ref("");
const searchEl = ref(null);

const filtro = ref(TIPOS.ALL);
const filtroOrigen = ref("ALL");

const filtroFacultad = ref("");
const filtroCarrera = ref("");
const filtroProyecto = ref("");

const filtroAnio = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");

const soloConPdf = ref(false);
const orden = ref("recientes");

/* ============================================================
  CONTROL DE PETICIONES Y TEMPORIZADORES
============================================================ */

let routeSyncTimer = null;
let reloadTimer = null;

let listRequestSequence = 0;
let summaryRequestSequence = 0;
let typeCountRequestSequence = 0;
let yearsRequestSequence = 0;

let hasLoadedOnce = false;

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

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}

function extractTotal(
  payload,
  fallback = 0
) {
  const total = Number(
    payload?.count ??
      payload?.total ??
      payload?.pagination?.count
  );

  return Number.isFinite(total)
    ? total
    : fallback;
}

function extractYears(payload) {
  const source = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.anios)
      ? payload.anios
      : [];

  return [
    ...new Set(
      source
        .map((value) => Number(value))
        .filter(
          (value) =>
            Number.isInteger(value) &&
            value > 0
        )
    ),
  ].sort((a, b) => b - a);
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
    return Object.entries(detail)
      .flatMap(([field, value]) => {
        const messages = Array.isArray(value)
          ? value
          : [value];

        return messages.map(
          (message) =>
            `${field}: ${String(message)}`
        );
      })
      .join(" ");
  }

  return String(
    detail ||
      fallback
  );
}

/* ============================================================
  NORMALIZACIÓN GENERAL
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

function normalizeQueryValue(value) {
  if (Array.isArray(value)) {
    return String(
      value[0] ?? ""
    ).trim();
  }

  return String(
    value ?? ""
  ).trim();
}

function normalizeBooleanQuery(value) {
  return [
    "1",
    "true",
    "si",
    "sí",
    "yes",
    "on",
  ].includes(
    normalizeQueryValue(value).toLowerCase()
  );
}

function getCatalogLabel(item) {
  return (
    String(
      item?.label ??
        item?.nombre ??
        item?.name ??
        item?.titulo ??
        ""
    ).trim() ||
    `Registro ${item?.id ?? ""}`.trim()
  );
}

function catalogContainsId(
  catalog,
  value
) {
  const normalized = String(
    value ?? ""
  );

  return catalog.some(
    (item) =>
      String(item?.id ?? "") === normalized
  );
}

/* ============================================================
  FECHAS Y AÑOS
============================================================ */

function formatFecha(fecha) {
  if (!fecha) {
    return "Sin fecha";
  }

  const normalized = String(
    fecha
  ).slice(0, 10);

  const date = new Date(
    `${normalized}T00:00:00`
  );

  if (Number.isNaN(date.getTime())) {
    return "Sin fecha";
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  ).format(date);
}

function normalizeSelectedYearRange() {
  const desde = Number(
    filtroAnioDesde.value
  );

  const hasta = Number(
    filtroAnioHasta.value
  );

  if (
    !Number.isInteger(desde) ||
    !Number.isInteger(hasta)
  ) {
    return;
  }

  if (desde > hasta) {
    const previousDesde =
      filtroAnioDesde.value;

    filtroAnioDesde.value =
      filtroAnioHasta.value;

    filtroAnioHasta.value =
      previousDesde;
  }
}

function syncSelectedYearsWithCatalog() {
  const availableYears = new Set(
    añosDisponibles.value.map(
      (value) => String(value)
    )
  );

  if (
    filtroAnio.value &&
    !availableYears.has(
      String(filtroAnio.value)
    )
  ) {
    filtroAnio.value = "";
  }

  if (
    filtroAnioDesde.value &&
    !availableYears.has(
      String(filtroAnioDesde.value)
    )
  ) {
    filtroAnioDesde.value = "";
  }

  if (
    filtroAnioHasta.value &&
    !availableYears.has(
      String(filtroAnioHasta.value)
    )
  ) {
    filtroAnioHasta.value = "";
  }

  normalizeSelectedYearRange();
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

  if (
    meta?.codigo &&
    meta.codigo !== "OTRO"
  ) {
    return meta.label;
  }

  return (
    String(
      item?.tipo_publicacion_final_label ||
        item?.tipo_publicacion_final ||
        item?.tipo ||
        "Publicación"
    ).trim() ||
    "Publicación"
  );
}

function resolveOrigenCode(item) {
  const raw = String(
    item?.origen_tipo || ""
  )
    .trim()
    .toLowerCase();

  return raw || "ninguno";
}

function resolveOrigenLabel(item) {
  const code = resolveOrigenCode(item);

  return (
    String(
      item?.origen_tipo_label ||
        ORIGEN_LABELS[code] ||
        code
    ).trim() ||
    "Ninguno"
  );
}

function resolveOrigenResumen(item) {
  const provided = String(
    item?.origen_resumen || ""
  ).trim();

  if (provided) {
    return provided;
  }

  const code = resolveOrigenCode(item);

  if (
    !code ||
    code === "ninguno"
  ) {
    return "";
  }

  const label = resolveOrigenLabel(item);

  const detail = String(
    item?.origen_grado || ""
  ).trim();

  if (
    ["tic", "otro"].includes(code) &&
    detail
  ) {
    return `${label} · ${detail}`;
  }

  return label;
}

function hasPdf(item) {
  return Boolean(
    item?.tiene_pdf ||
      item?.has_pdf ||
      item?.hasPdf
  );
}

function resolvePdfEndpoint(item) {
  const provided = String(
    item?.pdf_endpoint || ""
  ).trim();

  if (provided) {
    return provided;
  }

  return item?.id
    ? `/publicaciones/${item.id}/pdf/`
    : "";
}

function buildAcademicMeta(pub) {
  const facultad = String(
    pub?.facultad || ""
  ).trim();

  const carrera = String(
    pub?.carrera || ""
  ).trim();

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
  CATÁLOGOS
============================================================ */

async function loadFacultades() {
  try {
    const response = await api.get(
      FACULTADES_ENDPOINT
    );

    facultades.value = extractArray(
      response.data
    );
  } catch (error) {
    console.error(
      "Error cargando facultades:",
      error
    );

    facultades.value = [];
  }
}

async function fetchCarrerasByFacultad(
  facultadId
) {
  if (!facultadId) {
    return [];
  }

  const response = await api.get(
    `/selects/carreras/${facultadId}/`
  );

  return extractArray(response.data);
}

async function fetchProyectosByCarrera(
  carreraId
) {
  if (!carreraId) {
    return [];
  }

  const response = await api.get(
    `/selects/proyectos/${carreraId}/`
  );

  return extractArray(response.data);
}

async function loadDependentCatalogsFromState() {
  carreras.value = [];
  proyectos.value = [];

  if (!filtroFacultad.value) {
    filtroCarrera.value = "";
    filtroProyecto.value = "";
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasByFacultad(
        filtroFacultad.value
      );

    if (
      filtroCarrera.value &&
      !catalogContainsId(
        carreras.value,
        filtroCarrera.value
      )
    ) {
      filtroCarrera.value = "";
      filtroProyecto.value = "";
    }

    if (!filtroCarrera.value) {
      return;
    }

    proyectos.value =
      await fetchProyectosByCarrera(
        filtroCarrera.value
      );

    if (
      filtroProyecto.value &&
      !catalogContainsId(
        proyectos.value,
        filtroProyecto.value
      )
    ) {
      filtroProyecto.value = "";
    }
  } catch (error) {
    console.error(
      "Error cargando catálogos dependientes:",
      error
    );

    carreras.value = [];
    proyectos.value = [];
  }
}

async function onMainFacultadChange() {
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  if (!filtroFacultad.value) {
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasByFacultad(
        filtroFacultad.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras:",
      error
    );

    carreras.value = [];
  }
}

async function onMainCarreraChange() {
  filtroProyecto.value = "";
  proyectos.value = [];

  if (!filtroCarrera.value) {
    return;
  }

  try {
    proyectos.value =
      await fetchProyectosByCarrera(
        filtroCarrera.value
      );
  } catch (error) {
    console.error(
      "Error cargando proyectos:",
      error
    );

    proyectos.value = [];
  }
}

/* ============================================================
  ESTADO DESDE LA URL
============================================================ */

function resolveTipoFilterFromQuery(value) {
  const raw = normalizeQueryValue(
    value
  );

  if (!raw) {
    return TIPOS.ALL;
  }

  const normalized =
    raw.toLowerCase();

  return (
    TIPOS_LIST.find((item) => {
      return (
        item.value.toLowerCase() ===
          normalized ||
        String(
          item.apiValue || ""
        ).toLowerCase() === normalized
      );
    }) ||
    TIPOS.ALL
  );
}

function hydrateStateFromRoute() {
  filtro.value =
    resolveTipoFilterFromQuery(
      route.query.tipo
    );

  const origenQuery =
    normalizeQueryValue(
      route.query.origen
    ).toLowerCase();

  filtroOrigen.value =
    ORIGENES_LIST.some(
      (item) =>
        item.value === origenQuery
    )
      ? origenQuery
      : "ALL";

  q.value = normalizeQueryValue(
    route.query.q
  );

  filtroFacultad.value =
    normalizeQueryValue(
      route.query.facultad
    );

  filtroCarrera.value =
    normalizeQueryValue(
      route.query.carrera
    );

  filtroProyecto.value =
    normalizeQueryValue(
      route.query.proyecto
    );

  filtroAnio.value =
    normalizeQueryValue(
      route.query.anio
    );

  filtroAnioDesde.value =
    normalizeQueryValue(
      route.query.desde
    );

  filtroAnioHasta.value =
    normalizeQueryValue(
      route.query.hasta
    );

  soloConPdf.value =
    normalizeBooleanQuery(
      route.query.pdf
    );

  const orderQuery =
    normalizeQueryValue(
      route.query.orden
    );

  orden.value =
    ORDENES.some(
      (item) =>
        item.value === orderQuery
    )
      ? orderQuery
      : "recientes";

  const viewQuery =
    normalizeQueryValue(
      route.query.vista
    );

  vista.value =
    ["cards", "tabla"].includes(
      viewQuery
    )
      ? viewQuery
      : "cards";

  filtrosAvanzadosAbiertos.value = Boolean(
    filtroOrigen.value !== "ALL" ||
    filtroAnioDesde.value ||
    filtroAnioHasta.value ||
    soloConPdf.value ||
    orden.value !== "recientes"
  );

  if (filtroAnio.value) {
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  } else {
    normalizeSelectedYearRange();
  }
}

function buildStateQuery() {
  const query = {
    ...route.query,
  };

  const knownKeys = [
    "tipo",
    "origen",
    "q",
    "facultad",
    "carrera",
    "proyecto",
    "anio",
    "desde",
    "hasta",
    "pdf",
    "orden",
    "vista",
  ];

  knownKeys.forEach((key) => {
    delete query[key];
  });

  if (
    filtro.value?.value !== "ALL"
  ) {
    query.tipo =
      filtro.value.value;
  }

  if (
    filtroOrigen.value !== "ALL"
  ) {
    query.origen =
      filtroOrigen.value;
  }

  if (q.value.trim()) {
    query.q = q.value.trim();
  }

  if (filtroFacultad.value) {
    query.facultad =
      filtroFacultad.value;
  }

  if (filtroCarrera.value) {
    query.carrera =
      filtroCarrera.value;
  }

  if (filtroProyecto.value) {
    query.proyecto =
      filtroProyecto.value;
  }

  if (filtroAnio.value) {
    query.anio =
      filtroAnio.value;
  }

  if (filtroAnioDesde.value) {
    query.desde =
      filtroAnioDesde.value;
  }

  if (filtroAnioHasta.value) {
    query.hasta =
      filtroAnioHasta.value;
  }

  if (soloConPdf.value) {
    query.pdf = "1";
  }

  if (orden.value !== "recientes") {
    query.orden = orden.value;
  }

  if (vista.value !== "cards") {
    query.vista = vista.value;
  }

  return query;
}

function scheduleRouteSync() {
  window.clearTimeout(
    routeSyncTimer
  );

  routeSyncTimer = window.setTimeout(
    () => {
      router.replace({
        query: buildStateQuery(),
      });
    },
    ROUTE_SYNC_DEBOUNCE_MS
  );
}

/* ============================================================
  PARÁMETROS OFICIALES DEL BACKEND
============================================================ */

function buildBackendParams({
  includeType = true,
  includeOrdering = true,
  includePeriod = true,
} = {}) {
  const params = {};

  if (
    includeType &&
    filtro.value?.value !== "ALL"
  ) {
    params.tipo =
      filtro.value?.apiValue ||
      filtro.value?.value;
  }

  if (
    filtroOrigen.value !== "ALL"
  ) {
    params.origen_tipo =
      filtroOrigen.value;
  }

  if (includePeriod) {
    if (filtroAnio.value) {
      params.anio =
        filtroAnio.value;
    } else {
      if (filtroAnioDesde.value) {
        params.anio_desde =
          filtroAnioDesde.value;
      }

      if (filtroAnioHasta.value) {
        params.anio_hasta =
          filtroAnioHasta.value;
      }
    }
  }

  if (q.value.trim()) {
    params.texto =
      q.value.trim();
  }

  if (filtroFacultad.value) {
    params.facultad =
      filtroFacultad.value;
  }

  if (filtroCarrera.value) {
    params.carrera =
      filtroCarrera.value;
  }

  if (filtroProyecto.value) {
    params.proyecto =
      filtroProyecto.value;
  }

  if (soloConPdf.value) {
    params.solo_con_pdf = "true";
  }

  if (
    includeOrdering &&
    orden.value
  ) {
    params.orden =
      orden.value;
  }

  return params;
}

/* ============================================================
  COMPUTEDS
============================================================ */

const tipoFiltroValue = computed(
  () =>
    filtro.value?.value ||
    "ALL"
);

const tipoThemeCode = computed(
  () =>
    filtro.value?.value ||
    "ALL"
);

const publicacionesFiltradas =
  computed(
    () => publicaciones.value
  );

const activeFiltersCount =
  computed(() => {
    let total = 0;

    if (
      filtro.value?.value !== "ALL"
    ) {
      total += 1;
    }

    if (
      filtroOrigen.value !== "ALL"
    ) {
      total += 1;
    }

    if (q.value.trim()) {
      total += 1;
    }

    if (filtroFacultad.value) {
      total += 1;
    }

    if (filtroCarrera.value) {
      total += 1;
    }

    if (filtroProyecto.value) {
      total += 1;
    }

    if (
      filtroAnio.value ||
      filtroAnioDesde.value ||
      filtroAnioHasta.value
    ) {
      total += 1;
    }

    if (soloConPdf.value) {
      total += 1;
    }

    return total;
  });

const advancedFiltersCount =
  computed(() => {
    let total = 0;

    if (filtroOrigen.value !== "ALL") {
      total += 1;
    }

    if (
      filtroAnioDesde.value ||
      filtroAnioHasta.value
    ) {
      total += 1;
    }

    if (soloConPdf.value) {
      total += 1;
    }

    if (orden.value !== "recientes") {
      total += 1;
    }

    return total;
  });

const canClearFilters =
  computed(() => {
    return (
      filtro.value?.value !== "ALL" ||
      filtroOrigen.value !== "ALL" ||
      q.value.trim().length > 0 ||
      Boolean(filtroFacultad.value) ||
      Boolean(filtroCarrera.value) ||
      Boolean(filtroProyecto.value) ||
      Boolean(filtroAnio.value) ||
      Boolean(filtroAnioDesde.value) ||
      Boolean(filtroAnioHasta.value) ||
      soloConPdf.value ||
      orden.value !== "recientes"
    );
  });

const emptyMessage =
  computed(() => {
    if (errorMsg.value) {
      return errorMsg.value;
    }

    const hasSearch =
      q.value.trim().length > 0;

    const hasFilter =
      activeFiltersCount.value > 0;

    if (
      hasSearch &&
      hasFilter
    ) {
      return (
        "No se encontraron publicaciones con la búsqueda " +
        "y los filtros seleccionados."
      );
    }

    if (hasSearch) {
      return (
        "No se encontraron publicaciones para la " +
        "búsqueda ingresada."
      );
    }

    if (hasFilter) {
      return (
        "No hay publicaciones para los filtros seleccionados."
      );
    }

    return (
      "Aún no tienes publicaciones registradas."
    );
  });

/* ============================================================
  ACCIONES DE FILTROS
============================================================ */

function cambiarFiltro(tipo) {
  filtro.value = tipo;
}

function clearAllFilters() {
  filtro.value = TIPOS.ALL;
  filtroOrigen.value = "ALL";

  q.value = "";

  filtroFacultad.value = "";
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  filtroAnio.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";

  soloConPdf.value = false;
  orden.value = "recientes";
  filtrosAvanzadosAbiertos.value = false;
}

function countByType(typeValue) {
  return Number(
    typeCounts.value?.[typeValue] ||
      0
  );
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
    query: {
      from: "mis-publicaciones",
    },
  });
}

function editarPublicacion(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}/editar`,
    query: {
      from: "mis-publicaciones",
    },
  });
}

/* ============================================================
  PDF AUTENTICADO
============================================================ */

async function abrirPdf(publicacion) {
  const endpoint =
    resolvePdfEndpoint(publicacion);

  if (
    !endpoint ||
    openingPdfId.value !== null
  ) {
    return;
  }

  openingPdfId.value =
    publicacion.id;

  pdfErrorMsg.value = "";

  const previewWindow =
    window.open("", "_blank");

  if (previewWindow) {
    previewWindow.opener = null;
    previewWindow.document.title =
      "Cargando PDF…";
  }

  try {
    const response = await api.get(
      endpoint,
      {
        responseType: "blob",
      }
    );

    const contentType =
      response.headers?.["content-type"] ||
      "application/pdf";

    const blob = new Blob(
      [response.data],
      {
        type: contentType,
      }
    );

    const objectUrl =
      window.URL.createObjectURL(blob);

    if (
      previewWindow &&
      !previewWindow.closed
    ) {
      previewWindow.location.href =
        objectUrl;
    } else {
      const link =
        document.createElement("a");

      link.href = objectUrl;
      link.target = "_blank";
      link.rel =
        "noopener noreferrer";

      document.body.appendChild(link);
      link.click();
      link.remove();
    }

    window.setTimeout(() => {
      window.URL.revokeObjectURL(
        objectUrl
      );
    }, PDF_URL_REVOKE_DELAY_MS);
  } catch (error) {
    if (
      previewWindow &&
      !previewWindow.closed
    ) {
      previewWindow.close();
    }

    console.error(
      "Error abriendo PDF:",
      error
    );

    pdfErrorMsg.value =
      extractErrorMessage(
        error,
        "No se pudo abrir el PDF de la publicación."
      );
  } finally {
    openingPdfId.value = null;
  }
}

/* ============================================================
  ATAJOS DE TECLADO
============================================================ */

function onKey(event) {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform
      .toLowerCase()
      .includes("mac");

  const key = String(
    event.key || ""
  ).toLowerCase();

  const shortcutSearch =
    (
      isMac &&
      event.metaKey &&
      key === "k"
    ) ||
    (
      !isMac &&
      event.ctrlKey &&
      key === "k"
    );

  if (shortcutSearch) {
    event.preventDefault();
    searchEl.value?.focus();
  }

  if (
    event.key === "Escape" &&
    q.value
  ) {
    q.value = "";
  }
}

/* ============================================================
  AÑOS DISPONIBLES DESDE EL BACKEND
============================================================ */

async function cargarAniosDisponibles() {
  const requestSequence =
    ++yearsRequestSequence;

  loadingAnios.value = true;

  try {
    const response = await api.get(
      YEARS_ENDPOINT
    );

    if (
      requestSequence !==
      yearsRequestSequence
    ) {
      return;
    }

    añosDisponibles.value =
      extractYears(response.data);

    syncSelectedYearsWithCatalog();
  } catch (error) {
    if (
      requestSequence !==
      yearsRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando años disponibles:",
      error
    );

    añosDisponibles.value = [];
  } finally {
    if (
      requestSequence ===
      yearsRequestSequence
    ) {
      loadingAnios.value = false;
    }
  }
}

/* ============================================================
  RESUMEN GENERAL
============================================================ */

async function cargarResumen() {
  const requestSequence =
    ++summaryRequestSequence;

  try {
    const response = await api.get(
      LIST_ENDPOINT
    );

    if (
      requestSequence !==
      summaryRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    );

    totalPublicaciones.value =
      extractTotal(
        response.data,
        items.length
      );
  } catch (error) {
    if (
      requestSequence !==
      summaryRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando resumen de publicaciones:",
      error
    );
  }
}

/* ============================================================
  CONTEOS POR TIPO
============================================================ */

async function cargarConteosPorTipo() {
  const requestSequence =
    ++typeCountRequestSequence;

  const params =
    buildBackendParams({
      includeType: false,
      includeOrdering: false,
    });

  try {
    const response = await api.get(
      LIST_ENDPOINT,
      {
        params,
      }
    );

    if (
      requestSequence !==
      typeCountRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    ).map((item) => ({
      ...item,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          item
        ),
    }));

    const counts =
      Object.fromEntries(
        TIPOS_LIST.map((tipo) => [
          tipo.value,
          0,
        ])
      );

    counts.ALL = extractTotal(
      response.data,
      items.length
    );

    items.forEach((item) => {
      const code = resolveType(item);

      if (
        Object.hasOwn(
          counts,
          code
        )
      ) {
        counts[code] += 1;
      }
    });

    typeCounts.value = counts;
  } catch (error) {
    if (
      requestSequence !==
      typeCountRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando conteos por tipo:",
      error
    );
  }
}

/* ============================================================
  CARGA DE PUBLICACIONES
============================================================ */

async function cargarPublicaciones({
  forceLoading = false,
} = {}) {
  const requestSequence =
    ++listRequestSequence;

  const showLoading =
    forceLoading ||
    !hasLoadedOnce;

  if (showLoading) {
    loading.value = true;
  }

  errorMsg.value = "";
  pdfErrorMsg.value = "";

  try {
    const response = await api.get(
      LIST_ENDPOINT,
      {
        params:
          buildBackendParams(),
      }
    );

    if (
      requestSequence !==
      listRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    ).map((item) => ({
      ...item,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          item
        ),
    }));

    publicaciones.value = items;

    totalResultados.value =
      extractTotal(
        response.data,
        items.length
      );

    if (!canClearFilters.value) {
      totalPublicaciones.value =
        totalResultados.value;
    }

    hasLoadedOnce = true;

    void cargarConteosPorTipo();
  } catch (error) {
    if (
      requestSequence !==
      listRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando publicaciones:",
      error
    );

    publicaciones.value = [];
    totalResultados.value = 0;

    errorMsg.value =
      extractErrorMessage(
        error,
        "No se pudieron cargar tus publicaciones."
      );
  } finally {
    if (
      requestSequence ===
      listRequestSequence
    ) {
      loading.value = false;
    }
  }
}

function scheduleReload(
  delay = FILTER_DEBOUNCE_MS
) {
  window.clearTimeout(
    reloadTimer
  );

  reloadTimer = window.setTimeout(
    () => {
      void cargarPublicaciones();
    },
    delay
  );
}

/* ============================================================
  HIDRATACIÓN INICIAL
============================================================ */

hydrateStateFromRoute();

/* ============================================================
  WATCHERS DE PERIODO
============================================================ */

watch(
  filtroAnio,
  (value) => {
    if (!value) {
      return;
    }

    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  }
);

watch(
  [
    filtroAnioDesde,
    filtroAnioHasta,
  ],
  ([desde, hasta]) => {
    if (desde || hasta) {
      filtroAnio.value = "";
    }

    normalizeSelectedYearRange();
  }
);

/* ============================================================
  WATCHER GENERAL DE FILTROS
============================================================ */

watch(
  [
    q,
    tipoFiltroValue,
    filtroOrigen,
    filtroFacultad,
    filtroCarrera,
    filtroProyecto,
    filtroAnio,
    filtroAnioDesde,
    filtroAnioHasta,
    soloConPdf,
    orden,
  ],
  () => {
    scheduleRouteSync();
    scheduleReload();
  }
);

watch(
  vista,
  () => {
    scheduleRouteSync();
  }
);

/* ============================================================
  CICLO DE VIDA
============================================================ */

onMounted(async () => {
  window.addEventListener(
    "keydown",
    onKey
  );

  await loadFacultades();
  await loadDependentCatalogsFromState();

  await Promise.all([
    cargarResumen(),
    cargarAniosDisponibles(),
    cargarPublicaciones({
      forceLoading: true,
    }),
  ]);
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    onKey
  );

  window.clearTimeout(
    routeSyncTimer
  );

  window.clearTimeout(
    reloadTimer
  );

  listRequestSequence += 1;
  summaryRequestSequence += 1;
  typeCountRequestSequence += 1;
  yearsRequestSequence += 1;
});
</script>

<style src="../listado-publicaciones/sgpc-listados-base.css"></style>
<style src="./mis-publicaciones.css"></style>
