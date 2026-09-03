<template>
  <div class="sgpc-admin-page">
    <div class="users-admin">
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header
        class="users-admin__head"
        aria-labelledby="users-admin-title"
      >
        <div class="users-admin__head-main">
          <div class="users-admin__copy">
            <h1
              id="users-admin-title"
              class="users-admin__title"
            >
              Usuarios
            </h1>
          </div>

          <div class="users-admin__head-actions">
            <button
              class="users-btn users-btn--secondary"
              type="button"
              :disabled="refreshingAll || actionProcessing"
              @click="refrescarVista"
            >
              <span aria-hidden="true">↻</span>

              {{
                refreshingAll
                  ? "Actualizando…"
                  : "Actualizar"
              }}
            </button>

            <button
              class="users-btn users-btn--primary"
              type="button"
              :disabled="loading || actionProcessing"
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
                tab.key === "solicitudes"
                  ? tabCount(tab.key) === 1
                    ? "solicitud"
                    : "solicitudes"
                  : tabCount(tab.key) === 1
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
        class="users-admin__toolbar"
        role="search"
        :aria-label="
          activeTab === 'solicitudes'
            ? 'Buscar solicitudes'
            : 'Buscar usuarios'
        "
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
            :disabled="loading || loadingSolicitudes"
            :placeholder="
              activeTab === 'solicitudes'
                ? 'Buscar por usuario, correo o motivo'
                : 'Buscar usuarios'
            "
            @keyup.enter="handleSearch"
          />

          <button
            v-if="busquedaTrim"
            class="users-admin__search-clear"
            type="button"
            :disabled="loading || loadingSolicitudes"
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
          :disabled="loading || loadingSolicitudes"
          @click="handleSearch"
        >
          {{
            loading || loadingSolicitudes
              ? "Cargando…"
              : "Buscar"
          }}
        </button>
      </section>

      <AdminActionFeedback
        v-if="actionMessage"
        class="users-admin__action-feedback"
        :status="actionStatus"
        :message="actionMessage"
      />

      <!-- =====================================================
           ERROR
      ====================================================== -->
      <div
        v-if="errorCarga && activeTab !== 'solicitudes'"
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

      <div
        v-if="
          activeTab === 'solicitudes' &&
          errorSolicitudes
        "
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
            No se pudieron cargar las solicitudes
          </strong>
          <p>{{ errorSolicitudes }}</p>
        </div>
      </div>

      <!-- =====================================================
           LISTADO
      ====================================================== -->
      <section
        id="users-list-panel"
        class="users-admin__tablecard"
        role="tabpanel"
        :aria-labelledby="
          `users-tab-${activeTab}`
        "
        :aria-busy="currentLoading"
      >
        <div class="users-admin__sectionhead">
          <div class="users-admin__sectioncopy">
            <h2 class="users-admin__section-title">
              {{ sectionTitle }}
            </h2>
          </div>

          <span
            class="users-admin__badge"
            aria-live="polite"
            aria-atomic="true"
          >
            {{ resultCount }}
            {{ resultCountLabel }}
          </span>
        </div>

        <!-- ACTUALIZACIÓN SIN VACIAR RESULTADOS -->
        <AdminInlineLoader
          v-if="currentRefreshing"
          class="users-admin__inline-loader"
          :message="
            activeTab === 'solicitudes'
              ? 'Actualizando solicitudes…'
              : 'Actualizando usuarios…'
          "
        />

        <!-- CARGA INICIAL -->
        <AdminLoadingState
          v-if="currentInitialLoading"
          class="users-admin__loading-state"
          :message="
            activeTab === 'solicitudes'
              ? 'Cargando solicitudes de edición…'
              : 'Cargando usuarios…'
          "
          :description="
            activeTab === 'solicitudes'
              ? 'Consultando las solicitudes pendientes.'
              : 'Consultando las cuentas registradas.'
          "
          :skeleton-rows="5"
        />

        <!-- ESTADO VACÍO -->
        <div
          v-else-if="!resultCount && !currentError"
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
            {{
              activeTab === "solicitudes"
                ? busquedaTrim
                  ? "Sin coincidencias"
                  : "Sin solicitudes pendientes"
                : "Sin usuarios"
            }}
          </h3>

          <p
            class="users-admin__empty-text"
          >
            {{
              activeTab === "solicitudes"
                ? busquedaTrim
                  ? "No hay solicitudes pendientes que coincidan con la búsqueda."
                  : "No hay solicitudes de extensión del plazo de edición por revisar."
                : busquedaTrim
                  ? "Pruebe con otra búsqueda."
                  : "No hay usuarios para esta clasificación."
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
              v-if="activeTab !== 'solicitudes'"
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
          v-else-if="activeTab !== 'solicitudes'"
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
                  Tipo
                </th>

                <th scope="col">
                  Vinculación
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
                <td class="users-admin__cell-user" data-label="Usuario">
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

                      <span
                        v-if="hasPendingExtensionRequest(usuario)"
                        class="
                          users-pill
                          users-pill--mini
                          users-pill--extension
                        "
                      >
                        {{ formatRequestedHours(usuario) }}
                      </span>
                    </div>
                  </div>
                </td>

                <!-- CORREO -->
                <td
                  class="users-admin__cell-muted users-admin__cell-email"
                  data-label="Correo"
                >
                  {{
                    usuario.email ||
                    "No registrado"
                  }}
                </td>

                <!-- TIPO -->
                <td data-label="Tipo">
                  <span class="users-pill">
                    {{ tipoLabelHuman(usuario) }}
                  </span>
                </td>

                <!-- VINCULACIÓN -->
                <td
                  class="users-admin__cell-muted users-admin__cell-affiliation"
                  data-label="Vinculación"
                >
                  <div class="users-affiliation">
                    <strong>{{ carreraLabel(usuario) }}</strong>
                    <span>{{ facultadLabel(usuario) }}</span>
                    <small>{{ sedeLabel(usuario) }}</small>
                  </div>
                </td>

                <!-- ESTADO -->
                <td data-label="Estado">
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
                <td class="users-admin__td-actions" data-label="Acciones">
                  <div
                    class="users-actions"
                    @click.stop
                  >
                    <button
                      v-if="hasPendingExtensionRequest(usuario)"
                      class="
                        users-btn
                        users-btn--request
                        users-btn--sm
                      "
                      type="button"
                      :disabled="loading || loadingSolicitudes || actionProcessing"
                      :aria-label="
                        `Revisar solicitud de edición de ${fullName(usuario)}`
                      "
                      @click="openExtensionRequestForUser(usuario)"
                    >
                      Revisar solicitud
                    </button>

                    <button
                      class="users-btn users-btn--secondary users-btn--sm"
                      type="button"
                      :disabled="loading || actionProcessing"
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
                      :disabled="loading || actionProcessing"
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
                        :disabled="loading || actionProcessing"
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
        <!-- ===================================================
             COLA DE SOLICITUDES DE EDICIÓN
        ==================================================== -->
        <div
          v-else
          class="users-admin__requests-wrap"
        >
          <table class="users-admin__requests-table">
            <caption class="users-sr-only">
              Solicitudes pendientes para ampliar el plazo de edición del perfil
            </caption>

            <thead>
              <tr>
                <th scope="col">Usuario</th>
                <th scope="col">Solicitud</th>
                <th scope="col">Fecha</th>
                <th scope="col">Motivo</th>
                <th
                  scope="col"
                  class="users-admin__th-actions"
                >
                  Acción
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="solicitud in filteredSolicitudes"
                :key="solicitud.id"
              >
                <td data-label="Usuario">
                  <div class="users-request-user">
                    <strong class="users-request-user__name">
                      {{ solicitudUserName(solicitud) }}
                    </strong>
                    <span class="users-request-user__email">
                      {{ solicitudUserEmail(solicitud) }}
                    </span>
                  </div>
                </td>

                <td data-label="Solicitud">
                  <span class="users-request-hours">
                    {{ formatRequestHours(solicitud) }}
                  </span>
                </td>

                <td
                  class="users-admin__cell-muted"
                  data-label="Fecha"
                >
                  {{ formatRequestDate(solicitud?.solicitada_at) }}
                </td>

                <td
                  class="users-request-reason"
                  data-label="Motivo"
                >
                  <span :title="solicitud?.motivo || ''">
                    {{ truncateRequestReason(solicitud?.motivo) }}
                  </span>
                </td>

                <td
                  class="users-admin__td-actions"
                  data-label="Acción"
                >
                  <button
                    class="users-btn users-btn--request users-btn--sm"
                    type="button"
                    :disabled="loadingSolicitudes || actionProcessing"
                    :aria-label="
                      `Revisar solicitud de ${solicitudUserName(solicitud)}`
                    "
                    @click="openExtensionRequest(solicitud)"
                  >
                    Revisar solicitud
                  </button>
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
        mode="create"
        @close="closeModal"
        @done="handleUsuarioDone"
      />

      <ActivarUsuarioModal
        v-if="activateModal.open"
        :usuario="activateModal.usuario"
        @close="closeActivateModal"
        @done="handleActivated"
      />

      <SolicitudEdicionPerfilModal
        v-if="extensionModal.open"
        :solicitud="extensionModal.solicitud"
        @close="closeExtensionRequest"
        @resolved="handleExtensionResolved"
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
  listarSolicitudesExtensionPerfil,
  obtenerSolicitudExtensionPerfil,
} from "../../scripts/api/profileExtensionApi";
import {
  getAccountTypeLabel,
  isAdminUser,
  isExternalUser,
  isInstitutionalUser,
} from "../../scripts/utils/auth";

import { useNotice } from "../../scripts/composables/useNotice";

import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import { useActionState } from "../_shared/composables/useActionState";
import ActivarUsuarioModal from "./ActivarUsuarioModal.vue";
import SolicitudEdicionPerfilModal from "./SolicitudEdicionPerfilModal.vue";
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
const solicitudesExtension = ref([]);
const solicitudesExtensionCount = ref(0);
const loadingSolicitudes = ref(false);
const errorSolicitudes = ref("");

const {
  status: actionStatus,
  message: actionMessage,
  processing: actionProcessing,
  start: startAction,
  success: successAction,
  fail: failAction,
  reset: resetAction,
} = useActionState();

let actionFeedbackTimer = null;

const modal = reactive({
  open: false,
});


const activateModal = reactive({
  open: false,
  usuario: null,
});

const extensionModal = reactive({
  open: false,
  solicitud: null,
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
    key: "solicitudes",
    label: "Solicitudes de edición",
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


const refreshingAll = computed(() =>
  loading.value || loadingSolicitudes.value
);

const currentLoading = computed(() =>
  activeTab.value === "solicitudes"
    ? loadingSolicitudes.value
    : loading.value
);

const currentHasData = computed(() =>
  activeTab.value === "solicitudes"
    ? solicitudesExtension.value.length > 0
    : usuarios.value.length > 0
);

const currentInitialLoading = computed(() =>
  currentLoading.value && !currentHasData.value
);

const currentRefreshing = computed(() =>
  currentLoading.value && currentHasData.value
);

const currentError = computed(() =>
  activeTab.value === "solicitudes"
    ? errorSolicitudes.value
    : errorCarga.value
);

const scheduleActionFeedbackReset = () => {
  if (actionFeedbackTimer) {
    window.clearTimeout(actionFeedbackTimer);
  }

  actionFeedbackTimer = window.setTimeout(() => {
    resetAction();
    actionFeedbackTimer = null;
  }, 3600);
};


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


const normalizeExtensionRequestsResponse = (data) => {
  const results = Array.isArray(data)
    ? data
    : Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data?.data)
        ? data.data
        : [];

  const rawCount = Number(
    data?.count ?? results.length
  );

  return {
    results,
    count:
      Number.isFinite(rawCount) && rawCount >= 0
        ? rawCount
        : results.length,
  };
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


const sedeLabel = (usuario) => {
  if (!isInstitucional(usuario)) {
    return "No aplica";
  }

  return (
    usuario?.sede_nombre ||
    (typeof usuario?.sede === "object"
      ? usuario.sede?.nombre
      : usuario?.sede) ||
    "Sin asignar"
  );
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



const solicitudesPendientes = computed(() => {
  return (solicitudesExtension.value || []).filter(
    (solicitud) =>
      String(solicitud?.estado || "pendiente")
        .trim()
        .toLowerCase() === "pendiente"
  );
});


const solicitudesPendientesPorUsuario = computed(() => {
  const map = new Map();

  for (const solicitud of solicitudesPendientes.value) {
    const userId = Number(solicitud?.usuario_id);

    if (
      !Number.isInteger(userId) ||
      userId < 1
    ) {
      continue;
    }

    const current = map.get(userId);

    if (!current) {
      map.set(userId, solicitud);
      continue;
    }

    const currentDate = new Date(
      current?.solicitada_at || 0
    ).getTime();
    const nextDate = new Date(
      solicitud?.solicitada_at || 0
    ).getTime();

    if (nextDate > currentDate) {
      map.set(userId, solicitud);
    }
  }

  return map;
});


const solicitudPendienteUsuario = (usuario) => {
  const userId = Number(usuario?.id);

  if (
    !Number.isInteger(userId) ||
    userId < 1
  ) {
    return null;
  }

  return (
    solicitudesPendientesPorUsuario.value.get(userId) ||
    null
  );
};


const hasPendingExtensionRequest = (usuario) => {
  return Boolean(
    solicitudPendienteUsuario(usuario)
  );
};


const formatRequestedHours = (usuario) => {
  const solicitud =
    solicitudPendienteUsuario(usuario);
  const horas = Number(
    solicitud?.horas_solicitadas
  );

  return Number.isFinite(horas) && horas > 0
    ? `${horas} h solicitadas`
    : "Edición solicitada";
};


const solicitudUserName = (solicitud) => {
  return (
    normalizeText(solicitud?.usuario_nombre) ||
    "Usuario"
  );
};


const solicitudUserEmail = (solicitud) => {
  return (
    normalizeText(solicitud?.usuario_email) ||
    "Correo no disponible"
  );
};


const formatRequestHours = (solicitud) => {
  const hours = Number(
    solicitud?.horas_solicitadas
  );

  return Number.isFinite(hours) && hours > 0
    ? `${hours} horas`
    : "Tiempo no disponible";
};


const formatRequestDate = (value) => {
  if (!value) {
    return "No disponible";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};


const truncateRequestReason = (value) => {
  const text = normalizeText(value);

  if (!text) {
    return "Sin motivo registrado";
  }

  return text.length > 92
    ? `${text.slice(0, 89)}…`
    : text;
};


const filteredSolicitudes = computed(() => {
  const list = solicitudesPendientes.value;
  const query = normalizeSearchText(
    busquedaTrim.value
  );

  if (!query) {
    return list;
  }

  return list.filter((solicitud) => {
    const searchable = normalizeSearchText([
      solicitud?.usuario_nombre,
      solicitud?.usuario_email,
      solicitud?.motivo,
      solicitud?.horas_solicitadas,
    ].filter(Boolean).join(" "));

    return searchable.includes(query);
  });
});


/* ============================================================
   FILTROS
============================================================ */

const filteredUsuarios = computed(() => {
  /*
   * La búsqueda textual se resuelve en el backend mediante
   * adminApi.usuarios(busquedaTrim).
   *
   * No repetimos esa búsqueda en el navegador porque el backend
   * también puede encontrar cuentas mediante datos del Autor,
   * incluidos sus identificadores académicos, aunque esos campos
   * no formen parte del payload compacto de cada usuario.
   *
   * En el frontend únicamente conservamos los filtros visuales
   * de las pestañas administrativas.
   */
  const visibleUsers = Array.isArray(
    usuarios.value
  )
    ? usuarios.value
    : [];

  switch (activeTab.value) {
    case "pendientes":
      return visibleUsers.filter(
        isPendiente
      );

    case "solicitudes":
      return [];

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


const sectionTitle = computed(() => {
  return activeTab.value === "solicitudes"
    ? "Solicitudes de edición"
    : "Resultados";
});


const resultCount = computed(() => {
  return activeTab.value === "solicitudes"
    ? filteredSolicitudes.value.length
    : filteredUsuarios.value.length;
});


const resultCountLabel = computed(() => {
  if (activeTab.value === "solicitudes") {
    return resultCount.value === 1
      ? "solicitud"
      : "solicitudes";
  }

  return resultCount.value === 1
    ? "usuario"
    : "usuarios";
});


const tabCount = (key) => {
  const list = usuarios.value || [];

  switch (key) {
    case "pendientes":
      return list.filter(
        isPendiente
      ).length;

    case "solicitudes":
      return solicitudesExtensionCount.value;

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


const cargarSolicitudesExtension = async () => {
  if (loadingSolicitudes.value) {
    return;
  }

  loadingSolicitudes.value = true;
  errorSolicitudes.value = "";

  try {
    const data =
      await listarSolicitudesExtensionPerfil({
        estado: "pendiente",
        limit: 100,
      });

    const normalized =
      normalizeExtensionRequestsResponse(data);

    solicitudesExtension.value =
      normalized.results;
    solicitudesExtensionCount.value =
      normalized.count;
  } catch (error) {
    console.error(
      "Error cargando solicitudes de edición de perfil:",
      error
    );

    const baseMessage =
      error?.response?.data?.detail ||
      "No se pudieron cargar las solicitudes de edición de perfil.";

    errorSolicitudes.value =
      solicitudesExtension.value.length
        ? `${baseMessage} Se mantiene la última información cargada.`
        : baseMessage;
  } finally {
    loadingSolicitudes.value = false;
  }
};


const retirarSolicitudResueltaLocal = (solicitudId) => {
  const id = positiveRouteId(
    solicitudId
  );

  if (!id) {
    return false;
  }

  const previousLength =
    solicitudesExtension.value.length;

  solicitudesExtension.value =
    solicitudesExtension.value.filter(
      (solicitud) =>
        Number(solicitud?.id) !== id
    );

  return (
    solicitudesExtension.value.length !==
    previousLength
  );
};


const actualizarUsuarioLocal = (
  usuarioId,
  patch = {}
) => {
  const id = positiveRouteId(usuarioId);

  if (!id) {
    return false;
  }

  const index =
    usuarios.value.findIndex(
      (item) =>
        Number(item?.id) === id
    );

  if (index < 0) {
    return false;
  }

  usuarios.value[index] = {
    ...usuarios.value[index],
    ...(patch && typeof patch === "object"
      ? patch
      : {}),
  };

  return true;
};


const retirarUsuarioLocal = (
  usuarioId
) => {
  const id = positiveRouteId(usuarioId);

  if (!id) {
    return false;
  }

  const previousLength =
    usuarios.value.length;

  usuarios.value =
    usuarios.value.filter(
      (item) =>
        Number(item?.id) !== id
    );

  return (
    usuarios.value.length !==
    previousLength
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

    const baseMessage =
      resolveLoadError(error);

    errorCarga.value =
      usuarios.value.length
        ? `${baseMessage} Se mantiene la última información cargada.`
        : baseMessage;
  } finally {
    loading.value = false;
  }
};


const refrescarVista = async () => {
  await Promise.all([
    cargarUsuarios(),
    cargarSolicitudesExtension(),
  ]);
};


const clearSearchAndReload = async () => {
  busqueda.value = "";

  if (activeTab.value !== "solicitudes") {
    await cargarUsuarios();
  }
};


const handleSearch = async () => {
  if (activeTab.value === "solicitudes") {
    return;
  }

  await cargarUsuarios();
};


/* ============================================================
   MODAL DE USUARIO
============================================================ */

const openCreateExterno = () => {
  actionMenuId.value = null;
  modal.open = true;
};


const openEdit = (usuario) => {
  actionMenuId.value = null;

  const id = positiveRouteId(
    usuario?.id
  );

  if (!id) {
    openNotice({
      title: "No se pudo abrir la edición",
      message:
        "El usuario seleccionado no tiene un identificador válido.",
    });
    return;
  }

  router.push({
    name: "AdminUsuarioEditar",
    params: {
      id,
    },
    query: {
      origen: "usuarios",
      tab: activeTab.value,
    },
  });
};


const openExtensionRequest = (solicitud) => {
  actionMenuId.value = null;

  const requestId = positiveRouteId(
    solicitud?.id
  );

  if (!requestId) {
    openNotice({
      title: "Solicitud no disponible",
      message:
        "No fue posible identificar la solicitud seleccionada.",
    });
    return;
  }

  extensionModal.solicitud = {
    ...solicitud,
  };
  extensionModal.open = true;
};


const openExtensionRequestForUser = (usuario) => {
  const solicitud =
    solicitudPendienteUsuario(usuario);

  if (!solicitud) {
    openNotice({
      title: "Sin solicitud pendiente",
      message:
        "Este usuario ya no tiene una solicitud de edición pendiente.",
    });
    return;
  }

  openExtensionRequest(solicitud);
};


const closeExtensionRequest = async () => {
  extensionModal.open = false;
  extensionModal.solicitud = null;

  const nextQuery = {
    ...route.query,
  };

  delete nextQuery.solicitud;
  delete nextQuery.usuario;
  delete nextQuery.accion;
  delete nextQuery.horas;

  if (JSON.stringify(nextQuery) !== JSON.stringify(route.query)) {
    await router.replace({
      name: "AdminUsuarios",
      query: nextQuery,
    });
  }
};


const handleExtensionResolved = async (payload) => {
  const solicitud =
    payload?.solicitud ||
    extensionModal.solicitud;
  const requestId = positiveRouteId(
    solicitud?.id
  );

  if (requestId) {
    retirarSolicitudResueltaLocal(requestId);
  }

  solicitudesExtensionCount.value = Math.max(
    0,
    Number(solicitudesExtensionCount.value || 0) -
      (requestId ? 1 : 0)
  );

  /*
    La solicitud ya fue retirada de la cola de forma local.
    Solo sincronizamos usuarios porque el permiso de edición
    del perfil sí puede haber cambiado con la resolución.
  */
  await cargarUsuarios();

  successAction(
    payload?.decision === "rechazar"
      ? "Solicitud de edición rechazada correctamente."
      : "Solicitud de edición aprobada correctamente."
  );
  scheduleActionFeedbackReset();
};


const closeModal = () => {
  modal.open = false;
};


const handleUsuarioDone = async (
  payload
) => {
  closeModal();

  await cargarUsuarios();

  openNotice({
    title:
      payload?.title ||
      "Usuario registrado",

    message:
      payload?.message ||
      "El usuario se registró correctamente.",
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

  const id = positiveRouteId(
    usuario?.id
  );

  if (!id) {
    openNotice({
      title: "No se pudo abrir el usuario",
      message:
        "El usuario seleccionado no tiene un identificador válido.",
    });
    return;
  }

  router.push({
    name: "AdminUsuarioDetalle",
    params: {
      id,
    },
    query: {
      origen: "usuarios",
      tab: activeTab.value,
    },
  });
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
      if (actionProcessing.value) {
        return;
      }

      startAction("Eliminando usuario…");

      try {
        await adminApi.eliminarUsuario(
          usuario.id
        );

        retirarUsuarioLocal(
          usuario.id
        );

        successAction("Usuario eliminado correctamente.");
        scheduleActionFeedbackReset();

        deferNotice({
          title:
            "Usuario eliminado",

          message:
            "La cuenta se eliminó correctamente.",
        });
      } catch (error) {
        const data =
          error?.response?.data;

        failAction(
          data?.detail ||
          "No se pudo eliminar el usuario."
        );
        scheduleActionFeedbackReset();

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
      if (actionProcessing.value) {
        return;
      }

      startAction(
        desactivar
          ? "Desactivando usuario…"
          : "Reactivando usuario…"
      );

      try {
        const data =
          await adminApi.toggleActivo(
            usuario.id
          );

        actualizarUsuarioLocal(
          usuario.id,
          data
        );

        successAction(
          data?.is_active
            ? "Usuario reactivado correctamente."
            : "Usuario desactivado correctamente."
        );
        scheduleActionFeedbackReset();

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

        failAction(
          data?.detail ||
          "No se pudo cambiar el estado del usuario."
        );
        scheduleActionFeedbackReset();

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
   APERTURA DIRECTA DESDE NOTIFICACIONES
============================================================ */

const positiveRouteId = (value) => {
  const id = Number(value);
  return Number.isInteger(id) && id > 0
    ? id
    : null;
};


const openProfileExtensionFromRoute = async () => {
  const requestId = positiveRouteId(
    route.query?.solicitud
  );
  const userId = positiveRouteId(
    route.query?.usuario
  );
  const action = normalizeText(
    route.query?.accion
  ).toLowerCase();

  if (!requestId && action !== "extension-perfil") {
    return false;
  }

  let solicitud = null;

  if (requestId) {
    solicitud = solicitudesPendientes.value.find(
      (item) => Number(item?.id) === requestId
    ) || null;

    if (!solicitud) {
      try {
        solicitud =
          await obtenerSolicitudExtensionPerfil(
            requestId
          );
      } catch (error) {
        openNotice({
          title: "Solicitud no disponible",
          message:
            error?.response?.data?.detail ||
            "No se pudo cargar la solicitud seleccionada.",
        });
        return false;
      }
    }
  } else if (userId) {
    solicitud = solicitudesPendientes.value.find(
      (item) => Number(item?.usuario_id) === userId
    ) || null;

    if (!solicitud) {
      try {
        const payload =
          await listarSolicitudesExtensionPerfil({
            estado: "pendiente",
            usuario_id: userId,
            limit: 1,
          });

        solicitud = Array.isArray(payload?.results)
          ? payload.results[0] || null
          : null;
      } catch (error) {
        openNotice({
          title: "Solicitud no disponible",
          message:
            error?.response?.data?.detail ||
            "No se pudo verificar la solicitud pendiente de este usuario.",
        });
        return false;
      }
    }
  }

  if (!solicitud) {
    openNotice({
      title: "Sin solicitud pendiente",
      message:
        "La solicitud ya no está pendiente o el usuario no tiene una solicitud por revisar.",
    });

    const nextQuery = {
      ...route.query,
      tab: "solicitudes",
    };

    delete nextQuery.solicitud;
    delete nextQuery.usuario;
    delete nextQuery.accion;
    delete nextQuery.horas;

    await router.replace({
      name: "AdminUsuarios",
      query: nextQuery,
    });

    return false;
  }

  if (
    normalizeText(solicitud?.estado).toLowerCase() !==
    "pendiente"
  ) {
    openNotice({
      title: "Solicitud ya resuelta",
      message:
        "Esta solicitud ya fue procesada y no pertenece a la cola pendiente.",
    });

    const nextQuery = {
      ...route.query,
      tab: "solicitudes",
    };

    delete nextQuery.solicitud;
    delete nextQuery.usuario;
    delete nextQuery.accion;
    delete nextQuery.horas;

    await router.replace({
      name: "AdminUsuarios",
      query: nextQuery,
    });

    return false;
  }

  activeTab.value = "solicitudes";
  openExtensionRequest(solicitud);
  return true;
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


watch(
  () => [
    route.query?.accion,
    route.query?.usuario,
    route.query?.solicitud,
  ],
  async ([action, usuarioId, solicitudId]) => {
    if (
      positiveRouteId(solicitudId) ||
      (
        String(action || "").toLowerCase() ===
          "extension-perfil" &&
        positiveRouteId(usuarioId)
      )
    ) {
      await openProfileExtensionFromRoute();
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

  await Promise.all([
    cargarUsuarios(),
    cargarSolicitudesExtension(),
  ]);

  await openProfileExtensionFromRoute();
});


onBeforeUnmount(() => {
  if (actionFeedbackTimer) {
    window.clearTimeout(actionFeedbackTimer);
    actionFeedbackTimer = null;
  }

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

<style
  scoped
  src="./admin-usuarios-stage4.css"
></style>
