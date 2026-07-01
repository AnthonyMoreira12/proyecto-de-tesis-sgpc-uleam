<template>
  <main class="ivbi-page">
    <section class="ivbi-shell">
      <section
        class="ivbi-board"
        :class="{
          'is-loading': loading,
          'is-refreshing': isRefreshing
        }"
        :aria-busy="loading || isRefreshing ? 'true' : 'false'"
      >
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
                v-for="n in 5"
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

        <div v-else class="ivbi-dashboard">
          <header class="ivbi-header">
            <div class="ivbi-header__titlebox">
              <span class="ivbi-header__kicker">SGPC ULEAM</span>
              <h1 class="ivbi-header__title">Panel analítico institucional</h1>
              <p class="ivbi-header__meta">{{ dashboardMetaLine }}</p>
            </div>

            <nav class="ivbi-segmented" aria-label="Vistas del dashboard">
              <button
                v-for="vista in vistaOpciones"
                :key="vista.key"
                type="button"
                class="ivbi-segmented__btn"
                :class="{ 'is-active': vistaActiva === vista.key }"
                :aria-pressed="vistaActiva === vista.key"
                @click="vistaActiva = vista.key"
              >
                {{ vista.label }}
              </button>
            </nav>

            <section class="ivbi-filterbar" aria-label="Filtros del dashboard">
              <div class="ivbi-filterbar__fields">
                <label class="ivbi-field">
                  <span>Facultad</span>
                  <select v-model="globalFilters.facultad_id">
                    <option value="">Todas</option>
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
                    <option value="">Todas</option>
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
                    <option value="">Todos</option>
                    <option
                      v-for="tipo in tiposDisponiblesCanonicos"
                      :key="`tipo-${vistaActiva}-${tipo.codigo}`"
                      :value="tipo.codigo"
                    >
                      {{ tipo.nombre }}
                    </option>
                  </select>
                </label>

                <template v-if="vistaActiva === 'resumen'">
                  <label class="ivbi-field">
                    <span>Desde</span>
                    <select v-model="viewFilters.resumen.anio_desde">
                      <option value="">Todos</option>
                      <option
                        v-for="anio in filtrosDisponibles.anios"
                        :key="`r-desde-${anio.value}`"
                        :value="String(anio.value)"
                      >
                        {{ anio.label }}
                      </option>
                    </select>
                  </label>

                  <label class="ivbi-field">
                    <span>Hasta</span>
                    <select v-model="viewFilters.resumen.anio_hasta">
                      <option value="">Todos</option>
                      <option
                        v-for="anio in filtrosDisponibles.anios"
                        :key="`r-hasta-${anio.value}`"
                        :value="String(anio.value)"
                      >
                        {{ anio.label }}
                      </option>
                    </select>
                  </label>
                </template>

                <template v-else-if="vistaActiva === 'tendencia'">
                  <label class="ivbi-field">
                    <span>Desde</span>
                    <select v-model="viewFilters.tendencia.anio_desde">
                      <option value="">Todos</option>
                      <option
                        v-for="anio in filtrosDisponibles.anios"
                        :key="`t-desde-${anio.value}`"
                        :value="String(anio.value)"
                      >
                        {{ anio.label }}
                      </option>
                    </select>
                  </label>

                  <label class="ivbi-field">
                    <span>Hasta</span>
                    <select v-model="viewFilters.tendencia.anio_hasta">
                      <option value="">Todos</option>
                      <option
                        v-for="anio in filtrosDisponibles.anios"
                        :key="`t-hasta-${anio.value}`"
                        :value="String(anio.value)"
                      >
                        {{ anio.label }}
                      </option>
                    </select>
                  </label>

                  <label class="ivbi-field">
                    <span>Año mensual</span>
                    <select v-model="viewFilters.tendencia.anio">
                      <option value="">{{ autoAnioMensualLabel }}</option>
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

                <template v-else>
                  <label class="ivbi-field">
                    <span>Top</span>
                    <select v-model="viewFilters.rankings.top">
                      <option value="5">Top 5</option>
                      <option value="10">Top 10</option>
                      <option value="15">Top 15</option>
                      <option value="20">Top 20</option>
                    </select>
                  </label>
                </template>
              </div>

              <div class="ivbi-filterbar__actions">
                <button
                  class="ivbi-btn ivbi-btn--primary"
                  type="button"
                  :disabled="loading || isRefreshing || downloadingReport"
                  @click="downloadDashboardReport"
                >
                  {{ downloadingReport ? "Generando…" : "Descargar reporte" }}
                </button>

                <button
                  class="ivbi-btn ivbi-btn--ghost"
                  type="button"
                  :disabled="loading || isRefreshing || downloadingReport"
                  @click="resetCurrentViewFilters"
                >
                  Limpiar filtros
                </button>

                <button
                  class="ivbi-btn ivbi-btn--ghost"
                  type="button"
                  :disabled="loading || isRefreshing || downloadingReport"
                  @click="resetAllFilters"
                >
                  Restablecer todo
                </button>
              </div>
            </section>
          </header>

          <div v-if="error" class="ivbi-alert ivbi-alert--error">
            {{ error }}
          </div>

          <template v-if="hasData">
            <Transition name="ivbi-view" mode="out-in">
              <section
                v-if="vistaActiva === 'resumen'"
                key="resumen"
                class="ivbi-view-shell"
              >
                <section class="ivbi-kpi-strip" aria-label="Indicadores principales">
                  <article
                    v-for="kpi in headlineKpis"
                    :key="kpi.key"
                    class="ivbi-kpi-card"
                  >
                    <span class="ivbi-kpi-card__label">{{ kpi.label }}</span>

                    <strong class="ivbi-kpi-card__value">
                      {{ formatNumber(kpi.value) }}
                    </strong>

                    <span class="ivbi-kpi-card__hint">{{ kpi.hint }}</span>
                  </article>
                </section>

                <section class="ivbi-summary-grid">
                  <article class="ivbi-card ivbi-card--distribution">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Distribución</span>
                        <h3 class="ivbi-card__title">Publicaciones por tipo</h3>
                      </div>
                    </header>

                    <div
                      v-if="publicacionesPorTipo.items.length"
                      class="ivbi-donut-panel"
                    >
                      <div
                        class="ivbi-donut"
                        :class="{ 'is-focused': Boolean(hoveredTypeCode) }"
                        :style="{ background: donutGradient(publicacionesPorTipo.items) }"
                      >
                        <div class="ivbi-donut__center">
                          <strong>{{ donutCenterValue }}</strong>
                          <span>{{ donutCenterLabel }}</span>
                          <small v-if="donutCenterHint">{{ donutCenterHint }}</small>
                        </div>
                      </div>

                      <div class="ivbi-legend">
                        <button
                          v-for="(item, index) in publicacionesPorTipo.items"
                          :key="`tipo-${item.tipo_codigo}`"
                          type="button"
                          class="ivbi-legend__item"
                          :class="{
                            'is-muted': hoveredTypeCode && hoveredTypeCode !== item.tipo_codigo,
                            'is-active': hoveredTypeCode === item.tipo_codigo,
                            'is-selected': isTypeSelected(item.tipo_codigo)
                          }"
                          @mouseenter="handleLegendEnter(item.tipo_codigo)"
                          @mouseleave="handleLegendLeave"
                          @focus="handleLegendEnter(item.tipo_codigo)"
                          @blur="handleLegendLeave"
                          @click="applyTypeFilter(item.tipo_codigo)"
                        >
                          <span
                            class="ivbi-legend__swatch"
                            :style="{ background: getTypeColor(item.tipo_codigo, index) }"
                          ></span>

                          <span class="ivbi-legend__text">
                            <span class="ivbi-legend__label">
                              {{ item.tipo_nombre }}
                            </span>

                            <span class="ivbi-legend__meta">
                              {{ formatNumber(item.total) }} ·
                              {{ formatPercent(item.porcentaje) }}
                            </span>
                          </span>
                        </button>
                      </div>
                    </div>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>

                    <div class="ivbi-mini-stats">
                      <article class="ivbi-mini-stat">
                        <span>Tipos activos</span>
                        <strong>{{ publicacionesPorTipo.items.length }}</strong>
                      </article>

                      <article class="ivbi-mini-stat">
                        <span>Dominante</span>
                        <strong>
                          {{ tipoDominante ? tipoDominante.tipo_codigo : "—" }}
                        </strong>
                      </article>
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--comparison">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Comparativa anual</span>
                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo por año
                        </h3>
                      </div>
                    </header>

                    <div
                      v-if="hasGroupedData(publicacionesPorTipoAnual)"
                      class="ivbi-grouped-wrap"
                    >
                      <div class="ivbi-grouped">
                        <div
                          v-for="(category, catIndex) in publicacionesPorTipoAnual.categorias"
                          :key="`grupo-${category}`"
                          class="ivbi-grouped__group"
                        >
                          <div class="ivbi-grouped__bars">
                            <div
                              v-for="(serie, serieIndex) in publicacionesPorTipoAnual.series"
                              :key="`${serie.codigo}-${category}`"
                              class="ivbi-grouped__barbox"
                            >
                              <div
                                class="ivbi-grouped__bar"
                                :style="{
                                  '--grouped-h': groupedBarHeight(
                                    publicacionesPorTipoAnual.series,
                                    serie.data?.[catIndex] || 0
                                  ),
                                  '--grouped-delay': `${serieIndex * 45 + catIndex * 20}ms`,
                                  background: getTypeColor(serie.codigo, serieIndex)
                                }"
                                :title="`${serie.label}: ${serie.data?.[catIndex] || 0}`"
                              ></div>
                            </div>
                          </div>

                          <span class="ivbi-grouped__label">{{ category }}</span>
                        </div>
                      </div>

                      <div class="ivbi-series-legend">
                        <span
                          v-for="(serie, index) in publicacionesPorTipoAnual.series"
                          :key="`legend-${serie.codigo}`"
                          class="ivbi-series-legend__item"
                        >
                          <i
                            class="ivbi-series-legend__swatch"
                            :style="{ background: getTypeColor(serie.codigo, index) }"
                          ></i>
                          {{ serie.label }}
                        </span>
                      </div>
                    </div>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--facultades">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Concentración</span>
                        <h3 class="ivbi-card__title">Top facultades</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topFacultadesResumen.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topFacultadesResumen"
                        :key="`top-facultad-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topFacultadesResumen, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--autores">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Liderazgo autoral</span>
                        <h3 class="ivbi-card__title">Top autores principales</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topAutoresPrincipalesResumen.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topAutoresPrincipalesResumen"
                        :key="`top-autor-principal-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topAutoresPrincipalesResumen, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>

              <section
                v-else-if="vistaActiva === 'tendencia'"
                key="tendencia"
                class="ivbi-view-shell"
              >
                <section class="ivbi-trend-grid">
                  <article class="ivbi-card ivbi-card--historica">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Serie histórica</span>
                        <h3 class="ivbi-card__title">Publicaciones por año</h3>
                      </div>

                      <span class="ivbi-card__total">
                        {{ formatNumber(totalOf(publicacionesPorAnio)) }}
                      </span>
                    </header>

                    <div
                      v-if="publicacionesPorAnio.length"
                      class="ivbi-vbars ivbi-vbars--tall"
                    >
                      <button
                        v-for="(item, index) in publicacionesPorAnio"
                        :key="`trend-anio-${item.label}`"
                        type="button"
                        class="ivbi-vbars__col is-interactive"
                        :class="{
                          'is-selected': String(viewFilters.tendencia.anio) === String(item.label)
                        }"
                        @click="applyYearFromTrend(item.label)"
                      >
                        <span class="ivbi-vbars__value">{{ item.value }}</span>

                        <div class="ivbi-vbars__track">
                          <div
                            class="ivbi-vbars__bar"
                            :style="{
                              '--bar-h': verticalBarHeight(publicacionesPorAnio, item.value),
                              '--bar-delay': `${index * 35}ms`,
                              background: paletteColor(index)
                            }"
                          ></div>
                        </div>

                        <span class="ivbi-vbars__label">{{ item.label }}</span>
                      </button>
                    </div>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--comparativa">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Comparativa</span>
                        <h3 class="ivbi-card__title">
                          Publicaciones por tipo por año
                        </h3>
                      </div>
                    </header>

                    <div
                      v-if="hasGroupedData(publicacionesPorTipoAnual)"
                      class="ivbi-grouped-wrap"
                    >
                      <div class="ivbi-grouped">
                        <div
                          v-for="(category, catIndex) in publicacionesPorTipoAnual.categorias"
                          :key="`trend-group-${category}`"
                          class="ivbi-grouped__group"
                        >
                          <div class="ivbi-grouped__bars">
                            <div
                              v-for="(serie, serieIndex) in publicacionesPorTipoAnual.series"
                              :key="`trend-${serie.codigo}-${category}`"
                              class="ivbi-grouped__barbox"
                            >
                              <div
                                class="ivbi-grouped__bar"
                                :style="{
                                  '--grouped-h': groupedBarHeight(
                                    publicacionesPorTipoAnual.series,
                                    serie.data?.[catIndex] || 0
                                  ),
                                  '--grouped-delay': `${serieIndex * 45 + catIndex * 20}ms`,
                                  background: getTypeColor(serie.codigo, serieIndex)
                                }"
                              ></div>
                            </div>
                          </div>

                          <span class="ivbi-grouped__label">{{ category }}</span>
                        </div>
                      </div>

                      <div class="ivbi-series-legend">
                        <span
                          v-for="(serie, index) in publicacionesPorTipoAnual.series"
                          :key="`trend-legend-${serie.codigo}`"
                          class="ivbi-series-legend__item"
                        >
                          <i
                            class="ivbi-series-legend__swatch"
                            :style="{ background: getTypeColor(serie.codigo, index) }"
                          ></i>
                          {{ serie.label }}
                        </span>
                      </div>
                    </div>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--mensual">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Detalle temporal</span>
                        <h3 class="ivbi-card__title">Publicaciones por mes</h3>
                      </div>

                      <span class="ivbi-card__total">
                        {{ publicacionesPorMes.anio_base || "Auto" }}
                      </span>
                    </header>

                    <div v-if="publicacionesPorMes.items.length" class="ivbi-vbars">
                      <div
                        v-for="(item, index) in publicacionesPorMes.items"
                        :key="`mes-${item.label}`"
                        class="ivbi-vbars__col"
                      >
                        <span class="ivbi-vbars__value">{{ item.value }}</span>

                        <div class="ivbi-vbars__track">
                          <div
                            class="ivbi-vbars__bar"
                            :style="{
                              '--bar-h': verticalBarHeight(publicacionesPorMes.items, item.value),
                              '--bar-delay': `${index * 35}ms`,
                              background: paletteColor(index)
                            }"
                          ></div>
                        </div>

                        <span class="ivbi-vbars__label">{{ item.label }}</span>
                      </div>
                    </div>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>

              <section
                v-else
                key="rankings"
                class="ivbi-view-shell"
              >
                <section class="ivbi-rankings-grid">
                  <article class="ivbi-card ivbi-card--facultades-rank">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Concentración</span>
                        <h3 class="ivbi-card__title">Top facultades</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topFacultadesData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topFacultadesData"
                        :key="`rank-facultad-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topFacultadesData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--carreras-rank">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Concentración</span>
                        <h3 class="ivbi-card__title">Top carreras</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topCarrerasData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topCarrerasData"
                        :key="`rank-carrera-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topCarrerasData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--autores-rank">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Liderazgo autoral</span>
                        <h3 class="ivbi-card__title">Top autores principales</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topAutoresPrincipalesData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topAutoresPrincipalesData"
                        :key="`rank-autor-principal-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topAutoresPrincipalesData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--coautores-rank">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Colaboración científica</span>
                        <h3 class="ivbi-card__title">Top coautores</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="topCoautoresData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in topCoautoresData"
                        :key="`rank-coautor-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(topCoautoresData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--revistas">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Soporte</span>
                        <h3 class="ivbi-card__title">Revistas con más artículos</h3>
                      </div>
                    </header>

                    <TransitionGroup
                      v-if="journalsData.length"
                      name="ivbi-list"
                      tag="div"
                      class="ivbi-rank"
                    >
                      <div
                        v-for="(item, index) in journalsData"
                        :key="`journal-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(journalsData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>

                  <article class="ivbi-card ivbi-card--proyectos">
                    <header class="ivbi-card__head">
                      <div class="ivbi-card__head-main">
                        <span class="ivbi-card__eyebrow">Soporte</span>
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
                        v-for="(item, index) in projectsData"
                        :key="`project-${item.label}`"
                        class="ivbi-rank__row"
                      >
                        <div class="ivbi-rank__meta">
                          <span class="ivbi-rank__index">{{ index + 1 }}</span>

                          <span class="ivbi-rank__label" :title="item.label">
                            {{ item.label }}
                          </span>
                        </div>

                        <div class="ivbi-rank__track">
                          <div
                            class="ivbi-rank__bar"
                            :style="{
                              '--rank-w': horizontalWidth(projectsData, item.total, 'total'),
                              '--rank-delay': `${index * 45}ms`,
                              background: rankingBarColor(index)
                            }"
                          >
                            <span>{{ item.total }}</span>
                          </div>
                        </div>
                      </div>
                    </TransitionGroup>

                    <div v-else class="ivbi-empty">
                      Sin datos.
                    </div>
                  </article>
                </section>
              </section>
            </Transition>
          </template>

          <div v-else-if="loading || isRefreshing" class="ivbi-empty ivbi-empty--state">
            Actualizando…
          </div>

          <div v-else class="ivbi-empty ivbi-empty--state">
            Sin datos para los filtros seleccionados.
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";
import api from "../../scripts/api/axios";

const CANONICAL_TYPES = Object.freeze([
  { code: "AAI", label: "Artículo de alto impacto" },
  { code: "AR", label: "Artículo regional" },
  { code: "PON", label: "Ponencia" },
  { code: "CAP", label: "Capítulo de libro" },
  { code: "LIB", label: "Libro" },
  { code: "OTRO", label: "Otro" },
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
  OTRO: "--ivbi-chart-6",
});

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
      total_con_fecha: 0,
      total_sin_fecha: 0,
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
    top_autores_principales: {
      limite: 10,
      rol_autoria: "principal",
      total_autores_activos: 0,
      items: [],
    },
    top_coautores: {
      limite: 10,
      rol_autoria: "coautor",
      total_autores_activos: 0,
      items: [],
    },
    top_autores: {
      limite: 10,
      rol_autoria: "principal",
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

const vistaOpciones = Object.freeze([
  { key: "resumen", label: "Resumen" },
  { key: "tendencia", label: "Tendencia" },
  { key: "rankings", label: "Rankings" },
]);

let autoApplyTimer = null;
let requestId = 0;

const globalFilters = reactive({
  facultad_id: "",
  carrera_id: "",
});

const defaultViewFilters = () => ({
  resumen: {
    tipo_codigo: "",
    anio_desde: "",
    anio_hasta: "",
  },
  tendencia: {
    tipo_codigo: "",
    anio_desde: "",
    anio_hasta: "",
    anio: "",
  },
  rankings: {
    tipo_codigo: "",
    top: "10",
  },
});

const viewFilters = reactive(defaultViewFilters());

const activeViewFilters = computed(() => viewFilters[vistaActiva.value] || {});

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

  if (!raw) return "OTRO";
  if (CANONICAL_TYPE_MAP[raw]) return raw;

  if (raw === "AAI" || raw.includes("ALTO IMPACTO")) return "AAI";
  if (raw === "AR" || raw.includes("REGIONAL")) return "AR";
  if (raw === "PON" || raw.includes("PONENCIA")) return "PON";
  if (raw === "CAP" || raw.includes("CAPITULO")) return "CAP";
  if (raw === "LIB" || raw === "LIBRO" || raw.includes("LIBRO")) return "LIB";
  if (raw === "OTRO" || raw === "OTROS") return "OTRO";

  return "OTRO";
}

function getCanonicalTypeLabel(input) {
  const code = normalizeCanonicalCode(input);
  return CANONICAL_TYPE_MAP[code]?.label || "Otro";
}

function normalizeTiposDisponibles(rawTipos = []) {
  const totals = new Map(CANONICAL_TYPES.map((item) => [item.code, 0]));

  for (const item of rawTipos) {
    const code = normalizeCanonicalCode(
      item?.codigo || item?.id || item?.nombre || item?.label
    );

    totals.set(code, totals.get(code) + Number(item?.total || 0));
  }

  return CANONICAL_TYPES.map((item) => ({
    id: item.code,
    codigo: item.code,
    nombre: item.label,
    total: totals.get(item.code) || 0,
  }));
}

function normalizePublicacionesPorTipoPayload(payload, selectedCode = null) {
  const rawItems = Array.isArray(payload?.items) ? payload.items : [];
  const totals = new Map(CANONICAL_TYPES.map((item) => [item.code, 0]));

  for (const item of rawItems) {
    const code = normalizeCanonicalCode(
      item?.tipo_codigo || item?.tipo_id || item?.tipo_nombre || item?.label
    );

    totals.set(code, totals.get(code) + Number(item?.total || 0));
  }

  const backendTotal = Number(payload?.total_publicaciones || 0);
  const visibleTotal = [...totals.values()].reduce((acc, value) => acc + value, 0);
  const total = Math.max(backendTotal, visibleTotal);

  const allItems = CANONICAL_TYPES.map((item) => {
    const totalItem = totals.get(item.code) || 0;

    return {
      tipo_id: item.code,
      tipo_codigo: item.code,
      tipo_nombre: item.label,
      total: totalItem,
      porcentaje: total > 0 ? Number(((totalItem / total) * 100).toFixed(2)) : 0,
    };
  });

  return {
    total_publicaciones: total,
    seleccionado: selectedCode
      ? allItems.find((item) => item.tipo_codigo === selectedCode) || null
      : null,
    items: allItems.filter((item) => Number(item.total || 0) > 0),
  };
}

function normalizeSeriesPayload(payload) {
  const categorias = Array.isArray(payload?.categorias) ? payload.categorias : [];
  const rawSeries = Array.isArray(payload?.series) ? payload.series : [];

  const grouped = new Map(
    CANONICAL_TYPES.map((item) => [item.code, Array(categorias.length).fill(0)])
  );

  for (const serie of rawSeries) {
    const code = normalizeCanonicalCode(
      serie?.codigo || serie?.id || serie?.label || serie?.nombre
    );

    const target = grouped.get(code);

    categorias.forEach((_, index) => {
      target[index] += Number(serie?.data?.[index] || 0);
    });
  }

  return {
    categorias,
    series: CANONICAL_TYPES.map((item) => ({
      id: item.code,
      codigo: item.code,
      label: item.label,
      data: grouped.get(item.code) || Array(categorias.length).fill(0),
    })).filter((serie) => serie.data.some((value) => Number(value || 0) > 0)),
    total_publicaciones: Number(payload?.total_publicaciones || 0),
  };
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("es-EC");
}

function formatPercent(value) {
  return `${Number(value || 0).toLocaleString("es-EC", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })}%`;
}

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

  return palette[index % palette.length];
}

function rankingBarColor(index) {
  if (index === 0) return "var(--ivbi-accent)";

  if (index === 1) {
    return "color-mix(in srgb, var(--ivbi-accent) 82%, white 18%)";
  }

  if (index === 2) {
    return "color-mix(in srgb, var(--ivbi-accent) 72%, white 28%)";
  }

  return "color-mix(in srgb, var(--ivbi-accent) 58%, white 42%)";
}

function getTypeColor(code, fallbackIndex = 0) {
  const normalized = normalizeCanonicalCode(code);
  const cssVar = TYPE_COLOR_VAR_MAP[normalized] || null;
  return cssVar ? `var(${cssVar})` : paletteColor(fallbackIndex);
}

function totalOf(items = []) {
  return items.reduce((acc, item) => {
    return acc + Number(item?.total || item?.value || 0);
  }, 0);
}

function donutGradient(items = []) {
  const total = totalOf(items);

  if (!total) {
    return "conic-gradient(var(--ivbi-line) 0deg 360deg)";
  }

  let start = 0;

  const segments = items.map((item, index) => {
    const value = Number(item.total || item.value || 0);
    const angle = (value / total) * 360;
    const end = start + angle;
    const segment = `${getTypeColor(item.tipo_codigo, index)} ${start}deg ${end}deg`;
    start = end;
    return segment;
  });

  return `conic-gradient(${segments.join(", ")})`;
}

function maxValue(items = [], valueKey = "value") {
  return Math.max(...items.map((item) => Number(item?.[valueKey] || 0)), 0);
}

function verticalBarHeight(items = [], value = 0, valueKey = "value") {
  const max = maxValue(items, valueKey);
  if (!max) return "0%";

  const percent = Math.max((Number(value || 0) / max) * 100, 4);
  return `${percent}%`;
}

function horizontalWidth(items = [], value = 0, valueKey = "value") {
  const max = maxValue(items, valueKey);
  if (!max) return "0%";

  const percent = Math.max((Number(value || 0) / max) * 100, 12);
  return `${percent}%`;
}

function hasGroupedData(grouped) {
  return Boolean(
    grouped &&
      Array.isArray(grouped.categorias) &&
      grouped.categorias.length &&
      Array.isArray(grouped.series) &&
      grouped.series.length
  );
}

function groupedMax(series = []) {
  const values = series.flatMap((item) => item.data || []);
  return Math.max(...values, 0);
}

function groupedBarHeight(series = [], value = 0) {
  const max = groupedMax(series);
  if (!max) return "0%";

  const percent = Math.max((Number(value || 0) / max) * 100, 4);
  return `${percent}%`;
}

function clearAutoApplyTimer() {
  if (autoApplyTimer) {
    clearTimeout(autoApplyTimer);
    autoApplyTimer = null;
  }
}

function scheduleAutoApply(delay = 220) {
  if (!hasMounted.value || suppressAutoApply.value) return;

  clearAutoApplyTimer();

  autoApplyTimer = setTimeout(() => {
    aplicarFiltros();
  }, delay);
}

function buildParams() {
  const currentViewFilters = viewFilters[vistaActiva.value] || {};

  return Object.fromEntries(
    Object.entries({
      facultad_id: globalFilters.facultad_id || undefined,
      carrera_id: globalFilters.carrera_id || undefined,
      tipo_codigo: currentViewFilters.tipo_codigo || undefined,
      anio_desde: currentViewFilters.anio_desde || undefined,
      anio_hasta: currentViewFilters.anio_hasta || undefined,
      anio: currentViewFilters.anio || undefined,
      top: currentViewFilters.top || undefined,
    }).filter(([, value]) => value !== undefined && value !== "")
  );
}

function sanitizeFileNamePart(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function buildReportFileName() {
  const now = new Date();

  const datePart = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
  ].join("-");

  const viewPart = sanitizeFileNamePart(vistaActiva.value || "dashboard");

  const facultadPart = filtrosAplicados.value?.facultad_nombre
    ? sanitizeFileNamePart(filtrosAplicados.value.facultad_nombre)
    : "institucional";

  return `reporte-dashboard-sgpc-uleam-${viewPart}-${facultadPart}-${datePart}.xlsx`;
}

async function readBlobErrorMessage(errorBlob) {
  try {
    if (!(errorBlob instanceof Blob)) return "";

    const text = await errorBlob.text();

    if (!text) return "";

    try {
      const json = JSON.parse(text);
      return json?.detail || json?.error || json?.message || text;
    } catch {
      return text;
    }
  } catch {
    return "";
  }
}

async function downloadDashboardReport() {
  if (downloadingReport.value) return;

  downloadingReport.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/dashboard/reporte/excel/", {
      params: buildParams(),
      responseType: "blob",
    });

    const blob = new Blob([data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = buildReportFileName();

    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    const blobMessage = await readBlobErrorMessage(err?.response?.data);

    error.value =
      blobMessage ||
      err?.response?.data?.detail ||
      err?.message ||
      "No fue posible descargar el reporte del dashboard.";
  } finally {
    downloadingReport.value = false;
  }
}

const requestParamsKey = computed(() => JSON.stringify(buildParams()));

async function loadDashboard() {
  const currentRequestId = ++requestId;

  if (hasLoadedOnce.value) {
    isRefreshing.value = true;
  } else {
    loading.value = true;
  }

  error.value = "";

  try {
    const { data } = await api.get("/dashboard/resumen/", {
      params: buildParams(),
    });

    if (currentRequestId !== requestId) return;

    if (!data?.ok) {
      throw new Error("La API no devolvió una respuesta válida.");
    }

    response.value = data;

    const carrerasValidas = new Set(
      (data?.filtros_disponibles?.carreras || []).map((item) => String(item.id))
    );

    if (
      globalFilters.carrera_id &&
      !carrerasValidas.has(String(globalFilters.carrera_id))
    ) {
      suppressAutoApply.value = true;
      globalFilters.carrera_id = "";
      suppressAutoApply.value = false;
    }
  } catch (err) {
    if (currentRequestId !== requestId) return;

    error.value =
      err?.response?.data?.detail ||
      err?.message ||
      "No fue posible cargar el panel analítico.";

    response.value = EMPTY_RESPONSE;
  } finally {
    if (currentRequestId === requestId) {
      loading.value = false;
      isRefreshing.value = false;
      hasLoadedOnce.value = true;
    }
  }
}

async function aplicarFiltros() {
  const current = viewFilters[vistaActiva.value] || {};

  if (
    current.anio_desde &&
    current.anio_hasta &&
    Number(current.anio_desde) > Number(current.anio_hasta)
  ) {
    error.value = "El rango anual es inválido: 'Desde' no puede ser mayor que 'Hasta'.";
    return;
  }

  error.value = "";
  await loadDashboard();
}

async function resetCurrentViewFilters() {
  suppressAutoApply.value = true;

  if (vistaActiva.value === "resumen") {
    viewFilters.resumen.tipo_codigo = "";
    viewFilters.resumen.anio_desde = "";
    viewFilters.resumen.anio_hasta = "";
  } else if (vistaActiva.value === "tendencia") {
    viewFilters.tendencia.tipo_codigo = "";
    viewFilters.tendencia.anio_desde = "";
    viewFilters.tendencia.anio_hasta = "";
    viewFilters.tendencia.anio = "";
  } else {
    viewFilters.rankings.tipo_codigo = "";
    viewFilters.rankings.top = "10";
  }

  hoveredTypeCode.value = "";
  suppressAutoApply.value = false;
  clearAutoApplyTimer();
  await loadDashboard();
}

async function resetAllFilters() {
  suppressAutoApply.value = true;

  globalFilters.facultad_id = "";
  globalFilters.carrera_id = "";

  const defaults = defaultViewFilters();

  viewFilters.resumen.tipo_codigo = defaults.resumen.tipo_codigo;
  viewFilters.resumen.anio_desde = defaults.resumen.anio_desde;
  viewFilters.resumen.anio_hasta = defaults.resumen.anio_hasta;

  viewFilters.tendencia.tipo_codigo = defaults.tendencia.tipo_codigo;
  viewFilters.tendencia.anio_desde = defaults.tendencia.anio_desde;
  viewFilters.tendencia.anio_hasta = defaults.tendencia.anio_hasta;
  viewFilters.tendencia.anio = defaults.tendencia.anio;

  viewFilters.rankings.tipo_codigo = defaults.rankings.tipo_codigo;
  viewFilters.rankings.top = defaults.rankings.top;

  hoveredTypeCode.value = "";
  suppressAutoApply.value = false;
  clearAutoApplyTimer();
  await loadDashboard();
}

function handleLegendEnter(code) {
  hoveredTypeCode.value = normalizeCanonicalCode(code);
}

function handleLegendLeave() {
  hoveredTypeCode.value = "";
}

function isTypeSelected(code) {
  return String(activeViewFilters.value?.tipo_codigo || "") === String(code || "");
}

function applyTypeFilter(code) {
  const normalized = normalizeCanonicalCode(code);
  const current = String(activeViewFilters.value?.tipo_codigo || "");

  suppressAutoApply.value = true;
  activeViewFilters.value.tipo_codigo = current === normalized ? "" : normalized;
  suppressAutoApply.value = false;

  scheduleAutoApply(80);
}

function applyYearFromTrend(label) {
  const value = String(label || "").trim();

  if (!/^\d{4}$/.test(value)) return;

  suppressAutoApply.value = true;
  viewFilters.tendencia.anio =
    String(viewFilters.tendencia.anio) === value ? "" : value;
  suppressAutoApply.value = false;

  scheduleAutoApply(80);
}

function useTweenNumber(source, duration = 700) {
  const display = ref(Number(source.value || 0));
  let frame = 0;

  const stop = watch(
    source,
    (newValue) => {
      if (typeof window === "undefined") {
        display.value = Number(newValue || 0);
        return;
      }

      cancelAnimationFrame(frame);

      const startValue = Number(display.value || 0);
      const endValue = Number(newValue || 0);
      const startTime = performance.now();

      const tick = (now) => {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);

        display.value = Math.round(
          startValue + (endValue - startValue) * eased
        );

        if (progress < 1) {
          frame = requestAnimationFrame(tick);
        }
      };

      frame = requestAnimationFrame(tick);
    },
    { immediate: true }
  );

  onBeforeUnmount(() => {
    stop();

    if (typeof window !== "undefined") {
      cancelAnimationFrame(frame);
    }
  });

  return display;
}

const summary = computed(() => response.value?.summary || EMPTY_RESPONSE.summary);

const dashboards = computed(
  () => response.value?.dashboards || EMPTY_RESPONSE.dashboards
);

const filtrosDisponibles = computed(
  () => response.value?.filtros_disponibles || EMPTY_RESPONSE.filtros_disponibles
);

const filtrosAplicados = computed(() => {
  const raw = response.value?.filtros_aplicados || {};
  const tipoCodigo = raw?.tipo_codigo ? normalizeCanonicalCode(raw.tipo_codigo) : null;

  return {
    ...raw,
    tipo_codigo: tipoCodigo,
    tipo_nombre: raw?.tipo_nombre || (tipoCodigo ? getCanonicalTypeLabel(tipoCodigo) : null),
  };
});

const tiposDisponiblesCanonicos = computed(() =>
  normalizeTiposDisponibles(filtrosDisponibles.value?.tipos || [])
);

const carrerasFiltradas = computed(() => {
  const all = filtrosDisponibles.value?.carreras || [];

  if (!globalFilters.facultad_id) return all;

  return all.filter(
    (career) => String(career.facultad_id) === String(globalFilters.facultad_id)
  );
});

const publicacionesPorAnio = computed(
  () => dashboards.value.publicaciones_por_anio || []
);

const publicacionesPorMes = computed(
  () =>
    dashboards.value.publicaciones_por_mes ||
    EMPTY_RESPONSE.dashboards.publicaciones_por_mes
);

const publicacionesPorTipo = computed(() =>
  normalizePublicacionesPorTipoPayload(
    dashboards.value.publicaciones_por_tipo,
    filtrosAplicados.value?.tipo_codigo || null
  )
);

const publicacionesPorTipoAnual = computed(() =>
  normalizeSeriesPayload(dashboards.value.publicaciones_por_tipo_anual)
);

const topFacultades = computed(
  () => dashboards.value.top_facultades || EMPTY_RESPONSE.dashboards.top_facultades
);

const topCarreras = computed(
  () => dashboards.value.top_carreras || EMPTY_RESPONSE.dashboards.top_carreras
);

const topAutoresPrincipales = computed(
  () =>
    dashboards.value.top_autores_principales ||
    dashboards.value.top_autores ||
    EMPTY_RESPONSE.dashboards.top_autores_principales
);

const topCoautores = computed(
  () => dashboards.value.top_coautores || EMPTY_RESPONSE.dashboards.top_coautores
);

const journals = computed(
  () => dashboards.value.journals || EMPTY_RESPONSE.dashboards.journals
);

const projects = computed(
  () => dashboards.value.projects || EMPTY_RESPONSE.dashboards.projects
);

const anioBaseMensual = computed(
  () => filtrosDisponibles.value?.anio_base_mensual || null
);

const autoAnioMensualLabel = computed(() =>
  anioBaseMensual.value ? `Auto (${anioBaseMensual.value})` : "Auto"
);

const hasData = computed(() => {
  return (
    Number(summary.value.total_publicaciones || 0) > 0 ||
    publicacionesPorAnio.value.length > 0 ||
    publicacionesPorTipo.value.items.length > 0 ||
    topAutoresPrincipales.value.items.length > 0 ||
    topCoautores.value.items.length > 0
  );
});

const tipoDominante = computed(() => {
  const items = [...publicacionesPorTipo.value.items];

  if (!items.length) return null;

  items.sort((a, b) => Number(b.total || 0) - Number(a.total || 0));
  return items[0] || null;
});

const donutFocusItem = computed(() => {
  if (!hoveredTypeCode.value) return null;

  return (
    publicacionesPorTipo.value.items.find(
      (item) => item.tipo_codigo === hoveredTypeCode.value
    ) || null
  );
});

const donutCenterValue = computed(() => {
  if (donutFocusItem.value) {
    return formatNumber(donutFocusItem.value.total);
  }

  return formatNumber(totalOf(publicacionesPorTipo.value.items));
});

const donutCenterLabel = computed(() => {
  if (donutFocusItem.value) {
    return donutFocusItem.value.tipo_codigo;
  }

  return "Total";
});

const donutCenterHint = computed(() => {
  if (donutFocusItem.value) {
    return donutFocusItem.value.tipo_nombre;
  }

  return "Publicaciones";
});

const tipoDominanteResumen = computed(() => {
  if (!tipoDominante.value) return "—";

  return `${tipoDominante.value.tipo_nombre} · ${formatPercent(
    tipoDominante.value.porcentaje
  )}`;
});

const periodoResumen = computed(() => {
  const desde = filtrosAplicados.value?.anio_desde;
  const hasta = filtrosAplicados.value?.anio_hasta;

  if (desde && hasta) return `${desde} — ${hasta}`;
  if (desde) return `Desde ${desde}`;
  if (hasta) return `Hasta ${hasta}`;

  const categorias = publicacionesPorAnio.value || [];

  if (categorias.length >= 2) {
    return `${categorias[0].label} — ${categorias[categorias.length - 1].label}`;
  }

  if (categorias.length === 1) return categorias[0].label;

  return "Histórico";
});

const coberturaResumen = computed(() => {
  if (filtrosAplicados.value?.carrera_nombre) {
    return filtrosAplicados.value.carrera_nombre;
  }

  if (filtrosAplicados.value?.facultad_nombre) {
    return filtrosAplicados.value.facultad_nombre;
  }

  return "Toda la institución";
});

const dashboardMetaLine = computed(() =>
  [coberturaResumen.value, periodoResumen.value, tipoDominanteResumen.value]
    .filter(Boolean)
    .join(" · ")
);

const totalPublicacionesTween = useTweenNumber(
  computed(() => summary.value.total_publicaciones)
);

const totalAutoresTween = useTweenNumber(
  computed(() => summary.value.total_autores)
);

const totalFacultadesTween = useTweenNumber(
  computed(() => summary.value.total_facultades)
);

const totalCarrerasTween = useTweenNumber(
  computed(() => summary.value.total_carreras)
);

const totalProyectosTween = useTweenNumber(
  computed(() => summary.value.total_proyectos)
);

const totalAltoImpactoTween = useTweenNumber(
  computed(() => summary.value.articulos_alto_impacto)
);

const headlineKpis = computed(() => [
  {
    key: "publicaciones",
    label: "Publicaciones",
    value: totalPublicacionesTween.value,
    hint: periodoResumen.value,
  },
  {
    key: "autores",
    label: "Autores",
    value: totalAutoresTween.value,
    hint: "Autores vinculados",
  },
  {
    key: "facultades",
    label: "Facultades",
    value: totalFacultadesTween.value,
    hint: "Cobertura institucional",
  },
  {
    key: "carreras",
    label: "Carreras",
    value: totalCarrerasTween.value,
    hint: "Oferta académica",
  },
  {
    key: "proyectos",
    label: "Proyectos",
    value: totalProyectosTween.value,
    hint: "Proyectos asociados",
  },
  {
    key: "alto-impacto",
    label: "Alto impacto",
    value: totalAltoImpactoTween.value,
    hint: "Artículos indexados",
  },
]);

const topFacultadesData = computed(() =>
  (topFacultades.value.items || []).map((item) => ({
    label: item.facultad,
    total: Number(item.total || 0),
  }))
);

const topCarrerasData = computed(() =>
  (topCarreras.value.items || []).map((item) => ({
    label: item.carrera,
    total: Number(item.total || 0),
  }))
);

function normalizeAuthorRankingItems(items = [], fallbackLabel = "Autor") {
  return (items || []).map((item) => ({
    label: item.label || item.autor || fallbackLabel,
    total: Number(item.total_publicaciones || item.total || 0),
  }));
}

const topAutoresPrincipalesData = computed(() =>
  normalizeAuthorRankingItems(
    topAutoresPrincipales.value.items || [],
    "Autor principal"
  )
);

const topCoautoresData = computed(() =>
  normalizeAuthorRankingItems(topCoautores.value.items || [], "Coautor")
);

const journalsData = computed(() =>
  (journals.value.items || []).map((item) => ({
    label: item.label,
    total: Number(item.total || 0),
  }))
);

const projectsData = computed(() =>
  (projects.value.items || []).map((item) => ({
    label: item.label,
    total: Number(item.total || 0),
  }))
);

const topAutoresPrincipalesResumen = computed(() =>
  topAutoresPrincipalesData.value.slice(0, 5)
);

const topFacultadesResumen = computed(() => topFacultadesData.value.slice(0, 5));

watch(
  () => globalFilters.facultad_id,
  (newValue, oldValue) => {
    if (!hasMounted.value || newValue === oldValue) return;

    if (globalFilters.carrera_id) {
      suppressAutoApply.value = true;
      globalFilters.carrera_id = "";
      suppressAutoApply.value = false;
    }

    scheduleAutoApply();
  }
);

watch(
  () => vistaActiva.value,
  () => {
    if (!hasMounted.value) return;

    hoveredTypeCode.value = "";
    scheduleAutoApply(120);
  }
);

watch(requestParamsKey, (newValue, oldValue) => {
  if (!hasMounted.value || suppressAutoApply.value || newValue === oldValue) return;

  scheduleAutoApply();
});

onMounted(async () => {
  await loadDashboard();
  hasMounted.value = true;
});

onBeforeUnmount(() => {
  clearAutoApplyTimer();
});
</script>

<style src="./inicio-view.css"></style>