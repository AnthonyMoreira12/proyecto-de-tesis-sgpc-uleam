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
                Regional
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
                d="M4 4h16v16H4V4Zm2 2v12h12V6H6Zm2 2h8v2H8V8Zm0 4h6v2H8v-2Zm0 4h4v2H8v-2Z"
              />
            </svg>
          </div>

          <span>AR</span>
          <small>Artículo regional</small>
        </div>
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->

      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar un artículo regional"
        enctype="multipart/form-data"
        @submit.prevent="registrarArticuloRegional"
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
                id="ar-admin-context-anchor"
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
                  Datos generales
                </h2>

                <p class="sgpc-card-desc">
                  Información institucional para la clasificación del registro.
                </p>
              </div>
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
                  Origen de la publicación
                </h2>

                <p class="sgpc-card-desc">
                  Indique si el artículo proviene de un trabajo académico o si
                  no aplica.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-origen_tipo"
                  >
                    Origen
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
                    id="ar-origen-tipo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-origen_grado"
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
                    id="ar-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    :disabled="!['tic', 'otro'].includes(form.origen_tipo)"
                    :required="['tic', 'otro'].includes(form.origen_tipo)"
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="
                      fieldErrors.origen_grado
                        ? 'ar-origen-grado-error'
                        : undefined
                    "
                    :placeholder="
                      form.origen_tipo === 'otro'
                        ? 'Ej. Proyecto de investigación institucional'
                        : 'Ej. Ingeniería en TI / Ingeniería de Software / ...'
                    "
                  />

                  <p class="sgpc-hint">
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
                  Datos principales
                </h2>

                <p class="sgpc-card-desc">
                  Información base del artículo y su indexación regional.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-fecha_publicacion"
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
                    id="ar-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    :aria-invalid="Boolean(fieldErrors.fecha_publicacion)"
                    :aria-describedby="
                      fieldErrors.fecha_publicacion
                        ? 'ar-fecha-publicacion-error'
                        : undefined
                    "
                    required
                  />

                  <p
                    v-if="fieldErrors.fecha_publicacion"
                    id="ar-fecha-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-tipo_articulo"
                  >
                    Clasificación
                  </label>

                  <input
                    id="ar-tipo_articulo"
                    class="sgpc-input"
                    type="text"
                    value="Regional"
                    disabled
                  />
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
                    Base de datos / indexación
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
                  Identificación formal, metadatos y enlaces de acceso. Los
                  indicadores de impacto no aplican a artículos regionales.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-codigo_issn"
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
                    Código DOI
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

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="ar-link_revista"
                  >
                    Link de la revista
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
                    Link de la publicación
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
                  Seleccione autores, participación y orden de firma.
                </p>
              </div>
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
                  Adjuntos
                </h2>

                <p class="sgpc-card-desc">
                  Suba evidencias del artículo en PDF y asigne un nombre a cada
                  archivo cuando sea necesario.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="ar-archivo-input"
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

                <h3>
                  Resumen del registro
                </h3>
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
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredContext }"
                @click="goTo('sec-datos-generales')"
              >
                <div>
                  <strong>
                    Datos generales
                  </strong>

                  <span>
                    {{
                      hasRequiredContext
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredContext
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredOrigin }"
                @click="goTo('sec-origen')"
              >
                <div>
                  <strong>
                    Origen
                  </strong>

                  <span>
                    {{
                      hasRequiredOrigin
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredOrigin
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredMain }"
                @click="goTo('sec-principales')"
              >
                <div>
                  <strong>
                    Datos principales
                  </strong>

                  <span>
                    {{
                      hasRequiredMain
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredMain
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredJournal }"
                @click="goTo('sec-revista')"
              >
                <div>
                  <strong>
                    Revista y enlaces
                  </strong>

                  <span>
                    {{
                      hasRequiredJournal
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredJournal
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredAuthors }"
                @click="goTo('sec-autores')"
              >
                <div>
                  <strong>
                    Autores
                  </strong>

                  <span>
                    {{
                      hasRequiredAuthors
                        ? `${form.autores.length} autor(es)`
                        : "Sin autores"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredAuthors
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasAdjuntos }"
                @click="goTo('sec-adjuntos')"
              >
                <div>
                  <strong>
                    Adjuntos
                  </strong>

                  <span>
                    {{
                      hasAdjuntos
                        ? `${form.archivos.length} archivo(s)`
                        : "Opcional"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasAdjuntos
                      ? "Completo"
                      : "Opcional"
                  }}
                </em>
              </button>
            </div>

            <!-- ===============================================
                 ACCIONES ALINEADAS CON LOS DEMÁS FORMULARIOS
            ================================================ -->

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
                  {{ loading ? submitLoadingText : submitText }}
                </span>
              </button>

              <button
                type="button"
                class="sgpc-btn"
                :disabled="loading"
                title="Elimina únicamente el borrador guardado en este navegador"
                @click="limpiarBorrador"
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
import api from "../../scripts/api/axios";

import {
  appendArchivosToFormData,
  restoreDraftArchivos,
  serializeDraftArchivos,
} from "../../scripts/utils/adjuntosPdf";


defineOptions({
  name: "ArticuloRegionalForm",
});


const route = useRoute();


/* =========================================================
   CONFIGURACIÓN
========================================================= */

const BASE_DRAFT_KEY =
  "sgpc:draft:articulo_regional:v23";

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
  admin_context: "Usuario objetivo",
  general: "Validación general",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  tipo_codigo: "Tipo de artículo",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa u otro origen",
  nombre_articulo: "Título del artículo",
  base_datos_indexada: "Base de datos / indexación",
  base_datos_otra: "Base de datos (otra)",
  fecha_publicacion: "Fecha de publicación",
  codigo_issn: "ISSN",
  codigo_doi: "DOI",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_revista: "Link de la revista",
  link_publicacion: "Link de la publicación",
  autores: "Autores",
  archivos: "Adjuntos PDF",
});


const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "tipo_codigo",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "origen_tipo",
  "origen_grado",
  "fecha_publicacion",
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
    fecha_publicacion: "",

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

const draftInfo = ref("");

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
      adminContext.value
        .usuarioNombre ||

      `ID ${
        adminContext.value
          .usuarioId ||
        "—"
      }`
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
      "Registrar Artículo Regional"
    );
  }
);


const pageSubtitle = computed(
  () => {
    if (
      isAdminDelegado.value
    ) {
      return (
        "Registre datos generales, origen, indexación regional, revista, enlaces, autores y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios."
      );
    }

    return (
      "Registre datos generales, origen, indexación regional, revista, enlaces, autores y adjuntos. Los campos marcados con * son obligatorios."
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

const hasRequiredContext =
  computed(() => {
    const general =
      formDatos.value || {};

    return Boolean(
      general.facultad &&
      general.carrera &&
      general.area &&
      general.subarea
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
    if (
      !form.value
        .fecha_publicacion
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


const requiredSections =
  computed(() => {
    return [
      {
        key: "datos",
        done:
          hasRequiredContext.value,
      },

      {
        key: "origen",
        done:
          hasRequiredOrigin.value,
      },

      {
        key: "principal",
        done:
          hasRequiredMain.value,
      },

      {
        key: "revista",
        done:
          hasRequiredJournal.value,
      },

      {
        key: "autores",
        done:
          hasRequiredAuthors.value,
      },
    ];
  });


const completedRequiredCount =
  computed(() => {
    return (
      requiredSections.value
        .filter(
          (section) =>
            section.done
        )
        .length
    );
  });


const totalRequiredCount =
  computed(() => {
    return (
      requiredSections.value
        .length
    );
  });


const progressPercent =
  computed(() => {
    if (
      !totalRequiredCount.value
    ) {
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

    fecha_publicacion:
      "ar-fecha_publicacion",

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

              fecha_publicacion:
                form.value
                  .fecha_publicacion,

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

        fecha_publicacion:
          incoming.fecha_publicacion ||
          "",

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

    if (
      parsed?.updatedAt
    ) {
      const date =
        new Date(
          parsed.updatedAt
        );

      draftInfo.value =
        Number.isNaN(
          date.getTime()
        )
          ? "Se recuperó un borrador guardado."
          : `Se recuperó un borrador guardado (${date.toLocaleString()}).`;
    } else {
      draftInfo.value =
        "Se recuperó un borrador guardado.";
    }

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

          rol_autoria:
            orden === 1
              ? "principal"
              : "coautor",
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
      "Debe llegar al formulario con un usuario objetivo válido."
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
      "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
  }

  // -------------------------------------------------------
  // Clasificación institucional
  // -------------------------------------------------------

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

  if (
    !general.area
  ) {
    errors.area =
      "Seleccione un área del conocimiento (UNESCO).";
  }

  if (
    !general.subarea
  ) {
    errors.subarea =
      "Seleccione una subárea del conocimiento (UNESCO).";
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
      `El grado, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
  }

  // -------------------------------------------------------
  // Fecha
  // -------------------------------------------------------

  if (
    !form.value
      .fecha_publicacion
  ) {
    errors.fecha_publicacion =
      "Campo obligatorio.";
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

  draftInfo.value =
    "";

  formDatos.value =
    createDefaultFormDatos();

  form.value =
    createDefaultForm();
}


function limpiarBorrador() {
  clearTimeout(
    draftTimer
  );

  disableDraftTemporarily();

  clearDraftStorage();

  resetForm();

  successMessage.value =
    "Borrador eliminado.";

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

async function registrarArticuloRegional() {
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

  try {
    // -----------------------------------------------------
    // Validación frontend
    // -----------------------------------------------------

    if (
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
      "fecha_publicacion",
      form.value
        .fecha_publicacion
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
      form.value.archivos,
      {
        primaryField:
          null,

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
        ? "Artículo regional registrado correctamente para el usuario seleccionado."
        : "Artículo regional registrado correctamente.";

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
<style src="./articulo-regional-form.css"></style>