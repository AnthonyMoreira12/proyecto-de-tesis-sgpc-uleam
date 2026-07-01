import { defineStore } from "pinia";
import {
  scholarSuggest,
  searchScholarPublications,
  listScholarProfiles,
  getScholarProfileDetail,
} from "../api/scholarApi.js";

/* =========================
   Helpers
========================= */
const toStr = (v) => (v == null ? "" : String(v));

const num = (v, d = 0) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : d;
};

const stableKey = (obj) => {
  try {
    const keys = Object.keys(obj || {}).sort();
    const out = {};
    keys.forEach((k) => {
      out[k] = obj[k];
    });
    return JSON.stringify(out);
  } catch {
    return String(Date.now());
  }
};

const uniqueTextList = (items = []) => {
  const seen = new Set();
  const out = [];

  items.forEach((item) => {
    const text = toStr(item).trim();
    if (!text) return;

    const key = text.toLowerCase();
    if (seen.has(key)) return;

    seen.add(key);
    out.push(text);
  });

  return out;
};

const buildFullName = (item) => {
  const direct =
    toStr(item?.name ?? item?.nombre ?? item?.nombre_completo).trim();

  if (direct) return direct;

  const nombres = toStr(item?.nombres).trim();
  const apellidos = toStr(item?.apellidos).trim();
  return [nombres, apellidos].filter(Boolean).join(" ").trim();
};

const extractYear = (item) => {
  const direct = item?.year ?? item?.anio;
  const directNum = Number(direct);

  if (Number.isFinite(directNum) && directNum > 0) {
    return directNum;
  }

  const rawDate = toStr(
    item?.fecha_publicacion ?? item?.published_at ?? item?.date
  ).trim();

  const match = rawDate.match(/^(\d{4})/);
  return match ? Number(match[1]) : null;
};

const composeOrg = (item) => {
  const org = toStr(item?.org ?? item?.afiliacion).trim();
  const facultad = toStr(item?.facultad).trim();
  const carrera = toStr(item?.carrera).trim();

  const parts = uniqueTextList([org, facultad, carrera]);
  return parts.length ? parts.join(" · ") : "Sin afiliación registrada";
};

const normAuthors = (authors) => {
  if (Array.isArray(authors)) {
    const mapped = authors
      .map((item) => ({
        id: item?.id ?? item?.pk ?? item?.user_id ?? null,
        name: buildFullName(item) || "—",
      }))
      .filter((item) => item.name && item.name !== "—");

    return mapped.length ? mapped : "—";
  }

  const text = toStr(authors).trim();
  return text || "—";
};

const normPub = (item) => {
  const title =
    toStr(
      item?.title ??
        item?.titulo ??
        item?.nombre_articulo ??
        item?.nombre_ponencia ??
        item?.nombre_capitulo ??
        item?.nombre_libro ??
        item?.nombre
    ).trim() || "—";

  const tipoCodigo =
    toStr(
      item?.tipo_codigo ??
        item?.type_code ??
        item?.tipo_publicacion_final
    ).trim() || null;

  const tipoLabel =
    toStr(
      item?.tipo_label ??
        item?.tipo_publicacion_final_label ??
        item?.tipo ??
        item?.tipo_publicacion ??
        item?.type
    ).trim() || tipoCodigo || null;

  const authorsSource =
    item?.authors ??
    item?.autores ??
    item?.author_list ??
    item?.autor ??
    null;

  const venue =
    toStr(
      item?.venue ??
        item?.revista ??
        item?.evento ??
        item?.proyecto
    ).trim() || null;

  const sourceParts = uniqueTextList([
    item?.source,
    item?.facultad,
    item?.carrera,
  ]);

  return {
    id: item?.id ?? item?.pk ?? null,
    title,
    authors: normAuthors(authorsSource),
    venue,
    snippet: toStr(item?.snippet ?? item?.resumen ?? item?.descripcion).trim() || "",
    year: extractYear(item),
    tipo_codigo: tipoCodigo,
    tipo_label: tipoLabel,
    source: sourceParts.length ? sourceParts.join(" · ") : null,
    pdf_url: item?.pdf_url ?? item?.archivo_url ?? null,
    hasPdf: !!item?.hasPdf || !!item?.pdf_url || !!item?.archivo_url,
  };
};

const normAuthor = (item) => {
  const publicationsRaw =
    item?.publications ??
    item?.publicaciones ??
    item?.pubs ??
    item?.publicaciones_count;

  const publications = Array.isArray(publicationsRaw)
    ? publicationsRaw.length
    : num(publicationsRaw, 0);

  const baseTags = Array.isArray(item?.tags) ? item.tags : [];
  const extraTags = uniqueTextList([item?.facultad, item?.carrera]);

  return {
    id: item?.id ?? item?.pk ?? null,
    name: buildFullName(item) || "—",
    org: composeOrg(item),
    avatar: item?.avatar ?? item?.avatar_url ?? null,
    publications,
    verified: !!item?.verified,
    tags: uniqueTextList([...baseTags, ...extraTags]),
    es_externo:
      !!item?.es_externo ||
      toStr(item?.rol).trim().toLowerCase() === "autor_externo",
  };
};

const normalizeProfileDetail = (data) => {
  const rawPublications = Array.isArray(data?.publications)
    ? data.publications
    : Array.isArray(data?.publicaciones)
      ? data.publicaciones
      : [];

  return {
    id: data?.id ?? data?.pk ?? null,
    name: buildFullName(data) || "—",
    org: composeOrg(data),
    avatar: data?.avatar ?? data?.avatar_url ?? null,
    verified: !!data?.verified,
    tags: uniqueTextList([
      ...(Array.isArray(data?.tags) ? data.tags : []),
      data?.facultad,
      data?.carrera,
    ]),
    publications: rawPublications.map(normPub),
  };
};

const getRawPublications = (data) => {
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.publicaciones)) return data.publicaciones;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data)) return data;
  return [];
};

const getRawProfiles = (data) => {
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.perfiles)) return data.perfiles;

  const autores = Array.isArray(data?.autores) ? data.autores : [];
  const usuarios = Array.isArray(data?.usuarios) ? data.usuarios : [];

  if (autores.length || usuarios.length) {
    return [...autores, ...usuarios];
  }

  if (Array.isArray(data)) return data;
  return [];
};

const dedupeAuthors = (items) => {
  const seen = new Set();
  const out = [];

  items.forEach((item) => {
    const key = `${item?.id ?? "no-id"}::${toStr(item?.name).trim().toLowerCase()}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push(item);
  });

  return out;
};

const normalizeSuggestionKind = (kind) => {
  const value = toStr(kind).trim().toLowerCase();

  if (
    value.includes("publication") ||
    value.includes("publicacion") ||
    value.includes("paper") ||
    value.includes("article") ||
    value.includes("articulo") ||
    value.includes("work")
  ) {
    return "publication";
  }

  if (
    value.includes("profile") ||
    value.includes("perfil") ||
    value.includes("author") ||
    value.includes("autor") ||
    value.includes("investigador")
  ) {
    return "profile";
  }

  if (value.includes("project") || value.includes("proyecto")) {
    return "project";
  }

  if (
    value.includes("keyword") ||
    value.includes("topic") ||
    value.includes("tema") ||
    value.includes("tag")
  ) {
    return "keyword";
  }

  return "suggestion";
};

export const useScholarStore = defineStore("scholar", {
  state: () => ({
    q: "",

    suggestions: [],
    suggestLoading: false,
    _tSuggest: null,
    _abortSuggest: null,
    _ridSuggest: 0,

    pubs: [],
    pubsTotal: 0,
    pubsFacets: {
      years: [],
      types: [],
    },
    pubsParams: {
      year: "",
      type: "",
      sort: "relevance",
      facets: "1",
      lang: "all",
      author_id: "",
    },
    pubsLoading: false,
    pubsError: null,
    _abortPubs: null,
    _ridPubs: 0,
    _cachePubs: new Map(),

    perfiles: [],
    perfilesCount: 0,
    perfilesPage: 1,
    perfilesPageSize: 10,
    perfilesNext: null,
    perfilesPrev: null,
    perfilesLoading: false,
    perfilesError: null,
    _abortPerfiles: null,
    _ridPerfiles: 0,
    _cachePerfiles: new Map(),

    authorApplied: null,
    authorAppliedLoading: false,
    _abortAuthor: null,
    _ridAuthor: 0,

    perfilDetail: null,
    perfilDetailLoading: false,
    perfilDetailError: null,
    _abortPerfil: null,
    _ridPerfil: 0,
  }),

  getters: {
    hasAnyPubsFilter: (state) =>
      !!(
        state.pubsParams.year ||
        state.pubsParams.type ||
        (state.pubsParams.lang && state.pubsParams.lang !== "all") ||
        state.pubsParams.author_id
      ),

    activePubsFiltersCount: (state) => {
      let count = 0;
      if (state.pubsParams.year) count++;
      if (state.pubsParams.type) count++;
      if (state.pubsParams.lang && state.pubsParams.lang !== "all") count++;
      if (state.pubsParams.author_id) count++;
      return count;
    },
  },

  actions: {
    _cancelSuggestRequest() {
      if (this._tSuggest) clearTimeout(this._tSuggest);
      this._tSuggest = null;

      if (this._abortSuggest) this._abortSuggest.abort();
      this._abortSuggest = null;

      this._ridSuggest += 1;
      this.suggestLoading = false;
    },

    _cancelPubsRequest() {
      if (this._abortPubs) this._abortPubs.abort();
      this._abortPubs = null;

      this._ridPubs += 1;
      this.pubsLoading = false;
    },

    _cancelProfilesRequest() {
      if (this._abortPerfiles) this._abortPerfiles.abort();
      this._abortPerfiles = null;

      this._ridPerfiles += 1;
      this.perfilesLoading = false;
    },

    _cancelAuthorRequest() {
      if (this._abortAuthor) this._abortAuthor.abort();
      this._abortAuthor = null;

      this._ridAuthor += 1;
      this.authorAppliedLoading = false;
    },

    _cancelPerfilRequest() {
      if (this._abortPerfil) this._abortPerfil.abort();
      this._abortPerfil = null;

      this._ridPerfil += 1;
      this.perfilDetailLoading = false;
    },

    setQuery(q) {
      this.q = toStr(q).trim();
    },

    clearSuggestions() {
      this.suggestions = [];
      this._cancelSuggestRequest();
    },

    suggestSmart(q, { debounce = 180, min = 2 } = {}) {
      const query = toStr(q).trim();

      if (query.length < min) {
        this.clearSuggestions();
        return Promise.resolve([]);
      }

      if (this._tSuggest) clearTimeout(this._tSuggest);

      return new Promise((resolve) => {
        this._tSuggest = setTimeout(async () => {
          const result = await this.suggest(query);
          resolve(result || []);
        }, debounce);
      });
    },

    async suggest(q) {
      const query = toStr(q ?? this.q).trim();

      if (query.length < 2) {
        this.clearSuggestions();
        return [];
      }

      this._cancelSuggestRequest();
      const myRequestId = this._ridSuggest;
      this._abortSuggest = new AbortController();
      this.suggestLoading = true;

      try {
        const [smartResult, pubsResult] = await Promise.allSettled([
          scholarSuggest({
            q: query,
            limit: 8,
            signal: this._abortSuggest.signal,
          }),
          searchScholarPublications(
            {
              q: query,
              sort: "relevance",
              facets: "0",
              lang: "all",
              page: 1,
              page_size: 6,
            },
            {
              signal: this._abortSuggest.signal,
            }
          ),
        ]);

        if (myRequestId !== this._ridSuggest) return [];

        const smartRaw =
          smartResult.status === "fulfilled"
            ? Array.isArray(smartResult.value?.suggestions)
              ? smartResult.value.suggestions
              : Array.isArray(smartResult.value?.results)
                ? smartResult.value.results
                : []
            : [];

        const smartNormalized = smartRaw
          .map((item) => ({
            kind: normalizeSuggestionKind(item?.kind || "suggestion"),
            id: item?.id ?? null,
            label: toStr(
              item?.label ??
                item?.titulo ??
                item?.title ??
                item?.nombre ??
                item?.nombre_completo
            ).trim(),
            extra: toStr(
              item?.extra ??
                item?.subtitle ??
                item?.autor ??
                item?.correo
            ).trim(),
          }))
          .filter((item) => item.label);

        const pubsRaw =
          pubsResult.status === "fulfilled"
            ? getRawPublications(pubsResult.value)
            : [];

        const publicationSuggestions = pubsRaw
          .map((item) => {
            const pub = normPub(item);

            const authorsText = Array.isArray(pub.authors)
              ? pub.authors
                  .map((author) => toStr(author?.name).trim())
                  .filter(Boolean)
                  .join(", ")
              : toStr(pub.authors).trim();

            const extra = [authorsText, pub.year, pub.venue]
              .filter((value) => value != null && toStr(value).trim() !== "")
              .map((value) => toStr(value).trim())
              .join(" · ");

            return {
              kind: "publication",
              id: pub.id ?? null,
              label: toStr(pub.title).trim(),
              extra,
            };
          })
          .filter((item) => item.label && item.label !== "—");

        const merged = [];
        const seen = new Set();

        [...smartNormalized, ...publicationSuggestions].forEach((item) => {
          const key = [
            normalizeSuggestionKind(item.kind),
            item.id ?? "no-id",
            toStr(item.label).trim().toLowerCase(),
          ].join("::");

          if (seen.has(key)) return;
          seen.add(key);

          merged.push({
            kind: normalizeSuggestionKind(item.kind),
            id: item.id ?? null,
            label: toStr(item.label).trim(),
            extra: toStr(item.extra).trim(),
          });
        });

        const kindOrder = {
          publication: 0,
          profile: 1,
          project: 2,
          keyword: 3,
          suggestion: 4,
        };

        const normalized = merged
          .sort((a, b) => {
            const ka = kindOrder[a.kind] ?? 99;
            const kb = kindOrder[b.kind] ?? 99;
            if (ka !== kb) return ka - kb;
            return a.label.localeCompare(b.label, "es");
          })
          .slice(0, 10);

        this.suggestions = normalized;
        return normalized;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return [];
        this.suggestions = [];
        return [];
      } finally {
        if (myRequestId === this._ridSuggest) {
          this.suggestLoading = false;
        }
      }
    },

    async searchPublicaciones(input = {}) {
      const query = toStr(input.q ?? this.q).trim();
      this.q = query;

      const params = {
        q: query || "",
        year: toStr(input.year ?? this.pubsParams.year).trim(),
        type: toStr(input.type ?? this.pubsParams.type).trim(),
        sort: toStr(input.sort ?? this.pubsParams.sort ?? "relevance").trim() || "relevance",
        facets: toStr(input.facets ?? this.pubsParams.facets ?? "1").trim() || "1",
        lang: toStr(input.lang ?? this.pubsParams.lang ?? "all").trim() || "all",
        author_id: toStr(input.author_id ?? this.pubsParams.author_id).trim(),
      };

      this.pubsParams = {
        ...this.pubsParams,
        year: params.year,
        type: params.type,
        sort: params.sort,
        facets: params.facets,
        lang: params.lang,
        author_id: params.author_id,
      };

      const cacheKey = stableKey(params);

      this._cancelPubsRequest();
      this.pubsError = null;

      if (this._cachePubs.has(cacheKey)) {
        const cached = this._cachePubs.get(cacheKey);
        this.pubs = cached.pubs;
        this.pubsTotal = cached.total;
        this.pubsFacets = cached.facets;
        return cached.raw;
      }

      const myRequestId = this._ridPubs;
      this._abortPubs = new AbortController();
      this.pubsLoading = true;

      try {
        const data = await searchScholarPublications(
          {
            q: params.q,
            year: params.year,
            type: params.type,
            sort: params.sort,
            facets: params.facets,
            lang: params.lang,
            author_id: params.author_id,
          },
          { signal: this._abortPubs.signal }
        );

        if (myRequestId !== this._ridPubs) return null;

        const raw = getRawPublications(data);
        const pubs = raw.map(normPub);

        this.pubs = pubs;
        this.pubsTotal = num(
          data?.total ?? data?.count ?? data?.publicaciones?.length ?? pubs.length,
          pubs.length
        );
        this.pubsFacets = data?.facets || { years: [], types: [] };

        this._cachePubs.set(cacheKey, {
          pubs,
          total: this.pubsTotal,
          facets: this.pubsFacets,
          raw: data,
        });

        return data;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return null;

        this.pubsError = "No se pudo realizar la búsqueda de publicaciones.";
        this.pubs = [];
        this.pubsTotal = 0;
        this.pubsFacets = { years: [], types: [] };
        throw e;
      } finally {
        if (myRequestId === this._ridPubs) {
          this.pubsLoading = false;
        }
      }
    },

    async searchPerfiles({
      q,
      page = 1,
      pageSize = this.perfilesPageSize,
      preload = "0",
    } = {}) {
      const query = toStr(q ?? this.q).trim();
      this.q = query;

      const shouldPreload = !query && toStr(preload).trim() === "1";

      const params = {
        page: Number(page || 1),
        page_size: Number(pageSize || this.perfilesPageSize || 10),
      };

      if (query) {
        params.q = query;
      } else if (shouldPreload) {
        params.preload = "1";
      }

      const cacheKey = stableKey(params);

      this._cancelProfilesRequest();
      this.perfilesError = null;

      if (this._cachePerfiles.has(cacheKey)) {
        const cached = this._cachePerfiles.get(cacheKey);
        Object.assign(this, cached.state);
        return cached.raw;
      }

      const myRequestId = this._ridPerfiles;
      this._abortPerfiles = new AbortController();
      this.perfilesLoading = true;

      try {
        const data = await listScholarProfiles(params, {
          signal: this._abortPerfiles.signal,
        });

        if (myRequestId !== this._ridPerfiles) return null;

        const raw = getRawProfiles(data);
        const perfiles = dedupeAuthors(raw.map(normAuthor));

        const snapshot = {
          perfiles,
          perfilesCount: num(
            data?.count ??
              data?.total ??
              (Array.isArray(data?.autores) ? data.autores.length : 0) +
                (Array.isArray(data?.usuarios) ? data.usuarios.length : 0),
            perfiles.length
          ),
          perfilesNext: data?.next ?? null,
          perfilesPrev: data?.previous ?? null,
          perfilesPage: params.page,
          perfilesPageSize: params.page_size,
        };

        Object.assign(this, snapshot);

        this._cachePerfiles.set(cacheKey, {
          state: snapshot,
          raw: data,
        });

        return data;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return null;

        this.perfilesError = query
          ? "No se pudo cargar perfiles."
          : "No se pudieron cargar los perfiles sugeridos.";

        this.perfiles = [];
        this.perfilesCount = 0;
        this.perfilesNext = null;
        this.perfilesPrev = null;
        throw e;
      } finally {
        if (myRequestId === this._ridPerfiles) {
          this.perfilesLoading = false;
        }
      }
    },

    async fetchAuthorApplied(authorId) {
      const id = toStr(authorId).trim();

      this._cancelAuthorRequest();

      if (!id) {
        this.authorApplied = null;
        return null;
      }

      if (
        this.authorApplied &&
        String(this.authorApplied.id) === id &&
        !this.authorAppliedLoading
      ) {
        return this.authorApplied;
      }

      const myRequestId = this._ridAuthor;
      this._abortAuthor = new AbortController();
      this.authorAppliedLoading = true;

      try {
        const data = await getScholarProfileDetail(id, {
          signal: this._abortAuthor.signal,
        });

        if (myRequestId !== this._ridAuthor) return null;

        const normalized = normalizeProfileDetail(data || {});
        this.authorApplied = {
          id: normalized.id ?? id,
          name: normalized.name || "—",
          org: normalized.org || "Sin afiliación registrada",
          avatar: normalized.avatar ?? null,
          verified: !!normalized.verified,
        };

        return this.authorApplied;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return null;
        this.authorApplied = null;
        return null;
      } finally {
        if (myRequestId === this._ridAuthor) {
          this.authorAppliedLoading = false;
        }
      }
    },

    async fetchPerfilDetail(id) {
      const authorId = toStr(id).trim();

      this._cancelPerfilRequest();
      this.perfilDetailError = null;

      if (!authorId) {
        this.perfilDetail = null;
        return null;
      }

      const myRequestId = this._ridPerfil;
      this._abortPerfil = new AbortController();
      this.perfilDetailLoading = true;

      try {
        const data = await getScholarProfileDetail(authorId, {
          signal: this._abortPerfil.signal,
        });

        if (myRequestId !== this._ridPerfil) return null;

        this.perfilDetail = normalizeProfileDetail(data || {});
        return this.perfilDetail;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return null;

        this.perfilDetailError = "No se pudo cargar el perfil.";
        this.perfilDetail = null;
        throw e;
      } finally {
        if (myRequestId === this._ridPerfil) {
          this.perfilDetailLoading = false;
        }
      }
    },

    resetPublicacionesState() {
      this._cancelPubsRequest();
      this.pubs = [];
      this.pubsTotal = 0;
      this.pubsFacets = { years: [], types: [] };
      this.pubsError = null;
    },

    resetPerfilesState() {
      this._cancelProfilesRequest();
      this.perfiles = [];
      this.perfilesCount = 0;
      this.perfilesNext = null;
      this.perfilesPrev = null;
      this.perfilesError = null;
    },

    clearPubsCache() {
      this._cachePubs.clear();
    },

    clearProfilesCache() {
      this._cachePerfiles.clear();
    },

    clearDetail() {
      this._cancelPerfilRequest();
      this.perfilDetail = null;
      this.perfilDetailError = null;
      this.perfilDetailLoading = false;
    },

    clearAll() {
      this.q = "";

      this.clearSuggestions();

      this.resetPublicacionesState();
      this.pubsParams = {
        year: "",
        type: "",
        sort: "relevance",
        facets: "1",
        lang: "all",
        author_id: "",
      };
      this.clearPubsCache();

      this.resetPerfilesState();
      this.perfilesPage = 1;
      this.perfilesPageSize = 10;
      this.clearProfilesCache();

      this._cancelAuthorRequest();
      this.authorApplied = null;
      this.authorAppliedLoading = false;

      this.clearDetail();
    },
  },
});