<template>
  <div class="sgpc-admin-page">
    <div class="catalogos-manager">
      <!-- =====================================================
           NAVEGACIÓN DEL MÓDULO
      ====================================================== -->
      <header class="catalog-modulebar">
        <div class="catalog-modulebar__top">
          <button
            class="catalog-back"
            type="button"
            aria-label="Volver a Administración"
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

            Administración
          </button>

          <div class="catalog-modulebar__copy">
            <h1 class="catalog-modulebar__title">
              Estructura académica
            </h1>

            <p class="catalog-modulebar__subtitle">
              Administre facultades, carreras y sedes.
            </p>
          </div>
        </div>

        <nav
          class="catalog-tabs"
          role="tablist"
          aria-label="Secciones de estructura académica"
          @keydown="handleTabsKeydown"
        >
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="catalog-tabs__btn"
            :class="{ active: active === tab.key }"
            :id="`catalog-tab-${tab.key}`"
            type="button"
            role="tab"
            :aria-selected="active === tab.key"
            :aria-controls="`catalog-panel-${tab.key}`"
            :tabindex="active === tab.key ? 0 : -1"
            @click="setActive(tab.key)"
          >
            {{ tab.label }}
          </button>
        </nav>
      </header>

      <!-- =====================================================
           CONTENIDO DEL CATÁLOGO
      ====================================================== -->
      <section
        :id="`catalog-panel-${active}`"
        class="catalog-content"
        role="tabpanel"
        :aria-labelledby="`catalog-tab-${active}`"
      >
        <Transition
          name="catalog-switch"
          mode="out-in"
        >
          <CatalogCrud
            v-if="active === 'facultades'"
            key="facultades"
            title="Facultades"
            description="Gestione las facultades disponibles para la organización académica."
            create-label="Registrar facultad"
            create-title="Registrar facultad"
            embedded
            :fetchRows="fetchFacultades"
            :createRow="createFacultad"
            :updateRow="updateFacultad"
            :deleteRow="deleteFacultad"
            :columns="facultadColumns"
            :fields="facultadFields"
          />

          <CatalogCrud
            v-else-if="active === 'carreras'"
            key="carreras"
            title="Carreras"
            description="Gestione las carreras y su facultad de pertenencia."
            create-label="Registrar carrera"
            create-title="Registrar carrera"
            embedded
            :fetchRows="fetchCarreras"
            :createRow="createCarrera"
            :updateRow="updateCarrera"
            :deleteRow="deleteCarrera"
            :columns="carreraColumns"
            :fields="carreraFields"
          />

          <CatalogCrud
            v-else-if="active === 'sedes'"
            key="sedes"
            title="Sedes"
            description="Gestione las sedes habilitadas para usuarios, proyectos y publicaciones."
            create-label="Registrar sede"
            create-title="Registrar sede"
            embedded
            :fetchRows="fetchSedes"
            :createRow="createSede"
            :updateRow="updateSede"
            :deleteRow="deleteSede"
            :columns="sedeColumns"
            :fields="sedeFields"
          />

          <CatalogCrud
            v-else
            key="carreras-sedes"
            title="Carreras por sede"
            description="Defina en qué sedes está disponible cada carrera."
            create-label="Asignar carrera"
            create-title="Asignar carrera a sede"
            embedded
            :fetchRows="fetchCarrerasSedes"
            :createRow="createCarreraSede"
            :updateRow="updateCarreraSede"
            :deleteRow="deleteCarreraSede"
            :columns="carreraSedeColumns"
            :fields="carreraSedeFields"
          />
        </Transition>
      </section>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
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
    routeName: "AdminEstructuraFacultades",
  },
  {
    key: "carreras",
    label: "Carreras",
    routeName: "AdminEstructuraCarreras",
  },
  {
    key: "sedes",
    label: "Sedes",
    routeName: "AdminEstructuraSedes",
  },
  {
    key: "carreras-sedes",
    label: "Carreras por sede",
    routeName: "AdminEstructuraCarrerasSedes",
  },
];

const VALID_TABS = tabs.map(
  (tab) => tab.key
);

const active = ref("facultades");

const facultades = ref([]);
const sedes = ref([]);
const carrerasCatalogo = ref([]);

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
    route.meta?.structureTab ||
    route.query?.tab ||
    ""
  )
    .trim()
    .toLowerCase();

  active.value = VALID_TABS.includes(tab)
    ? tab
    : "facultades";
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

  const targetTab = tabs.find(
    (tab) => tab.key === key
  );

  if (!targetTab) {
    return;
  }

  active.value = key;

  if (route.name === targetTab.routeName) {
    return;
  }

  const query = {
    ...route.query,
  };

  delete query.tab;

  router.replace({
    name: targetTab.routeName,
    query,
  });
};

const handleTabsKeydown = (event) => {
  if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
    return;
  }

  const tablist = event.currentTarget;
  const current = event.target?.closest?.('[role="tab"]');

  if (!(tablist instanceof HTMLElement) || !(current instanceof HTMLElement)) {
    return;
  }

  const availableTabs = Array.from(
    tablist.querySelectorAll('[role="tab"]:not(:disabled)')
  );

  if (!availableTabs.length) return;

  const currentIndex = Math.max(0, availableTabs.indexOf(current));
  let targetIndex = currentIndex;

  if (event.key === "Home") {
    targetIndex = 0;
  } else if (event.key === "End") {
    targetIndex = availableTabs.length - 1;
  } else if (event.key === "ArrowRight") {
    targetIndex = (currentIndex + 1) % availableTabs.length;
  } else {
    targetIndex = (currentIndex - 1 + availableTabs.length) % availableTabs.length;
  }

  event.preventDefault();

  const target = availableTabs[targetIndex];
  target?.focus();
  target?.click();
};

watch(
  () => [
    route.name,
    route.meta?.structureTab,
    route.query?.tab,
  ],
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
    help:
      "Escriba el nombre oficial de la facultad.",
    maxLength: 140,
  },
  {
    key: "siglas",
    label: "Siglas",
    required: true,
    placeholder: "Ej.: FCVT",
    help:
      "Escriba las siglas oficiales de la facultad.",
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

  await loadCarrerasForSedeRelations();

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

  await loadCarrerasForSedeRelations();

  return data;
};

const deleteCarrera = async (id) => {
  const { data } = await api.delete(
    `admin/carreras/${id}/`
  );

  await loadCarrerasForSedeRelations();

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
      help:
        "Escriba el nombre oficial de la carrera.",
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
      help:
        "Seleccione la facultad a la que pertenece la carrera.",
    },
  ];
});

/* ============================================================
   SEDES
============================================================ */

const fetchSedes = async () => {
  const { data } = await api.get(
    "admin/sedes/"
  );

  const list = normalizeList(data);
  sedes.value = list;
  return list;
};

const buildSedeCode = (nombre) =>
  String(nombre || "")
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 50);

const createSede = async (payload) => {
  const { data } = await api.post(
    "admin/sedes/",
    {
      ...payload,
      codigo: buildSedeCode(payload?.nombre),
    }
  );

  await loadSedesForRelations();
  return data;
};

const updateSede = async (
  id,
  payload
) => {
  const { data } = await api.patch(
    `admin/sedes/${id}/`,
    payload
  );

  await loadSedesForRelations();
  return data;
};

const deleteSede = async (id) => {
  const { data } = await api.delete(
    `admin/sedes/${id}/`
  );

  await loadSedesForRelations();
  return data;
};

const sedeColumns = [
  {
    key: "nombre",
    label: "Sede",
  },
  {
    key: "ciudad",
    label: "Ciudad",
    map: (row) => row?.ciudad || "—",
  },
  {
    key: "activa",
    label: "Estado",
    map: (row) => row?.activa ? "Activa" : "Inactiva",
  },
];

const sedeFields = [
  {
    key: "nombre",
    label: "Nombre de la sede",
    required: true,
    placeholder: "Ej.: Matriz Manta",
    help: "Escriba el nombre oficial de la sede.",
    maxLength: 150,
  },
  {
    key: "ciudad",
    label: "Ciudad",
    required: false,
    placeholder: "Ej.: Manta",
    maxLength: 100,
  },
  {
    key: "descripcion",
    label: "Descripción (opcional)",
    required: false,
    placeholder: "Ej.: Campus principal de Manta",
  },
  {
    key: "activa",
    label: "Estado",
    required: true,
    type: "select",
    placeholder: "Seleccione el estado",
    options: [
      { value: true, label: "Activa" },
      { value: false, label: "Inactiva" },
    ],
    help: "Las sedes inactivas no estarán disponibles al registrar información.",
  },
];

/* ============================================================
   CARRERAS POR SEDE
============================================================ */

const loadSedesForRelations = async () => {
  try {
    const { data } = await api.get(
      "admin/sedes/"
    );

    sedes.value = normalizeList(data);
  } catch {
    sedes.value = [];
  }
};

const loadCarrerasForSedeRelations = async () => {
  try {
    const { data } = await api.get(
      "admin/carreras/"
    );

    carrerasCatalogo.value = normalizeList(data);
  } catch {
    carrerasCatalogo.value = [];
  }
};

const fetchCarrerasSedes = async () => {
  const { data } = await api.get(
    "admin/carreras-sedes/"
  );

  return normalizeList(data);
};

const createCarreraSede = async (payload) => {
  if (!payload?.sede || !payload?.carrera) {
    throw new Error(
      "Seleccione la sede y la carrera."
    );
  }

  const { data } = await api.post(
    "admin/carreras-sedes/",
    payload
  );

  return data;
};

const updateCarreraSede = async (
  id,
  payload
) => {
  const { data } = await api.patch(
    `admin/carreras-sedes/${id}/`,
    payload
  );

  return data;
};

const deleteCarreraSede = async (id) => {
  const { data } = await api.delete(
    `admin/carreras-sedes/${id}/`
  );

  return data;
};

const carreraSedeColumns = [
  {
    key: "sede_nombre",
    label: "Sede",
    map: (row) => row?.sede_nombre || "Sin sede",
  },
  {
    key: "carrera_nombre",
    label: "Carrera",
    map: (row) => row?.carrera_nombre || "Sin carrera",
  },
  {
    key: "facultad_nombre",
    label: "Facultad",
    map: (row) => row?.facultad_nombre || "—",
  },
  {
    key: "activa",
    label: "Estado",
    map: (row) => row?.activa ? "Activa" : "Inactiva",
  },
];

const carreraSedeFields = computed(() => {
  const siteOptions = (sedes.value || []).map(
    (sede) => ({
      value: sede.id,
      label: `${sede.nombre}${sede.activa ? "" : " · Inactiva"}`,
    })
  );

  const careerOptions = (
    carrerasCatalogo.value || []
  ).map((carrera) => ({
    value: carrera.id,
    label: `${carrera.nombre}${
      carrera.facultad_nombre
        ? ` · ${carrera.facultad_nombre}`
        : ""
    }`,
  }));

  return [
    {
      key: "sede",
      label: "Sede",
      required: true,
      type: "select",
      placeholder: siteOptions.length
        ? "Seleccione una sede"
        : "Registre primero una sede",
      options: siteOptions,
      help: "Seleccione la sede donde estará disponible la carrera.",
    },
    {
      key: "carrera",
      label: "Carrera",
      required: true,
      type: "select",
      placeholder: careerOptions.length
        ? "Seleccione una carrera"
        : "Registre primero una carrera",
      options: careerOptions,
      help: "Una carrera puede estar disponible en varias sedes.",
    },
    {
      key: "activa",
      label: "Estado",
      required: true,
      type: "select",
      placeholder: "Seleccione el estado",
      options: [
        { value: true, label: "Activa" },
        { value: false, label: "Inactiva" },
      ],
      help: "Si está inactiva, la carrera no podrá seleccionarse en esa sede.",
    },
  ];
});

/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(async () => {
  await Promise.all([
    loadFacultadesForCarreras(),
    loadSedesForRelations(),
    loadCarrerasForSedeRelations(),
  ]);
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./gestion-facultades-carreras.css"></style>