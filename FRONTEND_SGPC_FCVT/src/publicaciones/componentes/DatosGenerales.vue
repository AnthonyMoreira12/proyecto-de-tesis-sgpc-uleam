<template>
  <div class="dg">
    <!-- =====================================================
         CONTEXTO INSTITUCIONAL
    ====================================================== -->
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

      <div class="dg-grid dg-grid--institutional">
        <!-- Sede -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-sede"
          >
            Sede
            <span class="req" aria-hidden="true">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-sede"
              class="dg-input"
              :value="local.sede"
              :aria-invalid="Boolean(props.errors?.sede)"
              :aria-describedby="sedeDescriptionIds"
              required
              @change="setField('sede', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                Seleccione...
              </option>

              <option
                v-for="sede in sedes"
                :key="sede.id"
                :value="String(sede.id)"
              >
                {{ sede.nombre }}
              </option>
            </select>

            <p
              id="dg-sede-help"
              class="dg-hint"
            >
              La sede define las facultades y carreras disponibles para la publicación.
            </p>

            <p
              v-if="props.errors?.sede"
              id="dg-sede-error"
              class="dg-hint dg-hint-err"
              role="alert"
            >
              {{ props.errors.sede }}
            </p>
          </div>
        </div>

        <!-- Facultad disponible en la sede -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-facultad"
          >
            Facultad
            <span class="req" aria-hidden="true">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-facultad"
              class="dg-input"
              :value="local.facultad"
              :disabled="!local.sede || loadingFacultades"
              :aria-busy="loadingFacultades ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.facultad)"
              :aria-describedby="facultadDescriptionIds"
              required
              @change="setField('facultad', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.sede
                    ? "Seleccione sede..."
                    : loadingFacultades
                      ? "Cargando..."
                      : facultades.length
                        ? "Seleccione..."
                        : "Sin facultades disponibles"
                }}
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
              v-if="!local.sede"
              id="dg-facultad-help"
              class="dg-hint"
            >
              Seleccione primero una sede para mostrar las facultades disponibles.
            </p>

            <p
              v-else-if="
                !loadingFacultades &&
                facultades.length === 0
              "
              id="dg-facultad-empty"
              class="dg-hint dg-hint-warn"
            >
              No hay facultades con carreras habilitadas en la sede seleccionada.
            </p>

            <p
              v-else
              id="dg-facultad-available"
              class="dg-hint"
            >
              Solo se muestran facultades con carreras habilitadas en esta sede.
            </p>

            <p
              v-if="props.errors?.facultad"
              id="dg-facultad-error"
              class="dg-hint dg-hint-err"
              role="alert"
            >
              {{ props.errors.facultad }}
            </p>
          </div>
        </div>

        <!-- Carrera habilitada en sede + facultad -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-carrera"
          >
            Carrera
            <span class="req" aria-hidden="true">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-carrera"
              class="dg-input"
              :value="local.carrera"
              :disabled="!local.sede || !local.facultad || loadingCarreras"
              :aria-busy="loadingCarreras ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.carrera)"
              :aria-describedby="carreraDescriptionIds"
              required
              @change="setField('carrera', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.sede
                    ? "Seleccione sede..."
                    : !local.facultad
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
              v-if="!local.sede || !local.facultad"
              id="dg-carrera-help"
              class="dg-hint"
            >
              Seleccione una sede y una facultad para habilitar sus carreras.
            </p>

            <p
              v-else-if="
                !loadingCarreras &&
                carreras.length === 0
              "
              id="dg-carrera-empty"
              class="dg-hint dg-hint-warn"
            >
              No hay carreras activas para la sede y facultad seleccionadas.
            </p>

            <p
              v-else
              id="dg-carrera-available"
              class="dg-hint"
            >
              Solo se muestran carreras habilitadas en esta sede y facultad.
            </p>

            <p
              v-if="props.errors?.carrera"
              id="dg-carrera-error"
              class="dg-hint dg-hint-err"
              role="alert"
            >
              {{ props.errors.carrera }}
            </p>
          </div>
        </div>

        <!-- Proyecto -->
        <div class="dg-field">
          <label
            class="dg-label"
            for="dg-proyecto"
          >
            {{ proyectoLabelComputed }}
            <span v-if="props.proyectoOpcional">
              (opcional)
            </span>

            <span
              v-if="!props.proyectoOpcional"
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-proyecto"
              class="dg-input"
              :value="local.proyecto"
              :disabled="!local.sede || !local.facultad || !local.carrera || loadingProyectos"
              :aria-busy="loadingProyectos ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.proyecto)"
              :aria-describedby="proyectoDescriptionIds"
              :required="!props.proyectoOpcional"
              @change="setField('proyecto', $event.target.value)"
            >
              <option
                value=""
                disabled
              >
                {{
                  !local.sede
                    ? "Seleccione sede..."
                    : !local.facultad
                      ? "Seleccione facultad..."
                      : !local.carrera
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
                {{ proyectoOptionLabel(proyecto) }}
              </option>
            </select>

            <p
              v-if="!local.sede || !local.facultad || !local.carrera"
              id="dg-proyecto-help"
              class="dg-hint"
            >
              Seleccione sede, facultad y carrera para habilitar los proyectos compatibles.
            </p>

            <p
              v-else-if="
                !loadingProyectos &&
                proyectosVisibles.length === 0
              "
              id="dg-proyecto-empty"
              class="dg-hint dg-hint-warn"
            >
              No existen proyectos disponibles para esta carrera.

              <span v-if="props.proyectoOpcional">
                Puede seleccionar “Sin proyecto asociado”.
              </span>
            </p>

            <p
              v-if="props.errors?.proyecto"
              id="dg-proyecto-error"
              class="dg-hint dg-hint-err"
              role="alert"
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
            <span>(opcional)</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-area"
              class="dg-input"
              :value="local.area"
              :aria-invalid="Boolean(props.errors?.area)"
              :aria-describedby="areaDescriptionIds"
              @change="setField('area', $event.target.value)"
            >
              <option value="">
                Sin área seleccionada
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
              v-if="!local.area"
              id="dg-area-help"
              class="dg-hint"
            >
              Opcional. Seleccione un área únicamente si corresponde a la publicación.
            </p>

            <p
              v-if="props.errors?.area"
              id="dg-area-error"
              class="dg-hint dg-hint-err"
              role="alert"
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
            <span>(opcional)</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-subarea"
              class="dg-input"
              :value="local.subarea"
              :disabled="!local.area || loadingSubareas"
              :aria-busy="loadingSubareas ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.subarea)"
              :aria-describedby="subareaDescriptionIds"
              @change="setField('subarea', $event.target.value)"
            >
              <option value="">
                {{
                  !local.area
                    ? "Seleccione un área..."
                    : loadingSubareas
                      ? "Cargando..."
                      : "Sin subárea seleccionada"
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
              id="dg-subarea-help"
              class="dg-hint"
            >
              La subárea es opcional. Seleccione primero un área si desea registrarla.
            </p>

            <p
              v-else-if="
                !loadingSubareas &&
                subareas.length === 0
              "
              id="dg-subarea-empty"
              class="dg-hint dg-hint-warn"
            >
              No hay subáreas disponibles para el área seleccionada.
            </p>

            <p
              v-else-if="
                local.area &&
                !loadingSubareas
              "
              id="dg-subarea-optional"
              class="dg-hint"
            >
              Opcional. Puede dejar este campo sin seleccionar.
            </p>

            <p
              v-if="props.errors?.subarea"
              id="dg-subarea-error"
              class="dg-hint dg-hint-err"
              role="alert"
            >
              {{ props.errors.subarea }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- =====================================================
         UBICACIÓN GEOGRÁFICA
         Solo se muestra en formularios que la necesitan,
         principalmente Ponencia.
    ====================================================== -->
    <section
      v-if="!props.hideUbicacion"
      class="dg-section surface-enter surface-enter--2"
    >
      <header class="dg-section-head">
        <div>
          <p class="dg-kicker">
            {{ props.ubicacionKicker }}
          </p>

          <h4 class="dg-section-title">
            {{ props.ubicacionTitulo }}
          </h4>

          <p class="dg-section-desc">
            {{ props.ubicacionDescripcion }}
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
            {{ props.paisLabel }}
            <span class="req" aria-hidden="true">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-pais"
              class="dg-input"
              :value="local.pais"
              :aria-invalid="Boolean(props.errors?.pais)"
              :aria-describedby="
                props.errors?.pais
                  ? 'dg-pais-error'
                  : undefined
              "
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
              id="dg-pais-error"
              class="dg-hint dg-hint-err"
              role="alert"
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
            {{ props.ciudadLabel }}
            <span class="req" aria-hidden="true">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-ciudad"
              class="dg-input"
              :value="local.ciudad"
              :disabled="!local.pais || loadingCiudades"
              :aria-busy="loadingCiudades ? 'true' : 'false'"
              :aria-invalid="Boolean(props.errors?.ciudad)"
              :aria-describedby="ciudadDescriptionIds"
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
              id="dg-ciudad-help"
              class="dg-hint"
            >
              Seleccione un país para habilitar las ciudades.
            </p>

            <p
              v-else-if="
                !loadingCiudades &&
                ciudades.length === 0
              "
              id="dg-ciudad-empty"
              class="dg-hint dg-hint-warn"
            >
              No hay ciudades disponibles para este país.
            </p>

            <p
              v-if="props.errors?.ciudad"
              id="dg-ciudad-error"
              class="dg-hint dg-hint-err"
              role="alert"
            >
              {{ props.errors.ciudad }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Error general de catálogos -->
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
  onBeforeUnmount,
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
    default: true,
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

  ubicacionKicker: {
    type: String,
    default: "Ubicación",
  },

  ubicacionTitulo: {
    type: String,
    default: "Contexto geográfico",
  },

  ubicacionDescripcion: {
    type: String,
    default: "Seleccione el país y la ciudad relacionados con la publicación.",
  },

  paisLabel: {
    type: String,
    default: "País",
  },

  ciudadLabel: {
    type: String,
    default: "Ciudad",
  },
});

const emit = defineEmits([
  "update:modelValue",
]);

/* =========================================================
   HELPERS
========================================================= */

const asStr = (value) => {
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

  return Number.isFinite(number) && number > 0
    ? number
    : null;
};

const resolveProyectoLocal = (
  value,
  carrera
) => {
  if (
    value === 0 ||
    value === "0"
  ) {
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

  id:
    item?.id ??
    item?.value ??
    null,

  nombre: String(
    item?.nombre ||
    item?.label ||
    item?.name ||
    ""
  ).trim(),
});

const normalizeCarrera = (item) => ({
  ...normalizeCatalogItem(item),

  facultad_id:
    item?.facultad_id ??
    item?.facultad?.id ??
    item?.faculty_id ??
    null,

  facultad_nombre: String(
    item?.facultad_nombre ||
    (
      typeof item?.facultad === "string"
        ? item.facultad
        : item?.facultad?.nombre
    ) ||
    item?.faculty_name ||
    ""
  ).trim(),

  sede_id:
    item?.sede_id ??
    item?.sede?.id ??
    null,
});

const normalizeProyecto = (item) => ({
  ...item,

  id:
    item?.id ??
    item?.value ??
    null,

  nombre: String(
    item?.nombre ||
    item?.titulo ||
    item?.label ||
    item?.name ||
    "Proyecto sin nombre"
  ).trim(),

  estado: String(
    item?.estado || ""
  )
    .trim()
    .toLowerCase(),

  estado_label: String(
    item?.estado_label ||
    item?.estadoLabel ||
    ""
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

const sortPaises = (list) => (
  [...list].sort((a, b) => {
    const isoA = String(a?.iso2 || "")
      .trim()
      .toUpperCase();
    const isoB = String(b?.iso2 || "")
      .trim()
      .toUpperCase();

    const prioridadA = isoA === "EC" ? 0 : 1;
    const prioridadB = isoB === "EC" ? 0 : 1;

    if (prioridadA !== prioridadB) {
      return prioridadA - prioridadB;
    }

    return String(a?.nombre || "")
      .localeCompare(
        String(b?.nombre || ""),
        "es",
        {
          sensitivity: "base",
        }
      );
  })
);

const sortByCodigo = (list) => (
  [...list].sort((a, b) => {
    const codigoA = String(
      a?.codigo || ""
    ).trim();

    const codigoB = String(
      b?.codigo || ""
    ).trim();

    if (codigoA && codigoB) {
      return codigoA.localeCompare(
        codigoB,
        "es",
        {
          numeric: true,
        }
      );
    }

    return String(
      a?.nombre || ""
    ).localeCompare(
      String(
        b?.nombre || ""
      ),
      "es",
      {
        sensitivity: "base",
      }
    );
  })
);

const hasItemId = (
  list,
  value
) => {
  const target = asStr(value);

  if (!target) {
    return false;
  }

  return list.some(
    (item) => (
      String(item?.id) === target
    )
  );
};

const catalogErrorMessage = (
  catalogError,
  fallback
) => {
  const status =
    catalogError?.response?.status;

  if (status === 401) {
    return (
      "La sesión ha expirado. Inicie sesión nuevamente para cargar los catálogos."
    );
  }

  if (status === 403) {
    return (
      "No tiene permisos para consultar los catálogos requeridos."
    );
  }

  return fallback;
};

/* =========================================================
   ESTADO LOCAL
========================================================= */

const local = reactive({
  sede:
    asStr(
      props.modelValue?.sede
    ),

  facultad:
    asStr(
      props.modelValue?.facultad
    ),

  carrera:
    asStr(
      props.modelValue?.carrera
    ),

  proyecto:
    resolveProyectoLocal(
      props.modelValue?.proyecto,
      props.modelValue?.carrera
    ),

  area:
    asStr(
      props.modelValue?.area
    ),

  subarea:
    asStr(
      props.modelValue?.subarea
    ),

  pais:
    props.hideUbicacion
      ? ""
      : asStr(
          props.modelValue?.pais
        ),

  ciudad:
    props.hideUbicacion
      ? ""
      : asStr(
          props.modelValue?.ciudad
        ),
});

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);
const areas = ref([]);
const subareas = ref([]);
const paises = ref([]);
const ciudades = ref([]);

const loadingFacultades = ref(false);
const loadingCarreras = ref(false);
const loadingProyectos = ref(false);
const loadingSubareas = ref(false);
const loadingCiudades = ref(false);

const error = ref("");

/* =========================================================
   IDENTIFICADORES DE SOLICITUD

   Permiten ignorar respuestas antiguas cuando el usuario
   cambia rápidamente un select dependiente.
========================================================= */

let facultadesReq = 0;
let carrerasReq = 0;
let proyectosReq = 0;
let subareasReq = 0;
let ciudadesReq = 0;

let destroyed = false;

const invalidateFacultades = () => {
  facultadesReq += 1;
  loadingFacultades.value = false;
  facultades.value = [];
};

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

const sedeDescriptionIds = computed(() => {
  const ids = ["dg-sede-help"];

  if (props.errors?.sede) {
    ids.push("dg-sede-error");
  }

  return ids.join(" ");
});

const carreraSeleccionada = computed(() => (
  carreras.value.find(
    (item) => String(item?.id) === String(local.carrera || "")
  ) || null
));

const facultadDescriptionIds = computed(() => {
  const ids = [];

  if (!local.sede) {
    ids.push("dg-facultad-help");
  } else if (
    !loadingFacultades.value &&
    facultades.value.length === 0
  ) {
    ids.push("dg-facultad-empty");
  } else {
    ids.push("dg-facultad-available");
  }

  if (props.errors?.facultad) {
    ids.push("dg-facultad-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});

const carreraDescriptionIds = computed(() => {
  const ids = [];

  if (!local.sede || !local.facultad) {
    ids.push("dg-carrera-help");
  } else if (
    !loadingCarreras.value &&
    carreras.value.length === 0
  ) {
    ids.push("dg-carrera-empty");
  } else {
    ids.push("dg-carrera-available");
  }

  if (props.errors?.carrera) {
    ids.push("dg-carrera-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});

const areaDescriptionIds = computed(() => {
  const ids = [];

  if (!local.area) {
    ids.push("dg-area-help");
  }

  if (props.errors?.area) {
    ids.push("dg-area-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});


const proyectoDescriptionIds = computed(() => {
  const ids = [];

  if (!local.sede || !local.facultad || !local.carrera) {
    ids.push("dg-proyecto-help");
  }

  if (
    local.sede &&
    local.facultad &&
    local.carrera &&
    !loadingProyectos.value &&
    proyectosVisibles.value.length === 0
  ) {
    ids.push("dg-proyecto-empty");
  }

  if (props.errors?.proyecto) {
    ids.push("dg-proyecto-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});

const subareaDescriptionIds = computed(() => {
  const ids = [];

  if (!local.area) {
    ids.push("dg-subarea-help");
  }

  if (
    local.area &&
    !loadingSubareas.value &&
    subareas.value.length === 0
  ) {
    ids.push("dg-subarea-empty");
  }

  if (
    local.area &&
    !loadingSubareas.value &&
    subareas.value.length > 0
  ) {
    ids.push("dg-subarea-optional");
  }

  if (props.errors?.subarea) {
    ids.push("dg-subarea-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});

const ciudadDescriptionIds = computed(() => {
  const ids = [];

  if (!local.pais) {
    ids.push("dg-ciudad-help");
  }

  if (
    local.pais &&
    !loadingCiudades.value &&
    ciudades.value.length === 0
  ) {
    ids.push("dg-ciudad-empty");
  }

  if (props.errors?.ciudad) {
    ids.push("dg-ciudad-error");
  }

  return ids.length
    ? ids.join(" ")
    : undefined;
});

/* =========================================================
   PROYECTOS

   La política de qué proyectos puede consultar cada usuario
   corresponde al backend.

   Aquí únicamente se conservan comprobaciones de
   compatibilidad con respuestas antiguas.
========================================================= */

const isProyectoVisible = (proyecto) => {
  if (!proyecto) {
    return false;
  }

  if (proyecto.visible === false) {
    return false;
  }

  if (proyecto.activo === false) {
    return false;
  }

  if (proyecto.is_active === false) {
    return false;
  }

  return true;
};

const proyectosVisibles = computed(() => {
  const seleccionado =
    local.proyecto &&
    local.proyecto !== "0"
      ? String(local.proyecto)
      : "";

  const base =
    Array.isArray(proyectos.value)
      ? proyectos.value
      : [];

  const visibles = sortByNombre(
    base.filter(
      isProyectoVisible
    )
  );

  if (!seleccionado) {
    return visibles;
  }

  const seleccionadoYaVisible =
    visibles.some(
      (proyecto) => (
        String(proyecto.id) ===
        seleccionado
      )
    );

  if (seleccionadoYaVisible) {
    return visibles;
  }

  /*
   * Permite mantener visible un proyecto previamente
   * seleccionado aunque la respuesta lo marque con alguna
   * bandera heredada de visibilidad.
   */
  const proyectoSeleccionado =
    base.find(
      (proyecto) => (
        String(proyecto.id) ===
        seleccionado
      )
    );

  if (!proyectoSeleccionado) {
    return visibles;
  }

  return [
    proyectoSeleccionado,
    ...visibles.filter(
      (proyecto) => (
        String(proyecto.id) !==
        seleccionado
      )
    ),
  ];
});

const proyectoOptionLabel = (
  proyecto
) => {
  const nombre =
    String(
      proyecto?.nombre || ""
    ).trim() ||
    "Proyecto sin nombre";

  const estadoLabel =
    String(
      proyecto?.estado_label || ""
    ).trim();

  if (!estadoLabel) {
    return nombre;
  }

  return `${nombre} · ${estadoLabel}`;
};

/* =========================================================
   SINCRONIZACIÓN DEL MODELO
========================================================= */

const syncFacultadFromCarrera = () => {
  if (!local.carrera) {
    local.facultad = "";
    return;
  }

  const carrera = carreras.value.find(
    (item) => String(item?.id) === String(local.carrera)
  );

  local.facultad = carrera?.facultad_id
    ? String(carrera.facultad_id)
    : "";
};

const pushModel = () => {
  emit(
    "update:modelValue",
    {
      sede:
        toNumOrNull(
          local.sede
        ),

      /*
       * Facultad forma parte del flujo de selección
       * Sede -> Facultad -> Carrera.
       *
       * Debe emitirse aunque Carrera todavía no esté seleccionada;
       * de lo contrario el componente padre recibe null y vuelve a
       * limpiar el <select> de Facultad inmediatamente después del
       * cambio.
       *
       * Cuando se selecciona Carrera, syncFacultadFromCarrera()
       * vuelve a confirmar que esta Facultad corresponda realmente
       * a la Carrera elegida.
       */
      facultad:
        toNumOrNull(
          local.facultad
        ),

      carrera:
        toNumOrNull(
          local.carrera
        ),

      /*
       * "0" existe únicamente dentro del select para
       * representar "Sin proyecto".
       *
       * Nunca sale del componente como 0:
       * "0" -> null.
       */
      proyecto:
        toNumOrNull(
          local.proyecto
        ),

      area:
        toNumOrNull(
          local.area
        ),

      subarea:
        toNumOrNull(
          local.subarea
        ),

      pais:
        props.hideUbicacion
          ? null
          : toNumOrNull(
              local.pais
            ),

      ciudad:
        props.hideUbicacion
          ? null
          : toNumOrNull(
              local.ciudad
            ),
    }
  );
};

const setField = (
  key,
  value
) => {
  error.value = "";

  local[key] =
    value === null ||
    value === undefined
      ? ""
      : String(value);

  /*
   * Flujo institucional de selección:
   * Sede -> Facultad -> Carrera -> Proyecto.
   *
   * La relación real sigue siendo Carrera -> Facultad y
   * CarreraSede valida que la Carrera esté habilitada en la Sede.
   */
  if (key === "sede") {
    local.facultad = "";
    local.carrera = "";
    local.proyecto = "";
  }

  if (key === "facultad") {
    local.carrera = "";
    local.proyecto = "";
  }

  /*
   * Al cambiar Carrera se confirma la Facultad desde la propia
   * Carrera y cualquier proyecto anterior deja de ser válido.
   */
  if (key === "carrera") {
    syncFacultadFromCarrera();

    local.proyecto =
      props.proyectoOpcional
        ? "0"
        : "";
  }

  /*
   * Área -> Subárea
   */
  if (key === "area") {
    local.subarea = "";
  }

  /*
   * País -> Ciudad
   */
  if (key === "pais") {
    local.ciudad = "";
  }

  pushModel();
};

/* =========================================================
   CATÁLOGOS BASE
========================================================= */

const cargarSedes = async () => {
  const response = await api.get(
    "/selects/sedes/"
  );

  if (destroyed) {
    return;
  }

  sedes.value = sortByNombre(
    asArrayResponse(
      response.data
    )
      .map(
        normalizeCatalogItem
      )
      .filter(
        (item) => item.id
      )
  );

  if (
    local.sede &&
    !hasItemId(
      sedes.value,
      local.sede
    )
  ) {
    local.sede = "";
    local.facultad = "";
    local.carrera = "";
    local.proyecto = "";
    pushModel();
  }
};

const cargarFacultades = async (
  sedeId
) => {
  if (!sedeId) {
    facultades.value = [];
    return;
  }

  const requestId =
    ++facultadesReq;

  loadingFacultades.value = true;

  try {
    const response = await api.get(
      "/selects/facultades/",
      {
        params: {
          sede_id: sedeId,
        },
      }
    );

    if (
      destroyed ||
      requestId !== facultadesReq
    ) {
      return;
    }

    facultades.value = sortByNombre(
      asArrayResponse(
        response.data
      )
        .map(
          normalizeCatalogItem
        )
        .filter(
          (item) => item.id
        )
    );

    if (
      local.facultad &&
      !hasItemId(
        facultades.value,
        local.facultad
      )
    ) {
      local.facultad = "";
      local.carrera = "";
      local.proyecto =
        props.proyectoOpcional
          ? "0"
          : "";

      pushModel();
    }

    error.value = "";
  } finally {
    if (
      requestId === facultadesReq
    ) {
      loadingFacultades.value = false;
    }
  }
};

const cargarAreas = async () => {
  const response = await api.get(
    "/selects/areas/"
  );

  if (destroyed) {
    return;
  }

  areas.value = sortByCodigo(
    asArrayResponse(
      response.data
    )
      .map(
        normalizeCatalogItem
      )
      .filter(
        (item) => item.id
      )
  );
};

const cargarPaises = async () => {
  const response = await api.get(
    "/selects/paises/"
  );

  if (destroyed) {
    return;
  }

  paises.value = sortPaises(
    asArrayResponse(
      response.data
    )
      .map(
        normalizeCatalogItem
      )
      .filter(
        (item) => item.id
      )
  );
};

/* =========================================================
   CATÁLOGOS DEPENDIENTES
========================================================= */

const cargarCarreras = async (
  sedeId,
  facultadId
) => {
  if (!sedeId || !facultadId) {
    carreras.value = [];
    return;
  }

  const requestId =
    ++carrerasReq;

  loadingCarreras.value = true;

  try {
    const response = await api.get(
      "/selects/carreras/",
      {
        params: {
          sede_id: sedeId,
          facultad_id: facultadId,
        },
      }
    );

    if (
      destroyed ||
      requestId !== carrerasReq
    ) {
      return;
    }

    carreras.value = sortByNombre(
      asArrayResponse(
        response.data
      )
        .map(
          normalizeCarrera
        )
        .filter(
          (item) => item.id
        )
    );

    /*
     * Una Carrera restaurada desde un borrador solo se conserva
     * si continúa habilitada mediante CarreraSede en la Sede
     * seleccionada.
     */
    if (
      local.carrera &&
      !hasItemId(
        carreras.value,
        local.carrera
      )
    ) {
      local.carrera = "";

      local.proyecto =
        props.proyectoOpcional
          ? "0"
          : "";

      pushModel();
    } else if (local.carrera) {
      const facultadAnterior =
        local.facultad;

      syncFacultadFromCarrera();

      if (
        local.facultad !==
        facultadAnterior
      ) {
        pushModel();
      }
    }

    error.value = "";
  } finally {
    if (
      requestId === carrerasReq
    ) {
      loadingCarreras.value = false;
    }
  }
};

const cargarProyectos = async (
  carreraId
) => {
  if (!carreraId) {
    proyectos.value = [];
    return;
  }

  const requestId =
    ++proyectosReq;

  loadingProyectos.value = true;

  try {
    const params = {};

    if (local.sede) {
      params.sede_id = local.sede;
    }

    /*
     * El backend permite mantener un proyecto ya
     * seleccionado mediante ?include=<id>.
     */
    if (
      local.proyecto &&
      local.proyecto !== "0"
    ) {
      params.include =
        local.proyecto;
    }

    const response = await api.get(
      `/selects/proyectos/${carreraId}/`,
      {
        params,
      }
    );

    if (
      destroyed ||
      requestId !== proyectosReq
    ) {
      return;
    }

    proyectos.value = sortByNombre(
      asArrayResponse(
        response.data
      )
        .map(
          normalizeProyecto
        )
        .filter(
          (item) => item.id
        )
    );

    if (
      local.proyecto &&
      local.proyecto !== "0" &&
      !hasItemId(
        proyectos.value,
        local.proyecto
      )
    ) {
      local.proyecto =
        props.proyectoOpcional
          ? "0"
          : "";

      pushModel();
    }

    if (
      props.proyectoOpcional &&
      !local.proyecto
    ) {
      local.proyecto = "0";
      pushModel();
    }

    error.value = "";
  } finally {
    if (
      requestId === proyectosReq
    ) {
      loadingProyectos.value = false;
    }
  }
};

const cargarSubareas = async (
  areaId
) => {
  if (!areaId) {
    subareas.value = [];
    return;
  }

  const requestId =
    ++subareasReq;

  loadingSubareas.value = true;

  try {
    const response = await api.get(
      `/selects/subareas/${areaId}/`
    );

    if (
      destroyed ||
      requestId !== subareasReq
    ) {
      return;
    }

    subareas.value = sortByCodigo(
      asArrayResponse(
        response.data
      )
        .map(
          normalizeCatalogItem
        )
        .filter(
          (item) => item.id
        )
    );

    if (
      local.subarea &&
      !hasItemId(
        subareas.value,
        local.subarea
      )
    ) {
      local.subarea = "";
      pushModel();
    }

    error.value = "";
  } finally {
    if (
      requestId === subareasReq
    ) {
      loadingSubareas.value = false;
    }
  }
};

const cargarCiudades = async (
  paisId
) => {
  if (
    props.hideUbicacion ||
    !paisId
  ) {
    ciudades.value = [];
    return;
  }

  const requestId =
    ++ciudadesReq;

  loadingCiudades.value = true;

  try {
    const response = await api.get(
      `/selects/ciudades/${paisId}/`
    );

    if (
      destroyed ||
      requestId !== ciudadesReq
    ) {
      return;
    }

    ciudades.value = sortByNombre(
      asArrayResponse(
        response.data
      )
        .map(
          normalizeCatalogItem
        )
        .filter(
          (item) => item.id
        )
    );

    if (
      local.ciudad &&
      !hasItemId(
        ciudades.value,
        local.ciudad
      )
    ) {
      local.ciudad = "";
      pushModel();
    }

    error.value = "";
  } finally {
    if (
      requestId === ciudadesReq
    ) {
      loadingCiudades.value = false;
    }
  }
};

/* =========================================================
   OBSERVADORES
========================================================= */

/*
 * Sincroniza cambios que lleguen desde el componente padre:
 * restauración de borrador, edición, limpieza del formulario,
 * etc.
 */
watch(
  () => props.modelValue,

  (value) => {
    const nextSede =
      asStr(
        value?.sede
      );

    const nextFacultad =
      asStr(
        value?.facultad
      );

    const nextCarrera =
      asStr(
        value?.carrera
      );

    local.sede =
      nextSede;

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
      asStr(
        value?.area
      );

    local.subarea =
      asStr(
        value?.subarea
      );

    if (
      props.hideUbicacion
    ) {
      local.pais = "";
      local.ciudad = "";
    } else {
      local.pais =
        asStr(
          value?.pais
        );

      local.ciudad =
        asStr(
          value?.ciudad
        );
    }
  },

  {
    deep: true,
  }
);

/*
 * Al ocultar la ubicación se eliminan explícitamente país y
 * ciudad para impedir que una publicación que no los admite
 * los conserve en el payload.
 */
watch(
  () => props.hideUbicacion,

  async (hidden) => {
    if (hidden) {
      local.pais = "";
      local.ciudad = "";

      invalidateCiudades();

      pushModel();
      return;
    }

    try {
      await cargarPaises();

      if (local.pais) {
        await cargarCiudades(
          local.pais
        );
      }
    } catch (catalogError) {
      console.warn(
        "Error cargando ubicación:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar los catálogos de ubicación."
        );
    }
  }
);

/*
 * Sede -> Facultades disponibles
 */
watch(
  () => local.sede,

  async (value) => {
    invalidateFacultades();
    invalidateCarreras();
    invalidateProyectos();

    if (!value) {
      return;
    }

    try {
      await cargarFacultades(
        value
      );

      if (local.facultad) {
        await cargarCarreras(
          value,
          local.facultad
        );
      }
    } catch (catalogError) {
      console.warn(
        "Error cargando facultades por sede:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar las facultades disponibles para la sede."
        );
    }
  }
);

/*
 * Facultad -> Carreras habilitadas en la Sede
 */
watch(
  () => local.facultad,

  async (value) => {
    invalidateCarreras();
    invalidateProyectos();

    if (!value || !local.sede) {
      return;
    }

    try {
      await cargarCarreras(
        local.sede,
        value
      );
    } catch (catalogError) {
      console.warn(
        "Error cargando carreras por sede y facultad:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar las carreras de la facultad seleccionada."
        );
    }
  }
);

/*
 * Carrera -> Proyectos
 */
watch(
  () => local.carrera,

  async (value) => {
    invalidateProyectos();

    if (!value) {
      return;
    }

    syncFacultadFromCarrera();

    if (!local.sede) {
      return;
    }

    try {
      await cargarProyectos(
        value
      );
    } catch (catalogError) {
      console.warn(
        "Error cargando proyectos:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar los proyectos."
        );
    }
  }
);

/*
 * Área -> Subáreas
 */
watch(
  () => local.area,

  async (value) => {
    invalidateSubareas();

    if (!value) {
      return;
    }

    try {
      await cargarSubareas(
        value
      );
    } catch (catalogError) {
      console.warn(
        "Error cargando subáreas:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar las subáreas."
        );
    }
  }
);

/*
 * País -> Ciudades
 */
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
      await cargarCiudades(
        value
      );
    } catch (catalogError) {
      console.warn(
        "Error cargando ciudades:",
        catalogError
      );

      error.value =
        catalogErrorMessage(
          catalogError,
          "No se pudieron cargar las ciudades."
        );
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
      cargarSedes(),
      cargarAreas(),
    ];

    if (
      !props.hideUbicacion
    ) {
      baseLoads.push(
        cargarPaises()
      );
    }

    await Promise.all(
      baseLoads
    );

    /*
     * Carga inicial de catálogos dependientes cuando el
     * formulario viene restaurado desde borrador o edición.
     */
    if (
      local.sede
    ) {
      await cargarFacultades(
        local.sede
      );
    }

    if (
      local.sede &&
      local.facultad
    ) {
      await cargarCarreras(
        local.sede,
        local.facultad
      );
    }

    if (
      local.sede &&
      local.facultad &&
      local.carrera
    ) {
      await cargarProyectos(
        local.carrera
      );
    }

    if (
      local.area
    ) {
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

    /*
     * El valor "0" es exclusivamente visual.
     * pushModel() lo transforma inmediatamente en null.
     */
    if (
      props.proyectoOpcional &&
      local.carrera &&
      !local.proyecto
    ) {
      local.proyecto = "0";
      pushModel();
    }
  } catch (catalogError) {
    console.warn(
      "Error inicializando DatosGenerales:",
      catalogError
    );

    error.value =
      catalogErrorMessage(
        catalogError,
        "No se pudieron cargar los catálogos requeridos. Verifique la conexión con el servidor."
      );
  }
});

/* =========================================================
   LIMPIEZA
========================================================= */

onBeforeUnmount(() => {
  destroyed = true;

  /*
   * Invalida cualquier respuesta asíncrona pendiente.
   */
  facultadesReq += 1;
  carrerasReq += 1;
  proyectosReq += 1;
  subareasReq += 1;
  ciudadesReq += 1;
});
</script>

<style scoped src="./datos-generales.css"></style>
