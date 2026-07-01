<template>
  <div class="sch-page">
    <main class="sch-shell">
      <template v-if="hasSearched">
        <section
          class="sch-querybar page-summary page-stage"
          aria-label="Resumen de resultados"
        >
          <div class="sch-querybar__copy">
            <p class="sch-querybar__eyebrow">{{ scopeLabel }}</p>

            <h1 class="sch-querybar__title">
              {{ queryHeading }}
            </h1>

            <p class="sch-querybar__meta">{{ queryMeta }}</p>
          </div>

          <div class="sch-segment" role="tablist" aria-label="Tipo de resultados">
            <button
              class="sch-segment__btn"
              type="button"
              role="tab"
              :aria-selected="activeScope === 'pubs'"
              :class="{ active: activeScope === 'pubs' }"
              @click="handleScopeClick('pubs')"
            >
              Publicaciones
            </button>

            <button
              class="sch-segment__btn"
              type="button"
              role="tab"
              :aria-selected="activeScope === 'profiles'"
              :class="{ active: activeScope === 'profiles' }"
              @click="handleScopeClick('profiles')"
            >
              Investigadores
            </button>
          </div>
        </section>

        <section
          v-if="activeScope === 'pubs'"
          class="sch-controls page-toolbar page-stage"
          aria-label="Controles de resultados"
        >
          <div class="sch-control">
            <label class="sch-label" for="scholar-sort">Ordenar</label>
            <select
              id="scholar-sort"
              class="sch-select"
              :value="state.sort"
              @change="setParam('sort', $event.target.value)"
            >
              <option value="relevance">Relevancia</option>
              <option value="year_desc">Más recientes</option>
              <option value="year_asc">Más antiguas</option>
              <option value="title_asc">Título A–Z</option>
            </select>
          </div>

          <div class="sch-control">
            <label class="sch-label" for="scholar-year">Año</label>
            <select
              id="scholar-year"
              class="sch-select"
              :value="state.year"
              @change="setParam('year', $event.target.value)"
            >
              <option value="">Todos</option>
              <option
                v-for="item in yearFacets"
                :key="item.value"
                :value="item.value"
              >
                {{ item.label }}
              </option>
            </select>
          </div>

          <div class="sch-control">
            <label class="sch-label" for="scholar-type">Tipo</label>
            <select
              id="scholar-type"
              class="sch-select"
              :value="state.type"
              @change="setParam('type', $event.target.value)"
            >
              <option value="">Todos</option>
              <option
                v-for="item in typeFacets"
                :key="item.value"
                :value="item.value"
              >
                {{ item.label }}
              </option>
            </select>
          </div>

          <label class="sch-toggle">
            <input
              type="checkbox"
              :checked="state.hasPdf === '1'"
              @change="setParam('has_pdf', $event.target.checked ? '1' : '')"
            />
            <span>Solo con PDF</span>
          </label>
        </section>

        <section
          v-if="authorContext && activeScope === 'pubs'"
          class="sch-authorstrip page-summary page-stage"
          aria-label="Autor aplicado"
        >
          <div class="sch-authorstrip__main">
            <div class="sch-avatar sch-avatar--md">
              <img
                v-if="authorContext.avatar"
                :src="authorContext.avatar"
                alt="Foto del autor"
              />
              <div v-else class="sch-avatar__fallback">
                {{ (authorContext.name || '?').charAt(0).toUpperCase() }}
              </div>
            </div>

            <div class="sch-authorstrip__copy">
              <p class="sch-authorstrip__eyebrow">Autor aplicado</p>
              <h3 class="sch-authorstrip__name">
                {{ authorContext.name || "Autor" }}
              </h3>
              <p class="sch-authorstrip__org">
                {{ authorContext.org || "Sin afiliación registrada" }}
              </p>
            </div>
          </div>

          <div class="sch-actions">
            <button
              class="sch-btn sch-btn--ghost"
              type="button"
              @click="openProfile(authorContext.id)"
            >
              Ver perfil
            </button>

            <button
              class="sch-btn sch-btn--ghost"
              type="button"
              @click="clearAuthor"
            >
              Quitar
            </button>
          </div>
        </section>

        <div
          v-if="activeFilterChips.length && activeScope === 'pubs'"
          class="sch-chips page-chips page-stage"
          aria-label="Filtros activos"
        >
          <button
            v-for="chip in activeFilterChips"
            :key="chip.key"
            class="sch-chip"
            type="button"
            @click="chip.onRemove()"
          >
            {{ chip.label }}
          </button>
        </div>

        <section
          v-if="activeScope === 'pubs'"
          class="sch-results page-content page-stage"
          aria-label="Resultados de publicaciones"
        >
          <div v-if="store.pubsError" class="sch-state sch-state--error">
            <p class="sch-state__title">No se pudo completar la búsqueda</p>
            <p class="sch-state__text">{{ store.pubsError }}</p>
          </div>

          <div v-else-if="store.pubsLoading" class="sch-loading" aria-hidden="true">
            <div v-for="n in 5" :key="`pub-load-${n}`" class="sch-loading__item"></div>
          </div>

          <div
            v-else-if="resultsList.length"
            class="sch-list page-stagger page-stagger--mid"
          >
            <article
              v-for="r in resultsList"
              :key="r.id"
              class="sch-result sch-result--line"
            >
              <div class="sch-result__side">
                <span v-if="r.year" class="sch-meta sch-meta--year">{{ r.year }}</span>
              </div>

              <div class="sch-result__body">
                <div class="sch-result__badges">
                  <span v-if="r.tipo_label" class="sch-pill sch-pill--accent">
                    {{ r.tipo_label }}
                  </span>
                  <span v-if="r.hasPdf || r.pdf_url" class="sch-pill">PDF</span>
                </div>

                <h3 class="sch-result__title">
                  <button type="button" @click="openPublication(r.id)">
                    {{ r.title || "—" }}
                  </button>
                </h3>

                <div class="sch-result__meta">
                  <template v-if="Array.isArray(r.authors)">
                    <template
                      v-for="(a, i) in r.authors"
                      :key="a.id || `${a.name}-${i}`"
                    >
                      <button
                        class="sch-linkbtn"
                        type="button"
                        @click="openAuthorFromResults(a)"
                      >
                        {{ a.name }}
                      </button>
                      <span v-if="i < r.authors.length - 1">, </span>
                    </template>
                  </template>
                  <span v-else>{{ r.authors || "—" }}</span>

                  <span v-if="r.source"> · {{ r.source }}</span>
                  <span v-if="r.venue"> · {{ r.venue }}</span>
                </div>

                <p v-if="r.snippet" class="sch-result__snippet">
                  {{ r.snippet }}
                </p>

                <div class="sch-result__footer">
                  <div class="sch-result__tags">
                    <span v-if="r.doi" class="sch-pill">{{ r.doi }}</span>
                    <span v-if="r.area_label" class="sch-pill">{{ r.area_label }}</span>
                  </div>

                  <div class="sch-actions">
                    <button
                      v-if="r.pdf_url"
                      class="sch-textbtn"
                      type="button"
                      @click="openPdf(r.pdf_url)"
                    >
                      Abrir PDF
                    </button>

                    <button
                      class="sch-textbtn"
                      type="button"
                      @click="openPublication(r.id)"
                    >
                      Ver detalle
                    </button>
                  </div>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="sch-state">
            <p class="sch-state__title">Sin publicaciones encontradas</p>
            <p class="sch-state__text">Ajusta la consulta o los filtros aplicados.</p>
          </div>
        </section>

        <section
          v-else
          class="sch-results page-content page-stage"
          aria-label="Resultados de investigadores"
        >
          <div v-if="store.perfilesError" class="sch-state sch-state--error">
            <p class="sch-state__title">No se pudieron cargar los investigadores</p>
            <p class="sch-state__text">{{ store.perfilesError }}</p>
          </div>

          <div
            v-else-if="store.perfilesLoading"
            class="sch-loading"
            aria-hidden="true"
          >
            <div
              v-for="n in 4"
              :key="`profile-load-${n}`"
              class="sch-loading__item"
            ></div>
          </div>

          <div
            v-else-if="profilesList.length"
            class="sch-list page-stagger page-stagger--mid"
          >
            <article
              v-for="p in profilesList"
              :key="p.id"
              class="sch-profile sch-profile--line"
            >
              <div class="sch-profile__main">
                <div class="sch-avatar sch-avatar--md">
                  <img v-if="p.avatar" :src="p.avatar" alt="Foto del investigador" />
                  <div v-else class="sch-avatar__fallback">
                    {{ (p.name?.charAt(0) || "U").toUpperCase() }}
                  </div>
                </div>

                <div class="sch-profile__body">
                  <h3 class="sch-profile__name">
                    <button type="button" @click="openProfile(p.id)">
                      {{ p.name || "—" }}
                    </button>
                  </h3>

                  <p class="sch-profile__org">
                    {{ p.org || "Sin afiliación registrada" }}
                  </p>

                  <p class="sch-profile__meta">
                    <span v-if="p.publications != null">
                      {{ pluralize(p.publications, "publicación", "publicaciones") }}
                    </span>
                    <span v-if="p.es_externo"> · autor externo</span>
                  </p>
                </div>
              </div>

              <div class="sch-actions">
                <button
                  class="sch-textbtn"
                  type="button"
                  @click="openProfile(p.id)"
                >
                  Ver perfil
                </button>
              </div>
            </article>
          </div>

          <div v-else class="sch-state">
            <p class="sch-state__title">Sin investigadores encontrados</p>
            <p class="sch-state__text">No hay perfiles relacionados con esta consulta.</p>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useScholarStore } from "../../scripts/stores/scholarStore";
import { useUserStore } from "../../scripts/stores/userStore";

const PERFILES_PAGE_SIZE = 8;

const store = useScholarStore();
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

const activeScope = ref("pubs");
const userSelectedScope = ref(false);
const nextSearchPreferredScope = ref("");
const requestSerial = ref(0);

const buildSearchKey = ({ q = "", authorId = "" } = {}) =>
  JSON.stringify({
    q: String(q || "").trim(),
    authorId: String(authorId || "").trim(),
  });

const myAuthorId = computed(() =>
  String(
    userStore.autorId ??
      userStore.user?.autor_id ??
      userStore.user?.author_id ??
      ""
  ).trim()
);

const state = computed(() => ({
  q: String(route.query.q || "").trim(),
  authorId: String(route.query.author_id || "").trim(),
  year: String(route.query.year || "").trim(),
  type: String(route.query.type || "").trim(),
  sort: String(route.query.sort || "relevance").trim() || "relevance",
  hasPdf: String(route.query.has_pdf || "").trim(),
}));

const currentSearchKey = computed(() =>
  buildSearchKey({
    q: state.value.q,
    authorId: state.value.authorId,
  })
);

const rawResultsList = computed(() =>
  Array.isArray(store.pubs) ? store.pubs : []
);

const resultsList = computed(() => {
  const items = rawResultsList.value;

  if (state.value.hasPdf === "1") {
    return items.filter((item) => Boolean(item?.hasPdf || item?.pdf_url));
  }

  return items;
});

const profilesList = computed(() =>
  Array.isArray(store.perfiles) ? store.perfiles : []
);

const authorContext = computed(() => store.authorApplied || null);

const hasSearched = computed(() =>
  Boolean(state.value.q || state.value.authorId)
);

const profilesSearchText = computed(() => {
  if (state.value.q) return state.value.q;
  return String(authorContext.value?.name || "").trim();
});

const pubsCountView = computed(() => {
  if (state.value.hasPdf === "1") {
    return resultsList.value.length;
  }
  return Number(store.pubsTotal ?? resultsList.value.length ?? 0);
});

const profilesCountView = computed(() =>
  Number(store.perfilesCount ?? profilesList.value.length ?? 0)
);

const fmt = (value) => {
  try {
    return Number(value || 0).toLocaleString("es-EC");
  } catch {
    return String(value || 0);
  }
};

const pluralize = (value, singular, plural) => {
  const count = Number(value || 0);
  return `${fmt(count)} ${count === 1 ? singular : plural}`;
};

const resultSummary = computed(() => {
  if (activeScope.value === "profiles") {
    return pluralize(profilesCountView.value, "investigador", "investigadores");
  }
  return pluralize(pubsCountView.value, "publicación", "publicaciones");
});

const scopeLabel = computed(() =>
  activeScope.value === "profiles" ? "Investigadores" : "Publicaciones"
);

const queryHeading = computed(() => {
  if (activeScope.value === "profiles") {
    if (profilesSearchText.value) {
      return `“${profilesSearchText.value}”`;
    }
    return "Investigadores";
  }

  if (state.value.authorId && authorContext.value?.name) {
    return authorContext.value.name;
  }

  if (state.value.q) {
    return `“${state.value.q}”`;
  }

  return "Publicaciones";
});

const queryMeta = computed(() => {
  if (
    state.value.authorId &&
    authorContext.value?.name &&
    activeScope.value === "pubs"
  ) {
    return `Resultados del autor · ${resultSummary.value}`;
  }

  return resultSummary.value;
});

const typeFacets = computed(() => {
  const fromApi = Array.isArray(store.pubsFacets?.types)
    ? store.pubsFacets.types
    : null;

  if (fromApi?.length) {
    return fromApi
      .map((item) => {
        if (typeof item === "string") {
          return { value: item, label: item, count: null };
        }

        return {
          value: String(item.value ?? item.codigo ?? "").trim(),
          label: String(item.label ?? item.nombre ?? item.value ?? "").trim(),
          count: item.count ?? null,
        };
      })
      .filter((item) => item.value);
  }

  const map = new Map();

  rawResultsList.value.forEach((pub) => {
    const code = String(pub?.tipo_codigo || "").trim();
    if (!code) return;

    if (!map.has(code)) {
      map.set(code, {
        value: code,
        label: String(pub?.tipo_label || code).trim() || code,
        count: 0,
      });
    }

    map.get(code).count += 1;
  });

  return [...map.values()].sort((a, b) =>
    a.label.localeCompare(b.label, "es")
  );
});

const yearFacets = computed(() => {
  const fromApi = Array.isArray(store.pubsFacets?.years)
    ? store.pubsFacets.years
    : null;

  if (fromApi?.length) {
    return fromApi
      .map((item) => {
        if (typeof item === "string" || typeof item === "number") {
          const value = String(item);
          return { label: value, value, count: null };
        }

        const value = String(item.value ?? item.year ?? "").trim();
        return {
          label: String(item.label ?? value).trim(),
          value,
          count: item.count ?? null,
        };
      })
      .filter((item) => item.value);
  }

  const map = new Map();

  rawResultsList.value.forEach((pub) => {
    const year = Number(pub?.year);
    if (!Number.isFinite(year) || year < 1900) return;
    map.set(year, (map.get(year) || 0) + 1);
  });

  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .slice(0, 20)
    .map(([year, count]) => ({
      label: String(year),
      value: String(year),
      count,
    }));
});

const selectedTypeLabel = computed(() => {
  const code = state.value.type;
  if (!code) return "";
  const match = typeFacets.value.find((item) => item.value === code);
  return match?.label || code;
});

const activeFilterChips = computed(() => {
  const chips = [];

  if (state.value.year) {
    chips.push({
      key: "year",
      label: `Año: ${state.value.year}`,
      onRemove: () => setParam("year", ""),
    });
  }

  if (state.value.type) {
    chips.push({
      key: "type",
      label: `Tipo: ${selectedTypeLabel.value}`,
      onRemove: () => setParam("type", ""),
    });
  }

  if (state.value.hasPdf === "1") {
    chips.push({
      key: "has_pdf",
      label: "Solo con PDF",
      onRemove: () => setParam("has_pdf", ""),
    });
  }

  if (state.value.authorId) {
    chips.push({
      key: "author_id",
      label: `Autor: ${authorContext.value?.name || "aplicado"}`,
      onRemove: () => clearAuthor(),
    });
  }

  return chips;
});

const getVisiblePubsFound = () => resultsList.value.length;

const getProfilesFound = () => {
  const total = Number(
    store.perfilesCount ??
      (Array.isArray(store.perfiles) ? store.perfiles.length : 0)
  );
  return Number.isFinite(total) ? total : 0;
};

const setQuery = (patch = {}) => {
  const next = {
    ...route.query,
    ...patch,
  };

  delete next.scope;
  delete next.tab;

  Object.keys(next).forEach((key) => {
    const value = next[key];
    if (value == null || String(value).trim() === "") {
      delete next[key];
    }
  });

  router.push({
    path: "/scholar",
    query: next,
  });
};

const setParam = (key, value) => {
  setQuery({
    [key]: String(value ?? "").trim() || undefined,
  });
};

const handleScopeClick = (scope) => {
  activeScope.value = scope === "profiles" ? "profiles" : "pubs";
  userSelectedScope.value = true;
};

const clearAuthor = () => {
  nextSearchPreferredScope.value = "";
  userSelectedScope.value = false;
  activeScope.value = "pubs";

  setParam("author_id", "");
};

const openProfile = (id) => {
  const sid = String(id || "").trim();
  if (!sid) return;

  if (myAuthorId.value && sid === myAuthorId.value) {
    router.push("/perfil/me");
    return;
  }

  router.push({
    path: `/perfil/${sid}`,
    query: state.value.q ? { q: state.value.q } : {},
  });
};

const openAuthorFromResults = (author) => {
  if (author?.id) {
    openProfile(author.id);
    return;
  }

  const name = String(author?.name || "").trim();
  if (!name) return;

  nextSearchPreferredScope.value = "profiles";
  activeScope.value = "profiles";
  userSelectedScope.value = true;

  setQuery({
    q: name,
    author_id: undefined,
  });
};

const openPublication = (id) => {
  const sid = String(id || "").trim();
  if (!sid) return;
  router.push(`/publicacion/${sid}`);
};

const openPdf = (url) => {
  if (!url) return;
  window.open(url, "_blank", "noopener,noreferrer");
};

const isStaleRequest = (id) => id !== requestSerial.value;

watch(
  currentSearchKey,
  (next, prev) => {
    if (prev === undefined) return;
    if (next === prev) return;

    if (nextSearchPreferredScope.value) {
      activeScope.value = nextSearchPreferredScope.value;
      userSelectedScope.value = true;
      nextSearchPreferredScope.value = "";
      return;
    }

    activeScope.value = "pubs";
    userSelectedScope.value = false;
  },
  { immediate: true }
);

const runSearch = async () => {
  const runId = ++requestSerial.value;
  const s = state.value;

  try {
    if (!hasSearched.value) {
      activeScope.value = "pubs";
      userSelectedScope.value = false;
      nextSearchPreferredScope.value = "";
      store.resetPublicacionesState?.();
      store.resetPerfilesState?.();
      await store.fetchAuthorApplied?.(null);
      return;
    }

    let profileQuery = String(s.q || "").trim();

    if (s.authorId) {
      await store.fetchAuthorApplied?.(s.authorId);
      if (isStaleRequest(runId)) return;

      if (!profileQuery) {
        profileQuery = String(store.authorApplied?.name || "").trim();
      }
    } else {
      await store.fetchAuthorApplied?.(null);
      if (isStaleRequest(runId)) return;
    }

    const tasks = [
      store.searchPublicaciones?.({
        q: s.q || "",
        year: s.year || "",
        type: s.type || "",
        sort: s.sort || "relevance",
        facets: "1",
        author_id: s.authorId || "",
      }),
    ];

    if (profileQuery) {
      tasks.push(
        store.searchPerfiles?.({
          q: profileQuery,
          page: 1,
          pageSize: store.perfilesPageSize || PERFILES_PAGE_SIZE,
          preload: "0",
        })
      );
    } else {
      store.resetPerfilesState?.();
    }

    await Promise.all(tasks);
    if (isStaleRequest(runId)) return;

    if (!userSelectedScope.value) {
      const pubsFound = getVisiblePubsFound();
      const profilesFound = getProfilesFound();

      if (pubsFound > 0) {
        activeScope.value = "pubs";
      } else if (profilesFound > 0) {
        activeScope.value = "profiles";
      } else {
        activeScope.value = "pubs";
      }
    }
  } catch {
    if (isStaleRequest(runId)) return;
  }
};

watch(
  () => route.query,
  () => {
    runSearch();
  },
  { deep: true, immediate: true }
);
</script>

<style src="./busqueda.css"></style>