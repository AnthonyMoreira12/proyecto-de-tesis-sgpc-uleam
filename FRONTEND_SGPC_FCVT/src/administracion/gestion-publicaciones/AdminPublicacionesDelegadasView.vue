<template>
  <div class="sgpc-admin-page">
    <main class="adm-del-page">
      <section class="adm-del-shell">
        <!-- ===================================================
             ENCABEZADO
        ==================================================== -->
        <header
          class="adm-del-hero adm-surface adm-hero"
          aria-labelledby="adm-del-page-title"
        >
          <div class="adm-del-hero__copy">
            <span class="adm-kicker">
              Administración · Publicaciones
            </span>

            <h1
              id="adm-del-page-title"
              class="adm-title adm-del-title"
            >
              Registro delegado
            </h1>

            <p class="adm-subtitle adm-del-subtitle">
              Seleccione un usuario y registre producción científica
              histórica directamente en su perfil institucional.
            </p>
          </div>

          <div class="adm-del-hero__summary" aria-label="Flujo de trabajo">
            <span class="adm-del-step">
              <strong>1</strong>
              Buscar usuario
            </span>

            <span class="adm-del-step">
              <strong>2</strong>
              Seleccionar cuenta
            </span>

            <span class="adm-del-step">
              <strong>3</strong>
              Registrar publicación
            </span>
          </div>
        </header>

        <!-- ===================================================
             BÚSQUEDA Y SELECCIÓN
        ==================================================== -->
        <section
          class="adm-del-card adm-del-card--search adm-surface"
          aria-labelledby="adm-del-search-title"
          :aria-busy="loadingUsers ? 'true' : 'false'"
        >
          <div class="adm-del-card__head">
            <div>
              <h2
                id="adm-del-search-title"
                class="adm-del-card__title"
              >
                Seleccionar usuario
              </h2>

              <p class="adm-del-card__subtitle">
                Busque cuentas activas por nombre, correo,
                identificación, unidad académica o identificador académico.
              </p>
            </div>

            <span
              v-if="hasSearch && !loadingUsers"
              class="adm-del-count"
              aria-live="polite"
              aria-atomic="true"
            >
              {{ searchResultLabel }}
            </span>
          </div>

          <div
            class="adm-del-searchbar"
            role="search"
            aria-label="Buscar usuario para registro delegado"
          >
            <label
              class="adm-del-searchbar__label"
              for="adm-del-search-input"
            >
              Buscar usuario
            </label>

            <div class="adm-del-searchbar__row">
              <div class="adm-del-searchbar__control">
                <span
                  class="adm-del-searchbar__icon"
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
                  id="adm-del-search-input"
                  v-model.trim="search"
                  class="adm-del-input"
                  type="search"
                  placeholder="Ej.: María Pérez, cédula, correo u ORCID"
                  autocomplete="off"
                  :disabled="loadingUsers"
                  :aria-describedby="
                    searchFeedbackLabel
                      ? 'adm-del-search-feedback'
                      : undefined
                  "
                  @keydown.enter.prevent="fetchUsers"
                  @search="handleNativeSearch"
                />

                <button
                  v-if="hasSearch"
                  class="adm-del-searchbar__clear"
                  type="button"
                  :disabled="loadingUsers"
                  aria-label="Limpiar búsqueda"
                  title="Limpiar búsqueda"
                  @click="clearSearch"
                >
                  <span aria-hidden="true">×</span>
                </button>
              </div>

              <button
                class="adm-del-button adm-del-button--primary"
                type="button"
                :disabled="loadingUsers || !hasSearch"
                @click="fetchUsers"
              >
                <span
                  v-if="loadingUsers"
                  class="adm-del-spinner"
                  aria-hidden="true"
                ></span>

                {{ loadingUsers ? "Buscando..." : "Buscar" }}
              </button>
            </div>

            <p
              v-if="searchFeedbackLabel"
              id="adm-del-search-feedback"
              class="adm-del-searchbar__hint"
              aria-live="polite"
            >
              {{ searchFeedbackLabel }}
            </p>
          </div>

          <!-- Estado inicial -->
          <div
            v-if="!hasSearch && !loadingUsers && !userError"
            class="adm-del-state"
          >
            <div class="adm-del-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z"
                />
              </svg>
            </div>

            <div>
              <strong>Busque una cuenta activa</strong>

              <span>
                Los resultados aparecerán mientras escribe.
              </span>
            </div>
          </div>

          <!-- Carga -->
          <div
            v-else-if="loadingUsers"
            class="adm-del-results-skeleton"
            role="status"
            aria-live="polite"
          >
            <span class="adm-del-sr-only">
              Buscando usuarios.
            </span>

            <div
              v-for="index in 4"
              :key="index"
              class="adm-del-user-skeleton"
              aria-hidden="true"
            >
              <span class="adm-del-skeleton adm-del-skeleton--avatar"></span>

              <span class="adm-del-user-skeleton__copy">
                <span class="adm-del-skeleton adm-del-skeleton--name"></span>
                <span class="adm-del-skeleton adm-del-skeleton--email"></span>
              </span>

              <span class="adm-del-skeleton adm-del-skeleton--pill"></span>
            </div>
          </div>

          <!-- Error -->
          <div
            v-else-if="userError"
            class="adm-del-state adm-del-state--error"
            role="alert"
            aria-live="assertive"
          >
            <div class="adm-del-state__icon" aria-hidden="true">
              !
            </div>

            <div>
              <strong>No se pudo cargar el listado</strong>
              <span>{{ userError }}</span>
            </div>
          </div>

          <!-- Sin resultados -->
          <div
            v-else-if="!filteredUsers.length"
            class="adm-del-state"
          >
            <div class="adm-del-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M4 4h16v16H4V4Zm2 2v12h12V6H6Zm2 3h8v2H8V9Zm0 4h5v2H8v-2Z"
                />
              </svg>
            </div>

            <div>
              <strong>Sin coincidencias</strong>

              <span>
                No se encontraron usuarios para “{{ search }}”.
              </span>
            </div>
          </div>

          <!-- Resultados -->
          <ul
            v-else
            class="adm-del-results-grid"
            aria-label="Usuarios encontrados"
          >
            <li
              v-for="user in filteredUsers"
              :key="user.id"
              class="adm-del-results-grid__item"
            >
              <button
                type="button"
                class="adm-del-user-card"
                :class="{
                  'is-active':
                    Number(selectedUser?.id) === Number(user.id),
                }"
                :aria-pressed="
                  Number(selectedUser?.id) === Number(user.id)
                    ? 'true'
                    : 'false'
                "
                :aria-label="`Seleccionar a ${fullUserName(user)}`"
                @click="selectUser(user)"
              >
                <span
                  v-if="userBadgeLabel(user)"
                  class="adm-del-badge adm-del-user-card__badge"
                  :class="badgeScopeClass(user)"
                >
                  {{ userBadgeLabel(user) }}
                </span>

                <div class="adm-del-user-card__identity">
                  <div class="adm-del-user-card__avatar">
                    <img
                      v-if="hasUsableAvatar(user)"
                      :src="resolveAvatarUrl(user)"
                      :alt="`Foto de perfil de ${fullUserName(user)}`"
                      loading="lazy"
                      decoding="async"
                      @error="markAvatarBroken(user)"
                    />

                    <span v-else aria-hidden="true">
                      {{ initialsFromUser(user) }}
                    </span>
                  </div>

                  <div class="adm-del-user-card__identity-copy">
                    <strong class="adm-del-user-card__name">
                      {{ fullUserName(user) }}
                    </strong>

                    <p class="adm-del-user-card__meta">
                      {{
                        user.carrera_nombre ||
                        user.facultad_nombre ||
                        user.email ||
                        "Sin unidad académica registrada"
                      }}
                    </p>

                    <p
                      v-if="user.email && (user.carrera_nombre || user.facultad_nombre)"
                      class="adm-del-user-card__email"
                    >
                      {{ user.email }}
                    </p>
                  </div>
                </div>

                <div class="adm-del-user-card__publication-row">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h5M8 13h8M8 17h8"
                    />
                  </svg>

                  <span>
                    {{ publicationTotalLabel(user.total_publicaciones) }}
                  </span>
                </div>

                <div class="adm-del-user-card__footer">
                  <span
                    class="adm-del-user-card__action"
                    :class="{
                      'is-selected':
                        Number(selectedUser?.id) === Number(user.id),
                    }"
                  >
                    {{
                      Number(selectedUser?.id) === Number(user.id)
                        ? "Usuario seleccionado"
                        : "Seleccionar usuario"
                    }}

                    <span aria-hidden="true">
                      {{
                        Number(selectedUser?.id) === Number(user.id)
                          ? "✓"
                          : "→"
                      }}
                    </span>
                  </span>
                </div>
              </button>
            </li>
          </ul>
        </section>

        <!-- ===================================================
             ESPACIO DE TRABAJO SIN USUARIO
        ==================================================== -->
        <section
          v-if="!selectedUser"
          class="adm-del-empty-workspace adm-surface"
          aria-labelledby="adm-del-empty-title"
        >
          <div
            class="adm-del-empty-workspace__icon"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h5M8 13h8M8 17h8"
              />
            </svg>
          </div>

          <h2
            id="adm-del-empty-title"
            class="adm-del-empty-workspace__title"
          >
            Seleccione un usuario para continuar
          </h2>

          <p class="adm-del-empty-workspace__text">
            Después de seleccionar una cuenta podrá consultar su
            información, revisar el historial y abrir el formulario
            correspondiente al tipo de publicación.
          </p>
        </section>

        <!-- ===================================================
             ESPACIO DE TRABAJO
        ==================================================== -->
        <section
          v-else
          class="adm-del-workspace"
          aria-label="Registro delegado para el usuario seleccionado"
        >
          <!-- Usuario seleccionado -->
          <section
            class="adm-del-card adm-del-card--target adm-surface"
            aria-labelledby="adm-del-target-title"
          >
            <div class="adm-del-card__head">
              <div>
                <span class="adm-del-section-kicker">
                  Cuenta objetivo
                </span>

                <h2
                  id="adm-del-target-title"
                  class="adm-del-card__title"
                >
                  Usuario seleccionado
                </h2>
              </div>

              <span class="adm-del-mini-pill adm-del-mini-pill--selected">
                Seleccionado
              </span>
            </div>

            <div class="adm-del-target-panel">
              <div class="adm-del-target-panel__identity">
                <div class="adm-del-target-avatar">
                  <img
                    v-if="hasUsableAvatar(selectedUser)"
                    :src="resolveAvatarUrl(selectedUser)"
                    :alt="`Foto de perfil de ${fullUserName(selectedUser)}`"
                    decoding="async"
                    @error="markAvatarBroken(selectedUser)"
                  />

                  <span v-else aria-hidden="true">
                    {{ selectedInitials }}
                  </span>
                </div>

                <div class="adm-del-target-copy">
                  <h3 class="adm-del-target-name">
                    {{ fullUserName(selectedUser) }}
                  </h3>

                  <p class="adm-del-target-email">
                    {{
                      selectedUser.email ||
                      "Sin correo registrado"
                    }}
                  </p>

                  <div class="adm-del-target-pills">
                    <span
                      v-if="userBadgeLabel(selectedUser)"
                      class="adm-del-mini-pill"
                    >
                      {{ userBadgeLabel(selectedUser) }}
                    </span>

                    <span class="adm-del-mini-pill">
                      {{
                        publicationTotalLabel(
                          selectedUser.total_publicaciones
                        )
                      }}
                    </span>
                  </div>
                </div>
              </div>

              <dl class="adm-del-target-grid">
                <div class="adm-del-info-box">
                  <dt class="adm-del-info-box__label">
                    Facultad
                  </dt>

                  <dd class="adm-del-info-box__value">
                    {{
                      selectedUser.facultad_nombre ||
                      "Sin facultad asignada"
                    }}
                  </dd>
                </div>

                <div class="adm-del-info-box">
                  <dt class="adm-del-info-box__label">
                    Carrera
                  </dt>

                  <dd class="adm-del-info-box__value">
                    {{
                      selectedUser.carrera_nombre ||
                      "Sin carrera asignada"
                    }}
                  </dd>
                </div>

                <div class="adm-del-info-box">
                  <dt class="adm-del-info-box__label">
                    Autor vinculado
                  </dt>

                  <dd class="adm-del-info-box__value">
                    {{
                      selectedUser.autor_nombre ||
                      fullUserName(selectedUser)
                    }}
                  </dd>
                </div>
              </dl>
            </div>
          </section>

          <!-- Tipos de publicación -->
          <section
            class="adm-del-card adm-del-card--actions adm-surface"
            aria-labelledby="adm-del-actions-title"
          >
            <div class="adm-del-card__head">
              <div>
                <span class="adm-del-section-kicker">
                  Nuevo registro
                </span>

                <h2
                  id="adm-del-actions-title"
                  class="adm-del-card__title"
                >
                  Registrar publicación
                </h2>

                <p class="adm-del-card__subtitle">
                  El formulario se abrirá en modo administrativo
                  delegado para la cuenta seleccionada.
                </p>
              </div>
            </div>

            <div class="adm-del-action-grid">
              <button
                v-for="type in publicationTypes"
                :key="type.key"
                type="button"
                class="adm-del-action-card"
                :class="`adm-del-action-card--${type.tone}`"
                :aria-label="
                  `Registrar ${type.title} para ${fullUserName(selectedUser)}`
                "
                @click="goToForm(type.key)"
              >
                <span class="adm-del-action-card__code">
                  {{ type.code }}
                </span>

                <strong>
                  {{ type.title }}
                </strong>

                <span class="adm-del-action-card__arrow" aria-hidden="true">
                  →
                </span>
              </button>
            </div>
          </section>

          <!-- Historial -->
          <section
            class="adm-del-card adm-del-card--history adm-surface"
            aria-labelledby="adm-del-history-title"
            :aria-busy="loadingPublicaciones ? 'true' : 'false'"
          >
            <div class="adm-del-card__head">
              <div>
                <span class="adm-del-section-kicker">
                  Producción registrada
                </span>

                <h2
                  id="adm-del-history-title"
                  class="adm-del-card__title"
                >
                  Historial de publicaciones
                </h2>

                <p class="adm-del-card__subtitle">
                  Registros encontrados para el usuario objetivo.
                </p>
              </div>

              <div class="adm-del-head-actions">
                <span
                  class="adm-del-count"
                  aria-live="polite"
                >
                  {{ historyCountLabel }}
                </span>

                <button
                  class="adm-del-button adm-del-button--secondary adm-del-button--icon-text"
                  type="button"
                  :disabled="loadingPublicaciones"
                  @click="refreshSelectedHistory"
                >
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M17.7 6.3A8 8 0 1 0 20 12h-2a6 6 0 1 1-1.8-4.3L13 11h8V3l-3.3 3.3Z"
                    />
                  </svg>

                  Actualizar
                </button>
              </div>
            </div>

            <!-- Carga -->
            <div
              v-if="
                loadingPublicaciones &&
                !userPublicaciones.length
              "
              class="adm-del-history-skeleton"
              role="status"
              aria-live="polite"
            >
              <span class="adm-del-sr-only">
                Cargando historial de publicaciones.
              </span>

              <article
                v-for="index in 4"
                :key="index"
                class="adm-del-history-skeleton__card"
                aria-hidden="true"
              >
                <span class="adm-del-skeleton adm-del-skeleton--history-chip"></span>
                <span class="adm-del-skeleton adm-del-skeleton--history-title"></span>
                <span class="adm-del-skeleton adm-del-skeleton--history-meta"></span>
              </article>
            </div>

            <!-- Error -->
            <div
              v-else-if="publicacionesError"
              class="adm-del-state adm-del-state--error"
              role="alert"
              aria-live="assertive"
            >
              <div class="adm-del-state__icon" aria-hidden="true">
                !
              </div>

              <div>
                <strong>No se pudo cargar el historial</strong>
                <span>{{ publicacionesError }}</span>
              </div>
            </div>

            <!-- Vacío -->
            <div
              v-else-if="!userPublicaciones.length"
              class="adm-del-state"
            >
              <div class="adm-del-state__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h5M8 13h8M8 17h8"
                  />
                </svg>
              </div>

              <div>
                <strong>Sin publicaciones registradas</strong>

                <span>
                  Este usuario todavía no muestra publicaciones
                  en esta vista.
                </span>
              </div>
            </div>

            <!-- Resultados -->
            <div
              v-else
              class="adm-del-history-grid"
              role="list"
              aria-label="Historial de publicaciones"
            >
              <article
                v-for="(item, index) in userPublicaciones"
                :key="historyItemKey(item, index)"
                class="adm-del-history-card"
                role="listitem"
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
                    {{ publicationPeriod(item) }}
                  </span>
                </div>

                <strong class="adm-del-history-card__title">
                  {{
                    item.titulo ||
                    item.titulo_admin ||
                    "Publicación sin título"
                  }}
                </strong>

                <p class="adm-del-history-card__meta">
                  {{
                    item.autor ||
                    item.autores ||
                    item.primer_autor ||
                    "Sin autores registrados"
                  }}
                </p>

                <div class="adm-del-history-card__footer">
                  <span>
                    {{
                      item.carrera ||
                      item.carrera_nombre ||
                      "Sin carrera"
                    }}
                  </span>

                  <span>
                    {{
                      item.facultad ||
                      item.facultad_nombre ||
                      "Sin facultad"
                    }}
                  </span>
                </div>
              </article>
            </div>
          </section>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
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
const brokenAvatarKeys = ref(new Set());

const loadingPublicaciones = ref(false);
const publicacionesError = ref("");
const userPublicaciones = ref([]);

let searchTimer = null;
let usersRequestSerial = 0;
let publicacionesRequestSerial = 0;

const publicationTypes = Object.freeze([
  {
    key: "articuloAltoImpacto",
    code: "AAI",
    title: "Artículo de alto impacto",
    tone: "aai",
  },
  {
    key: "articuloRegional",
    code: "AR",
    title: "Artículo regional",
    tone: "ar",
  },
  {
    key: "ponencia",
    code: "PON",
    title: "Ponencia",
    tone: "pon",
  },
  {
    key: "libro",
    code: "LIB",
    title: "Libro",
    tone: "lib",
  },
  {
    key: "capitulo",
    code: "CAP",
    title: "Capítulo de libro",
    tone: "cap",
  },
]);

const normalizeRows = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
};

const getBackendOrigin = () => {
  const configuredApiUrl = String(
    import.meta.env.VITE_API_URL || ""
  ).trim();

  const fallbackOrigin =
    typeof window !== "undefined"
      ? window.location.origin
      : "";

  const candidate = configuredApiUrl || fallbackOrigin;

  try {
    return new URL(candidate).origin;
  } catch {
    return fallbackOrigin;
  }
};

const normalizeAvatarPath = (value) => {
  const raw = String(value || "").trim();

  if (!raw) {
    return "";
  }

  if (/^(https?:|data:|blob:)/i.test(raw)) {
    return raw;
  }

  if (raw.startsWith("//")) {
    const protocol =
      typeof window !== "undefined"
        ? window.location.protocol
        : "https:";

    return `${protocol}${raw}`;
  }

  const backendOrigin = getBackendOrigin();

  if (!backendOrigin) {
    return raw;
  }

  let normalizedPath = raw;

  if (!normalizedPath.startsWith("/")) {
    normalizedPath = normalizedPath.startsWith("media/")
      ? `/${normalizedPath}`
      : `/media/${normalizedPath}`;
  }

  try {
    return new URL(normalizedPath, `${backendOrigin}/`).href;
  } catch {
    return raw;
  }
};

const resolveAvatarUrl = (user) => {
  if (!user) {
    return "";
  }

  const candidate =
    user.avatar_url ||
    user.avatar ||
    user.foto_perfil_url ||
    user.foto_perfil ||
    user.foto_url ||
    user.imagen_url ||
    user.imagen ||
    user.photo_url ||
    user.photo ||
    user.profile_picture_url ||
    user.profile_picture ||
    user.usuario?.avatar_url ||
    user.usuario?.avatar ||
    user.autor?.avatar_url ||
    user.autor?.avatar ||
    user.perfil?.avatar_url ||
    user.perfil?.avatar ||
    user.perfil_academico?.avatar_url ||
    user.perfil_academico?.avatar ||
    "";

  return normalizeAvatarPath(candidate);
};

const avatarFailureKey = (user) => {
  const identity = String(
    user?.id || user?.email || "usuario"
  ).trim();

  return `${identity}|${resolveAvatarUrl(user)}`;
};

const hasUsableAvatar = (user) => {
  const avatarUrl = resolveAvatarUrl(user);

  if (!avatarUrl) {
    return false;
  }

  return !brokenAvatarKeys.value.has(
    avatarFailureKey(user)
  );
};

const markAvatarBroken = (user) => {
  const key = avatarFailureKey(user);

  if (!key || key.endsWith("|")) {
    return;
  }

  const next = new Set(brokenAvatarKeys.value);
  next.add(key);
  brokenAvatarKeys.value = next;
};

const hasSearch = computed(() => {
  return Boolean(String(search.value || "").trim());
});

const filteredUsers = computed(() => {
  /*
   * La búsqueda ya se resuelve en el backend.
   *
   * No volvemos a filtrar localmente porque el backend también
   * puede encontrar usuarios por datos del Autor (por ejemplo,
   * ORCID, Registro SENESCYT o Scopus ID) que no necesariamente
   * forman parte del payload compacto del usuario.
   */
  if (!hasSearch.value) {
    return [];
  }

  return Array.isArray(users.value)
    ? users.value
    : [];
});

const selectedInitials = computed(() => {
  return initialsFromUser(selectedUser.value);
});

const searchResultLabel = computed(() => {
  const total = filteredUsers.value.length;

  return total === 1
    ? "1 usuario encontrado"
    : `${total} usuarios encontrados`;
});

const searchFeedbackLabel = computed(() => {
  if (!hasSearch.value) {
    return "";
  }

  if (loadingUsers.value) {
    return "Buscando usuarios...";
  }

  const total = filteredUsers.value.length;

  if (!total) {
    return `No hay coincidencias para “${search.value}”.`;
  }

  return total === 1
    ? "Se encontró 1 usuario."
    : `Se encontraron ${total} usuarios.`;
});

const historyCountLabel = computed(() => {
  const total = userPublicaciones.value.length;

  return total === 1
    ? "1 registro"
    : `${total} registros`;
});

const resolveRouteUsuarioId = () => {
  const raw =
    route.params?.usuarioId ||
    route.query?.usuario_objetivo_id ||
    route.query?.usuario_id ||
    route.query?.usuarioId ||
    route.query?.user_id ||
    "";

  const parsed = Number(String(raw).trim());

  return Number.isFinite(parsed) && parsed > 0
    ? parsed
    : null;
};

const fullUserName = (user) => {
  const nombres = String(user?.nombres || "").trim();
  const apellidos = String(user?.apellidos || "").trim();

  return (
    `${nombres} ${apellidos}`.trim() ||
    `Usuario #${user?.id || "—"}`
  );
};

const initialsFromUser = (user) => {
  if (!user) {
    return "—";
  }

  const firstName =
    String(user?.nombres || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)[0] || "";

  const firstSurname =
    String(user?.apellidos || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)[0] || "";

  const initials = [
    firstName.charAt(0),
    firstSurname.charAt(0),
  ]
    .filter(Boolean)
    .join("")
    .toUpperCase();

  return initials || "US";
};

const userBadgeLabel = (user) => {
  if (user?.es_pendiente) {
    return "Pendiente";
  }

  if (user?.es_externo) {
    return "Externo";
  }

  if (user?.es_institucional) {
    return "Institucional";
  }

  return "";
};

const badgeScopeClass = (user) => {
  if (user?.es_pendiente) {
    return "is-warning";
  }

  if (user?.es_institucional) {
    return "is-primary";
  }

  return "is-soft";
};

const publicationTotalLabel = (value) => {
  const total = Number(value || 0);

  return total === 1
    ? "1 publicación"
    : `${total} publicaciones`;
};

const MONTH_LABELS = Object.freeze({
  1: "Enero",
  2: "Febrero",
  3: "Marzo",
  4: "Abril",
  5: "Mayo",
  6: "Junio",
  7: "Julio",
  8: "Agosto",
  9: "Septiembre",
  10: "Octubre",
  11: "Noviembre",
  12: "Diciembre",
});


const publicationPeriod = (item) => {
  const rawYear =
    item?.anio_publicacion ??
    item?.anio ??
    null;

  const year = Number(rawYear);

  const rawMonth =
    item?.mes_publicacion ??
    item?.mes ??
    null;

  const month = Number(rawMonth);

  const backendMonthLabel = String(
    item?.mes_publicacion_label || ""
  ).trim();

  const monthLabel =
    backendMonthLabel ||
    (
      Number.isInteger(month) &&
      month >= 1 &&
      month <= 12
        ? MONTH_LABELS[month]
        : ""
    );

  const hasYear =
    Number.isInteger(year) &&
    year > 0;

  if (hasYear && monthLabel) {
    return `${monthLabel} de ${year}`;
  }

  if (hasYear) {
    return String(year);
  }

  if (monthLabel) {
    return monthLabel;
  }

  return "Sin período";
};

const historyItemKey = (item, index) => {
  return [
    item?.id,
    item?.numero,
    item?.titulo,
    index,
  ]
    .filter(
      (value) =>
        value !== undefined &&
        value !== null &&
        value !== ""
    )
    .join("-");
};

const mergeUserIntoList = (user) => {
  if (!user?.id) {
    return;
  }

  const index = users.value.findIndex(
    (item) => Number(item.id) === Number(user.id)
  );

  if (index >= 0) {
    users.value.splice(index, 1, user);
    return;
  }

  users.value.unshift(user);
};

const fetchUserById = async (userId) => {
  return adminApi.obtenerUsuario(userId);
};

const fetchUsers = async () => {
  const query = String(search.value || "").trim();

  if (!query) {
    usersRequestSerial += 1;
    users.value = [];
    userError.value = "";
    loadingUsers.value = false;
    return;
  }

  const requestId = ++usersRequestSerial;

  loadingUsers.value = true;
  userError.value = "";

  try {
    const data = await adminApi.usuarios(query, {
      scope: "activos",
    });

    if (requestId !== usersRequestSerial) {
      return;
    }

    users.value = normalizeRows(data);

    if (selectedUser.value?.id) {
      const refreshedUser = users.value.find(
        (item) =>
          Number(item.id) === Number(selectedUser.value.id)
      );

      if (refreshedUser) {
        selectedUser.value = refreshedUser;
      }
    }
  } catch (error) {
    if (requestId !== usersRequestSerial) {
      return;
    }

    console.error("Error buscando usuarios:", error);

    userError.value =
      error?.response?.data?.detail ||
      "No fue posible consultar los usuarios en este momento.";

    users.value = [];
  } finally {
    if (requestId === usersRequestSerial) {
      loadingUsers.value = false;
    }
  }
};

const fetchUserPublicaciones = async () => {
  if (!selectedUser.value?.id) {
    publicacionesRequestSerial += 1;
    userPublicaciones.value = [];
    publicacionesError.value = "";
    loadingPublicaciones.value = false;
    return;
  }

  const requestId = ++publicacionesRequestSerial;
  const selectedUserId = selectedUser.value.id;

  loadingPublicaciones.value = true;
  publicacionesError.value = "";

  try {
    const response = await listarAdminPublicaciones({
      usuario_objetivo_id: selectedUserId,
      ordering: "anio_desc",
    });

    if (requestId !== publicacionesRequestSerial) {
      return;
    }

    userPublicaciones.value = normalizeRows(response);
  } catch (error) {
    if (requestId !== publicacionesRequestSerial) {
      return;
    }

    console.error(
      "Error cargando publicaciones del usuario:",
      error
    );

    publicacionesError.value =
      error?.response?.data?.detail ||
      "No fue posible cargar el historial del usuario seleccionado.";

    userPublicaciones.value = [];
  } finally {
    if (requestId === publicacionesRequestSerial) {
      loadingPublicaciones.value = false;
    }
  }
};

const buildTarget = (user = selectedUser.value) => {
  if (!user?.id) {
    return null;
  }

  return {
    usuarioId: user.id,
    autorId: user.autor_id || null,
    usuarioNombre: fullUserName(user),
    autorNombre: user.autor_nombre || "",
  };
};

const syncRouteWithSelectedUser = async (user) => {
  if (!user?.id) {
    return;
  }

  const usuarioId = String(user.id);
  const currentUsuarioId = String(
    resolveRouteUsuarioId() || ""
  );
  const currentRouteName = String(route.name || "");

  const query = buildAdminPublicacionTargetQuery(
    buildTarget(user)
  );

  if (
    currentRouteName === "AdminPublicacionesUsuario" &&
    currentUsuarioId === usuarioId
  ) {
    return;
  }

  await router.replace({
    name: "AdminPublicacionesUsuario",
    params: {
      usuarioId,
    },
    query,
  });
};

const selectUser = async (user, options = {}) => {
  const { syncRoute = true } = options;

  if (!user?.id) {
    return;
  }

  selectedUser.value = user;
  mergeUserIntoList(user);

  if (syncRoute) {
    await syncRouteWithSelectedUser(user);
  }

  await fetchUserPublicaciones();
};

const goToForm = (kind) => {
  const target = buildTarget();

  if (!target) {
    return;
  }

  const links = buildAdminPublicacionLinks(target);
  const destination = links[kind];

  if (!destination) {
    return;
  }

  router.push(destination);
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
  if (!String(search.value || "").trim()) {
    clearSearch();
  }
};

const refreshSelectedHistory = async () => {
  await fetchUserPublicaciones();
};

const hydrateSelectedUserFromRoute = async () => {
  const usuarioId = resolveRouteUsuarioId();

  if (!usuarioId) {
    return;
  }

  if (
    Number(selectedUser.value?.id) === Number(usuarioId)
  ) {
    return;
  }

  let user =
    users.value.find(
      (item) => Number(item.id) === Number(usuarioId)
    ) || null;

  if (!user) {
    try {
      user = await fetchUserById(usuarioId);

      if (user) {
        mergeUserIntoList(user);
      }
    } catch (error) {
      console.error(
        "No se pudo recuperar el usuario de la ruta:",
        error
      );

      userError.value =
        error?.response?.data?.detail ||
        "No se pudo recuperar el usuario indicado en la ruta.";
    }
  }

  if (user) {
    await selectUser(user, {
      syncRoute: false,
    });
  }
};

watch(search, () => {
  if (searchTimer) {
    clearTimeout(searchTimer);
  }

  const query = String(search.value || "").trim();

  if (!query) {
    usersRequestSerial += 1;
    users.value = [];
    userError.value = "";
    loadingUsers.value = false;
    searchTimer = null;
    return;
  }

  searchTimer = window.setTimeout(() => {
    fetchUsers();
  }, 350);
});

watch(
  () => [
    route.name,
    route.params?.usuarioId,
    route.query?.usuario_objetivo_id,
    route.query?.usuario_id,
  ],
  async () => {
    await hydrateSelectedUserFromRoute();
  }
);

onMounted(async () => {
  await hydrateSelectedUserFromRoute();
});

onBeforeUnmount(() => {
  usersRequestSerial += 1;
  publicacionesRequestSerial += 1;

  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-publicaciones-delegadas.css"></style>
