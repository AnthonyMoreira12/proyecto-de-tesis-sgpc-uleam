<template>
  <div class="sgpc-admin-page adm-review-detail-page">
    <main
      class="adm-review-detail-shell"
      :aria-busy="loading || actionLoading ? 'true' : 'false'"
    >
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="adm-review-detail-header page-stage page-main">
        <div class="adm-review-detail-header__top">
          <button
            class="adm-review-detail-back"
            type="button"
            @click="goBackToReview"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M10.7 5.3 4 12l6.7 6.7 1.4-1.4L7.8 13H20v-2H7.8l4.3-4.3-1.4-1.4Z"
              />
            </svg>

            Volver a revisión
          </button>

          <span
            class="adm-review-detail-state"
            :data-tone="stateTone"
          >
            {{ stateLabel }}
          </span>

          <div class="adm-review-detail-header__actions">
            <button
              class="adm-review-detail-icon-button"
              type="button"
              :disabled="loading"
              title="Actualizar"
              aria-label="Actualizar"
              @click="loadAll"
            >
              <svg
                :class="{ 'adm-review-detail-refresh-spin': loading }"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  fill="currentColor"
                  d="M12 4a8 8 0 0 1 7.45 5H17l3.5 3.5L24 9h-2.47A10 10 0 1 0 22 15h-2.1A8 8 0 1 1 12 4Z"
                />
              </svg>
            </button>

            <button
              class="adm-review-detail-text-button"
              type="button"
              :disabled="!publicationId"
              @click="openLegacyDetail"
            >
              Ver publicación
            </button>
          </div>
        </div>

        <div class="adm-review-detail-header__main">
          <div>
            <h1>{{ publicationTitle }}</h1>

            <p>
              {{ publicationType }}

              <template v-if="creatorLabel">
                · Registrada por {{ creatorLabel }}
              </template>
            </p>
          </div>

          <dl class="adm-review-detail-header__facts">
            <div>
              <dt>Período</dt>
              <dd>{{ publicationPeriod }}</dd>
            </div>

            <div>
              <dt>Sede</dt>
              <dd>{{ siteLabel || "Sin sede" }}</dd>
            </div>

            <div>
              <dt>Último cambio</dt>
              <dd>{{ formatDateTime(updatedAt) }}</dd>
            </div>
          </dl>
        </div>
      </header>

      <!-- =====================================================
           MENSAJES
      ====================================================== -->
      <div
        v-if="errorMessage"
        class="adm-review-detail-message adm-review-detail-message--error"
        role="alert"
      >
        <div>
          <strong>
            {{
              detail
                ? "No se pudo actualizar la publicación."
                : "No se pudo mostrar la publicación."
            }}
          </strong>
          <span>{{ errorMessage }}</span>
        </div>

        <button
          type="button"
          @click="loadAll"
        >
          Reintentar
        </button>
      </div>

      <div
        v-if="successMessage"
        class="adm-review-detail-message adm-review-detail-message--success adm-review-detail-stage3-success"
        role="status"
      >
        <div>
          <strong>Cambio guardado.</strong>
          <span>{{ successMessage }}</span>
        </div>

        <div class="adm-review-detail-stage3-success__actions">
          <button
            v-if="nextReviewId || nextReviewLoading"
            class="adm-review-detail-stage3-next"
            type="button"
            :disabled="nextReviewLoading || !nextReviewId"
            @click="goToNextReview"
          >
            {{ nextReviewLoading ? "Buscando siguiente…" : "Revisar siguiente" }}
          </button>

          <button
            type="button"
            aria-label="Cerrar mensaje"
            @click="successMessage = ''"
          >
            ×
          </button>
        </div>
      </div>

      <AdminInlineLoader
        v-if="refreshingDetail && loadingFeedbackVisible"
        class="adm-review-detail-stage3-inline"
        message="Actualizando la publicación…"
      />

      <AdminLoadingState
        v-if="initialLoading && loadingFeedbackVisible"
        class="adm-review-detail-stage3-loading page-stage page-main"
        message="Cargando publicación…"
        description="Estamos preparando la información, el documento y el historial de revisión."
        :skeleton-rows="5"
      />

      <template v-else-if="detail">
        <!-- ===================================================
             DOCUMENTO + DECISIÓN
        ==================================================== -->
        <section class="adm-review-detail-workspace page-stage page-main">
          <article class="adm-review-detail-document adm-review-detail-local-surface">
            <header class="adm-review-detail-cardhead">
              <h2>Documento</h2>

              <span
                class="adm-review-detail-document-status"
                :class="{ 'is-missing': !hasPdf }"
              >
                {{ hasPdf ? "Documento disponible" : "Sin documento" }}
              </span>
            </header>

            <div
              v-if="hasPdf"
              class="adm-review-detail-pdf"
            >
              <div class="adm-review-detail-pdf__preview">
                <iframe
                  v-if="pdfPreviewUrl"
                  :src="pdfPreviewUrl"
                  :title="`PDF de ${publicationTitle}`"
                ></iframe>

                <div
                  v-else-if="pdfLoading"
                  class="adm-review-detail-pdf__placeholder"
                >
                  <span
                    class="adm-review-detail-spinner"
                    aria-hidden="true"
                  ></span>

                  <strong>Cargando documento…</strong>
                </div>

                <div
                  v-else
                  class="adm-review-detail-pdf__placeholder"
                >
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8M8 17h6"
                    />
                  </svg>

                  <strong>No se pudo mostrar el documento</strong>

                  <span>
                    {{
                      pdfError ||
                      "Vuelva a intentar cargar el documento."
                    }}
                  </span>

                  <button
                    class="adm-review-detail-button adm-review-detail-button--secondary"
                    type="button"
                    :disabled="pdfLoading"
                    @click="loadPdfPreview"
                  >
                    Reintentar
                  </button>
                </div>
              </div>

              <div class="adm-review-detail-pdf__actions">
                <button
                  class="adm-review-detail-button adm-review-detail-button--secondary"
                  type="button"
                  :disabled="pdfLoading || !pdfPreviewUrl"
                  @click="openPdfInNewTab"
                >
                  Abrir documento
                </button>
              </div>
            </div>

            <div
              v-else
              class="adm-review-detail-empty-document"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8M8 17h6"
                />
              </svg>

              <strong>Sin documento</strong>

              <span>
                Esta publicación no tiene un documento adjunto.
              </span>
            </div>
          </article>

          <aside class="adm-review-detail-review-column">
            <section
              class="adm-review-detail-review-panel adm-review-detail-local-surface"
              :class="{ 'is-closed': !isReviewable }"
            >
              <header class="adm-review-detail-review-panel__head">
                <div>
                  <h2>Revisión</h2>

                  <p>
                    {{
                      isReviewable
                        ? "Revise la información y el documento antes de elegir una acción."
                        : closedStateHelp
                    }}
                  </p>
                </div>
              </header>

              <div
                v-if="lastRelevantComment"
                class="adm-review-detail-review-note"
                :data-tone="lastRelevantComment.tone"
              >
                <span>
                  {{ lastRelevantComment.label }}
                </span>

                <p>
                  {{ lastRelevantComment.comment }}
                </p>

                <small>
                  {{ lastRelevantComment.actor }} ·
                  {{ formatDateTime(lastRelevantComment.date) }}
                </small>
              </div>

              <template v-if="isReviewable">
                <div class="adm-review-detail-review-actions">
                  <button
                    class="adm-review-detail-button adm-review-detail-button--primary adm-review-detail-button--approve"
                    type="button"
                    :disabled="actionLoading"
                    @click="approvePublication"
                  >
                    <span aria-hidden="true">✓</span>
                    {{
                      actionLoading && activeAction === "aprobar"
                        ? "Aprobando…"
                        : "Aprobar"
                    }}
                  </button>

                  <button
                    class="adm-review-detail-button adm-review-detail-button--correction"
                    type="button"
                    :class="{ 'is-active': decisionMode === 'observar' }"
                    :disabled="actionLoading"
                    @click="selectDecisionMode('observar')"
                  >
                    Solicitar corrección
                  </button>

                  <button
                    class="adm-review-detail-button adm-review-detail-button--reject"
                    type="button"
                    :class="{ 'is-active': decisionMode === 'rechazar' }"
                    :disabled="actionLoading"
                    @click="selectDecisionMode('rechazar')"
                  >
                    Rechazar
                  </button>
                </div>

                <AdminActionFeedback
                  v-if="actionLoading"
                  class="adm-review-detail-stage3-action-feedback"
                  status="loading"
                  :message="actionFeedbackMessage"
                />

                <div
                  v-if="decisionMode"
                  class="adm-review-detail-decision-editor"
                  :data-tone="decisionMode === 'rechazar' ? 'danger' : 'warning'"
                >
                  <label>
                    <span>
                      {{
                        decisionMode === "rechazar"
                          ? "Motivo del rechazo"
                          : "Qué debe corregirse"
                      }}
                    </span>

                    <textarea
                      v-model="decisionComment"
                      rows="5"
                      maxlength="3000"
                      :disabled="actionLoading"
                      :placeholder="decisionPlaceholder"
                    ></textarea>

                    <small>
                      {{ decisionComment.trim().length }} / 3000
                    </small>
                  </label>

                  <div
                    v-if="decisionError"
                    class="adm-review-detail-inline-error"
                    role="alert"
                  >
                    {{ decisionError }}
                  </div>

                  <div class="adm-review-detail-decision-editor__actions">
                    <button
                      class="adm-review-detail-button adm-review-detail-button--secondary"
                      type="button"
                      :disabled="actionLoading"
                      @click="cancelDecision"
                    >
                      Cancelar
                    </button>

                    <button
                      class="adm-review-detail-button"
                      :class="
                        decisionMode === 'rechazar'
                          ? 'adm-review-detail-button--danger'
                          : 'adm-review-detail-button--warning'
                      "
                      type="button"
                      :disabled="actionLoading"
                      @click="submitDecision"
                    >
                      {{
                        actionLoading
                          ? decisionMode === "rechazar"
                            ? "Rechazando…"
                            : "Enviando corrección…"
                          : decisionMode === "rechazar"
                            ? "Confirmar rechazo"
                            : "Solicitar corrección"
                      }}
                    </button>
                  </div>
                </div>
              </template>


            </section>

            <article class="adm-review-detail-card adm-review-detail-info adm-review-detail-local-surface">
              <header class="adm-review-detail-cardhead adm-review-detail-cardhead--data">
                <h2>Información registrada</h2>
              </header>

              <section class="adm-review-detail-info__section">
                <h3>Información académica</h3>

                <dl class="adm-review-detail-facts">
                  <div
                    v-for="field in institutionalFields"
                    :key="`institutional-${field.label}`"
                  >
                    <dt>{{ field.label }}</dt>
                    <dd>{{ field.value }}</dd>
                  </div>
                </dl>
              </section>

              <section class="adm-review-detail-info__section">
                <h3>Publicación</h3>

                <dl class="adm-review-detail-facts">
                  <div
                    v-for="field in publicationFields"
                    :key="`publication-${field.label}`"
                  >
                    <dt>{{ field.label }}</dt>

                    <dd>
                      <a
                        v-if="field.href"
                        :href="field.href"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {{ field.value }}
                      </a>

                      <template v-else>
                        {{ field.value }}
                      </template>
                    </dd>
                  </div>
                </dl>
              </section>
            </article>
          </aside>
        </section>

        <!-- ===================================================
             INFORMACIÓN SECUNDARIA
        ==================================================== -->
        <section class="adm-review-detail-secondary page-stage page-main">
          <section class="adm-review-detail-card adm-review-detail-local-surface">
            <header class="adm-review-detail-cardhead">
              <h2>Autores</h2>

              <span class="adm-review-detail-count">
                {{ authors.length }}
                {{ authors.length === 1 ? "autor" : "autores" }}
              </span>
            </header>

            <div
              v-if="authors.length"
              class="adm-review-detail-authors"
            >
              <article
                v-for="(author, index) in authors"
                :key="author.key"
                class="adm-review-detail-author"
              >
                <span class="adm-review-detail-author__order">
                  {{ index + 1 }}
                </span>

                <div>
                  <strong>{{ author.name }}</strong>

                  <span v-if="author.email">
                    {{ author.email }}
                  </span>

                  <small v-if="author.institution">
                    {{ author.institution }}
                  </small>
                </div>
              </article>
            </div>

            <div
              v-else
              class="adm-review-detail-inline-empty"
            >
              No hay autores asociados.
            </div>
          </section>

          <section class="adm-review-detail-card adm-review-detail-local-surface">
            <header class="adm-review-detail-cardhead adm-review-detail-cardhead--audit">
              <h2>Actividad de revisión</h2>

              <button
                class="adm-review-detail-text-button adm-review-detail-history-toggle"
                type="button"
                :aria-expanded="historyOpen ? 'true' : 'false'"
                @click="toggleHistory"
              >
                {{
                  historyOpen
                    ? "Ocultar actividad"
                    : `Mostrar actividad (${history.length})`
                }}
              </button>
            </header>

            <div
              v-if="historyOpen"
              class="adm-review-detail-history-body"
            >
              <div
                v-if="historyLoading && !history.length"
                class="adm-review-detail-audit-loading"
              >
                <span
                  class="adm-review-detail-spinner"
                  aria-hidden="true"
                ></span>

                Cargando actividad…
              </div>

              <div
                v-else-if="historyError"
                class="adm-review-detail-inline-error"
              >
                {{ historyError }}
              </div>

              <ol
                v-else-if="history.length"
                class="adm-review-detail-timeline"
              >
                <li
                  v-for="event in history"
                  :key="event.id || `${eventCode(event)}-${event.created_at}`"
                  class="adm-review-detail-event"
                  :data-tone="eventTone(event)"
                >
                  <div
                    class="adm-review-detail-event__rail"
                    aria-hidden="true"
                  >
                    <span>{{ eventSymbol(event) }}</span>
                  </div>

                  <article class="adm-review-detail-event__card">
                    <header>
                      <div>
                        <span>{{ eventLabel(event) }}</span>
                        <strong>{{ eventActor(event) }}</strong>
                      </div>

                      <time :datetime="event.created_at || ''">
                        {{ formatDateTime(event.created_at) }}
                      </time>
                    </header>

                    <div
                      v-if="eventTransition(event)"
                      class="adm-review-detail-event__transition"
                    >
                      {{ eventTransition(event) }}
                    </div>

                    <p
                      v-if="eventChangesLabel(event)"
                      class="adm-review-detail-event__changes-summary"
                    >
                      {{ eventChangesLabel(event) }}
                    </p>

                    <p
                      v-if="eventComment(event)"
                      class="adm-review-detail-event__comment"
                    >
                      {{ eventComment(event) }}
                    </p>
                  </article>
                </li>
              </ol>

              <div
                v-else
                class="adm-review-detail-inline-empty"
              >
                Todavía no hay actividad de revisión.
              </div>
            </div>

            <div
              v-else
              class="adm-review-detail-history-preview"
            >
              Abra esta sección para consultar los cambios y decisiones
              realizados.
            </div>
          </section>
        </section>
      </template>

      <NoticeDialog
        :modelValue="notice"
        @close="closeNotice"
      />
    </main>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";

import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import api from "../../scripts/api/axios";
import { useNotice } from "../../scripts/composables/useNotice";
import {
  aprobarAdminPublicacion,
  listarAdminPublicaciones,
  observarAdminPublicacion,
  obtenerAdminPublicacion,
  obtenerAdminPublicacionHistorial,
  rechazarAdminPublicacion,
} from "../../scripts/api/publicacionesAdminApi";
import {
  ESTADO_PUBLICACION,
  estadoPublicacionLabel,
  estadoPublicacionTone,
  normalizarEstadoPublicacion,
} from "../../scripts/utils/publicacion-estados";

const route = useRoute();
const router = useRouter();
const { notice, openNotice, closeNotice } = useNotice();

const detail = ref(null);
const history = ref([]);
const loading = ref(false);
const hasLoadedDetail = ref(false);
const loadingFeedbackVisible = ref(false);
const historyLoading = ref(false);
const actionLoading = ref(false);
const activeAction = ref("");
const nextReviewId = ref(0);
const nextReviewLoading = ref(false);
const errorMessage = ref("");
const historyError = ref("");
const successMessage = ref("");

const historyOpen = ref(false);
const pdfPreviewUrl = ref("");
const pdfLoading = ref(false);
const pdfError = ref("");

const decisionMode = ref("");
const decisionComment = ref("");
const decisionError = ref("");

let detailRequestSerial = 0;
let historyRequestSerial = 0;
let pdfRequestSerial = 0;
let loadingFeedbackTimer = null;

const publicationId = computed(() => {
  const parsed = Number(route.params?.id || 0);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 0;
});

const initialLoading = computed(() =>
  loading.value && !hasLoadedDetail.value && !detail.value
);

const refreshingDetail = computed(() =>
  loading.value && hasLoadedDetail.value && Boolean(detail.value)
);

const actionFeedbackMessage = computed(() => {
  if (!actionLoading.value) return "";

  if (activeAction.value === "aprobar") return "Aprobando publicación…";
  if (activeAction.value === "rechazar") return "Rechazando publicación…";
  if (activeAction.value === "observar") return "Enviando solicitud de corrección…";
  return "Procesando decisión…";
});

const normalizedDetail = computed(() => {
  const value = detail.value;

  if (value?.publicacion && typeof value.publicacion === "object") {
    return value.publicacion;
  }

  if (value?.data && typeof value.data === "object" && !Array.isArray(value.data)) {
    return value.data;
  }

  return value && typeof value === "object" ? value : {};
});

const state = computed(() =>
  normalizarEstadoPublicacion(
    normalizedDetail.value?.estado ||
      normalizedDetail.value?.status ||
      ""
  )
);

const stateLabel = computed(() =>
  String(normalizedDetail.value?.estado_label || "").trim() ||
  estadoPublicacionLabel(state.value) ||
  "Sin estado"
);

const stateTone = computed(() =>
  estadoPublicacionTone(state.value) || "neutral"
);

const publicationTitle = computed(() =>
  firstFilled(
    normalizedDetail.value?.titulo,
    normalizedDetail.value?.nombre_publicacion,
    normalizedDetail.value?.titulo_publicacion,
    normalizedDetail.value?.nombre_articulo,
    normalizedDetail.value?.nombre_ponencia,
    normalizedDetail.value?.nombre_capitulo,
    normalizedDetail.value?.nombre_libro,
    "Publicación sin título"
  )
);

const publicationType = computed(() =>
  firstFilled(
    normalizedDetail.value?.tipo_publicacion_final_label,
    normalizedDetail.value?.tipo_label,
    normalizedDetail.value?.tipo_nombre,
    normalizedDetail.value?.tipo,
    normalizedDetail.value?.categoria_label,
    "Publicación"
  )
);

const creatorLabel = computed(() =>
  firstFilled(
    normalizedDetail.value?.usuario_creador_nombre,
    normalizedDetail.value?.usuario_creador_email,
    normalizedDetail.value?.usuario_creador?.nombre_completo,
    normalizedDetail.value?.usuario_creador?.email,
    normalizedDetail.value?.creado_por_nombre,
    normalizedDetail.value?.creado_por_email
  )
);

const siteLabel = computed(() =>
  valueLabel(
    normalizedDetail.value?.sede,
    normalizedDetail.value?.sede_nombre
  )
);

const facultyLabel = computed(() =>
  valueLabel(
    normalizedDetail.value?.facultad,
    normalizedDetail.value?.facultad_nombre
  )
);

const careerLabel = computed(() =>
  valueLabel(
    normalizedDetail.value?.carrera,
    normalizedDetail.value?.carrera_nombre
  )
);

const projectLabel = computed(() =>
  valueLabel(
    normalizedDetail.value?.proyecto,
    normalizedDetail.value?.proyecto_nombre
  )
);

const publicationPeriod = computed(() => {
  const year = Number(
    normalizedDetail.value?.anio_publicacion ??
      normalizedDetail.value?.anio ??
      0
  );

  const month = Number(
    normalizedDetail.value?.mes_publicacion ??
      normalizedDetail.value?.mes ??
      0
  );

  const monthLabel = firstFilled(
    normalizedDetail.value?.mes_publicacion_label,
    normalizedDetail.value?.mes_label,
    MONTHS[month]
  );

  if (Number.isInteger(year) && year > 0 && monthLabel) {
    return `${monthLabel} de ${year}`;
  }

  if (Number.isInteger(year) && year > 0) {
    return String(year);
  }

  if (monthLabel) return monthLabel;
  return "Sin período";
});

const updatedAt = computed(() =>
  firstFilled(
    normalizedDetail.value?.updated_at,
    normalizedDetail.value?.fecha_actualizacion,
    normalizedDetail.value?.created_at,
    normalizedDetail.value?.fecha_creacion
  )
);

const pdfUrl = computed(() => {
  const raw = firstFilled(
    normalizedDetail.value?.archivo_pdf_url,
    normalizedDetail.value?.pdf_url,
    normalizedDetail.value?.archivo_pdf,
    normalizedDetail.value?.pdf,
    normalizedDetail.value?.archivo,
    normalizedDetail.value?.archivos?.[0]?.url,
    normalizedDetail.value?.archivos?.[0]?.archivo_url,
    normalizedDetail.value?.archivos?.[0]?.archivo,
    normalizedDetail.value?.adjuntos?.[0]?.url,
    normalizedDetail.value?.adjuntos?.[0]?.archivo_url,
    normalizedDetail.value?.adjuntos?.[0]?.archivo
  );

  return resolveFileUrl(raw);
});

const hasPdf = computed(() =>
  Boolean(
    pdfUrl.value ||
      normalizedDetail.value?.tiene_pdf ||
      normalizedDetail.value?.has_pdf ||
      normalizedDetail.value?.hasPdf ||
      normalizedDetail.value?.tiene_pdf_principal ||
      normalizedDetail.value?.archivo_pdf ||
      normalizedDetail.value?.pdf_url
  )
);


const authors = computed(() => normalizeAuthors(normalizedDetail.value?.autores));

const institutionalFields = computed(() =>
  visibleFields([
    field("Sede", siteLabel.value),
    field("Facultad", facultyLabel.value),
    field("Carrera", careerLabel.value),
    field("Proyecto", projectLabel.value || "Sin proyecto"),
    field(
      "Área del conocimiento",
      valueLabel(
        normalizedDetail.value?.area,
        normalizedDetail.value?.area_nombre
      )
    ),
    field(
      "Subárea del conocimiento",
      valueLabel(
        normalizedDetail.value?.subarea,
        normalizedDetail.value?.subarea_nombre
      )
    ),
    field(
      "País",
      valueLabel(
        normalizedDetail.value?.pais,
        normalizedDetail.value?.pais_nombre
      )
    ),
    field(
      "Ciudad",
      valueLabel(
        normalizedDetail.value?.ciudad,
        normalizedDetail.value?.ciudad_nombre
      )
    ),
  ])
);

const publicationFields = computed(() => {
  const data = normalizedDetail.value || {};
  const doi = firstFilled(data.codigo_doi, data.doi);

  return visibleFields([
    field("Tipo", publicationType.value),
    field("Período", publicationPeriod.value),
    field("Origen", firstFilled(data.origen_tipo_label, data.origen_tipo)),
    field("Información de origen", data.origen_grado),
    field("Revista", firstFilled(data.nombre_revista, data.revista)),
    field("Evento", firstFilled(data.nombre_evento, data.evento)),
    field("Editorial", firstFilled(data.editorial, data.editorial_compilador)),
    field("Editor / compilador", data.editor_compilador),
    field("DOI", doi, doi ? doiUrl(doi) : ""),
    field("ISSN", firstFilled(data.codigo_issn, data.issn)),
    field("ISSN / ISBN", data.codigo_issn_isbn),
    field("ISBN", firstFilled(data.codigo_isbn, data.isbn)),
    field("Cuartil", firstFilled(data.cuartil, data.quartile)),
    field("Volumen", data.volumen),
    field("Número", firstFilled(data.numero_revista, data.numero_edicion)),
    field("Páginas", firstFilled(data.paginas, data.paginas_capitulo)),
    field("Revisión por pares / arbitraje", booleanLabel(data.revisor_par_arbitraje)),
    field("Modalidad", data.modalidad),
    field("Enlace del evento", data.link_evento, normalizeExternalUrl(data.link_evento)),
  ]);
});

const isReviewable = computed(() =>
  state.value === ESTADO_PUBLICACION.EN_REVISION
);

const decisionPlaceholder = computed(() =>
  decisionMode.value === "rechazar"
    ? "Explique claramente por qué se rechaza la publicación."
    : "Indique qué debe corregir el autor antes de reenviar la publicación."
);

const closedStateHelp = computed(() => {
  const messages = {
    [ESTADO_PUBLICACION.OBSERVADA]:
      "Se solicitaron correcciones al autor. Podrá revisarse nuevamente cuando sea reenviada.",
    [ESTADO_PUBLICACION.APROBADA]:
      "La publicación ya fue aprobada.",
    [ESTADO_PUBLICACION.RECHAZADA]:
      "La publicación fue rechazada.",
    [ESTADO_PUBLICACION.BORRADOR]:
      "La publicación aún no ha sido enviada a revisión.",
  };

  return (
    messages[state.value] ||
    "Esta publicación no requiere una decisión en este momento."
  );
});

const lastRelevantComment = computed(() => {
  const candidates = history.value
    .map((event) => {
      const comment = eventComment(event);
      if (!comment) return null;

      const code = eventCode(event);
      const relevant = ["observada", "rechazada", "aprobada"].includes(code);
      if (!relevant) return null;

      return {
        event,
        code,
        comment,
      };
    })
    .filter(Boolean);

  if (!candidates.length) return null;

  const selected = candidates[0];

  return {
    label: eventLabel(selected.event),
    comment: selected.comment,
    actor: eventActor(selected.event),
    date: selected.event?.created_at,
    tone: eventTone(selected.event),
    symbol: eventSymbol(selected.event),
  };
});

const MONTHS = Object.freeze({
  1: "Enero",
  2: "Febrero",
  3: "Marzo",
  4: "Abril",
  5: "Mayo",
  6: "Junio",
  7: "Julio",
  8: "Agosto",
  9: "Septiembre",
  10: "Octubre",
  11: "Noviembre",
  12: "Diciembre",
});

const AUDIT_EVENT_LABELS = Object.freeze({
  creada: "Publicación registrada",
  editada: "Publicación actualizada",
  enviada_revision: "Enviada a revisión",
  observada: "Correcciones solicitadas",
  aprobada: "Publicación aprobada",
  rechazada: "Publicación rechazada",
  reenviada_revision: "Reenviada a revisión",
});

const AUDIT_FIELD_LABELS = Object.freeze({
  sede: "Sede",
  sede_id: "Sede",
  facultad: "Facultad",
  facultad_id: "Facultad",
  carrera: "Carrera",
  carrera_id: "Carrera",
  proyecto: "Proyecto",
  proyecto_id: "Proyecto",
  area: "Área del conocimiento",
  area_id: "Área del conocimiento",
  subarea: "Subárea del conocimiento",
  subarea_id: "Subárea del conocimiento",
  pais: "País",
  pais_id: "País",
  ciudad: "Ciudad",
  ciudad_id: "Ciudad",
  origen_tipo: "Origen",
  origen_grado: "Información de origen",
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",

  // Distintos nombres internos representan para el usuario una sola cosa.
  archivo_pdf: "Documento PDF",
  archivo_pdf_nombre: "Documento PDF",
  pdf: "Documento PDF",
  pdf_principal: "Documento PDF",
  quitar_archivo_pdf: "Documento PDF",
  quitar_pdf_actual: "Documento PDF",
  eliminar_pdf: "Documento PDF",
  remover_pdf: "Documento PDF",
  remove_pdf: "Documento PDF",

  adjuntos: "Documentos adjuntos",
  adjuntos_pdf: "Documentos adjuntos",
  autores: "Autores",
  nombre_articulo: "Título del artículo",
  nombre_ponencia: "Título de la ponencia",
  nombre_libro: "Título del libro",
  nombre_capitulo: "Título del capítulo",
  codigo_doi: "DOI",
  codigo_issn: "ISSN",
  codigo_issn_isbn: "ISSN / ISBN",
  codigo_isbn: "ISBN",
  nombre_revista: "Revista",
  nombre_evento: "Evento",
  editorial_compilador: "Editorial / compilador",
  editor_compilador: "Editor / compilador",
  revisor_par_arbitraje: "Revisión por pares / arbitraje",
  base_datos_indexada: "Base de datos de indexación",
  base_datos_otra: "Otra base de datos",
  factor_impacto: "Factor de impacto",
  cuartil: "Cuartil",
  sjr: "SJR",
  jcr: "JCR",
  numero_revista: "Número de revista",
  numero_edicion: "Número de edición",
  paginas: "Páginas",
  paginas_capitulo: "Páginas del capítulo",
  modalidad: "Modalidad",
  link_publicacion: "Enlace de la publicación",
  link_revista: "Enlace de la revista",
  link_evento: "Enlace del evento",
  link_libro: "Enlace del libro",
  link_capitulo: "Enlace del capítulo",
});

const AUDIT_HIDDEN_FIELDS = new Set([
  "id",
  "publicacion_id",
  "estado",
  "estado_publicacion",
  "estado_anterior",
  "estado_resultante",
  "created_at",
  "updated_at",
]);

function firstFilled(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;

    if (typeof value === "string") {
      const text = value.trim();
      if (text) return text;
      continue;
    }

    if (typeof value === "number" && Number.isFinite(value)) {
      return String(value);
    }

    if (typeof value === "object" && !Array.isArray(value)) {
      const label = firstFilled(
        value.nombre,
        value.name,
        value.label,
        value.descripcion,
        value.email
      );
      if (label) return label;
    }
  }

  return "";
}

function valueLabel(...values) {
  return firstFilled(...values);
}

function field(label, value, href = "") {
  return {
    label,
    value: firstFilled(value),
    href: String(href || "").trim(),
  };
}

function visibleFields(items) {
  return items.filter((item) => item?.value);
}

function booleanLabel(value) {
  if (value === true || value === 1 || value === "true" || value === "1") {
    return "Sí";
  }

  if (value === false || value === 0 || value === "false" || value === "0") {
    return "No";
  }

  return "";
}

function normalizeAuthors(raw) {
  if (!Array.isArray(raw)) return [];

  return raw
    .map((item, index) => {
      const nested = item?.autor && typeof item.autor === "object"
        ? item.autor
        : {};

      const name = firstFilled(
        item?.autor_nombre,
        item?.nombre_completo,
        item?.nombre,
        nested?.nombre_completo,
        nested?.nombres && nested?.apellidos
          ? `${nested.nombres} ${nested.apellidos}`
          : "",
        nested?.nombre,
        `${firstFilled(item?.nombres)} ${firstFilled(item?.apellidos)}`.trim()
      );

      const order = Number(item?.orden || index + 1);

      return {
        key: firstFilled(item?.id, item?.autor_id, nested?.id, `${index}`),
        name: name || `Autor ${index + 1}`,
        email: firstFilled(
          item?.correo,
          item?.email,
          nested?.correo,
          nested?.email
        ),
        institution: firstFilled(
          item?.institucion,
          nested?.institucion
        ),
        order: Number.isFinite(order) && order > 0 ? order : index + 1,
      };
    })
    .sort((a, b) => a.order - b.order);
}

function normalizeHistory(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function normalizeError(error, fallback) {
  const status = Number(error?.response?.status || 0);
  const payload = error?.response?.data;

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para realizar esta acción.";
  }

  if (status === 404) {
    return "No se encontró la publicación solicitada.";
  }

  if (status === 409) {
    return "La publicación cambió mientras la revisaba. Actualice la información e inténtelo nuevamente.";
  }

  const direct =
    payload && typeof payload === "object"
      ? [
          payload.detail,
          payload.message,
          payload.mensaje,
          payload.error,
        ].find((value) => typeof value === "string" && value.trim())
      : "";

  const candidate = String(
    direct ||
      (typeof payload === "string" ? payload : "") ||
      ""
  ).trim();

  const technicalPattern =
    /(traceback|exception|database|sql|backend|endpoint|jwt|token|serializer|queryset|http\s*\d{3}|internal server|stack|foreign key|constraint)/i;

  if (candidate && !technicalPattern.test(candidate)) {
    return candidate;
  }

  return String(fallback || "No se pudo completar la acción.").trim();
}

function getBackendBase() {
  const environmentBase = firstFilled(
    import.meta.env.VITE_API_URL,
    import.meta.env.VITE_API_BASE_URL,
    import.meta.env.VITE_AXIOS_BASE_URL
  );

  const axiosBase = firstFilled(api?.defaults?.baseURL);
  const base = environmentBase || axiosBase;

  if (/^https?:\/\//i.test(base)) {
    return base
      .replace(/\/api\/?$/i, "")
      .replace(/\/$/, "");
  }

  return typeof window !== "undefined"
    ? window.location.origin
    : "";
}

function resolveFileUrl(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";

  if (/^https?:\/\//i.test(raw) || raw.startsWith("blob:") || raw.startsWith("data:")) {
    return raw;
  }

  const clean = raw.startsWith("/")
    ? raw
    : `/${raw.replace(/^\.?\//, "")}`;

  return `${getBackendBase()}${clean}`;
}

function fileNameFromUrl(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";

  try {
    const parsed = new URL(
      raw,
      typeof window !== "undefined" ? window.location.origin : "http://localhost"
    );

    return decodeURIComponent(
      parsed.pathname.split("/").filter(Boolean).pop() || ""
    );
  } catch {
    return "";
  }
}

function doiUrl(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;

  const clean = raw
    .replace(/^doi:\s*/i, "")
    .replace(/^https?:\/\/(dx\.)?doi\.org\//i, "");

  return `https://doi.org/${clean}`;
}

function normalizeExternalUrl(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  return `https://${raw.replace(/^\/+/, "")}`;
}

function formatDateTime(value) {
  if (!value) return "Sin fecha";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  const datePart = new Intl.DateTimeFormat("es-EC", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);

  const timePart = new Intl.DateTimeFormat("es-EC", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);

  return `${datePart} · ${timePart}`;
}

function eventCode(event) {
  return String(event?.evento || "").trim().toLowerCase();
}

function eventLabel(event) {
  const code = eventCode(event);

  return (
    AUDIT_EVENT_LABELS[code] ||
    String(event?.evento_label || "").trim() ||
    "Acción registrada"
  );
}

function eventTone(event) {
  const code = eventCode(event);
  if (code === "aprobada") return "success";
  if (code === "observada") return "warning";
  if (code === "rechazada") return "danger";
  if (["enviada_revision", "reenviada_revision"].includes(code)) {
    return "info";
  }
  return "neutral";
}

function eventSymbol(event) {
  const symbols = {
    creada: "+",
    editada: "✎",
    enviada_revision: "→",
    observada: "!",
    aprobada: "✓",
    rechazada: "×",
    reenviada_revision: "↻",
  };

  return symbols[eventCode(event)] || "·";
}

function eventActor(event) {
  return firstFilled(
    event?.actor_nombre,
    event?.actor_email,
    "Usuario no disponible"
  );
}

function eventTransition(event) {
  const previous = normalizarEstadoPublicacion(event?.estado_anterior);
  const result = normalizarEstadoPublicacion(event?.estado_resultante);

  // Si una edición no cambió el estado, no añadimos ruido al historial.
  if (previous && result && previous === result) {
    return "";
  }

  if (previous && result) {
    return `${estadoPublicacionLabel(previous)} → ${estadoPublicacionLabel(result)}`;
  }

  if (eventCode(event) === "creada" && result) {
    return `Estado inicial: ${estadoPublicacionLabel(result)}`;
  }

  if (result) return `Estado: ${estadoPublicacionLabel(result)}`;
  if (previous) return `Estado anterior: ${estadoPublicacionLabel(previous)}`;
  return "";
}

function humanizeAuditField(value) {
  const raw = String(value || "").trim();
  if (!raw || AUDIT_HIDDEN_FIELDS.has(raw)) return "";
  if (AUDIT_FIELD_LABELS[raw]) return AUDIT_FIELD_LABELS[raw];

  const readable = raw
    .replace(/_id$/, "")
    .replace(/_/g, " ")
    .trim();

  return readable
    ? readable.charAt(0).toUpperCase() + readable.slice(1)
    : "";
}

function eventChangedFields(event) {
  const fields = event?.detalle?.campos_modificados;
  if (!Array.isArray(fields)) return [];

  return [
    ...new Set(
      fields
        .map(humanizeAuditField)
        .filter(Boolean)
    ),
  ];
}

function naturalList(values) {
  const items = values.filter(Boolean);
  if (!items.length) return "";
  if (items.length === 1) return items[0];
  if (items.length === 2) return `${items[0]} y ${items[1]}`;
  return `${items.slice(0, -1).join(", ")} y ${items.at(-1)}`;
}

function eventChangesLabel(event) {
  const fields = eventChangedFields(event);
  if (!fields.length) return "";

  const visible = fields.slice(0, 4);
  const remaining = fields.length - visible.length;
  const prefix = fields.length === 1 ? "Se actualizó" : "Se actualizaron";

  if (remaining > 0) {
    return `${prefix}: ${visible.join(", ")} y ${remaining} ${
      remaining === 1 ? "dato más" : "datos más"
    }.`;
  }

  return `${prefix}: ${naturalList(visible)}.`;
}

function eventComment(event) {
  return firstFilled(
    event?.comentario,
    event?.observacion,
    event?.mensaje,
    event?.detalle?.comentario,
    event?.detalle?.observacion,
    event?.detalle?.mensaje
  );
}


function releasePdfPreview() {
  const current = String(pdfPreviewUrl.value || "");

  if (current.startsWith("blob:")) {
    URL.revokeObjectURL(current);
  }

  pdfPreviewUrl.value = "";
}

async function fetchPdfBlob() {
  if (!publicationId.value) {
    throw new Error("No se pudo identificar la publicación.");
  }

  const response = await api.get(
    `/publicaciones/${publicationId.value}/pdf/`,
    {
      responseType: "blob",
      headers: {
        Accept: "application/pdf",
      },
    }
  );

  const contentType = String(
    response.headers?.["content-type"] || ""
  ).toLowerCase();

  if (
    contentType &&
    !contentType.includes("application/pdf")
  ) {
    throw new Error(
      "El archivo recibido no corresponde a un documento PDF."
    );
  }

  return new Blob(
    [response.data],
    {
      type: "application/pdf",
    }
  );
}

async function loadPdfPreview() {
  const id = publicationId.value;
  const requestId = ++pdfRequestSerial;

  releasePdfPreview();
  pdfError.value = "";

  if (!id || !hasPdf.value) {
    pdfLoading.value = false;
    return;
  }

  pdfLoading.value = true;

  try {
    const blob = await fetchPdfBlob();

    if (requestId !== pdfRequestSerial) {
      return;
    }

    pdfPreviewUrl.value =
      URL.createObjectURL(blob);
  } catch (error) {
    if (requestId !== pdfRequestSerial) {
      return;
    }

    console.error(
      "No se pudo preparar el documento:",
      error
    );

    pdfError.value = normalizeError(
      error,
      "No se pudo mostrar el documento. Intente nuevamente."
    );
  } finally {
    if (requestId === pdfRequestSerial) {
      pdfLoading.value = false;
    }
  }
}

function openPdfInNewTab() {
  const url = String(
    pdfPreviewUrl.value || ""
  ).trim();

  if (!url) {
    openNotice({
      title: "Documento no disponible",
      message:
        "La vista previa todavía no está lista. Intente cargar nuevamente el documento.",
    });
    return;
  }

  // Se abre primero una pestaña vacía durante el gesto directo del usuario.
  // Esto permite distinguir un bloqueo real del navegador. Usar
  // `noopener` directamente como feature de window.open puede hacer que
  // algunos navegadores devuelvan null aunque la pestaña sí haya abierto.
  const previewWindow = window.open(
    "about:blank",
    "_blank"
  );

  if (!previewWindow) {
    openNotice({
      title: "No se pudo abrir el documento",
      message:
        "El navegador bloqueó la nueva pestaña. Permita ventanas emergentes para este sitio e inténtelo nuevamente.",
    });
    return;
  }

  try {
    // Evita que la pestaña nueva conserve acceso a la ventana del SGPC.
    previewWindow.opener = null;
    previewWindow.location.replace(url);
  } catch (error) {
    console.error(
      "No se pudo mostrar el documento en la nueva pestaña:",
      error
    );

    try {
      previewWindow.close();
    } catch {
      // La pestaña puede haberse cerrado o quedar fuera de nuestro control.
    }

    openNotice({
      title: "No se pudo abrir el documento",
      message:
        "Ocurrió un problema al abrir el documento. Inténtelo nuevamente.",
    });
  }
}

function toggleHistory() {
  historyOpen.value =
    !historyOpen.value;
}

function scheduleLoadingFeedback() {
  if (loadingFeedbackTimer) {
    clearTimeout(loadingFeedbackTimer);
  }

  loadingFeedbackVisible.value = false;
  loadingFeedbackTimer = setTimeout(() => {
    if (loading.value) {
      loadingFeedbackVisible.value = true;
    }
  }, 220);
}

function clearLoadingFeedback() {
  if (loadingFeedbackTimer) {
    clearTimeout(loadingFeedbackTimer);
    loadingFeedbackTimer = null;
  }

  loadingFeedbackVisible.value = false;
}

async function loadDetail() {
  const id = publicationId.value;
  if (!id) {
    detail.value = null;
    errorMessage.value = "No se pudo identificar la publicación solicitada.";
    return;
  }

  const requestId = ++detailRequestSerial;
  const hadDetail = Boolean(detail.value);
  loading.value = true;
  errorMessage.value = "";
  scheduleLoadingFeedback();

  try {
    const response = await obtenerAdminPublicacion(id);
    if (requestId !== detailRequestSerial) return;
    detail.value = response || null;
    hasLoadedDetail.value = true;
  } catch (error) {
    if (requestId !== detailRequestSerial) return;

    if (!hadDetail) {
      detail.value = null;
    }

    errorMessage.value = normalizeError(
      error,
      hadDetail
        ? "No se pudo actualizar la publicación. Se mantiene la última información disponible."
        : "No se pudo cargar la información de la publicación."
    );
  } finally {
    if (requestId === detailRequestSerial) {
      loading.value = false;
      clearLoadingFeedback();
    }
  }
}

async function loadHistory() {
  const id = publicationId.value;
  if (!id) return;

  const requestId = ++historyRequestSerial;
  historyLoading.value = true;
  historyError.value = "";

  try {
    const response = await obtenerAdminPublicacionHistorial(id);
    if (requestId !== historyRequestSerial) return;

    history.value = normalizeHistory(response);
  } catch (error) {
    if (requestId !== historyRequestSerial) return;

    history.value = [];
    historyError.value = normalizeError(
      error,
      "No se pudo cargar la actividad de revisión."
    );
  } finally {
    if (requestId === historyRequestSerial) {
      historyLoading.value = false;
    }
  }
}

async function loadAll() {
  successMessage.value = "";

  await Promise.all([
    loadDetail(),
    loadHistory(),
  ]);

  await loadPdfPreview();
}

function reviewContextQuery() {
  const allowed = [
    "estado",
    "q",
    "sede_id",
    "facultad_id",
    "carrera_id",
    "tipo",
    "anio",
    "solo_con_pdf",
    "pagina",
  ];

  return allowed.reduce((query, key) => {
    const value = route.query?.[key];
    if (value !== undefined && value !== null && String(value).trim()) {
      query[key] = value;
    }
    return query;
  }, {});
}

function goBackToReview() {
  router.push({
    name: "AdminRevisionPublicaciones",
    query: reviewContextQuery(),
  });
}

function routeNextId() {
  const parsed = Number(route.query?.next_id || 0);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 0;
}

async function findNextReviewable() {
  nextReviewLoading.value = true;

  try {
    const response = await listarAdminPublicaciones({
      estado: ESTADO_PUBLICACION.EN_REVISION,
      q: route.query?.q || undefined,
      sede_id: route.query?.sede_id || undefined,
      facultad_id: route.query?.facultad_id || undefined,
      carrera_id: route.query?.carrera_id || undefined,
      tipo: route.query?.tipo || undefined,
      anio: route.query?.anio || undefined,
      solo_con_pdf: route.query?.solo_con_pdf ? true : undefined,
      ordering: "updated_desc",
      page: 1,
      page_size: 2,
    });

    const rows = normalizeHistory(response?.results || response?.items || response?.data || response);
    const next = rows.find((item) => {
      const id = Number(item?.id || item?.publicacion_id || 0);
      return Number.isInteger(id) && id > 0 && id !== publicationId.value;
    });

    const candidate = Number(next?.id || next?.publicacion_id || routeNextId() || 0);
    nextReviewId.value = Number.isInteger(candidate) && candidate > 0
      ? candidate
      : 0;
  } catch (error) {
    const fallback = routeNextId();
    nextReviewId.value = fallback && fallback !== publicationId.value
      ? fallback
      : 0;
  } finally {
    nextReviewLoading.value = false;
  }
}

function goToNextReview() {
  const id = Number(nextReviewId.value || 0);
  if (!Number.isInteger(id) || id < 1 || actionLoading.value) return;

  successMessage.value = "";
  nextReviewId.value = 0;

  router.push({
    name: "AdminRevisionDetalle",
    params: { id },
    query: {
      ...reviewContextQuery(),
      estado: ESTADO_PUBLICACION.EN_REVISION,
    },
  });
}

function openLegacyDetail() {
  if (!publicationId.value) return;

  router.push({
    name: "AdminPublicacionDetalle",
    params: { id: publicationId.value },
  });
}

function selectDecisionMode(mode) {
  if (!isReviewable.value || actionLoading.value) return;
  if (!["observar", "rechazar"].includes(mode)) return;

  if (decisionMode.value === mode) {
    cancelDecision();
    return;
  }

  decisionMode.value = mode;
  decisionComment.value = "";
  decisionError.value = "";
}

function cancelDecision() {
  if (actionLoading.value) return;
  decisionMode.value = "";
  decisionComment.value = "";
  decisionError.value = "";
}

function approvePublication() {
  if (!publicationId.value || !isReviewable.value || actionLoading.value) {
    return;
  }

  openNotice({
    title: "Aprobar publicación",
    message:
      `¿Desea aprobar “${publicationTitle.value}”? ` +
      "El autor será notificado del resultado.",
    confirm: true,
    confirmText: "Aprobar publicación",
    cancelText: "Cancelar",
    onConfirm: confirmApprovePublication,
  });
}

async function confirmApprovePublication() {
  if (!publicationId.value || !isReviewable.value || actionLoading.value) {
    return;
  }

  actionLoading.value = true;
  activeAction.value = "aprobar";
  nextReviewId.value = 0;
  errorMessage.value = "";
  successMessage.value = "";
  decisionError.value = "";

  try {
    const response = await aprobarAdminPublicacion(publicationId.value);

    successMessage.value =
      response?.message ||
      "La publicación fue aprobada correctamente.";

    cancelDecisionAfterSave();
    await Promise.all([
      loadDetail(),
      loadHistory(),
    ]);
    await findNextReviewable();
  } catch (error) {
    errorMessage.value = normalizeError(
      error,
      "No fue posible aprobar la publicación."
    );
  } finally {
    actionLoading.value = false;
    activeAction.value = "";
  }
}

async function submitDecision() {
  if (!publicationId.value || !isReviewable.value || actionLoading.value) {
    return;
  }

  const comment = String(decisionComment.value || "").trim();

  if (!comment) {
    decisionError.value =
      decisionMode.value === "rechazar"
        ? "El motivo del rechazo es obligatorio."
        : "Indique qué debe corregir el autor.";
    return;
  }

  const submittedMode = decisionMode.value;

  actionLoading.value = true;
  activeAction.value = submittedMode;
  nextReviewId.value = 0;
  decisionError.value = "";
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const response =
      submittedMode === "rechazar"
        ? await rechazarAdminPublicacion(publicationId.value, comment)
        : await observarAdminPublicacion(publicationId.value, comment);

    successMessage.value =
      response?.message ||
      (submittedMode === "rechazar"
        ? "La publicación fue rechazada correctamente."
        : "La observación fue enviada al autor correctamente.");

    cancelDecisionAfterSave();
    await Promise.all([loadDetail(), loadHistory()]);
    await findNextReviewable();
  } catch (error) {
    decisionError.value = normalizeError(
      error,
      submittedMode === "rechazar"
        ? "No fue posible rechazar la publicación."
        : "No fue posible enviar la solicitud de corrección."
    );
  } finally {
    actionLoading.value = false;
    activeAction.value = "";
  }
}

function cancelDecisionAfterSave() {
  decisionMode.value = "";
  decisionComment.value = "";
  decisionError.value = "";
}

watch(
  () => route.params?.id,
  async () => {
    decisionMode.value = "";
    decisionComment.value = "";
    decisionError.value = "";
    activeAction.value = "";
    nextReviewId.value = 0;
    hasLoadedDetail.value = false;
    detail.value = null;
    history.value = [];
    historyOpen.value = false;
    pdfRequestSerial += 1;
    releasePdfPreview();
    await loadAll();
  }
);

onMounted(loadAll);

onBeforeUnmount(() => {
  detailRequestSerial += 1;
  historyRequestSerial += 1;
  pdfRequestSerial += 1;
  clearLoadingFeedback();
  releasePdfPreview();
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./admin-revision-detalle.css"></style>
<style src="./admin-revision-detalle-stage3.css"></style>
