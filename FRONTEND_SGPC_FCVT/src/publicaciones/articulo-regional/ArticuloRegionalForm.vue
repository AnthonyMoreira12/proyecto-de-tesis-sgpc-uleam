<template>
  <div class="sgpc-form-page sgpc-form-page--articulo-regional">
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
        aria-label="Formulario para registrar un artículo regional"
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
                id="ar-admin-context-anchor"
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
                id="ar-admin-context-error"
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
                v-model="formDatos"
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
                    for="ar-origen_tipo"
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
                    id="ar-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    :aria-invalid="Boolean(fieldErrors.origen_tipo)"
                    :aria-describedby="
                      fieldErrors.origen_tipo
                        ? 'ar-origen-tipo-error'
                        : undefined
                    "
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
                    id="ar-origen-tipo-error"
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
                    for="ar-origen_grado"
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
                    id="ar-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    required
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="
                      fieldErrors.origen_grado
                        ? 'ar-origen-grado-error'
                        : undefined
                    "
                    :placeholder="
                      form.origen_tipo === 'otro'
                        ? 'Ej. Proyecto de investigación institucional'
                        : 'Ej. Ingeniería en Tecnologías de la Información'
                    "
                  />

                  <p class="sgpc-hint">
                    {{
                      form.origen_tipo === "otro"
                        ? "Indique de qué trabajo, proyecto o proceso se originó."
                        : "Indique la carrera o programa relacionado con el trabajo."
                    }}
                  </p>

                  <p
                    v-if="fieldErrors.origen_grado"
                    id="ar-origen-grado-error"
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
               DATOS PRINCIPALES
          ================================================== -->

          <section
            id="sec-principales"
            class="sgpc-card"
            data-section="03"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Información del artículo
                </h2>

                <p class="sgpc-card-desc">
                  Ingrese el título, la fecha y la base de datos donde está indexado.
                </p>
              </div>

              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredMain, optionalMainMissingCount)"
              >
                {{ sectionStateLabel(hasRequiredMain, optionalMainMissingCount) }}
              </span>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-3">
                  <label
                    class="sgpc-label"
                    for="ar-anio_publicacion"
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
                    id="ar-anio_publicacion"
                    v-model.number="form.anio_publicacion"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    placeholder="Ej. 2026"
                    :aria-invalid="Boolean(fieldErrors.anio_publicacion)"
                    :aria-describedby="
                      fieldErrors.anio_publicacion
                        ? 'ar-anio-publicacion-error'
                        : undefined
                    "
                    required
                  />

                  <p
                    v-if="fieldErrors.anio_publicacion"
                    id="ar-anio-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.anio_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-3">
                  <label
                    class="sgpc-label"
                    for="ar-mes_publicacion"
                  >
                    Mes de publicación
                    <span class="sgpc-label-optional">
                      (opcional)
                    </span>
                  </label>

                  <select
                    id="ar-mes_publicacion"
                    v-model="form.mes_publicacion"
                    class="sgpc-input"
                    :aria-invalid="Boolean(fieldErrors.mes_publicacion)"
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
                    id="ar-mes-publicacion-help"
                    class="sgpc-hint"
                  >
                    Puede dejar el mes vacío si no consta en la fuente bibliográfica.
                  </p>

                  <p
                    v-if="fieldErrors.mes_publicacion"
                    id="ar-mes-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.mes_publicacion }}
                  </p>
                </div>


                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="ar-nombre_articulo"
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
                    id="ar-nombre_articulo"
                    v-model.trim="form.nombre_articulo"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    :aria-invalid="Boolean(fieldErrors.nombre_articulo)"
                    :aria-describedby="
                      fieldErrors.nombre_articulo
                        ? 'ar-nombre-articulo-error'
                        : undefined
                    "
                    required
                    placeholder="Ej. Análisis regional de la producción científica"
                  />

                  <p
                    v-if="fieldErrors.nombre_articulo"
                    id="ar-nombre-articulo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_articulo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-base_datos_indexada"
                  >
                    Base de datos de indexación
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <select
                    id="ar-base_datos_indexada"
                    v-model="form.base_datos_indexada"
                    class="sgpc-input"
                    :aria-invalid="Boolean(fieldErrors.base_datos_indexada)"
                    :aria-describedby="
                      fieldErrors.base_datos_indexada
                        ? 'ar-base-datos-indexada-error'
                        : undefined
                    "
                    required
                  >
                    <option
                      disabled
                      value=""
                    >
                      Seleccione una opción
                    </option>

                    <option value="latindex">
                      Latindex
                    </option>

                    <option value="scielo">
                      SciELO
                    </option>

                    <option value="redalyc">
                      Redalyc
                    </option>

                    <option value="dialnet">
                      Dialnet
                    </option>

                    <option value="google_scholar">
                      Google Scholar
                    </option>

                    <option value="otra">
                      Otra
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.base_datos_indexada"
                    id="ar-base-datos-indexada-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.base_datos_indexada }}
                  </p>
                </div>

                <div
                  v-if="form.base_datos_indexada === 'otra'"
                  class="sgpc-field sgpc-col-span-6"
                >
                  <label
                    class="sgpc-label"
                    for="ar-base_datos_otra"
                  >
                    Especifique la base de datos
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="ar-base_datos_otra"
                    v-model.trim="form.base_datos_otra"
                    class="sgpc-input"
                    type="text"
                    maxlength="150"
                    :aria-invalid="Boolean(fieldErrors.base_datos_otra)"
                    :aria-describedby="
                      fieldErrors.base_datos_otra
                        ? 'ar-base-datos-otra-error'
                        : undefined
                    "
                    required
                    placeholder="Ej. Repositorio institucional / Revista local / ..."
                  />

                  <p
                    v-if="fieldErrors.base_datos_otra"
                    id="ar-base-datos-otra-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.base_datos_otra }}
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
                  Revista y enlaces
                </h2>

                <p class="sgpc-card-desc">
                  Complete los datos de la revista y agregue los enlaces disponibles.
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
                  <span>Datos principales de la revista donde se publicó el artículo.</span>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-codigo_issn"
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
                    id="ar-codigo_issn"
                    v-model.trim="form.codigo_issn"
                    class="sgpc-input"
                    type="text"
                    maxlength="100"
                    :aria-invalid="Boolean(fieldErrors.codigo_issn)"
                    :aria-describedby="
                      fieldErrors.codigo_issn
                        ? 'ar-codigo-issn-error'
                        : undefined
                    "
                    required
                    placeholder="Ej. 1234-5678"
                  />

                  <p
                    v-if="fieldErrors.codigo_issn"
                    id="ar-codigo-issn-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_issn }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-codigo_doi"
                  >
                    DOI
                  </label>

                  <input
                    id="ar-codigo_doi"
                    v-model.trim="form.codigo_doi"
                    class="sgpc-input"
                    type="text"
                    maxlength="150"
                    :aria-invalid="Boolean(fieldErrors.codigo_doi)"
                    :aria-describedby="
                      fieldErrors.codigo_doi
                        ? 'ar-codigo-doi-error'
                        : undefined
                    "
                    placeholder="Ej. 10.1234/abcd.2025"
                  />

                  <p
                    v-if="fieldErrors.codigo_doi"
                    id="ar-codigo-doi-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_doi }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="ar-nombre_revista"
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
                    id="ar-nombre_revista"
                    v-model.trim="form.nombre_revista"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    :aria-invalid="Boolean(fieldErrors.nombre_revista)"
                    :aria-describedby="
                      fieldErrors.nombre_revista
                        ? 'ar-nombre-revista-error'
                        : undefined
                    "
                    required
                    placeholder="Ej. Revista Científica Regional"
                  />

                  <p
                    v-if="fieldErrors.nombre_revista"
                    id="ar-nombre-revista-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-numero_revista"
                  >
                    Número de la revista
                  </label>

                  <input
                    id="ar-numero_revista"
                    v-model.number="form.numero_revista"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    :aria-invalid="Boolean(fieldErrors.numero_revista)"
                    :aria-describedby="
                      fieldErrors.numero_revista
                        ? 'ar-numero-revista-error'
                        : undefined
                    "
                    placeholder="Ej. 12"
                  />

                  <p
                    v-if="fieldErrors.numero_revista"
                    id="ar-numero-revista-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.numero_revista }}
                  </p>
                </div>

                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Enlaces</strong>
                  <span>Agregue los enlaces solo si están disponibles.</span>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-link_revista"
                  >
                    Enlace de la revista
                  </label>

                  <input
                    id="ar-link_revista"
                    v-model.trim="form.link_revista"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    :aria-invalid="Boolean(fieldErrors.link_revista)"
                    :aria-describedby="
                      fieldErrors.link_revista
                        ? 'ar-link-revista-error'
                        : undefined
                    "
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_revista"
                    id="ar-link-revista-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-link_publicacion"
                  >
                    Enlace de la publicación
                  </label>

                  <input
                    id="ar-link_publicacion"
                    v-model.trim="form.link_publicacion"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    :aria-invalid="Boolean(fieldErrors.link_publicacion)"
                    :aria-describedby="
                      fieldErrors.link_publicacion
                        ? 'ar-link-publicacion-error'
                        : undefined
                    "
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_publicacion"
                    id="ar-link-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_publicacion }}
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
                id="ar-autores-anchor"
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
                input-id="ar-archivo-input"
                title=""
                description=""
                helper-text=""
                :multiple="true"
                :max-files="3"
                :uses-primary-slot="true"
                :primary-max-size-mb="5"
                :attachment-max-size-mb="3"
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
            <span>Corrija los siguientes puntos antes de registrar:</span>
            <ul>
              <li
                v-for="(item, index) in prevalidacionBloqueantes"
                :key="`ar-pre-block-${item.codigo || index}`"
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
            <span>Estas observaciones no impiden el registro, pero conviene verificarlas antes de continuar:</span>
            <ul>
              <li
                v-for="(item, index) in prevalidacionAdvertencias"
                :key="`ar-pre-warning-${item.codigo || index}`"
              >
                {{ item.mensaje }}
              </li>
            </ul>
          </div>

          <!-- =================================================
               MENSAJES
          ================================================== -->

          <div
            v-if="successMessage"
            class="sgpc-alert is-success"
            role="status"
            aria-live="polite"
          >
            {{ successMessage }}
          </div>

          <div
            v-if="errorMessage"
            class="sgpc-alert is-error"
            role="alert"
            aria-live="assertive"
          >
            {{ errorMessage }}
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
              <strong>
                Falta completar
              </strong>

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
                  {{ loading ? submitLoadingText : submitText }}
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
          aria-labelledby="ar-discard-draft-title"
          aria-describedby="ar-discard-draft-description"
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
            <h2 id="ar-discard-draft-title">
              ¿Descartar este borrador?
            </h2>

            <p id="ar-discard-draft-description">
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

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

import { useRoute } from "vue-router";

import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import api from "../../scripts/api/axios";
import {
  prevalidarPublicacion,
} from "../../scripts/api/publicacionesApi";
import { useNotice } from "../../scripts/composables/useNotice.js";

import {
  appendArchivosToFormData,
  restoreDraftArchivos,
  serializeDraftArchivos,
} from "../../scripts/utils/adjuntosPdf";


defineOptions({
  name: "ArticuloRegionalForm",
});


const route = useRoute();


const {
  notice: prevalidationNotice,
  openNotice: openPrevalidationNotice,
  closeNotice: closePrevalidationNoticeBase,
} = useNotice();

let prevalidationDecisionResolver = null;


function resolvePrevalidationDecision(value) {
  const resolver =
    prevalidationDecisionResolver;

  prevalidationDecisionResolver =
    null;

  if (
    typeof resolver ===
    "function"
  ) {
    resolver(
      Boolean(value)
    );
  }
}


function closePrevalidationNotice() {
  resolvePrevalidationDecision(
    false
  );

  closePrevalidationNoticeBase();
}


function confirmarAdvertenciasPrevalidacion(
  advertencias = []
) {
  const items =
    Array.isArray(advertencias)
      ? advertencias
      : [];

  if (!items.length) {
    return Promise.resolve(true);
  }

  closePrevalidationNotice();

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
      prevalidationDecisionResolver =
        resolve;

      openPrevalidationNotice({
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
          resolvePrevalidationDecision(
            true
          );
        },
        onCancel: () => {
          resolvePrevalidationDecision(
            false
          );
        },
      });
    }
  );
}


/* =========================================================
   CONFIGURACIÓN
========================================================= */

const BASE_DRAFT_KEY =
  "sgpc:draft:articulo_regional:v24";

const STANDARD_CREATE_ENDPOINT =
  "/publicaciones/articulos/crear/";

const ADMIN_CREATE_ENDPOINT =
  "/admin/publicaciones/articulos/crear/";


const FIELD_LIMITS = Object.freeze({
  origen_grado: 120,
  nombre_articulo: 255,
  base_datos_otra: 150,
  codigo_issn: 100,
  codigo_doi: 150,
  nombre_revista: 255,
  link_revista: 500,
  link_publicacion: 500,
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


const REGIONAL_DATABASES = new Set([
  "latindex",
  "scielo",
  "redalyc",
  "dialnet",
  "google_scholar",
  "otra",
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
  origen_tipo: "Origen académico",
  origen_grado: "Carrera, programa u otro origen",
  nombre_articulo: "Título del artículo",
  base_datos_indexada: "Base de datos de indexación",
  base_datos_otra: "Base de datos (otra)",
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",
  codigo_issn: "ISSN",
  codigo_doi: "DOI",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_revista: "Enlace de la revista",
  link_publicacion: "Enlace de la publicación",
  autores: "Autores",
  archivos: "Documentos",
});


const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "tipo_codigo",
  "sede",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "origen_tipo",
  "origen_grado",
  "anio_publicacion",
  "mes_publicacion",
  "nombre_articulo",
  "base_datos_indexada",
  "base_datos_otra",
  "codigo_issn",
  "codigo_doi",
  "nombre_revista",
  "numero_revista",
  "link_revista",
  "link_publicacion",
  "autores",
  "archivos",
  "general",
]);


/* =========================================================
   ESTADO INICIAL
========================================================= */

function createDefaultFormDatos() {
  return {
    sede: null,
    facultad: null,
    carrera: null,
    proyecto: null,
    area: null,
    subarea: null,
    pais: null,
    ciudad: null,
  };
}


function createDefaultForm() {
  return {
    origen_tipo: "",
    origen_grado: "",

    nombre_articulo: "",
    base_datos_indexada: "",
    base_datos_otra: "",
    anio_publicacion: null,
    mes_publicacion: "",

    codigo_issn: "",
    codigo_doi: "",
    nombre_revista: "",
    numero_revista: null,
    link_revista: "",
    link_publicacion: "",

    autores: [],
    archivos: [],
  };
}


/* =========================================================
   HELPERS
========================================================= */

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

        fields[normalizedKey] =
          message;

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


function appendFormValue(
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


/* =========================================================
   ESTADO
========================================================= */

const adminContext = ref({
  usuarioId: null,
  autorId: null,
  usuarioNombre: "",
  autorNombre: "",
});


const formDatos = ref(
  createDefaultFormDatos()
);


const form = ref(
  createDefaultForm()
);


const loading = ref(false);

const successMessage = ref("");
const errorMessage = ref("");

const fieldErrors = ref({});

const prevalidacionBloqueantes = ref([]);
const prevalidacionAdvertencias = ref([]);
const prevalidacionResumen = ref(null);

const draftInfo = ref("");
const showDiscardDraftDialog = ref(false);
const discardDraftDialog = ref(null);

let draftTimer = null;
let draftEnabled = true;


/* =========================================================
   CONTEXTO ADMINISTRATIVO
========================================================= */

const isAdminDelegado = computed(() => {
  const path = String(
    route.path || ""
  );

  return Boolean(
    route.meta?.delegatedPublication ||

    path.startsWith(
      "/admin/publicaciones/usuario/"
    )
  );
});


const storageKey = computed(() => {
  if (
    !isAdminDelegado.value
  ) {
    return (
      `${BASE_DRAFT_KEY}:self`
    );
  }

  const usuarioId =
    adminContext.value
      .usuarioId ||

    Number(
      route.params
        ?.usuarioId ||
      0
    ) ||

    "sin-usuario";

  return (
    `${BASE_DRAFT_KEY}:admin:${usuarioId}`
  );
});


const adminDisplayUsuario =
  computed(() => {
    return (
      adminContext.value.usuarioNombre || "Usuario seleccionado"
    );
  });


const adminDisplayAutor =
  computed(() => {
    if (
      adminContext.value
        .autorNombre
    ) {
      return (
        adminContext.value
          .autorNombre
      );
    }

    if (
      adminContext.value
        .autorId
    ) {
      return (
        `ID ${
          adminContext.value
            .autorId
        }`
      );
    }

    return (
      "Se resolverá automáticamente"
    );
  });


const showAutorObjetivo =
  computed(() => {
    if (
      !isAdminDelegado.value
    ) {
      return false;
    }

    /*
     * Usuario.id y Autor.id son identificadores
     * de entidades diferentes, por lo que no deben
     * compararse entre sí.
     */
    return Boolean(
      adminContext.value
        .autorId ||

      String(
        adminContext.value
          .autorNombre ||
        ""
      ).trim()
    );
  });


const adminReady =
  computed(() => {
    return (
      !isAdminDelegado.value ||
      Boolean(
        adminContext.value
          .usuarioId
      )
    );
  });


/* =========================================================
   TEXTOS DEL FORMULARIO
========================================================= */

const pageKicker = computed(
  () => {
    return (
      isAdminDelegado.value
        ? "Administración · Artículos"
        : "Artículos"
    );
  }
);


const pageTitle = computed(
  () => {
    return (
      "Registrar artículo regional"
    );
  }
);


const pageSubtitle = computed(
  () => {
    return (
      "Complete los datos de la publicación. Los campos con * son obligatorios."
    );
  }
);


const submitText = computed(
  () => {
    return (
      "Registrar artículo regional"
    );
  }
);


const submitLoadingText =
  computed(() => {
    return "Guardando...";
  });


const createEndpoint = computed(
  () => {
    return (
      isAdminDelegado.value
        ? ADMIN_CREATE_ENDPOINT
        : STANDARD_CREATE_ENDPOINT
    );
  }
);


/* =========================================================
   PROGRESO
========================================================= */

const publicationMonths =
  computed(() =>
    PUBLICATION_MONTHS
  );


const monthDescriptionIds =
  computed(() => {
    const ids = [
      "ar-mes-publicacion-help",
    ];

    if (
      fieldErrors.value
        .mes_publicacion
    ) {
      ids.push(
        "ar-mes-publicacion-error"
      );
    }

    return ids.join(" ");
  });


const hasRequiredContext =
  computed(() => {
    const general =
      formDatos.value || {};

    return Boolean(
      general.sede &&
      general.facultad &&
      general.carrera
    );
  });


const hasRequiredOrigin =
  computed(() => {
    if (
      !form.value
        .origen_tipo
    ) {
      return false;
    }

    if (
      ["tic", "otro"].includes(form.value
        .origen_tipo)
    ) {
      return Boolean(
        String(
          form.value
            .origen_grado ||
          ""
        ).trim()
      );
    }

    return true;
  });


const hasRequiredMain =
  computed(() => {
    const publicationYear =
      Number(
        form.value
          .anio_publicacion
      );

    if (
      !Number.isInteger(
        publicationYear
      ) ||
      publicationYear < 1900 ||
      publicationYear > 2100
    ) {
      return false;
    }

    if (
      !String(
        form.value
          .nombre_articulo ||
        ""
      ).trim()
    ) {
      return false;
    }

    if (
      !String(
        form.value
          .base_datos_indexada ||
        ""
      ).trim()
    ) {
      return false;
    }

    if (
      form.value
        .base_datos_indexada ===
        "otra" &&

      !String(
        form.value
          .base_datos_otra ||
        ""
      ).trim()
    ) {
      return false;
    }

    return true;
  });


const hasRequiredJournal =
  computed(() => {
    if (
      !String(
        form.value
          .codigo_issn ||
        ""
      ).trim()
    ) {
      return false;
    }

    if (
      !String(
        form.value
          .nombre_revista ||
        ""
      ).trim()
    ) {
      return false;
    }

    return true;
  });


const hasRequiredAuthors =
  computed(() => {
    return (
      Array.isArray(
        form.value.autores
      ) &&

      form.value
        .autores
        .length >
        0
    );
  });


const hasAdjuntos =
  computed(() => {
    return (
      Array.isArray(
        form.value.archivos
      ) &&

      form.value
        .archivos
        .length >
        0
    );
  });


const optionalMissingItems =
  computed(() => {
    const general =
      formDatos.value || {};

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
        sectionLabel: "Información académica",
      });
    } else if (!hasValue(general.subarea)) {
      items.push({
        key: "subarea",
        label: "Subárea del conocimiento (UNESCO)",
        section: "datos",
        sectionLabel: "Información académica",
      });
    }

    if (!hasValue(form.value.mes_publicacion)) {
      items.push({
        key: "mes_publicacion",
        label: "Mes de publicación",
        section: "principal",
        sectionLabel: "Información del artículo",
      });
    }

    if (!hasValue(form.value.codigo_doi)) {
      items.push({
        key: "codigo_doi",
        label: "DOI",
        section: "revista",
        sectionLabel: "Revista y enlaces",
      });
    }

    if (!hasValue(form.value.numero_revista)) {
      items.push({
        key: "numero_revista",
        label: "Número de la revista",
        section: "revista",
        sectionLabel: "Revista y enlaces",
      });
    }

    if (!hasValue(form.value.link_revista)) {
      items.push({
        key: "link_revista",
        label: "Enlace de la revista",
        section: "revista",
        sectionLabel: "Revista y enlaces",
      });
    }

    if (!hasValue(form.value.link_publicacion)) {
      items.push({
        key: "link_publicacion",
        label: "Enlace de la publicación",
        section: "revista",
        sectionLabel: "Revista y enlaces",
      });
    }

    if (!hasAdjuntos.value) {
      items.push({
        key: "archivos",
        label: "Documentos",
        section: "adjuntos",
        sectionLabel: "Documentos",
      });
    }

    return items;
  });


const optionalMissingCount =
  computed(() =>
    optionalMissingItems.value.length
  );


const totalOptionalCount =
  computed(() => {
    const general =
      formDatos.value || {};

    const hasArea =
      general.area !== null &&
      general.area !== undefined &&
      String(general.area).trim() !== "";

    /*
     * Proyecto, área, mes, DOI, número de revista,
     * link de revista, link de publicación y adjuntos.
     * La subárea solo aplica cuando existe un área elegida.
     */
    return 8 +
      (hasArea ? 1 : 0);
  });


const optionalCompletedCount =
  computed(() => {
    return Math.max(
      0,
      totalOptionalCount.value -
        optionalMissingCount.value
    );
  });


const optionalContextMissingCount =
  computed(() => {
    return optionalMissingItems.value
      .filter(
        (item) =>
          item.section === "datos"
      )
      .length;
  });


const optionalMainMissingCount =
  computed(() => {
    return optionalMissingItems.value
      .filter(
        (item) =>
          item.section === "principal"
      )
      .length;
  });


const optionalJournalMissingCount =
  computed(() => {
    return optionalMissingItems.value
      .filter(
        (item) =>
          item.section === "revista"
      )
      .length;
  });


function sectionStatusText() {
  return "Listo";
}


function sectionStateLabel(
  requiredDone
) {
  return requiredDone
    ? "Listo"
    : "Falta información";
}


function sectionStateClass(
  requiredDone
) {
  return requiredDone
    ? "is-complete"
    : "is-pending";
}


const summarySections =
  computed(() => {
    const sections = [
      {
        key: "datos",
        target: "sec-datos-generales",
        label: "Información académica",
        done: hasRequiredContext.value,
        required: true,
        optionalMissing:
          optionalContextMissingCount.value,
        detail:
          hasRequiredContext.value
            ? "Listo"
            : "Complete sede, facultad y carrera",
        status:
          hasRequiredContext.value
            ? "Listo"
            : "Falta información",
      },
      {
        key: "origen",
        target: "sec-origen",
        label: "Origen académico",
        done: hasRequiredOrigin.value,
        required: true,
        optionalMissing: 0,
        detail:
          hasRequiredOrigin.value
            ? "Listo"
            : "Seleccione el origen",
        status:
          hasRequiredOrigin.value
            ? "Listo"
            : "Falta información",
      },
      {
        key: "principal",
        target: "sec-principales",
        label: "Información del artículo",
        done: hasRequiredMain.value,
        required: true,
        optionalMissing:
          optionalMainMissingCount.value,
        detail:
          hasRequiredMain.value
            ? "Listo"
            : "Complete título, año e indexación",
        status:
          hasRequiredMain.value
            ? "Listo"
            : "Falta información",
      },
      {
        key: "revista",
        target: "sec-revista",
        label: "Revista y enlaces",
        done: hasRequiredJournal.value,
        required: true,
        optionalMissing:
          optionalJournalMissingCount.value,
        detail:
          hasRequiredJournal.value
            ? "Listo"
            : "Complete revista e ISSN",
        status:
          hasRequiredJournal.value
            ? "Listo"
            : "Falta información",
      },
      {
        key: "autores",
        target: "sec-autores",
        label: "Autores",
        done: hasRequiredAuthors.value,
        required: true,
        optionalMissing: 0,
        detail:
          hasRequiredAuthors.value
            ? "Listo"
            : "Agregue al menos un autor",
        status:
          hasRequiredAuthors.value
            ? "Listo"
            : "Falta información",
      },
      {
        key: "documentos",
        target: "sec-adjuntos",
        label: "Documentos",
        done: hasAdjuntos.value,
        required: false,
        optionalMissing:
          hasAdjuntos.value ? 0 : 1,
        detail:
          hasAdjuntos.value
            ? "Documentos agregados"
            : "Opcional",
        status:
          hasAdjuntos.value
            ? "Listo"
            : "Opcional",
      },
    ];

    if (isAdminDelegado.value) {
      return [
        {
          key: "admin",
          target: "sec-contexto-admin",
          label: "Persona seleccionada",
          done: adminReady.value,
          required: true,
          optionalMissing: 0,
          detail:
            adminReady.value
              ? "Listo"
              : "Seleccione la persona",
          status:
            adminReady.value
              ? "Listo"
              : "Falta información",
        },
        ...sections,
      ];
    }

    return sections;
  });


const pendingRequiredSections =
  computed(() => {
    return summarySections.value
      .filter(
        (section) =>
          section.required &&
          !section.done
      );
  });


const requiredSections =
  computed(() => {
    return summarySections.value
      .filter(
        (section) =>
          section.required
      );
  });


const completedRequiredCount =
  computed(() => {
    return requiredSections.value
      .filter(
        (section) =>
          section.done
      )
      .length;
  });


const totalRequiredCount =
  computed(() =>
    requiredSections.value.length
  );


const progressPercent =
  computed(() => {
    if (!totalRequiredCount.value) {
      return 0;
    }

    return Math.round(
      (
        completedRequiredCount.value /
        totalRequiredCount.value
      ) *
      100
    );
  });


const canSubmit =
  computed(() => {
    return Boolean(
      totalRequiredCount.value > 0 &&
      completedRequiredCount.value ===
        totalRequiredCount.value
    );
  });


/* =========================================================
   NAVEGACIÓN Y FOCO
========================================================= */

const goTo = (id) => {
  const element =
    document.getElementById(
      id
    );

  element?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
};


function focusField(key) {
  const map = {
    admin_context:
      "ar-admin-context-anchor",

    origen_tipo:
      "ar-origen_tipo",

    origen_grado:
      "ar-origen_grado",

    anio_publicacion:
      "ar-anio_publicacion",

    mes_publicacion:
      "ar-mes_publicacion",

    nombre_articulo:
      "ar-nombre_articulo",

    base_datos_indexada:
      "ar-base_datos_indexada",

    base_datos_otra:
      "ar-base_datos_otra",

    codigo_issn:
      "ar-codigo_issn",

    codigo_doi:
      "ar-codigo_doi",

    nombre_revista:
      "ar-nombre_revista",

    numero_revista:
      "ar-numero_revista",

    link_revista:
      "ar-link_revista",

    link_publicacion:
      "ar-link_publicacion",

    autores:
      "ar-autores-anchor",

    archivos:
      "ar-archivo-input",
  };

  const element =
    document.getElementById(
      `dg-${key}`
    ) ||

    document.getElementById(
      map[key] || ""
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
}


function focusOptionalItem(item) {
  if (!item) {
    return;
  }

  if (item.key === "archivos") {
    goTo("sec-adjuntos");
    return;
  }

  focusField(item.key);
}


function reviewOptionalFields() {
  const first =
    optionalMissingItems.value[0];

  if (!first) {
    return;
  }

  nextTick(() => {
    focusOptionalItem(first);
  });
}


async function handleSubmitIntent() {
  if (loading.value) {
    return;
  }

  successMessage.value = "";
  errorMessage.value = "";
  fieldErrors.value = {};

  if (!validateFront()) {
    return;
  }

  await registrarArticuloRegional({
    skipFrontValidation: true,
  });
}


/* =========================================================
   CONTEXTO DE RUTA
========================================================= */

function hydrateAdminContextFromRoute() {
  const query =
    route.query || {};

  const params =
    route.params || {};

  const usuarioId =
    Number(
      params.usuarioId ||

      query.usuario_objetivo_id ||

      query.usuario_id ||

      query.usuarioId ||

      query.user_id ||

      0
    );

  const autorId =
    Number(
      params.autorId ||

      query.autor_objetivo_id ||

      query.autor_id ||

      query.autorId ||

      0
    );

  adminContext.value = {
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
}


/* =========================================================
   BORRADOR
========================================================= */

function normalizeRecoveredPeriod(
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

  const legacyKey =
    [
      "fecha",
      "publicacion",
    ].join("_");

  const legacyValue =
    String(
      recovered?.[
        legacyKey
      ] ||
      ""
    ).trim();

  const legacyMatch =
    legacyValue.match(
      /^(\d{4})-(\d{2})/
    );

  if (legacyMatch) {
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
}


function saveDraft() {
  if (
    !draftEnabled
  ) {
    return;
  }

  clearTimeout(
    draftTimer
  );

  draftTimer =
    window.setTimeout(
      () => {
        try {
          const payload = {
            formDatos: {
              ...formDatos.value,

              pais: null,
              ciudad: null,
            },

            form: {
              origen_tipo:
                form.value
                  .origen_tipo,

              origen_grado:
                form.value
                  .origen_grado,

              nombre_articulo:
                form.value
                  .nombre_articulo,

              base_datos_indexada:
                form.value
                  .base_datos_indexada,

              base_datos_otra:
                form.value
                  .base_datos_otra,

              anio_publicacion:
                form.value
                  .anio_publicacion,

              mes_publicacion:
                form.value
                  .mes_publicacion,

              codigo_issn:
                form.value
                  .codigo_issn,

              codigo_doi:
                form.value
                  .codigo_doi,

              nombre_revista:
                form.value
                  .nombre_revista,

              numero_revista:
                form.value
                  .numero_revista,

              link_revista:
                form.value
                  .link_revista,

              link_publicacion:
                form.value
                  .link_publicacion,

              autores:
                form.value
                  .autores,

              archivos:
                serializeDraftArchivos(
                  form.value
                    .archivos
                ),
            },

            updatedAt:
              new Date()
                .toISOString(),
          };

          localStorage.setItem(
            storageKey.value,
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
      300
    );
}


function loadDraft() {
  let raw = null;

  try {
    raw =
      localStorage.getItem(
        storageKey.value
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

    disableDraftTemporarily();

    if (
      parsed?.formDatos
    ) {
      formDatos.value = {
        ...createDefaultFormDatos(),
        ...parsed.formDatos,

        pais: null,
        ciudad: null,
      };
    }

    if (
      parsed?.form
    ) {
      const incoming =
        parsed.form || {};

      form.value = {
        ...createDefaultForm(),

        origen_tipo:
          incoming.origen_tipo ||
          "",

        origen_grado:
          incoming.origen_grado ||
          "",

        nombre_articulo:
          incoming.nombre_articulo ||
          "",

        base_datos_indexada:
          incoming.base_datos_indexada ||
          "",

        base_datos_otra:
          incoming.base_datos_otra ||
          "",

        anio_publicacion:
          normalizeRecoveredPeriod(
            incoming
          ).anio_publicacion,

        mes_publicacion:
          normalizeRecoveredPeriod(
            incoming
          ).mes_publicacion,

        codigo_issn:
          incoming.codigo_issn ||
          "",

        codigo_doi:
          incoming.codigo_doi ||
          "",

        nombre_revista:
          incoming.nombre_revista ||
          "",

        numero_revista:
          incoming.numero_revista ??
          null,

        link_revista:
          incoming.link_revista ||
          "",

        link_publicacion:
          incoming.link_publicacion ||
          "",

        autores:
          Array.isArray(
            incoming.autores
          )
            ? incoming.autores
            : [],

        archivos:
          restoreDraftArchivos(
            incoming.archivos
          ),
      };
    }

    draftInfo.value =
      "Borrador recuperado. Puede continuar donde lo dejó.";

    successMessage.value =
      "";

    errorMessage.value =
      "";
  } catch (error) {
    console.warn(
      "El borrador está dañado y se ignorará.",
      error
    );
  }
}


function clearDraftStorage() {
  try {
    localStorage.removeItem(
      storageKey.value
    );
  } catch (error) {
    console.warn(
      "No se pudo limpiar el borrador.",
      error
    );
  }
}


function disableDraftTemporarily() {
  draftEnabled =
    false;

  nextTick(
    () => {
      draftEnabled =
        true;
    }
  );
}


/* =========================================================
   PREVALIDACIÓN BACKEND
========================================================= */

function clearPrevalidationState() {
  prevalidacionBloqueantes.value = [];
  prevalidacionAdvertencias.value = [];
  prevalidacionResumen.value = null;
}

function normalizePrevalidationIssues(items) {
  return (Array.isArray(items) ? items : [])
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
        item?.mensaje ?? item?.message ?? item?.detail ?? ""
      ).trim();

      if (!mensaje) return null;

      return {
        codigo: String(
          item?.codigo ?? item?.code ?? `validacion-${index}`
        ).trim(),
        nivel: String(item?.nivel || "").trim(),
        campo: item?.campo ? String(item.campo).trim() : null,
        mensaje,
        origen: String(item?.origen || "validacion").trim(),
        metadata:
          item?.metadata && typeof item.metadata === "object"
            ? item.metadata
            : {},
      };
    })
    .filter(Boolean);
}

function applyPrevalidationFieldErrors(items) {
  const next = { ...fieldErrors.value };

  normalizePrevalidationIssues(items).forEach((item) => {
    const rawField = String(item.campo || "").trim();
    if (!rawField) return;

    const field = ERROR_KEY_ALIASES[rawField] || rawField;
    if (!next[field]) next[field] = item.mensaje;
  });

  fieldErrors.value = next;
}

function selectedUploadItems() {
  return (Array.isArray(form.value.archivos) ? form.value.archivos : [])
    .filter((item) => item?.file);
}

function buildPrevalidationPayload(autoresPayload) {
  const general = formDatos.value || {};
  const uploadItems = selectedUploadItems();

  return {
    tipo_codigo: "articulo_regional",
    sede: general.sede || null,
    facultad: general.facultad || null,
    carrera: general.carrera || null,
    proyecto: general.proyecto || null,
    area: general.area || null,
    subarea: general.subarea || null,
    origen_tipo: form.value.origen_tipo || "ninguno",
    origen_grado: form.value.origen_grado || "",
    nombre_articulo: String(form.value.nombre_articulo || "").trim(),
    anio_publicacion: form.value.anio_publicacion,
    mes_publicacion: form.value.mes_publicacion || null,
    base_datos_indexada: String(form.value.base_datos_indexada || "").trim().toLowerCase(),
    base_datos_otra: String(form.value.base_datos_otra || "").trim(),
    codigo_issn: String(form.value.codigo_issn || "").trim(),
    codigo_doi: String(form.value.codigo_doi || "").trim(),
    nombre_revista: String(form.value.nombre_revista || "").trim(),
    numero_revista: form.value.numero_revista || null,
    link_revista: String(form.value.link_revista || "").trim(),
    link_publicacion: String(form.value.link_publicacion || "").trim(),
    autores: autoresPayload,
    archivo_pdf: uploadItems[0]?.file || null,
    registrado_por_admin: isAdminDelegado.value,
    usuario_objetivo_id: isAdminDelegado.value ? adminContext.value.usuarioId : null,
    autor_objetivo_id: isAdminDelegado.value ? adminContext.value.autorId : null,
  };
}

async function ejecutarPrevalidacion(autoresPayload) {
  clearPrevalidationState();

  let response;

  try {
    response = await prevalidarPublicacion(
      buildPrevalidationPayload(autoresPayload)
    );
  } catch (error) {
    const normalized = normalizeDrfErrors(error?.response?.data);

    fieldErrors.value = {
      ...fieldErrors.value,
      ...(normalized.fields || {}),
    };
    errorMessage.value =
      normalized.message ||
      "No se pudo verificar la información antes del registro. Revise los datos e inténtelo nuevamente.";
    successMessage.value = "";

    const first = firstErrorField(fieldErrors.value);
    if (first) nextTick(() => focusField(first));
    return false;
  }

  const bloqueantes = normalizePrevalidationIssues(response?.bloqueantes);
  const advertencias = normalizePrevalidationIssues(response?.advertencias);

  prevalidacionBloqueantes.value = bloqueantes;
  prevalidacionAdvertencias.value = advertencias;
  prevalidacionResumen.value = response?.resumen || null;

  if (response?.puede_continuar === false || bloqueantes.length) {
    applyPrevalidationFieldErrors(bloqueantes);
    errorMessage.value =
      "Hay datos que deben corregirse antes de registrar el artículo.";
    successMessage.value = "";

    const first = firstErrorField(fieldErrors.value);
    if (first) nextTick(() => focusField(first));
    return false;
  }

  if (advertencias.length) {
    const continuar =
      await confirmarAdvertenciasPrevalidacion(
        advertencias
      );

    if (!continuar) {
      errorMessage.value =
        "Revise las observaciones antes de continuar con el registro.";
      successMessage.value =
        "";

      return false;
    }
  }

  return true;
}

/* =========================================================
   AUTORES
========================================================= */

function buildAutoresPayload() {
  const raw =
    Array.isArray(
      form.value.autores
    )
      ? form.value.autores
      : [];

  return raw
    .map(
      (
        autor,
        index
      ) => {
        const id =
          Number(
            autor?.autor_id ??

            autor?.id ??

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
}


/* =========================================================
   ADJUNTOS RECUPERADOS
========================================================= */

function hasPendingRecoveredFiles() {
  const archivos =
    Array.isArray(
      form.value.archivos
    )
      ? form.value.archivos
      : [];

  return archivos.some(
    (item) =>
      !item?.file &&
      item?.originalName
  );
}


/* =========================================================
   VALIDACIÓN ADMIN
========================================================= */

function validateAdminContext() {
  if (
    !isAdminDelegado.value
  ) {
    return null;
  }

  if (
    !adminContext.value
      .usuarioId
  ) {
    return (
      "Seleccione nuevamente al usuario para continuar con el registro."
    );
  }

  return null;
}


/* =========================================================
   VALIDACIÓN FRONTEND
========================================================= */

function validateFront() {
  const errors = {};

  const general =
    formDatos.value || {};

  // -------------------------------------------------------
  // Contexto administrativo
  // -------------------------------------------------------

  if (
    isAdminDelegado.value &&
    !adminContext.value
      .usuarioId
  ) {
    errors.admin_context =
      "Seleccione nuevamente al usuario para continuar con el registro.";
  }

  // -------------------------------------------------------
  // Clasificación institucional
  // -------------------------------------------------------

  if (
    !general.sede
  ) {
    errors.sede =
      "Seleccione una sede.";
  }

  if (
    !general.facultad
  ) {
    errors.facultad =
      "Seleccione una facultad.";
  }

  if (
    !general.carrera
  ) {
    errors.carrera =
      "Seleccione una carrera.";
  }

  // -------------------------------------------------------
  // Origen
  // -------------------------------------------------------

  if (
    !String(
      form.value
        .origen_tipo ||
      ""
    ).trim()
  ) {
    errors.origen_tipo =
      "Seleccione el origen de la publicación.";
  }

  if (
    ["tic", "otro"].includes(form.value
      .origen_tipo) &&

    !String(
      form.value
        .origen_grado ||
      ""
    ).trim()
  ) {
    errors.origen_grado =
      "Campo obligatorio.";
  }

  if (
    exceedsLength(
      form.value
        .origen_grado,
      FIELD_LIMITS
        .origen_grado
    )
  ) {
    errors.origen_grado =
      `La carrera, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
  }

  // -------------------------------------------------------
  // Período de publicación
  // -------------------------------------------------------

  const publicationYear =
    Number(
      form.value
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
      "Ingrese un año de publicación válido entre 1900 y 2100.";
  }

  if (
    form.value
      .mes_publicacion !== ""
  ) {
    const publicationMonth =
      Number(
        form.value
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

  // -------------------------------------------------------
  // Artículo
  // -------------------------------------------------------

  if (
    !String(
      form.value
        .nombre_articulo ||
      ""
    ).trim()
  ) {
    errors.nombre_articulo =
      "Campo obligatorio.";
  } else if (
    exceedsLength(
      form.value
        .nombre_articulo,
      FIELD_LIMITS
        .nombre_articulo
    )
  ) {
    errors.nombre_articulo =
      `El título no puede superar ${FIELD_LIMITS.nombre_articulo} caracteres.`;
  }

  // -------------------------------------------------------
  // Base de indexación
  // -------------------------------------------------------

  const database =
    String(
      form.value
        .base_datos_indexada ||
      ""
    )
      .trim()
      .toLowerCase();

  if (!database) {
    errors.base_datos_indexada =
      "Seleccione una base de datos / indexación.";
  } else if (
    !REGIONAL_DATABASES.has(
      database
    )
  ) {
    errors.base_datos_indexada =
      "La base de datos / indexación seleccionada no es válida.";
  }

  if (
    database === "otra" &&
    !String(
      form.value
        .base_datos_otra ||
      ""
    ).trim()
  ) {
    errors.base_datos_otra =
      "Debe especificar la base de datos cuando seleccione “Otra”.";
  }

  if (
    database === "otra" &&
    exceedsLength(
      form.value
        .base_datos_otra,
      FIELD_LIMITS
        .base_datos_otra
    )
  ) {
    errors.base_datos_otra =
      `La base de datos no puede superar ${FIELD_LIMITS.base_datos_otra} caracteres.`;
  }

  // -------------------------------------------------------
  // ISSN
  // -------------------------------------------------------

  if (
    !String(
      form.value
        .codigo_issn ||
      ""
    ).trim()
  ) {
    errors.codigo_issn =
      "Campo obligatorio.";
  } else if (
    exceedsLength(
      form.value
        .codigo_issn,
      FIELD_LIMITS
        .codigo_issn
    )
  ) {
    errors.codigo_issn =
      `El ISSN no puede superar ${FIELD_LIMITS.codigo_issn} caracteres.`;
  }

  // -------------------------------------------------------
  // DOI
  // -------------------------------------------------------

  if (
    exceedsLength(
      form.value
        .codigo_doi,
      FIELD_LIMITS
        .codigo_doi
    )
  ) {
    errors.codigo_doi =
      `El DOI no puede superar ${FIELD_LIMITS.codigo_doi} caracteres.`;
  }

  // -------------------------------------------------------
  // Revista
  // -------------------------------------------------------

  if (
    !String(
      form.value
        .nombre_revista ||
      ""
    ).trim()
  ) {
    errors.nombre_revista =
      "Campo obligatorio.";
  } else if (
    exceedsLength(
      form.value
        .nombre_revista,
      FIELD_LIMITS
        .nombre_revista
    )
  ) {
    errors.nombre_revista =
      `El nombre de la revista no puede superar ${FIELD_LIMITS.nombre_revista} caracteres.`;
  }

  // -------------------------------------------------------
  // Número de revista
  // -------------------------------------------------------

  if (
    form.value
      .numero_revista !==
      null &&

    form.value
      .numero_revista !==
      ""
  ) {
    const numero =
      Number(
        form.value
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

  // -------------------------------------------------------
  // Enlaces
  // -------------------------------------------------------

  if (
    exceedsLength(
      form.value
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
      form.value
        .link_publicacion,
      FIELD_LIMITS
        .link_publicacion
    )
  ) {
    errors.link_publicacion =
      `El enlace no puede superar ${FIELD_LIMITS.link_publicacion} caracteres.`;
  }

  // -------------------------------------------------------
  // Autores
  // -------------------------------------------------------

  if (
    !Array.isArray(
      form.value.autores
    ) ||

    form.value
      .autores
      .length ===
      0
  ) {
    errors.autores =
      "Debe registrar al menos un autor.";
  }

  // -------------------------------------------------------
  // Adjuntos recuperados
  // -------------------------------------------------------

  if (
    hasPendingRecoveredFiles()
  ) {
    errors.archivos =
      "Hay adjuntos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
  }

  fieldErrors.value =
    errors;

  if (
    Object.keys(
      errors
    ).length
  ) {
    errorMessage.value =
      "Complete o corrija los campos marcados antes de guardar.";

    successMessage.value =
      "";

    const first =
      firstErrorField(
        errors
      );

    if (first) {
      nextTick(
        () => {
          focusField(
            first
          );
        }
      );
    }

    return false;
  }

  return true;
}


/* =========================================================
   RESET
========================================================= */

function resetForm() {
  fieldErrors.value =
    {};

  prevalidacionBloqueantes.value = [];
  prevalidacionAdvertencias.value = [];
  prevalidacionResumen.value = null;

  draftInfo.value =
    "";

  showDiscardDraftDialog.value =
    false;

  formDatos.value =
    createDefaultFormDatos();

  form.value =
    createDefaultForm();
}


function requestDiscardDraft() {
  if (loading.value) {
    return;
  }

  showDiscardDraftDialog.value =
    true;

  nextTick(() => {
    discardDraftDialog.value
      ?.focus?.();
  });
}


function cancelDiscardDraft() {
  showDiscardDraftDialog.value =
    false;
}


function confirmDiscardDraft() {
  showDiscardDraftDialog.value =
    false;

  limpiarBorrador();
}


function limpiarBorrador() {
  clearTimeout(
    draftTimer
  );

  disableDraftTemporarily();

  clearDraftStorage();

  resetForm();

  successMessage.value =
    "Borrador descartado.";

  errorMessage.value =
    "";
}


function handleRouteContextChange() {
  clearTimeout(
    draftTimer
  );

  hydrateAdminContextFromRoute();

  disableDraftTemporarily();

  resetForm();

  loadDraft();
}


/* =========================================================
   REGISTRO
========================================================= */

async function registrarArticuloRegional({ skipFrontValidation = false } = {}) {
  if (
    loading.value
  ) {
    return;
  }

  loading.value =
    true;

  successMessage.value =
    "";

  errorMessage.value =
    "";

  fieldErrors.value =
    {};

  clearPrevalidationState();

  try {
    // -----------------------------------------------------
    // Validación frontend
    // -----------------------------------------------------

    if (
      !skipFrontValidation &&
      !validateFront()
    ) {
      return;
    }

    // -----------------------------------------------------
    // Autores
    // -----------------------------------------------------

    const autoresPayload =
      buildAutoresPayload();

    if (
      !autoresPayload.length
    ) {
      fieldErrors.value = {
        ...fieldErrors.value,

        autores:
          "Los autores seleccionados no tienen un identificador válido.",
      };

      errorMessage.value =
        "Revise la sección de autores.";

      focusField(
        "autores"
      );

      return;
    }

    // -----------------------------------------------------
    // Contexto administrativo
    // -----------------------------------------------------

    const adminValidationError =
      validateAdminContext();

    if (
      adminValidationError
    ) {
      fieldErrors.value = {
        ...fieldErrors.value,

        admin_context:
          adminValidationError,
      };

      errorMessage.value =
        adminValidationError;

      successMessage.value =
        "";

      focusField(
        "admin_context"
      );

      return;
    }

    // -----------------------------------------------------
    // Prevalidación backend: integridad, PDF y duplicados
    // -----------------------------------------------------

    const prevalidacionOk =
      await ejecutarPrevalidacion(
        autoresPayload
      );

    if (!prevalidacionOk) {
      return;
    }

    // -----------------------------------------------------
    // FormData
    // -----------------------------------------------------

    const formData =
      new FormData();

    formData.append(
      "tipo_codigo",
      "articulo_regional"
    );

    // -----------------------------------------------------
    // Datos institucionales
    // -----------------------------------------------------

    const generalPayload = {
      ...formDatos.value,

      /*
       * País y ciudad no aplican a artículos.
       */
      pais: null,
      ciudad: null,
    };

    Object.entries(
      generalPayload
    ).forEach(
      ([key, value]) => {
        if (
          key === "pais" ||
          key === "ciudad"
        ) {
          return;
        }

        appendFormValue(
          formData,
          key,
          value
        );
      }
    );

    // -----------------------------------------------------
    // Origen
    // -----------------------------------------------------

    appendFormValue(
      formData,
      "origen_tipo",
      form.value
        .origen_tipo ||
        "ninguno"
    );

    if (
      ["tic", "otro"].includes(form.value
        .origen_tipo)
    ) {
      appendFormValue(
        formData,
        "origen_grado",
        String(
          form.value
            .origen_grado ||
          ""
        ).trim()
      );
    }

    // -----------------------------------------------------
    // Campos del artículo regional
    // -----------------------------------------------------

    appendFormValue(
      formData,
      "nombre_articulo",
      form.value
        .nombre_articulo
    );

    appendFormValue(
      formData,
      "anio_publicacion",
      form.value
        .anio_publicacion
    );

    appendFormValue(
      formData,
      "mes_publicacion",
      form.value
        .mes_publicacion
    );

    appendFormValue(
      formData,
      "base_datos_indexada",
      String(
        form.value
          .base_datos_indexada ||
        ""
      )
        .trim()
        .toLowerCase()
    );

    if (
      form.value
        .base_datos_indexada ===
      "otra"
    ) {
      appendFormValue(
        formData,
        "base_datos_otra",
        form.value
          .base_datos_otra
      );
    }

    appendFormValue(
      formData,
      "codigo_issn",
      form.value
        .codigo_issn
    );

    appendFormValue(
      formData,
      "codigo_doi",
      form.value
        .codigo_doi
    );

    appendFormValue(
      formData,
      "nombre_revista",
      form.value
        .nombre_revista
    );

    appendFormValue(
      formData,
      "numero_revista",
      form.value
        .numero_revista
    );

    appendFormValue(
      formData,
      "link_revista",
      form.value
        .link_revista
    );

    appendFormValue(
      formData,
      "link_publicacion",
      form.value
        .link_publicacion
    );

    // -----------------------------------------------------
    // Autores
    // -----------------------------------------------------

    formData.append(
      "autores",
      JSON.stringify(
        autoresPayload
      )
    );

    // -----------------------------------------------------
    // Registro delegado
    // -----------------------------------------------------

    if (
      isAdminDelegado.value &&
      adminContext.value
        .usuarioId
    ) {
      formData.append(
        "usuario_objetivo_id",
        String(
          adminContext.value
            .usuarioId
        )
      );

      if (
        adminContext.value
          .autorId
      ) {
        formData.append(
          "autor_objetivo_id",
          String(
            adminContext.value
              .autorId
          )
        );
      }
    }

    // -----------------------------------------------------
    // Adjuntos
    // -----------------------------------------------------

    appendArchivosToFormData(
      formData,
      selectedUploadItems(),
      {
        primaryField:
          "archivo_pdf",

        filesField:
          "archivos",

        metaField:
          "archivos_meta",
      }
    );

    // -----------------------------------------------------
    // Request
    // -----------------------------------------------------

    await api.post(
      createEndpoint.value,
      formData
    );

    // -----------------------------------------------------
    // Éxito
    // -----------------------------------------------------

    disableDraftTemporarily();

    clearDraftStorage();

    resetForm();

    successMessage.value =
      isAdminDelegado.value
        ? "Artículo regional guardado correctamente para el usuario seleccionado. La publicación quedó en estado Borrador y puede editarse o enviarse a revisión desde la gestión de publicaciones."
        : "La publicación se guardó correctamente y quedó en estado Borrador. Revise la información y edítela si es necesario antes de enviarla a revisión. Una vez enviada, la edición quedará bloqueada hasta que el administrador apruebe, rechace o solicite correcciones.";

    errorMessage.value =
      "";
  } catch (error) {
    const status =
      error
        ?.response
        ?.status;

    const data =
      error
        ?.response
        ?.data;

    // -----------------------------------------------------
    // Sesión
    // -----------------------------------------------------

    if (
      status === 401
    ) {
      errorMessage.value =
        "Sesión expirada. Vuelva a iniciar sesión.";

      successMessage.value =
        "";

      return;
    }

    // -----------------------------------------------------
    // Permisos
    // -----------------------------------------------------

    if (
      status === 403
    ) {
      errorMessage.value =
        "No tiene permisos para realizar este registro.";

      successMessage.value =
        "";

      return;
    }

    // -----------------------------------------------------
    // Errores DRF
    // -----------------------------------------------------

    const normalized =
      normalizeDrfErrors(
        data
      );

    fieldErrors.value =
      normalized.fields ||
      {};

    errorMessage.value =
      normalized.message ||
      "Error al registrar el artículo. Verifique los campos.";

    successMessage.value =
      "";

    const first =
      firstErrorField(
        fieldErrors.value
      );

    if (first) {
      nextTick(
        () => {
          focusField(
            first
          );
        }
      );
    }

    console.error(
      "Error al registrar el artículo regional:",
      data || error
    );
  } finally {
    loading.value =
      false;
  }
}


/* =========================================================
   CICLO DE VIDA
========================================================= */

onMounted(() => {
  formDatos.value.pais =
    null;

  formDatos.value.ciudad =
    null;

  hydrateAdminContextFromRoute();

  loadDraft();
});


onBeforeUnmount(() => {
  closePrevalidationNotice();

  clearTimeout(
    draftTimer
  );
});


/* =========================================================
   WATCHERS
========================================================= */

watch(
  formDatos,
  saveDraft,
  {
    deep: true,
  }
);


watch(
  form,
  saveDraft,
  {
    deep: true,
  }
);


watch(
  () =>
    route.fullPath,

  () => {
    handleRouteContextChange();
  }
);


watch(
  () =>
    form.value.origen_tipo,

  (value) => {
    if (
      !["tic", "otro"].includes(value)
    ) {
      form.value.origen_grado =
        "";
    }
  }
);


watch(
  () =>
    form.value.base_datos_indexada,

  (value) => {
    if (
      value !== "otra"
    ) {
      form.value.base_datos_otra =
        "";
    }
  }
);
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
