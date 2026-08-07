<template>
  <main class="ivbi-page">
    <section class="ivbi-shell">
      <section
        class="ivbi-board"
        :class="{
          'is-loading': loading,
          'is-refreshing': isRefreshing,
        }"
        :aria-busy="loading || isRefreshing ? 'true' : 'false'"
      >
        <!-- =====================================================
             SKELETON INICIAL
        ====================================================== -->
        <div
          v-if="loading && !hasLoadedOnce"
          class="ivbi-skeleton-shell"
          aria-hidden="true"
        >
          <div class="ivbi-sk-header">
            <div class="ivbi-skeleton-block ivbi-skeleton-block--hero">
              <div class="ivbi-sk-line ivbi-sk-line--kicker"></div>
              <div class="ivbi-sk-line ivbi-sk-line--title"></div>
              <div class="ivbi-sk-line ivbi-sk-line--meta"></div>
            </div>

            <div class="ivbi-sk-tabs">
              <span
                v-for="n in 3"
                :key="`tab-${n}`"
                class="ivbi-sk-pill"
              ></span>
            </div>

            <div class="ivbi-sk-filters">
              <span
                v-for="n in 6"
                :key="`gf-${n}`"
                class="ivbi-sk-field"
              ></span>
            </div>
          </div>

          <div class="ivbi-sk-kpis">
            <article
              v-for="n in 6"
              :key="`kpi-${n}`"
              class="ivbi-sk-card ivbi-sk-card--kpi"
            ></article>
          </div>

          <div class="ivbi-sk-grid ivbi-sk-grid--summary">
            <article class="ivbi-sk-card ivbi-sk-card--distribution"></article>
            <article class="ivbi-sk-card ivbi-sk-card--comparison"></article>
            <article class="ivbi-sk-card ivbi-sk-card--facultades"></article>
            <article class="ivbi-sk-card ivbi-sk-card--autores"></article>
          </div>
        </div>

        <!-- =====================================================
             DASHBOARD
        ====================================================== -->
        <div v-else class="ivbi-dashboard">
          <header class="ivbi-header">
            <!-- =================================================
                 CABECERA COMPACTA
            ================================================== -->
            <section
              class="ivbi-header__top"
              aria-labelledby="ivbi-dashboard-title"
            >
              <div class="ivbi-header__identity">
                <div
                  class="ivbi-header__brandmark"
                  aria-hidden="true"
                >
                  <img
                    src="../../assets/LOGO-ULEAM-VERTICAL.png"
                    alt=""
                  />
                </div>

                <div class="ivbi-header__titlebox">
                  <span class="ivbi-header__kicker">
                    SGPC ULEAM
                  </span>

                  <h1
                    id="ivbi-dashboard-title"
                    class="ivbi-header__title"
                  >
                    Panel analítico institucional
                  </h1>

                  <p class="ivbi-header__meta">
                    {{ dashboardMetaLine }}
                  </p>
                </div>
              </div>

              <div class="ivbi-header__actions">
                <button
                  class="ivbi-btn ivbi-btn--primary ivbi-btn--download"
                  type="button"
                  :disabled="
                    loading ||
                    isRefreshing ||
                    downloadingReport
                  "
                  @click="downloadDashboardReport"
                >
                  <svg
                    v-if="!downloadingReport"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <path
                      d="M10 3v9M6.5 9.5 10 13l3.5-3.5M4 16.5h12"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>

                  <span
                    v-else
                    class="ivbi-btn__spinner"
                    aria-hidden="true"
                  ></span>

                  <span>
                    {{
                      downloadingReport
                        ? "Generando reporte…"
                        : "Descargar reporte"
                    }}
                  </span>
                </button>
              </div>
            </section>

            <!-- =================================================
                 NAVEGACIÓN
            ================================================== -->
            <section
              class="ivbi-header__navigation"
              aria-label="Vista actual del dashboard"
            >
              <nav
                class="ivbi-segmented"
                aria-label="Vistas del dashboard"
              >
                <button
                  v-for="vista in vistaOpciones"
                  :key="vista.key"
                  type="button"
                  class="ivbi-segmented__btn"
                  :class="{
                    'is-active': vistaActiva === vista.key,
                  }"
                  :aria-pressed="vistaActiva === vista.key"
                  @click="vistaActiva = vista.key"
                >
                  {{ vista.label }}
                </button>
              </nav>

              <div class="ivbi-header__view-context">
                <span
                  class="ivbi-header__view-icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 20 20">
                    <circle
                      cx="10"
                      cy="10"
                      r="7.4"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />

                    <path
                      d="M10 8.8v4.6M10 6.3h.01"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>

                <p class="ivbi-header__view-help">
                  <strong>
                    {{ activeViewLabel }}
                  </strong>

                  <span>
                    {{ activeViewDescription }}
                  </span>
                </p>
              </div>
            </section>

            <!-- =================================================
                 FILTROS COMPACTOS
            ================================================== -->
            <section
              class="ivbi-filterbar ivbi-filterbar--compact"
              aria-labelledby="ivbi-filters-title"
            >
              <div class="ivbi-filterbar__compact-title">
                <span
                  class="ivbi-filterbar__compact-icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 20 20">
                    <path
                      d="M3 4h14l-5.2 6.1v4.6l-3.6 1.8v-6.4L3 4Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div class="ivbi-filterbar__compact-copy">
                  <span class="ivbi-filterbar__eyebrow">
                    Filtros
                  </span>

                  <h2 id="ivbi-filters-title">
                    {{ activeViewLabel }}
                  </h2>
                </div>

                <span
                  class="ivbi-filterbar__status"
                  :class="{
                    'is-live': !isRefreshing,
                    'is-updating': isRefreshing,
                  }"
                  :title="
                    isRefreshing
                      ? 'Actualizando información'
                      : 'Los filtros se aplican automáticamente'
                  "
                  aria-live="polite"
                >
                  {{
                    isRefreshing
                      ? "Actualizando…"
                      : "Auto"
                  }}
                </span>
              </div>

              <!-- CAMPOS -->
              <div class="ivbi-filterbar__fields">
                <label class="ivbi-field">
                  <span>Facultad</span>

                  <select v-model="globalFilters.facultad_id">
                    <option value="">
                      Todas
                    </option>

                    <option
                      v-for="facultad in filtrosDisponibles.facultades"
                      :key="facultad.id"
                      :value="String(facultad.id)"
                    >
                      {{ facultad.nombre }}
                    </option>
                  </select>
                </label>

                <label class="ivbi-field">
                  <span>Carrera</span>

                  <select v-model="globalFilters.carrera_id">
                    <option value="">
                      Todas
                    </option>

                    <option
                      v-for="carrera in carrerasFiltradas"
                      :key="carrera.id"
                      :value="String(carrera.id)"
                    >
                      {{ carrera.nombre }}
                    </option>
                  </select>
                </label>

                <label class="ivbi-field">
                  <span>Tipo</span>

                  <select v-model="activeViewFilters.tipo_codigo">
                    <option value="">
                      Todos
                    </option>

                    <option
                      v-for="tipo in tiposDisponiblesCanonicos"
                      :key="`tipo-${vistaActiva}-${tipo.codigo}`"
                      :value="tipo.codigo"
                    >
                      {{ tipo.nombre }}
                    </option>
                  </select>
                </label>

                <!-- RESUMEN -->
                <template v-if="vistaActiva === 'resumen'">
                  <label class="ivbi-field ivbi-field--month">
                    <span>Desde</span>

                    <input
                      v-model="viewFilters.resumen.mes_desde"
                      type="month"
                      aria-label="Mes inicial del período"
                      title="Seleccione el mes inicial"
                      autocomplete="off"
                    />
                  </label>

                  <label class="ivbi-field ivbi-field--month">
                    <span>Hasta</span>

                    <input
                      v-model="viewFilters.resumen.mes_hasta"
                      type="month"
                      aria-label="Mes final del período"
                      title="Seleccione el mes final"
                      autocomplete="off"
                    />
                  </label>
                </template>

                <!-- TENDENCIA -->
                <template v-else-if="vistaActiva === 'tendencia'">
                  <label class="ivbi-field ivbi-field--month">
                    <span>Desde</span>

                    <input
                      v-model="viewFilters.tendencia.mes_desde"
                      type="month"
                      aria-label="Mes inicial de la tendencia"
                      title="Seleccione el mes inicial"
                      autocomplete="off"
                    />
                  </label>

                  <label class="ivbi-field ivbi-field--month">
                    <span>Hasta</span>

                    <input
                      v-model="viewFilters.tendencia.mes_hasta"
                      type="month"
                      aria-label="Mes final de la tendencia"
                      title="Seleccione el mes final"
                      autocomplete="off"
                    />
                  </label>

                  <label class="ivbi-field">
                    <span>Año mensual</span>

                    <select v-model="viewFilters.tendencia.anio">
                      <option value="">
                        {{ autoAnioMensualLabel }}
                      </option>

                      <option
                        v-for="anio in filtrosDisponibles.anios"
                        :key="`t-anio-${anio.value}`"
                        :value="String(anio.value)"
                      >
                        {{ anio.label }}
                      </option>
                    </select>
                  </label>
                </template>

                <!-- RANKINGS -->
                <template v-else>
                  <label class="ivbi-field ivbi-field--month">
                    <span>Desde</span>

                    <input
                      v-model="viewFilters.rankings.mes_desde"
                      type="month"
                      aria-label="Mes inicial de los rankings"
                      title="Seleccione el mes inicial"
                      autocomplete="off"
                    />
                  </label>

                  <label class="ivbi-field ivbi-field--month">
                    <span>Hasta</span>

                    <input
                      v-model="viewFilters.rankings.mes_hasta"
                      type="month"
                      aria-label="Mes final de los rankings"
                      title="Seleccione el mes final"
                      autocomplete="off"
                    />
                  </label>

                  <label class="ivbi-field">
                    <span>Cantidad</span>

                    <select v-model="viewFilters.rankings.top">
                      <option value="5">Top 5</option>
                      <option value="10">Top 10</option>
                      <option value="15">Top 15</option>
                      <option value="20">Top 20</option>
                    </select>
                  </label>
                </template>
              </div>

              <!-- ACCIONES -->
              <div class="ivbi-filterbar__actions">
                <button
                  class="ivbi-filter-action"
                  type="button"
                  title="Restablecer filtros de la vista actual"
                  :disabled="
                    loading ||
                    isRefreshing ||
                    downloadingReport
                  "
                  @click="resetCurrentViewFilters"
                >
                  <svg
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <path
                      d="M4 4v5h5M4.7 8.5a6.5 6.5 0 1 1 1.1 6.2"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>

                  <span>Restablecer</span>
                </button>

                <button
                  class="
                    ivbi-filter-action
                    ivbi-filter-action--ghost
                  "
                  type="button"
                  title="Restablecer todos los filtros"
                  :disabled="
                    loading ||
                    isRefreshing ||
                    downloadingReport
                  "
                  @click="resetAllFilters"
                >
                  <span>Limpiar todo</span>
                </button>
              </div>
            </section>
          </header>

          <!-- =================================================
               ERROR
          ================================================== -->
          <div
            v-if="error"
            class="ivbi-alert ivbi-alert--error"
          >
            {{ error }}
          </div>

          <!-- =================================================
               CONTENIDO
          ================================================== -->
          <template v-if="hasData">
            <Transition
              name="ivbi-view"
              mode="out-in"
            >
              <!-- =============================================
                   RESUMEN
              ============================================== -->
              <section
                v-if="vistaActiva === 'resumen'"
                key="resumen"
                class="ivbi-view-shell"
              >
                <!-- KPIs -->
                <section
                  :key="`kpi-strip-${visualRevision}`"
                  class="ivbi-kpi-strip"
                  aria-label="Indicadores principales"
                >
                  <article
                    v-for="(kpi, kpiIndex) in headlineKpis"
                    :key="kpi.key"
                    class="ivbi-kpi-card"
                    :class="[
                      `ivbi-kpi-card--${kpi.key}`,
                      {
                        'is-primary': [
                          'publicaciones',
                          'alto-impacto',
                        ].includes(kpi.key),

                        'is-coverage': [
                          'facultades',
                          'carreras',
                        ].includes(kpi.key),
                      },
                    ]"
                    :style="{
                      '--kpi-delay': `${kpiIndex * 55}ms`,
                    }"
                  >
                    <span
                      class="ivbi-kpi-card__icon"
                      aria-hidden="true"
                    >
                      <svg viewBox="0 0 24 24">
                        <path
                          :d="kpi.iconPath"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.7"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>

                    <div class="ivbi-kpi-card__copy">
                      <span class="ivbi-kpi-card__label">
                        {{ kpi.label }}
                      </span>

                      <strong class="ivbi-kpi-card__value">
                        {{ formatNumber(kpi.value) }}
                      </strong>

                      <span class="ivbi-kpi-card__hint">
                        {{ kpi.hint }}
                      </span>
                    </div>
                  </article>
                </section>

                <!-- GRID RESUMEN -->
                <section
                  :key="`summary-grid-${visualRevision}`"
                  class="ivbi-summary-grid"
                >
                  <!-- DISTRIBUCIÓN -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--distribution
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Distribución
                        </span>

                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo
                        </h3>
                      </div>

                      <div class="ivbi-card__head-tools">
                        <span
                          v-if="tipoDominante"
                          class="ivbi-insight-pill"
                        >
                          Dominante:
                          {{ tipoDominante.tipo_codigo }}
                          ·
                          {{
                            formatPercent(
                              tipoDominante.porcentaje
                            )
                          }}
                        </span>

                        <span
                          class="ivbi-info-tip"
                          tabindex="0"
                        >
                          <span aria-hidden="true">
                            i
                          </span>

                          <span
                            class="ivbi-info-tip__content"
                            role="tooltip"
                          >
                            Seleccione un tipo en la
                            leyenda para aplicar o quitar
                            ese filtro.
                          </span>
                        </span>
                      </div>
                    </header>

                    <div
                      v-if="publicacionesPorTipo.items.length"
                      class="ivbi-donut-panel"
                    >
                      <div
                        class="ivbi-donut"
                        :class="{
                          'is-focused':
                            Boolean(hoveredTypeCode),
                        }"
                        :style="{
                          background:
                            donutGradient(
                              publicacionesPorTipo.items
                            ),
                        }"
                      >
                        <div class="ivbi-donut__center">
                          <strong>
                            {{ donutCenterValue }}
                          </strong>

                          <span>
                            {{ donutCenterLabel }}
                          </span>

                          <small v-if="donutCenterHint">
                            {{ donutCenterHint }}
                          </small>
                        </div>
                      </div>

                      <div class="ivbi-legend">
                        <button
                          v-for="(
                            item,
                            index
                          ) in publicacionesPorTipo.items"
                          :key="`tipo-${item.tipo_codigo}`"
                          type="button"
                          class="ivbi-legend__item"
                          :class="{
                            'is-muted':
                              hoveredTypeCode &&
                              hoveredTypeCode !==
                                item.tipo_codigo,

                            'is-active':
                              hoveredTypeCode ===
                              item.tipo_codigo,

                            'is-selected':
                              isTypeSelected(
                                item.tipo_codigo
                              ),
                          }"
                          @mouseenter="
                            handleLegendEnter(
                              item.tipo_codigo
                            )
                          "
                          @mouseleave="
                            handleLegendLeave
                          "
                          @focus="
                            handleLegendEnter(
                              item.tipo_codigo
                            )
                          "
                          @blur="
                            handleLegendLeave
                          "
                          @click="
                            applyTypeFilter(
                              item.tipo_codigo
                            )
                          "
                        >
                          <span
                            class="
                              ivbi-legend__swatch
                            "
                            :style="{
                              background:
                                getTypeColor(
                                  item.tipo_codigo,
                                  index
                                ),
                            }"
                          ></span>

                          <span
                            class="
                              ivbi-legend__text
                            "
                          >
                            <span
                              class="
                                ivbi-legend__label
                              "
                            >
                              {{ item.tipo_nombre }}
                            </span>

                            <span
                              class="
                                ivbi-legend__meta
                              "
                            >
                              {{
                                formatNumber(
                                  item.total
                                )
                              }}
                              ·
                              {{
                                formatPercent(
                                  item.porcentaje
                                )
                              }}
                            </span>
                          </span>
                        </button>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- COMPARATIVA ANUAL -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--comparison
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Comparativa anual
                        </span>

                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo por año
                        </h3>
                      </div>
                    </header>

                    <div
                      v-if="
                        hasGroupedData(
                          publicacionesPorTipoAnual
                        )
                      "
                      class="ivbi-grouped-wrap"
                    >
                      <div class="ivbi-grouped">
                        <div
                          v-for="(
                            category,
                            catIndex
                          ) in publicacionesPorTipoAnual.categorias"
                          :key="`grupo-${category}`"
                          class="ivbi-grouped__group"
                        >
                          <div class="ivbi-grouped__bars">
                            <div
                              v-for="(
                                serie,
                                serieIndex
                              ) in publicacionesPorTipoAnual.series"
                              :key="
                                `${serie.codigo}-${category}`
                              "
                              class="
                                ivbi-grouped__barbox
                              "
                              :style="{
                                '--grouped-h':
                                  groupedBarHeight(
                                    publicacionesPorTipoAnual.series,
                                    serie.data?.[
                                      catIndex
                                    ] || 0
                                  ),

                                '--grouped-delay':
                                  `${
                                    serieIndex * 45 +
                                    catIndex * 20
                                  }ms`,
                              }"
                            >
                              <span
                                class="
                                  ivbi-grouped__value
                                "
                              >
                                {{
                                  serie.data?.[
                                    catIndex
                                  ] || 0
                                }}
                              </span>

                              <div
                                class="
                                  ivbi-grouped__bar
                                "
                                :style="{
                                  background:
                                    getTypeColor(
                                      serie.codigo,
                                      serieIndex
                                    ),
                                }"
                                :title="
                                  `${serie.label}: ${
                                    serie.data?.[
                                      catIndex
                                    ] || 0
                                  }`
                                "
                              ></div>
                            </div>
                          </div>

                          <span
                            class="
                              ivbi-grouped__label
                            "
                          >
                            {{ category }}
                          </span>
                        </div>
                      </div>

                      <div class="ivbi-series-legend">
                        <span
                          v-for="(
                            serie,
                            index
                          ) in publicacionesPorTipoAnual.series"
                          :key="
                            `legend-${serie.codigo}`
                          "
                          class="
                            ivbi-series-legend__item
                          "
                        >
                          <i
                            class="
                              ivbi-series-legend__swatch
                            "
                            :style="{
                              background:
                                getTypeColor(
                                  serie.codigo,
                                  index
                                ),
                            }"
                          ></i>

                          {{ serie.label }}
                        </span>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- FACULTADES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--facultades
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Concentración
                        </span>

                        <h3 class="ivbi-card__title">
                          Top facultades
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="
                        topFacultadesResumen.length
                      "
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in topFacultadesResumen"
                        :key="
                          `top-facultad-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="
                              ivbi-rank__index
                            "
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="
                              ivbi-rank__label
                            "
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="
                              ivbi-rank__bar
                            "
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  topFacultadesResumen,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- AUTORES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--autores
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Producción autoral
                        </span>

                        <h3 class="ivbi-card__title">
                          Top autores
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="
                        topAutoresResumen.length
                      "
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in topAutoresResumen"
                        :key="
                          `top-autor-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="
                              ivbi-rank__index
                            "
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="
                              ivbi-rank__label
                            "
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="
                              ivbi-rank__bar
                            "
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  topAutoresResumen,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>

              <!-- =============================================
                   TENDENCIA
              ============================================== -->
              <section
                v-else-if="
                  vistaActiva === 'tendencia'
                "
                key="tendencia"
                class="ivbi-view-shell"
              >
                <section
                  :key="
                    `trend-grid-${visualRevision}`
                  "
                  class="ivbi-trend-grid"
                >
                  <!-- HISTÓRICA -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--historica
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Serie histórica
                        </span>

                        <h3 class="ivbi-card__title">
                          Publicaciones por año
                        </h3>
                      </div>

                      <span class="ivbi-card__total">
                        {{
                          formatNumber(
                            totalOf(
                              publicacionesPorAnio
                            )
                          )
                        }}
                      </span>
                    </header>

                    <div
                      v-if="
                        publicacionesPorAnio.length
                      "
                      class="
                        ivbi-vbars
                        ivbi-vbars--tall
                      "
                    >
                      <button
                        v-for="(
                          item,
                          index
                        ) in publicacionesPorAnio"
                        :key="
                          `trend-anio-${item.label}`
                        "
                        type="button"
                        class="
                          ivbi-vbars__col
                          is-interactive
                        "
                        :class="{
                          'is-selected':
                            String(
                              viewFilters
                                .tendencia
                                .anio
                            ) ===
                            String(item.label),
                        }"
                        @click="
                          applyYearFromTrend(
                            item.label
                          )
                        "
                      >
                        <span
                          class="ivbi-vbars__value"
                        >
                          {{ item.value }}
                        </span>

                        <div
                          class="
                            ivbi-vbars__track
                          "
                        >
                          <div
                            class="
                              ivbi-vbars__bar
                            "
                            :style="{
                              '--bar-h':
                                verticalBarHeight(
                                  publicacionesPorAnio,
                                  item.value
                                ),

                              '--bar-delay':
                                `${index * 35}ms`,

                              background:
                                paletteColor(
                                  index
                                ),
                            }"
                          ></div>
                        </div>

                        <span
                          class="
                            ivbi-vbars__label
                          "
                        >
                          {{ item.label }}
                        </span>
                      </button>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- COMPARATIVA -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--comparativa
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Comparativa
                        </span>

                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo por año
                        </h3>
                      </div>
                    </header>

                    <div
                      v-if="
                        hasGroupedData(
                          publicacionesPorTipoAnual
                        )
                      "
                      class="ivbi-grouped-wrap"
                    >
                      <div class="ivbi-grouped">
                        <div
                          v-for="(
                            category,
                            catIndex
                          ) in publicacionesPorTipoAnual.categorias"
                          :key="
                            `trend-group-${category}`
                          "
                          class="ivbi-grouped__group"
                        >
                          <div
                            class="
                              ivbi-grouped__bars
                            "
                          >
                            <div
                              v-for="(
                                serie,
                                serieIndex
                              ) in publicacionesPorTipoAnual.series"
                              :key="
                                `trend-${serie.codigo}-${category}`
                              "
                              class="
                                ivbi-grouped__barbox
                              "
                              :style="{
                                '--grouped-h':
                                  groupedBarHeight(
                                    publicacionesPorTipoAnual.series,
                                    serie.data?.[
                                      catIndex
                                    ] || 0
                                  ),

                                '--grouped-delay':
                                  `${
                                    serieIndex * 45 +
                                    catIndex * 20
                                  }ms`,
                              }"
                            >
                              <span
                                class="
                                  ivbi-grouped__value
                                "
                              >
                                {{
                                  serie.data?.[
                                    catIndex
                                  ] || 0
                                }}
                              </span>

                              <div
                                class="
                                  ivbi-grouped__bar
                                "
                                :style="{
                                  background:
                                    getTypeColor(
                                      serie.codigo,
                                      serieIndex
                                    ),
                                }"
                              ></div>
                            </div>
                          </div>

                          <span
                            class="
                              ivbi-grouped__label
                            "
                          >
                            {{ category }}
                          </span>
                        </div>
                      </div>

                      <div
                        class="
                          ivbi-series-legend
                        "
                      >
                        <span
                          v-for="(
                            serie,
                            index
                          ) in publicacionesPorTipoAnual.series"
                          :key="
                            `trend-legend-${serie.codigo}`
                          "
                          class="
                            ivbi-series-legend__item
                          "
                        >
                          <i
                            class="
                              ivbi-series-legend__swatch
                            "
                            :style="{
                              background:
                                getTypeColor(
                                  serie.codigo,
                                  index
                                ),
                            }"
                          ></i>

                          {{ serie.label }}
                        </span>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- MENSUAL -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--mensual
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Detalle temporal
                        </span>

                        <h3 class="ivbi-card__title">
                          Publicaciones por mes
                        </h3>
                      </div>

                      <span class="ivbi-card__total">
                        {{
                          publicacionesPorMes.anio_base ||
                          "Auto"
                        }}
                      </span>
                    </header>

                    <div
                      v-if="
                        publicacionesPorMes.items
                          .length
                      "
                      class="ivbi-vbars"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in publicacionesPorMes.items"
                        :key="`mes-${item.label}`"
                        class="ivbi-vbars__col"
                      >
                        <span
                          class="ivbi-vbars__value"
                        >
                          {{ item.value }}
                        </span>

                        <div
                          class="
                            ivbi-vbars__track
                          "
                        >
                          <div
                            class="
                              ivbi-vbars__bar
                            "
                            :style="{
                              '--bar-h':
                                verticalBarHeight(
                                  publicacionesPorMes.items,
                                  item.value
                                ),

                              '--bar-delay':
                                `${index * 35}ms`,

                              background:
                                paletteColor(
                                  index
                                ),
                            }"
                          ></div>
                        </div>

                        <span
                          class="
                            ivbi-vbars__label
                          "
                        >
                          {{ item.label }}
                        </span>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>

              <!-- =============================================
                   RANKINGS
              ============================================== -->
              <section
                v-else
                key="rankings"
                class="ivbi-view-shell"
              >
                <section
                  :key="
                    `rankings-grid-${visualRevision}`
                  "
                  class="ivbi-rankings-grid"
                >
                  <!-- FACULTADES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--facultades-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Concentración
                        </span>

                        <h3 class="ivbi-card__title">
                          Top facultades
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topFacultadesData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in topFacultadesData"
                        :key="
                          `rank-facultad-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="ivbi-rank__index"
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="ivbi-rank__label"
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  topFacultadesData,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- CARRERAS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--carreras-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Concentración
                        </span>

                        <h3 class="ivbi-card__title">
                          Top carreras
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topCarrerasData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in topCarrerasData"
                        :key="
                          `rank-carrera-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="ivbi-rank__index"
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="ivbi-rank__label"
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  topCarrerasData,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- AUTORES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--autores-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Producción autoral
                        </span>

                        <h3 class="ivbi-card__title">
                          Top autores
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="
                        topAutoresData.length
                      "
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in topAutoresData"
                        :key="
                          `rank-autor-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="ivbi-rank__index"
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="ivbi-rank__label"
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  topAutoresData,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>


                  <!-- REVISTAS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--revistas
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Difusión científica
                        </span>

                        <h3 class="ivbi-card__title">
                          Revistas con más artículos
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="journalsData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in journalsData"
                        :key="
                          `journal-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="ivbi-rank__index"
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="ivbi-rank__label"
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  journalsData,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>

                  <!-- PROYECTOS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--proyectos
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">
                          Vinculación investigativa
                        </span>

                        <h3 class="ivbi-card__title">
                          Proyectos con más publicaciones
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="projectsData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in projectsData"
                        :key="
                          `project-${item.label}`
                        "
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span
                            class="ivbi-rank__index"
                          >
                            {{ index + 1 }}
                          </span>

                          <span
                            class="ivbi-rank__label"
                            :title="item.label"
                          >
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w':
                                horizontalWidth(
                                  projectsData,
                                  item.total,
                                  'total'
                                ),

                              '--rank-delay':
                                `${index * 45}ms`,

                              background:
                                rankingBarColor(
                                  index
                                ),
                            }"
                          >
                            <span>
                              {{ item.total }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>
            </Transition>
          </template>

          <!-- =================================================
               ESTADOS
          ================================================== -->
          <div
            v-else-if="loading || isRefreshing"
            class="ivbi-empty ivbi-empty--state"
          >
            Actualizando…
          </div>

          <div
            v-else
            class="ivbi-empty ivbi-empty--state"
          >
            Sin datos para los filtros seleccionados.
          </div>

          <!-- =================================================
               NOTA
          ================================================== -->
          <footer
            v-if="hasData"
            class="ivbi-dashboard-note"
          >
            <span
              class="ivbi-dashboard-note__icon"
              aria-hidden="true"
            >
              <svg viewBox="0 0 20 20">
                <circle
                  cx="10"
                  cy="10"
                  r="7.4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                />

                <path
                  d="M10 8.8v4.6M10 6.3h.01"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <span>
              Los datos se actualizan automáticamente
              según los filtros seleccionados.
            </span>
          </footer>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import api from "../../scripts/api/axios";

/* =========================================================
   TIPOS CANÓNICOS
========================================================= */

const CANONICAL_TYPES = Object.freeze([
  {
    code: "AAI",
    label: "Artículo de alto impacto",
  },
  {
    code: "AR",
    label: "Artículo regional",
  },
  {
    code: "PON",
    label: "Ponencia",
  },
  {
    code: "CAP",
    label: "Capítulo de libro",
  },
  {
    code: "LIB",
    label: "Libro",
  },
]);

const CANONICAL_TYPE_MAP = Object.freeze(
  CANONICAL_TYPES.reduce((acc, item) => {
    acc[item.code] = item;
    return acc;
  }, {})
);

const TYPE_COLOR_VAR_MAP = Object.freeze({
  AAI: "--ivbi-chart-1",
  AR: "--ivbi-chart-2",
  PON: "--ivbi-chart-3",
  CAP: "--ivbi-chart-4",
  LIB: "--ivbi-chart-5",
});

/* =========================================================
   RESPUESTA VACÍA
========================================================= */

const EMPTY_RESPONSE = Object.freeze({
  ok: true,

  summary: {
    total_publicaciones: 0,
    total_autores: 0,
    total_facultades: 0,
    total_carreras: 0,
    total_proyectos: 0,
    articulos_alto_impacto: 0,
    articulos_regionales: 0,
  },

  dashboards: {
    publicaciones_por_anio: [],

    publicaciones_por_mes: {
      anio_base: null,
      items: [],
      total_publicaciones_anio: 0,
      total_con_mes: 0,
      total_sin_mes: 0,
    },

    publicaciones_por_tipo: {
      total_publicaciones: 0,
      seleccionado: null,
      items: [],
    },

    publicaciones_por_tipo_anual: {
      categorias: [],
      series: [],
      total_publicaciones: 0,
    },

    top_facultades: {
      limite: 10,
      items: [],
    },

    top_carreras: {
      limite: 10,
      items: [],
    },

    top_autores: {
      limite: 10,
      total_autores_activos: 0,
      items: [],
    },

    journals: {
      limite: 10,
      items: [],
    },

    projects: {
      limite: 10,
      items: [],
    },
  },

  filtros_disponibles: {
    tipos: [],
    facultades: [],
    carreras: [],
    anios: [],
    anio_base_mensual: null,
  },

  filtros_aplicados: {},
});

/* =========================================================
   ESTADO
========================================================= */

const loading = ref(false);
const isRefreshing = ref(false);
const downloadingReport = ref(false);

const error = ref("");
const response = ref(null);

const hasMounted = ref(false);
const hasLoadedOnce = ref(false);

const suppressAutoApply = ref(false);

const vistaActiva = ref("resumen");

const hoveredTypeCode = ref("");
const visualRevision = ref(0);

let autoApplyTimer = null;
let requestId = 0;

/* =========================================================
   VISTAS
========================================================= */

const vistaOpciones = Object.freeze([
  {
    key: "resumen",
    label: "Resumen",
  },
  {
    key: "tendencia",
    label: "Tendencia",
  },
  {
    key: "rankings",
    label: "Rankings",
  },
]);

const activeViewLabel = computed(() => {
  return (
    vistaOpciones.find(
      (item) =>
        item.key === vistaActiva.value
    )?.label || "Resumen"
  );
});

const activeViewDescription = computed(() => {
  const descriptions = {
    resumen:
      "Indicadores generales, distribución y concentración institucional.",

    tendencia:
      "Evolución histórica, comparativa anual y comportamiento mensual.",

    rankings:
      "Facultades, carreras, autores, revistas y proyectos destacados.",
  };

  return (
    descriptions[vistaActiva.value] ||
    descriptions.resumen
  );
});

/* =========================================================
   FILTROS
========================================================= */

const globalFilters = reactive({
  facultad_id: "",
  carrera_id: "",
});

const defaultViewFilters = () => ({
  resumen: {
    tipo_codigo: "",
    mes_desde: "",
    mes_hasta: "",
  },

  tendencia: {
    tipo_codigo: "",
    mes_desde: "",
    mes_hasta: "",
    anio: "",
  },

  rankings: {
    tipo_codigo: "",
    mes_desde: "",
    mes_hasta: "",
    top: "10",
  },
});

const viewFilters = reactive(
  defaultViewFilters()
);

const activeViewFilters = computed(() => {
  return (
    viewFilters[vistaActiva.value] || {}
  );
});

/* =========================================================
   NORMALIZACIÓN
========================================================= */

function normalizeTextToken(input) {
  return String(input || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, " ")
    .trim();
}

function normalizeCanonicalCode(input) {
  const raw = normalizeTextToken(input);

  if (!raw) {
    return null;
  }

  if (CANONICAL_TYPE_MAP[raw]) {
    return raw;
  }

  if (
    raw === "AAI" ||
    raw.includes("ALTO IMPACTO")
  ) {
    return "AAI";
  }

  if (
    raw === "AR" ||
    raw.includes("REGIONAL")
  ) {
    return "AR";
  }

  if (
    raw === "PON" ||
    raw.includes("PONENCIA")
  ) {
    return "PON";
  }

  if (
    raw === "CAP" ||
    raw.includes("CAPITULO")
  ) {
    return "CAP";
  }

  if (
    raw === "LIB" ||
    raw === "LIBRO" ||
    raw.includes("LIBRO")
  ) {
    return "LIB";
  }

  return null;
}

function getCanonicalTypeLabel(input) {
  const code =
    normalizeCanonicalCode(input);

  return (
    CANONICAL_TYPE_MAP[code]?.label ||
    "Tipo de publicación"
  );
}

function normalizeTiposDisponibles(
  rawTipos = []
) {
  const totals = new Map(
    CANONICAL_TYPES.map((item) => [
      item.code,
      0,
    ])
  );

  for (const item of rawTipos) {
    const code =
      normalizeCanonicalCode(
        item?.codigo ||
          item?.id ||
          item?.nombre ||
          item?.label
      );

    if (!code) {
      continue;
    }

    totals.set(
      code,
      (totals.get(code) || 0) +
        Number(item?.total || 0)
    );
  }

  return CANONICAL_TYPES.map(
    (item) => ({
      id: item.code,
      codigo: item.code,
      nombre: item.label,
      total:
        totals.get(item.code) || 0,
    })
  );
}

function normalizePublicacionesPorTipoPayload(
  payload,
  selectedCode = null
) {
  const rawItems =
    Array.isArray(payload?.items)
      ? payload.items
      : [];

  const totals = new Map(
    CANONICAL_TYPES.map((item) => [
      item.code,
      0,
    ])
  );

  for (const item of rawItems) {
    const code =
      normalizeCanonicalCode(
        item?.tipo_codigo ||
          item?.tipo_id ||
          item?.tipo_nombre ||
          item?.label
      );

    if (!code) {
      continue;
    }

    totals.set(
      code,
      (totals.get(code) || 0) +
        Number(item?.total || 0)
    );
  }

  const backendTotal = Number(
    payload?.total_publicaciones || 0
  );

  const visibleTotal = [
    ...totals.values(),
  ].reduce(
    (acc, value) => acc + value,
    0
  );

  const total = Math.max(
    backendTotal,
    visibleTotal
  );

  const allItems =
    CANONICAL_TYPES.map((item) => {
      const totalItem =
        totals.get(item.code) || 0;

      return {
        tipo_id: item.code,
        tipo_codigo: item.code,
        tipo_nombre: item.label,
        total: totalItem,

        porcentaje:
          total > 0
            ? Number(
                (
                  (totalItem / total) *
                  100
                ).toFixed(2)
              )
            : 0,
      };
    });

  return {
    total_publicaciones: total,

    seleccionado: selectedCode
      ? allItems.find(
          (item) =>
            item.tipo_codigo ===
            selectedCode
        ) || null
      : null,

    items: allItems.filter(
      (item) =>
        Number(item.total || 0) > 0
    ),
  };
}

function normalizeSeriesPayload(payload) {
  const categorias =
    Array.isArray(payload?.categorias)
      ? payload.categorias
      : [];

  const rawSeries =
    Array.isArray(payload?.series)
      ? payload.series
      : [];

  const grouped = new Map(
    CANONICAL_TYPES.map((item) => [
      item.code,
      Array(categorias.length).fill(0),
    ])
  );

  for (const serie of rawSeries) {
    const code =
      normalizeCanonicalCode(
        serie?.codigo ||
          serie?.id ||
          serie?.label ||
          serie?.nombre
      );

    const target =
      grouped.get(code);

    if (!target) {
      continue;
    }

    categorias.forEach(
      (_, index) => {
        target[index] += Number(
          serie?.data?.[index] || 0
        );
      }
    );
  }

  return {
    categorias,

    series: CANONICAL_TYPES.map(
      (item) => ({
        id: item.code,
        codigo: item.code,
        label: item.label,

        data:
          grouped.get(item.code) ||
          Array(
            categorias.length
          ).fill(0),
      })
    ).filter((serie) =>
      serie.data.some(
        (value) =>
          Number(value || 0) > 0
      )
    ),

    total_publicaciones: Number(
      payload?.total_publicaciones || 0
    ),
  };
}

/* =========================================================
   FORMATO
========================================================= */

function formatNumber(value) {
  return Number(
    value || 0
  ).toLocaleString("es-EC");
}

function formatPercent(value) {
  return `${Number(
    value || 0
  ).toLocaleString("es-EC", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })}%`;
}

const MONTH_NAMES_ES = Object.freeze([
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
]);

function formatMonthYear(value) {
  const match = String(value || "")
    .trim()
    .match(/^(\d{4})-(\d{2})/);

  if (!match) {
    return "";
  }

  const year = Number(match[1]);
  const month = Number(match[2]);

  if (
    !Number.isInteger(year) ||
    month < 1 ||
    month > 12
  ) {
    return "";
  }

  const monthName =
    MONTH_NAMES_ES[month - 1];

  return (
    monthName.charAt(0).toUpperCase() +
    monthName.slice(1) +
    ` ${year}`
  );
}

/* =========================================================
   COLORES
========================================================= */

function paletteColor(index) {
  const palette = [
    "var(--ivbi-chart-1)",
    "var(--ivbi-chart-2)",
    "var(--ivbi-chart-3)",
    "var(--ivbi-chart-4)",
    "var(--ivbi-chart-5)",
    "var(--ivbi-chart-6)",
    "var(--ivbi-chart-7)",
    "var(--ivbi-chart-8)",
  ];

  return palette[
    index % palette.length
  ];
}

function rankingBarColor(index) {
  const palette = [
    "var(--ivbi-rank-1)",
    "var(--ivbi-rank-2)",
    "var(--ivbi-rank-3)",
    "var(--ivbi-rank-4)",
    "var(--ivbi-rank-5)",
  ];

  return palette[
    index % palette.length
  ];
}

function getTypeColor(
  code,
  fallbackIndex = 0
) {
  const normalized =
    normalizeCanonicalCode(code);

  const cssVar =
    TYPE_COLOR_VAR_MAP[
      normalized
    ] || null;

  return cssVar
    ? `var(${cssVar})`
    : paletteColor(fallbackIndex);
}

/* =========================================================
   GRÁFICOS
========================================================= */

function totalOf(items = []) {
  return items.reduce(
    (acc, item) => {
      return (
        acc +
        Number(
          item?.total ||
            item?.value ||
            0
        )
      );
    },
    0
  );
}

function donutGradient(items = []) {
  const total =
    totalOf(items);

  if (!total) {
    return (
      "conic-gradient(" +
      "var(--ivbi-line) " +
      "0deg 360deg)"
    );
  }

  let start = 0;

  const segments =
    items.map((item, index) => {
      const value = Number(
        item.total ||
          item.value ||
          0
      );

      const angle =
        (value / total) * 360;

      const end =
        start + angle;

      const segment =
        `${getTypeColor(
          item.tipo_codigo,
          index
        )} ${start}deg ${end}deg`;

      start = end;

      return segment;
    });

  return `conic-gradient(${segments.join(
    ", "
  )})`;
}

function maxValue(
  items = [],
  valueKey = "value"
) {
  return Math.max(
    ...items.map((item) =>
      Number(
        item?.[valueKey] || 0
      )
    ),
    0
  );
}

function verticalBarHeight(
  items = [],
  value = 0,
  valueKey = "value"
) {
  const max =
    maxValue(items, valueKey);

  if (!max) {
    return "0%";
  }

  const percent = Math.max(
    (Number(value || 0) / max) *
      100,
    4
  );

  return `${percent}%`;
}

function horizontalWidth(
  items = [],
  value = 0,
  valueKey = "value"
) {
  const max =
    maxValue(items, valueKey);

  if (!max) {
    return "0%";
  }

  const percent = Math.max(
    (Number(value || 0) / max) *
      100,
    4
  );

  return `${percent}%`;
}

function hasGroupedData(grouped) {
  return Boolean(
    grouped &&
      Array.isArray(
        grouped.categorias
      ) &&
      grouped.categorias.length &&
      Array.isArray(
        grouped.series
      ) &&
      grouped.series.length
  );
}

function groupedMax(series = []) {
  const values =
    series.flatMap(
      (item) => item.data || []
    );

  return Math.max(
    ...values,
    0
  );
}

function groupedBarHeight(
  series = [],
  value = 0
) {
  const max =
    groupedMax(series);

  if (!max) {
    return "0%";
  }

  const percent = Math.max(
    (Number(value || 0) / max) *
      100,
    4
  );

  return `${percent}%`;
}

/* =========================================================
   AUTO APLICACIÓN
========================================================= */

function clearAutoApplyTimer() {
  if (!autoApplyTimer) {
    return;
  }

  clearTimeout(autoApplyTimer);

  autoApplyTimer = null;
}

function scheduleAutoApply(
  delay = 220
) {
  if (
    !hasMounted.value ||
    suppressAutoApply.value
  ) {
    return;
  }

  clearAutoApplyTimer();

  autoApplyTimer =
    setTimeout(() => {
      aplicarFiltros();
    }, delay);
}

async function replayDashboardMotion() {
  await nextTick();

  visualRevision.value += 1;
}

/* =========================================================
   PARÁMETROS
========================================================= */

function buildParams() {
  const currentViewFilters =
    viewFilters[
      vistaActiva.value
    ] || {};

  return Object.fromEntries(
    Object.entries({
      facultad_id:
        globalFilters.facultad_id ||
        undefined,

      carrera_id:
        globalFilters.carrera_id ||
        undefined,

      tipo_codigo:
        currentViewFilters
          .tipo_codigo ||
        undefined,

      mes_desde:
        currentViewFilters
          .mes_desde ||
        undefined,

      mes_hasta:
        currentViewFilters
          .mes_hasta ||
        undefined,

      anio:
        currentViewFilters.anio ||
        undefined,

      top:
        currentViewFilters.top ||
        undefined,
    }).filter(
      ([, value]) =>
        value !== undefined &&
        value !== ""
    )
  );
}

/* =========================================================
   REPORTE EXCEL
========================================================= */

function sanitizeFileNamePart(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    )
    .toLowerCase()
    .replace(
      /[^a-z0-9]+/g,
      "-"
    )
    .replace(
      /^-+|-+$/g,
      ""
    )
    .slice(0, 80);
}

function buildReportFileName() {
  const now = new Date();

  const datePart = [
    now.getFullYear(),

    String(
      now.getMonth() + 1
    ).padStart(2, "0"),

    String(
      now.getDate()
    ).padStart(2, "0"),
  ].join("-");

  const viewPart =
    sanitizeFileNamePart(
      vistaActiva.value ||
        "dashboard"
    );

  const facultadPart =
    filtrosAplicados.value
      ?.facultad_nombre
      ? sanitizeFileNamePart(
          filtrosAplicados.value
            .facultad_nombre
        )
      : "institucional";

  return (
    "reporte-dashboard-" +
    "sgpc-uleam-" +
    `${viewPart}-` +
    `${facultadPart}-` +
    `${datePart}.xlsx`
  );
}

function extractApiErrorMessage(
  payload,
  fallback = ""
) {
  if (!payload) {
    return fallback;
  }

  if (typeof payload === "string") {
    return payload;
  }

  const direct =
    payload.detail ||
    payload.error ||
    payload.message;

  if (direct) {
    return String(direct);
  }

  for (const value of Object.values(payload)) {
    if (Array.isArray(value) && value.length) {
      return String(value[0]);
    }

    if (typeof value === "string") {
      return value;
    }
  }

  return fallback;
}

async function readBlobErrorMessage(
  errorBlob
) {
  try {
    if (
      !(errorBlob instanceof Blob)
    ) {
      return "";
    }

    const text =
      await errorBlob.text();

    if (!text) {
      return "";
    }

    try {
      const json =
        JSON.parse(text);

      return extractApiErrorMessage(
        json,
        text
      );
    } catch {
      return text;
    }
  } catch {
    return "";
  }
}

async function downloadDashboardReport() {
  if (
    downloadingReport.value
  ) {
    return;
  }

  downloadingReport.value = true;
  error.value = "";

  try {
    const { data } =
      await api.get(
        "/dashboard/reporte/excel/",
        {
          params: buildParams(),
          responseType: "blob",
        }
      );

    const blob = new Blob(
      [data],
      {
        type:
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      }
    );

    const url =
      window.URL.createObjectURL(
        blob
      );

    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      buildReportFileName();

    document.body.appendChild(
      link
    );

    link.click();

    link.remove();

    window.setTimeout(() => {
      window.URL.revokeObjectURL(
        url
      );
    }, 1000);
  } catch (err) {
    const blobMessage =
      await readBlobErrorMessage(
        err?.response?.data
      );

    error.value =
      blobMessage ||
      extractApiErrorMessage(
        err?.response?.data,
        err?.message
      ) ||
      "No fue posible descargar el reporte del dashboard.";
  } finally {
    downloadingReport.value = false;
  }
}

/* =========================================================
   CARGA DE DASHBOARD
========================================================= */

const requestParamsKey =
  computed(() =>
    JSON.stringify(
      buildParams()
    )
  );

async function loadDashboard() {
  const currentRequestId =
    ++requestId;

  if (hasLoadedOnce.value) {
    isRefreshing.value = true;
  } else {
    loading.value = true;
  }

  error.value = "";

  try {
    const { data } =
      await api.get(
        "/dashboard/resumen/",
        {
          params: buildParams(),
        }
      );

    if (
      currentRequestId !==
      requestId
    ) {
      return;
    }

    if (!data?.ok) {
      throw new Error(
        "La API no devolvió una respuesta válida."
      );
    }

    response.value = data;

    await replayDashboardMotion();

    const carrerasValidas =
      new Set(
        (
          data
            ?.filtros_disponibles
            ?.carreras || []
        ).map((item) =>
          String(item.id)
        )
      );

    if (
      globalFilters.carrera_id &&
      !carrerasValidas.has(
        String(
          globalFilters.carrera_id
        )
      )
    ) {
      suppressAutoApply.value = true;

      globalFilters.carrera_id = "";

      suppressAutoApply.value = false;
    }
  } catch (err) {
    if (
      currentRequestId !==
      requestId
    ) {
      return;
    }

    error.value =
      extractApiErrorMessage(
        err?.response?.data,
        err?.message
      ) ||
      "No fue posible cargar el panel analítico.";

    response.value =
      EMPTY_RESPONSE;

    await replayDashboardMotion();
  } finally {
    if (
      currentRequestId ===
      requestId
    ) {
      loading.value = false;
      isRefreshing.value = false;
      hasLoadedOnce.value = true;
    }
  }
}

async function aplicarFiltros() {
  const current =
    viewFilters[
      vistaActiva.value
    ] || {};

  if (
    current.mes_desde &&
    current.mes_hasta &&
    current.mes_desde >
      current.mes_hasta
  ) {
    error.value =
      "El período mensual es inválido: " +
      "'Desde' no puede ser posterior " +
      "a 'Hasta'.";

    return;
  }

  error.value = "";

  await loadDashboard();
}

/* =========================================================
   RESTABLECER FILTROS
========================================================= */

async function resetCurrentViewFilters() {
  suppressAutoApply.value = true;

  if (
    vistaActiva.value ===
    "resumen"
  ) {
    viewFilters.resumen.tipo_codigo =
      "";

    viewFilters.resumen.mes_desde =
      "";

    viewFilters.resumen.mes_hasta =
      "";
  } else if (
    vistaActiva.value ===
    "tendencia"
  ) {
    viewFilters.tendencia.tipo_codigo =
      "";

    viewFilters.tendencia.mes_desde =
      "";

    viewFilters.tendencia.mes_hasta =
      "";

    viewFilters.tendencia.anio =
      "";
  } else {
    viewFilters.rankings.tipo_codigo =
      "";

    viewFilters.rankings.mes_desde =
      "";

    viewFilters.rankings.mes_hasta =
      "";

    viewFilters.rankings.top =
      "10";
  }

  hoveredTypeCode.value = "";

  suppressAutoApply.value = false;

  clearAutoApplyTimer();

  await loadDashboard();
}

async function resetAllFilters() {
  suppressAutoApply.value = true;

  globalFilters.facultad_id =
    "";

  globalFilters.carrera_id =
    "";

  const defaults =
    defaultViewFilters();

  Object.assign(
    viewFilters.resumen,
    defaults.resumen
  );

  Object.assign(
    viewFilters.tendencia,
    defaults.tendencia
  );

  Object.assign(
    viewFilters.rankings,
    defaults.rankings
  );

  hoveredTypeCode.value = "";

  suppressAutoApply.value = false;

  clearAutoApplyTimer();

  await loadDashboard();
}

/* =========================================================
   INTERACCIONES
========================================================= */

function handleLegendEnter(code) {
  hoveredTypeCode.value =
    normalizeCanonicalCode(code) || "";
}

function handleLegendLeave() {
  hoveredTypeCode.value = "";
}

function isTypeSelected(code) {
  return (
    String(
      activeViewFilters.value
        ?.tipo_codigo || ""
    ) ===
    String(code || "")
  );
}

function applyTypeFilter(code) {
  const normalized =
    normalizeCanonicalCode(code);

  if (!normalized) {
    return;
  }

  const current =
    String(
      activeViewFilters.value
        ?.tipo_codigo || ""
    );

  suppressAutoApply.value = true;

  activeViewFilters.value.tipo_codigo =
    current === normalized
      ? ""
      : normalized;

  suppressAutoApply.value = false;

  scheduleAutoApply(80);
}

function applyYearFromTrend(label) {
  const value =
    String(label || "").trim();

  if (
    !/^\d{4}$/.test(value)
  ) {
    return;
  }

  suppressAutoApply.value = true;

  viewFilters.tendencia.anio =
    String(
      viewFilters.tendencia.anio
    ) === value
      ? ""
      : value;

  suppressAutoApply.value = false;

  scheduleAutoApply(80);
}

/* =========================================================
   ANIMACIÓN NUMÉRICA
========================================================= */

function useTweenNumber(
  source,
  duration = 700
) {
  const display = ref(
    Number(source.value || 0)
  );

  let frame = 0;

  const stop = watch(
    source,
    (newValue) => {
      if (
        typeof window ===
        "undefined"
      ) {
        display.value = Number(
          newValue || 0
        );

        return;
      }

      cancelAnimationFrame(
        frame
      );

      const startValue =
        Number(
          display.value || 0
        );

      const endValue =
        Number(
          newValue || 0
        );

      const startTime =
        performance.now();

      const tick = (now) => {
        const progress = Math.min(
          (now - startTime) /
            duration,
          1
        );

        const eased =
          1 -
          Math.pow(
            1 - progress,
            3
          );

        display.value =
          Math.round(
            startValue +
              (
                endValue -
                startValue
              ) *
                eased
          );

        if (progress < 1) {
          frame =
            requestAnimationFrame(
              tick
            );
        }
      };

      frame =
        requestAnimationFrame(
          tick
        );
    },
    {
      immediate: true,
    }
  );

  onBeforeUnmount(() => {
    stop();

    if (
      typeof window !==
      "undefined"
    ) {
      cancelAnimationFrame(
        frame
      );
    }
  });

  return display;
}

/* =========================================================
   COMPUTED — RESPUESTA
========================================================= */

const summary = computed(
  () =>
    response.value?.summary ||
    EMPTY_RESPONSE.summary
);

const dashboards = computed(
  () =>
    response.value
      ?.dashboards ||
    EMPTY_RESPONSE.dashboards
);

const filtrosDisponibles =
  computed(
    () =>
      response.value
        ?.filtros_disponibles ||
      EMPTY_RESPONSE
        .filtros_disponibles
  );

const filtrosAplicados =
  computed(() => {
    const raw =
      response.value
        ?.filtros_aplicados || {};

    const tipoCodigo =
      raw?.tipo_codigo
        ? normalizeCanonicalCode(
            raw.tipo_codigo
          )
        : null;

    return {
      ...raw,

      tipo_codigo:
        tipoCodigo,

      tipo_nombre:
        raw?.tipo_nombre ||
        (
          tipoCodigo
            ? getCanonicalTypeLabel(
                tipoCodigo
              )
            : null
        ),
    };
  });

const tiposDisponiblesCanonicos =
  computed(() =>
    normalizeTiposDisponibles(
      filtrosDisponibles.value
        ?.tipos || []
    )
  );

const carrerasFiltradas =
  computed(() => {
    const all =
      filtrosDisponibles.value
        ?.carreras || [];

    if (
      !globalFilters.facultad_id
    ) {
      return all;
    }

    return all.filter(
      (career) =>
        String(
          career.facultad_id
        ) ===
        String(
          globalFilters.facultad_id
        )
    );
  });

/* =========================================================
   COMPUTED — DASHBOARDS
========================================================= */

const publicacionesPorAnio =
  computed(
    () =>
      dashboards.value
        .publicaciones_por_anio ||
      []
  );

const publicacionesPorMes =
  computed(
    () =>
      dashboards.value
        .publicaciones_por_mes ||
      EMPTY_RESPONSE
        .dashboards
        .publicaciones_por_mes
  );

const publicacionesPorTipo =
  computed(() =>
    normalizePublicacionesPorTipoPayload(
      dashboards.value
        .publicaciones_por_tipo,

      filtrosAplicados.value
        ?.tipo_codigo || null
    )
  );

const publicacionesPorTipoAnual =
  computed(() =>
    normalizeSeriesPayload(
      dashboards.value
        .publicaciones_por_tipo_anual
    )
  );

const topFacultades =
  computed(
    () =>
      dashboards.value
        .top_facultades ||
      EMPTY_RESPONSE
        .dashboards
        .top_facultades
  );

const topCarreras =
  computed(
    () =>
      dashboards.value
        .top_carreras ||
      EMPTY_RESPONSE
        .dashboards
        .top_carreras
  );

const topAutores =
  computed(
    () =>
      dashboards.value
        .top_autores ||
      EMPTY_RESPONSE
        .dashboards
        .top_autores
  );

const journals =
  computed(
    () =>
      dashboards.value
        .journals ||
      EMPTY_RESPONSE
        .dashboards
        .journals
  );

const projects =
  computed(
    () =>
      dashboards.value
        .projects ||
      EMPTY_RESPONSE
        .dashboards
        .projects
  );

const anioBaseMensual =
  computed(
    () =>
      filtrosDisponibles.value
        ?.anio_base_mensual ||
      null
  );

const autoAnioMensualLabel =
  computed(() =>
    anioBaseMensual.value
      ? `Auto (${anioBaseMensual.value})`
      : "Auto"
  );

/* =========================================================
   DATOS DISPONIBLES
========================================================= */

const hasData = computed(() => {
  return Boolean(
    Number(
      summary.value
        .total_publicaciones || 0
    ) > 0 ||
      publicacionesPorAnio.value
        .length > 0 ||
      publicacionesPorTipo.value
        .items.length > 0 ||
      topAutores.value
        .items.length > 0 ||
      topFacultades.value
        .items.length > 0 ||
      topCarreras.value
        .items.length > 0 ||
      journals.value
        .items.length > 0 ||
      projects.value
        .items.length > 0
  );
});

/* =========================================================
   DONUT
========================================================= */

const tipoDominante =
  computed(() => {
    const items = [
      ...publicacionesPorTipo
        .value.items,
    ];

    if (!items.length) {
      return null;
    }

    items.sort(
      (a, b) =>
        Number(
          b.total || 0
        ) -
        Number(
          a.total || 0
        )
    );

    return items[0] || null;
  });

const donutFocusItem =
  computed(() => {
    if (
      !hoveredTypeCode.value
    ) {
      return null;
    }

    return (
      publicacionesPorTipo
        .value.items.find(
          (item) =>
            item.tipo_codigo ===
            hoveredTypeCode.value
        ) || null
    );
  });

const donutCenterValue =
  computed(() => {
    if (
      donutFocusItem.value
    ) {
      return formatNumber(
        donutFocusItem.value.total
      );
    }

    return formatNumber(
      totalOf(
        publicacionesPorTipo
          .value.items
      )
    );
  });

const donutCenterLabel =
  computed(() => {
    if (
      donutFocusItem.value
    ) {
      return (
        donutFocusItem.value
          .tipo_codigo
      );
    }

    return "Total";
  });

const donutCenterHint =
  computed(() => {
    if (
      donutFocusItem.value
    ) {
      return (
        donutFocusItem.value
          .tipo_nombre
      );
    }

    return "Publicaciones";
  });

/* =========================================================
   CONTEXTO DEL DASHBOARD
========================================================= */

const tipoDominanteResumen =
  computed(() => {
    if (
      !tipoDominante.value
    ) {
      return "—";
    }

    return (
      `${tipoDominante.value.tipo_nombre}` +
      ` · ` +
      `${formatPercent(
        tipoDominante.value
          .porcentaje
      )}`
    );
  });

const periodoResumen =
  computed(() => {
    const mesDesde =
      filtrosAplicados.value
        ?.mes_desde;

    const mesHasta =
      filtrosAplicados.value
        ?.mes_hasta;

    const desde =
      formatMonthYear(mesDesde);

    const hasta =
      formatMonthYear(mesHasta);

    if (desde && hasta) {
      return desde === hasta
        ? desde
        : `${desde} — ${hasta}`;
    }

    if (desde) {
      return `Desde ${desde}`;
    }

    if (hasta) {
      return `Hasta ${hasta}`;
    }

    const anioDesde =
      filtrosAplicados.value
        ?.anio_desde;

    const anioHasta =
      filtrosAplicados.value
        ?.anio_hasta;

    if (anioDesde && anioHasta) {
      return anioDesde === anioHasta
        ? String(anioDesde)
        : `${anioDesde} — ${anioHasta}`;
    }

    if (anioDesde) {
      return `Desde ${anioDesde}`;
    }

    if (anioHasta) {
      return `Hasta ${anioHasta}`;
    }

    const categorias =
      publicacionesPorAnio.value ||
      [];

    if (
      categorias.length >= 2
    ) {
      return (
        `${categorias[0].label}` +
        ` — ` +
        `${
          categorias[
            categorias.length - 1
          ].label
        }`
      );
    }

    if (
      categorias.length === 1
    ) {
      return categorias[0].label;
    }

    return "Histórico";
  });

const coberturaResumen =
  computed(() => {
    if (
      filtrosAplicados.value
        ?.carrera_nombre
    ) {
      return (
        filtrosAplicados.value
          .carrera_nombre
      );
    }

    if (
      filtrosAplicados.value
        ?.facultad_nombre
    ) {
      return (
        filtrosAplicados.value
          .facultad_nombre
      );
    }

    return "Toda la institución";
  });

const dashboardMetaLine =
  computed(() =>
    [
      coberturaResumen.value,
      periodoResumen.value,
      tipoDominanteResumen.value,
    ]
      .filter(Boolean)
      .join(" · ")
  );

/* =========================================================
   KPIs
========================================================= */

const totalPublicacionesTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_publicaciones
    )
  );

const totalAutoresTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_autores
    )
  );

const totalFacultadesTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_facultades
    )
  );

const totalCarrerasTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_carreras
    )
  );

const totalProyectosTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_proyectos
    )
  );

const totalAltoImpactoTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .articulos_alto_impacto
    )
  );

const headlineKpis =
  computed(() => [
    {
      key: "publicaciones",
      label: "Publicaciones",
      value:
        totalPublicacionesTween.value,
      hint: periodoResumen.value,
      iconPath:
        "M6 3h8l4 4v14H6V3Zm8 0v5h5M9 13h6M9 17h6",
    },

    {
      key: "autores",
      label: "Autores",
      value:
        totalAutoresTween.value,
      hint: "Autores vinculados",
      iconPath:
        "M8.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7-1a3 3 0 1 0 0-6M2.5 21c.6-4.2 3-6.5 6-6.5s5.4 2.3 6 6.5M14 14.8c3.6.4 5.7 2.4 6 6.2",
    },

    {
      key: "facultades",
      label: "Facultades",
      value:
        totalFacultadesTween.value,
      hint:
        "Cobertura institucional",
      iconPath:
        "M3 9 12 4l9 5M5 10v8M9 10v8M15 10v8M19 10v8M3 20h18",
    },

    {
      key: "carreras",
      label: "Carreras",
      value:
        totalCarrerasTween.value,
      hint: "Oferta académica",
      iconPath:
        "M3 8l9-5 9 5-9 5-9-5Zm4 3v5c3 2 7 2 10 0v-5M21 8v6",
    },

    {
      key: "proyectos",
      label: "Proyectos",
      value:
        totalProyectosTween.value,
      hint: "Proyectos asociados",
      iconPath:
        "M8 6V4h8v2M4 7h16v13H4V7Zm0 5h16M9 12v2h6v-2",
    },

    {
      key: "alto-impacto",
      label: "Alto impacto",
      value:
        totalAltoImpactoTween.value,
      hint: "Artículos indexados",
      iconPath:
        "m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2-4.5-4.4 6.2-.9L12 3Z",
    },
  ]);

/* =========================================================
   RANKINGS
========================================================= */

const topFacultadesData =
  computed(() =>
    (
      topFacultades.value.items ||
      []
    ).map((item) => ({
      label:
        item.facultad ||
        item.label ||
        "Facultad",

      total: Number(
        item.total || 0
      ),
    }))
  );

const topCarrerasData =
  computed(() =>
    (
      topCarreras.value.items ||
      []
    ).map((item) => ({
      label:
        item.carrera ||
        item.label ||
        "Carrera",

      total: Number(
        item.total || 0
      ),
    }))
  );

function normalizeAuthorRankingItems(
  items = [],
  fallbackLabel = "Autor"
) {
  return (items || []).map(
    (item) => ({
      label:
        item.label ||
        item.autor ||
        fallbackLabel,

      total: Number(
        item.total_publicaciones ||
          item.total ||
          0
      ),
    })
  );
}

const topAutoresData =
  computed(() =>
    normalizeAuthorRankingItems(
      topAutores.value
        .items || [],
      "Autor"
    )
  );

const journalsData =
  computed(() =>
    (
      journals.value.items ||
      []
    ).map((item) => ({
      label:
        item.label ||
        item.revista ||
        "Revista",

      total: Number(
        item.total || 0
      ),
    }))
  );

const projectsData =
  computed(() =>
    (
      projects.value.items ||
      []
    ).map((item) => ({
      label:
        item.label ||
        item.proyecto ||
        "Proyecto",

      total: Number(
        item.total || 0
      ),
    }))
  );

const topAutoresResumen =
  computed(() =>
    topAutoresData
      .value.slice(0, 5)
  );

const topFacultadesResumen =
  computed(() =>
    topFacultadesData.value.slice(
      0,
      5
    )
  );

/* =========================================================
   WATCHERS
========================================================= */

watch(
  () =>
    globalFilters.facultad_id,

  (newValue, oldValue) => {
    if (
      !hasMounted.value ||
      newValue === oldValue
    ) {
      return;
    }

    if (
      globalFilters.carrera_id
    ) {
      suppressAutoApply.value =
        true;

      globalFilters.carrera_id =
        "";

      suppressAutoApply.value =
        false;
    }

    scheduleAutoApply();
  }
);

watch(
  () => vistaActiva.value,

  () => {
    if (!hasMounted.value) {
      return;
    }

    hoveredTypeCode.value = "";

    scheduleAutoApply(120);
  }
);

watch(
  requestParamsKey,

  (newValue, oldValue) => {
    if (
      !hasMounted.value ||
      suppressAutoApply.value ||
      newValue === oldValue
    ) {
      return;
    }

    scheduleAutoApply();
  }
);

/* =========================================================
   CICLO DE VIDA
========================================================= */

onMounted(async () => {
  await loadDashboard();

  hasMounted.value = true;
});

onBeforeUnmount(() => {
  clearAutoApplyTimer();
});
</script>

<style src="./inicio-view.css"></style>
