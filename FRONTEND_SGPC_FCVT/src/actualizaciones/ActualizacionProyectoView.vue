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

          <h1>
            {{
              project?.nombre ||
              project?.titulo ||
              `Proyecto #${route.params.id}`
            }}
          </h1>

          <p>
            Solo se modificarán los campos habilitados
            mediante la campaña de actualización.
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
          <strong>Cargando proyecto</strong>

          <span>
            Consultando la información del proyecto.
          </span>
        </div>
      </section>

      <section
        v-else-if="!fields.length"
        class="record-panel record-empty"
      >
        <strong>No hay campos habilitados</strong>

        <span>
          Este proyecto no requiere información adicional
          dentro de la campaña actual.
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
        <section class="record-fields-note">
          <div>
            <strong>Campos habilitados</strong>

            <small>
              Solo estos datos serán modificados.
            </small>
          </div>

          <div class="record-field-chips">
            <span
              v-for="field in fields"
              :key="field"
            >
              {{ label(field) }}
            </span>
          </div>
        </section>

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
              v-for="item in options.sede"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.nombre }}
            </option>
          </select>
        </label>

        <label
          v-if="has('carrera')"
          class="record-field"
        >
          <span>Carrera</span>

          <select
            v-model="form.carrera"
            :disabled="!form.sede"
            required
          >
            <option value="">
              {{
                form.sede
                  ? "Seleccione"
                  : "Seleccione primero una sede"
              }}
            </option>

            <option
              v-for="item in options.carrera"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.nombre }}
            </option>
          </select>
        </label>

        <label
          v-if="has('descripcion')"
          class="record-field record-wide"
        >
          <span>Descripción</span>

          <textarea
            v-model.trim="form.descripcion"
            rows="5"
            required
          ></textarea>
        </label>

        <label
          v-if="has('fecha_inicio')"
          class="record-field"
        >
          <span>Fecha de inicio</span>

          <input
            v-model="form.fecha_inicio"
            type="date"
            required
          >
        </label>

        <label
          v-if="has('fecha_fin_planificada')"
          class="record-field"
        >
          <span>Fecha de finalización planificada</span>

          <input
            v-model="form.fecha_fin_planificada"
            type="date"
            required
          >
        </label>

        <label
          v-if="has('fecha_fin_prorrogada')"
          class="record-field"
        >
          <span>Fecha de finalización prorrogada</span>

          <input
            v-model="form.fecha_fin_prorrogada"
            type="date"
            required
          >
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

import adminApi from "../scripts/api/adminApi";

import {
  actualizarProyecto,
  obtenerProyecto,
} from "../scripts/api/proyectosApi";

import {
  apiErrorMessage,
  asResults,
  recalcularMiActualizacion,
} from "../scripts/api/actualizacionesApi";


const route = useRoute();
const router = useRouter();

const project = ref(null);

const loading = ref(true);
const saving = ref(false);

const error = ref("");

const form = reactive({
  sede: "",
  carrera: "",
  descripcion: "",
  fecha_inicio: "",
  fecha_fin_planificada: "",
  fecha_fin_prorrogada: "",
});

const options = reactive({
  sede: [],
  carrera: [],
});


const allowedFields = [
  "sede",
  "carrera",
  "descripcion",
  "fecha_inicio",
  "fecha_fin_planificada",
  "fecha_fin_prorrogada",
];


const fields = computed(() => (
  String(route.query.campos || "")
    .split(",")
    .map((value) => value.trim())
    .filter(
      (field) =>
        allowedFields.includes(field)
    )
));


const labels = {
  sede: "Sede",
  carrera: "Carrera",
  descripcion: "Descripción",
  fecha_inicio: "Fecha de inicio",
  fecha_fin_planificada:
    "Fecha de finalización planificada",
  fecha_fin_prorrogada:
    "Fecha de finalización prorrogada",
};


function has(field) {
  return fields.value.includes(field);
}


function label(field) {
  return labels[field] || field;
}


function list(payload) {
  const results = asResults(payload);

  return results.length
    ? results
    : Array.isArray(payload)
      ? payload
      : [];
}


function idValue(value) {
  if (
    value &&
    typeof value === "object"
  ) {
    return String(
      value.id || ""
    );
  }

  return String(
    value || ""
  );
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
    list(
      await adminApi.selectsCarreras({
        sedeId: form.sede,
      })
    );
}


async function onSedeChange() {
  if (!has("carrera")) {
    return;
  }

  form.carrera = "";
  options.carrera = [];

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


async function hydrate() {
  loading.value = true;
  error.value = "";

  try {
    project.value =
      await obtenerProyecto(
        route.params.id
      );

    for (const field of fields.value) {
      if (
        field === "sede" ||
        field === "carrera"
      ) {
        form[field] =
          idValue(
            project.value?.[`${field}_id`] ||
            project.value?.[field]
          );
      } else {
        form[field] =
          project.value?.[field] ||
          "";
      }
    }

    options.sede =
      list(
        await adminApi.selectsSedes()
      );

    await loadCarreras();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudo cargar el proyecto."
      );
  } finally {
    loading.value = false;
  }
}


function validate() {
  for (const field of fields.value) {
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

  if (
    has("fecha_inicio") &&
    has("fecha_fin_planificada") &&
    form.fecha_inicio &&
    form.fecha_fin_planificada &&
    form.fecha_fin_planificada <
      form.fecha_inicio
  ) {
    throw new Error(
      "La fecha de finalización planificada no puede ser anterior a la fecha de inicio."
    );
  }

  if (
    has("fecha_fin_prorrogada") &&
    form.fecha_fin_planificada &&
    form.fecha_fin_prorrogada &&
    form.fecha_fin_prorrogada <
      form.fecha_fin_planificada
  ) {
    throw new Error(
      "La fecha prorrogada no puede ser anterior a la fecha de finalización planificada."
    );
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

    for (const field of fields.value) {
      payload[field] =
        ["sede", "carrera"].includes(field)
          ? Number(form[field])
          : form[field];
    }

    await actualizarProyecto(
      route.params.id,
      payload
    );

    if (route.query.participacion) {
      await recalcularMiActualizacion(
        route.query.participacion
      );
    }

    await router.push(
      "/informacion-pendiente"
    );
  } catch (err) {
    error.value =
      err?.message?.startsWith(
        "Complete:"
      ) ||
      err?.message?.startsWith(
        "La fecha"
      )
        ? err.message
        : apiErrorMessage(
            err,
            "No se pudo guardar el proyecto."
          );
  } finally {
    saving.value = false;
  }
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