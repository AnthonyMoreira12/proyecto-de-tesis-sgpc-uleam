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
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->

      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar un artículo de alto impacto"
        enctype="multipart/form-data"
        @submit.prevent="handleSubmitIntent"
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
            <div class="sgpc-card-body">
              <div
                id="ai-admin-context-anchor"
                tabindex="-1"
              ></div>

              <div class="sgpc-admin-context">
                <span class="sgpc-admin-context__label">
                  Registrando para
                </span>

                <strong class="sgpc-admin-context__value">
                  {{ adminDisplayUsuario }}
                </strong>
              </div>

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
                  Información académica
                </h2>

                <p class="sgpc-card-desc">
                  Indique dónde se desarrolló o a qué área corresponde la publicación.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredContext, optionalContextMissingCount)"
              >
                {{ sectionStateLabel(hasRequiredContext, optionalContextMissingCount) }}
              </span>

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
                  Origen académico
                </h2>

                <p class="sgpc-card-desc">
                  Indique si el artículo se originó a partir de otro trabajo académico.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredOrigin, 0)"
              >
                {{ sectionStateLabel(hasRequiredOrigin, 0) }}
              </span>

            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="ai-origen_tipo"
                  >
                    ¿Esta publicación se originó a partir de otro trabajo académico?
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
                      No
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

                <div
                  v-if="['tic', 'otro'].includes(form.origen_tipo)"
                  class="sgpc-field sgpc-col-span-12 sgpc-origin-extra"
                >
                  <label
                    class="sgpc-label"
                    for="ai-origen_grado"
                  >
                    {{
                      form.origen_tipo === "otro"
                        ? "Especifique el origen"
                        : "Carrera o programa relacionado"
                    }}

                    <span
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
                    required
                    :aria-invalid="hasFieldError('origen_grado')"
                    :aria-describedby="originGradeDescriptionIds"
                    :placeholder="
                      form.origen_tipo === 'otro'
                        ? 'Ej. Proyecto de investigación institucional'
                        : 'Ej. Ingeniería en Tecnologías de la Información'
                    "
                  />

                  <p
                    id="ai-origen-grado-help"
                    class="sgpc-hint"
                  >
                    {{
                      form.origen_tipo === "otro"
                        ? "Indique de qué trabajo, proyecto o proceso se originó."
                        : "Indique la carrera o programa relacionado con el trabajo."
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
                  Ingrese el título y la fecha de publicación.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredArticle, optionalArticleMissingCount)"
              >
                {{ sectionStateLabel(hasRequiredArticle, optionalArticleMissingCount) }}
              </span>

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

                <div class="sgpc-field sgpc-col-span-3">
                  <label
                    class="sgpc-label"
                    for="ai-anio_publicacion"
                  >
                    Año de publicación
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-anio_publicacion"
                    v-model.number="form.anio_publicacion"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    placeholder="Ej. 2026"
                    :aria-invalid="hasFieldError('anio_publicacion')"
                    :aria-describedby="errorDescriptionId('anio_publicacion')"
                    required
                  />

                  <p
                    v-if="fieldErrors.anio_publicacion"
                    :id="fieldErrorId('anio_publicacion')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.anio_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-3">
                  <label
                    class="sgpc-label"
                    for="ai-mes_publicacion"
                  >
                    Mes de publicación
                    <span class="sgpc-label-optional">
                      (opcional)
                    </span>
                  </label>

                  <select
                    id="ai-mes_publicacion"
                    v-model="form.mes_publicacion"
                    class="sgpc-input"
                    :aria-invalid="hasFieldError('mes_publicacion')"
                    :aria-describedby="monthDescriptionIds"
                  >
                    <option value="">
                      Sin mes especificado
                    </option>

                    <option
                      v-for="month in publicationMonths"
                      :key="month.value"
                      :value="month.value"
                    >
                      {{ month.label }}
                    </option>
                  </select>

                  <p
                    id="ai-mes-publicacion-help"
                    class="sgpc-hint"
                  >
                    Puede dejar el mes vacío si no consta en la fuente bibliográfica.
                  </p>

                  <p
                    v-if="fieldErrors.mes_publicacion"
                    :id="fieldErrorId('mes_publicacion')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.mes_publicacion }}
                  </p>
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
                  Complete los datos de la revista y, si dispone de ellos, sus enlaces e indicadores.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredJournal, optionalJournalMissingCount)"
              >
                {{ sectionStateLabel(hasRequiredJournal, optionalJournalMissingCount) }}
              </span>

            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Revista</strong>
                  <span>Datos principales de la publicación.</span>
                </div>

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
                    DOI
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
                    ISSN
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

                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Enlaces</strong>
                  <span>Agregue los enlaces disponibles.</span>
                </div>

                <!-- Link revista -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-link_revista"
                  >
                    Enlace de la revista
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
                    Enlace de la publicación
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

                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Indicadores</strong>
                  <span>Complete esta información solo cuando corresponda.</span>
                </div>

                <!-- Factor -->

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ai-factor_impacto"
                  >
                    Indicador de impacto
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

                <!-- JCR -->

                <div
                  v-if="form.factor_impacto === 'jcr'"
                  class="sgpc-field sgpc-col-span-12"
                >
                  <label
                    class="sgpc-label"
                    for="ai-jcr"
                  >
                    JCR (valor)

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ai-jcr"
                    v-model.trim="form.jcr"
                    class="sgpc-input"
                    type="text"
                    inputmode="decimal"
                    maxlength="100"
                    :aria-invalid="hasFieldError('jcr')"
                    :aria-describedby="errorDescriptionId('jcr')"
                    placeholder="Ej. 3.25"
                    required
                  />

                  <p
                    v-if="fieldErrors.jcr"
                    :id="fieldErrorId('jcr')"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.jcr }}
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
                  Agregue las personas que participaron y colóquelas en el orden en que deben aparecer.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredAuthors, 0)"
              >
                {{ sectionStateLabel(hasRequiredAuthors, 0) }}
              </span>

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
                  Documentos
                </h2>

                <p class="sgpc-card-desc">
                  Adjunte el documento del artículo y, si corresponde, archivos adicionales.
                </p>
              </div>
              <span
                class="sgpc-section-state"
                :class="hasAdjuntos ? 'is-complete' : 'is-optional'"
              >
                {{ hasAdjuntos ? "Completado" : "Opcional" }}
              </span>

            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                :disabled="loading"
                input-id="ai-archivo-input"
                title=""
                description=""
                helper-text=""
                :multiple="true"
                :max-files="3"
                :uses-primary-slot="true"
                :primary-max-size-mb="5"
                :attachment-max-size-mb="3"
                :validate-signature="true"
              />
            </div>
          </section>

          <!-- =================================================
               PREVALIDACIÓN
          ================================================== -->

          <div
            v-if="prevalidacionBloqueantes.length"
            class="sgpc-alert is-error"
            role="alert"
            aria-live="assertive"
          >
            <strong>Corrija antes de continuar</strong>
            <span>
              Corrija los siguientes puntos antes de registrar:
            </span>
            <ul>
              <li
                v-for="(item, index) in prevalidacionBloqueantes"
                :key="`ai-pre-block-${item.codigo || index}`"
              >
                {{ item.mensaje }}
              </li>
            </ul>
          </div>

          <div
            v-if="prevalidacionAdvertencias.length"
            class="sgpc-alert is-info"
            role="status"
            aria-live="polite"
          >
            <strong>Revise antes de registrar</strong>
            <span>
              Estas observaciones no impiden el registro, pero conviene verificarlas antes de continuar:
            </span>
            <ul>
              <li
                v-for="(item, index) in prevalidacionAdvertencias"
                :key="`ai-pre-warning-${item.codigo || index}`"
              >
                {{ item.mensaje }}
              </li>
            </ul>
          </div>

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
             ESTADO DEL REGISTRO
        ==================================================== -->

        <aside class="sgpc-form-aside page-stage page-aside">
          <div class="sgpc-summary-card">
            <div class="sgpc-summary-head">
              <div>
                <h2>
                  Estado del registro
                </h2>
              </div>
            </div>

            <div
              class="sgpc-progress"
              :class="{ 'is-complete': canSubmit }"
            >
              <div class="sgpc-progress-row">
                <span>
                  Progreso
                </span>

                <strong>
                  {{ progressPercent }}%
                </strong>
              </div>

              <div
                class="sgpc-progress-bar"
                role="progressbar"
                aria-label="Progreso del formulario"
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
                secciones obligatorias listas
              </p>
            </div>

            <div
              v-if="pendingRequiredSections.length"
              class="sgpc-pending-summary"
            >
              <strong>Falta completar</strong>

              <div class="sgpc-pending-summary__list">
                <button
                  v-for="item in pendingRequiredSections"
                  :key="item.key"
                  type="button"
                  class="sgpc-pending-summary__item"
                  @click="goTo(item.target)"
                >
                  <span>{{ item.label }}</span>
                  <small>{{ item.detail }}</small>
                </button>
              </div>
            </div>

            <div
              v-else
              class="sgpc-ready-notice"
              role="status"
              aria-live="polite"
            >
              <strong>
                Listo para registrar
              </strong>

              <span>
                Todos los datos obligatorios están completos.
              </span>
            </div>

            <div
              v-if="optionalMissingCount > 0"
              class="sgpc-optional-summary sgpc-optional-summary--compact"
            >
              <p>
                Hay
                <strong>{{ optionalMissingCount }}</strong>
                {{
                  optionalMissingCount === 1
                    ? "dato opcional sin completar"
                    : "datos opcionales sin completar"
                }}.
                Puede registrar sin completarlos.
              </p>

              <button
                type="button"
                class="sgpc-summary-link"
                @click="reviewOptionalFields"
              >
                Revisarlos
              </button>
            </div>

            <div class="sgpc-summary-actions">
              <button
                class="sgpc-btn-primary sgpc-publication-submit"
                type="submit"
                :disabled="loading || !canSubmit"
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

              <p class="sgpc-draft-note">
                Los cambios se guardan automáticamente en este navegador.
              </p>

              <button
                type="button"
                class="sgpc-btn sgpc-discard-draft-btn"
                :disabled="loading"
                @click="requestDiscardDraft"
              >
                Descartar borrador
              </button>
            </div>
          </div>
        </aside>
      </form>

      <div
        v-if="showDiscardDraftDialog"
        class="sgpc-review-modal sgpc-review-modal--discard"
        role="presentation"
        @mousedown.self="cancelDiscardDraft"
      >
        <section
          ref="discardDraftDialog"
          class="sgpc-review-modal__dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="ai-discard-draft-title"
          aria-describedby="ai-discard-draft-description"
          tabindex="-1"
          @keydown.esc="cancelDiscardDraft"
        >
          <div
            class="sgpc-review-modal__icon"
            aria-hidden="true"
          >
            !
          </div>

          <div class="sgpc-review-modal__content">
            <h2 id="ai-discard-draft-title">
              ¿Descartar este borrador?
            </h2>

            <p id="ai-discard-draft-description">
              Se eliminarán los datos que ha ingresado en este formulario.
              Esta acción no se puede deshacer.
            </p>

            <div class="sgpc-review-modal__actions">
              <button
                type="button"
                class="sgpc-btn"
                @click="cancelDiscardDraft"
              >
                Cancelar
              </button>

              <button
                type="button"
                class="sgpc-btn-danger"
                @click="confirmDiscardDraft"
              >
                Descartar borrador
              </button>
            </div>
          </div>
        </section>
      </div>

      <NoticeDialog
        :model-value="prevalidationNotice"
        @close="closePrevalidationNotice"
      />

    </div>
  </div>
</template>

<script>
import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import api from "../../scripts/api/axios";
import {
  prevalidarPublicacion,
} from "../../scripts/api/publicacionesApi";

import {
  appendArchivosToFormData,
  restoreDraftArchivos,
  serializeDraftArchivos,
} from "../../scripts/utils/adjuntosPdf";


const BASE_STORAGE_KEY =
  "sgpc-articulo-alto-impacto-draft:v24";

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
  jcr: 100,
});


const PUBLICATION_MONTHS = Object.freeze([
  { value: 1, label: "Enero" },
  { value: 2, label: "Febrero" },
  { value: 3, label: "Marzo" },
  { value: 4, label: "Abril" },
  { value: 5, label: "Mayo" },
  { value: 6, label: "Junio" },
  { value: 7, label: "Julio" },
  { value: 8, label: "Agosto" },
  { value: 9, label: "Septiembre" },
  { value: 10, label: "Octubre" },
  { value: 11, label: "Noviembre" },
  { value: 12, label: "Diciembre" },
]);


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
  admin_context: "Usuario seleccionado",
  general: "Validación general",
  sede: "Sede",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  tipo_codigo: "Tipo de artículo",
  nombre_articulo: "Título del artículo",
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",
  codigo_doi: "DOI",
  codigo_issn: "ISSN",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_publicacion: "Enlace de la publicación",
  link_revista: "Enlace de la revista",
  factor_impacto: "Indicador de impacto",
  cuartil: "Cuartil",
  sjr: "SJR",
  jcr: "JCR",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Carrera, programa u otro origen",
  autores: "Autores",
  archivos: "Documentos",
});


const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "sede",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "tipo_codigo",
  "origen_tipo",
  "origen_grado",
  "nombre_articulo",
  "anio_publicacion",
  "mes_publicacion",
  "nombre_revista",
  "numero_revista",
  "codigo_issn",
  "codigo_doi",
  "link_revista",
  "link_publicacion",
  "factor_impacto",
  "cuartil",
  "sjr",
  "jcr",
  "autores",
  "archivos",
  "general",
]);


function createEmptyForm() {
  return {
    datos_generales: {
      sede: null,
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
    anio_publicacion: null,
    mes_publicacion: "",

    codigo_doi: "",
    codigo_issn: "",
    nombre_revista: "",
    numero_revista: null,
    link_revista: "",
    link_publicacion: "",

    factor_impacto: "",
    cuartil: "",
    sjr: "",
    jcr: "",

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
          "Revise la sección de Documentos.";
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
    NoticeDialog,
  },

  data() {
    return {
      loading: false,

      mensaje: "",
      mensajeTipo: "",

      fieldErrors: {},

      prevalidacionBloqueantes: [],
      prevalidacionAdvertencias: [],
      prevalidacionResumen: null,

      prevalidationNotice: {
        open: false,
        title: "",
        message: "",
        details: null,
        confirm: false,
        confirmText: "Confirmar",
        cancelText: "Cancelar",
        onConfirm: null,
        onCancel: null,
      },
      prevalidationDecisionResolver: null,

      draftInfo: "",
      showDiscardDraftDialog: false,
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
    publicationMonths() {
      return PUBLICATION_MONTHS;
    },

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
        this.adminContext.usuarioNombre || "Usuario seleccionado"
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

    adminReady() {
      return (
        !this.isAdminDelegado ||
        Boolean(
          this.adminContext
            .usuarioId
        )
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
        "Registrar artículo de alto impacto"
      );
    },

    pageSubtitle() {
      return (
        "Complete los datos de la publicación. Los campos con * son obligatorios."
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
        datos.sede &&
        datos.facultad &&
        datos.carrera
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

        Number.isInteger(
          Number(
            this.form
              .anio_publicacion
          )
        ) &&

        Number(
          this.form
            .anio_publicacion
        ) >= 1900 &&

        Number(
          this.form
            .anio_publicacion
        ) <= 2100
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

      if (
        this.form
          .factor_impacto ===
          "jcr" &&

        !String(
          this.form.jcr ||
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

    optionalMissingItems() {
      const general =
        this.form.datos_generales || {};

      const hasValue = (value) =>
        value !== null &&
        value !== undefined &&
        String(value).trim() !== "";

      const items = [];

      if (!hasValue(general.proyecto)) {
        items.push({
          key: "proyecto",
          label: "Proyecto de investigación",
          section: "datos",
          sectionLabel: "Información académica",
        });
      }

      if (!hasValue(general.area)) {
        items.push({
          key: "area",
          label: "Área del conocimiento (UNESCO)",
          section: "datos",
          sectionLabel: "Datos generales",
        });
      } else if (!hasValue(general.subarea)) {
        items.push({
          key: "subarea",
          label: "Subárea del conocimiento (UNESCO)",
          section: "datos",
          sectionLabel: "Datos generales",
        });
      }

      if (!hasValue(this.form.mes_publicacion)) {
        items.push({
          key: "mes_publicacion",
          label: "Mes de publicación",
          section: "articulo",
          sectionLabel: "Información del artículo",
        });
      }

      if (!hasValue(this.form.numero_revista)) {
        items.push({
          key: "numero_revista",
          label: "Número de la revista",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!hasValue(this.form.codigo_doi)) {
        items.push({
          key: "codigo_doi",
          label: "DOI",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!hasValue(this.form.link_revista)) {
        items.push({
          key: "link_revista",
          label: "Enlace de la revista",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!hasValue(this.form.link_publicacion)) {
        items.push({
          key: "link_publicacion",
          label: "Enlace de la publicación",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!hasValue(this.form.factor_impacto)) {
        items.push({
          key: "factor_impacto",
          label: "Indicador de impacto",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!hasValue(this.form.cuartil)) {
        items.push({
          key: "cuartil",
          label: "Cuartil",
          section: "revista",
          sectionLabel: "Revista e indicadores",
        });
      }

      if (!this.hasAdjuntos) {
        items.push({
          key: "archivos",
          label: "Documentos",
          section: "adjuntos",
          sectionLabel: "Documentos",
        });
      }

      return items;
    },

    optionalMissingCount() {
      return this.optionalMissingItems.length;
    },

    totalOptionalCount() {
      const general =
        this.form.datos_generales || {};

      const hasArea =
        general.area !== null &&
        general.area !== undefined &&
        String(general.area).trim() !== "";

      /*
       * Proyecto, área, mes, número de revista, DOI,
       * link de revista, link de publicación, factor de impacto,
       * cuartil y adjuntos.
       *
       * La subárea solamente aplica si se seleccionó un área.
       * SJR/JCR no se cuentan como opcionales: el valor del indicador
       * seleccionado se convierte en requisito condicional.
       */
      return 10 + (hasArea ? 1 : 0);
    },

    optionalCompletedCount() {
      return Math.max(
        0,
        this.totalOptionalCount -
          this.optionalMissingCount
      );
    },

    optionalContextMissingCount() {
      return this.optionalMissingItems
        .filter((item) => item.section === "datos")
        .length;
    },

    optionalArticleMissingCount() {
      return this.optionalMissingItems
        .filter((item) => item.section === "articulo")
        .length;
    },

    optionalJournalMissingCount() {
      return this.optionalMissingItems
        .filter((item) => item.section === "revista")
        .length;
    },

    canSubmit() {
      return Boolean(
        this.totalRequiredCount > 0 &&
        this.completedRequiredCount ===
          this.totalRequiredCount
      );
    },

    summarySections() {
      const sections = [
        {
          key: "datos",
          target: "sec-datos-generales",
          label: "Información académica",
          done: this.hasRequiredContext,
          required: true,
          optionalMissing:
            this.optionalContextMissingCount,
          detail:
            this.hasRequiredContext
              ? "Listo"
              : "Complete sede, facultad y carrera",
          status:
            this.hasRequiredContext
              ? "Listo"
              : "Falta información",
        },

        {
          key: "origen",
          target: "sec-origen",
          label: "Origen académico",
          done: this.hasRequiredOrigin,
          required: true,
          optionalMissing: 0,
          detail:
            this.hasRequiredOrigin
              ? "Listo"
              : "Seleccione el origen",
          status:
            this.hasRequiredOrigin
              ? "Listo"
              : "Falta información",
        },

        {
          key: "articulo",
          target: "sec-articulo",
          label: "Información del artículo",
          done: this.hasRequiredArticle,
          required: true,
          optionalMissing:
            this.optionalArticleMissingCount,
          detail:
            this.hasRequiredArticle
              ? "Listo"
              : "Complete el título y el año",
          status:
            this.hasRequiredArticle
              ? "Listo"
              : "Falta información",
        },

        {
          key: "revista",
          target: "sec-revista",
          label: "Revista e indicadores",
          done: this.hasRequiredJournal,
          required: true,
          optionalMissing:
            this.optionalJournalMissingCount,
          detail:
            this.hasRequiredJournal
              ? "Listo"
              : "Complete revista, ISSN y el indicador requerido",
          status:
            this.hasRequiredJournal
              ? "Listo"
              : "Falta información",
        },

        {
          key: "autores",
          target: "sec-autores",
          label: "Autores",
          done: this.hasRequiredAuthors,
          required: true,
          optionalMissing: 0,
          detail:
            this.hasRequiredAuthors
              ? "Listo"
              : "Agregue al menos un autor",
          status:
            this.hasRequiredAuthors
              ? "Listo"
              : "Falta información",
        },

        {
          key: "documentos",
          target: "sec-adjuntos",
          label: "Documentos",
          done: this.hasAdjuntos,
          required: false,
          optionalMissing:
            this.hasAdjuntos ? 0 : 1,
          detail:
            this.hasAdjuntos
              ? "Documentos agregados"
              : "Opcional",
          status:
            this.hasAdjuntos
              ? "Listo"
              : "Opcional",
        },
      ];

      if (this.isAdminDelegado) {
        return [
          {
            key: "admin",
            target: "sec-contexto-admin",
            label: "Persona seleccionada",
            done: this.adminReady,
            required: true,
            optionalMissing: 0,
            detail:
              this.adminReady
                ? "Listo"
                : "Seleccione la persona",
            status:
              this.adminReady
                ? "Listo"
                : "Falta información",
          },
          ...sections,
        ];
      }

      return sections;
    },

    pendingRequiredSections() {
      return this.summarySections
        .filter(
          (section) =>
            section.required &&
            !section.done
        );
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

    monthDescriptionIds() {
      const ids = [
        "ai-mes-publicacion-help",
      ];

      if (
        this.fieldErrors
          .mes_publicacion
      ) {
        ids.push(
          this.fieldErrorId(
            "mes_publicacion"
          )
        );
      }

      return ids.join(" ");
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
    this.closePrevalidationNotice();

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
        if (!this.loading) {
          this.clearPrevalidationState();
        }

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

      if (
        value !== "jcr"
      ) {
        this.form.jcr =
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

    resetPrevalidationNotice() {
      Object.assign(
        this.prevalidationNotice,
        {
          open: false,
          title: "",
          message: "",
          details: null,
          confirm: false,
          confirmText: "Confirmar",
          cancelText: "Cancelar",
          onConfirm: null,
          onCancel: null,
        }
      );
    },

    resolvePrevalidationDecision(value) {
      const resolver =
        this.prevalidationDecisionResolver;

      this.prevalidationDecisionResolver =
        null;

      if (
        typeof resolver ===
        "function"
      ) {
        resolver(
          Boolean(value)
        );
      }
    },

    closePrevalidationNotice() {
      this.resolvePrevalidationDecision(
        false
      );

      this.resetPrevalidationNotice();
    },

    confirmarAdvertenciasPrevalidacion(
      advertencias = []
    ) {
      const items =
        Array.isArray(advertencias)
          ? advertencias
          : [];

      if (!items.length) {
        return Promise.resolve(true);
      }

      this.closePrevalidationNotice();

      const visibles =
        items.slice(0, 5);

      const details = [
        ...visibles.map(
          (item) =>
            `• ${String(
              item?.mensaje ||
              "Revise la información indicada."
            ).trim()}`
        ),
        ...(
          items.length > 5
            ? [
                `• Hay ${
                  items.length - 5
                } observación${
                  items.length - 5 === 1
                    ? ""
                    : "es"
                } adicional${
                  items.length - 5 === 1
                    ? ""
                    : "es"
                } en el formulario.`,
              ]
            : []
        ),
      ].join("\n");

      return new Promise(
        (resolve) => {
          this.prevalidationDecisionResolver =
            resolve;

          Object.assign(
            this.prevalidationNotice,
            {
              open: true,
              title:
                "Revise antes de registrar",
              message:
                "Hay información que requiere atención. Estas observaciones no impiden el registro, pero conviene verificarlas antes de continuar.",
              details,
              confirm: true,
              confirmText:
                "Continuar con el registro",
              cancelText:
                "Volver a revisar",
              onConfirm: () => {
                this.resolvePrevalidationDecision(
                  true
                );
              },
              onCancel: () => {
                this.resolvePrevalidationDecision(
                  false
                );
              },
            }
          );
        }
      );
    },

    /* ========================================================
       RESUMEN / OPCIONALES
    ======================================================== */

    sectionStatusText() {
      return "Listo";
    },

    sectionStateLabel(requiredDone) {
      return requiredDone
        ? "Listo"
        : "Falta información";
    },

    sectionStateClass(requiredDone) {
      return requiredDone
        ? "is-complete"
        : "is-pending";
    },

    focusOptionalItem(item) {
      if (!item) {
        return;
      }

      if (item.key === "archivos") {
        this.goTo("sec-adjuntos");
        return;
      }

      this.focusField(item.key);
    },

    reviewOptionalFields() {
      const first =
        this.optionalMissingItems[0];

      if (!first) {
        return;
      }

      this.$nextTick(() => {
        this.focusOptionalItem(first);
      });
    },

    async handleSubmitIntent() {
      if (this.loading) {
        return;
      }

      this.clearErrors();

      if (!this.validateFront()) {
        return;
      }

      await this.registrarArticulo({
        skipFrontValidation: true,
      });
    },

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

    clearPrevalidationState() {
      this.prevalidacionBloqueantes = [];
      this.prevalidacionAdvertencias = [];
      this.prevalidacionResumen = null;
    },

    clearErrors() {
      this.fieldErrors =
        {};

      this.clearPrevalidationState();

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
          "Seleccione nuevamente al usuario para continuar con el registro."
        );
      }

      return null;
    },

    // ========================================================
    // BORRADOR
    // ========================================================

    normalizeRecoveredPeriod(
      recovered
    ) {
      const rawYear =
        Number(
          recovered
            ?.anio_publicacion
        );

      let year = (
        Number.isInteger(
          rawYear
        ) &&
        rawYear > 0
      )
        ? rawYear
        : null;

      const rawMonth =
        Number(
          recovered
            ?.mes_publicacion
        );

      let month = (
        Number.isInteger(
          rawMonth
        ) &&
        rawMonth >= 1 &&
        rawMonth <= 12
      )
        ? rawMonth
        : "";

      /*
       * Compatibilidad defensiva con borradores antiguos:
       * si existiera una fecha YYYY-MM-DD, conservamos solo
       * año y mes y descartamos el día.
       */
      const legacyDate =
        String(
          recovered?.[
            "fecha_" + "publicacion"
          ] ||
          ""
        ).trim();

      const legacyMatch =
        legacyDate.match(
          /^(\d{4})-(\d{2})/
        );

      if (
        legacyMatch
      ) {
        if (!year) {
          const parsedYear =
            Number(
              legacyMatch[1]
            );

          if (
            Number.isInteger(
              parsedYear
            ) &&
            parsedYear > 0
          ) {
            year =
              parsedYear;
          }
        }

        if (!month) {
          const parsedMonth =
            Number(
              legacyMatch[2]
            );

          if (
            Number.isInteger(
              parsedMonth
            ) &&
            parsedMonth >= 1 &&
            parsedMonth <= 12
          ) {
            month =
              parsedMonth;
          }
        }
      }

      return {
        anio_publicacion:
          year,

        mes_publicacion:
          month,
      };
    },

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

          anio_publicacion:
            value.anio_publicacion,

          mes_publicacion:
            value.mes_publicacion,

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

          jcr:
            value.jcr,

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

        const recoveredPeriod =
          this.normalizeRecoveredPeriod(
            recovered
          );

        const base =
          createEmptyForm();

        this.disableDraftTemporarily();

        this.form = {
          ...base,
          ...recovered,

          anio_publicacion:
            recoveredPeriod
              .anio_publicacion,

          mes_publicacion:
            recoveredPeriod
              .mes_publicacion,

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

        this.draftInfo =
          "Borrador recuperado. Puede continuar donde lo dejó.";
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

    requestDiscardDraft() {
      if (this.loading) {
        return;
      }

      this.showDiscardDraftDialog =
        true;

      this.$nextTick(() => {
        this.$refs.discardDraftDialog
          ?.focus?.();
      });
    },

    cancelDiscardDraft() {
      this.showDiscardDraftDialog =
        false;
    },

    confirmDiscardDraft() {
      this.showDiscardDraftDialog =
        false;

      this.clearDraft();
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
        "Borrador descartado.";

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

        anio_publicacion:
          "ai-anio_publicacion",

        mes_publicacion:
          "ai-mes_publicacion",

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

        jcr:
          "ai-jcr",

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
    // PREVALIDACIÓN
    // ========================================================

    normalizePrevalidationIssues(items) {
      const raw = Array.isArray(items)
        ? items
        : [];

      return raw
        .map((item, index) => {
          if (typeof item === "string") {
            return {
              codigo: `validacion-${index}`,
              nivel: "",
              campo: null,
              mensaje: item.trim(),
              origen: "validacion",
              metadata: {},
            };
          }

          const mensaje = String(
            item?.mensaje ??
            item?.message ??
            item?.detail ??
            ""
          ).trim();

          if (!mensaje) {
            return null;
          }

          return {
            codigo: String(
              item?.codigo ??
              item?.code ??
              `validacion-${index}`
            ).trim(),
            nivel: String(item?.nivel || "").trim(),
            campo: item?.campo
              ? String(item.campo).trim()
              : null,
            mensaje,
            origen: String(item?.origen || "validacion").trim(),
            metadata:
              item?.metadata && typeof item.metadata === "object"
                ? item.metadata
                : {},
          };
        })
        .filter(Boolean);
    },

    applyPrevalidationFieldErrors(items) {
      const next = {
        ...this.fieldErrors,
      };

      this.normalizePrevalidationIssues(items)
        .forEach((item) => {
          const rawField = String(item.campo || "").trim();

          if (!rawField) {
            return;
          }

          const field =
            ERROR_KEY_ALIASES[rawField] ||
            rawField;

          if (!next[field]) {
            next[field] = item.mensaje;
          }
        });

      this.fieldErrors = next;
    },

    selectedUploadItems() {
      return (
        Array.isArray(this.form.archivos)
          ? this.form.archivos
          : []
      ).filter((item) => item?.file);
    },

    buildPrevalidationPayload(autoresPayload) {
      const datos =
        this.form.datos_generales || {};

      const uploadItems =
        this.selectedUploadItems();

      return {
        tipo_codigo:
          "articulo_alto_impacto",

        sede: datos.sede || null,
        facultad: datos.facultad || null,
        carrera: datos.carrera || null,
        proyecto: datos.proyecto || null,
        area: datos.area || null,
        subarea: datos.subarea || null,

        origen_tipo:
          this.form.origen_tipo ||
          "ninguno",
        origen_grado:
          this.form.origen_grado ||
          "",

        nombre_articulo:
          String(this.form.nombre_articulo || "").trim(),
        anio_publicacion:
          this.form.anio_publicacion,
        mes_publicacion:
          this.form.mes_publicacion || null,
        codigo_doi:
          String(this.form.codigo_doi || "").trim(),
        codigo_issn:
          String(this.form.codigo_issn || "").trim(),
        nombre_revista:
          String(this.form.nombre_revista || "").trim(),
        numero_revista:
          this.form.numero_revista || null,
        link_revista:
          String(this.form.link_revista || "").trim(),
        link_publicacion:
          String(this.form.link_publicacion || "").trim(),
        factor_impacto:
          this.form.factor_impacto || "",
        cuartil:
          normalizeCuartil(this.form.cuartil),
        sjr:
          String(this.form.sjr || "").trim(),
        jcr:
          String(this.form.jcr || "").trim(),

        autores: autoresPayload,
        archivo_pdf:
          uploadItems[0]?.file ||
          null,

        registrado_por_admin:
          this.isAdminDelegado,
        usuario_objetivo_id:
          this.isAdminDelegado
            ? this.adminContext.usuarioId
            : null,
        autor_objetivo_id:
          this.isAdminDelegado
            ? this.adminContext.autorId
            : null,
      };
    },

    async ejecutarPrevalidacion(autoresPayload) {
      this.clearPrevalidationState();

      let response;

      try {
        response = await prevalidarPublicacion(
          this.buildPrevalidationPayload(
            autoresPayload
          )
        );
      } catch (error) {
        const normalized =
          normalizeDrfErrors(
            error?.response?.data
          );

        this.fieldErrors = {
          ...this.fieldErrors,
          ...(normalized.fields || {}),
        };

        this.mensaje =
          normalized.message ||
          "No se pudo verificar la información antes del registro. Revise los datos e inténtelo nuevamente.";
        this.mensajeTipo = "error";

        const first =
          firstErrorField(
            this.fieldErrors
          );

        if (first) {
          this.$nextTick(() => {
            this.focusField(first);
          });
        }

        return false;
      }

      const bloqueantes =
        this.normalizePrevalidationIssues(
          response?.bloqueantes
        );
      const advertencias =
        this.normalizePrevalidationIssues(
          response?.advertencias
        );

      this.prevalidacionBloqueantes =
        bloqueantes;
      this.prevalidacionAdvertencias =
        advertencias;
      this.prevalidacionResumen =
        response?.resumen || null;

      const puedeContinuar =
        response?.puede_continuar !== false &&
        bloqueantes.length === 0;

      if (!puedeContinuar) {
        this.applyPrevalidationFieldErrors(
          bloqueantes
        );

        this.mensaje =
          "Hay datos que deben corregirse antes de registrar el artículo.";
        this.mensajeTipo = "error";

        const first =
          firstErrorField(
            this.fieldErrors
          );

        if (first) {
          this.$nextTick(() => {
            this.focusField(first);
          });
        }

        return false;
      }

      if (advertencias.length) {
        const continuar =
          await this.confirmarAdvertenciasPrevalidacion(
            advertencias
          );

        if (!continuar) {
          this.mensaje =
            "Revise las observaciones antes de continuar con el registro.";
          this.mensajeTipo =
            "info";

          return false;
        }
      }

      return true;
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
          "Seleccione nuevamente al usuario para continuar con el registro.";
      }

      // ------------------------------------------------------
      // Datos institucionales
      // ------------------------------------------------------

      if (
        !datos.sede
      ) {
        errors.sede =
          "Seleccione una sede.";
      }

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
          `La carrera, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
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

      const publicationYear =
        Number(
          this.form
            .anio_publicacion
        );

      if (
        !Number.isInteger(
          publicationYear
        ) ||
        publicationYear < 1900 ||
        publicationYear > 2100
      ) {
        errors.anio_publicacion =
          "El año de publicación debe estar entre 1900 y 2100.";
      }

      if (
        this.form
          .mes_publicacion !== ""
      ) {
        const publicationMonth =
          Number(
            this.form
              .mes_publicacion
          );

        if (
          !Number.isInteger(
            publicationMonth
          ) ||
          publicationMonth < 1 ||
          publicationMonth > 12
        ) {
          errors.mes_publicacion =
            "Seleccione un mes válido.";
        }
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

      if (
        this.form
          .factor_impacto ===
          "jcr" &&

        !String(
          this.form.jcr ||
          ""
        ).trim()
      ) {
        errors.jcr =
          "Ingrese el valor JCR o seleccione otro factor.";
      }

      if (
        exceedsLength(
          this.form.jcr,
          FIELD_LIMITS.jcr
        )
      ) {
        errors.jcr =
          `El valor JCR no puede superar ${FIELD_LIMITS.jcr} caracteres.`;
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

    async registrarArticulo({ skipFrontValidation = false } = {}) {
      if (
        this.loading
      ) {
        return;
      }

      this.loading =
        true;

      if (!skipFrontValidation) {
        this.clearErrors();
      }

      try {
        if (
          !skipFrontValidation &&
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
        // Prevalidación backend
        // ----------------------------------------------------

        const prevalidacionOk =
          await this.ejecutarPrevalidacion(
            autoresPayload
          );

        if (!prevalidacionOk) {
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
          "anio_publicacion",
          "mes_publicacion",
          "codigo_doi",
          "codigo_issn",
          "nombre_revista",
          "numero_revista",
          "link_revista",
          "link_publicacion",
          "factor_impacto",
          "cuartil",
          "sjr",
          "jcr",
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
          this.selectedUploadItems(),
          {
            primaryField:
              "archivo_pdf",

            filesField:
              "archivos",

            metaField:
              "archivos_meta",
          }
        );

        // ----------------------------------------------------
        // Request
        // ----------------------------------------------------

        const response = await api.post(
          this.createEndpoint,
          formData
        );

        const responseData =
          response?.data || {};

        const publicacionId = Number(
          responseData?.articulo?.publicacion_id ??
          responseData?.publicacion?.id ??
          responseData?.publicacion_id ??
          0
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
            ? "Artículo guardado correctamente para el usuario seleccionado. La publicación quedó en estado Borrador y puede editarse o enviarse a revisión desde la gestión de publicaciones."
            : "La publicación se guardó correctamente y quedó en estado Borrador. Revise la información y edítela si es necesario antes de enviarla a revisión. Una vez enviada, la edición quedará bloqueada hasta que el administrador apruebe, rechace o solicite correcciones.";

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

      this.clearPrevalidationState();

      this.draftInfo =
        "";

      this.showDiscardDraftDialog =
        false;

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
