<template>
  <div class="dg">
    <section class="dg-section surface-enter surface-enter--1">
      <header class="dg-section-head">
        <div>
          <p class="dg-kicker">
            Clasificación
          </p>

          <h4 class="dg-section-title">
            Contexto institucional
          </h4>

          <p class="dg-section-desc">
            Seleccione los valores que clasifican correctamente la publicación
            dentro del sistema.
          </p>
        </div>
      </header>

      <div class="dg-grid">
        <!-- Facultad -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-facultad"
          >
            Facultad
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-facultad"
              class="dg-input"
              :value="local.facultad"
              :aria-invalid="Boolean(props.errors?.facultad)"
              required
              @change="setField('facultad', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                Seleccione...
              </option>

              <option
                v-for="facultad in facultades"
                :key="facultad.id"
                :value="String(facultad.id)"
              >
                {{ facultad.nombre }}
              </option>
            </select>

            <p
              v-if="props.errors?.facultad"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.facultad }}
            </p>
          </div>
        </div>

        <!-- Carrera -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-carrera"
          >
            Carrera
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-carrera"
              class="dg-input"
              :value="local.carrera"
              :disabled="!local.facultad || loadingCarreras"
              :aria-busy="loadingCarreras ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.carrera)"
              required
              @change="setField('carrera', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.facultad
                    ? "Seleccione facultad..."
                    : loadingCarreras
                      ? "Cargando..."
                      : carreras.length
                        ? "Seleccione..."
                        : "Sin carreras disponibles"
                }}
              </option>

              <option
                v-for="carrera in carreras"
                :key="carrera.id"
                :value="String(carrera.id)"
              >
                {{ carrera.nombre }}
              </option>
            </select>

            <p
              v-if="!local.facultad"
              class="dg-hint"
            >
              Seleccione una facultad para habilitar las carreras.
            </p>

            <p
              v-else-if="!loadingCarreras && carreras.length === 0"
              class="dg-hint dg-hint-warn"
            >
              No hay carreras disponibles para esta facultad. Revise los
              catálogos.
            </p>

            <p
              v-if="props.errors?.carrera"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.carrera }}
            </p>
          </div>
        </div>

        <!-- Proyecto -->
        <div class="dg-field dg-span-2">
          <label
            class="dg-label"
            for="dg-proyecto"
          >
            {{ proyectoLabelComputed }}

            <span
              v-if="!props.proyectoOpcional"
              class="req"
            >
              *
            </span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-proyecto"
              class="dg-input"
              :value="local.proyecto"
              :disabled="!local.carrera || loadingProyectos"
              :aria-busy="loadingProyectos ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.proyecto)"
              :required="!props.proyectoOpcional"
              @change="setField('proyecto', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.carrera
                    ? "Seleccione carrera..."
                    : loadingProyectos
                      ? "Cargando..."
                      : "Seleccione..."
                }}
              </option>

              <option
                v-if="props.proyectoOpcional"
                value="0"
              >
                Sin proyecto asociado
              </option>

              <option
                v-for="proyecto in proyectosVisibles"
                :key="proyecto.id"
                :value="String(proyecto.id)"
              >
                {{ proyecto.nombre }}
              </option>
            </select>

            <p
              v-if="!local.carrera"
              class="dg-hint"
            >
              Seleccione una carrera para habilitar los proyectos.
            </p>

            <p
              v-else-if="
                !loadingProyectos &&
                proyectosVisibles.length === 0
              "
              class="dg-hint dg-hint-warn"
            >
              No existen proyectos para esta carrera.

              <span v-if="props.proyectoOpcional">
                Puede seleccionar “Sin proyecto asociado”.
              </span>
            </p>

            <p
              v-if="props.errors?.proyecto"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.proyecto }}
            </p>
          </div>
        </div>

        <!-- Área -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-area"
          >
            {{ areaLabelComputed }}
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-area"
              class="dg-input"
              :value="local.area"
              :aria-invalid="Boolean(props.errors?.area)"
              required
              @change="setField('area', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                Seleccione...
              </option>

              <option
                v-for="area in areas"
                :key="area.id"
                :value="String(area.id)"
              >
                {{ area.nombre }}
              </option>
            </select>

            <p
              v-if="props.errors?.area"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.area }}
            </p>
          </div>
        </div>

        <!-- Subárea -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-subarea"
          >
            {{ subareaLabelComputed }}
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-subarea"
              class="dg-input"
              :value="local.subarea"
              :disabled="!local.area || loadingSubareas"
              :aria-busy="loadingSubareas ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.subarea)"
              required
              @change="setField('subarea', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.area
                    ? "Seleccione área..."
                    : loadingSubareas
                      ? "Cargando..."
                      : subareas.length
                        ? "Seleccione..."
                        : "Sin subáreas disponibles"
                }}
              </option>

              <option
                v-for="subarea in subareas"
                :key="subarea.id"
                :value="String(subarea.id)"
              >
                {{ subarea.nombre }}
              </option>
            </select>

            <p
              v-if="!local.area"
              class="dg-hint"
            >
              Seleccione un área para habilitar las subáreas.
            </p>

            <p
              v-else-if="
                !loadingSubareas &&
                subareas.length === 0
              "
              class="dg-hint dg-hint-warn"
            >
              No hay subáreas para esta área. Revise los catálogos.
            </p>

            <p
              v-if="props.errors?.subarea"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.subarea }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Ubicación -->
    <section
      v-if="!props.hideUbicacion"
      class="dg-section surface-enter surface-enter--2"
    >
      <header class="dg-section-head">
        <div>
          <p class="dg-kicker">
            Ubicación
          </p>

          <h4 class="dg-section-title">
            País y ciudad
          </h4>

          <p class="dg-section-desc">
            Seleccione el país y la ciudad asociados a la publicación.
          </p>
        </div>
      </header>

      <div class="dg-grid">
        <!-- País -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-pais"
          >
            País
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-pais"
              class="dg-input"
              :value="local.pais"
              :aria-invalid="Boolean(props.errors?.pais)"
              required
              @change="setField('pais', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                Seleccione...
              </option>

              <option
                v-for="pais in paises"
                :key="pais.id"
                :value="String(pais.id)"
              >
                {{ pais.nombre }}
              </option>
            </select>

            <p
              v-if="props.errors?.pais"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.pais }}
            </p>
          </div>
        </div>

        <!-- Ciudad -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-ciudad"
          >
            Ciudad
            <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-ciudad"
              class="dg-input"
              :value="local.ciudad"
              :disabled="!local.pais || loadingCiudades"
              :aria-busy="loadingCiudades ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.ciudad)"
              required
              @change="setField('ciudad', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.pais
                    ? "Seleccione país..."
                    : loadingCiudades
                      ? "Cargando..."
                      : ciudades.length
                        ? "Seleccione..."
                        : "Sin ciudades disponibles"
                }}
              </option>

              <option
                v-for="ciudad in ciudades"
                :key="ciudad.id"
                :value="String(ciudad.id)"
              >
                {{ ciudad.nombre }}
              </option>
            </select>

            <p
              v-if="!local.pais"
              class="dg-hint"
            >
              Seleccione un país para habilitar las ciudades.
            </p>

            <p
              v-else-if="
                !loadingCiudades &&
                ciudades.length === 0
              "
              class="dg-hint dg-hint-warn"
            >
              No hay ciudades para este país. Revise los catálogos.
            </p>

            <p
              v-if="props.errors?.ciudad"
              class="dg-hint dg-hint-err"
            >
              {{ props.errors.ciudad }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!--
      El error general se mantiene fuera de la sección de ubicación.
      De este modo también se muestra cuando hideUbicacion es true.
    -->
    <p
      v-if="error"
      class="dg-alert dg-alert-error"
      role="alert"
      aria-live="assertive"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import api from "../../scripts/api/axios";

/* =========================================================
   PROPIEDADES Y EVENTOS
========================================================= */

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },

  errors: {
    type: Object,
    default: () => ({}),
  },

  hideUbicacion: {
    type: Boolean,
    default: false,
  },

  proyectoOpcional: {
    type: Boolean,
    default: false,
  },

  proyectoLabel: {
    type: String,
    default: "Proyecto de investigación",
  },

  areaLabel: {
    type: String,
    default: "Área del conocimiento (UNESCO)",
  },

  subareaLabel: {
    type: String,
    default: "Subárea del conocimiento (UNESCO)",
  },
});

const emit = defineEmits([
  "update:modelValue",
]);

/* =========================================================
   NORMALIZACIÓN
========================================================= */

const asStr = (value) => {
  if (value === 0 || value === "0") {
    return "0";
  }

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "";
  }

  return String(value);
};

const toNumOrNull = (value) => {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    value === 0 ||
    value === "0"
  ) {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : null;
};

const resolveProyectoLocal = (
  value,
  carrera
) => {
  if (value === 0 || value === "0") {
    return "0";
  }

  if (
    props.proyectoOpcional &&
    carrera &&
    (
      value === null ||
      value === undefined ||
      value === ""
    )
  ) {
    return "0";
  }

  return asStr(value);
};

const asArrayResponse = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
};

const normalizeCatalogItem = (item) => ({
  ...item,

  id: item?.id,

  nombre: String(
    item?.nombre ||
    item?.label ||
    item?.name ||
    ""
  ).trim(),
});

const normalizeProyecto = (item) => ({
  ...item,

  id: item?.id,

  nombre: String(
    item?.nombre ||
    item?.titulo ||
    item?.label ||
    item?.name ||
    `Proyecto #${item?.id || ""}`
  ).trim(),
});

const sortByNombre = (list) => (
  [...list].sort((a, b) => (
    String(a?.nombre || "")
      .localeCompare(
        String(b?.nombre || ""),
        "es",
        {
          sensitivity: "base",
        }
      )
  ))
);

/* =========================================================
   ESTADO LOCAL
========================================================= */

const local = reactive({
  facultad:
    asStr(props.modelValue?.facultad),

  carrera:
    asStr(props.modelValue?.carrera),

  proyecto:
    resolveProyectoLocal(
      props.modelValue?.proyecto,
      props.modelValue?.carrera
    ),

  area:
    asStr(props.modelValue?.area),

  subarea:
    asStr(props.modelValue?.subarea),

  pais:
    asStr(props.modelValue?.pais),

  ciudad:
    asStr(props.modelValue?.ciudad),
});

const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);
const areas = ref([]);
const subareas = ref([]);
const paises = ref([]);
const ciudades = ref([]);

const loadingCarreras = ref(false);
const loadingProyectos = ref(false);
const loadingSubareas = ref(false);
const loadingCiudades = ref(false);

const error = ref("");

/* =========================================================
   IDENTIFICADORES DE SOLICITUD

   Permiten ignorar respuestas antiguas cuando el usuario
   cambia rápidamente una selección dependiente.
========================================================= */

let carrerasReq = 0;
let proyectosReq = 0;
let subareasReq = 0;
let ciudadesReq = 0;

const invalidateCarreras = () => {
  carrerasReq += 1;
  loadingCarreras.value = false;
  carreras.value = [];
};

const invalidateProyectos = () => {
  proyectosReq += 1;
  loadingProyectos.value = false;
  proyectos.value = [];
};

const invalidateSubareas = () => {
  subareasReq += 1;
  loadingSubareas.value = false;
  subareas.value = [];
};

const invalidateCiudades = () => {
  ciudadesReq += 1;
  loadingCiudades.value = false;
  ciudades.value = [];
};

/* =========================================================
   PROPIEDADES CALCULADAS
========================================================= */

const proyectoLabelComputed = computed(
  () => (
    props.proyectoLabel ||
    "Proyecto de investigación"
  )
);

const areaLabelComputed = computed(
  () => (
    props.areaLabel ||
    "Área del conocimiento (UNESCO)"
  )
);

const subareaLabelComputed = computed(
  () => (
    props.subareaLabel ||
    "Subárea del conocimiento (UNESCO)"
  )
);

const isProyectoVisible = (proyecto) => {
  if (!proyecto) {
    return false;
  }

  if (proyecto.activo === false) {
    return false;
  }

  if (proyecto.is_active === false) {
    return false;
  }

  if (proyecto.visible === false) {
    return false;
  }

  if (typeof proyecto.estado === "boolean") {
    return proyecto.estado;
  }

  return true;
};

const proyectosVisibles = computed(() => {
  const seleccionado = local.proyecto
    ? String(local.proyecto)
    : null;

  const base = Array.isArray(proyectos.value)
    ? proyectos.value
    : [];

  const visibles = sortByNombre(
    base.filter(isProyectoVisible)
  );

  if (seleccionado === "0") {
    return visibles;
  }

  const incluido = visibles.some(
    (proyecto) => (
      String(proyecto.id) === seleccionado
    )
  );

  if (seleccionado && !incluido) {
    const proyectoSeleccionado = base.find(
      (proyecto) => (
        String(proyecto.id) === seleccionado
      )
    );

    if (proyectoSeleccionado) {
      return [
        proyectoSeleccionado,
        ...visibles,
      ];
    }
  }

  return visibles;
});

/* =========================================================
   SINCRONIZACIÓN DEL MODELO
========================================================= */

const pushModel = () => {
  emit("update:modelValue", {
    facultad:
      toNumOrNull(local.facultad),

    carrera:
      toNumOrNull(local.carrera),

    proyecto:
      toNumOrNull(local.proyecto),

    area:
      toNumOrNull(local.area),

    subarea:
      toNumOrNull(local.subarea),

    pais:
      props.hideUbicacion
        ? null
        : toNumOrNull(local.pais),

    ciudad:
      props.hideUbicacion
        ? null
        : toNumOrNull(local.ciudad),
  });
};

const setField = (
  key,
  value
) => {
  local[key] = value;

  if (key === "facultad") {
    local.carrera = "";
    local.proyecto = "";

    invalidateCarreras();
    invalidateProyectos();
  }

  if (key === "carrera") {
    local.proyecto =
      props.proyectoOpcional
        ? "0"
        : "";

    invalidateProyectos();
  }

  if (key === "area") {
    local.subarea = "";

    invalidateSubareas();
  }

  if (key === "pais") {
    local.ciudad = "";

    invalidateCiudades();
  }

  pushModel();
};

/* =========================================================
   CARGA DE CATÁLOGOS BASE
========================================================= */

const cargarFacultades = async () => {
  const response = await api.get(
    "/selects/facultades/"
  );

  facultades.value = sortByNombre(
    asArrayResponse(response.data)
      .map(normalizeCatalogItem)
      .filter((item) => item.id)
  );
};

const cargarAreas = async () => {
  const response = await api.get(
    "/selects/areas/"
  );

  areas.value = sortByNombre(
    asArrayResponse(response.data)
      .map(normalizeCatalogItem)
      .filter((item) => item.id)
  );
};

const cargarPaises = async () => {
  const response = await api.get(
    "/selects/paises/"
  );

  paises.value = sortByNombre(
    asArrayResponse(response.data)
      .map(normalizeCatalogItem)
      .filter((item) => item.id)
  );
};

/* =========================================================
   CARGA DE CATÁLOGOS DEPENDIENTES
========================================================= */

const cargarCarreras = async (
  facultadId
) => {
  if (!facultadId) {
    return;
  }

  const requestId = ++carrerasReq;

  loadingCarreras.value = true;

  try {
    const response = await api.get(
      `/selects/carreras/${facultadId}/`
    );

    if (requestId !== carrerasReq) {
      return;
    }

    carreras.value = sortByNombre(
      asArrayResponse(response.data)
        .map(normalizeCatalogItem)
        .filter((item) => item.id)
    );

    error.value = "";
  } finally {
    if (requestId === carrerasReq) {
      loadingCarreras.value = false;
    }
  }
};

const cargarProyectos = async (
  carreraId
) => {
  if (!carreraId) {
    return;
  }

  const requestId = ++proyectosReq;

  loadingProyectos.value = true;

  try {
    const params = {};

    if (
      local.proyecto &&
      local.proyecto !== "0"
    ) {
      params.include = local.proyecto;
    }

    const response = await api.get(
      `/selects/proyectos/${carreraId}/`,
      {
        params,
      }
    );

    if (requestId !== proyectosReq) {
      return;
    }

    proyectos.value = sortByNombre(
      asArrayResponse(response.data)
        .map(normalizeProyecto)
        .filter((item) => item.id)
    );

    error.value = "";

    if (
      props.proyectoOpcional &&
      !local.proyecto
    ) {
      local.proyecto = "0";

      pushModel();
    }
  } finally {
    if (requestId === proyectosReq) {
      loadingProyectos.value = false;
    }
  }
};

const cargarSubareas = async (
  areaId
) => {
  if (!areaId) {
    return;
  }

  const requestId = ++subareasReq;

  loadingSubareas.value = true;

  try {
    const response = await api.get(
      `/selects/subareas/${areaId}/`
    );

    if (requestId !== subareasReq) {
      return;
    }

    subareas.value = sortByNombre(
      asArrayResponse(response.data)
        .map(normalizeCatalogItem)
        .filter((item) => item.id)
    );

    error.value = "";
  } finally {
    if (requestId === subareasReq) {
      loadingSubareas.value = false;
    }
  }
};

const cargarCiudades = async (
  paisId
) => {
  if (!paisId) {
    return;
  }

  const requestId = ++ciudadesReq;

  loadingCiudades.value = true;

  try {
    const response = await api.get(
      `/selects/ciudades/${paisId}/`
    );

    if (requestId !== ciudadesReq) {
      return;
    }

    ciudades.value = sortByNombre(
      asArrayResponse(response.data)
        .map(normalizeCatalogItem)
        .filter((item) => item.id)
    );

    error.value = "";
  } finally {
    if (requestId === ciudadesReq) {
      loadingCiudades.value = false;
    }
  }
};

/* =========================================================
   OBSERVADORES
========================================================= */

watch(
  () => props.modelValue,

  (value) => {
    const nextFacultad =
      asStr(value?.facultad);

    const nextCarrera =
      asStr(value?.carrera);

    local.facultad =
      nextFacultad;

    local.carrera =
      nextCarrera;

    local.proyecto =
      resolveProyectoLocal(
        value?.proyecto,
        nextCarrera
      );

    local.area =
      asStr(value?.area);

    local.subarea =
      asStr(value?.subarea);

    if (!props.hideUbicacion) {
      local.pais =
        asStr(value?.pais);

      local.ciudad =
        asStr(value?.ciudad);
    } else {
      local.pais = "";
      local.ciudad = "";
    }
  },

  {
    deep: true,
  }
);

watch(
  () => props.hideUbicacion,

  (hidden) => {
    if (!hidden) {
      return;
    }

    local.pais = "";
    local.ciudad = "";

    invalidateCiudades();
    pushModel();
  }
);

watch(
  () => local.facultad,

  async (value) => {
    invalidateCarreras();
    invalidateProyectos();

    if (!value) {
      return;
    }

    try {
      await cargarCarreras(value);
    } catch (catalogError) {
      console.warn(catalogError);

      error.value =
        "No se pudieron cargar las carreras.";
    }
  }
);

watch(
  () => local.carrera,

  async (value) => {
    invalidateProyectos();

    if (!value) {
      return;
    }

    try {
      await cargarProyectos(value);
    } catch (catalogError) {
      console.warn(catalogError);

      error.value =
        "No se pudieron cargar los proyectos.";
    }
  }
);

watch(
  () => local.area,

  async (value) => {
    invalidateSubareas();

    if (!value) {
      return;
    }

    try {
      await cargarSubareas(value);
    } catch (catalogError) {
      console.warn(catalogError);

      error.value =
        "No se pudieron cargar las subáreas.";
    }
  }
);

watch(
  () => local.pais,

  async (value) => {
    invalidateCiudades();

    if (
      props.hideUbicacion ||
      !value
    ) {
      return;
    }

    try {
      await cargarCiudades(value);
    } catch (catalogError) {
      console.warn(catalogError);

      error.value =
        "No se pudieron cargar las ciudades.";
    }
  }
);

/* =========================================================
   INICIALIZACIÓN
========================================================= */

onMounted(async () => {
  error.value = "";

  try {
    const baseLoads = [
      cargarFacultades(),
      cargarAreas(),
    ];

    if (!props.hideUbicacion) {
      baseLoads.push(
        cargarPaises()
      );
    }

    await Promise.all(baseLoads);

    if (local.facultad) {
      await cargarCarreras(
        local.facultad
      );
    }

    if (local.carrera) {
      await cargarProyectos(
        local.carrera
      );
    }

    if (local.area) {
      await cargarSubareas(
        local.area
      );
    }

    if (
      !props.hideUbicacion &&
      local.pais
    ) {
      await cargarCiudades(
        local.pais
      );
    }

    if (
      props.proyectoOpcional &&
      local.carrera &&
      !local.proyecto
    ) {
      local.proyecto = "0";

      pushModel();
    }
  } catch (catalogError) {
    console.warn(catalogError);

    error.value =
      "No se pudieron cargar los catálogos requeridos. Revise los endpoints /selects/*.";
  }
});
</script>

<style scoped src="./datos-generales.css"></style>