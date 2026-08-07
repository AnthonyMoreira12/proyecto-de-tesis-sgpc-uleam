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
          <span class="pub-eyebrow">
            Producción científica
          </span>

          <h1 class="pub-title">
            Publicaciones institucionales
          </h1>

          <p class="pub-subtitle">
            Consulte, filtre y exporte la producción científica registrada en
            el sistema.
          </p>

          <div
            class="pub-chips"
            aria-label="Resumen general de publicaciones"
          >
            <span class="pub-chip">
              Total:
              <strong>{{ totalInstitucional }}</strong>
            </span>

            <span class="pub-chip">
              Resultados:
              <strong>{{ totalResultadosVisibles }}</strong>
            </span>

            <span
              v-if="totalActiveFiltersCountVisible"
              class="pub-chip pub-chip--active"
            >
              Filtros:
              <strong>{{ totalActiveFiltersCountVisible }}</strong>
            </span>
          </div>
        </div>

        <div
          class="pub-header__tools"
          aria-label="Herramientas principales"
        >
          <label
            class="search search--navbar"
            aria-label="Buscar publicación"
          >
            <span
              class="search__lead"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                class="search__svg"
                aria-hidden="true"
              >
                <path
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 1 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </span>

            <input
              id="fTexto"
              ref="searchEl"
              v-model="textoFiltroActivo"
              class="search__input"
              type="search"
              inputmode="search"
              autocomplete="off"
              placeholder="Buscar por título, autor, tipo, proyecto, facultad o carrera…"
            />

            <button
              type="button"
              class="search__action"
              :aria-label="
                hayBusquedaVisible
                  ? 'Limpiar búsqueda'
                  : 'Enfocar campo de búsqueda'
              "
              @click="handleSearchAction"
            >
              <span
                v-if="hayBusquedaVisible"
                class="search__x"
                aria-hidden="true"
              >
                ×
              </span>

              <svg
                v-else
                viewBox="0 0 24 24"
                class="search__svg"
                aria-hidden="true"
              >
                <path
                  d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Zm6.1-1.06 4.05 4.06a1 1 0 1 1-1.42 1.42l-4.06-4.05a9 9 0 1 1 1.42-1.42Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </label>

          <div
            class="pub-header__actions"
            aria-label="Acciones del listado"
          >
            <button
              class="pub-btn pub-btn--ghost"
              :class="{
                'is-active': panelLateralActivo === 'filtros',
              }"
              type="button"
              :aria-pressed="panelLateralActivo === 'filtros'"
              @click="abrirPanelFiltros"
            >
              Filtros
            </button>

            <button
              class="pub-btn pub-btn--primary"
              :class="{
                'is-active': panelLateralActivo === 'export',
              }"
              type="button"
              :aria-pressed="panelLateralActivo === 'export'"
              :disabled="loading"
              @click="abrirPanelExportacion"
            >
              Exportar Excel
            </button>
          </div>
        </div>
      </header>

      <!-- =====================================================
        CONTENIDO GENERAL
      ====================================================== -->
      <section
        class="pub-layout page-stage page-stage-2"
        aria-label="Consulta de publicaciones"
      >
        <!-- ===================================================
          PANEL LATERAL
        ==================================================== -->
        <aside
          class="pub-side"
          aria-label="Panel lateral de consulta"
        >
          <div class="pub-sideStack">
            <!-- ===============================================
              FILTROS AVANZADOS
            ================================================ -->
            <section
              v-if="panelLateralActivo === 'filtros'"
              class="pub-sidePanel"
            >
              <header class="pub-sidePanel__head">
                <div>
                  <span class="pub-sidePanel__eyebrow">
                    Refinar resultados
                  </span>

                  <h2 class="pub-sidePanel__title">
                    Filtros
                  </h2>
                </div>

                <span
                  class="pub-sidePanel__badge"
                  aria-label="Cantidad de filtros avanzados activos"
                >
                  {{ activeAdvancedFiltersCount }}
                </span>
              </header>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Ubicación académica
                </h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fFacultad"
                    >
                      Facultad
                    </label>

                    <select
                      id="fFacultad"
                      v-model="filtroFacultad"
                      class="pub-select"
                      @change="onMainFacultadChange"
                    >
                      <option value="">
                        Todas las facultades
                      </option>

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
                    <label
                      class="pub-label"
                      for="fCarrera"
                    >
                      Carrera
                    </label>

                    <select
                      id="fCarrera"
                      v-model="filtroCarrera"
                      class="pub-select"
                      :disabled="!filtroFacultad"
                      @change="onMainCarreraChange"
                    >
                      <option value="">
                        Todas las carreras
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

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fProyecto"
                    >
                      Proyecto
                    </label>

                    <select
                      id="fProyecto"
                      v-model="filtroProyecto"
                      class="pub-select"
                      :disabled="!filtroCarrera"
                    >
                      <option value="">
                        Todos los proyectos
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
                </div>
              </section>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Origen y ordenamiento
                </h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fOrigen"
                    >
                      Origen
                    </label>

                    <select
                      id="fOrigen"
                      v-model="filtroOrigen"
                      class="pub-select"
                    >
                      <option
                        v-for="origen in ORIGENES_LIST"
                        :key="`origen-${origen.value}`"
                        :value="origen.value"
                      >
                        {{ origen.label }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fOrden"
                    >
                      Ordenar por
                    </label>

                    <select
                      id="fOrden"
                      v-model="ordenListado"
                      class="pub-select"
                    >
                      <option
                        v-for="option in ORDENES_LIST"
                        :key="`orden-${option.value}`"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Disponibilidad
                </h3>

                <label
                  class="pub-toggleCard"
                  for="fSoloPdf"
                >
                  <input
                    id="fSoloPdf"
                    v-model="soloConPdf"
                    class="pub-toggleCard__input"
                    type="checkbox"
                  />

                  <span
                    class="pub-toggleCard__control"
                    aria-hidden="true"
                  >
                    <span class="pub-toggleCard__thumb"></span>
                  </span>

                  <span class="pub-toggleCard__content">
                    <strong class="pub-toggleCard__title">
                      Solo con PDF
                    </strong>

                    <span class="pub-toggleCard__description">
                      Incluye PDF principal o archivos adjuntos.
                    </span>
                  </span>
                </label>
              </section>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Período de publicación
                </h3>

                <div
                  class="
                    pub-sidePanel__fields
                    pub-sidePanel__fields--years
                  "
                >
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fAnio"
                    >
                      Año exacto
                    </label>

                    <select
                      id="fAnio"
                      v-model="filtroAnio"
                      class="pub-select"
                      :disabled="
                        loadingAnios ||
                        !añosDisponibles.length ||
                        Boolean(filtroAnioDesde || filtroAnioHasta)
                      "
                    >
                      <option value="">
                        Todos los años
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

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fMes"
                    >
                      Mes
                    </label>

                    <select
                      id="fMes"
                      v-model="filtroMes"
                      class="pub-select"
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

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fAnioDesde"
                    >
                      Desde
                    </label>

                    <select
                      id="fAnioDesde"
                      v-model="filtroAnioDesde"
                      class="pub-select"
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

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="fAnioHasta"
                    >
                      Hasta
                    </label>

                    <select
                      id="fAnioHasta"
                      v-model="filtroAnioHasta"
                      class="pub-select"
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
              </section>

              <footer class="pub-sidePanel__footer">
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost pub-btn--block"
                  :disabled="!hayFiltros && !hayBusqueda"
                  @click="limpiarFiltros"
                >
                  Limpiar filtros
                </button>
              </footer>
            </section>

            <!-- ===============================================
              EXPORTACIÓN
            ================================================ -->
            <section
              v-else
              class="pub-sidePanel pub-sidePanel--export"
            >
              <header class="pub-sidePanel__head">
                <div>
                  <span class="pub-sidePanel__eyebrow">
                    Reporte institucional
                  </span>

                  <h2 class="pub-sidePanel__title">
                    Exportar Excel
                  </h2>
                </div>

                <span
                  class="
                    pub-sidePanel__badge
                    pub-sidePanel__badge--soft
                  "
                  aria-label="Registros incluidos en el reporte"
                >
                  {{ exportPreviewLoading ? "…" : exportPreviewCount }}
                </span>
              </header>

              <div
                v-if="exportErrorMsg"
                class="pub-alert"
                role="alert"
              >
                {{ exportErrorMsg }}
              </div>

              <div class="pub-sidePanel__actions">
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost"
                  @click="syncExportFiltersFromVisible"
                >
                  Usar visibles
                </button>

                <button
                  type="button"
                  class="pub-btn pub-btn--ghost"
                  @click="limpiarExportFilters"
                >
                  Limpiar
                </button>
              </div>

              <section class="pub-sidePanel__section">
                <h3 class="pub-sidePanel__sectionTitle">
                  Criterios del reporte
                </h3>

                <div class="pub-sidePanel__fields">
                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expTexto"
                    >
                      Texto
                    </label>

                    <input
                      id="expTexto"
                      v-model="exportFiltroTexto"
                      class="pub-input"
                      type="search"
                      inputmode="search"
                      autocomplete="off"
                      placeholder="Título, autor, proyecto, facultad o carrera…"
                    />
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expTipo"
                    >
                      Tipo
                    </label>

                    <select
                      id="expTipo"
                      v-model="exportFiltroTipo"
                      class="pub-select"
                    >
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
                    <label
                      class="pub-label"
                      for="expOrigen"
                    >
                      Origen
                    </label>

                    <select
                      id="expOrigen"
                      v-model="exportFiltroOrigen"
                      class="pub-select"
                    >
                      <option
                        v-for="origen in ORIGENES_LIST"
                        :key="`exp-origen-${origen.value}`"
                        :value="origen.value"
                      >
                        {{ origen.label }}
                      </option>
                    </select>
                  </div>

                  <div class="pub-field pub-field--full">
                    <span class="pub-label">
                      Disponibilidad
                    </span>

                    <label
                      class="pub-toggleCard pub-toggleCard--compact"
                      for="expSoloPdf"
                    >
                      <input
                        id="expSoloPdf"
                        v-model="exportSoloConPdf"
                        class="pub-toggleCard__input"
                        type="checkbox"
                      />

                      <span
                        class="pub-toggleCard__control"
                        aria-hidden="true"
                      >
                        <span class="pub-toggleCard__thumb"></span>
                      </span>

                      <span class="pub-toggleCard__content">
                        <strong class="pub-toggleCard__title">
                          Solo con PDF
                        </strong>

                        <span class="pub-toggleCard__description">
                          Exportar únicamente publicaciones con archivos PDF.
                        </span>
                      </span>
                    </label>
                  </div>

                  <div class="pub-field">
                    <label
                      class="pub-label"
                      for="expFacultad"
                    >
                      Facultad
                    </label>

                    <select
                      id="expFacultad"
                      v-model="exportFiltroFacultad"
                      class="pub-select"
                      @change="onExportFacultadChange"
                    >
                      <option value="">
                        Todas las facultades
                      </option>

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
                    <label
                      class="pub-label"
                      for="expCarrera"
                    >
                      Carrera
                    </label>

                    <select
                      id="expCarrera"
                      v-model="exportFiltroCarrera"
                      class="pub-select"
                      :disabled="!exportFiltroFacultad"
                      @change="onExportCarreraChange"
                    >
                      <option value="">
                        Todas las carreras
                      </option>

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
                    <label
                      class="pub-label"
                      for="expProyecto"
                    >
                      Proyecto
                    </label>

                    <select
                      id="expProyecto"
                      v-model="exportFiltroProyecto"
                      class="pub-select"
                      :disabled="!exportFiltroCarrera"
                    >
                      <option value="">
                        Todos los proyectos
                      </option>

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
                    <label
                      class="pub-label"
                      for="expAnio"
                    >
                      Año exacto
                    </label>

                    <select
                      id="expAnio"
                      v-model="exportFiltroAnio"
                      class="pub-select"
                      :disabled="
                        loadingAnios ||
                        !añosDisponibles.length ||
                        Boolean(
                          exportFiltroAnioDesde ||
                            exportFiltroAnioHasta
                        )
                      "
                    >
                      <option value="">
                        Todos los años
                      </option>

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
                    <label
                      class="pub-label"
                      for="expMes"
                    >
                      Mes
                    </label>

                    <select
                      id="expMes"
                      v-model="exportFiltroMes"
                      class="pub-select"
                    >
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
                    <label
                      class="pub-label"
                      for="expAnioDesde"
                    >
                      Desde
                    </label>

                    <select
                      id="expAnioDesde"
                      v-model="exportFiltroAnioDesde"
                      class="pub-select"
                      :disabled="loadingAnios || !añosDisponibles.length || Boolean(exportFiltroAnio)"
                    >
                      <option value="">
                        Sin mínimo
                      </option>

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
                    <label
                      class="pub-label"
                      for="expAnioHasta"
                    >
                      Hasta
                    </label>

                    <select
                      id="expAnioHasta"
                      v-model="exportFiltroAnioHasta"
                      class="pub-select"
                      :disabled="loadingAnios || !añosDisponibles.length || Boolean(exportFiltroAnio)"
                    >
                      <option value="">
                        Sin máximo
                      </option>

                      <option
                        v-for="anio in añosDisponibles"
                        :key="`exp-hasta-${anio}`"
                        :value="String(anio)"
                      >
                        {{ anio }}
                      </option>
                    </select>
                  </div>
                </div>
              </section>

              <footer
                class="
                  pub-sidePanel__footer
                  pub-sidePanel__footer--stack
                "
              >
                <button
                  type="button"
                  class="pub-btn pub-btn--ghost pub-btn--block"
                  :disabled="exporting"
                  @click="abrirPanelFiltros"
                >
                  Volver a filtros
                </button>

                <button
                  type="button"
                  class="pub-btn pub-btn--primary pub-btn--block"
                  :disabled="
                    loading ||
                      exporting ||
                      exportPreviewLoading ||
                      !exportPreviewCount
                  "
                  @click="confirmarExportacion"
                >
                  {{
                    exporting
                      ? "Generando..."
                      : "Generar Excel"
                  }}
                </button>
              </footer>
            </section>
          </div>
        </aside>

        <!-- ===================================================
          RESULTADOS
        ==================================================== -->
        <section class="pub-main">
          <section
            class="pub-typeFilter"
            aria-label="Filtrado por tipo de publicación"
          >
            <header class="pub-typeFilter__head">
              <div>
                <span class="pub-typeFilter__eyebrow">
                  {{
                    panelLateralActivo === "export"
                      ? "Vista previa del reporte"
                      : "Clasificación"
                  }}
                </span>

                <h2 class="pub-typeFilter__title">
                  Tipo de publicación
                </h2>
              </div>

              <button
                v-if="hayFiltrosVisibles || hayBusquedaVisible"
                type="button"
                class="pub-inlineAction"
                @click="limpiarFiltrosVisibles"
              >
                Limpiar todo
              </button>
            </header>

            <div class="pub-typeFilter__chips">
              <button
                v-for="tipo in TIPOS_LIST"
                :key="`top-${tipo.value}`"
                type="button"
                class="pub-typeFilter__chip"
                :class="{
                  'is-active': tipoFiltroActivo === tipo.value,
                }"
                :aria-pressed="tipoFiltroActivo === tipo.value"
                @click="tipoFiltroActivo = tipo.value"
              >
                <span
                  class="pub-typeFilter__dot"
                  :data-tipo="tipo.value"
                  aria-hidden="true"
                ></span>

                <span class="pub-typeFilter__label">
                  {{ tipo.label }}
                </span>

                <span class="pub-typeFilter__count">
                  {{ countByTypeVisible(tipo.value) }}
                </span>
              </button>
            </div>
          </section>

          <!-- ===============================================
            CARGA
          ================================================ -->
          <section
            v-if="resultadosLoading"
            class="pub-state"
            aria-live="polite"
          >
            <div
              class="pub-skeleton-grid"
              aria-label="Cargando publicaciones"
            >
              <div
                v-for="n in 6"
                :key="n"
                class="pub-skeleton-card"
              ></div>
            </div>
          </section>

          <!-- ===============================================
            ERROR
          ================================================ -->
          <section
            v-else-if="resultadosErrorMsg"
            class="pub-state pub-state--error"
          >
            <div
              class="pub-alert"
              role="alert"
            >
              {{ resultadosErrorMsg }}
            </div>

            <button
              type="button"
              class="pub-btn pub-btn--primary"
              :disabled="resultadosLoading"
              @click="reintentarCargaVisible"
            >
              Reintentar
            </button>
          </section>

          <!-- ===============================================
            CONTENIDO
          ================================================ -->
          <section
            v-else
            class="pub-content"
          >
            <div
              v-if="listaFiltrada.length"
              class="pub-grid page-stagger page-stagger--mid"
            >
              <article
                v-for="pub in listaFiltrada"
                :key="pub.id"
                class="pub-card pub-card--interactive"
                :data-tipo="resolveType(pub)"
                tabindex="0"
                role="button"
                :aria-label="
                  `Ver detalle de ${
                    pub.titulo ||
                    pub.proyecto ||
                    'la publicación'
                  }`
                "
                @click="verDetalles(pub.id)"
                @keydown.enter.prevent="verDetalles(pub.id)"
                @keydown.space.prevent="verDetalles(pub.id)"
              >
                <div class="pub-card__head">
                  <span
                    class="pub-badge"
                    :data-tipo="resolveType(pub)"
                  >
                    {{ resolveLabel(pub) }}
                  </span>

                  <time
                    class="pub-date"
                    :datetime="publicationPeriodDatetime(pub)"
                  >
                    {{ formatPublicationPeriod(pub) }}
                  </time>
                </div>

                <div class="pub-card__body">
                  <h3
                    class="pub-card__title"
                    :title="
                      pub.titulo ||
                        pub.proyecto ||
                        'Sin título'
                    "
                  >
                    {{
                      pub.titulo ||
                        pub.proyecto ||
                        "Sin título"
                    }}
                  </h3>

                  <p
                    v-if="pub.autor"
                    class="
                      pub-card__meta
                      pub-card__meta--soft
                    "
                    :title="pub.autor"
                  >
                    {{ pub.autor }}
                  </p>

                  <p
                    v-if="pub.proyecto"
                    class="pub-card__meta"
                    :title="pub.proyecto"
                  >
                    {{ pub.proyecto }}
                  </p>

                  <p
                    class="pub-card__meta"
                    :title="buildAcademicMeta(pub)"
                  >
                    {{ buildAcademicMeta(pub) }}
                  </p>

                  <p
                    v-if="resolveOrigenResumen(pub)"
                    class="pub-card__meta pub-card__meta--origin"
                    :title="resolveOrigenResumen(pub)"
                  >
                    <strong>Origen:</strong>
                    {{ resolveOrigenResumen(pub) }}
                  </p>
                </div>

                <footer class="pub-card__footer">
                  <span class="pub-card__action">
                    Ver detalle
                  </span>
                </footer>
              </article>
            </div>

            <div
              v-else
              class="pub-empty"
              role="status"
              aria-live="polite"
            >
              <div
                class="pub-empty__mark"
                aria-hidden="true"
              ></div>

              <h3 class="pub-empty__title">
                {{ emptyTitle }}
              </h3>

              <p class="pub-empty__text">
                {{ emptyText }}
              </p>

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

import {
  PUBLICACION_TIPOS,
  getTipoPublicacionMetaFromItem,
} from "../../scripts/utils/publicacion-tipos";

/* ============================================================
  CONFIGURACIÓN
============================================================ */

const LIST_ENDPOINT = "/publicaciones/";
const YEARS_ENDPOINT = "/publicaciones/anios-disponibles/";
const EXPORT_ENDPOINT = "/reportes/publicaciones/excel/";
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
    label: "Ninguno",
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
  ninguno: "Ninguno",
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
  const responseData = error?.response?.data;

  const detail =
    responseData?.detail ||
    responseData?.message ||
    responseData?.error ||
    error?.message;

  if (Array.isArray(detail)) {
    return detail.join(", ");
  }

  if (detail && typeof detail === "object") {
    return Object.entries(detail)
      .flatMap(([field, value]) => {
        const messages = Array.isArray(value)
          ? value
          : [value];

        return messages.map(
          (message) => `${field}: ${String(message)}`
        );
      })
      .join(" ");
  }

  return String(detail || fallback);
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
  const facultad = String(
    publicacion?.facultad || ""
  ).trim();

  const carrera = String(
    publicacion?.carrera || ""
  ).trim();

  if (facultad && carrera) {
    return `${facultad} · ${carrera}`;
  }

  return (
    facultad ||
    carrera ||
    "Sin ubicación académica"
  );
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

async function loadFacultades() {
  const response = await api.get(
    "/selects/facultades/"
  );

  facultades.value = extractArray(response.data);
}

async function fetchCarrerasByFacultad(facultadId) {
  if (!facultadId) {
    return [];
  }

  const response = await api.get(
    `/selects/carreras/${facultadId}/`
  );

  return extractArray(response.data);
}

async function fetchProyectosByCarrera(carreraId) {
  if (!carreraId) {
    return [];
  }

  const response = await api.get(
    `/selects/proyectos/${carreraId}/`
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
    if (exportFiltroFacultad.value) {
      exportCarreras.value =
        await fetchCarrerasByFacultad(
          exportFiltroFacultad.value
        );
    }

    if (exportFiltroCarrera.value) {
      exportProyectos.value =
        await fetchProyectosByCarrera(
          exportFiltroCarrera.value
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

async function onMainFacultadChange() {
  filtroCarrera.value = "";
  filtroProyecto.value = "";

  carreras.value = [];
  proyectos.value = [];

  if (!filtroFacultad.value) {
    return;
  }

  try {
    carreras.value =
      await fetchCarrerasByFacultad(
        filtroFacultad.value
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
  CATÁLOGOS DEPENDIENTES DE EXPORTACIÓN
============================================================ */

async function onExportFacultadChange() {
  exportFiltroCarrera.value = "";
  exportFiltroProyecto.value = "";

  exportCarreras.value = [];
  exportProyectos.value = [];

  if (!exportFiltroFacultad.value) {
    return;
  }

  try {
    exportCarreras.value =
      await fetchCarrerasByFacultad(
        exportFiltroFacultad.value
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
        exportFiltroCarrera.value
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
      "No se pudo calcular la vista previa del reporte."
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

    const response = await api.get(
      EXPORT_ENDPOINT,
      {
        params,
        responseType: "blob",
      }
    );

    const blob = new Blob([response.data], {
      type:
        "application/vnd.openxmlformats-" +
        "officedocument.spreadsheetml.sheet",
    });

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    const timestamp = new Date()
      .toISOString()
      .slice(0, 19)
      .replace(/[:T]/g, "-");

    link.href = url;
    link.setAttribute(
      "download",
      `reporte_publicaciones_${timestamp}.xlsx`
    );

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 1000);
  } catch (error) {
    console.error(
      "Error exportando Excel:",
      error
    );

    exportErrorMsg.value = extractErrorMessage(
      error,
      "No se pudo generar el archivo Excel."
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
