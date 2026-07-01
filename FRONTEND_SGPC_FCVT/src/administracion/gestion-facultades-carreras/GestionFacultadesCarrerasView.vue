<template>
  <div class="sgpc-admin-page admin-container">
    <div class="catalogos-manager">
      <header
        class="catalog-head adm-surface page-stage page-hero"
        aria-label="Administrar facultades y carreras"
      >
        <div class="catalog-head__main">
          <div class="catalog-head__copy">
            <span class="adm-kicker">Catálogos</span>

            <h1 class="adm-title catalog-head__title">
              Administrar facultades y carreras
            </h1>

            <p class="adm-subtitle catalog-head__subtitle">
              Gestione los catálogos académicos principales desde una vista directa,
              compacta y consistente con la línea institucional del sistema.
            </p>
          </div>

          <div class="catalog-head__actions">
            <button class="catalog-back btn-soft" type="button" @click="goBack">
              Volver
            </button>
          </div>
        </div>

        <div
          class="adm-tabs catalog-tabs"
          role="tablist"
          aria-label="Seleccionar catálogo"
        >
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="adm-tab catalog-tabs__btn"
            :class="{ active: active === tab.key }"
            type="button"
            role="tab"
            :aria-selected="active === tab.key ? 'true' : 'false'"
            @click="setActive(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>
      </header>

      <section class="catalog-content page-stage page-main">
        <Transition name="page-assembly" mode="out-in">
          <CatalogCrud
            v-if="active === 'facultades'"
            key="facultades"
            title="Facultades"
            description="Cree, edite y mantenga las facultades registradas."
            :fetchRows="fetchFacultades"
            :createRow="createFacultad"
            :updateRow="updateFacultad"
            :deleteRow="deleteFacultad"
            :columns="facultadColumns"
            :fields="facultadFields"
          />

          <CatalogCrud
            v-else
            key="carreras"
            title="Carreras"
            description="Administre las carreras asociadas a cada facultad."
            :fetchRows="fetchCarreras"
            :createRow="createCarrera"
            :updateRow="updateCarrera"
            :deleteRow="deleteCarrera"
            :columns="carreraColumns"
            :fields="carreraFields"
          />
        </Transition>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import api from "../../scripts/api/axios";
import CatalogCrud from "./FacultadesCarrerasCrud.vue";

const router = useRouter();
const route = useRoute();

const tabs = [
  { key: "facultades", label: "Facultades" },
  { key: "carreras", label: "Carreras" },
];

const VALID_TABS = tabs.map((tab) => tab.key);

const active = ref("facultades");
const facultades = ref([]);

const normalizeList = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
};

const syncTabFromRoute = () => {
  const tab = String(route.query?.tab || "").toLowerCase();
  active.value = VALID_TABS.includes(tab) ? tab : "facultades";
};

watch(
  () => route.query?.tab,
  () => syncTabFromRoute(),
  { immediate: true }
);

const goBack = () => {
  router.push("/admin/panel");
};

const setActive = (key) => {
  if (!VALID_TABS.includes(key) || active.value === key) return;

  active.value = key;

  router.replace({
    query: {
      ...route.query,
      tab: key,
    },
  });
};

/* ============================================================
   FACULTADES
============================================================ */

const fetchFacultades = async () => {
  const { data } = await api.get("admin/facultades/");
  const list = normalizeList(data);
  facultades.value = list;
  return list;
};

const createFacultad = async (payload) => {
  const { data } = await api.post("admin/facultades/", payload);
  await loadFacultadesForCarreras();
  return data;
};

const updateFacultad = async (id, payload) => {
  const { data } = await api.patch(`admin/facultades/${id}/`, payload);
  await loadFacultadesForCarreras();
  return data;
};

const deleteFacultad = async (id) => {
  const { data } = await api.delete(`admin/facultades/${id}/`);
  await loadFacultadesForCarreras();
  return data;
};

const facultadColumns = [
  { key: "nombre", label: "Nombre" },
  { key: "siglas", label: "Siglas" },
];

const facultadFields = [
  {
    key: "nombre",
    label: "Nombre de la facultad",
    required: true,
    placeholder: "Ej.: Facultad de Ciencias de la Vida y Tecnologías",
    helpTitle: "Nombre",
    help: "Use el nombre institucional completo y consistente.",
    maxLength: 140,
  },
  {
    key: "siglas",
    label: "Siglas",
    required: true,
    placeholder: "Ej.: FCVT",
    helpTitle: "Siglas",
    help: "Abreviatura corta y reconocible.",
    maxLength: 20,
  },
];

/* ============================================================
   CARRERAS
============================================================ */

const fetchCarreras = async () => {
  const { data } = await api.get("admin/carreras/");
  return normalizeList(data);
};

const createCarrera = async (payload) => {
  if (!payload?.facultad) {
    throw new Error("Seleccione una facultad.");
  }

  const { data } = await api.post("admin/carreras/", payload);
  return data;
};

const updateCarrera = async (id, payload) => {
  if ("facultad" in payload && !payload?.facultad) {
    throw new Error("Seleccione una facultad.");
  }

  const { data } = await api.patch(`admin/carreras/${id}/`, payload);
  return data;
};

const deleteCarrera = async (id) => {
  const { data } = await api.delete(`admin/carreras/${id}/`);
  return data;
};

const loadFacultadesForCarreras = async () => {
  try {
    const { data } = await api.get("selects/facultades/");
    facultades.value = normalizeList(data);
  } catch {
    const { data } = await api.get("admin/facultades/");
    facultades.value = normalizeList(data);
  }
};

const carreraColumns = [
  { key: "nombre", label: "Nombre" },
  {
    key: "facultad_nombre",
    label: "Facultad",
    map: (row) => row?.facultad_nombre || row?.facultad?.nombre || "-",
  },
];

const carreraFields = computed(() => {
  const facOptions = (facultades.value || []).map((facultad) => ({
    value: facultad.id,
    label: `${facultad.nombre}${facultad.siglas ? ` (${facultad.siglas})` : ""}`,
  }));

  return [
    {
      key: "nombre",
      label: "Nombre de la carrera",
      required: true,
      placeholder: "Ej.: Tecnologías de la Información",
      helpTitle: "Nombre",
      help: "Use el nombre formal de la carrera.",
      maxLength: 140,
    },
    {
      key: "facultad",
      label: "Facultad",
      required: true,
      type: "select",
      placeholder: facOptions.length
        ? "Seleccione una facultad"
        : "Registre primero una facultad",
      options: facOptions,
      helpTitle: "Relación",
      help: "Cada carrera debe pertenecer a una facultad.",
    },
  ];
});

onMounted(async () => {
  await loadFacultadesForCarreras();
});
</script>

<style scoped src="./gestion-facultades-carreras.css"></style>