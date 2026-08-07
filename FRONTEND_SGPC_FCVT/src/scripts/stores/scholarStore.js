import { defineStore } from "pinia";

import {
  getScholarProfileDetail,
  listScholarProfiles,
  scholarSuggest,
  searchScholarPublications,
  updateScholarMyProfile,
} from "../api/scholarApi.js";


/* ==========================================================
   CONFIGURACIÓN
========================================================== */

const CACHE_MAX_ENTRIES = 30;
const CACHE_TTL_MS = 5 * 60 * 1000;

const DEFAULT_PUBLICATIONS_PAGE_SIZE = 10;
const DEFAULT_PROFILES_PAGE_SIZE = 10;


/* ==========================================================
   HELPERS GENERALES
========================================================== */

const toStr = (
  value
) => (
  value == null
    ? ""
    : String(value)
);

const num = (
  value,
  defaultValue = 0
) => {
  const parsedValue =
    Number(value);

  return Number.isFinite(
    parsedValue
  )
    ? parsedValue
    : defaultValue;
};

const positiveInteger = (
  value,
  defaultValue = 1
) => {
  const parsedValue =
    Math.trunc(
      num(
        value,
        defaultValue
      )
    );

  return parsedValue > 0
    ? parsedValue
    : defaultValue;
};

const toBool = (
  value
) => {
  if (
    typeof value
    === "boolean"
  ) {
    return value;
  }

  if (
    value == null
    || value === ""
  ) {
    return false;
  }

  const normalized =
    toStr(
      value
    )
      .trim()
      .toLowerCase();

  return [
    "1",
    "true",
    "t",
    "yes",
    "y",
    "si",
    "sí",
    "on",
  ].includes(
    normalized
  );
};

const normalizeBinaryFilter = (
  value
) => (
  toBool(value)
    ? "1"
    : ""
);

const stableKey = (
  object
) => {
  try {
    const keys =
      Object.keys(
        object || {}
      ).sort();

    const output = {};

    keys.forEach(
      (key) => {
        output[key] =
          object[key];
      }
    );

    return JSON.stringify(
      output
    );
  } catch {
    return String(
      Date.now()
    );
  }
};

const uniqueTextList = (
  items = []
) => {
  const seen =
    new Set();

  const output = [];

  items.forEach(
    (item) => {
      const text =
        toStr(
          item
        ).trim();

      if (
        !text
      ) {
        return;
      }

      const key =
        text.toLowerCase();

      if (
        seen.has(
          key
        )
      ) {
        return;
      }

      seen.add(
        key
      );

      output.push(
        text
      );
    }
  );

  return output;
};

const buildFullName = (
  item
) => {
  const directName =
    toStr(
      item?.name
      ?? item?.nombre
      ?? item?.nombre_completo
    ).trim();

  if (
    directName
  ) {
    return directName;
  }

  const names =
    toStr(
      item?.nombres
    ).trim();

  const surnames =
    toStr(
      item?.apellidos
    ).trim();

  return [
    names,
    surnames,
  ]
    .filter(
      Boolean
    )
    .join(" ")
    .trim();
};

const extractYear = (
  item
) => {
  const value =
    item?.anio_publicacion
    ?? item?.year
    ?? item?.anio;

  const parsed =
    Number(
      value
    );

  return (
    Number.isFinite(
      parsed
    )
    && parsed > 0
  )
    ? parsed
    : null;
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


const extractMonth = (
  item
) => {
  const value =
    item?.mes_publicacion
    ?? item?.month
    ?? item?.mes;

  if (
    value == null
    || value === ""
  ) {
    return null;
  }

  const parsed =
    Number(
      value
    );

  return (
    Number.isInteger(
      parsed
    )
    && parsed >= 1
    && parsed <= 12
  )
    ? parsed
    : null;
};


const extractMonthLabel = (
  item,
  month = extractMonth(item)
) => {
  const direct =
    toStr(
      item?.mes_publicacion_label
      ?? item?.month_label
      ?? item?.mes_label
    ).trim();

  if (
    direct
  ) {
    return direct;
  }

  return month
    ? (
        MONTH_LABELS[month]
        || null
      )
    : null;
};


const buildPeriodLabel = (
  item
) => {
  const year =
    extractYear(
      item
    );

  const month =
    extractMonth(
      item
    );

  const monthLabel =
    extractMonthLabel(
      item,
      month
    );

  if (
    year
    && monthLabel
  ) {
    return `${monthLabel} de ${year}`;
  }

  if (
    year
  ) {
    return String(year);
  }

  return monthLabel
    || null;
};


const composeOrg = (
  item
) => {
  const organization =
    toStr(
      item?.org
      ?? item?.afiliacion
      ?? item?.institucion
    ).trim();

  const faculty =
    toStr(
      item?.facultad
    ).trim();

  const career =
    toStr(
      item?.carrera
    ).trim();

  const parts =
    uniqueTextList([
      organization,
      faculty,
      career,
    ]);

  return parts.length
    ? parts.join(" · ")
    : "Sin afiliación registrada";
};

const extractErrorMessage = (
  error,
  fallback
) => {
  const detail =
    error?.response?.data?.detail
    ?? error?.response?.data?.message
    ?? error?.message;

  if (
    Array.isArray(
      detail
    )
  ) {
    const joined =
      detail
        .map(
          (item) => toStr(item).trim()
        )
        .filter(
          Boolean
        )
        .join(" ");

    return joined
      || fallback;
  }

  const normalized =
    toStr(
      detail
    ).trim();

  return normalized
    || fallback;
};


/* ==========================================================
   CACHÉ CONTROLADA
========================================================== */

const getCacheEntry = (
  cache,
  key
) => {
  if (
    !(cache instanceof Map)
  ) {
    return null;
  }

  const entry =
    cache.get(
      key
    );

  if (
    !entry
  ) {
    return null;
  }

  const createdAt =
    num(
      entry.createdAt,
      0
    );

  if (
    !createdAt
    || (
      Date.now()
      - createdAt
    ) > CACHE_TTL_MS
  ) {
    cache.delete(
      key
    );

    return null;
  }

  /*
   * Reinserta el elemento para que el Map funcione como una
   * caché LRU sencilla.
   */
  cache.delete(
    key
  );

  cache.set(
    key,
    entry
  );

  return entry.value;
};

const setCacheEntry = (
  cache,
  key,
  value
) => {
  if (
    !(cache instanceof Map)
  ) {
    return;
  }

  if (
    cache.has(
      key
    )
  ) {
    cache.delete(
      key
    );
  }

  cache.set(
    key,
    {
      createdAt:
        Date.now(),
      value,
    }
  );

  while (
    cache.size
    > CACHE_MAX_ENTRIES
  ) {
    const oldestKey =
      cache
        .keys()
        .next()
        .value;

    cache.delete(
      oldestKey
    );
  }
};


/* ==========================================================
   NORMALIZACIÓN DE AUTORES DE PUBLICACIÓN
========================================================== */

const normAuthors = (
  authors
) => {
  if (
    Array.isArray(
      authors
    )
  ) {
    const mapped =
      authors
        .map(
          (
            item,
            index
          ) => {
            const order =
              positiveInteger(
                item?.order
                ?? item?.orden,
                index + 1
              );

            return {
              id: (
                item?.autor_id
                ?? item?.id
                ?? item?.pk
                ?? item?.user_id
                ?? null
              ),

              autor_id: (
                item?.autor_id
                ?? item?.id
                ?? item?.pk
                ?? null
              ),

              name: (
                buildFullName(
                  item
                )
                || "—"
              ),

              order,

              orden:
                order,

              es_externo:
                toBool(
                  item?.es_externo
                ),
            };
          }
        )
        .filter(
          (item) => (
            item.name
            && item.name !== "—"
          )
        )
        .sort(
          (
            first,
            second
          ) => (
            first.order
            - second.order
          )
        );

    return mapped.length
      ? mapped
      : "—";
  }

  const text =
    toStr(
      authors
    ).trim();

  return text
    || "—";
};


/* ==========================================================
   NORMALIZACIÓN DE PUBLICACIONES
========================================================== */

const normPub = (
  item
) => {
  const title = (
    toStr(
      item?.title
      ?? item?.titulo
      ?? item?.nombre_articulo
      ?? item?.nombre_ponencia
      ?? item?.nombre_capitulo
      ?? item?.nombre_libro
      ?? item?.nombre
    ).trim()
    || "—"
  );

  const typeCode = (
    toStr(
      item?.tipo_codigo
      ?? item?.type_code
      ?? item?.tipo_publicacion_final
    ).trim()
    || null
  );

  const typeLabel = (
    toStr(
      item?.tipo_label
      ?? item?.tipo_publicacion_final_label
      ?? item?.tipo
      ?? item?.tipo_publicacion
      ?? item?.type
    ).trim()
    || typeCode
    || null
  );

  const authorsSource = (
    item?.authors
    ?? item?.autores
    ?? item?.author_list
    ?? item?.autor
    ?? null
  );

  const venue = (
    toStr(
      item?.venue
      ?? item?.revista
      ?? item?.evento
      ?? item?.editorial
      ?? item?.proyecto
    ).trim()
    || null
  );

  const sourceParts =
    uniqueTextList([
      item?.source,
      item?.proyecto,
      item?.facultad,
      item?.carrera,
    ]);

  const pdfUrl = (
    item?.pdf_url
    ?? item?.archivo_pdf_url
    ?? item?.archivo_url
    ?? null
  );

  const hasPdf =
    toBool(
      item?.hasPdf
      ?? item?.has_pdf
      ?? item?.tiene_pdf
    )
    || Boolean(
      pdfUrl
    );

  const areaLabel = (
    toStr(
      item?.area_label
      ?? item?.area
    ).trim()
    || null
  );

  const year =
    extractYear(
      item
    );

  const month =
    extractMonth(
      item
    );

  const monthLabel =
    extractMonthLabel(
      item,
      month
    );

  const periodLabel =
    buildPeriodLabel(
      item
    );

  return {
    id:
      item?.id
      ?? item?.pk
      ?? null,

    title,

    authors:
      normAuthors(
        authorsSource
      ),

    venue,

    snippet: (
      toStr(
        item?.snippet
        ?? item?.resumen
        ?? item?.descripcion
      ).trim()
      || ""
    ),

    year,

    anio_publicacion:
      year,

    month,

    mes_publicacion:
      month,

    month_label:
      monthLabel,

    mes_publicacion_label:
      monthLabel,

    period_label:
      periodLabel,

    tipo_codigo:
      typeCode,

    tipo_label:
      typeLabel,

    area_label:
      areaLabel,

    source: (
      sourceParts.length
        ? sourceParts.join(" · ")
        : null
    ),

    proyecto: (
      toStr(
        item?.proyecto
      ).trim()
      || null
    ),

    facultad: (
      toStr(
        item?.facultad
      ).trim()
      || null
    ),

    carrera: (
      toStr(
        item?.carrera
      ).trim()
      || null
    ),

    doi: (
      toStr(
        item?.doi
      ).trim()
      || null
    ),

    external_url: (
      toStr(
        item?.external_url
      ).trim()
      || null
    ),

    pdf_url:
      pdfUrl,

    archivo_pdf_url:
      pdfUrl,

    hasPdf,

    has_pdf:
      hasPdf,

    tiene_pdf:
      hasPdf,
  };
};


/* ==========================================================
   NORMALIZACIÓN DE INVESTIGADORES
========================================================== */

const normalizeAcademicIdentifiers = (
  item
) => {
  const nested = (
    item?.academic_identifiers
    && typeof item.academic_identifiers
      === "object"
  )
    ? item.academic_identifiers
    : {};

  return {
    orcid:
      toStr(
        item?.orcid
        ?? nested?.orcid
      ).trim()
      || null,

    registro_senescyt:
      toStr(
        item?.registro_senescyt
        ?? nested?.registro_senescyt
      ).trim()
      || null,

    google_scholar:
      toStr(
        item?.google_scholar
        ?? nested?.google_scholar
      ).trim()
      || null,

    scopus_id:
      toStr(
        item?.scopus_id
        ?? nested?.scopus_id
      ).trim()
      || null,
  };
};


const normAuthor = (
  item
) => {
  const publicationsRaw = (
    item?.publications
    ?? item?.publicaciones
    ?? item?.pubs
    ?? item?.publicaciones_count
  );

  const publications =
    Array.isArray(
      publicationsRaw
    )
      ? publicationsRaw.length
      : num(
          publicationsRaw,
          0
        );

  const baseTags =
    Array.isArray(
      item?.tags
    )
      ? item.tags
      : [];

  const extraTags =
    uniqueTextList([
      item?.facultad,
      item?.carrera,
      item?.area,
      item?.area_label,
    ]);

  const userState = (
    toStr(
      item?.usuario_estado
    ).trim()
    || (
      toBool(
        item?.usuario_pendiente
      )
        ? "pendiente"
        : (
          toBool(
            item?.usuario_activo
          )
            ? "activo"
            : "sin_usuario"
        )
    )
  );

  const authorId = (
    item?.autor_id
    ?? item?.id
    ?? item?.pk
    ?? null
  );

  const academicIdentifiers =
    normalizeAcademicIdentifiers(
      item
    );

  return {
    id:
      authorId,

    autor_id:
      authorId,

    name: (
      buildFullName(
        item
      )
      || "—"
    ),

    org:
      composeOrg(
        item
      ),

    avatar: (
      item?.avatar
      ?? item?.avatar_url
      ?? null
    ),

    publications,

    academic_identifiers:
      academicIdentifiers,

    orcid:
      academicIdentifiers.orcid,

    registro_senescyt:
      academicIdentifiers
        .registro_senescyt,

    google_scholar:
      academicIdentifiers
        .google_scholar,

    scopus_id:
      academicIdentifiers
        .scopus_id,

    verified:
      toBool(
        item?.verified
      ),

    tags:
      uniqueTextList([
        ...baseTags,
        ...extraTags,
      ]),

    es_externo: (
      toBool(
        item?.es_externo
      )
      || (
        toStr(
          item?.rol
        )
          .trim()
          .toLowerCase()
        === "autor_externo"
      )
    ),

    usuario_activo:
      toBool(
        item?.usuario_activo
      ),

    usuario_pendiente:
      toBool(
        item?.usuario_pendiente
      ),

    usuario_estado:
      userState,

    perfil_disponible: (
      item?.perfil_disponible
      !== false
      && Boolean(
        authorId
      )
    ),
  };
};

const normalizeProfileDetail = (
  data
) => {
  const rawPublications =
    Array.isArray(
      data?.publications
    )
      ? data.publications
      : (
        Array.isArray(
          data?.publicaciones
        )
          ? data.publicaciones
          : []
      );

  const normalizedAuthor =
    normAuthor(
      data || {}
    );

  const relatedAuthorsRaw = (
    Array.isArray(
      data?.related_authors
    )
      ? data.related_authors
      : (
          Array.isArray(
            data?.autores_relacionados
          )
            ? data.autores_relacionados
            : (
                Array.isArray(
                  data?.coauthors
                )
                  ? data.coauthors
                  : []
              )
        )
  );

  const relatedAuthors =
    dedupeAuthors(
      relatedAuthorsRaw.map(
        normAuthor
      )
    );

  return {
    ...normalizedAuthor,

    publications:
      rawPublications.map(
        normPub
      ),

    related_authors:
      relatedAuthors,

    autores_relacionados:
      relatedAuthors,
  };
};


/* ==========================================================
   EXTRACCIÓN DE COLECCIONES
========================================================== */

const getRawPublications = (
  data
) => {
  if (
    Array.isArray(
      data?.results
    )
  ) {
    return data.results;
  }

  if (
    Array.isArray(
      data?.publicaciones
    )
  ) {
    return data.publicaciones;
  }

  if (
    Array.isArray(
      data?.items
    )
  ) {
    return data.items;
  }

  if (
    Array.isArray(
      data
    )
  ) {
    return data;
  }

  return [];
};

const getRawProfiles = (
  data
) => {
  if (
    Array.isArray(
      data?.results
    )
  ) {
    return data.results;
  }

  if (
    Array.isArray(
      data?.investigadores
    )
  ) {
    return data.investigadores;
  }

  if (
    Array.isArray(
      data?.perfiles
    )
  ) {
    return data.perfiles;
  }

  const authors =
    Array.isArray(
      data?.autores
    )
      ? data.autores
      : [];

  const users =
    Array.isArray(
      data?.usuarios
    )
      ? data.usuarios
      : [];

  if (
    authors.length
    || users.length
  ) {
    return [
      ...authors,
      ...users,
    ];
  }

  if (
    Array.isArray(
      data
    )
  ) {
    return data;
  }

  return [];
};


/* ==========================================================
   DEDUPLICACIÓN DE INVESTIGADORES
========================================================== */

const dedupeAuthors = (
  items
) => {
  const byKey =
    new Map();

  items.forEach(
    (item) => {
      const id =
        item?.autor_id
        ?? item?.id
        ?? null;

      const normalizedName =
        toStr(
          item?.name
        )
          .trim()
          .toLowerCase();

      const normalizedOrg =
        toStr(
          item?.org
        )
          .trim()
          .toLowerCase();

      const key = (
        id != null
          ? `autor:${id}`
          : (
            `name:${normalizedName}`
            + `::org:${normalizedOrg}`
          )
      );

      const existing =
        byKey.get(
          key
        );

      if (
        !existing
      ) {
        byKey.set(
          key,
          item
        );

        return;
      }

      byKey.set(
        key,
        {
          ...existing,
          ...item,

          avatar: (
            item?.avatar
            || existing?.avatar
            || null
          ),

          publications:
            Math.max(
              num(
                existing?.publications,
                0
              ),
              num(
                item?.publications,
                0
              )
            ),

          verified: (
            Boolean(
              existing?.verified
            )
            || Boolean(
              item?.verified
            )
          ),

          tags:
            uniqueTextList([
              ...(
                Array.isArray(
                  existing?.tags
                )
                  ? existing.tags
                  : []
              ),
              ...(
                Array.isArray(
                  item?.tags
                )
                  ? item.tags
                  : []
              ),
            ]),

          perfil_disponible: (
            existing?.perfil_disponible
            !== false
            || item?.perfil_disponible
            !== false
          ),
        }
      );
    }
  );

  return Array.from(
    byKey.values()
  ).filter(
    (item) => (
      item?.id != null
      && item?.perfil_disponible
      !== false
    )
  );
};


/* ==========================================================
   SUGERENCIAS
========================================================== */

const normalizeSuggestionKind = (
  kind
) => {
  const value =
    toStr(
      kind
    )
      .trim()
      .toLowerCase();

  if (
    value.includes(
      "publication"
    )
    || value.includes(
      "publicacion"
    )
    || value.includes(
      "paper"
    )
    || value.includes(
      "article"
    )
    || value.includes(
      "articulo"
    )
    || value.includes(
      "work"
    )
  ) {
    return "publication";
  }

  if (
    value.includes(
      "profile"
    )
    || value.includes(
      "perfil"
    )
    || value.includes(
      "author"
    )
    || value.includes(
      "autor"
    )
    || value.includes(
      "investigador"
    )
  ) {
    return "profile";
  }

  if (
    value.includes(
      "project"
    )
    || value.includes(
      "proyecto"
    )
  ) {
    return "project";
  }

  if (
    value.includes(
      "keyword"
    )
    || value.includes(
      "topic"
    )
    || value.includes(
      "tema"
    )
    || value.includes(
      "tag"
    )
  ) {
    return "keyword";
  }

  return "suggestion";
};


/* ==========================================================
   FACETAS
========================================================== */

const normalizeFacets = (
  facets
) => {
  const value =
    facets
    && typeof facets === "object"
      ? facets
      : {};

  return {
    years:
      Array.isArray(
        value.years
      )
        ? value.years
        : [],

    types:
      Array.isArray(
        value.types
      )
        ? value.types
        : [],

    months:
      Array.isArray(
        value.months
      )
        ? value.months
        : [],
  };
};


/* ==========================================================
   STORE
========================================================== */

export const useScholarStore =
  defineStore(
    "scholar",
    {
      state: () => ({
        q: "",

        suggestions: [],
        suggestLoading: false,
        _tSuggest: null,
        _resolveSuggestDebounce: null,
        _abortSuggest: null,
        _ridSuggest: 0,

        pubs: [],
        pubsTotal: 0,
        pubsFacets: {
          years: [],
          types: [],
          months: [],
        },
        pubsParams: {
          year: "",
          month: "",
          type: "",
          sort: "relevance",
          facets: "1",
          lang: "all",
          author_id: "",
          has_pdf: "",
        },
        pubsPage: 1,
        pubsPageSize:
          DEFAULT_PUBLICATIONS_PAGE_SIZE,
        pubsNext: null,
        pubsPrev: null,
        pubsLoading: false,
        pubsError: null,
        _abortPubs: null,
        _ridPubs: 0,
        _cachePubs: new Map(),

        perfiles: [],
        perfilesCount: 0,
        perfilesPage: 1,
        perfilesPageSize:
          DEFAULT_PROFILES_PAGE_SIZE,
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
        hasAnyPubsFilter: (
          state
        ) => Boolean(
          state.pubsParams.year
          || state.pubsParams.month
          || state.pubsParams.type
          || (
            state.pubsParams.lang
            && state.pubsParams.lang
            !== "all"
          )
          || state.pubsParams.author_id
          || state.pubsParams.has_pdf
        ),

        activePubsFiltersCount: (
          state
        ) => {
          let count = 0;

          if (
            state.pubsParams.year
          ) {
            count += 1;
          }

          if (
            state.pubsParams.month
          ) {
            count += 1;
          }

          if (
            state.pubsParams.type
          ) {
            count += 1;
          }

          if (
            state.pubsParams.lang
            && state.pubsParams.lang
            !== "all"
          ) {
            count += 1;
          }

          if (
            state.pubsParams.author_id
          ) {
            count += 1;
          }

          if (
            state.pubsParams.has_pdf
          ) {
            count += 1;
          }

          return count;
        },

        pubsHasNext: (
          state
        ) => Boolean(
          state.pubsNext
        ),

        pubsHasPrevious: (
          state
        ) => Boolean(
          state.pubsPrev
        ),

        perfilesHasNext: (
          state
        ) => Boolean(
          state.perfilesNext
        ),

        perfilesHasPrevious: (
          state
        ) => Boolean(
          state.perfilesPrev
        ),
      },

      actions: {
        /* ==================================================
           CANCELACIÓN DE SOLICITUDES
        ================================================== */

        _cancelSuggestDebounce() {
          if (
            this._tSuggest
          ) {
            clearTimeout(
              this._tSuggest
            );
          }

          this._tSuggest = null;

          if (
            typeof this
              ._resolveSuggestDebounce
            === "function"
          ) {
            this
              ._resolveSuggestDebounce(
                []
              );
          }

          this._resolveSuggestDebounce =
            null;
        },

        _cancelSuggestRequest() {
          this
            ._cancelSuggestDebounce();

          if (
            this._abortSuggest
          ) {
            this
              ._abortSuggest
              .abort();
          }

          this._abortSuggest =
            null;

          this._ridSuggest += 1;
          this.suggestLoading = false;
        },

        _cancelPubsRequest() {
          if (
            this._abortPubs
          ) {
            this
              ._abortPubs
              .abort();
          }

          this._abortPubs =
            null;

          this._ridPubs += 1;
          this.pubsLoading = false;
        },

        _cancelProfilesRequest() {
          if (
            this._abortPerfiles
          ) {
            this
              ._abortPerfiles
              .abort();
          }

          this._abortPerfiles =
            null;

          this._ridPerfiles += 1;
          this.perfilesLoading = false;
        },

        _cancelAuthorRequest() {
          if (
            this._abortAuthor
          ) {
            this
              ._abortAuthor
              .abort();
          }

          this._abortAuthor =
            null;

          this._ridAuthor += 1;
          this.authorAppliedLoading =
            false;
        },

        _cancelPerfilRequest() {
          if (
            this._abortPerfil
          ) {
            this
              ._abortPerfil
              .abort();
          }

          this._abortPerfil =
            null;

          this._ridPerfil += 1;
          this.perfilDetailLoading =
            false;
        },

        /* ==================================================
           CONSULTA
        ================================================== */

        setQuery(
          query
        ) {
          this.q =
            toStr(
              query
            ).trim();
        },

        /* ==================================================
           SUGERENCIAS
        ================================================== */

        clearSuggestions() {
          this
            ._cancelSuggestRequest();

          this.suggestions = [];
        },

        suggestSmart(
          queryValue,
          {
            debounce = 180,
            min = 2,
          } = {}
        ) {
          const query =
            toStr(
              queryValue
            ).trim();

          this
            ._cancelSuggestRequest();

          if (
            query.length < min
          ) {
            this.suggestions = [];

            return Promise.resolve(
              []
            );
          }

          return new Promise(
            (resolve) => {
              this._resolveSuggestDebounce =
                resolve;

              this._tSuggest =
                setTimeout(
                  async () => {
                    const pendingResolve =
                      this
                        ._resolveSuggestDebounce;

                    this._resolveSuggestDebounce =
                      null;

                    this._tSuggest =
                      null;

                    const result =
                      await this.suggest(
                        query
                      );

                    if (
                      typeof pendingResolve
                      === "function"
                    ) {
                      pendingResolve(
                        result || []
                      );
                    }
                  },
                  debounce
                );
            }
          );
        },

        async suggest(
          queryValue
        ) {
          const query =
            toStr(
              queryValue
              ?? this.q
            ).trim();

          if (
            query.length < 2
          ) {
            this
              .clearSuggestions();

            return [];
          }

          this
            ._cancelSuggestRequest();

          const myRequestId =
            this._ridSuggest;

          this._abortSuggest =
            new AbortController();

          this.suggestLoading =
            true;

          try {
            const [
              smartResult,
              publicationsResult,
            ] = await Promise.allSettled([
              scholarSuggest({
                q: query,
                limit: 8,
                signal:
                  this
                    ._abortSuggest
                    .signal,
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
                  signal:
                    this
                      ._abortSuggest
                      .signal,
                }
              ),
            ]);

            if (
              myRequestId
              !== this._ridSuggest
            ) {
              return [];
            }

            const smartRaw = (
              smartResult.status
              === "fulfilled"
                ? (
                  Array.isArray(
                    smartResult
                      .value
                      ?.suggestions
                  )
                    ? smartResult
                        .value
                        .suggestions
                    : (
                      Array.isArray(
                        smartResult
                          .value
                          ?.results
                      )
                        ? smartResult
                            .value
                            .results
                        : []
                    )
                )
                : []
            );

            const smartNormalized =
              smartRaw
                .map(
                  (item) => ({
                    kind:
                      normalizeSuggestionKind(
                        item?.kind
                        || "suggestion"
                      ),

                    id:
                      item?.id
                      ?? null,

                    label:
                      toStr(
                        item?.label
                        ?? item?.titulo
                        ?? item?.title
                        ?? item?.nombre
                        ?? item?.nombre_completo
                      ).trim(),

                    extra:
                      toStr(
                        item?.extra
                        ?? item?.subtitle
                        ?? item?.autor
                        ?? ""
                      ).trim(),
                  })
                )
                .filter(
                  (item) => (
                    item.label
                  )
                );

            const publicationsRaw = (
              publicationsResult.status
              === "fulfilled"
                ? getRawPublications(
                    publicationsResult.value
                  )
                : []
            );

            const publicationSuggestions =
              publicationsRaw
                .map(
                  (item) => {
                    const publication =
                      normPub(
                        item
                      );

                    const authorsText =
                      Array.isArray(
                        publication.authors
                      )
                        ? publication
                            .authors
                            .map(
                              (author) => (
                                toStr(
                                  author?.name
                                ).trim()
                              )
                            )
                            .filter(
                              Boolean
                            )
                            .join(", ")
                        : toStr(
                            publication.authors
                          ).trim();

                    const extra = [
                      authorsText,
                      publication.period_label
                      || publication.year,
                      publication.venue,
                    ]
                      .filter(
                        (value) => (
                          value != null
                          && toStr(
                            value
                          ).trim() !== ""
                        )
                      )
                      .map(
                        (value) => (
                          toStr(
                            value
                          ).trim()
                        )
                      )
                      .join(" · ");

                    return {
                      kind:
                        "publication",

                      id:
                        publication.id
                        ?? null,

                      label:
                        toStr(
                          publication.title
                        ).trim(),

                      extra,
                    };
                  }
                )
                .filter(
                  (item) => (
                    item.label
                    && item.label !== "—"
                  )
                );

            const merged = [];
            const seen = new Set();

            [
              ...smartNormalized,
              ...publicationSuggestions,
            ].forEach(
              (item) => {
                const key = [
                  normalizeSuggestionKind(
                    item.kind
                  ),
                  item.id
                  ?? "no-id",
                  toStr(
                    item.label
                  )
                    .trim()
                    .toLowerCase(),
                ].join("::");

                if (
                  seen.has(
                    key
                  )
                ) {
                  return;
                }

                seen.add(
                  key
                );

                merged.push({
                  kind:
                    normalizeSuggestionKind(
                      item.kind
                    ),

                  id:
                    item.id
                    ?? null,

                  label:
                    toStr(
                      item.label
                    ).trim(),

                  extra:
                    toStr(
                      item.extra
                    ).trim(),
                });
              }
            );

            const kindOrder = {
              publication: 0,
              profile: 1,
              project: 2,
              keyword: 3,
              suggestion: 4,
            };

            const normalized =
              merged
                .sort(
                  (
                    first,
                    second
                  ) => {
                    const firstOrder =
                      kindOrder[
                        first.kind
                      ]
                      ?? 99;

                    const secondOrder =
                      kindOrder[
                        second.kind
                      ]
                      ?? 99;

                    if (
                      firstOrder
                      !== secondOrder
                    ) {
                      return (
                        firstOrder
                        - secondOrder
                      );
                    }

                    return (
                      first
                        .label
                        .localeCompare(
                          second.label,
                          "es"
                        )
                    );
                  }
                )
                .slice(
                  0,
                  10
                );

            this.suggestions =
              normalized;

            return normalized;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return [];
            }

            this.suggestions = [];

            return [];
          } finally {
            if (
              myRequestId
              === this._ridSuggest
            ) {
              this.suggestLoading =
                false;
            }
          }
        },

        /* ==================================================
           PUBLICACIONES
        ================================================== */

        async searchPublicaciones(
          input = {}
        ) {
          const query =
            toStr(
              input.q
              ?? this.q
            ).trim();

          this.q = query;

          const params = {
            q:
              query
              || "",

            year:
              toStr(
                input.year
                ?? this
                  .pubsParams
                  .year
              ).trim(),

            month:
              toStr(
                input.month
                ?? input.mes
                ?? this
                  .pubsParams
                  .month
              ).trim(),

            type:
              toStr(
                input.type
                ?? this
                  .pubsParams
                  .type
              ).trim(),

            sort: (
              toStr(
                input.sort
                ?? this
                  .pubsParams
                  .sort
                ?? "relevance"
              ).trim()
              || "relevance"
            ),

            facets: (
              toStr(
                input.facets
                ?? this
                  .pubsParams
                  .facets
                ?? "1"
              ).trim()
              || "1"
            ),

            lang: (
              toStr(
                input.lang
                ?? this
                  .pubsParams
                  .lang
                ?? "all"
              ).trim()
              || "all"
            ),

            author_id:
              toStr(
                input.author_id
                ?? this
                  .pubsParams
                  .author_id
              ).trim(),

            has_pdf:
              normalizeBinaryFilter(
                input.has_pdf
                ?? input.hasPdf
                ?? this
                  .pubsParams
                  .has_pdf
              ),

            page:
              positiveInteger(
                input.page,
                1
              ),

            page_size:
              positiveInteger(
                input.page_size
                ?? input.pageSize,
                this.pubsPageSize
                || DEFAULT_PUBLICATIONS_PAGE_SIZE
              ),
          };

          this.pubsParams = {
            ...this.pubsParams,

            year:
              params.year,

            month:
              params.month,

            type:
              params.type,

            sort:
              params.sort,

            facets:
              params.facets,

            lang:
              params.lang,

            author_id:
              params.author_id,

            has_pdf:
              params.has_pdf,
          };

          const cacheKey =
            stableKey(
              params
            );

          this
            ._cancelPubsRequest();

          this.pubsError =
            null;

          const cached =
            getCacheEntry(
              this._cachePubs,
              cacheKey
            );

          if (
            cached
          ) {
            this.pubs =
              cached.pubs;

            this.pubsTotal =
              cached.total;

            this.pubsFacets =
              cached.facets;

            this.pubsPage =
              cached.page;

            this.pubsPageSize =
              cached.pageSize;

            this.pubsNext =
              cached.next;

            this.pubsPrev =
              cached.previous;

            return cached.raw;
          }

          const myRequestId =
            this._ridPubs;

          this._abortPubs =
            new AbortController();

          this.pubsLoading =
            true;

          try {
            const data =
              await searchScholarPublications(
                {
                  q:
                    params.q,

                  year:
                    params.year,

                  month:
                    params.month,

                  type:
                    params.type,

                  sort:
                    params.sort,

                  facets:
                    params.facets,

                  lang:
                    params.lang,

                  author_id:
                    params.author_id,

                  has_pdf:
                    params.has_pdf,

                  page:
                    params.page,

                  page_size:
                    params.page_size,
                },
                {
                  signal:
                    this
                      ._abortPubs
                      .signal,
                }
              );

            if (
              myRequestId
              !== this._ridPubs
            ) {
              return null;
            }

            const raw =
              getRawPublications(
                data
              );

            const publications =
              raw.map(
                normPub
              );

            const total =
              num(
                data?.total
                ?? data?.count
                ?? publications.length,
                publications.length
              );

            const facets =
              normalizeFacets(
                data?.facets
              );

            const snapshot = {
              pubs:
                publications,

              total,

              facets,

              page:
                positiveInteger(
                  data?.page
                  ?? params.page,
                  params.page
                ),

              pageSize:
                positiveInteger(
                  data?.page_size
                  ?? data?.pageSize
                  ?? params.page_size,
                  params.page_size
                ),

              next:
                data?.next
                ?? null,

              previous:
                data?.previous
                ?? data?.prev
                ?? null,

              raw:
                data,
            };

            this.pubs =
              snapshot.pubs;

            this.pubsTotal =
              snapshot.total;

            this.pubsFacets =
              snapshot.facets;

            this.pubsPage =
              snapshot.page;

            this.pubsPageSize =
              snapshot.pageSize;

            this.pubsNext =
              snapshot.next;

            this.pubsPrev =
              snapshot.previous;

            setCacheEntry(
              this._cachePubs,
              cacheKey,
              snapshot
            );

            return data;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return null;
            }

            this.pubsError =
              extractErrorMessage(
                error,
                (
                  "No se pudo realizar "
                  + "la búsqueda de publicaciones."
                )
              );

            this.pubs = [];
            this.pubsTotal = 0;
            this.pubsFacets = {
              years: [],
              types: [],
              months: [],
            };
            this.pubsNext = null;
            this.pubsPrev = null;

            throw error;
          } finally {
            if (
              myRequestId
              === this._ridPubs
            ) {
              this.pubsLoading =
                false;
            }
          }
        },

        async goToPublicationsPage(
          page
        ) {
          return this
            .searchPublicaciones({
              q:
                this.q,

              ...this.pubsParams,

              page:
                positiveInteger(
                  page,
                  1
                ),

              page_size:
                this.pubsPageSize,
            });
        },

        /* ==================================================
           PERFILES
        ================================================== */

        async searchPerfiles({
          q,
          page = 1,
          pageSize =
            this.perfilesPageSize,
          preload = "0",
        } = {}) {
          const query =
            toStr(
              q
              ?? this.q
            ).trim();

          this.q =
            query;

          const shouldPreload = (
            !query
            && toStr(
              preload
            ).trim() === "1"
          );

          const params = {
            page:
              positiveInteger(
                page,
                1
              ),

            page_size:
              positiveInteger(
                pageSize,
                this.perfilesPageSize
                || DEFAULT_PROFILES_PAGE_SIZE
              ),
          };

          if (
            query
          ) {
            params.q =
              query;
          } else if (
            shouldPreload
          ) {
            params.preload =
              "1";
          }

          const cacheKey =
            stableKey(
              params
            );

          this
            ._cancelProfilesRequest();

          this.perfilesError =
            null;

          const cached =
            getCacheEntry(
              this._cachePerfiles,
              cacheKey
            );

          if (
            cached
          ) {
            Object.assign(
              this,
              cached.state
            );

            return cached.raw;
          }

          const myRequestId =
            this._ridPerfiles;

          this._abortPerfiles =
            new AbortController();

          this.perfilesLoading =
            true;

          try {
            const data =
              await listScholarProfiles(
                params,
                {
                  signal:
                    this
                      ._abortPerfiles
                      .signal,
                }
              );

            if (
              myRequestId
              !== this._ridPerfiles
            ) {
              return null;
            }

            const raw =
              getRawProfiles(
                data
              );

            const profiles =
              dedupeAuthors(
                raw.map(
                  normAuthor
                )
              );

            const countFallback = (
              Array.isArray(
                data?.investigadores
              )
                ? data
                    .investigadores
                    .length
                : (
                  Array.isArray(
                    data?.autores
                  )
                    ? data
                        .autores
                        .length
                    : 0
                )
            );

            const snapshot = {
              perfiles:
                profiles,

              perfilesCount:
                num(
                  data?.count
                  ?? data?.total
                  ?? countFallback,
                  profiles.length
                ),

              perfilesNext:
                data?.next
                ?? null,

              perfilesPrev:
                data?.previous
                ?? data?.prev
                ?? null,

              perfilesPage:
                positiveInteger(
                  data?.page
                  ?? params.page,
                  params.page
                ),

              perfilesPageSize:
                positiveInteger(
                  data?.page_size
                  ?? data?.pageSize
                  ?? params.page_size,
                  params.page_size
                ),
            };

            Object.assign(
              this,
              snapshot
            );

            setCacheEntry(
              this._cachePerfiles,
              cacheKey,
              {
                state:
                  snapshot,

                raw:
                  data,
              }
            );

            return data;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return null;
            }

            this.perfilesError =
              extractErrorMessage(
                error,
                (
                  query
                    ? "No se pudieron cargar los perfiles."
                    : (
                      "No se pudieron cargar "
                      + "los perfiles sugeridos."
                    )
                )
              );

            this.perfiles = [];
            this.perfilesCount = 0;
            this.perfilesNext = null;
            this.perfilesPrev = null;

            throw error;
          } finally {
            if (
              myRequestId
              === this._ridPerfiles
            ) {
              this.perfilesLoading =
                false;
            }
          }
        },

        async goToProfilesPage(
          page
        ) {
          return this
            .searchPerfiles({
              q:
                this.q,

              page:
                positiveInteger(
                  page,
                  1
                ),

              pageSize:
                this.perfilesPageSize,

              preload:
                this.q
                  ? "0"
                  : "1",
            });
        },

        /* ==================================================
           AUTOR APLICADO
        ================================================== */

        async fetchAuthorApplied(
          authorId
        ) {
          const id =
            toStr(
              authorId
            ).trim();

          this
            ._cancelAuthorRequest();

          if (
            !id
          ) {
            this.authorApplied =
              null;

            return null;
          }

          if (
            this.authorApplied
            && String(
              this.authorApplied.id
            ) === id
            && !this
              .authorAppliedLoading
          ) {
            return this
              .authorApplied;
          }

          const myRequestId =
            this._ridAuthor;

          this._abortAuthor =
            new AbortController();

          this.authorAppliedLoading =
            true;

          try {
            const data =
              await getScholarProfileDetail(
                id,
                {
                  signal:
                    this
                      ._abortAuthor
                      .signal,
                }
              );

            if (
              myRequestId
              !== this._ridAuthor
            ) {
              return null;
            }

            const normalized =
              normalizeProfileDetail(
                data || {}
              );

            this.authorApplied = {
              id:
                normalized.id
                ?? id,

              name:
                normalized.name
                || "—",

              org:
                normalized.org
                || (
                  "Sin afiliación "
                  + "registrada"
                ),

              avatar:
                normalized.avatar
                ?? null,

              verified:
                Boolean(
                  normalized.verified
                ),

              es_externo:
                Boolean(
                  normalized.es_externo
                ),

              usuario_activo:
                Boolean(
                  normalized
                    .usuario_activo
                ),

              usuario_pendiente:
                Boolean(
                  normalized
                    .usuario_pendiente
                ),

              usuario_estado:
                normalized
                  .usuario_estado
                || "sin_usuario",

              perfil_disponible:
                normalized
                  .perfil_disponible
                !== false,
            };

            return this
              .authorApplied;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return null;
            }

            this.authorApplied =
              null;

            return null;
          } finally {
            if (
              myRequestId
              === this._ridAuthor
            ) {
              this.authorAppliedLoading =
                false;
            }
          }
        },

        /* ==================================================
           DETALLE DE PERFIL
        ================================================== */

        async fetchPerfilDetail(
          id
        ) {
          const authorId =
            toStr(
              id
            ).trim();

          this
            ._cancelPerfilRequest();

          this.perfilDetailError =
            null;

          if (
            !authorId
          ) {
            this.perfilDetail =
              null;

            return null;
          }

          const myRequestId =
            this._ridPerfil;

          this._abortPerfil =
            new AbortController();

          this.perfilDetailLoading =
            true;

          try {
            const data =
              await getScholarProfileDetail(
                authorId,
                {
                  signal:
                    this
                      ._abortPerfil
                      .signal,
                }
              );

            if (
              myRequestId
              !== this._ridPerfil
            ) {
              return null;
            }

            this.perfilDetail =
              normalizeProfileDetail(
                data || {}
              );

            return this
              .perfilDetail;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return null;
            }

            this.perfilDetailError =
              extractErrorMessage(
                error,
                (
                  "No se pudo cargar "
                  + "el perfil."
                )
              );

            this.perfilDetail =
              null;

            throw error;
          } finally {
            if (
              myRequestId
              === this._ridPerfil
            ) {
              this.perfilDetailLoading =
                false;
            }
          }
        },

        async fetchPerfilMe() {
          return this
            .fetchPerfilDetail(
              "me"
            );
        },

        async updatePerfilMe(
          payload = {}
        ) {
          this.perfilDetailError =
            null;

          try {
            const data =
              await updateScholarMyProfile(
                payload
              );

            this.perfilDetail =
              normalizeProfileDetail(
                data || {}
              );

            this
              .clearProfilesCache();

            this
              .clearPubsCache();

            return this
              .perfilDetail;
          } catch (
            error
          ) {
            this.perfilDetailError =
              extractErrorMessage(
                error,
                (
                  "No se pudieron actualizar "
                  + "los identificadores académicos."
                )
              );

            throw error;
          }
        },

        /* ==================================================
           REINICIO Y CACHÉ
        ================================================== */

        resetPublicacionesState() {
          this
            ._cancelPubsRequest();

          this.pubs = [];
          this.pubsTotal = 0;
          this.pubsFacets = {
            years: [],
            types: [],
            months: [],
          };
          this.pubsPage = 1;
          this.pubsNext = null;
          this.pubsPrev = null;
          this.pubsError = null;
        },

        resetPerfilesState() {
          this
            ._cancelProfilesRequest();

          this.perfiles = [];
          this.perfilesCount = 0;
          this.perfilesPage = 1;
          this.perfilesNext = null;
          this.perfilesPrev = null;
          this.perfilesError = null;
        },

        clearPubsCache() {
          this
            ._cachePubs
            .clear();
        },

        clearProfilesCache() {
          this
            ._cachePerfiles
            .clear();
        },

        invalidateSearchCaches() {
          this
            .clearPubsCache();

          this
            .clearProfilesCache();
        },

        clearDetail() {
          this
            ._cancelPerfilRequest();

          this.perfilDetail =
            null;

          this.perfilDetailError =
            null;

          this.perfilDetailLoading =
            false;
        },

        clearAll() {
          this.q = "";

          this
            .clearSuggestions();

          this
            .resetPublicacionesState();

          this.pubsParams = {
            year: "",
            month: "",
            type: "",
            sort: "relevance",
            facets: "1",
            lang: "all",
            author_id: "",
            has_pdf: "",
          };

          this.pubsPageSize =
            DEFAULT_PUBLICATIONS_PAGE_SIZE;

          this
            .clearPubsCache();

          this
            .resetPerfilesState();

          this.perfilesPageSize =
            DEFAULT_PROFILES_PAGE_SIZE;

          this
            .clearProfilesCache();

          this
            ._cancelAuthorRequest();

          this.authorApplied =
            null;

          this.authorAppliedLoading =
            false;

          this
            .clearDetail();
        },
      },
    }
  );
