import { defineStore } from "pinia";

import api from "../api/axios";


/* =========================================================
   ESTRUCTURA
========================================================= */

const emptyCounts = () => ({
  usuarios: 0,
  autores: 0,
  investigadores: 0,
  proyectos: 0,
  publicaciones: 0,
  total: 0,
});

const emptyTruncated = () => ({
  usuarios: false,
  autores: false,
  investigadores: false,
  proyectos: false,
  publicaciones: false,
});

const emptyResultados = () => ({
  usuarios: [],
  autores: [],
  investigadores: [],
  proyectos: [],
  publicaciones: [],

  counts: emptyCounts(),
  truncated: emptyTruncated(),

  query: "",
  limit: 8,

  filters: {
    solo_con_pdf: false,
    has_pdf: false,
  },
});


/* =========================================================
   UTILIDADES
========================================================= */

const toStr = (
  value
) => (
  String(
    value ?? ""
  ).trim()
);

const toPositiveInteger = (
  value,
  fallback = 8
) => {
  const parsedValue =
    Number.parseInt(
      String(
        value ?? ""
      ),
      10
    );

  if (
    !Number.isFinite(
      parsedValue
    )
    || parsedValue < 1
  ) {
    return fallback;
  }

  return parsedValue;
};

const toBoolean = (
  value
) => {
  if (
    typeof value === "boolean"
  ) {
    return value;
  }

  const normalized =
    toStr(
      value
    ).toLowerCase();

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

const safeArray = (
  value
) => (
  Array.isArray(
    value
  )
    ? value
    : []
);

const extractErrorMessage = (
  error,
  fallback
) => {
  const detail = (
    error?.response?.data?.detail
    ?? error?.response?.data?.message
    ?? error?.message
  );

  if (
    Array.isArray(
      detail
    )
  ) {
    const message =
      detail
        .map(
          (item) => toStr(item)
        )
        .filter(
          Boolean
        )
        .join(" ");

    return message || fallback;
  }

  return (
    toStr(
      detail
    )
    || fallback
  );
};

const canonicalAuthorId = (
  item
) => (
  item?.autor_id
  ?? item?.id
  ?? item?.pk
  ?? null
);

const canonicalAuthorName = (
  item
) => {
  const directName =
    toStr(
      item?.name
      ?? item?.nombre
      ?? item?.nombre_completo
  );

  if (
    directName
  ) {
    return directName;
  }

  return [
    toStr(
      item?.nombres
    ),
    toStr(
      item?.apellidos
    ),
  ]
    .filter(
      Boolean
    )
    .join(" ");
};

const dedupeInvestigadores = (
  items
) => {
  const map =
    new Map();

  safeArray(
    items
  ).forEach(
    (item) => {
      const authorId =
        canonicalAuthorId(
          item
        );

      const name =
        canonicalAuthorName(
          item
        ).toLowerCase();

      const key = (
        authorId != null
          ? `autor:${authorId}`
          : `nombre:${name}`
      );

      if (
        !authorId
        && !name
      ) {
        return;
      }

      const previous =
        map.get(
          key
        );

      if (
        !previous
      ) {
        map.set(
          key,
          item
        );

        return;
      }

      map.set(
        key,
        {
          ...previous,
          ...item,

          id:
            authorId
            ?? canonicalAuthorId(
              previous
            ),

          autor_id:
            authorId
            ?? canonicalAuthorId(
              previous
            ),

          avatar: (
            item?.avatar
            ?? item?.avatar_url
            ?? previous?.avatar
            ?? previous?.avatar_url
            ?? null
          ),

          publications: Math.max(
            Number(
              previous?.publications
              ?? previous?.publicaciones
              ?? 0
            ) || 0,

            Number(
              item?.publications
              ?? item?.publicaciones
              ?? 0
            ) || 0
          ),
        }
      );
    }
  );

  return Array.from(
    map.values()
  );
};

const normalizeResultados = (
  data = {}
) => {
  const usuarios =
    safeArray(
      data?.usuarios
    );

  const autores =
    safeArray(
      data?.autores
    );

  const investigadores = (
    safeArray(
      data?.investigadores
    ).length
      ? dedupeInvestigadores(
          data.investigadores
        )
      : dedupeInvestigadores([
          ...autores,
          ...usuarios,
        ])
  );

  const proyectos =
    safeArray(
      data?.proyectos
    );

  const publicaciones =
    safeArray(
      data?.publicaciones
    );

  const sourceCounts = (
    data?.counts
    && typeof data.counts === "object"
      ? data.counts
      : {}
  );

  const counts = {
    usuarios:
      Number(
        sourceCounts.usuarios
      ) || usuarios.length,

    autores:
      Number(
        sourceCounts.autores
      ) || autores.length,

    investigadores:
      Number(
        sourceCounts.investigadores
      ) || investigadores.length,

    proyectos:
      Number(
        sourceCounts.proyectos
      ) || proyectos.length,

    publicaciones:
      Number(
        sourceCounts.publicaciones
      ) || publicaciones.length,

    total: 0,
  };

  counts.total = (
    Number(
      sourceCounts.total
    )
    || (
      counts.investigadores
      + counts.proyectos
      + counts.publicaciones
    )
  );

  return {
    usuarios,
    autores,
    investigadores,
    proyectos,
    publicaciones,

    counts,

    truncated: {
      ...emptyTruncated(),
      ...(
        data?.truncated
        && typeof data.truncated === "object"
          ? data.truncated
          : {}
      ),
    },

    query:
      toStr(
        data?.query
      ),

    limit:
      toPositiveInteger(
        data?.limit,
        8
      ),

    filters: {
      solo_con_pdf:
        toBoolean(
          data?.filters?.solo_con_pdf
        ),

      has_pdf:
        toBoolean(
          data?.filters?.has_pdf
        ),
    },
  };
};


/* =========================================================
   STORE
========================================================= */

export const useSearchStore =
  defineStore(
    "search",
    {
      state: () => ({
        query: "",
        resultados:
          emptyResultados(),

        loading: false,
        error: null,

        _timer: null,
        _resolveDebounce: null,

        _requestId: 0,
        _abortController: null,

        suspendBackend: false,
      }),

      getters: {
        resultadosEncontrados(
          state
        ) {
          const results =
            state.resultados;

          return Boolean(
            results.investigadores.length
            || results.proyectos.length
            || results.publicaciones.length
          );
        },

        total(
          state
        ) {
          return Number(
            state
              .resultados
              .counts
              ?.total
            ?? 0
          );
        },

        totalInvestigadores(
          state
        ) {
          return Number(
            state
              .resultados
              .counts
              ?.investigadores
            ?? 0
          );
        },

        totalProyectos(
          state
        ) {
          return Number(
            state
              .resultados
              .counts
              ?.proyectos
            ?? 0
          );
        },

        totalPublicaciones(
          state
        ) {
          return Number(
            state
              .resultados
              .counts
              ?.publicaciones
            ?? 0
          );
        },
      },

      actions: {
        _cancelDebounce(
          result = null
        ) {
          if (
            this._timer
          ) {
            clearTimeout(
              this._timer
            );
          }

          this._timer = null;

          if (
            typeof this
              ._resolveDebounce
            === "function"
          ) {
            this
              ._resolveDebounce(
                result
                ?? emptyResultados()
              );
          }

          this._resolveDebounce =
            null;
        },

        _cancelNetworkRequest() {
          if (
            this._abortController
          ) {
            this
              ._abortController
              .abort();
          }

          this._abortController =
            null;

          this._requestId += 1;
          this.loading = false;
        },

        _cancelAllRequests() {
          this
            ._cancelDebounce();

          this
            ._cancelNetworkRequest();
        },

        setQuery(
          query
        ) {
          this.query =
            toStr(
              query
            );
        },

        setResultados(
          response
        ) {
          this.resultados =
            normalizeResultados(
              response
            );
        },

        clearResultados() {
          this
            ._cancelAllRequests();

          this.resultados =
            emptyResultados();

          this.loading = false;
          this.error = null;
        },

        clear() {
          this
            .clearResultados();

          this.query = "";
        },

        async _searchNow(
          query,
          {
            limit = 8,
            hasPdf = false,
          } = {}
        ) {
          const normalizedQuery =
            toStr(
              query
            );

          this.query =
            normalizedQuery;

          if (
            !normalizedQuery
          ) {
            this
              .clearResultados();

            return emptyResultados();
          }

          if (
            this.suspendBackend
          ) {
            const empty =
              emptyResultados();

            empty.query =
              normalizedQuery;

            this.resultados =
              empty;

            this.loading = false;
            this.error = null;

            return empty;
          }

          this
            ._cancelNetworkRequest();

          const currentRequestId =
            this._requestId;

          this._abortController =
            new AbortController();

          this.loading = true;
          this.error = null;

          try {
            const response =
              await api.get(
                "busqueda/",
                {
                  params: {
                    q:
                      normalizedQuery,

                    limit:
                      toPositiveInteger(
                        limit,
                        8
                      ),

                    has_pdf:
                      toBoolean(
                        hasPdf
                      )
                        ? "1"
                        : undefined,
                  },

                  signal:
                    this
                      ._abortController
                      .signal,
                }
              );

            if (
              currentRequestId
              !== this._requestId
            ) {
              return emptyResultados();
            }

            const data = (
              response?.data
              ?? response
              ?? {}
            );

            const normalized =
              normalizeResultados(
                data
              );

            this.resultados =
              normalized;

            return normalized;
          } catch (
            error
          ) {
            if (
              error?.code
              === "ERR_CANCELED"
            ) {
              return emptyResultados();
            }

            this.resultados =
              emptyResultados();

            this.error =
              extractErrorMessage(
                error,
                (
                  "No se pudo completar "
                  + "la búsqueda general."
                )
              );

            throw error;
          } finally {
            if (
              currentRequestId
              === this._requestId
            ) {
              this.loading = false;
            }
          }
        },

        search(
          query,
          {
            debounce = 250,
            min = 2,
            limit = 8,
            hasPdf = false,
          } = {}
        ) {
          const normalizedQuery =
            toStr(
              query
            );

          this.query =
            normalizedQuery;

          this
            ._cancelDebounce();

          if (
            normalizedQuery.length
            < min
          ) {
            this
              ._cancelNetworkRequest();

            this.resultados =
              emptyResultados();

            this.error = null;

            return Promise.resolve(
              this.resultados
            );
          }

          return new Promise(
            (
              resolve,
              reject
            ) => {
              this._resolveDebounce =
                resolve;

              this._timer =
                setTimeout(
                  async () => {
                    const pendingResolve =
                      this
                        ._resolveDebounce;

                    this._resolveDebounce =
                      null;

                    this._timer =
                      null;

                    try {
                      const data =
                        await this
                          ._searchNow(
                            normalizedQuery,
                            {
                              limit,
                              hasPdf,
                            }
                          );

                      if (
                        typeof pendingResolve
                        === "function"
                      ) {
                        pendingResolve(
                          data
                        );
                      }
                    } catch (
                      error
                    ) {
                      reject(
                        error
                      );
                    }
                  },
                  debounce
                );
            }
          );
        },

        setSuspendBackend(
          value
        ) {
          this.suspendBackend =
            Boolean(
              value
            );

          if (
            this.suspendBackend
          ) {
            this
              .clearResultados();
          }
        },
      },
    }
  );
