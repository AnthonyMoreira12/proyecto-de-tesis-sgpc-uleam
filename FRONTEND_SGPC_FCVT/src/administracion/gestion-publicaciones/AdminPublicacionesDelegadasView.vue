<template>
  <div class="sgpc-admin-page">
    <main class="adm-delegated">
      <header class="adm-delegated__header">
        <div>
          <h1>Registrar publicación para otra persona</h1>

          <p>
            Busque y seleccione a la persona para la que desea
            registrar una publicación.
          </p>
        </div>

        <button
          class="adm-delegated__review-link"
          type="button"
          @click="goToReview"
        >
          Ir a revisión
          <span aria-hidden="true">→</span>
        </button>
      </header>

      <nav
        class="adm-delegated__progress"
        aria-label="Pasos para registrar una publicación"
      >
        <ol>
          <li class="is-active" aria-current="step">
            <span class="adm-delegated__step-number">1</span>
            <span class="adm-delegated__step-copy">
              <strong>Seleccionar usuario</strong>
            </span>
          </li>
          <li>
            <span class="adm-delegated__step-number">2</span>
            <span class="adm-delegated__step-copy">
              <strong>Elegir tipo</strong>
            </span>
          </li>
          <li>
            <span class="adm-delegated__step-number">3</span>
            <span class="adm-delegated__step-copy">
              <strong>Completar datos</strong>
            </span>
          </li>
        </ol>
      </nav>

      <section
        class="adm-delegated__search-panel adm-delegated__surface"
        aria-labelledby="delegated-search-title"
      >
        <div class="adm-delegated__search-copy">
          <h2 id="delegated-search-title">
            Buscar usuario
          </h2>

          <p>
            Busque por nombre, correo, cédula u ORCID.
          </p>
        </div>

        <form
          class="adm-delegated__search"
          role="search"
          @submit.prevent="fetchUsers"
        >
          <span
            class="adm-delegated__search-icon"
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
            v-model="search"
            type="search"
            autocomplete="off"
            placeholder="Nombre, correo, cédula u ORCID"
            aria-label="Buscar usuario"
            @search="handleNativeSearch"
          />

          <button
            v-if="hasSearch"
            class="adm-delegated__clear"
            type="button"
            aria-label="Limpiar búsqueda"
            @click="clearSearch"
          >
            ×
          </button>

        </form>
      </section>

      <section
        class="adm-delegated__results adm-delegated__surface"
        :aria-busy="loadingUsers"
      >
        <header class="adm-delegated__results-head">
          <div>
            <h2>Usuarios encontrados</h2>

            <p v-if="hasSearch && users.length">
              {{ resultsLabel }}
            </p>


          </div>
        </header>

        <AdminInlineLoader
          v-if="loadingUsers && users.length"
          message="Actualizando resultados…"
          class="adm-delegated__inline-loader"
        />

        <div
          v-if="!hasSearch && !loadingUsers"
          class="adm-delegated__state"
        >
          <div>
            <strong>Busque un usuario</strong>

            <span>
              Escriba un nombre, correo, cédula u ORCID.
            </span>
          </div>
        </div>

        <div
          v-else-if="loadingUsers && !users.length"
          class="adm-delegated__state"
          role="status"
        >
          <span
            class="adm-delegated__spinner"
            aria-hidden="true"
          ></span>

          <div>
            <strong>Buscando usuarios</strong>
            <span>Buscando coincidencias…</span>
          </div>
        </div>

        <div
          v-else-if="userError && !users.length"
          class="adm-delegated__state adm-delegated__state--error"
          role="alert"
        >
          <div>
            <strong>No se pudo completar la búsqueda</strong>
            <span>{{ userError }}</span>
          </div>
        </div>

        <div
          v-else-if="!users.length"
          class="adm-delegated__state"
        >
          <div>
            <strong>No encontramos usuarios</strong>

            <span>
              No encontramos usuarios para “{{ searchTrim }}”.
            </span>
          </div>
        </div>

        <div
          v-if="userError && users.length"
          class="adm-delegated__refresh-error"
          role="status"
        >
          No pudimos actualizar los resultados. Se mantienen las últimas coincidencias disponibles.
        </div>

        <ul
          v-if="users.length"
          class="adm-delegated__user-list"
          aria-label="Usuarios encontrados"
        >
          <li
            v-for="user in users"
            :key="user.id"
          >
            <button
              type="button"
              class="adm-delegated__user"
              @click="selectUser(user)"
            >
              <span
                class="adm-delegated__avatar"
                aria-hidden="true"
              >
                {{ initialsFromUser(user) }}
              </span>

              <span class="adm-delegated__identity">
                <strong>{{ fullUserName(user) }}</strong>
                <span>{{ user.email || "Sin correo registrado" }}</span>
              </span>

              <span class="adm-delegated__academic">
                <strong>{{ userScopeLabel(user) }}</strong>

                <span>
                  {{ userAcademicLabel(user) }}
                </span>
              </span>

              <span class="adm-delegated__production">
                <strong>{{ publicationTotal(user) }}</strong>
                <span>
                  {{
                    publicationTotal(user) === 1
                      ? "publicación"
                      : "publicaciones"
                  }}
                </span>
              </span>

              <span class="adm-delegated__select">
                Seleccionar
                <span aria-hidden="true">→</span>
              </span>
            </button>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";

import {
  useRouter,
} from "vue-router";

import { adminApi } from "../../scripts/api/adminApi";

import AdminInlineLoader from
  "../_shared/components/feedback/AdminInlineLoader.vue";

import {
  buildAdminPublicacionLinks,
} from "./admin-publicaciones-route-utils";

const router = useRouter();

const search = ref("");
const users = ref([]);
const loadingUsers = ref(false);
const userError = ref("");

let searchTimer = null;
let usersRequestSerial = 0;

const searchTrim = computed(() =>
  String(search.value || "").trim()
);

const hasSearch = computed(() =>
  Boolean(searchTrim.value)
);

const normalizeRows = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
};

const fullUserName = (user) => {
  const name = [
    String(user?.nombres || "").trim(),
    String(user?.apellidos || "").trim(),
  ]
    .filter(Boolean)
    .join(" ");

  return (
    name ||
    user?.email ||
    "Usuario sin nombre"
  );
};

const initialsFromUser = (user) => {
  const names = [
    String(user?.nombres || "").trim(),
    String(user?.apellidos || "").trim(),
  ].filter(Boolean);

  const initials = names
    .map((value) =>
      value
        .split(/\s+/)
        .filter(Boolean)[0]
        ?.charAt(0)
    )
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return initials || "US";
};

const publicationTotal = (user) => {
  const total = Number(user?.total_publicaciones);

  return Number.isFinite(total) && total >= 0
    ? total
    : 0;
};

const userScopeLabel = (user) => {
  if (user?.es_institucional) {
    return "Institucional";
  }

  if (user?.es_externo) {
    return "Externo";
  }

  return "Usuario";
};

const userAcademicLabel = (user) => {
  if (!user?.es_institucional) {
    return "No aplica";
  }

  const sede =
    user?.sede_nombre ||
    (
      typeof user?.sede === "object"
        ? user.sede?.nombre
        : user?.sede
    ) ||
    "";

  const unidad =
    user?.carrera_nombre ||
    user?.facultad_nombre ||
    "";

  return (
    [sede, unidad]
      .filter(Boolean)
      .join(" · ") ||
    "Información académica no registrada"
  );
};

const resultsLabel = computed(() => {
  const total = users.value.length;

  return total === 1
    ? "1 usuario encontrado"
    : `${total} usuarios encontrados`;
});

const getFriendlyError = (
  error,
  fallback
) => {
  const status =
    Number(error?.response?.status || 0);

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para realizar esta acción.";
  }

  if (status === 429) {
    return "Se realizaron demasiadas solicitudes. Intente nuevamente en unos minutos.";
  }

  const candidate =
    error?.response?.data?.detail ||
    error?.response?.data?.error ||
    "";

  const text =
    typeof candidate === "string"
      ? candidate.trim()
      : "";

  const technical =
    /(backend|endpoint|serializer|queryset|jwt|token|sql|postgres|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|http\s*\d{3}|request|response)/i;

  return (
    text &&
    !technical.test(text)
      ? text
      : fallback
  );
};

const fetchUsers = async () => {
  const query = searchTrim.value;

  if (!query) {
    usersRequestSerial += 1;
    users.value = [];
    userError.value = "";
    loadingUsers.value = false;
    return;
  }

  const requestId =
    ++usersRequestSerial;

  loadingUsers.value = true;
  userError.value = "";

  try {
    const data =
      await adminApi.usuarios(
        query,
        {
          scope: "activos",
        }
      );

    if (
      requestId !==
      usersRequestSerial
    ) {
      return;
    }

    users.value =
      normalizeRows(data);
  } catch (error) {
    if (
      requestId !==
      usersRequestSerial
    ) {
      return;
    }

    console.error(
      "Error buscando usuarios:",
      error
    );

    userError.value =
      getFriendlyError(
        error,
        "No pudimos buscar usuarios en este momento. Intente nuevamente."
      );

    /*
      Si ya existían resultados, se conservan para evitar que una
      incidencia temporal vacíe la pantalla y haga perder contexto.
    */
  } finally {
    if (
      requestId ===
      usersRequestSerial
    ) {
      loadingUsers.value = false;
    }
  }
};

const buildTarget = (user) => ({
  usuarioId: user.id,
  autorId: user.autor_id || null,
  usuarioNombre: fullUserName(user),
  autorNombre: user.autor_nombre || "",
});

const selectUser = (user) => {
  if (!user?.id) return;

  const links =
    buildAdminPublicacionLinks(
      buildTarget(user)
    );

  router.push(links.panel);
};

const clearSearch = () => {
  usersRequestSerial += 1;

  search.value = "";
  users.value = [];
  userError.value = "";
  loadingUsers.value = false;

  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
};

const handleNativeSearch = () => {
  if (!searchTrim.value) {
    clearSearch();
  }
};

const goToReview = () => {
  router.push({
    name: "AdminRevisionPublicaciones",
  });
};

watch(
  search,
  () => {
    if (searchTimer) {
      clearTimeout(searchTimer);
    }

    if (!searchTrim.value) {
      usersRequestSerial += 1;
      users.value = [];
      userError.value = "";
      loadingUsers.value = false;
      searchTimer = null;
      return;
    }

    searchTimer =
      window.setTimeout(
        fetchUsers,
        350
      );
  }
);

onBeforeUnmount(() => {
  usersRequestSerial += 1;

  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-publicaciones-delegadas.css"></style>
<style scoped src="./admin-publicaciones-delegadas-stage5.css"></style>
  