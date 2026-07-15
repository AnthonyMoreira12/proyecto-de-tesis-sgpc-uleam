<template>
  <main class="gsp-page">
    <div class="gsp-shell">
      <!-- =====================================================
           ESTADO DE CARGA
      ====================================================== -->
      <template v-if="loading">
        <section
          class="gsp-profile gsp-profile--loading page-stage page-header"
          aria-label="Cargando perfil académico"
          aria-busy="true"
        >
          <div class="gsp-skeleton gsp-skeleton--avatar"></div>

          <div class="gsp-profile__main">
            <div class="gsp-skeleton gsp-skeleton--eyebrow"></div>
            <div class="gsp-skeleton gsp-skeleton--profile-name"></div>
            <div class="gsp-skeleton gsp-skeleton--organization"></div>

            <div class="gsp-profile__meta">
              <div class="gsp-skeleton gsp-skeleton--chip"></div>
              <div class="gsp-skeleton gsp-skeleton--chip"></div>
              <div class="gsp-skeleton gsp-skeleton--chip"></div>
            </div>
          </div>

          <div class="gsp-profile__stats">
            <div
              v-for="n in 3"
              :key="`profile-stat-loading-${n}`"
              class="gsp-stat"
            >
              <div class="gsp-skeleton gsp-skeleton--stat-label"></div>
              <div class="gsp-skeleton gsp-skeleton--stat-value"></div>
            </div>
          </div>
        </section>

        <section
          class="gsp-publications page-stage page-main"
          aria-label="Cargando publicaciones"
          aria-busy="true"
        >
          <div class="gsp-publications__header">
            <div>
              <div class="gsp-skeleton gsp-skeleton--section-title"></div>
              <div class="gsp-skeleton gsp-skeleton--section-text"></div>
            </div>
          </div>

          <div class="gsp-skeleton gsp-skeleton--search"></div>

          <div class="gsp-results">
            <article
              v-for="n in 5"
              :key="`publication-loading-${n}`"
              class="gsp-result gsp-result--loading"
            >
              <div class="gsp-result__badges">
                <div class="gsp-skeleton gsp-skeleton--badge"></div>
                <div class="gsp-skeleton gsp-skeleton--badge-small"></div>
              </div>

              <div class="gsp-skeleton gsp-skeleton--title"></div>
              <div class="gsp-skeleton gsp-skeleton--line"></div>
              <div class="gsp-skeleton gsp-skeleton--line is-short"></div>
            </article>
          </div>
        </section>
      </template>

      <!-- =====================================================
           ESTADO DE ERROR
      ====================================================== -->
      <section
        v-else-if="error"
        class="gsp-state gsp-state--error page-stage page-main"
        role="alert"
      >
        <span
          class="gsp-state__icon"
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 24 24"
            focusable="false"
          >
            <circle
              cx="12"
              cy="12"
              r="9"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            />

            <path
              d="M12 7.5V13"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />

            <circle
              cx="12"
              cy="16.5"
              r="1"
              fill="currentColor"
            />
          </svg>
        </span>

        <div class="gsp-state__content">
          <h1 class="gsp-state__title">
            No se pudo cargar el perfil
          </h1>

          <p class="gsp-state__text">
            {{ error }}
          </p>

          <div class="gsp-state__actions">
            <button
              class="gsp-btn gsp-btn--primary"
              type="button"
              @click="fetchDetail"
            >
              Intentar nuevamente
            </button>

            <button
              v-if="cameFromQuery"
              class="gsp-btn gsp-btn--secondary"
              type="button"
              @click="goBackToSearch"
            >
              Volver a búsqueda
            </button>
          </div>
        </div>
      </section>

      <!-- =====================================================
           PERFIL
      ====================================================== -->
      <template v-else-if="P">
        <header
          class="gsp-profile page-stage page-header"
          aria-labelledby="academic-profile-name"
        >
          <div class="gsp-profile__avatar">
            <img
              v-if="profileAvatar"
              :src="profileAvatar"
              :alt="`Foto de perfil de ${profileName}`"
              @error="handleAvatarError"
            />

            <div
              v-else
              class="gsp-profile__avatar-fallback"
              aria-hidden="true"
            >
              {{ initial }}
            </div>
          </div>

          <div class="gsp-profile__main">
            <div class="gsp-profile__heading">
              <p class="gsp-profile__eyebrow">
                Perfil académico
              </p>

              <h1
                id="academic-profile-name"
                class="gsp-profile__name"
              >
                {{ profileName }}
              </h1>

              <p class="gsp-profile__org">
                {{ P.org || "Sin afiliación registrada" }}
              </p>
            </div>

            <div
              v-if="P.verified"
              class="gsp-profile__verified"
            >
              <span
                class="gsp-profile__verified-icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 20 20"
                  focusable="false"
                >
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                  />

                  <path
                    d="m6.3 10.1 2.2 2.2 5-5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <span>Correo verificado</span>
            </div>

            <div
              v-if="P.tags?.length"
              class="gsp-topics"
              aria-label="Áreas académicas del perfil"
            >
              <span
                v-for="tag in P.tags"
                :key="tag"
                class="gsp-topic"
              >
                {{ tag }}
              </span>
            </div>

            <div
              v-if="cameFromQuery"
              class="gsp-profile__actions"
            >
              <button
                class="gsp-btn gsp-btn--secondary"
                type="button"
                @click="goBackToSearch"
              >
                <svg
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    d="M15.5 10h-11M8.8 5.7 4.5 10l4.3 4.3"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>

                <span>Volver a búsqueda</span>
              </button>
            </div>
          </div>

          <dl
            class="gsp-profile__stats"
            aria-label="Resumen del perfil académico"
          >
            <div class="gsp-stat">
              <dt class="gsp-stat__label">
                Publicaciones
              </dt>

              <dd class="gsp-stat__value">
                {{ pubCount }}
              </dd>
            </div>

            <div class="gsp-stat">
              <dt class="gsp-stat__label">
                Periodo
              </dt>

              <dd class="gsp-stat__value gsp-stat__value--text">
                {{ pubsYearRange || "Sin datos" }}
              </dd>
            </div>

            <div class="gsp-stat">
              <dt class="gsp-stat__label">
                Áreas
              </dt>

              <dd class="gsp-stat__value">
                {{ tagCount }}
              </dd>
            </div>
          </dl>
        </header>

        <!-- ===================================================
             PUBLICACIONES
        ==================================================== -->
        <section
          class="gsp-publications page-stage page-main"
          aria-labelledby="profile-publications-title"
        >
          <header class="gsp-publications__header">
            <div class="gsp-publications__heading">
              <span class="gsp-publications__label">
                Producción científica
              </span>

              <h2
                id="profile-publications-title"
                class="gsp-publications__title"
              >
                Publicaciones
              </h2>

              <p class="gsp-publications__description">
                Consulte los trabajos registrados para este perfil académico.
              </p>
            </div>

            <div
              class="gsp-publications__count"
              aria-live="polite"
            >
              <strong>{{ filteredPubs.length }}</strong>

              <span>
                {{
                  filteredPubs.length === 1
                    ? "resultado"
                    : "resultados"
                }}
              </span>
            </div>
          </header>

          <div class="gsp-toolbar">
            <div class="gsp-search">
              <span
                class="gsp-search__icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                >
                  <circle
                    cx="10.5"
                    cy="10.5"
                    r="6.5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />

                  <path
                    d="m15.5 15.5 5 5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />
                </svg>
              </span>

              <label
                class="sr-only"
                for="profile-pub-search"
              >
                Buscar en las publicaciones del perfil
              </label>

              <input
                id="profile-pub-search"
                v-model="localQuery"
                class="gsp-input"
                type="search"
                placeholder="Buscar por título, autor, año, tipo, área o DOI"
                autocomplete="off"
              />

              <button
                v-if="localQuery"
                class="gsp-search__clear"
                type="button"
                aria-label="Limpiar búsqueda"
                title="Limpiar búsqueda"
                @click="clearFilter"
              >
                <svg
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    d="M5 5l10 10M15 5 5 15"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div
            v-if="filteredPubs.length"
            class="gsp-results"
            aria-label="Publicaciones del autor"
          >
            <article
              v-for="pub in filteredPubs"
              :key="
                pub.id ||
                `${pub.title}-${pub.year}-${pub.authorsText}`
              "
              class="gsp-result"
              :class="{
                'has-pdf': pub.hasPdf || pub.pdfUrl,
              }"
            >
              <div class="gsp-result__accent"></div>

              <div class="gsp-result__content">
                <div class="gsp-result__badges">
                  <span
                    v-if="pub.tipoLabel"
                    class="gsp-result__badge gsp-result__badge--accent"
                  >
                    {{ pub.tipoLabel }}
                  </span>

                  <span
                    v-if="pub.year"
                    class="gsp-result__badge"
                  >
                    {{ pub.year }}
                  </span>

                  <span
                    v-if="pub.hasPdf || pub.pdfUrl"
                    class="gsp-result__badge gsp-result__badge--pdf"
                  >
                    <svg
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <path
                        d="M5 2.5h6l4 4v11H5v-15Zm6 0v4h4"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linejoin="round"
                      />
                    </svg>

                    <span>PDF</span>
                  </span>
                </div>

                <div class="gsp-result__body">
                  <h3 class="gsp-result__title">
                    <button
                      type="button"
                      :disabled="!pub.id"
                      @click="openPublication(pub.id)"
                    >
                      {{ pub.title || "Sin título" }}
                    </button>
                  </h3>

                  <div class="gsp-result__details">
                    <p class="gsp-result__authors">
                      <span
                        class="gsp-result__detail-icon"
                        aria-hidden="true"
                      >
                        <svg
                          viewBox="0 0 20 20"
                          focusable="false"
                        >
                          <circle
                            cx="10"
                            cy="6.5"
                            r="3"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                          />

                          <path
                            d="M4.5 16c.5-3 2.6-4.5 5.5-4.5s5 1.5 5.5 4.5"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                          />
                        </svg>
                      </span>

                      <span>
                        {{
                          pub.authorsText ||
                          "Autores no disponibles"
                        }}
                      </span>
                    </p>

                    <p
                      v-if="pub.venue"
                      class="gsp-result__venue"
                    >
                      <span
                        class="gsp-result__detail-icon"
                        aria-hidden="true"
                      >
                        <svg
                          viewBox="0 0 20 20"
                          focusable="false"
                        >
                          <path
                            d="M4 3.5h12v13H4v-13Zm3 3h6M7 9.5h6M7 12.5h4"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                        </svg>
                      </span>

                      <span>{{ pub.venue }}</span>
                    </p>
                  </div>

                  <div
                    v-if="pub.areaLabel || pub.doi"
                    class="gsp-result__extras"
                  >
                    <span
                      v-if="pub.areaLabel"
                      class="gsp-inline-tag"
                    >
                      {{ pub.areaLabel }}
                    </span>

                    <span
                      v-if="pub.doi"
                      class="gsp-inline-tag gsp-inline-tag--mono"
                      :title="pub.doi"
                    >
                      DOI: {{ pub.doi }}
                    </span>
                  </div>
                </div>

                <div class="gsp-result__actions">
                  <button
                    class="gsp-linkbtn"
                    type="button"
                    :disabled="!pub.id"
                    @click="openPublication(pub.id)"
                  >
                    <span>Ver detalle</span>

                    <svg
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <path
                        d="M4.5 10h11M11.2 5.7l4.3 4.3-4.3 4.3"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </article>
          </div>

          <!-- =================================================
               SIN RESULTADOS
          ================================================== -->
          <div
            v-else
            class="gsp-state gsp-state--empty"
          >
            <span
              class="gsp-state__icon"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                focusable="false"
              >
                <circle
                  cx="10.5"
                  cy="10.5"
                  r="6.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />

                <path
                  d="m15.5 15.5 5 5M8 10.5h5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div class="gsp-state__content">
              <h3 class="gsp-state__title">
                {{
                  localQuery
                    ? "No se encontraron coincidencias"
                    : "Este perfil no tiene publicaciones"
                }}
              </h3>

              <p class="gsp-state__text">
                {{
                  localQuery
                    ? "Pruebe con otro título, autor, año, área o DOI."
                    : "Las publicaciones registradas aparecerán en esta sección."
                }}
              </p>

              <button
                v-if="localQuery"
                class="gsp-btn gsp-btn--secondary"
                type="button"
                @click="clearFilter"
              >
                Limpiar búsqueda
              </button>
            </div>
          </div>
        </section>
      </template>

      <!-- =====================================================
           PERFIL NO DISPONIBLE
      ====================================================== -->
      <section
        v-else
        class="gsp-state page-stage page-main"
      >
        <span
          class="gsp-state__icon"
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 24 24"
            focusable="false"
          >
            <circle
              cx="12"
              cy="8"
              r="4"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
            />

            <path
              d="M4.5 20c.7-4.3 3.5-6.5 7.5-6.5s6.8 2.2 7.5 6.5"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
          </svg>
        </span>

        <div class="gsp-state__content">
          <h1 class="gsp-state__title">
            Perfil no disponible
          </h1>

          <p class="gsp-state__text">
            No se encontró información académica para este perfil.
          </p>

          <button
            v-if="cameFromQuery"
            class="gsp-btn gsp-btn--secondary"
            type="button"
            @click="goBackToSearch"
          >
            Volver a búsqueda
          </button>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import { useScholarStore } from "../../scripts/stores/scholarStore";

const props = defineProps({
  id: {
    type: String,
    default: "",
  },

  q: {
    type: String,
    default: "",
  },
});

const route = useRoute();
const router = useRouter();
const store = useScholarStore();

const localQuery = ref("");
const avatarBroken = ref(false);

const loading = computed(() => {
  return Boolean(store.perfilDetailLoading);
});

const error = computed(() => {
  return store.perfilDetailError || null;
});

const P = computed(() => {
  return store.perfilDetail || null;
});

const resolvedProfileId = computed(() => {
  return String(props.id || "").trim();
});

const profileName = computed(() => {
  return String(
    P.value?.name ||
    P.value?.nombre ||
    "Perfil académico"
  ).trim();
});

const profileAvatar = computed(() => {
  if (avatarBroken.value) {
    return null;
  }

  const avatar = String(
    P.value?.avatar ||
    P.value?.avatar_url ||
    P.value?.foto ||
    ""
  ).trim();

  return avatar || null;
});

const cameFromQuery = computed(() => {
  return String(
    props.q ||
    route.query.q ||
    ""
  ).trim().length > 0;
});

const initial = computed(() => {
  const name = profileName.value.trim();

  return (
    name
      .split(/\s+/)
      .find(Boolean)
      ?.charAt(0)
      ?.toUpperCase() ||
    "?"
  );
});

const pubs = computed(() => {
  const items = Array.isArray(
    P.value?.publications
  )
    ? P.value.publications
    : [];

  return items.map((item) => {
    const authorsArray = Array.isArray(
      item?.authors
    )
      ? item.authors.map((author) => ({
          id:
            author?.id ??
            null,

          name:
            String(
              author?.name ??
              author?.nombre ??
              ""
            ).trim() ||
            "—",
        }))
      : [];

    const authorsText =
      authorsArray.length
        ? authorsArray
            .map((author) => author.name)
            .join(", ")
        : String(
            item?.authors ??
            item?.autores ??
            ""
          ).trim() ||
          "—";

    return {
      id:
        item?.id ??
        null,

      title:
        String(
          item?.title ??
          item?.titulo ??
          ""
        ).trim() ||
        "Sin título",

      authors:
        authorsArray.length
          ? authorsArray
          : authorsText,

      authorsText,

      venue:
        String(
          item?.venue ??
          item?.revista ??
          item?.evento ??
          item?.fuente ??
          item?.source ??
          ""
        ).trim() ||
        null,

      year:
        item?.year ??
        item?.anio ??
        null,

      tipoLabel:
        String(
          item?.tipo_label ??
          item?.tipo ??
          item?.tipo_publicacion ??
          item?.type_label ??
          ""
        ).trim() ||
        null,

      areaLabel:
        String(
          item?.area_label ??
          item?.area ??
          ""
        ).trim() ||
        null,

      doi:
        String(
          item?.doi ??
          ""
        ).trim() ||
        null,

      pdfUrl:
        String(
          item?.pdf_url ??
          item?.archivo_pdf ??
          ""
        ).trim() ||
        null,

      hasPdf:
        Boolean(
          item?.hasPdf ??
          item?.has_pdf ??
          item?.tiene_pdf ??
          item?.pdf_url
        ),
    };
  });
});

const pubCount = computed(() => {
  return pubs.value.length;
});

const tagCount = computed(() => {
  return Array.isArray(P.value?.tags)
    ? P.value.tags.length
    : 0;
});

const pubsYearRange = computed(() => {
  const years = pubs.value
    .map((item) => Number(item?.year))
    .filter(
      (year) =>
        Number.isFinite(year) &&
        year > 0
    );

  if (!years.length) {
    return null;
  }

  const minimum = Math.min(...years);
  const maximum = Math.max(...years);

  return minimum === maximum
    ? String(minimum)
    : `${minimum}–${maximum}`;
});

const filteredPubs = computed(() => {
  const query = localQuery.value
    .trim()
    .toLowerCase();

  const filtered = pubs.value.filter(
    (item) => {
      if (!query) {
        return true;
      }

      return [
        item.title,
        item.authorsText,
        item.venue,
        item.year,
        item.tipoLabel,
        item.areaLabel,
        item.doi,
      ]
        .map((value) =>
          String(value ?? "")
            .toLowerCase()
        )
        .some((value) =>
          value.includes(query)
        );
    }
  );

  return [...filtered].sort(
    (a, b) =>
      Number(b?.year || 0) -
      Number(a?.year || 0)
  );
});

async function fetchDetail() {
  const id = resolvedProfileId.value;

  if (!id) {
    store.perfilDetailError =
      "El identificador del perfil no es válido.";

    return;
  }

  avatarBroken.value = false;

  try {
    await store.fetchPerfilDetail(id);
  } catch {
    // El store administra el estado de error.
  }
}

function handleAvatarError() {
  avatarBroken.value = true;
}

function clearFilter() {
  localQuery.value = "";
}

function goBackToSearch() {
  const query = String(
    props.q ||
    route.query.q ||
    ""
  ).trim();

  router.push({
    path: "/busqueda",

    query: query
      ? {
          q: query,
          scope: "profiles",
        }
      : {
          scope: "profiles",
        },
  });
}

function openPublication(id) {
  if (!id) {
    return;
  }

  router.push({
    name: "PublicacionDetalle",

    params: {
      id,
    },
  });
}

watch(
  resolvedProfileId,
  fetchDetail,
  {
    immediate: true,
  }
);

watch(
  () => P.value,
  () => {
    avatarBroken.value = false;
    localQuery.value = "";
  }
);

onBeforeUnmount(() => {
  store.clearDetail?.();
});
</script>

<style src="./perfil-academico.css"></style>