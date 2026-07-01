<template>
  <div class="pr-page">
    <div class="pr-shell">
      <header
        class="pr-hero page-stage page-stage-1"
        :aria-label="mensajesVista.heroAriaLabel"
      >
        <div class="pr-hero__main">
          <div class="pr-hero__copy">
            <span class="pr-eyebrow">{{ mensajesVista.eyebrow }}</span>

            <h1 class="pr-title">{{ mensajesVista.titulo }}</h1>

            <p class="pr-subtitle">
              {{ mensajesVista.subtitulo }}
            </p>
          </div>

          <div class="pr-pills" aria-label="Resumen de proyectos">
            <span class="pr-pill">
              Total: <strong>{{ totalRegistros }}</strong>
            </span>

            <span class="pr-pill">
              Página: <strong>{{ paginaActual }}</strong>
            </span>

            <span class="pr-pill">
              Visibles: <strong>{{ resultadosPagina }}</strong>
            </span>

            <span v-if="filtrosActivosCount" class="pr-pill pr-pill--active">
              Filtros: <strong>{{ filtrosActivosCount }}</strong>
            </span>
          </div>
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

      <section class="pr-card page-stage page-stage-3">
        <div class="pr-card-head">
          <div class="pr-card-head__info">
            <h2 class="pr-card-title">{{ mensajesVista.cardTitulo }}</h2>
          </div>

          <div class="pr-card-meta">
            <span>{{ totalRegistros }} resultados</span>
            <span>{{ resultadosPagina }} visibles</span>
          </div>
        </div>

        <div v-if="loadingProyectos" class="pr-state pr-state--loading">
          {{ mensajesVista.loading }}
        </div>

        <div
          v-else-if="errorProyectos"
          class="pr-state pr-state--error"
          role="alert"
        >
          {{ errorProyectos }}
        </div>

        <div
          v-else
          class="pr-table-wrap"
          role="region"
          :aria-label="mensajesVista.tablaAriaLabel"
        >
          <table class="pr-table" :class="{ 'pr-table--admin': esAdmin }">
            <thead>
              <tr>
                <th>Proyecto</th>
                <th>Profesores</th>
                <th>Carrera / Facultad</th>
                <th class="pr-th-center">Periodo</th>
                <th class="pr-th-center">Fecha final</th>
                <th class="pr-th-center">Estado</th>
                <th class="pr-th-center">PDF</th>
                <th v-if="esAdmin" class="pr-th-right">Acciones</th>
              </tr>
            </thead>

            <tbody>
              <tr v-if="proyectosFiltrados.length === 0">
                <td class="pr-empty" :colspan="esAdmin ? 8 : 7">
                  {{ mensajesVista.empty }}
                </td>
              </tr>

              <tr v-for="p in proyectosFiltrados" :key="p.id" class="pr-row">
                <td class="pr-strong">
                  <div class="pr-name" :title="p.nombre || '—'">
                    {{ p.nombre || "—" }}
                  </div>

                  <p v-if="p.descripcion" class="pr-description">
                    {{ truncateText(p.descripcion, 110) }}
                  </p>
                </td>

                <td>
                  <div v-if="autoresResumen(p).length" class="pr-authors-mini">
                    <span
                      v-for="autor in autoresResumen(p).slice(0, 2)"
                      :key="autor.id"
                      class="pr-author-chip"
                      :title="autor.nombre"
                    >
                      {{ autor.nombre }}
                    </span>

                    <span
                      v-if="autoresResumen(p).length > 2"
                      class="pr-author-chip pr-author-chip--more"
                    >
                      +{{ autoresResumen(p).length - 2 }}
                    </span>
                  </div>

                  <span v-else class="pr-muted-text">
                    Sin profesores
                  </span>
                </td>

                <td>
                  <div class="pr-stack">
                    <strong :title="p.carrera_nombre || '—'">
                      {{ p.carrera_nombre || "—" }}
                    </strong>

                    <span :title="p.facultad || '—'">
                      {{ p.facultad || "—" }}
                    </span>
                  </div>
                </td>

                <td class="pr-td-center">
                  <span class="pr-year">
                    {{ periodoProyecto(p) }}
                  </span>
                </td>

                <td class="pr-td-center">
                  <span class="pr-date">
                    {{ fechaFinalProyecto(p) }}
                  </span>
                </td>

                <td class="pr-td-center">
                  <span
                    class="pr-badge"
                    :class="estadoBadgeClass(p.estado)"
                    :data-estado="p.estado || 'nuevo'"
                  >
                    {{ labelEstadoProyecto(p.estado) }}
                  </span>
                </td>

                <td class="pr-td-center">
                  <a
                    v-if="p.archivo_pdf_url"
                    class="pr-pdf-link"
                    :href="p.archivo_pdf_url"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Ver PDF
                  </a>

                  <span v-else class="pr-muted-text">
                    —
                  </span>
                </td>

                <td v-if="esAdmin" class="pr-td-right">
                  <div class="pr-actions">
                    <button
                      class="pr-btn-mini"
                      type="button"
                      :disabled="processingProjectId === p.id || savingExtension"
                      @click="editarProyecto(p)"
                    >
                      Editar
                    </button>

                    <button
                      v-if="puedeExtenderProyecto(p)"
                      class="pr-btn-mini"
                      type="button"
                      :disabled="processingProjectId === p.id || savingExtension"
                      @click="abrirExtensionFecha(p)"
                    >
                      Extender
                    </button>

                    <button
                      class="pr-btn-mini"
                      type="button"
                      :class="estadoActionClass(p.estado)"
                      :disabled="processingProjectId === p.id || savingExtension"
                      @click="cambiarEstado(p)"
                    >
                      {{
                        processingProjectId === p.id
                          ? "Procesando..."
                          : textoAccionEstado(p.estado)
                      }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer
          v-if="!loadingProyectos && !errorProyectos && totalPaginas > 1"
          class="pr-pagination"
          aria-label="Paginación de proyectos"
        >
          <button
            class="pr-btn pr-btn--ghost"
            type="button"
            :disabled="!puedeIrAnterior"
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
            :disabled="!puedeIrSiguiente"
            @click="paginaSiguiente"
          >
            Siguiente
          </button>
        </footer>
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
            <span class="pr-eyebrow">Extensión de proyecto</span>

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
              :disabled="savingExtension"
            />
          </label>

          <p class="pr-ext-help">
            La fecha se guardará como fecha prorrogada y el proyecto pasará a
            estado Arrastre.
          </p>

          <p v-if="extensionError" class="pr-ext-error" role="alert">
            {{ extensionError }}
          </p>
        </div>

        <footer class="pr-ext-actions">
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
            {{ savingExtension ? "Guardando..." : "Guardar extensión" }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";

/* ============================================================
  ENLACES BASE
============================================================ */
const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

/* ============================================================
  CONFIGURACIÓN
============================================================ */
const PAGE_SIZE = 20;

/* ============================================================
  SESIÓN / PERMISOS
============================================================ */
const esAdmin = computed(() => userStore.isAdmin);

/* ============================================================
  MENSAJES DINÁMICOS SEGÚN ROL
============================================================ */
const mensajesVista = computed(() =>
  esAdmin.value
    ? {
        heroAriaLabel: "Gestión de proyectos institucionales",
        eyebrow: "Gestión académica",
        titulo: "Proyectos institucionales",
        subtitulo:
          "Revise, registre y actualice proyectos institucionales con profesores vinculados, periodo, estado y documento PDF.",
        toolbarAriaLabel: "Filtros y acciones",
        busquedaAriaLabel: "Buscar proyecto",
        cardTitulo: "Listado de proyectos",
        tablaAriaLabel: "Tabla de proyectos institucionales",
        loading: "Cargando proyectos...",
        empty: "No se encontraron proyectos con los filtros actuales.",
        placeholderBusqueda: "Buscar por proyecto, profesor, carrera o facultad",
      }
    : {
        heroAriaLabel: "Consulta de proyectos institucionales",
        eyebrow: "Consulta académica",
        titulo: "Consulta de proyectos institucionales",
        subtitulo:
          "Revise los proyectos institucionales activos, sus profesores vinculados y su información principal.",
        toolbarAriaLabel: "Filtros de consulta",
        busquedaAriaLabel: "Buscar proyecto",
        cardTitulo: "Proyectos registrados",
        tablaAriaLabel: "Tabla de consulta de proyectos",
        loading: "Cargando proyectos...",
        empty: "No se encontraron proyectos con los filtros actuales.",
        placeholderBusqueda: "Buscar por proyecto, profesor, carrera o facultad",
      }
);

/* ============================================================
  ESTADO PRINCIPAL
============================================================ */
const proyectos = ref([]);
const loadingProyectos = ref(false);
const errorProyectos = ref("");

/* ============================================================
  FILTROS
============================================================ */
const searchQuery = ref("");
const debouncedSearch = ref("");
const filtroAnio = ref("");
const filtroEstado = ref("");
const listaAnios = ref([]);
const loadingAnios = ref(false);

/* ============================================================
  PAGINACIÓN
============================================================ */
const totalRegistros = ref(0);
const paginaActual = ref(1);

/* ============================================================
  MODAL EXTENSIÓN
============================================================ */
const extensionModalAbierto = ref(false);
const proyectoExtension = ref(null);
const extensionFecha = ref("");
const extensionError = ref("");
const savingExtension = ref(false);

/* ============================================================
  FEEDBACK / OPERACIONES
============================================================ */
const feedbackMessage = ref("");
const feedbackType = ref("info");
const processingProjectId = ref(null);

/* ============================================================
  DROPDOWNS
============================================================ */
const dropdownAnioAbierto = ref(false);
const dropdownEstadoAbierto = ref(false);
const dropdownAnioRef = ref(null);
const dropdownEstadoRef = ref(null);

/* ============================================================
  CONTROL INTERNO
============================================================ */
let searchTimer = null;
let feedbackTimer = null;
let abortController = null;
let suspendFilterWatchers = false;

/* ============================================================
  OPCIONES
============================================================ */
const estadoOptions = [
  { value: "nuevo", label: "Nuevo" },
  { value: "arrastre", label: "Arrastre" },
  { value: "cierre", label: "Cierre" },
];

/* ============================================================
  HELPERS GENERALES
============================================================ */
function setFeedback(message = "", type = "info") {
  feedbackMessage.value = message;
  feedbackType.value = type;

  clearTimeout(feedbackTimer);

  if (message) {
    feedbackTimer = setTimeout(() => {
      feedbackMessage.value = "";
    }, 3200);
  }
}

function sanitizeQuery(value) {
  return String(value || "").trim();
}

function normalizeEstado(value) {
  return String(value || "nuevo").trim().toLowerCase();
}

function normalizeDate(value) {
  if (!value) return "";
  return String(value).slice(0, 10);
}

function formatFecha(value) {
  const normalized = normalizeDate(value);
  if (!normalized) return "—";

  const date = new Date(`${normalized}T00:00:00`);
  if (Number.isNaN(date.getTime())) return normalized;

  return new Intl.DateTimeFormat("es-EC", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(date);
}

function truncateText(value, max = 96) {
  const text = String(value || "").trim();
  if (text.length <= max) return text;
  return `${text.slice(0, max).trim()}…`;
}

function prettyError(val) {
  if (val == null) return "";
  if (typeof val === "string") return val;
  if (Array.isArray(val)) return val.map(prettyError).join(", ");

  if (typeof val === "object") {
    return Object.entries(val)
      .map(([key, value]) => `${key}: ${prettyError(value)}`)
      .join(" | ");
  }

  return String(val);
}

function extractProjectPayload(payload) {
  if (!payload) return null;
  if (payload?.id) return payload;
  if (payload?.proyecto?.id) return payload.proyecto;
  if (payload?.data?.id) return payload.data;
  return null;
}

function updateProjectInCurrentPage(project) {
  if (!project?.id) return false;

  const index = proyectos.value.findIndex((item) => item.id === project.id);
  if (index === -1) return false;

  proyectos.value[index] = {
    ...proyectos.value[index],
    ...project,
  };

  return true;
}

function buildFallbackYears() {
  const currentYear = new Date().getFullYear();
  const minYear = 2000;
  const years = [];

  for (let year = currentYear + 1; year >= minYear; year -= 1) {
    years.push(year);
  }

  return years;
}

function normalizeYears(payload) {
  const source = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.results)
      ? payload.results
      : [];

  return [
    ...new Set(
      source
        .map((item) => Number(item))
        .filter((item) => Number.isInteger(item) && item > 1900)
    ),
  ].sort((a, b) => b - a);
}

function labelEstadoProyecto(estado) {
  const normalized = normalizeEstado(estado);
  const option = estadoOptions.find((item) => item.value === normalized);
  return option?.label || "Nuevo";
}

function estadoBadgeClass(estado) {
  const normalized = normalizeEstado(estado);

  return {
    "pr-badge-new": normalized === "nuevo",
    "pr-badge-progress": normalized === "arrastre",
    "pr-badge-closed": normalized === "cierre",
  };
}

function estadoActionClass(estado) {
  const normalized = normalizeEstado(estado);

  return {
    success: normalized === "nuevo" || normalized === "cierre",
    danger: normalized === "arrastre",
  };
}

function textoAccionEstado(estado) {
  const normalized = normalizeEstado(estado);

  if (normalized === "nuevo") return "Pasar a arrastre";
  if (normalized === "arrastre") return "Cerrar";
  if (normalized === "cierre") return "Reabrir";

  return "Cambiar estado";
}

function periodoProyecto(proyecto) {
  const inicio = proyecto?.anio_inicio;
  const fin = proyecto?.anio_fin;

  if (inicio && fin) return `${inicio} - ${fin}`;
  if (inicio) return `Desde ${inicio}`;
  if (fin) return `Hasta ${fin}`;

  return "—";
}

function fechaFinalProyecto(proyecto) {
  return formatFecha(
    proyecto?.fecha_fin_vigente ||
      proyecto?.fecha_fin_prorrogada ||
      proyecto?.fecha_fin_planificada ||
      proyecto?.fecha_cierre
  );
}

function autoresResumen(proyecto) {
  const source = Array.isArray(proyecto?.autores_resumen)
    ? proyecto.autores_resumen
    : Array.isArray(proyecto?.autores)
      ? proyecto.autores
      : [];

  return source
    .map((item) => {
      const id = item.id || item.autor_id || item.autor;
      const nombre =
        item.nombre ||
        item.nombre_completo ||
        `${item.nombres || ""} ${item.apellidos || ""}`.trim();

      return {
        id,
        nombre: nombre || `Autor #${id}`,
        rol: item.rol,
        rol_label: item.rol_label,
        orden: item.orden,
      };
    })
    .filter((item) => item.id);
}

function puedeExtenderProyecto(proyecto) {
  const estado = normalizeEstado(proyecto?.estado);
  return estado !== "cierre";
}

/* ============================================================
  CARGA DE AÑOS
============================================================ */
async function cargarAniosDisponibles() {
  loadingAnios.value = true;

  try {
    const params = {};

    if (debouncedSearch.value) {
      params.q = debouncedSearch.value;
    }

    if (esAdmin.value && filtroEstado.value) {
      params.estado = filtroEstado.value;
    }

    const res = await api.get("/proyectos/anios/", { params });
    const years = normalizeYears(res.data);

    listaAnios.value = years.length ? years : buildFallbackYears();

    if (
      filtroAnio.value &&
      !listaAnios.value.some((anio) => String(anio) === String(filtroAnio.value))
    ) {
      suspendFilterWatchers = true;
      filtroAnio.value = "";
      suspendFilterWatchers = false;
    }
  } catch (error) {
    console.error("Error cargando años de proyectos:", error);
    listaAnios.value = buildFallbackYears();
  } finally {
    loadingAnios.value = false;
  }
}

async function recargarAniosYProyectosPorFiltros({ silent = true } = {}) {
  await cargarAniosDisponibles();
  await cargarProyectos({ silent });
}

/* ============================================================
  DROPDOWN AÑO
============================================================ */
function cerrarDropdownAnio() {
  dropdownAnioAbierto.value = false;
}

function toggleDropdownAnio() {
  if (loadingAnios.value) return;
  dropdownEstadoAbierto.value = false;
  dropdownAnioAbierto.value = !dropdownAnioAbierto.value;
}

function seleccionarAnio(anio) {
  filtroAnio.value = anio;
  cerrarDropdownAnio();
}

/* ============================================================
  DROPDOWN ESTADO
============================================================ */
function cerrarDropdownEstado() {
  dropdownEstadoAbierto.value = false;
}

function toggleDropdownEstado() {
  dropdownAnioAbierto.value = false;
  dropdownEstadoAbierto.value = !dropdownEstadoAbierto.value;
}

function seleccionarEstado(estado) {
  filtroEstado.value = estado;
  cerrarDropdownEstado();
}

/* ============================================================
  INTERACCIONES GLOBALES
============================================================ */
function handleClickOutside(event) {
  if (dropdownAnioRef.value && !dropdownAnioRef.value.contains(event.target)) {
    cerrarDropdownAnio();
  }

  if (dropdownEstadoRef.value && !dropdownEstadoRef.value.contains(event.target)) {
    cerrarDropdownEstado();
  }
}

function handleGlobalKeydown(event) {
  if (event.key === "Escape") {
    cerrarDropdownAnio();
    cerrarDropdownEstado();

    if (extensionModalAbierto.value) {
      cerrarExtensionFecha();
    }
  }
}

/* ============================================================
  COMPUTEDS
============================================================ */
const placeholderBusqueda = computed(
  () => mensajesVista.value.placeholderBusqueda
);

const proyectosFiltrados = computed(() => proyectos.value);

const resultadosPagina = computed(() => proyectosFiltrados.value.length);

const filtrosActivosCount = computed(() => {
  let total = 0;
  if (debouncedSearch.value) total += 1;
  if (filtroAnio.value) total += 1;
  if (esAdmin.value && filtroEstado.value) total += 1;
  return total;
});

const textoFiltroAnio = computed(() => {
  if (loadingAnios.value) return "Cargando años...";
  return filtroAnio.value || "Todos los años";
});

const textoFiltroEstado = computed(() => {
  if (!filtroEstado.value) return "Todos los estados";
  const opcion = estadoOptions.find((item) => item.value === filtroEstado.value);
  return opcion?.label || "Todos los estados";
});

const totalPaginas = computed(() => {
  const total = Math.ceil(totalRegistros.value / PAGE_SIZE);
  return total > 0 ? total : 1;
});

const puedeIrAnterior = computed(() => paginaActual.value > 1);
const puedeIrSiguiente = computed(() => paginaActual.value < totalPaginas.value);

/* ============================================================
  CARGA PRINCIPAL
============================================================ */
async function cargarProyectos({ silent = false } = {}) {
  abortController?.abort?.();

  const currentController = new AbortController();
  abortController = currentController;

  loadingProyectos.value = true;
  errorProyectos.value = "";

  try {
    const params = {
      page: paginaActual.value,
      page_size: PAGE_SIZE,
    };

    if (debouncedSearch.value) {
      params.q = debouncedSearch.value;
    }

    if (filtroAnio.value) {
      params.anio = filtroAnio.value;
    }

    if (esAdmin.value && filtroEstado.value) {
      params.estado = filtroEstado.value;
    }

    const res = await api.get("/proyectos/", {
      params,
      signal: currentController.signal,
    });

    if (abortController !== currentController) return;

    proyectos.value = Array.isArray(res.data?.results) ? res.data.results : [];
    totalRegistros.value = Number(res.data?.count || 0);

    const maxPage = Math.max(1, Math.ceil(totalRegistros.value / PAGE_SIZE));

    if (paginaActual.value > maxPage) {
      paginaActual.value = maxPage;
      await cargarProyectos({ silent: true });
    }
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") {
      return;
    }

    console.error("Error cargando proyectos:", error);

    proyectos.value = [];
    totalRegistros.value = 0;
    errorProyectos.value = "No se pudieron cargar los proyectos. Intente nuevamente.";

    if (!silent) {
      setFeedback("No se pudo actualizar la lista de proyectos.", "error");
    }
  } finally {
    if (abortController === currentController) {
      loadingProyectos.value = false;
    }
  }
}

/* ============================================================
  NAVEGACIÓN A FORMULARIO
============================================================ */
function irANuevoProyecto() {
  router.push({ name: "ProyectoNuevo" });
}

function editarProyecto(proyecto) {
  if (!proyecto?.id) return;

  router.push({
    name: "ProyectoEditar",
    params: { id: proyecto.id },
  });
}

/* ============================================================
  CAMBIO DE ESTADO
============================================================ */
async function cambiarEstado(proyecto) {
  if (!proyecto?.id) return;

  processingProjectId.value = proyecto.id;

  try {
    const res = await api.patch(`/proyectos/${proyecto.id}/cambiar_estado/`);
    const proyectoActualizado = extractProjectPayload(res?.data);

    if (proyectoActualizado?.id) {
      const updatedLocally = updateProjectInCurrentPage(proyectoActualizado);

      if (!updatedLocally) {
        await cargarProyectos({ silent: true });
      }
    } else {
      await cargarProyectos({ silent: true });
    }

    await cargarAniosDisponibles();

    setFeedback("El estado del proyecto se actualizó correctamente.", "success");
  } catch (error) {
    console.error("Error cambiando estado del proyecto:", error);
    setFeedback("No se pudo actualizar el estado del proyecto.", "error");
  } finally {
    processingProjectId.value = null;
  }
}

/* ============================================================
  EXTENDER FECHA
============================================================ */
function abrirExtensionFecha(proyecto) {
  if (!proyecto?.id) return;

  proyectoExtension.value = proyecto;
  extensionFecha.value = normalizeDate(
    proyecto.fecha_fin_prorrogada ||
      proyecto.fecha_fin_vigente ||
      proyecto.fecha_fin_planificada ||
      ""
  );
  extensionError.value = "";
  extensionModalAbierto.value = true;
}

function cerrarExtensionFecha() {
  if (savingExtension.value) return;

  extensionModalAbierto.value = false;
  proyectoExtension.value = null;
  extensionFecha.value = "";
  extensionError.value = "";
}

async function confirmarExtensionFecha() {
  if (!proyectoExtension.value?.id) return;

  extensionError.value = "";

  if (!extensionFecha.value) {
    extensionError.value = "Debe seleccionar una nueva fecha de finalización.";
    return;
  }

  const fechaInicio = normalizeDate(proyectoExtension.value.fecha_inicio);

  if (fechaInicio && extensionFecha.value < fechaInicio) {
    extensionError.value = "La fecha extendida no puede ser menor a la fecha de inicio.";
    return;
  }

  const fechaPlanificada = normalizeDate(proyectoExtension.value.fecha_fin_planificada);

  if (fechaPlanificada && extensionFecha.value < fechaPlanificada) {
    extensionError.value =
      "La fecha extendida no puede ser menor a la fecha final planificada.";
    return;
  }

  savingExtension.value = true;

  try {
    const res = await api.patch(
      `/proyectos/${proyectoExtension.value.id}/extender_fecha/`,
      {
        fecha_fin_prorrogada: extensionFecha.value,
      }
    );

    const proyectoActualizado = extractProjectPayload(res?.data);

    if (proyectoActualizado?.id) {
      const updatedLocally = updateProjectInCurrentPage(proyectoActualizado);

      if (!updatedLocally) {
        await cargarProyectos({ silent: true });
      }
    } else {
      await cargarProyectos({ silent: true });
    }

    await cargarAniosDisponibles();

    setFeedback("La fecha final del proyecto se extendió correctamente.", "success");
    cerrarExtensionFecha();
  } catch (error) {
    console.error("Error extendiendo fecha del proyecto:", error);
    extensionError.value =
      error?.response?.data
        ? prettyError(error.response.data)
        : "No se pudo extender la fecha final del proyecto.";
  } finally {
    savingExtension.value = false;
  }
}

/* ============================================================
  FILTROS / ACCIONES
============================================================ */
async function limpiarFiltros() {
  suspendFilterWatchers = true;
  searchQuery.value = "";
  debouncedSearch.value = "";
  filtroAnio.value = "";
  filtroEstado.value = "";
  paginaActual.value = 1;
  suspendFilterWatchers = false;

  cerrarDropdownAnio();
  cerrarDropdownEstado();

  await recargarAniosYProyectosPorFiltros({ silent: true });
}

async function recargarProyectos() {
  await recargarAniosYProyectosPorFiltros({ silent: false });
  setFeedback("La lista de proyectos se actualizó correctamente.", "info");
}

/* ============================================================
  PAGINACIÓN
============================================================ */
async function irAPagina(page) {
  if (page < 1 || page > totalPaginas.value || page === paginaActual.value) return;

  paginaActual.value = page;
  await cargarProyectos({ silent: true });
}

async function paginaAnterior() {
  if (!puedeIrAnterior.value) return;
  await irAPagina(paginaActual.value - 1);
}

async function paginaSiguiente() {
  if (!puedeIrSiguiente.value) return;
  await irAPagina(paginaActual.value + 1);
}

/* ============================================================
  LIMPIEZA DE QUERY PARAMS LEGACY
============================================================ */
async function limpiarQueryLegacy() {
  const nextQuery = { ...route.query };
  let changed = false;

  ["tab", "scope", "type", "project"].forEach((key) => {
    if (key in nextQuery) {
      delete nextQuery[key];
      changed = true;
    }
  });

  if (changed) {
    await router.replace({ query: nextQuery });
  }
}

/* ============================================================
  WATCHERS
============================================================ */
watch(searchQuery, (value) => {
  if (suspendFilterWatchers) return;

  clearTimeout(searchTimer);

  searchTimer = setTimeout(async () => {
    debouncedSearch.value = sanitizeQuery(value);
    paginaActual.value = 1;
    await recargarAniosYProyectosPorFiltros({ silent: true });
  }, 300);
});

watch(filtroEstado, async () => {
  if (suspendFilterWatchers) return;

  paginaActual.value = 1;
  await recargarAniosYProyectosPorFiltros({ silent: true });
});

watch(filtroAnio, async () => {
  if (suspendFilterWatchers) return;

  paginaActual.value = 1;
  await cargarProyectos({ silent: true });
});

/* ============================================================
  CICLO DE VIDA
============================================================ */
onMounted(async () => {
  document.addEventListener("click", handleClickOutside);
  document.addEventListener("keydown", handleGlobalKeydown);

  await limpiarQueryLegacy();
  await recargarAniosYProyectosPorFiltros({ silent: true });

  const debeAbrirNuevo = route.query?.nuevo === "1";

  if (debeAbrirNuevo && esAdmin.value) {
    const nextQuery = { ...route.query };
    delete nextQuery.nuevo;
    await router.replace({ query: nextQuery });
    irANuevoProyecto();
  }

  if (route.query?.guardado === "1") {
    setFeedback("El proyecto se guardó correctamente.", "success");

    const nextQuery = { ...route.query };
    delete nextQuery.guardado;
    await router.replace({ query: nextQuery });
  }
});

onBeforeUnmount(() => {
  clearTimeout(searchTimer);
  clearTimeout(feedbackTimer);
  abortController?.abort?.();

  document.removeEventListener("click", handleClickOutside);
  document.removeEventListener("keydown", handleGlobalKeydown);
});
</script>

<style src="./proyectos-listado.css" lang="css"></style>