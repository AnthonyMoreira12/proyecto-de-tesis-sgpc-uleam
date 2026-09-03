<template>
  <div class="sgpc-admin-page">
    <main
      class="adm-delegated-user"
      :aria-busy="loadingUser || loadingPublications"
    >
      <header class="adm-delegated-user__topbar">
        <button
          class="adm-delegated-user__back"
          type="button"
          @click="changeUser"
        >
          <span aria-hidden="true">←</span>
          Elegir otro usuario
        </button>

        <button
          class="adm-delegated-user__refresh"
          type="button"
          :disabled="loadingUser || loadingPublications"
          @click="refreshAll"
        >
          <span aria-hidden="true">↻</span>
          {{
            loadingUser || loadingPublications
              ? "Actualizando…"
              : "Actualizar"
          }}
        </button>
      </header>

      <nav
        class="adm-delegated-user__progress"
        aria-label="Pasos para registrar una publicación"
      >
        <ol>
          <li class="is-complete">
            <span class="adm-delegated-user__step-number" aria-hidden="true">✓</span>
            <span class="adm-delegated-user__step-copy">
              <strong>Usuario seleccionado</strong>
            </span>
          </li>
          <li class="is-active" aria-current="step">
            <span class="adm-delegated-user__step-number">2</span>
            <span class="adm-delegated-user__step-copy">
              <strong>Elegir tipo</strong>
            </span>
          </li>
          <li>
            <span class="adm-delegated-user__step-number">3</span>
            <span class="adm-delegated-user__step-copy">
              <strong>Completar datos</strong>
            </span>
          </li>
        </ol>
      </nav>

      <section
        v-if="loadingUser && !user"
        class="adm-delegated-user__state adm-delegated-user__surface"
        role="status"
      >
        <span
          class="adm-delegated-user__spinner"
          aria-hidden="true"
        ></span>

        <div>
          <strong>Cargando usuario</strong>
          <span>Cargando información…</span>
        </div>
      </section>

      <section
        v-else-if="userError && !user"
        class="adm-delegated-user__state adm-delegated-user__state--error adm-delegated-user__surface"
        role="alert"
      >
        <div>
          <strong>No pudimos cargar el usuario.</strong>
          <span>{{ userError }}</span>
        </div>

        <button
          type="button"
          @click="loadUser"
        >
          Reintentar
        </button>
      </section>

      <template v-else-if="user">
        <section
          class="adm-delegated-user__context adm-delegated-user__surface"
          aria-labelledby="delegated-user-name"
        >
          <span
            class="adm-delegated-user__avatar"
            aria-hidden="true"
          >
            {{ initials }}
          </span>

          <div class="adm-delegated-user__identity">
            <span class="adm-delegated-user__eyebrow">
              Registrar publicación para
            </span>

            <h1 id="delegated-user-name">
              {{ fullName }}
            </h1>

            <p>
              {{ user.email || "Sin correo registrado" }}
            </p>
          </div>

          <dl class="adm-delegated-user__facts">
            <div>
              <dt>Tipo de usuario</dt>
              <dd>{{ accountTypeLabel }}</dd>
            </div>

            <div>
              <dt>Sede</dt>
              <dd>{{ sedeLabel }}</dd>
            </div>

            <div>
              <dt>Carrera</dt>
              <dd>{{ carreraLabel }}</dd>
            </div>

            <div>
              <dt>Publicaciones</dt>
              <dd>{{ publicationCountLabel }}</dd>
            </div>
          </dl>
        </section>

        <AdminInlineLoader
          v-if="loadingUser && user"
          message="Actualizando información del usuario…"
          class="adm-delegated-user__inline-loader"
        />

        <div
          v-if="userError && user"
          class="adm-delegated-user__refresh-error"
          role="status"
        >
          No pudimos actualizar los datos del usuario. Se mantiene la última información disponible.
        </div>

        <section
          class="adm-delegated-user__register adm-delegated-user__surface"
          aria-labelledby="delegated-register-title"
        >
          <header class="adm-delegated-user__section-head">
            <div>
              <h2 id="delegated-register-title">
                Tipo de publicación
              </h2>

              <p>
                Seleccione el tipo que desea registrar.
              </p>
            </div>
          </header>

          <div class="adm-delegated-user__type-grid">
            <button
              v-for="type in publicationTypes"
              :key="type.key"
              class="adm-delegated-user__type"
              type="button"
              @click="goToForm(type.key)"
            >

              <span class="adm-delegated-user__type-copy">
                <strong>{{ type.title }}</strong>
              </span>

              <span
                class="adm-delegated-user__type-arrow"
                aria-hidden="true"
              >
                →
              </span>
            </button>
          </div>
        </section>

        <section
          class="adm-delegated-user__history adm-delegated-user__surface"
          :aria-busy="loadingPublications"
          aria-labelledby="delegated-history-title"
        >
          <header class="adm-delegated-user__section-head">
            <div>
              <h2 id="delegated-history-title">
                Publicaciones registradas
              </h2>

              <p>
                Revise lo que ya está registrado antes de añadir una nueva publicación.
              </p>
            </div>
          </header>

          <AdminInlineLoader
            v-if="loadingPublications && publications.length"
            message="Actualizando publicaciones…"
            class="adm-delegated-user__inline-loader"
          />

          <div
            v-if="loadingPublications && !publications.length"
            class="adm-delegated-user__history-state"
            role="status"
          >
            <span
              class="adm-delegated-user__spinner"
              aria-hidden="true"
            ></span>

            <span>Cargando publicaciones…</span>
          </div>

          <div
            v-else-if="publicationsError && !publications.length"
            class="adm-delegated-user__history-state adm-delegated-user__history-state--error"
            role="alert"
          >
            <span>{{ publicationsError }}</span>

            <button
              type="button"
              @click="loadPublications"
            >
              Reintentar
            </button>
          </div>

          <div
            v-else-if="!publications.length"
            class="adm-delegated-user__history-state"
          >
            <span>
              Aún no hay publicaciones registradas para esta persona.
            </span>
          </div>

          <div
            v-if="publicationsError && publications.length"
            class="adm-delegated-user__refresh-error"
            role="status"
          >
            No pudimos actualizar las publicaciones. Se conserva la última información disponible.
          </div>

          <div
            v-if="publications.length"
            class="adm-delegated-user__table-wrap"
          >
            <table class="adm-delegated-user__table">
              <caption class="adm-delegated-user__sr-only">
                Publicaciones registradas para la persona seleccionada
              </caption>

              <thead>
                <tr>
                  <th scope="col">Publicación</th>
                  <th scope="col">Tipo</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Período</th>
                  <th scope="col">Acciones</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="item in publications"
                  :key="item.id"
                >
                  <td data-label="Publicación">
                    <div class="adm-delegated-user__publication">
                      <strong>
                        {{
                          item.titulo ||
                          item.titulo_admin ||
                          "Publicación sin título"
                        }}
                      </strong>

                    </div>
                  </td>

                  <td data-label="Tipo">
                    <span class="adm-delegated-user__type-label">
                      {{ publicationTypeLabel(item) }}
                    </span>
                  </td>

                  <td data-label="Estado">
                    <span
                      class="adm-delegated-user__state-pill"
                      :class="`is-${stateTone(item)}`"
                    >
                      {{ stateLabel(item) }}
                    </span>
                  </td>

                  <td data-label="Período">
                    <span class="adm-delegated-user__period">
                      {{ publicationPeriod(item) }}
                    </span>
                  </td>

                  <td data-label="Acciones">
                    <div class="adm-delegated-user__row-actions">
                      <button
                        type="button"
                        :disabled="!item?.id"
                        @click="goToPublicationDetail(item)"
                      >
                        Ver publicación
                      </button>

                      <details class="adm-delegated-user__more">
                        <summary>Más</summary>

                        <div class="adm-delegated-user__more-menu">
                          <button
                            type="button"
                            :disabled="!item?.id"
                            @click="goToPublicationEdit(item)"
                          >
                            Editar
                          </button>

                          <button
                            type="button"
                            :disabled="!item?.id"
                            @click="goToReview(item)"
                          >
                            Ver revisión
                          </button>
                        </div>
                      </details>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </main>
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

import { adminApi } from "../../scripts/api/adminApi";

import AdminInlineLoader from
  "../_shared/components/feedback/AdminInlineLoader.vue";

import {
  listarAdminPublicaciones,
} from "../../scripts/api/publicacionesAdminApi";

import {
  buildAdminPublicacionLinks,
} from "./admin-publicaciones-route-utils";

import {
  estadoPublicacionLabel,
  normalizarEstadoPublicacion,
} from "../../scripts/utils/publicacion-estados";

const route = useRoute();
const router = useRouter();

const user = ref(null);
const publications = ref([]);

const loadingUser = ref(false);
const loadingPublications = ref(false);

const userError = ref("");
const publicationsError = ref("");

let userRequestSerial = 0;
let publicationsRequestSerial = 0;

const publicationTypes = Object.freeze([
  {
    key: "articuloAltoImpacto",
    title: "Artículo de alto impacto",
  },
  {
    key: "articuloRegional",
    title: "Artículo regional",
  },
  {
    key: "ponencia",
    title: "Ponencia",
  },
  {
    key: "libro",
    title: "Libro",
  },
  {
    key: "capitulo",
    title: "Capítulo de libro",
  },
]);

const userId = computed(() => {
  const parsed = Number(
    String(route.params?.usuarioId || "").trim()
  );

  return (
    Number.isFinite(parsed) &&
    parsed > 0
      ? parsed
      : null
  );
});

const normalizeRows = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
};

const fullName = computed(() => {
  const value = [
    String(user.value?.nombres || "").trim(),
    String(user.value?.apellidos || "").trim(),
  ]
    .filter(Boolean)
    .join(" ");

  return (
    value ||
    user.value?.email ||
    "Usuario sin nombre"
  );
});

const initials = computed(() => {
  const parts = [
    String(user.value?.nombres || "").trim(),
    String(user.value?.apellidos || "").trim(),
  ].filter(Boolean);

  const value = parts
    .map((part) =>
      part
        .split(/\s+/)
        .filter(Boolean)[0]
        ?.charAt(0)
    )
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return value || "US";
});

const accountTypeLabel = computed(() => {
  if (user.value?.es_institucional) {
    return "Usuario institucional";
  }

  if (user.value?.es_externo) {
    return "Usuario externo";
  }

  return "Usuario";
});

const sedeLabel = computed(() => {
  if (!user.value?.es_institucional) {
    return "No aplica";
  }

  return (
    user.value?.sede_nombre ||
    (
      typeof user.value?.sede === "object"
        ? user.value.sede?.nombre
        : user.value?.sede
    ) ||
    "Sin sede"
  );
});

const carreraLabel = computed(() => {
  if (!user.value?.es_institucional) {
    return "No aplica";
  }

  return (
    user.value?.carrera_nombre ||
    (
      typeof user.value?.carrera === "object"
        ? user.value.carrera?.nombre
        : null
    ) ||
    user.value?.facultad_nombre ||
    "Sin carrera"
  );
});

const publicationCountLabel = computed(() => {
  const backendTotal =
    Number(user.value?.total_publicaciones);

  const total =
    Number.isFinite(backendTotal) &&
    backendTotal >= 0
      ? backendTotal
      : publications.value.length;

  return Number(total).toLocaleString("es-EC");
});

const buildTarget = () => ({
  usuarioId: user.value?.id || userId.value,
  autorId: user.value?.autor_id || null,
  usuarioNombre: fullName.value,
  autorNombre: user.value?.autor_nombre || "",
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

  if (status === 404) {
    return "No encontramos la información solicitada.";
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

const loadUser = async () => {
  if (!userId.value) {
    user.value = null;
    userError.value =
      "No encontramos el usuario solicitado.";
    return;
  }

  const requestId =
    ++userRequestSerial;

  loadingUser.value = true;
  userError.value = "";

  try {
    const data =
      await adminApi.obtenerUsuario(
        userId.value
      );

    if (
      requestId !==
      userRequestSerial
    ) {
      return;
    }

    user.value = data;
  } catch (error) {
    if (
      requestId !==
      userRequestSerial
    ) {
      return;
    }

    console.error(
      "Error cargando usuario delegado:",
      error
    );

    userError.value =
      getFriendlyError(
        error,
        "No pudimos cargar el usuario seleccionado."
      );

    if (!user.value) {
      user.value = null;
    }
  } finally {
    if (
      requestId ===
      userRequestSerial
    ) {
      loadingUser.value = false;
    }
  }
};

const loadPublications = async () => {
  if (!userId.value) {
    publications.value = [];
    return;
  }

  const requestId =
    ++publicationsRequestSerial;

  loadingPublications.value = true;
  publicationsError.value = "";

  try {
    const response =
      await listarAdminPublicaciones({
        usuario_objetivo_id:
          userId.value,
        ordering: "anio_desc",
      });

    if (
      requestId !==
      publicationsRequestSerial
    ) {
      return;
    }

    publications.value =
      normalizeRows(response);
  } catch (error) {
    if (
      requestId !==
      publicationsRequestSerial
    ) {
      return;
    }

    console.error(
      "Error cargando publicaciones del usuario:",
      error
    );

    publicationsError.value =
      getFriendlyError(
        error,
        "No pudimos cargar las publicaciones."
      );

    /*
      Se conservan los datos ya visibles cuando el refresco falla.
      Así una incidencia temporal no vacía el historial del usuario.
    */
  } finally {
    if (
      requestId ===
      publicationsRequestSerial
    ) {
      loadingPublications.value = false;
    }
  }
};

const refreshAll = async () => {
  await Promise.all([
    loadUser(),
    loadPublications(),
  ]);
};

const changeUser = () => {
  router.push({
    name: "AdminPublicaciones",
  });
};

const goToForm = (kind) => {
  if (!userId.value) return;

  const links =
    buildAdminPublicacionLinks(
      buildTarget()
    );

  const destination =
    links[kind];

  if (destination) {
    router.push(destination);
  }
};

const goToPublicationDetail = (item) => {
  const id = Number(item?.id || 0);

  if (
    !Number.isInteger(id) ||
    id <= 0
  ) {
    return;
  }

  router.push({
    name: "AdminPublicacionDetalle",
    params: {
      id,
    },
  });
};

const goToPublicationEdit = (item) => {
  const id = Number(item?.id || 0);

  if (
    !Number.isInteger(id) ||
    id <= 0
  ) {
    return;
  }

  router.push({
    name: "AdminEditarPublicacion",
    params: {
      id,
    },
  });
};

const goToReview = (item) => {
  const id = Number(item?.id || 0);

  if (
    !Number.isInteger(id) ||
    id <= 0
  ) {
    return;
  }

  router.push({
    name: "AdminRevisionDetalle",
    params: {
      id,
    },
  });
};

const publicationTypeLabel = (item) =>
  String(
    item?.tipo_publicacion_final_label ||
    item?.tipo_publicacion_label ||
    item?.tipo ||
    "Publicación"
  ).trim();

const stateLabel = (item) => {
  const raw =
    item?.estado ||
    item?.estado_publicacion ||
    "";

  const normalized =
    normalizarEstadoPublicacion(raw);

  return (
    estadoPublicacionLabel(normalized) ||
    "Sin estado"
  );
};

const stateTone = (item) => {
  const raw =
    normalizarEstadoPublicacion(
      item?.estado ||
      item?.estado_publicacion ||
      ""
    );

  if (raw === "aprobada") {
    return "success";
  }

  if (raw === "rechazada") {
    return "danger";
  }

  if (
    raw === "observada" ||
    raw === "en_revision"
  ) {
    return "warning";
  }

  return "neutral";
};

const MONTHS = Object.freeze({
  1: "Ene",
  2: "Feb",
  3: "Mar",
  4: "Abr",
  5: "May",
  6: "Jun",
  7: "Jul",
  8: "Ago",
  9: "Sep",
  10: "Oct",
  11: "Nov",
  12: "Dic",
});

const publicationPeriod = (item) => {
  const year = Number(
    item?.anio_publicacion ??
    item?.anio ??
    0
  );

  const month = Number(
    item?.mes_publicacion ??
    item?.mes ??
    0
  );

  const hasYear =
    Number.isInteger(year) &&
    year > 0;

  const monthLabel =
    item?.mes_publicacion_label ||
    MONTHS[month] ||
    "";

  if (
    hasYear &&
    monthLabel
  ) {
    return `${monthLabel} ${year}`;
  }

  if (hasYear) {
    return String(year);
  }

  return "Sin período";
};

watch(
  userId,
  async () => {
    user.value = null;
    publications.value = [];

    await refreshAll();
  }
);

onMounted(refreshAll);
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-publicaciones-usuario.css"></style>
<style scoped src="./admin-publicaciones-usuario-stage5.css"></style>
