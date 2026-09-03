<template>
  <main class="record-update-page">
    <section class="record-update-shell">
      <header class="record-update-hero">
        <button
          type="button"
          class="record-back"
          @click="goBack"
        >
          ← Volver
        </button>

        <div class="record-update-hero__copy">
          <span>Actualización controlada</span>

          <h1>{{ title }}</h1>

          <p>
            Revise la información actual y complete únicamente los datos
            solicitados por la campaña de actualización vigente.
          </p>
        </div>
      </header>

      <p
        v-if="error"
        class="record-alert record-alert--error"
        role="alert"
      >
        {{ error }}
      </p>

      <section
        v-if="loading"
        class="record-panel record-loading"
      >
        <span class="record-spinner"></span>

        <div>
          <strong>Cargando publicación</strong>
          <span>Consultando la información disponible.</span>
        </div>
      </section>

      <section
        v-else-if="!allowed.length"
        class="record-panel record-empty"
      >
        <strong>No hay información pendiente</strong>

        <span>
          Esta publicación no tiene campos habilitados para actualizar
          mediante la campaña actual.
        </span>

        <button
          type="button"
          class="record-secondary"
          @click="goBack"
        >
          Volver
        </button>
      </section>

      <form
        v-else
        class="record-panel record-form"
        @submit.prevent="save"
      >
        <!-- =====================================================
             INFORMACIÓN ACTUAL / SOLO LECTURA
        ====================================================== -->
        <section
          v-if="contextItems.length"
          class="record-current-info"
          aria-labelledby="record-current-title"
        >
          <header class="record-section-heading">
            <div>
              <strong id="record-current-title">
                Información actual
              </strong>

              <small>
                Estos datos son de referencia y no se modificarán con
                esta actualización.
              </small>
            </div>

            <span class="record-readonly-badge">
              Solo lectura
            </span>
          </header>

          <dl class="record-current-grid">
            <div
              v-for="item in contextItems"
              :key="item.key"
              class="record-current-item"
            >
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>
        </section>

        <!-- =====================================================
             INFORMACIÓN PENDIENTE / EDITABLE
        ====================================================== -->
        <section
          class="record-pending-heading"
          aria-labelledby="record-pending-title"
        >
          <div>
            <strong id="record-pending-title">
              Información pendiente
            </strong>

            <small>
              {{ pendingSummary }} Solo estos datos serán enviados al guardar.
            </small>
          </div>
        </section>

        <!-- SEDE -->
        <label
          v-if="has('sede')"
          class="record-field"
        >
          <span>Sede</span>

          <select
            v-model="form.sede"
            required
            @change="onSedeChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in options.sede || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- CARRERA -->
        <label
          v-if="has('carrera')"
          class="record-field"
        >
          <span>Carrera</span>

          <small class="record-field__context">
            Sede relacionada: {{ dependencyValue('sede') }}
          </small>

          <select
            v-model="form.carrera"
            required
            @change="onCarreraChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in options.carrera || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- ÁREA -->
        <label
          v-if="has('area')"
          class="record-field"
        >
          <span>Área UNESCO</span>

          <select
            v-model="form.area"
            required
            @change="onAreaChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in options.area || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- SUBÁREA -->
        <label
          v-if="has('subarea')"
          class="record-field"
        >
          <span>Subárea UNESCO</span>

          <small class="record-field__context">
            Área UNESCO relacionada: {{ dependencyValue('area') }}
          </small>

          <select
            v-model="form.subarea"
            :disabled="!form.area"
            required
          >
            <option value="">
              {{
                form.area
                  ? "Seleccione"
                  : "Seleccione primero un área"
              }}
            </option>

            <option
              v-for="item in options.subarea || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- PAÍS -->
        <label
          v-if="has('pais')"
          class="record-field"
        >
          <span>País</span>

          <select
            v-model="form.pais"
            required
            @change="onPaisChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in options.pais || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- CIUDAD -->
        <label
          v-if="has('ciudad')"
          class="record-field"
        >
          <span>Ciudad</span>

          <small class="record-field__context">
            País relacionado: {{ dependencyValue('pais') }}
          </small>

          <select
            v-model="form.ciudad"
            :disabled="!form.pais"
            required
          >
            <option value="">
              {{
                form.pais
                  ? "Seleccione"
                  : "Seleccione primero un país"
              }}
            </option>

            <option
              v-for="item in options.ciudad || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>
        </label>

        <!-- PROYECTO -->
        <label
          v-if="has('proyecto')"
          class="record-field record-wide"
        >
          <span>Proyecto asociado</span>

          <small class="record-field__context">
            Carrera relacionada: {{ dependencyValue('carrera') }}
          </small>

          <select
            v-model="form.proyecto"
            :disabled="!form.carrera"
            required
          >
            <option value="">
              {{
                form.carrera
                  ? "Seleccione"
                  : "Seleccione primero una carrera"
              }}
            </option>

            <option
              v-for="item in options.proyecto || []"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ optionLabel(item) }}
            </option>
          </select>

          <small
            v-if="form.carrera && !options.proyecto.length"
            class="record-help"
          >
            No hay proyectos disponibles para la carrera relacionada con
            esta publicación.
          </small>
        </label>

        <footer class="record-actions">
          <button
            type="button"
            class="record-secondary"
            :disabled="saving"
            @click="goBack"
          >
            Cancelar
          </button>

          <button
            type="submit"
            :disabled="saving"
          >
            {{
              saving
                ? "Guardando..."
                : "Guardar información"
            }}
          </button>
        </footer>
      </form>
    </section>

    <!-- =====================================================
         CONFIRMACIÓN DE ACTUALIZACIÓN
    ====================================================== -->
    <div
      v-if="successVisible"
      class="record-success-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="record-success-title"
      aria-describedby="record-success-description"
    >
      <div
        class="record-success-modal__backdrop"
        aria-hidden="true"
      ></div>

      <section
        class="record-success-modal__card"
        tabindex="-1"
      >
        <span
          class="record-success-modal__icon"
          aria-hidden="true"
        >
          <svg viewBox="0 0 24 24">
            <circle
              cx="12"
              cy="12"
              r="9"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            />

            <path
              d="m8 12.2 2.5 2.5L16.5 9"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>

        <div class="record-success-modal__content">
          <span class="record-success-modal__eyebrow">
            Actualización completada
          </span>

          <h2 id="record-success-title">
            Información guardada correctamente
          </h2>

          <p id="record-success-description">
            {{ successMessage }}
          </p>
        </div>

        <button
          type="button"
          class="record-success-modal__button"
          autofocus
          @click="finishSuccessfulUpdate"
        >
          Entendido
        </button>
      </section>
    </div>
  </main>
</template>

<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../scripts/api/axios";

import {
  obtenerPublicacionDetalle,
} from "../scripts/api/publicacionesApi";

import {
  apiErrorMessage,
  asResults,
  recalcularMiActualizacion,
} from "../scripts/api/actualizacionesApi";


const route = useRoute();
const router = useRouter();

const detail = ref(null);

const loading = ref(true);
const saving = ref(false);

const error = ref("");
const successVisible = ref(false);

const form = reactive({
  sede: "",
  carrera: "",
  area: "",
  subarea: "",
  pais: "",
  ciudad: "",
  proyecto: "",
});

const options = reactive({
  sede: [],
  carrera: [],
  area: [],
  subarea: [],
  pais: [],
  ciudad: [],
  proyecto: [],
});


const requested = computed(() => (
  String(route.query.campos || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean)
));


const allowed = computed(() => {
  const backend =
    Array.isArray(
      detail.value?.campos_editables_campania
    )
      ? detail.value.campos_editables_campania
      : [];

  if (!requested.value.length) {
    return backend;
  }

  return backend.filter(
    (field) =>
      requested.value.includes(field)
  );
});


const title = computed(() => (
  detail.value?.nombre_articulo ||
  detail.value?.nombre_ponencia ||
  detail.value?.nombre_libro ||
  detail.value?.nombre_capitulo ||
  detail.value?.titulo ||
  `Publicación #${route.params.id}`
));


const labels = {
  sede: "Sede",
  carrera: "Carrera",
  area: "Área UNESCO",
  subarea: "Subárea UNESCO",
  pais: "País",
  ciudad: "Ciudad",
  proyecto: "Proyecto asociado",
};


const pendingSummary = computed(() => {
  const total = allowed.value.length;

  if (total === 1) {
    return "Hay 1 dato que requiere actualización.";
  }

  return `Hay ${total} datos que requieren actualización.`;
});


const successMessage = computed(() => {
  const total = allowed.value.length;

  if (total === 1) {
    return (
      "El dato solicitado fue actualizado correctamente. " +
      "Puede volver a Información pendiente para continuar."
    );
  }

  return (
    `Los ${total} datos solicitados fueron actualizados correctamente. ` +
    "Puede volver a Información pendiente para continuar."
  );
});


const contextItems = computed(() => {
  const data = detail.value || {};

  const items = [
    {
      key: "tipo",
      field: null,
      label: "Tipo de publicación",
      value:
        data.tipo_publicacion_final_label ||
        data.tipo ||
        data.tipo_codigo,
    },
    {
      key: "periodo",
      field: null,
      label: "Periodo de publicación",
      value: publicationPeriod(data),
    },
    {
      key: "sede",
      field: "sede",
      label: "Sede",
      value: data.sede,
    },
    {
      key: "facultad",
      field: null,
      label: "Facultad",
      value: data.facultad,
    },
    {
      key: "carrera",
      field: "carrera",
      label: "Carrera",
      value: data.carrera,
    },
    {
      key: "area",
      field: "area",
      label: "Área UNESCO",
      value: data.area,
    },
    {
      key: "subarea",
      field: "subarea",
      label: "Subárea UNESCO",
      value: data.subarea,
    },
    {
      key: "pais",
      field: "pais",
      label: "País",
      value: data.pais,
    },
    {
      key: "ciudad",
      field: "ciudad",
      label: "Ciudad",
      value: data.ciudad,
    },
    {
      key: "proyecto",
      field: "proyecto",
      label: "Proyecto asociado",
      value: data.proyecto,
    },
  ];

  return items
    .filter((item) => (
      !item.field || !has(item.field)
    ))
    .map((item) => ({
      ...item,
      value: readableValue(item.value),
    }))
    .filter((item) => Boolean(item.value));
});


function has(field) {
  return allowed.value.includes(field);
}


function label(field) {
  return labels[field] || field;
}


function optionLabel(item) {
  return (
    item?.nombre ||
    item?.titulo ||
    item?.label ||
    `Registro ${item?.id ?? ""}`
  );
}


function readableValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "";
  }

  if (typeof value === "object") {
    return optionLabel(value);
  }

  return String(value).trim();
}


function publicationPeriod(data) {
  const year = readableValue(
    data?.anio_publicacion
  );

  const month = readableValue(
    data?.mes_publicacion_label
  );

  if (month && year) {
    return `${month} ${year}`;
  }

  return year || month;
}


function dependencyValue(field) {
  const selectedId = form[field];

  if (selectedId) {
    const selected =
      (options[field] || []).find(
        (item) =>
          String(item?.id) ===
          String(selectedId)
      );

    if (selected) {
      return optionLabel(selected);
    }
  }

  const current = readableValue(
    detail.value?.[field]
  );

  return current || "Sin información registrada";
}


function list(payload) {
  const results = asResults(payload);

  if (results.length) {
    return results;
  }

  return Array.isArray(payload)
    ? payload
    : [];
}


function idValue(value) {
  if (
    value &&
    typeof value === "object"
  ) {
    return value.id
      ? String(value.id)
      : "";
  }

  if (
    value !== null &&
    value !== undefined &&
    /^\d+$/.test(String(value))
  ) {
    return String(value);
  }

  return "";
}


async function get(url, params = undefined) {
  const response =
    await api.get(
      url,
      params
        ? { params }
        : undefined
    );

  return list(response.data);
}


async function loadCarreras() {
  if (!has("carrera")) {
    return;
  }

  if (!form.sede) {
    options.carrera = [];
    return;
  }

  options.carrera =
    await get(
      "selects/carreras/",
      {
        sede_id: form.sede,
      }
    );
}


async function loadSubareas() {
  if (!has("subarea")) {
    return;
  }

  if (!form.area) {
    options.subarea = [];
    return;
  }

  options.subarea =
    await get(
      `selects/subareas/${form.area}/`
    );
}


async function loadCiudades() {
  if (!has("ciudad")) {
    return;
  }

  if (!form.pais) {
    options.ciudad = [];
    return;
  }

  options.ciudad =
    await get(
      `selects/ciudades/${form.pais}/`
    );
}


async function loadProyectos() {
  if (!has("proyecto")) {
    return;
  }

  if (!form.carrera) {
    options.proyecto = [];
    return;
  }

  options.proyecto =
    await get(
      `selects/proyectos/${form.carrera}/`
    );
}


async function onSedeChange() {
  if (has("carrera")) {
    form.carrera = "";
    options.carrera = [];
  }

  if (has("proyecto")) {
    form.proyecto = "";
    options.proyecto = [];
  }

  try {
    await loadCarreras();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudieron cargar las carreras."
      );
  }
}


async function onCarreraChange() {
  if (has("proyecto")) {
    form.proyecto = "";
    options.proyecto = [];
  }

  try {
    await loadProyectos();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudieron cargar los proyectos."
      );
  }
}


async function onAreaChange() {
  if (has("subarea")) {
    form.subarea = "";
    options.subarea = [];
  }

  try {
    await loadSubareas();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudieron cargar las subáreas."
      );
  }
}


async function onPaisChange() {
  if (has("ciudad")) {
    form.ciudad = "";
    options.ciudad = [];
  }

  try {
    await loadCiudades();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudieron cargar las ciudades."
      );
  }
}


async function hydrate() {
  loading.value = true;
  error.value = "";

  try {
    detail.value =
      await obtenerPublicacionDetalle(
        route.params.id
      );

    if (
      !detail.value
        ?.edicion_por_campania
    ) {
      throw new Error(
        "Esta publicación no tiene una campaña de actualización activa."
      );
    }

    // Los campos padre se cargan como contexto aunque no estén habilitados
    // para edición. Esto permite resolver correctamente dependencias como:
    // Área -> Subárea, Carrera -> Proyecto, País -> Ciudad y Sede -> Carrera.
    const contextFields = [
      "sede",
      "carrera",
      "area",
      "pais",
    ];

    for (const field of contextFields) {
      form[field] =
        idValue(
          detail.value?.[`${field}_id`] ??
          detail.value?.[field]
        );
    }

    // Los valores habilitados por la campaña se conservan cuando ya existen.
    // Al guardar, únicamente estos campos forman parte del payload PATCH.
    for (const field of allowed.value) {
      form[field] =
        idValue(
          detail.value?.[`${field}_id`] ??
          detail.value?.[field]
        );
    }

    const initialLoaders = [];

    if (has("sede")) {
      initialLoaders.push(
        get("selects/sedes/")
          .then(
            (items) =>
              options.sede = items
          )
      );
    }

    if (has("area")) {
      initialLoaders.push(
        get("selects/areas/")
          .then(
            (items) =>
              options.area = items
          )
      );
    }

    if (has("pais")) {
      initialLoaders.push(
        get("selects/paises/")
          .then(
            (items) =>
              options.pais = items
          )
      );
    }

    await Promise.all(
      initialLoaders
    );

    await loadCarreras();
    await loadSubareas();
    await loadCiudades();
    await loadProyectos();
  } catch (err) {
    error.value =
      err?.message?.startsWith(
        "Esta publicación"
      )
        ? err.message
        : apiErrorMessage(
            err,
            "No se pudo cargar la publicación."
          );
  } finally {
    loading.value = false;
  }
}


function validate() {
  for (const field of allowed.value) {
    if (
      form[field] === "" ||
      form[field] === null ||
      form[field] === undefined
    ) {
      throw new Error(
        `Complete: ${label(field)}.`
      );
    }
  }
}


async function save() {
  if (saving.value) {
    return;
  }

  saving.value = true;
  error.value = "";

  try {
    validate();

    const payload = {};

    // Protección de actualización controlada:
    // nunca se envían datos de solo lectura o contexto.
    for (const field of allowed.value) {
      payload[field] =
        Number(form[field]);
    }

    await api.patch(
      `publicaciones/${route.params.id}/`,
      payload
    );

    if (route.query.participacion) {
      await recalcularMiActualizacion(
        route.query.participacion
      );
    }

    successVisible.value = true;
  } catch (err) {
    error.value =
      err?.message?.startsWith(
        "Complete:"
      )
        ? err.message
        : apiErrorMessage(
            err,
            "No se pudo guardar la información."
          );
  } finally {
    saving.value = false;
  }
}


async function finishSuccessfulUpdate() {
  successVisible.value = false;

  await router.push(
    "/informacion-pendiente"
  );
}


function goBack() {
  router.push(
    "/informacion-pendiente"
  );
}


onMounted(
  hydrate
);
</script>

<style src="./actualizacion-registro.css"></style>
