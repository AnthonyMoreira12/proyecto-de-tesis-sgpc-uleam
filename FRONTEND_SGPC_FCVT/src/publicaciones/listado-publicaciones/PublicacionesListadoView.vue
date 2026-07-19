<template>
  <div class="pub-list-page" :data-tipo="filtroTipo">
    <main class="pub-shell">
      <!-- =====================================================
        ENCABEZADO
      ====================================================== -->
      <header
        class="pub-header page-stage page-stage-1"
        aria-label="Listado de publicaciones institucionales"
      >
        <div class="pub-header__copy">
          <span class="pub-eyebrow">
            Producción científica
          </span>

          <h1 class="pub-title">
            Publicaciones institucionales
          </h1>

          <p class="pub-subtitle">
            Consulte, filtre y exporte la producción científica registrada en
            el sistema.
          </p>

          <div
            class="pub-chips"
            aria-label="Resumen general de publicaciones"
          >
            <span class="pub-chip">
              Total:
              <strong>{{ publicaciones.length }}</strong>
            </span>

            <span class="pub-chip">
              Resultados:
              <strong>{{ listaFiltrada.length }}</strong>
            </span>

            <span
              v-if="totalActiveFiltersCount"
              class="pub-chip pub-chip--active"
            >
              Filtros:
              <strong>{{ totalActiveFiltersCount }}</strong>
            </span>
          </div>
        </div>

        <div
          class="pub-header__tools"
          aria-label="Herramientas principales"
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
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 1 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </span>

            <input
              id="fTexto"
              ref="searchEl"
              v-model="filtroTexto"
              class="search__input"
              type="search"
              inputmode="search"
              autocomplete="off"
              placeholder="Buscar por título, autor, proyecto, facultad o carrera…"
            />

            <button
              type="button"
              class="search__action"
              :aria-label="
                hayBusqueda
                  ? 'Limpiar búsqueda'
                  : 'Enfocar campo de búsqueda'
              "
              @click="handleSearchAction"
            >
              <span
                v-if="hayBusqueda"
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
            class="pub-header__actions"
            aria-label="Acciones del listado"
          >
            <button
              class="pub-btn pub-btn--ghost"
              :class="{
                'is-active': panelLateralActivo === 'filtros',
              }"
              type="button"
              :aria-pressed="panelLateralActivo === 'filtros'"
              @click="abrirPanelFiltros"
            >
              Filtros
            </button>

            <button
              class="pub-btn pub-btn--primary"
              :class="{
                'is-active': panelLateralActivo === 'export',
              }"
              type="button"
              :aria-pressed="panelLateralActivo === 'export'"
              :disabled="loading"
              @click="abrirPanelExportacion"
            >
              Exportar Excel
            </button>
          </div>
        </div>
      </header>

      <!-- =====================================================
        CONTENIDO GENERAL
      ====================================================== -->
      <section
        class="pub-layout page-stage page-stage-2"
        aria-label="Consulta de publicaciones"
      >
        <!-- ===================================================
          PANEL LATERAL
        ==================================================== -->
        <aside
          class="pub-side"
          aria-label="Panel lateral de consulta"
        >
          <div class="pub-sideStack">
            <!-- ===============================================
              FILTROS AVANZADOS
            ================================================ -->
            <section
              v-if="panelLateralActivo === 'filtros'"
              class="pub-sidePanel"
            >
              <header class="pub-sidePanel__head">
                <div>
                  <span class="pub-sidePanel__eyebrow">
                    Refinar resultados
                  </span>

                  <h2 class="pub-sidePanel__title">
                    Filtros
                  </h2>
                </div>

                <span
                  class="pub-sidePanel__badge"
                  aria-label="Cantidad de filtros avanzados activos"
                >
                  {{ activeAdvancedFiltersCount }}
                </span>
              </header>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Ubicación académica
                </h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fFacultad"
                    >
                      Facultad
                    </label>

                    <select
                      id="fFacultad"
                      v-model="filtroFacultad"
                      class="pub-select"
                      @change="onMainFacultadChange"
                    >
                      <option value="">
                        Todas las facultades
                      </option>

                      <option
                        v-for="fac in facultades"
                        :key="`fac-${fac.id}`"
                        :value="String(fac.id)"
                      >
                        {{ fac.nombre }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fCarrera"
                    >
                      Carrera
                    </label>

                    <select
                      id="fCarrera"
                      v-model="filtroCarrera"
                      class="pub-select"
                      :disabled="!filtroFacultad"
                      @change="onMainCarreraChange"
                    >
                      <option value="">
                        Todas las carreras
                      </option>

                      <option
                        v-for="car in carreras"
                        :key="`car-${car.id}`"
                        :value="String(car.id)"
                      >
                        {{ car.nombre }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fProyecto"
                    >
                      Proyecto
                    </label>

                    <select
                      id="fProyecto"
                      v-model="filtroProyecto"
                      class="pub-select"
                      :disabled="!filtroCarrera"
                    >
                      <option value="">
                        Todos los proyectos
                      </option>

                      <option
                        v-for="proy in proyectos"
                        :key="`proy-${proy.id}`"
                        :value="String(proy.id)"
                      >
                        {{ proy.nombre }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Periodo de publicación
                </h3>

                <div
                  class="
                    pub-sidePanel__fields
                    pub-sidePanel__fields--years
                  "
                >
                  <div class="pub-field pub-field--full">
                    <label
                      class="pub-label"
                      for="fAnio"
                    >
                      Año exacto
                    </label>

                    <select
                      id="fAnio"
                      v-model="filtroAnio"
                      class="pub-select"
                      :disabled="
                        Boolean(filtroAnioDesde || filtroAnioHasta)
                      "
                    >
                      <option value="">
                        Todos los años
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`exact-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fAnioDesde"
                    >
                      Desde
                    </label>

                    <select
                      id="fAnioDesde"
                      v-model="filtroAnioDesde"
                      class="pub-select"
                      :disabled="Boolean(filtroAnio)"
                    >
                      <option value="">
                        Sin mínimo
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`desde-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fAnioHasta"
                    >
                      Hasta
                    </label>

                    <select
                      id="fAnioHasta"
                      v-model="filtroAnioHasta"
                      class="pub-select"
                      :disabled="Boolean(filtroAnio)"
                    >
                      <option value="">
                        Actual
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`hasta-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <footer class="pub-sidePanel__footer">
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost pub-btn--block"
                  :disabled="!hayFiltros && !hayBusqueda"
                  @click="limpiarFiltros"
                >
                  Limpiar filtros
                </button>
              </footer>
            </section>

            <!-- ===============================================
              EXPORTACIÓN
            ================================================ -->
            <section
              v-else
              class="pub-sidePanel pub-sidePanel--export"
            >
              <header class="pub-sidePanel__head">
                <div>
                  <span class="pub-sidePanel__eyebrow">
                    Reporte institucional
                  </span>

                  <h2 class="pub-sidePanel__title">
                    Exportar Excel
                  </h2>
                </div>

                <span
                  class="
                    pub-sidePanel__badge
                    pub-sidePanel__badge--soft
                  "
                  aria-label="Registros incluidos en el reporte"
                >
                  {{ exportPreviewCount }}
                </span>
              </header>

              <div
                v-if="exportErrorMsg"
                class="pub-alert"
                role="alert"
              >
                {{ exportErrorMsg }}
              </div>

              <div class="pub-sidePanel__actions">
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost"
                  @click="syncExportFiltersFromVisible"
                >
                  Usar visibles
                </button>

                <button
                  type="button"
                  class="pub-btn pub-btn--ghost"
                  @click="limpiarExportFilters"
                >
                  Limpiar
                </button>
              </div>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Criterios del reporte
                </h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expTexto"
                    >
                      Texto
                    </label>

                    <input
                      id="expTexto"
                      v-model="exportFiltroTexto"
                      class="pub-input"
                      type="search"
                      inputmode="search"
                      autocomplete="off"
                      placeholder="Título, autor, proyecto, facultad o carrera…"
                    />
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expTipo"
                    >
                      Tipo
                    </label>

                    <select
                      id="expTipo"
                      v-model="exportFiltroTipo"
                      class="pub-select"
                    >
                      <option
                        v-for="tipo in TIPOS_LIST"
                        :key="`exp-${tipo.value}`"
                        :value="tipo.value"
                      >
                        {{ tipo.label }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expFacultad"
                    >
                      Facultad
                    </label>

                    <select
                      id="expFacultad"
                      v-model="exportFiltroFacultad"
                      class="pub-select"
                      @change="onExportFacultadChange"
                    >
                      <option value="">
                        Todas las facultades
                      </option>

                      <option
                        v-for="fac in facultades"
                        :key="`exp-fac-${fac.id}`"
                        :value="String(fac.id)"
                      >
                        {{ fac.nombre }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expCarrera"
                    >
                      Carrera
                    </label>

                    <select
                      id="expCarrera"
                      v-model="exportFiltroCarrera"
                      class="pub-select"
                      :disabled="!exportFiltroFacultad"
                      @change="onExportCarreraChange"
                    >
                      <option value="">
                        Todas las carreras
                      </option>

                      <option
                        v-for="car in exportCarreras"
                        :key="`exp-car-${car.id}`"
                        :value="String(car.id)"
                      >
                        {{ car.nombre }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expProyecto"
                    >
                      Proyecto
                    </label>

                    <select
                      id="expProyecto"
                      v-model="exportFiltroProyecto"
                      class="pub-select"
                      :disabled="!exportFiltroCarrera"
                    >
                      <option value="">
                        Todos los proyectos
                      </option>

                      <option
                        v-for="proy in exportProyectos"
                        :key="`exp-proy-${proy.id}`"
                        :value="String(proy.id)"
                      >
                        {{ proy.nombre }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expAnio"
                    >
                      Año exacto
                    </label>

                    <select
                      id="expAnio"
                      v-model="exportFiltroAnio"
                      class="pub-select"
                      :disabled="
                        Boolean(
                          exportFiltroAnioDesde ||
                            exportFiltroAnioHasta
                        )
                      "
                    >
                      <option value="">
                        Todos los años
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`exp-exact-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expAnioDesde"
                    >
                      Desde
                    </label>

                    <select
                      id="expAnioDesde"
                      v-model="exportFiltroAnioDesde"
                      class="pub-select"
                      :disabled="Boolean(exportFiltroAnio)"
                    >
                      <option value="">
                        Sin mínimo
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`exp-desde-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expAnioHasta"
                    >
                      Hasta
                    </label>

                    <select
                      id="expAnioHasta"
                      v-model="exportFiltroAnioHasta"
                      class="pub-select"
                      :disabled="Boolean(exportFiltroAnio)"
                    >
                      <option value="">
                        Actual
                      </option>

                      <option
                        v-for="anio in años"
                        :key="`exp-hasta-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <footer
                class="
                  pub-sidePanel__footer
                  pub-sidePanel__footer--stack
                "
              >
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost pub-btn--block"
                  :disabled="exporting"
                  @click="abrirPanelFiltros"
                >
                  Volver a filtros
                </button>

                <button
                  type="button"
                  class="pub-btn pub-btn--primary pub-btn--block"
                  :disabled="
                    loading ||
                      exporting ||
                      !exportPreviewCount
                  "
                  @click="confirmarExportacion"
                >
                  {{
                    exporting
                      ? "Generando..."
                      : "Generar Excel"
                  }}
                </button>
              </footer>
            </section>
          </div>
        </aside>

        <!-- ===================================================
          RESULTADOS
        ==================================================== -->
        <section class="pub-main">
          <section
            class="pub-typeFilter"
            aria-label="Filtrado por tipo de publicación"
          >
            <header class="pub-typeFilter__head">
              <div>
                <span class="pub-typeFilter__eyebrow">
                  Clasificación
                </span>

                <h2 class="pub-typeFilter__title">
                  Tipo de publicación
                </h2>
              </div>

              <button
                v-if="hayFiltros || hayBusqueda"
                type="button"
                class="pub-inlineAction"
                @click="limpiarFiltros"
              >
                Limpiar todo
              </button>
            </header>

            <div class="pub-typeFilter__chips">
              <button
                v-for="tipo in TIPOS_LIST"
                :key="`top-${tipo.value}`"
                type="button"
                class="pub-typeFilter__chip"
                :class="{
                  'is-active': filtroTipo === tipo.value,
                }"
                :aria-pressed="filtroTipo === tipo.value"
                @click="filtroTipo = tipo.value"
              >
                <span
                  class="pub-typeFilter__dot"
                  :data-tipo="tipo.value"
                  aria-hidden="true"
                ></span>

                <span class="pub-typeFilter__label">
                  {{ tipo.label }}
                </span>

                <span class="pub-typeFilter__count">
                  {{ countByType(tipo.value) }}
                </span>
              </button>
            </div>
          </section>

          <!-- ===============================================
            CARGA
          ================================================ -->
          <section
            v-if="loading"
            class="pub-state"
            aria-live="polite"
          >
            <div
              class="pub-skeleton-grid"
              aria-label="Cargando publicaciones"
            >
              <div
                v-for="n in 6"
                :key="n"
                class="pub-skeleton-card"
              ></div>
            </div>
          </section>

          <!-- ===============================================
            ERROR
          ================================================ -->
          <section
            v-else-if="errorMsg"
            class="pub-state pub-state--error"
          >
            <div
              class="pub-alert"
              role="alert"
            >
              {{ errorMsg }}
            </div>
          </section>

          <!-- ===============================================
            CONTENIDO
          ================================================ -->
          <section
            v-else
            class="pub-content"
          >
            <div
              v-if="listaFiltrada.length"
              class="pub-grid page-stagger page-stagger--mid"
            >
              <article
                v-for="pub in listaFiltrada"
                :key="pub.id"
                class="pub-card pub-card--interactive"
                :data-tipo="resolveType(pub)"
                tabindex="0"
                role="button"
                :aria-label="
                  `Ver detalle de ${
                    pub.titulo ||
                    pub.proyecto ||
                    'la publicación'
                  }`
                "
                @click="verDetalles(pub.id)"
                @keydown.enter.prevent="verDetalles(pub.id)"
                @keydown.space.prevent="verDetalles(pub.id)"
              >
                <div class="pub-card__head">
                  <span
                    class="pub-badge"
                    :data-tipo="resolveType(pub)"
                  >
                    {{ resolveLabel(pub) }}
                  </span>

                  <time
                    class="pub-date"
                    :datetime="pub.fecha_publicacion || ''"
                  >
                    {{ formatFecha(pub.fecha_publicacion) }}
                  </time>
                </div>

                <div class="pub-card__body">
                  <h3
                    class="pub-card__title"
                    :title="
                      pub.titulo ||
                        pub.proyecto ||
                        'Sin título'
                    "
                  >
                    {{
                      pub.titulo ||
                        pub.proyecto ||
                        "Sin título"
                    }}
                  </h3>

                  <p
                    v-if="pub.autor"
                    class="
                      pub-card__meta
                      pub-card__meta--soft
                    "
                    :title="pub.autor"
                  >
                    {{ pub.autor }}
                  </p>

                  <p
                    v-if="pub.proyecto"
                    class="pub-card__meta"
                    :title="pub.proyecto"
                  >
                    {{ pub.proyecto }}
                  </p>

                  <p
                    class="pub-card__meta"
                    :title="buildAcademicMeta(pub)"
                  >
                    {{ buildAcademicMeta(pub) }}
                  </p>
                </div>

                <footer class="pub-card__footer">
                  <span class="pub-card__action">
                    Ver detalle
                  </span>
                </footer>
              </article>
            </div>

            <div
              v-else
              class="pub-empty"
              role="status"
              aria-live="polite"
            >
              <div
                class="pub-empty__mark"
                aria-hidden="true"
              ></div>

              <h3 class="pub-empty__title">
                {{ emptyTitle }}
              </h3>

              <p class="pub-empty__text">
                {{ emptyText }}
              </p>

              <button
                v-if="hayFiltros || hayBusqueda"
                class="pub-btn pub-btn--primary"
                type="button"
                @click="limpiarFiltros"
              >
                Limpiar filtros
              </button>
            </div>
          </section>
        </section>
      </section>
    </main>
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
const searchEl = ref(null);

/* ============================================================
  PANEL LATERAL
============================================================ */

const panelLateralActivo = ref("filtros");

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
  DATOS PRINCIPALES
============================================================ */

const publicaciones = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);
const años = ref([]);

/* ============================================================
  FILTROS VISIBLES
============================================================ */

const filtroTipo = ref(TIPOS.ALL.value);
const filtroAnio = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");
const filtroTexto = ref("");
const filtroFacultad = ref("");
const filtroCarrera = ref("");
const filtroProyecto = ref("");

/* ============================================================
  FILTROS DE EXPORTACIÓN
============================================================ */

const exportFiltroTipo = ref(TIPOS.ALL.value);
const exportFiltroAnio = ref("");
const exportFiltroAnioDesde = ref("");
const exportFiltroAnioHasta = ref("");
const exportFiltroTexto = ref("");
const exportFiltroFacultad = ref("");
const exportFiltroCarrera = ref("");
const exportFiltroProyecto = ref("");

const exportCarreras = ref([]);
const exportProyectos = ref([]);

/* ============================================================
  ESTADOS
============================================================ */

const loading = ref(false);
const exporting = ref(false);
const errorMsg = ref("");
const exportErrorMsg = ref("");

/* ============================================================
  HELPERS DE INTERFAZ
============================================================ */

function focusSearch() {
  searchEl.value?.focus();
}

function handleSearchAction() {
  if (filtroTexto.value) {
    filtroTexto.value = "";
    focusSearch();
    return;
  }

  focusSearch();
}

function abrirPanelFiltros() {
  panelLateralActivo.value = "filtros";
}

async function abrirPanelExportacion() {
  panelLateralActivo.value = "export";
  await syncExportFiltersFromVisible();
}

/* ============================================================
  NORMALIZACIÓN
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
  fallback = "No se pudieron cargar los datos."
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

function findById(list, id) {
  return list.find(
    (item) =>
      String(item?.id) === String(id || "")
  );
}

function extractYear(fecha) {
  const raw = String(fecha || "").substring(0, 4);

  return /^\d{4}$/.test(raw)
    ? Number(raw)
    : null;
}

function compareCatalogValue(value, selectedLabel) {
  if (!selectedLabel) {
    return true;
  }

  const normalizedValue = normalizeText(value);
  const normalizedLabel = normalizeText(selectedLabel);

  return (
    normalizedValue === normalizedLabel ||
    normalizedValue.includes(normalizedLabel) ||
    normalizedLabel.includes(normalizedValue)
  );
}

/* ============================================================
  METADATOS DE PUBLICACIÓN
============================================================ */

function getResolvedMeta(publicacion) {
  return (
    publicacion?.__tipoMeta ||
    getTipoPublicacionMetaFromItem(publicacion)
  );
}

function resolveType(publicacion) {
  const meta = getResolvedMeta(publicacion);

  return meta?.codigo || "OTRO";
}

function resolveLabel(publicacion) {
  const meta = getResolvedMeta(publicacion);

  if (meta?.codigo && meta.codigo !== "OTRO") {
    return meta.label;
  }

  return (
    String(
      publicacion?.tipo_publicacion_final_label ||
        publicacion?.tipo_publicacion_final ||
        publicacion?.tipo ||
        "Publicación"
    ).trim() || "Publicación"
  );
}

function buildAcademicMeta(publicacion) {
  const facultad = String(
    publicacion?.facultad || ""
  ).trim();

  const carrera = String(
    publicacion?.carrera || ""
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
  CATÁLOGOS SELECCIONADOS
============================================================ */

const selectedFacultadNombre = computed(() => {
  const facultad = findById(
    facultades.value,
    filtroFacultad.value
  );

  return facultad?.nombre || "";
});

const selectedCarreraNombre = computed(() => {
  const carrera = findById(
    carreras.value,
    filtroCarrera.value
  );

  return carrera?.nombre || "";
});

const selectedProyectoNombre = computed(() => {
  const proyecto = findById(
    proyectos.value,
    filtroProyecto.value
  );

  return proyecto?.nombre || "";
});

const selectedExportFacultadNombre = computed(() => {
  const facultad = findById(
    facultades.value,
    exportFiltroFacultad.value
  );

  return facultad?.nombre || "";
});

const selectedExportCarreraNombre = computed(() => {
  const carrera = findById(
    exportCarreras.value,
    exportFiltroCarrera.value
  );

  return carrera?.nombre || "";
});

const selectedExportProyectoNombre = computed(() => {
  const proyecto = findById(
    exportProyectos.value,
    exportFiltroProyecto.value
  );

  return proyecto?.nombre || "";
});

/* ============================================================
  MOTOR DE FILTRADO
============================================================ */

function filterPublicaciones(items, criteria) {
  const query = normalizeText(criteria.texto);

  const anioExacto = criteria.anio
    ? Number(criteria.anio)
    : null;

  const anioDesde = criteria.anioDesde
    ? Number(criteria.anioDesde)
    : null;

  const anioHasta = criteria.anioHasta
    ? Number(criteria.anioHasta)
    : null;

  const minYear =
    !anioExacto && anioDesde && anioHasta
      ? Math.min(anioDesde, anioHasta)
      : anioDesde;

  const maxYear =
    !anioExacto && anioDesde && anioHasta
      ? Math.max(anioDesde, anioHasta)
      : anioHasta;

  return items.filter((publicacion) => {
    const tipoResuelto = resolveType(publicacion);

    const year = extractYear(
      publicacion?.fecha_publicacion
    );

    const cumpleTipo =
      criteria.tipo &&
      criteria.tipo !== TIPOS.ALL.value
        ? tipoResuelto === criteria.tipo
        : true;

    let cumpleAnio = true;

    if (anioExacto) {
      cumpleAnio = year === anioExacto;
    } else {
      if (
        minYear &&
        (!year || year < minYear)
      ) {
        cumpleAnio = false;
      }

      if (
        maxYear &&
        (!year || year > maxYear)
      ) {
        cumpleAnio = false;
      }
    }

    const cumpleFacultad = compareCatalogValue(
      publicacion?.facultad,
      criteria.facultadLabel
    );

    const cumpleCarrera = compareCatalogValue(
      publicacion?.carrera,
      criteria.carreraLabel
    );

    const cumpleProyecto = compareCatalogValue(
      publicacion?.proyecto,
      criteria.proyectoLabel
    );

    const searchableText = [
      publicacion?.titulo,
      publicacion?.proyecto,
      publicacion?.autor,
      publicacion?.tipo,
      publicacion?.tipo_codigo,
      publicacion?.tipo_publicacion_final,
      publicacion?.tipo_publicacion_final_label,
      publicacion?.facultad,
      publicacion?.carrera,
      publicacion?.fecha_publicacion,
      resolveLabel(publicacion),
      resolveType(publicacion),
      buildAcademicMeta(publicacion),
    ]
      .map((value) => normalizeText(value))
      .join(" ");

    const cumpleTexto = query
      ? searchableText.includes(query)
      : true;

    return (
      cumpleTipo &&
      cumpleAnio &&
      cumpleFacultad &&
      cumpleCarrera &&
      cumpleProyecto &&
      cumpleTexto
    );
  });
}

/* ============================================================
  CRITERIOS COMPUTADOS
============================================================ */

const mainCriteria = computed(() => ({
  tipo: filtroTipo.value,
  anio: filtroAnio.value,
  anioDesde: filtroAnioDesde.value,
  anioHasta: filtroAnioHasta.value,
  texto: filtroTexto.value,
  facultadLabel: selectedFacultadNombre.value,
  carreraLabel: selectedCarreraNombre.value,
  proyectoLabel: selectedProyectoNombre.value,
}));

const exportCriteria = computed(() => ({
  tipo: exportFiltroTipo.value,
  anio: exportFiltroAnio.value,
  anioDesde: exportFiltroAnioDesde.value,
  anioHasta: exportFiltroAnioHasta.value,
  texto: exportFiltroTexto.value,
  facultadLabel:
    selectedExportFacultadNombre.value,
  carreraLabel:
    selectedExportCarreraNombre.value,
  proyectoLabel:
    selectedExportProyectoNombre.value,
}));

/* ============================================================
  ESTADOS COMPUTADOS
============================================================ */

const hayBusqueda = computed(() => {
  return Boolean(filtroTexto.value?.trim());
});

const hayFiltros = computed(() => {
  return (
    filtroTipo.value !== TIPOS.ALL.value ||
    Boolean(filtroAnio.value) ||
    Boolean(filtroAnioDesde.value) ||
    Boolean(filtroAnioHasta.value) ||
    Boolean(filtroFacultad.value) ||
    Boolean(filtroCarrera.value) ||
    Boolean(filtroProyecto.value)
  );
});

const activeAdvancedFiltersCount = computed(() => {
  return [
    Boolean(filtroFacultad.value),
    Boolean(filtroCarrera.value),
    Boolean(filtroProyecto.value),
    Boolean(filtroAnio.value),
    Boolean(filtroAnioDesde.value),
    Boolean(filtroAnioHasta.value),
  ].filter(Boolean).length;
});

const totalActiveFiltersCount = computed(() => {
  let total = activeAdvancedFiltersCount.value;

  if (filtroTipo.value !== TIPOS.ALL.value) {
    total += 1;
  }

  if (hayBusqueda.value) {
    total += 1;
  }

  return total;
});

const listaFiltrada = computed(() => {
  return filterPublicaciones(
    publicaciones.value,
    mainCriteria.value
  );
});

const exportPreviewCount = computed(() => {
  return filterPublicaciones(
    publicaciones.value,
    exportCriteria.value
  ).length;
});

const emptyTitle = computed(() => {
  if (hayBusqueda.value || hayFiltros.value) {
    return "No se encontraron publicaciones";
  }

  return "No hay publicaciones registradas";
});

const emptyText = computed(() => {
  if (hayBusqueda.value || hayFiltros.value) {
    return (
      "No existen resultados que coincidan con los " +
      "criterios seleccionados."
    );
  }

  return (
    "Todavía no existen publicaciones disponibles " +
    "para esta consulta."
  );
});

/* ============================================================
  CONTEO POR TIPO
============================================================ */

function countByType(typeValue) {
  if (typeValue === TIPOS.ALL.value) {
    return publicaciones.value.length;
  }

  return publicaciones.value.filter(
    (item) => resolveType(item) === typeValue
  ).length;
}

/* ============================================================
  CARGA DE DATOS
============================================================ */

async function loadPublicaciones() {
  const response = await api.get("/publicaciones/");

  publicaciones.value = extractArray(
    response.data
  ).map((publicacion) => ({
    ...publicacion,

    __tipoMeta:
      getTipoPublicacionMetaFromItem(publicacion),
  }));

  const extractedYears = publicaciones.value
    .map((publicacion) =>
      extractYear(publicacion?.fecha_publicacion)
    )
    .filter((year) => Number.isInteger(year));

  años.value = [
    ...new Set(extractedYears),
  ].sort((a, b) => b - a);
}

async function loadFacultades() {
  const response = await api.get(
    "/selects/facultades/"
  );

  facultades.value = extractArray(response.data);
}

async function fetchCarrerasByFacultad(facultadId) {
  if (!facultadId) {
    return [];
  }

  const response = await api.get(
    `/selects/carreras/${facultadId}/`
  );

  return extractArray(response.data);
}

async function fetchProyectosByCarrera(carreraId) {
  if (!carreraId) {
    return [];
  }

  const response = await api.get(
    `/selects/proyectos/${carreraId}/`
  );

  return extractArray(response.data);
}

/* ============================================================
  LIMPIEZA DE FILTROS
============================================================ */

function limpiarFiltros() {
  filtroTipo.value = TIPOS.ALL.value;
  filtroAnio.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";
  filtroTexto.value = "";
  filtroFacultad.value = "";
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];
}

function limpiarExportFilters() {
  exportFiltroTipo.value = TIPOS.ALL.value;
  exportFiltroAnio.value = "";
  exportFiltroAnioDesde.value = "";
  exportFiltroAnioHasta.value = "";
  exportFiltroTexto.value = "";
  exportFiltroFacultad.value = "";
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";

  exportCarreras.value = [];
  exportProyectos.value = [];

  exportErrorMsg.value = "";
}

/* ============================================================
  SINCRONIZACIÓN DE FILTROS DE EXPORTACIÓN
============================================================ */

async function syncExportFiltersFromVisible() {
  exportFiltroTipo.value = filtroTipo.value;
  exportFiltroAnio.value = filtroAnio.value;
  exportFiltroAnioDesde.value =
    filtroAnioDesde.value;
  exportFiltroAnioHasta.value =
    filtroAnioHasta.value;
  exportFiltroTexto.value = filtroTexto.value;
  exportFiltroFacultad.value =
    filtroFacultad.value;
  exportFiltroCarrera.value =
    filtroCarrera.value;
  exportFiltroProyecto.value =
    filtroProyecto.value;

  exportCarreras.value = [];
  exportProyectos.value = [];
  exportErrorMsg.value = "";

  if (exportFiltroFacultad.value) {
    try {
      exportCarreras.value =
        await fetchCarrerasByFacultad(
          exportFiltroFacultad.value
        );
    } catch (error) {
      console.error(
        "Error cargando carreras para exportación:",
        error
      );

      exportCarreras.value = [];
    }
  }

  if (exportFiltroCarrera.value) {
    try {
      exportProyectos.value =
        await fetchProyectosByCarrera(
          exportFiltroCarrera.value
        );
    } catch (error) {
      console.error(
        "Error cargando proyectos para exportación:",
        error
      );

      exportProyectos.value = [];
    }
  }
}

/* ============================================================
  CATÁLOGOS DEPENDIENTES PRINCIPALES
============================================================ */

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
  CATÁLOGOS DEPENDIENTES DE EXPORTACIÓN
============================================================ */

async function onExportFacultadChange() {
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";

  exportCarreras.value = [];
  exportProyectos.value = [];

  if (!exportFiltroFacultad.value) {
    return;
  }

  try {
    exportCarreras.value =
      await fetchCarrerasByFacultad(
        exportFiltroFacultad.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras para exportación:",
      error
    );

    exportCarreras.value = [];
  }
}

async function onExportCarreraChange() {
  exportFiltroProyecto.value = "";
  exportProyectos.value = [];

  if (!exportFiltroCarrera.value) {
    return;
  }

  try {
    exportProyectos.value =
      await fetchProyectosByCarrera(
        exportFiltroCarrera.value
      );
  } catch (error) {
    console.error(
      "Error cargando proyectos para exportación:",
      error
    );

    exportProyectos.value = [];
  }
}

/* ============================================================
  CONSTRUCCIÓN DE PARÁMETROS DE EXPORTACIÓN
============================================================ */

function buildParamsFromState({
  tipo,
  anio,
  anioDesde,
  anioHasta,
  texto,
  facultad,
  carrera,
  proyecto,
}) {
  const params = new URLSearchParams();

  if (
    tipo &&
    tipo !== TIPOS.ALL.value
  ) {
    params.append("tipo", tipo);
  }

  if (anio) {
    params.append("anio", anio);
  } else {
    if (anioDesde) {
      params.append("anio_desde", anioDesde);
    }

    if (anioHasta) {
      params.append("anio_hasta", anioHasta);
    }
  }

  if (texto?.trim()) {
    params.append("texto", texto.trim());
  }

  if (facultad) {
    params.append("facultad", facultad);
  }

  if (carrera) {
    params.append("carrera", carrera);
  }

  if (proyecto) {
    params.append("proyecto", proyecto);
  }

  return params;
}

/* ============================================================
  EXPORTACIÓN EXCEL
============================================================ */

async function confirmarExportacion() {
  exporting.value = true;
  exportErrorMsg.value = "";

  try {
    const params = buildParamsFromState({
      tipo: exportFiltroTipo.value,
      anio: exportFiltroAnio.value,
      anioDesde:
        exportFiltroAnioDesde.value,
      anioHasta:
        exportFiltroAnioHasta.value,
      texto: exportFiltroTexto.value,
      facultad:
        exportFiltroFacultad.value,
      carrera:
        exportFiltroCarrera.value,
      proyecto:
        exportFiltroProyecto.value,
    });

    const query = params.toString();

    const endpoint = query
      ? `/reportes/publicaciones/excel/?${query}`
      : "/reportes/publicaciones/excel/";

    const response = await api.get(endpoint, {
      responseType: "blob",
    });

    const blob = new Blob(
      [response.data],
      {
        type:
          "application/vnd.openxmlformats-" +
          "officedocument.spreadsheetml.sheet",
      }
    );

    const url =
      window.URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    const timestamp = new Date()
      .toISOString()
      .slice(0, 19)
      .replace(/[:T]/g, "-");

    link.href = url;

    link.setAttribute(
      "download",
      `reporte_publicaciones_${timestamp}.xlsx`
    );

    document.body.appendChild(link);

    link.click();
    link.remove();

    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error(
      "Error exportando Excel:",
      error
    );

    exportErrorMsg.value =
      extractErrorMessage(
        error,
        "No se pudo generar el archivo Excel."
      );
  } finally {
    exporting.value = false;
  }
}

/* ============================================================
  NAVEGACIÓN AL DETALLE
============================================================ */

function verDetalles(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}`,
    query: {
      from: "publicaciones",
    },
  });
}

/* ============================================================
  ATAJOS DE TECLADO
============================================================ */

function handleGlobalKeydown(event) {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform
      .toLowerCase()
      .includes("mac");

  const key = String(
    event.key || ""
  ).toLowerCase();

  const searchShortcut =
    (isMac &&
      event.metaKey &&
      key === "k") ||
    (!isMac &&
      event.ctrlKey &&
      key === "k");

  if (searchShortcut) {
    event.preventDefault();
    focusSearch();
  }

  if (
    event.key === "Escape" &&
    hayBusqueda.value
  ) {
    filtroTexto.value = "";
  }
}

/* ============================================================
  WATCHERS
============================================================ */

watch(filtroAnio, (value) => {
  if (value) {
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  }
});

watch(
  [filtroAnioDesde, filtroAnioHasta],
  ([desde, hasta]) => {
    if (desde || hasta) {
      filtroAnio.value = "";
    }
  }
);

watch(exportFiltroAnio, (value) => {
  if (value) {
    exportFiltroAnioDesde.value = "";
    exportFiltroAnioHasta.value = "";
  }
});

watch(
  [
    exportFiltroAnioDesde,
    exportFiltroAnioHasta,
  ],
  ([desde, hasta]) => {
    if (desde || hasta) {
      exportFiltroAnio.value = "";
    }
  }
);

/* ============================================================
  CICLO DE VIDA
============================================================ */

onMounted(async () => {
  window.addEventListener(
    "keydown",
    handleGlobalKeydown
  );

  loading.value = true;
  errorMsg.value = "";

  try {
    await Promise.all([
      loadPublicaciones(),
      loadFacultades(),
    ]);
  } catch (error) {
    console.error(
      "Error cargando publicaciones:",
      error
    );

    errorMsg.value =
      extractErrorMessage(
        error,
        "No se pudieron cargar las publicaciones."
      );
  } finally {
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    handleGlobalKeydown
  );
});
</script>

<style src="./sgpc-listados-base.css"></style>
<style src="./listado-publicaciones.css"></style>