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

          <h1>Completar mi perfil</h1>

          <p>
            Solo se modificarán los datos habilitados por
            la campaña de actualización.
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
          <strong>Cargando perfil</strong>
          <span>Consultando su información académica.</span>
        </div>
      </section>

      <section
        v-else-if="!fields.length"
        class="record-panel record-empty"
      >
        <strong>No hay información pendiente</strong>

        <span>
          La campaña actual no tiene campos de perfil
          pendientes para completar.
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
              Los demás datos de su perfil permanecerán sin cambios.
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
          v-if="has('identificacion')"
          class="record-field record-wide"
        >
          <span>Cédula</span>

          <input
            v-model.trim="form.identificacion"
            type="text"
            maxlength="20"
            required
            autocomplete="off"
          >
        </label>

        <label
          v-if="has('sede') || has('carrera')"
          class="record-field"
        >
          <span>Sede</span>

          <select
            v-model="form.sede"
            :disabled="!has('sede')"
            required
            @change="onSedeChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in sedes"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.nombre }}
            </option>
          </select>

          <small
            v-if="!has('sede')"
            class="record-help"
          >
            La sede se muestra como referencia y no puede
            modificarse en esta campaña.
          </small>
        </label>

        <label
          v-if="has('carrera')"
          class="record-field"
        >
          <span>Facultad</span>

          <select
            v-model="form.facultad"
            required
            @change="onFacultadChange"
          >
            <option value="">
              Seleccione
            </option>

            <option
              v-for="item in facultades"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.nombre }}
            </option>
          </select>
        </label>

        <label
          v-if="has('carrera')"
          class="record-field record-wide"
        >
          <span>Carrera</span>

          <select
            v-model="form.carrera"
            :disabled="
              !form.sede ||
              !form.facultad
            "
            required
          >
            <option value="">
              {{
                form.sede && form.facultad
                  ? "Seleccione"
                  : "Seleccione sede y facultad"
              }}
            </option>

            <option
              v-for="item in carreras"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.nombre }}
            </option>
          </select>
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

import api from "../scripts/api/axios";
import adminApi from "../scripts/api/adminApi";

import {
  apiErrorMessage,
  asResults,
  recalcularMiActualizacion,
} from "../scripts/api/actualizacionesApi";


const route = useRoute();
const router = useRouter();

const loading = ref(true);
const saving = ref(false);

const error = ref("");

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);

const form = reactive({
  identificacion: "",
  sede: "",
  facultad: "",
  carrera: "",
});


const fields = computed(() => (
  String(route.query.campos || "")
    .split(",")
    .map((value) => value.trim())
    .filter(
      (field) =>
        [
          "identificacion",
          "sede",
          "carrera",
        ].includes(field)
    )
));


const labels = {
  identificacion: "Cédula",
  sede: "Sede",
  carrera: "Carrera",
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
  if (
    !form.sede ||
    !form.facultad
  ) {
    carreras.value = [];
    return;
  }

  carreras.value =
    list(
      await adminApi.selectsCarreras({
        sedeId: form.sede,
        facultadId: form.facultad,
      })
    );
}


async function onSedeChange() {
  if (!has("carrera")) {
    return;
  }

  form.facultad = "";
  form.carrera = "";

  carreras.value = [];
}


async function onFacultadChange() {
  form.carrera = "";

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


async function load() {
  loading.value = true;
  error.value = "";

  try {
    const [
      profileResponse,
      sedesResponse,
      facultadesResponse,
    ] = await Promise.all([
      api.get("auth/profile/"),
      adminApi.selectsSedes(),
      adminApi.selectsFacultades(),
    ]);

    const data =
      profileResponse.data || {};

    sedes.value =
      list(sedesResponse);

    facultades.value =
      list(facultadesResponse);

    form.identificacion =
      data.identificacion || "";

    form.sede =
      idValue(
        data.sede_id ||
        data.sede
      );

    form.facultad =
      idValue(
        data.facultad_id ||
        data.facultad ||
        data.carrera?.facultad_id ||
        data.carrera?.facultad
      );

    form.carrera =
      idValue(
        data.carrera_id ||
        data.carrera
      );

    if (has("carrera")) {
      await loadCarreras();
    }
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudo cargar el perfil."
      );
  } finally {
    loading.value = false;
  }
}


function validate() {
  if (
    has("identificacion") &&
    !form.identificacion
  ) {
    throw new Error(
      "Complete: Cédula."
    );
  }

  if (
    has("sede") &&
    !form.sede
  ) {
    throw new Error(
      "Complete: Sede."
    );
  }

  if (has("carrera")) {
    if (
      !form.sede ||
      !form.facultad ||
      !form.carrera
    ) {
      throw new Error(
        "Complete: sede, facultad y carrera."
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

    if (has("identificacion")) {
      payload.identificacion =
        form.identificacion;
    }

    if (has("sede")) {
      payload.sede_set =
        Number(form.sede);
    }

    if (has("carrera")) {
      payload.facultad_set =
        Number(form.facultad);

      payload.carrera_set =
        Number(form.carrera);
    }

    await api.patch(
      "auth/profile/",
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
      )
        ? err.message
        : apiErrorMessage(
            err,
            "No se pudo guardar el perfil."
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
  load
);
</script>

<style src="./actualizacion-registro.css"></style>