<template>
  <div class="pub-list-page" :data-tipo="filtroTipo">
    <main class="pub-shell">
      <header class="pub-header" aria-label="Listado de publicaciones">
        <div class="hero__left">
          <h1 class="pub-title">Publicaciones</h1>

          <div class="pub-chips" aria-label="Resumen general">
            <span class="pub-chip">
              Total: <strong>{{ publicaciones.length }}</strong>
            </span>

            <span class="pub-chip">
              Resultados: <strong>{{ listaFiltrada.length }}</strong>
            </span>
          </div>
        </div>

        <div class="hero__right" aria-label="Herramientas principales">
          <label class="search search--navbar" aria-label="Buscar publicación">
            <span class="search__lead" aria-hidden="true">
              <svg viewBox="0 0 24 24" class="search__svg" aria-hidden="true">
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
              :aria-label="hayBusqueda ? 'Limpiar búsqueda' : 'Enfocar búsqueda'"
              @click="hayBusqueda ? (filtroTexto = '') : focusSearch()"
            >
              <span v-if="hayBusqueda" class="search__x" aria-hidden="true">×</span>

              <svg
                v-else
                viewBox="0 0 24 24"
                class="search__svg search__svg--white"
                aria-hidden="true"
              >
                <path
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 1 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </label>

          <div class="hero__actions" aria-label="Acciones">
            <button
              class="hero__btn hero__btn--ghost"
              type="button"
              @click="abrirPanelFiltros"
            >
              Filtros
            </button>

            <button
              class="hero__btn hero__btn--primary"
              type="button"
              @click="abrirPanelExportacion"
              :disabled="loading"
            >
              Exportar Excel
            </button>
          </div>
        </div>

        <div class="hero__topline" aria-hidden="true"></div>
      </header>

      <section class="pub-layout">
        <aside class="pub-side" aria-label="Panel lateral">
          <div class="pub-sideStack">
            <section
              v-if="panelLateralActivo === 'filtros'"
              class="pub-sidePanel"
            >
              <div class="pub-sidePanel__head">
                <h2 class="pub-sidePanel__title">Filtros</h2>
                <span class="pub-sidePanel__badge">
                  {{ activeAdvancedFiltersCount }}
                </span>
              </div>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">Ubicación</h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label class="pub-label" for="fFacultad">Facultad</label>
                    <select
                      id="fFacultad"
                      v-model="filtroFacultad"
                      class="pub-select"
                      @change="onMainFacultadChange"
                    >
                      <option value="">Todas</option>
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
                    <label class="pub-label" for="fCarrera">Carrera</label>
                    <select
                      id="fCarrera"
                      v-model="filtroCarrera"
                      class="pub-select"
                      :disabled="!filtroFacultad"
                      @change="onMainCarreraChange"
                    >
                      <option value="">Todas</option>
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
                    <label class="pub-label" for="fProyecto">Proyecto</label>
                    <select
                      id="fProyecto"
                      v-model="filtroProyecto"
                      class="pub-select"
                      :disabled="!filtroCarrera"
                    >
                      <option value="">Todos</option>
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
                <h3 class="pub-sidePanel__sectionTitle">Periodo</h3>

                <div class="pub-sidePanel__fields pub-sidePanel__fields--years">
                  <div class="pub-field pub-field--full">
                    <label class="pub-label" for="fAnio">Año exacto</label>
                    <select
                      id="fAnio"
                      v-model="filtroAnio"
                      class="pub-select"
                      :disabled="Boolean(filtroAnioDesde || filtroAnioHasta)"
                    >
                      <option value="">Todos</option>
                      <option
                        v-for="a in años"
                        :key="`exact-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label class="pub-label" for="fAnioDesde">Desde</label>
                    <select
                      id="fAnioDesde"
                      v-model="filtroAnioDesde"
                      class="pub-select"
                      :disabled="Boolean(filtroAnio)"
                    >
                      <option value="">Sin mínimo</option>
                      <option
                        v-for="a in años"
                        :key="`desde-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label class="pub-label" for="fAnioHasta">Hasta</label>
                    <select
                      id="fAnioHasta"
                      v-model="filtroAnioHasta"
                      class="pub-select"
                      :disabled="Boolean(filtroAnio)"
                    >
                      <option value="">Actual</option>
                      <option
                        v-for="a in años"
                        :key="`hasta-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <div class="pub-sidePanel__footer">
                <button
                  type="button"
                  class="hero__btn hero__btn--ghost"
                  @click="limpiarFiltros"
                >
                  Limpiar
                </button>
              </div>
            </section>

            <section
              v-else
              class="pub-sidePanel pub-sidePanel--export"
            >
              <div class="pub-sidePanel__head">
                <h2 class="pub-sidePanel__title">Exportar Excel</h2>
                <span class="pub-sidePanel__badge pub-sidePanel__badge--soft">
                  {{ exportPreviewCount }}
                </span>
              </div>

              <div v-if="exportErrorMsg" class="pub-alert" role="alert">
                <strong>Error:</strong> {{ exportErrorMsg }}
              </div>

              <div class="pub-sidePanel__actions">
                <button
                  type="button"
                  class="hero__btn hero__btn--ghost"
                  @click="syncExportFiltersFromVisible"
                >
                  Usar visibles
                </button>

                <button
                  type="button"
                  class="hero__btn"
                  @click="limpiarExportFilters"
                >
                  Limpiar Excel
                </button>
              </div>

              <section class="pub-sidePanel__section">
                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label class="pub-label" for="expTexto">Texto</label>
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
                    <label class="pub-label" for="expTipo">Tipo</label>
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
                    <label class="pub-label" for="expFacultad">Facultad</label>
                    <select
                      id="expFacultad"
                      v-model="exportFiltroFacultad"
                      class="pub-select"
                      @change="onExportFacultadChange"
                    >
                      <option value="">Todas</option>
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
                    <label class="pub-label" for="expCarrera">Carrera</label>
                    <select
                      id="expCarrera"
                      v-model="exportFiltroCarrera"
                      class="pub-select"
                      :disabled="!exportFiltroFacultad"
                      @change="onExportCarreraChange"
                    >
                      <option value="">Todas</option>
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
                    <label class="pub-label" for="expProyecto">Proyecto</label>
                    <select
                      id="expProyecto"
                      v-model="exportFiltroProyecto"
                      class="pub-select"
                      :disabled="!exportFiltroCarrera"
                    >
                      <option value="">Todos</option>
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
                    <label class="pub-label" for="expAnio">Año exacto</label>
                    <select
                      id="expAnio"
                      v-model="exportFiltroAnio"
                      class="pub-select"
                      :disabled="Boolean(exportFiltroAnioDesde || exportFiltroAnioHasta)"
                    >
                      <option value="">Todos</option>
                      <option
                        v-for="a in años"
                        :key="`exp-exact-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label class="pub-label" for="expAnioDesde">Desde</label>
                    <select
                      id="expAnioDesde"
                      v-model="exportFiltroAnioDesde"
                      class="pub-select"
                      :disabled="Boolean(exportFiltroAnio)"
                    >
                      <option value="">Sin mínimo</option>
                      <option
                        v-for="a in años"
                        :key="`exp-desde-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label class="pub-label" for="expAnioHasta">Hasta</label>
                    <select
                      id="expAnioHasta"
                      v-model="exportFiltroAnioHasta"
                      class="pub-select"
                      :disabled="Boolean(exportFiltroAnio)"
                    >
                      <option value="">Actual</option>
                      <option
                        v-for="a in años"
                        :key="`exp-hasta-${a}`"
                        :value="String(a)"
                      >
                        {{ a }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <div class="pub-sidePanel__footer pub-sidePanel__footer--stack">
                <button
                  type="button"
                  class="hero__btn hero__btn--ghost"
                  @click="abrirPanelFiltros"
                >
                  Volver
                </button>

                <button
                  type="button"
                  class="hero__btn hero__btn--primary"
                  @click="confirmarExportacion"
                  :disabled="loading || exporting || !exportPreviewCount"
                >
                  <span v-if="exporting">Generando...</span>
                  <span v-else>Generar Excel</span>
                </button>
              </div>
            </section>
          </div>
        </aside>

        <section class="pub-main">
          <section class="pub-typeFilter" aria-label="Filtrado por tipo de publicación">
            <div class="pub-typeFilter__head">
              <h2 class="pub-typeFilter__title">Tipo</h2>

              <button
                v-if="hayFiltros || hayBusqueda"
                type="button"
                class="pub-inlineAction"
                @click="limpiarFiltros"
              >
                Limpiar todo
              </button>
            </div>

            <div class="pub-typeFilter__chips">
              <button
                v-for="tipo in TIPOS_LIST"
                :key="`top-${tipo.value}`"
                type="button"
                :class="[
                  'pub-typeFilter__chip',
                  { 'is-active': filtroTipo === tipo.value }
                ]"
                @click="filtroTipo = tipo.value"
              >
                <span
                  class="pub-typeFilter__dot"
                  :data-tipo="tipo.value"
                  aria-hidden="true"
                ></span>
                <span class="pub-typeFilter__label">{{ tipo.label }}</span>
                <span class="pub-typeFilter__count">{{ countByType(tipo.value) }}</span>
              </button>
            </div>
          </section>

          <section class="pub-state" v-if="loading">
            <div class="pub-skeleton-grid" aria-label="Cargando publicaciones">
              <div class="pub-skeleton-card" v-for="n in 8" :key="n"></div>
            </div>
          </section>

          <section class="pub-state pub-state--error" v-else-if="errorMsg">
            <div class="pub-alert" role="alert">
              <strong>Error:</strong> {{ errorMsg }}
            </div>
          </section>

          <section v-else class="pub-content">
            <div class="pub-grid" v-if="listaFiltrada.length">
              <article
                v-for="pub in listaFiltrada"
                :key="pub.id"
                class="pub-card pub-card--interactive"
                :data-tipo="resolveType(pub)"
                tabindex="0"
                role="button"
                @click="verDetalles(pub.id)"
                @keydown.enter.prevent="verDetalles(pub.id)"
                @keydown.space.prevent="verDetalles(pub.id)"
              >
                <div class="pub-card__head">
                  <span class="pub-badge" :data-tipo="resolveType(pub)">
                    {{ resolveLabel(pub) }}
                  </span>

                  <time class="pub-date" :datetime="pub.fecha_publicacion || ''">
                    {{ formatFecha(pub.fecha_publicacion) }}
                  </time>
                </div>

                <div class="pub-card__body">
                  <h3
                    class="pub-card__title"
                    :title="pub.titulo || pub.proyecto || 'Sin título'"
                  >
                    {{ pub.titulo || pub.proyecto || "Sin título" }}
                  </h3>

                  <p
                    v-if="pub.autor"
                    class="pub-card__meta pub-card__meta--soft"
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

                <div class="pub-card__footer" aria-hidden="true">
                  <span class="pub-card__action">Ver detalle</span>
                </div>
              </article>
            </div>

            <div v-else class="pub-empty" role="status" aria-live="polite">
              <div class="pub-empty__mark" aria-hidden="true"></div>
              <h3 class="pub-empty__title">{{ emptyTitle }}</h3>
              <p class="pub-empty__text">{{ emptyText }}</p>

              <button
                v-if="hayFiltros || hayBusqueda"
                class="hero__btn hero__btn--primary"
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
import { ref, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../../scripts/api/axios";
import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

const router = useRouter();
const searchEl = ref(null);

const panelLateralActivo = ref("filtros");

const TIPOS = {
  ALL: { label: "Todos", value: "ALL" },
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

const publicaciones = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);
const años = ref([]);

const filtroTipo = ref(TIPOS.ALL.value);
const filtroAnio = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");
const filtroTexto = ref("");
const filtroFacultad = ref("");
const filtroCarrera = ref("");
const filtroProyecto = ref("");

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

const loading = ref(false);
const exporting = ref(false);
const errorMsg = ref("");
const exportErrorMsg = ref("");

const focusSearch = () => {
  searchEl.value?.focus();
};

const abrirPanelFiltros = () => {
  panelLateralActivo.value = "filtros";
};

const abrirPanelExportacion = async () => {
  panelLateralActivo.value = "export";
  await syncExportFiltersFromVisible();
};

const normalizeText = (value) =>
  String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

const extractArray = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.publicaciones)) return payload.publicaciones;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
};

const findById = (list, id) =>
  list.find((item) => String(item?.id) === String(id || ""));

const extractYear = (fecha) => {
  const raw = String(fecha || "").substring(0, 4);
  return /^\d{4}$/.test(raw) ? Number(raw) : null;
};

const compareCatalogValue = (value, selectedLabel) => {
  if (!selectedLabel) return true;
  const a = normalizeText(value);
  const b = normalizeText(selectedLabel);
  return a === b || a.includes(b) || b.includes(a);
};

const getResolvedMeta = (p) => p?.__tipoMeta || getTipoPublicacionMetaFromItem(p);

const resolveType = (p) => {
  const meta = getResolvedMeta(p);
  return meta?.codigo || "OTRO";
};

const resolveLabel = (p) => {
  const meta = getResolvedMeta(p);

  if (meta?.codigo && meta.codigo !== "OTRO") {
    return meta.label;
  }

  return (
    String(
      p?.tipo_publicacion_final_label ||
        p?.tipo_publicacion_final ||
        p?.tipo ||
        "Publicación"
    ).trim() || "Publicación"
  );
};

const buildAcademicMeta = (pub) => {
  const facultad = String(pub?.facultad || "").trim();
  const carrera = String(pub?.carrera || "").trim();

  if (facultad && carrera) return `${facultad} · ${carrera}`;
  if (facultad) return facultad;
  if (carrera) return carrera;
  return "—";
};

const selectedFacultadNombre = computed(() => {
  const fac = findById(facultades.value, filtroFacultad.value);
  return fac?.nombre || "";
});

const selectedCarreraNombre = computed(() => {
  const car = findById(carreras.value, filtroCarrera.value);
  return car?.nombre || "";
});

const selectedProyectoNombre = computed(() => {
  const proy = findById(proyectos.value, filtroProyecto.value);
  return proy?.nombre || "";
});

const selectedExportFacultadNombre = computed(() => {
  const fac = findById(facultades.value, exportFiltroFacultad.value);
  return fac?.nombre || "";
});

const selectedExportCarreraNombre = computed(() => {
  const car = findById(exportCarreras.value, exportFiltroCarrera.value);
  return car?.nombre || "";
});

const selectedExportProyectoNombre = computed(() => {
  const proy = findById(exportProyectos.value, exportFiltroProyecto.value);
  return proy?.nombre || "";
});

const filterPublicaciones = (items, criteria) => {
  const q = normalizeText(criteria.texto);

  const anioExacto = criteria.anio ? Number(criteria.anio) : null;
  const anioDesde = criteria.anioDesde ? Number(criteria.anioDesde) : null;
  const anioHasta = criteria.anioHasta ? Number(criteria.anioHasta) : null;

  const minYear =
    !anioExacto && anioDesde && anioHasta ? Math.min(anioDesde, anioHasta) : anioDesde;

  const maxYear =
    !anioExacto && anioDesde && anioHasta ? Math.max(anioDesde, anioHasta) : anioHasta;

  return items.filter((p) => {
    const tipoResuelto = resolveType(p);
    const year = extractYear(p?.fecha_publicacion);

    const cumpleTipo =
      criteria.tipo && criteria.tipo !== TIPOS.ALL.value
        ? tipoResuelto === criteria.tipo
        : true;

    let cumpleAnio = true;
    if (anioExacto) {
      cumpleAnio = year === anioExacto;
    } else {
      if (minYear && (!year || year < minYear)) cumpleAnio = false;
      if (maxYear && (!year || year > maxYear)) cumpleAnio = false;
    }

    const cumpleFacultad = compareCatalogValue(p?.facultad, criteria.facultadLabel);
    const cumpleCarrera = compareCatalogValue(p?.carrera, criteria.carreraLabel);
    const cumpleProyecto = compareCatalogValue(p?.proyecto, criteria.proyectoLabel);

    const blob = [
      p?.titulo,
      p?.proyecto,
      p?.autor,
      p?.tipo,
      p?.tipo_codigo,
      p?.tipo_publicacion_final,
      p?.tipo_publicacion_final_label,
      p?.facultad,
      p?.carrera,
      p?.fecha_publicacion,
      resolveLabel(p),
      resolveType(p),
      buildAcademicMeta(p),
    ]
      .map((x) => normalizeText(x))
      .join(" ");

    const cumpleTexto = q ? blob.includes(q) : true;

    return (
      cumpleTipo &&
      cumpleAnio &&
      cumpleFacultad &&
      cumpleCarrera &&
      cumpleProyecto &&
      cumpleTexto
    );
  });
};

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
  facultadLabel: selectedExportFacultadNombre.value,
  carreraLabel: selectedExportCarreraNombre.value,
  proyectoLabel: selectedExportProyectoNombre.value,
}));

const hayBusqueda = computed(() => Boolean(filtroTexto.value?.trim()));

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

const listaFiltrada = computed(() =>
  filterPublicaciones(publicaciones.value, mainCriteria.value)
);

const exportPreviewCount = computed(() =>
  filterPublicaciones(publicaciones.value, exportCriteria.value).length
);

const emptyTitle = computed(() => {
  if (hayBusqueda.value || hayFiltros.value) return "No se encontraron publicaciones";
  return "No hay publicaciones";
});

const emptyText = computed(() => {
  if (hayBusqueda.value || hayFiltros.value) {
    return "Pruebe con otros filtros o limpie la búsqueda.";
  }
  return "No existen publicaciones registradas.";
});

const countByType = (typeValue) => {
  if (typeValue === "ALL") return publicaciones.value.length;
  return publicaciones.value.filter((item) => resolveType(item) === typeValue).length;
};

const loadPublicaciones = async () => {
  const res = await api.get("/publicaciones/");
  publicaciones.value = extractArray(res.data).map((p) => ({
    ...p,
    __tipoMeta: getTipoPublicacionMetaFromItem(p),
  }));

  const extraidos = publicaciones.value
    .map((p) => extractYear(p?.fecha_publicacion))
    .filter((x) => Number.isInteger(x));

  años.value = [...new Set(extraidos)].sort((a, b) => b - a);
};

const loadFacultades = async () => {
  const res = await api.get("/selects/facultades/");
  facultades.value = extractArray(res.data);
};

const fetchCarrerasByFacultad = async (facultadId) => {
  if (!facultadId) return [];
  const res = await api.get(`/selects/carreras/${facultadId}/`);
  return extractArray(res.data);
};

const fetchProyectosByCarrera = async (carreraId) => {
  if (!carreraId) return [];
  const res = await api.get(`/selects/proyectos/${carreraId}/`);
  return extractArray(res.data);
};

const limpiarFiltros = () => {
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
};

const limpiarExportFilters = () => {
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
};

const syncExportFiltersFromVisible = async () => {
  exportFiltroTipo.value = filtroTipo.value;
  exportFiltroAnio.value = filtroAnio.value;
  exportFiltroAnioDesde.value = filtroAnioDesde.value;
  exportFiltroAnioHasta.value = filtroAnioHasta.value;
  exportFiltroTexto.value = filtroTexto.value;
  exportFiltroFacultad.value = filtroFacultad.value;
  exportFiltroCarrera.value = filtroCarrera.value;
  exportFiltroProyecto.value = filtroProyecto.value;
  exportCarreras.value = [];
  exportProyectos.value = [];
  exportErrorMsg.value = "";

  if (exportFiltroFacultad.value) {
    try {
      exportCarreras.value = await fetchCarrerasByFacultad(exportFiltroFacultad.value);
    } catch (error) {
      console.error("Error cargando carreras para exportación:", error);
      exportCarreras.value = [];
    }
  }

  if (exportFiltroCarrera.value) {
    try {
      exportProyectos.value = await fetchProyectosByCarrera(exportFiltroCarrera.value);
    } catch (error) {
      console.error("Error cargando proyectos para exportación:", error);
      exportProyectos.value = [];
    }
  }
};

const onMainFacultadChange = async () => {
  filtroCarrera.value = "";
  filtroProyecto.value = "";
  carreras.value = [];
  proyectos.value = [];

  if (!filtroFacultad.value) return;

  try {
    carreras.value = await fetchCarrerasByFacultad(filtroFacultad.value);
  } catch (error) {
    console.error("Error cargando carreras:", error);
    carreras.value = [];
  }
};

const onMainCarreraChange = async () => {
  filtroProyecto.value = "";
  proyectos.value = [];

  if (!filtroCarrera.value) return;

  try {
    proyectos.value = await fetchProyectosByCarrera(filtroCarrera.value);
  } catch (error) {
    console.error("Error cargando proyectos:", error);
    proyectos.value = [];
  }
};

const onExportFacultadChange = async () => {
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";
  exportCarreras.value = [];
  exportProyectos.value = [];

  if (!exportFiltroFacultad.value) return;

  try {
    exportCarreras.value = await fetchCarrerasByFacultad(exportFiltroFacultad.value);
  } catch (error) {
    console.error("Error cargando carreras para exportación:", error);
    exportCarreras.value = [];
  }
};

const onExportCarreraChange = async () => {
  exportFiltroProyecto.value = "";
  exportProyectos.value = [];

  if (!exportFiltroCarrera.value) return;

  try {
    exportProyectos.value = await fetchProyectosByCarrera(exportFiltroCarrera.value);
  } catch (error) {
    console.error("Error cargando proyectos para exportación:", error);
    exportProyectos.value = [];
  }
};

const buildParamsFromState = ({
  tipo,
  anio,
  anioDesde,
  anioHasta,
  texto,
  facultad,
  carrera,
  proyecto,
}) => {
  const params = new URLSearchParams();

  if (tipo && tipo !== TIPOS.ALL.value) {
    params.append("tipo", tipo);
  }

  if (anio) {
    params.append("anio", anio);
  } else {
    if (anioDesde) params.append("anio_desde", anioDesde);
    if (anioHasta) params.append("anio_hasta", anioHasta);
  }

  if (texto?.trim()) {
    params.append("texto", texto.trim());
  }

  if (facultad) params.append("facultad", facultad);
  if (carrera) params.append("carrera", carrera);
  if (proyecto) params.append("proyecto", proyecto);

  return params;
};

const confirmarExportacion = async () => {
  exporting.value = true;
  exportErrorMsg.value = "";

  try {
    const params = buildParamsFromState({
      tipo: exportFiltroTipo.value,
      anio: exportFiltroAnio.value,
      anioDesde: exportFiltroAnioDesde.value,
      anioHasta: exportFiltroAnioHasta.value,
      texto: exportFiltroTexto.value,
      facultad: exportFiltroFacultad.value,
      carrera: exportFiltroCarrera.value,
      proyecto: exportFiltroProyecto.value,
    });

    const query = params.toString();
    const endpoint = query
      ? `/reportes/publicaciones/excel/?${query}`
      : "/reportes/publicaciones/excel/";

    const response = await api.get(endpoint, {
      responseType: "blob",
    });

    const blob = new Blob([response.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");

    link.href = url;
    link.setAttribute("download", `reporte_publicaciones_${timestamp}.xlsx`);

    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error exportando Excel:", error);
    exportErrorMsg.value = "No se pudo generar el archivo Excel.";
  } finally {
    exporting.value = false;
  }
};

const verDetalles = (id) => {
  router.push({
    path: `/publicacion/${id}`,
    query: { from: "publicaciones" },
  });
};

const formatFecha = (fecha) => {
  if (!fecha) return "Sin fecha";

  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "Sin fecha";

  return d.toLocaleDateString("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

watch(filtroAnio, (value) => {
  if (value) {
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  }
});

watch([filtroAnioDesde, filtroAnioHasta], ([desde, hasta]) => {
  if (desde || hasta) {
    filtroAnio.value = "";
  }
});

watch(exportFiltroAnio, (value) => {
  if (value) {
    exportFiltroAnioDesde.value = "";
    exportFiltroAnioHasta.value = "";
  }
});

watch([exportFiltroAnioDesde, exportFiltroAnioHasta], ([desde, hasta]) => {
  if (desde || hasta) {
    exportFiltroAnio.value = "";
  }
});

onMounted(async () => {
  loading.value = true;
  errorMsg.value = "";

  try {
    await Promise.all([loadPublicaciones(), loadFacultades()]);
  } catch (error) {
    console.error("Error cargando publicaciones:", error);
    errorMsg.value = "No se pudieron cargar las publicaciones.";
  } finally {
    loading.value = false;
  }
});
</script>

<style src="./sgpc-listados-base.css"></style>
<style src="./listado-publicaciones.css"></style>