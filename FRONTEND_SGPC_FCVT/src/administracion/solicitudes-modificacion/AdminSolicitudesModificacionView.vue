<template>
  <main class="asm-page">
    <section class="asm-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="asm-hero">
        <div class="asm-hero__copy">
          <span>Administración</span>

          <h1>Solicitudes de modificación</h1>

          <p>
            Revise y resuelva cambios sensibles solicitados sobre
            publicaciones que ya fueron aprobadas.
          </p>
        </div>
      </header>

      <!-- =====================================================
           FILTROS AUTOMÁTICOS
      ====================================================== -->
      <section
        class="asm-filters"
        role="search"
        aria-label="Filtros de solicitudes"
      >
        <label class="asm-field asm-field--search">
          <span>Buscar</span>

          <input
            v-model.trim="filters.q"
            type="search"
            placeholder="Usuario, publicación o motivo"
            aria-label="Buscar solicitudes"
          >
        </label>

        <label class="asm-field">
          <span>Estado</span>

          <select
            v-model="filters.estado"
            aria-label="Filtrar por estado"
          >
            <option value="">
              Todos los estados
            </option>

            <option value="pendiente">
              Pendientes
            </option>

            <option value="aprobada">
              Aprobadas
            </option>

            <option value="rechazada">
              Rechazadas
            </option>

            <option value="cancelada">
              Canceladas
            </option>
          </select>
        </label>

        <button
          v-if="hasFilters"
          type="button"
          class="asm-clear"
          @click="clearFilters"
        >
          Limpiar
        </button>
      </section>

      <AdminInlineLoader
        v-if="loading && requests.length"
        class="asm-inline-loader"
        message="Actualizando solicitudes…"
      />

      <AdminActionFeedback
        v-if="actionMessage"
        class="asm-action-feedback"
        :status="actionStatus"
        :message="actionMessage"
      />

      <!-- =====================================================
           ERROR
      ====================================================== -->
      <p
        v-if="error"
        class="asm-error"
        role="alert"
      >
        {{ error }}
      </p>

      <!-- =====================================================
           CARGA
      ====================================================== -->
      <AdminLoadingState
        v-if="loading && !requests.length"
        class="asm-loading"
        message="Cargando solicitudes de modificación…"
        description="Consultando los cambios pendientes y su información asociada."
        :skeleton-rows="4"
      />

      <!-- =====================================================
           LISTADO
      ====================================================== -->
      <section
        v-else
        class="asm-list"
        :aria-busy="loading"
      >
        <article
          v-for="item in requests"
          :key="item.id"
          class="asm-card"
        >
          <header class="asm-card__head">
            <div class="asm-card__identity">
              <span>
                Solicitud de modificación
              </span>

              <h2>
                {{
                  item.publicacion_titulo ||
                  "Publicación sin título"
                }}
              </h2>

              <p>
                {{ item.solicitante_nombre || "Usuario" }}
                ·
                {{ date(item.created_at) }}
              </p>
            </div>

            <span
              class="asm-state"
              :data-state="item.estado"
            >
              {{ stateLabel(item.estado) }}
            </span>
          </header>

          <section class="asm-reason">
            <span>Motivo</span>

            <p>
              {{
                item.motivo ||
                "Sin motivo especificado."
              }}
            </p>
          </section>

          <!-- RESUMEN DE CAMBIOS -->
          <section
            v-if="requestedChanges(item).length"
            class="asm-changes"
          >
            <article
              v-for="change in requestedChanges(item)"
              :key="change.field"
              class="asm-change"
            >
              <header>
                <strong>
                  {{ label(change.field) }}
                </strong>
              </header>

              <div class="asm-change__comparison">
                <div class="asm-change__value">
                  <span>Actual</span>

                  <strong>
                    {{
                      displayValue(
                        change.before,
                        change.field
                      )
                    }}
                  </strong>
                </div>

                <span
                  class="asm-change__arrow"
                  aria-hidden="true"
                >
                  →
                </span>

                <div
                  class="
                    asm-change__value
                    asm-change__value--requested
                  "
                >
                  <span>Solicitado</span>

                  <strong>
                    {{
                      displayValue(
                        change.after,
                        change.field
                      )
                    }}
                  </strong>
                </div>
              </div>
            </article>
          </section>

          <section
            v-else
            class="asm-nochanges"
          >
            No se encontraron campos comparables en la solicitud.
          </section>

          <footer class="asm-card__actions">
            <button
              type="button"
              @click="openDetail(item)"
            >
              Ver detalle
            </button>

            <button
              v-if="item.estado === 'pendiente'"
              type="button"
              class="approve"
              :disabled="busy"
              @click="openResolve(item, true)"
            >
              Aprobar
            </button>

            <button
              v-if="item.estado === 'pendiente'"
              type="button"
              class="reject"
              :disabled="busy"
              @click="openResolve(item, false)"
            >
              Rechazar
            </button>
          </footer>
        </article>

        <div
          v-if="!loading && !requests.length && !error"
          class="asm-empty"
        >
          <strong>
            No hay solicitudes
          </strong>

          <span>
            No se encontraron solicitudes para los filtros
            seleccionados.
          </span>
        </div>
      </section>
    </section>

    <!-- =======================================================
         MODALES
    ======================================================== -->
    <Teleport to="body">
      <!-- =====================================================
           DETALLE
      ====================================================== -->
      <div
        v-if="selected"
        class="sgpc-modal-overlay asm-overlay"
        @click.self="closeDetail"
      >
        <section
          class="sgpc-modal-card asm-modal asm-modal--detail"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`asm-detail-title-${selected.id}`"
        >
          <header class="asm-modal__header">
            <div>
              <span>Solicitud de modificación</span>

              <h2
                :id="`asm-detail-title-${selected.id}`"
              >
                Detalle de la solicitud
              </h2>
            </div>

            <button
              type="button"
              class="asm-modal__close"
              aria-label="Cerrar"
              title="Cerrar"
              @click="closeDetail"
            >
              ×
            </button>
          </header>

          <!-- RESUMEN -->
          <section class="asm-detail-summary">
            <div>
              <strong>
                {{
                  selected.publicacion_titulo ||
                  "Publicación sin título"
                }}
              </strong>

              <span>
                {{ selected.solicitante_nombre || "Usuario" }}
                ·
                {{ date(selected.created_at) }}
              </span>
            </div>

            <span
              class="asm-state"
              :data-state="selected.estado"
            >
              {{ stateLabel(selected.estado) }}
            </span>
          </section>

          <!-- INFORMACIÓN -->
          <section class="asm-modal-section">
            <h3>Información de la solicitud</h3>

            <dl class="asm-info-grid">
              <div>
                <dt>Solicitante</dt>

                <dd>
                  {{
                    selected.solicitante_nombre ||
                    "Sin información"
                  }}
                </dd>
              </div>

              <div>
                <dt>Fecha de solicitud</dt>

                <dd>
                  {{ longDate(selected.created_at) }}
                </dd>
              </div>

              <div>
                <dt>Estado</dt>

                <dd>
                  {{ stateLabel(selected.estado) }}
                </dd>
              </div>

              <div>
                <dt>Campos solicitados</dt>

                <dd>
                  {{
                    selected.campos_solicitados?.length || 0
                  }}
                </dd>
              </div>
            </dl>
          </section>

          <!-- MOTIVO -->
          <section class="asm-modal-section">
            <h3>Motivo</h3>

            <p class="asm-detail-text">
              {{
                selected.motivo ||
                "No se especificó un motivo."
              }}
            </p>
          </section>

          <!-- COMPARACIÓN -->
          <section class="asm-modal-section">
            <header class="asm-sectionhead">
              <div>
                <h3>Cambios solicitados</h3>

                <p>
                  Compare la información actualmente registrada
                  con el valor propuesto por el usuario.
                </p>
              </div>

              <span class="asm-change-count">
                {{ selectedChanges.length }}
                {{
                  selectedChanges.length === 1
                    ? "cambio"
                    : "cambios"
                }}
              </span>
            </header>

            <div
              v-if="selectedChanges.length"
              class="asm-detail-changes"
            >
              <article
                v-for="change in selectedChanges"
                :key="change.field"
                class="asm-detail-change"
              >
                <header>
                  <strong>
                    {{ label(change.field) }}
                  </strong>
                </header>

                <div class="asm-detail-change__body">
                  <div class="asm-detail-value">
                    <span>Actual</span>

                    <strong>
                      {{
                        displayValue(
                          change.before,
                          change.field
                        )
                      }}
                    </strong>
                  </div>

                  <span
                    class="asm-detail-arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>

                  <div
                    class="
                      asm-detail-value
                      asm-detail-value--requested
                    "
                  >
                    <span>Solicitado</span>

                    <strong>
                      {{
                        displayValue(
                          change.after,
                          change.field
                        )
                      }}
                    </strong>
                  </div>
                </div>
              </article>
            </div>

            <div
              v-else
              class="asm-nochanges"
            >
              No hay diferencias para mostrar.
            </div>
          </section>

          <!-- RESOLUCIÓN -->
          <section
            v-if="
              selected.estado !== 'pendiente' &&
              (
                selected.comentario_resolucion ||
                selected.revisor_nombre ||
                selected.resuelto_at
              )
            "
            class="asm-modal-section"
          >
            <h3>Resolución</h3>

            <dl class="asm-info-grid">
              <div v-if="selected.revisor_nombre">
                <dt>Revisado por</dt>

                <dd>
                  {{ selected.revisor_nombre }}
                </dd>
              </div>

              <div v-if="selected.resuelto_at">
                <dt>Fecha</dt>

                <dd>
                  {{ longDate(selected.resuelto_at) }}
                </dd>
              </div>
            </dl>

            <p
              v-if="selected.comentario_resolucion"
              class="asm-resolution-comment"
            >
              {{ selected.comentario_resolucion }}
            </p>
          </section>

          <!-- DATOS TÉCNICOS -->
          <!-- ACCIONES -->
          <footer
            v-if="selected.estado === 'pendiente'"
            class="asm-modal__footer"
          >
            <button
              type="button"
              :disabled="busy"
              @click="openResolve(selected, false)"
            >
              Rechazar
            </button>

            <button
              type="button"
              class="approve"
              :disabled="busy"
              @click="openResolve(selected, true)"
            >
              Aprobar solicitud
            </button>
          </footer>
        </section>
      </div>

      <!-- =====================================================
           RESOLVER
      ====================================================== -->
      <div
        v-if="resolveItem"
        class="sgpc-modal-overlay asm-overlay"
        @click.self="closeResolve"
      >
        <form
          class="sgpc-modal-card asm-modal asm-modal--resolve"
          role="dialog"
          aria-modal="true"
          aria-labelledby="asm-resolve-title"
          @submit.prevent="resolve"
        >
          <header class="asm-modal__header">
            <div>
              <span>
                Resolución administrativa
              </span>

              <h2 id="asm-resolve-title">
                {{
                  approveMode
                    ? "Aprobar solicitud"
                    : "Rechazar solicitud"
                }}
              </h2>
            </div>

            <button
              type="button"
              class="asm-modal__close"
              aria-label="Cerrar"
              title="Cerrar"
              :disabled="busy"
              @click="closeResolve"
            >
              ×
            </button>
          </header>

          <section class="asm-resolve-intro">
            <strong>
              {{
                resolveItem.publicacion_titulo ||
                "Publicación sin título"
              }}
            </strong>

            <span>
              {{ resolveItem.solicitante_nombre || "Usuario" }}
            </span>
          </section>

          <!-- CAMBIOS QUE SE RESOLVERÁN -->
          <section class="asm-modal-section">
            <header class="asm-sectionhead">
              <div>
                <h3>
                  {{
                    approveMode
                      ? "Cambios que se aplicarán"
                      : "Cambios solicitados"
                  }}
                </h3>

                <p>
                  {{
                    approveMode
                      ? "Al aprobar, estos valores serán aplicados a la publicación."
                      : "Estos cambios permanecerán sin aplicar."
                  }}
                </p>
              </div>
            </header>

            <div class="asm-resolve-changes">
              <article
                v-for="change in resolveChanges"
                :key="change.field"
              >
                <span>
                  {{ label(change.field) }}
                </span>

                <strong>
                  {{
                    displayValue(
                      change.after,
                      change.field
                    )
                  }}
                </strong>
              </article>
            </div>
          </section>

          <!-- COMENTARIO -->
          <section class="asm-modal-section">
            <label class="asm-comment-field">
              <span>
                {{
                  approveMode
                    ? "Comentario"
                    : "Motivo del rechazo"
                }}
              </span>

              <textarea
                v-model.trim="comment"
                rows="4"
                :required="!approveMode"
                :placeholder="
                  approveMode
                    ? 'Comentario opcional para el solicitante'
                    : 'Explique por qué la solicitud fue rechazada'
                "
              ></textarea>

              <small>
                {{
                  approveMode
                    ? "Este comentario será visible para el solicitante."
                    : "El motivo es obligatorio y será informado al solicitante."
                }}
              </small>
            </label>
          </section>

          <footer class="asm-modal__footer">
            <button
              type="button"
              :disabled="busy"
              @click="closeResolve"
            >
              Cancelar
            </button>

            <button
              type="submit"
              :class="
                approveMode
                  ? 'approve'
                  : 'reject'
              "
              :disabled="
                busy ||
                (
                  !approveMode &&
                  !comment.trim()
                )
              "
            >
              {{
                busy
                  ? approveMode
                    ? "Aprobando y aplicando…"
                    : "Rechazando solicitud…"
                  : approveMode
                    ? "Aprobar y aplicar"
                    : "Rechazar solicitud"
              }}
            </button>
          </footer>
        </form>
      </div>
    </Teleport>
  </main>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
} from "vue";

import {
  aprobarSolicitudModificacion,
  listarSolicitudesModificacionAdmin,
  rechazarSolicitudModificacion,
} from "../../scripts/api/solicitudesModificacionApi";

import {
  useAutoFilters,
} from "../../scripts/composables/useAutoFilters";

import {
  useModalLayer,
} from "../../scripts/composables/useModalLayer";

import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import { useActionState } from "../_shared/composables/useActionState";


/* ============================================================
   ESTADO
============================================================ */

const requests = ref([]);

const selected = ref(null);
const resolveItem = ref(null);

const approveMode = ref(false);

const comment = ref("");

const busy = ref(false);
const loading = ref(false);

const error = ref("");

const {
  status: actionStatus,
  message: actionMessage,
  start: startAction,
  success: successAction,
  fail: failAction,
  reset: resetAction,
} = useActionState();

let actionFeedbackTimer = null;
let loadSequence = 0;


const filters = reactive({
  q: "",
  estado: "pendiente",
});


const defaultFilters = {
  q: "",
  estado: "pendiente",
};


/* ============================================================
   ETIQUETAS
============================================================ */

const labels = {
  anio_publicacion: "Año de publicación",
  mes_publicacion: "Mes de publicación",

  origen_tipo: "Origen",
  origen_grado: "Grado o programa",

  autores: "Autores",

  nombre_evento: "Nombre del evento",
  nombre_ponencia: "Nombre de la ponencia",

  codigo_issn_isbn: "ISSN / ISBN",

  tipo_presentacion: "Tipo de presentación",
  tipo_presentacion_otro: "Otra presentación",

  link_evento: "Enlace del evento",

  revisor_par_arbitraje: "Revisión por pares",

  nombre_articulo: "Nombre del artículo",

  base_datos_indexada: "Base de datos indexada",
  base_datos_otra: "Otra base de datos",

  codigo_doi: "DOI",
  codigo_issn: "ISSN",

  nombre_revista: "Revista",
  numero_revista: "Número de revista",

  link_publicacion: "Enlace de publicación",
  link_revista: "Enlace de revista",

  factor_impacto: "Factor de impacto",

  cuartil: "Cuartil",
  sjr: "SJR",
  jcr: "JCR",

  nombre_libro: "Nombre del libro",
  codigo_isbn: "ISBN",

  editorial_compilador:
    "Editorial o compilador",

  link_libro: "Enlace del libro",

  nombre_capitulo:
    "Nombre del capítulo",

  editor_compilador:
    "Editor o compilador",

  link_capitulo:
    "Enlace del capítulo",
};


/* ============================================================
   COMPUTADOS
============================================================ */

const hasFilters = computed(() => (
  filters.q !== defaultFilters.q ||
  filters.estado !== defaultFilters.estado
));


const modalOpen = computed(() => (
  Boolean(
    selected.value ||
    resolveItem.value
  )
));


const selectedChanges = computed(() => (
  selected.value
    ? requestedChanges(
        selected.value
      )
    : []
));


const resolveChanges = computed(() => (
  resolveItem.value
    ? requestedChanges(
        resolveItem.value
      )
    : []
));


/* ============================================================
   COMPOSABLES
============================================================ */

useAutoFilters(
  filters,
  load,
  {
    delay: 300,
  }
);


useModalLayer(
  modalOpen
);


/* ============================================================
   FORMATO
============================================================ */

function label(field) {
  return (
    labels[field] ||
    humanize(field)
  );
}


function stateLabel(state) {
  const states = {
    pendiente: "Pendiente",
    aprobada: "Aprobada",
    rechazada: "Rechazada",
    cancelada: "Cancelada",
  };

  return (
    states[state] ||
    humanize(state)
  );
}


function humanize(value) {
  if (!value) {
    return "Campo";
  }

  const text =
    String(value)
      .replace(
        /([a-z])([A-Z])/g,
        "$1 $2"
      )
      .replace(/_/g, " ")
      .trim();

  return (
    text.charAt(0).toUpperCase() +
    text.slice(1)
  );
}


function date(value) {
  if (!value) {
    return "—";
  }

  const parsed =
    new Date(value);

  if (
    Number.isNaN(
      parsed.getTime()
    )
  ) {
    return String(value);
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      dateStyle: "short",
      timeStyle: "short",
    }
  ).format(parsed);
}


function longDate(value) {
  if (!value) {
    return "—";
  }

  const parsed =
    new Date(value);

  if (
    Number.isNaN(
      parsed.getTime()
    )
  ) {
    return String(value);
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(parsed);
}


function displayValue(
  value,
  field = ""
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Sin información";
  }

  if (
    typeof value === "boolean"
  ) {
    return value
      ? "Sí"
      : "No";
  }

  if (
    field === "mes_publicacion"
  ) {
    return monthLabel(value);
  }

  if (
    Array.isArray(value)
  ) {
    if (!value.length) {
      return "Sin información";
    }

    return value
      .map((item) => (
        typeof item === "object"
          ? objectSummary(item)
          : String(item)
      ))
      .join(", ");
  }

  if (
    typeof value === "object"
  ) {
    return objectSummary(value);
  }

  return String(value);
}


function monthLabel(value) {
  const numeric =
    Number(value);

  if (
    !Number.isInteger(numeric) ||
    numeric < 1 ||
    numeric > 12
  ) {
    return String(value);
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      month: "long",
    }
  ).format(
    new Date(
      2026,
      numeric - 1,
      1
    )
  );
}


function objectSummary(value) {
  if (!value) {
    return "Sin información";
  }

  if (
    value.nombre ||
    value.name ||
    value.titulo ||
    value.label
  ) {
    return (
      value.nombre ||
      value.name ||
      value.titulo ||
      value.label
    );
  }

  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}



/* ============================================================
   CAMBIOS
============================================================ */

function requestedChanges(item) {
  if (!item) {
    return [];
  }

  const fields =
    Array.isArray(
      item.campos_solicitados
    )
      ? item.campos_solicitados
      : Object.keys(
          item.cambios_solicitados ||
          {}
        );

  return fields.map(
    (field) => ({
      field,

      before:
        item.datos_anteriores
          ?.[field],

      after:
        item.cambios_solicitados
          ?.[field],
    })
  );
}


/* ============================================================
   RESPUESTAS API
============================================================ */

function asList(payload) {
  if (
    Array.isArray(payload)
  ) {
    return payload;
  }

  if (
    Array.isArray(
      payload?.results
    )
  ) {
    return payload.results;
  }

  if (
    Array.isArray(
      payload?.data
    )
  ) {
    return payload.data;
  }

  return [];
}


/* ============================================================
   MODALES
============================================================ */

function openDetail(item) {
  selected.value = item;
}


function closeDetail() {
  selected.value = null;
}


function openResolve(
  item,
  approve
) {
  selected.value = null;

  resolveItem.value = item;

  approveMode.value =
    Boolean(approve);

  comment.value = "";
}


function closeResolve() {
  if (busy.value) {
    return;
  }

  resolveItem.value = null;

  comment.value = "";
}


const scheduleActionFeedbackReset = () => {
  if (actionFeedbackTimer) {
    window.clearTimeout(actionFeedbackTimer);
  }

  actionFeedbackTimer = window.setTimeout(() => {
    resetAction();
    actionFeedbackTimer = null;
  }, 3600);
};


/* ============================================================
   DATOS
============================================================ */

async function load() {
  const sequence =
    ++loadSequence;

  loading.value = true;

  error.value = "";

  try {
    const payload =
      asList(
        await listarSolicitudesModificacionAdmin({
          ...filters,
        })
      );

    if (
      sequence !== loadSequence
    ) {
      return;
    }

    requests.value =
      payload;
  } catch (err) {
    if (
      sequence !== loadSequence
    ) {
      return;
    }

    const baseMessage =
      getErrorMessage(
        err,
        "No fue posible cargar las solicitudes."
      );

    error.value =
      requests.value.length
        ? `${baseMessage} Se mantienen los últimos resultados cargados.`
        : baseMessage;
  } finally {
    if (
      sequence === loadSequence
    ) {
      loading.value = false;
    }
  }
}


function clearFilters() {
  Object.assign(
    filters,
    defaultFilters
  );
}


/* ============================================================
   RESOLUCIÓN
============================================================ */

async function resolve() {
  if (
    busy.value ||
    !resolveItem.value
  ) {
    return;
  }

  if (
    !approveMode.value &&
    !comment.value.trim()
  ) {
    return;
  }

  busy.value = true;

  error.value = "";
  startAction(
    approveMode.value
      ? "Aprobando y aplicando cambios…"
      : "Rechazando solicitud…"
  );

  try {
    const id =
      resolveItem.value.id;

    let resolvedPayload = null;

    if (approveMode.value) {
      resolvedPayload =
        await aprobarSolicitudModificacion(
          id,
          comment.value
        );
    } else {
      resolvedPayload =
        await rechazarSolicitudModificacion(
          id,
          comment.value
        );
    }

    const resolvedAsApproved =
      approveMode.value;

    resolveItem.value = null;
    comment.value = "";

    /*
      La vista abre por defecto con solicitudes pendientes.
      En ese caso no necesitamos volver a descargar toda la cola:
      retiramos localmente la solicitud ya resuelta.
      Para otros estados intentamos fusionar la respuesta del backend
      y solo recargamos si la API no devolvió el registro actualizado.
    */
    if (filters.estado === "pendiente") {
      requests.value =
        requests.value.filter(
          (item) =>
            Number(item?.id) !==
            Number(id)
        );
    } else {
      const resolvedRequest =
        resolvedPayload?.solicitud ||
        resolvedPayload?.data ||
        resolvedPayload;

      if (
        resolvedRequest &&
        typeof resolvedRequest === "object" &&
        Number(resolvedRequest?.id) ===
          Number(id)
      ) {
        requests.value =
          requests.value.map(
            (item) =>
              Number(item?.id) ===
                Number(id)
                ? {
                    ...item,
                    ...resolvedRequest,
                  }
                : item
          );
      } else {
        await load();
      }
    }

    successAction(
      resolvedAsApproved
        ? "Solicitud aprobada y cambios aplicados correctamente."
        : "Solicitud rechazada correctamente."
    );
    scheduleActionFeedbackReset();
  } catch (err) {
    error.value =
      (
        err?.response?.data
          ?.comentario?.[0] ||
        getErrorMessage(
          err,
          "No fue posible resolver la solicitud."
        )
      );

    failAction(error.value);
    scheduleActionFeedbackReset();
  } finally {
    busy.value = false;
  }
}


/* ============================================================
   ERROR
============================================================ */

function getErrorMessage(
  err,
  fallback
) {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}


/* ============================================================
   INICIO
============================================================ */

onMounted(
  load
);

onBeforeUnmount(() => {
  if (actionFeedbackTimer) {
    window.clearTimeout(actionFeedbackTimer);
    actionFeedbackTimer = null;
  }
});
</script>

<style src="./admin-solicitudes-modificacion.css"></style>
<style scoped src="./admin-solicitudes-modificacion-stage4.css"></style>