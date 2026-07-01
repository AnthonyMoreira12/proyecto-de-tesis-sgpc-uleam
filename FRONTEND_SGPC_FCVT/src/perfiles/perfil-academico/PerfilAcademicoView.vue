<template>
  <div class="gsp-page">
    <div class="gsp-shell">
      <header v-if="P" class="gsp-profile page-stage page-header">
        <div class="gsp-profile__avatar" aria-hidden="true">
          <img v-if="P.avatar" :src="P.avatar" alt="Foto de perfil" />
          <div v-else class="gsp-profile__avatar-fallback">
            {{ initial }}
          </div>
        </div>

        <div class="gsp-profile__main">
          <p class="gsp-profile__eyebrow">Perfil académico</p>

          <h1 class="gsp-profile__name">
            {{ P.name || "Perfil académico" }}
          </h1>

          <p class="gsp-profile__org">
            {{ P.org || "Sin afiliación registrada" }}
          </p>

          <p v-if="P.verified" class="gsp-profile__verified">
            Dirección de correo verificada
          </p>

          <div class="gsp-profile__meta">
            <span class="gsp-chip">
              Publicaciones: <strong>{{ pubCount }}</strong>
            </span>

            <span v-if="pubsYearRange" class="gsp-chip">
              Años: <strong>{{ pubsYearRange }}</strong>
            </span>

            <span v-if="tagCount" class="gsp-chip">
              Áreas: <strong>{{ tagCount }}</strong>
            </span>
          </div>

          <div class="gsp-profile__actions">
            <button
              v-if="cameFromQuery"
              class="gsp-btn gsp-btn--soft"
              type="button"
              @click="goBackToSearch"
            >
              Volver a búsqueda
            </button>
          </div>

          <div
            v-if="P.tags?.length"
            class="gsp-topics"
            aria-label="Áreas del perfil"
          >
            <span
              v-for="tag in P.tags"
              :key="tag"
              class="gsp-topic"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </header>

      <section v-if="loading" class="gsp-content page-stage">
        <div class="gsp-toolbar gsp-toolbar--loading">
          <div class="gsp-skel gsp-skel--search"></div>
        </div>

        <div class="gsp-results">
          <article
            v-for="n in 5"
            :key="`gsp-loading-${n}`"
            class="gsp-result gsp-result--loading"
          >
            <div class="gsp-skel gsp-skel--badge"></div>
            <div class="gsp-skel gsp-skel--title"></div>
            <div class="gsp-skel gsp-skel--line"></div>
            <div class="gsp-skel gsp-skel--line short"></div>
          </article>
        </div>
      </section>

      <section
        v-else-if="error"
        class="gsp-state gsp-state--error page-main page-stage"
      >
        <p class="gsp-state__title">No se pudo cargar el perfil</p>
        <p class="gsp-state__text">{{ error }}</p>
      </section>

      <section v-else-if="P" class="gsp-content page-stage">
        <div class="gsp-toolbar">
          <div class="gsp-search">
            <label class="sr-only" for="profile-pub-search">
              Buscar publicaciones
            </label>

            <input
              id="profile-pub-search"
              v-model="localQuery"
              class="gsp-input"
              type="search"
              placeholder="Buscar publicaciones"
            />
          </div>
        </div>

        <section
          v-if="filteredPubs.length"
          class="gsp-results"
          aria-label="Publicaciones del autor"
        >
          <article
            v-for="pub in filteredPubs"
            :key="pub.id || `${pub.title}-${pub.year}-${pub.authorsText}`"
            class="gsp-result"
          >
            <div class="gsp-result__meta">
              <div class="gsp-result__badges">
                <span
                  v-if="pub.tipoLabel"
                  class="gsp-result__badge gsp-result__badge--accent"
                >
                  {{ pub.tipoLabel }}
                </span>

                <span v-if="pub.year" class="gsp-result__badge">
                  {{ pub.year }}
                </span>

                <span v-if="pub.hasPdf || pub.pdfUrl" class="gsp-result__badge">
                  PDF
                </span>
              </div>
            </div>

            <div class="gsp-result__body">
              <h3 class="gsp-result__title">
                <button
                  type="button"
                  @click="openPublication(pub.id)"
                  :disabled="!pub.id"
                >
                  {{ pub.title || "Sin título" }}
                </button>
              </h3>

              <p class="gsp-result__authors">
                {{ pub.authorsText || "Autores no disponibles" }}
              </p>

              <p v-if="pub.venue" class="gsp-result__venue">
                {{ pub.venue }}
              </p>

              <div v-if="pub.areaLabel || pub.doi" class="gsp-result__extras">
                <span v-if="pub.areaLabel" class="gsp-inline-tag">
                  {{ pub.areaLabel }}
                </span>

                <span
                  v-if="pub.doi"
                  class="gsp-inline-tag gsp-inline-tag--mono"
                >
                  {{ pub.doi }}
                </span>
              </div>

              <div class="gsp-result__actions">
                <button
                  class="gsp-linkbtn"
                  type="button"
                  @click="openPublication(pub.id)"
                  :disabled="!pub.id"
                >
                  Ver detalle
                </button>
              </div>
            </div>
          </article>
        </section>

        <div v-else class="gsp-state">
          <p class="gsp-state__title">Sin publicaciones para este filtro</p>
          <p class="gsp-state__text">
            Prueba con otro término.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
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

const loading = computed(() => !!store.perfilDetailLoading);
const error = computed(() => store.perfilDetailError || null);
const P = computed(() => store.perfilDetail || null);

const resolvedProfileId = computed(() => String(props.id || "").trim());

const cameFromQuery = computed(() => {
  return String(props.q || route.query.q || "").trim().length > 0;
});

const initial = computed(() => {
  const name = String(P.value?.name || "?").trim();
  return (name.charAt(0) || "?").toUpperCase();
});

const pubs = computed(() => {
  const items = Array.isArray(P.value?.publications) ? P.value.publications : [];

  return items.map((item) => {
    const authorsArray = Array.isArray(item?.authors)
      ? item.authors.map((a) => ({
          id: a?.id ?? null,
          name: String(a?.name ?? a?.nombre ?? "").trim() || "—",
        }))
      : [];

    const authorsText = authorsArray.length
      ? authorsArray.map((a) => a.name).join(", ")
      : String(item?.authors ?? item?.autores ?? "").trim() || "—";

    return {
      id: item?.id ?? null,
      title: String(item?.title ?? item?.titulo ?? "").trim() || "—",
      authors: authorsArray.length ? authorsArray : authorsText,
      authorsText,
      venue: String(
        item?.venue ??
          item?.revista ??
          item?.evento ??
          item?.fuente ??
          item?.source ??
          ""
      ).trim() || null,
      year: item?.year ?? item?.anio ?? null,
      tipoLabel: String(
        item?.tipo_label ??
          item?.tipo ??
          item?.tipo_publicacion ??
          item?.type_label ??
          ""
      ).trim() || null,
      areaLabel: String(item?.area_label ?? item?.area ?? "").trim() || null,
      doi: String(item?.doi ?? "").trim() || null,
      pdfUrl: String(item?.pdf_url ?? item?.archivo_pdf ?? "").trim() || null,
      hasPdf: Boolean(
        item?.hasPdf ?? item?.has_pdf ?? item?.tiene_pdf ?? item?.pdf_url
      ),
    };
  });
});

const pubCount = computed(() => pubs.value.length);

const tagCount = computed(() => {
  return Array.isArray(P.value?.tags) ? P.value.tags.length : 0;
});

const pubsYearRange = computed(() => {
  const years = pubs.value
    .map((item) => Number(item?.year))
    .filter((year) => Number.isFinite(year) && year > 0);

  if (!years.length) return null;

  const min = Math.min(...years);
  const max = Math.max(...years);
  return min === max ? String(min) : `${min}–${max}`;
});

const filteredPubs = computed(() => {
  const q = localQuery.value.trim().toLowerCase();

  const list = pubs.value.filter((item) => {
    if (!q) return true;

    return [
      item.title,
      item.authorsText,
      item.venue,
      item.year,
      item.tipoLabel,
      item.areaLabel,
      item.doi,
    ]
      .map((value) => String(value ?? "").toLowerCase())
      .some((value) => value.includes(q));
  });

  return [...list].sort(
    (a, b) => Number(b?.year || 0) - Number(a?.year || 0)
  );
});

async function fetchDetail() {
  const id = resolvedProfileId.value;

  if (!id) {
    store.perfilDetailError = "Identificador de perfil no válido.";
    return;
  }

  try {
    await store.fetchPerfilDetail(id);
  } catch {
    // el store ya controla el estado de error
  }
}

function goBackToSearch() {
  const q = String(props.q || route.query.q || "").trim();

  router.push({
    path: "/scholar",
    query: q ? { q, scope: "profiles" } : { scope: "profiles" },
  });
}

function openPublication(id) {
  if (!id) return;
  router.push(`/publicacion/${id}`);
}

watch(resolvedProfileId, fetchDetail, { immediate: true });

onBeforeUnmount(() => {
  store.clearDetail?.();
});
</script>

<style src="./perfil-academico.css"></style>