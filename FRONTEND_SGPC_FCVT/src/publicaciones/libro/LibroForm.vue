<template>
  <div class="sgpc-form-page sgpc-form-page--libro">
    <div class="sgpc-form-shell">
      <header class="sgpc-form-header sgpc-publication-header page-stage page-header">
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
            <div class="sgpc-card-body">
              <div
                id="lb-admin-context-anchor"
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
                  Origen académico
                </h2>

                <p class="sgpc-card-desc">
                  Indique si el libro se originó a partir de otro trabajo académico.
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
                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Libro</strong>
                  <span>Identifique la obra y su fecha de publicación.</span>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="lb-origen_tipo"
                  >
                    ¿Este libro se originó a partir de otro trabajo académico?
                    <span
                      class="req"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <select
                    id="lb-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    required
                    :aria-invalid="Boolean(fieldErrors.origen_tipo)"
                    :aria-describedby="
                      fieldErrors.origen_tipo
                        ? 'lb-origen-tipo-error'
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
                    id="lb-origen-tipo-error"
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
                    for="lb-origen_grado"
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
                    id="lb-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    maxlength="120"
                    required
                    :aria-invalid="Boolean(fieldErrors.origen_grado)"
                    :aria-describedby="
                      fieldErrors.origen_grado
                        ? 'lb-origen-grado-error'
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
                    id="lb-origen-grado-error"
                    class="sgpc-hint sgpc-hint-error"
                    role="alert"
                  >
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
                  Complete los datos bibliográficos, editoriales y de acceso del libro.
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
                    Título del libro
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

                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Datos editoriales</strong>
                  <span>Complete la información editorial de la obra.</span>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label
                    class="sgpc-label"
                    for="lb-codigo_isbn"
                  >
                    ISBN
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
                    Editorial o compilador
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
                    ¿El libro tuvo revisión por pares o arbitraje?
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

                <div class="sgpc-form-subsection sgpc-col-span-12">
                  <strong>Acceso</strong>
                  <span>Indique dónde puede consultarse el libro.</span>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label
                    class="sgpc-label"
                    for="lb-link_libro"
                  >
                    Enlace del libro
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
                  Agregue las personas que participaron y colóquelas en el
                  orden en que deben aparecer.
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
                  Documentos
                </h2>

                <p class="sgpc-card-desc">
                  Adjunte el documento del libro y, si corresponde, archivos adicionales.
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

          <!-- =====================================================
               PREVALIDACIÓN
          ====================================================== -->

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
                :key="`lb-pre-block-${item.codigo || index}`"
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
                :key="`lb-pre-warning-${item.codigo || index}`"
              >
                {{ item.mensaje }}
              </li>
            </ul>
          </div>

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
             ESTADO DEL REGISTRO
        ====================================================== -->

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
                class="sgpc-btn sgpc-discard-draft-btn"
                type="button"
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
          aria-labelledby="lb-discard-draft-title"
          aria-describedby="lb-discard-draft-description"
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
            <h2 id="lb-discard-draft-title">
              ¿Descartar este borrador?
            </h2>

            <p id="lb-discard-draft-description">
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
  admin_context: "Usuario seleccionado",
  sede: "Sede",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  origen_tipo: "Origen académico",
  origen_grado: "Carrera, programa u otro origen",
  nombre_libro: "Título del libro",
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",
  codigo_isbn: "ISBN",
  editorial_compilador: "Editorial o compilador",
  revisor_par_arbitraje: "¿El libro tuvo revisión por pares o arbitraje?",
  link_libro: "Enlace del libro",
  autores: "Autores",
  archivos: "Documentos",
});

const ERROR_FIELD_ORDER = Object.freeze([
  "general",
  "admin_context",
  "sede",
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
      return "Registrar libro";
    },

    pageSubtitle() {
      return (
        "Complete los datos de la publicación. Los campos con * son obligatorios."
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
        general.sede &&
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
        ) >= 1900 &&

        Number(
          this.form
            .anio_publicacion
        ) <= 2100 &&
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

    summarySections() {
      const sections = [
        {
          key: "datos",
          target: "sec-datos-generales",
          label: "Información académica",
          done: this.hasRequiredContext,
          required: true,
          detail:
            this.hasRequiredContext
              ? "Listo"
              : "Complete sede, facultad y carrera",
        },

        {
          key: "origen",
          target: "sec-origen",
          label: "Origen académico",
          done: this.hasRequiredOrigin,
          required: true,
          detail:
            this.hasRequiredOrigin
              ? "Listo"
              : "Seleccione el origen",
        },

        {
          key: "libro",
          target: "sec-libro",
          label: "Información del libro",
          done: this.hasRequiredBook,
          required: true,
          detail:
            this.hasRequiredBook
              ? "Listo"
              : "Complete los datos obligatorios del libro",
        },

        {
          key: "autores",
          target: "sec-autores",
          label: "Autores",
          done: this.hasRequiredAuthors,
          required: true,
          detail:
            this.hasRequiredAuthors
              ? "Listo"
              : "Agregue al menos un autor",
        },
      ];

      if (this.isAdminDelegado) {
        return [
          {
            key: "admin",
            target: "sec-contexto-admin",
            label: "Persona seleccionada",
            done: Boolean(
              this.adminContext
                .usuarioId
            ),
            required: true,
            detail:
              this.adminContext.usuarioId
                ? "Listo"
                : "Seleccione la persona",
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

    requiredSections() {
      return this.summarySections
        .filter(
          (section) =>
            section.required
        );
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
    this.closePrevalidationNotice();

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

        this.draftInfo =
          "Borrador recuperado. Puede continuar donde lo dejó.";

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
        "Borrador descartado.";

      this.mensajeTipo =
        "info";
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

    /* ========================================================
       PREVALIDACIÓN BACKEND
    ======================================================== */

    clearPrevalidationState() {
      this.prevalidacionBloqueantes = [];
      this.prevalidacionAdvertencias = [];
      this.prevalidacionResumen = null;
    },

    normalizePrevalidationIssues(items) {
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

          if (!mensaje) {
            return null;
          }

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
    },

    applyPrevalidationFieldErrors(items) {
      const next = { ...this.fieldErrors };

      this.normalizePrevalidationIssues(items).forEach((item) => {
        const rawField = String(item.campo || "").trim();

        if (!rawField) {
          return;
        }

        const field = ERROR_KEY_ALIASES[rawField] || rawField;

        if (!next[field]) {
          next[field] = item.mensaje;
        }
      });

      this.fieldErrors = next;
    },

    buildPrevalidationPayload(autoresPayload) {
      const general = this.form.datos_generales || {};
      const uploadItems = this.selectedUploadItems();

      return {
        tipo_codigo: "libro",
        sede: general.sede || null,
        facultad: general.facultad || null,
        carrera: general.carrera || null,
        proyecto: general.proyecto || null,
        area: general.area || null,
        subarea: general.subarea || null,
        origen_tipo: this.form.origen_tipo || "ninguno",
        origen_grado: this.form.origen_grado || "",
        nombre_libro: String(this.form.nombre_libro || "").trim(),
        anio_publicacion: this.form.anio_publicacion,
        mes_publicacion: this.form.mes_publicacion || null,
        codigo_isbn: String(this.form.codigo_isbn || "").trim(),
        editorial_compilador: String(this.form.editorial_compilador || "").trim(),
        revisor_par_arbitraje: String(this.form.revisor_par_arbitraje || "").trim().toLowerCase(),
        link_libro: String(this.form.link_libro || "").trim(),
        autores: autoresPayload,
        archivo_pdf: uploadItems[0]?.file || null,
        registrado_por_admin: this.isAdminDelegado,
        usuario_objetivo_id: this.isAdminDelegado ? this.adminContext.usuarioId : null,
        autor_objetivo_id: this.isAdminDelegado ? this.adminContext.autorId : null,
      };
    },

    async ejecutarPrevalidacion(autoresPayload) {
      this.clearPrevalidationState();

      let response;

      try {
        response = await prevalidarPublicacion(
          this.buildPrevalidationPayload(autoresPayload)
        );
      } catch (error) {
        const normalized = normalizeDrfErrors(error?.response?.data);

        this.fieldErrors = {
          ...this.fieldErrors,
          ...(normalized.fields || {}),
        };

        this.mensaje =
          normalized.message ||
          "No se pudo verificar la información antes del registro. Revise los datos e inténtelo nuevamente.";
        this.mensajeTipo = "error";

        const first = firstErrorField(this.fieldErrors);

        if (first) {
          this.$nextTick(() => this.focusField(first));
        }

        return false;
      }

      const bloqueantes = this.normalizePrevalidationIssues(
        response?.bloqueantes
      );
      const advertencias = this.normalizePrevalidationIssues(
        response?.advertencias
      );

      this.prevalidacionBloqueantes = bloqueantes;
      this.prevalidacionAdvertencias = advertencias;
      this.prevalidacionResumen = response?.resumen || null;

      if (response?.puede_continuar === false || bloqueantes.length) {
        this.applyPrevalidationFieldErrors(bloqueantes);
        this.mensaje =
          "Hay datos que deben corregirse antes de registrar el libro.";
        this.mensajeTipo = "error";

        const first = firstErrorField(this.fieldErrors);

        if (first) {
          this.$nextTick(() => this.focusField(first));
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
          "Seleccione nuevamente al usuario para continuar con el registro."
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
          "Seleccione nuevamente al usuario para continuar con el registro.";
      }

      if (!general.sede) {
        errors.sede =
          "Seleccione una sede.";
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
          "Seleccione el origen académico.";
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
          `La carrera, programa u origen especificado no puede superar ${FIELD_LIMITS.origen_grado} caracteres.`;
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
          `El título del libro no puede superar ${FIELD_LIMITS.nombre_libro} caracteres.`;
      }
      const publicationYear = Number(this.form.anio_publicacion);

      if (
        !Number.isInteger(publicationYear) ||
        publicationYear < 1900 ||
        publicationYear > 2100
      ) {
        errors.anio_publicacion =
          "Ingrese un año válido entre 1900 y 2100.";
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
          `La editorial o compilador no puede superar ${FIELD_LIMITS.editorial_compilador} caracteres.`;
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
          "Hay documentos del borrador que deben seleccionarse nuevamente o eliminarse antes de guardar.";
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
          "No pudimos asociar los documentos a la publicación. Intente nuevamente."
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
        "El libro fue guardado como Borrador, pero algunos documentos adicionales no pudieron cargarse. No vuelva a registrarlo; agregue los documentos faltantes desde el detalle de la publicación antes de enviarla a revisión.";

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
      this.clearPrevalidationState();

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

        const prevalidacionOk =
          await this.ejecutarPrevalidacion(
            autoresPayload
          );

        if (!prevalidacionOk) {
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
            ? "Libro guardado correctamente para el usuario seleccionado. La publicación quedó en estado Borrador y puede editarse o enviarse a revisión desde la gestión de publicaciones."
            : "La publicación se guardó correctamente y quedó en estado Borrador. Revise la información y edítela si es necesario antes de enviarla a revisión. Una vez enviada, la edición quedará bloqueada hasta que el administrador apruebe, rechace o solicite correcciones."
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
      this.prevalidacionBloqueantes = [];
      this.prevalidacionAdvertencias = [];
      this.prevalidacionResumen = null;
      this.draftInfo = "";
      this.showDiscardDraftDialog = false;
      this.form = createEmptyForm();
    },
  },
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
