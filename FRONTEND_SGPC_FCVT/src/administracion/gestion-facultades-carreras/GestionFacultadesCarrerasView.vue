<template>
  <div class="sgpc-admin-page">
    <div class="catalogos-manager">
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header
        class="catalog-head adm-surface adm-hero"
        aria-labelledby="catalog-page-title"
      >
        <div class="catalog-head__main">
          <div class="catalog-head__copy">
            <span class="adm-kicker">
              Administración académica
            </span>

            <h1
              id="catalog-page-title"
              class="adm-title catalog-head__title"
            >
              Facultades y carreras
            </h1>

            <p class="adm-subtitle catalog-head__subtitle">
              Mantenga actualizada la estructura académica institucional
              y la relación entre las facultades y sus carreras.
            </p>
          </div>

          <div class="catalog-head__actions">
            <button
              class="catalog-back btn-soft"
              type="button"
              aria-label="Volver al panel administrativo"
              @click="goBack"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  fill="currentColor"
                  d="m10.6 5.3-6 6a1 1 0 0 0 0 1.4l6 6 1.4-1.4L7.7 13H20v-2H7.7L12 6.7l-1.4-1.4Z"
                />
              </svg>

              Volver al panel
            </button>
          </div>
        </div>

        <!-- ===================================================
             PESTAÑAS
        ==================================================== -->
        <div
          class="adm-tabs catalog-tabs"
          role="tablist"
          aria-label="Seleccionar catálogo académico"
        >
          <button
            v-for="tab in tabs"
            :id="`catalog-tab-${tab.key}`"
            :key="tab.key"
            class="adm-tab catalog-tabs__btn"
            :class="{ active: active === tab.key }"
            type="button"
            role="tab"
            :aria-selected="active === tab.key"
            aria-controls="catalog-tabpanel"
            :tabindex="active === tab.key ? 0 : -1"
            @click="setActive(tab.key)"
            @keydown.left.prevent="moveTab(tab.key, -1)"
            @keydown.right.prevent="moveTab(tab.key, 1)"
            @keydown.home.prevent="focusBoundaryTab('first')"
            @keydown.end.prevent="focusBoundaryTab('last')"
          >
            <span
              class="catalog-tabs__icon"
              aria-hidden="true"
            >
              <svg
                v-if="tab.key === 'facultades'"
                viewBox="0 0 24 24"
              >
                <path
                  fill="currentColor"
                  d="M3 10.5 12 4l9 6.5v1.8H3v-1.8ZM5 14h2v5H5v-5Zm4 0h2v5H9v-5Zm4 0h2v5h-2v-5Zm4 0h2v5h-2v-5ZM3 21v-2h18v2H3Z"
                />
              </svg>

              <svg
                v-else
                viewBox="0 0 24 24"
              >
                <path
                  fill="currentColor"
                  d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z"
                />
              </svg>
            </span>

            {{ tab.label }}
          </button>
        </div>
      </header>

      <!-- =====================================================
           CONTENIDO DEL CATÁLOGO
      ====================================================== -->
      <section
        id="catalog-tabpanel"
        class="catalog-content"
        role="tabpanel"
        :aria-labelledby="`catalog-tab-${active}`"
        tabindex="0"
      >
        <Transition
          name="catalog-switch"
          mode="out-in"
        >
          <CatalogCrud
            v-if="active === 'facultades'"
            key="facultades"
            title="Facultades"
            description="Cree, edite y mantenga actualizadas las facultades registradas en la institución."
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
            description="Administre las carreras y mantenga correctamente su relación con cada facultad."
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
import {
  computed,
  nextTick,
  onMounted,
  ref,
  watch,
} from "vue";
import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";
import CatalogCrud from "./FacultadesCarrerasCrud.vue";

const router = useRouter();
const route = useRoute();

const tabs = [
  {
    key: "facultades",
    label: "Facultades",
  },
  {
    key: "carreras",
    label: "Carreras",
  },
];

const VALID_TABS = tabs.map(
  (tab) => tab.key
);

const active = ref("facultades");
const facultades = ref([]);

/* ============================================================
   UTILIDADES
============================================================ */

const normalizeList = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
};

const syncTabFromRoute = () => {
  const tab = String(
    route.query?.tab || ""
  )
    .trim()
    .toLowerCase();

  active.value = VALID_TABS.includes(tab)
    ? tab
    : "facultades";
};

const focusTab = async (key) => {
  await nextTick();

  document
    .getElementById(`catalog-tab-${key}`)
    ?.focus();
};

/* ============================================================
   NAVEGACIÓN
============================================================ */

const goBack = () => {
  router.push("/admin/panel");
};

const setActive = (key) => {
  if (!VALID_TABS.includes(key)) {
    return;
  }

  active.value = key;

  router.replace({
    query: {
      ...route.query,
      tab: key,
    },
  });
};

const moveTab = (currentKey, offset) => {
  const currentIndex = tabs.findIndex(
    (tab) => tab.key === currentKey
  );

  if (currentIndex < 0) {
    return;
  }

  const nextIndex =
    (
      currentIndex +
      offset +
      tabs.length
    ) % tabs.length;

  const nextKey = tabs[nextIndex].key;

  setActive(nextKey);
  focusTab(nextKey);
};

const focusBoundaryTab = (position) => {
  const targetTab =
    position === "last"
      ? tabs[tabs.length - 1]
      : tabs[0];

  setActive(targetTab.key);
  focusTab(targetTab.key);
};

watch(
  () => route.query?.tab,
  syncTabFromRoute,
  {
    immediate: true,
  }
);

/* ============================================================
   FACULTADES
============================================================ */

const fetchFacultades = async () => {
  const { data } = await api.get(
    "admin/facultades/"
  );

  const list = normalizeList(data);

  facultades.value = list;

  return list;
};

const createFacultad = async (payload) => {
  const { data } = await api.post(
    "admin/facultades/",
    payload
  );

  await loadFacultadesForCarreras();

  return data;
};

const updateFacultad = async (
  id,
  payload
) => {
  const { data } = await api.patch(
    `admin/facultades/${id}/`,
    payload
  );

  await loadFacultadesForCarreras();

  return data;
};

const deleteFacultad = async (id) => {
  const { data } = await api.delete(
    `admin/facultades/${id}/`
  );

  await loadFacultadesForCarreras();

  return data;
};

const facultadColumns = [
  {
    key: "nombre",
    label: "Nombre",
  },
  {
    key: "siglas",
    label: "Siglas",
  },
];

const facultadFields = [
  {
    key: "nombre",
    label: "Nombre de la facultad",
    required: true,
    placeholder:
      "Ej.: Facultad de Ciencias de la Vida y Tecnologías",
    helpTitle: "Nombre",
    help:
      "Use el nombre institucional completo y consistente.",
    maxLength: 140,
  },
  {
    key: "siglas",
    label: "Siglas",
    required: true,
    placeholder: "Ej.: FCVT",
    helpTitle: "Siglas",
    help:
      "Utilice una abreviatura corta y reconocible.",
    maxLength: 20,
  },
];

/* ============================================================
   CARRERAS
============================================================ */

const fetchCarreras = async () => {
  const { data } = await api.get(
    "admin/carreras/"
  );

  return normalizeList(data);
};

const createCarrera = async (payload) => {
  if (!payload?.facultad) {
    throw new Error(
      "Seleccione una facultad."
    );
  }

  const { data } = await api.post(
    "admin/carreras/",
    payload
  );

  return data;
};

const updateCarrera = async (
  id,
  payload
) => {
  if (
    "facultad" in payload &&
    !payload?.facultad
  ) {
    throw new Error(
      "Seleccione una facultad."
    );
  }

  const { data } = await api.patch(
    `admin/carreras/${id}/`,
    payload
  );

  return data;
};

const deleteCarrera = async (id) => {
  const { data } = await api.delete(
    `admin/carreras/${id}/`
  );

  return data;
};

const loadFacultadesForCarreras =
  async () => {
    try {
      const { data } = await api.get(
        "selects/facultades/"
      );

      facultades.value =
        normalizeList(data);
    } catch {
      const { data } = await api.get(
        "admin/facultades/"
      );

      facultades.value =
        normalizeList(data);
    }
  };

const carreraColumns = [
  {
    key: "nombre",
    label: "Nombre",
  },
  {
    key: "facultad_nombre",
    label: "Facultad",
    map: (row) =>
      row?.facultad_nombre ||
      row?.facultad?.nombre ||
      "Sin asignar",
  },
];

const carreraFields = computed(() => {
  const facultadOptions = (
    facultades.value || []
  ).map((facultad) => ({
    value: facultad.id,
    label: `${facultad.nombre}${
      facultad.siglas
        ? ` (${facultad.siglas})`
        : ""
    }`,
  }));

  return [
    {
      key: "nombre",
      label: "Nombre de la carrera",
      required: true,
      placeholder:
        "Ej.: Tecnologías de la Información",
      helpTitle: "Nombre",
      help:
        "Use el nombre institucional formal de la carrera.",
      maxLength: 140,
    },
    {
      key: "facultad",
      label: "Facultad",
      required: true,
      type: "select",
      placeholder: facultadOptions.length
        ? "Seleccione una facultad"
        : "Registre primero una facultad",
      options: facultadOptions,
      helpTitle: "Relación académica",
      help:
        "Cada carrera debe estar asociada a una facultad.",
    },
  ];
});

/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(async () => {
  await loadFacultadesForCarreras();
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./gestion-facultades-carreras.css"></style>