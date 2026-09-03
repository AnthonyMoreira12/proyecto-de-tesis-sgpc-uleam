<template>
  <main class="admin-updates">
    <section class="admin-updates__shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="admin-updates__hero">
        <div class="admin-updates__hero-copy">
          <span>Administración</span>

          <h1>Actualización de datos</h1>

          <p>
            Habilite periodos controlados para completar información
            histórica sin abrir campos sensibles del sistema.
          </p>
        </div>

        <button
          type="button"
          :disabled="initialLoading || Boolean(workingKey)"
          @click="openNew"
        >
          Nueva campaña
        </button>
      </header>

      <!-- =====================================================
           PESTAÑAS
      ====================================================== -->
      <nav
        class="admin-updates__tabs"
        aria-label="Secciones de actualización"
      >
        <button
          type="button"
          :class="{ active: tab === 'campanias' }"
          @click="tab = 'campanias'"
        >
          Campañas
        </button>

        <button
          type="button"
          :class="{ active: tab === 'comunicaciones' }"
          @click="tab = 'comunicaciones'"
        >
          Comunicaciones globales
        </button>
      </nav>

      <!-- =====================================================
           ERROR
      ====================================================== -->
      <AdminErrorState
        v-if="error && !hasLoadedData && !loading"
        :message="error"
        :retrying="loading"
        @retry="load"
      />

      <AdminActionFeedback
        v-else-if="error && hasLoadedData"
        status="error"
        :message="`${error} Se mantiene la última información disponible.`"
      />

      <AdminActionFeedback
        v-if="successMessage"
        status="success"
        :message="successMessage"
      />

      <!-- =====================================================
           CARGA
      ====================================================== -->
      <AdminLoadingState
        v-if="initialLoading"
        message="Cargando actualización de datos…"
        description="Consultando campañas, comunicaciones y catálogos institucionales."
        :skeleton-rows="4"
      />

      <AdminInlineLoader
        v-else-if="refreshing"
        message="Actualizando campañas y comunicaciones…"
      />

      <!-- =====================================================
           CAMPAÑAS
      ====================================================== -->
      <section
        v-if="tab === 'campanias'"
        class="admin-updates__list"
      >
        <article
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="admin-updates__card"
        >
          <header class="admin-updates__card-head">
            <div>
              <span>
                {{ typeLabel(campaign.tipo) }}
              </span>

              <h2>
                {{ campaign.titulo }}
              </h2>

              <p class="admin-updates__period">
                {{ campaignPeriod(campaign) }}
              </p>
            </div>

            <span
              class="admin-updates__state"
              :data-state="campaign.estado"
            >
              {{ stateLabel(campaign.estado) }}
            </span>
          </header>

          <p class="admin-updates__description">
            {{
              campaign.descripcion ||
              "Sin descripción."
            }}
          </p>

          <!-- ALCANCE -->
          <div class="admin-updates__meta">
            <span>Alcance</span>

            <strong>
              {{ scopeLabel(campaign) }}
            </strong>
          </div>

          <!-- CAMPOS -->
          <section
            v-if="campaign.campos_habilitados?.length"
            class="admin-updates__fields"
          >
            <span class="admin-updates__fields-label">
              Campos habilitados
            </span>

            <div>
              <span
                v-for="field in campaign.campos_habilitados"
                :key="field"
              >
                {{ fieldLabel(field) }}
              </span>
            </div>
          </section>

          <!-- PROGRESO -->
          <section class="admin-updates__metrics">
            <article>
              <span>Pendientes</span>

              <strong>
                {{ campaign.progreso?.pendientes || 0 }}
              </strong>
            </article>

            <article>
              <span>En progreso</span>

              <strong>
                {{ campaign.progreso?.en_progreso || 0 }}
              </strong>
            </article>

            <article>
              <span>Completados</span>

              <strong>
                {{ campaign.progreso?.completadas || 0 }}
              </strong>
            </article>

            <article>
              <span>Afectados</span>

              <strong>
                {{ campaign.progreso?.total || 0 }}
              </strong>
            </article>
          </section>

          <!-- ACCIONES -->
          <footer class="admin-updates__card-actions">
            <div class="admin-updates__primary-actions">
              <button
                type="button"
                :disabled="isCampaignBusy(campaign)"
                @click="showParticipants(campaign)"
              >
                {{
                  isWorking(campaign, "participants")
                    ? "Cargando participantes…"
                    : "Participantes"
                }}
              </button>

              <button
                v-if="campaign.estado === 'borrador'"
                type="button"
                class="primary"
                :disabled="isCampaignBusy(campaign)"
                @click="requestActivate(campaign)"
              >
                Activar
              </button>

              <button
                v-else-if="campaign.estado === 'activa'"
                type="button"
                class="primary"
                :disabled="isCampaignBusy(campaign)"
                @click="requestFinish(campaign)"
              >
                Finalizar
              </button>
            </div>

            <details
              v-if="campaign.estado === 'borrador' || campaign.estado === 'activa'"
              class="admin-updates__more"
            >
              <summary>Más</summary>

              <div class="admin-updates__more-menu">
                <template v-if="campaign.estado === 'borrador'">
                  <button
                    type="button"
                    :disabled="isCampaignBusy(campaign)"
                    @click="diagnose(campaign)"
                  >
                    {{
                      isWorking(campaign, "diagnostic")
                        ? "Generando diagnóstico…"
                        : "Diagnóstico"
                    }}
                  </button>

                  <button
                    type="button"
                    :disabled="isCampaignBusy(campaign)"
                    @click="edit(campaign)"
                  >
                    Editar
                  </button>

                  <button
                    type="button"
                    class="danger"
                    :disabled="isCampaignBusy(campaign)"
                    @click="remove(campaign)"
                  >
                    Eliminar
                  </button>
                </template>

                <template v-else>
                  <button
                    type="button"
                    :disabled="isCampaignBusy(campaign)"
                    @click="requestReminder(campaign)"
                  >
                    {{
                      isWorking(campaign, "reminder")
                        ? "Enviando recordatorio…"
                        : "Enviar recordatorio"
                    }}
                  </button>

                  <button
                    type="button"
                    :disabled="isCampaignBusy(campaign)"
                    @click="recalc(campaign)"
                  >
                    {{
                      isWorking(campaign, "recalculate")
                        ? "Recalculando…"
                        : "Recalcular pendientes"
                    }}
                  </button>

                  <button
                    type="button"
                    class="danger"
                    :disabled="isCampaignBusy(campaign)"
                    @click="requestCancel(campaign)"
                  >
                    Cancelar campaña
                  </button>
                </template>
              </div>
            </details>
          </footer>
        </article>

        <div
          v-if="!loading && !campaigns.length"
          class="admin-updates__empty"
        >
          <strong>No hay campañas registradas</strong>

          <span>
            Cree una campaña cuando necesite solicitar
            información adicional a los usuarios.
          </span>
        </div>
      </section>

      <!-- =====================================================
           COMUNICACIONES
      ====================================================== -->
      <section
        v-else
        class="admin-updates__list"
      >
        <div class="admin-updates__toolbar">
          <button
            type="button"
            @click="openCommunication"
          >
            Nueva comunicación
          </button>
        </div>

        <article
          v-for="communication in communications"
          :key="communication.id"
          class="admin-updates__card"
        >
          <header class="admin-updates__card-head">
            <div>
              <span>
                {{ commType(communication.tipo) }}
              </span>

              <h2>
                {{ communication.titulo }}
              </h2>
            </div>

            <span
              class="admin-updates__state"
              :data-state="
                communication.activa
                  ? 'activa'
                  : 'inactiva'
              "
            >
              {{
                communication.activa
                  ? "Activa"
                  : "Inactiva"
              }}
            </span>
          </header>

          <p class="admin-updates__description">
            {{ communication.mensaje }}
          </p>

          <div
            v-if="
              communication.etiqueta_accion ||
              communication.ruta_accion
            "
            class="admin-updates__communication-action"
          >
            <span>Acción configurada</span>

            <strong>
              {{
                communication.etiqueta_accion ||
                "Abrir"
              }}
            </strong>

          </div>

          <footer class="admin-updates__card-actions">
            <button
              type="button"
              @click="editCommunication(communication)"
            >
              Editar
            </button>

            <button
              type="button"
              class="danger"
              @click="removeCommunication(communication)"
            >
              Eliminar
            </button>
          </footer>
        </article>

        <div
          v-if="!loading && !communications.length"
          class="admin-updates__empty"
        >
          <strong>No hay comunicaciones globales</strong>

          <span>
            Puede publicar un aviso cuando necesite informar
            algo a los usuarios del sistema.
          </span>
        </div>
      </section>
    </section>

    <!-- =======================================================
         MODALES
    ======================================================== -->
    <Teleport to="body">
      <!-- =====================================================
           CAMPAÑA
      ====================================================== -->
      <div
        v-if="showCampaignForm"
        class="sgpc-modal-overlay admin-updates__overlay"
        @click.self="closeForm"
      >
        <form
          class="sgpc-modal-card admin-updates__modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="campaign-form-title"
          @submit.prevent="saveCampaign"
        >
          <header class="admin-updates__modal-header">
            <div>
              <span>Administración</span>

              <h2 id="campaign-form-title">
                {{
                  editingId
                    ? "Editar campaña"
                    : "Nueva campaña"
                }}
              </h2>
            </div>

            <button
              type="button"
              class="admin-updates__modal-close"
              aria-label="Cerrar"
              :disabled="formBusy"
              @click="closeForm"
            >
              ×
            </button>
          </header>

          <div class="admin-updates__modal-body">
            <!-- INFORMACIÓN -->
            <section class="admin-updates__form-section">
              <header>
                <h3>Información general</h3>

                <p>
                  Identifique el propósito y periodo de la campaña.
                </p>
              </header>

              <label class="admin-updates__field">
                <span>Título</span>

                <input
                  v-model.trim="form.titulo"
                  required
                  maxlength="180"
                >
              </label>

              <label class="admin-updates__field">
                <span>Descripción</span>

                <textarea
                  v-model.trim="form.descripcion"
                  rows="3"
                  maxlength="1000"
                ></textarea>
              </label>

              <div class="admin-updates__grid">
                <label class="admin-updates__field">
                  <span>Tipo de información</span>

                  <select
                    v-model="form.tipo"
                    @change="onTypeChange"
                  >
                    <option value="perfil">
                      Perfil
                    </option>

                    <option value="publicacion">
                      Publicaciones
                    </option>

                    <option value="proyecto">
                      Proyectos
                    </option>
                  </select>
                </label>

                <label class="admin-updates__field">
                  <span>Alcance</span>

                  <select
                    v-model="form.alcance"
                    @change="onScopeChange"
                  >
                    <option value="todos">
                      Todos
                    </option>

                    <option value="sede">
                      Sede
                    </option>

                    <option value="facultad">
                      Facultad
                    </option>

                    <option value="carrera">
                      Carrera
                    </option>

                    <option value="usuarios">
                      Usuarios específicos
                    </option>
                  </select>
                </label>
              </div>

              <p
                v-if="form.tipo === 'publicacion'"
                class="admin-updates__business-rule"
              >
                Las campañas de publicaciones se aplican únicamente a
                publicaciones aprobadas. Los demás estados continúan en su
                flujo normal de revisión y corrección.
              </p>

              <!-- FILTRO DE ALCANCE -->
              <label
                v-if="
                  ['sede', 'facultad', 'carrera']
                    .includes(form.alcance)
                "
                class="admin-updates__field"
              >
                <span>
                  {{ scopeFieldLabel }}
                </span>

                <select
                  v-model="scopeId"
                  required
                >
                  <option value="">
                    Seleccione
                  </option>

                  <option
                    v-for="item in scopeOptions"
                    :key="item.id"
                    :value="String(item.id)"
                  >
                    {{
                      item.nombre ||
                      item.label ||
                      `Registro ${item.id}`
                    }}
                  </option>
                </select>
              </label>

              <label
                v-if="form.alcance === 'usuarios'"
                class="admin-updates__field"
              >
                <span>Usuarios específicos</span>

                <input
                  v-model.trim="userIds"
                  placeholder="Ejemplo: 12, 18, 25"
                  required
                >

                <small>
                  Ingrese los identificadores separados por coma.
                </small>
              </label>

              <div class="admin-updates__grid">
                <label class="admin-updates__field">
                  <span>Fecha de inicio</span>

                  <input
                    v-model="form.fecha_inicio"
                    type="datetime-local"
                  >
                </label>

                <label class="admin-updates__field">
                  <span>Fecha de finalización</span>

                  <input
                    v-model="form.fecha_fin"
                    type="datetime-local"
                  >
                </label>
              </div>

              <label class="admin-updates__check">
                <input
                  v-model="form.solo_incompletos"
                  type="checkbox"
                >

                <span>
                  Incluir únicamente registros con información
                  pendiente
                </span>
              </label>
            </section>

            <!-- CAMPOS -->
            <section class="admin-updates__form-section">
              <header>
                <h3>Campos habilitados</h3>

                <p>
                  Seleccione exactamente qué información podrá
                  completar el usuario.
                </p>
              </header>

              <fieldset class="admin-updates__field-options">
                <label
                  v-for="field in fieldsForType"
                  :key="field"
                >
                  <input
                    v-model="form.campos_habilitados"
                    type="checkbox"
                    :value="field"
                  >

                  <span>
                    {{ fieldLabel(field) }}
                  </span>
                </label>
              </fieldset>

              <p
                v-if="
                  campaignValidationError &&
                  !form.campos_habilitados.length
                "
                class="admin-updates__inline-error"
              >
                Seleccione al menos un campo.
              </p>
            </section>

            <!-- COMUNICACIÓN -->
            <section class="admin-updates__form-section">
              <header>
                <h3>Comunicación</h3>

                <p>
                  Defina cómo se informará a los participantes
                  cuando se active la campaña.
                </p>
              </header>

              <div class="admin-updates__communication-options">
                <label>
                  <input
                    v-model="form.crear_aviso"
                    type="checkbox"
                  >

                  <span>
                    Publicar comunicación global
                  </span>
                </label>

                <label>
                  <input
                    v-model="form.notificar_internamente"
                    type="checkbox"
                  >

                  <span>
                    Enviar notificación interna
                  </span>
                </label>

                <label>
                  <input
                    v-model="form.enviar_correo"
                    type="checkbox"
                  >

                  <span>
                    Enviar correo electrónico
                  </span>
                </label>
              </div>
            </section>
          </div>

          <footer class="admin-updates__modal-footer">
            <button
              type="button"
              :disabled="formBusy"
              @click="closeForm"
            >
              Cancelar
            </button>

            <button
              type="submit"
              class="primary"
              :disabled="formBusy"
            >
              {{
                formBusy
                  ? (editingId ? "Guardando cambios…" : "Creando campaña…")
                  : (editingId ? "Guardar cambios" : "Crear campaña")
              }}
            </button>
          </footer>
        </form>
      </div>

      <!-- =====================================================
           DETALLE DIAGNÓSTICO / PARTICIPANTES
      ====================================================== -->
      <div
        v-if="detail"
        class="sgpc-modal-overlay admin-updates__overlay"
        @click.self="closeDetail"
      >
        <section
          class="
            sgpc-modal-card
            admin-updates__modal
            admin-updates__modal--wide
          "
          role="dialog"
          aria-modal="true"
          aria-labelledby="admin-update-detail-title"
        >
          <header class="admin-updates__modal-header">
            <div>
              <span>
                {{
                  detail.kind === "participants"
                    ? "Participantes"
                    : "Diagnóstico"
                }}
              </span>

              <h2 id="admin-update-detail-title">
                {{ detail.title }}
              </h2>
            </div>

            <button
              type="button"
              class="admin-updates__modal-close"
              aria-label="Cerrar"
              @click="closeDetail"
            >
              ×
            </button>
          </header>

          <div class="admin-updates__modal-body">
            <!-- PARTICIPANTES -->
            <template v-if="detail.kind === 'participants'">
              <section
                v-if="participantRows.length"
                class="admin-updates__participants"
              >
                <header class="admin-updates__detail-heading">
                  <div>
                    <h3>Participantes de la campaña</h3>

                    <p>
                      {{ participantRows.length }}
                      {{
                        participantRows.length === 1
                          ? "participante"
                          : "participantes"
                      }}
                      registrados.
                    </p>
                  </div>
                </header>

                <article
                  v-for="participant in participantRows"
                  :key="participant.key"
                  class="admin-updates__participant"
                >
                  <div class="admin-updates__participant-main">
                    <strong>
                      {{ participant.name }}
                    </strong>

                    <span v-if="participant.email">
                      {{ participant.email }}
                    </span>
                  </div>

                  <div class="admin-updates__participant-meta">
                    <span
                      class="admin-updates__state"
                      :data-state="participant.state"
                    >
                      {{ participant.stateLabel }}
                    </span>

                    <span v-if="participant.pending !== null">
                      {{ participant.pending }}
                      pendientes
                    </span>
                  </div>
                </article>
              </section>

              <section
                v-else
                class="admin-updates__detail-empty"
              >
                No se encontraron participantes para mostrar.
              </section>
            </template>

            <!-- DIAGNÓSTICO -->
            <template v-else>
              <section class="admin-updates__diagnostic">
                <header class="admin-updates__detail-heading">
                  <div>
                    <h3>Resultado del diagnóstico</h3>

                    <p>
                      Revise el alcance calculado antes de activar
                      la campaña.
                    </p>
                  </div>
                </header>

                <div
                  v-if="detailRows.length"
                  class="admin-updates__detail-grid"
                >
                  <article
                    v-for="row in detailRows"
                    :key="row.key"
                  >
                    <span>
                      {{ row.label }}
                    </span>

                    <strong>
                      {{ row.value }}
                    </strong>
                  </article>
                </div>

                <div
                  v-else
                  class="admin-updates__detail-empty"
                >
                  El diagnóstico no devolvió información resumible.
                </div>
              </section>
            </template>

          </div>
        </section>
      </div>

      <!-- =====================================================
           COMUNICACIÓN
      ====================================================== -->
      <div
        v-if="showCommForm"
        class="sgpc-modal-overlay admin-updates__overlay"
        @click.self="closeCommunication"
      >
        <form
          class="sgpc-modal-card admin-updates__modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="communication-form-title"
          @submit.prevent="saveCommunication"
        >
          <header class="admin-updates__modal-header">
            <div>
              <span>Comunicación global</span>

              <h2 id="communication-form-title">
                {{
                  commEditing
                    ? "Editar comunicación"
                    : "Nueva comunicación"
                }}
              </h2>
            </div>

            <button
              type="button"
              class="admin-updates__modal-close"
              aria-label="Cerrar"
              :disabled="commBusy"
              @click="closeCommunication"
            >
              ×
            </button>
          </header>

          <div class="admin-updates__modal-body">
            <section class="admin-updates__form-section">
              <label class="admin-updates__field">
                <span>Título</span>

                <input
                  v-model.trim="commForm.titulo"
                  required
                  maxlength="180"
                >
              </label>

              <label class="admin-updates__field">
                <span>Tipo</span>

                <select v-model="commForm.tipo">
                  <option value="informacion">
                    Información
                  </option>

                  <option value="actualizacion">
                    Actualización
                  </option>

                  <option value="importante">
                    Importante
                  </option>

                  <option value="mantenimiento">
                    Mantenimiento
                  </option>
                </select>
              </label>

              <label class="admin-updates__field">
                <span>Mensaje</span>

                <textarea
                  v-model.trim="commForm.mensaje"
                  rows="5"
                  required
                ></textarea>
              </label>

              <div class="admin-updates__grid">
                <label class="admin-updates__field">
                  <span>Texto del botón</span>

                  <input
                    v-model.trim="commForm.etiqueta_accion"
                    placeholder="Ejemplo: Completar información"
                  >
                </label>

                <label class="admin-updates__field">
                  <span>Ruta</span>

                  <input
                    v-model.trim="commForm.ruta_accion"
                    placeholder="/informacion-pendiente"
                  >
                </label>
              </div>

              <label class="admin-updates__check">
                <input
                  v-model="commForm.activa"
                  type="checkbox"
                >

                <span>
                  Comunicación activa
                </span>
              </label>
            </section>
          </div>

          <footer class="admin-updates__modal-footer">
            <button
              type="button"
              :disabled="commBusy"
              @click="closeCommunication"
            >
              Cancelar
            </button>

            <button
              type="submit"
              class="primary"
              :disabled="commBusy"
            >
              {{
                commBusy
                  ? (commEditing ? "Guardando cambios…" : "Creando comunicación…")
                  : (commEditing ? "Guardar cambios" : "Crear comunicación")
              }}
            </button>
          </footer>
        </form>
      </div>
    </Teleport>

    <!-- =======================================================
         CONFIRMACIÓN
    ======================================================== -->
    <SgpcConfirmDialog
      v-model="confirmDialog.open"
      :eyebrow="confirmDialog.eyebrow"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :confirm-label="confirmDialog.confirmLabel"
      :tone="confirmDialog.tone"
      :busy="confirmBusy"
      @confirm="acceptConfirmation"
    />
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

import SgpcConfirmDialog from "../../inicio/ui/SgpcConfirmDialog.vue";

import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";

import {
  useModalLayer,
} from "../../scripts/composables/useModalLayer";

import {
  getAdminCarreras,
  getAdminFacultades,
  getAdminSedes,
} from "../_shared/utils/adminCatalogCache";

import {
  activarCampania,
  actualizarCampania,
  actualizarComunicacion,
  apiErrorMessage,
  asResults,
  cancelarCampania,
  crearCampania,
  crearComunicacion,
  diagnosticarCampania,
  eliminarCampania,
  eliminarComunicacion,
  enviarRecordatorioCampania,
  finalizarCampania,
  listarCampanias,
  listarComunicaciones,
  listarParticipantesCampania,
  recalcularCampania,
} from "../../scripts/api/actualizacionesApi";


/* ============================================================
   ESTADO
============================================================ */

const tab = ref("campanias");

const campaigns = ref([]);
const communications = ref([]);

const loading = ref(false);
const visibleLoadFeedback = ref(false);
const loadedOnce = ref(false);

const error = ref("");
const successMessage = ref("");

const showCampaignForm = ref(false);
const editingId = ref(null);

const scopeId = ref("");
const userIds = ref("");

const detail = ref(null);

const showCommForm = ref(false);
const commEditing = ref(null);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);

const formBusy = ref(false);
const commBusy = ref(false);
const confirmBusy = ref(false);

const workingKey = ref("");
let loadFeedbackTimer = null;

const campaignValidationError = ref(false);

const hasLoadedData = computed(() => (
  Boolean(campaigns.value.length || communications.value.length)
));

const initialLoading = computed(() => (
  loading.value &&
  visibleLoadFeedback.value &&
  !loadedOnce.value
));

const refreshing = computed(() => (
  loading.value &&
  visibleLoadFeedback.value &&
  loadedOnce.value
));


/* ============================================================
   CONFIRMACIÓN
============================================================ */

const confirmDialog = reactive({
  open: false,
  eyebrow: "Administración",
  title: "Confirmar acción",
  message: "",
  confirmLabel: "Confirmar",
  tone: "primary",
  action: null,
});


/* ============================================================
   FORMULARIOS
============================================================ */

function emptyCampaign() {
  return {
    titulo: "",
    descripcion: "",
    tipo: "perfil",
    alcance: "todos",
    fecha_inicio: "",
    fecha_fin: "",
    solo_incompletos: true,
    campos_habilitados: [],
    crear_aviso: true,
    notificar_internamente: true,
    enviar_correo: false,
  };
}


const form = reactive(
  emptyCampaign()
);


const commForm = reactive({
  titulo: "",
  mensaje: "",
  tipo: "informacion",
  etiqueta_accion: "",
  ruta_accion: "",
  activa: true,
});


/* ============================================================
   CATÁLOGOS
============================================================ */

const fieldMap = {
  perfil: [
    "identificacion",
    "sede",
    "carrera",
  ],

  publicacion: [
    "sede",
    "carrera",
    "area",
    "subarea",
    "pais",
    "ciudad",
    "proyecto",
  ],

  proyecto: [
    "sede",
    "carrera",
    "descripcion",
    "fecha_inicio",
    "fecha_fin_planificada",
    "fecha_fin_prorrogada",
  ],
};


const fieldLabels = {
  identificacion: "Cédula",
  sede: "Sede",
  carrera: "Carrera",

  area: "Área UNESCO",
  subarea: "Subárea UNESCO",

  pais: "País",
  ciudad: "Ciudad",

  proyecto: "Proyecto",

  descripcion: "Descripción",

  fecha_inicio: "Fecha de inicio",

  fecha_fin_planificada:
    "Fecha de finalización planificada",

  fecha_fin_prorrogada:
    "Fecha de finalización prorrogada",
};


const fieldsForType = computed(() => (
  fieldMap[form.tipo] || []
));


const scopeOptions = computed(() => {
  if (form.alcance === "sede") {
    return sedes.value;
  }

  if (form.alcance === "facultad") {
    return facultades.value;
  }

  if (form.alcance === "carrera") {
    return carreras.value;
  }

  return [];
});


const scopeFieldLabel = computed(() => {
  const labels = {
    sede: "Sede",
    facultad: "Facultad",
    carrera: "Carrera",
  };

  return labels[form.alcance] || "Filtro";
});


/* ============================================================
   MODALES
============================================================ */

const modalOpen = computed(() => (
  Boolean(
    showCampaignForm.value ||
    detail.value ||
    showCommForm.value
  )
));


useModalLayer(
  modalOpen
);


/* ============================================================
   DETALLE
============================================================ */

const participantRows = computed(() => {
  if (
    !detail.value ||
    detail.value.kind !== "participants"
  ) {
    return [];
  }

  const items =
    extractParticipantList(
      detail.value.data
    );

  return items.map(
    (item, index) => {
      const state =
        item.estado ||
        item.status ||
        "pendiente";

      return {
        key:
          item.id ||
          item.usuario_id ||
          index,

        name:
          item.usuario_nombre ||
          item.nombre ||
          item.nombre_completo ||
          item.full_name ||
          item.email ||
          `Participante #${item.id || index + 1}`,

        email:
          item.usuario_email ||
          item.email ||
          "",

        state,

        stateLabel:
          participantStateLabel(state),

        pending:
          participantPending(item),
      };
    }
  );
});


const detailRows = computed(() => {
  if (
    !detail.value ||
    detail.value.kind !== "diagnostic"
  ) {
    return [];
  }

  return flattenDetail(
    detail.value.data
  );
});




/* ============================================================
   ETIQUETAS
============================================================ */

function fieldLabel(value) {
  return (
    fieldLabels[value] ||
    humanize(value)
  );
}


function typeLabel(value) {
  const values = {
    perfil: "Perfil",
    publicacion: "Publicaciones",
    proyecto: "Proyectos",
  };

  return (
    values[value] ||
    humanize(value)
  );
}


function stateLabel(value) {
  const values = {
    borrador: "Borrador",
    activa: "Activa",
    finalizada: "Finalizada",
    cancelada: "Cancelada",
  };

  return (
    values[value] ||
    humanize(value)
  );
}


function participantStateLabel(value) {
  const values = {
    pendiente: "Pendiente",
    en_progreso: "En progreso",
    completada: "Completada",
    cancelada: "Cancelada",
  };

  return (
    values[value] ||
    humanize(value)
  );
}


function commType(value) {
  const values = {
    informacion: "Información",
    actualizacion: "Actualización",
    importante: "Importante",
    mantenimiento: "Mantenimiento",
  };

  return (
    values[value] ||
    humanize(value)
  );
}


function humanize(value) {
  if (!value) {
    return "";
  }

  const text =
    String(value)
      .replace(/_/g, " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2")
      .trim();

  return (
    text.charAt(0).toUpperCase() +
    text.slice(1)
  );
}


/* ============================================================
   CAMPAÑAS
============================================================ */

function campaignPeriod(campaign) {
  const start =
    formatDate(campaign.fecha_inicio);

  const end =
    formatDate(campaign.fecha_fin);

  if (
    start !== "Sin fecha" &&
    end !== "Sin fecha"
  ) {
    return `${start} – ${end}`;
  }

  if (start !== "Sin fecha") {
    return `Desde ${start}`;
  }

  if (end !== "Sin fecha") {
    return `Hasta ${end}`;
  }

  return "Sin periodo definido";
}


function formatDate(value) {
  if (!value) {
    return "Sin fecha";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
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
  ).format(date);
}


function scopeLabel(campaign) {
  const scope =
    campaign.alcance ||
    "todos";

  if (scope === "todos") {
    return "Todos";
  }

  if (scope === "usuarios") {
    const total =
      campaign.filtros_destinatarios
        ?.usuarios?.length || 0;

    return (
      total
        ? `${total} usuarios específicos`
        : "Usuarios específicos"
    );
  }

  const filters =
    campaign.filtros_destinatarios ||
    {};

  let id = null;
  let catalog = [];

  if (scope === "sede") {
    id = filters.sede_id;
    catalog = sedes.value;
  }

  if (scope === "facultad") {
    id = filters.facultad_id;
    catalog = facultades.value;
  }

  if (scope === "carrera") {
    id = filters.carrera_id;
    catalog = carreras.value;
  }

  const found =
    catalog.find(
      (item) =>
        String(item.id) === String(id)
    );

  if (found) {
    return (
      found.nombre ||
      found.label ||
      humanize(scope)
    );
  }

  return humanize(scope);
}


/* ============================================================
   RESPUESTAS API
============================================================ */

function list(payload) {
  const results =
    asResults(payload);

  if (results.length) {
    return results;
  }

  return Array.isArray(payload)
    ? payload
    : [];
}


/* ============================================================
   CARGA
============================================================ */

async function loadCampaigns() {
  const campaignData =
    await listarCampanias();

  campaigns.value =
    list(campaignData);

  return campaigns.value;
}


async function loadCommunications() {
  const communicationData =
    await listarComunicaciones();

  communications.value =
    list(communicationData);

  return communications.value;
}


async function loadCatalogs() {
  const [
    sedeData,
    facultadData,
    carreraData,
  ] = await Promise.all([
    getAdminSedes(),
    getAdminFacultades(),
    getAdminCarreras(),
  ]);

  sedes.value =
    list(sedeData);

  facultades.value =
    list(facultadData);

  carreras.value =
    list(carreraData);
}


async function load() {
  loading.value = true;
  error.value = "";
  visibleLoadFeedback.value = false;

  window.clearTimeout(loadFeedbackTimer);
  loadFeedbackTimer = window.setTimeout(() => {
    if (loading.value) {
      visibleLoadFeedback.value = true;
    }
  }, 220);

  try {
    await Promise.all([
      loadCampaigns(),
      loadCommunications(),
      loadCatalogs(),
    ]);
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible cargar la información."
      );
  } finally {
    window.clearTimeout(loadFeedbackTimer);
    loadFeedbackTimer = null;
    visibleLoadFeedback.value = false;
    loadedOnce.value = true;
    loading.value = false;
  }
}


/* ============================================================
   FORMULARIO CAMPAÑA
============================================================ */

function openNew() {
  successMessage.value = "";

  Object.assign(
    form,
    emptyCampaign()
  );

  editingId.value = null;

  scopeId.value = "";
  userIds.value = "";

  campaignValidationError.value =
    false;

  showCampaignForm.value =
    true;
}


function edit(campaign) {
  successMessage.value = "";

  Object.assign(
    form,
    {
      titulo:
        campaign.titulo || "",

      descripcion:
        campaign.descripcion || "",

      tipo:
        campaign.tipo || "perfil",

      alcance:
        campaign.alcance || "todos",

      fecha_inicio:
        datetimeLocal(
          campaign.fecha_inicio
        ),

      fecha_fin:
        datetimeLocal(
          campaign.fecha_fin
        ),

      solo_incompletos:
        campaign.solo_incompletos ??
        true,

      campos_habilitados: [
        ...(
          campaign.campos_habilitados ||
          []
        ),
      ],

      crear_aviso:
        campaign.crear_aviso ??
        true,

      notificar_internamente:
        campaign.notificar_internamente ??
        true,

      enviar_correo:
        campaign.enviar_correo ??
        false,
    }
  );

  editingId.value =
    campaign.id;

  const filters =
    campaign.filtros_destinatarios ||
    {};

  scopeId.value =
    String(
      filters.sede_id ||
      filters.facultad_id ||
      filters.carrera_id ||
      ""
    );

  userIds.value =
    (
      filters.usuarios ||
      []
    ).join(", ");

  campaignValidationError.value =
    false;

  showCampaignForm.value =
    true;
}


function closeForm() {
  if (formBusy.value) {
    return;
  }

  showCampaignForm.value =
    false;

  campaignValidationError.value =
    false;
}


function onTypeChange() {
  form.campos_habilitados = [];
}


function onScopeChange() {
  scopeId.value = "";
  userIds.value = "";
}


function datetimeLocal(value) {
  return value
    ? String(value).slice(0, 16)
    : "";
}


/* ============================================================
   VALIDACIÓN CAMPAÑA
============================================================ */

function validateCampaign() {
  campaignValidationError.value =
    true;

  if (!form.titulo.trim()) {
    throw new Error(
      "Ingrese el título de la campaña."
    );
  }

  if (!form.campos_habilitados.length) {
    throw new Error(
      "Seleccione al menos un campo habilitado."
    );
  }

  if (
    ["sede", "facultad", "carrera"]
      .includes(form.alcance) &&
    !scopeId.value
  ) {
    throw new Error(
      `Seleccione ${scopeFieldLabel.value.toLowerCase()}.`
    );
  }

  if (
    form.alcance === "usuarios" &&
    !parsedUserIds().length
  ) {
    throw new Error(
      "Ingrese al menos un usuario válido."
    );
  }

  if (
    form.fecha_inicio &&
    form.fecha_fin &&
    new Date(form.fecha_fin) <=
      new Date(form.fecha_inicio)
  ) {
    throw new Error(
      "La fecha de finalización debe ser posterior a la fecha de inicio."
    );
  }
}


function parsedUserIds() {
  return userIds.value
    .split(",")
    .map(
      (value) =>
        Number(value.trim())
    )
    .filter(
      (value) =>
        Number.isInteger(value) &&
        value > 0
    );
}


/* ============================================================
   PAYLOAD CAMPAÑA
============================================================ */

function campaignPayload() {
  const filters = {};

  if (form.alcance === "sede") {
    filters.sede_id =
      Number(scopeId.value);
  }

  if (form.alcance === "facultad") {
    filters.facultad_id =
      Number(scopeId.value);
  }

  if (form.alcance === "carrera") {
    filters.carrera_id =
      Number(scopeId.value);
  }

  if (form.alcance === "usuarios") {
    filters.usuarios =
      parsedUserIds();
  }

  return {
    titulo:
      form.titulo.trim(),

    descripcion:
      form.descripcion.trim(),

    tipo:
      form.tipo,

    alcance:
      form.alcance,

    fecha_inicio:
      form.fecha_inicio ||
      null,

    fecha_fin:
      form.fecha_fin ||
      null,

    solo_incompletos:
      Boolean(
        form.solo_incompletos
      ),

    campos_habilitados: [
      ...form.campos_habilitados,
    ],

    crear_aviso:
      Boolean(form.crear_aviso),

    notificar_internamente:
      Boolean(
        form.notificar_internamente
      ),

    enviar_correo:
      Boolean(form.enviar_correo),

    filtros_destinatarios:
      filters,
  };
}


/* ============================================================
   GUARDAR CAMPAÑA
============================================================ */

async function saveCampaign() {
  if (formBusy.value) {
    return;
  }

  formBusy.value = true;

  error.value = "";
  successMessage.value = "";

  const wasEditing = Boolean(editingId.value);

  try {
    validateCampaign();

    const payload =
      campaignPayload();

    if (editingId.value) {
      await actualizarCampania(
        editingId.value,
        payload
      );
    } else {
      await crearCampania(
        payload
      );
    }

    showCampaignForm.value =
      false;

    successMessage.value = wasEditing
      ? "Los cambios de la campaña se guardaron correctamente."
      : "La campaña se creó correctamente.";

    try {
      await loadCampaigns();
    } catch (refreshError) {
      console.warn(
        "La campaña se guardó, pero no se pudo actualizar el listado:",
        refreshError
      );

      error.value =
        "La campaña se guardó correctamente, pero el listado no pudo sincronizarse. Use Actualizar para volver a cargarlo.";
    }
  } catch (err) {
    error.value =
      err instanceof Error &&
      !err.response
        ? err.message
        : apiErrorMessage(
            err,
            "No fue posible guardar la campaña."
          );
  } finally {
    formBusy.value = false;
  }
}


/* ============================================================
   ACCIONES
============================================================ */

function workKey(
  campaign,
  action
) {
  return `${action}:${campaign.id}`;
}


function isWorking(
  campaign,
  action
) {
  return (
    workingKey.value ===
    workKey(campaign, action)
  );
}

function isCampaignBusy(campaign) {
  if (!campaign?.id) {
    return false;
  }

  return Boolean(workingKey.value);
}

function campaignActionSuccess(action, campaign) {
  const title = campaign?.titulo || "La campaña";

  const messages = {
    activate: `“${title}” quedó activa.`,
    finish: `“${title}” se finalizó correctamente.`,
    cancel: `“${title}” fue cancelada.`,
    reminder: `Se envió el recordatorio de “${title}”.`,
    recalculate: `Se recalcularon los pendientes de “${title}”.`,
    delete: `“${title}” fue eliminada.`,
  };

  return messages[action] || "La operación se completó correctamente.";
}


async function runCampaignAction(
  fn,
  campaign,
  action
) {
  workingKey.value =
    workKey(campaign, action);

  error.value = "";
  successMessage.value = "";

  try {
    await fn(campaign.id);

    successMessage.value =
      campaignActionSuccess(action, campaign);

    try {
      await loadCampaigns();
    } catch (refreshError) {
      console.warn(
        "La acción se completó, pero no se pudo actualizar la lista de campañas:",
        refreshError
      );

      error.value =
        "La operación se completó correctamente, pero la lista de campañas no pudo sincronizarse. Use Actualizar para volver a cargarla.";
    }

    return true;
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible completar la acción."
      );

    return false;
  } finally {
    workingKey.value = "";
  }
}


async function recalc(campaign) {
  await runCampaignAction(
    recalcularCampania,
    campaign,
    "recalculate"
  );
}


/* ============================================================
   CONFIRMACIONES
============================================================ */

function askConfirmation({
  eyebrow = "Administración",
  title,
  message,
  confirmLabel = "Confirmar",
  tone = "primary",
  action,
}) {
  Object.assign(
    confirmDialog,
    {
      open: true,
      eyebrow,
      title,
      message,
      confirmLabel,
      tone,
      action,
    }
  );
}


async function acceptConfirmation() {
  const action =
    confirmDialog.action;

  if (
    !action ||
    confirmBusy.value
  ) {
    return;
  }

  confirmBusy.value = true;

  try {
    const success =
      await action();

    if (success !== false) {
      confirmDialog.open =
        false;

      confirmDialog.action =
        null;
    }
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible completar la acción."
      );
  } finally {
    confirmBusy.value = false;
  }
}


async function requestActivate(campaign) {
  workingKey.value =
    workKey(
      campaign,
      "diagnostic"
    );

  error.value = "";
  successMessage.value = "";

  try {
    const diagnostic =
      await diagnosticarCampania(
        campaign.id
      );

    const affected = Number(
      diagnostic?.afectados_estimados ?? 0
    );

    const candidates = Number(
      diagnostic?.candidatos ?? 0
    );

    const pending = Number(
      diagnostic?.con_pendientes ?? 0
    );

    if (affected <= 0) {
      detail.value = {
        kind: "diagnostic",
        title: campaign.titulo,
        data: diagnostic,
      };

      error.value =
        "La campaña no puede activarse porque el diagnóstico no encontró usuarios que requieran completar los campos seleccionados.";

      return;
    }

    askConfirmation({
      eyebrow: "Diagnóstico completado",
      title: "Activar campaña",

      message:
        `Se evaluaron ${candidates} usuarios. ${pending} tienen información pendiente y ${affected} quedarán afectados por la campaña "${campaign.titulo}". ¿Desea activarla?`,

      confirmLabel:
        "Activar",

      action: () =>
        runCampaignAction(
          activarCampania,
          campaign,
          "activate"
        ),
    });
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible generar el diagnóstico previo a la activación."
      );
  } finally {
    workingKey.value = "";
  }
}


function requestFinish(campaign) {
  askConfirmation({
    title: "Finalizar campaña",

    message:
      `La campaña "${campaign.titulo}" se cerrará y los usuarios ya no podrán realizar nuevas actualizaciones mediante ella.`,

    confirmLabel:
      "Finalizar",

    action: () =>
      runCampaignAction(
        finalizarCampania,
        campaign,
        "finish"
      ),
  });
}


function requestCancel(campaign) {
  askConfirmation({
    title: "Cancelar campaña",

    message:
      `La campaña "${campaign.titulo}" será cancelada. Los participantes dejarán de tener acceso al proceso de actualización.`,

    confirmLabel:
      "Cancelar campaña",

    tone:
      "danger",

    action: () =>
      runCampaignAction(
        cancelarCampania,
        campaign,
        "cancel"
      ),
  });
}


function requestReminder(campaign) {
  askConfirmation({
    title: "Enviar recordatorio",

    message:
      `Se enviará un recordatorio a los participantes pendientes de la campaña "${campaign.titulo}".`,

    confirmLabel:
      "Enviar",

    action: () =>
      runCampaignAction(
        enviarRecordatorioCampania,
        campaign,
        "reminder"
      ),
  });
}


function remove(campaign) {
  askConfirmation({
    title:
      "Eliminar campaña",

    message:
      `La campaña "${campaign.titulo}" será eliminada definitivamente mientras permanezca en borrador.`,

    confirmLabel:
      "Eliminar",

    tone:
      "danger",

    action: () =>
      runCampaignAction(
        eliminarCampania,
        campaign,
        "delete"
      ),
  });
}


/* ============================================================
   DIAGNÓSTICO
============================================================ */

async function diagnose(campaign) {
  workingKey.value =
    workKey(
      campaign,
      "diagnostic"
    );

  error.value = "";
  successMessage.value = "";

  try {
    const data =
      await diagnosticarCampania(
        campaign.id
      );

    detail.value = {
      kind:
        "diagnostic",

      title:
        campaign.titulo,

      data,
    };
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible generar el diagnóstico."
      );
  } finally {
    workingKey.value = "";
  }
}


/* ============================================================
   PARTICIPANTES
============================================================ */

async function showParticipants(
  campaign
) {
  workingKey.value =
    workKey(
      campaign,
      "participants"
    );

  error.value = "";
  successMessage.value = "";

  try {
    const data =
      await listarParticipantesCampania(
        campaign.id
      );

    detail.value = {
      kind:
        "participants",

      title:
        campaign.titulo,

      data,
    };
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible cargar los participantes."
      );
  } finally {
    workingKey.value = "";
  }
}


function closeDetail() {
  detail.value = null;
}


/* ============================================================
   PARTICIPANTES · NORMALIZACIÓN
============================================================ */

function extractParticipantList(
  payload
) {
  if (Array.isArray(payload)) {
    return payload;
  }

  const candidates = [
    payload?.results,
    payload?.participantes,
    payload?.participants,
    payload?.data,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate)) {
      return candidate;
    }
  }

  return [];
}


function participantPending(item) {
  if (
    Array.isArray(
      item.campos_pendientes
    )
  ) {
    return (
      item.campos_pendientes.length
    );
  }

  if (
    typeof item.pendientes ===
    "number"
  ) {
    return item.pendientes;
  }

  return null;
}


/* ============================================================
   DIAGNÓSTICO · HUMANIZACIÓN
============================================================ */

function flattenDetail(
  value,
  prefix = "",
  rows = [],
  depth = 0
) {
  if (depth > 4) {
    return rows;
  }

  if (
    value === null ||
    value === undefined
  ) {
    if (prefix) {
      rows.push({
        key: prefix,
        label:
          detailLabel(prefix),
        value:
          "Sin información",
      });
    }

    return rows;
  }

  if (Array.isArray(value)) {
    if (!prefix) {
      return rows;
    }

    if (
      value.every(
        (item) =>
          item === null ||
          ["string", "number", "boolean"]
            .includes(typeof item)
      )
    ) {
      rows.push({
        key: prefix,
        label:
          detailLabel(prefix),

        value:
          value.length
            ? value
                .map(formatDetailValue)
                .join(", ")
            : "Sin registros",
      });
    } else {
      rows.push({
        key: prefix,
        label:
          detailLabel(prefix),

        value:
          `${value.length} ${
            value.length === 1
              ? "registro"
              : "registros"
          }`,
      });
    }

    return rows;
  }

  if (
    typeof value === "object"
  ) {
    Object.entries(value)
      .forEach(
        ([key, child]) => {
          const path =
            prefix
              ? `${prefix}.${key}`
              : key;

          flattenDetail(
            child,
            path,
            rows,
            depth + 1
          );
        }
      );

    return rows;
  }

  rows.push({
    key: prefix,
    label:
      detailLabel(prefix),

    value:
      formatDetailValue(value),
  });

  return rows;
}


function detailLabel(path) {
  const key =
    String(path)
      .split(".")
      .at(-1);

  const labels = {
    total: "Total",
    afectados: "Afectados",
    elegibles: "Elegibles",
    participantes: "Participantes",

    pendientes: "Pendientes",
    completadas: "Completados",
    en_progreso: "En progreso",

    usuarios: "Usuarios",
    publicaciones: "Publicaciones",
    proyectos: "Proyectos",

    con_datos_incompletos:
      "Con información incompleta",

    sin_datos:
      "Sin información",

    campos:
      "Campos",

    registros:
      "Registros",
  };

  return (
    labels[key] ||
    humanize(key)
  );
}


function formatDetailValue(value) {
  if (value === true) {
    return "Sí";
  }

  if (value === false) {
    return "No";
  }

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Sin información";
  }

  return String(value);
}


/* ============================================================
   COMUNICACIONES
============================================================ */

function openCommunication() {
  successMessage.value = "";
  commEditing.value = null;

  Object.assign(
    commForm,
    {
      titulo: "",
      mensaje: "",
      tipo: "informacion",
      etiqueta_accion: "",
      ruta_accion: "",
      activa: true,
    }
  );

  showCommForm.value =
    true;
}


function editCommunication(
  communication
) {
  commEditing.value =
    communication.id;

  Object.assign(
    commForm,
    {
      titulo:
        communication.titulo ||
        "",

      mensaje:
        communication.mensaje ||
        "",

      tipo:
        communication.tipo ||
        "informacion",

      etiqueta_accion:
        communication.etiqueta_accion ||
        "",

      ruta_accion:
        communication.ruta_accion ||
        "",

      activa:
        Boolean(
          communication.activa
        ),
    }
  );

  showCommForm.value =
    true;
}


function closeCommunication() {
  if (commBusy.value) {
    return;
  }

  showCommForm.value =
    false;
}


/* ============================================================
   GUARDAR COMUNICACIÓN
============================================================ */

async function saveCommunication() {
  if (commBusy.value) {
    return;
  }

  commBusy.value = true;

  error.value = "";
  successMessage.value = "";

  const wasEditing = Boolean(commEditing.value);

  try {
    const payload = {
      titulo:
        commForm.titulo.trim(),

      mensaje:
        commForm.mensaje.trim(),

      tipo:
        commForm.tipo,

      etiqueta_accion:
        commForm.etiqueta_accion.trim(),

      ruta_accion:
        commForm.ruta_accion.trim(),

      activa:
        Boolean(
          commForm.activa
        ),
    };

    if (commEditing.value) {
      await actualizarComunicacion(
        commEditing.value,
        payload
      );
    } else {
      await crearComunicacion(
        payload
      );
    }

    showCommForm.value =
      false;

    successMessage.value = wasEditing
      ? "Los cambios de la comunicación se guardaron correctamente."
      : "La comunicación se creó correctamente.";

    try {
      await loadCommunications();
    } catch (refreshError) {
      console.warn(
        "La comunicación se guardó, pero no se pudo actualizar el listado:",
        refreshError
      );

      error.value =
        "La comunicación se guardó correctamente, pero el listado no pudo sincronizarse. Use Actualizar para volver a cargarlo.";
    }
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible guardar la comunicación."
      );
  } finally {
    commBusy.value = false;
  }
}


/* ============================================================
   ELIMINAR COMUNICACIÓN
============================================================ */

function removeCommunication(
  communication
) {
  askConfirmation({
    title:
      "Eliminar comunicación",

    message:
      `La comunicación "${communication.titulo}" dejará de estar disponible y será eliminada.`,

    confirmLabel:
      "Eliminar",

    tone:
      "danger",

    action:
      async () => {
        try {
          successMessage.value = "";

          await eliminarComunicacion(
            communication.id
          );

          communications.value =
            communications.value.filter(
              (item) =>
                Number(item?.id) !==
                Number(communication.id)
            );

          successMessage.value =
            "La comunicación se eliminó correctamente.";

          return true;
        } catch (err) {
          error.value =
            apiErrorMessage(
              err,
              "No fue posible eliminar la comunicación."
            );

          return false;
        }
      },
  });
}


/* ============================================================
   INICIO
============================================================ */

onMounted(
  load
);

onBeforeUnmount(() => {
  window.clearTimeout(loadFeedbackTimer);
});
</script>

<style src="./admin-actualizaciones.css"></style>
<style src="./admin-actualizaciones-stage6.css"></style>