<template>
  <div class="sgpc-admin-page">
    <div class="users-admin">
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header
        class="users-admin__head adm-surface adm-hero"
        aria-labelledby="users-admin-title"
      >
        <div class="users-admin__head-main">
          <div class="users-admin__copy">
            <span class="adm-kicker">
              Administración
            </span>

            <h1
              id="users-admin-title"
              class="users-admin__title"
            >
              Gestión de usuarios
            </h1>

            <p class="users-admin__subtitle">
              Administre cuentas externas, revise usuarios
              institucionales y controle el acceso al sistema
              desde una sola interfaz.
            </p>
          </div>

          <div class="users-admin__head-actions">
            <button
              class="users-btn users-btn--secondary"
              type="button"
              :disabled="loading"
              @click="refrescarVista"
            >
              <span aria-hidden="true">↻</span>

              {{
                loading
                  ? "Actualizando..."
                  : "Refrescar"
              }}
            </button>

            <button
              class="users-btn users-btn--primary"
              type="button"
              :disabled="loading"
              @click="openCreateExterno"
            >
              <span aria-hidden="true">＋</span>
              Nuevo usuario externo
            </button>
          </div>
        </div>

        <!-- ===================================================
             PESTAÑAS
        ==================================================== -->
        <div
          class="users-tabs"
          role="tablist"
          aria-label="Clasificación de usuarios"
        >
          <button
            v-for="tab in tabs"
            :id="`users-tab-${tab.key}`"
            :key="tab.key"
            class="users-tab"
            :class="{
              active: activeTab === tab.key,
            }"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.key"
            aria-controls="users-list-panel"
            :tabindex="
              activeTab === tab.key
                ? 0
                : -1
            "
            :disabled="loading"
            @click="setTab(tab.key)"
            @keydown.left.prevent="
              moveTabFocus(tab.key, -1)
            "
            @keydown.right.prevent="
              moveTabFocus(tab.key, 1)
            "
            @keydown.home.prevent="
              focusBoundaryTab('first')
            "
            @keydown.end.prevent="
              focusBoundaryTab('last')
            "
          >
            <span>{{ tab.label }}</span>

            <span
              class="users-tab__count"
              aria-hidden="true"
            >
              {{ tabCount(tab.key) }}
            </span>

            <span class="users-sr-only">
              {{ tabCount(tab.key) }}
              {{
                tabCount(tab.key) === 1
                  ? "usuario"
                  : "usuarios"
              }}
            </span>
          </button>
        </div>
      </header>

      <!-- =====================================================
           BÚSQUEDA
      ====================================================== -->
      <section
        class="users-admin__toolbar adm-surface"
        role="search"
        aria-label="Buscar usuarios"
      >
        <div class="users-admin__search">
          <label
            for="users-admin-search"
            class="users-sr-only"
          >
            Buscar usuarios
          </label>

          <span
            class="users-admin__search-icon"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="m20.7 19.3-4.2-4.2a7.5 7.5 0 1 0-1.4 1.4l4.2 4.2a1 1 0 0 0 1.4-1.4ZM5 10.5a5.5 5.5 0 1 1 11 0 5.5 5.5 0 0 1-11 0Z"
              />
            </svg>
          </span>

          <input
            id="users-admin-search"
            v-model="busqueda"
            class="users-admin__search-input"
            type="search"
            autocomplete="off"
            :disabled="loading"
            placeholder="Buscar por nombre, correo, cédula, Facultad, Carrera o publicación"
            @keyup.enter="cargarUsuarios"
          />

          <button
            v-if="busquedaTrim"
            class="users-admin__search-clear"
            type="button"
            :disabled="loading"
            aria-label="Limpiar búsqueda"
            title="Limpiar búsqueda"
            @click="clearSearchAndReload"
          >
            ×
          </button>
        </div>

        <button
          class="users-btn users-btn--primary users-admin__search-button"
          type="button"
          :disabled="loading"
          @click="cargarUsuarios"
        >
          {{
            loading
              ? "Buscando..."
              : "Buscar"
          }}
        </button>
      </section>

      <!-- =====================================================
           ERROR
      ====================================================== -->
      <div
        v-if="errorCarga"
        class="users-alert users-alert--error"
        role="alert"
        aria-live="assertive"
      >
        <span
          class="users-alert__icon"
          aria-hidden="true"
        >
          !
        </span>

        <div>
          <strong>
            No se pudo cargar la información
          </strong>

          <p>{{ errorCarga }}</p>
        </div>
      </div>

      <!-- =====================================================
           LISTADO
      ====================================================== -->
      <section
        id="users-list-panel"
        class="users-admin__tablecard adm-surface"
        role="tabpanel"
        :aria-labelledby="
          `users-tab-${activeTab}`
        "
        :aria-busy="loading"
      >
        <div class="users-admin__sectionhead">
          <div class="users-admin__sectioncopy">
            <h2 class="users-admin__section-title">
              Listado de usuarios
            </h2>

            <p class="users-admin__section-sub">
              {{ tableSubtitle }}
            </p>
          </div>

          <span
            class="users-admin__badge"
            aria-live="polite"
            aria-atomic="true"
          >
            {{ filteredUsuarios.length }}

            {{
              filteredUsuarios.length === 1
                ? "usuario visible"
                : "usuarios visibles"
            }}
          </span>
        </div>

        <!-- PROGRESO -->
        <div
          v-if="loading"
          class="users-admin__progress"
          role="status"
          aria-live="polite"
        >
          <span
            class="users-admin__spinner"
            aria-hidden="true"
          ></span>

          Actualizando listado de usuarios...
        </div>

        <!-- CARGA INICIAL -->
        <div
          v-if="
            loading &&
            !usuarios.length
          "
          class="users-admin__loading-state"
          aria-hidden="true"
        >
          <div
            v-for="index in 5"
            :key="index"
            class="users-skeleton-row"
          >
            <span
              class="users-skeleton users-skeleton--name"
            ></span>

            <span
              class="users-skeleton users-skeleton--email"
            ></span>

            <span
              class="users-skeleton users-skeleton--short"
            ></span>

            <span
              class="users-skeleton users-skeleton--status"
            ></span>
          </div>
        </div>

        <!-- ESTADO VACÍO -->
        <div
          v-else-if="!filteredUsuarios.length"
          class="users-admin__empty"
        >
          <div
            class="users-admin__empty-icon"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z"
              />
            </svg>
          </div>

          <h3 class="users-admin__empty-title">
            Sin usuarios para mostrar
          </h3>

          <p class="users-admin__empty-text">
            {{
              busquedaTrim
                ? `No se encontraron coincidencias para “${busquedaTrim}”.`
                : "No existen usuarios dentro de la clasificación seleccionada."
            }}
          </p>

          <div class="users-admin__empty-actions">
            <button
              v-if="busquedaTrim"
              class="users-btn users-btn--secondary"
              type="button"
              @click="clearSearchAndReload"
            >
              Limpiar búsqueda
            </button>

            <button
              class="users-btn users-btn--primary"
              type="button"
              @click="openCreateExterno"
            >
              Nuevo usuario externo
            </button>
          </div>
        </div>

        <!-- ===================================================
             TABLA
        ==================================================== -->
        <div
          v-else
          class="users-admin__table-wrap"
        >
          <table class="users-admin__table">
            <caption class="users-sr-only">
              Usuarios registrados en el Sistema de Gestión de
              Producción Científica de la ULEAM
            </caption>

            <thead>
              <tr>
                <th scope="col">
                  Usuario
                </th>

                <th scope="col">
                  Correo
                </th>

                <th scope="col">
                  Número de cédula
                </th>

                <th scope="col">
                  Tipo
                </th>

                <th scope="col">
                  Facultad
                </th>

                <th scope="col">
                  Carrera
                </th>

                <th scope="col">
                  Estado
                </th>

                <th
                  scope="col"
                  class="users-admin__th-actions"
                >
                  Acciones
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="usuario in filteredUsuarios"
                :key="usuario.id"
              >
                <!-- USUARIO -->
                <td class="users-admin__cell-user">
                  <div class="users-user">
                    <strong class="users-user__name">
                      {{ fullName(usuario) }}
                    </strong>

                    <div class="users-user__meta">
                      <span
                        class="users-pill users-pill--mini"
                        :class="{
                          'users-pill--muted':
                            !usuario.tiene_autor,
                        }"
                      >
                        {{
                          usuario.tiene_autor
                            ? "Autor vinculado"
                            : "Sin autor"
                        }}
                      </span>

                      <span
                        v-if="isAdministrator(usuario)"
                        class="users-pill users-pill--mini users-pill--admin"
                      >
                        Administrador
                      </span>

                      <span
                        class="users-pill users-pill--mini"
                      >
                        {{ totalPublicaciones(usuario) }}

                        {{
                          totalPublicaciones(usuario) === 1
                            ? "publicación"
                            : "publicaciones"
                        }}
                      </span>
                    </div>
                  </div>
                </td>

                <!-- CORREO -->
                <td
                  class="users-admin__cell-muted users-admin__cell-email"
                >
                  {{
                    usuario.email ||
                    "No registrado"
                  }}
                </td>

                <!-- CÉDULA -->
                <td class="users-admin__cell-muted">
                  {{
                    usuario.identificacion ||
                    "No registrada"
                  }}
                </td>

                <!-- TIPO -->
                <td>
                  <span class="users-pill">
                    {{ tipoLabelHuman(usuario) }}
                  </span>
                </td>

                <!-- FACULTAD -->
                <td class="users-admin__cell-muted">
                  {{ facultadLabel(usuario) }}
                </td>

                <!-- CARRERA -->
                <td class="users-admin__cell-muted">
                  {{ carreraLabel(usuario) }}
                </td>

                <!-- ESTADO -->
                <td>
                  <span
                    v-if="isPendiente(usuario)"
                    class="users-pill users-pill--pending"
                  >
                    Pendiente
                  </span>

                  <span
                    v-else
                    class="users-pill"
                    :class="
                      usuario.is_active
                        ? 'users-pill--ok'
                        : 'users-pill--off'
                    "
                  >
                    {{
                      usuario.is_active
                        ? "Activo"
                        : "Inactivo"
                    }}
                  </span>
                </td>

                <!-- ACCIONES -->
                <td class="users-admin__td-actions">
                  <div
                    class="users-actions"
                    @click.stop
                  >
                    <button
                      class="users-btn users-btn--secondary users-btn--sm"
                      type="button"
                      :disabled="loading"
                      :aria-label="
                        `Ver detalle de ${fullName(usuario)}`
                      "
                      @click="openDetalle(usuario)"
                    >
                      Detalle
                    </button>

                    <button
                      class="users-btn users-btn--secondary users-btn--sm"
                      type="button"
                      :disabled="loading"
                      :aria-label="
                        `Editar ${fullName(usuario)}`
                      "
                      @click="openEdit(usuario)"
                    >
                      Editar
                    </button>

                    <div class="users-more">
                      <button
                        :id="
                          `users-more-trigger-${usuario.id}`
                        "
                        class="users-btn users-btn--secondary users-btn--sm users-btn--more"
                        type="button"
                        :disabled="loading"
                        :aria-label="
                          `Más acciones para ${fullName(usuario)}`
                        "
                        :aria-expanded="
                          isActionsMenuOpen(usuario)
                        "
                        :aria-controls="
                          `users-more-menu-${usuario.id}`
                        "
                        aria-haspopup="menu"
                        @click="toggleActionsMenu(usuario)"
                      >
                        Más
                        <span aria-hidden="true">⌄</span>
                      </button>

                      <div
                        v-if="
                          isActionsMenuOpen(usuario)
                        "
                        :id="
                          `users-more-menu-${usuario.id}`
                        "
                        class="users-more__menu"
                        role="menu"
                        :aria-labelledby="
                          `users-more-trigger-${usuario.id}`
                        "
                        @keydown.esc.stop.prevent="
                          closeActionMenuAndFocus(usuario)
                        "
                      >
                        <!-- ACTIVAR CUENTA PENDIENTE -->
                        <button
                          v-if="isPendiente(usuario)"
                          class="users-more__item users-more__item--primary"
                          type="button"
                          role="menuitem"
                          @click="
                            openActivateFromMenu(usuario)
                          "
                        >
                          Activar cuenta
                        </button>

                        <!-- ACTIVAR O DESACTIVAR CUENTA EXISTENTE -->
                        <button
                          v-else
                          class="users-more__item"
                          :class="
                            usuario.is_active
                              ? 'users-more__item--danger'
                              : 'users-more__item--success'
                          "
                          type="button"
                          role="menuitem"
                          @click="
                            toggleActivoFromMenu(usuario)
                          "
                        >
                          {{
                            usuario.is_active
                              ? "Desactivar cuenta"
                              : "Reactivar cuenta"
                          }}
                        </button>

                        <div
                          class="users-more__separator"
                          role="separator"
                        ></div>

                        <button
                          class="users-more__item users-more__item--danger"
                          type="button"
                          role="menuitem"
                          @click="
                            eliminarFromMenu(usuario)
                          "
                        >
                          Eliminar usuario
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- =====================================================
           MODALES
      ====================================================== -->
      <UsuarioModal
        v-if="modal.open"
        :mode="modal.mode"
        :usuario="modal.usuario"
        @close="closeModal"
        @done="handleUsuarioDone"
      />

      <ActivarUsuarioModal
        v-if="activateModal.open"
        :usuario="activateModal.usuario"
        @close="closeActivateModal"
        @done="handleActivated"
      />

      <DetalleAutorUsuarioModal
        v-if="detailModal.open"
        :usuario="detailModal.usuario"
        @close="closeDetailModal"
      />

      <NoticeDialog
        :model-value="notice"
        @close="closeNotice"
      />
    </div>
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

import {
  useRoute,
  useRouter,
} from "vue-router";

import { adminApi } from "../../scripts/api/adminApi";

import {
  getAccountTypeLabel,
  isAdminUser,
  isExternalUser,
  isInstitutionalUser,
} from "../../scripts/utils/auth";

import { useNotice } from "../../scripts/composables/useNotice";

import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import ActivarUsuarioModal from "./ActivarUsuarioModal.vue";
import DetalleAutorUsuarioModal from "./DetalleAutorUsuarioModal.vue";
import UsuarioModal from "./UsuarioModal.vue";


const router = useRouter();
const route = useRoute();

const {
  notice,
  openNotice,
  closeNotice,
} = useNotice();


const usuarios = ref([]);
const busqueda = ref("");
const loading = ref(false);
const errorCarga = ref("");
const activeTab = ref("activos");
const actionMenuId = ref(null);


const modal = reactive({
  open: false,
  mode: "create",
  usuario: null,
});


const activateModal = reactive({
  open: false,
  usuario: null,
});


const detailModal = reactive({
  open: false,
  usuario: null,
});


const tabs = Object.freeze([
  {
    key: "todos",
    label: "Todos",
  },
  {
    key: "pendientes",
    label: "Pendientes",
  },
  {
    key: "activos",
    label: "Activos",
  },
  {
    key: "institucionales",
    label: "Institucionales",
  },
  {
    key: "externos",
    label: "Externos",
  },
]);


/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) => {
  return String(value ?? "")
    .trim();
};


const normalizeSearchText = (value) => {
  return normalizeText(value)
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "");
};


const busquedaTrim = computed(() => {
  return normalizeText(
    busqueda.value
  );
});


const normalizeUsersResponse = (data) => {
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


/* ============================================================
   CLASIFICACIÓN
============================================================ */

const isExterno = (usuario) => {
  return isExternalUser(usuario);
};


const isInstitucional = (usuario) => {
  return isInstitutionalUser(usuario);
};


const isAdministrator = (usuario) => {
  return isAdminUser(usuario);
};


const isPendiente = (usuario) => {
  /*
    La condición de pendiente depende también de que la cuenta
    todavía no posea una contraseña utilizable. Esa información
    solo debe determinarla el backend.
  */
  return usuario?.es_pendiente === true;
};


const tipoLabelHuman = (usuario) => {
  const label =
    getAccountTypeLabel(usuario);

  if (label === "Cuenta institucional") {
    return "Institucional";
  }

  if (label === "Cuenta externa") {
    return "Externo";
  }

  return "Sin clasificación";
};


const facultadLabel = (usuario) => {
  if (!isInstitucional(usuario)) {
    return "No aplica";
  }

  return (
    usuario?.facultad_nombre ||
    "Sin asignar"
  );
};


const carreraLabel = (usuario) => {
  if (!isInstitucional(usuario)) {
    return "No aplica";
  }

  return (
    usuario?.carrera_nombre ||
    "Sin asignar"
  );
};


/* ============================================================
   INFORMACIÓN DEL USUARIO
============================================================ */

const fullName = (usuario) => {
  const nombres = normalizeText(
    usuario?.nombres
  );

  const apellidos = normalizeText(
    usuario?.apellidos
  );

  return (
    `${nombres} ${apellidos}`.trim() ||
    "Usuario"
  );
};


const totalPublicaciones = (usuario) => {
  const total = Number(
    usuario?.total_publicaciones
  );

  if (
    Number.isFinite(total) &&
    total >= 0
  ) {
    return total;
  }

  if (
    Array.isArray(
      usuario?.publicaciones_relacionadas
    )
  ) {
    return (
      usuario.publicaciones_relacionadas.length
    );
  }

  return 0;
};


/* ============================================================
   BÚSQUEDA
============================================================ */

const publicationSearchText = (usuario) => {
  const publications =
    Array.isArray(
      usuario?.publicaciones_relacionadas
    )
      ? usuario.publicaciones_relacionadas
      : [];

  return publications
    .map((publication) => {
      return [
        publication?.label,
        publication?.titulo,
        publication?.rol_label,
        publication?.rol_autoria,
        publication?.tipo,
        publication?.tipo_codigo,
        publication?.numero,
        publication?.anio_publicacion,
      ]
        .map(normalizeText)
        .filter(Boolean)
        .join(" ");
    })
    .join(" ");
};


const passesSearch = (
  usuario,
  query
) => {
  if (!query) {
    return true;
  }

  const searchableValues = [
    fullName(usuario),
    usuario?.nombres,
    usuario?.apellidos,
    usuario?.email,
    usuario?.identificacion,
    usuario?.facultad_nombre,
    usuario?.carrera_nombre,
    usuario?.autor_nombre,
    publicationSearchText(usuario),
  ];

  return searchableValues.some(
    (value) => {
      return normalizeSearchText(
        value
      ).includes(query);
    }
  );
};


/* ============================================================
   FILTROS
============================================================ */

const filteredUsuarios = computed(() => {
  const query = normalizeSearchText(
    busquedaTrim.value
  );

  const visibleUsers = (
    usuarios.value || []
  ).filter((usuario) => {
    return passesSearch(
      usuario,
      query
    );
  });

  switch (activeTab.value) {
    case "pendientes":
      return visibleUsers.filter(
        isPendiente
      );

    case "activos":
      return visibleUsers.filter(
        (usuario) =>
          Boolean(usuario?.is_active)
      );

    case "institucionales":
      return visibleUsers.filter(
        isInstitucional
      );

    case "externos":
      return visibleUsers.filter(
        isExterno
      );

    default:
      return visibleUsers;
  }
});


const tabLabel = (key) => {
  return (
    tabs.find(
      (tab) => tab.key === key
    )?.label ||
    "Todos"
  );
};


const tableSubtitle = computed(() => {
  const currentTab =
    tabLabel(activeTab.value);

  if (busquedaTrim.value) {
    return (
      `${currentTab}. Búsqueda aplicada: ` +
      `“${busquedaTrim.value}”.`
    );
  }

  return (
    `Clasificación actual: ${currentTab}.`
  );
});


const tabCount = (key) => {
  const list = usuarios.value || [];

  switch (key) {
    case "pendientes":
      return list.filter(
        isPendiente
      ).length;

    case "activos":
      return list.filter(
        (usuario) =>
          Boolean(usuario?.is_active)
      ).length;

    case "institucionales":
      return list.filter(
        isInstitucional
      ).length;

    case "externos":
      return list.filter(
        isExterno
      ).length;

    default:
      return list.length;
  }
};


/* ============================================================
   PESTAÑAS
============================================================ */

const setTab = (key) => {
  if (
    !tabs.some(
      (tab) => tab.key === key
    )
  ) {
    return;
  }

  activeTab.value = key;
  actionMenuId.value = null;

  router.replace({
    query: {
      ...route.query,
      tab: key,
    },
  });
};


const focusTab = (key) => {
  window.requestAnimationFrame(() => {
    document
      .getElementById(
        `users-tab-${key}`
      )
      ?.focus();
  });
};


const moveTabFocus = (
  currentKey,
  offset
) => {
  const currentIndex =
    tabs.findIndex(
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

  const nextKey =
    tabs[nextIndex].key;

  setTab(nextKey);
  focusTab(nextKey);
};


const focusBoundaryTab = (
  position
) => {
  const targetTab =
    position === "last"
      ? tabs[tabs.length - 1]
      : tabs[0];

  setTab(targetTab.key);
  focusTab(targetTab.key);
};


/* ============================================================
   CARGA DE USUARIOS
============================================================ */

const resolveLoadError = (error) => {
  const data =
    error?.response?.data;

  if (
    typeof data?.detail === "string"
  ) {
    return data.detail;
  }

  if (
    Array.isArray(data?.detail) &&
    data.detail[0]
  ) {
    return String(
      data.detail[0]
    );
  }

  if (
    typeof data?.error === "string"
  ) {
    return data.error;
  }

  return (
    "No se pudo cargar la lista de usuarios. " +
    "Intente nuevamente."
  );
};


const cargarUsuarios = async () => {
  if (loading.value) {
    return;
  }

  loading.value = true;
  errorCarga.value = "";
  actionMenuId.value = null;

  try {
    const data =
      await adminApi.usuarios(
        busquedaTrim.value
      );

    usuarios.value =
      normalizeUsersResponse(data);
  } catch (error) {
    console.error(
      "Error cargando usuarios:",
      error
    );

    errorCarga.value =
      resolveLoadError(error);
  } finally {
    loading.value = false;
  }
};


const refrescarVista = async () => {
  await cargarUsuarios();
};


const clearSearchAndReload = async () => {
  busqueda.value = "";

  await cargarUsuarios();
};


/* ============================================================
   MODAL DE USUARIO
============================================================ */

const openCreateExterno = () => {
  actionMenuId.value = null;

  modal.open = true;
  modal.mode = "create";
  modal.usuario = null;
};


const openEdit = (usuario) => {
  actionMenuId.value = null;

  modal.open = true;
  modal.mode = "edit";
  modal.usuario = usuario;
};


const closeModal = () => {
  modal.open = false;
  modal.usuario = null;
};


const handleUsuarioDone = async (
  payload
) => {
  closeModal();

  await cargarUsuarios();

  openNotice({
    title:
      payload?.title ||
      "Cambios guardados",

    message:
      payload?.message ||
      "La información del usuario se actualizó correctamente.",
  });
};


/* ============================================================
   MODAL DE ACTIVACIÓN
============================================================ */

const openActivate = (usuario) => {
  actionMenuId.value = null;

  if (!isPendiente(usuario)) {
    openNotice({
      title:
        "Cuenta no disponible para activación",

      message:
        "La activación con credenciales solo está disponible para cuentas externas pendientes.",
    });

    return;
  }

  activateModal.open = true;
  activateModal.usuario = usuario;
};


const closeActivateModal = () => {
  activateModal.open = false;
  activateModal.usuario = null;
};


const handleActivated = async (
  payload
) => {
  closeActivateModal();

  await cargarUsuarios();

  openNotice({
    title:
      payload?.title ||
      "Cuenta activada",

    message:
      payload?.message ||
      "El usuario ya puede iniciar sesión en el sistema.",
  });
};


/* ============================================================
   MODAL DE DETALLE
============================================================ */

const openDetalle = (usuario) => {
  actionMenuId.value = null;

  detailModal.open = true;
  detailModal.usuario = usuario;
};


const closeDetailModal = () => {
  detailModal.open = false;
  detailModal.usuario = null;
};


/* ============================================================
   MENÚ DE ACCIONES
============================================================ */

const isActionsMenuOpen = (
  usuario
) => {
  return (
    actionMenuId.value ===
    String(usuario?.id ?? "")
  );
};


const toggleActionsMenu = (
  usuario
) => {
  const id = String(
    usuario?.id ?? ""
  );

  if (!id) {
    return;
  }

  actionMenuId.value =
    actionMenuId.value === id
      ? null
      : id;
};


const closeActionMenuAndFocus = (
  usuario
) => {
  actionMenuId.value = null;

  window.requestAnimationFrame(() => {
    document
      .getElementById(
        `users-more-trigger-${usuario?.id}`
      )
      ?.focus();
  });
};


const openActivateFromMenu = (
  usuario
) => {
  actionMenuId.value = null;

  openActivate(usuario);
};


const toggleActivoFromMenu = async (
  usuario
) => {
  actionMenuId.value = null;

  await toggleActivo(usuario);
};


const eliminarFromMenu = async (
  usuario
) => {
  actionMenuId.value = null;

  await eliminar(usuario);
};


/* ============================================================
   ELIMINAR
============================================================ */

const deferNotice = (payload) => {
  window.setTimeout(() => {
    openNotice(payload);
  }, 0);
};


const eliminar = async (usuario) => {
  openNotice({
    title:
      "Confirmar eliminación",

    message:
      "¿Desea eliminar esta cuenta? Las publicaciones y demás registros científicos relacionados se conservarán de acuerdo con las reglas del sistema.",

    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, eliminar",

    onConfirm: async () => {
      try {
        await adminApi.eliminarUsuario(
          usuario.id
        );

        await cargarUsuarios();

        deferNotice({
          title:
            "Usuario eliminado",

          message:
            "La cuenta se eliminó correctamente.",
        });
      } catch (error) {
        const data =
          error?.response?.data;

        deferNotice({
          title:
            "No se pudo eliminar",

          message:
            data?.detail ||
            "No se pudo eliminar el usuario. Intente nuevamente.",
        });
      }
    },
  });
};


/* ============================================================
   ACTIVAR O DESACTIVAR
============================================================ */

const toggleActivo = async (
  usuario
) => {
  /*
    Las cuentas pendientes deben pasar por el modal que exige
    correo y contraseña.
  */
  if (isPendiente(usuario)) {
    openActivate(usuario);
    return;
  }

  const desactivar =
    Boolean(usuario?.is_active);

  openNotice({
    title:
      desactivar
        ? "Confirmar desactivación"
        : "Confirmar reactivación",

    message:
      desactivar
        ? "¿Desea desactivar este usuario? No podrá iniciar sesión."
        : "¿Desea reactivar este usuario? Podrá iniciar sesión con sus credenciales actuales.",

    confirm: true,
    cancelText: "Cancelar",

    confirmText:
      desactivar
        ? "Sí, desactivar"
        : "Sí, reactivar",

    onConfirm: async () => {
      try {
        const data =
          await adminApi.toggleActivo(
            usuario.id
          );

        await cargarUsuarios();

        deferNotice({
          title:
            "Estado actualizado",

          message:
            data?.is_active
              ? "El usuario fue reactivado correctamente."
              : "El usuario fue desactivado correctamente.",
        });
      } catch (error) {
        const data =
          error?.response?.data;

        deferNotice({
          title:
            "No se pudo actualizar",

          message:
            data?.detail ||
            "No se pudo cambiar el estado del usuario.",
        });
      }
    },
  });
};


/* ============================================================
   EVENTOS GLOBALES
============================================================ */

const closeActionMenuOnDocumentClick = () => {
  actionMenuId.value = null;
};


const closeActionMenuOnEscape = (
  event
) => {
  if (event.key === "Escape") {
    actionMenuId.value = null;
  }
};


/* ============================================================
   SINCRONIZACIÓN CON LA RUTA
============================================================ */

watch(
  () => route.query?.tab,
  (value) => {
    const key = String(
      value || ""
    );

    if (
      tabs.some(
        (tab) => tab.key === key
      )
    ) {
      activeTab.value = key;
    }
  }
);


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(async () => {
  const queryTab = String(
    route.query?.tab || ""
  );

  if (
    tabs.some(
      (tab) => tab.key === queryTab
    )
  ) {
    activeTab.value = queryTab;
  } else {
    activeTab.value = "activos";

    await router.replace({
      query: {
        ...route.query,
        tab: "activos",
      },
    });
  }

  document.addEventListener(
    "click",
    closeActionMenuOnDocumentClick
  );

  document.addEventListener(
    "keydown",
    closeActionMenuOnEscape
  );

  await cargarUsuarios();
});


onBeforeUnmount(() => {
  document.removeEventListener(
    "click",
    closeActionMenuOnDocumentClick
  );

  document.removeEventListener(
    "keydown",
    closeActionMenuOnEscape
  );
});
</script>

<style src="../styles/admin-shared.css"></style>

<style
  scoped
  src="./admin-usuarios.css"
></style>