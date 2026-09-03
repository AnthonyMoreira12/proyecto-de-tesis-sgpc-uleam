<template>
  <div
    class="mispub"
    :data-tipo="tipoThemeCode"
  >
    <main class="mispub__wrap">
      <!-- =====================================================
        ENCABEZADO
      ====================================================== -->
      <header
        class="mispub-header page-stage page-stage-1"
        aria-label="Mis publicaciones"
      >
        <div class="mispub-header__copy">
          <h1 class="mispub-title">
            Mis publicaciones
          </h1>

          <p class="mispub-subtitle">
            Revise sus publicaciones, consulte su estado y realice las acciones disponibles.
          </p>
        </div>
      </header>

      <!-- =====================================================
        BÚSQUEDA
      ====================================================== -->
      <section
        class="mispub-discovery page-stage page-stage-2"
        aria-label="Buscar en mis publicaciones"
      >
        <MisPublicacionesSearchField
          ref="searchEl"
          v-model="q"
          placeholder="Buscar por título, autor o proyecto"
        />
      </section>

      <!-- =====================================================
        FILTROS
      ====================================================== -->
      <section
        class="mispub-filters page-stage page-stage-3"
        aria-label="Filtros de mis publicaciones"
      >
        <div class="mispub-filters__topline">
          <div>
            <h2 class="mispub-section-title">
              Filtros
            </h2>
          </div>

          <div class="mispub-filters__status">
            <button
              v-if="canClearFilters"
              type="button"
              class="mispub-text-action"
              @click="clearAllFilters"
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        <div class="mispub-quick-filters">
          <div class="mispub-field">
            <label
              class="mispub-label"
              for="mispub-sede"
            >
              Sede
            </label>

            <select
              id="mispub-sede"
              v-model="filtroSede"
              class="mispub-select"
              @change="onMainSedeChange"
            >
              <option value="">
                Todas las sedes
              </option>

              <option
                v-for="sede in sedes"
                :key="`sede-${sede.id}`"
                :value="String(sede.id)"
              >
                {{ getCatalogLabel(sede) }}
              </option>
            </select>
          </div>

          <div class="mispub-field">
            <label
              class="mispub-label"
              for="mispub-facultad"
            >
              Facultad
            </label>

            <select
              id="mispub-facultad"
              v-model="filtroFacultad"
              class="mispub-select"
              @change="onMainFacultadChange"
            >
              <option value="">
                Todas las facultades
              </option>

              <option
                v-for="facultad in facultades"
                :key="`facultad-${facultad.id}`"
                :value="String(facultad.id)"
              >
                {{ getCatalogLabel(facultad) }}
              </option>
            </select>
          </div>

          <div class="mispub-field">
            <label
              class="mispub-label"
              for="mispub-carrera"
            >
              Carrera
            </label>

            <select
              id="mispub-carrera"
              v-model="filtroCarrera"
              class="mispub-select"
              :disabled="!filtroSede && !filtroFacultad"
              @change="onMainCarreraChange"
            >
              <option value="">
                {{
                  filtroSede || filtroFacultad
                    ? "Todas las carreras"
                    : "Seleccione sede o facultad"
                }}
              </option>

              <option
                v-for="carrera in carreras"
                :key="`carrera-${carrera.id}`"
                :value="String(carrera.id)"
              >
                {{ getCatalogLabel(carrera) }}
              </option>
            </select>
          </div>

          <div class="mispub-field">
            <label
              class="mispub-label"
              for="mispub-estado"
            >
              Estado
            </label>

            <select
              id="mispub-estado"
              v-model="filtroEstado"
              class="mispub-select"
            >
              <option
                v-for="estado in ESTADOS_FILTER_LIST"
                :key="`estado-${estado.value}`"
                :value="estado.value"
              >
                {{ estado.label }}
              </option>
            </select>
          </div>

          <div class="mispub-field">
            <label
              class="mispub-label"
              for="mispub-orden"
            >
              Ordenar por
            </label>

            <select
              id="mispub-orden"
              v-model="orden"
              class="mispub-select"
            >
              <option
                v-for="option in ORDENES"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <label
            class="mispub-pdf-toggle"
            for="mispub-solo-pdf"
          >
            <input
              id="mispub-solo-pdf"
              v-model="soloConPdf"
              class="mispub-pdf-toggle__input"
              type="checkbox"
            />

            <span
              class="mispub-pdf-toggle__control"
              aria-hidden="true"
            >
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="m9.2 16.2-3.4-3.4 1.4-1.4 2 2 7.6-7.6 1.4 1.4-9 9Z"
                />
              </svg>
            </span>

            <span>Solo con documento</span>
          </label>
        </div>

        <button
          type="button"
          class="mispub-advanced-trigger"
          :class="{
            'is-open': filtrosAvanzadosAbiertos,
            'has-active': advancedFiltersCount > 0,
          }"
          :aria-expanded="filtrosAvanzadosAbiertos"
          aria-controls="mispub-advanced-filters"
          @click="filtrosAvanzadosAbiertos = !filtrosAvanzadosAbiertos"
        >
          <span class="mispub-advanced-trigger__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M4 6h10v2H4V6Zm0 10h6v2H4v-2Zm0-5h16v2H4v-2Zm14-7h2v6h-2V4Zm-6 10h2v6h-2v-6Z"
              />
            </svg>
          </span>

          <span class="mispub-advanced-trigger__copy">
            <strong>Más filtros</strong>
            <small>Proyecto, origen y período</small>
          </span>

          <span
            v-if="advancedFiltersCount"
            class="mispub-advanced-trigger__count"
          >
            {{ advancedFiltersCount }}
          </span>

          <span
            class="mispub-advanced-trigger__chevron"
            aria-hidden="true"
          >
            ⌄
          </span>
        </button>

        <Transition name="filters-advanced">
          <div
            v-if="filtrosAvanzadosAbiertos"
            id="mispub-advanced-filters"
            class="mispub-advanced"
          >
            <div class="mispub-advanced__row mispub-advanced__row--two">
              <div class="mispub-field">
                <label
                  class="mispub-label"
                  for="mispub-proyecto"
                >
                  Proyecto
                </label>

                <select
                  id="mispub-proyecto"
                  v-model="filtroProyecto"
                  class="mispub-select"
                  :disabled="!filtroCarrera"
                >
                  <option value="">
                    {{ filtroCarrera ? "Todos los proyectos" : "Seleccione una carrera" }}
                  </option>

                  <option
                    v-for="proyecto in proyectos"
                    :key="`proyecto-${proyecto.id}`"
                    :value="String(proyecto.id)"
                  >
                    {{ getCatalogLabel(proyecto) }}
                  </option>
                </select>
              </div>

              <div class="mispub-field">
                <label
                  class="mispub-label"
                  for="mispub-origen"
                >
                  Origen
                </label>

                <select
                  id="mispub-origen"
                  v-model="filtroOrigen"
                  class="mispub-select"
                >
                  <option
                    v-for="origen in ORIGENES_LIST"
                    :key="origen.value"
                    :value="origen.value"
                  >
                    {{ origen.label }}
                  </option>
                </select>
              </div>
            </div>

            <div class="mispub-period">
              <div class="mispub-period__head">
                <div>
                  <strong>Período</strong>
                  <span>Elija un año concreto o un rango de años.</span>
                </div>
              </div>

              <div class="mispub-period__options">
                <div class="mispub-period__group">
                  <span class="mispub-period__label">
                    Año y mes
                  </span>

                  <div class="mispub-period__controls">
                    <div class="mispub-field">
                      <label
                        class="mispub-label mispub-label--muted"
                        for="mispub-anio"
                      >
                        Año
                      </label>

                      <select
                        id="mispub-anio"
                        v-model="filtroAnio"
                        class="mispub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnioDesde || filtroAnioHasta)"
                      >
                        <option value="">
                          {{
                            loadingAnios
                              ? "Cargando años…"
                              : añosDisponibles.length
                                ? "Todos los años"
                                : "Sin años disponibles"
                          }}
                        </option>

                        <option
                          v-for="anio in añosDisponibles"
                          :key="`exact-${anio}`"
                          :value="String(anio)"
                        >
                          {{ anio }}
                        </option>
                      </select>
                    </div>

                    <div class="mispub-field">
                      <label
                        class="mispub-label mispub-label--muted"
                        for="mispub-mes"
                      >
                        Mes
                      </label>

                      <select
                        id="mispub-mes"
                        v-model="filtroMes"
                        class="mispub-select"
                      >
                        <option
                          v-for="mes in MESES_LIST"
                          :key="`mes-${mes.value || 'all'}`"
                          :value="mes.value"
                        >
                          {{ mes.label }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>

                <span class="mispub-period__separator">
                  o
                </span>

                <div class="mispub-period__group">
                  <span class="mispub-period__label">
                    Rango
                  </span>

                  <div class="mispub-period__controls">
                    <div class="mispub-field">
                      <label
                        class="mispub-label mispub-label--muted"
                        for="mispub-anio-desde"
                      >
                        Desde
                      </label>

                      <select
                        id="mispub-anio-desde"
                        v-model="filtroAnioDesde"
                        class="mispub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
                      >
                        <option value="">
                          Sin mínimo
                        </option>

                        <option
                          v-for="anio in añosDisponibles"
                          :key="`desde-${anio}`"
                          :value="String(anio)"
                        >
                          {{ anio }}
                        </option>
                      </select>
                    </div>

                    <div class="mispub-field">
                      <label
                        class="mispub-label mispub-label--muted"
                        for="mispub-anio-hasta"
                      >
                        Hasta
                      </label>

                      <select
                        id="mispub-anio-hasta"
                        v-model="filtroAnioHasta"
                        class="mispub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
                      >
                        <option value="">
                          Sin máximo
                        </option>

                        <option
                          v-for="anio in añosDisponibles"
                          :key="`hasta-${anio}`"
                          :value="String(anio)"
                        >
                          {{ anio }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>

        <div
          v-if="activeFilterChips.length"
          class="mispub-active-filters"
          aria-label="Filtros activos"
        >
          <span class="mispub-active-filters__label">
            Aplicados
          </span>

          <button
            v-for="chip in activeFilterChips"
            :key="chip.key"
            type="button"
            class="mispub-filter-chip"
            :aria-label="`Quitar filtro ${chip.label}`"
            @click="removeActiveFilter(chip.key)"
          >
            <span>{{ chip.label }}</span>
            <span aria-hidden="true">×</span>
          </button>
        </div>
      </section>

      <!-- =====================================================
        MENSAJES DEL WORKFLOW
      ====================================================== -->
      <section
        v-if="pdfErrorMsg || workflowMessage || workflowError"
        class="mispub-feedback page-stage page-stage-4"
        aria-live="polite"
      >
        <div
          v-if="pdfErrorMsg"
          class="mispub-alert mispub-alert--error"
          role="alert"
        >
          <span>{{ pdfErrorMsg }}</span>
          <button type="button" @click="pdfErrorMsg = ''">
            Cerrar
          </button>
        </div>

        <div
          v-if="workflowMessage || workflowError"
          class="mispub-alert"
          :class="workflowError ? 'mispub-alert--error' : 'mispub-alert--success'"
          :role="workflowError ? 'alert' : 'status'"
        >
          <span>{{ workflowError || workflowMessage }}</span>
          <button type="button" @click="clearWorkflowFeedback">
            Cerrar
          </button>
        </div>
      </section>

      <!-- =====================================================
        RESULTADOS
      ====================================================== -->
      <section
        class="mispub-results page-stage page-stage-4"
        aria-label="Resultados de mis publicaciones"
      >
        <div class="mispub-results__head">
          <div>
            <h2 class="mispub-results__title">
              {{ totalResultados }}
              {{ totalResultados === 1 ? "publicación" : "publicaciones" }}
            </h2>

            <p>
              Revise el estado y use las acciones disponibles en cada publicación.
            </p>
          </div>

          <div
            class="mispub-view-switch"
            role="group"
            aria-label="Vista de resultados"
          >
            <button
              type="button"
              :class="{ 'is-active': vista === 'cards' }"
              :aria-pressed="vista === 'cards'"
              @click="vista = 'cards'"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path fill="currentColor" d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z" />
              </svg>
              Tarjetas
            </button>

            <button
              type="button"
              :class="{ 'is-active': vista === 'tabla' }"
              :aria-pressed="vista === 'tabla'"
              @click="vista = 'tabla'"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path fill="currentColor" d="M4 5h16v3H4V5Zm0 5h16v3H4v-3Zm0 5h16v3H4v-3Z" />
              </svg>
              Tabla
            </button>
          </div>
        </div>

        <div
          class="mispub-type-filter"
          aria-label="Tipo de publicación"
        >
          <span class="mispub-type-filter__label">
            Tipo
          </span>

          <div class="mispub-type-filter__chips">
            <button
              v-for="tipo in TIPOS_LIST"
              :key="tipo.value"
              type="button"
              class="mispub-type-filter__chip"
              :class="{ 'is-active': filtro.value === tipo.value }"
              :aria-pressed="filtro.value === tipo.value"
              @click="cambiarFiltro(tipo)"
            >
              <span
                class="mispub-type-filter__dot"
                :data-tipo="tipo.value"
                aria-hidden="true"
              ></span>

              <span>{{ tipo.label }}</span>
              <strong>{{ countByType(tipo.value) }}</strong>
            </button>
          </div>
        </div>

        <!-- Carga -->
        <div
          v-if="loading"
          class="mispub-state"
          aria-live="polite"
        >
          <div
            v-if="vista === 'cards'"
            class="mispub-skeleton-grid"
            aria-label="Cargando publicaciones"
          >
            <div
              v-for="n in 6"
              :key="n"
              class="mispub-skeleton-card"
            >
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>

          <div
            v-else
            class="mispub-loading-line"
          >
            Cargando publicaciones…
          </div>
        </div>

        <!-- Vacío / error -->
        <div
          v-else-if="publicacionesFiltradas.length === 0"
          class="mispub-empty"
          :class="{ 'is-error': Boolean(errorMsg) }"
          :role="errorMsg ? 'alert' : 'status'"
        >
          <div class="mispub-empty__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M4 3h11l5 5v13H4V3Zm2 2v14h12V9h-4V5H6Zm3 8h6v2H9v-2Zm0-4h3v2H9V9Z"
              />
            </svg>
          </div>

          <h3>
            {{ errorMsg ? "No pudimos cargar sus publicaciones" : "No encontramos publicaciones" }}
          </h3>

          <p>{{ emptyMessage }}</p>

          <button
            v-if="errorMsg"
            type="button"
            class="mispub-btn mispub-btn--primary"
            @click="cargarPublicaciones({ forceLoading: true })"
          >
            Reintentar
          </button>

          <button
            v-else-if="canClearFilters"
            type="button"
            class="mispub-btn mispub-btn--primary"
            @click="clearAllFilters"
          >
            Limpiar filtros
          </button>
        </div>

        <template v-else>
          <!-- Vista de tarjetas -->
          <div
            v-if="vista === 'cards'"
            class="mispub-grid page-stagger page-stagger--mid"
          >
            <article
              v-for="pub in publicacionesFiltradas"
              :key="pub.id"
              class="mispub-card"
              :data-tipo="resolveType(pub)"
            >
              <div class="mispub-card__accent" aria-hidden="true"></div>

              <div class="mispub-card__head">
                <div class="mispub-card__badges">
                  <span
                    class="mispub-badge"
                    :data-tipo="resolveType(pub)"
                  >
                    <span class="mispub-badge__dot" aria-hidden="true"></span>
                    {{ resolveLabel(pub) }}
                  </span>

                  <span
                    class="mispub-status"
                    :data-estado="resolveEstadoValue(pub)"
                  >
                    {{ resolveEstadoLabel(pub) }}
                  </span>
                </div>

                <time
                  class="mispub-date"
                  :datetime="publicationPeriodDatetime(pub)"
                >
                  {{ formatPublicationPeriod(pub) }}
                </time>
              </div>

              <div class="mispub-card__body">
                <RouterLink
                  class="mispub-card__title-link"
                  :to="`/publicacion/${pub.id}`"
                  :aria-label="`Ver publicación ${pub.titulo || ''}`"
                >
                  <h3
                    class="mispub-card__title"
                    :title="pub.titulo || 'Sin título'"
                  >
                    {{ pub.titulo || "Sin título" }}
                  </h3>
                </RouterLink>

                <div
                  v-if="pub.autor"
                  class="mispub-card__section"
                >
                  <span class="mispub-card__section-label">
                    Autores
                  </span>
                  <p
                    class="mispub-card__authors"
                    :title="pub.autor"
                  >
                    {{ pub.autor }}
                  </p>
                </div>

                <div
                  class="mispub-card__academic"
                  :title="buildAcademicMeta(pub)"
                >
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M12 3 2 8l10 5 8-4v6h2V8L12 3Zm-6 9.1V16c0 2.2 2.7 4 6 4s6-1.8 6-4v-3.9l-6 3-6-3Z"
                    />
                  </svg>
                  <span>{{ buildAcademicMeta(pub) }}</span>
                </div>

                <div
                  v-if="pub.proyecto || resolveOrigenResumen(pub) || hasPdf(pub)"
                  class="mispub-card__tags"
                  aria-label="Información adicional"
                >
                  <span
                    v-if="pub.proyecto"
                    class="mispub-meta-chip mispub-meta-chip--project"
                    :title="pub.proyecto"
                  >
                    {{ pub.proyecto }}
                  </span>

                  <span
                    v-if="resolveOrigenResumen(pub)"
                    class="mispub-meta-chip mispub-meta-chip--origin"
                    :title="resolveOrigenResumen(pub)"
                  >
                    {{ resolveOrigenResumen(pub) }}
                  </span>

                  <span
                    v-if="hasPdf(pub)"
                    class="mispub-meta-chip mispub-meta-chip--pdf"
                  >
                    Documento disponible
                  </span>
                </div>

                <div
                  v-if="resolveWorkflowHint(pub)"
                  class="mispub-workflow"
                  :data-estado="resolveEstadoValue(pub)"
                >
                  <span class="mispub-workflow__dot" aria-hidden="true"></span>
                  <span>{{ resolveWorkflowHint(pub) }}</span>
                </div>
              </div>

              <footer class="mispub-card__footer">
                <button
                  type="button"
                  class="mispub-card__detail"
                  @click="verDetalles(pub.id)"
                >
                  {{ verActionLabel(pub) }}
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="m13.2 5.6 6.4 6.4-6.4 6.4-1.4-1.4 4-4H4v-2h11.8l-4-4 1.4-1.4Z"
                    />
                  </svg>
                </button>

                <div class="mispub-card__actions">
                  <button
                    v-if="puedeEditarDesdeListado(pub)"
                    type="button"
                    class="mispub-action"
                    :disabled="workflowPublicationId !== null"
                    @click="editarPublicacion(pub.id)"
                  >
                    Editar
                  </button>

                  <button
                    v-if="puedeEnviarDesdeListado(pub)"
                    type="button"
                    class="mispub-action mispub-action--primary"
                    :disabled="workflowPublicationId !== null"
                    @click="enviarARevisionDesdeListado(pub)"
                  >
                    {{
                      isWorkflowLoading(pub.id, "enviar")
                        ? "Enviando…"
                        : "Enviar a revisión"
                    }}
                  </button>

                  <button
                    v-if="puedeReenviarDesdeListado(pub)"
                    type="button"
                    class="mispub-action mispub-action--warning"
                    :disabled="workflowPublicationId !== null"
                    @click="reenviarARevisionDesdeListado(pub)"
                  >
                    {{
                      isWorkflowLoading(pub.id, "reenviar")
                        ? "Reenviando…"
                        : "Reenviar"
                    }}
                  </button>

                  <button
                    v-if="hasPdf(pub)"
                    type="button"
                    class="mispub-action"
                    :disabled="openingPdfId !== null"
                    @click="abrirPdf(pub)"
                  >
                    {{ openingPdfId === pub.id ? "Abriendo…" : "Documento" }}
                  </button>
                </div>
              </footer>
            </article>
          </div>

          <!-- Vista de tabla -->
          <div
            v-else
            class="mispub-table-wrap"
            role="region"
            aria-label="Tabla detallada de publicaciones"
            tabindex="0"
          >
            <table class="mispub-table">
              <thead>
                <tr>
                  <th scope="col">Tipo</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Título</th>
                  <th scope="col">Origen</th>
                  <th scope="col">Proyecto</th>
                  <th scope="col">Período</th>
                  <th scope="col">Sede</th>
                  <th scope="col">Facultad</th>
                  <th scope="col">Carrera</th>
                  <th scope="col" class="mispub-table__actions-head">
                    Opciones
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="pub in publicacionesFiltradas"
                  :key="pub.id"
                >
                  <td data-label="Tipo">
                    <span
                      class="mispub-table-badge"
                      :data-tipo="resolveType(pub)"
                    >
                      {{ resolveLabel(pub) }}
                    </span>
                  </td>

                  <td data-label="Estado">
                    <span
                      class="mispub-status mispub-status--table"
                      :data-estado="resolveEstadoValue(pub)"
                    >
                      {{ resolveEstadoLabel(pub) }}
                    </span>
                  </td>

                  <td class="mispub-table__title-cell" data-label="Publicación">
                    <RouterLink
                      class="mispub-table__title-link"
                      :to="`/publicacion/${pub.id}`"
                    >
                      {{ pub.titulo || "Sin título" }}
                    </RouterLink>
                  </td>

                  <td data-label="Origen">{{ resolveOrigenResumen(pub) || "—" }}</td>
                  <td data-label="Proyecto">{{ pub.proyecto || "—" }}</td>
                  <td data-label="Período">{{ formatPublicationPeriod(pub) }}</td>
                  <td data-label="Sede">{{ pub.sede || "—" }}</td>
                  <td data-label="Facultad">{{ pub.facultad || "—" }}</td>
                  <td data-label="Carrera">{{ pub.carrera || "—" }}</td>

                  <td data-label="Acciones">
                    <div class="mispub-table__actions">
                      <button
                        class="mispub-action"
                        type="button"
                        @click="verDetalles(pub.id)"
                      >
                        {{ verActionLabel(pub) }}
                      </button>

                      <button
                        v-if="puedeEditarDesdeListado(pub)"
                        class="mispub-action"
                        type="button"
                        :disabled="workflowPublicationId !== null"
                        @click="editarPublicacion(pub.id)"
                      >
                        Editar
                      </button>

                      <button
                        v-if="puedeEnviarDesdeListado(pub)"
                        class="mispub-action mispub-action--primary"
                        type="button"
                        :disabled="workflowPublicationId !== null"
                        @click="enviarARevisionDesdeListado(pub)"
                      >
                        {{
                          isWorkflowLoading(pub.id, "enviar")
                            ? "Enviando…"
                            : "Enviar"
                        }}
                      </button>

                      <button
                        v-if="puedeReenviarDesdeListado(pub)"
                        class="mispub-action mispub-action--warning"
                        type="button"
                        :disabled="workflowPublicationId !== null"
                        @click="reenviarARevisionDesdeListado(pub)"
                      >
                        {{
                          isWorkflowLoading(pub.id, "reenviar")
                            ? "Reenviando…"
                            : "Reenviar"
                        }}
                      </button>

                      <button
                        v-if="hasPdf(pub)"
                        class="mispub-action"
                        type="button"
                        :disabled="openingPdfId !== null"
                        @click="abrirPdf(pub)"
                      >
                        {{ openingPdfId === pub.id ? "Abriendo…" : "Documento" }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </section>
    </main>

    <NoticeDialog
      :modelValue="notice"
      @close="closeNotice"
    />
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

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";
import { useNotice } from "../../scripts/composables/useNotice";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import MisPublicacionesSearchField from "./MisPublicacionesSearchField.vue";

import {
  enviarPublicacionRevision,
  reenviarPublicacionRevision,
} from "../../scripts/api/publicacionesApi";

import {
  ESTADO_PUBLICACION,
  ESTADOS_PUBLICACION,
  obtenerEstadoPublicacion,
  puedeEditarPublicacion,
  puedeEnviarRevision,
  puedeReenviarRevision,
} from "../../scripts/utils/publicacion-estados";

import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

/* ============================================================
  CONFIGURACIÓN
============================================================ */

const LIST_ENDPOINT = "/publicaciones/mias/";
const YEARS_ENDPOINT = "/publicaciones/mias/anios-disponibles/";
const SEDES_ENDPOINT = "/selects/sedes/";
const FACULTADES_ENDPOINT = "/selects/facultades/";

const FILTER_DEBOUNCE_MS = 350;
const ROUTE_SYNC_DEBOUNCE_MS = 180;
const PDF_URL_REVOKE_DELAY_MS = 60_000;

/* ============================================================
  NAVEGACIÓN
============================================================ */

const route = useRoute();
const router = useRouter();

const {
  notice,
  openNotice,
  closeNotice,
} = useNotice();

/* ============================================================
  TIPOS DE PUBLICACIÓN
============================================================ */

const TIPOS = Object.freeze({
  ALL: Object.freeze({
    label: "Todos",
    value: "ALL",
    apiValue: "",
  }),

  AAI: Object.freeze({
    label: PUBLICACION_TIPOS.AAI.label,
    value: PUBLICACION_TIPOS.AAI.codigo,
    apiValue: PUBLICACION_TIPOS.AAI.apiCodigo,
  }),

  AR: Object.freeze({
    label: PUBLICACION_TIPOS.AR.label,
    value: PUBLICACION_TIPOS.AR.codigo,
    apiValue: PUBLICACION_TIPOS.AR.apiCodigo,
  }),

  PON: Object.freeze({
    label: PUBLICACION_TIPOS.PON.label,
    value: PUBLICACION_TIPOS.PON.codigo,
    apiValue: PUBLICACION_TIPOS.PON.apiCodigo,
  }),

  CAP: Object.freeze({
    label: PUBLICACION_TIPOS.CAP.label,
    value: PUBLICACION_TIPOS.CAP.codigo,
    apiValue: PUBLICACION_TIPOS.CAP.apiCodigo,
  }),

  LIB: Object.freeze({
    label: PUBLICACION_TIPOS.LIB.label,
    value: PUBLICACION_TIPOS.LIB.codigo,
    apiValue: PUBLICACION_TIPOS.LIB.apiCodigo,
  }),
});

const TIPOS_LIST = Object.freeze([
  TIPOS.ALL,
  TIPOS.AAI,
  TIPOS.AR,
  TIPOS.PON,
  TIPOS.CAP,
  TIPOS.LIB,
]);

/* ============================================================
  ORÍGENES
============================================================ */

const ORIGENES_LIST = Object.freeze([
  {
    label: "Todos los orígenes",
    value: "ALL",
  },
  {
    label: "Sin origen académico",
    value: "ninguno",
  },
  {
    label: "Trabajo de integración curricular",
    value: "tic",
  },
  {
    label: "Tesis de maestría",
    value: "maestria",
  },
  {
    label: "Tesis doctoral",
    value: "doctoral",
  },
  {
    label: "Otro",
    value: "otro",
  },
]);

const ORIGEN_LABELS = Object.freeze({
  ninguno: "Sin origen académico",
  tic: "Trabajo de integración curricular",
  maestria: "Tesis de maestría",
  doctoral: "Tesis doctoral",
  otro: "Otro",
});

/* ============================================================
  ORDENAMIENTO
============================================================ */

const ORDENES = Object.freeze([
  {
    label: "Más recientes",
    value: "recientes",
  },
  {
    label: "Más antiguas",
    value: "antiguas",
  },
  {
    label: "Título A–Z",
    value: "titulo_asc",
  },
  {
    label: "Título Z–A",
    value: "titulo_desc",
  },
  {
    label: "Tipo de publicación",
    value: "tipo",
  },
]);

const MESES_LIST = Object.freeze([
  { value: "", label: "Todos los meses" },
  { value: "1", label: "Enero" },
  { value: "2", label: "Febrero" },
  { value: "3", label: "Marzo" },
  { value: "4", label: "Abril" },
  { value: "5", label: "Mayo" },
  { value: "6", label: "Junio" },
  { value: "7", label: "Julio" },
  { value: "8", label: "Agosto" },
  { value: "9", label: "Septiembre" },
  { value: "10", label: "Octubre" },
  { value: "11", label: "Noviembre" },
  { value: "12", label: "Diciembre" },
]);

const ESTADOS_FILTER_LIST = Object.freeze([
  Object.freeze({
    value: "ALL",
    label: "Todos los estados",
  }),
  ...ESTADOS_PUBLICACION.map((estado) =>
    Object.freeze({
      value: estado.value,
      label: estado.label,
    })
  ),
]);

/* ============================================================
  DATOS PRINCIPALES
============================================================ */

const publicaciones = ref([]);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);

const totalPublicaciones = ref(0);
const totalResultados = ref(0);
const añosDisponibles = ref([]);

const typeCounts = ref(
  Object.fromEntries(
    TIPOS_LIST.map((tipo) => [
      tipo.value,
      0,
    ])
  )
);

/* ============================================================
  ESTADOS
============================================================ */

const loading = ref(true);
const loadingAnios = ref(true);
const errorMsg = ref("");
const pdfErrorMsg = ref("");
const openingPdfId = ref(null);

const workflowPublicationId = ref(null);
const workflowAction = ref("");
const workflowMessage = ref("");
const workflowError = ref("");

/* ============================================================
  ESTADO DE LA INTERFAZ
============================================================ */

const vista = ref("cards");
const filtrosAvanzadosAbiertos = ref(false);

const q = ref("");
const searchEl = ref(null);

const filtro = ref(TIPOS.ALL);
const filtroOrigen = ref("ALL");
const filtroEstado = ref("ALL");

const filtroSede = ref("");
const filtroFacultad = ref("");
const filtroCarrera = ref("");
const filtroProyecto = ref("");

const filtroAnio = ref("");
const filtroMes = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");

const soloConPdf = ref(false);
const orden = ref("recientes");

/* ============================================================
  CONTROL DE PETICIONES Y TEMPORIZADORES
============================================================ */

let routeSyncTimer = null;
let reloadTimer = null;

let listRequestSequence = 0;
let summaryRequestSequence = 0;
let typeCountRequestSequence = 0;
let yearsRequestSequence = 0;

let hasLoadedOnce = false;

/* ============================================================
  NORMALIZACIÓN DE RESPUESTAS
============================================================ */

function extractArray(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  if (Array.isArray(payload?.publicaciones)) {
    return payload.publicaciones;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}

function extractTotal(
  payload,
  fallback = 0
) {
  const total = Number(
    payload?.count ??
      payload?.total ??
      payload?.pagination?.count
  );

  return Number.isFinite(total)
    ? total
    : fallback;
}

function extractYears(payload) {
  const source = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.anios)
      ? payload.anios
      : [];

  return [
    ...new Set(
      source
        .map((value) => Number(value))
        .filter(
          (value) =>
            Number.isInteger(value) &&
            value > 0
        )
    ),
  ].sort((a, b) => b - a);
}

function extractErrorMessage(
  error,
  fallback = "No se pudieron cargar las publicaciones."
) {
  const status = Number(error?.response?.status || 0);

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

  const responseData = error?.response?.data;
  const detail =
    responseData?.detail ||
    responseData?.message ||
    responseData?.error;

  const text = Array.isArray(detail)
    ? detail.join(" ")
    : typeof detail === "string"
      ? detail
      : "";

  const technicalPattern =
    /(backend|endpoint|serializer|queryset|jwt|token|sql|postgres|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|http\s*\d{3}|request|response)/i;

  if (
    text &&
    text.length <= 240 &&
    !technicalPattern.test(text)
  ) {
    return text;
  }

  return fallback;
}

/* ============================================================
  NORMALIZACIÓN GENERAL
============================================================ */

function normalizeText(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function normalizeQueryValue(value) {
  if (Array.isArray(value)) {
    return String(
      value[0] ?? ""
    ).trim();
  }

  return String(
    value ?? ""
  ).trim();
}

function normalizeBooleanQuery(value) {
  return [
    "1",
    "true",
    "si",
    "sí",
    "yes",
    "on",
  ].includes(
    normalizeQueryValue(value).toLowerCase()
  );
}

function getCatalogLabel(item) {
  return (
    String(
      item?.label ??
        item?.nombre ??
        item?.name ??
        item?.titulo ??
        ""
    ).trim() ||
    "Sin nombre"
  );
}

function catalogContainsId(
  catalog,
  value
) {
  const normalized = String(
    value ?? ""
  );

  return catalog.some(
    (item) =>
      String(item?.id ?? "") === normalized
  );
}

/* ============================================================
  PERÍODOS Y AÑOS
============================================================ */

function resolvePublicationYear(publicacion) {
  const year = Number(
    publicacion?.anio_publicacion ??
      publicacion?.anio ??
      publicacion?.year
  );

  return Number.isInteger(year) && year > 0
    ? year
    : null;
}

function resolvePublicationMonth(publicacion) {
  const month = Number(
    publicacion?.mes_publicacion ??
      publicacion?.mes ??
      publicacion?.month
  );

  return (
    Number.isInteger(month) &&
    month >= 1 &&
    month <= 12
  )
    ? month
    : null;
}

function formatPublicationPeriod(publicacion) {
  const year =
    resolvePublicationYear(publicacion);

  if (!year) {
    return "Sin período";
  }

  const month =
    resolvePublicationMonth(publicacion);

  if (!month) {
    return String(year);
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      month: "long",
      year: "numeric",
    }
  ).format(
    new Date(
      year,
      month - 1,
      1
    )
  );
}

function publicationPeriodDatetime(publicacion) {
  const year =
    resolvePublicationYear(publicacion);

  if (!year) {
    return "";
  }

  const month =
    resolvePublicationMonth(publicacion);

  return month
    ? `${year}-${String(month).padStart(2, "0")}`
    : String(year);
}

function normalizeSelectedYearRange() {
  const desde = Number(
    filtroAnioDesde.value
  );

  const hasta = Number(
    filtroAnioHasta.value
  );

  if (
    !Number.isInteger(desde) ||
    !Number.isInteger(hasta)
  ) {
    return;
  }

  if (desde > hasta) {
    const previousDesde =
      filtroAnioDesde.value;

    filtroAnioDesde.value =
      filtroAnioHasta.value;

    filtroAnioHasta.value =
      previousDesde;
  }
}

function syncSelectedYearsWithCatalog() {
  const availableYears = new Set(
    añosDisponibles.value.map(
      (value) => String(value)
    )
  );

  if (
    filtroAnio.value &&
    !availableYears.has(
      String(filtroAnio.value)
    )
  ) {
    filtroAnio.value = "";
  }

  if (
    filtroAnioDesde.value &&
    !availableYears.has(
      String(filtroAnioDesde.value)
    )
  ) {
    filtroAnioDesde.value = "";
  }

  if (
    filtroAnioHasta.value &&
    !availableYears.has(
      String(filtroAnioHasta.value)
    )
  ) {
    filtroAnioHasta.value = "";
  }

  normalizeSelectedYearRange();
}

/* ============================================================
  METADATOS DE PUBLICACIÓN
============================================================ */

function getResolvedMeta(item) {
  return (
    item?.__tipoMeta ||
    getTipoPublicacionMetaFromItem(item)
  );
}

function resolveType(item) {
  const meta = getResolvedMeta(item);

  return meta?.codigo || "OTRO";
}

function resolveLabel(item) {
  const meta = getResolvedMeta(item);

  if (
    meta?.codigo &&
    meta.codigo !== "OTRO"
  ) {
    return meta.label;
  }

  return (
    String(
      item?.tipo_publicacion_final_label ||
        item?.tipo_publicacion_final ||
        item?.tipo ||
        "Publicación"
    ).trim() ||
    "Publicación"
  );
}

function resolveOrigenCode(item) {
  const raw = String(
    item?.origen_tipo || ""
  )
    .trim()
    .toLowerCase();

  return raw || "ninguno";
}

function resolveOrigenLabel(item) {
  const code = resolveOrigenCode(item);

  return (
    String(
      item?.origen_tipo_label ||
        ORIGEN_LABELS[code] ||
        code
    ).trim() ||
    "Ninguno"
  );
}

function resolveOrigenResumen(item) {
  const provided = String(
    item?.origen_resumen || ""
  ).trim();

  if (provided) {
    return provided;
  }

  const code = resolveOrigenCode(item);

  if (
    !code ||
    code === "ninguno"
  ) {
    return "";
  }

  const label = resolveOrigenLabel(item);

  const detail = String(
    item?.origen_grado || ""
  ).trim();

  if (
    ["tic", "otro"].includes(code) &&
    detail
  ) {
    return `${label} · ${detail}`;
  }

  return label;
}

function resolveEstadoValue(item) {
  return (
    obtenerEstadoPublicacion(
      item?.estado
    ).value ||
    ""
  );
}

function resolveEstadoLabel(item) {
  return (
    String(
      item?.estado_label ||
        ""
    ).trim() ||
    obtenerEstadoPublicacion(
      item?.estado
    ).label
  );
}

function resolveWorkflowHint(item) {
  const estado =
    resolveEstadoValue(item);

  const hints = {
    [ESTADO_PUBLICACION.BORRADOR]:
      "Complete la información y envíela a revisión cuando esté lista.",

    [ESTADO_PUBLICACION.EN_REVISION]:
      "",

    [ESTADO_PUBLICACION.OBSERVADA]:
      "Revise las correcciones solicitadas.",

    [ESTADO_PUBLICACION.APROBADA]:
      "",

    [ESTADO_PUBLICACION.RECHAZADA]:
      "Consulte el motivo del rechazo.",
  };

  const baseHint =
    hints[estado] || "";

  const blockReason = String(
    item?.motivo_bloqueo_edicion || ""
  ).trim();

  if (
    blockReason &&
    !puedeEditarDesdeListado(item)
  ) {
    return baseHint
      ? `${baseHint} ${blockReason}`
      : blockReason;
  }

  return baseHint;
}

function verActionLabel(item) {
  const estado =
    resolveEstadoValue(item);

  if (
    estado ===
    ESTADO_PUBLICACION.OBSERVADA
  ) {
    return "Ver correcciones";
  }

  if (
    estado ===
    ESTADO_PUBLICACION.RECHAZADA
  ) {
    return "Ver motivo";
  }

  return "Ver publicación";
}

function puedeEditarDesdeListado(item) {
  if (
    typeof item?.puede_editar ===
    "boolean"
  ) {
    return item.puede_editar;
  }

  if (
    typeof item?.estado_editable ===
    "boolean"
  ) {
    return item.estado_editable;
  }

  return puedeEditarPublicacion(item);
}

function puedeEnviarDesdeListado(item) {
  if (
    typeof item?.puede_enviar_revision ===
    "boolean"
  ) {
    return item.puede_enviar_revision;
  }

  return (
    puedeEditarDesdeListado(item) &&
    puedeEnviarRevision(item)
  );
}

function puedeReenviarDesdeListado(item) {
  if (
    typeof item?.puede_reenviar_revision ===
    "boolean"
  ) {
    return item.puede_reenviar_revision;
  }

  return (
    puedeEditarDesdeListado(item) &&
    puedeReenviarRevision(item)
  );
}

function hasPdf(item) {
  return Boolean(
    item?.tiene_pdf ||
      item?.has_pdf ||
      item?.hasPdf
  );
}

function resolvePdfEndpoint(item) {
  const provided = String(
    item?.pdf_endpoint || ""
  ).trim();

  if (provided) {
    return provided;
  }

  return item?.id
    ? `/publicaciones/${item.id}/pdf/`
    : "";
}

function buildAcademicMeta(pub) {
  const sede = String(
    pub?.sede || ""
  ).trim();

  const facultad = String(
    pub?.facultad || ""
  ).trim();

  const carrera = String(
    pub?.carrera || ""
  ).trim();

  const parts = [
    sede,
    facultad,
    carrera,
  ].filter(Boolean);

  return (
    parts.join(" · ") ||
    "Sin ubicación académica"
  );
}

/* ============================================================
  CATÁLOGOS
============================================================ */

async function loadSedes() {
  try {
    const response = await api.get(
      SEDES_ENDPOINT
    );

    sedes.value = extractArray(
      response.data
    );
  } catch (error) {
    console.error(
      "Error cargando sedes:",
      error
    );

    sedes.value = [];
  }
}

async function loadFacultades() {
  try {
    const response = await api.get(
      FACULTADES_ENDPOINT
    );

    facultades.value = extractArray(
      response.data
    );
  } catch (error) {
    console.error(
      "Error cargando facultades:",
      error
    );

    facultades.value = [];
  }
}

async function fetchCarrerasByFacultad(
  facultadId
) {
  if (!facultadId) {
    return [];
  }

  const response = await api.get(
    `/selects/carreras/${facultadId}/`
  );

  return extractArray(response.data);
}

async function fetchCarrerasBySede(
  sedeId
) {
  if (!sedeId) {
    return [];
  }

  const response = await api.get(
    `/selects/carreras/sede/${sedeId}/`
  );

  return extractArray(response.data);
}

async function fetchCarrerasDisponibles() {
  const sedeId =
    filtroSede.value;

  const facultadId =
    filtroFacultad.value;

  if (!sedeId && !facultadId) {
    return [];
  }

  if (
    sedeId &&
    !facultadId
  ) {
    return fetchCarrerasBySede(
      sedeId
    );
  }

  if (
    facultadId &&
    !sedeId
  ) {
    return fetchCarrerasByFacultad(
      facultadId
    );
  }

  const [
    bySede,
    byFacultad,
  ] = await Promise.all([
    fetchCarrerasBySede(
      sedeId
    ),
    fetchCarrerasByFacultad(
      facultadId
    ),
  ]);

  const idsFacultad = new Set(
    byFacultad.map(
      (item) =>
        String(item?.id ?? "")
    )
  );

  return bySede.filter(
    (item) =>
      idsFacultad.has(
        String(item?.id ?? "")
      )
  );
}

async function fetchProyectosByCarrera(
  carreraId
) {
  if (!carreraId) {
    return [];
  }

  const response = await api.get(
    `/selects/proyectos/${carreraId}/`
  );

  return extractArray(response.data);
}

async function reloadCarreras({
  resetSelection = false,
} = {}) {
  if (resetSelection) {
    filtroCarrera.value = "";
    filtroProyecto.value = "";
  }

  carreras.value = [];
  proyectos.value = [];

  if (
    !filtroSede.value &&
    !filtroFacultad.value
  ) {
    filtroCarrera.value = "";
    filtroProyecto.value = "";
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasDisponibles();

    if (
      filtroCarrera.value &&
      !catalogContainsId(
        carreras.value,
        filtroCarrera.value
      )
    ) {
      filtroCarrera.value = "";
      filtroProyecto.value = "";
    }

    if (!filtroCarrera.value) {
      return;
    }

    proyectos.value =
      await fetchProyectosByCarrera(
        filtroCarrera.value
      );

    if (
      filtroProyecto.value &&
      !catalogContainsId(
        proyectos.value,
        filtroProyecto.value
      )
    ) {
      filtroProyecto.value = "";
    }
  } catch (error) {
    console.error(
      "Error cargando carreras/proyectos:",
      error
    );

    carreras.value = [];
    proyectos.value = [];
  }
}

async function loadDependentCatalogsFromState() {
  await reloadCarreras({
    resetSelection: false,
  });
}

async function onMainSedeChange() {
  await reloadCarreras({
    resetSelection: true,
  });
}

async function onMainFacultadChange() {
  await reloadCarreras({
    resetSelection: true,
  });
}

async function onMainCarreraChange() {
  filtroProyecto.value = "";
  proyectos.value = [];

  if (!filtroCarrera.value) {
    return;
  }

  try {
    proyectos.value =
      await fetchProyectosByCarrera(
        filtroCarrera.value
      );
  } catch (error) {
    console.error(
      "Error cargando proyectos:",
      error
    );

    proyectos.value = [];
  }
}

/* ============================================================
  ESTADO DESDE LA URL
============================================================ */

function resolveTipoFilterFromQuery(value) {
  const raw = normalizeQueryValue(
    value
  );

  if (!raw) {
    return TIPOS.ALL;
  }

  const normalized =
    raw.toLowerCase();

  return (
    TIPOS_LIST.find((item) => {
      return (
        item.value.toLowerCase() ===
          normalized ||
        String(
          item.apiValue || ""
        ).toLowerCase() === normalized
      );
    }) ||
    TIPOS.ALL
  );
}

function hydrateStateFromRoute() {
  filtro.value =
    resolveTipoFilterFromQuery(
      route.query.tipo
    );

  const origenQuery =
    normalizeQueryValue(
      route.query.origen
    ).toLowerCase();

  filtroOrigen.value =
    ORIGENES_LIST.some(
      (item) =>
        item.value === origenQuery
    )
      ? origenQuery
      : "ALL";

  q.value = normalizeQueryValue(
    route.query.q
  );

  const estadoQuery =
    normalizeQueryValue(
      route.query.estado
    ).toLowerCase();

  filtroEstado.value =
    ESTADOS_FILTER_LIST.some(
      (item) =>
        item.value === estadoQuery
    )
      ? estadoQuery
      : "ALL";

  filtroSede.value =
    normalizeQueryValue(
      route.query.sede
    );

  filtroFacultad.value =
    normalizeQueryValue(
      route.query.facultad
    );

  filtroCarrera.value =
    normalizeQueryValue(
      route.query.carrera
    );

  filtroProyecto.value =
    normalizeQueryValue(
      route.query.proyecto
    );

  filtroAnio.value =
    normalizeQueryValue(
      route.query.anio
    );

  const mesQuery =
    normalizeQueryValue(
      route.query.mes
    );

  filtroMes.value =
    MESES_LIST.some(
      (item) =>
        item.value === mesQuery
    )
      ? mesQuery
      : "";

  filtroAnioDesde.value =
    normalizeQueryValue(
      route.query.desde
    );

  filtroAnioHasta.value =
    normalizeQueryValue(
      route.query.hasta
    );

  soloConPdf.value =
    normalizeBooleanQuery(
      route.query.pdf
    );

  const orderQuery =
    normalizeQueryValue(
      route.query.orden
    );

  orden.value =
    ORDENES.some(
      (item) =>
        item.value === orderQuery
    )
      ? orderQuery
      : "recientes";

  const viewQuery =
    normalizeQueryValue(
      route.query.vista
    );

  vista.value =
    ["cards", "tabla"].includes(
      viewQuery
    )
      ? viewQuery
      : "cards";

  filtrosAvanzadosAbiertos.value = Boolean(
    filtroOrigen.value !== "ALL" ||
    filtroAnioDesde.value ||
    filtroAnioHasta.value ||
    soloConPdf.value ||
    orden.value !== "recientes"
  );

  if (filtroAnio.value) {
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  } else {
    normalizeSelectedYearRange();
  }
}

function buildStateQuery() {
  const query = {
    ...route.query,
  };

  const knownKeys = [
    "tipo",
    "origen",
    "q",
    "estado",
    "sede",
    "facultad",
    "carrera",
    "proyecto",
    "anio",
    "mes",
    "desde",
    "hasta",
    "pdf",
    "orden",
    "vista",
  ];

  knownKeys.forEach((key) => {
    delete query[key];
  });

  if (
    filtro.value?.value !== "ALL"
  ) {
    query.tipo =
      filtro.value.value;
  }

  if (
    filtroOrigen.value !== "ALL"
  ) {
    query.origen =
      filtroOrigen.value;
  }

  if (q.value.trim()) {
    query.q = q.value.trim();
  }

  if (
    filtroEstado.value !== "ALL"
  ) {
    query.estado =
      filtroEstado.value;
  }

  if (filtroSede.value) {
    query.sede =
      filtroSede.value;
  }

  if (filtroFacultad.value) {
    query.facultad =
      filtroFacultad.value;
  }

  if (filtroCarrera.value) {
    query.carrera =
      filtroCarrera.value;
  }

  if (filtroProyecto.value) {
    query.proyecto =
      filtroProyecto.value;
  }

  if (filtroAnio.value) {
    query.anio =
      filtroAnio.value;
  }

  if (filtroMes.value) {
    query.mes =
      filtroMes.value;
  }

  if (filtroAnioDesde.value) {
    query.desde =
      filtroAnioDesde.value;
  }

  if (filtroAnioHasta.value) {
    query.hasta =
      filtroAnioHasta.value;
  }

  if (soloConPdf.value) {
    query.pdf = "1";
  }

  if (orden.value !== "recientes") {
    query.orden = orden.value;
  }

  if (vista.value !== "cards") {
    query.vista = vista.value;
  }

  return query;
}

function scheduleRouteSync() {
  window.clearTimeout(
    routeSyncTimer
  );

  routeSyncTimer = window.setTimeout(
    () => {
      router.replace({
        query: buildStateQuery(),
      });
    },
    ROUTE_SYNC_DEBOUNCE_MS
  );
}

/* ============================================================
  PARÁMETROS OFICIALES DEL BACKEND
============================================================ */

function buildBackendParams({
  includeType = true,
  includeOrdering = true,
  includePeriod = true,
} = {}) {
  const params = {};

  if (
    includeType &&
    filtro.value?.value !== "ALL"
  ) {
    params.tipo =
      filtro.value?.apiValue ||
      filtro.value?.value;
  }

  if (
    filtroOrigen.value !== "ALL"
  ) {
    params.origen_tipo =
      filtroOrigen.value;
  }

  if (includePeriod) {
    if (filtroAnio.value) {
      params.anio =
        filtroAnio.value;
    } else {
      if (filtroAnioDesde.value) {
        params.anio_desde =
          filtroAnioDesde.value;
      }

      if (filtroAnioHasta.value) {
        params.anio_hasta =
          filtroAnioHasta.value;
      }
    }

    if (filtroMes.value) {
      params.mes =
        filtroMes.value;
    }
  }

  if (q.value.trim()) {
    params.texto =
      q.value.trim();
  }

  if (
    filtroEstado.value !== "ALL"
  ) {
    params.estado =
      filtroEstado.value;
  }

  if (filtroSede.value) {
    params.sede =
      filtroSede.value;
  }

  if (filtroFacultad.value) {
    params.facultad =
      filtroFacultad.value;
  }

  if (filtroCarrera.value) {
    params.carrera =
      filtroCarrera.value;
  }

  if (filtroProyecto.value) {
    params.proyecto =
      filtroProyecto.value;
  }

  if (soloConPdf.value) {
    params.solo_con_pdf = "true";
  }

  if (
    includeOrdering &&
    orden.value
  ) {
    params.orden =
      orden.value;
  }

  return params;
}

/* ============================================================
  COMPUTEDS
============================================================ */

const tipoFiltroValue = computed(
  () =>
    filtro.value?.value ||
    "ALL"
);

const tipoThemeCode = computed(
  () =>
    filtro.value?.value ||
    "ALL"
);

const publicacionesFiltradas =
  computed(
    () => publicaciones.value
  );

const activeFiltersCount =
  computed(() => {
    let total = 0;

    if (
      filtro.value?.value !== "ALL"
    ) {
      total += 1;
    }

    if (
      filtroOrigen.value !== "ALL"
    ) {
      total += 1;
    }

    if (q.value.trim()) {
      total += 1;
    }

    if (
      filtroEstado.value !== "ALL"
    ) {
      total += 1;
    }

    if (filtroSede.value) {
      total += 1;
    }

    if (filtroFacultad.value) {
      total += 1;
    }

    if (filtroCarrera.value) {
      total += 1;
    }

    if (filtroProyecto.value) {
      total += 1;
    }

    if (
      filtroAnio.value ||
      filtroMes.value ||
      filtroAnioDesde.value ||
      filtroAnioHasta.value
    ) {
      total += 1;
    }

    if (soloConPdf.value) {
      total += 1;
    }

    return total;
  });

const advancedFiltersCount =
  computed(() => {
    let total = 0;

    if (filtroProyecto.value) {
      total += 1;
    }

    if (filtroOrigen.value !== "ALL") {
      total += 1;
    }

    if (
      filtroAnio.value ||
      filtroMes.value ||
      filtroAnioDesde.value ||
      filtroAnioHasta.value
    ) {
      total += 1;
    }

    return total;
  });

const periodFilterLabel = computed(() => {
  const monthLabel = MESES_LIST.find(
    (item) => item.value === filtroMes.value
  )?.label;

  if (filtroAnio.value) {
    return filtroMes.value
      ? `${monthLabel || "Mes"} de ${filtroAnio.value}`
      : `Año ${filtroAnio.value}`;
  }

  if (filtroAnioDesde.value || filtroAnioHasta.value) {
    if (filtroAnioDesde.value && filtroAnioHasta.value) {
      return `${filtroAnioDesde.value}–${filtroAnioHasta.value}`;
    }

    if (filtroAnioDesde.value) {
      return `Desde ${filtroAnioDesde.value}`;
    }

    return `Hasta ${filtroAnioHasta.value}`;
  }

  if (filtroMes.value) {
    return monthLabel || "Mes";
  }

  return "";
});

function findCatalogLabel(
  catalog,
  value,
  fallback
) {
  const normalized = String(value ?? "");
  const item = catalog.find(
    (entry) => String(entry?.id ?? "") === normalized
  );

  return item
    ? getCatalogLabel(item)
    : fallback;
}

const activeFilterChips = computed(() => {
  const chips = [];

  if (filtroSede.value) {
    chips.push({
      key: "sede",
      label: findCatalogLabel(
        sedes.value,
        filtroSede.value,
        "Sede"
      ),
    });
  }

  if (filtroFacultad.value) {
    chips.push({
      key: "facultad",
      label: findCatalogLabel(
        facultades.value,
        filtroFacultad.value,
        "Facultad"
      ),
    });
  }

  if (filtroCarrera.value) {
    chips.push({
      key: "carrera",
      label: findCatalogLabel(
        carreras.value,
        filtroCarrera.value,
        "Carrera"
      ),
    });
  }

  if (filtroEstado.value !== "ALL") {
    const estado = ESTADOS_FILTER_LIST.find(
      (item) => item.value === filtroEstado.value
    );

    chips.push({
      key: "estado",
      label: estado?.label || "Estado",
    });
  }

  if (filtroProyecto.value) {
    chips.push({
      key: "proyecto",
      label: findCatalogLabel(
        proyectos.value,
        filtroProyecto.value,
        "Proyecto"
      ),
    });
  }

  if (filtroOrigen.value !== "ALL") {
    const origen = ORIGENES_LIST.find(
      (item) => item.value === filtroOrigen.value
    );

    chips.push({
      key: "origen",
      label: origen?.label || "Origen",
    });
  }

  if (periodFilterLabel.value) {
    chips.push({
      key: "periodo",
      label: periodFilterLabel.value,
    });
  }

  if (soloConPdf.value) {
    chips.push({
      key: "pdf",
      label: "Solo con PDF",
    });
  }

  return chips;
});

const canClearFilters =
  computed(() => {
    return (
      filtro.value?.value !== "ALL" ||
      filtroOrigen.value !== "ALL" ||
      filtroEstado.value !== "ALL" ||
      q.value.trim().length > 0 ||
      Boolean(filtroSede.value) ||
      Boolean(filtroFacultad.value) ||
      Boolean(filtroCarrera.value) ||
      Boolean(filtroProyecto.value) ||
      Boolean(filtroAnio.value) ||
      Boolean(filtroMes.value) ||
      Boolean(filtroAnioDesde.value) ||
      Boolean(filtroAnioHasta.value) ||
      soloConPdf.value ||
      orden.value !== "recientes"
    );
  });

const emptyMessage =
  computed(() => {
    if (errorMsg.value) {
      return errorMsg.value;
    }

    const hasSearch =
      q.value.trim().length > 0;

    const hasFilter =
      activeFiltersCount.value > 0;

    if (
      hasSearch &&
      hasFilter
    ) {
      return (
        "No se encontraron publicaciones con la búsqueda " +
        "y los filtros seleccionados."
      );
    }

    if (hasSearch) {
      return (
        "No se encontraron publicaciones para la " +
        "búsqueda ingresada."
      );
    }

    if (hasFilter) {
      return (
        "No hay publicaciones para los filtros seleccionados."
      );
    }

    return (
      "Aún no tienes publicaciones registradas."
    );
  });

/* ============================================================
  ACCIONES DE FILTROS
============================================================ */

async function removeActiveFilter(key) {
  if (key === "sede") {
    filtroSede.value = "";
    await onMainSedeChange();
    return;
  }

  if (key === "facultad") {
    filtroFacultad.value = "";
    await onMainFacultadChange();
    return;
  }

  if (key === "carrera") {
    filtroCarrera.value = "";
    await onMainCarreraChange();
    return;
  }

  if (key === "estado") {
    filtroEstado.value = "ALL";
    return;
  }

  if (key === "proyecto") {
    filtroProyecto.value = "";
    return;
  }

  if (key === "origen") {
    filtroOrigen.value = "ALL";
    return;
  }

  if (key === "periodo") {
    filtroAnio.value = "";
    filtroMes.value = "";
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
    return;
  }

  if (key === "pdf") {
    soloConPdf.value = false;
  }
}

function cambiarFiltro(tipo) {
  filtro.value = tipo;
}

function clearAllFilters() {
  filtro.value = TIPOS.ALL;
  filtroOrigen.value = "ALL";
  filtroEstado.value = "ALL";

  q.value = "";

  filtroSede.value = "";
  filtroFacultad.value = "";
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  filtroAnio.value = "";
  filtroMes.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";

  soloConPdf.value = false;
  orden.value = "recientes";
  filtrosAvanzadosAbiertos.value = false;
}

function countByType(typeValue) {
  return Number(
    typeCounts.value?.[typeValue] ||
      0
  );
}

/* ============================================================
  BUSCADOR
============================================================ */

function handleSearchAction() {
  if (q.value) {
    q.value = "";
    searchEl.value?.focus();
    return;
  }

  searchEl.value?.focus();
}

/* ============================================================
  NAVEGACIÓN
============================================================ */

function verDetalles(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}`,
    query: {
      from: "mis-publicaciones",
    },
  });
}

function editarPublicacion(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}/editar`,
    query: {
      from: "mis-publicaciones",
    },
  });
}

function clearWorkflowFeedback() {
  workflowMessage.value = "";
  workflowError.value = "";
}

function isWorkflowLoading(
  publicacionId,
  action
) {
  return (
    Number(
      workflowPublicationId.value
    ) === Number(publicacionId) &&
    workflowAction.value === action
  );
}

async function refreshAfterWorkflow() {
  await Promise.all([
    cargarResumen(),
    cargarPublicaciones({
      forceLoading: true,
    }),
  ]);
}

function workflowPublicationTitle(publicacion) {
  return (
    String(
      publicacion?.titulo ||
      publicacion?.nombre ||
      ""
    ).trim() ||
    "esta publicación"
  );
}

async function executeSendToReviewFromList(
  publicacion
) {
  clearWorkflowFeedback();

  workflowPublicationId.value =
    publicacion.id;

  workflowAction.value =
    "enviar";

  try {
    await enviarPublicacionRevision(
      publicacion.id
    );

    workflowMessage.value =
      "La publicación fue enviada a revisión correctamente.";

    try {
      await refreshAfterWorkflow();
    } catch (refreshError) {
      console.warn(
        "La publicación fue enviada, pero no se pudo refrescar el listado:",
        refreshError
      );

      workflowMessage.value =
        "La publicación fue enviada a revisión. Actualice el listado si el nuevo estado no aparece inmediatamente.";
    }
  } catch (error) {
    console.error(
      "Error enviando publicación a revisión:",
      error
    );

    workflowError.value =
      extractErrorMessage(
        error,
        "No se pudo enviar la publicación a revisión."
      );
  } finally {
    workflowPublicationId.value = null;
    workflowAction.value = "";
  }
}

function enviarARevisionDesdeListado(
  publicacion
) {
  if (
    !publicacion?.id ||
    workflowPublicationId.value !== null ||
    !puedeEnviarDesdeListado(publicacion)
  ) {
    return;
  }

  const title =
    workflowPublicationTitle(publicacion);

  openNotice({
    title: "Enviar a revisión",
    message:
      `¿Desea enviar “${title}” a revisión? ` +
      "Mientras permanezca en revisión no podrá editarla.",
    confirm: true,
    confirmText: "Enviar a revisión",
    cancelText: "Cancelar",
    onConfirm: async () => {
      await executeSendToReviewFromList(
        publicacion
      );
    },
  });
}

async function executeResendToReviewFromList(
  publicacion
) {
  clearWorkflowFeedback();

  workflowPublicationId.value =
    publicacion.id;

  workflowAction.value =
    "reenviar";

  try {
    await reenviarPublicacionRevision(
      publicacion.id
    );

    workflowMessage.value =
      "La publicación fue reenviada a revisión correctamente.";

    try {
      await refreshAfterWorkflow();
    } catch (refreshError) {
      console.warn(
        "La publicación fue reenviada, pero no se pudo refrescar el listado:",
        refreshError
      );

      workflowMessage.value =
        "La publicación fue reenviada a revisión. Actualice el listado si el nuevo estado no aparece inmediatamente.";
    }
  } catch (error) {
    console.error(
      "Error reenviando publicación a revisión:",
      error
    );

    workflowError.value =
      extractErrorMessage(
        error,
        "No se pudo reenviar la publicación a revisión."
      );
  } finally {
    workflowPublicationId.value = null;
    workflowAction.value = "";
  }
}

function reenviarARevisionDesdeListado(
  publicacion
) {
  if (
    !publicacion?.id ||
    workflowPublicationId.value !== null ||
    !puedeReenviarDesdeListado(publicacion)
  ) {
    return;
  }

  const title =
    workflowPublicationTitle(publicacion);

  openNotice({
    title: "Reenviar a revisión",
    message:
      `Confirme que realizó las correcciones solicitadas en “${title}”. ` +
      "La publicación volverá a revisión y no podrá editarla mientras permanezca en ese estado.",
    confirm: true,
    confirmText: "Reenviar a revisión",
    cancelText: "Cancelar",
    onConfirm: async () => {
      await executeResendToReviewFromList(
        publicacion
      );
    },
  });
}


/* ============================================================
  PDF AUTENTICADO
============================================================ */

async function abrirPdf(publicacion) {
  const endpoint =
    resolvePdfEndpoint(publicacion);

  if (
    !endpoint ||
    openingPdfId.value !== null
  ) {
    return;
  }

  openingPdfId.value =
    publicacion.id;

  pdfErrorMsg.value = "";

  const previewWindow =
    window.open("", "_blank");

  if (previewWindow) {
    previewWindow.opener = null;
    previewWindow.document.title =
      "Cargando PDF…";
  }

  try {
    const response = await api.get(
      endpoint,
      {
        responseType: "blob",
      }
    );

    const contentType =
      response.headers?.["content-type"] ||
      "application/pdf";

    const blob = new Blob(
      [response.data],
      {
        type: contentType,
      }
    );

    const objectUrl =
      window.URL.createObjectURL(blob);

    if (
      previewWindow &&
      !previewWindow.closed
    ) {
      previewWindow.location.href =
        objectUrl;
    } else {
      const link =
        document.createElement("a");

      link.href = objectUrl;
      link.target = "_blank";
      link.rel =
        "noopener noreferrer";

      document.body.appendChild(link);
      link.click();
      link.remove();
    }

    window.setTimeout(() => {
      window.URL.revokeObjectURL(
        objectUrl
      );
    }, PDF_URL_REVOKE_DELAY_MS);
  } catch (error) {
    if (
      previewWindow &&
      !previewWindow.closed
    ) {
      previewWindow.close();
    }

    console.error(
      "Error abriendo PDF:",
      error
    );

    pdfErrorMsg.value =
      extractErrorMessage(
        error,
        "No se pudo abrir el PDF de la publicación."
      );
  } finally {
    openingPdfId.value = null;
  }
}

/* ============================================================
  ATAJOS DE TECLADO
============================================================ */

function onKey(event) {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform
      .toLowerCase()
      .includes("mac");

  const key = String(
    event.key || ""
  ).toLowerCase();

  const shortcutSearch =
    (
      isMac &&
      event.metaKey &&
      key === "k"
    ) ||
    (
      !isMac &&
      event.ctrlKey &&
      key === "k"
    );

  if (shortcutSearch) {
    event.preventDefault();
    searchEl.value?.focus();
  }

  if (
    event.key === "Escape" &&
    q.value
  ) {
    q.value = "";
  }
}

/* ============================================================
  AÑOS DISPONIBLES DESDE EL BACKEND
============================================================ */

async function cargarAniosDisponibles() {
  const requestSequence =
    ++yearsRequestSequence;

  loadingAnios.value = true;

  try {
    const response = await api.get(
      YEARS_ENDPOINT
    );

    if (
      requestSequence !==
      yearsRequestSequence
    ) {
      return;
    }

    añosDisponibles.value =
      extractYears(response.data);

    syncSelectedYearsWithCatalog();
  } catch (error) {
    if (
      requestSequence !==
      yearsRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando años disponibles:",
      error
    );

    añosDisponibles.value = [];
  } finally {
    if (
      requestSequence ===
      yearsRequestSequence
    ) {
      loadingAnios.value = false;
    }
  }
}

/* ============================================================
  RESUMEN GENERAL
============================================================ */

async function cargarResumen() {
  const requestSequence =
    ++summaryRequestSequence;

  try {
    const response = await api.get(
      LIST_ENDPOINT
    );

    if (
      requestSequence !==
      summaryRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    );

    totalPublicaciones.value =
      extractTotal(
        response.data,
        items.length
      );
  } catch (error) {
    if (
      requestSequence !==
      summaryRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando resumen de publicaciones:",
      error
    );
  }
}

/* ============================================================
  CONTEOS POR TIPO
============================================================ */

async function cargarConteosPorTipo() {
  const requestSequence =
    ++typeCountRequestSequence;

  const params =
    buildBackendParams({
      includeType: false,
      includeOrdering: false,
    });

  try {
    const response = await api.get(
      LIST_ENDPOINT,
      {
        params,
      }
    );

    if (
      requestSequence !==
      typeCountRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    ).map((item) => ({
      ...item,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          item
        ),
    }));

    const counts =
      Object.fromEntries(
        TIPOS_LIST.map((tipo) => [
          tipo.value,
          0,
        ])
      );

    counts.ALL = extractTotal(
      response.data,
      items.length
    );

    items.forEach((item) => {
      const code = resolveType(item);

      if (
        Object.hasOwn(
          counts,
          code
        )
      ) {
        counts[code] += 1;
      }
    });

    typeCounts.value = counts;
  } catch (error) {
    if (
      requestSequence !==
      typeCountRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando conteos por tipo:",
      error
    );
  }
}

/* ============================================================
  CARGA DE PUBLICACIONES
============================================================ */

async function cargarPublicaciones({
  forceLoading = false,
} = {}) {
  const requestSequence =
    ++listRequestSequence;

  const showLoading =
    forceLoading ||
    !hasLoadedOnce;

  if (showLoading) {
    loading.value = true;
  }

  errorMsg.value = "";
  pdfErrorMsg.value = "";

  try {
    const response = await api.get(
      LIST_ENDPOINT,
      {
        params:
          buildBackendParams(),
      }
    );

    if (
      requestSequence !==
      listRequestSequence
    ) {
      return;
    }

    const items = extractArray(
      response.data
    ).map((item) => ({
      ...item,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          item
        ),
    }));

    publicaciones.value = items;

    totalResultados.value =
      extractTotal(
        response.data,
        items.length
      );

    if (!canClearFilters.value) {
      totalPublicaciones.value =
        totalResultados.value;
    }

    hasLoadedOnce = true;

    void cargarConteosPorTipo();
  } catch (error) {
    if (
      requestSequence !==
      listRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando publicaciones:",
      error
    );

    publicaciones.value = [];
    totalResultados.value = 0;

    errorMsg.value =
      extractErrorMessage(
        error,
        "No se pudieron cargar sus publicaciones."
      );
  } finally {
    if (
      requestSequence ===
      listRequestSequence
    ) {
      loading.value = false;
    }
  }
}

function scheduleReload(
  delay = FILTER_DEBOUNCE_MS
) {
  window.clearTimeout(
    reloadTimer
  );

  reloadTimer = window.setTimeout(
    () => {
      void cargarPublicaciones();
    },
    delay
  );
}

/* ============================================================
  HIDRATACIÓN INICIAL
============================================================ */

hydrateStateFromRoute();

/* ============================================================
  WATCHERS DE PERIODO
============================================================ */

watch(
  filtroAnio,
  (value) => {
    if (!value) {
      return;
    }

    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  }
);

watch(
  [
    filtroAnioDesde,
    filtroAnioHasta,
  ],
  ([desde, hasta]) => {
    if (desde || hasta) {
      filtroAnio.value = "";
    }

    normalizeSelectedYearRange();
  }
);

/* ============================================================
  WATCHER GENERAL DE FILTROS
============================================================ */

watch(
  [
    q,
    tipoFiltroValue,
    filtroOrigen,
    filtroEstado,
    filtroSede,
    filtroFacultad,
    filtroCarrera,
    filtroProyecto,
    filtroAnio,
    filtroMes,
    filtroAnioDesde,
    filtroAnioHasta,
    soloConPdf,
    orden,
  ],
  () => {
    scheduleRouteSync();
    scheduleReload();
  }
);

watch(
  vista,
  () => {
    scheduleRouteSync();
  }
);

/* ============================================================
  CICLO DE VIDA
============================================================ */

onMounted(async () => {
  window.addEventListener(
    "keydown",
    onKey
  );

  await Promise.all([
    loadSedes(),
    loadFacultades(),
  ]);

  await loadDependentCatalogsFromState();

  await Promise.all([
    cargarResumen(),
    cargarAniosDisponibles(),
    cargarPublicaciones({
      forceLoading: true,
    }),
  ]);
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    onKey
  );

  window.clearTimeout(
    routeSyncTimer
  );

  window.clearTimeout(
    reloadTimer
  );

  listRequestSequence += 1;
  summaryRequestSequence += 1;
  typeCountRequestSequence += 1;
  yearsRequestSequence += 1;
});
</script>

<style src="../listado-publicaciones/sgpc-listados-base.css"></style>
<style src="./mis-publicaciones.css"></style>
