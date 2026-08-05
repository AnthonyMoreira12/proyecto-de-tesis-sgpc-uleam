<template>
  <div class="sgpc-form-page sgpc-form-page--capitulo-libro">
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
                Publicación científica
              </span>

              <span
                class="sgpc-publication-chip sgpc-publication-chip--accent"
              >
                Capítulo de libro
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
                d="M5 3h11a3 3 0 0 1 3 3v15H8a3 3 0 0 1-3-3V3Zm3 2H7v13a1 1 0 0 0 1 1h9V6a1 1 0 0 0-1-1H8Zm1 3h6v2H9V8Zm0 4h6v2H9v-2Z"
              />
            </svg>
          </div>

          <span>CAP</span>
          <small>Capítulo de libro</small>
        </div>
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->
      <form
        class="sgpc-form sgpc-form--with-aside"
        aria-label="Formulario para registrar un capítulo de libro"
        enctype="multipart/form-data"
        @submit.prevent="registrarCapitulo"
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
                id="cl-admin-context-anchor"
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
                id="cl-admin-context-error"
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
                  Indique la relación académica del capítulo registrado.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <!-- Origen tipo -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-origen_tipo"
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
                    id="cl-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    required
                    :aria-invalid="Boolean(fieldErrors.origen_tipo)"
                    :aria-describedby="
                      fieldErrors.origen_tipo
                        ? 'cl-origen-tipo-error'
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

                    <option value="otro">
                      Otro
                    </option>
                  </select>

                  <p
                    v-if="fieldErrors.origen_tipo"
                    id="cl-origen-tipo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <!-- Origen grado -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-origen_grado"
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
                    id="cl-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    :disabled="!['tic', 'otro'].includes(form.origen_tipo)"
                    :required="['tic', 'otro'].includes(form.origen_tipo)"
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="
                      fieldErrors.origen_grado
                        ? 'cl-origen-grado-error'
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
                    id="cl-origen-grado-error"
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
               INFORMACIÓN DEL CAPÍTULO
          ================================================== -->
          <section
            id="sec-capitulo"
            class="sgpc-card"
            data-section="03"
          >
            <div class="sgpc-card-head">
              <div>
                <h2 class="sgpc-card-title">
                  Información del capítulo
                </h2>

                <p class="sgpc-card-desc">
                  Datos editoriales del capítulo y de la obra a la que
                  pertenece.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <!-- Nombre capítulo -->
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="cl-nombre_capitulo"
                  >
                    Nombre del capítulo

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="cl-nombre_capitulo"
                    v-model.trim="form.nombre_capitulo"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    required
                    :aria-invalid="Boolean(fieldErrors.nombre_capitulo)"
                    :aria-describedby="
                      fieldErrors.nombre_capitulo
                        ? 'cl-nombre-capitulo-error'
                        : undefined
                    "
                    placeholder="Ej. Tecnologías emergentes en la educación"
                  />

                  <p
                    v-if="fieldErrors.nombre_capitulo"
                    id="cl-nombre-capitulo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_capitulo }}
                  </p>
                </div>

                <!-- Nombre libro -->
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="cl-nombre_libro"
                  >
                    Nombre del libro

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="cl-nombre_libro"
                    v-model.trim="form.nombre_libro"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    required
                    :aria-invalid="Boolean(fieldErrors.nombre_libro)"
                    :aria-describedby="
                      fieldErrors.nombre_libro
                        ? 'cl-nombre-libro-error'
                        : undefined
                    "
                    placeholder="Ej. Innovación y Ciencia en América Latina"
                  />

                  <p
                    v-if="fieldErrors.nombre_libro"
                    id="cl-nombre-libro-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.nombre_libro }}
                  </p>
                </div>

                <!-- Fecha -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-fecha_publicacion"
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
                    id="cl-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    required
                    :aria-invalid="Boolean(fieldErrors.fecha_publicacion)"
                    :aria-describedby="
                      fieldErrors.fecha_publicacion
                        ? 'cl-fecha-publicacion-error'
                        : undefined
                    "
                  />

                  <p
                    v-if="fieldErrors.fecha_publicacion"
                    id="cl-fecha-publicacion-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <!-- ISBN -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-codigo_isbn"
                  >
                    Código ISBN

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="cl-codigo_isbn"
                    v-model.trim="form.codigo_isbn"
                    class="sgpc-input"
                    type="text"
                    maxlength="100"
                    required
                    :aria-invalid="Boolean(fieldErrors.codigo_isbn)"
                    :aria-describedby="
                      fieldErrors.codigo_isbn
                        ? 'cl-codigo-isbn-error'
                        : undefined
                    "
                    placeholder="Ej. 978-9942-xx-xxxx-x"
                  />

                  <p
                    v-if="fieldErrors.codigo_isbn"
                    id="cl-codigo-isbn-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.codigo_isbn }}
                  </p>

                  <p class="sgpc-hint">
                    Registre el ISBN para conservar la trazabilidad editorial.
                  </p>
                </div>

                <!-- Editor -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-editor_compilador"
                  >
                    Editor / Compilador

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="cl-editor_compilador"
                    v-model.trim="form.editor_compilador"
                    class="sgpc-input"
                    type="text"
                    maxlength="255"
                    required
                    :aria-invalid="Boolean(fieldErrors.editor_compilador)"
                    :aria-describedby="
                      fieldErrors.editor_compilador
                        ? 'cl-editor-compilador-error'
                        : undefined
                    "
                    placeholder="Ej. Dr. Juan Pérez"
                  />

                  <p
                    v-if="fieldErrors.editor_compilador"
                    id="cl-editor-compilador-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.editor_compilador }}
                  </p>
                </div>

                <!-- Arbitraje -->
                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="cl-revisor_par_arbitraje"
                  >
                    Revisor par / arbitraje

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <select
                    id="cl-revisor_par_arbitraje"
                    v-model="form.revisor_par_arbitraje"
                    class="sgpc-input"
                    required
                    :aria-invalid="
                      Boolean(fieldErrors.revisor_par_arbitraje)
                    "
                    :aria-describedby="
                      fieldErrors.revisor_par_arbitraje
                        ? 'cl-revisor-par-arbitraje-error'
                        : undefined
                    "
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
                    id="cl-revisor-par-arbitraje-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.revisor_par_arbitraje }}
                  </p>
                </div>

                <!-- Link -->
                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="cl-link_capitulo"
                  >
                    Link del capítulo

                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="cl-link_capitulo"
                    v-model.trim="form.link_capitulo"
                    class="sgpc-input"
                    type="url"
                    inputmode="url"
                    maxlength="500"
                    required
                    :aria-invalid="Boolean(fieldErrors.link_capitulo)"
                    :aria-describedby="
                      fieldErrors.link_capitulo
                        ? 'cl-link-capitulo-error'
                        : undefined
                    "
                    placeholder="https://..."
                  />

                  <p
                    v-if="fieldErrors.link_capitulo"
                    id="cl-link-capitulo-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
                    {{ fieldErrors.link_capitulo }}
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
                  Seleccione autores y defina su participación y orden de firma.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div
                id="cl-autores-anchor"
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
                  Adjunte el PDF principal del capítulo y los soportes
                  complementarios necesarios.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="cl-archivo-input"
                title="Agregar archivos PDF"
                description="El primer archivo será el PDF principal del capítulo. Puede agregar hasta 2 adjuntos adicionales."
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
            :class="['sgpc-alert', `is-${mensajeTipo}`]"
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
                    d="M5 3h11a3 3 0 0 1 3 3v15H8a3 3 0 0 1-3-3V3Zm3 2H7v13a1 1 0 0 0 1 1h9V6a1 1 0 0 0-1-1H8Zm1 3h6v2H9V8Z"
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

            <!-- Progreso -->
            <div class="sgpc-progress">
              <div class="sgpc-progress-row">
                <span>Completitud</span>
                <strong>{{ progressPercent }}%</strong>
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

            <!-- Estados -->
            <div class="sgpc-status-list">
              <button
                type="button"
                class="sgpc-status-item"
                :class="{
                  'is-ok': hasRequiredContext,
                }"
                @click="goTo('sec-datos-generales')"
              >
                <div>
                  <strong>Datos generales</strong>

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
                  <strong>Origen</strong>

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
                  'is-ok': hasRequiredChapter,
                }"
                @click="goTo('sec-capitulo')"
              >
                <div>
                  <strong>
                    Información del capítulo
                  </strong>

                  <span>
                    {{
                      hasRequiredChapter
                        ? "Completo"
                        : "Campos pendientes"
                    }}
                  </span>
                </div>

                <em>
                  {{
                    hasRequiredChapter
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
                  <strong>Autores</strong>

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
                  <strong>Archivos PDF</strong>

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

            <!-- Acciones -->
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
  "sgpc-capitulo-libro-draft:v22";

const STANDARD_CREATE_ENDPOINT =
  "/capitulos-libro/";

const ADMIN_CREATE_ENDPOINT =
  "/admin/publicaciones/capitulos/crear/";

const BULK_ATTACHMENTS_ENDPOINT =
  "/archivos-publicacion/bulk-upload/";

/* ============================================================
   ERRORES
============================================================ */

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
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa u otro origen",
  nombre_capitulo: "Nombre del capítulo",
  nombre_libro: "Nombre del libro",
  fecha_publicacion: "Fecha de publicación",
  codigo_isbn: "Código ISBN",
  editor_compilador: "Editor / Compilador",
  revisor_par_arbitraje: "Revisor par / arbitraje",
  link_capitulo: "Link del capítulo",
  autores: "Autores",
  archivos: "Archivos PDF",
});

const ERROR_FIELD_ORDER = Object.freeze([
  "admin_context",
  "general",
  "facultad",
  "carrera",
  "proyecto",
  "area",
  "subarea",
  "origen_tipo",
  "origen_grado",
  "nombre_capitulo",
  "nombre_libro",
  "fecha_publicacion",
  "codigo_isbn",
  "editor_compilador",
  "revisor_par_arbitraje",
  "link_capitulo",
  "autores",
  "archivos",
]);

/* ============================================================
   FORMULARIO VACÍO
============================================================ */

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

    nombre_capitulo: "",
    nombre_libro: "",
    fecha_publicacion: "",
    codigo_isbn: "",
    editor_compilador: "",
    revisor_par_arbitraje: "",
    link_capitulo: "",

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

  const rawErrors =
    data?.errors &&
    typeof data.errors === "object" &&
    data.errors !== null
      ? data.errors
      : data;

  if (
    typeof rawErrors !== "object" ||
    rawErrors === null
  ) {
    return {
      fields: {},
      message:
        typeof data?.detail === "string"
          ? data.detail
          : "No se pudo guardar. Verifique los campos.",
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
    typeof data?.detail === "string" &&
    data.detail.trim()
      ? data.detail.trim()
      : "No se pudo registrar. Revise los campos marcados.";

  if (fields.admin_context) {
    message =
      fields.admin_context;
  } else if (fields.general) {
    message =
      fields.general;
  } else if (fields.autores) {
    message =
      "Revise la sección de Autores: debe existir al menos un autor y el orden debe ser válido.";
  } else if (fields.archivos) {
    message =
      "Revise la sección de Archivos PDF.";
  } else if (
    first &&
    !(
      typeof data?.detail === "string" &&
      data.detail.trim()
    )
  ) {
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

function extractPublicacionId(
  payload
) {
  return positiveId(
    payload?.publicacion_id ??
    payload?.publicacion?.id ??
    payload?.capitulo?.publicacion_id
  );
}

/* ============================================================
   COMPONENTE
============================================================ */

export default {
  name: "CapituloLibroRegistro",

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
      _draftTimer: null,
      _draftSuspended: false,

      adminContext: {
        usuarioId: null,
        autorId: null,
        usuarioNombre: "",
        autorNombre: "",
      },

      form:
        createEmptyForm(),
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

      return Boolean(
        this.$route?.meta
          ?.delegatedPublication ||
        path.startsWith(
          "/admin/publicaciones/usuario/"
        )
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
      if (
        !this.isAdminDelegado
      ) {
        return false;
      }

      /*
       * Usuario.id y Autor.id pertenecen a
       * entidades distintas.
       *
       * Nunca deben compararse directamente.
       */
      return Boolean(
        this.adminContext
          .autorId ||
        this.adminContext
          .autorNombre
      );
    },

    pageKicker() {
      return (
        this.isAdminDelegado
          ? "Administración · Libros y capítulos"
          : "Libros y capítulos"
      );
    },

    pageTitle() {
      return (
        "Registrar Capítulo de Libro"
      );
    },

    pageSubtitle() {
      return (
        this.isAdminDelegado
          ? "Registre la información editorial del capítulo para el usuario seleccionado. Los campos marcados con * son obligatorios."
          : "Registre la información editorial del capítulo. Los campos marcados con * son obligatorios."
      );
    },

    submitText() {
      return (
        "Registrar capítulo"
      );
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
        general.carrera &&
        general.area &&
        general.subarea
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

    hasRequiredChapter() {
      return Boolean(
        String(
          this.form
            .nombre_capitulo ||
          ""
        ).trim() &&

        String(
          this.form
            .nombre_libro ||
          ""
        ).trim() &&

        this.form
          .fecha_publicacion &&

        String(
          this.form
            .codigo_isbn ||
          ""
        ).trim() &&

        String(
          this.form
            .editor_compilador ||
          ""
        ).trim() &&

        String(
          this.form
            .revisor_par_arbitraje ||
          ""
        ).trim() &&

        String(
          this.form
            .link_capitulo ||
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
          key: "capitulo",
          done:
            this.hasRequiredChapter,
        },

        {
          key: "autores",
          done:
            this.hasRequiredAuthors,
        },
      ];
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
        !this
          .totalRequiredCount
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
      this._draftTimer
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
          this._draftSuspended
        ) {
          return;
        }

        clearTimeout(
          this._draftTimer
        );

        this._draftTimer =
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

                    pais: null,
                    ciudad: null,
                  },

                  origen_tipo:
                    value.origen_tipo,

                  origen_grado:
                    value.origen_grado,

                  nombre_capitulo:
                    value.nombre_capitulo,

                  nombre_libro:
                    value.nombre_libro,

                  fecha_publicacion:
                    value.fecha_publicacion,

                  codigo_isbn:
                    value.codigo_isbn,

                  editor_compilador:
                    value.editor_compilador,

                  revisor_par_arbitraje:
                    value.revisor_par_arbitraje,

                  link_capitulo:
                    value.link_capitulo,

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
                  "No se pudo guardar el borrador.",
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
        !["tic", "otro"].includes(value)
      ) {
        this.form
          .origen_grado =
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
        this.$route
          ?.query ||
        {};

      const params =
        this.$route
          ?.params ||
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
            query.autorId
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
          JSON.parse(
            raw
          );

        const savedForm =
          parsed.form ||
          parsed;

        const empty =
          createEmptyForm();

        this.suspendDraftOnce();

        this.form = {
          ...empty,
          ...savedForm,

          datos_generales: {
            ...empty
              .datos_generales,

            ...(
              savedForm
                ?.datos_generales ||
              {}
            ),

            /*
             * País y ciudad no aplican
             * para capítulos.
             */
            pais: null,
            ciudad: null,
          },

          autores:
            Array.isArray(
              savedForm
                ?.autores
            )
              ? savedForm
                  .autores
              : [],

          archivos:
            restoreDraftArchivos(
              savedForm
                ?.archivos
            ),
        };

        if (
          parsed
            ?.updatedAt
        ) {
          const date =
            new Date(
              parsed
                .updatedAt
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
          "Borrador corrupto, se ignora.",
          error
        );
      }
    },

    suspendDraftOnce() {
      this._draftSuspended =
        true;

      this.$nextTick(
        () => {
          this._draftSuspended =
            false;
        }
      );
    },

    removeStoredDraft() {
      clearTimeout(
        this._draftTimer
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
          "No se pudo eliminar el borrador guardado.",
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
        this._draftTimer
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
        ?.scrollIntoView(
          {
            behavior:
              "smooth",

            block:
              "start",
          }
        );
    },

    focusField(key) {
      const localIdMap = {
        admin_context:
          "cl-admin-context-anchor",

        origen_tipo:
          "cl-origen_tipo",

        origen_grado:
          "cl-origen_grado",

        nombre_capitulo:
          "cl-nombre_capitulo",

        nombre_libro:
          "cl-nombre_libro",

        fecha_publicacion:
          "cl-fecha_publicacion",

        codigo_isbn:
          "cl-codigo_isbn",

        editor_compilador:
          "cl-editor_compilador",

        revisor_par_arbitraje:
          "cl-revisor_par_arbitraje",

        link_capitulo:
          "cl-link_capitulo",

        autores:
          "cl-autores-anchor",

        archivos:
          "cl-archivo-input",
      };

      const element =
        document
          .getElementById(
            `dg-${key}`
          ) ||
        document
          .getElementById(
            localIdMap[
              key
            ] ||
            ""
          );

      if (!element) {
        return;
      }

      if (
        key ===
          "autores" ||
        key ===
          "archivos" ||
        key ===
          "admin_context"
      ) {
        element
          .scrollIntoView
          ?.({
            behavior:
              "smooth",

            block:
              "center",
          });

        element
          .focus
          ?.({
            preventScroll:
              true,
          });

        return;
      }

      if (
        typeof
          element.focus ===
        "function"
      ) {
        element.focus({
          preventScroll:
            false,
        });

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
                autor
                  ?.autor_id ??
                autor
                  ?.id ??
                autor
                  ?.autor
                  ?.id
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
            !item
              ?.file &&
            Boolean(
              item
                ?.originalName
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
       VALIDACIÓN FRONTEND
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
          "Seleccione un área del conocimiento (UNESCO).";
      }

      if (
        !general
          .subarea
      ) {
        errors.subarea =
          "Seleccione una subárea del conocimiento (UNESCO).";
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
        !String(
          this.form
            .nombre_capitulo ||
          ""
        ).trim()
      ) {
        errors.nombre_capitulo =
          "Campo obligatorio.";
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
      }

      if (
        !this.form
          .fecha_publicacion
      ) {
        errors.fecha_publicacion =
          "Campo obligatorio.";
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
      }

      if (
        !String(
          this.form
            .editor_compilador ||
          ""
        ).trim()
      ) {
        errors.editor_compilador =
          "Campo obligatorio.";
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
            .link_capitulo ||
          ""
        ).trim()
      ) {
        errors.link_capitulo =
          "Campo obligatorio.";
      }

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
          "Complete los campos obligatorios antes de guardar.";

        this.mensajeTipo =
          "error";

        if (first) {
          this.focusField(
            first
          );
        }

        return false;
      }

      return true;
    },

    /* ========================================================
       FORMDATA PRINCIPAL
    ======================================================== */

    buildCreateFormData(
      autoresPayload
    ) {
      const formData =
        new FormData();

      Object.entries(
        this.form
          .datos_generales ||
        {}
      ).forEach(
        (
          [
            key,
            value,
          ]
        ) => {
          /*
           * País/Ciudad no aplican
           * a capítulos.
           */
          if (
            key ===
              "pais" ||
            key ===
              "ciudad"
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
        ["tic", "otro"].includes(this.form
          .origen_tipo)
      ) {
        appendIfPresent(
          formData,
          "origen_grado",
          this.form
            .origen_grado
        );
      }

      [
        "nombre_capitulo",
        "nombre_libro",
        "fecha_publicacion",
        "codigo_isbn",
        "editor_compilador",
        "revisor_par_arbitraje",
        "link_capitulo",
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

      return formData;
    },

    /* ========================================================
       PDF PRINCIPAL + ADJUNTOS
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
       * ADMINISTRACIÓN
       *
       * El endpoint delegado administra:
       *
       * - archivo_pdf
       * - archivos
       * - archivos_meta
       *
       * en la propia operación de creación.
       */
      if (
        this
          .isAdminDelegado
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
       * /capitulos-libro/
       * consume el PDF principal.
       *
       * Los adjuntos adicionales se cargan
       * posteriormente mediante bulk-upload.
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
       * El capítulo ya existe.
       *
       * Borramos el borrador y limpiamos el formulario
       * para evitar que el usuario presione "Registrar"
       * nuevamente y duplique la publicación.
       */
      this.removeStoredDraft();
      this.suspendDraftOnce();
      this.resetForm();

      this.fieldErrors =
        {};

      this.mensaje =
        `El capítulo fue registrado correctamente${
          publicacionId
            ? ` (publicación #${publicacionId})`
            : ""
        }, pero no se pudieron cargar los adjuntos complementarios. No vuelva a registrar el capítulo; agregue los adjuntos desde el detalle de la publicación.`;

      this.mensajeTipo =
        "error";

      console.error(
        "❌ Capítulo creado, pero falló la carga de adjuntos:",
        error?.response
          ?.data ||
        error
      );
    },

    /* ========================================================
       REGISTRAR
    ======================================================== */

    async registrarCapitulo() {
      if (
        this.loading
      ) {
        return;
      }

      this.loading =
        true;

      this.clearErrors();

      try {
        /* -----------------------------------------------
           1. Validación frontend
        ------------------------------------------------ */

        if (
          !this.validateFront()
        ) {
          return;
        }

        /* -----------------------------------------------
           2. Autores
        ------------------------------------------------ */

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

        /* -----------------------------------------------
           3. Contexto administrativo
        ------------------------------------------------ */

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

        /* -----------------------------------------------
           4. Payload principal
        ------------------------------------------------ */

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

        /* -----------------------------------------------
           5. Endpoint
        ------------------------------------------------ */

        const endpoint =
          this.isAdminDelegado
            ? ADMIN_CREATE_ENDPOINT
            : STANDARD_CREATE_ENDPOINT;

        const response =
          await api.post(
            endpoint,
            formData
          );

        /* -----------------------------------------------
           6. Publicación creada
        ------------------------------------------------ */

        const publicacionId =
          extractPublicacionId(
            response?.data
          );

        /* -----------------------------------------------
           7. Adjuntos adicionales usuario normal
        ------------------------------------------------ */

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

        /* -----------------------------------------------
           8. Éxito
        ------------------------------------------------ */

        this.finalizeSuccess(
          this.isAdminDelegado
            ? "Capítulo registrado correctamente para el usuario seleccionado."
            : "Capítulo registrado exitosamente."
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

        /* -----------------------------------------------
           Sesión
        ------------------------------------------------ */

        if (
          status ===
          401
        ) {
          this.mensaje =
            "Sesión expirada. Vuelva a iniciar sesión.";

          this.mensajeTipo =
            "error";

          return;
        }

        /* -----------------------------------------------
           Permisos
        ------------------------------------------------ */

        if (
          status ===
          403
        ) {
          this.mensaje =
            "No tiene permisos para registrar este capítulo.";

          this.mensajeTipo =
            "error";

          return;
        }

        /* -----------------------------------------------
           Errores DRF
        ------------------------------------------------ */

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
          "Error al registrar el capítulo.";

        this.mensajeTipo =
          "error";

        const first =
          firstErrorField(
            this
              .fieldErrors
          );

        if (first) {
          this.focusField(
            first
          );
        }

        console.error(
          "❌ Error capítulo:",
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
        createEmptyForm();
    },
  },
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
<style src="./capitulo-libro-form.css"></style>