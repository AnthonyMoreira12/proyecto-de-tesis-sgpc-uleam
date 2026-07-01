<template>
  <div class="sgpc-admin-page admin-container">
    <div class="users-admin">
      <header
        class="users-admin__head adm-surface"
        aria-label="Gestión de usuarios"
      >
        <div class="users-admin__head-main">
          <div class="users-admin__copy">
            <span class="adm-kicker">Usuarios</span>

            <h1 class="users-admin__title">Gestión de usuarios</h1>

            <p class="users-admin__subtitle">
              Administre cuentas externas, revise usuarios institucionales y controle el acceso
              al sistema desde una vista directa.
            </p>
          </div>

          <div class="users-admin__head-actions">
            <button
              class="users-btn users-btn--ghost"
              type="button"
              @click="refrescarVista"
              :disabled="loading"
            >
              {{ loading ? "Actualizando..." : "Refrescar" }}
            </button>

            <button
              class="users-btn users-btn--primary"
              type="button"
              @click="openCreateExterno"
              :disabled="loading"
            >
              Nuevo usuario externo
            </button>
          </div>
        </div>

        <div
          class="users-tabs"
          role="tablist"
          aria-label="Filtros de usuarios"
        >
          <button
            v-for="t in tabs"
            :key="t.key"
            class="users-tab"
            :class="{ active: activeTab === t.key }"
            type="button"
            role="tab"
            :aria-selected="activeTab === t.key ? 'true' : 'false'"
            @click="setTab(t.key)"
            :disabled="loading"
          >
            <span>{{ t.label }}</span>

            <span class="users-tab__count">
              {{ tabCount(t.key) }}
            </span>
          </button>
        </div>
      </header>

      <section
        class="users-admin__toolbar adm-surface"
        role="region"
        aria-label="Búsqueda de usuarios"
      >
        <div class="users-admin__search">
          <span class="users-admin__search-icon" aria-hidden="true">
            ⌕
          </span>

          <input
            v-model="busqueda"
            class="users-admin__search-input"
            placeholder="Buscar por nombre, correo, identificación, facultad, carrera o publicación..."
            @keyup.enter="cargarUsuarios"
            :disabled="loading"
            type="search"
            autocomplete="off"
          />

          <button
            v-if="busquedaTrim"
            class="users-admin__search-clear"
            type="button"
            @click="clearSearch"
            :disabled="loading"
            aria-label="Limpiar búsqueda"
            title="Limpiar búsqueda"
          >
            ×
          </button>
        </div>

        <div class="users-admin__toolbar-actions">
          <button
            class="users-btn users-btn--primary"
            type="button"
            @click="cargarUsuarios"
            :disabled="loading"
          >
            {{ loading ? "Buscando..." : "Buscar" }}
          </button>

          <button
            class="users-btn users-btn--ghost"
            type="button"
            @click="clearSearchAndReload"
            :disabled="loading || !busquedaTrim"
          >
            Limpiar
          </button>
        </div>
      </section>

      <div v-if="errorCarga" class="users-alert users-alert--error">
        {{ errorCarga }}
      </div>

      <section class="users-admin__tablecard adm-surface">
        <div class="users-admin__sectionhead">
          <div>
            <h2 class="users-admin__section-title">Listado</h2>
            <p class="users-admin__section-sub">
              {{ tableSubtitle }}
            </p>
          </div>

          <span class="users-admin__badge">
            {{ filteredUsuarios.length }} visible(s)
          </span>
        </div>

        <div
          v-if="!filteredUsuarios.length && !loading"
          class="users-admin__empty"
        >
          <p class="users-admin__empty-title">Sin resultados</p>

          <p class="users-admin__empty-text">
            {{
              busquedaTrim
                ? `No se encontraron usuarios para “${busquedaTrim}”.`
                : "No hay usuarios para mostrar con el filtro actual."
            }}
          </p>

          <div class="users-admin__empty-actions">
            <button
              v-if="busquedaTrim"
              class="users-btn users-btn--ghost"
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

        <div v-else class="users-admin__table-wrap">
          <table class="users-admin__table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo</th>
                <th>Identificación</th>
                <th>Tipo</th>
                <th>Facultad</th>
                <th>Carrera</th>
                <th>Estado</th>
                <th class="users-admin__th-actions">Acciones</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="u in filteredUsuarios" :key="u.id">
                <td class="users-admin__cell-user">
                  <div class="users-user">
                    <strong class="users-user__name">
                      {{ fullName(u) }}
                    </strong>

                    <div class="users-user__meta">
                      <span
                        class="users-pill users-pill--mini"
                        :class="{ 'users-pill--muted': !u.tiene_autor }"
                      >
                        {{ u.tiene_autor ? "Autor vinculado" : "Sin autor" }}
                      </span>

                      <span
                        v-if="u.es_admin || u.is_staff || u.is_superuser"
                        class="users-pill users-pill--mini users-pill--admin"
                      >
                        Admin
                      </span>

                      <span class="users-pill users-pill--mini">
                        {{ u.total_publicaciones || 0 }} pub.
                      </span>
                    </div>
                  </div>
                </td>

                <td class="users-admin__cell-muted">
                  {{ u.email || "-" }}
                </td>

                <td class="users-admin__cell-muted">
                  {{ u.identificacion || "-" }}
                </td>

                <td>
                  <span class="users-pill">
                    {{ tipoLabelHuman(u) }}
                  </span>
                </td>

                <td class="users-admin__cell-muted">
                  {{ u.facultad_nombre || "-" }}
                </td>

                <td class="users-admin__cell-muted">
                  {{ u.carrera_nombre || "-" }}
                </td>

                <td>
                  <span
                    v-if="isPendiente(u)"
                    class="users-pill users-pill--pending"
                  >
                    Pendiente
                  </span>

                  <span
                    v-else
                    class="users-pill"
                    :class="u.is_active ? 'users-pill--ok' : 'users-pill--off'"
                  >
                    {{ u.is_active ? "Activo" : "Inactivo" }}
                  </span>
                </td>

                <td class="users-admin__td-actions">
                  <div class="users-actions" @click.stop>
                    <button
                      class="users-btn users-btn--ghost users-btn--sm"
                      type="button"
                      @click="openDetalle(u)"
                      :disabled="loading"
                    >
                      Detalle
                    </button>

                    <button
                      class="users-btn users-btn--ghost users-btn--sm"
                      type="button"
                      @click="openEdit(u)"
                      :disabled="loading"
                    >
                      Editar
                    </button>

                    <div class="users-more">
                      <button
                        class="users-btn users-btn--ghost users-btn--sm"
                        type="button"
                        @click="toggleActionsMenu(u)"
                        :disabled="loading"
                        :aria-expanded="isActionsMenuOpen(u) ? 'true' : 'false'"
                        aria-haspopup="menu"
                      >
                        Más
                      </button>

                      <div
                        v-if="isActionsMenuOpen(u)"
                        class="users-more__menu"
                        role="menu"
                      >
                        <button
                          v-if="isPendiente(u)"
                          class="users-more__item users-more__item--primary"
                          type="button"
                          role="menuitem"
                          @click="openActivateFromMenu(u)"
                        >
                          Activar cuenta
                        </button>

                        <button
                          v-else
                          class="users-more__item"
                          :class="u.is_active ? 'users-more__item--danger' : 'users-more__item--success'"
                          type="button"
                          role="menuitem"
                          @click="toggleActivoFromMenu(u)"
                        >
                          {{ u.is_active ? "Desactivar cuenta" : "Activar cuenta" }}
                        </button>

                        <button
                          class="users-more__item users-more__item--danger"
                          type="button"
                          role="menuitem"
                          @click="eliminarFromMenu(u)"
                        >
                          Eliminar usuario
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>

              <tr v-if="loading && !filteredUsuarios.length">
                <td colspan="8" class="users-admin__empty-row">
                  Cargando usuarios...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

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

      <NoticeDialog :modelValue="notice" @close="closeNotice" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { adminApi } from "../../scripts/api/adminApi";
import { useNotice } from "../../scripts/composables/useNotice";

import UsuarioModal from "./UsuarioModal.vue";
import ActivarUsuarioModal from "./ActivarUsuarioModal.vue";
import DetalleAutorUsuarioModal from "./DetalleAutorUsuarioModal.vue";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";

const router = useRouter();
const route = useRoute();

const { notice, openNotice, closeNotice } = useNotice();

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

const tabs = [
  { key: "todos", label: "Todos" },
  { key: "pendientes", label: "Pendientes" },
  { key: "activos", label: "Activos" },
  { key: "institucionales", label: "Institucionales" },
  { key: "externos", label: "Externos" },
];

const busquedaTrim = computed(() => String(busqueda.value || "").trim());

const tableSubtitle = computed(() => {
  const current = tabLabel(activeTab.value);

  if (busquedaTrim.value) {
    return `${current}. Búsqueda aplicada: “${busquedaTrim.value}”.`;
  }

  return `Gestión general de cuentas. Filtro actual: ${current}.`;
});

const deferNotice = (payload) => {
  window.setTimeout(() => {
    openNotice(payload);
  }, 0);
};

const normalize = (value) =>
  String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();

const fullName = (u) => {
  const nombres = String(u?.nombres || "").trim();
  const apellidos = String(u?.apellidos || "").trim();
  return `${nombres} ${apellidos}`.trim() || "Usuario";
};

const isExterno = (u) =>
  String(u?.auth_source || "").toLowerCase() === "local" &&
  String(u?.rol || "").toLowerCase() === "autor_externo";

const isInstitucional = (u) =>
  String(u?.auth_source || "").toLowerCase() === "microsoft";

const isPendiente = (u) => isExterno(u) && !u?.is_active;

const tipoLabelHuman = (u) => {
  if (isInstitucional(u)) return "Institucional";
  if (isExterno(u)) return "Externo";
  return "Usuario";
};

const passesSearch = (u, q) => {
  if (!q) return true;

  const publicacionesTexto = (u?.publicaciones_relacionadas || [])
    .map((p) => `${p?.label || ""} ${p?.rol_label || ""} ${p?.tipo || ""}`)
    .join(" ");

  return [
    fullName(u),
    u?.email,
    u?.identificacion,
    u?.facultad_nombre,
    u?.carrera_nombre,
    u?.autor_nombre,
    publicacionesTexto,
  ].some((item) => normalize(item).includes(q));
};

const filteredUsuarios = computed(() => {
  const q = normalize(busquedaTrim.value);
  const list = (usuarios.value || []).filter((u) => passesSearch(u, q));

  switch (activeTab.value) {
    case "pendientes":
      return list.filter((u) => isPendiente(u));
    case "activos":
      return list.filter((u) => !!u?.is_active);
    case "institucionales":
      return list.filter((u) => isInstitucional(u));
    case "externos":
      return list.filter((u) => isExterno(u));
    default:
      return list;
  }
});

const tabLabel = (key) => tabs.find((item) => item.key === key)?.label || "Todos";

const tabCount = (key) => {
  const list = usuarios.value || [];

  switch (key) {
    case "pendientes":
      return list.filter((u) => isPendiente(u)).length;
    case "activos":
      return list.filter((u) => !!u?.is_active).length;
    case "institucionales":
      return list.filter((u) => isInstitucional(u)).length;
    case "externos":
      return list.filter((u) => isExterno(u)).length;
    default:
      return list.length;
  }
};

const setTab = (key) => {
  if (!tabs.some((item) => item.key === key)) return;

  activeTab.value = key;
  actionMenuId.value = null;

  router.replace({
    query: {
      ...route.query,
      tab: key,
    },
  });
};

const cargarUsuarios = async () => {
  loading.value = true;
  errorCarga.value = "";
  actionMenuId.value = null;

  try {
    const data = await adminApi.usuarios(busquedaTrim.value);
    usuarios.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Error cargando usuarios:", error);
    errorCarga.value = "No se pudo cargar la lista de usuarios. Intente nuevamente.";
  } finally {
    loading.value = false;
  }
};

const refrescarVista = async () => {
  await cargarUsuarios();
};

const clearSearch = () => {
  busqueda.value = "";
};

const clearSearchAndReload = async () => {
  busqueda.value = "";
  await cargarUsuarios();
};

const openCreateExterno = () => {
  actionMenuId.value = null;
  modal.open = true;
  modal.mode = "create";
  modal.usuario = null;
};

const openEdit = (u) => {
  actionMenuId.value = null;
  modal.open = true;
  modal.mode = "edit";
  modal.usuario = u;
};

const closeModal = () => {
  modal.open = false;
  modal.usuario = null;
};

const openActivate = (u) => {
  actionMenuId.value = null;
  activateModal.open = true;
  activateModal.usuario = u;
};

const closeActivateModal = () => {
  activateModal.open = false;
  activateModal.usuario = null;
};

const openDetalle = (u) => {
  actionMenuId.value = null;
  detailModal.open = true;
  detailModal.usuario = u;
};

const closeDetailModal = () => {
  detailModal.open = false;
  detailModal.usuario = null;
};

const handleUsuarioDone = async (payload) => {
  closeModal();
  await cargarUsuarios();

  openNotice({
    title: payload?.title || "Cambios guardados",
    message: payload?.message || "La información del usuario se actualizó correctamente.",
  });
};

const handleActivated = async (payload) => {
  closeActivateModal();
  await cargarUsuarios();

  openNotice({
    title: payload?.title || "Cuenta activada",
    message: payload?.message || "Listo. El usuario ya puede iniciar sesión.",
  });
};

const isActionsMenuOpen = (u) => {
  return actionMenuId.value === String(u?.id);
};

const toggleActionsMenu = (u) => {
  const id = String(u?.id || "");
  actionMenuId.value = actionMenuId.value === id ? null : id;
};

const openActivateFromMenu = (u) => {
  actionMenuId.value = null;
  openActivate(u);
};

const toggleActivoFromMenu = async (u) => {
  actionMenuId.value = null;
  await toggleActivo(u);
};

const eliminarFromMenu = async (u) => {
  actionMenuId.value = null;
  await eliminar(u);
};

const eliminar = async (u) => {
  openNotice({
    title: "Confirmar eliminación",
    message:
      "¿Desea eliminar este usuario? Si no tiene publicaciones, también se eliminará su autor vinculado.",
    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, eliminar",
    onConfirm: async () => {
      try {
        await adminApi.eliminarUsuario(u.id);
        await cargarUsuarios();

        deferNotice({
          title: "Eliminado",
          message: "Usuario eliminado correctamente.",
        });
      } catch (error) {
        const data = error?.response?.data;

        deferNotice({
          title: "No se pudo eliminar",
          message: data?.detail || "No se pudo eliminar el usuario. Intente nuevamente.",
        });
      }
    },
  });
};

const toggleActivo = async (u) => {
  const msg = u.is_active
    ? "¿Desea desactivar este usuario? No podrá iniciar sesión."
    : "¿Desea activar este usuario? Podrá iniciar sesión.";

  openNotice({
    title: u.is_active ? "Confirmar desactivación" : "Confirmar activación",
    message: msg,
    confirm: true,
    cancelText: "Cancelar",
    confirmText: u.is_active ? "Sí, desactivar" : "Sí, activar",
    onConfirm: async () => {
      try {
        const data = await adminApi.toggleActivo(u.id);
        u.is_active = !!data?.is_active;

        deferNotice({
          title: "Actualizado",
          message: `Usuario ${u.is_active ? "activado" : "desactivado"} correctamente.`,
        });
      } catch (error) {
        const data = error?.response?.data;

        deferNotice({
          title: "No se pudo actualizar",
          message:
            data?.detail || "No se pudo cambiar el estado del usuario. Intente nuevamente.",
        });
      }
    },
  });
};

const closeActionMenuOnDocumentClick = () => {
  actionMenuId.value = null;
};

onMounted(async () => {
  const qtab = String(route.query?.tab || "");

  if (tabs.some((item) => item.key === qtab)) {
    activeTab.value = qtab;
  } else {
    activeTab.value = "activos";

    router.replace({
      query: {
        ...route.query,
        tab: "activos",
      },
    });
  }

  document.addEventListener("click", closeActionMenuOnDocumentClick);

  await cargarUsuarios();
});

onBeforeUnmount(() => {
  document.removeEventListener("click", closeActionMenuOnDocumentClick);
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-usuarios.css"></style>