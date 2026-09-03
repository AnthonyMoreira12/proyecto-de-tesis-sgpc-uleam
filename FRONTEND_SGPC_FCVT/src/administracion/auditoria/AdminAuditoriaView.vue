<template>
  <main class="audit-page">
    <section class="audit-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="audit-hero">
        <div class="audit-hero__copy">
          <span>Administración</span>

          <h1>Auditoría</h1>

          <p>
            Consulte los movimientos registrados en el SGPC y
            revise qué información cambió en cada operación.
          </p>
        </div>

        <button
          type="button"
          class="audit-export"
          :disabled="loading || exporting"
          @click="download"
        >
          {{ exporting ? "Generando Excel…" : "Exportar Excel" }}
        </button>
      </header>

      <!-- =====================================================
           RESUMEN
      ====================================================== -->
      <section
        class="audit-metrics"
        aria-label="Resumen de auditoría"
        :aria-busy="summaryLoading ? 'true' : 'false'"
      >
        <article>
          <span>Últimas 24 h</span>
          <strong>
            {{ summary.ultimas_24_horas || 0 }}
          </strong>
        </article>

        <article>
          <span>Usuarios activos</span>
          <strong>
            {{ summary.usuarios_activos_24h || 0 }}
          </strong>
        </article>

        <article>
          <span>Publicaciones</span>
          <strong>
            {{ summary.publicaciones_24h || 0 }}
          </strong>
        </article>

        <article>
          <span>Administrativas</span>
          <strong>
            {{ summary.administrativas_24h || 0 }}
          </strong>
        </article>
      </section>

      <!-- =====================================================
           FILTROS AUTOMÁTICOS
      ====================================================== -->
      <section
        class="audit-filters"
        role="search"
        aria-label="Filtros de auditoría"
      >
        <label class="audit-field audit-field--search">
          <span>Buscar</span>

          <input
            v-model.trim="filters.q"
            type="search"
            placeholder="Usuario, registro o descripción"
            aria-label="Buscar en auditoría"
          >
        </label>

        <label class="audit-field">
          <span>Módulo</span>

          <select
            v-model="filters.modulo"
            aria-label="Filtrar por módulo"
          >
            <option value="">
              Todos
            </option>

            <option
              v-for="item in modules"
              :key="item"
              :value="item"
            >
              {{ moduleLabel(item) }}
            </option>
          </select>
        </label>

        <label class="audit-field">
          <span>Acción</span>

          <select
            v-model="filters.accion"
            aria-label="Filtrar por acción"
          >
            <option value="">
              Todas
            </option>

            <option
              v-for="item in actions"
              :key="item"
              :value="item"
            >
              {{ actionLabel(item) }}
            </option>
          </select>
        </label>

        <label class="audit-field">
          <span>Desde</span>

          <input
            v-model="filters.fecha_desde"
            type="date"
            aria-label="Fecha desde"
          >
        </label>

        <label class="audit-field">
          <span>Hasta</span>

          <input
            v-model="filters.fecha_hasta"
            type="date"
            aria-label="Fecha hasta"
          >
        </label>

        <button
          v-if="hasFilters"
          type="button"
          class="audit-clear"
          @click="clearFilters"
        >
          Limpiar
        </button>
      </section>

      <!-- =====================================================
           MENSAJES
      ====================================================== -->
      <AdminErrorState
        v-if="error && !events.length && !loading"
        :message="error"
        :retrying="loading"
        @retry="load"
      />

      <AdminActionFeedback
        v-else-if="error && events.length"
        status="error"
        :message="`${error} Se mantienen los últimos movimientos cargados.`"
      />

      <AdminInlineLoader
        v-if="refreshing"
        message="Actualizando movimientos…"
      />

      <AdminLoadingState
        v-if="initialLoading"
        message="Cargando movimientos de auditoría…"
        description="Consultando la actividad registrada en el sistema."
        :skeleton-rows="5"
      />

      <!-- =====================================================
           TABLA
      ====================================================== -->
      <section
        v-else
        class="audit-table-wrap"
        :aria-busy="loading ? 'true' : 'false'"
      >
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Módulo</th>
              <th>Descripción</th>
              <th aria-label="Acciones"></th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="event in events"
              :key="event.id"
            >
              <td class="audit-date">
                {{ date(event.created_at) }}
              </td>

              <td>
                <strong>
                  {{ event.actor_nombre || "Sistema" }}
                </strong>

                <small v-if="event.actor_email">
                  {{ event.actor_email }}
                </small>
              </td>

              <td>
                <span class="audit-chip">
                  {{ actionLabel(event.accion) }}
                </span>
              </td>

              <td>
                {{ moduleLabel(event.modulo) }}
              </td>

              <td class="audit-description">
                {{ event.descripcion || eventSummary(event) }}
              </td>

              <td class="audit-table-action">
                <button
                  type="button"
                  @click="openDetail(event)"
                >
                  Ver
                </button>
              </td>
            </tr>

            <tr v-if="!loading && !events.length">
              <td
                colspan="6"
                class="audit-empty"
              >
                {{ hasFilters ? "No encontramos movimientos con los filtros seleccionados." : "Todavía no hay movimientos registrados." }}
              </td>
            </tr>

          </tbody>
        </table>
      </section>
    </section>

    <!-- =======================================================
         DETALLE
    ======================================================== -->
    <Teleport to="body">
      <div
        v-if="selected"
        class="sgpc-modal-overlay audit-overlay"
        @click.self="closeDetail"
      >
        <section
          class="sgpc-modal-card audit-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="audit-modal-title"
        >
          <!-- CABECERA -->
          <header class="audit-modal__header">
            <div>
              <span>Registro de actividad</span>

              <h2 id="audit-modal-title">
                Detalle de auditoría
              </h2>
            </div>

            <button
              type="button"
              class="audit-modal__close"
              aria-label="Cerrar"
              title="Cerrar"
              @click="closeDetail"
            >
              ×
            </button>
          </header>

          <!-- RESUMEN DEL EVENTO -->
          <section class="audit-event-summary">
            <div class="audit-event-summary__main">
              <strong>
                {{ selected.actor_nombre || "Sistema" }}
              </strong>

              <span>
                {{ eventSummary(selected) }}
              </span>
            </div>

            <time>
              {{ longDate(selected.created_at) }}
            </time>
          </section>

          <!-- INFORMACIÓN PRINCIPAL -->
          <section class="audit-modal-section">
            <h3>Información del evento</h3>

            <dl class="audit-info-grid">
              <div>
                <dt>Usuario</dt>
                <dd>
                  {{ selected.actor_nombre || "Sistema" }}

                  <small v-if="selected.actor_email">
                    {{ selected.actor_email }}
                  </small>
                </dd>
              </div>

              <div>
                <dt>Acción</dt>
                <dd>
                  {{ actionLabel(selected.accion) }}
                </dd>
              </div>

              <div>
                <dt>Módulo</dt>
                <dd>
                  {{ moduleLabel(selected.modulo) }}
                </dd>
              </div>

              <div>
                <dt>Registro afectado</dt>
                <dd>
                  {{ entityLabel(selected) }}
                </dd>
              </div>
            </dl>
          </section>

          <!-- CAMBIOS -->
          <section class="audit-modal-section">
            <div class="audit-sectionhead">
              <div>
                <h3>
                  {{ changesSectionTitle }}
                </h3>

                <p>
                  {{ changesSectionDescription }}
                </p>
              </div>

              <span
                v-if="visibleChanges.length"
                class="audit-change-count"
              >
                {{ visibleChanges.length }}
                {{ visibleChanges.length === 1 ? "cambio" : "cambios" }}
              </span>
            </div>

            <!-- UPDATE -->
            <div
              v-if="auditMode === 'update' && visibleChanges.length"
              class="audit-change-list"
            >
              <article
                v-for="change in visibleChanges"
                :key="change.path"
                class="audit-change"
              >
                <header>
                  <strong>
                    {{ fieldLabel(change.path) }}
                  </strong>
                </header>

                <div class="audit-change__values">
                  <div class="audit-change__value">
                    <span>Antes</span>

                    <strong>
                      {{ displayValue(change.before, change.path) }}
                    </strong>
                  </div>

                  <div
                    class="audit-change__arrow"
                    aria-hidden="true"
                  >
                    →
                  </div>

                  <div class="audit-change__value audit-change__value--new">
                    <span>Después</span>

                    <strong>
                      {{ displayValue(change.after, change.path) }}
                    </strong>
                  </div>
                </div>
              </article>
            </div>

            <!-- CREATE / DELETE -->
            <div
              v-else-if="visibleChanges.length"
              class="audit-value-list"
            >
              <article
                v-for="change in visibleChanges"
                :key="change.path"
              >
                <span>
                  {{ fieldLabel(change.path) }}
                </span>

                <strong>
                  {{
                    displayValue(
                      auditMode === "delete"
                        ? change.before
                        : change.after,
                      change.path
                    )
                  }}
                </strong>
              </article>
            </div>

            <!-- SIN CAMBIOS -->
            <div
              v-else
              class="audit-nochanges"
            >
              <strong>
                No se detectaron diferencias de datos para mostrar.
              </strong>

              <span>
                El evento quedó registrado correctamente en la auditoría.
              </span>
            </div>
          </section>

          <!-- DESCRIPCIÓN -->
          <section
            v-if="selected.descripcion"
            class="audit-modal-section"
          >
            <h3>Descripción</h3>

            <p class="audit-event-description">
              {{ selected.descripcion }}
            </p>
          </section>

          <!-- CONTEXTO FUNCIONAL -->
          <section
            v-if="hasContext"
            class="audit-modal-section"
          >
            <h3>Contexto</h3>

            <dl class="audit-context-grid">
              <div
                v-for="item in contextItems"
                :key="item.key"
              >
                <dt>
                  {{ fieldLabel(item.key) }}
                </dt>

                <dd>
                  {{ displayValue(item.value, item.key) }}
                </dd>
              </div>
            </dl>
          </section>

          <!-- INFORMACIÓN AVANZADA -->
          <section
            v-if="hasAdvancedInfo"
            class="audit-technical"
          >
            <button
              type="button"
              class="audit-technical__toggle"
              :aria-expanded="technicalOpen"
              @click="technicalOpen = !technicalOpen"
            >
              <span>Información avanzada</span>

              <span aria-hidden="true">
                {{ technicalOpen ? "−" : "+" }}
              </span>
            </button>

            <div
              v-if="technicalOpen"
              class="audit-technical__body"
            >
              <dl class="audit-technical-grid">
                <div v-if="selected.ip">
                  <dt>Origen de red</dt>
                  <dd>{{ selected.ip }}</dd>
                </div>

                <div v-if="selected.metodo_http">
                  <dt>Tipo de operación</dt>
                  <dd>{{ selected.metodo_http }}</dd>
                </div>

                <div v-if="selected.ruta">
                  <dt>Ruta utilizada</dt>
                  <dd>{{ selected.ruta }}</dd>
                </div>
              </dl>
            </div>
          </section>
        </section>
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
  apiErrorMessage,
  asResults,
  exportarAuditoria,
  listarAuditoria,
  resumenAuditoria,
} from "../../scripts/api/actualizacionesApi";

import {
  useAutoFilters,
} from "../../scripts/composables/useAutoFilters";

import {
  useModalLayer,
} from "../../scripts/composables/useModalLayer";

import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";


/* ============================================================
   ESTADO
============================================================ */

const events = ref([]);
const selected = ref(null);

const error = ref("");
const loading = ref(false);
const visibleLoadFeedback = ref(false);
const exporting = ref(false);
const summaryLoading = ref(false);

const technicalOpen = ref(false);

let loadSequence = 0;
let loadFeedbackTimer = null;

const summary = reactive({});

const filters = reactive({
  q: "",
  modulo: "",
  accion: "",
  fecha_desde: "",
  fecha_hasta: "",
});


/* ============================================================
   CATÁLOGOS
============================================================ */

const modules = [
  "actualizaciones",
  "comunicaciones",
  "publicaciones",
  "proyectos",
  "perfil",
  "usuarios",
  "notificaciones",
  "estructura_academica",
  "autores",
  "archivos",
  "revision",
  "autenticacion",
];


const actions = [
  "crear",
  "actualizar",
  "eliminar",
  "activar",
  "finalizar",
  "cancelar",
  "aprobar",
  "rechazar",
  "observar",
  "enviar",
  "exportar",
  "iniciar_sesion",
  "cerrar_sesion",
];


const MODULE_LABELS = {
  actualizaciones: "Actualización de datos",
  comunicaciones: "Comunicaciones",
  publicaciones: "Publicaciones",
  proyectos: "Proyectos",
  perfil: "Perfil",
  usuarios: "Usuarios",
  notificaciones: "Notificaciones",
  estructura_academica: "Estructura académica",
  autores: "Autores",
  archivos: "Archivos",
  revision: "Revisión de publicaciones",
  autenticacion: "Autenticación",
};


const ACTION_LABELS = {
  crear: "Creación",
  actualizar: "Actualización",
  eliminar: "Eliminación",
  activar: "Activación",
  finalizar: "Finalización",
  cancelar: "Cancelación",
  aprobar: "Aprobación",
  rechazar: "Rechazo",
  observar: "Observación",
  enviar: "Envío",
  exportar: "Exportación",
  iniciar_sesion: "Inicio de sesión",
  cerrar_sesion: "Cierre de sesión",
};


const ENTITY_LABELS = {
  Usuario: "Usuario",
  Publicacion: "Publicación",
  Proyecto: "Proyecto",
  ComunicacionGlobal: "Comunicación global",
  CampaniaActualizacion: "Campaña de actualización",
  CampaniaActualizacionUsuario: "Participante de campaña",
  Notificacion: "Notificación",
  Facultad: "Facultad",
  Carrera: "Carrera",
  Sede: "Sede",
  CarreraSede: "Relación carrera-sede",
  Autor: "Autor",
  PublicacionArchivo: "Archivo de publicación",
  PublicacionRevision: "Revisión de publicación",
};


const FIELD_LABELS = {
  tipo: "Tipo",
  activa: "Estado",
  activo: "Estado",
  titulo: "Título",
  nombre: "Nombre",
  mensaje: "Mensaje",
  descripcion: "Descripción",

  fecha_inicio: "Fecha de inicio",
  fecha_fin: "Fecha de finalización",
  fecha_fin_planificada: "Fecha de finalización planificada",
  fecha_fin_prorrogada: "Fecha de finalización prorrogada",

  sede: "Sede",
  sede_id: "Sede",
  carrera: "Carrera",
  carrera_id: "Carrera",
  facultad: "Facultad",
  facultad_id: "Facultad",

  estado: "Estado",
  perfil_completo: "Perfil completo",

  area: "Área UNESCO",
  area_id: "Área UNESCO",
  subarea: "Subárea UNESCO",
  subarea_id: "Subárea UNESCO",

  pais: "País",
  ciudad: "Ciudad",

  proyecto: "Proyecto",
  proyecto_id: "Proyecto",

  archivo_pdf_nombre_original: "Nombre original del PDF",
  archivo_pdf_tamano_bytes: "Tamaño del PDF",
  archivo_pdf_sha256: "SHA-256 del PDF",

  campania_id: "Campaña",
  origen: "Origen",
  destinatarios: "Destinatarios",

  created_at: "Creado",
  updated_at: "Última actualización",
};


/* ============================================================
   COMPUTADOS
============================================================ */

const hasFilters = computed(() => (
  Object.values(filters).some(Boolean)
));

const initialLoading = computed(() => (
  loading.value &&
  visibleLoadFeedback.value &&
  !events.value.length
));

const refreshing = computed(() => (
  loading.value &&
  visibleLoadFeedback.value &&
  Boolean(events.value.length)
));

const hasAdvancedInfo = computed(() => Boolean(
  selected.value?.ip ||
  selected.value?.metodo_http ||
  selected.value?.ruta
));


const modalOpen = computed(() => (
  Boolean(selected.value)
));


const beforeData = computed(() => (
  normalizeObject(
    selected.value?.datos_anteriores
  )
));


const afterData = computed(() => (
  normalizeObject(
    selected.value?.datos_nuevos
  )
));


const contextData = computed(() => (
  normalizeObject(
    selected.value?.contexto
  )
));


const hasContext = computed(() => (
  Object.keys(contextData.value).length > 0
));


const contextItems = computed(() => (
  Object.entries(contextData.value).map(
    ([key, value]) => ({
      key,
      value,
    })
  )
));


const auditMode = computed(() => {
  const beforeKeys = Object.keys(beforeData.value);
  const afterKeys = Object.keys(afterData.value);

  if (
    !beforeKeys.length &&
    afterKeys.length
  ) {
    return "create";
  }

  if (
    beforeKeys.length &&
    !afterKeys.length
  ) {
    return "delete";
  }

  return "update";
});


const visibleChanges = computed(() => {
  if (!selected.value) {
    return [];
  }

  if (auditMode.value === "create") {
    return flattenEntries(
      {},
      afterData.value
    );
  }

  if (auditMode.value === "delete") {
    return flattenEntries(
      beforeData.value,
      {}
    );
  }

  return diffObjects(
    beforeData.value,
    afterData.value
  );
});


const changesSectionTitle = computed(() => {
  if (auditMode.value === "create") {
    return "Información registrada";
  }

  if (auditMode.value === "delete") {
    return "Información eliminada";
  }

  return "Cambios realizados";
});


const changesSectionDescription = computed(() => {
  if (auditMode.value === "create") {
    return "Información principal registrada durante esta operación.";
  }

  if (auditMode.value === "delete") {
    return "Información que tenía el registro antes de su eliminación.";
  }

  return "Se muestran únicamente los campos cuyo valor cambió.";
});


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

function moduleLabel(value) {
  if (!value) {
    return "General";
  }

  return (
    MODULE_LABELS[value] ||
    humanize(value)
  );
}


function actionLabel(value) {
  if (!value) {
    return "Movimiento";
  }

  return (
    ACTION_LABELS[value] ||
    humanize(value)
  );
}


function entityLabel(event) {
  if (!event) {
    return "—";
  }

  const type =
    ENTITY_LABELS[event.entidad_tipo] ||
    humanize(event.entidad_tipo || "");

  if (!type) {
    return "—";
  }

  return type;
}


function eventSummary(event) {
  if (!event) {
    return "";
  }

  const action =
    actionVerb(event.accion);

  const entity =
    ENTITY_LABELS[event.entidad_tipo] ||
    moduleLabel(event.modulo).toLowerCase();

  return `${action} ${lowerFirst(entity)}.`;
}


function actionVerb(action) {
  const map = {
    crear: "Creó",
    actualizar: "Actualizó",
    eliminar: "Eliminó",
    activar: "Activó",
    finalizar: "Finalizó",
    cancelar: "Canceló",
    aprobar: "Aprobó",
    rechazar: "Rechazó",
    observar: "Observó",
    enviar: "Envió",
    exportar: "Exportó",
    iniciar_sesion: "Inició sesión en",
    cerrar_sesion: "Cerró sesión en",
  };

  return map[action] || "Realizó una acción sobre";
}


function fieldLabel(path) {
  if (!path) {
    return "Campo";
  }

  const key = path
    .split(".")
    .at(-1);

  return (
    FIELD_LABELS[key] ||
    humanize(key)
  );
}


function humanize(value) {
  if (!value) {
    return "";
  }

  const text = String(value)
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  return text.charAt(0).toUpperCase() +
    text.slice(1);
}


function lowerFirst(value) {
  if (!value) {
    return "";
  }

  return value.charAt(0).toLowerCase() +
    value.slice(1);
}


function date(value) {
  if (!value) {
    return "—";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
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
    return "Fecha no disponible";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
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


function isDateLike(value) {
  if (typeof value !== "string") {
    return false;
  }

  return (
    /^\d{4}-\d{2}-\d{2}T/.test(value) ||
    /^\d{4}-\d{2}-\d{2}$/.test(value)
  );
}


function displayValue(value, path = "") {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Sin valor";
  }

  if (typeof value === "boolean") {
    return value
      ? "Sí"
      : "No";
  }

  if (
    path.endsWith("tamano_bytes") &&
    Number.isFinite(Number(value))
  ) {
    return formatBytes(
      Number(value)
    );
  }

  if (isDateLike(value)) {
    return longDate(value);
  }

  if (Array.isArray(value)) {
    if (!value.length) {
      return "Sin elementos";
    }

    return value
      .map((item) => (
        isPrimitive(item)
          ? displayValue(item)
          : compactJson(item)
      ))
      .join(", ");
  }

  if (
    typeof value === "object"
  ) {
    return compactJson(value);
  }

  return String(value);
}


function formatBytes(bytes) {
  if (!bytes) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let value = bytes;
  let unitIndex = 0;

  while (
    value >= 1024 &&
    unitIndex < units.length - 1
  ) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${value.toFixed(
    unitIndex ? 2 : 0
  )} ${units[unitIndex]}`;
}


function pretty(value) {
  return JSON.stringify(
    normalizeObject(value),
    null,
    2
  );
}


function compactJson(value) {
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}


function normalizeObject(value) {
  if (
    !value ||
    typeof value !== "object" ||
    Array.isArray(value)
  ) {
    return {};
  }

  return value;
}


function isPrimitive(value) {
  return (
    value === null ||
    ["string", "number", "boolean"].includes(
      typeof value
    )
  );
}


/* ============================================================
   COMPARACIÓN
============================================================ */

function valuesEqual(a, b) {
  return stableStringify(a) ===
    stableStringify(b);
}


function stableStringify(value) {
  if (
    value === null ||
    typeof value !== "object"
  ) {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return JSON.stringify(
      value.map((item) => (
        JSON.parse(
          stableStringify(item)
        )
      ))
    );
  }

  const normalized = {};

  Object.keys(value)
    .sort()
    .forEach((key) => {
      normalized[key] =
        value[key];
    });

  return JSON.stringify(normalized);
}


function diffObjects(
  before,
  after,
  parentPath = ""
) {
  const changes = [];

  const keys = new Set([
    ...Object.keys(before || {}),
    ...Object.keys(after || {}),
  ]);

  keys.forEach((key) => {
    const oldValue =
      before?.[key];

    const newValue =
      after?.[key];

    const path =
      parentPath
        ? `${parentPath}.${key}`
        : key;

    if (
      isPlainObject(oldValue) &&
      isPlainObject(newValue)
    ) {
      changes.push(
        ...diffObjects(
          oldValue,
          newValue,
          path
        )
      );

      return;
    }

    if (
      !valuesEqual(
        oldValue,
        newValue
      )
    ) {
      changes.push({
        path,
        before: oldValue,
        after: newValue,
      });
    }
  });

  return changes;
}


function flattenEntries(
  before,
  after
) {
  const source =
    Object.keys(after || {}).length
      ? after
      : before;

  return Object.entries(source)
    .map(([key, value]) => ({
      path: key,
      before: before?.[key],
      after: after?.[key],
    }));
}


function isPlainObject(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}


/* ============================================================
   MODAL
============================================================ */

function openDetail(event) {
  technicalOpen.value = false;
  selected.value = event;
}


function closeDetail() {
  technicalOpen.value = false;
  selected.value = null;
}


/* ============================================================
   DATOS
============================================================ */

async function load() {
  const sequence =
    ++loadSequence;

  loading.value = true;
  error.value = "";
  visibleLoadFeedback.value = false;

  window.clearTimeout(loadFeedbackTimer);
  loadFeedbackTimer = window.setTimeout(() => {
    if (
      loading.value &&
      sequence === loadSequence
    ) {
      visibleLoadFeedback.value = true;
    }
  }, 220);

  try {
    const payload = asResults(
      await listarAuditoria({
        ...filters,
      })
    );

    if (
      sequence !== loadSequence
    ) {
      return;
    }

    events.value = payload;
  } catch (err) {
    if (
      sequence !== loadSequence
    ) {
      return;
    }

    error.value =
      apiErrorMessage(err);
  } finally {
    if (
      sequence === loadSequence
    ) {
      window.clearTimeout(loadFeedbackTimer);
      loadFeedbackTimer = null;
      visibleLoadFeedback.value = false;
      loading.value = false;
    }
  }
}


async function loadSummary() {
  summaryLoading.value = true;

  try {
    Object.assign(
      summary,
      await resumenAuditoria()
    );
  } catch {
    // El resumen no bloquea el listado.
  } finally {
    summaryLoading.value = false;
  }
}


function clearFilters() {
  Object.assign(
    filters,
    {
      q: "",
      modulo: "",
      accion: "",
      fecha_desde: "",
      fecha_hasta: "",
    }
  );
}


async function download() {
  if (exporting.value) {
    return;
  }

  exporting.value = true;

  try {
    error.value = "";

    const response =
      await exportarAuditoria({
        ...filters,
      });

    const blob =
      response.data instanceof Blob
        ? response.data
        : new Blob(
            [response.data],
            {
              type:
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
          );

    const contentDisposition =
      response.headers?.[
        "content-disposition"
      ] || "";

    const match =
      contentDisposition.match(
        /filename="?([^";]+)"?/i
      );

    const filename =
      match?.[1] ||
      `auditoria_sgpc_${dateStamp()}.xlsx`;

    const url =
      URL.createObjectURL(
        blob
      );

    const anchor =
      document.createElement("a");

    anchor.href =
      url;

    anchor.download =
      filename;

    document.body.appendChild(
      anchor
    );

    anchor.click();

    anchor.remove();

    URL.revokeObjectURL(
      url
    );
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudo exportar el reporte de auditoría."
      );
  } finally {
    exporting.value = false;
  }
}


function dateStamp() {
  const now =
    new Date();

  const pad = (
    value
  ) => String(
    value
  ).padStart(
    2,
    "0"
  );

  return [
    now.getFullYear(),
    pad(
      now.getMonth() + 1
    ),
    pad(
      now.getDate()
    ),
    "_",
    pad(
      now.getHours()
    ),
    pad(
      now.getMinutes()
    ),
    pad(
      now.getSeconds()
    ),
  ].join("");
}


/* ============================================================
   INICIO
============================================================ */

onMounted(() => {
  load();
  loadSummary();
});

onBeforeUnmount(() => {
  window.clearTimeout(loadFeedbackTimer);
});
</script>

<style src="./admin-auditoria.css"></style>
<style src="./admin-auditoria-stage6.css"></style>