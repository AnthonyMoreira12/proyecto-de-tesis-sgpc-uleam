<template>
  <div class="pr-page">
    <div class="pr-shell">
      <header
        class="pr-context page-stage page-stage-1"
        :aria-label="mensajesVista.heroAriaLabel"
      >
        <div class="pr-context__main">
          <h1 class="pr-context__title">
            Proyectos
          </h1>
        </div>

      </header>

      <section
        class="pr-toolbar page-stage page-stage-2"
        :aria-label="mensajesVista.toolbarAriaLabel"
      >
        <div
          class="pr-toolbar__filters"
          :class="{ 'pr-toolbar__filters--no-estado': !esAdmin }"
        >
          <label
            class="pr-field pr-field--search"
            :aria-label="mensajesVista.busquedaAriaLabel"
          >
            <span class="pr-field__icon" aria-hidden="true">⌕</span>

            <input
              v-model="searchQuery"
              type="text"
              class="pr-control"
              :placeholder="placeholderBusqueda"
            />

            <button
              v-if="searchQuery"
              class="pr-clear"
              type="button"
              @click="searchQuery = ''"
              aria-label="Limpiar búsqueda"
              title="Limpiar"
            >
              ✕
            </button>
          </label>

          <label class="pr-field pr-field--sm pr-field--select">
            <span class="pr-sr-only">Filtrar por sede</span>
            <select
              v-model="filtroSede"
              class="pr-control pr-control--native"
              :disabled="loadingSedes"
              aria-label="Filtrar proyectos por sede"
            >
              <option value="">
                {{ loadingSedes ? "Cargando sedes..." : "Todas las sedes" }}
              </option>
              <option
                v-for="sede in sedes"
                :key="sede.id"
                :value="String(sede.id)"
              >
                {{ sede.nombre }}
              </option>
            </select>
          </label>

          <div
            ref="dropdownAnioRef"
            class="pr-field pr-field--sm pr-field--dropdown"
            :class="{ 'is-open': dropdownAnioAbierto }"
          >
            <button
              type="button"
              class="pr-control pr-control--button"
              :disabled="loadingAnios"
              :aria-expanded="dropdownAnioAbierto ? 'true' : 'false'"
              aria-haspopup="listbox"
              aria-label="Filtrar por año"
              @click="toggleDropdownAnio"
            >
              <span
                class="pr-control__value"
                :class="{ 'is-placeholder': !filtroAnio }"
              >
                {{ textoFiltroAnio }}
              </span>
            </button>

            <span class="pr-field__chevron" aria-hidden="true">⌄</span>

            <transition name="dropdown-fade">
              <div
                v-if="dropdownAnioAbierto"
                class="pr-dropdown"
                role="listbox"
                aria-label="Opciones de año"
              >
                <button
                  type="button"
                  class="pr-dropdown__option"
                  :class="{ 'is-selected': filtroAnio === '' }"
                  @click="seleccionarAnio('')"
                >
                  Todos los años
                </button>

                <template v-if="listaAnios.length">
                  <button
                    v-for="anio in listaAnios"
                    :key="anio"
                    type="button"
                    class="pr-dropdown__option"
                    :class="{ 'is-selected': filtroAnio === String(anio) }"
                    @click="seleccionarAnio(String(anio))"
                  >
                    {{ anio }}
                  </button>
                </template>

                <div v-else class="pr-dropdown__empty">
                  No hay años disponibles
                </div>
              </div>
            </transition>
          </div>

          <div
            v-if="esAdmin"
            ref="dropdownEstadoRef"
            class="pr-field pr-field--sm pr-field--dropdown"
            :class="{ 'is-open': dropdownEstadoAbierto }"
          >
            <button
              type="button"
              class="pr-control pr-control--button"
              :aria-expanded="dropdownEstadoAbierto ? 'true' : 'false'"
              aria-haspopup="listbox"
              aria-label="Filtrar por estado"
              @click="toggleDropdownEstado"
            >
              <span
                class="pr-control__value"
                :class="{ 'is-placeholder': !filtroEstado }"
              >
                {{ textoFiltroEstado }}
              </span>
            </button>

            <span class="pr-field__chevron" aria-hidden="true">⌄</span>

            <transition name="dropdown-fade">
              <div
                v-if="dropdownEstadoAbierto"
                class="pr-dropdown"
                role="listbox"
                aria-label="Opciones de estado"
              >
                <button
                  type="button"
                  class="pr-dropdown__option"
                  :class="{ 'is-selected': filtroEstado === '' }"
                  @click="seleccionarEstado('')"
                >
                  Todos los estados
                </button>

                <button
                  v-for="opcion in estadoOptions"
                  :key="opcion.value"
                  type="button"
                  class="pr-dropdown__option"
                  :class="{ 'is-selected': filtroEstado === opcion.value }"
                  @click="seleccionarEstado(opcion.value)"
                >
                  {{ opcion.label }}
                </button>
              </div>
            </transition>
          </div>
        </div>

        <div class="pr-toolbar__actions">
          <button
            v-if="filtrosActivosCount"
            class="pr-btn pr-btn--ghost"
            type="button"
            @click="limpiarFiltros"
          >
            Limpiar filtros
          </button>

          <button
            v-if="errorProyectos"
            class="pr-btn pr-btn--ghost"
            type="button"
            @click="recargarProyectos"
          >
            Reintentar
          </button>

          <button
            v-if="esAdmin"
            class="pr-btn pr-btn--primary"
            type="button"
            @click="irANuevoProyecto"
          >
            Nuevo proyecto
          </button>
        </div>
      </section>

      <div
        v-if="feedbackMessage"
        class="pr-feedback page-stage page-stage-3"
        :class="`pr-feedback--${feedbackType}`"
        :role="feedbackType === 'error' ? 'alert' : 'status'"
      >
        {{ feedbackMessage }}
      </div>

      <section
        class="pr-card page-stage page-stage-3"
        :aria-busy="loadingProyectos"
      >
        <div class="pr-card-head">
          <div class="pr-card-meta">
            <span>
              <strong class="pr-card-meta__count">{{ totalRegistros }}</strong>
              {{ totalRegistros === 1 ? "proyecto encontrado" : "proyectos encontrados" }}
            </span>
          </div>
        </div>

        <div
          v-if="initialProjectsLoading"
          class="pr-state pr-state--loading"
          role="status"
        >
          {{ mensajesVista.loading }}
        </div>

        <div
          v-if="refreshingProjects"
          class="pr-refresh-state"
          role="status"
          aria-live="polite"
        >
          <span class="pr-refresh-state__spinner" aria-hidden="true"></span>
          <span>Actualizando proyectos…</span>
        </div>

        <div
          v-if="errorProyectos && !proyectos.length"
          class="pr-state pr-state--error"
          role="alert"
        >
          {{ errorProyectos }}
        </div>

        <div
          v-if="errorProyectos && proyectos.length"
          class="pr-refresh-error"
          role="status"
        >
          No pudimos actualizar la lista. Se mantienen los últimos proyectos disponibles.
        </div>

        <div
          v-if="!initialProjectsLoading && !errorProyectos && proyectosFiltrados.length === 0"
          class="pr-state pr-state--empty"
          role="status"
        >
          {{ mensajesVista.empty }}
        </div>

        <div
          v-if="proyectosFiltrados.length"
          class="pr-results-grid"
          :aria-label="mensajesVista.tablaAriaLabel"
        >
          <article
            v-for="p in proyectosFiltrados"
            :key="p.id"
            class="pr-project-card"
            :data-estado="p.estado || 'nuevo'"
          >
            <header class="pr-project-card__head">
              <div class="pr-project-card__badges">
                <span
                  class="pr-badge"
                  :class="estadoBadgeClass(p.estado)"
                  :data-estado="p.estado || 'nuevo'"
                >
                  {{ labelEstadoProyecto(p.estado) }}
                </span>

                <span class="pr-year">
                  {{ periodoProyecto(p) }}
                </span>
              </div>

              <span class="pr-project-card__end">
                Finaliza {{ fechaFinalProyecto(p) }}
              </span>
            </header>

            <div class="pr-project-card__body">
              <h3
                class="pr-project-card__title"
                :title="p.nombre || 'Proyecto'"
              >
                {{ p.nombre || "Proyecto" }}
              </h3>

              <p
                v-if="p.descripcion"
                class="pr-project-card__description"
              >
                {{ truncateText(p.descripcion, 120) }}
              </p>

              <div class="pr-project-card__meta">
                <div class="pr-project-card__meta-block">
                  <span class="pr-project-card__label">
                    Unidad académica
                  </span>

                  <strong :title="p.carrera_nombre || '—'">
                    {{ p.carrera_nombre || "—" }}
                  </strong>

                  <span :title="p.facultad || '—'">
                    {{ p.facultad || "—" }}
                  </span>

                  <span class="pr-location-site">
                    {{ p.sede_nombre || "Sin sede" }}
                  </span>
                </div>

                <div class="pr-project-card__meta-block">
                  <span class="pr-project-card__label">
                    Profesores
                  </span>

                  <div
                    v-if="autoresResumen(p).length"
                    class="pr-project-card__authors"
                  >
                    <span
                      v-for="autor in autoresResumen(p).slice(0, 3)"
                      :key="autor.id"
                      class="pr-author-chip"
                      :title="autor.nombre"
                    >
                      {{ autor.nombre }}
                    </span>

                    <span
                      v-if="autoresResumen(p).length > 3"
                      class="pr-author-chip pr-author-chip--more"
                    >
                      +{{ autoresResumen(p).length - 3 }}
                    </span>
                  </div>

                  <span v-else class="pr-muted-text">
                    Sin profesores
                  </span>

                  <span
                    v-if="
                      autoresResumen(p).length &&
                      !tieneInvestigadorPrincipal(p)
                    "
                    class="pr-muted-text"
                  >
                    Sin investigador principal
                  </span>
                </div>
              </div>
            </div>

            <footer class="pr-project-card__footer">
              <a
                v-if="p.archivo_pdf_url"
                class="pr-pdf-link"
                :href="p.archivo_pdf_url"
                target="_blank"
                rel="noopener noreferrer"
              >
                PDF
              </a>

              <span v-else class="pr-muted-text">
                Sin documento
              </span>

              <div v-if="esAdmin" class="pr-actions">
                <button
                  class="pr-btn-mini"
                  type="button"
                  :disabled="processingProjectId === p.id || savingExtension"
                  @click="editarProyecto(p)"
                >
                  Editar
                </button>

                <details class="pr-more-menu">
                  <summary class="pr-btn-mini pr-btn-mini--more">
                    Más
                    <span aria-hidden="true">⌄</span>
                  </summary>

                  <div class="pr-more-menu__panel">
                    <button
                      type="button"
                      :disabled="
                        loadingProduccionProyecto &&
                        proyectoProduccion?.id === p.id
                      "
                      @click="abrirProduccionProyecto(p)"
                    >
                      Ver producción
                    </button>

                    <button
                      v-if="puedeExtenderProyecto(p)"
                      type="button"
                      :disabled="
                        processingProjectId === p.id ||
                        savingExtension
                      "
                      @click="abrirExtensionFecha(p)"
                    >
                      Extender plazo
                    </button>

                    <button
                      type="button"
                      :class="estadoActionClass(p.estado)"
                      :disabled="
                        processingProjectId === p.id ||
                        savingExtension ||
                        !puedeCambiarEstado(p)
                      "
                      :title="tituloAccionEstado(p)"
                      @click="cambiarEstado(p)"
                    >
                      {{
                        processingProjectId === p.id
                          ? "Actualizando estado…"
                          : textoAccionEstado(p.estado)
                      }}
                    </button>
                  </div>
                </details>
              </div>

              <button
                v-else
                class="pr-btn-mini"
                type="button"
                :disabled="
                  loadingProduccionProyecto &&
                  proyectoProduccion?.id === p.id
                "
                @click="abrirProduccionProyecto(p)"
              >
                Ver producción
              </button>
            </footer>
          </article>
        </div>

        <footer
          v-if="!errorProyectos && totalPaginas > 1"
          class="pr-pagination"
          aria-label="Paginación de proyectos"
        >
          <button
            class="pr-btn pr-btn--ghost"
            type="button"
            :disabled="loadingProyectos || !puedeIrAnterior"
            @click="paginaAnterior"
          >
            Anterior
          </button>

          <span class="pr-pagination__info">
            Página <strong>{{ paginaActual }}</strong> de
            <strong>{{ totalPaginas }}</strong>
          </span>

          <button
            class="pr-btn pr-btn--ghost"
            type="button"
            :disabled="loadingProyectos || !puedeIrSiguiente"
            @click="paginaSiguiente"
          >
            Siguiente
          </button>
        </footer>
      </section>
    </div>

    <Teleport to="body">
    <div
      v-if="produccionModalAbierto"
      class="pr-prod-overlay"
      role="presentation"
      @mousedown.self="cerrarProduccionProyecto"
    >
      <section
        class="pr-prod-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pr-prod-title"
      >
        <header class="pr-prod-head">
          <div>
            <h2 id="pr-prod-title" class="pr-prod-title">
              {{ proyectoProduccion?.nombre || "Proyecto" }}
            </h2>
            <p class="pr-prod-subtitle">
              {{ produccionProyectoLocation }}
            </p>
          </div>
          <button
            type="button"
            class="pr-ext-close"
            @click="cerrarProduccionProyecto"
            aria-label="Cerrar información del proyecto"
          >
            ✕
          </button>
        </header>

        <div class="pr-prod-body">
          <div v-if="loadingProduccionProyecto" class="pr-production__state">
            Cargando información...
          </div>

          <div
            v-else-if="errorProduccionProyecto"
            class="pr-production__state pr-production__state--error"
            role="alert"
          >
            {{ errorProduccionProyecto }}
            <button type="button" class="pr-link-action" @click="recargarProduccionProyecto">
              Reintentar
            </button>
          </div>

          <template v-else-if="produccionProyectoData">
            <div class="pr-prod-metrics">
              <article><span>Total</span><strong>{{ produccionResumen.total_publicaciones }}</strong></article>
              <article><span>Aprobadas</span><strong>{{ produccionResumen.aprobada }}</strong></article>
              <article><span>En revisión</span><strong>{{ produccionResumen.en_revision }}</strong></article>
              <article><span>Observadas</span><strong>{{ produccionResumen.observada }}</strong></article>
              <article><span>Rechazadas</span><strong>{{ produccionResumen.rechazada }}</strong></article>
              <article><span>Cobertura PDF</span><strong>{{ formatPercent(produccionResumen.cobertura_pdf) }}</strong></article>
            </div>

            <div class="pr-prod-grid">
              <article class="pr-prod-section">
                <header><h3>Producción por tipo</h3></header>
                <div v-if="produccionPorTipo.length" class="pr-prod-table-wrap">
                  <table class="pr-prod-table">
                    <thead><tr><th>Tipo</th><th>Total</th><th>Aprobadas</th></tr></thead>
                    <tbody>
                      <tr v-for="item in produccionPorTipo" :key="item.tipo_id || item.codigo">
                        <td>{{ item.nombre || item.codigo || "Sin tipo" }}</td>
                        <td>{{ item.total }}</td>
                        <td>{{ item.aprobadas }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-else class="pr-production-empty">Sin datos por tipo.</p>
              </article>

              <article class="pr-prod-section">
                <header><h3>Evolución anual</h3></header>
                <div v-if="produccionPorAnio.length" class="pr-prod-table-wrap">
                  <table class="pr-prod-table">
                    <thead><tr><th>Año</th><th>Total</th><th>Aprobadas</th><th>Observadas</th></tr></thead>
                    <tbody>
                      <tr v-for="item in produccionPorAnio" :key="item.anio">
                        <td>{{ item.anio }}</td>
                        <td>{{ item.total }}</td>
                        <td>{{ item.aprobadas }}</td>
                        <td>{{ item.observadas }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-else class="pr-production-empty">Sin datos por año.</p>
              </article>
            </div>

            <article class="pr-prod-section">
              <header>
                <h3>Autores</h3>
                <span>{{ produccionAutores.length }}</span>
              </header>
              <div v-if="produccionAutores.length" class="pr-prod-authors">
                <div v-for="autor in produccionAutores" :key="autor.autor_id">
                  <span>
                    <strong>{{ autor.nombre_completo || "Autor" }}</strong>
                    <small>{{ autor.institucion || autor.correo || "Sin institución" }}</small>
                  </span>
                  <span>
                    <strong>{{ autor.total_publicaciones }}</strong>
                    <small>{{ autor.aprobadas }} aprobadas</small>
                  </span>
                </div>
              </div>
              <p v-else class="pr-production-empty">Sin autores.</p>
            </article>
          </template>
        </div>
      </section>
    </div>

    <div
      v-if="extensionModalAbierto"
      class="pr-ext-overlay"
      role="presentation"
      @mousedown.self="cerrarExtensionFecha"
    >
      <section
        class="pr-ext-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pr-ext-title"
      >
        <header class="pr-ext-head">
          <div>
            <h2 id="pr-ext-title" class="pr-ext-title">
              Extender fecha final
            </h2>

            <p class="pr-ext-subtitle">
              {{ proyectoExtension?.nombre || "Proyecto seleccionado" }}
            </p>
          </div>

          <button
            type="button"
            class="pr-ext-close"
            :disabled="savingExtension"
            @click="cerrarExtensionFecha"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </header>

        <div class="pr-ext-body">
          <label class="pr-ext-field" for="extension-fecha">
            <span>Nueva fecha de finalización</span>

            <input
              id="extension-fecha"
              v-model="extensionFecha"
              type="date"
              :min="extensionFechaMin || undefined"
              :disabled="savingExtension || Boolean(extensionSuccess)"
            />
          </label>

          <p v-if="extensionError" class="pr-ext-error" role="alert">
            {{ extensionError }}
          </p>

          <div
            v-if="extensionSuccess"
            class="pr-ext-success"
            role="status"
            aria-live="polite"
          >
            <span class="pr-ext-success__icon" aria-hidden="true">✓</span>

            <div>
              <strong>Fecha final actualizada</strong>
              <p>{{ extensionSuccess }}</p>
            </div>
          </div>
        </div>

        <footer class="pr-ext-actions">
          <template v-if="extensionSuccess">
            <button
              type="button"
              class="pr-btn pr-btn--primary"
              @click="cerrarExtensionFecha"
            >
              Cerrar
            </button>
          </template>

          <template v-else>
            <button
              type="button"
              class="pr-btn pr-btn--ghost"
              :disabled="savingExtension"
              @click="cerrarExtensionFecha"
            >
              Cancelar
            </button>

            <button
              type="button"
              class="pr-btn pr-btn--primary"
              :disabled="savingExtension"
              @click="confirmarExtensionFecha"
            >
              {{ savingExtension ? "Guardando plazo…" : "Guardar" }}
            </button>
          </template>
        </footer>
      </section>
    </div>
    </Teleport>
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

import {
  cambiarEstadoProyecto,
  compararProduccionProyectos,
  consultarAniosProyectos,
  consultarSedesProyecto,
  extenderFechaProyecto,
  getProyectoApiErrorMessage,
  listarProyectos,
  obtenerProduccionProyecto,
} from "../../scripts/api/proyectosApi";

import {
  useUserStore,
} from "../../scripts/stores/userStore";


/* ============================================================
   ENLACES BASE
============================================================ */

const route =
  useRoute();

const router =
  useRouter();

const userStore =
  useUserStore();


/* ============================================================
   CONFIGURACIÓN
============================================================ */

const PAGE_SIZE = 20;
const MIN_PROJECT_YEAR = 1900;
const MAX_PROJECT_FUTURE_YEARS = 50;


/* ============================================================
   SESIÓN Y PERMISOS
============================================================ */

const esAdmin =
  computed(
    () => Boolean(
      userStore.isAdmin
    )
  );


/* ============================================================
   MENSAJES SEGÚN ROL
============================================================ */

const mensajesVista =
  computed(
    () => (
      esAdmin.value
        ? {
            heroAriaLabel:
              "Administración de proyectos",

            eyebrow:
              "Proyectos",

            titulo:
              "Proyectos",

            subtitulo:
              "Proyectos institucionales.",

            toolbarAriaLabel:
              "Filtros y acciones",

            busquedaAriaLabel:
              "Buscar proyecto",

            cardTitulo:
              "Proyectos",

            tablaAriaLabel:
              "Lista de proyectos",

            loading:
              "Cargando proyectos...",

            empty:
              "Sin proyectos para estos filtros.",

            placeholderBusqueda:
              "Buscar proyectos",
          }
        : {
            heroAriaLabel:
              "Consulta de proyectos",

            eyebrow:
              "Proyectos",

            titulo:
              "Consulta de proyectos",

            subtitulo:
              "Proyectos institucionales.",

            toolbarAriaLabel:
              "Filtros de consulta",

            busquedaAriaLabel:
              "Buscar proyecto",

            cardTitulo:
              "Proyectos registrados",

            tablaAriaLabel:
              "Lista de proyectos",

            loading:
              "Cargando proyectos...",

            empty:
              "Sin proyectos para estos filtros.",

            placeholderBusqueda:
              "Buscar proyectos",
          }
    )
  );


/* ============================================================
   ESTADO PRINCIPAL
============================================================ */

const proyectos =
  ref([]);

const loadingProyectos =
  ref(false);

const errorProyectos =
  ref("");

const hasLoadedProjects =
  ref(false);

const initialProjectsLoading =
  computed(
    () =>
      loadingProyectos.value &&
      !hasLoadedProjects.value &&
      proyectos.value.length === 0
  );

const refreshingProjects =
  computed(
    () =>
      loadingProyectos.value &&
      hasLoadedProjects.value
  );


/* ============================================================
   FILTROS
============================================================ */

const searchQuery =
  ref("");

const debouncedSearch =
  ref("");

const filtroSede =
  ref("");

const sedes =
  ref([]);

const loadingSedes =
  ref(false);

const filtroAnio =
  ref("");

const filtroEstado =
  ref("");

const listaAnios =
  ref([]);

const loadingAnios =
  ref(false);


/* ============================================================
   PRODUCCIÓN CIENTÍFICA
============================================================ */

const comparativaProduccion =
  ref(null);

const loadingComparativa =
  ref(false);

const errorComparativa =
  ref("");

const produccionModalAbierto =
  ref(false);

const proyectoProduccion =
  ref(null);

const produccionProyectoData =
  ref(null);

const loadingProduccionProyecto =
  ref(false);

const errorProduccionProyecto =
  ref("");


/* ============================================================
   PAGINACIÓN
============================================================ */

const totalRegistros =
  ref(0);

const paginaActual =
  ref(1);


/* ============================================================
   MODAL DE EXTENSIÓN
============================================================ */

const extensionModalAbierto =
  ref(false);

const proyectoExtension =
  ref(null);

const extensionFecha =
  ref("");

const extensionError =
  ref("");

const extensionSuccess =
  ref("");

const savingExtension =
  ref(false);


/* ============================================================
   FEEDBACK Y OPERACIONES
============================================================ */

const feedbackMessage =
  ref("");

const feedbackType =
  ref("info");

const processingProjectId =
  ref(null);


/* ============================================================
   DROPDOWNS
============================================================ */

const dropdownAnioAbierto =
  ref(false);

const dropdownEstadoAbierto =
  ref(false);

const dropdownAnioRef =
  ref(null);

const dropdownEstadoRef =
  ref(null);


/* ============================================================
   CONTROL INTERNO
============================================================ */

let searchTimer = null;
let feedbackTimer = null;
let abortController = null;
let yearsAbortController = null;
let sitesAbortController = null;
let comparisonAbortController = null;
let productionAbortController = null;
let suspendFilterWatchers = false;


/* ============================================================
   OPCIONES
============================================================ */

const estadoOptions = [
  {
    value: "nuevo",
    label: "Nuevo",
  },
  {
    value: "arrastre",
    label: "Arrastre",
  },
  {
    value: "cierre",
    label: "Cierre",
  },
];


/* ============================================================
   HELPERS GENERALES
============================================================ */

function setFeedback(
  message = "",
  type = "info"
) {
  feedbackMessage.value =
    message;

  feedbackType.value =
    type;

  clearTimeout(
    feedbackTimer
  );

  if (
    message
  ) {
    feedbackTimer =
      setTimeout(
        () => {
          feedbackMessage.value =
            "";
        },
        4200
      );
  }
}


function sanitizeQuery(
  value
) {
  return String(
    value || ""
  ).trim();
}


function normalizeEstado(
  value
) {
  return String(
    value || "nuevo"
  )
    .trim()
    .toLowerCase();
}


function normalizeDate(
  value
) {
  if (
    !value
  ) {
    return "";
  }

  return String(
    value
  ).slice(
    0,
    10
  );
}


function addDaysToDate(
  value,
  days
) {
  const normalized =
    normalizeDate(
      value
    );

  if (
    !normalized
  ) {
    return "";
  }

  const date =
    new Date(
      `${normalized}T00:00:00`
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  date.setDate(
    date.getDate()
    + Number(
      days || 0
    )
  );

  return date
    .toISOString()
    .slice(
      0,
      10
    );
}


function formatFecha(
  value
) {
  const normalized =
    normalizeDate(
      value
    );

  if (
    !normalized
  ) {
    return "—";
  }

  const date =
    new Date(
      `${normalized}T00:00:00`
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return normalized;
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      year: "numeric",
      month: "short",
      day: "2-digit",
    }
  ).format(
    date
  );
}


function truncateText(
  value,
  max = 96
) {
  const text =
    String(
      value || ""
    ).trim();

  if (
    text.length <= max
  ) {
    return text;
  }

  return (
    `${text.slice(
      0,
      max
    ).trim()}…`
  );
}


function extractProjectPayload(
  payload
) {
  if (
    !payload
  ) {
    return null;
  }

  if (
    payload?.id
  ) {
    return payload;
  }

  if (
    payload?.proyecto?.id
  ) {
    return payload.proyecto;
  }

  if (
    payload?.data?.id
  ) {
    return payload.data;
  }

  return null;
}


function updateProjectInCurrentPage(
  project
) {
  if (
    !project?.id
  ) {
    return false;
  }

  const index =
    proyectos.value.findIndex(
      (item) => (
        item.id
        === project.id
      )
    );

  if (
    index === -1
  ) {
    return false;
  }

  proyectos.value[
    index
  ] = {
    ...proyectos.value[
      index
    ],
    ...project,
  };

  return true;
}


function buildFallbackYears() {
  const currentYear =
    new Date().getFullYear();

  const maximumYear = (
    currentYear
    + MAX_PROJECT_FUTURE_YEARS
  );

  const years = [];

  for (
    let year = maximumYear;
    year >= MIN_PROJECT_YEAR;
    year -= 1
  ) {
    years.push(
      year
    );
  }

  return years;
}


function normalizeYears(
  payload
) {
  const source = (
    Array.isArray(
      payload
    )
      ? payload
      : (
        Array.isArray(
          payload?.results
        )
          ? payload.results
          : []
      )
  );

  const maximumYear = (
    new Date().getFullYear()
    + MAX_PROJECT_FUTURE_YEARS
  );

  return [
    ...new Set(
      source
        .map(
          (item) => Number(
            item
          )
        )
        .filter(
          (item) => (
            Number.isInteger(
              item
            )
            && item
            >= MIN_PROJECT_YEAR
            && item
            <= maximumYear
          )
        )
    ),
  ].sort(
    (
      first,
      second
    ) => (
      second
      - first
    )
  );
}


function labelEstadoProyecto(
  estado
) {
  const normalized =
    normalizeEstado(
      estado
    );

  const option =
    estadoOptions.find(
      (item) => (
        item.value
        === normalized
      )
    );

  return (
    option?.label
    || "Nuevo"
  );
}


function estadoBadgeClass(
  estado
) {
  const normalized =
    normalizeEstado(
      estado
    );

  return {
    "pr-badge-new":
      normalized === "nuevo",

    "pr-badge-progress":
      normalized === "arrastre",

    "pr-badge-closed":
      normalized === "cierre",
  };
}


function estadoActionClass(
  estado
) {
  const normalized =
    normalizeEstado(
      estado
    );

  return {
    success: (
      normalized === "nuevo"
      || normalized === "cierre"
    ),

    danger:
      normalized === "arrastre",
  };
}


function textoAccionEstado(
  estado
) {
  const normalized =
    normalizeEstado(
      estado
    );

  if (
    normalized === "nuevo"
  ) {
    return "Pasar a arrastre";
  }

  if (
    normalized === "arrastre"
  ) {
    return "Cerrar";
  }

  if (
    normalized === "cierre"
  ) {
    return "Reabrir";
  }

  return "Cambiar estado";
}


function periodoProyecto(
  proyecto
) {
  const inicio =
    proyecto?.anio_inicio;

  const fin =
    proyecto?.anio_fin;

  if (
    inicio
    && fin
  ) {
    return `${inicio} - ${fin}`;
  }

  if (
    inicio
  ) {
    return `Desde ${inicio}`;
  }

  if (
    fin
  ) {
    return `Hasta ${fin}`;
  }

  return "—";
}


function fechaFinalProyecto(
  proyecto
) {
  return formatFecha(
    proyecto?.fecha_fin_vigente
    || proyecto?.fecha_fin_prorrogada
    || proyecto?.fecha_cierre
    || proyecto?.fecha_fin_planificada
  );
}


function autoresResumen(
  proyecto
) {
  const source = (
    Array.isArray(
      proyecto?.autores_resumen
    )
      ? proyecto.autores_resumen
      : (
        Array.isArray(
          proyecto?.autores
        )
          ? proyecto.autores
          : []
      )
  );

  return source
    .map(
      (item) => {
        const id = (
          item.id
          || item.autor_id
          || item.autor
        );

        const nombre = (
          item.nombre
          || item.nombre_completo
          || (
            `${item.nombres || ""} `
            + `${item.apellidos || ""}`
          ).trim()
        );

        return {
          id,

          nombre: (
            nombre
            || `Autor #${id}`
          ),

          rol:
            item.rol,

          rol_label:
            item.rol_label,

          orden:
            item.orden,
        };
      }
    )
    .filter(
      (item) => Boolean(
        item.id
      )
    )
    .sort(
      (
        first,
        second
      ) => (
        Number(
          first.orden || 0
        )
        - Number(
          second.orden || 0
        )
      )
    );
}


function tieneInvestigadorPrincipal(
  proyecto
) {
  if (
    typeof proyecto
      ?.tiene_investigador_principal
    === "boolean"
  ) {
    return proyecto
      .tiene_investigador_principal;
  }

  return autoresResumen(
    proyecto
  ).some(
    (autor) => (
      String(
        autor.rol || ""
      ).toLowerCase()
      === "principal"
      && Number(
        autor.orden || 0
      ) === 1
    )
  );
}


function puedeExtenderProyecto(
  proyecto
) {
  return (
    normalizeEstado(
      proyecto?.estado
    )
    !== "cierre"
  );
}


function puedeCambiarEstado(
  proyecto
) {
  const estado =
    normalizeEstado(
      proyecto?.estado
    );

  if (
    estado === "arrastre"
  ) {
    return tieneInvestigadorPrincipal(
      proyecto
    );
  }

  return [
    "nuevo",
    "cierre",
  ].includes(
    estado
  );
}


function tituloAccionEstado(
  proyecto
) {
  const estado =
    normalizeEstado(
      proyecto?.estado
    );

  if (
    estado === "arrastre"
    && !tieneInvestigadorPrincipal(
      proyecto
    )
  ) {
    return (
      "No se puede cerrar el proyecto porque no tiene "
      + "un investigador principal en el orden 1."
    );
  }

  return textoAccionEstado(
    estado
  );
}


function fechaReferenciaExtension(
  proyecto
) {
  return normalizeDate(
    proyecto?.fecha_fin_vigente
    || proyecto?.fecha_fin_prorrogada
    || proyecto?.fecha_cierre
    || proyecto?.fecha_fin_planificada
    || proyecto?.fecha_inicio
  );
}


function extractCatalogArray(
  payload
) {
  if (
    Array.isArray(
      payload
    )
  ) {
    return payload;
  }

  const candidates = [
    payload?.results,
    payload?.items,
    payload?.data,
  ];

  return (
    candidates.find(
      Array.isArray
    )
    || []
  );
}


function formatMetric(
  value
) {
  const number =
    Number(
      value || 0
    );

  return Number.isFinite(
    number
  )
    ? new Intl.NumberFormat(
        "es-EC",
        {
          maximumFractionDigits: 2,
        }
      ).format(
        number
      )
    : "0";
}


function formatPercent(
  value
) {
  return `${formatMetric(
    value
  )}%`;
}


function productionLocationLabel(
  item
) {
  const values = [
    item?.sede?.nombre,
    item?.facultad?.nombre,
    item?.carrera?.nombre,
  ].filter(Boolean);

  return (
    values.join(
      " · "
    )
    || "Sin información académica"
  );
}


/* ============================================================
   COMPUTEDS
============================================================ */

const placeholderBusqueda =
  computed(
    () => (
      mensajesVista
        .value
        .placeholderBusqueda
    )
  );


const proyectosFiltrados =
  computed(
    () => proyectos.value
  );


const resultadosPagina =
  computed(
    () => (
      proyectosFiltrados
        .value
        .length
    )
  );


const filtrosActivosCount =
  computed(
    () => {
      let total = 0;

      if (
        debouncedSearch.value
      ) {
        total += 1;
      }

      if (
        filtroSede.value
      ) {
        total += 1;
      }

      if (
        filtroAnio.value
      ) {
        total += 1;
      }

      if (
        esAdmin.value
        && filtroEstado.value
      ) {
        total += 1;
      }

      return total;
    }
  );


const textoFiltroAnio =
  computed(
    () => {
      if (
        loadingAnios.value
      ) {
        return "Cargando años...";
      }

      return (
        filtroAnio.value
        || "Todos los años"
      );
    }
  );


const textoFiltroEstado =
  computed(
    () => {
      if (
        !filtroEstado.value
      ) {
        return "Todos los estados";
      }

      const option =
        estadoOptions.find(
          (item) => (
            item.value
            === filtroEstado.value
          )
        );

      return (
        option?.label
        || "Todos los estados"
      );
    }
  );


const comparativaResumen =
  computed(
    () => (
      comparativaProduccion.value?.resumen
      || {}
    )
  );

const rankingProductividad =
  computed(
    () => (
      Array.isArray(
        comparativaProduccion.value?.ranking_productividad
      )
        ? comparativaProduccion.value.ranking_productividad
        : []
    )
  );

const proyectosSinProduccion =
  computed(
    () => (
      Array.isArray(
        comparativaProduccion.value?.proyectos_sin_produccion
      )
        ? comparativaProduccion.value.proyectos_sin_produccion
        : []
    )
  );

const comparativaPorSede =
  computed(
    () => (
      Array.isArray(
        comparativaProduccion.value?.por_sede
      )
        ? comparativaProduccion.value.por_sede
        : []
    )
  );

const produccionResumen =
  computed(
    () => (
      produccionProyectoData.value?.resumen
      || {}
    )
  );

const produccionPorTipo =
  computed(
    () => (
      Array.isArray(
        produccionProyectoData.value?.por_tipo
      )
        ? produccionProyectoData.value.por_tipo
        : []
    )
  );

const produccionPorAnio =
  computed(
    () => (
      Array.isArray(
        produccionProyectoData.value?.por_anio
      )
        ? produccionProyectoData.value.por_anio
        : []
    )
  );

const produccionAutores =
  computed(
    () => (
      Array.isArray(
        produccionProyectoData.value?.autores_produccion
      )
        ? produccionProyectoData.value.autores_produccion
        : []
    )
  );

const produccionProyectoLocation =
  computed(
    () => {
      const project =
        produccionProyectoData.value?.proyecto;

      if (
        project
      ) {
        return productionLocationLabel(
          project
        );
      }

      return [
        proyectoProduccion.value?.sede_nombre,
        proyectoProduccion.value?.facultad,
        proyectoProduccion.value?.carrera_nombre,
      ]
        .filter(Boolean)
        .join(" · ")
        || "Sin información académica";
    }
  );


const totalPaginas =
  computed(
    () => {
      const total =
        Math.ceil(
          totalRegistros.value
          / PAGE_SIZE
        );

      return (
        total > 0
          ? total
          : 1
      );
    }
  );


const puedeIrAnterior =
  computed(
    () => (
      paginaActual.value > 1
    )
  );


const puedeIrSiguiente =
  computed(
    () => (
      paginaActual.value
      < totalPaginas.value
    )
  );


const extensionFechaMin =
  computed(
    () => addDaysToDate(
      fechaReferenciaExtension(
        proyectoExtension.value
      ),
      1
    )
  );


/* ============================================================
   SEDES Y PRODUCCIÓN CIENTÍFICA
============================================================ */

async function cargarSedesDisponibles() {
  sitesAbortController
    ?.abort?.();

  const controller =
    new AbortController();

  sitesAbortController =
    controller;

  loadingSedes.value =
    true;

  try {
    const payload =
      await consultarSedesProyecto({
        signal:
          controller.signal,
      });

    if (
      sitesAbortController
      !== controller
    ) {
      return;
    }

    sedes.value =
      extractCatalogArray(
        payload
      )
        .map(
          (item) => ({
            id:
              item?.id,
            nombre:
              item?.nombre
              || item?.label
              || item?.name
              || "",
          })
        )
        .filter(
          (item) => (
            item.id
            && item.nombre
          )
        );
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
      || error?.name
        === "CanceledError"
    ) {
      return;
    }

    console.error(
      "Error cargando sedes de proyectos:",
      error
    );

    sedes.value = [];
  } finally {
    if (
      sitesAbortController
      === controller
    ) {
      loadingSedes.value =
        false;
    }
  }
}


async function cargarComparativaProduccion() {
  if (
    !esAdmin.value
  ) {
    comparativaProduccion.value =
      null;
    return;
  }

  comparisonAbortController
    ?.abort?.();

  const controller =
    new AbortController();

  comparisonAbortController =
    controller;

  loadingComparativa.value =
    true;

  errorComparativa.value =
    "";

  const params = {
    limite: 5,
  };

  if (
    filtroSede.value
  ) {
    params.sede =
      filtroSede.value;
  }

  if (
    filtroEstado.value
  ) {
    params.estado_proyecto =
      filtroEstado.value;
  }

  if (
    filtroAnio.value
  ) {
    params.anio =
      filtroAnio.value;
  }

  try {
    const payload =
      await compararProduccionProyectos(
        params,
        {
          signal:
            controller.signal,
        }
      );

    if (
      comparisonAbortController
      !== controller
    ) {
      return;
    }

    comparativaProduccion.value =
      payload || {};
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
      || error?.name
        === "CanceledError"
    ) {
      return;
    }

    console.error(
      "Error cargando comparativa de producción:",
      error
    );

    comparativaProduccion.value =
      null;

    errorComparativa.value =
      getProyectoApiErrorMessage(
        error,
        "No pudimos cargar el resumen de producción."
      );
  } finally {
    if (
      comparisonAbortController
      === controller
    ) {
      loadingComparativa.value =
        false;
    }
  }
}


async function cargarProduccionProyecto(
  proyectoId
) {
  if (
    !esAdmin.value
    || !proyectoId
  ) {
    return;
  }

  productionAbortController
    ?.abort?.();

  const controller =
    new AbortController();

  productionAbortController =
    controller;

  loadingProduccionProyecto.value =
    true;

  errorProduccionProyecto.value =
    "";

  try {
    const payload =
      await obtenerProduccionProyecto(
        proyectoId,
        {},
        {
          signal:
            controller.signal,
        }
      );

    if (
      productionAbortController
      !== controller
    ) {
      return;
    }

    produccionProyectoData.value =
      payload || {};
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
      || error?.name
        === "CanceledError"
    ) {
      return;
    }

    console.error(
      "Error cargando producción del proyecto:",
      error
    );

    produccionProyectoData.value =
      null;

    errorProduccionProyecto.value =
      getProyectoApiErrorMessage(
        error,
        "No pudimos cargar la producción del proyecto."
      );
  } finally {
    if (
      productionAbortController
      === controller
    ) {
      loadingProduccionProyecto.value =
        false;
    }
  }
}


async function abrirProduccionProyecto(
  proyecto
) {
  if (
    !proyecto?.id
    || !esAdmin.value
  ) {
    return;
  }

  proyectoProduccion.value =
    proyecto;

  produccionProyectoData.value =
    null;

  errorProduccionProyecto.value =
    "";

  produccionModalAbierto.value =
    true;

  await cargarProduccionProyecto(
    proyecto.id
  );
}


async function abrirProduccionDesdeComparativa(
  item
) {
  if (
    !item?.proyecto_id
  ) {
    return;
  }

  await abrirProduccionProyecto({
    id:
      item.proyecto_id,
    nombre:
      item.nombre,
    sede_nombre:
      item?.sede?.nombre || "",
    facultad:
      item?.facultad?.nombre || "",
    carrera_nombre:
      item?.carrera?.nombre || "",
  });
}


function cerrarProduccionProyecto() {
  productionAbortController
    ?.abort?.();

  produccionModalAbierto.value =
    false;

  proyectoProduccion.value =
    null;

  produccionProyectoData.value =
    null;

  errorProduccionProyecto.value =
    "";
}


async function recargarProduccionProyecto() {
  if (
    proyectoProduccion.value?.id
  ) {
    await cargarProduccionProyecto(
      proyectoProduccion.value.id
    );
  }
}


/* ============================================================
   AÑOS DISPONIBLES
============================================================ */

async function cargarAniosDisponibles() {
  yearsAbortController?.abort?.();

  const currentController =
    new AbortController();

  yearsAbortController =
    currentController;

  loadingAnios.value =
    true;

  try {
    const params = {};

    if (
      filtroSede.value
    ) {
      params.sede =
        filtroSede.value;
    }

    if (
      debouncedSearch.value
    ) {
      params.q =
        debouncedSearch.value;
    }

    if (
      esAdmin.value
      && filtroEstado.value
    ) {
      params.estado =
        filtroEstado.value;
    }

    const payload =
      await consultarAniosProyectos(
        params,
        {
          signal:
            currentController.signal,
        }
      );

    if (
      yearsAbortController
      !== currentController
    ) {
      return;
    }

    const years =
      normalizeYears(
        payload
      );

    listaAnios.value = (
      years.length
        ? years
        : buildFallbackYears()
    );

    if (
      filtroAnio.value
      && !listaAnios.value.some(
        (year) => (
          String(
            year
          )
          === String(
            filtroAnio.value
          )
        )
      )
    ) {
      suspendFilterWatchers =
        true;

      filtroAnio.value =
        "";

      suspendFilterWatchers =
        false;
    }
  } catch (
    error
  ) {
    if (
      error?.name === "CanceledError"
      || error?.code === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error cargando años de proyectos:",
      error
    );

    listaAnios.value =
      buildFallbackYears();
  } finally {
    if (
      yearsAbortController
      === currentController
    ) {
      loadingAnios.value =
        false;
    }
  }
}


async function recargarAniosYProyectosPorFiltros({
  silent = true,
} = {}) {
  await cargarAniosDisponibles();

  await cargarProyectos({
    silent,
  });

}


/* ============================================================
   DROPDOWN AÑO
============================================================ */

function cerrarDropdownAnio() {
  dropdownAnioAbierto.value =
    false;
}


function toggleDropdownAnio() {
  if (
    loadingAnios.value
  ) {
    return;
  }

  dropdownEstadoAbierto.value =
    false;

  dropdownAnioAbierto.value =
    !dropdownAnioAbierto.value;
}


function seleccionarAnio(
  anio
) {
  filtroAnio.value =
    anio;

  cerrarDropdownAnio();
}


/* ============================================================
   DROPDOWN ESTADO
============================================================ */

function cerrarDropdownEstado() {
  dropdownEstadoAbierto.value =
    false;
}


function toggleDropdownEstado() {
  dropdownAnioAbierto.value =
    false;

  dropdownEstadoAbierto.value =
    !dropdownEstadoAbierto.value;
}


function seleccionarEstado(
  estado
) {
  filtroEstado.value =
    estado;

  cerrarDropdownEstado();
}


/* ============================================================
   INTERACCIONES GLOBALES
============================================================ */

function handleClickOutside(
  event
) {
  if (
    dropdownAnioRef.value
    && !dropdownAnioRef.value.contains(
      event.target
    )
  ) {
    cerrarDropdownAnio();
  }

  if (
    dropdownEstadoRef.value
    && !dropdownEstadoRef.value.contains(
      event.target
    )
  ) {
    cerrarDropdownEstado();
  }
}


function handleGlobalKeydown(
  event
) {
  if (
    event.key !== "Escape"
  ) {
    return;
  }

  cerrarDropdownAnio();
  cerrarDropdownEstado();

  if (
    produccionModalAbierto.value
  ) {
    cerrarProduccionProyecto();
    return;
  }

  if (
    extensionModalAbierto.value
  ) {
    cerrarExtensionFecha();
  }
}


/* ============================================================
   CARGA PRINCIPAL
============================================================ */

async function cargarProyectos({
  silent = false,
} = {}) {
  abortController?.abort?.();

  const currentController =
    new AbortController();

  abortController =
    currentController;

  loadingProyectos.value =
    true;

  errorProyectos.value =
    "";

  try {
    const params = {
      page:
        paginaActual.value,

      page_size:
        PAGE_SIZE,
    };

    if (
      filtroSede.value
    ) {
      params.sede =
        filtroSede.value;
    }

    if (
      debouncedSearch.value
    ) {
      params.q =
        debouncedSearch.value;
    }

    if (
      filtroAnio.value
    ) {
      params.anio =
        filtroAnio.value;
    }

    if (
      esAdmin.value
      && filtroEstado.value
    ) {
      params.estado =
        filtroEstado.value;
    }

    const payload =
      await listarProyectos(
        params,
        {
          signal:
            currentController.signal,
        }
      );

    if (
      abortController
      !== currentController
    ) {
      return;
    }

    proyectos.value = (
      Array.isArray(
        payload?.results
      )
        ? payload.results
        : (
          Array.isArray(
            payload
          )
            ? payload
            : []
        )
    );

    totalRegistros.value =
      Number(
        payload?.count
        ?? proyectos.value.length
        ?? 0
      ) || 0;

    hasLoadedProjects.value =
      true;

    const maxPage =
      Math.max(
        1,
        Math.ceil(
          totalRegistros.value
          / PAGE_SIZE
        )
      );

    if (
      paginaActual.value
      > maxPage
    ) {
      paginaActual.value =
        maxPage;

      await cargarProyectos({
        silent: true,
      });
    }
  } catch (
    error
  ) {
    if (
      error?.name === "CanceledError"
      || error?.code === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error cargando proyectos:",
      error
    );

    hasLoadedProjects.value =
      true;

    errorProyectos.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudieron cargar los proyectos. "
          + "Intente nuevamente."
        )
      );

    if (
      !silent
    ) {
      setFeedback(
        errorProyectos.value,
        "error"
      );
    }
  } finally {
    if (
      abortController
      === currentController
    ) {
      loadingProyectos.value =
        false;
    }
  }
}


/* ============================================================
   NAVEGACIÓN AL FORMULARIO
============================================================ */

function irANuevoProyecto() {
  router.push({
    name:
      "ProyectoNuevo",
  });
}


function editarProyecto(
  proyecto
) {
  if (
    !proyecto?.id
  ) {
    return;
  }

  router.push({
    name:
      "ProyectoEditar",

    params: {
      id:
        proyecto.id,
    },
  });
}


/* ============================================================
   CAMBIO DE ESTADO
============================================================ */

async function cambiarEstado(
  proyecto
) {
  if (
    !proyecto?.id
  ) {
    return;
  }

  if (
    !puedeCambiarEstado(
      proyecto
    )
  ) {
    setFeedback(
      tituloAccionEstado(
        proyecto
      ),
      "error"
    );

    return;
  }

  processingProjectId.value =
    proyecto.id;

  try {
    const payload =
      await cambiarEstadoProyecto(
        proyecto.id
      );

    const updatedProject =
      extractProjectPayload(
        payload
      );

    if (
      updatedProject?.id
    ) {
      const updatedLocally =
        updateProjectInCurrentPage(
          updatedProject
        );

      if (
        !updatedLocally
      ) {
        await cargarProyectos({
          silent: true,
        });
      }
    } else {
      await cargarProyectos({
        silent: true,
      });
    }

    await cargarAniosDisponibles();

    setFeedback(
      (
        "Estado actualizado."
      ),
      "success"
    );
  } catch (
    error
  ) {
    console.error(
      "Error cambiando estado del proyecto:",
      error
    );

    setFeedback(
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudo actualizar el "
          + "estado del proyecto."
        )
      ),
      "error"
    );
  } finally {
    processingProjectId.value =
      null;
  }
}


/* ============================================================
   EXTENSIÓN DE FECHA
============================================================ */

function abrirExtensionFecha(
  proyecto
) {
  if (
    !proyecto?.id
  ) {
    return;
  }

  proyectoExtension.value =
    proyecto;

  extensionError.value =
    "";

  extensionSuccess.value =
    "";

  extensionModalAbierto.value =
    true;

  extensionFecha.value = (
    addDaysToDate(
      fechaReferenciaExtension(
        proyecto
      ),
      1
    )
    || ""
  );
}


function cerrarExtensionFecha() {
  if (
    savingExtension.value
  ) {
    return;
  }

  extensionModalAbierto.value =
    false;

  proyectoExtension.value =
    null;

  extensionFecha.value =
    "";

  extensionError.value =
    "";

  extensionSuccess.value =
    "";
}


async function confirmarExtensionFecha() {
  if (
    !proyectoExtension.value?.id
    || extensionSuccess.value
  ) {
    return;
  }

  extensionError.value =
    "";

  extensionSuccess.value =
    "";

  if (
    !extensionFecha.value
  ) {
    extensionError.value =
      (
        "Debe seleccionar una nueva "
        + "fecha de finalización."
      );

    return;
  }

  const minimumDate =
    extensionFechaMin.value;

  if (
    minimumDate
    && extensionFecha.value
    < minimumDate
  ) {
    extensionError.value = (
      "La nueva fecha debe ser posterior "
      + "a la fecha final vigente."
    );

    return;
  }

  savingExtension.value =
    true;

  try {
    const payload =
      await extenderFechaProyecto(
        proyectoExtension.value.id,
        extensionFecha.value
      );

    const updatedProject =
      extractProjectPayload(
        payload
      );

    if (
      updatedProject?.id
    ) {
      const updatedLocally =
        updateProjectInCurrentPage(
          updatedProject
        );

      if (
        !updatedLocally
      ) {
        await cargarProyectos({
          silent: true,
        });
      }
    } else {
      await cargarProyectos({
        silent: true,
      });
    }

    await cargarAniosDisponibles();

    const fechaGuardada =
      formatFecha(
        extensionFecha.value
      );

    extensionSuccess.value = (
      "La nueva fecha de finalización se guardó correctamente: "
      + `${fechaGuardada}.`
    );

    setFeedback(
      (
        "Fecha final actualizada correctamente."
      ),
      "success"
    );
  } catch (
    error
  ) {
    console.error(
      "Error extendiendo fecha del proyecto:",
      error
    );

    extensionError.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudo extender la fecha "
          + "final del proyecto."
        )
      );
  } finally {
    savingExtension.value =
      false;
  }
}


/* ============================================================
   FILTROS Y ACCIONES
============================================================ */

async function limpiarFiltros() {
  suspendFilterWatchers =
    true;

  searchQuery.value =
    "";

  debouncedSearch.value =
    "";

  filtroSede.value =
    "";

  filtroAnio.value =
    "";

  filtroEstado.value =
    "";

  paginaActual.value =
    1;

  suspendFilterWatchers =
    false;

  cerrarDropdownAnio();
  cerrarDropdownEstado();

  await recargarAniosYProyectosPorFiltros({
    silent: true,
  });
}


async function recargarProyectos() {
  await recargarAniosYProyectosPorFiltros({
    silent: false,
  });

  if (
    !errorProyectos.value
  ) {
    setFeedback(
      (
        "La lista de proyectos se "
        + "actualizó correctamente."
      ),
      "info"
    );
  }
}


/* ============================================================
   PAGINACIÓN
============================================================ */

async function irAPagina(
  page
) {
  if (
    page < 1
    || page > totalPaginas.value
    || page === paginaActual.value
  ) {
    return;
  }

  paginaActual.value =
    page;

  await cargarProyectos({
    silent: true,
  });
}


async function paginaAnterior() {
  if (
    !puedeIrAnterior.value
  ) {
    return;
  }

  await irAPagina(
    paginaActual.value
    - 1
  );
}


async function paginaSiguiente() {
  if (
    !puedeIrSiguiente.value
  ) {
    return;
  }

  await irAPagina(
    paginaActual.value
    + 1
  );
}


/* ============================================================
   QUERY PARAMS HEREDADOS
============================================================ */

async function limpiarQueryLegacy() {
  const nextQuery = {
    ...route.query,
  };

  let changed =
    false;

  [
    "tab",
    "scope",
    "type",
    "project",
  ].forEach(
    (key) => {
      if (
        key in nextQuery
      ) {
        delete nextQuery[
          key
        ];

        changed =
          true;
      }
    }
  );

  if (
    changed
  ) {
    await router.replace({
      query:
        nextQuery,
    });
  }
}


/* ============================================================
   WATCHERS
============================================================ */

watch(
  searchQuery,
  (
    value
  ) => {
    if (
      suspendFilterWatchers
    ) {
      return;
    }

    clearTimeout(
      searchTimer
    );

    searchTimer =
      setTimeout(
        async () => {
          debouncedSearch.value =
            sanitizeQuery(
              value
            );

          paginaActual.value =
            1;

          await recargarAniosYProyectosPorFiltros({
            silent: true,
          });
        },
        300
      );
  }
);


watch(
  filtroSede,
  async () => {
    if (
      suspendFilterWatchers
    ) {
      return;
    }

    paginaActual.value =
      1;

    await recargarAniosYProyectosPorFiltros({
      silent: true,
    });
  }
);


watch(
  filtroEstado,
  async () => {
    if (
      suspendFilterWatchers
    ) {
      return;
    }

    paginaActual.value =
      1;

    await recargarAniosYProyectosPorFiltros({
      silent: true,
    });
  }
);


watch(
  filtroAnio,
  async () => {
    if (
      suspendFilterWatchers
    ) {
      return;
    }

    paginaActual.value =
      1;

    await cargarProyectos({
      silent: true,
    });

  }
);


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(
  async () => {
    document.addEventListener(
      "click",
      handleClickOutside
    );

    document.addEventListener(
      "keydown",
      handleGlobalKeydown
    );

    await limpiarQueryLegacy();

    await cargarSedesDisponibles();

    await recargarAniosYProyectosPorFiltros({
      silent: true,
    });

    const shouldOpenNew = (
      route.query?.nuevo
      === "1"
    );

    if (
      shouldOpenNew
      && esAdmin.value
    ) {
      const nextQuery = {
        ...route.query,
      };

      delete nextQuery.nuevo;

      await router.replace({
        query:
          nextQuery,
      });

      irANuevoProyecto();
    }

    if (
      route.query?.guardado
      === "1"
    ) {
      setFeedback(
        (
          "El proyecto se guardó "
          + "correctamente."
        ),
        "success"
      );

      const nextQuery = {
        ...route.query,
      };

      delete nextQuery.guardado;

      await router.replace({
        query:
          nextQuery,
      });
    }
  }
);


onBeforeUnmount(
  () => {
    clearTimeout(
      searchTimer
    );

    clearTimeout(
      feedbackTimer
    );

    abortController?.abort?.();
    yearsAbortController?.abort?.();
    sitesAbortController?.abort?.();
    comparisonAbortController?.abort?.();
    productionAbortController?.abort?.();

    document.removeEventListener(
      "click",
      handleClickOutside
    );

    document.removeEventListener(
      "keydown",
      handleGlobalKeydown
    );
  }
);
</script>

<style src="./proyectos-listado.css" lang="css"></style>
<style src="./proyectos-listado-stage5.css" lang="css"></style>
