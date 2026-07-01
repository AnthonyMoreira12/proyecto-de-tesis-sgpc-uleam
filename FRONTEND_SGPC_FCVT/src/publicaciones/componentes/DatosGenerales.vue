<template>
  <div class="dg">
    <section class="dg-section surface-enter surface-enter--1">
      <header class="dg-section-head">
        <div>
          <p class="dg-kicker">Clasificación</p>
          <h4 class="dg-section-title">Contexto institucional</h4>
          <p class="dg-section-desc">
            Seleccione los valores que clasifican correctamente la publicación dentro del sistema.
          </p>
        </div>
      </header>

      <div class="dg-grid">
        <div class="dg-field">
          <label class="dg-label" for="dg-facultad">
            Facultad <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-facultad"
              class="dg-input"
              :value="local.facultad"
              @change="setField('facultad', $event.target.value)"
            >
              <option value="" disabled>Seleccione...</option>

              <option
                v-for="f in facultades"
                :key="f.id"
                :value="String(f.id)"
              >
                {{ f.nombre }}
              </option>
            </select>

            <p v-if="props.errors?.facultad" class="dg-hint dg-hint-err">
              {{ props.errors.facultad }}
            </p>
          </div>
        </div>

        <div class="dg-field">
          <label class="dg-label" for="dg-carrera">
            Carrera <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-carrera"
              class="dg-input"
              :value="local.carrera"
              @change="setField('carrera', $event.target.value)"
              :disabled="!local.facultad || loadingCarreras"
            >
              <option value="" disabled>
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
                v-for="c in carreras"
                :key="c.id"
                :value="String(c.id)"
              >
                {{ c.nombre }}
              </option>
            </select>

            <p v-if="!local.facultad" class="dg-hint">
              Seleccione una facultad para habilitar las carreras.
            </p>

            <p
              v-else-if="!loadingCarreras && carreras.length === 0"
              class="dg-hint dg-hint-warn"
            >
              No hay carreras disponibles para esta facultad. Revise catálogos.
            </p>

            <p v-if="props.errors?.carrera" class="dg-hint dg-hint-err">
              {{ props.errors.carrera }}
            </p>
          </div>
        </div>

        <div class="dg-field dg-span-2">
          <label class="dg-label" for="dg-proyecto">
            {{ proyectoLabelComputed }}
            <span v-if="!props.proyectoOpcional" class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-proyecto"
              class="dg-input"
              :value="local.proyecto"
              @change="setField('proyecto', $event.target.value)"
              :disabled="!local.carrera || loadingProyectos"
            >
              <option value="" disabled>
                {{
                  !local.carrera
                    ? "Seleccione carrera..."
                    : loadingProyectos
                      ? "Cargando..."
                      : "Seleccione..."
                }}
              </option>

              <option v-if="props.proyectoOpcional" value="0">
                Sin proyecto asociado
              </option>

              <option
                v-for="p in proyectosVisibles"
                :key="p.id"
                :value="String(p.id)"
              >
                {{ p.nombre }}
              </option>
            </select>

            <p v-if="!local.carrera" class="dg-hint">
              Seleccione una carrera para habilitar los proyectos.
            </p>

            <p
              v-else-if="!loadingProyectos && proyectosVisibles.length === 0"
              class="dg-hint dg-hint-warn"
            >
              No existen proyectos para esta carrera.
              <span v-if="props.proyectoOpcional">
                Puede seleccionar “Sin proyecto asociado”.
              </span>
            </p>

            <p v-if="props.errors?.proyecto" class="dg-hint dg-hint-err">
              {{ props.errors.proyecto }}
            </p>
          </div>
        </div>

        <div class="dg-field">
          <label class="dg-label" for="dg-area">
            {{ areaLabelComputed }} <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-area"
              class="dg-input"
              :value="local.area"
              @change="setField('area', $event.target.value)"
            >
              <option value="" disabled>Seleccione...</option>

              <option
                v-for="a in areas"
                :key="a.id"
                :value="String(a.id)"
              >
                {{ a.nombre }}
              </option>
            </select>

            <p v-if="props.errors?.area" class="dg-hint dg-hint-err">
              {{ props.errors.area }}
            </p>
          </div>
        </div>

        <div class="dg-field">
          <label class="dg-label" for="dg-subarea">
            {{ subareaLabelComputed }} <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-subarea"
              class="dg-input"
              :value="local.subarea"
              @change="setField('subarea', $event.target.value)"
              :disabled="!local.area || loadingSubareas"
            >
              <option value="" disabled>
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
                v-for="s in subareas"
                :key="s.id"
                :value="String(s.id)"
              >
                {{ s.nombre }}
              </option>
            </select>

            <p v-if="!local.area" class="dg-hint">
              Seleccione un área para habilitar las subáreas.
            </p>

            <p
              v-else-if="!loadingSubareas && subareas.length === 0"
              class="dg-hint dg-hint-warn"
            >
              No hay subáreas para esta área. Revise catálogos.
            </p>

            <p v-if="props.errors?.subarea" class="dg-hint dg-hint-err">
              {{ props.errors.subarea }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="!props.hideUbicacion"
      class="dg-section surface-enter surface-enter--2"
    >
      <header class="dg-section-head">
        <div>
          <p class="dg-kicker">Ubicación</p>
          <h4 class="dg-section-title">País y ciudad</h4>
          <p class="dg-section-desc">
            Seleccione país y ciudad asociados a la publicación.
          </p>
        </div>
      </header>

      <div class="dg-grid">
        <div class="dg-field">
          <label class="dg-label" for="dg-pais">
            País <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-pais"
              class="dg-input"
              :value="local.pais"
              @change="setField('pais', $event.target.value)"
            >
              <option value="" disabled>Seleccione...</option>

              <option
                v-for="p in paises"
                :key="p.id"
                :value="String(p.id)"
              >
                {{ p.nombre }}
              </option>
            </select>

            <p v-if="props.errors?.pais" class="dg-hint dg-hint-err">
              {{ props.errors.pais }}
            </p>
          </div>
        </div>

        <div class="dg-field">
          <label class="dg-label" for="dg-ciudad">
            Ciudad <span class="req">*</span>
          </label>

          <div class="dg-control dg-control--select">
            <select
              id="dg-ciudad"
              class="dg-input"
              :value="local.ciudad"
              @change="setField('ciudad', $event.target.value)"
              :disabled="!local.pais || loadingCiudades"
            >
              <option value="" disabled>
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
                v-for="c in ciudades"
                :key="c.id"
                :value="String(c.id)"
              >
                {{ c.nombre }}
              </option>
            </select>

            <p v-if="!local.pais" class="dg-hint">
              Seleccione un país para habilitar las ciudades.
            </p>

            <p
              v-else-if="!loadingCiudades && ciudades.length === 0"
              class="dg-hint dg-hint-warn"
            >
              No hay ciudades para este país. Revise catálogos.
            </p>

            <p v-if="props.errors?.ciudad" class="dg-hint dg-hint-err">
              {{ props.errors.ciudad }}
            </p>
          </div>
        </div>
      </div>

      <p v-if="error" class="dg-alert dg-alert-error">{{ error }}</p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch, computed } from "vue";
import api from "../../scripts/api/axios";

const props = defineProps({
  modelValue: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  hideUbicacion: { type: Boolean, default: false },
  proyectoOpcional: { type: Boolean, default: false },
  proyectoLabel: { type: String, default: "Proyecto de investigación" },
  areaLabel: { type: String, default: "Área del conocimiento (UNESCO)" },
  subareaLabel: { type: String, default: "Subárea del conocimiento (UNESCO)" },
});

const emit = defineEmits(["update:modelValue"]);

const asStr = (value) => {
  if (value === 0 || value === "0") return "0";
  if (value === null || value === undefined || value === "") return "";
  return String(value);
};

const resolveProyectoLocal = (value, carrera) => {
  if (value === 0 || value === "0") return "0";
  if (props.proyectoOpcional && carrera && (value === null || value === undefined || value === "")) {
    return "0";
  }
  return asStr(value);
};

const local = reactive({
  facultad: asStr(props.modelValue?.facultad),
  carrera: asStr(props.modelValue?.carrera),
  proyecto: resolveProyectoLocal(props.modelValue?.proyecto, props.modelValue?.carrera),
  area: asStr(props.modelValue?.area),
  subarea: asStr(props.modelValue?.subarea),
  pais: asStr(props.modelValue?.pais),
  ciudad: asStr(props.modelValue?.ciudad),
});

const proyectoLabelComputed = computed(
  () => props.proyectoLabel || "Proyecto de investigación"
);

const areaLabelComputed = computed(
  () => props.areaLabel || "Área del conocimiento (UNESCO)"
);

const subareaLabelComputed = computed(
  () => props.subareaLabel || "Subárea del conocimiento (UNESCO)"
);

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

let carrerasReq = 0;
let proyectosReq = 0;
let subareasReq = 0;
let ciudadesReq = 0;

const asArrayResponse = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
};

const normalizeText = (value) =>
  String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

const sortByNombre = (list) =>
  [...list].sort((a, b) =>
    String(a?.nombre || "").localeCompare(String(b?.nombre || ""), "es", {
      sensitivity: "base",
    })
  );

const normalizeCatalogItem = (item) => ({
  ...item,
  id: item?.id,
  nombre: String(item?.nombre || item?.label || item?.name || "").trim(),
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

const toNumOrNull = (value) => {
  if (!value) return null;
  if (String(value) === "0") return null;

  const number = Number(value);
  return Number.isFinite(number) ? number : null;
};

const isProyectoVisible = (proyecto) => {
  if (!proyecto) return false;

  if (proyecto.activo === false) return false;
  if (proyecto.is_active === false) return false;
  if (proyecto.visible === false) return false;

  if (typeof proyecto.estado === "boolean") {
    return proyecto.estado === true;
  }

  return true;
};

const proyectosVisibles = computed(() => {
  const seleccionado = local.proyecto ? String(local.proyecto) : null;
  const base = Array.isArray(proyectos.value) ? proyectos.value : [];
  const visibles = sortByNombre(base.filter(isProyectoVisible));

  if (seleccionado === "0") {
    return visibles;
  }

  if (seleccionado && !visibles.some((p) => String(p.id) === seleccionado)) {
    const seleccionadoObj = base.find((p) => String(p.id) === seleccionado);

    if (seleccionadoObj) {
      return [seleccionadoObj, ...visibles];
    }
  }

  return visibles;
});

const pushModel = () => {
  emit("update:modelValue", {
    facultad: toNumOrNull(local.facultad),
    carrera: toNumOrNull(local.carrera),
    proyecto: toNumOrNull(local.proyecto),
    area: toNumOrNull(local.area),
    subarea: toNumOrNull(local.subarea),
    pais: props.hideUbicacion ? null : toNumOrNull(local.pais),
    ciudad: props.hideUbicacion ? null : toNumOrNull(local.ciudad),
  });
};

const setField = (key, value) => {
  local[key] = value;

  if (key === "facultad") {
    local.carrera = "";
    local.proyecto = "";
    carreras.value = [];
    proyectos.value = [];
  }

  if (key === "carrera") {
    local.proyecto = props.proyectoOpcional ? "0" : "";
    proyectos.value = [];
  }

  if (key === "area") {
    local.subarea = "";
    subareas.value = [];
  }

  if (key === "pais") {
    local.ciudad = "";
    ciudades.value = [];
  }

  pushModel();
};

const cargarFacultades = async () => {
  const res = await api.get("/selects/facultades/");
  facultades.value = sortByNombre(
    asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
  );
};

const cargarAreas = async () => {
  const res = await api.get("/selects/areas/");
  areas.value = sortByNombre(
    asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
  );
};

const cargarPaises = async () => {
  const res = await api.get("/selects/paises/");
  paises.value = sortByNombre(
    asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
  );
};

const cargarCarreras = async (facultadId) => {
  if (!facultadId) return;

  const reqId = ++carrerasReq;
  loadingCarreras.value = true;

  try {
    const res = await api.get(`/selects/carreras/${facultadId}/`);

    if (reqId !== carrerasReq) return;

    carreras.value = sortByNombre(
      asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
    );
    error.value = "";
  } finally {
    if (reqId === carrerasReq) loadingCarreras.value = false;
  }
};

const cargarProyectos = async (carreraId) => {
  if (!carreraId) return;

  const reqId = ++proyectosReq;
  loadingProyectos.value = true;

  try {
    const params = {};

    if (local.proyecto && local.proyecto !== "0") {
      params.include = local.proyecto;
    }

    const res = await api.get(`/selects/proyectos/${carreraId}/`, { params });

    if (reqId !== proyectosReq) return;

    proyectos.value = sortByNombre(
      asArrayResponse(res.data).map(normalizeProyecto).filter((item) => item.id)
    );

    error.value = "";

    if (props.proyectoOpcional && !local.proyecto) {
      local.proyecto = "0";
      pushModel();
    }
  } finally {
    if (reqId === proyectosReq) loadingProyectos.value = false;
  }
};

const cargarSubareas = async (areaId) => {
  if (!areaId) return;

  const reqId = ++subareasReq;
  loadingSubareas.value = true;

  try {
    const res = await api.get(`/selects/subareas/${areaId}/`);

    if (reqId !== subareasReq) return;

    subareas.value = sortByNombre(
      asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
    );
    error.value = "";
  } finally {
    if (reqId === subareasReq) loadingSubareas.value = false;
  }
};

const cargarCiudades = async (paisId) => {
  if (!paisId) return;

  const reqId = ++ciudadesReq;
  loadingCiudades.value = true;

  try {
    const res = await api.get(`/selects/ciudades/${paisId}/`);

    if (reqId !== ciudadesReq) return;

    ciudades.value = sortByNombre(
      asArrayResponse(res.data).map(normalizeCatalogItem).filter((item) => item.id)
    );
    error.value = "";
  } finally {
    if (reqId === ciudadesReq) loadingCiudades.value = false;
  }
};

watch(
  () => props.modelValue,
  (value) => {
    const nextFacultad = asStr(value?.facultad);
    const nextCarrera = asStr(value?.carrera);

    local.facultad = nextFacultad;
    local.carrera = nextCarrera;
    local.proyecto = resolveProyectoLocal(value?.proyecto, nextCarrera);
    local.area = asStr(value?.area);
    local.subarea = asStr(value?.subarea);

    if (!props.hideUbicacion) {
      local.pais = asStr(value?.pais);
      local.ciudad = asStr(value?.ciudad);
    } else {
      local.pais = "";
      local.ciudad = "";
    }
  },
  { deep: true }
);

watch(
  () => props.hideUbicacion,
  (hidden) => {
    if (hidden) {
      local.pais = "";
      local.ciudad = "";
      ciudades.value = [];
      pushModel();
    }
  }
);

watch(
  () => local.facultad,
  async (value) => {
    carreras.value = [];
    proyectos.value = [];

    if (!value) return;

    try {
      await cargarCarreras(value);
    } catch (e) {
      console.warn(e);
      error.value = "Error cargando carreras.";
    }
  }
);

watch(
  () => local.carrera,
  async (value) => {
    proyectos.value = [];

    if (!value) return;

    try {
      await cargarProyectos(value);
    } catch (e) {
      console.warn(e);
      error.value = "Error cargando proyectos.";
    }
  }
);

watch(
  () => local.area,
  async (value) => {
    subareas.value = [];

    if (!value) return;

    try {
      await cargarSubareas(value);
    } catch (e) {
      console.warn(e);
      error.value = "Error cargando subáreas.";
    }
  }
);

watch(
  () => local.pais,
  async (value) => {
    if (props.hideUbicacion) return;

    ciudades.value = [];

    if (!value) return;

    try {
      await cargarCiudades(value);
    } catch (e) {
      console.warn(e);
      error.value = "Error cargando ciudades.";
    }
  }
);

onMounted(async () => {
  error.value = "";

  try {
    const baseLoads = [cargarFacultades(), cargarAreas()];

    if (!props.hideUbicacion) {
      baseLoads.push(cargarPaises());
    }

    await Promise.all(baseLoads);

    if (local.facultad) await cargarCarreras(local.facultad);
    if (local.carrera) await cargarProyectos(local.carrera);
    if (local.area) await cargarSubareas(local.area);
    if (!props.hideUbicacion && local.pais) await cargarCiudades(local.pais);

    if (props.proyectoOpcional && local.carrera && !local.proyecto) {
      local.proyecto = "0";
      pushModel();
    }
  } catch (e) {
    error.value =
      "No se pudieron cargar los catálogos requeridos. Revise los endpoints /selects/*.";
    console.warn(e);
  }
});
</script>

<style scoped src="./datos-generales.css"></style>