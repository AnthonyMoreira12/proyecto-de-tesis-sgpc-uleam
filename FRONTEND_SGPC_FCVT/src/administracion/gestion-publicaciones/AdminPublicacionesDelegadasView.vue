<template>
  <main class="adm-del-page">
    <section class="adm-del-shell">
      <header class="adm-del-hero page-stage page-hero">
        <div class="adm-del-hero__copy">
          <p class="adm-del-kicker">Administración · Publicaciones</p>

          <h1 class="adm-del-title">
            Carga histórica por usuario
          </h1>

          <p class="adm-del-subtitle">
            Busque un usuario y registre publicaciones antiguas directamente en su perfil.
          </p>
        </div>
      </header>

      <section class="adm-del-main">
        <section class="adm-del-card adm-del-card--search">
          <div class="adm-del-card__head">
            <div>
              <h2 class="adm-del-card__title">Seleccionar usuario</h2>
            </div>
          </div>

          <div class="adm-del-card__body">
            <div class="adm-del-searchbar">
              <div class="adm-del-searchbar__field">
                <label
                  class="adm-del-searchbar__label"
                  for="adm-del-search-input"
                >
                  Buscar usuario
                </label>

                <div class="adm-del-searchbar__control">
                  <span class="adm-del-searchbar__icon" aria-hidden="true">
                    ⌕
                  </span>

                  <input
                    id="adm-del-search-input"
                    v-model.trim="search"
                    class="adm-del-input"
                    :class="{ 'is-loading': loadingUsers }"
                    type="search"
                    placeholder="Ej. María Pérez, 1312345678, correo@uleam.edu.ec..."
                    autocomplete="off"
                    @keydown.enter.prevent="fetchUsers()"
                    @search="handleNativeSearch"
                  />

                  <button
                    v-if="hasSearch"
                    class="adm-del-searchbar__clear"
                    type="button"
                    aria-label="Limpiar búsqueda"
                    title="Limpiar búsqueda"
                    @click="clearSearch"
                  >
                    ×
                  </button>
                </div>

                <small
                  v-if="searchFeedbackLabel"
                  class="adm-del-searchbar__hint"
                >
                  {{ searchFeedbackLabel }}
                </small>
              </div>
            </div>
          </div>

          <div class="adm-del-card__body adm-del-card__body--results">
            <div
              v-if="!hasSearch && !loadingUsers && !userError"
              class="adm-del-state"
            >
              <strong>Empiece a escribir para buscar</strong>
              <span>
                Puede buscar por nombre, apellido, correo o identificación.
              </span>
            </div>

            <div v-else-if="loadingUsers" class="adm-del-state">
              <strong>Buscando usuarios...</strong>
              <span>Espere un momento mientras se consultan los registros.</span>
            </div>

            <div
              v-else-if="userError"
              class="adm-del-state adm-del-state--error"
            >
              <strong>No se pudo cargar el listado.</strong>
              <span>{{ userError }}</span>
            </div>

            <div v-else-if="!filteredUsers.length" class="adm-del-state">
              <strong>Sin resultados</strong>
              <span>No hay coincidencias para “{{ search }}”.</span>
            </div>

            <div v-else class="adm-del-results-grid">
              <button
                v-for="user in filteredUsers"
                :key="user.id"
                type="button"
                class="adm-del-user-card"
                :class="{ 'is-active': selectedUser?.id === user.id }"
                :aria-pressed="selectedUser?.id === user.id ? 'true' : 'false'"
                @click="selectUser(user)"
              >
                <div class="adm-del-user-card__identity">
                  <div class="adm-del-user-card__avatar">
                    {{ initialsFromUser(user) }}
                  </div>

                  <div class="adm-del-user-card__identity-copy">
                    <div class="adm-del-user-card__top">
                      <strong>{{ fullUserName(user) }}</strong>

                      <span
                        v-if="userBadgeLabel(user)"
                        class="adm-del-badge"
                        :class="badgeScopeClass(user)"
                      >
                        {{ userBadgeLabel(user) }}
                      </span>
                    </div>

                    <p class="adm-del-user-card__meta">
                      {{ user.email || "Sin correo" }}
                    </p>

                    <p class="adm-del-user-card__submeta">
                      <span v-if="user.identificacion">
                        CI: {{ user.identificacion }}
                      </span>
                      <span v-else>Sin identificación</span>

                      <span v-if="user.facultad_nombre">
                        · {{ user.facultad_nombre }}
                      </span>

                      <span v-if="user.carrera_nombre">
                        · {{ user.carrera_nombre }}
                      </span>
                    </p>
                  </div>
                </div>

                <div class="adm-del-user-card__metrics">
                  <span class="adm-del-mini-pill">
                    {{ user.total_publicaciones || 0 }} publicaciones
                  </span>

                  <span
                    v-if="selectedUser?.id === user.id"
                    class="adm-del-mini-pill adm-del-mini-pill--selected"
                  >
                    Seleccionado
                  </span>
                </div>
              </button>
            </div>
          </div>
        </section>

        <section
          v-if="selectedUser"
          class="adm-del-card adm-del-card--target adm-del-card--highlight"
        >
          <div class="adm-del-card__head">
            <div>
              <h2 class="adm-del-card__title">Usuario seleccionado</h2>
            </div>
          </div>

          <div class="adm-del-card__body">
            <div class="adm-del-target-panel">
              <div class="adm-del-target-panel__identity">
                <div class="adm-del-target-avatar">
                  {{ selectedInitials }}
                </div>

                <div class="adm-del-target-copy">
                  <h3 class="adm-del-target-name">
                    {{ fullUserName(selectedUser) }}
                  </h3>

                  <p class="adm-del-target-email">
                    {{ selectedUser.email || "Sin correo registrado" }}
                  </p>

                  <div class="adm-del-target-pills">
                    <span
                      v-if="userBadgeLabel(selectedUser)"
                      class="adm-del-mini-pill"
                    >
                      {{ userBadgeLabel(selectedUser) }}
                    </span>

                    <span class="adm-del-mini-pill">
                      {{ selectedUser.total_publicaciones || 0 }} publicaciones
                    </span>
                  </div>
                </div>
              </div>

              <div class="adm-del-target-grid">
                <article class="adm-del-info-box">
                  <span class="adm-del-info-box__label">Facultad</span>
                  <strong class="adm-del-info-box__value">
                    {{ selectedUser.facultad_nombre || "Sin facultad" }}
                  </strong>
                </article>

                <article class="adm-del-info-box">
                  <span class="adm-del-info-box__label">Carrera</span>
                  <strong class="adm-del-info-box__value">
                    {{ selectedUser.carrera_nombre || "Sin carrera" }}
                  </strong>
                </article>

                <article class="adm-del-info-box">
                  <span class="adm-del-info-box__label">Autor vinculado</span>
                  <strong class="adm-del-info-box__value">
                    {{ selectedUser.autor_nombre || fullUserName(selectedUser) }}
                  </strong>
                </article>
              </div>
            </div>
          </div>
        </section>

        <section
          v-if="selectedUser"
          class="adm-del-card adm-del-card--actions"
        >
          <div class="adm-del-card__head">
            <div>
              <h2 class="adm-del-card__title">Registrar publicación</h2>
            </div>
          </div>

          <div class="adm-del-card__body">
            <div class="adm-del-action-grid">
              <button
                type="button"
                class="adm-del-action-card adm-del-action-card--aai"
                @click="goToForm('articuloAltoImpacto')"
              >
                <span class="adm-del-action-card__code">AAI</span>
                <strong>Artículo de alto impacto</strong>
                <span class="adm-del-action-card__hint">Abrir formulario</span>
              </button>

              <button
                type="button"
                class="adm-del-action-card adm-del-action-card--ar"
                @click="goToForm('articuloRegional')"
              >
                <span class="adm-del-action-card__code">AR</span>
                <strong>Artículo regional</strong>
                <span class="adm-del-action-card__hint">Abrir formulario</span>
              </button>

              <button
                type="button"
                class="adm-del-action-card adm-del-action-card--pon"
                @click="goToForm('ponencia')"
              >
                <span class="adm-del-action-card__code">PON</span>
                <strong>Ponencia</strong>
                <span class="adm-del-action-card__hint">Abrir formulario</span>
              </button>

              <button
                type="button"
                class="adm-del-action-card adm-del-action-card--lib"
                @click="goToForm('libro')"
              >
                <span class="adm-del-action-card__code">LIB</span>
                <strong>Libro</strong>
                <span class="adm-del-action-card__hint">Abrir formulario</span>
              </button>

              <button
                type="button"
                class="adm-del-action-card adm-del-action-card--cap"
                @click="goToForm('capitulo')"
              >
                <span class="adm-del-action-card__code">CAP</span>
                <strong>Capítulo de libro</strong>
                <span class="adm-del-action-card__hint">Abrir formulario</span>
              </button>
            </div>
          </div>
        </section>

        <section
          v-if="selectedUser"
          class="adm-del-card adm-del-card--history"
        >
          <div class="adm-del-card__head">
            <div>
              <h2 class="adm-del-card__title">Historial</h2>
            </div>

            <div class="adm-del-head-actions">
              <span class="adm-del-mini-pill">
                {{ userPublicaciones.length }} registros
              </span>
            </div>
          </div>

          <div class="adm-del-card__body">
            <div
              v-if="loadingPublicaciones && !userPublicaciones.length"
              class="adm-del-state"
            >
              <strong>Cargando historial...</strong>
              <span>Consultando publicaciones del usuario seleccionado.</span>
            </div>

            <div
              v-else-if="publicacionesError"
              class="adm-del-state adm-del-state--error"
            >
              <strong>No se pudo cargar el historial.</strong>
              <span>{{ publicacionesError }}</span>
            </div>

            <div v-else-if="!userPublicaciones.length" class="adm-del-state">
              <strong>Sin publicaciones registradas</strong>
              <span>Este usuario todavía no muestra publicaciones en esta vista.</span>
            </div>

            <div v-else class="adm-del-history-grid">
              <article
                v-for="item in userPublicaciones"
                :key="item.id"
                class="adm-del-history-card"
              >
                <div class="adm-del-history-card__top">
                  <span class="adm-del-badge adm-del-badge--soft">
                    {{
                      item.tipo_publicacion_final_label ||
                      item.tipo ||
                      "Publicación"
                    }}
                  </span>

                  <span class="adm-del-mini-pill">
                    {{ item.anio_publicacion || "s/a" }}
                  </span>
                </div>

                <strong class="adm-del-history-card__title">
                  {{ item.titulo || item.titulo_admin || "Sin título" }}
                </strong>

                <p class="adm-del-history-card__meta">
                  {{ item.autor_principal || item.autor || "Sin autor principal" }}
                </p>

                <p class="adm-del-history-card__submeta">
                  {{ item.carrera || item.carrera_nombre || "Sin carrera" }} ·
                  {{ item.facultad || item.facultad_nombre || "Sin facultad" }}
                </p>
              </article>
            </div>
          </div>
        </section>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { adminApi } from "../../scripts/api/adminApi";
import { listarAdminPublicaciones } from "../../scripts/api/publicacionesAdminApi";
import {
  buildAdminPublicacionLinks,
  buildAdminPublicacionTargetQuery,
} from "./admin-publicaciones-route-utils";

const router = useRouter();
const route = useRoute();

const search = ref("");
const loadingUsers = ref(false);
const userError = ref("");
const users = ref([]);
const selectedUser = ref(null);

const loadingPublicaciones = ref(false);
const publicacionesError = ref("");
const userPublicaciones = ref([]);

let searchTimer = null;

const hasSearch = computed(() => Boolean(String(search.value || "").trim()));

const filteredUsers = computed(() => {
  const q = normalizeText(search.value);

  if (!q) return [];

  return users.value.filter((user) => {
    const blob = [
      user?.nombres,
      user?.apellidos,
      user?.email,
      user?.identificacion,
      user?.autor_nombre,
      user?.facultad_nombre,
      user?.carrera_nombre,
    ]
      .join(" ")
      .toLowerCase();

    return normalizeText(blob).includes(q);
  });
});

const selectedInitials = computed(() => initialsFromUser(selectedUser.value));

const searchFeedbackLabel = computed(() => {
  if (!hasSearch.value) return "";
  if (loadingUsers.value) return "Buscando usuarios...";
  if (!filteredUsers.value.length) {
    return `No hay coincidencias para “${search.value}”.`;
  }

  return `${filteredUsers.value.length} resultado(s).`;
});

function normalizeText(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();
}

function resolveRouteUsuarioId() {
  const raw =
    route.params?.usuarioId ||
    route.query?.usuario_objetivo_id ||
    route.query?.usuario_id ||
    route.query?.usuarioId ||
    route.query?.user_id ||
    "";

  const parsed = Number(String(raw).trim());
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function fullUserName(user) {
  return (
    `${user?.nombres || ""} ${user?.apellidos || ""}`.trim() ||
    `Usuario #${user?.id || "—"}`
  );
}

function initialsFromUser(user) {
  if (!user) return "—";

  const primerNombre =
    String(user?.nombres || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)[0] || "";

  const primerApellido =
    String(user?.apellidos || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)[0] || "";

  const inicialNombre = primerNombre
    ? primerNombre.charAt(0).toUpperCase()
    : "";

  const inicialApellido = primerApellido
    ? primerApellido.charAt(0).toUpperCase()
    : "";

  const result = `${inicialNombre}${inicialApellido}`.trim();

  if (result) return result;
  if (inicialNombre) return inicialNombre;
  if (inicialApellido) return inicialApellido;

  return "US";
}

function userBadgeLabel(user) {
  if (user?.es_pendiente) return "Pendiente";
  if (user?.es_externo) return "Externo";
  if (user?.es_institucional) return "Institucional";
  return "";
}

function badgeScopeClass(user) {
  if (user?.es_pendiente) return "is-warning";
  if (user?.es_externo) return "is-soft";
  if (user?.es_institucional) return "is-primary";
  return "is-soft";
}

function mergeUserIntoList(user) {
  if (!user?.id) return;

  const index = users.value.findIndex(
    (item) => Number(item.id) === Number(user.id)
  );

  if (index >= 0) {
    users.value.splice(index, 1, user);
    return;
  }

  users.value.unshift(user);
}

async function fetchUserById(userId) {
  return adminApi.obtenerUsuario(userId);
}

async function fetchUsers() {
  const q = String(search.value || "").trim();

  if (!q) {
    users.value = [];
    userError.value = "";
    loadingUsers.value = false;
    return;
  }

  loadingUsers.value = true;
  userError.value = "";

  try {
    const data = await adminApi.usuarios(q, {
      scope: "activos",
    });

    users.value = Array.isArray(data) ? data : [];

    if (selectedUser.value?.id) {
      const refreshed = users.value.find(
        (item) => Number(item.id) === Number(selectedUser.value.id)
      );

      if (refreshed) {
        selectedUser.value = refreshed;
      }
    }
  } catch (error) {
    console.error(error);
    userError.value = "No fue posible consultar los usuarios en este momento.";
    users.value = [];
  } finally {
    loadingUsers.value = false;
  }
}

async function fetchUserPublicaciones() {
  if (!selectedUser.value?.id) {
    userPublicaciones.value = [];
    publicacionesError.value = "";
    return;
  }

  loadingPublicaciones.value = true;
  publicacionesError.value = "";

  try {
    const response = await listarAdminPublicaciones({
      usuario_objetivo_id: selectedUser.value.id,
      ordering: "fecha_desc",
    });

    userPublicaciones.value = Array.isArray(response?.results)
      ? response.results
      : [];
  } catch (error) {
    console.error(error);
    publicacionesError.value =
      "No fue posible cargar el historial del usuario seleccionado.";
    userPublicaciones.value = [];
  } finally {
    loadingPublicaciones.value = false;
  }
}

function buildTarget(user = selectedUser.value) {
  if (!user?.id) return null;

  return {
    usuarioId: user.id,
    autorId: user.autor_id || null,
    usuarioNombre: fullUserName(user),
    autorNombre: user.autor_nombre || "",
  };
}

async function syncRouteWithSelectedUser(user) {
  if (!user?.id) return;

  const usuarioId = String(user.id);
  const currentUsuarioId = String(resolveRouteUsuarioId() || "");
  const currentRouteName = String(route.name || "");
  const query = buildAdminPublicacionTargetQuery(buildTarget(user));

  if (
    currentRouteName === "AdminPublicacionesUsuario" &&
    currentUsuarioId === usuarioId
  ) {
    return;
  }

  await router.replace({
    name: "AdminPublicacionesUsuario",
    params: { usuarioId },
    query,
  });
}

async function selectUser(user, options = {}) {
  const { syncRoute = true } = options;

  if (!user?.id) return;

  selectedUser.value = user;
  mergeUserIntoList(user);

  if (syncRoute) {
    await syncRouteWithSelectedUser(user);
  }

  await fetchUserPublicaciones();
}

function goToForm(kind) {
  const target = buildTarget();
  if (!target) return;

  const links = buildAdminPublicacionLinks(target);
  const destination = links[kind];

  if (!destination) return;

  router.push(destination);
}

function clearSearch() {
  search.value = "";
  users.value = [];
  userError.value = "";
  loadingUsers.value = false;

  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
}

function handleNativeSearch() {
  if (!String(search.value || "").trim()) {
    clearSearch();
  }
}

async function hydrateSelectedUserFromRoute() {
  const usuarioId = resolveRouteUsuarioId();

  if (!usuarioId) return;

  if (Number(selectedUser.value?.id) === Number(usuarioId)) {
    return;
  }

  let user =
    users.value.find((item) => Number(item.id) === Number(usuarioId)) || null;

  if (!user) {
    try {
      user = await fetchUserById(usuarioId);

      if (user) {
        mergeUserIntoList(user);
      }
    } catch (error) {
      console.error(error);
    }
  }

  if (user) {
    await selectUser(user, { syncRoute: false });
  }
}

watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer);

  const q = String(search.value || "").trim();

  if (!q) {
    users.value = [];
    userError.value = "";
    loadingUsers.value = false;
    searchTimer = null;
    return;
  }

  searchTimer = setTimeout(() => {
    fetchUsers();
  }, 350);
});

watch(
  () => route.fullPath,
  async () => {
    await hydrateSelectedUserFromRoute();
  }
);

onMounted(async () => {
  await hydrateSelectedUserFromRoute();
});

onBeforeUnmount(() => {
  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
});
</script>

<style src="./admin-publicaciones-delegadas.css"></style>