<template>
  <main class="sch-page">
    <div class="sch-shell">
      <!-- =====================================================
           ESTADO INICIAL
      ====================================================== -->
      <section
        v-if="!hasSearched"
        class="sch-empty-hero page-stage"
        aria-labelledby="sch-empty-title"
      >
        <div class="sch-empty-hero__content">
          <span class="sch-empty-hero__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
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

              <path
                d="M8 8.5h5M8 11.5h3.5"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
          </span>

          <div class="sch-empty-hero__copy">
            <span class="sch-eyebrow">
              Búsqueda académica
            </span>

            <h1
              id="sch-empty-title"
              class="sch-empty-hero__title"
            >
              Consulte publicaciones e investigadores
            </h1>

            <p class="sch-empty-hero__text">
              Encuentre producción científica registrada en SGPC ULEAM mediante
              títulos, autores, identificadores académicos, DOI, revistas, eventos o proyectos.
            </p>
          </div>

          <form
            class="sch-empty-search"
            @submit.prevent="submitInlineSearch"
          >
            <label
              class="sch-empty-search__label"
              for="sch-empty-search-input"
            >
              Buscar en SGPC ULEAM
            </label>

            <div class="sch-empty-search__box">
              <span
                class="sch-search-icon"
                aria-hidden="true"
              >
                <svg viewBox="0 0 24 24">
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

              <input
                id="sch-empty-search-input"
                v-model.trim="inlineQuery"
                class="sch-empty-search__input"
                type="search"
                placeholder="Título, autor, ORCID, DOI, revista..."
                autocomplete="off"
              />

              <button
                class="sch-btn sch-btn--primary sch-btn--search"
                type="submit"
                :disabled="!inlineQuery.trim()"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <circle
                    cx="8.5"
                    cy="8.5"
                    r="5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                  />

                  <path
                    d="m12.4 12.4 4 4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>

                <span>Buscar</span>
              </button>
            </div>
          </form>

          <div
            class="sch-suggestions"
            aria-label="Búsquedas sugeridas"
          >
            <span class="sch-suggestions__label">
              Sugerencias:
            </span>

            <button
              v-for="suggestion in searchSuggestions"
              :key="suggestion"
              class="sch-suggestion"
              type="button"
              @click="applySuggestion(suggestion)"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </section>

      <!-- =====================================================
           RESULTADOS
      ====================================================== -->
      <template v-else>
        <section
          class="sch-querybar page-stage"
          aria-labelledby="sch-results-title"
        >
          <div class="sch-querybar__top">
            <div class="sch-querybar__copy">
              <span class="sch-eyebrow">
                {{ scopeLabel }}
              </span>

              <h1
                id="sch-results-title"
                class="sch-querybar__title"
              >
                {{ queryHeading }}
              </h1>

              <p
                class="sch-querybar__meta"
                aria-live="polite"
              >
                {{ queryMeta }}
              </p>
            </div>

            <div
              class="sch-segment"
              role="tablist"
              aria-label="Tipo de resultado"
            >
              <button
                id="sch-publications-tab"
                class="sch-segment__btn"
                type="button"
                role="tab"
                aria-controls="sch-publications-panel"
                :aria-selected="activeScope === 'pubs'"
                :class="{ active: activeScope === 'pubs' }"
                @click="handleScopeClick('pubs')"
              >
                <span>Publicaciones</span>

                <strong>{{ fmt(pubsCountView) }}</strong>
              </button>

              <button
                id="sch-profiles-tab"
                class="sch-segment__btn"
                type="button"
                role="tab"
                aria-controls="sch-profiles-panel"
                :aria-selected="activeScope === 'profiles'"
                :class="{ active: activeScope === 'profiles' }"
                @click="handleScopeClick('profiles')"
              >
                <span>Investigadores</span>

                <strong>{{ fmt(profilesCountView) }}</strong>
              </button>
            </div>
          </div>

          <form
            class="sch-results-search"
            role="search"
            @submit.prevent="submitInlineSearch"
          >
            <label
              class="sch-sr-only"
              for="sch-results-search-input"
            >
              Modificar consulta académica
            </label>

            <span
              class="sch-results-search__icon"
              aria-hidden="true"
            >
              <svg viewBox="0 0 24 24">
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

            <input
              id="sch-results-search-input"
              v-model.trim="inlineQuery"
              type="search"
              placeholder="Modificar búsqueda..."
              autocomplete="off"
            />

            <button
              v-if="inlineQuery"
              class="sch-results-search__clear"
              type="button"
              aria-label="Limpiar búsqueda"
              title="Limpiar búsqueda"
              @click="resetSearch"
            >
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <path
                  d="m5 5 10 10M15 5 5 15"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
            </button>

            <button
              class="sch-btn sch-btn--primary sch-results-search__submit"
              type="submit"
              :disabled="!inlineQuery.trim()"
            >
              Buscar
            </button>
          </form>
        </section>

        <!-- ===================================================
             FILTROS
        ==================================================== -->
        <section
          v-if="activeScope === 'pubs'"
          class="sch-controls page-stage"
          aria-labelledby="sch-filter-title"
        >
          <div class="sch-controls__heading">
            <div>
              <span class="sch-controls__eyebrow">
                Refinar resultados
              </span>

              <h2 id="sch-filter-title">
                Filtros de publicaciones
              </h2>
            </div>

            <button
              v-if="refinementFilterCount"
              class="sch-clear-filters"
              type="button"
              @click="clearRefinementFilters"
            >
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <path
                  d="M4 5h12M6.5 10h7M8.5 15h3"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
              </svg>

              <span>Limpiar filtros</span>

              <strong>{{ refinementFilterCount }}</strong>
            </button>
          </div>

          <div class="sch-controls__grid">
            <label class="sch-control">
              <span class="sch-label">
                Ordenar
              </span>

              <span class="sch-select-wrap">
                <select
                  id="scholar-sort"
                  class="sch-select"
                  :value="state.sort"
                  @change="setParam('sort', $event.target.value)"
                >
                  <option value="relevance">
                    Relevancia
                  </option>

                  <option value="year_desc">
                    Más recientes
                  </option>

                  <option value="year_asc">
                    Más antiguas
                  </option>

                  <option value="title_asc">
                    Título A–Z
                  </option>
                </select>

                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="m6 8 4 4 4-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </label>

            <label class="sch-control">
              <span class="sch-label">
                Año
              </span>

              <span class="sch-select-wrap">
                <select
                  id="scholar-year"
                  class="sch-select"
                  :value="state.year"
                  @change="setParam('year', $event.target.value)"
                >
                  <option value="">
                    Todos los años
                  </option>

                  <option
                    v-for="item in yearFacets"
                    :key="item.value"
                    :value="item.value"
                  >
                    {{ item.label }}
                  </option>
                </select>

                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="m6 8 4 4 4-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </label>

            <label class="sch-control">
              <span class="sch-label">
                Mes
              </span>

              <span class="sch-select-wrap">
                <select
                  id="scholar-month"
                  class="sch-select"
                  :value="state.month"
                  @change="setParam('month', $event.target.value)"
                >
                  <option value="">
                    Todos los meses
                  </option>

                  <option
                    v-for="item in monthFacets"
                    :key="item.value"
                    :value="item.value"
                  >
                    {{ item.label }}
                  </option>
                </select>

                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="m6 8 4 4 4-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </label>

            <label class="sch-control">
              <span class="sch-label">
                Tipo
              </span>

              <span class="sch-select-wrap">
                <select
                  id="scholar-type"
                  class="sch-select"
                  :value="state.type"
                  @change="setParam('type', $event.target.value)"
                >
                  <option value="">
                    Todos los tipos
                  </option>

                  <option
                    v-for="item in typeFacets"
                    :key="item.value"
                    :value="item.value"
                  >
                    {{ item.label }}
                  </option>
                </select>

                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="m6 8 4 4 4-4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </label>

            <label
              class="sch-pdf-filter"
              :class="{ active: state.hasPdf === '1' }"
            >
              <input
                type="checkbox"
                :checked="state.hasPdf === '1'"
                @change="
                  setParam(
                    'has_pdf',
                    $event.target.checked ? '1' : ''
                  )
                "
              />

              <span class="sch-pdf-filter__icon" aria-hidden="true">
                <svg viewBox="0 0 20 20">
                  <path
                    d="M5 2.5h6l4 4v11H5v-15Zm6 0v4h4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <span class="sch-pdf-filter__copy">
                <strong>Solo con PDF</strong>
                <small>Documentos disponibles</small>
              </span>

              <span class="sch-switch" aria-hidden="true">
                <span></span>
              </span>
            </label>
          </div>
        </section>

        <!-- ===================================================
             AUTOR APLICADO
        ==================================================== -->
        <section
          v-if="authorContext && activeScope === 'pubs'"
          class="sch-authorstrip page-stage"
          aria-label="Autor aplicado"
        >
          <div class="sch-authorstrip__main">
            <div class="sch-avatar sch-avatar--md">
              <img
                v-if="authorContext.avatar"
                :src="authorContext.avatar"
                alt="Foto del autor"
              />

              <div
                v-else
                class="sch-avatar__fallback"
                aria-hidden="true"
              >
                {{
                  (authorContext.name || "?")
                    .charAt(0)
                    .toUpperCase()
                }}
              </div>
            </div>

            <div class="sch-authorstrip__copy">
              <span class="sch-authorstrip__eyebrow">
                Autor aplicado
              </span>

              <h2 class="sch-authorstrip__name">
                {{ authorContext.name || "Autor" }}
              </h2>

              <p class="sch-authorstrip__org">
                {{
                  authorContext.org ||
                  "Sin afiliación registrada"
                }}
              </p>
            </div>
          </div>

          <div class="sch-actions">
            <button
              class="sch-btn sch-btn--secondary"
              type="button"
              @click="openProfile(authorContext.id)"
            >
              <svg viewBox="0 0 20 20" aria-hidden="true">
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

              <span>Ver perfil</span>
            </button>

            <button
              class="sch-btn sch-btn--ghost"
              type="button"
              @click="clearAuthor"
            >
              Quitar autor
            </button>
          </div>
        </section>

        <!-- ===================================================
             FILTROS ACTIVOS
        ==================================================== -->
        <div
          v-if="
            activeFilterChips.length &&
            activeScope === 'pubs'
          "
          class="sch-active-filters page-stage"
          aria-label="Filtros activos"
        >
          <span class="sch-active-filters__label">
            Filtros activos:
          </span>

          <div class="sch-chips">
            <button
              v-for="chip in activeFilterChips"
              :key="chip.key"
              class="sch-chip"
              type="button"
              :title="`Quitar filtro ${chip.label}`"
              @click="chip.onRemove()"
            >
              <span>{{ chip.label }}</span>

              <svg viewBox="0 0 20 20" aria-hidden="true">
                <path
                  d="m6 6 8 8M14 6l-8 8"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- ===================================================
             PUBLICACIONES
        ==================================================== -->
        <section
          v-if="activeScope === 'pubs'"
          id="sch-publications-panel"
          class="sch-results page-stage"
          role="tabpanel"
          aria-labelledby="sch-publications-tab"
          :aria-busy="store.pubsLoading ? 'true' : 'false'"
        >
          <div
            v-if="store.pubsError"
            class="sch-state sch-state--error"
            role="alert"
          >
            <span class="sch-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <circle
                  cx="12"
                  cy="12"
                  r="9"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />

                <path
                  d="M12 7.5V13M12 16.5h.01"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div class="sch-state__content">
              <h2 class="sch-state__title">
                No se pudo completar la búsqueda
              </h2>

              <p class="sch-state__text">
                {{ store.pubsError }}
              </p>

              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                @click="runSearch"
              >
                Intentar nuevamente
              </button>
            </div>
          </div>

          <div
            v-else-if="store.pubsLoading"
            class="sch-loading"
            aria-hidden="true"
          >
            <article
              v-for="n in 5"
              :key="`pub-load-${n}`"
              class="sch-loading-card"
            >
              <div class="sch-loading-card__year"></div>

              <div class="sch-loading-card__body">
                <div class="sch-loading-card__badges">
                  <span></span>
                  <span></span>
                </div>

                <div class="sch-loading-card__title"></div>
                <div class="sch-loading-card__line"></div>
                <div class="sch-loading-card__line is-short"></div>
              </div>
            </article>
          </div>

          <template v-else-if="resultsList.length">
            <div class="sch-publication-list">
            <article
              v-for="r in resultsList"
              :key="r.id"
              class="sch-publication-card"
              :class="{
                'has-pdf': r.hasPdf || r.pdf_url,
              }"
            >
              <div class="sch-publication-card__accent"></div>

              <aside
                class="sch-publication-card__year"
                :aria-label="publicationPeriodLabel(r)"
              >
                <small
                  v-if="publicationMonthShort(r)"
                  class="sch-publication-card__month"
                >
                  {{ publicationMonthShort(r) }}
                </small>

                <strong class="sch-publication-card__year-value">
                  {{ r.year || "S/F" }}
                </strong>
              </aside>

              <div class="sch-publication-card__content">
                <div class="sch-publication-card__badges">
                  <span
                    v-if="r.tipo_label"
                    class="sch-pill sch-pill--accent"
                  >
                    {{ r.tipo_label }}
                  </span>

                  <span
                    v-if="r.hasPdf || r.pdf_url"
                    class="sch-pill sch-pill--pdf"
                  >
                    <svg viewBox="0 0 20 20" aria-hidden="true">
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

                  <span
                    v-if="r.area_label"
                    class="sch-pill"
                  >
                    {{ r.area_label }}
                  </span>
                </div>

                <h2 class="sch-publication-card__title">
                  <button
                    type="button"
                    @click="openPublication(r.id)"
                  >
                    {{ r.title || "Sin título" }}
                  </button>
                </h2>

                <div class="sch-publication-card__details">
                  <div class="sch-publication-card__detail">
                    <span
                      class="sch-publication-card__detail-icon"
                      aria-hidden="true"
                    >
                      <svg viewBox="0 0 20 20">
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

                    <p>
                      <template v-if="Array.isArray(r.authors)">
                        <template
                          v-for="(author, index) in r.authors"
                          :key="
                            author.id ||
                            `${author.name}-${index}`
                          "
                        >
                          <button
                            class="sch-author-link"
                            type="button"
                            @click="openAuthorFromResults(author)"
                          >
                            {{ author.name }}
                          </button>

                          <span
                            v-if="
                              index <
                              r.authors.length - 1
                            "
                          >
                            ,
                          </span>
                        </template>
                      </template>

                      <span v-else>
                        {{ r.authors || "Autores no disponibles" }}
                      </span>
                    </p>
                  </div>

                  <div
                    v-if="r.source || r.venue"
                    class="sch-publication-card__detail"
                  >
                    <span
                      class="sch-publication-card__detail-icon"
                      aria-hidden="true"
                    >
                      <svg viewBox="0 0 20 20">
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

                    <p>
                      <span v-if="r.source">
                        {{ r.source }}
                      </span>

                      <span
                        v-if="r.source && r.venue"
                        aria-hidden="true"
                      >
                        ·
                      </span>

                      <span v-if="r.venue">
                        {{ r.venue }}
                      </span>
                    </p>
                  </div>
                </div>

                <p
                  v-if="r.snippet"
                  class="sch-publication-card__snippet"
                >
                  {{ r.snippet }}
                </p>

                <footer class="sch-publication-card__footer">
                  <div class="sch-publication-card__tags">
                    <span
                      v-if="r.doi"
                      class="sch-doi"
                      :title="r.doi"
                    >
                      DOI: {{ r.doi }}
                    </span>
                  </div>

                  <div class="sch-actions">
                    <button
                      v-if="r.pdf_url"
                      class="sch-action-link"
                      type="button"
                      @click="openPdf(r.pdf_url)"
                    >
                      <svg viewBox="0 0 20 20" aria-hidden="true">
                        <path
                          d="M10 3v9M6.5 9.5 10 13l3.5-3.5M4 16.5h12"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.6"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>

                      <span>Abrir PDF</span>
                    </button>

                    <button
                      class="sch-action-link sch-action-link--primary"
                      type="button"
                      @click="openPublication(r.id)"
                    >
                      <span>Ver detalle</span>

                      <svg viewBox="0 0 20 20" aria-hidden="true">
                        <path
                          d="M4.5 10h11M11.2 5.7l4.3 4.3-4.3 4.3"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.7"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </button>
                  </div>
                </footer>
              </div>
            </article>
            </div>

            <nav
              v-if="pubsTotalPages > 1"
              class="sch-pagination"
              aria-label="Paginación de publicaciones"
            >
              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                :disabled="
                  store.pubsLoading ||
                  pubsCurrentPage <= 1
                "
                @click="
                  goToPublicationsPage(
                    pubsCurrentPage - 1
                  )
                "
              >
                Anterior
              </button>

              <span
                class="sch-pagination__status"
                aria-live="polite"
              >
                Página {{ pubsCurrentPage }} de
                {{ pubsTotalPages }}
              </span>

              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                :disabled="
                  store.pubsLoading ||
                  pubsCurrentPage >= pubsTotalPages
                "
                @click="
                  goToPublicationsPage(
                    pubsCurrentPage + 1
                  )
                "
              >
                Siguiente
              </button>
            </nav>
          </template>

          <div
            v-else
            class="sch-state"
          >
            <span class="sch-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <circle
                  cx="10.5"
                  cy="10.5"
                  r="6.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />

                <path
                  d="m15.5 15.5 5 5M7.5 10.5h6"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div class="sch-state__content">
              <h2 class="sch-state__title">
                Sin publicaciones encontradas
              </h2>

              <p class="sch-state__text">
                Modifique la consulta o elimine algunos filtros para ampliar los
                resultados.
              </p>

              <button
                v-if="refinementFilterCount"
                class="sch-btn sch-btn--secondary"
                type="button"
                @click="clearRefinementFilters"
              >
                Limpiar filtros
              </button>
            </div>
          </div>
        </section>

        <!-- ===================================================
             INVESTIGADORES
        ==================================================== -->
        <section
          v-else
          id="sch-profiles-panel"
          class="sch-results page-stage"
          role="tabpanel"
          aria-labelledby="sch-profiles-tab"
          :aria-busy="store.perfilesLoading ? 'true' : 'false'"
        >
          <div
            v-if="store.perfilesError"
            class="sch-state sch-state--error"
            role="alert"
          >
            <span class="sch-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <circle
                  cx="12"
                  cy="12"
                  r="9"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />

                <path
                  d="M12 7.5V13M12 16.5h.01"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div class="sch-state__content">
              <h2 class="sch-state__title">
                No se pudieron cargar los investigadores
              </h2>

              <p class="sch-state__text">
                {{ store.perfilesError }}
              </p>

              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                @click="runSearch"
              >
                Intentar nuevamente
              </button>
            </div>
          </div>

          <div
            v-else-if="store.perfilesLoading"
            class="sch-profile-loading-grid"
            aria-hidden="true"
          >
            <article
              v-for="n in 6"
              :key="`profile-load-${n}`"
              class="sch-profile-loading-card"
            >
              <div class="sch-profile-loading-card__avatar"></div>

              <div class="sch-profile-loading-card__body">
                <div class="sch-profile-loading-card__name"></div>
                <div class="sch-profile-loading-card__line"></div>
                <div class="sch-profile-loading-card__line is-short"></div>
              </div>
            </article>
          </div>

          <template v-else-if="profilesList.length">
            <div class="sch-profile-grid">
            <article
              v-for="profile in profilesList"
              :key="profile.id"
              class="sch-profile-card"
            >
              <div class="sch-profile-card__header">
                <div class="sch-avatar sch-avatar--lg">
                  <img
                    v-if="profile.avatar"
                    :src="profile.avatar"
                    alt="Foto del investigador"
                  />

                  <div
                    v-else
                    class="sch-avatar__fallback"
                    aria-hidden="true"
                  >
                    {{
                      (
                        profile.name?.charAt(0) ||
                        "U"
                      ).toUpperCase()
                    }}
                  </div>
                </div>

                <span
                  v-if="profile.es_externo"
                  class="sch-profile-card__type"
                >
                  Autor externo
                </span>

                <span
                  v-if="profile.usuario_pendiente"
                  class="sch-profile-card__type"
                  title="Autor registrado sin acceso activo al sistema"
                >
                  Cuenta pendiente
                </span>
              </div>

              <div class="sch-profile-card__body">
                <h2 class="sch-profile-card__name">
                  <button
                    type="button"
                    @click="openProfile(profile.id)"
                  >
                    {{ profile.name || "Sin nombre" }}
                  </button>
                </h2>

                <p class="sch-profile-card__org">
                  {{
                    profile.org ||
                    "Sin afiliación registrada"
                  }}
                </p>

                <div class="sch-profile-card__meta">
                  <span
                    v-if="profile.publications != null"
                  >
                    <svg viewBox="0 0 20 20" aria-hidden="true">
                      <path
                        d="M5 2.5h7l3 3v12H5v-15Zm7 0v3h3"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linejoin="round"
                      />
                    </svg>

                    {{
                      pluralize(
                        profile.publications,
                        "publicación",
                        "publicaciones"
                      )
                    }}
                  </span>
                </div>

                <div
                  v-if="
                    Array.isArray(profile.tags) &&
                    profile.tags.length
                  "
                  class="sch-profile-card__tags"
                >
                  <span
                    v-for="tag in profile.tags.slice(0, 3)"
                    :key="tag"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>

              <footer class="sch-profile-card__footer">
                <button
                  class="sch-action-link sch-action-link--primary"
                  type="button"
                  @click="openProfile(profile.id)"
                >
                  <span>Ver perfil académico</span>

                  <svg viewBox="0 0 20 20" aria-hidden="true">
                    <path
                      d="M4.5 10h11M11.2 5.7l4.3 4.3-4.3 4.3"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>
              </footer>
            </article>
            </div>

            <nav
              v-if="profilesTotalPages > 1"
              class="sch-pagination"
              aria-label="Paginación de investigadores"
            >
              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                :disabled="
                  store.perfilesLoading ||
                  profilesCurrentPage <= 1
                "
                @click="
                  goToProfilesPage(
                    profilesCurrentPage - 1
                  )
                "
              >
                Anterior
              </button>

              <span
                class="sch-pagination__status"
                aria-live="polite"
              >
                Página {{ profilesCurrentPage }} de
                {{ profilesTotalPages }}
              </span>

              <button
                class="sch-btn sch-btn--secondary"
                type="button"
                :disabled="
                  store.perfilesLoading ||
                  profilesCurrentPage >= profilesTotalPages
                "
                @click="
                  goToProfilesPage(
                    profilesCurrentPage + 1
                  )
                "
              >
                Siguiente
              </button>
            </nav>
          </template>

          <div
            v-else
            class="sch-state"
          >
            <span class="sch-state__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
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

            <div class="sch-state__content">
              <h2 class="sch-state__title">
                Sin investigadores encontrados
              </h2>

              <p class="sch-state__text">
                No existen perfiles académicos relacionados con esta consulta.
              </p>
            </div>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup>
import {
  computed,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import { useScholarStore } from "../../scripts/stores/scholarStore";
import { useUserStore } from "../../scripts/stores/userStore";

const PUBLICACIONES_PAGE_SIZE = 10;
const PERFILES_PAGE_SIZE = 8;

const searchSuggestions = [
  "Inteligencia artificial",
  "Ciencias ambientales",
  "Salud pública",
  "Producción científica",
];

const store = useScholarStore();
const userStore = useUserStore();

const route = useRoute();
const router = useRouter();

const activeScope = ref("pubs");
const userSelectedScope = ref(false);
const nextSearchPreferredScope = ref("");
const requestSerial = ref(0);
const inlineQuery = ref("");

const buildSearchKey = ({
  q = "",
  authorId = "",
} = {}) => {
  return JSON.stringify({
    q: String(q || "").trim(),
    authorId: String(authorId || "").trim(),
  });
};

const myAuthorId = computed(() => {
  return String(
    userStore.autorId ??
    userStore.user?.autor_id ??
    userStore.user?.author_id ??
    ""
  ).trim();
});

const state = computed(() => ({
  q: String(route.query.q || "").trim(),

  authorId:
    String(
      route.query.author_id || ""
    ).trim(),

  year:
    String(
      route.query.year || ""
    ).trim(),

  month:
    String(
      route.query.month || ""
    ).trim(),

  type:
    String(
      route.query.type || ""
    ).trim(),

  sort:
    String(
      route.query.sort || "relevance"
    ).trim() || "relevance",

  hasPdf:
    String(
      route.query.has_pdf || ""
    ).trim(),

  page:
    Math.max(
      1,
      Number.parseInt(
        String(
          route.query.page || "1"
        ),
        10
      ) || 1
    ),

  profilePage:
    Math.max(
      1,
      Number.parseInt(
        String(
          route.query.profile_page || "1"
        ),
        10
      ) || 1
    ),
}));

const currentSearchKey = computed(() => {
  return buildSearchKey({
    q: state.value.q,
    authorId: state.value.authorId,
  });
});

const rawResultsList = computed(() => {
  return Array.isArray(store.pubs)
    ? store.pubs
    : [];
});

const resultsList = computed(() => {
  /*
   * El filtro PDF se ejecuta en el backend. De esta forma, el
   * total y la paginación representan todas las coincidencias,
   * no únicamente la página que ya llegó al navegador.
   */
  return rawResultsList.value;
});

const profilesList = computed(() => {
  return Array.isArray(store.perfiles)
    ? store.perfiles
    : [];
});

const authorContext = computed(() => {
  return store.authorApplied || null;
});

const hasSearched = computed(() => {
  return Boolean(
    state.value.q ||
    state.value.authorId
  );
});

const profilesSearchText = computed(() => {
  if (state.value.q) {
    return state.value.q;
  }

  return String(
    authorContext.value?.name || ""
  ).trim();
});

const pubsCountView = computed(() => {
  return Number(
    store.pubsTotal ??
    resultsList.value.length ??
    0
  );
});

const profilesCountView = computed(() => {
  return Number(
    store.perfilesCount ??
    profilesList.value.length ??
    0
  );
});

const pubsCurrentPage = computed(() => {
  return Math.max(
    1,
    Number(
      store.pubsPage ??
      state.value.page ??
      1
    ) || 1
  );
});

const pubsPageSize = computed(() => {
  return Math.max(
    1,
    Number(
      store.pubsPageSize ??
      PUBLICACIONES_PAGE_SIZE
    ) || PUBLICACIONES_PAGE_SIZE
  );
});

const pubsTotalPages = computed(() => {
  return Math.max(
    1,
    Math.ceil(
      pubsCountView.value /
      pubsPageSize.value
    )
  );
});

const profilesCurrentPage = computed(() => {
  return Math.max(
    1,
    Number(
      store.perfilesPage ??
      state.value.profilePage ??
      1
    ) || 1
  );
});

const profilesPageSize = computed(() => {
  return Math.max(
    1,
    Number(
      store.perfilesPageSize ??
      PERFILES_PAGE_SIZE
    ) || PERFILES_PAGE_SIZE
  );
});

const profilesTotalPages = computed(() => {
  return Math.max(
    1,
    Math.ceil(
      profilesCountView.value /
      profilesPageSize.value
    )
  );
});

const fmt = (value) => {
  try {
    return Number(
      value || 0
    ).toLocaleString("es-EC");
  } catch {
    return String(value || 0);
  }
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


const publicationMonthLabel = (publication) => {
  const direct = String(
    publication?.mes_publicacion_label ??
    publication?.month_label ??
    ""
  ).trim();

  if (direct) {
    return direct;
  }

  const month = Number(
    publication?.mes_publicacion ??
    publication?.month ??
    publication?.mes ??
    0
  );

  return (
    Number.isInteger(month) &&
    month >= 1 &&
    month <= 12
  )
    ? MONTH_LABELS[month]
    : "";
};


const publicationMonthShort = (publication) => {
  const label =
    publicationMonthLabel(
      publication
    );

  return label
    ? label.slice(0, 3).toUpperCase()
    : "";
};


const publicationPeriodLabel = (publication) => {
  const year = Number(
    publication?.anio_publicacion ??
    publication?.year ??
    publication?.anio ??
    0
  );

  const monthLabel =
    publicationMonthLabel(
      publication
    );

  if (
    Number.isFinite(year) &&
    year > 0 &&
    monthLabel
  ) {
    return `${monthLabel} de ${year}`;
  }

  if (
    Number.isFinite(year) &&
    year > 0
  ) {
    return String(year);
  }

  return monthLabel || "Sin período";
};


const pluralize = (
  value,
  singular,
  plural
) => {
  const count = Number(value || 0);

  return `${fmt(count)} ${
    count === 1
      ? singular
      : plural
  }`;
};

const resultSummary = computed(() => {
  if (activeScope.value === "profiles") {
    return pluralize(
      profilesCountView.value,
      "investigador",
      "investigadores"
    );
  }

  return pluralize(
    pubsCountView.value,
    "publicación",
    "publicaciones"
  );
});

const scopeLabel = computed(() => {
  return activeScope.value === "profiles"
    ? "Investigadores"
    : "Publicaciones";
});

const queryHeading = computed(() => {
  if (activeScope.value === "profiles") {
    return profilesSearchText.value
      ? `Resultados para “${profilesSearchText.value}”`
      : "Investigadores";
  }

  if (
    state.value.authorId &&
    authorContext.value?.name
  ) {
    return authorContext.value.name;
  }

  if (state.value.q) {
    return `Resultados para “${state.value.q}”`;
  }

  return "Publicaciones";
});

const queryMeta = computed(() => {
  if (
    state.value.authorId &&
    authorContext.value?.name &&
    activeScope.value === "pubs"
  ) {
    return `Producción registrada por el autor · ${resultSummary.value}`;
  }

  return `${resultSummary.value} encontrados`;
});

const typeFacets = computed(() => {
  const fromApi =
    Array.isArray(
      store.pubsFacets?.types
    )
      ? store.pubsFacets.types
      : null;

  if (fromApi?.length) {
    return fromApi
      .map((item) => {
        if (typeof item === "string") {
          return {
            value: item,
            label: item,
            count: null,
          };
        }

        return {
          value:
            String(
              item.value ??
              item.codigo ??
              ""
            ).trim(),

          label:
            String(
              item.label ??
              item.nombre ??
              item.value ??
              ""
            ).trim(),

          count:
            item.count ??
            null,
        };
      })
      .filter((item) => item.value);
  }

  const map = new Map();

  rawResultsList.value.forEach((publication) => {
    const code =
      String(
        publication?.tipo_codigo || ""
      ).trim();

    if (!code) {
      return;
    }

    if (!map.has(code)) {
      map.set(code, {
        value: code,

        label:
          String(
            publication?.tipo_label ||
            code
          ).trim() || code,

        count: 0,
      });
    }

    map.get(code).count += 1;
  });

  return [...map.values()].sort(
    (a, b) => {
      return a.label.localeCompare(
        b.label,
        "es"
      );
    }
  );
});

const yearFacets = computed(() => {
  const fromApi =
    Array.isArray(
      store.pubsFacets?.years
    )
      ? store.pubsFacets.years
      : null;

  if (fromApi?.length) {
    return fromApi
      .map((item) => {
        if (
          typeof item === "string" ||
          typeof item === "number"
        ) {
          const value = String(item);

          return {
            label: value,
            value,
            count: null,
          };
        }

        const value =
          String(
            item.value ??
            item.year ??
            ""
          ).trim();

        return {
          label:
            String(
              item.label ??
              value
            ).trim(),

          value,

          count:
            item.count ??
            null,
        };
      })
      .filter((item) => item.value);
  }

  const map = new Map();

  rawResultsList.value.forEach((publication) => {
    const year = Number(publication?.year);

    if (
      !Number.isFinite(year) ||
      year < 1900
    ) {
      return;
    }

    map.set(
      year,
      (map.get(year) || 0) + 1
    );
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

const monthFacets = computed(() => {
  const fromApi =
    Array.isArray(
      store.pubsFacets?.months
    )
      ? store.pubsFacets.months
      : null;

  if (fromApi?.length) {
    return fromApi
      .map((item) => {
        if (
          typeof item === "string" ||
          typeof item === "number"
        ) {
          const value =
            String(item).trim();

          const month =
            Number(value);

          return {
            value,
            label:
              MONTH_LABELS[month] ||
              value,
            count: null,
          };
        }

        const value =
          String(
            item.value ??
            item.month ??
            item.mes ??
            ""
          ).trim();

        const month =
          Number(value);

        return {
          value,

          label:
            String(
              item.label ??
              item.nombre ??
              MONTH_LABELS[month] ??
              value
            ).trim(),

          count:
            item.count ??
            null,
        };
      })
      .filter((item) => {
        const month =
          Number(item.value);

        return (
          Number.isInteger(month) &&
          month >= 1 &&
          month <= 12
        );
      })
      .sort(
        (a, b) =>
          Number(a.value) -
          Number(b.value)
      );
  }

  const map = new Map();

  rawResultsList.value.forEach(
    (publication) => {
      const month = Number(
        publication?.mes_publicacion ??
        publication?.month ??
        publication?.mes ??
        0
      );

      if (
        !Number.isInteger(month) ||
        month < 1 ||
        month > 12
      ) {
        return;
      }

      map.set(
        month,
        (map.get(month) || 0) + 1
      );
    }
  );

  return [...map.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([month, count]) => ({
      value: String(month),
      label:
        MONTH_LABELS[month] ||
        String(month),
      count,
    }));
});


const selectedMonthLabel = computed(() => {
  const month =
    String(
      state.value.month || ""
    ).trim();

  if (!month) {
    return "";
  }

  const match =
    monthFacets.value.find(
      (item) =>
        String(item.value) === month
    );

  return (
    match?.label ||
    MONTH_LABELS[Number(month)] ||
    month
  );
});


const selectedTypeLabel = computed(() => {
  const code = state.value.type;

  if (!code) {
    return "";
  }

  const match =
    typeFacets.value.find(
      (item) =>
        item.value === code
    );

  return match?.label || code;
});

const activeFilterChips = computed(() => {
  const chips = [];

  if (state.value.year) {
    chips.push({
      key: "year",
      label: `Año: ${state.value.year}`,
      onRemove: () =>
        setParam("year", ""),
    });
  }

  if (state.value.month) {
    chips.push({
      key: "month",
      label: `Mes: ${selectedMonthLabel.value}`,
      onRemove: () =>
        setParam("month", ""),
    });
  }

  if (state.value.type) {
    chips.push({
      key: "type",
      label: `Tipo: ${selectedTypeLabel.value}`,
      onRemove: () =>
        setParam("type", ""),
    });
  }

  if (state.value.hasPdf === "1") {
    chips.push({
      key: "has_pdf",
      label: "Solo con PDF",
      onRemove: () =>
        setParam("has_pdf", ""),
    });
  }

  if (state.value.authorId) {
    chips.push({
      key: "author_id",

      label:
        `Autor: ${
          authorContext.value?.name ||
          "aplicado"
        }`,

      onRemove: clearAuthor,
    });
  }

  return chips;
});

const refinementFilterCount = computed(() => {
  let count = 0;

  if (state.value.year) {
    count += 1;
  }

  if (state.value.month) {
    count += 1;
  }

  if (state.value.type) {
    count += 1;
  }

  if (state.value.hasPdf === "1") {
    count += 1;
  }

  return count;
});

const getVisiblePubsFound = () => {
  return resultsList.value.length;
};

const getProfilesFound = () => {
  const total = Number(
    store.perfilesCount ??
    (
      Array.isArray(store.perfiles)
        ? store.perfiles.length
        : 0
    )
  );

  return Number.isFinite(total)
    ? total
    : 0;
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

    if (
      value == null ||
      String(value).trim() === ""
    ) {
      delete next[key];
    }
  });

  router.push({
    path:
      route.path ||
      "/busqueda",

    query: next,
  });
};

const setParam = (key, value) => {
  const patch = {
    [key]:
      String(value ?? "").trim() ||
      undefined,
  };

  if (
    [
      "year",
      "month",
      "type",
      "sort",
      "has_pdf",
      "author_id",
    ].includes(key)
  ) {
    patch.page = undefined;
  }

  setQuery(patch);
};

const submitInlineSearch = () => {
  const query =
    String(
      inlineQuery.value || ""
    ).trim();

  if (!query) {
    resetSearch();
    return;
  }

  nextSearchPreferredScope.value = "";
  userSelectedScope.value = false;
  activeScope.value = "pubs";

  setQuery({
    q: query,
    author_id: undefined,
    year: undefined,
    month: undefined,
    type: undefined,
    has_pdf: undefined,
    sort: "relevance",
    page: undefined,
    profile_page: undefined,
  });
};

const applySuggestion = (suggestion) => {
  inlineQuery.value = suggestion;
  submitInlineSearch();
};

const resetSearch = () => {
  inlineQuery.value = "";

  activeScope.value = "pubs";
  userSelectedScope.value = false;
  nextSearchPreferredScope.value = "";

  router.push({
    path:
      route.path ||
      "/busqueda",

    query: {},
  });
};

const clearRefinementFilters = () => {
  setQuery({
    year: undefined,
    month: undefined,
    type: undefined,
    has_pdf: undefined,
    sort: "relevance",
    page: undefined,
  });
};

const handleScopeClick = (scope) => {
  activeScope.value =
    scope === "profiles"
      ? "profiles"
      : "pubs";

  userSelectedScope.value = true;
};

function clearAuthor() {
  nextSearchPreferredScope.value = "";
  userSelectedScope.value = false;
  activeScope.value = "pubs";

  setParam("author_id", "");
}

const goToPublicationsPage = (page) => {
  const nextPage = Math.min(
    pubsTotalPages.value,
    Math.max(
      1,
      Number(page) || 1
    )
  );

  if (
    nextPage === pubsCurrentPage.value
  ) {
    return;
  }

  setQuery({
    page:
      nextPage > 1
        ? String(nextPage)
        : undefined,
  });
};

const goToProfilesPage = (page) => {
  const nextPage = Math.min(
    profilesTotalPages.value,
    Math.max(
      1,
      Number(page) || 1
    )
  );

  if (
    nextPage === profilesCurrentPage.value
  ) {
    return;
  }

  setQuery({
    profile_page:
      nextPage > 1
        ? String(nextPage)
        : undefined,
  });
};

const openProfile = (id) => {
  const profileId =
    String(id || "").trim();

  if (!profileId) {
    return;
  }

  if (
    myAuthorId.value &&
    profileId === myAuthorId.value
  ) {
    router.push("/perfil/me");
    return;
  }

  router.push({
    path: `/perfil/${profileId}`,

    query:
      state.value.q
        ? {
            q: state.value.q,
          }
        : {},
  });
};

const openAuthorFromResults = (author) => {
  if (author?.id) {
    openProfile(author.id);
    return;
  }

  const name =
    String(
      author?.name || ""
    ).trim();

  if (!name) {
    return;
  }

  nextSearchPreferredScope.value =
    "profiles";

  activeScope.value =
    "profiles";

  userSelectedScope.value =
    true;

  setQuery({
    q: name,
    author_id: undefined,
    page: undefined,
    profile_page: undefined,
  });
};

const openPublication = (id) => {
  const publicationId =
    String(id || "").trim();

  if (!publicationId) {
    return;
  }

  router.push(
    `/publicacion/${publicationId}`
  );
};

const openPdf = (url) => {
  if (!url) {
    return;
  }

  window.open(
    url,
    "_blank",
    "noopener,noreferrer"
  );
};

const isStaleRequest = (id) => {
  return id !== requestSerial.value;
};

watch(
  () => state.value.q,
  (query) => {
    inlineQuery.value = query || "";
  },
  {
    immediate: true,
  }
);

watch(
  currentSearchKey,
  (next, previous) => {
    if (previous === undefined) {
      return;
    }

    if (next === previous) {
      return;
    }

    if (nextSearchPreferredScope.value) {
      activeScope.value =
        nextSearchPreferredScope.value;

      userSelectedScope.value = true;
      nextSearchPreferredScope.value = "";

      return;
    }

    activeScope.value = "pubs";
    userSelectedScope.value = false;
  },
  {
    immediate: true,
  }
);

const runSearch = async () => {
  const runId =
    ++requestSerial.value;

  const currentState =
    state.value;

  try {
    if (!hasSearched.value) {
      activeScope.value = "pubs";
      userSelectedScope.value = false;
      nextSearchPreferredScope.value = "";

      store.resetPublicacionesState?.();
      store.resetPerfilesState?.();

      await store.fetchAuthorApplied?.(
        null
      );

      return;
    }

    let profileQuery =
      String(
        currentState.q || ""
      ).trim();

    if (currentState.authorId) {
      await store.fetchAuthorApplied?.(
        currentState.authorId
      );

      if (isStaleRequest(runId)) {
        return;
      }

      if (!profileQuery) {
        profileQuery =
          String(
            store.authorApplied?.name ||
            ""
          ).trim();
      }
    } else {
      await store.fetchAuthorApplied?.(
        null
      );

      if (isStaleRequest(runId)) {
        return;
      }
    }

    const tasks = [
      store.searchPublicaciones?.({
        q:
          currentState.q ||
          "",

        year:
          currentState.year ||
          "",

        month:
          currentState.month ||
          "",

        type:
          currentState.type ||
          "",

        sort:
          currentState.sort ||
          "relevance",

        facets:
          "1",

        author_id:
          currentState.authorId ||
          "",

        has_pdf:
          currentState.hasPdf === "1"
            ? "1"
            : "",

        page:
          currentState.page,

        page_size:
          store.pubsPageSize ||
          PUBLICACIONES_PAGE_SIZE,
      }),
    ];

    if (profileQuery) {
      tasks.push(
        store.searchPerfiles?.({
          q: profileQuery,
          page:
            currentState.profilePage,

          pageSize:
            store.perfilesPageSize ||
            PERFILES_PAGE_SIZE,

          preload: "0",
        })
      );
    } else {
      store.resetPerfilesState?.();
    }

    await Promise.all(tasks);

    if (isStaleRequest(runId)) {
      return;
    }

    if (!userSelectedScope.value) {
      const publicationsFound =
        getVisiblePubsFound();

      const profilesFound =
        getProfilesFound();

      if (publicationsFound > 0) {
        activeScope.value = "pubs";
      } else if (profilesFound > 0) {
        activeScope.value = "profiles";
      } else {
        activeScope.value = "pubs";
      }
    }
  } catch {
    if (isStaleRequest(runId)) {
      return;
    }
  }
};

watch(
  () => route.query,
  runSearch,
  {
    deep: true,
    immediate: true,
  }
);
</script>

<style src="./busqueda.css"></style>