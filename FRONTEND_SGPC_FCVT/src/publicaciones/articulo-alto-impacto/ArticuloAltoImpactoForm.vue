<template>
  <div class="sgpc-form-page sgpc-form-page--alto-impacto">
    <div class="sgpc-form-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->

      <header
        class="sgpc-form-header sgpc-publication-header page-stage page-header"
      >
        <div class="sgpc-form-heading">
          <div class="sgpc-publication-header__topline">
            <p class="sgpc-form-kicker">
              {{ pageKicker }}
            </p>

            <div
              class="sgpc-publication-header__chips"
              aria-label="Clasificación del formulario"
            >
              <span class="sgpc-publication-chip">
                Publicación científica
              </span>

              <span
                class="sgpc-publication-chip sgpc-publication-chip--accent"
              >
                Alto impacto
              </span>
            </div>
          </div>

          <h1 class="sgpc-form-title">
            {{ pageTitle }}
          </h1>

          <p class="sgpc-form-subtitle">
            {{ pageSubtitle }}
          </p>

          <p
            v-if="draftInfo"
            class="sgpc-banner-info"
            role="status"
            aria-live="polite"
          >
            {{ draftInfo }}
          </p>
        </div>

        <div
          class="sgpc-publication-header__mark"
          aria-hidden="true"
        >
          <div class="sgpc-publication-header__mark-icon">
            <svg
              viewBox="0 0 24 24"
              width="30"
              height="30"
            >
              <path
                fill="currentColor"
                d="M7 3h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm1 4v2h8V7H8Zm0 4v2h8v-2H8Zm0 4v2h5v-2H8Z"
              />
            </svg>
          </div>

          <span>AAI</span>
          <small>
            Artículo de alto impacto
          </small>
        </div>
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->

      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar un artículo de alto impacto"
        enctype="multipart/form-data"
        @submit.prevent="registrarArticulo"
      >
        <main class="sgpc-form-main page-stage page-main">
          <!-- =================================================
               CONTEXTO ADMINISTRATIVO
          ================================================== -->

          <section
            v-if="isAdminDelegado"
            id="sec-contexto-admin"
            class="sgpc-card sgpc-card--admin-context"
            data-section="ADMIN"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Contexto del registro
                </h2>

                <p class="sgpc-card-desc">
                  Este registro se guardará para el usuario seleccionado.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div
                id="ai-admin-context-anchor"
                tabindex="-1"
              ></div>

              <div class="sgpc-admin-context">
                <article class="sgpc-admin-context__item">
                  <span class="sgpc-admin-context__label">
                    Usuario objetivo
                  </span>

                  <strong class="sgpc-admin-context__value">
                    {{ adminDisplayUsuario }}
                  </strong>
                </article>

                <article
                  v-if="showAutorObjetivo"
                  class="sgpc-admin-context__item"
                >
                  <span class="sgpc-admin-context__label">
                    Autor objetivo
                  </span>

                  <strong class="sgpc-admin-context__value">
                    {{ adminDisplayAutor }}
                  </strong>
                </article>
              </div>

              <p class="sgpc-hint">
                El autor objetivo se agregará automáticamente a la autoría del
                registro.
              </p>

              <p
                v-if="fieldErrors.admin_context"
                id="ai-admin-context-error"
                class="sgpc-hint sgpc-hint-error"
                role="alert"
              >
                {{ fieldErrors.admin_context }}
              </p>
            </div>
          </section>

          <!-- =================================================
               DATOS GENERALES
          ================================================== -->

          <section
            id="sec-datos-generales"
            class="sgpc-card"
            data-section="01"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Datos generales
                </h2>

                <p class="sgpc-card-desc">
                  Clasificación institucional del registro.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <DatosGenerales
                v-model="form.datos_generales"
                :errors="fieldErrors"
                :hide-ubicacion="true"
                :proyecto-opcional="true"
                proyecto-label="Proyecto de investigación"
                area-label="Área del conocimiento (UNESCO)"
                subarea-label="Subárea del conocimiento (UNESCO)"
              />
            </div>
          </section>

          <!-- =================================================
               ORIGEN
          ================================================== -->

          <section
            id="sec-origen"
            class="sgpc-card"
            data-section="02"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Origen de la publicación
                </h2>

                <p class="sgpc-card-desc">
                  Relación académica del artículo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-origen_tipo"
                  >
                    Origen de la publicación
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <select
                    id="ai-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    :aria-invalid="hasFieldError('origen_tipo')"
                    :aria-describedby="errorDescriptionId('origen_tipo')"
                    required
                  >
                    <option
                      disabled
                      value=""
                    >
                      Seleccione...
                    </option>

                    <option value="ninguno">
                      Ninguno
                    </option>

                    <option value="tic">
                      Trabajo de integración curricular
                    </option>

                    <option value="maestria">
                      Tesis de maestría
                    </option>

                    <option value="doctoral">
                      Tesis doctoral
                    </option>

                    <option value="otro">
                      Otro
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.origen_tipo"
                    :id="fieldErrorId('origen_tipo')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-origen_grado"
                  >
                    {{
                      form.origen_tipo === "otro"
                        ? "Especifique el origen"
                        : "Grado / programa"
                    }}

                    <span
                      v-if="['tic', 'otro'].includes(form.origen_tipo)"
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    :disabled="!['tic', 'otro'].includes(form.origen_tipo)"
                    :required="['tic', 'otro'].includes(form.origen_tipo)"
                    :aria-invalid="hasFieldError('origen_grado')"
                    :aria-describedby="originGradeDescriptionIds"
                    :placeholder="
                      form.origen_tipo === 'otro'
                        ? 'Ej. Proyecto de investigación institucional'
                        : 'Ej. Ingeniería en TI / Ingeniería de Software / ...'
                    "
                  />

                  <p
                    id="ai-origen-grado-help"
                    class="sgpc-hint"
                  >
                    {{
                      form.origen_tipo === "otro"
                        ? "Escriba el origen específico de la publicación."
                        : form.origen_tipo === "tic"
                          ? "Indique el grado o programa relacionado con el trabajo de integración curricular."
                          : "Seleccione Trabajo de integración curricular u Otro para habilitar este campo."
                    }}
                  </p>

                  <p
                    v-if="fieldErrors.origen_grado"
                    :id="fieldErrorId('origen_grado')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.origen_grado }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <!-- =================================================
               ARTÍCULO
          ================================================== -->

          <section
            id="sec-articulo"
            class="sgpc-card"
            data-section="03"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Información del artículo
                </h2>

                <p class="sgpc-card-desc">
                  Datos básicos de la publicación.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="ai-nombre_articulo"
                  >
                    Título del artículo
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-nombre_articulo"
                    v-model.trim="form.nombre_articulo"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    :aria-invalid="hasFieldError('nombre_articulo')"
                    :aria-describedby="errorDescriptionId('nombre_articulo')"
                    required
                  />

                  <p
                    v-if="fieldErrors.nombre_articulo"
                    :id="fieldErrorId('nombre_articulo')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_articulo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-fecha_publicacion"
                  >
                    Fecha de publicación
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    :aria-invalid="hasFieldError('fecha_publicacion')"
                    :aria-describedby="errorDescriptionId('fecha_publicacion')"
                    required
                  />

                  <p
                    v-if="fieldErrors.fecha_publicacion"
                    :id="fieldErrorId('fecha_publicacion')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-tipo_articulo"
                  >
                    Clasificación
                  </label>

                  <input
                    id="ai-tipo_articulo"
                    class="sgpc-input"
                    type="text"
                    value="Alto impacto"
                    disabled
                  />
                </div>
              </div>
            </div>
          </section>

          <!-- =================================================
               REVISTA
          ================================================== -->

          <section
            id="sec-revista"
            class="sgpc-card"
            data-section="04"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Revista e indicadores
                </h2>

                <p class="sgpc-card-desc">
                  Información editorial, enlaces e indicadores de alto impacto.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <!-- Revista -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-nombre_revista"
                  >
                    Nombre de la revista
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-nombre_revista"
                    v-model.trim="form.nombre_revista"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    :aria-invalid="hasFieldError('nombre_revista')"
                    :aria-describedby="errorDescriptionId('nombre_revista')"
                    required
                  />

                  <p
                    v-if="fieldErrors.nombre_revista"
                    :id="fieldErrorId('nombre_revista')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_revista }}
                  </p>
                </div>

                <!-- Número -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-numero_revista"
                  >
                    Número de la revista
                  </label>

                  <input
                    id="ai-numero_revista"
                    v-model.number="form.numero_revista"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    :aria-invalid="hasFieldError('numero_revista')"
                    :aria-describedby="errorDescriptionId('numero_revista')"
                    placeholder="Ej. 12"
                  />

                  <p
                    v-if="fieldErrors.numero_revista"
                    :id="fieldErrorId('numero_revista')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.numero_revista }}
                  </p>
                </div>

                <!-- DOI -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-codigo_doi"
                  >
                    Código DOI
                  </label>

                  <input
                    id="ai-codigo_doi"
                    v-model.trim="form.codigo_doi"
                    class="sgpc-input"
                    type="text"
                    maxlength="150"
                    :aria-invalid="hasFieldError('codigo_doi')"
                    :aria-describedby="errorDescriptionId('codigo_doi')"
                    placeholder="Ej. 10.1234/xxxxx"
                  />

                  <p
                    v-if="fieldErrors.codigo_doi"
                    :id="fieldErrorId('codigo_doi')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_doi }}
                  </p>
                </div>

                <!-- ISSN -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-codigo_issn"
                  >
                    Código ISSN
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-codigo_issn"
                    v-model.trim="form.codigo_issn"
                    class="sgpc-input"
                    type="text"
                    maxlength="100"
                    :aria-invalid="hasFieldError('codigo_issn')"
                    :aria-describedby="errorDescriptionId('codigo_issn')"
                    placeholder="Ej. 1234-5678"
                    required
                  />

                  <p
                    v-if="fieldErrors.codigo_issn"
                    :id="fieldErrorId('codigo_issn')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_issn }}
                  </p>
                </div>

                <!-- Link revista -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-link_revista"
                  >
                    Link de la revista
                  </label>

                  <input
                    id="ai-link_revista"
                    v-model.trim="form.link_revista"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    :aria-invalid="hasFieldError('link_revista')"
                    :aria-describedby="errorDescriptionId('link_revista')"
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_revista"
                    :id="fieldErrorId('link_revista')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_revista }}
                  </p>
                </div>

                <!-- Link publicación -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-link_publicacion"
                  >
                    Link de la publicación
                  </label>

                  <input
                    id="ai-link_publicacion"
                    v-model.trim="form.link_publicacion"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    :aria-invalid="hasFieldError('link_publicacion')"
                    :aria-describedby="errorDescriptionId('link_publicacion')"
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_publicacion"
                    :id="fieldErrorId('link_publicacion')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_publicacion }}
                  </p>
                </div>

                <!-- Factor -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-factor_impacto"
                  >
                    Factor de impacto
                  </label>

                  <select
                    id="ai-factor_impacto"
                    v-model="form.factor_impacto"
                    class="sgpc-input"
                    :aria-invalid="hasFieldError('factor_impacto')"
                    :aria-describedby="errorDescriptionId('factor_impacto')"
                  >
                    <option value="">
                      No aplica / no disponible
                    </option>

                    <option value="sjr">
                      SJR (Scimago Journal Rank)
                    </option>

                    <option value="jcr">
                      JCR (Journal Citation Reports)
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.factor_impacto"
                    :id="fieldErrorId('factor_impacto')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.factor_impacto }}
                  </p>
                </div>

                <!-- Cuartil -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-cuartil"
                  >
                    Cuartil
                  </label>

                  <select
                    id="ai-cuartil"
                    v-model="form.cuartil"
                    class="sgpc-input"
                    :aria-invalid="hasFieldError('cuartil')"
                    :aria-describedby="errorDescriptionId('cuartil')"
                  >
                    <option value="">
                      Seleccione...
                    </option>

                    <option value="q1">
                      Q1
                    </option>

                    <option value="q2">
                      Q2
                    </option>

                    <option value="q3">
                      Q3
                    </option>

                    <option value="q4">
                      Q4
                    </option>

                    <option value="sin_cuartil">
                      Sin cuartil
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.cuartil"
                    :id="fieldErrorId('cuartil')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.cuartil }}
                  </p>
                </div>

                <!-- SJR -->

                <div
                  v-if="form.factor_impacto === 'sjr'"
                  class="sgpc-field sgpc-col-span-12"
                >
                  <label
                    class="sgpc-label"
                    for="ai-sjr"
                  >
                    SJR (valor)

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-sjr"
                    v-model.trim="form.sjr"
                    class="sgpc-input"
                    type="text"
                    inputmode="decimal"
                    maxlength="100"
                    :aria-invalid="hasFieldError('sjr')"
                    :aria-describedby="errorDescriptionId('sjr')"
                    placeholder="Ej. 0.45"
                    required
                  />

                  <p
                    v-if="fieldErrors.sjr"
                    :id="fieldErrorId('sjr')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.sjr }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <!-- =================================================
               AUTORES
          ================================================== -->

          <section
            id="sec-autores"
            class="sgpc-card"
            data-section="05"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Autores
                </h2>

                <p class="sgpc-card-desc">
                  Seleccione autores y defina su jerarquía y orden.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div
                id="ai-autores-anchor"
                tabindex="-1"
              ></div>

              <AutoresSelector
                v-model="form.autores"
                :error="fieldErrors.autores"
              />
            </div>
          </section>

          <!-- =================================================
               ADJUNTOS
          ================================================== -->

          <section
            id="sec-adjuntos"
            class="sgpc-card"
            data-section="06"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Adjuntos
                </h2>

                <p class="sgpc-card-desc">
                  Adjunte la carta de aceptación y otros soportes relacionados.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="ai-archivo-input"
                title="Agregar archivos PDF"
                description="Puede cargar hasta 2 PDF complementarios."
                helper-text="Formato permitido: PDF. Máximo 2 archivos y 3 MB por archivo."
                :multiple="true"
                :max-files="2"
                :uses-primary-slot="false"
                :attachment-max-size-mb="3"
              />
            </div>
          </section>

          <!-- =================================================
               MENSAJE
          ================================================== -->

          <div
            v-if="mensaje"
            :class="[
              'sgpc-alert',
              `is-${mensajeTipo}`,
            ]"
            :role="mensajeTipo === 'error' ? 'alert' : 'status'"
            :aria-live="mensajeTipo === 'error' ? 'assertive' : 'polite'"
          >
            {{ mensaje }}
          </div>
        </main>

        <!-- ===================================================
             RESUMEN
        ==================================================== -->

        <aside class="sgpc-form-aside page-stage page-aside">
          <div class="sgpc-summary-card">
            <div class="sgpc-summary-head">
              <div
                class="sgpc-summary-icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                >
                  <path
                    fill="currentColor"
                    d="M4 4h16v16H4V4Zm2 2v12h12V6H6Zm2 2h8v2H8V8Zm0 4h5v2H8v-2Z"
                  />
                </svg>
              </div>

              <div>
                <p class="sgpc-summary-kicker">
                  Seguimiento
                </p>

                <h2>
                  Resumen del registro
                </h2>
              </div>
            </div>

            <div class="sgpc-progress">
              <div class="sgpc-progress-row">
                <span>
                  Completitud
                </span>

                <strong>
                  {{ progressPercent }}%
                </strong>
              </div>

              <div
                class="sgpc-progress-bar"
                role="progressbar"
                aria-label="Completitud del formulario"
                aria-valuemin="0"
                aria-valuemax="100"
                :aria-valuenow="progressPercent"
              >
                <span
                  :style="{
                    width: `${progressPercent}%`,
                  }"
                ></span>
              </div>

              <p class="sgpc-progress-caption">
                {{ completedRequiredCount }} de
                {{ totalRequiredCount }}
                secciones obligatorias completas
              </p>
            </div>

            <div class="sgpc-status-list">
              <button
                v-for="item in summarySections"
                :key="item.key"
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': item.done,
                }"
                @click="goTo(item.target)"
              >
                <div>
                  <strong>
                    {{ item.label }}
                  </strong>

                  <span>
                    {{ item.detail }}
                  </span>
                </div>

                <em>
                  {{ item.status }}
                </em>
              </button>
            </div>

            <div class="sgpc-summary-actions">
              <button
                class="sgpc-btn-primary sgpc-publication-submit"
                type="submit"
                :disabled="loading"
                :aria-busy="loading ? 'true' : 'false'"
              >
                <span
                  v-if="loading"
                  class="sgpc-spinner"
                  aria-hidden="true"
                ></span>

                <svg
                  v-else
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  aria-hidden="true"
                >
                  <path
                    fill="currentColor"
                    d="M5 4h12l2 2v14H5V4Zm2 2v12h10V7.2L15.8 6H7Zm2 2h6v4H9V8Zm0 6h6v2H9v-2Z"
                  />
                </svg>

                <span>
                  {{
                    loading
                      ? submitLoadingText
                      : submitText
                  }}
                </span>
              </button>

              <button
                type="button"
                class="sgpc-btn"
                :disabled="loading"
                title="Elimina únicamente el borrador guardado en este navegador"
                @click="clearDraft"
              >
                Limpiar borrador
              </button>
            </div>
          </div>
        </aside>
      </form>
    </div>
  </div>
</template>

<script>
import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";
import api from "../../scripts/api/axios";

import {
  appendArchivosToFormData,
  restoreDraftArchivos,
  serializeDraftArchivos,
} from "../../scripts/utils/adjuntosPdf";


const BASE_STORAGE_KEY =
  "sgpc-articulo-alto-impacto-draft:v23";

const STANDARD_CREATE_ENDPOINT =
  "/publicaciones/articulos/crear/";

const ADMIN_CREATE_ENDPOINT =
  "/admin/publicaciones/articulos/crear/";


const FIELD_LIMITS = Object.freeze({
  origen_grado: 120,
  nombre_articulo: 255,
  codigo_doi: 150,
  codigo_issn: 100,
  nombre_revista: 255,
  link_revista: 500,
  link_publicacion: 500,
  sjr: 100,
});


const ERROR_KEY_ALIASES = Object.freeze({
  usuario_objetivo_id: "admin_context",
  usuario_id: "admin_context",
  autor_objetivo_id: "admin_context",
  autor_id: "admin_context",
  usuario_creador: "admin_context",

  meta: "archivos",
  archivos_meta: "archivos",
  files: "archivos",
  archivos: "archivos",
  adjuntos: "archivos",
  archivo: "archivos",
  archivo_pdf: "archivos",

  non_field_errors: "general",
});


const FIELD_LABELS = Object.freeze({
  admin_context: "Usuario objetivo",
  general: "Validación general",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  tipo_codigo: "Tipo de artículo",
  nombre_articulo: "Título del artículo",
  fecha_publicacion: "Fecha de publicación",
  codigo_doi: "DOI",
  codigo_issn: "ISSN",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_publicacion: "Link de la publicación",
  link_revista: "Link de la revista",
  factor_impacto: "Factor de impacto",
  cuartil: "Cuartil",
  sjr: "SJR",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa u otro origen",
  autores: "Autores",
  archivos: "Adjuntos PDF",
});


const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "tipo_codigo",
  "origen_tipo",
  "origen_grado",
  "nombre_articulo",
  "fecha_publicacion",
  "nombre_revista",
  "numero_revista",
  "codigo_issn",
  "codigo_doi",
  "link_revista",
  "link_publicacion",
  "factor_impacto",
  "cuartil",
  "sjr",
  "autores",
  "archivos",
  "general",
]);


function createEmptyForm() {
  return {
    datos_generales: {
      facultad: null,
      carrera: null,
      proyecto: null,
      area: null,
      subarea: null,
      pais: null,
      ciudad: null,
    },

    origen_tipo: "",
    origen_grado: "",

    nombre_articulo: "",
    fecha_publicacion: "",

    codigo_doi: "",
    codigo_issn: "",
    nombre_revista: "",
    numero_revista: null,
    link_revista: "",
    link_publicacion: "",

    factor_impacto: "",
    cuartil: "",
    sjr: "",

    autores: [],
    archivos: [],
  };
}


function asText(value) {
  if (Array.isArray(value)) {
    return value
      .map(asText)
      .filter(Boolean)
      .join(", ");
  }

  if (
    value !== null &&
    value !== undefined &&
    typeof value === "object"
  ) {
    return Object.values(value)
      .map(asText)
      .filter(Boolean)
      .join(", ");
  }

  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  return String(value).trim();
}


function normalizeErrorKey(key) {
  return (
    ERROR_KEY_ALIASES[key] ||
    key
  );
}


function normalizeDrfErrors(data) {
  if (!data) {
    return {
      fields: {},
      message:
        "No se pudo guardar. Verifique los campos.",
    };
  }

  const rawErrors =
    data?.errors &&
    typeof data.errors === "object"
      ? data.errors
      : typeof data === "object" &&
          data !== null
        ? data
        : null;

  if (
    rawErrors &&
    typeof rawErrors === "object"
  ) {
    const fields = {};
    let first = null;

    Object.entries(
      rawErrors
    ).forEach(
      ([key, value]) => {
        if (key === "detail") {
          return;
        }

        const normalizedKey =
          normalizeErrorKey(key);

        const message =
          asText(value);

        if (!message) {
          return;
        }

        fields[
          normalizedKey
        ] = message;

        if (!first) {
          first =
            normalizedKey;
        }
      }
    );

    if (
      Object.keys(fields).length
    ) {
      let message =
        "No se pudo registrar. Revise los campos marcados.";

      if (
        fields.admin_context
      ) {
        message =
          fields.admin_context;
      } else if (
        fields.general
      ) {
        message =
          fields.general;
      } else if (
        fields.autores
      ) {
        message =
          "Revise la sección de Autores: debe existir al menos un autor y el orden debe ser válido.";
      } else if (
        fields.archivos
      ) {
        message =
          "Revise la sección de Adjuntos PDF.";
      } else if (first) {
        const label =
          FIELD_LABELS[first] ||
          first;

        message =
          `${label}: ${fields[first]}`;
      }

      return {
        fields,
        message,
      };
    }
  }

  if (
    typeof data?.detail ===
    "string"
  ) {
    return {
      fields: {},
      message: data.detail,
    };
  }

  return {
    fields: {},
    message:
      "No se pudo guardar. Verifique los campos.",
  };
}


function firstErrorField(fields) {
  for (
    const key
    of ERROR_FIELD_ORDER
  ) {
    if (
      fields?.[key]
    ) {
      return key;
    }
  }

  return (
    Object.keys(
      fields || {}
    )[0] ||
    null
  );
}


function normalizeCuartil(value) {
  const raw = String(
    value ?? ""
  )
    .trim()
    .toLowerCase();

  if (!raw) {
    return "";
  }

  if (
    [
      "sin cuartil",
      "sin-cuartil",
      "sin_cuartil",
    ].includes(raw)
  ) {
    return "sin_cuartil";
  }

  return raw;
}


function appendIfPresent(
  formData,
  key,
  value
) {
  if (
    value === null ||
    value === "" ||
    value === undefined
  ) {
    return;
  }

  if (
    typeof value === "number" &&
    !Number.isFinite(value)
  ) {
    return;
  }

  formData.append(
    key,
    String(value)
  );
}


function exceedsLength(
  value,
  maxLength
) {
  return (
    String(value || "")
      .trim()
      .length >
    maxLength
  );
}


export default {
  name:
    "ArticuloAltoImpactoRegistro",

  components: {
    DatosGenerales,
    AutoresSelector,
    AdjuntosPdfUploader,
  },

  data() {
    return {
      loading: false,

      mensaje: "",
      mensajeTipo: "",

      fieldErrors: {},

      draftInfo: "",
      draftTimer: null,
      draftEnabled: true,

      adminContext: {
        usuarioId: null,
        autorId: null,
        usuarioNombre: "",
        autorNombre: "",
      },

      form: createEmptyForm(),
    };
  },

  computed: {
    // ========================================================
    // CONTEXTO ADMINISTRATIVO
    // ========================================================

    isAdminDelegado() {
      const path = String(
        this.$route?.path ||
        ""
      );

      return Boolean(
        this.$route
          ?.meta
          ?.delegatedPublication ||

        path.startsWith(
          "/admin/publicaciones/usuario/"
        )
      );
    },

    storageKey() {
      if (
        !this.isAdminDelegado
      ) {
        return (
          `${BASE_STORAGE_KEY}:self`
        );
      }

      const usuarioId =
        this.adminContext
          .usuarioId ||

        Number(
          this.$route
            ?.params
            ?.usuarioId ||
          0
        ) ||

        "sin-usuario";

      return (
        `${BASE_STORAGE_KEY}:admin:${usuarioId}`
      );
    },

    adminDisplayUsuario() {
      return (
        this.adminContext
          .usuarioNombre ||

        `ID ${
          this.adminContext
            .usuarioId ||
          "—"
        }`
      );
    },

    adminDisplayAutor() {
      if (
        this.adminContext
          .autorNombre
      ) {
        return (
          this.adminContext
            .autorNombre
        );
      }

      if (
        this.adminContext
          .autorId
      ) {
        return (
          `ID ${
            this.adminContext
              .autorId
          }`
        );
      }

      return (
        "Se resolverá automáticamente"
      );
    },

    showAutorObjetivo() {
      if (
        !this.isAdminDelegado
      ) {
        return false;
      }

      /*
       * Usuario.id y Autor.id pertenecen a entidades
       * diferentes y nunca deben compararse entre sí.
       *
       * Si tenemos información explícita del Autor,
       * simplemente la mostramos.
       */
      return Boolean(
        this.adminContext
          .autorId ||

        String(
          this.adminContext
            .autorNombre ||
          ""
        ).trim()
      );
    },

    // ========================================================
    // CABECERA
    // ========================================================

    pageKicker() {
      return (
        this.isAdminDelegado
          ? "Administración · Artículos"
          : "Artículos"
      );
    },

    pageTitle() {
      return (
        "Registrar Artículo de Alto Impacto"
      );
    },

    pageSubtitle() {
      if (
        this.isAdminDelegado
      ) {
        return (
          "Registre datos bibliográficos, editoriales, indicadores de alto impacto, autoría y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios."
        );
      }

      return (
        "Registre datos bibliográficos, editoriales, indicadores de alto impacto, autoría y adjuntos del artículo. Los campos marcados con * son obligatorios."
      );
    },

    submitText() {
      return (
        "Registrar artículo"
      );
    },

    submitLoadingText() {
      return "Guardando...";
    },

    createEndpoint() {
      return (
        this.isAdminDelegado
          ? ADMIN_CREATE_ENDPOINT
          : STANDARD_CREATE_ENDPOINT
      );
    },

    // ========================================================
    // PROGRESO
    // ========================================================

    hasRequiredContext() {
      const datos =
        this.form
          .datos_generales ||
        {};

      return Boolean(
        datos.facultad &&
        datos.carrera &&
        datos.area &&
        datos.subarea
      );
    },

    hasRequiredOrigin() {
      if (
        !this.form
          .origen_tipo
      ) {
        return false;
      }

      if (
        ["tic", "otro"].includes(this.form
          .origen_tipo)
      ) {
        return Boolean(
          String(
            this.form
              .origen_grado ||
            ""
          ).trim()
        );
      }

      return true;
    },

    hasRequiredArticle() {
      return Boolean(
        String(
          this.form
            .nombre_articulo ||
          ""
        ).trim() &&

        this.form
          .fecha_publicacion
      );
    },

    hasRequiredJournal() {
      if (
        !String(
          this.form
            .nombre_revista ||
          ""
        ).trim()
      ) {
        return false;
      }

      if (
        !String(
          this.form
            .codigo_issn ||
          ""
        ).trim()
      ) {
        return false;
      }

      if (
        this.form
          .factor_impacto ===
          "sjr" &&

        !String(
          this.form.sjr ||
          ""
        ).trim()
      ) {
        return false;
      }

      return true;
    },

    hasRequiredAuthors() {
      return (
        Array.isArray(
          this.form.autores
        ) &&

        this.form
          .autores
          .length >
          0
      );
    },

    hasAdjuntos() {
      return (
        Array.isArray(
          this.form.archivos
        ) &&

        this.form
          .archivos
          .length >
          0
      );
    },

    summarySections() {
      return [
        {
          key: "datos",
          target:
            "sec-datos-generales",
          label:
            "Datos generales",
          done:
            this.hasRequiredContext,
          required: true,
          detail:
            this.hasRequiredContext
              ? "Completo"
              : "Campos pendientes",
          status:
            this.hasRequiredContext
              ? "Completo"
              : "Pendiente",
        },

        {
          key: "origen",
          target:
            "sec-origen",
          label: "Origen",
          done:
            this.hasRequiredOrigin,
          required: true,
          detail:
            this.hasRequiredOrigin
              ? "Completo"
              : "Seleccione origen",
          status:
            this.hasRequiredOrigin
              ? "Completo"
              : "Pendiente",
        },

        {
          key: "articulo",
          target:
            "sec-articulo",
          label: "Artículo",
          done:
            this.hasRequiredArticle,
          required: true,
          detail:
            this.hasRequiredArticle
              ? "Completo"
              : "Título o fecha pendientes",
          status:
            this.hasRequiredArticle
              ? "Completo"
              : "Pendiente",
        },

        {
          key: "revista",
          target:
            "sec-revista",
          label: "Revista",
          done:
            this.hasRequiredJournal,
          required: true,
          detail:
            this.hasRequiredJournal
              ? "Completo"
              : "Revista o ISSN pendientes",
          status:
            this.hasRequiredJournal
              ? "Completo"
              : "Pendiente",
        },

        {
          key: "autores",
          target:
            "sec-autores",
          label: "Autores",
          done:
            this.hasRequiredAuthors,
          required: true,
          detail:
            this.hasRequiredAuthors
              ? `${
                  this.form
                    .autores
                    .length
                } autor(es)`
              : "Sin autores",
          status:
            this.hasRequiredAuthors
              ? "Completo"
              : "Pendiente",
        },

        {
          key: "adjuntos",
          target:
            "sec-adjuntos",
          label: "Adjuntos",
          done:
            this.hasAdjuntos,
          required: false,
          detail:
            this.hasAdjuntos
              ? `${
                  this.form
                    .archivos
                    .length
                } archivo(s)`
              : "Opcional",
          status:
            this.hasAdjuntos
              ? "Completo"
              : "Opcional",
        },
      ];
    },

    completedRequiredCount() {
      return (
        this.summarySections
          .filter(
            (section) =>
              section.required &&
              section.done
          )
          .length
      );
    },

    totalRequiredCount() {
      return (
        this.summarySections
          .filter(
            (section) =>
              section.required
          )
          .length
      );
    },

    progressPercent() {
      if (
        !this.totalRequiredCount
      ) {
        return 0;
      }

      return Math.round(
        (
          this.completedRequiredCount /
          this.totalRequiredCount
        ) *
        100
      );
    },

    originGradeDescriptionIds() {
      const ids = [
        "ai-origen-grado-help",
      ];

      if (
        this.fieldErrors
          .origen_grado
      ) {
        ids.push(
          this.fieldErrorId(
            "origen_grado"
          )
        );
      }

      return ids.join(" ");
    },
  },

  // ==========================================================
  // CICLO DE VIDA
  // ==========================================================

  created() {
    this.hydrateAdminContextFromRoute();
    this.loadDraft();
  },

  beforeUnmount() {
    clearTimeout(
      this.draftTimer
    );
  },

  // ==========================================================
  // WATCHERS
  // ==========================================================

  watch: {
    form: {
      deep: true,

      handler(value) {
        if (
          !this.draftEnabled
        ) {
          return;
        }

        clearTimeout(
          this.draftTimer
        );

        this.draftTimer =
          setTimeout(
            () => {
              this.saveDraft(
                value
              );
            },
            300
          );
      },
    },

    "$route.fullPath"() {
      this.handleRouteContextChange();
    },

    "form.origen_tipo"(
      value
    ) {
      if (
        !["tic", "otro"].includes(value)
      ) {
        this.form
          .origen_grado =
          "";
      }
    },

    "form.factor_impacto"(
      value
    ) {
      if (
        value !== "sjr"
      ) {
        this.form.sjr =
          "";
      }
    },

    "form.cuartil"(
      value
    ) {
      const normalized =
        normalizeCuartil(
          value
        );

      if (
        normalized !==
        value
      ) {
        this.form.cuartil =
          normalized;
      }
    },
  },

  methods: {
    // ========================================================
    // ERRORES
    // ========================================================

    fieldErrorId(key) {
      return (
        `ai-${key}-error`
      );
    },

    hasFieldError(key) {
      return Boolean(
        this.fieldErrors?.[
          key
        ]
      );
    },

    errorDescriptionId(
      key
    ) {
      return (
        this.hasFieldError(
          key
        )
          ? this.fieldErrorId(
              key
            )
          : undefined
      );
    },

    clearErrors() {
      this.fieldErrors =
        {};

      this.mensaje =
        "";

      this.mensajeTipo =
        "";
    },

    // ========================================================
    // CONTEXTO DE RUTA
    // ========================================================

    handleRouteContextChange() {
      this.hydrateAdminContextFromRoute();

      this.disableDraftTemporarily();

      this.resetForm();

      this.loadDraft();
    },

    hydrateAdminContextFromRoute() {
      const query =
        this.$route?.query ||
        {};

      const params =
        this.$route?.params ||
        {};

      const usuarioId =
        Number(
          params.usuarioId ||

          query.usuario_id ||

          query.usuarioId ||

          query.user_id ||

          0
        );

      const autorId =
        Number(
          params.autorId ||

          query.autor_id ||

          query.autorId ||

          0
        );

      this.adminContext = {
        usuarioId:
          Number.isFinite(
            usuarioId
          ) &&
          usuarioId > 0
            ? usuarioId
            : null,

        autorId:
          Number.isFinite(
            autorId
          ) &&
          autorId > 0
            ? autorId
            : null,

        usuarioNombre:
          String(
            query.usuario_nombre ||

            query.usuarioNombre ||

            query.user_name ||

            ""
          ).trim(),

        autorNombre:
          String(
            query.autor_nombre ||

            query.autorNombre ||

            query.author_name ||

            ""
          ).trim(),
      };
    },

    validateAdminContext() {
      if (
        !this.isAdminDelegado
      ) {
        return null;
      }

      if (
        !this.adminContext
          .usuarioId
      ) {
        return (
          "Debe llegar al formulario con un usuario objetivo válido."
        );
      }

      return null;
    },

    // ========================================================
    // BORRADOR
    // ========================================================

    saveDraft(value) {
      const payload = {
        form: {
          datos_generales: {
            ...(
              value
                .datos_generales ||
              {}
            ),

            pais: null,
            ciudad: null,
          },

          origen_tipo:
            value.origen_tipo,

          origen_grado:
            value.origen_grado,

          nombre_articulo:
            value.nombre_articulo,

          fecha_publicacion:
            value.fecha_publicacion,

          codigo_doi:
            value.codigo_doi,

          codigo_issn:
            value.codigo_issn,

          nombre_revista:
            value.nombre_revista,

          numero_revista:
            value.numero_revista,

          link_revista:
            value.link_revista,

          link_publicacion:
            value.link_publicacion,

          factor_impacto:
            value.factor_impacto,

          cuartil:
            normalizeCuartil(
              value.cuartil
            ),

          sjr:
            value.sjr,

          autores:
            value.autores,

          archivos:
            serializeDraftArchivos(
              value.archivos
            ),
        },

        updatedAt:
          new Date()
            .toISOString(),
      };

      try {
        localStorage.setItem(
          this.storageKey,
          JSON.stringify(
            payload
          )
        );
      } catch (error) {
        console.warn(
          "No se pudo guardar el borrador.",
          error
        );
      }
    },

    loadDraft() {
      let raw = null;

      try {
        raw =
          localStorage.getItem(
            this.storageKey
          );
      } catch (error) {
        console.warn(
          "No se pudo leer el borrador.",
          error
        );

        return;
      }

      if (!raw) {
        return;
      }

      try {
        const parsed =
          JSON.parse(raw);

        const recovered =
          parsed.form ||
          parsed;

        const base =
          createEmptyForm();

        this.disableDraftTemporarily();

        this.form = {
          ...base,
          ...recovered,

          datos_generales: {
            ...base
              .datos_generales,

            ...(
              recovered
                ?.datos_generales ||
              {}
            ),

            pais: null,
            ciudad: null,
          },

          cuartil:
            normalizeCuartil(
              recovered
                ?.cuartil
            ),

          autores:
            Array.isArray(
              recovered
                ?.autores
            )
              ? recovered
                  .autores
              : [],

          archivos:
            restoreDraftArchivos(
              recovered
                ?.archivos
            ),
        };

        if (
          parsed?.updatedAt
        ) {
          const date =
            new Date(
              parsed.updatedAt
            );

          this.draftInfo =
            Number.isNaN(
              date.getTime()
            )
              ? "Se recuperó un borrador guardado."
              : `Se recuperó un borrador guardado (${date.toLocaleString()}).`;
        } else {
          this.draftInfo =
            "Se recuperó un borrador guardado.";
        }
      } catch (error) {
        console.warn(
          "El borrador está dañado y se ignorará.",
          error
        );
      }
    },

    disableDraftTemporarily() {
      this.draftEnabled =
        false;

      this.$nextTick(
        () => {
          this.draftEnabled =
            true;
        }
      );
    },

    clearDraft() {
      this.disableDraftTemporarily();

      try {
        localStorage.removeItem(
          this.storageKey
        );
      } catch (error) {
        console.warn(
          "No se pudo eliminar el borrador.",
          error
        );
      }

      this.resetForm();

      this.mensaje =
        "Borrador eliminado.";

      this.mensajeTipo =
        "info";
    },

    // ========================================================
    // NAVEGACIÓN / FOCUS
    // ========================================================

    goTo(id) {
      const element =
        document.getElementById(
          id
        );

      element?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    },

    focusField(key) {
      const localIdMap = {
        admin_context:
          "ai-admin-context-anchor",

        nombre_articulo:
          "ai-nombre_articulo",

        fecha_publicacion:
          "ai-fecha_publicacion",

        codigo_doi:
          "ai-codigo_doi",

        codigo_issn:
          "ai-codigo_issn",

        nombre_revista:
          "ai-nombre_revista",

        numero_revista:
          "ai-numero_revista",

        link_revista:
          "ai-link_revista",

        link_publicacion:
          "ai-link_publicacion",

        factor_impacto:
          "ai-factor_impacto",

        cuartil:
          "ai-cuartil",

        sjr:
          "ai-sjr",

        origen_tipo:
          "ai-origen_tipo",

        origen_grado:
          "ai-origen_grado",

        autores:
          "ai-autores-anchor",

        archivos:
          "ai-archivo-input",
      };

      const element =
        document.getElementById(
          `dg-${key}`
        ) ||

        document.getElementById(
          localIdMap[key] ||
          ""
        );

      if (!element) {
        return;
      }

      element.scrollIntoView?.({
        behavior: "smooth",
        block: "center",
      });

      if (
        ![
          "autores",
          "archivos",
          "admin_context",
        ].includes(key) &&

        typeof element.focus ===
          "function"
      ) {
        window.setTimeout(
          () => {
            element.focus({
              preventScroll:
                true,
            });
          },
          280
        );
      }
    },

    // ========================================================
    // AUTORES
    // ========================================================

    buildAutoresPayload() {
      const raw =
        Array.isArray(
          this.form.autores
        )
          ? this.form.autores
          : [];

      return raw
        .map(
          (
            autor,
            index
          ) => {
            const id =
              Number(
                autor
                  ?.autor_id ??

                autor
                  ?.id ??

                autor
                  ?.autor
                  ?.id
              );

            if (
              !Number.isFinite(
                id
              ) ||
              id <= 0
            ) {
              return null;
            }

            const orden =
              index + 1;

            return {
              autor_id: id,

              orden,

              rol_autoria:
                orden === 1
                  ? "principal"
                  : "coautor",
            };
          }
        )
        .filter(Boolean);
    },

    // ========================================================
    // ARCHIVOS
    // ========================================================

    hasPendingRecoveredFiles() {
      const archivos =
        Array.isArray(
          this.form.archivos
        )
          ? this.form.archivos
          : [];

      return (
        archivos.some(
          (item) =>
            !item?.file &&
            item
              ?.originalName
        )
      );
    },

    // ========================================================
    // VALIDACIÓN FRONTEND
    // ========================================================

    validateFront() {
      const errors = {};

      const datos =
        this.form
          .datos_generales ||
        {};

      // ------------------------------------------------------
      // Administración
      // ------------------------------------------------------

      if (
        this.isAdminDelegado &&
        !this.adminContext
          .usuarioId
      ) {
        errors.admin_context =
          "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
      }

      // ------------------------------------------------------
      // Datos institucionales
      // ------------------------------------------------------

      if (
        !datos.facultad
      ) {
        errors.facultad =
          "Seleccione una facultad.";
      }

      if (
        !datos.carrera
      ) {
        errors.carrera =
          "Seleccione una carrera.";
      }

      if (
        !datos.area
      ) {
        errors.area =
          "Seleccione un área del conocimiento (UNESCO).";
      }

      if (
        !datos.subarea
      ) {
        errors.subarea =
          "Seleccione una subárea del conocimiento (UNESCO).";
      }

      // ------------------------------------------------------
      // Origen
      // ------------------------------------------------------

      if (
        !String(
          this.form
            .origen_tipo ||
          ""
        ).trim()
      ) {
        errors.origen_tipo =
          "Seleccione el origen de la publicación.";
      }

      if (
        ["tic", "otro"].includes(this.form
          .origen_tipo) &&

        !String(
          this.form
            .origen_grado ||
          ""
        ).trim()
      ) {
        errors.origen_grado =
          "Campo obligatorio.";
      }

      if (
        exceedsLength(
          this.form
            .origen_grado,
          FIELD_LIMITS
            .origen_grado
        )
      ) {
        errors.origen_grado =
          `El grado, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
      }

      // ------------------------------------------------------
      // Artículo
      // ------------------------------------------------------

      if (
        !String(
          this.form
            .nombre_articulo ||
          ""
        ).trim()
      ) {
        errors.nombre_articulo =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form
            .nombre_articulo,
          FIELD_LIMITS
            .nombre_articulo
        )
      ) {
        errors.nombre_articulo =
          `El título no puede superar ${FIELD_LIMITS.nombre_articulo} caracteres.`;
      }

      if (
        !this.form
          .fecha_publicacion
      ) {
        errors.fecha_publicacion =
          "Campo obligatorio.";
      }

      // ------------------------------------------------------
      // Revista
      // ------------------------------------------------------

      if (
        !String(
          this.form
            .codigo_issn ||
          ""
        ).trim()
      ) {
        errors.codigo_issn =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form
            .codigo_issn,
          FIELD_LIMITS
            .codigo_issn
        )
      ) {
        errors.codigo_issn =
          `El ISSN no puede superar ${FIELD_LIMITS.codigo_issn} caracteres.`;
      }

      if (
        !String(
          this.form
            .nombre_revista ||
          ""
        ).trim()
      ) {
        errors.nombre_revista =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form
            .nombre_revista,
          FIELD_LIMITS
            .nombre_revista
        )
      ) {
        errors.nombre_revista =
          `El nombre de la revista no puede superar ${FIELD_LIMITS.nombre_revista} caracteres.`;
      }

      if (
        exceedsLength(
          this.form
            .codigo_doi,
          FIELD_LIMITS
            .codigo_doi
        )
      ) {
        errors.codigo_doi =
          `El DOI no puede superar ${FIELD_LIMITS.codigo_doi} caracteres.`;
      }

      if (
        exceedsLength(
          this.form
            .link_revista,
          FIELD_LIMITS
            .link_revista
        )
      ) {
        errors.link_revista =
          `El enlace no puede superar ${FIELD_LIMITS.link_revista} caracteres.`;
      }

      if (
        exceedsLength(
          this.form
            .link_publicacion,
          FIELD_LIMITS
            .link_publicacion
        )
      ) {
        errors.link_publicacion =
          `El enlace no puede superar ${FIELD_LIMITS.link_publicacion} caracteres.`;
      }

      // ------------------------------------------------------
      // Número revista
      // ------------------------------------------------------

      if (
        this.form
          .numero_revista !==
          null &&

        this.form
          .numero_revista !==
          ""
      ) {
        const numero =
          Number(
            this.form
              .numero_revista
          );

        if (
          !Number.isInteger(
            numero
          ) ||
          numero < 1
        ) {
          errors.numero_revista =
            "El número de la revista debe ser un entero mayor o igual a 1.";
        }
      }

      // ------------------------------------------------------
      // Factor
      // ------------------------------------------------------

      const validFactors =
        new Set([
          "",
          "sjr",
          "jcr",
        ]);

      if (
        !validFactors.has(
          String(
            this.form
              .factor_impacto ||
            ""
          ).toLowerCase()
        )
      ) {
        errors.factor_impacto =
          "Seleccione un factor de impacto válido.";
      }

      const validQuartiles =
        new Set([
          "",
          "q1",
          "q2",
          "q3",
          "q4",
          "sin_cuartil",
        ]);

      const normalizedCuartil =
        normalizeCuartil(
          this.form.cuartil
        );

      if (
        !validQuartiles.has(
          normalizedCuartil
        )
      ) {
        errors.cuartil =
          "Seleccione un cuartil válido.";
      }

      if (
        this.form
          .factor_impacto ===
          "sjr" &&

        !String(
          this.form.sjr ||
          ""
        ).trim()
      ) {
        errors.sjr =
          "Ingrese el valor SJR o seleccione otro factor.";
      }

      if (
        exceedsLength(
          this.form.sjr,
          FIELD_LIMITS.sjr
        )
      ) {
        errors.sjr =
          `El valor SJR no puede superar ${FIELD_LIMITS.sjr} caracteres.`;
      }

      // ------------------------------------------------------
      // Autores
      // ------------------------------------------------------

      if (
        !Array.isArray(
          this.form.autores
        ) ||

        this.form
          .autores
          .length ===
          0
      ) {
        errors.autores =
          "Debe registrar al menos un autor.";
      }

      // ------------------------------------------------------
      // Adjuntos recuperados
      // ------------------------------------------------------

      if (
        this.hasPendingRecoveredFiles()
      ) {
        errors.archivos =
          "Hay adjuntos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
      }

      this.fieldErrors =
        errors;

      if (
        Object.keys(
          errors
        ).length
      ) {
        const first =
          firstErrorField(
            errors
          );

        this.mensaje =
          "Complete o corrija los campos marcados antes de guardar.";

        this.mensajeTipo =
          "error";

        if (first) {
          this.$nextTick(
            () => {
              this.focusField(
                first
              );
            }
          );
        }

        return false;
      }

      return true;
    },

    // ========================================================
    // REGISTRO
    // ========================================================

    async registrarArticulo() {
      if (
        this.loading
      ) {
        return;
      }

      this.loading =
        true;

      this.clearErrors();

      try {
        if (
          !this.validateFront()
        ) {
          return;
        }

        // ----------------------------------------------------
        // Autores
        // ----------------------------------------------------

        const autoresPayload =
          this.buildAutoresPayload();

        if (
          !autoresPayload.length
        ) {
          this.fieldErrors = {
            ...this.fieldErrors,

            autores:
              "Los autores seleccionados no tienen un identificador válido.",
          };

          this.mensaje =
            "Revise la sección de autores.";

          this.mensajeTipo =
            "error";

          this.focusField(
            "autores"
          );

          return;
        }

        // ----------------------------------------------------
        // Contexto administrador
        // ----------------------------------------------------

        const adminValidationError =
          this.validateAdminContext();

        if (
          adminValidationError
        ) {
          this.fieldErrors = {
            ...this.fieldErrors,

            admin_context:
              adminValidationError,
          };

          this.mensaje =
            adminValidationError;

          this.mensajeTipo =
            "error";

          this.focusField(
            "admin_context"
          );

          return;
        }

        // ----------------------------------------------------
        // FormData
        // ----------------------------------------------------

        const formData =
          new FormData();

        formData.append(
          "tipo_codigo",
          "articulo_alto_impacto"
        );

        // ----------------------------------------------------
        // Datos generales
        // ----------------------------------------------------

        Object.entries(
          this.form
            .datos_generales ||
          {}
        ).forEach(
          ([key, value]) => {
            /*
             * País y ciudad solamente aplican
             * a Ponencia en el backend.
             */
            if (
              key === "pais" ||
              key === "ciudad"
            ) {
              return;
            }

            appendIfPresent(
              formData,
              key,
              value
            );
          }
        );

        // ----------------------------------------------------
        // Origen
        // ----------------------------------------------------

        formData.append(
          "origen_tipo",
          String(
            this.form
              .origen_tipo ||
            "ninguno"
          )
        );

        if (
          ["tic", "otro"].includes(this.form
            .origen_tipo) &&

          String(
            this.form
              .origen_grado ||
            ""
          ).trim()
        ) {
          formData.append(
            "origen_grado",
            String(
              this.form
                .origen_grado
            ).trim()
          );
        }

        // ----------------------------------------------------
        // Artículo
        // ----------------------------------------------------

        [
          "nombre_articulo",
          "fecha_publicacion",
          "codigo_doi",
          "codigo_issn",
          "nombre_revista",
          "numero_revista",
          "link_revista",
          "link_publicacion",
          "factor_impacto",
          "cuartil",
          "sjr",
        ].forEach(
          (key) => {
            const value =
              key === "cuartil"
                ? normalizeCuartil(
                    this.form[
                      key
                    ]
                  )
                : this.form[
                    key
                  ];

            appendIfPresent(
              formData,
              key,
              value
            );
          }
        );

        // ----------------------------------------------------
        // Autores
        // ----------------------------------------------------

        formData.append(
          "autores",
          JSON.stringify(
            autoresPayload
          )
        );

        // ----------------------------------------------------
        // Registro delegado
        // ----------------------------------------------------

        if (
          this.isAdminDelegado &&
          this.adminContext
            .usuarioId
        ) {
          formData.append(
            "usuario_objetivo_id",
            String(
              this.adminContext
                .usuarioId
            )
          );

          if (
            this.adminContext
              .autorId
          ) {
            formData.append(
              "autor_objetivo_id",
              String(
                this.adminContext
                  .autorId
              )
            );
          }
        }

        // ----------------------------------------------------
        // Adjuntos
        // ----------------------------------------------------

        appendArchivosToFormData(
          formData,
          this.form.archivos,
          {
            primaryField:
              null,

            filesField:
              "archivos",

            metaField:
              "archivos_meta",
          }
        );

        // ----------------------------------------------------
        // Request
        // ----------------------------------------------------

        await api.post(
          this.createEndpoint,
          formData
        );

        // ----------------------------------------------------
        // Limpiar borrador
        // ----------------------------------------------------

        this.disableDraftTemporarily();

        try {
          localStorage.removeItem(
            this.storageKey
          );
        } catch (error) {
          console.warn(
            "No se pudo eliminar el borrador después del registro.",
            error
          );
        }

        this.resetForm();

        this.mensaje =
          this.isAdminDelegado
            ? "Artículo registrado exitosamente para el usuario seleccionado."
            : "Artículo registrado exitosamente.";

        this.mensajeTipo =
          "success";
      } catch (error) {
        const status =
          error
            ?.response
            ?.status;

        const data =
          error
            ?.response
            ?.data;

        // ----------------------------------------------------
        // Sesión
        // ----------------------------------------------------

        if (
          status === 401
        ) {
          this.mensaje =
            "Sesión expirada. Vuelva a iniciar sesión.";

          this.mensajeTipo =
            "error";

          return;
        }

        // ----------------------------------------------------
        // Permisos
        // ----------------------------------------------------

        if (
          status === 403
        ) {
          this.mensaje =
            "No tiene permisos para realizar este registro.";

          this.mensajeTipo =
            "error";

          return;
        }

        // ----------------------------------------------------
        // Errores DRF
        // ----------------------------------------------------

        const normalized =
          normalizeDrfErrors(
            data
          );

        this.fieldErrors =
          normalized.fields ||
          {};

        this.mensaje =
          normalized.message ||
          "No se pudo registrar el artículo.";

        this.mensajeTipo =
          "error";

        const first =
          firstErrorField(
            this.fieldErrors
          );

        if (first) {
          this.$nextTick(
            () => {
              this.focusField(
                first
              );
            }
          );
        }

        console.error(
          "Error al registrar el artículo:",
          data || error
        );
      } finally {
        this.loading =
          false;
      }
    },

    // ========================================================
    // RESET
    // ========================================================

    resetForm() {
      this.fieldErrors =
        {};

      this.draftInfo =
        "";

      this.mensaje =
        "";

      this.mensajeTipo =
        "";

      this.form =
        createEmptyForm();
    },
  },
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
<style src="./articulo-alto-impacto-form.css"></style>