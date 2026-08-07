<template>
  <div class="sgpc-form-page sgpc-form-page--libro">
    <div class="sgpc-form-shell">
      <header class="sgpc-form-header sgpc-publication-header page-stage page-header">
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

              <span class="sgpc-publication-chip sgpc-publication-chip--accent">
                Libro
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
                d="M4 3h13a3 3 0 0 1 3 3v15H7a3 3 0 0 1-3-3V3Zm3 2H6v13a1 1 0 0 0 1 1h11V6a1 1 0 0 0-1-1H7Zm2 3h6v2H9V8Zm0 4h6v2H9v-2Zm0 4h4v2H9v-2Z"
              />
            </svg>
          </div>

          <span>LIB</span>
          <small>Libro científico</small>
        </div>
      </header>

      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar un libro"
        enctype="multipart/form-data"
        @submit.prevent="handleSubmitIntent"
      >
        <main class="sgpc-form-main page-stage page-main">
          <!-- =====================================================
               CONTEXTO ADMINISTRATIVO
          ====================================================== -->

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
              <div id="lb-admin-context-anchor" tabindex="-1"></div>

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
                id="lb-admin-context-error"
                class="sgpc-hint sgpc-hint-error"
                role="alert"
              >
                {{ fieldErrors.admin_context }}
              </p>
            </div>
          </section>

          <!-- =====================================================
               DATOS GENERALES
          ====================================================== -->

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
                  Información institucional para la clasificación del
                  registro.
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

          <!-- =====================================================
               ORIGEN
          ====================================================== -->

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
                  Indique la relación académica del libro registrado.
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
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-origen_tipo"
                  >
                    Origen de la publicación
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <select
                    id="lb-origen_tipo"
                    :aria-invalid="Boolean(fieldErrors.origen_tipo)"
                    :aria-describedby="fieldErrors.origen_tipo ? 'lb-origen-tipo-error' : undefined"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
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
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-origen-tipo-error"
                    role="alert">
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-origen_grado"
                  >
                    {{
                      form.origen_tipo === "otro"
                        ? "Especifique el origen"
                        : "Grado / programa"
                    }}

                    <span
                      v-if="['tic', 'otro'].includes(form.origen_tipo)"
                      class="req"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="lb-origen_grado"
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="fieldErrors.origen_grado ? 'lb-origen-grado-error' : undefined"
                    maxlength="120"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    :disabled="!['tic', 'otro'].includes(form.origen_tipo)"
                    :required="['tic', 'otro'].includes(form.origen_tipo)"
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
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-origen-grado-error"
                    role="alert">
                    {{ fieldErrors.origen_grado }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <!-- =====================================================
               INFORMACIÓN DEL LIBRO
          ====================================================== -->

          <section
            id="sec-libro"
            class="sgpc-card"
            data-section="03"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Información del libro
                </h2>

                <p class="sgpc-card-desc">
                  Datos bibliográficos y editoriales principales de la obra
                  publicada.
                </p>
              </div>

              <span
                class="sgpc-section-state"
                :class="sectionStateClass(hasRequiredBook, optionalBookMissingCount)"
              >
                {{ sectionStateLabel(hasRequiredBook, optionalBookMissingCount) }}
              </span>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="lb-nombre_libro"
                  >
                    Nombre del libro
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <input
                    id="lb-nombre_libro"
                    :aria-invalid="Boolean(fieldErrors.nombre_libro)"
                    :aria-describedby="fieldErrors.nombre_libro ? 'lb-nombre-libro-error' : undefined"
                    maxlength="255"
                    v-model.trim="form.nombre_libro"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Innovación y desarrollo científico"
                  />

                  <p
                    v-if="fieldErrors.nombre_libro"
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-nombre-libro-error"
                    role="alert">
                    {{ fieldErrors.nombre_libro }}
                  </p>
                </div>

                <!-- Período -->
                <div class="sgpc-field sgpc-field--period sgpc-col-span-3">
                  <label class="sgpc-label" for="lb-anio_publicacion">
                    Año de publicación
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <input
                    id="lb-anio_publicacion"
                    v-model.number="form.anio_publicacion"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    placeholder="Ej. 2026"
                    required
                    :aria-invalid="Boolean(fieldErrors.anio_publicacion)"
                    :aria-describedby="
                      fieldErrors.anio_publicacion
                        ? 'lb-anio-publicacion-error'
                        : undefined
                    "
                  />

                  <p
                    v-if="fieldErrors.anio_publicacion"
                    id="lb-anio-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.anio_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-field--period sgpc-col-span-3">
                  <label class="sgpc-label" for="lb-mes_publicacion">
                    Mes de publicación
                    <span class="sgpc-label-optional">(opcional)</span>
                  </label>

                  <select
                    id="lb-mes_publicacion"
                    v-model="form.mes_publicacion"
                    class="sgpc-input"
                    :aria-invalid="Boolean(fieldErrors.mes_publicacion)"
                    :aria-describedby="monthDescriptionIds"
                  >
                    <option value="">Sin mes especificado</option>
                    <option
                      v-for="month in publicationMonths"
                      :key="month.value"
                      :value="month.value"
                    >
                      {{ month.label }}
                    </option>
                  </select>

                  <p id="lb-mes-publicacion-help" class="sgpc-hint">
                    Puede dejar el mes vacío si no consta en la fuente bibliográfica.
                  </p>

                  <p
                    v-if="fieldErrors.mes_publicacion"
                    id="lb-mes-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.mes_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-codigo_isbn"
                  >
                    Código ISBN
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <input
                    id="lb-codigo_isbn"
                    :aria-invalid="Boolean(fieldErrors.codigo_isbn)"
                    :aria-describedby="fieldErrors.codigo_isbn ? 'lb-codigo-isbn-error' : undefined"
                    maxlength="100"
                    v-model.trim="form.codigo_isbn"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. 978-9942-xx-xxxx-x"
                  />

                  <p
                    v-if="fieldErrors.codigo_isbn"
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-codigo-isbn-error"
                    role="alert">
                    {{ fieldErrors.codigo_isbn }}
                  </p>

                  <p class="sgpc-hint">
                    Ingrese el ISBN asignado oficialmente a la obra.
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-editorial_compilador"
                  >
                    Editorial / Compilador
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <input
                    id="lb-editorial_compilador"
                    :aria-invalid="Boolean(fieldErrors.editorial_compilador)"
                    :aria-describedby="fieldErrors.editorial_compilador ? 'lb-editorial-compilador-error' : undefined"
                    maxlength="255"
                    v-model.trim="form.editorial_compilador"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Editorial ULEAM"
                  />

                  <p
                    v-if="fieldErrors.editorial_compilador"
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-editorial-compilador-error"
                    role="alert">
                    {{ fieldErrors.editorial_compilador }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-revisor_par_arbitraje"
                  >
                    Revisor par / arbitraje
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <select
                    id="lb-revisor_par_arbitraje"
                    :aria-invalid="Boolean(fieldErrors.revisor_par_arbitraje)"
                    :aria-describedby="fieldErrors.revisor_par_arbitraje ? 'lb-revisor-par-arbitraje-error' : undefined"
                    v-model="form.revisor_par_arbitraje"
                    class="sgpc-input"
                    required
                  >
                    <option
                      disabled
                      value=""
                    >
                      Seleccione...
                    </option>

                    <option value="si">
                      Sí
                    </option>

                    <option value="no">
                      No
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.revisor_par_arbitraje"
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-revisor-par-arbitraje-error"
                    role="alert">
                    {{ fieldErrors.revisor_par_arbitraje }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="lb-link_libro"
                  >
                    Link del libro
                    <span class="req" aria-hidden="true">*</span>
                  </label>

                  <input
                    id="lb-link_libro"
                    :aria-invalid="Boolean(fieldErrors.link_libro)"
                    :aria-describedby="fieldErrors.link_libro ? 'lb-link-libro-error' : undefined"
                    maxlength="500"
                    v-model.trim="form.link_libro"
                    class="sgpc-input"
                    type="url"
                    required
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_libro"
                    class="sgpc-hint sgpc-hint-error"
                  
                    id="lb-link-libro-error"
                    role="alert">
                    {{ fieldErrors.link_libro }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <!-- =====================================================
               AUTORES
          ====================================================== -->

          <section
            id="sec-autores"
            class="sgpc-card"
            data-section="04"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Autores
                </h2>

                <p class="sgpc-card-desc">
                  Seleccione autores y defina su participación y orden de
                  firma.
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
              <div id="lb-autores-anchor" tabindex="-1"></div>

              <AutoresSelector
                v-model="form.autores"
                :error="fieldErrors.autores"
              />
            </div>
          </section>

          <!-- =====================================================
               ADJUNTOS
          ====================================================== -->

          <section
            id="sec-adjuntos"
            class="sgpc-card"
            data-section="05"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Adjuntos PDF
                </h2>

                <p class="sgpc-card-desc">
                  Adjunte el PDF principal del libro y los soportes
                  complementarios necesarios.
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
                input-id="lb-archivo-input"
                title="Agregar archivos PDF"
                description="El primer archivo será el PDF principal del libro. Puede agregar hasta 2 adjuntos adicionales."
                helper-text="PDF principal hasta 5 MB. Adjuntos hasta 3 MB. Máximo 3 archivos."
                :multiple="true"
                :max-files="3"
                :uses-primary-slot="true"
                :primary-max-size-mb="5"
                :attachment-max-size-mb="3"
              />
            </div>
          </section>

          <!-- =====================================================
               MENSAJES
          ====================================================== -->

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

        <!-- =====================================================
             RESUMEN LATERAL
        ====================================================== -->

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
                    d="M4 3h13a3 3 0 0 1 3 3v15H7a3 3 0 0 1-3-3V3Zm3 2H6v13a1 1 0 0 0 1 1h11V6a1 1 0 0 0-1-1H7Zm2 3h6v2H9V8Z"
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

            <div
              class="sgpc-progress"
              :class="{ 'is-complete': canSubmit }"
            >
              <div class="sgpc-progress-row">
                <span>Completitud</span>

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
                {{ totalRequiredCount }} secciones obligatorias completas
              </p>
            </div>

            <div class="sgpc-optional-summary">
              <div class="sgpc-optional-summary__head">
                <span>Información complementaria</span>
                <strong>{{ optionalCompletedCount }}/{{ totalOptionalCount }}</strong>
              </div>

              <p v-if="optionalMissingCount > 0">
                <strong>{{ optionalMissingCount }}</strong>
                {{ optionalMissingCount === 1 ? "dato opcional sin completar" : "datos opcionales sin completar" }}.
                Puede registrar igualmente, pero conviene revisarlos si dispone de esa información.
              </p>

              <p v-else class="is-complete">
                Toda la información complementaria aplicable está completa.
              </p>

              <button
                v-if="optionalMissingCount > 0"
                type="button"
                class="sgpc-summary-link"
                @click="reviewOptionalFields"
              >
                Revisar opcionales
              </button>
            </div>

            <div
              v-if="canSubmit"
              class="sgpc-ready-notice"
              :class="{ 'has-optional-gap': optionalMissingCount > 0 }"
              role="status"
              aria-live="polite"
            >
              <strong>
                {{ optionalMissingCount > 0 ? "Listo para registrar" : "Registro completo" }}
              </strong>

              <span v-if="optionalMissingCount > 0">
                Los datos obligatorios están completos. Quedan opcionales que puede revisar antes de guardar.
              </span>

              <span v-else>
                Los datos obligatorios y complementarios están completos.
              </span>
            </div>

            <div class="sgpc-status-list">
              <button
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': hasRequiredContext,
                  'has-optional-gap': hasRequiredContext && optionalContextMissingCount > 0,
                }"
                @click="goTo('sec-datos-generales')"
              >
                <div>
                  <strong>
                    Datos generales
                  </strong>

                  <span>
                    {{
                      hasRequiredContext
                        ? sectionStatusText(optionalContextMissingCount)
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
                :class="{
                  'is-ok': hasRequiredOrigin,
                }"
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
                :class="{
                  'is-ok': hasRequiredBook,
                  'has-optional-gap': hasRequiredBook && optionalBookMissingCount > 0,
                }"
                @click="goTo('sec-libro')"
              >
                <div>
                  <strong>
                    Información del libro
                  </strong>

                  <span>
                    {{
                      hasRequiredBook
                        ? sectionStatusText(optionalBookMissingCount)
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredBook
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': hasRequiredAuthors,
                }"
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
                :class="{
                  'is-ok': hasAdjuntos,
                  'is-optional-empty': !hasAdjuntos,
                }"
                @click="goTo('sec-adjuntos')"
              >
                <div>
                  <strong>
                    Adjuntos PDF
                  </strong>

                  <span>
                    {{
                      hasAdjuntos
                        ? `${form.archivos.length} archivo(s)`
                        : "Sin archivos adjuntos"
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
                class="sgpc-btn"
                type="button"
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

      <div
        v-if="showOptionalReviewDialog"
        class="sgpc-review-modal"
        role="presentation"
        @mousedown.self="closeOptionalReviewDialog"
      >
        <section
          ref="optionalReviewDialog"
          class="sgpc-review-modal__dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="lb-optional-review-title"
          aria-describedby="lb-optional-review-description"
          tabindex="-1"
          @keydown.esc="closeOptionalReviewDialog"
        >
          <div class="sgpc-review-modal__icon" aria-hidden="true">!</div>

          <div class="sgpc-review-modal__content">
            <p class="sgpc-review-modal__kicker">Revisión final</p>

            <h2 id="lb-optional-review-title">
              El libro está listo para registrarse
            </h2>

            <p id="lb-optional-review-description">
              Todos los campos obligatorios están completos, pero quedan
              {{ optionalMissingCount }}
              {{ optionalMissingCount === 1 ? "dato opcional vacío" : "datos opcionales vacíos" }}.
              Esto no impide guardar el registro.
            </p>

            <ul class="sgpc-review-modal__list">
              <li
                v-for="item in optionalMissingItems"
                :key="item.key"
              >
                <span>{{ item.label }}</span>
                <small>{{ item.sectionLabel }}</small>
              </li>
            </ul>

            <div class="sgpc-review-modal__actions">
              <button
                type="button"
                class="sgpc-btn-primary"
                @click="confirmOptionalRegistration"
              >
                Registrar de todas formas
              </button>

              <button
                type="button"
                class="sgpc-btn"
                @click="reviewOptionalFields"
              >
                Revisar opcionales
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";

import api from "../../scripts/api/axios";

import {
  restoreDraftArchivos,
  serializeDraftArchivos,
  appendArchivosToFormData,
} from "../../scripts/utils/adjuntosPdf";

const BASE_STORAGE_KEY =
  "sgpc-libro-draft:v21";

const STANDARD_CREATE_ENDPOINT =
  "/libros/";

const ADMIN_CREATE_ENDPOINT =
  "/admin/publicaciones/libros/crear/";

const BULK_ATTACHMENTS_ENDPOINT =
  "/archivos-publicacion/bulk-upload/";

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

  adjuntos: "archivos",
  meta: "archivos",
  archivos_meta: "archivos",
  files: "archivos",
  archivos: "archivos",
  archivo: "archivos",
  archivo_pdf: "archivos",

  non_field_errors: "general",
  detail: "general",
});

const FIELD_LABELS = Object.freeze({
  general: "Validación general",
  admin_context: "Usuario objetivo",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa u otro origen",
  nombre_libro: "Nombre del libro",
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",
  codigo_isbn: "Código ISBN",
  editorial_compilador: "Editorial / Compilador",
  revisor_par_arbitraje: "Revisor par / arbitraje",
  link_libro: "Link del libro",
  autores: "Autores",
  archivos: "Adjuntos PDF",
});

const ERROR_FIELD_ORDER = Object.freeze([
  "general",
  "admin_context",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "origen_tipo",
  "origen_grado",
  "nombre_libro",
  "anio_publicacion",
  "mes_publicacion",
  "codigo_isbn",
  "editorial_compilador",
  "revisor_par_arbitraje",
  "link_libro",
  "autores",
  "archivos",
]);

const FIELD_LIMITS = Object.freeze({
  origen_grado: 120,
  nombre_libro: 255,
  codigo_isbn: 100,
  editorial_compilador: 255,
  link_libro: 500,
});

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
    nombre_libro: "",
    anio_publicacion: null,
    mes_publicacion: "",
    codigo_isbn: "",
    editorial_compilador: "",
    revisor_par_arbitraje: "",
    link_libro: "",
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
  return ERROR_KEY_ALIASES[key] || key;
}

function normalizeDrfErrors(data) {
  if (!data) {
    return {
      fields: {},
      message:
        "No se pudo guardar. Verifique los campos.",
    };
  }

  if (
    typeof data?.detail === "string"
  ) {
    return {
      fields: {},
      message: data.detail,
    };
  }

  const rawErrors =
    data?.errors &&
    typeof data.errors === "object"
      ? data.errors
      : data;

  if (
    typeof rawErrors !== "object" ||
    rawErrors === null
  ) {
    return {
      fields: {},
      message:
        "No se pudo guardar. Verifique los campos.",
    };
  }

  const fields = {};
  let first = null;

  Object.entries(rawErrors).forEach(
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
        first = normalizedKey;
      }
    }
  );

  let message =
    "No se pudo registrar. Revise los campos marcados.";

  if (fields.admin_context) {
    message =
      fields.admin_context;
  } else if (fields.autores) {
    message =
      "Revise la sección de Autores: debe existir al menos un autor y el orden debe ser válido.";
  } else if (fields.archivos) {
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

function firstErrorField(fields) {
  for (const key of ERROR_FIELD_ORDER) {
    if (fields?.[key]) {
      return key;
    }
  }

  return (
    Object.keys(fields || {})[0] ||
    null
  );
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

function positiveId(value) {
  const parsed =
    Number(value);

  return (
    Number.isInteger(parsed) &&
    parsed > 0
      ? parsed
      : null
  );
}

function extractPublicacionId(payload) {
  return positiveId(
    payload?.publicacion_id ??
    payload?.publicacion?.id ??
    payload?.libro?.publicacion_id
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

function normalizeRecoveredPeriod(recovered) {
  const rawYear = Number(recovered?.anio_publicacion);
  let year = Number.isInteger(rawYear) && rawYear > 0 ? rawYear : null;

  const rawMonth = Number(recovered?.mes_publicacion);
  let month =
    Number.isInteger(rawMonth) && rawMonth >= 1 && rawMonth <= 12
      ? rawMonth
      : "";

  const legacyKey = ["fecha", "publicacion"].join("_");
  const legacyValue = String(recovered?.[legacyKey] || "").trim();
  const legacyMatch = legacyValue.match(/^(\d{4})-(\d{2})/);

  if (legacyMatch) {
    if (!year) {
      const parsedYear = Number(legacyMatch[1]);
      if (Number.isInteger(parsedYear) && parsedYear > 0) {
        year = parsedYear;
      }
    }

    if (!month) {
      const parsedMonth = Number(legacyMatch[2]);
      if (
        Number.isInteger(parsedMonth) &&
        parsedMonth >= 1 &&
        parsedMonth <= 12
      ) {
        month = parsedMonth;
      }
    }
  }

  return {
    anio_publicacion: year,
    mes_publicacion: month,
  };
}


export default {
  name: "LibroRegistro",

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
      showOptionalReviewDialog: false,
      _draftTimer: null,
      _draftSuspended: false,

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

    monthDescriptionIds() {
      const ids = ["lb-mes-publicacion-help"];
      if (this.fieldErrors.mes_publicacion) {
        ids.push("lb-mes-publicacion-error");
      }
      return ids.join(" ");
    },


    isAdminDelegado() {
      const path =
        String(
          this.$route?.path ||
          ""
        );

      return Boolean(
        this.$route?.meta
          ?.delegatedPublication ||
        path.startsWith(
          "/admin/publicaciones/usuario/"
        )
      );
    },

    draftStorageKey() {
      if (!this.isAdminDelegado) {
        return (
          `${BASE_STORAGE_KEY}:self`
        );
      }

      const usuarioId =
        this.adminContext
          .usuarioId ||
        positiveId(
          this.$route?.params
            ?.usuarioId
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
          `ID ${this.adminContext.autorId}`
        );
      }

      return (
        "Se resolverá automáticamente"
      );
    },

    showAutorObjetivo() {
      if (!this.isAdminDelegado) {
        return false;
      }

      /*
       * Usuario.id y Autor.id pertenecen a entidades
       * diferentes y no deben compararse entre sí.
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

    pageKicker() {
      return this.isAdminDelegado
        ? "Administración · Libros y capítulos"
        : "Libros y capítulos";
    },

    pageTitle() {
      return "Registrar Libro";
    },

    pageSubtitle() {
      if (this.isAdminDelegado) {
        return (
          "Registre la información editorial del libro para el usuario seleccionado. Los campos marcados con * son obligatorios."
        );
      }

      return (
        "Registre la información editorial del libro, sus autores y evidencias. Los campos marcados con * son obligatorios."
      );
    },

    submitText() {
      return "Registrar libro";
    },

    submitLoadingText() {
      return "Guardando...";
    },

    hasRequiredContext() {
      const general =
        this.form
          .datos_generales ||
        {};

      return Boolean(
        general.facultad &&
        general.carrera
      );
    },

    hasRequiredOrigin() {
      if (
        !this.form.origen_tipo
      ) {
        return false;
      }

      if (
        ["tic", "otro"].includes(this.form.origen_tipo)
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

    hasRequiredBook() {
      return Boolean(
        String(
          this.form
            .nombre_libro ||
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
        ) > 0 &&
        String(
          this.form
            .codigo_isbn ||
          ""
        ).trim() &&
        String(
          this.form
            .editorial_compilador ||
          ""
        ).trim() &&
        String(
          this.form
            .revisor_par_arbitraje ||
          ""
        ).trim() &&
        String(
          this.form
            .link_libro ||
          ""
        ).trim()
      );
    },

    hasRequiredAuthors() {
      return (
        Array.isArray(
          this.form.autores
        ) &&
        this.form.autores
          .length > 0
      );
    },

    hasAdjuntos() {
      return (
        Array.isArray(
          this.form.archivos
        ) &&
        this.form.archivos
          .length > 0
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
          sectionLabel: "Datos generales",
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
          section: "libro",
          sectionLabel: "Información del libro",
        });
      }

      if (!this.hasAdjuntos) {
        items.push({
          key: "archivos",
          label: "Adjuntos PDF",
          section: "adjuntos",
          sectionLabel: "Adjuntos PDF",
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

      // Proyecto, área, mes y adjuntos.
      // La subárea solo aplica cuando existe un área seleccionada.
      return 4 + (hasArea ? 1 : 0);
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

    optionalBookMissingCount() {
      return this.optionalMissingItems
        .filter((item) => item.section === "libro")
        .length;
    },

    canSubmit() {
      return Boolean(
        this.totalRequiredCount > 0 &&
        this.completedRequiredCount ===
          this.totalRequiredCount
      );
    },

    requiredSections() {
      return [
        {
          key: "datos",
          done:
            this.hasRequiredContext,
        },
        {
          key: "origen",
          done:
            this.hasRequiredOrigin,
        },
        {
          key: "libro",
          done:
            this.hasRequiredBook,
        },
        {
          key: "autores",
          done:
            this.hasRequiredAuthors,
        },
      ];
    },

    completedRequiredCount() {
      return this.requiredSections
        .filter(
          (section) =>
            section.done
        )
        .length;
    },

    totalRequiredCount() {
      return (
        this.requiredSections
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
        ) * 100
      );
    },
  },

  created() {
    this.hydrateAdminContextFromRoute();
    this.loadDraft();
  },

  beforeUnmount() {
    clearTimeout(
      this._draftTimer
    );
  },

  watch: {
    form: {
      deep: true,

      handler(value) {
        if (
          this._draftSuspended
        ) {
          return;
        }

        clearTimeout(
          this._draftTimer
        );

        this._draftTimer =
          setTimeout(() => {
            const payload = {
              form: {
                datos_generales: {
                  ...value.datos_generales,
                  pais: null,
                  ciudad: null,
                },

                origen_tipo:
                  value.origen_tipo,

                origen_grado:
                  value.origen_grado,

                nombre_libro:
                  value.nombre_libro,
                  anio_publicacion:
                    value.anio_publicacion,

                  mes_publicacion:
                    value.mes_publicacion,

                codigo_isbn:
                  value.codigo_isbn,

                editorial_compilador:
                  value.editorial_compilador,

                revisor_par_arbitraje:
                  value.revisor_par_arbitraje,

                link_libro:
                  value.link_libro,

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
                this.draftStorageKey,
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
          }, 250);
      },
    },

    "form.origen_tipo"(value) {
      if (!["tic", "otro"].includes(value)) {
        this.form.origen_grado =
          "";
      }
    },

    "$route.fullPath"() {
      this.handleRouteContextChange();
    },
  },

  methods: {
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

    loadDraft() {
      let raw = null;

      try {
        raw =
          localStorage.getItem(
            this.draftStorageKey
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

        const recoveredPeriod =
          normalizeRecoveredPeriod(
            (parsed.form || parsed)
          );

        this.suspendDraftOnce();

        this.form = {
          ...this.form,
          ...(parsed.form || parsed),

          anio_publicacion:
            recoveredPeriod.anio_publicacion,

          mes_publicacion:
            recoveredPeriod.mes_publicacion,

          datos_generales: {
            ...this.form
              .datos_generales,

            ...(
              (
                parsed.form
                  ?.datos_generales ||
                parsed.datos_generales
              ) ||
              {}
            ),

            pais: null,
            ciudad: null,
          },

          autores:
            Array.isArray(
              parsed.form?.autores ??
              parsed.autores
            )
              ? (
                  parsed.form?.autores ??
                  parsed.autores
                )
              : [],

          archivos:
            restoreDraftArchivos(
              parsed.form?.archivos ??
              parsed.archivos
            ),
        };

        if (parsed?.updatedAt) {
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
          "Borrador corrupto, se ignora.",
          error
        );
      }
    },

    suspendDraftOnce() {
      this._draftSuspended = true;

      this.$nextTick(() => {
        this._draftSuspended = false;
      });
    },

    handleRouteContextChange() {
      clearTimeout(this._draftTimer);
      this.hydrateAdminContextFromRoute();
      this.suspendDraftOnce();
      this.resetForm();
      this.loadDraft();
    },

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

    clearDraft() {
      clearTimeout(this._draftTimer);

      try {
        localStorage.removeItem(
          this.draftStorageKey
        );
      } catch (error) {
        console.warn(
          "No se pudo eliminar el borrador.",
          error
        );
      }

      this.suspendDraftOnce();
      this.resetForm();

      this.mensaje =
        "Borrador eliminado.";

      this.mensajeTipo =
        "info";
    },

    /* ========================================================
       RESUMEN / OPCIONALES
    ======================================================== */

    sectionStatusText(optionalMissing = 0) {
      if (optionalMissing > 0) {
        return `${optionalMissing} ${
          optionalMissing === 1
            ? "opcional sin completar"
            : "opcionales sin completar"
        }`;
      }

      return "Información completa";
    },

    sectionStateLabel(requiredDone, optionalMissing = 0) {
      if (!requiredDone) {
        return "Pendiente";
      }

      return optionalMissing > 0
        ? "Completo · revisar opcionales"
        : "Completo";
    },

    sectionStateClass(requiredDone, optionalMissing = 0) {
      if (!requiredDone) {
        return "is-pending";
      }

      return optionalMissing > 0
        ? "is-complete has-optional-gap"
        : "is-complete";
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

      this.closeOptionalReviewDialog();

      if (!first) {
        return;
      }

      this.$nextTick(() => {
        this.focusOptionalItem(first);
      });
    },

    openOptionalReviewDialog() {
      this.showOptionalReviewDialog =
        true;

      this.$nextTick(() => {
        this.$refs.optionalReviewDialog
          ?.focus?.();
      });
    },

    closeOptionalReviewDialog() {
      this.showOptionalReviewDialog =
        false;
    },

    async confirmOptionalRegistration() {
      this.closeOptionalReviewDialog();

      await this.registrarLibro({
        skipFrontValidation: true,
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

      if (this.optionalMissingCount > 0) {
        this.openOptionalReviewDialog();
        return;
      }

      await this.registrarLibro({
        skipFrontValidation: true,
      });
    },

    /* ========================================================
       NAVEGACIÓN / ERRORES
    ======================================================== */

    clearErrors() {
      this.fieldErrors = {};
      this.mensaje = "";
      this.mensajeTipo = "";
    },

    focusField(key) {
      const localIdMap = {
        admin_context:
          "lb-admin-context-anchor",

        origen_tipo:
          "lb-origen_tipo",

        origen_grado:
          "lb-origen_grado",

        nombre_libro:
          "lb-nombre_libro",

        anio_publicacion:
          "lb-anio_publicacion",

        mes_publicacion:
          "lb-mes_publicacion",

        codigo_isbn:
          "lb-codigo_isbn",

        editorial_compilador:
          "lb-editorial_compilador",

        revisor_par_arbitraje:
          "lb-revisor_par_arbitraje",

        link_libro:
          "lb-link_libro",

        autores:
          "lb-autores-anchor",

        archivos:
          "lb-archivo-input",
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

      if (
        key === "autores" ||
        key === "archivos" ||
        key === "admin_context"
      ) {
        element.scrollIntoView?.({
          behavior: "smooth",
          block: "center",
        });

        element.focus?.({
          preventScroll: true,
        });

        return;
      }

      if (
        typeof element.focus ===
        "function"
      ) {
        element.focus({
          preventScroll: false,
        });
      } else {
        element.scrollIntoView?.({
          behavior: "smooth",
          block: "center",
        });
      }
    },

    buildAutoresPayload() {
      const raw =
        Array.isArray(
          this.form.autores
        )
          ? this.form.autores
          : [];

      return raw
        .map(
          (autor, index) => {
            const id =
              Number(
                autor?.autor_id ??
                autor?.id ??
                autor?.autor?.id
              );

            if (
              !Number.isFinite(id) ||
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

    hasPendingRecoveredFiles() {
      return (
        Array.isArray(
          this.form.archivos
        )
          ? this.form.archivos
          : []
      ).some(
        (item) =>
          !item?.file &&
          item?.originalName
      );
    },

    selectedUploadItems() {
      return (
        Array.isArray(
          this.form.archivos
        )
          ? this.form.archivos
          : []
      ).filter(
        (item) =>
          item?.file
      );
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
          "Debe abrir este formulario desde la administración con un usuario objetivo válido."
        );
      }

      return null;
    },

    validateFront() {
      const errors = {};

      const general =
        this.form
          .datos_generales ||
        {};

      if (
        this.isAdminDelegado &&
        !this.adminContext
          .usuarioId
      ) {
        errors.admin_context =
          "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
      }

      if (!general.facultad) {
        errors.facultad =
          "Seleccione una facultad.";
      }

      if (!general.carrera) {
        errors.carrera =
          "Seleccione una carrera.";
      }
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
        ["tic", "otro"].includes(this.form.origen_tipo) &&
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
          this.form.origen_grado,
          FIELD_LIMITS.origen_grado
        )
      ) {
        errors.origen_grado =
          `El grado, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
      }

      if (
        !String(
          this.form
            .nombre_libro ||
          ""
        ).trim()
      ) {
        errors.nombre_libro =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form.nombre_libro,
          FIELD_LIMITS.nombre_libro
        )
      ) {
        errors.nombre_libro =
          `El nombre del libro no puede superar ${FIELD_LIMITS.nombre_libro} caracteres.`;
      }
      const publicationYear = Number(this.form.anio_publicacion);

      if (!Number.isInteger(publicationYear) || publicationYear <= 0) {
        errors.anio_publicacion =
          "Ingrese un año válido.";
      }

      if (this.form.mes_publicacion !== "") {
        const publicationMonth = Number(this.form.mes_publicacion);

        if (
          !Number.isInteger(publicationMonth) ||
          publicationMonth < 1 ||
          publicationMonth > 12
        ) {
          errors.mes_publicacion =
            "Seleccione un mes válido.";
        }
      }
if (
        !String(
          this.form
            .codigo_isbn ||
          ""
        ).trim()
      ) {
        errors.codigo_isbn =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form.codigo_isbn,
          FIELD_LIMITS.codigo_isbn
        )
      ) {
        errors.codigo_isbn =
          `El ISBN no puede superar ${FIELD_LIMITS.codigo_isbn} caracteres.`;
      }

      if (
        !String(
          this.form
            .editorial_compilador ||
          ""
        ).trim()
      ) {
        errors.editorial_compilador =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form.editorial_compilador,
          FIELD_LIMITS.editorial_compilador
        )
      ) {
        errors.editorial_compilador =
          `La editorial / compilador no puede superar ${FIELD_LIMITS.editorial_compilador} caracteres.`;
      }

      const arbitraje =
        String(
          this.form
            .revisor_par_arbitraje ||
          ""
        )
          .trim()
          .toLowerCase();

      if (
        ![
          "si",
          "no",
        ].includes(
          arbitraje
        )
      ) {
        errors.revisor_par_arbitraje =
          "Seleccione Sí o No.";
      }

      if (
        !String(
          this.form
            .link_libro ||
          ""
        ).trim()
      ) {
        errors.link_libro =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form.link_libro,
          FIELD_LIMITS.link_libro
        )
      ) {
        errors.link_libro =
          `El enlace del libro no puede superar ${FIELD_LIMITS.link_libro} caracteres.`;
      }

      if (
        !Array.isArray(
          this.form.autores
        ) ||
        this.form.autores
          .length === 0
      ) {
        errors.autores =
          "Debe registrar al menos un autor.";
      }

      if (
        this.hasPendingRecoveredFiles()
      ) {
        errors.archivos =
          "Hay adjuntos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
      }

      this.fieldErrors =
        errors;

      if (
        Object.keys(errors)
          .length
      ) {
        const first =
          firstErrorField(
            errors
          );

        this.mensaje =
          "Complete los campos obligatorios antes de guardar.";

        this.mensajeTipo =
          "error";

        if (first) {
          this.focusField(first);
        }

        return false;
      }

      return true;
    },

    appendCreateFiles(
      formData
    ) {
      const uploadItems =
        this.selectedUploadItems();

      if (!uploadItems.length) {
        return {
          attachments: [],
        };
      }

      /*
       * En el endpoint delegado, el backend procesa el
       * PDF principal y los adjuntos dentro de la misma
       * transacción.
       */
      if (this.isAdminDelegado) {
        appendArchivosToFormData(
          formData,
          uploadItems,
          {
            primaryField:
              "archivo_pdf",

            filesField:
              "archivos",

            metaField:
              "archivos_meta",
          }
        );

        return {
          attachments: [],
        };
      }

      /*
       * El endpoint estándar /libros/ consume únicamente
       * el PDF principal. Los adjuntos complementarios se
       * cargan después mediante bulk-upload.
       */
      appendArchivosToFormData(
        formData,
        uploadItems.slice(
          0,
          1
        ),
        {
          primaryField:
            "archivo_pdf",

          filesField:
            "archivos",

          metaField:
            "archivos_meta",
        }
      );

      return {
        attachments:
          uploadItems.slice(
            1
          ),
      };
    },

    async uploadStandardAttachments(
      publicacionId,
      attachments
    ) {
      if (!attachments.length) {
        return 0;
      }

      if (!positiveId(publicacionId)) {
        throw new Error(
          "El backend no devolvió un publicacion_id válido para asociar los adjuntos."
        );
      }

      const formData =
        new FormData();

      formData.append(
        "publicacion_id",
        String(publicacionId)
      );

      appendArchivosToFormData(
        formData,
        attachments,
        {
          primaryField:
            null,

          filesField:
            "archivos",

          metaField:
            "archivos_meta",
        }
      );

      await api.post(
        BULK_ATTACHMENTS_ENDPOINT,
        formData
      );

      return attachments.length;
    },

    finalizeSuccess(
      message
    ) {
      clearTimeout(
        this._draftTimer
      );

      try {
        localStorage.removeItem(
          this.draftStorageKey
        );
      } catch (error) {
        console.warn(
          "No se pudo eliminar el borrador después del registro.",
          error
        );
      }

      this.suspendDraftOnce();
      this.resetForm();

      this.mensaje =
        message;

      this.mensajeTipo =
        "success";
    },

    finalizePartialAttachmentFailure(
      publicacionId,
      error
    ) {
      /*
       * El libro ya fue creado. Se elimina el borrador y se
       * limpia el formulario para impedir un registro duplicado.
       */
      clearTimeout(
        this._draftTimer
      );

      try {
        localStorage.removeItem(
          this.draftStorageKey
        );
      } catch (storageError) {
        console.warn(
          "No se pudo eliminar el borrador después del registro.",
          storageError
        );
      }

      this.suspendDraftOnce();
      this.resetForm();

      this.fieldErrors =
        {};

      this.mensaje =
        `El libro fue registrado correctamente${
          publicacionId
            ? ` (publicación #${publicacionId})`
            : ""
        }, pero no se pudieron cargar los adjuntos complementarios. No vuelva a registrar el libro; agregue los adjuntos desde el detalle de la publicación.`;

      this.mensajeTipo =
        "error";

      console.error(
        "Libro creado, pero falló la carga de adjuntos:",
        error?.response?.data ||
        error
      );
    },

    async registrarLibro({ skipFrontValidation = false } = {}) {
      if (this.loading) {
        return;
      }

      this.loading = true;

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

        const autoresPayload =
          this.buildAutoresPayload();

        if (
          !autoresPayload.length
        ) {
          this.fieldErrors = {
            ...this.fieldErrors,

            autores:
              "Los autores seleccionados no tienen ID válido.",
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

        const formData =
          new FormData();

        Object.entries(
          this.form
            .datos_generales
        ).forEach(
          ([key, value]) => {
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

        appendIfPresent(
          formData,
          "origen_tipo",
          this.form.origen_tipo ||
            "ninguno"
        );

        if (
          ["tic", "otro"].includes(this.form.origen_tipo)
        ) {
          appendIfPresent(
            formData,
            "origen_grado",
            this.form
              .origen_grado
          );
        }

        const fields = [
          "nombre_libro",
          "anio_publicacion",
        "mes_publicacion",
          "codigo_isbn",
          "editorial_compilador",
          "revisor_par_arbitraje",
          "link_libro",
        ];

        fields.forEach(
          (key) => {
            appendIfPresent(
              formData,
              key,
              this.form[key]
            );
          }
        );

        formData.append(
          "autores",
          JSON.stringify(
            autoresPayload
          )
        );

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

        const {
          attachments,
        } =
          this.appendCreateFiles(
            formData
          );

        const endpoint =
          this.isAdminDelegado
            ? ADMIN_CREATE_ENDPOINT
            : STANDARD_CREATE_ENDPOINT;

        const response =
          await api.post(
            endpoint,
            formData
          );

        const publicacionId =
          extractPublicacionId(
            response?.data
          );

        if (
          !this.isAdminDelegado &&
          attachments.length
        ) {
          try {
            await this.uploadStandardAttachments(
              publicacionId,
              attachments
            );
          } catch (attachmentError) {
            this.finalizePartialAttachmentFailure(
              publicacionId,
              attachmentError
            );

            return;
          }
        }

        this.finalizeSuccess(
          this.isAdminDelegado
            ? "Libro registrado correctamente para el usuario seleccionado."
            : "Libro registrado exitosamente."
        );
      } catch (error) {
        const status =
          error?.response
            ?.status;

        const data =
          error?.response
            ?.data;

        if (status === 401) {
          this.mensaje =
            "Sesión expirada. Vuelva a iniciar sesión.";

          this.mensajeTipo =
            "error";

          return;
        }

        if (status === 403) {
          this.mensaje =
            "No tiene permisos para registrar este libro.";

          this.mensajeTipo =
            "error";

          return;
        }

        const normalized =
          normalizeDrfErrors(
            data
          );

        this.fieldErrors =
          normalized.fields ||
          {};

        this.mensaje =
          normalized.message ||
          "Error al registrar el libro.";

        this.mensajeTipo =
          "error";

        const first =
          firstErrorField(
            this.fieldErrors
          );

        if (first) {
          this.focusField(first);
        }

        console.error(
          "❌ Error libro:",
          data || error
        );
      } finally {
        this.loading = false;
      }
    },

    resetForm() {
      this.fieldErrors = {};
      this.draftInfo = "";
      this.showOptionalReviewDialog = false;
      this.form = createEmptyForm();
    },
  },
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
