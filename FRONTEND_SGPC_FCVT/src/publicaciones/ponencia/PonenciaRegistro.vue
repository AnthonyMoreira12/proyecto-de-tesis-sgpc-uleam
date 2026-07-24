<template>
  <div class="sgpc-form-page sgpc-form-page--ponencia">
    <div class="sgpc-form-shell">
      <!-- =====================================================
           ENCABEZADO
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
                Producción científica
              </span>

              <span
                class="sgpc-publication-chip sgpc-publication-chip--accent"
              >
                Ponencia
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
                d="M4 4h16v12H13v2h3v2H8v-2h3v-2H4V4Zm2 2v8h12V6H6Zm3 2h6v2H9V8Zm-2 3h10v2H7v-2Z"
              />
            </svg>
          </div>

          <span>PON</span>
          <small>Ponencia científica</small>
        </div>
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->

      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar una ponencia"
        enctype="multipart/form-data"
        @submit.prevent="registrarPonencia"
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
                  Esta ponencia se registrará para el usuario seleccionado
                  desde el módulo administrativo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div
                id="pn-admin-context-anchor"
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

                <article class="sgpc-admin-context__item">
                  <span class="sgpc-admin-context__label">
                    Modalidad
                  </span>

                  <strong class="sgpc-admin-context__value">
                    Registro administrativo delegado
                  </strong>
                </article>
              </div>

              <p class="sgpc-hint">
                El autor objetivo será incorporado por el backend dentro de la
                autoría de la publicación.
              </p>

              <p
                v-if="fieldErrors.admin_context"
                id="pn-admin-context-error"
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
                  Información institucional, área del conocimiento y ubicación
                  geográfica del evento.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <DatosGenerales
                v-model="form.datos_generales"
                :errors="fieldErrors"
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
                  Indique si la ponencia proviene de un trabajo académico o si
                  no posee un origen de este tipo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="pn-origen_tipo"
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
                    id="pn-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    required
                    :aria-invalid="Boolean(fieldErrors.origen_tipo)"
                    :aria-describedby="
                      fieldErrors.origen_tipo
                        ? 'pn-origen-tipo-error'
                        : undefined
                    "
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
                  </select>

                  <p
                    v-if="fieldErrors.origen_tipo"
                    id="pn-origen-tipo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="pn-origen_grado"
                  >
                    Grado / programa

                    <span
                      v-if="form.origen_tipo === 'tic'"
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="pn-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    :disabled="form.origen_tipo !== 'tic'"
                    :required="form.origen_tipo === 'tic'"
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="
                      fieldErrors.origen_grado
                        ? 'pn-origen-grado-error'
                        : undefined
                    "
                    placeholder="Ej. Ingeniería de Software"
                  />

                  <p class="sgpc-hint">
                    Se habilita cuando el origen es “Trabajo de integración
                    curricular”.
                  </p>

                  <p
                    v-if="fieldErrors.origen_grado"
                    id="pn-origen-grado-error"
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
               EVENTO Y PONENCIA
          ================================================== -->

          <section
            id="sec-evento"
            class="sgpc-card"
            data-section="03"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Evento y ponencia
                </h2>

                <p class="sgpc-card-desc">
                  Información del evento académico, trabajo presentado,
                  modalidad de exposición y enlaces de respaldo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <!-- Nombre evento -->
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="pn-nombre_evento"
                  >
                    Nombre del evento

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="pn-nombre_evento"
                    v-model.trim="form.nombre_evento"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    required
                    :aria-invalid="Boolean(fieldErrors.nombre_evento)"
                    :aria-describedby="
                      fieldErrors.nombre_evento
                        ? 'pn-nombre-evento-error'
                        : undefined
                    "
                    placeholder="Ej. Congreso Internacional de Ciencia y Tecnología"
                  />

                  <p
                    v-if="fieldErrors.nombre_evento"
                    id="pn-nombre-evento-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_evento }}
                  </p>
                </div>

                <!-- Nombre ponencia -->
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="pn-nombre_ponencia"
                  >
                    Nombre de la ponencia

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="pn-nombre_ponencia"
                    v-model.trim="form.nombre_ponencia"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    required
                    :aria-invalid="Boolean(fieldErrors.nombre_ponencia)"
                    :aria-describedby="
                      fieldErrors.nombre_ponencia
                        ? 'pn-nombre-ponencia-error'
                        : undefined
                    "
                    placeholder="Ej. Innovación tecnológica aplicada a la investigación científica"
                  />

                  <p
                    v-if="fieldErrors.nombre_ponencia"
                    id="pn-nombre-ponencia-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_ponencia }}
                  </p>
                </div>

                <!-- Fecha -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="pn-fecha_publicacion"
                  >
                    Fecha de presentación

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="pn-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    required
                    :aria-invalid="Boolean(fieldErrors.fecha_publicacion)"
                    :aria-describedby="
                      fieldErrors.fecha_publicacion
                        ? 'pn-fecha-publicacion-error'
                        : undefined
                    "
                  />

                  <p class="sgpc-hint">
                    Corresponde a la fecha en la que se presentó o expuso el
                    trabajo.
                  </p>

                  <p
                    v-if="fieldErrors.fecha_publicacion"
                    id="pn-fecha-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <!-- ISSN / ISBN -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="pn-codigo_issn_isbn"
                  >
                    Código ISSN / ISBN
                  </label>

                  <input
                    id="pn-codigo_issn_isbn"
                    v-model.trim="form.codigo_issn_isbn"
                    class="sgpc-input"
                    type="text"
                    maxlength="100"
                    :aria-invalid="Boolean(fieldErrors.codigo_issn_isbn)"
                    :aria-describedby="
                      fieldErrors.codigo_issn_isbn
                        ? 'pn-codigo-issn-isbn-error'
                        : undefined
                    "
                    placeholder="Ej. 1234-5678 o 978-9942-00-0000-0"
                  />

                  <p class="sgpc-hint">
                    Registre el código de las memorias o actas del evento,
                    cuando corresponda.
                  </p>

                  <p
                    v-if="fieldErrors.codigo_issn_isbn"
                    id="pn-codigo-issn-isbn-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_issn_isbn }}
                  </p>
                </div>

                <!-- Tipo presentación -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="pn-tipo_presentacion"
                  >
                    Tipo de presentación
                  </label>

                  <select
                    id="pn-tipo_presentacion"
                    v-model="form.tipo_presentacion"
                    class="sgpc-input"
                    :aria-invalid="Boolean(fieldErrors.tipo_presentacion)"
                    :aria-describedby="
                      fieldErrors.tipo_presentacion
                        ? 'pn-tipo-presentacion-error'
                        : undefined
                    "
                  >
                    <option value="">
                      Seleccione...
                    </option>

                    <option value="magistral">
                      Conferencia magistral
                    </option>

                    <option value="oral">
                      Conferencia oral
                    </option>

                    <option value="poster">
                      Póster
                    </option>

                    <option value="otro">
                      Otro
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.tipo_presentacion"
                    id="pn-tipo-presentacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.tipo_presentacion }}
                  </p>
                </div>

                <!-- Otro -->
                <div
                  v-if="form.tipo_presentacion === 'otro'"
                  class="sgpc-field sgpc-col-span-6"
                >
                  <label
                    class="sgpc-label"
                    for="pn-tipo_presentacion_otro"
                  >
                    Especifique el tipo de presentación

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="pn-tipo_presentacion_otro"
                    v-model.trim="form.tipo_presentacion_otro"
                    class="sgpc-input"
                    type="text"
                    maxlength="150"
                    required
                    :aria-invalid="
                      Boolean(fieldErrors.tipo_presentacion_otro)
                    "
                    :aria-describedby="
                      fieldErrors.tipo_presentacion_otro
                        ? 'pn-tipo-presentacion-otro-error'
                        : undefined
                    "
                    placeholder="Ej. Mesa redonda, taller o panel"
                  />

                  <p
                    v-if="fieldErrors.tipo_presentacion_otro"
                    id="pn-tipo-presentacion-otro-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.tipo_presentacion_otro }}
                  </p>
                </div>

                <!-- Link -->
                <div
                  class="sgpc-field"
                  :class="
                    form.tipo_presentacion === 'otro'
                      ? 'sgpc-col-span-12'
                      : 'sgpc-col-span-6'
                  "
                >
                  <label
                    class="sgpc-label"
                    for="pn-link_evento"
                  >
                    Link del evento
                  </label>

                  <input
                    id="pn-link_evento"
                    v-model.trim="form.link_evento"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    :aria-invalid="Boolean(fieldErrors.link_evento)"
                    :aria-describedby="
                      fieldErrors.link_evento
                        ? 'pn-link-evento-error'
                        : undefined
                    "
                    placeholder="https://..."
                  />

                  <p class="sgpc-hint">
                    Puede incluir la página oficial, memorias, programa o
                    repositorio del evento.
                  </p>

                  <p
                    v-if="fieldErrors.link_evento"
                    id="pn-link-evento-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_evento }}
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
            data-section="04"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Autores
                </h2>

                <p class="sgpc-card-desc">
                  Seleccione los autores y establezca el orden de firma de la
                  ponencia.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div
                id="pn-autores-anchor"
                tabindex="-1"
              ></div>

              <AutoresSelector
                v-model="form.autores"
                :error="fieldErrors.autores"
              />
            </div>
          </section>

          <!-- =================================================
               ARCHIVOS PDF
          ================================================== -->

          <section
            id="sec-adjuntos"
            class="sgpc-card"
            data-section="05"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Archivos PDF
                </h2>

                <p class="sgpc-card-desc">
                  Adjunte el documento principal de la ponencia y los soportes
                  complementarios disponibles.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="pn-archivo-input"
                title="Agregar archivos PDF"
                description="El primer archivo será el PDF principal de la ponencia. Puede agregar hasta 2 adjuntos adicionales."
                helper-text="PDF principal hasta 5 MB. Adjuntos hasta 3 MB. Máximo 3 archivos."
                :multiple="true"
                :max-files="3"
                :uses-primary-slot="true"
                :primary-max-size-mb="5"
                :attachment-max-size-mb="3"
              />
            </div>
          </section>

          <!-- =================================================
               MENSAJE GLOBAL
          ================================================== -->

          <div
            v-if="mensaje"
            :class="[
              'sgpc-alert',
              `is-${mensajeTipo}`,
            ]"
            :role="mensajeTipo === 'error' ? 'alert' : 'status'"
            :aria-live="
              mensajeTipo === 'error'
                ? 'assertive'
                : 'polite'
            "
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
                    d="M4 4h16v12H13v2h3v2H8v-2h3v-2H4V4Zm2 2v8h12V6H6Zm3 2h6v2H9V8Z"
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
                v-if="isAdminDelegado"
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': adminReady,
                }"
                @click="goTo('sec-contexto-admin')"
              >
                <div>
                  <strong>
                    Contexto administrativo
                  </strong>

                  <span>
                    {{
                      adminReady
                        ? "Usuario objetivo válido"
                        : "Falta usuario objetivo"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    adminReady
                      ? "Completo"
                      : "Pendiente"
                  }}
                </em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': hasRequiredContext,
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
                  'is-ok': hasRequiredEvent,
                }"
                @click="goTo('sec-evento')"
              >
                <div>
                  <strong>
                    Evento y ponencia
                  </strong>

                  <span>
                    {{
                      hasRequiredEvent
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredEvent
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
                }"
                @click="goTo('sec-adjuntos')"
              >
                <div>
                  <strong>
                    Archivos PDF
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

/* ============================================================
   CONFIGURACIÓN
============================================================ */

const BASE_STORAGE_KEY =
  "sgpc-ponencia-draft:v23";

const STANDARD_CREATE_ENDPOINT =
  "/ponencias/registrar/";

const ADMIN_CREATE_ENDPOINT =
  "/admin/publicaciones/ponencias/crear/";

const BULK_ATTACHMENTS_ENDPOINT =
  "/archivos-publicacion/bulk-upload/";

const FIELD_LIMITS = Object.freeze({
  origen_grado: 120,
  nombre_evento: 255,
  nombre_ponencia: 255,
  codigo_issn_isbn: 100,
  tipo_presentacion_otro: 150,
  link_evento: 500,
});

const VALID_PRESENTATION_TYPES =
  new Set([
    "",
    "magistral",
    "oral",
    "poster",
    "otro",
  ]);

/* ============================================================
   ERRORES
============================================================ */

const ERROR_KEY_ALIASES = Object.freeze({
  meta: "archivos",
  archivos_meta: "archivos",
  files: "archivos",
  archivos: "archivos",
  archivo: "archivos",
  archivo_pdf: "archivos",
  non_field_errors: "admin_context",
});

const FIELD_LABELS = Object.freeze({
  admin_context: "Contexto administrativo",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento",
  subarea: "Subárea del conocimiento",
  pais: "País",
  ciudad: "Ciudad",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa",
  nombre_evento: "Nombre del evento",
  nombre_ponencia: "Nombre de la ponencia",
  fecha_publicacion: "Fecha de presentación",
  codigo_issn_isbn: "Código ISSN / ISBN",
  tipo_presentacion: "Tipo de presentación",
  tipo_presentacion_otro: "Otro tipo de presentación",
  link_evento: "Link del evento",
  autores: "Autores",
  archivos: "Archivos PDF",
});

const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "pais",
  "ciudad",
  "origen_tipo",
  "origen_grado",
  "nombre_evento",
  "nombre_ponencia",
  "fecha_publicacion",
  "codigo_issn_isbn",
  "tipo_presentacion",
  "tipo_presentacion_otro",
  "link_evento",
  "autores",
  "archivos",
]);

/* ============================================================
   ESTADO INICIAL
============================================================ */

function createDefaultDatosGenerales() {
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
    datos_generales:
      createDefaultDatosGenerales(),

    origen_tipo: "",
    origen_grado: "",

    nombre_evento: "",
    nombre_ponencia: "",
    fecha_publicacion: "",
    codigo_issn_isbn: "",
    tipo_presentacion: "",
    tipo_presentacion_otro: "",
    link_evento: "",

    autores: [],
    archivos: [],
  };
}

/* ============================================================
   HELPERS
============================================================ */

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
    typeof data.errors === "object" &&
    data.errors !== null
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

      if (fields.admin_context) {
        message =
          fields.admin_context;
      } else if (fields.autores) {
        message =
          "Revise la sección de autores: debe existir al menos un autor y el orden debe ser válido.";
      } else if (fields.archivos) {
        message =
          "Revise la sección de archivos PDF.";
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
      message:
        data.detail,
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
    if (fields?.[key]) {
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

function extractPublicacionId(data) {
  return positiveId(
    data?.publicacion_id ??
    data?.publicacion?.id ??
    data?.ponencia?.publicacion_id
  );
}

/* ============================================================
   COMPONENTE
============================================================ */

export default {
  name: "PonenciaRegistro",

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
      draftSuspended: false,

      adminContext: {
        usuarioId: null,
        autorId: null,
        usuarioNombre: "",
        autorNombre: "",
      },

      form:
        createDefaultForm(),
    };
  },

  /* ==========================================================
     COMPUTED
  ========================================================== */

  computed: {
    isAdminDelegado() {
      const path =
        String(
          this.$route?.path ||
          ""
        );

      const query =
        this.$route?.query ||
        {};

      const params =
        this.$route?.params ||
        {};

      return Boolean(
        this.$route?.meta
          ?.delegatedPublication ||

        path.startsWith(
          "/admin/publicaciones/usuario/"
        ) ||

        params.usuarioId ||

        query.modo ===
          "delegado" ||

        query.delegado ===
          "1" ||

        query.admin ===
          "1"
      );
    },

    draftStorageKey() {
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

        positiveId(
          this.$route?.params
            ?.usuarioId
        ) ||

        "sin-usuario";

      return (
        `${BASE_STORAGE_KEY}:admin:${usuarioId}`
      );
    },

    adminReady() {
      if (
        !this.isAdminDelegado
      ) {
        return true;
      }

      return Boolean(
        this.adminContext
          .usuarioId
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
       * Usuario.id y Autor.id pertenecen a tablas distintas.
       * Nunca deben compararse entre sí.
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
      return (
        this.isAdminDelegado
          ? "Administración · Ponencias"
          : "Ponencias y eventos"
      );
    },

    pageTitle() {
      return (
        "Registrar Ponencia"
      );
    },

    pageSubtitle() {
      return (
        this.isAdminDelegado
          ? "Registre la información del evento, ubicación, presentación, autores y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios."
          : "Registre la información del evento, ubicación, presentación, autores y adjuntos. Los campos marcados con * son obligatorios."
      );
    },

    submitText() {
      return (
        this.isAdminDelegado
          ? "Registrar ponencia para el usuario"
          : "Registrar ponencia"
      );
    },

    submitLoadingText() {
      return (
        this.isAdminDelegado
          ? "Guardando registro delegado..."
          : "Guardando..."
      );
    },

    hasRequiredContext() {
      const general =
        this.form
          .datos_generales ||
        {};

      return Boolean(
        general.facultad &&
        general.carrera &&
        general.area &&
        general.subarea &&
        general.pais &&
        general.ciudad
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
        this.form
          .origen_tipo ===
        "tic"
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

    hasRequiredEvent() {
      const basic =
        Boolean(
          String(
            this.form
              .nombre_evento ||
            ""
          ).trim() &&

          String(
            this.form
              .nombre_ponencia ||
            ""
          ).trim() &&

          this.form
            .fecha_publicacion
        );

      if (!basic) {
        return false;
      }

      if (
        this.form
          .tipo_presentacion ===
          "otro" &&

        !String(
          this.form
            .tipo_presentacion_otro ||
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

    requiredSections() {
      const sections = [
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
          key: "evento",
          done:
            this.hasRequiredEvent,
        },

        {
          key: "autores",
          done:
            this.hasRequiredAuthors,
        },
      ];

      if (
        this.isAdminDelegado
      ) {
        return [
          {
            key: "admin",
            done:
              this.adminReady,
          },

          ...sections,
        ];
      }

      return sections;
    },

    completedRequiredCount() {
      return (
        this.requiredSections
          .filter(
            (section) =>
              section.done
          )
          .length
      );
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
        ) *
        100
      );
    },
  },

  /* ==========================================================
     CICLO DE VIDA
  ========================================================== */

  created() {
    this.hydrateAdminContextFromRoute();
    this.loadDraft();
  },

  beforeUnmount() {
    clearTimeout(
      this.draftTimer
    );
  },

  /* ==========================================================
     WATCHERS
  ========================================================== */

  watch: {
    form: {
      deep: true,

      handler(value) {
        if (
          this.draftSuspended
        ) {
          return;
        }

        clearTimeout(
          this.draftTimer
        );

        this.draftTimer =
          setTimeout(
            () => {
              const payload = {
                form: {
                  datos_generales: {
                    ...(
                      value
                        .datos_generales ||
                      {}
                    ),
                  },

                  origen_tipo:
                    value.origen_tipo,

                  origen_grado:
                    value.origen_grado,

                  nombre_evento:
                    value.nombre_evento,

                  nombre_ponencia:
                    value.nombre_ponencia,

                  fecha_publicacion:
                    value.fecha_publicacion,

                  codigo_issn_isbn:
                    value.codigo_issn_isbn,

                  tipo_presentacion:
                    value.tipo_presentacion,

                  tipo_presentacion_otro:
                    value.tipo_presentacion_otro,

                  link_evento:
                    value.link_evento,

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
                localStorage
                  .setItem(
                    this
                      .draftStorageKey,

                    JSON.stringify(
                      payload
                    )
                  );
              } catch (
                error
              ) {
                console.warn(
                  "No se pudo guardar el borrador de la ponencia.",
                  error
                );
              }
            },

            250
          );
      },
    },

    "form.origen_tipo"(
      value
    ) {
      if (
        value !==
        "tic"
      ) {
        this.form
          .origen_grado =
          "";
      }
    },

    "form.tipo_presentacion"(
      value
    ) {
      if (
        value !==
        "otro"
      ) {
        this.form
          .tipo_presentacion_otro =
          "";
      }
    },

    "$route.fullPath"() {
      this.handleRouteContextChange();
    },
  },

  /* ==========================================================
     MÉTODOS
  ========================================================== */

  methods: {
    /* ========================================================
       CONTEXTO ADMINISTRATIVO
    ======================================================== */

    hydrateAdminContextFromRoute() {
      const query =
        this.$route?.query ||
        {};

      const params =
        this.$route?.params ||
        {};

      this.adminContext = {
        usuarioId:
          positiveId(
            params.usuarioId ||

            query.usuario_objetivo_id ||

            query.usuario_id ||

            query.usuarioId ||

            query.user_id
          ),

        autorId:
          positiveId(
            params.autorId ||

            query.autor_objetivo_id ||

            query.autor_id ||

            query.autorId ||

            query.author_id
          ),

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
          "Debe abrir este formulario desde la administración con un usuario objetivo válido."
        );
      }

      return null;
    },

    /* ========================================================
       BORRADOR
    ======================================================== */

    loadDraft() {
      let raw =
        null;

      try {
        raw =
          localStorage
            .getItem(
              this
                .draftStorageKey
            );
      } catch (
        error
      ) {
        console.warn(
          "No se pudo leer el borrador de la ponencia.",
          error
        );

        return;
      }

      if (!raw) {
        return;
      }

      try {
        const parsed =
          JSON.parse(
            raw
          );

        const incoming =
          parsed.form ||
          parsed ||
          {};

        const empty =
          createDefaultForm();

        this.form = {
          ...empty,
          ...incoming,

          datos_generales: {
            ...empty
              .datos_generales,

            ...(
              incoming
                .datos_generales ||
              {}
            ),
          },

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
      } catch (
        error
      ) {
        console.warn(
          "El borrador de la ponencia está corrupto y será ignorado.",
          error
        );
      }
    },

    suspendDraftOnce() {
      this.draftSuspended =
        true;

      this.$nextTick(
        () => {
          this.draftSuspended =
            false;
        }
      );
    },

    removeStoredDraft() {
      clearTimeout(
        this.draftTimer
      );

      try {
        localStorage
          .removeItem(
            this
              .draftStorageKey
          );
      } catch (
        error
      ) {
        console.warn(
          "No se pudo eliminar el borrador de la ponencia.",
          error
        );
      }
    },

    clearDraft() {
      this.removeStoredDraft();

      this.suspendDraftOnce();

      this.resetForm();

      this.mensaje =
        "Borrador eliminado.";

      this.mensajeTipo =
        "info";
    },

    handleRouteContextChange() {
      clearTimeout(
        this.draftTimer
      );

      this.hydrateAdminContextFromRoute();

      this.suspendDraftOnce();

      this.resetForm();

      this.loadDraft();
    },

    /* ========================================================
       NAVEGACIÓN / ERRORES
    ======================================================== */

    clearErrors() {
      this.fieldErrors =
        {};

      this.mensaje =
        "";

      this.mensajeTipo =
        "";
    },

    goTo(id) {
      const element =
        document
          .getElementById(
            id
          );

      element
        ?.scrollIntoView({
          behavior:
            "smooth",

          block:
            "start",
        });
    },

    focusField(key) {
      const localIdMap = {
        admin_context:
          "pn-admin-context-anchor",

        origen_tipo:
          "pn-origen_tipo",

        origen_grado:
          "pn-origen_grado",

        nombre_evento:
          "pn-nombre_evento",

        nombre_ponencia:
          "pn-nombre_ponencia",

        fecha_publicacion:
          "pn-fecha_publicacion",

        codigo_issn_isbn:
          "pn-codigo_issn_isbn",

        tipo_presentacion:
          "pn-tipo_presentacion",

        tipo_presentacion_otro:
          "pn-tipo_presentacion_otro",

        link_evento:
          "pn-link_evento",

        autores:
          "pn-autores-anchor",

        archivos:
          "pn-archivo-input",
      };

      const element =
        document
          .getElementById(
            `dg-${key}`
          ) ||

        document
          .getElementById(
            localIdMap[key] ||
            ""
          );

      if (!element) {
        return;
      }

      element
        .scrollIntoView
        ?.({
          behavior:
            "smooth",

          block:
            "center",
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

          250
        );
      }
    },

    /* ========================================================
       AUTORES
    ======================================================== */

    buildAutoresPayload() {
      const raw =
        Array.isArray(
          this.form
            .autores
        )
          ? this.form
              .autores
          : [];

      return raw
        .map(
          (
            autor,
            index
          ) => {
            const id =
              positiveId(
                autor?.autor_id ??

                autor?.id ??

                autor?.autor?.id
              );

            if (!id) {
              return null;
            }

            const orden =
              index +
              1;

            return {
              autor_id:
                id,

              orden,

              rol_autoria:
                orden ===
                1
                  ? "principal"
                  : "coautor",
            };
          }
        )
        .filter(
          Boolean
        );
    },

    /* ========================================================
       ARCHIVOS
    ======================================================== */

    hasPendingRecoveredFiles() {
      const archivos =
        Array.isArray(
          this.form
            .archivos
        )
          ? this.form
              .archivos
          : [];

      return archivos
        .some(
          (item) =>
            !item?.file &&
            Boolean(
              item?.originalName
            )
        );
    },

    selectedUploadItems() {
      return (
        Array.isArray(
          this.form
            .archivos
        )
          ? this.form
              .archivos
          : []
      ).filter(
        (item) =>
          item?.file
      );
    },

    /* ========================================================
       VALIDACIÓN
    ======================================================== */

    validateFront() {
      const errors =
        {};

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

      if (
        !general
          .facultad
      ) {
        errors.facultad =
          "Seleccione una facultad.";
      }

      if (
        !general
          .carrera
      ) {
        errors.carrera =
          "Seleccione una carrera.";
      }

      if (
        !general
          .area
      ) {
        errors.area =
          "Seleccione un área del conocimiento.";
      }

      if (
        !general
          .subarea
      ) {
        errors.subarea =
          "Seleccione una subárea del conocimiento.";
      }

      if (
        !general
          .pais
      ) {
        errors.pais =
          "Seleccione un país.";
      }

      if (
        !general
          .ciudad
      ) {
        errors.ciudad =
          "Seleccione una ciudad.";
      }

      /* ----------------------------------------------------
         Origen
      ---------------------------------------------------- */

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
        this.form
          .origen_tipo ===
          "tic" &&

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
          `El grado / programa no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
      }

      /* ----------------------------------------------------
         Evento
      ---------------------------------------------------- */

      if (
        !String(
          this.form
            .nombre_evento ||
          ""
        ).trim()
      ) {
        errors.nombre_evento =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form
            .nombre_evento,

          FIELD_LIMITS
            .nombre_evento
        )
      ) {
        errors.nombre_evento =
          `El nombre del evento no puede superar ${FIELD_LIMITS.nombre_evento} caracteres.`;
      }

      if (
        !String(
          this.form
            .nombre_ponencia ||
          ""
        ).trim()
      ) {
        errors.nombre_ponencia =
          "Campo obligatorio.";
      } else if (
        exceedsLength(
          this.form
            .nombre_ponencia,

          FIELD_LIMITS
            .nombre_ponencia
        )
      ) {
        errors.nombre_ponencia =
          `El nombre de la ponencia no puede superar ${FIELD_LIMITS.nombre_ponencia} caracteres.`;
      }

      if (
        !this.form
          .fecha_publicacion
      ) {
        errors.fecha_publicacion =
          "Campo obligatorio.";
      }

      if (
        exceedsLength(
          this.form
            .codigo_issn_isbn,

          FIELD_LIMITS
            .codigo_issn_isbn
        )
      ) {
        errors.codigo_issn_isbn =
          `El código ISSN / ISBN no puede superar ${FIELD_LIMITS.codigo_issn_isbn} caracteres.`;
      }

      /* ----------------------------------------------------
         Presentación
      ---------------------------------------------------- */

      const presentation =
        String(
          this.form
            .tipo_presentacion ||
          ""
        )
          .trim()
          .toLowerCase();

      if (
        !VALID_PRESENTATION_TYPES
          .has(
            presentation
          )
      ) {
        errors.tipo_presentacion =
          "Seleccione un tipo de presentación válido.";
      }

      if (
        presentation ===
          "otro" &&

        !String(
          this.form
            .tipo_presentacion_otro ||
          ""
        ).trim()
      ) {
        errors.tipo_presentacion_otro =
          "Debe especificar el tipo de presentación.";
      }

      if (
        exceedsLength(
          this.form
            .tipo_presentacion_otro,

          FIELD_LIMITS
            .tipo_presentacion_otro
        )
      ) {
        errors.tipo_presentacion_otro =
          `El tipo de presentación no puede superar ${FIELD_LIMITS.tipo_presentacion_otro} caracteres.`;
      }

      if (
        exceedsLength(
          this.form
            .link_evento,

          FIELD_LIMITS
            .link_evento
        )
      ) {
        errors.link_evento =
          `El enlace no puede superar ${FIELD_LIMITS.link_evento} caracteres.`;
      }

      /* ----------------------------------------------------
         Autores
      ---------------------------------------------------- */

      if (
        !Array.isArray(
          this.form
            .autores
        ) ||

        this.form
          .autores
          .length ===
          0
      ) {
        errors.autores =
          "Debe registrar al menos un autor.";
      }

      /* ----------------------------------------------------
         Borradores de archivos
      ---------------------------------------------------- */

      if (
        this.hasPendingRecoveredFiles()
      ) {
        errors.archivos =
          "Hay archivos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
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

    /* ========================================================
       FORMDATA BASE
    ======================================================== */

    buildCreateFormData(
      autoresPayload
    ) {
      const formData =
        new FormData();

      const general =
        this.form
          .datos_generales ||
        {};

      Object.entries(
        general
      ).forEach(
        (
          [
            key,
            value,
          ]
        ) => {
          /*
           * PonenciaRegistroSerializer no recibe Facultad.
           *
           * Facultad se deriva de:
           *
           * carrera.facultad
           *
           * El selector de Facultad sigue siendo necesario
           * en la interfaz para filtrar Carreras.
           */
          if (
            key ===
            "facultad"
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
        this.form
          .origen_tipo ||
        "ninguno"
      );

      if (
        this.form
          .origen_tipo ===
        "tic"
      ) {
        appendIfPresent(
          formData,
          "origen_grado",
          this.form
            .origen_grado
        );
      }

      [
        "nombre_evento",
        "nombre_ponencia",
        "fecha_publicacion",
        "codigo_issn_isbn",
        "tipo_presentacion",
        "link_evento",
      ].forEach(
        (key) => {
          appendIfPresent(
            formData,
            key,
            this.form[
              key
            ]
          );
        }
      );

      if (
        this.form
          .tipo_presentacion ===
        "otro"
      ) {
        appendIfPresent(
          formData,
          "tipo_presentacion_otro",
          this.form
            .tipo_presentacion_otro
        );
      }

      formData.append(
        "autores",
        JSON.stringify(
          autoresPayload
        )
      );

      /*
       * La creación administrativa obtiene el usuario
       * objetivo mediante estos campos.
       */
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

      return formData;
    },

    /* ========================================================
       PDF PRINCIPAL Y ADJUNTOS
    ======================================================== */

    appendCreateFiles(
      formData
    ) {
      const uploadItems =
        this
          .selectedUploadItems();

      if (
        !uploadItems
          .length
      ) {
        return {
          attachments:
            [],
        };
      }

      /*
       * ADMINISTRADOR
       *
       * AdminPublicacionViewSet procesa:
       *
       * - archivo_pdf
       * - archivos
       * - archivos_meta
       *
       * en la misma transacción de creación.
       */
      if (
        this.isAdminDelegado
      ) {
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
          attachments:
            [],
        };
      }

      /*
       * USUARIO NORMAL
       *
       * PonenciaRegistroSerializer procesa únicamente:
       *
       * archivo_pdf
       *
       * Por eso mandamos aquí solamente el primero.
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

      /*
       * Los demás se subirán después de conocer
       * publicacion_id.
       */
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
      if (
        !attachments
          .length
      ) {
        return 0;
      }

      if (
        !positiveId(
          publicacionId
        )
      ) {
        throw new Error(
          "El backend no devolvió un publicacion_id válido para asociar los adjuntos."
        );
      }

      const formData =
        new FormData();

      formData.append(
        "publicacion_id",
        String(
          publicacionId
        )
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

      return (
        attachments
          .length
      );
    },

    /* ========================================================
       FINALIZACIÓN
    ======================================================== */

    finalizeSuccess(
      message
    ) {
      this.removeStoredDraft();

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
       * La publicación YA fue creada.
       *
       * No debemos conservar el formulario completo porque
       * el usuario podría pulsar nuevamente "Registrar" y
       * crear una ponencia duplicada.
       */
      this.removeStoredDraft();

      this.suspendDraftOnce();

      this.resetForm();

      this.fieldErrors =
        {};

      this.mensaje =
        `La ponencia fue registrada correctamente${
          publicacionId
            ? ` (publicación #${publicacionId})`
            : ""
        }, pero no se pudieron cargar los adjuntos complementarios. No vuelva a registrar la ponencia; agregue los adjuntos desde el detalle de la publicación.`;

      this.mensajeTipo =
        "error";

      console.error(
        "Ponencia creada, pero falló la carga de adjuntos:",
        error?.response
          ?.data ||
        error
      );
    },

    /* ========================================================
       REGISTRO
    ======================================================== */

    async registrarPonencia() {
      if (
        this.loading
      ) {
        return;
      }

      this.loading =
        true;

      this.clearErrors();

      try {
        /* --------------------------------------------------
           1. Validación frontend
        -------------------------------------------------- */

        if (
          !this.validateFront()
        ) {
          return;
        }

        /* --------------------------------------------------
           2. Autores
        -------------------------------------------------- */

        const autoresPayload =
          this
            .buildAutoresPayload();

        if (
          !autoresPayload
            .length
        ) {
          this.fieldErrors = {
            ...this
              .fieldErrors,

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

        /* --------------------------------------------------
           3. Contexto administrativo
        -------------------------------------------------- */

        const adminValidationError =
          this
            .validateAdminContext();

        if (
          adminValidationError
        ) {
          this.fieldErrors = {
            ...this
              .fieldErrors,

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

        /* --------------------------------------------------
           4. FormData
        -------------------------------------------------- */

        const formData =
          this
            .buildCreateFormData(
              autoresPayload
            );

        const {
          attachments,
        } =
          this
            .appendCreateFiles(
              formData
            );

        /* --------------------------------------------------
           5. Crear publicación
        -------------------------------------------------- */

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

        /* --------------------------------------------------
           6. Adjuntos adicionales usuario normal
        -------------------------------------------------- */

        if (
          !this.isAdminDelegado &&
          attachments.length
        ) {
          try {
            await this
              .uploadStandardAttachments(
                publicacionId,
                attachments
              );
          } catch (
            attachmentError
          ) {
            this
              .finalizePartialAttachmentFailure(
                publicacionId,
                attachmentError
              );

            return;
          }
        }

        /* --------------------------------------------------
           7. Éxito
        -------------------------------------------------- */

        this.finalizeSuccess(
          this.isAdminDelegado
            ? "Ponencia registrada correctamente para el usuario seleccionado."
            : "Ponencia registrada correctamente."
        );
      } catch (
        error
      ) {
        const status =
          error?.response
            ?.status;

        const data =
          error?.response
            ?.data;

        /* --------------------------------------------------
           401
        -------------------------------------------------- */

        if (
          status ===
          401
        ) {
          this.mensaje =
            "La sesión ha expirado. Vuelva a iniciar sesión.";

          this.mensajeTipo =
            "error";

          return;
        }

        /* --------------------------------------------------
           403
        -------------------------------------------------- */

        if (
          status ===
          403
        ) {
          this.mensaje =
            "No tiene permisos para registrar esta ponencia.";

          this.mensajeTipo =
            "error";

          return;
        }

        /* --------------------------------------------------
           DRF
        -------------------------------------------------- */

        const normalized =
          normalizeDrfErrors(
            data
          );

        this.fieldErrors =
          normalized
            .fields ||
          {};

        this.mensaje =
          normalized
            .message ||
          "No se pudo registrar la ponencia.";

        this.mensajeTipo =
          "error";

        const first =
          firstErrorField(
            this
              .fieldErrors
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
          "Error al registrar la ponencia:",
          data ||
          error
        );
      } finally {
        this.loading =
          false;
      }
    },

    /* ========================================================
       RESET
    ======================================================== */

    resetForm() {
      this.fieldErrors =
        {};

      this.draftInfo =
        "";

      this.form =
        createDefaultForm();
    },
  },
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
<style src="./ponencia-registro.css"></style>