<template>
  <div class="mispub" :data-tipo="tipoThemeCode">
    <div class="mispub__wrap">
      <header class="mispub__hero" aria-label="Mis publicaciones">
        <div class="hero__left">
          <h1 class="hero__title">Mis publicaciones</h1>

          <div class="hero__pills" aria-label="Resumen">
            <span class="pill">
              Total: <strong>{{ publicaciones.length }}</strong>
            </span>

            <span class="pill">
              Resultados: <strong>{{ publicacionesFiltradas.length }}</strong>
            </span>

            <span v-if="activeFiltersCount" class="pill">
              Filtros: <strong>{{ activeFiltersCount }}</strong>
            </span>
          </div>
        </div>

        <div class="hero__right" aria-label="Herramientas de consulta">
          <div class="hero__tools">
            <label class="search search--navbar" aria-label="Buscar publicación">
              <span class="search__lead" aria-hidden="true">
                <svg viewBox="0 0 24 24" class="search__svg" aria-hidden="true">
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
                @click="q ? (q = '') : searchEl?.focus()"
              >
                <span v-if="q" class="search__x" aria-hidden="true">×</span>

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

            <div class="view__switch" role="tablist" aria-label="Vista de resultados">
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
        </div>

        <div class="hero__topline" aria-hidden="true"></div>
      </header>

      <section class="mispub__filters" aria-label="Filtros">
        <div class="filters__head">
          <div class="filters__titlewrap">
            <h2 class="filters__title">Filtros</h2>
          </div>

          <button
            type="button"
            class="filters__clear"
            :class="{ 'is-hidden': !canClearFilters }"
            :disabled="!canClearFilters"
            @click="clearAllFilters"
          >
            Limpiar
          </button>
        </div>

        <div class="filters__row">
          <button
            v-for="t in TIPOS_LIST"
            :key="t.value"
            type="button"
            :class="['chip', { activo: filtro.value === t.value }]"
            @click="cambiarFiltro(t)"
          >
            <span class="chip__dot" :data-tipo="t.value" aria-hidden="true"></span>
            <span class="chip__label">{{ t.label }}</span>
            <span class="chip__count" aria-hidden="true">{{ countByType(t.value) }}</span>
          </button>
        </div>

        <div class="filters__dateGrid">
          <div class="filter-field filter-field--full">
            <label class="filter-label" for="mispub-anio">Año exacto</label>
            <select
              id="mispub-anio"
              v-model="filtroAnio"
              class="filter-select"
              :disabled="Boolean(filtroAnioDesde || filtroAnioHasta)"
            >
              <option value="">Todos</option>
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
            <label class="filter-label" for="mispub-anio-desde">Desde</label>
            <select
              id="mispub-anio-desde"
              v-model="filtroAnioDesde"
              class="filter-select"
              :disabled="Boolean(filtroAnio)"
            >
              <option value="">Sin mínimo</option>
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
            <label class="filter-label" for="mispub-anio-hasta">Hasta</label>
            <select
              id="mispub-anio-hasta"
              v-model="filtroAnioHasta"
              class="filter-select"
              :disabled="Boolean(filtroAnio)"
            >
              <option value="">Actual</option>
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

      <section class="mispub__state" aria-live="polite">
        <div v-if="loading" class="state state--loading">
          <span class="dot" aria-hidden="true"></span>
          Cargando publicaciones…
        </div>

        <div v-else-if="publicacionesFiltradas.length === 0" class="state state--empty">
          {{ emptyMessage }}
        </div>
      </section>

      <section
        v-if="!loading && publicacionesFiltradas.length > 0"
        class="mispub__results"
        aria-label="Resultados"
      >
        <div v-if="vista === 'cards'" class="cards">
          <article
            v-for="pub in publicacionesFiltradas"
            :key="pub.id"
            class="card"
            :data-tipo="resolveType(pub)"
            tabindex="0"
            role="button"
            @click="verDetalles(pub.id)"
            @keydown.enter.prevent="verDetalles(pub.id)"
            @keydown.space.prevent="verDetalles(pub.id)"
          >
            <div class="card__head">
              <span class="type__badge" :data-tipo="resolveType(pub)">
                {{ resolveLabel(pub) }}
              </span>

              <time class="date" :datetime="pub.fecha_publicacion || ''">
                {{ formatFecha(pub.fecha_publicacion) }}
              </time>
            </div>

            <div class="card__body">
              <h3 class="card__title" :title="pub.titulo || '—'">
                {{ pub.titulo || "—" }}
              </h3>

              <p v-if="pub.autor" class="card__meta card__meta--soft" :title="pub.autor">
                {{ pub.autor }}
              </p>

              <p v-if="pub.proyecto" class="card__meta" :title="pub.proyecto">
                {{ pub.proyecto }}
              </p>

              <p class="card__meta" :title="buildAcademicMeta(pub)">
                {{ buildAcademicMeta(pub) }}
              </p>
            </div>

            <div class="card__footer" aria-hidden="true">
              <span class="card__action">Ver detalle</span>
            </div>
          </article>
        </div>

        <div v-else class="table-wrap" aria-label="Tabla detallada">
          <table class="table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Título</th>
                <th>Proyecto</th>
                <th>Fecha</th>
                <th>Facultad</th>
                <th>Carrera</th>
                <th class="th-actions">Opciones</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="pub in publicacionesFiltradas" :key="pub.id">
                <td class="td-strong">
                  <span class="mini-badge" :data-tipo="resolveType(pub)">
                    {{ resolveLabel(pub) }}
                  </span>
                </td>

                <td class="td-title" :title="pub.titulo || '—'">
                  {{ pub.titulo || "—" }}
                </td>

                <td :title="pub.proyecto || ''">{{ pub.proyecto || "—" }}</td>
                <td>{{ formatFecha(pub.fecha_publicacion) }}</td>
                <td :title="pub.facultad || ''">{{ pub.facultad || "—" }}</td>
                <td :title="pub.carrera || ''">{{ pub.carrera || "—" }}</td>
                <td class="td-actions">
                  <button class="btn-mini" type="button" @click="verDetalles(pub.id)">
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../../scripts/api/axios";
import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

const router = useRouter();

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

const TIPOS_LIST = [TIPOS.ALL, TIPOS.AAI, TIPOS.AR, TIPOS.PON, TIPOS.CAP, TIPOS.LIB];

const publicaciones = ref([]);
const loading = ref(true);
const errorMsg = ref("");

const vista = ref("cards");
const q = ref("");
const searchEl = ref(null);
const filtro = ref(TIPOS.ALL);

const filtroAnio = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");

const extractArray = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.publicaciones)) return payload.publicaciones;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
};

const extractErrorMessage = (error, fallback) => {
  const detail =
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message;

  return String(detail || fallback);
};

const normalizeText = (value) =>
  String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

const extractYear = (fecha) => {
  const raw = String(fecha || "").substring(0, 4);
  return /^\d{4}$/.test(raw) ? Number(raw) : null;
};

const getResolvedMeta = (item) =>
  item?.__tipoMeta || getTipoPublicacionMetaFromItem(item);

const resolveType = (item) => {
  const meta = getResolvedMeta(item);
  return meta?.codigo || "OTRO";
};

const resolveLabel = (item) => {
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
};

const buildAcademicMeta = (pub) => {
  const facultad = String(pub?.facultad || "").trim();
  const carrera = String(pub?.carrera || "").trim();

  if (facultad && carrera) return `${facultad} · ${carrera}`;
  if (facultad) return facultad;
  if (carrera) return carrera;
  return "Sin ubicación académica";
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

const añosDisponibles = computed(() => {
  const years = publicaciones.value
    .map((item) => extractYear(item?.fecha_publicacion))
    .filter((value) => Number.isInteger(value));

  return [...new Set(years)].sort((a, b) => b - a);
});

const tipoThemeCode = computed(() => filtro.value?.value || "ALL");

const activeFiltersCount = computed(() => {
  let total = 0;

  if (filtro.value?.value !== "ALL") total += 1;
  if (normalizeText(q.value)) total += 1;
  if (filtroAnio.value) total += 1;
  if (filtroAnioDesde.value) total += 1;
  if (filtroAnioHasta.value) total += 1;

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

const cambiarFiltro = (tipo) => {
  filtro.value = tipo;
};

const clearAllFilters = () => {
  filtro.value = TIPOS.ALL;
  q.value = "";
  filtroAnio.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";
};

const countByType = (typeValue) => {
  if (typeValue === "ALL") return publicaciones.value.length;
  return publicaciones.value.filter((item) => resolveType(item) === typeValue).length;
};

const publicacionesFiltradas = computed(() => {
  const base =
    filtro.value.value === "ALL"
      ? publicaciones.value
      : publicaciones.value.filter((item) => resolveType(item) === filtro.value.value);

  const term = normalizeText(q.value);
  const anioExacto = filtroAnio.value ? Number(filtroAnio.value) : null;
  const anioDesde = filtroAnioDesde.value ? Number(filtroAnioDesde.value) : null;
  const anioHasta = filtroAnioHasta.value ? Number(filtroAnioHasta.value) : null;

  const minYear =
    !anioExacto && anioDesde && anioHasta ? Math.min(anioDesde, anioHasta) : anioDesde;

  const maxYear =
    !anioExacto && anioDesde && anioHasta ? Math.max(anioDesde, anioHasta) : anioHasta;

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

    const cumpleTexto = term ? haystack.includes(term) : true;

    const year = extractYear(item?.fecha_publicacion);
    let cumpleFecha = true;

    if (anioExacto) {
      cumpleFecha = year === anioExacto;
    } else {
      if (minYear && (!year || year < minYear)) cumpleFecha = false;
      if (maxYear && (!year || year > maxYear)) cumpleFecha = false;
    }

    return cumpleTexto && cumpleFecha;
  });
});

const emptyMessage = computed(() => {
  if (errorMsg.value) return errorMsg.value;

  const hasSearch = normalizeText(q.value).length > 0;
  const hasFilter =
    filtro.value.value !== "ALL" ||
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

const verDetalles = (id) => {
  router.push(`/publicacion/${id}`);
};

const onKey = (event) => {
  const isMac = navigator.platform.toLowerCase().includes("mac");
  const key = String(event.key || "").toLowerCase();

  const cmdk =
    (isMac && event.metaKey && key === "k") ||
    (!isMac && event.ctrlKey && key === "k");

  if (cmdk) {
    event.preventDefault();
    searchEl.value?.focus();
  }

  if (event.key === "Escape" && q.value) {
    q.value = "";
  }
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

onMounted(async () => {
  window.addEventListener("keydown", onKey);

  loading.value = true;
  errorMsg.value = "";

  try {
    const { data } = await api.get("/publicaciones/mias/");
    publicaciones.value = extractArray(data).map((item) => ({
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
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKey);
});
</script>

<style src="../listado-publicaciones/sgpc-listados-base.css"></style>
<style src="./mis-publicaciones.css"></style>