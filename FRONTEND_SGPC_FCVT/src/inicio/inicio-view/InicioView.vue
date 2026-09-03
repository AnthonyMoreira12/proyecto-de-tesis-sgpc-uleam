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
                v-for="n in 7"
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
                <div class="ivbi-header__titlebox">
                  <h1
                    id="ivbi-dashboard-title"
                    class="ivbi-header__title"
                  >
                    Producción científica
                  </h1>

                  <p class="ivbi-header__meta">
                    {{ dashboardMetaLine }}
                  </p>
                </div>
              </div>

              <div class="ivbi-header__actions">
                <div
                  ref="reportMenuRef"
                  class="ivbi-report-menu"
                >
                  <button
                    class="ivbi-btn ivbi-btn--primary ivbi-btn--download"
                    type="button"
                    :disabled="
                      loading ||
                      isRefreshing ||
                      downloadingReport
                    "
                    :aria-expanded="reportMenuOpen ? 'true' : 'false'"
                    aria-haspopup="menu"
                    @click="toggleReportMenu"
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
                          ? downloadingReportLabel
                          : "Descargar informe"
                      }}
                    </span>

                    <svg
                      v-if="!downloadingReport"
                      class="ivbi-report-menu__chevron"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path
                        d="m6 8 4 4 4-4"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </button>

                  <div
                    v-if="reportMenuOpen"
                    class="ivbi-report-menu__panel"
                    role="menu"
                    aria-label="Formato del informe"
                  >
                    <button
                      class="ivbi-report-option is-primary"
                      type="button"
                      role="menuitem"
                      @click="downloadDashboardReport('pdf')"
                    >
                      <span class="ivbi-report-option__icon">PDF</span>

                      <span class="ivbi-report-option__copy">
                        <strong>Informe en PDF</strong>
                        <small>Listo para compartir o imprimir</small>
                      </span>

                      <span class="ivbi-report-option__tag">Recomendado</span>
                    </button>

                    <button
                      class="ivbi-report-option"
                      type="button"
                      role="menuitem"
                      @click="downloadDashboardReport('excel')"
                    >
                      <span class="ivbi-report-option__icon">XLS</span>

                      <span class="ivbi-report-option__copy">
                        <strong>Datos en Excel</strong>
                        <small>Para ordenar, filtrar o trabajar con los datos</small>
                      </span>
                    </button>

                    <button
                      v-if="isAdmin"
                      class="ivbi-report-option"
                      type="button"
                      role="menuitem"
                      @click="downloadDashboardReport('institutional_excel')"
                    >
                      <span class="ivbi-report-option__icon">ADM</span>

                      <span class="ivbi-report-option__copy">
                        <strong>Excel institucional detallado</strong>
                        <small>Publicaciones aprobadas con detalle para gestión administrativa</small>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- =================================================
                 NAVEGACIÓN
            ================================================== -->
            <section
              class="ivbi-header__navigation"
              aria-label="Vista de producción científica"
            >
              <nav
                class="ivbi-segmented"
                aria-label="Vistas de producción científica"
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

            </section>

            <!-- =================================================
                 FILTROS COMPACTOS
            ================================================== -->
            <section
              class="ivbi-filterbar ivbi-filterbar--compact"
              :class="`is-${vistaActiva}`"
              aria-label="Filtros de producción científica"
            >
              <!-- CAMPOS -->
              <div class="ivbi-filterbar__fields">
                <label class="ivbi-field ivbi-field--institutional ivbi-field--sede">
                  <span>Sede</span>

                  <select
                    v-model="globalFilters.sede_id"
                    aria-label="Filtrar por sede"
                  >
                    <option value="">
                      Todas las sedes
                    </option>

                    <option
                      v-for="sede in filtrosDisponibles.sedes"
                      :key="sede.id"
                      :value="String(sede.id)"
                    >
                      {{ sede.nombre }}
                    </option>
                  </select>
                </label>

                <label class="ivbi-field ivbi-field--institutional ivbi-field--facultad">
                  <span>Facultad</span>

                  <select
                    v-model="globalFilters.facultad_id"
                    aria-label="Filtrar por facultad"
                  >
                    <option value="">
                      Todas las facultades
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

                <label class="ivbi-field ivbi-field--institutional ivbi-field--carrera">
                  <span>Carrera</span>

                  <select
                    v-model="globalFilters.carrera_id"
                    aria-label="Filtrar por carrera"
                    :disabled="!globalFilters.facultad_id"
                  >
                    <option value="">
                      {{
                        globalFilters.facultad_id
                          ? "Todas las carreras"
                          : "Seleccione una facultad"
                      }}
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

                <label class="ivbi-field ivbi-field--tipo">
                  <span>Tipo de publicación</span>

                  <select v-model="activeViewFilters.tipo_codigo">
                    <option value="">
                      Todos los tipos
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

                <PeriodRangePicker
                  :from="activeViewFilters.mes_desde"
                  :to="activeViewFilters.mes_hasta"
                  :period="periodoDisponible"
                  @update:from="activeViewFilters.mes_desde = $event"
                  @update:to="activeViewFilters.mes_hasta = $event"
                />

                <!-- DESTACADOS: límite del ranking -->
                <template v-if="vistaActiva === 'rankings'">
                  <label class="ivbi-field">
                    <span>Cantidad</span>

                    <select v-model="viewFilters.rankings.top">
                      <option value="5">5</option>
                      <option value="10">10</option>
                      <option value="15">15</option>
                      <option value="20">20</option>
                    </select>
                  </label>
                </template>
              </div>

              <!-- ACCIONES -->
              <div class="ivbi-filterbar__actions">
                <button
                  class="ivbi-filter-action"
                  type="button"
                  title="Quitar filtros"
                  :disabled="
                    loading ||
                    isRefreshing ||
                    downloadingReport
                  "
                  @click="resetCurrentFilters"
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

                  <span>Quitar filtros</span>
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
                    class="ivbi-kpi-card ivbi-hover-info ivbi-hover-info--kpi"
                    tabindex="0"
                    :data-tooltip="kpi.tooltip"
                    :aria-label="`${kpi.label}: ${formatNumber(kpi.value)}. ${kpi.tooltip}`"
                    :class="[
                      `ivbi-kpi-card--${kpi.key}`,
                      {
                        'is-primary':
                          kpi.key === 'publicaciones',

                        'is-coverage': [
                          'sedes',
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

                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo
                        </h3>
                      </div>

                      <div class="ivbi-card__head-tools">
                        <span
                          v-if="tipoDominante"
                          class="ivbi-insight-pill"
                        >
                          Más frecuente:
                          {{ tipoDominante.tipo_nombre }}
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
                            Haz clic en un tipo para ver solo
                            esas publicaciones. Haz clic de
                            nuevo para mostrar todas.
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
                      No hay publicaciones para mostrar.
                    </div>
                  </article>

                  <!-- SEDES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--sedes
                      ivbi-card--compact-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">

                        <h3 class="ivbi-card__title">
                          Sedes
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topSedesResumen.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topSedesResumen"
                        :key="`top-sede-${item.label}`"
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">
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
                              '--rank-w': horizontalWidth(
                                topSedesResumen,
                                item.total,
                                'total'
                              ),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index),
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay sedes con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- FACULTADES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--facultades
                      ivbi-card--compact-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">

                        <h3 class="ivbi-card__title">
                          Facultades
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
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
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
                      No hay facultades con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- AUTORES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--autores
                      ivbi-card--compact-rank
                      ivbi-card--simple-list
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Autores
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topAutoresResumen.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-simple-list"
                    >
                      <div
                        v-for="(item, index) in topAutoresResumen"
                        :key="`top-autor-${item.label}`"
                        class="
                          ivbi-simple-list__row
                          ivbi-hover-info
                          ivbi-hover-info--rank
                        "
                        tabindex="0"
                        :data-tooltip="buildRankingTooltip(item, index)"
                        :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
                      >
                        <span class="ivbi-simple-list__index">
                          {{ index + 1 }}
                        </span>

                        <span
                          class="ivbi-simple-list__label"
                          :title="item.label"
                        >
                          {{ item.label }}
                        </span>

                        <strong class="ivbi-simple-list__count">
                          {{ publicationCountText(item.total) }}
                        </strong>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay autores con publicaciones para esta selección.
                    </div>
                  </article>
                </section>
              </section>

              <!-- =============================================
                   TENDENCIA / EVOLUCIÓN
              ============================================== -->
              <section
                v-else-if="
                  vistaActiva === 'tendencia'
                "
                key="tendencia"
                class="
                  ivbi-view-shell
                  ivbi-view-shell--trend
                "
              >
                <section
                  :key="
                    `trend-grid-${visualRevision}`
                  "
                  class="ivbi-trend-grid"
                  aria-label="Evolución de la producción científica"
                >
                  <!-- =========================================
                       1. EVOLUCIÓN HISTÓRICA
                  ========================================== -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--trend-panel
                      ivbi-card--historica
                    "
                  >
                    <header class="ivbi-card__head ivbi-trend-head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Evolución de la producción
                        </h3>

                        <p class="ivbi-card__subtitle">
                          Comportamiento histórico de las publicaciones
                        </p>
                      </div>

                      <span
                        v-if="annualRangeLabel"
                        class="ivbi-trend-context"
                      >
                        {{ annualRangeLabel }}
                      </span>
                    </header>

                    <div
                      v-if="publicacionesPorAnio.length"
                      class="
                        ivbi-line-chart
                        ivbi-line-chart--annual
                      "
                    >
                      <div class="ivbi-line-chart__plot">
                        <svg
                          class="ivbi-line-chart__svg"
                          viewBox="0 0 100 100"
                          preserveAspectRatio="none"
                          aria-hidden="true"
                          focusable="false"
                        >
                          <line
                            v-for="level in [25, 50, 75]"
                            :key="`annual-grid-${level}`"
                            x1="3"
                            x2="97"
                            :y1="level"
                            :y2="level"
                            class="ivbi-line-chart__gridline"
                          />

                          <polyline
                            :points="
                              lineChartPolyline(
                                publicacionesPorAnio
                              )
                            "
                            class="ivbi-line-chart__line"
                          />
                        </svg>

                        <button
                          v-for="(
                            item,
                            index
                          ) in publicacionesPorAnio"
                          :key="
                            `annual-point-${item.label}`
                          "
                          type="button"
                          class="
                            ivbi-line-chart__point
                            ivbi-hover-info
                          "
                          :class="[
                            tooltipEdgeClass(
                              index,
                              publicacionesPorAnio.length
                            ),
                            {
                              'is-selected':
                                String(
                                  viewFilters
                                    .tendencia
                                    .anio
                                ) === String(item.label),
                            },
                          ]"
                          :style="
                            lineChartPointStyle(
                              publicacionesPorAnio,
                              item,
                              index
                            )
                          "
                          :data-tooltip="
                            buildAnnualTooltip(
                              item,
                              index
                            )
                          "
                          :aria-label="
                            buildAnnualTooltip(
                              item,
                              index
                            )
                          "
                          @click="
                            applyYearFromTrend(
                              item.label
                            )
                          "
                        >
                          <span
                            class="
                              ivbi-line-chart__value
                            "
                          >
                            {{ item.value }}
                          </span>

                          <span
                            class="
                              ivbi-line-chart__dot
                            "
                          ></span>
                        </button>
                      </div>

                      <div class="ivbi-line-chart__axis">
                        <span
                          v-for="item in publicacionesPorAnio"
                          :key="
                            `annual-label-${item.label}`
                          "
                          class="
                            ivbi-line-chart__axis-label
                          "
                        >
                          {{ item.label }}
                        </span>
                      </div>

                      <p
                        class="
                          ivbi-chart-note
                          ivbi-chart-note--interactive
                        "
                      >
                        Haz clic en un año para ver su detalle mensual.
                      </p>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay publicaciones por año para esta selección.
                    </div>
                  </article>

                  <!-- =========================================
                       2. EVOLUCIÓN POR TIPO
                  ========================================== -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--trend-panel
                      ivbi-card--comparativa
                    "
                  >
                    <header class="ivbi-card__head ivbi-trend-head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Evolución por tipo de publicación
                        </h3>

                        <p class="ivbi-card__subtitle">
                          Comparación anual según categoría
                        </p>
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
                          class="
                            ivbi-grouped__group
                          "
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
                                ivbi-hover-info
                                ivbi-hover-info--chart
                              "
                              tabindex="0"
                              :data-tooltip="
                                buildTypeYearTooltip(
                                  serie,
                                  catIndex,
                                  category
                                )
                              "
                              :aria-label="
                                buildTypeYearTooltip(
                                  serie,
                                  catIndex,
                                  category
                                )
                              "
                              :class="
                                tooltipEdgeClass(
                                  serieIndex,
                                  publicacionesPorTipoAnual
                                    .series.length
                                )
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
                        aria-label="Tipos de publicación"
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
                            aria-hidden="true"
                          ></i>

                          {{ serie.label }}
                        </span>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay información para comparar.
                    </div>
                  </article>

                  <!-- =========================================
                       3. COMPORTAMIENTO MENSUAL
                  ========================================== -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--trend-panel
                      ivbi-card--mensual
                    "
                  >
                    <header class="ivbi-card__head ivbi-trend-head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Comportamiento mensual
                        </h3>

                        <p class="ivbi-card__subtitle">
                          Distribución de publicaciones durante el año
                        </p>
                      </div>

                      <span class="ivbi-trend-context">
                        {{
                          publicacionesPorMes.anio_base ||
                          "Último año con información"
                        }}
                      </span>
                    </header>

                    <div
                      v-if="
                        publicacionesPorMes.items.length
                      "
                      class="
                        ivbi-line-chart
                        ivbi-line-chart--area
                        ivbi-line-chart--monthly
                      "
                    >
                      <div class="ivbi-line-chart__plot">
                        <svg
                          class="ivbi-line-chart__svg"
                          viewBox="0 0 100 100"
                          preserveAspectRatio="none"
                          aria-hidden="true"
                          focusable="false"
                        >
                          <line
                            v-for="level in [25, 50, 75]"
                            :key="
                              `monthly-grid-${level}`
                            "
                            x1="3"
                            x2="97"
                            :y1="level"
                            :y2="level"
                            class="
                              ivbi-line-chart__gridline
                            "
                          />

                          <polygon
                            :points="
                              lineChartAreaPoints(
                                publicacionesPorMes.items
                              )
                            "
                            class="
                              ivbi-line-chart__area
                            "
                          />

                          <polyline
                            :points="
                              lineChartPolyline(
                                publicacionesPorMes.items
                              )
                            "
                            class="
                              ivbi-line-chart__line
                            "
                          />
                        </svg>

                        <div
                          v-for="(
                            item,
                            index
                          ) in publicacionesPorMes.items"
                          :key="
                            `monthly-point-${item.label}`
                          "
                          class="
                            ivbi-line-chart__point
                            ivbi-line-chart__point--static
                            ivbi-hover-info
                          "
                          tabindex="0"
                          :class="
                            tooltipEdgeClass(
                              index,
                              publicacionesPorMes
                                .items.length
                            )
                          "
                          :style="
                            lineChartPointStyle(
                              publicacionesPorMes.items,
                              item,
                              index
                            )
                          "
                          :data-tooltip="
                            buildMonthlyTooltip(
                              item,
                              index
                            )
                          "
                          :aria-label="
                            buildMonthlyTooltip(
                              item,
                              index
                            )
                          "
                        >
                          <span
                            class="
                              ivbi-line-chart__value
                            "
                          >
                            {{ item.value }}
                          </span>

                          <span
                            class="
                              ivbi-line-chart__dot
                            "
                          ></span>
                        </div>
                      </div>

                      <div class="ivbi-line-chart__axis">
                        <span
                          v-for="item in publicacionesPorMes.items"
                          :key="
                            `monthly-label-${item.label}`
                          "
                          class="
                            ivbi-line-chart__axis-label
                          "
                          :title="item.label"
                        >
                          {{ item.label }}
                        </span>
                      </div>
                    </div>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay publicaciones por mes para esta selección.
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
                  <!-- SEDES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--sedes-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">

                        <h3 class="ivbi-card__title">
                          Sedes
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topSedesData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topSedesData"
                        :key="`rank-sede-${item.label}`"
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">
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
                              '--rank-w': horizontalWidth(
                                topSedesData,
                                item.total,
                                'total'
                              ),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index),
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      No hay sedes con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- FACULTADES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--facultades-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">

                        <h3 class="ivbi-card__title">
                          Facultades
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
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
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
                      No hay facultades con publicaciones para esta selección.
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

                        <h3 class="ivbi-card__title">
                          Carreras
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
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
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
                      No hay carreras con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- AUTORES -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--autores-rank
                      ivbi-card--simple-list
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Autores
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topAutoresData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-simple-list"
                    >
                      <div
                        v-for="(item, index) in topAutoresData"
                        :key="`rank-autor-${item.label}`"
                        class="
                          ivbi-simple-list__row
                          ivbi-hover-info
                          ivbi-hover-info--rank
                        "
                        tabindex="0"
                        :data-tooltip="buildRankingTooltip(item, index)"
                        :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
                      >
                        <span class="ivbi-simple-list__index">
                          {{ index + 1 }}
                        </span>

                        <span
                          class="ivbi-simple-list__label"
                          :title="item.label"
                        >
                          {{ item.label }}
                        </span>

                        <strong class="ivbi-simple-list__count">
                          {{ publicationCountText(item.total) }}
                        </strong>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay autores con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- ÁREAS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--areas-rank
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">

                        <h3 class="ivbi-card__title">
                          Áreas de conocimiento
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="areasData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(
                          item,
                          index
                        ) in areasData"
                        :key="
                          `rank-area-${item.label}`
                        "
                        class="ivbi-rank__row ivbi-hover-info ivbi-hover-info--rank"
                      tabindex="0"
                      :data-tooltip="buildRankingTooltip(item, index)"
                      :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
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
                                  areasData,
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
                      No hay áreas con publicaciones para esta selección.
                    </div>
                  </article>

                  <!-- REVISTAS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--revistas
                      ivbi-card--simple-list
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Revistas
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="journalsData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-simple-list"
                    >
                      <div
                        v-for="(item, index) in journalsData"
                        :key="`journal-${item.label}`"
                        class="
                          ivbi-simple-list__row
                          ivbi-hover-info
                          ivbi-hover-info--rank
                        "
                        tabindex="0"
                        :data-tooltip="buildRankingTooltip(item, index, 'artículo', 'artículos')"
                        :aria-label="`${item.label}. ${buildRankingTooltip(item, index, 'artículo', 'artículos')}`"
                      >
                        <span class="ivbi-simple-list__index">
                          {{ index + 1 }}
                        </span>

                        <span
                          class="ivbi-simple-list__label"
                          :title="item.label"
                        >
                          {{ item.label }}
                        </span>

                        <strong class="ivbi-simple-list__count">
                          {{ countText(item.total, "artículo", "artículos") }}
                        </strong>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay revistas con artículos para esta selección.
                    </div>
                  </article>

                  <!-- PROYECTOS -->
                  <article
                    class="
                      ivbi-card
                      ivbi-card--proyectos
                      ivbi-card--simple-list
                    "
                  >
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <h3 class="ivbi-card__title">
                          Proyectos
                        </h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="projectsData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-simple-list ivbi-simple-list--projects"
                    >
                      <div
                        v-for="(item, index) in projectsData"
                        :key="`project-${item.label}`"
                        class="
                          ivbi-simple-list__row
                          ivbi-hover-info
                          ivbi-hover-info--rank
                        "
                        tabindex="0"
                        :data-tooltip="buildRankingTooltip(item, index)"
                        :aria-label="`${item.label}. ${buildRankingTooltip(item, index)}`"
                      >
                        <span class="ivbi-simple-list__index">
                          {{ index + 1 }}
                        </span>

                        <span
                          class="ivbi-simple-list__label"
                          :title="item.label"
                        >
                          {{ item.label }}
                        </span>

                        <strong class="ivbi-simple-list__count">
                          {{ publicationCountText(item.total) }}
                        </strong>
                      </div>
                    </TransitionGroup>

                    <div
                      v-else
                      class="ivbi-empty"
                    >
                      No hay proyectos con publicaciones para esta selección.
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
            Actualizando información…
          </div>

          <div
            v-else
            class="ivbi-empty ivbi-empty--state"
          >
            No encontramos publicaciones con las opciones seleccionadas.
          </div>
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
import { useUserStore } from "../../scripts/stores/userStore";
import PeriodRangePicker from "./PeriodRangePicker.vue";

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
    total_sedes: 0,
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

    top_sedes: {
      limite: 10,
      items: [],
    },

    top_facultades: {
      limite: 10,
      items: [],
    },

    top_carreras: {
      limite: 10,
      items: [],
    },

    areas: {
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
    sedes: [],
    facultades: [],
    carreras: [],
    anios: [],
    periodo: {
      anio_min: null,
      anio_max: null,
      mes_min: null,
      mes_max: null,
      mes_actual: null,
      ultimo_mes_con_datos: null,
      anios: [],
      meses: [],
      meses_con_datos: {},
      total_con_mes: 0,
      total_sin_mes: 0,
    },
    anio_base_mensual: null,
  },

  filtros_aplicados: {},
});

/* =========================================================
   ESTADO
========================================================= */

const userStore = useUserStore();

const isAdmin = computed(() =>
  Boolean(
    userStore?.isAdmin ||
    userStore?.esAdmin ||
    userStore?.user?.es_admin ||
    userStore?.user?.is_staff ||
    userStore?.user?.is_superuser
  )
);

const loading = ref(false);
const isRefreshing = ref(false);
const downloadingReportFormat = ref("");
const downloadingReport = computed(() =>
  Boolean(downloadingReportFormat.value)
);
const reportMenuOpen = ref(false);
const reportMenuRef = ref(null);

const downloadingReportLabel = computed(() => {
  if (
    downloadingReportFormat.value ===
    "institutional_excel"
  ) {
    return "Preparando Excel institucional…";
  }

  return downloadingReportFormat.value === "excel"
    ? "Preparando Excel…"
    : "Preparando PDF…";
});

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
    label: "Evolución",
  },
  {
    key: "rankings",
    label: "Destacados",
  },
]);



/* =========================================================
   FILTROS
========================================================= */

const globalFilters = reactive({
  sede_id: "",
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


function tooltipEdgeClass(
  index,
  total
) {
  const count = Number(total || 0);

  if (count <= 1) {
    return "ivbi-tooltip--center";
  }

  if (index <= 1) {
    return "ivbi-tooltip--left";
  }

  if (index >= count - 2) {
    return "ivbi-tooltip--right";
  }

  return "ivbi-tooltip--center";
}

function countText(
  value,
  singular = "publicación",
  plural = "publicaciones"
) {
  const total = Number(value || 0);

  return `${formatNumber(total)} ${
    total === 1
      ? singular
      : plural
  }`;
}

function lineChartX(index, total) {
  if (Number(total || 0) <= 1) {
    return 50;
  }

  return 4 +
    (Number(index || 0) /
      (Number(total) - 1)) *
      92;
}

function lineChartY(items, value) {
  const values = (items || []).map(
    (item) => Number(item?.value || 0)
  );

  const maxValue = Math.max(
    1,
    ...values
  );

  const ratio = Math.max(
    0,
    Math.min(
      1,
      Number(value || 0) /
        maxValue
    )
  );

  return 84 - ratio * 70;
}

function lineChartPolyline(items = []) {
  const total = items.length;

  return items
    .map(
      (item, index) =>
        `${lineChartX(index, total)},${lineChartY(items, item?.value)}`
    )
    .join(" ");
}

function lineChartAreaPoints(items = []) {
  if (!items.length) {
    return "";
  }

  const total = items.length;
  const firstX = lineChartX(0, total);
  const lastX = lineChartX(
    total - 1,
    total
  );

  return [
    `${firstX},88`,
    lineChartPolyline(items),
    `${lastX},88`,
  ]
    .filter(Boolean)
    .join(" ");
}

function lineChartPointStyle(
  items,
  item,
  index
) {
  return {
    left:
      `${lineChartX(index, items.length)}%`,
    top:
      `${lineChartY(items, item?.value)}%`,
  };
}

function publicationCountText(value) {
  return countText(
    value,
    "publicación",
    "publicaciones"
  );
}

function partPercentText(value, total) {
  const base = Number(total || 0);

  if (base <= 0) {
    return "";
  }

  return formatPercent(
    (Number(value || 0) / base) * 100
  );
}

function buildRankingTooltip(
  item,
  index,
  singular = "publicación",
  plural = "publicaciones"
) {
  const totalGeneral = Number(
    summary.value?.total_publicaciones || 0
  );

  const percentage =
    partPercentText(
      item?.total,
      totalGeneral
    );

  const position =
    index === 0
      ? "1.er lugar"
      : `${index + 1}.º lugar`;

  return [
    position,
    countText(
      item?.total,
      singular,
      plural
    ),
    percentage
      ? `${percentage} del total mostrado`
      : "",
  ]
    .filter(Boolean)
    .join("\n");
}

function buildAnnualTooltip(item, index) {
  const totalPeriodo =
    totalOf(publicacionesPorAnio.value);

  const current =
    Number(item?.value || 0);

  const previous =
    index > 0
      ? Number(
          publicacionesPorAnio.value[
            index - 1
          ]?.value || 0
        )
      : null;

  let comparison = "";

  if (previous !== null) {
    const difference =
      current - previous;

    if (difference > 0) {
      comparison =
        `${formatNumber(difference)} más que el año anterior`;
    } else if (difference < 0) {
      comparison =
        `${formatNumber(Math.abs(difference))} menos que el año anterior`;
    } else {
      comparison =
        "La misma cantidad que el año anterior";
    }
  }

  const percentage =
    partPercentText(
      current,
      totalPeriodo
    );

  return [
    String(item?.label || "Año"),
    publicationCountText(current),
    comparison,
    percentage
      ? `${percentage} del período mostrado`
      : "",
    "Haz clic para ver este año",
  ]
    .filter(Boolean)
    .join("\n");
}

function buildMonthlyTooltip(item, index) {
  const items =
    publicacionesPorMes.value?.items || [];

  const current =
    Number(item?.value || 0);

  const previous =
    index > 0
      ? Number(
          items[index - 1]?.value || 0
        )
      : null;

  let comparison = "";

  if (previous !== null) {
    const difference =
      current - previous;

    if (difference > 0) {
      comparison =
        `${formatNumber(difference)} más que el mes anterior`;
    } else if (difference < 0) {
      comparison =
        `${formatNumber(Math.abs(difference))} menos que el mes anterior`;
    } else {
      comparison =
        "La misma cantidad que el mes anterior";
    }
  }

  const year =
    publicacionesPorMes.value?.anio_base;

  const percentage =
    partPercentText(
      current,
      totalOf(items)
    );

  return [
    [item?.label, year]
      .filter(Boolean)
      .join(" "),
    publicationCountText(current),
    comparison,
    percentage
      ? `${percentage} del año mostrado`
      : "",
  ]
    .filter(Boolean)
    .join("\n");
}

function buildTypeYearTooltip(
  serie,
  catIndex,
  category
) {
  const value = Number(
    serie?.data?.[catIndex] || 0
  );

  return [
    String(category || ""),
    String(
      serie?.label ||
      "Tipo de publicación"
    ),
    publicationCountText(value),
  ]
    .filter(Boolean)
    .join("\n");
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
      sede_id:
        globalFilters.sede_id ||
        undefined,

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

function buildInstitutionalReportParams() {
  const dashboardParams = buildParams();

  const params = {
    sede_id:
      dashboardParams.sede_id ||
      undefined,

    facultad_id:
      dashboardParams.facultad_id ||
      undefined,

    carrera_id:
      dashboardParams.carrera_id ||
      undefined,

    tipo_codigo:
      dashboardParams.tipo_codigo ||
      undefined,
  };

  if (dashboardParams.anio) {
    params.periodo_modo = "anual";
    params.anio = dashboardParams.anio;
  } else if (
    dashboardParams.mes_desde ||
    dashboardParams.mes_hasta
  ) {
    params.periodo_modo = "personalizado";
    params.mes_desde =
      dashboardParams.mes_desde ||
      undefined;
    params.mes_hasta =
      dashboardParams.mes_hasta ||
      undefined;
  } else {
    params.periodo_modo = "historico";
  }

  return Object.fromEntries(
    Object.entries(params).filter(
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

function buildReportFileName(format = "pdf") {
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

  const sedePart =
    filtrosAplicados.value
      ?.sede_nombre
      ? sanitizeFileNamePart(
          filtrosAplicados.value
            .sede_nombre
        )
      : "todas-las-sedes";

  const facultadPart =
    filtrosAplicados.value
      ?.facultad_nombre
      ? sanitizeFileNamePart(
          filtrosAplicados.value
            .facultad_nombre
        )
      : "todas-las-facultades";

  const carreraPart =
    filtrosAplicados.value
      ?.carrera_nombre
      ? `-${sanitizeFileNamePart(
          filtrosAplicados.value
            .carrera_nombre
        )}`
      : "";

  const institutional =
    format === "institutional_excel";

  const prefix = institutional
    ? "reporte-produccion-institucional-detallado-"
    : "informe-produccion-cientifica-";

  const extension =
    format === "pdf"
      ? "pdf"
      : "xlsx";

  return (
    prefix +
    "sgpc-uleam-" +
    `${viewPart}-` +
    `${sedePart}-` +
    `${facultadPart}` +
    `${carreraPart}-` +
    `${datePart}.${extension}`
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

const TECHNICAL_ERROR_PATTERN =
  /(backend|endpoint|serializer|queryset|jwt|token|sql|postgres|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|request|response|\/api\/|http\s*\d{3})/i;

function sanitizeUserMessage(
  message,
  fallback
) {
  const text = String(message || "").trim();

  if (
    !text ||
    TECHNICAL_ERROR_PATTERN.test(text)
  ) {
    return fallback;
  }

  return text;
}

function toUserErrorMessage(
  error,
  fallback
) {
  const status = Number(
    error?.response?.status || 0
  );

  if (status === 401) {
    return "La sesión terminó. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "Su cuenta no puede consultar esta información.";
  }

  if (status === 429) {
    return "Se hicieron demasiados intentos en poco tiempo. Espere unos minutos y vuelva a intentarlo.";
  }

  return sanitizeUserMessage(
    extractApiErrorMessage(
      error?.response?.data,
      error?.message
    ),
    fallback
  );
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

function toggleReportMenu() {
  if (downloadingReport.value) {
    return;
  }

  reportMenuOpen.value =
    !reportMenuOpen.value;
}

function closeReportMenu() {
  reportMenuOpen.value = false;
}

function handleReportMenuOutside(event) {
  const root = reportMenuRef.value;

  if (
    !root ||
    root.contains(event.target)
  ) {
    return;
  }

  closeReportMenu();
}

async function downloadDashboardReport(
  format = "pdf"
) {
  if (downloadingReport.value) {
    return;
  }

  const normalizedFormat =
    format === "excel"
      ? "excel"
      : format === "institutional_excel"
        ? "institutional_excel"
        : "pdf";

  if (
    normalizedFormat ===
      "institutional_excel" &&
    !isAdmin.value
  ) {
    error.value =
      "Solo los administradores pueden descargar el Excel institucional detallado.";
    reportMenuOpen.value = false;
    return;
  }

  downloadingReportFormat.value =
    normalizedFormat;
  reportMenuOpen.value = false;
  error.value = "";

  const isExcel =
    normalizedFormat !== "pdf";

  const isInstitutionalExcel =
    normalizedFormat ===
    "institutional_excel";

  const endpoint =
    isInstitutionalExcel
      ? "/reportes/produccion/excel/"
      : isExcel
        ? "/dashboard/reporte/excel/"
        : "/dashboard/reporte/pdf/";

  const params =
    isInstitutionalExcel
      ? buildInstitutionalReportParams()
      : buildParams();

  try {
    const { data } =
      await api.get(
        endpoint,
        {
          params,
          responseType: "blob",
        }
      );

    const blob = new Blob(
      [data],
      {
        type: isExcel
          ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          : "application/pdf",
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
      buildReportFileName(
        normalizedFormat
      );

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

    const fallback =
      isInstitutionalExcel
        ? "No se pudo descargar el Excel institucional detallado. Vuelva a intentarlo."
        : isExcel
          ? "No se pudo descargar el archivo Excel. Vuelva a intentarlo."
          : "No se pudo descargar el informe PDF. Vuelva a intentarlo.";

    error.value =
      sanitizeUserMessage(
        blobMessage ||
          extractApiErrorMessage(
            err?.response?.data,
            err?.message
          ),
        fallback
      );
  } finally {
    downloadingReportFormat.value = "";
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
        "No pudimos cargar la información."
      );
    }

    response.value = data;

    await replayDashboardMotion();

    const sedesValidas =
      new Set(
        (
          data
            ?.filtros_disponibles
            ?.sedes || []
        ).map((item) =>
          String(item.id)
        )
      );

    if (
      globalFilters.sede_id &&
      !sedesValidas.has(
        String(
          globalFilters.sede_id
        )
      )
    ) {
      suppressAutoApply.value = true;
      globalFilters.sede_id = "";
      globalFilters.facultad_id = "";
      globalFilters.carrera_id = "";
      suppressAutoApply.value = false;
    }

    const facultadesValidas =
      new Set(
        (
          data
            ?.filtros_disponibles
            ?.facultades || []
        ).map((item) =>
          String(item.id)
        )
      );

    if (
      globalFilters.facultad_id &&
      !facultadesValidas.has(
        String(
          globalFilters.facultad_id
        )
      )
    ) {
      suppressAutoApply.value = true;
      globalFilters.facultad_id = "";
      globalFilters.carrera_id = "";
      suppressAutoApply.value = false;
    }

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
      toUserErrorMessage(
        err,
        "No se pudo cargar la información. Vuelva a intentarlo."
      );

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
      "El mes inicial no puede ser posterior al mes final.";

    return;
  }

  error.value = "";

  await loadDashboard();
}

/* =========================================================
   RESTABLECER FILTROS
========================================================= */

async function resetCurrentFilters() {
  suppressAutoApply.value = true;

  // Los filtros institucionales son comunes a las tres vistas.
  globalFilters.sede_id = "";
  globalFilters.facultad_id = "";
  globalFilters.carrera_id = "";

  // Solo se restablecen los filtros propios de la vista activa.
  const defaults = defaultViewFilters();
  const currentView = vistaActiva.value;

  Object.assign(
    viewFilters[currentView],
    defaults[currentView]
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

const periodoDisponible =
  computed(
    () =>
      filtrosDisponibles.value
        ?.periodo ||
      EMPTY_RESPONSE
        .filtros_disponibles
        .periodo
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


const annualRangeLabel =
  computed(() => {
    const items =
      publicacionesPorAnio.value ||
      [];

    if (!items.length) {
      return "";
    }

    const first =
      items[0]?.label;

    const last =
      items[
        items.length - 1
      ]?.label;

    if (!first && !last) {
      return "";
    }

    if (
      String(first) ===
      String(last)
    ) {
      return String(first || "");
    }

    return `${first || "—"}–${last || "—"}`;
  });

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

const topSedes =
  computed(
    () =>
      dashboards.value
        .top_sedes ||
      EMPTY_RESPONSE
        .dashboards
        .top_sedes
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

const areas =
  computed(
    () =>
      dashboards.value
        .areas ||
      EMPTY_RESPONSE
        .dashboards
        .areas
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
      areas.value
        .items.length > 0 ||
      topSedes.value
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

const tipoFiltroResumen =
  computed(() => {
    const codigo =
      filtrosAplicados.value
        ?.tipo_codigo;

    if (!codigo) {
      return "";
    }

    const tipo =
      tiposDisponiblesCanonicos.value
        .find(
          (item) =>
            String(item.codigo) ===
            String(codigo)
        );

    return (
      tipo?.nombre ||
      String(codigo)
    );
  });

const periodoResumen =
  computed(() => {
    const fechaDesde =
      filtrosAplicados.value
        ?.mes_desde;

    const fechaHasta =
      filtrosAplicados.value
        ?.mes_hasta;

    const desde =
      formatMonthYear(fechaDesde);

    const hasta =
      formatMonthYear(fechaHasta);

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

    return "Todo el período";
  });

const coberturaResumen =
  computed(() => {
    const partes = [
      filtrosAplicados.value
        ?.sede_nombre,
      filtrosAplicados.value
        ?.facultad_nombre,
      filtrosAplicados.value
        ?.carrera_nombre,
    ].filter(Boolean);

    return partes.length
      ? partes.join(" · ")
      : "Toda la institución";
  });

const dashboardMetaLine =
  computed(() =>
    [
      coberturaResumen.value,
      periodoResumen.value,
      tipoFiltroResumen.value,
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

const totalSedesTween =
  useTweenNumber(
    computed(
      () =>
        summary.value
          .total_sedes
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

const headlineKpis =
  computed(() => [
    {
      key: "publicaciones",
      label: "Publicaciones",
      value:
        totalPublicacionesTween.value,
      hint: periodoResumen.value,
      tooltip: [
        periodoResumen.value,
        coberturaResumen.value,
        tipoFiltroResumen.value,
      ]
        .filter(Boolean)
        .join("\n"),
      iconPath:
        "M6 3h8l4 4v14H6V3Zm8 0v5h5M9 13h6M9 17h6",
    },

    {
      key: "autores",
      label: "Autores",
      value:
        totalAutoresTween.value,
      hint: "Autores con publicaciones",
      tooltip:
        "Personas que aparecen como autoras en las publicaciones mostradas.",
      iconPath:
        "M8.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7-1a3 3 0 1 0 0-6M2.5 21c.6-4.2 3-6.5 6-6.5s5.4 2.3 6 6.5M14 14.8c3.6.4 5.7 2.4 6 6.2",
    },

    {
      key: "sedes",
      label: "Sedes",
      value:
        totalSedesTween.value,
      hint: "Sedes con publicaciones",
      tooltip:
        "Sedes que tienen al menos una publicación en esta selección.",
      iconPath:
        "M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Zm0-8.2a2.8 2.8 0 1 0 0-5.6 2.8 2.8 0 0 0 0 5.6Z",
    },

    {
      key: "facultades",
      label: "Facultades",
      value:
        totalFacultadesTween.value,
      hint:
        "Con publicaciones",
      tooltip:
        "Facultades que tienen al menos una publicación en esta selección.",
      iconPath:
        "M3 9 12 4l9 5M5 10v8M9 10v8M15 10v8M19 10v8M3 20h18",
    },

    {
      key: "carreras",
      label: "Carreras",
      value:
        totalCarrerasTween.value,
      hint: "Con publicaciones",
      tooltip:
        "Carreras que tienen al menos una publicación en esta selección.",
      iconPath:
        "M3 8l9-5 9 5-9 5-9-5Zm4 3v5c3 2 7 2 10 0v-5M21 8v6",
    },

    {
      key: "proyectos",
      label: "Proyectos",
      value:
        totalProyectosTween.value,
      hint: "Proyectos relacionados con publicaciones",
      tooltip:
        "Proyectos relacionados con las publicaciones mostradas.",
      iconPath:
        "M8 6V4h8v2M4 7h16v13H4V7Zm0 5h16M9 12v2h6v-2",
    },

  ]);

/* =========================================================
   RANKINGS
========================================================= */

const topSedesData =
  computed(() =>
    (
      topSedes.value.items ||
      []
    ).map((item) => ({
      label:
        item.sede ||
        item.label ||
        "Sede",

      total: Number(
        item.total || 0
      ),
    }))
  );

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

const areasData =
  computed(() =>
    (
      areas.value.items ||
      []
    ).map((item) => ({
      label:
        item.label ||
        item.area ||
        "Área",

      total: Number(
        item.total || 0
      ),
    }))
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
      .value.slice(0, 3)
  );

const topSedesResumen =
  computed(() =>
    topSedesData.value.slice(
      0,
      3
    )
  );

const topFacultadesResumen =
  computed(() =>
    topFacultadesData.value.slice(
      0,
      3
    )
  );

/* =========================================================
   WATCHERS
========================================================= */

watch(
  () =>
    globalFilters.sede_id,

  (newValue, oldValue) => {
    if (
      !hasMounted.value ||
      newValue === oldValue
    ) {
      return;
    }

    suppressAutoApply.value = true;

    globalFilters.facultad_id =
      "";

    globalFilters.carrera_id =
      "";

    suppressAutoApply.value = false;

    scheduleAutoApply();
  }
);

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
  document.addEventListener(
    "pointerdown",
    handleReportMenuOutside
  );

  await loadDashboard();

  hasMounted.value = true;
});

onBeforeUnmount(() => {
  clearAutoApplyTimer();

  document.removeEventListener(
    "pointerdown",
    handleReportMenuOutside
  );
});
</script>

<style src="./inicio-view.css"></style>
