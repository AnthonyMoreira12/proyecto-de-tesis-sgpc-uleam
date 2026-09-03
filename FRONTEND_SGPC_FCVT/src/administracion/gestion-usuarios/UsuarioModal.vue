<template>
  <Teleport
    to="body"
    :disabled="embedded"
  >
    <div
      :class="
        embedded
          ? 'usermodal-embedded'
          : 'sgpc-admin-modal modal-overlay'
      "
      @click.self="handleBackdropClick"
    >
      <div
        :class="[
          'modal',
          'modal--user',
          {
            'modal--user-embedded': embedded,
          },
        ]"
        :role="embedded ? 'region' : 'dialog'"
        :aria-modal="embedded ? undefined : 'true'"
        :aria-label="
          embedded
            ? 'Editar usuario'
            : mode === 'create'
              ? 'Registrar usuario externo'
              : 'Editar usuario'
        "
      >
      <header
        v-if="!embedded"
        class="modal__header usermodal-header"
      >
        <div class="usermodal-titlewrap">
          <div class="usermodal-titleline">
            <h2 class="modal__title usermodal-title">
              {{ mode === "create" ? "Registrar usuario externo" : "Editar usuario" }}
            </h2>

            <div class="usermodal-badges" aria-label="Tipo y estado">
              <span class="usermodal-badge usermodal-badge--neutral">
                {{ tipoUsuarioLabel }}
              </span>

              <span class="usermodal-badge" :class="estadoBadgeClass">
                {{ estadoLabel }}
              </span>
            </div>
          </div>

          <p
            v-if="mode === 'create'"
            class="modal__subtitle usermodal-subtitle"
          >
            Complete los datos necesarios para registrar la cuenta.
          </p>
        </div>

        <button
          type="button"
          class="btn-cerrar modal__close usermodal-close"
          :disabled="saving || actionBusy"
          @click="emit('close')"
          aria-label="Cerrar"
          title="Cerrar"
        >
          ✕
        </button>
      </header>

      <form class="usermodal-form" @submit.prevent="submit">
        <div class="usermodal-scroll">
          <div
            v-if="embedded && mode === 'edit'"
            class="usermodal-account-summary"
            aria-label="Tipo y estado de la cuenta"
          >
            <span>{{ tipoUsuarioLabel }}</span>

            <span
              class="usermodal-account-summary__separator"
              aria-hidden="true"
            >
              ·
            </span>

            <strong
              :class="[
                'usermodal-account-summary__state',
                estadoBadgeClass,
              ]"
            >
              {{ estadoLabel }}
            </strong>
          </div>

          <section class="usermodal-section" aria-label="Datos personales">
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Datos personales</h3>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Nombres</label>

                <input
                  v-model="form.nombres"
                  class="field-control usermodal-input"
                  required
                  placeholder="Ej.: Andrea Sofía"
                  autocomplete="given-name"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Apellidos</label>

                <input
                  v-model="form.apellidos"
                  class="field-control usermodal-input"
                  required
                  placeholder="Ej.: García López"
                  autocomplete="family-name"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Correo electrónico</label>

                <input
                  v-model="form.email"
                  class="field-control usermodal-input"
                  required
                  type="email"
                  placeholder="Ej.: usuario@correo.com"
                  :disabled="emailLocked"
                  :class="{
                    'input-readonly': emailLocked,
                    'usermodal-input--invalid': institutionalEmailOnCreate
                  }"
                  :aria-invalid="institutionalEmailOnCreate ? 'true' : undefined"
                  autocomplete="email"
                  inputmode="email"
                />

                <p
                  v-if="institutionalEmailOnCreate"
                  class="usermodal-help usermodal-help--danger"
                  role="alert"
                  aria-live="polite"
                >
                  Este correo pertenece a una cuenta institucional ULEAM.
                  Debe ingresar mediante Microsoft 365 y no debe registrarse
                  como usuario externo.
                </p>

                <p v-else-if="emailLocked" class="usermodal-help">
                  Cuenta institucional: el correo no se modifica desde este panel.
                </p>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label usermodal-label--with-help">
                  <span>Identificación</span>

                  <InfoTip title="Identificación">
                    Dato único para evitar duplicados. Debe tener 10 dígitos numéricos.
                  </InfoTip>
                </label>

                <input
                  v-model="form.identificacion"
                  class="field-control usermodal-input"
                  :required="mode === 'create'"
                  placeholder="Ej.: 1312345678"
                  autocomplete="off"
                  inputmode="numeric"
                />

                <p class="usermodal-help">
                  Solo números, sin espacios ni guiones.
                </p>
              </div>
            </div>
          </section>

          <section
            v-if="showAcademicoSection"
            class="usermodal-section"
            aria-label="Asignación académica"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Información académica</h3>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Facultad</label>

                <select
                  v-model="form.facultad"
                  class="field-control usermodal-input"
                  :disabled="saving || loadingCatalogos"
                  required
                  @change="onFacultadChange"
                >
                  <option value="">Seleccione una facultad</option>

                  <option
                    v-for="f in facultades"
                    :key="f.value"
                    :value="f.value"
                  >
                    {{ f.label }}
                  </option>
                </select>

                <p v-if="loadingCatalogos" class="usermodal-help">
                  Cargando facultades...
                </p>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Carrera</label>

                <select
                  v-model="form.carrera"
                  class="field-control usermodal-input"
                  :disabled="saving || loadingCatalogos || !form.facultad"
                  required
                >
                  <option value="">Seleccione una carrera</option>

                  <option
                    v-for="c in carreras"
                    :key="c.value"
                    :value="c.value"
                  >
                    {{ c.label }}
                  </option>
                </select>

                <p v-if="form.facultad && loadingCarreras" class="usermodal-help">
                  Cargando carreras...
                </p>
              </div>
            </div>

            <p v-if="isInstitucional" class="usermodal-note usermodal-note--info">
              El acceso institucional continúa gestionado por Microsoft 365.
            </p>
          </section>

          <section
            v-if="mode === 'edit'"
            ref="profileControlSectionRef"
            class="usermodal-section"
            :class="{ 'is-request-focus': focusProfileEdit }"
            aria-label="Control de edición del perfil"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Permiso para editar el perfil</h3>
              </div>

              <InfoTip title="Control de edición">
                Habilitar desbloquea y reinicia intentos. Extender suma horas al plazo. Bloquear impide editar el perfil.
              </InfoTip>
            </div>

            <div
              v-if="
                !isExtensionRequestContext &&
                extensionRequestLoadErrorState
              "
              class="usermodal-note usermodal-note--warn"
              role="alert"
            >
              <strong>No se pudo verificar el estado de solicitudes.</strong>
              <span>
                Los controles manuales del permiso permanecen bloqueados hasta
                que el sistema pueda confirmar que no existe una solicitud pendiente.
              </span>
            </div>

            <div
              v-if="extensionRequestUnavailable"
              class="usermodal-note usermodal-note--warn"
              role="alert"
            >
              <strong>No se pudo cargar la solicitud pendiente.</strong>
              <span>
                {{
                  extensionRequestLoadErrorState ||
                  "No fue posible recuperar el detalle de la solicitud. Las acciones manuales de edición están bloqueadas para evitar resolverla por una vía incorrecta."
                }}
              </span>

              <button
                v-if="extensionRequestId"
                type="button"
                class="usermodal-action-btn usermodal-action-btn--soft"
                :disabled="saving || actionBusy || extensionRequestLoading"
                @click="retryExtensionRequestLoad"
              >
                {{ extensionRequestLoading ? "Reintentando..." : "Reintentar carga" }}
              </button>
            </div>

            <div
              v-if="
                !isExtensionRequestContext &&
                hasPendingExtensionRequest
              "
              class="usermodal-note usermodal-note--warn"
              role="status"
            >
              <strong>Solicitud de edición pendiente.</strong>
              <span>
                Este usuario tiene una solicitud por revisar. Los controles
                manuales del permiso están deshabilitados para evitar que la
                solicitud quede abierta por error.
              </span>

              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--soft"
                :disabled="saving || actionBusy"
                @click="emit('open-extension-request', extensionRequestState)"
              >
                Ir a la solicitud
              </button>
            </div>

            <div
              v-if="isExtensionRequestContext && extensionRequestState"
              class="usermodal-request-context"
              :data-state="extensionRequestState.estado || 'pendiente'"
            >
              <div class="usermodal-request-context__head">
                <div>
                  <span>Solicitud de extensión</span>
                  <strong>Petición enviada por el usuario</strong>
                </div>

                <span class="usermodal-request-context__status">
                  {{ extensionRequestState.estado_label || extensionRequestState.estado || "Pendiente" }}
                </span>
              </div>

              <div class="usermodal-request-context__facts">
                <span>
                  Solicitado:
                  <strong>{{ extensionRequestState.horas_solicitadas || "—" }} horas</strong>
                </span>

                <span v-if="extensionRequestState.solicitada_at">
                  Fecha:
                  <strong>{{ formatRequestDate(extensionRequestState.solicitada_at) }}</strong>
                </span>
              </div>

              <div class="usermodal-request-context__reason">
                <span>Comentario del usuario</span>
                <p>
                  {{ extensionRequestState.motivo || "Sin comentario registrado." }}
                </p>
              </div>

              <p
                v-if="extensionRequestResolved"
                class="usermodal-note usermodal-note--info"
              >
                Esta solicitud ya fue resuelta. Para realizar una extensión manual, cierre esta ventana y abra nuevamente el usuario desde el listado general.
              </p>

              <div
                v-if="hasPendingExtensionRequest"
                class="usermodal-request-resolution"
              >
                <label class="usermodal-field">
                  <span class="usermodal-label">Motivo del rechazo</span>
                  <textarea
                    v-model="extensionResolutionReason"
                    class="field-control usermodal-input usermodal-textarea"
                    rows="3"
                    maxlength="1000"
                    :disabled="saving || actionBusy"
                    placeholder="Solo es necesario si decide rechazar la solicitud."
                  ></textarea>
                </label>

                <button
                  type="button"
                  class="usermodal-action-btn usermodal-action-btn--danger"
                  :disabled="saving || actionBusy"
                  @click="handleRejectExtensionRequest"
                >
                  {{ actionBusy ? "Procesando..." : "Rechazar solicitud" }}
                </button>
              </div>
            </div>

            <div class="usermodal-status-grid">
              <div class="usermodal-status">
                <span>Estado</span>
                <strong>{{ uiProfileLockedLabel }}</strong>
              </div>

              <div class="usermodal-status">
                <span>Puede editar hasta</span>
                <strong>{{ uiProfileUntilLabel }}</strong>
              </div>
            </div>

            <div class="usermodal-control-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Tiempo adicional</label>

                <div class="extend-row">
                  <select
                    ref="extendHoursSelectRef"
                    v-model="extendHours"
                    class="field-control usermodal-input"
                    :disabled="saving || actionBusy || extensionDecisionDisabled"
                  >
                    <option :value="6">6 horas</option>
                    <option :value="12">12 horas</option>
                    <option :value="24">24 horas</option>
                    <option :value="48">48 horas</option>
                    <option :value="72">72 horas</option>
                  </select>

                  <button
                    type="button"
                    class="usermodal-action-btn usermodal-action-btn--soft"
                    :disabled="saving || actionBusy || extensionDecisionDisabled"
                    @click="handleExtenderEdicion"
                  >
                    {{
                      actionBusy
                        ? "Procesando..."
                        : hasPendingExtensionRequest
                          ? "Aprobar y ampliar"
                          : "Ampliar plazo"
                    }}
                  </button>
                </div>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Motivo del bloqueo</label>

                <input
                  v-model="blockReason"
                  class="field-control usermodal-input"
                  :disabled="saving || actionBusy || manualProfileActionsDisabled"
                  maxlength="255"
                  placeholder="Ej.: Validación pendiente"
                />
              </div>
            </div>

            <div class="perfil-actions">
              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--primary"
                :disabled="saving || actionBusy || manualProfileActionsDisabled"
                :title="manualProfileActionsDisabled ? 'Las acciones manuales están deshabilitadas mientras se revisa una solicitud de extensión.' : undefined"
                @click="handleHabilitarEdicion"
              >
                {{ actionBusy ? "Procesando..." : "Permitir edición" }}
              </button>

              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--danger"
                :disabled="saving || actionBusy || manualProfileActionsDisabled"
                :title="manualProfileActionsDisabled ? 'Las acciones manuales están deshabilitadas mientras se revisa una solicitud de extensión.' : undefined"
                @click="handleBloquearEdicion"
              >
                {{ actionBusy ? "Procesando..." : "Quitar permiso" }}
              </button>
            </div>

          </section>

          <section class="usermodal-section" aria-label="Acceso administrativo">
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Acceso administrativo</h3>
              </div>
            </div>

            <div
              v-if="mode === 'create'"
              class="usermodal-grid"
            >
              <div class="usermodal-field">
                <label class="usermodal-label">Tipo de cuenta</label>
                <input
                  :value="tipoUsuarioLabel"
                  disabled
                  class="field-control usermodal-input input-readonly"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Estado de la cuenta</label>
                <input
                  :value="estadoLabel"
                  disabled
                  class="field-control usermodal-input input-readonly"
                />
              </div>
            </div>

            <template v-if="mode === 'edit'">
              <label class="usermodal-checkline">
                <input type="checkbox" v-model="form.is_staff" />

                <span>
                  <strong>Puede administrar el sistema</strong>
                </span>
              </label>
            </template>

            <template v-else>
              <p class="usermodal-note usermodal-note--info">
                La cuenta se registrará como <b>Pendiente</b> hasta que sea activada.
              </p>
            </template>
          </section>

          <div v-if="error" class="usermodal-alert" role="alert" aria-live="polite">
            {{ error }}
          </div>
        </div>

        <footer class="modal__footer usermodal-footer">
          <button
            type="button"
            class="btn-cerrar"
            :disabled="saving || actionBusy"
            @click="emit('close')"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="btn-guardar"
            :disabled="
              saving ||
              actionBusy ||
              institutionalEmailOnCreate
            "
          >
            {{ saving ? "Guardando..." : mode === "create" ? "Registrar" : "Guardar cambios" }}
          </button>
        </footer>
      </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from "vue";

import { adminApi } from "../../scripts/api/adminApi";
import {
  obtenerSolicitudExtensionPerfil,
  resolverSolicitudExtensionPerfil,
} from "../../scripts/api/profileExtensionApi";
import { useNotice } from "../../scripts/composables/useNotice";

import InfoTip from "../../inicio/ui/InfoTip.vue";

const props = defineProps({
  mode: { type: String, required: true },
  usuario: { type: Object, default: null },
  embedded: { type: Boolean, default: false },
  extensionRequest: { type: Object, default: null },
  extensionRequestRequired: { type: Boolean, default: false },
  extensionRequestId: { type: Number, default: null },
  extensionRequestLoadError: { type: String, default: "" },
  focusProfileEdit: { type: Boolean, default: false },
  initialExtendHours: { type: Number, default: 24 },
});

const emit = defineEmits([
  "close",
  "done",
  "extension-resolved",
  "open-extension-request",
]);

const embedded = computed(() =>
  Boolean(props.embedded)
);

const handleBackdropClick = () => {
  if (!embedded.value) {
    emit("close");
  }
};
const { openNotice } = useNotice();

const saving = ref(false);
const error = ref("");
const actionBusy = ref(false);

const loadingCatalogos = ref(false);
const loadingCarreras = ref(false);

const facultades = ref([]);
const carreras = ref([]);

const extendHours = ref(24);
const blockReason = ref("");
const extensionRequestState = ref(null);
const extensionRequestLoading = ref(false);
const extensionRequestLoadErrorState = ref("");
const extensionResolutionReason = ref("");
const profileControlSectionRef = ref(null);
const extendHoursSelectRef = ref(null);

const form = reactive({
  id: null,
  nombres: "",
  apellidos: "",
  email: "",
  identificacion: "",
  is_staff: false,
  facultad: "",
  carrera: "",
});

const profileLocked = ref(null);
const attemptsLeft = ref(null);
const profileUntil = ref(null);

const hasPendingExtensionRequest = computed(() => {
  return (
    props.mode === "edit" &&
    Number(extensionRequestState.value?.id) > 0 &&
    String(
      extensionRequestState.value?.estado ||
      "pendiente"
    ).toLowerCase() === "pendiente"
  );
});

const isExtensionRequestContext = computed(() => {
  return (
    props.mode === "edit" &&
    Boolean(props.extensionRequestRequired)
  );
});

const extensionRequestUnavailable = computed(() => {
  return (
    isExtensionRequestContext.value &&
    !extensionRequestState.value
  );
});

const extensionRequestResolved = computed(() => {
  return (
    isExtensionRequestContext.value &&
    Boolean(extensionRequestState.value) &&
    !hasPendingExtensionRequest.value
  );
});

const manualProfileActionsDisabled = computed(() => {
  return (
    isExtensionRequestContext.value ||
    hasPendingExtensionRequest.value ||
    Boolean(extensionRequestLoadErrorState.value)
  );
});

const extensionDecisionDisabled = computed(() => {
  if (!isExtensionRequestContext.value) {
    return (
      hasPendingExtensionRequest.value ||
      Boolean(extensionRequestLoadErrorState.value)
    );
  }

  return !hasPendingExtensionRequest.value;
});

const normalizeExtensionHours = (value) => {
  const hours = Number(value);
  return [6, 12, 24, 48, 72].includes(hours)
    ? hours
    : 24;
};

const formatRequestDate = (value) => {
  if (!value) return "No disponible";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(date);
};

const focusProfileControl = async () => {
  if (!props.focusProfileEdit) {
    return;
  }

  await nextTick();

  window.setTimeout(() => {
    profileControlSectionRef.value
      ?.scrollIntoView?.({
        behavior: "smooth",
        block: "center",
      });

    extendHoursSelectRef.value
      ?.focus?.({
        preventScroll: true,
      });
  }, 120);
};

const isInstitucional = computed(() => {
  return props.mode === "edit" && props.usuario?.auth_source === "microsoft";
});

const isExterno = computed(() => {
  if (props.mode === "create") return true;

  return (
    props.usuario?.auth_source === "local" &&
    props.usuario?.rol === "autor_externo"
  );
});

const isPendiente = computed(() => {
  if (props.mode === "create") return true;
  return isExterno.value && !props.usuario?.is_active;
});

const emailLocked = computed(() => props.mode === "edit" && isInstitucional.value);

const INSTITUTIONAL_EMAIL_DOMAINS = Object.freeze([
  "uleam.edu.ec",
]);

const INSTITUTIONAL_EMAIL_EXCEPTIONS = Object.freeze([
  "e1316718111@live.uleam.edu.ec",
]);

const isInstitutionalEmail = (value) => {
  const normalized = String(value || "")
    .trim()
    .toLowerCase();

  if (!normalized || !normalized.includes("@")) {
    return false;
  }

  if (INSTITUTIONAL_EMAIL_EXCEPTIONS.includes(normalized)) {
    return true;
  }

  const parts = normalized.split("@");

  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    return false;
  }

  return INSTITUTIONAL_EMAIL_DOMAINS.includes(parts[1]);
};

const institutionalEmailOnCreate = computed(() =>
  props.mode === "create" &&
  isInstitutionalEmail(form.email)
);

const tipoUsuarioLabel = computed(() => {
  if (props.mode === "create") return "Externo";
  if (isInstitucional.value) return "Institucional";
  if (isExterno.value) return "Externo";
  return "Usuario";
});

const estadoLabel = computed(() => {
  if (props.mode === "create") return "Pendiente";
  if (isPendiente.value) return "Pendiente";
  return props.usuario?.is_active ? "Activo" : "Inactivo";
});

const estadoBadgeClass = computed(() => {
  const value = String(estadoLabel.value || "").toLowerCase().trim();

  if (value.includes("pend")) return "usermodal-badge--warn";
  if (value.includes("inactivo")) return "usermodal-badge--off";
  if (value.includes("activo")) return "usermodal-badge--ok";

  return "usermodal-badge--neutral";
});

const showAcademicoSection = computed(() => {
  if (props.mode !== "edit") return false;
  if (isExterno.value) return false;
  return true;
});

const uiProfileLockedLabel = computed(() => {
  if (
    profileLocked.value === null ||
    profileLocked.value === undefined
  ) {
    return "Estado no disponible";
  }

  return profileLocked.value
    ? "No puede editar"
    : "Puede editar";
});

const uiProfileUntilLabel = computed(() => {
  if (!profileUntil.value) return "—";

  try {
    const date = new Date(profileUntil.value);
    if (Number.isNaN(date.getTime())) return String(profileUntil.value);
    return date.toLocaleString();
  } catch {
    return String(profileUntil.value);
  }
});

const toSelectOptions = (arr) => {
  if (!Array.isArray(arr)) return [];

  return arr.map((item) => ({
    value: item.id ?? item.value,
    label: item.nombre ?? item.label ?? String(item),
  }));
};

const resolveApiError = (data) => {
  if (!data) return "";

  if (typeof data?.detail === "string" && data.detail) return data.detail;
  if (typeof data?.error === "string" && data.error) return data.error;

  const priorityKeys = [
    "email",
    "identificacion",
    "facultad",
    "carrera",
    "rol",
    "auth_source",
    "is_staff",
    "is_active",
    "non_field_errors",
  ];

  for (const key of priorityKeys) {
    const value = data?.[key];

    if (Array.isArray(value) && value[0]) return String(value[0]);
    if (typeof value === "string" && value) return value;
  }

  const firstKey = Object.keys(data || {})[0];
  const firstValue = firstKey ? data[firstKey] : null;

  if (Array.isArray(firstValue) && firstValue[0]) return String(firstValue[0]);
  if (typeof firstValue === "string" && firstValue) return firstValue;

  return "";
};

const loadFacultades = async () => {
  loadingCatalogos.value = true;

  try {
    const data = await adminApi.selectsFacultades();
    facultades.value = toSelectOptions(data);
  } catch {
    facultades.value = [];
    error.value = "No se pudieron cargar las facultades.";
  } finally {
    loadingCatalogos.value = false;
  }
};

const loadCarreras = async (facultadId) => {
  carreras.value = [];

  if (!facultadId) return;

  loadingCarreras.value = true;

  try {
    const data = await adminApi.selectsCarrerasByFacultad(facultadId);
    carreras.value = toSelectOptions(data);
  } catch {
    carreras.value = [];
    error.value = "No se pudieron cargar las carreras.";
  } finally {
    loadingCarreras.value = false;
  }
};

const onFacultadChange = async () => {
  form.carrera = "";
  await loadCarreras(form.facultad);
};

watch(
  () => [props.mode, props.usuario],
  async ([mode, usuario]) => {
    error.value = "";

    if (mode === "create") {
      form.id = null;
      form.nombres = "";
      form.apellidos = "";
      form.email = "";
      form.identificacion = "";
      form.is_staff = false;
      form.facultad = "";
      form.carrera = "";

      facultades.value = [];
      carreras.value = [];

      profileLocked.value = null;
      attemptsLeft.value = null;
      profileUntil.value = null;

      extendHours.value = 24;
      blockReason.value = "";
      extensionRequestState.value = null;
      extensionRequestLoading.value = false;
      extensionRequestLoadErrorState.value = "";
      extensionResolutionReason.value = "";
      return;
    }

    if (!usuario) return;

    form.id = usuario.id;
    form.nombres = usuario.nombres || "";
    form.apellidos = usuario.apellidos || "";
    form.email = usuario.email || "";
    form.identificacion = usuario.identificacion || "";
    form.is_staff = !!usuario.is_staff;
    form.facultad = usuario.facultad ?? "";
    form.carrera = usuario.carrera ?? "";

    profileLocked.value = usuario.profile_edit_locked ?? null;
    attemptsLeft.value = usuario.profile_edit_attempts_left ?? null;
    profileUntil.value = usuario.profile_edit_until ?? null;

    extensionRequestState.value =
      props.extensionRequest
        ? { ...props.extensionRequest }
        : null;
    extensionRequestLoadErrorState.value = String(
      props.extensionRequestLoadError || ""
    ).trim();

    extendHours.value = normalizeExtensionHours(
      extensionRequestState.value?.horas_solicitadas ??
      props.initialExtendHours
    );
    blockReason.value = "";
    extensionResolutionReason.value = "";

    await focusProfileControl();

    if (showAcademicoSection.value) {
      await loadFacultades();

      if (form.facultad) {
        await loadCarreras(form.facultad);
      }
    } else {
      facultades.value = [];
      carreras.value = [];
    }
  },
  { immediate: true }
);

watch(
  () => [
    props.extensionRequest,
    props.extensionRequestLoadError,
    props.extensionRequestId,
  ],
  async ([request, loadError]) => {
    extensionRequestState.value =
      request
        ? { ...request }
        : null;

    extensionRequestLoadErrorState.value =
      String(loadError || "").trim();

    if (request) {
      extendHours.value =
        normalizeExtensionHours(
          request.horas_solicitadas ??
          props.initialExtendHours
        );
    }

    extensionResolutionReason.value = "";
    await focusProfileControl();
  },
  { deep: true }
);

const retryExtensionRequestLoad = async () => {
  const requestId = Number(
    props.extensionRequestId
  );

  if (
    !isExtensionRequestContext.value ||
    !Number.isInteger(requestId) ||
    requestId < 1 ||
    extensionRequestLoading.value
  ) {
    return;
  }

  extensionRequestLoading.value = true;
  extensionRequestLoadErrorState.value = "";

  try {
    const request =
      await obtenerSolicitudExtensionPerfil(
        requestId
      );

    const requestUserId = Number(
      request?.usuario_id
    );

    if (
      !Number.isInteger(requestUserId) ||
      requestUserId < 1
    ) {
      throw new Error(
        "La solicitud recuperada no contiene un usuario válido."
      );
    }

    if (Number(form.id) !== requestUserId) {
      throw new Error(
        "La solicitud recuperada no corresponde a este usuario."
      );
    }

    extensionRequestState.value = {
      ...request,
    };

    extendHours.value =
      normalizeExtensionHours(
        request?.horas_solicitadas ??
        props.initialExtendHours
      );

    extensionRequestLoadErrorState.value = "";
  } catch (exception) {
    extensionRequestState.value = null;
    extensionRequestLoadErrorState.value = String(
      exception?.response?.data?.detail ||
      exception?.response?.data?.message ||
      exception?.message ||
      "No se pudo cargar el detalle de la solicitud."
    ).trim();
  } finally {
    extensionRequestLoading.value = false;
    await focusProfileControl();
  }
};


const handleHabilitarEdicion = async () => {
  if (!form.id) return;

  if (manualProfileActionsDisabled.value) {
    openNotice({
      title: "Solicitud en revisión",
      message:
        "Resuelva la solicitud de extensión antes de utilizar acciones manuales sobre el plazo de edición.",
    });
    return;
  }

  actionBusy.value = true;

  try {
    const res = await adminApi.habilitarEdicionPerfil(form.id);

    profileLocked.value = res?.profile_edit_locked ?? false;
    attemptsLeft.value = res?.profile_edit_attempts_left ?? 3;
    profileUntil.value = res?.profile_edit_until ?? null;

    openNotice({
      title: "Edición habilitada",
      message: "Listo. El usuario ya puede editar su perfil nuevamente.",
    });
  } catch (e) {
    const data = e?.response?.data;

    openNotice({
      title: "No se pudo habilitar",
      message:
        resolveApiError(data) ||
        "No se pudo habilitar la edición del perfil. Intente nuevamente.",
    });
  } finally {
    actionBusy.value = false;
  }
};

const handleExtenderEdicion = async () => {
  if (!form.id) return;

  if (
    isExtensionRequestContext.value &&
    !hasPendingExtensionRequest.value
  ) {
    openNotice({
      title: extensionRequestUnavailable.value
        ? "Solicitud no disponible"
        : "Solicitud ya resuelta",
      message: extensionRequestUnavailable.value
        ? "No se aplicará una extensión manual mientras no pueda verificarse la solicitud pendiente."
        : "Esta solicitud ya fue resuelta. Abra el usuario desde el listado general si necesita realizar una acción manual adicional.",
    });
    return;
  }

  actionBusy.value = true;

  try {
    const horas = normalizeExtensionHours(
      extendHours.value
    );

    if (hasPendingExtensionRequest.value) {
      const result =
        await resolverSolicitudExtensionPerfil(
          extensionRequestState.value.id,
          {
            decision: "aprobar",
            horas_aprobadas: horas,
            motivo_resolucion: "",
          }
        );

      const solicitud =
        result?.solicitud ||
        extensionRequestState.value;

      extensionRequestState.value = {
        ...solicitud,
      };

      profileLocked.value = false;
      attemptsLeft.value = Math.max(
        Number(attemptsLeft.value || 0),
        3
      );
      profileUntil.value =
        solicitud?.nuevo_plazo ||
        profileUntil.value;

      emit("extension-resolved", {
        solicitud,
        decision: "aprobar",
      });

      openNotice({
        title: "Solicitud aprobada",
        message:
          `Se aprobaron ${horas} horas adicionales. El usuario ya puede editar su perfil dentro del nuevo plazo.`,
      });

      return;
    }

    const res =
      await adminApi.extenderEdicionPerfil(
        form.id,
        horas
      );

    if (res && typeof res === "object") {
      if ("profile_edit_until" in res) {
        profileUntil.value =
          res.profile_edit_until;
      }
      if ("profile_edit_locked" in res) {
        profileLocked.value =
          !!res.profile_edit_locked;
      }
      if ("profile_edit_attempts_left" in res) {
        attemptsLeft.value =
          res.profile_edit_attempts_left;
      }
    }

    openNotice({
      title: "Edición extendida",
      message:
        `Listo. Se extendió el plazo de edición en ${horas} horas.`,
    });
  } catch (e) {
    const data = e?.response?.data;

    openNotice({
      title:
        hasPendingExtensionRequest.value
          ? "No se pudo aprobar la solicitud"
          : "No se pudo extender",
      message:
        resolveApiError(data) ||
        "No se pudo extender la edición del perfil. Intente nuevamente.",
    });
  } finally {
    actionBusy.value = false;
  }
};

const handleRejectExtensionRequest = async () => {
  if (
    !hasPendingExtensionRequest.value ||
    actionBusy.value
  ) {
    return;
  }

  const reason = String(
    extensionResolutionReason.value || ""
  ).trim();

  if (reason.length < 10) {
    openNotice({
      title: "Falta el motivo",
      message:
        "Para rechazar la solicitud indique un motivo de al menos 10 caracteres.",
    });
    return;
  }

  actionBusy.value = true;

  try {
    const result =
      await resolverSolicitudExtensionPerfil(
        extensionRequestState.value.id,
        {
          decision: "rechazar",
          motivo_resolucion: reason,
        }
      );

    const solicitud =
      result?.solicitud ||
      extensionRequestState.value;

    extensionRequestState.value = {
      ...solicitud,
    };
    extensionResolutionReason.value = "";

    emit("extension-resolved", {
      solicitud,
      decision: "rechazar",
    });

    openNotice({
      title: "Solicitud rechazada",
      message:
        "La solicitud fue rechazada y el usuario recibirá la decisión en sus notificaciones.",
    });
  } catch (e) {
    const data = e?.response?.data;

    openNotice({
      title: "No se pudo rechazar",
      message:
        resolveApiError(data) ||
        "No se pudo resolver la solicitud. Intente nuevamente.",
    });
  } finally {
    actionBusy.value = false;
  }
};

const handleBloquearEdicion = async () => {
  if (!form.id) return;

  if (manualProfileActionsDisabled.value) {
    openNotice({
      title: "Solicitud en revisión",
      message:
        "Resuelva la solicitud de extensión antes de utilizar acciones manuales sobre el plazo de edición.",
    });
    return;
  }

  openNotice({
    title: "Confirmar bloqueo",
    message:
      "¿Desea bloquear la edición del perfil para este usuario? Podrá habilitarla nuevamente cuando lo necesite.",
    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, bloquear",
    onConfirm: async () => {
      actionBusy.value = true;

      try {
        const res = await adminApi.bloquearEdicionPerfil(form.id, blockReason.value);

        profileLocked.value = res?.profile_edit_locked ?? true;
        attemptsLeft.value = res?.profile_edit_attempts_left ?? 0;
        profileUntil.value = res?.profile_edit_until ?? null;

        openNotice({
          title: "Edición bloqueada",
          message: "Listo. El usuario no podrá editar su perfil hasta nueva habilitación.",
        });
      } catch (e) {
        const data = e?.response?.data;

        openNotice({
          title: "No se pudo bloquear",
          message:
            resolveApiError(data) ||
            "No se pudo bloquear la edición del perfil. Intente nuevamente.",
        });
      } finally {
        actionBusy.value = false;
      }
    },
  });
};

const submit = async () => {
  error.value = "";
  saving.value = true;

  try {
    const nombres = String(form.nombres || "").trim();
    const apellidos = String(form.apellidos || "").trim();
    const email = String(form.email || "").trim().toLowerCase();
    const identificacionRaw = String(form.identificacion || "").trim();
    const identificacion = identificacionRaw || null;

    if (!nombres || !apellidos || !email) {
      error.value = "Complete los campos obligatorios antes de guardar.";
      return;
    }

    if (
      props.mode === "create" &&
      isInstitutionalEmail(email)
    ) {
      error.value =
        "Este correo corresponde a una cuenta institucional ULEAM. " +
        "Los usuarios institucionales deben ingresar mediante Microsoft 365 " +
        "y no pueden registrarse como usuarios externos.";

      openNotice({
        title: "Cuenta institucional",
        message: error.value,
      });

      return;
    }

    if (props.mode === "create" && !identificacion) {
      error.value = "Ingrese la identificación del usuario externo.";
      return;
    }

    if (identificacion && !/^\d+$/.test(identificacion)) {
      error.value = "La identificación debe contener solo números.";
      return;
    }

    if (identificacion && identificacion.length !== 10) {
      error.value = "La identificación debe tener 10 dígitos numéricos.";
      return;
    }

    if (props.mode === "create") {
      await adminApi.crearUsuario({
        nombres,
        apellidos,
        email,
        identificacion,
      });

      emit("done", {
        title: "Usuario registrado",
        message: "Se registró correctamente. Para permitir acceso: Pendientes → Activar cuenta.",
      });

      return;
    }

    if (!form.id) {
      throw new Error("ID faltante en edición.");
    }

    const payload = {
      nombres,
      apellidos,
      email,
      identificacion,
      is_staff_set: !!form.is_staff,
    };

    if (showAcademicoSection.value) {
      const facultad = form.facultad ? Number(form.facultad) : null;
      const carrera = form.carrera ? Number(form.carrera) : null;

      if (!facultad || !carrera) {
        error.value = "Seleccione facultad y carrera para completar la asignación académica.";
        return;
      }

      payload.facultad = facultad;
      payload.carrera = carrera;
    }

    await adminApi.editarUsuario(form.id, payload);

    emit("done", {
      title: "Cambios guardados",
      message: "Listo. Los datos del usuario se actualizaron correctamente.",
    });
  } catch (e) {
    const data = e?.response?.data;

    error.value = resolveApiError(data) || "No se pudo guardar la información.";

    openNotice({
      title: "No se pudo guardar",
      message: error.value || "Revise los campos e intente nuevamente.",
    });
  } finally {
    saving.value = false;
  }
};
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./usuario-modal.css"></style>
