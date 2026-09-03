<template>
  <div class="pub-list-page" :data-tipo="tipoFiltroActivo">
    <main class="pub-shell">
      <!-- =====================================================
        ENCABEZADO
      ====================================================== -->
      <header
        class="pub-header page-stage page-stage-1"
        aria-label="Listado de publicaciones institucionales"
      >
        <div class="pub-header__copy">
          <h1 class="pub-title">
            Publicaciones
          </h1>

          <p class="pub-subtitle">
            Consulte y filtre las publicaciones disponibles en la institución.
          </p>
        </div>

        <div class="pub-header__actions" aria-label="Acciones del catálogo">
          <button
            v-if="panelLateralActivo === 'export'"
            type="button"
            class="pub-btn pub-btn--ghost"
            @click="abrirPanelFiltros"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="m15.4 18.4-6.4-6.4 6.4-6.4L14 4.2 5.8 12l8.2 7.8 1.4-1.4Z"
              />
            </svg>
            Volver a publicaciones
          </button>

          <button
            v-else
            type="button"
            class="pub-btn pub-btn--primary"
            :disabled="loading"
            @click="abrirPanelExportacion"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M11 3h2v10.17l3.59-3.58L18 11l-6 6-6-6 1.41-1.41L11 13.17V3ZM5 19h14v2H5v-2Z"
              />
            </svg>
            Exportar
          </button>
        </div>
      </header>

      <!-- =====================================================
        BÚSQUEDA PRINCIPAL
      ====================================================== -->
      <section
        class="pub-discovery page-stage page-stage-2"
        aria-label="Buscar publicaciones"
      >
        <PublicacionesSearchField
          ref="searchEl"
          v-model="textoFiltroActivo"
          :placeholder="
            panelLateralActivo === 'export'
              ? 'Buscar dentro de la descarga'
              : 'Buscar por título, autor, DOI, ISBN o proyecto'
          "
        />
      </section>

      <!-- =====================================================
        CATÁLOGO: FILTROS RÁPIDOS + AVANZADOS
      ====================================================== -->
      <section
        v-if="panelLateralActivo === 'filtros'"
        class="pub-filters page-stage page-stage-3"
        aria-label="Filtros del catálogo"
      >
        <div class="pub-filters__topline">
          <div>
            <h2 class="pub-section-title">
              Filtros
            </h2>
          </div>

          <div class="pub-filters__status">
            <button
              v-if="hayFiltros || hayBusqueda"
              type="button"
              class="pub-text-action"
              @click="limpiarFiltros"
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        <div class="pub-quick-filters">
          <div class="pub-field">
            <label class="pub-label" for="fSede">Sede</label>
            <select
              id="fSede"
              v-model="filtroSede"
              class="pub-select"
              @change="onMainSedeChange"
            >
              <option value="">Todas las sedes</option>
              <option
                v-for="sede in sedes"
                :key="`sede-${sede.id}`"
                :value="String(sede.id)"
              >
                {{ sede.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="fFacultad">Facultad</label>
            <select
              id="fFacultad"
              v-model="filtroFacultad"
              class="pub-select"
              @change="onMainFacultadChange"
            >
              <option value="">Todas las facultades</option>
              <option
                v-for="fac in facultades"
                :key="`fac-${fac.id}`"
                :value="String(fac.id)"
              >
                {{ fac.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="fCarrera">Carrera</label>
            <select
              id="fCarrera"
              v-model="filtroCarrera"
              class="pub-select"
              :disabled="!filtroSede && !filtroFacultad"
              @change="onMainCarreraChange"
            >
              <option value="">
                {{
                  !filtroSede && !filtroFacultad
                    ? 'Seleccione sede o facultad'
                    : 'Todas las carreras'
                }}
              </option>
              <option
                v-for="car in carreras"
                :key="`car-${car.id}`"
                :value="String(car.id)"
              >
                {{ car.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field pub-field--order">
            <label class="pub-label" for="fOrden">Ordenar por</label>
            <select id="fOrden" v-model="ordenListado" class="pub-select">
              <option
                v-for="option in ORDENES_LIST"
                :key="`orden-${option.value}`"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <label class="pub-pdf-toggle" for="fSoloPdf">
            <input
              id="fSoloPdf"
              v-model="soloConPdf"
              class="pub-pdf-toggle__input"
              type="checkbox"
            />
            <span class="pub-pdf-toggle__control" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="m9.2 16.2-3.4-3.4 1.4-1.4 2 2 7.6-7.6 1.4 1.4-9 9Z" />
              </svg>
            </span>
            <span>Solo con documento</span>
          </label>
        </div>

        <details
          class="pub-advanced"
          :open="advancedOnlyFiltersCount > 0"
        >
          <summary class="pub-advanced__summary">
            <span class="pub-advanced__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M4 6h10v2H4V6Zm0 10h6v2H4v-2Zm0-5h16v2H4v-2Zm14-7h2v6h-2V4Zm-6 10h2v6h-2v-6Z" />
              </svg>
            </span>
            <span class="pub-advanced__copy">
              <strong>Más filtros</strong>
              <small>Proyecto, origen y período</small>
            </span>
            <span v-if="advancedOnlyFiltersCount" class="pub-advanced__count">
              {{ advancedOnlyFiltersCount }}
            </span>
            <span class="pub-advanced__chevron" aria-hidden="true">⌄</span>
          </summary>

          <div class="pub-advanced__body">
            <div class="pub-advanced__row pub-advanced__row--two">
              <div class="pub-field">
                <label class="pub-label" for="fProyecto">Proyecto</label>
                <select
                  id="fProyecto"
                  v-model="filtroProyecto"
                  class="pub-select"
                  :disabled="!filtroCarrera"
                >
                  <option value="">
                    {{ filtroCarrera ? 'Todos los proyectos' : 'Seleccione una carrera' }}
                  </option>
                  <option
                    v-for="proy in proyectos"
                    :key="`proy-${proy.id}`"
                    :value="String(proy.id)"
                  >
                    {{ proy.nombre }}
                  </option>
                </select>
              </div>

              <div class="pub-field">
                <label class="pub-label" for="fOrigen">Origen</label>
                <select id="fOrigen" v-model="filtroOrigen" class="pub-select">
                  <option
                    v-for="origen in ORIGENES_LIST"
                    :key="`origen-${origen.value}`"
                    :value="origen.value"
                  >
                    {{ origen.label }}
                  </option>
                </select>
              </div>
            </div>

            <div class="pub-period">
              <div class="pub-period__heading">
                <span class="pub-label">Período</span>
                <small>Elija un año concreto o un rango.</small>
              </div>

              <div class="pub-period__options">
                <div class="pub-period__group">
                  <span class="pub-period__group-label">Año y mes</span>

                  <div class="pub-period__fields">
                    <div class="pub-field">
                      <label class="pub-label pub-label--muted" for="fAnio">Año</label>
                      <select
                        id="fAnio"
                        v-model="filtroAnio"
                        class="pub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnioDesde || filtroAnioHasta)"
                      >
                        <option value="">Todos los años</option>
                        <option
                          v-for="anio in añosDisponibles"
                          :key="`exact-${anio}`"
                          :value="String(anio)"
                        >
                          {{ anio }}
                        </option>
                      </select>
                    </div>

                    <div class="pub-field">
                      <label class="pub-label pub-label--muted" for="fMes">Mes</label>
                      <select id="fMes" v-model="filtroMes" class="pub-select">
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

                <span class="pub-period__or" aria-hidden="true">o</span>

                <div class="pub-period__group">
                  <span class="pub-period__group-label">Rango</span>

                  <div class="pub-period__fields">
                    <div class="pub-field">
                      <label class="pub-label pub-label--muted" for="fAnioDesde">Desde</label>
                      <select
                        id="fAnioDesde"
                        v-model="filtroAnioDesde"
                        class="pub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
                      >
                        <option value="">Sin mínimo</option>
                        <option
                          v-for="anio in añosDisponibles"
                          :key="`desde-${anio}`"
                          :value="String(anio)"
                        >
                          {{ anio }}
                        </option>
                      </select>
                    </div>

                    <div class="pub-field">
                      <label class="pub-label pub-label--muted" for="fAnioHasta">Hasta</label>
                      <select
                        id="fAnioHasta"
                        v-model="filtroAnioHasta"
                        class="pub-select"
                        :disabled="loadingAnios || !añosDisponibles.length || Boolean(filtroAnio)"
                      >
                        <option value="">Sin máximo</option>
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
        </details>

        <div v-if="activeFilterChips.length" class="pub-active-filters" aria-label="Filtros activos">
          <span class="pub-active-filters__label">Aplicados</span>

          <button
            v-for="chip in activeFilterChips"
            :key="chip.key"
            type="button"
            class="pub-filter-chip"
            :aria-label="`Quitar filtro ${chip.label}`"
            @click="removeActiveFilter(chip.key)"
          >
            <span>{{ chip.label }}</span>
            <span aria-hidden="true">×</span>
          </button>
        </div>
      </section>

      <!-- =====================================================
        EXPORTACIÓN
      ====================================================== -->
      <section
        v-else
        class="pub-export page-stage page-stage-3"
        aria-label="Configuración de exportación"
      >
        <header class="pub-export__head">
          <div>
            
            <h2 class="pub-section-title">Descargar publicaciones</h2>
            <p>
              Elija el formato y los filtros que desea aplicar al archivo.
            </p>
          </div>

          <div class="pub-export__metric">
            <strong>{{ exportPreviewLoading ? '…' : exportPreviewCount }}</strong>
            <span>publicaciones</span>
          </div>
        </header>

        <div v-if="exportErrorMsg" class="pub-alert" role="alert">
          {{ exportErrorMsg }}
        </div>

        <div class="pub-export-format" aria-label="Formato de exportación">
          <button
            type="button"
            class="pub-export-format__option"
            :class="{ 'is-active': exportFormat === 'excel' }"
            :aria-pressed="exportFormat === 'excel'"
            @click="exportFormat = 'excel'"
          >
            <span class="pub-export-format__icon pub-export-format__icon--excel" aria-hidden="true">
              XLSX
            </span>
            <span>
              <strong>Excel</strong>
              <small>Para analizar y trabajar con los datos.</small>
            </span>
          </button>

          <button
            type="button"
            class="pub-export-format__option"
            :class="{ 'is-active': exportFormat === 'pdf' }"
            :aria-pressed="exportFormat === 'pdf'"
            @click="exportFormat = 'pdf'"
          >
            <span class="pub-export-format__icon pub-export-format__icon--pdf" aria-hidden="true">
              PDF
            </span>
            <span>
              <strong>PDF</strong>
              <small>Para presentar, imprimir o compartir.</small>
            </span>
          </button>
        </div>

        <div class="pub-export__actions">
          <button type="button" class="pub-btn pub-btn--ghost" @click="syncExportFiltersFromVisible">
            Usar filtros actuales
          </button>
          <button type="button" class="pub-text-action" @click="limpiarExportFilters">
            Limpiar filtros
          </button>
        </div>

        <div class="pub-export__grid">
          <div class="pub-field">
            <label class="pub-label" for="expTipo">Tipo</label>
            <select id="expTipo" v-model="exportFiltroTipo" class="pub-select">
              <option
                v-for="tipo in TIPOS_LIST"
                :key="`exp-${tipo.value}`"
                :value="tipo.value"
              >
                {{ tipo.label }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expOrigen">Origen</label>
            <select id="expOrigen" v-model="exportFiltroOrigen" class="pub-select">
              <option
                v-for="origen in ORIGENES_LIST"
                :key="`exp-origen-${origen.value}`"
                :value="origen.value"
              >
                {{ origen.label }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expSede">Sede</label>
            <select id="expSede" v-model="exportFiltroSede" class="pub-select" @change="onExportSedeChange">
              <option value="">Todas las sedes</option>
              <option
                v-for="sede in sedes"
                :key="`exp-sede-${sede.id}`"
                :value="String(sede.id)"
              >
                {{ sede.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expFacultad">Facultad</label>
            <select id="expFacultad" v-model="exportFiltroFacultad" class="pub-select" @change="onExportFacultadChange">
              <option value="">Todas las facultades</option>
              <option
                v-for="fac in facultades"
                :key="`exp-fac-${fac.id}`"
                :value="String(fac.id)"
              >
                {{ fac.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expCarrera">Carrera</label>
            <select
              id="expCarrera"
              v-model="exportFiltroCarrera"
              class="pub-select"
              :disabled="!exportFiltroSede && !exportFiltroFacultad"
              @change="onExportCarreraChange"
            >
              <option value="">Todas las carreras</option>
              <option
                v-for="car in exportCarreras"
                :key="`exp-car-${car.id}`"
                :value="String(car.id)"
              >
                {{ car.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expProyecto">Proyecto</label>
            <select id="expProyecto" v-model="exportFiltroProyecto" class="pub-select" :disabled="!exportFiltroCarrera">
              <option value="">Todos los proyectos</option>
              <option
                v-for="proy in exportProyectos"
                :key="`exp-proy-${proy.id}`"
                :value="String(proy.id)"
              >
                {{ proy.nombre }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expAnio">Año</label>
            <select
              id="expAnio"
              v-model="exportFiltroAnio"
              class="pub-select"
              :disabled="loadingAnios || !añosDisponibles.length || Boolean(exportFiltroAnioDesde || exportFiltroAnioHasta)"
            >
              <option value="">Todos los años</option>
              <option
                v-for="anio in añosDisponibles"
                :key="`exp-exact-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expMes">Mes</label>
            <select id="expMes" v-model="exportFiltroMes" class="pub-select">
              <option
                v-for="mes in MESES_LIST"
                :key="`exp-mes-${mes.value || 'all'}`"
                :value="mes.value"
              >
                {{ mes.label }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expAnioDesde">Desde</label>
            <select
              id="expAnioDesde"
              v-model="exportFiltroAnioDesde"
              class="pub-select"
              :disabled="loadingAnios || !añosDisponibles.length || Boolean(exportFiltroAnio)"
            >
              <option value="">Sin mínimo</option>
              <option
                v-for="anio in añosDisponibles"
                :key="`exp-desde-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>

          <div class="pub-field">
            <label class="pub-label" for="expAnioHasta">Hasta</label>
            <select
              id="expAnioHasta"
              v-model="exportFiltroAnioHasta"
              class="pub-select"
              :disabled="loadingAnios || !añosDisponibles.length || Boolean(exportFiltroAnio)"
            >
              <option value="">Sin máximo</option>
              <option
                v-for="anio in añosDisponibles"
                :key="`exp-hasta-${anio}`"
                :value="String(anio)"
              >
                {{ anio }}
              </option>
            </select>
          </div>

          <label class="pub-pdf-toggle pub-pdf-toggle--export" for="expSoloPdf">
            <input id="expSoloPdf" v-model="exportSoloConPdf" class="pub-pdf-toggle__input" type="checkbox" />
            <span class="pub-pdf-toggle__control" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="m9.2 16.2-3.4-3.4 1.4-1.4 2 2 7.6-7.6 1.4 1.4-9 9Z" />
              </svg>
            </span>
            <span>Solo con documento</span>
          </label>
        </div>

        <footer class="pub-export__footer">
          <div class="pub-export__note">
            <strong>{{ exportPreviewCount }}</strong>
            <span>{{ exportPreviewCount === 1 ? 'publicación será exportada' : 'publicaciones serán exportadas' }}</span>
          </div>

          <button
            type="button"
            class="pub-btn pub-btn--primary"
            :disabled="loading || exporting || exportPreviewLoading || !exportPreviewCount"
            @click="confirmarExportacion"
          >
            {{
              exporting
                ? 'Preparando…'
                : exportFormat === 'pdf'
                  ? 'Descargar PDF'
                  : 'Descargar Excel'
            }}
          </button>
        </footer>
      </section>

      <!-- =====================================================
        CLASIFICACIÓN Y RESULTADOS
      ====================================================== -->
      <section class="pub-results page-stage page-stage-4" aria-label="Resultados de publicaciones">
        <div class="pub-results__head">
          <div>
            <h2 class="pub-results__title">
              {{ totalResultadosVisibles }}
              {{ totalResultadosVisibles === 1 ? 'publicación' : 'publicaciones' }}
            </h2>

            <p>
              {{
                panelLateralActivo === 'export'
                  ? `Estas publicaciones se incluirán en el archivo ${exportFormat === 'pdf' ? 'PDF' : 'Excel'}.`
                  : 'Explore las publicaciones que coinciden con los filtros seleccionados.'
              }}
            </p>
          </div>
        </div>

        <div class="pub-typeFilter" aria-label="Tipo de publicación">
          <span class="pub-typeFilter__label">Tipo</span>

          <div class="pub-typeFilter__chips">
            <button
              v-for="tipo in TIPOS_LIST"
              :key="`top-${tipo.value}`"
              type="button"
              class="pub-typeFilter__chip"
              :class="{ 'is-active': tipoFiltroActivo === tipo.value }"
              :aria-pressed="tipoFiltroActivo === tipo.value"
              @click="tipoFiltroActivo = tipo.value"
            >
              <span class="pub-typeFilter__dot" :data-tipo="tipo.value" aria-hidden="true"></span>
              <span>{{ tipo.label }}</span>
              <strong>{{ countByTypeVisible(tipo.value) }}</strong>
            </button>
          </div>
        </div>

        <section v-if="resultadosLoading" class="pub-state" aria-live="polite">
          <div class="pub-skeleton-grid" aria-label="Cargando publicaciones">
            <div v-for="n in 6" :key="n" class="pub-skeleton-card">
              <span></span><span></span><span></span><span></span>
            </div>
          </div>
        </section>

        <section v-else-if="resultadosErrorMsg" class="pub-state pub-state--error">
          <div class="pub-alert" role="alert">{{ resultadosErrorMsg }}</div>
          <button type="button" class="pub-btn pub-btn--primary" :disabled="resultadosLoading" @click="reintentarCargaVisible">
            Reintentar
          </button>
        </section>

        <section v-else class="pub-content">
          <div v-if="listaFiltrada.length" class="pub-grid page-stagger page-stagger--mid">
            <article
              v-for="pub in listaFiltrada"
              :key="pub.id"
              class="pub-card pub-card--interactive"
              :data-tipo="resolveType(pub)"
              tabindex="0"
              role="button"
              :aria-label="`Ver publicación ${pub.titulo || pub.proyecto || ''}`"
              @click="verDetalles(pub.id)"
              @keydown.enter.prevent="verDetalles(pub.id)"
              @keydown.space.prevent="verDetalles(pub.id)"
            >
              <div class="pub-card__accent" aria-hidden="true"></div>

              <div class="pub-card__head">
                <span class="pub-badge" :data-tipo="resolveType(pub)">
                  <span class="pub-badge__dot" aria-hidden="true"></span>
                  {{ resolveLabel(pub) }}
                </span>

                <time class="pub-date" :datetime="publicationPeriodDatetime(pub)">
                  {{ formatPublicationPeriod(pub) }}
                </time>
              </div>

              <div class="pub-card__body">
                <h3 class="pub-card__title" :title="pub.titulo || pub.proyecto || 'Sin título'">
                  {{ pub.titulo || pub.proyecto || 'Sin título' }}
                </h3>

                <div v-if="pub.autor" class="pub-card__section">
                  <span class="pub-card__section-label">Autores</span>
                  <p class="pub-card__authors" :title="pub.autor">
                    {{ compactAuthors(pub.autor) }}
                  </p>
                </div>

                <div class="pub-card__academic" :title="buildAcademicMeta(pub)">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path fill="currentColor" d="M12 3 2 8l10 5 8-4v6h2V8L12 3Zm-6 9.1V16c0 2.2 2.7 4 6 4s6-1.8 6-4v-3.9l-6 3-6-3Z" />
                  </svg>
                  <span>{{ buildAcademicMeta(pub) }}</span>
                </div>

                <div
                  v-if="(pub.titulo && pub.proyecto) || resolveOrigenResumen(pub) || hasPublicationPdf(pub)"
                  class="pub-card__tags"
                  aria-label="Información adicional"
                >
                  <span
                    v-if="pub.titulo && pub.proyecto"
                    class="pub-meta-chip pub-meta-chip--project"
                    :title="pub.proyecto"
                  >
                    {{ pub.proyecto }}
                  </span>
                  <span v-if="resolveOrigenResumen(pub)" class="pub-meta-chip pub-meta-chip--origin" :title="resolveOrigenResumen(pub)">
                    {{ resolveOrigenResumen(pub) }}
                  </span>
                  <span v-if="hasPublicationPdf(pub)" class="pub-meta-chip pub-meta-chip--pdf">
                    Documento disponible
                  </span>
                </div>
              </div>

              <footer class="pub-card__footer">
                <span class="pub-card__action">
                  Ver publicación
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path fill="currentColor" d="m13.2 5.6 6.4 6.4-6.4 6.4-1.4-1.4 4-4H4v-2h11.8l-4-4 1.4-1.4Z" />
                  </svg>
                </span>
              </footer>
            </article>
          </div>

          <div v-else class="pub-empty" role="status" aria-live="polite">
            <div class="pub-empty__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M4 3h11l5 5v13H4V3Zm2 2v14h12V9h-4V5H6Zm3 8h6v2H9v-2Zm0-4h3v2H9V9Z" />
              </svg>
            </div>
            <h3 class="pub-empty__title">{{ emptyTitle }}</h3>
            <p class="pub-empty__text">{{ emptyText }}</p>
            <button
              v-if="hayFiltrosVisibles || hayBusquedaVisible"
              class="pub-btn pub-btn--primary"
              type="button"
              @click="limpiarFiltrosVisibles"
            >
              Limpiar filtros
            </button>
          </div>
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
import { useRouter } from "vue-router";

import api from "../../scripts/api/axios";
import PublicacionesSearchField from "./PublicacionesSearchField.vue";

import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

/* ============================================================
  CONFIGURACIÓN
============================================================ */

const LIST_ENDPOINT = "/publicaciones/";
const YEARS_ENDPOINT = "/publicaciones/anios-disponibles/";
const EXPORT_EXCEL_ENDPOINT = "/reportes/publicaciones/excel/";
const EXPORT_PDF_ENDPOINT = "/reportes/publicaciones/pdf/";
const EXPORT_PREVIEW_ENDPOINT =
  "/reportes/publicaciones/excel/preview/";

const MAIN_FILTER_DEBOUNCE_MS = 350;
const EXPORT_PREVIEW_DEBOUNCE_MS = 350;

/* ============================================================
  NAVEGACIÓN
============================================================ */

const router = useRouter();
const searchEl = ref(null);

/* ============================================================
  PANEL LATERAL
============================================================ */

const panelLateralActivo = ref("filtros");

/* ============================================================
  TIPOS DE PUBLICACIÓN
============================================================ */

const TIPOS = Object.freeze({
  ALL: {
    label: "Todos",
    value: "ALL",
    apiValue: "",
  },

  AAI: {
    label: PUBLICACION_TIPOS.AAI.label,
    value: PUBLICACION_TIPOS.AAI.codigo,
    apiValue: PUBLICACION_TIPOS.AAI.apiCodigo,
  },

  AR: {
    label: PUBLICACION_TIPOS.AR.label,
    value: PUBLICACION_TIPOS.AR.codigo,
    apiValue: PUBLICACION_TIPOS.AR.apiCodigo,
  },

  PON: {
    label: PUBLICACION_TIPOS.PON.label,
    value: PUBLICACION_TIPOS.PON.codigo,
    apiValue: PUBLICACION_TIPOS.PON.apiCodigo,
  },

  CAP: {
    label: PUBLICACION_TIPOS.CAP.label,
    value: PUBLICACION_TIPOS.CAP.codigo,
    apiValue: PUBLICACION_TIPOS.CAP.apiCodigo,
  },

  LIB: {
    label: PUBLICACION_TIPOS.LIB.label,
    value: PUBLICACION_TIPOS.LIB.codigo,
    apiValue: PUBLICACION_TIPOS.LIB.apiCodigo,
  },
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
  ORÍGENES DE PUBLICACIÓN
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

const ORDENES_LIST = Object.freeze([
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

/* ============================================================
  DATOS PRINCIPALES
============================================================ */

const publicaciones = ref([]);
const exportPreviewPublicaciones = ref([]);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const proyectos = ref([]);

const añosDisponibles = ref([]);

/* ============================================================
  FILTROS VISIBLES
============================================================ */

const filtroTipo = ref(TIPOS.ALL.value);
const filtroOrigen = ref("ALL");
const ordenListado = ref("recientes");
const filtroAnio = ref("");
const filtroMes = ref("");
const filtroAnioDesde = ref("");
const filtroAnioHasta = ref("");
const filtroTexto = ref("");
const filtroSede = ref("");
const filtroFacultad = ref("");
const filtroCarrera = ref("");
const filtroProyecto = ref("");
const soloConPdf = ref(false);

/* ============================================================
  FILTROS DE EXPORTACIÓN
============================================================ */

const exportFiltroTipo = ref(TIPOS.ALL.value);
const exportFiltroOrigen = ref("ALL");
const exportFiltroAnio = ref("");
const exportFiltroMes = ref("");
const exportFiltroAnioDesde = ref("");
const exportFiltroAnioHasta = ref("");
const exportFiltroTexto = ref("");
const exportFiltroSede = ref("");
const exportFiltroFacultad = ref("");
const exportFiltroCarrera = ref("");
const exportFiltroProyecto = ref("");
const exportSoloConPdf = ref(false);

const exportCarreras = ref([]);
const exportProyectos = ref([]);

/* ============================================================
  ESTADOS
============================================================ */

const loading = ref(false);
const loadingAnios = ref(true);
const exporting = ref(false);
const exportFormat = ref("excel");
const exportPreviewLoading = ref(false);

const errorMsg = ref("");
const exportErrorMsg = ref("");

const totalInstitucional = ref(0);
const totalResultados = ref(0);
const exportPreviewCount = ref(0);

const typeCounts = ref(
  Object.fromEntries(
    TIPOS_LIST.map((tipo) => [tipo.value, 0])
  )
);

const exportTypeCounts = ref(
  Object.fromEntries(
    TIPOS_LIST.map((tipo) => [tipo.value, 0])
  )
);

let mainReloadTimer = null;
let exportPreviewTimer = null;
let listRequestSequence = 0;
let typeCountRequestSequence = 0;
let exportPreviewRequestSequence = 0;
let yearsRequestSequence = 0;
let hasLoadedOnce = false;

/* ============================================================
  HELPERS DE INTERFAZ
============================================================ */

function focusSearch() {
  searchEl.value?.focus();
}

function handleSearchAction() {
  if (textoFiltroActivo.value) {
    textoFiltroActivo.value = "";
    focusSearch();
    return;
  }

  focusSearch();
}

function abrirPanelFiltros() {
  panelLateralActivo.value = "filtros";
}

async function abrirPanelExportacion() {
  panelLateralActivo.value = "export";
  await syncExportFiltersFromVisible();
}

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

  return [];
}

function extractTotal(payload, fallback = 0) {
  const count = Number(
    payload?.count ??
      payload?.total ??
      payload?.pagination?.count
  );

  return Number.isFinite(count)
    ? count
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
  fallback = "No se pudieron cargar los datos."
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
  METADATOS DE PUBLICACIÓN
============================================================ */

function getResolvedMeta(publicacion) {
  return (
    publicacion?.__tipoMeta ||
    getTipoPublicacionMetaFromItem(publicacion)
  );
}

function resolveType(publicacion) {
  const meta = getResolvedMeta(publicacion);

  return meta?.codigo || "OTRO";
}

function resolveLabel(publicacion) {
  const meta = getResolvedMeta(publicacion);

  if (meta?.codigo && meta.codigo !== "OTRO") {
    return meta.label;
  }

  return (
    String(
      publicacion?.tipo_publicacion_final_label ||
        publicacion?.tipo_publicacion_final ||
        publicacion?.tipo ||
        "Publicación"
    ).trim() || "Publicación"
  );
}

function resolveOrigenCode(publicacion) {
  const value = String(
    publicacion?.origen_tipo || ""
  )
    .trim()
    .toLowerCase();

  return value || "ninguno";
}

function resolveOrigenLabel(publicacion) {
  const code = resolveOrigenCode(publicacion);

  return (
    String(
      publicacion?.origen_tipo_label ||
        ORIGEN_LABELS[code] ||
        code
    ).trim() || "Ninguno"
  );
}

function resolveOrigenResumen(publicacion) {
  const provided = String(
    publicacion?.origen_resumen || ""
  ).trim();

  if (provided) {
    return provided;
  }

  const code = resolveOrigenCode(publicacion);

  if (!code || code === "ninguno") {
    return "";
  }

  const label = resolveOrigenLabel(publicacion);
  const detail = String(
    publicacion?.origen_grado || ""
  ).trim();

  if (["tic", "otro"].includes(code) && detail) {
    return `${label} · ${detail}`;
  }

  return label;
}

function buildAcademicMeta(publicacion) {
  const sede = String(
    publicacion?.sede ||
      publicacion?.sede_nombre ||
      ""
  ).trim();

  const facultad = String(
    publicacion?.facultad || ""
  ).trim();

  const carrera = String(
    publicacion?.carrera || ""
  ).trim();

  const parts = [
    sede,
    facultad,
    carrera,
  ].filter(Boolean);

  return parts.length
    ? parts.join(" · ")
    : "Sin ubicación académica";
}

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

/* ============================================================
  CONSTRUCCIÓN ÚNICA DE PARÁMETROS
============================================================ */

function resolveTipoApiValue(tipoValue) {
  if (!tipoValue || tipoValue === TIPOS.ALL.value) {
    return "";
  }

  const tipo = TIPOS_LIST.find((item) => {
    return (
      item.value === tipoValue ||
      item.apiValue === tipoValue
    );
  });

  return tipo?.apiValue || tipoValue;
}

function buildParamsFromState({
  tipo,
  origen,
  anio,
  mes,
  anioDesde,
  anioHasta,
  texto,
  sede,
  facultad,
  carrera,
  proyecto,
  soloConPdf: filterSoloConPdf,
  orden,
}) {
  const params = {};

  const tipoApiValue = resolveTipoApiValue(tipo);

  if (tipoApiValue) {
    params.tipo = tipoApiValue;
  }

  if (origen && origen !== "ALL") {
    params.origen_tipo = origen;
  }

  if (anio) {
    params.anio = anio;
  } else {
    if (anioDesde) {
      params.anio_desde = anioDesde;
    }

    if (anioHasta) {
      params.anio_hasta = anioHasta;
    }
  }

  if (mes) {
    params.mes = mes;
  }

  if (texto?.trim()) {
    params.texto = texto.trim();
  }

  if (sede) {
    params.sede = sede;
  }

  if (facultad) {
    params.facultad = facultad;
  }

  if (carrera) {
    params.carrera = carrera;
  }

  if (proyecto) {
    params.proyecto = proyecto;
  }

  if (filterSoloConPdf) {
    params.solo_con_pdf = "true";
  }

  if (orden) {
    params.orden = orden;
  }

  return params;
}

function getMainFilterState({
  includeType = true,
  includeOrdering = true,
} = {}) {
  return {
    tipo: includeType
      ? filtroTipo.value
      : TIPOS.ALL.value,
    origen: filtroOrigen.value,
    anio: filtroAnio.value,
    mes: filtroMes.value,
    anioDesde: filtroAnioDesde.value,
    anioHasta: filtroAnioHasta.value,
    texto: filtroTexto.value,
    sede: filtroSede.value,
    facultad: filtroFacultad.value,
    carrera: filtroCarrera.value,
    proyecto: filtroProyecto.value,
    soloConPdf: soloConPdf.value,
    orden: includeOrdering
      ? ordenListado.value
      : "",
  };
}

function getExportFilterState() {
  return {
    tipo: exportFiltroTipo.value,
    origen: exportFiltroOrigen.value,
    anio: exportFiltroAnio.value,
    mes: exportFiltroMes.value,
    anioDesde: exportFiltroAnioDesde.value,
    anioHasta: exportFiltroAnioHasta.value,
    texto: exportFiltroTexto.value,
    sede: exportFiltroSede.value,
    facultad: exportFiltroFacultad.value,
    carrera: exportFiltroCarrera.value,
    proyecto: exportFiltroProyecto.value,
    soloConPdf: exportSoloConPdf.value,
    orden: "",
  };
}

/* ============================================================
  ESTADOS COMPUTADOS
============================================================ */

const tipoFiltroActivo = computed({
  get() {
    return panelLateralActivo.value === "export"
      ? exportFiltroTipo.value
      : filtroTipo.value;
  },

  set(value) {
    if (panelLateralActivo.value === "export") {
      exportFiltroTipo.value = value;
      return;
    }

    filtroTipo.value = value;
  },
});

const textoFiltroActivo = computed({
  get() {
    return panelLateralActivo.value === "export"
      ? exportFiltroTexto.value
      : filtroTexto.value;
  },

  set(value) {
    if (panelLateralActivo.value === "export") {
      exportFiltroTexto.value = value;
      return;
    }

    filtroTexto.value = value;
  },
});

const listaFiltrada = computed(() => {
  if (panelLateralActivo.value === "export") {
    return exportPreviewPublicaciones.value;
  }

  return publicaciones.value;
});

const totalResultadosVisibles = computed(() => {
  if (panelLateralActivo.value === "export") {
    return exportPreviewCount.value;
  }

  return totalResultados.value;
});

const resultadosLoading = computed(() => {
  if (panelLateralActivo.value === "export") {
    return exportPreviewLoading.value;
  }

  return loading.value;
});

const resultadosErrorMsg = computed(() => {
  if (panelLateralActivo.value === "export") {
    return exportErrorMsg.value;
  }

  return errorMsg.value;
});

const hayBusqueda = computed(() => {
  return Boolean(filtroTexto.value?.trim());
});

const hayBusquedaExportacion = computed(() => {
  return Boolean(exportFiltroTexto.value?.trim());
});

const hayFiltros = computed(() => {
  return (
    filtroTipo.value !== TIPOS.ALL.value ||
    filtroOrigen.value !== "ALL" ||
    Boolean(filtroAnio.value) ||
    Boolean(filtroMes.value) ||
    Boolean(filtroAnioDesde.value) ||
    Boolean(filtroAnioHasta.value) ||
    Boolean(filtroSede.value) ||
    Boolean(filtroFacultad.value) ||
    Boolean(filtroCarrera.value) ||
    Boolean(filtroProyecto.value) ||
    soloConPdf.value
  );
});

const hayFiltrosExportacion = computed(() => {
  return (
    exportFiltroTipo.value !== TIPOS.ALL.value ||
    exportFiltroOrigen.value !== "ALL" ||
    Boolean(exportFiltroAnio.value) ||
    Boolean(exportFiltroMes.value) ||
    Boolean(exportFiltroAnioDesde.value) ||
    Boolean(exportFiltroAnioHasta.value) ||
    Boolean(exportFiltroSede.value) ||
    Boolean(exportFiltroFacultad.value) ||
    Boolean(exportFiltroCarrera.value) ||
    Boolean(exportFiltroProyecto.value) ||
    exportSoloConPdf.value
  );
});

const hayBusquedaVisible = computed(() => {
  return panelLateralActivo.value === "export"
    ? hayBusquedaExportacion.value
    : hayBusqueda.value;
});

const hayFiltrosVisibles = computed(() => {
  return panelLateralActivo.value === "export"
    ? hayFiltrosExportacion.value
    : hayFiltros.value;
});

const activeAdvancedFiltersCount = computed(() => {
  const hasPeriod = Boolean(
    filtroAnio.value ||
      filtroMes.value ||
      filtroAnioDesde.value ||
      filtroAnioHasta.value
  );

  return [
    Boolean(filtroSede.value),
    Boolean(filtroFacultad.value),
    Boolean(filtroCarrera.value),
    Boolean(filtroProyecto.value),
    filtroOrigen.value !== "ALL",
    hasPeriod,
    soloConPdf.value,
  ].filter(Boolean).length;
});

const totalActiveFiltersCount = computed(() => {
  let total = activeAdvancedFiltersCount.value;

  if (filtroTipo.value !== TIPOS.ALL.value) {
    total += 1;
  }

  if (hayBusqueda.value) {
    total += 1;
  }

  return total;
});

const exportActiveFiltersCount = computed(() => {
  const hasPeriod = Boolean(
    exportFiltroAnio.value ||
      exportFiltroMes.value ||
      exportFiltroAnioDesde.value ||
      exportFiltroAnioHasta.value
  );

  return [
    exportFiltroTipo.value !== TIPOS.ALL.value,
    exportFiltroOrigen.value !== "ALL",
    Boolean(exportFiltroFacultad.value),
    Boolean(exportFiltroCarrera.value),
    Boolean(exportFiltroProyecto.value),
    hasPeriod,
    exportSoloConPdf.value,
    hayBusquedaExportacion.value,
  ].filter(Boolean).length;
});

const totalActiveFiltersCountVisible = computed(() => {
  return panelLateralActivo.value === "export"
    ? exportActiveFiltersCount.value
    : totalActiveFiltersCount.value;
});


const advancedOnlyFiltersCount = computed(() => {
  const hasPeriod = Boolean(
    filtroAnio.value ||
      filtroMes.value ||
      filtroAnioDesde.value ||
      filtroAnioHasta.value
  );

  return [
    Boolean(filtroProyecto.value),
    filtroOrigen.value !== "ALL",
    hasPeriod,
  ].filter(Boolean).length;
});

function findCatalogLabel(items, value, fallback = "") {
  if (!value) return fallback;

  const item = items.find(
    (entry) => String(entry?.id) === String(value)
  );

  return String(item?.nombre || fallback || value).trim();
}

function getMonthLabel(value) {
  if (!value) return "";

  return (
    MESES_LIST.find(
      (item) => String(item.value) === String(value)
    )?.label || ""
  );
}

const periodFilterLabel = computed(() => {
  if (filtroAnio.value) {
    const month = getMonthLabel(filtroMes.value);
    return month
      ? `${month} de ${filtroAnio.value}`
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
    return getMonthLabel(filtroMes.value);
  }

  return "";
});

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
    const origin = ORIGENES_LIST.find(
      (item) => item.value === filtroOrigen.value
    );

    chips.push({
      key: "origen",
      label: origin?.label || "Origen",
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

function compactAuthors(value, maxVisible = 2) {
  const text = String(value || "").trim();

  if (!text) return "";

  const authors = text
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  if (authors.length <= maxVisible) {
    return text;
  }

  const visible = authors.slice(0, maxVisible).join(", ");
  const remaining = authors.length - maxVisible;

  return `${visible} · +${remaining} ${remaining === 1 ? "autor" : "autores"}`;
}

function hasPublicationPdf(publicacion) {
  return Boolean(
    publicacion?.tiene_pdf ||
      publicacion?.archivo_pdf ||
      publicacion?.archivo_pdf_url ||
      publicacion?.pdf ||
      publicacion?.pdf_url ||
      publicacion?.documento_pdf
  );
}

const emptyTitle = computed(() => {
  if (hayBusquedaVisible.value || hayFiltrosVisibles.value) {
    return panelLateralActivo.value === "export"
      ? "El reporte no contiene publicaciones"
      : "No se encontraron publicaciones";
  }

  return "No hay publicaciones registradas";
});

const emptyText = computed(() => {
  if (hayBusquedaVisible.value || hayFiltrosVisibles.value) {
    return panelLateralActivo.value === "export"
      ? (
          "No existen registros que coincidan con los " +
          "criterios seleccionados para el archivo Excel."
        )
      : (
          "No existen resultados que coincidan con los " +
          "criterios seleccionados."
        );
  }

  return (
    "Todavía no existen publicaciones disponibles " +
    "para esta consulta."
  );
});

/* ============================================================
  CONTEOS
============================================================ */

function countByType(typeValue) {
  return Number(
    typeCounts.value?.[typeValue] || 0
  );
}

function countByTypeVisible(typeValue) {
  const counts =
    panelLateralActivo.value === "export"
      ? exportTypeCounts.value
      : typeCounts.value;

  return Number(
    counts?.[typeValue] || 0
  );
}

function syncYearFiltersWithCatalog() {
  const availableYears = new Set(
    añosDisponibles.value.map(
      (value) => String(value)
    )
  );

  const syncGroup = (
    exactRef,
    fromRef,
    toRef
  ) => {
    if (
      exactRef.value &&
      !availableYears.has(
        String(exactRef.value)
      )
    ) {
      exactRef.value = "";
    }

    if (
      fromRef.value &&
      !availableYears.has(
        String(fromRef.value)
      )
    ) {
      fromRef.value = "";
    }

    if (
      toRef.value &&
      !availableYears.has(
        String(toRef.value)
      )
    ) {
      toRef.value = "";
    }

    normalizeYearRange(
      fromRef,
      toRef
    );
  };

  syncGroup(
    filtroAnio,
    filtroMes,
    filtroAnioDesde,
    filtroAnioHasta
  );

  syncGroup(
    exportFiltroAnio,
    exportFiltroMes,
    exportFiltroAnioDesde,
    exportFiltroAnioHasta
  );
}

async function loadAvailableYears() {
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

    syncYearFiltersWithCatalog();
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

async function loadTotalInstitucional() {
  try {
    const response = await api.get(
      EXPORT_PREVIEW_ENDPOINT
    );

    totalInstitucional.value = Number(
      response.data?.total || 0
    );
  } catch (error) {
    console.error(
      "Error cargando el total institucional:",
      error
    );
  }
}

async function loadTypeCounts() {
  const requestSequence =
    ++typeCountRequestSequence;

  const baseParams = buildParamsFromState(
    getMainFilterState({
      includeType: false,
      includeOrdering: false,
    })
  );

  try {
    const responses = await Promise.all(
      TIPOS_LIST.map((tipo) => {
        const params = {
          ...baseParams,
        };

        if (tipo.value !== TIPOS.ALL.value) {
          params.tipo = tipo.apiValue || tipo.value;
        }

        return api.get(
          EXPORT_PREVIEW_ENDPOINT,
          {
            params,
          }
        );
      })
    );

    if (
      requestSequence !==
      typeCountRequestSequence
    ) {
      return;
    }

    typeCounts.value = Object.fromEntries(
      TIPOS_LIST.map((tipo, index) => [
        tipo.value,
        Number(
          responses[index]?.data?.total || 0
        ),
      ])
    );
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
  CARGA DE PUBLICACIONES DESDE EL BACKEND
============================================================ */

async function loadPublicaciones({
  forceSkeleton = false,
} = {}) {
  const requestSequence = ++listRequestSequence;
  const showSkeleton =
    forceSkeleton || !hasLoadedOnce;

  if (showSkeleton) {
    loading.value = true;
  }

  errorMsg.value = "";

  try {
    const params = buildParamsFromState(
      getMainFilterState()
    );

    const response = await api.get(
      LIST_ENDPOINT,
      {
        params,
      }
    );

    if (requestSequence !== listRequestSequence) {
      return;
    }

    const items = extractArray(response.data).map(
      (publicacion) => ({
        ...publicacion,
        __tipoMeta:
          getTipoPublicacionMetaFromItem(
            publicacion
          ),
      })
    );

    publicaciones.value = items;
    totalResultados.value = extractTotal(
      response.data,
      items.length
    );

    hasLoadedOnce = true;

    void loadTypeCounts();
  } catch (error) {
    if (requestSequence !== listRequestSequence) {
      return;
    }

    console.error(
      "Error cargando publicaciones:",
      error
    );

    publicaciones.value = [];
    totalResultados.value = 0;
    errorMsg.value = extractErrorMessage(
      error,
      "No se pudieron cargar las publicaciones."
    );
  } finally {
    if (requestSequence === listRequestSequence) {
      loading.value = false;
    }
  }
}

function scheduleMainReload(delay = MAIN_FILTER_DEBOUNCE_MS) {
  window.clearTimeout(mainReloadTimer);

  mainReloadTimer = window.setTimeout(() => {
    void loadPublicaciones();
  }, delay);
}

/* ============================================================
  CATÁLOGOS
============================================================ */

async function loadSedes() {
  const response = await api.get(
    "/selects/sedes/"
  );

  sedes.value = extractArray(response.data);
}

async function loadFacultades() {
  const response = await api.get(
    "/selects/facultades/"
  );

  facultades.value = extractArray(response.data);
}

async function fetchCarrerasByFacultad(
  facultadId,
  sedeId = ""
) {
  if (!facultadId && !sedeId) {
    return [];
  }

  const response = await api.get(
    "/selects/carreras/",
    {
      params: {
        facultad_id: facultadId || undefined,
        sede_id: sedeId || undefined,
      },
    }
  );

  return extractArray(response.data);
}

async function fetchProyectosByCarrera(
  carreraId,
  sedeId = ""
) {
  if (!carreraId) {
    return [];
  }

  const response = await api.get(
    `/selects/proyectos/${carreraId}/`,
    {
      params: {
        sede_id: sedeId || undefined,
      },
    }
  );

  return extractArray(response.data);
}

/* ============================================================
  LIMPIEZA DE FILTROS
============================================================ */

function limpiarFiltros() {
  filtroTipo.value = TIPOS.ALL.value;
  filtroOrigen.value = "ALL";
  ordenListado.value = "recientes";
  filtroAnio.value = "";
  filtroMes.value = "";
  filtroAnioDesde.value = "";
  filtroAnioHasta.value = "";
  filtroTexto.value = "";
  filtroSede.value = "";
  filtroFacultad.value = "";
  filtroCarrera.value = "";
  filtroProyecto.value = "";
  soloConPdf.value = false;

  carreras.value = [];
  proyectos.value = [];
}

function limpiarExportFilters() {
  exportFiltroTipo.value = TIPOS.ALL.value;
  exportFiltroOrigen.value = "ALL";
  exportFiltroAnio.value = "";
  exportFiltroMes.value = "";
  exportFiltroAnioDesde.value = "";
  exportFiltroAnioHasta.value = "";
  exportFiltroTexto.value = "";
  exportFiltroSede.value = "";
  exportFiltroFacultad.value = "";
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";
  exportSoloConPdf.value = false;

  exportCarreras.value = [];
  exportProyectos.value = [];
  exportErrorMsg.value = "";
}

function limpiarFiltrosVisibles() {
  if (panelLateralActivo.value === "export") {
    limpiarExportFilters();
    return;
  }

  limpiarFiltros();
}

function reintentarCargaVisible() {
  if (panelLateralActivo.value === "export") {
    void loadExportPreview();
    return;
  }

  void cargarDatosIniciales();
}

/* ============================================================
  SINCRONIZACIÓN DE FILTROS DE EXPORTACIÓN
============================================================ */

async function syncExportFiltersFromVisible() {
  exportFiltroTipo.value = filtroTipo.value;
  exportFiltroOrigen.value = filtroOrigen.value;
  exportFiltroAnio.value = filtroAnio.value;
  exportFiltroMes.value = filtroMes.value;
  exportFiltroAnioDesde.value =
    filtroAnioDesde.value;
  exportFiltroAnioHasta.value =
    filtroAnioHasta.value;
  exportFiltroTexto.value = filtroTexto.value;
  exportFiltroSede.value = filtroSede.value;
  exportFiltroFacultad.value =
    filtroFacultad.value;
  exportFiltroCarrera.value =
    filtroCarrera.value;
  exportFiltroProyecto.value =
    filtroProyecto.value;
  exportSoloConPdf.value =
    soloConPdf.value;

  exportCarreras.value = [];
  exportProyectos.value = [];
  exportErrorMsg.value = "";

  try {
    if (
      exportFiltroSede.value ||
      exportFiltroFacultad.value
    ) {
      exportCarreras.value =
        await fetchCarrerasByFacultad(
          exportFiltroFacultad.value,
          exportFiltroSede.value
        );
    }

    if (exportFiltroCarrera.value) {
      exportProyectos.value =
        await fetchProyectosByCarrera(
          exportFiltroCarrera.value,
          exportFiltroSede.value
        );
    }
  } catch (error) {
    console.error(
      "Error sincronizando catálogos de exportación:",
      error
    );
  }

  scheduleExportPreview(0);
}

/* ============================================================
  CATÁLOGOS DEPENDIENTES PRINCIPALES
============================================================ */

async function onMainSedeChange() {
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  if (
    !filtroSede.value &&
    !filtroFacultad.value
  ) {
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasByFacultad(
        filtroFacultad.value,
        filtroSede.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras por sede:",
      error
    );

    carreras.value = [];
  }
}

async function onMainFacultadChange() {
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  if (
    !filtroSede.value &&
    !filtroFacultad.value
  ) {
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasByFacultad(
        filtroFacultad.value,
        filtroSede.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras:",
      error
    );

    carreras.value = [];
  }
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
        filtroCarrera.value,
        filtroSede.value
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
  CATÁLOGOS DEPENDIENTES DE EXPORTACIÓN
============================================================ */

async function onExportSedeChange() {
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";

  exportCarreras.value = [];
  exportProyectos.value = [];

  if (
    !exportFiltroSede.value &&
    !exportFiltroFacultad.value
  ) {
    return;
  }

  try {
    exportCarreras.value =
      await fetchCarrerasByFacultad(
        exportFiltroFacultad.value,
        exportFiltroSede.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras por sede para exportación:",
      error
    );

    exportCarreras.value = [];
  }
}

async function onExportFacultadChange() {
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";

  exportCarreras.value = [];
  exportProyectos.value = [];

  if (
    !exportFiltroSede.value &&
    !exportFiltroFacultad.value
  ) {
    return;
  }

  try {
    exportCarreras.value =
      await fetchCarrerasByFacultad(
        exportFiltroFacultad.value,
        exportFiltroSede.value
      );
  } catch (error) {
    console.error(
      "Error cargando carreras para exportación:",
      error
    );

    exportCarreras.value = [];
  }
}

async function onExportCarreraChange() {
  exportFiltroProyecto.value = "";
  exportProyectos.value = [];

  if (!exportFiltroCarrera.value) {
    return;
  }

  try {
    exportProyectos.value =
      await fetchProyectosByCarrera(
        exportFiltroCarrera.value,
        exportFiltroSede.value
      );
  } catch (error) {
    console.error(
      "Error cargando proyectos para exportación:",
      error
    );

    exportProyectos.value = [];
  }
}

/* ============================================================
  VISTA PREVIA DE EXPORTACIÓN
============================================================ */

async function loadExportPreview() {
  const requestSequence =
    ++exportPreviewRequestSequence;

  exportPreviewLoading.value = true;
  exportErrorMsg.value = "";

  try {
    const exportState = getExportFilterState();

    const params = buildParamsFromState(
      exportState
    );

    const countParams = buildParamsFromState({
      ...exportState,
      tipo: TIPOS.ALL.value,
    });

    const [
      previewResponse,
      publicacionesResponse,
      countSourceResponse,
    ] = await Promise.all([
      api.get(
        EXPORT_PREVIEW_ENDPOINT,
        {
          params,
        }
      ),

      api.get(
        LIST_ENDPOINT,
        {
          params,
        }
      ),

      api.get(
        LIST_ENDPOINT,
        {
          params: countParams,
        }
      ),
    ]);

    if (
      requestSequence !==
      exportPreviewRequestSequence
    ) {
      return;
    }

    const previewItems = extractArray(
      publicacionesResponse.data
    ).map((publicacion) => ({
      ...publicacion,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          publicacion
        ),
    }));

    const countSourceItems = extractArray(
      countSourceResponse.data
    ).map((publicacion) => ({
      ...publicacion,
      __tipoMeta:
        getTipoPublicacionMetaFromItem(
          publicacion
        ),
    }));

    exportPreviewPublicaciones.value =
      previewItems;

    const previewTotal = Number(
      previewResponse.data?.total
    );

    exportPreviewCount.value =
      Number.isFinite(previewTotal)
        ? previewTotal
        : extractTotal(
            publicacionesResponse.data,
            previewItems.length
          );

    const counts = Object.fromEntries(
      TIPOS_LIST.map((tipo) => [
        tipo.value,
        0,
      ])
    );

    counts[TIPOS.ALL.value] = extractTotal(
      countSourceResponse.data,
      countSourceItems.length
    );

    countSourceItems.forEach((item) => {
      const typeCode = resolveType(item);

      if (
        Object.hasOwn(
          counts,
          typeCode
        )
      ) {
        counts[typeCode] += 1;
      }
    });

    exportTypeCounts.value = counts;
  } catch (error) {
    if (
      requestSequence !==
      exportPreviewRequestSequence
    ) {
      return;
    }

    console.error(
      "Error cargando vista previa de exportación:",
      error
    );

    exportPreviewCount.value = 0;
    exportPreviewPublicaciones.value = [];

    exportTypeCounts.value =
      Object.fromEntries(
        TIPOS_LIST.map((tipo) => [
          tipo.value,
          0,
        ])
      );

    exportErrorMsg.value = extractErrorMessage(
      error,
      "No se pudo preparar la vista previa de la descarga."
    );
  } finally {
    if (
      requestSequence ===
      exportPreviewRequestSequence
    ) {
      exportPreviewLoading.value = false;
    }
  }
}

function scheduleExportPreview(
  delay = EXPORT_PREVIEW_DEBOUNCE_MS
) {
  window.clearTimeout(exportPreviewTimer);

  exportPreviewTimer = window.setTimeout(() => {
    void loadExportPreview();
  }, delay);
}

/* ============================================================
  EXPORTACIÓN EXCEL
============================================================ */

async function confirmarExportacion() {
  exporting.value = true;
  exportErrorMsg.value = "";

  try {
    const params = buildParamsFromState(
      getExportFilterState()
    );

    const isPdf =
      exportFormat.value === "pdf";

    const endpoint = isPdf
      ? EXPORT_PDF_ENDPOINT
      : EXPORT_EXCEL_ENDPOINT;

    const response = await api.get(
      endpoint,
      {
        params,
        responseType: "blob",
      }
    );

    const mimeType = isPdf
      ? "application/pdf"
      : (
          "application/vnd.openxmlformats-" +
          "officedocument.spreadsheetml.sheet"
        );

    const extension = isPdf
      ? "pdf"
      : "xlsx";

    const blob = new Blob(
      [response.data],
      {
        type: mimeType,
      }
    );

    const url =
      window.URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    const timestamp = new Date()
      .toISOString()
      .slice(0, 19)
      .replace(/[:T]/g, "-");

    link.href = url;
    link.setAttribute(
      "download",
      `reporte_publicaciones_${timestamp}.${extension}`
    );

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 1000);
  } catch (error) {
    console.error(
      `Error exportando ${exportFormat.value}:`,
      error
    );

    exportErrorMsg.value =
      extractErrorMessage(
        error,
        exportFormat.value === "pdf"
          ? "No se pudo generar el archivo PDF."
          : "No se pudo generar el archivo Excel."
      );
  } finally {
    exporting.value = false;
  }
}

/* ============================================================
  NAVEGACIÓN AL DETALLE
============================================================ */

function verDetalles(id) {
  if (!id) {
    return;
  }

  router.push({
    path: `/publicacion/${id}`,
    query: {
      from: "publicaciones",
    },
  });
}

/* ============================================================
  ATAJOS DE TECLADO
============================================================ */

function handleGlobalKeydown(event) {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform
      .toLowerCase()
      .includes("mac");

  const key = String(event.key || "").toLowerCase();

  const searchShortcut =
    (isMac && event.metaKey && key === "k") ||
    (!isMac && event.ctrlKey && key === "k");

  if (searchShortcut) {
    event.preventDefault();
    focusSearch();
  }

  if (
    event.key === "Escape" &&
    hayBusquedaVisible.value
  ) {
    textoFiltroActivo.value = "";
  }
}

/* ============================================================
  WATCHERS
============================================================ */

watch(panelLateralActivo, (panel) => {
  if (panel === "export") {
    scheduleExportPreview(0);
  }
});

function normalizeYearRange(desdeRef, hastaRef) {
  const desde = Number(desdeRef.value);
  const hasta = Number(hastaRef.value);

  if (
    !Number.isInteger(desde) ||
    !Number.isInteger(hasta) ||
    desde <= hasta
  ) {
    return;
  }

  const previousDesde = desdeRef.value;
  desdeRef.value = hastaRef.value;
  hastaRef.value = previousDesde;
}

watch(filtroAnio, (value) => {
  if (value) {
    filtroAnioDesde.value = "";
    filtroAnioHasta.value = "";
  }
});

watch(
  [filtroAnioDesde, filtroAnioHasta],
  ([desde, hasta]) => {
    if (desde || hasta) {
      filtroAnio.value = "";
    }

    normalizeYearRange(
      filtroAnioDesde,
      filtroAnioHasta
    );
  }
);

watch(exportFiltroAnio, (value) => {
  if (value) {
    exportFiltroAnioDesde.value = "";
    exportFiltroAnioHasta.value = "";
  }
});

watch(
  [exportFiltroAnioDesde, exportFiltroAnioHasta],
  ([desde, hasta]) => {
    if (desde || hasta) {
      exportFiltroAnio.value = "";
    }

    normalizeYearRange(
      exportFiltroAnioDesde,
      exportFiltroAnioHasta
    );
  }
);

watch(
  [
    filtroTipo,
    filtroOrigen,
    ordenListado,
    filtroAnio,
    filtroAnioDesde,
    filtroAnioHasta,
    filtroTexto,
    filtroSede,
    filtroFacultad,
    filtroCarrera,
    filtroProyecto,
    soloConPdf,
  ],
  () => {
    scheduleMainReload();
  }
);

watch(
  [
    exportFiltroTipo,
    exportFiltroOrigen,
    exportFiltroAnio,
    exportFiltroAnioDesde,
    exportFiltroAnioHasta,
    exportFiltroTexto,
    exportFiltroSede,
    exportFiltroFacultad,
    exportFiltroCarrera,
    exportFiltroProyecto,
    exportSoloConPdf,
  ],
  () => {
    if (panelLateralActivo.value === "export") {
      scheduleExportPreview();
    }
  }
);

/* ============================================================
  CICLO DE VIDA
============================================================ */

async function cargarDatosIniciales() {
  errorMsg.value = "";

  try {
    await Promise.all([
      loadSedes(),
      loadFacultades(),
      loadAvailableYears(),
      loadTotalInstitucional(),
      loadPublicaciones({
        forceSkeleton: true,
      }),
    ]);
  } catch (error) {
    console.error(
      "Error cargando datos iniciales:",
      error
    );

    errorMsg.value = extractErrorMessage(
      error,
      "No se pudieron cargar los datos iniciales."
    );
  }
}

onMounted(async () => {
  window.addEventListener(
    "keydown",
    handleGlobalKeydown
  );

  await cargarDatosIniciales();
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    handleGlobalKeydown
  );

  window.clearTimeout(mainReloadTimer);
  window.clearTimeout(exportPreviewTimer);

  listRequestSequence += 1;
  typeCountRequestSequence += 1;
  exportPreviewRequestSequence += 1;
  yearsRequestSequence += 1;
});
</script>

<style src="./sgpc-listados-base.css"></style>
<style src="./listado-publicaciones.css"></style>
