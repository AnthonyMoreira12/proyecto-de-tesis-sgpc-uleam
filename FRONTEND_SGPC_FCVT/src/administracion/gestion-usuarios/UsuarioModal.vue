<template>
  <div
    class="sgpc-admin-modal modal-overlay"
    @click.self="requestClose"
  >
    <div
      ref="dialogRef"
      class="modal modal--user"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="dialogTitleId"
      :aria-describedby="dialogDescriptionId"
      :aria-busy="formBusy"
      tabindex="-1"
      @keydown="handleDialogKeydown"
    >
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header class="modal__header usermodal-header">
        <div class="usermodal-titlewrap">
          <div class="usermodal-titleline">
            <h2
              :id="dialogTitleId"
              class="modal__title usermodal-title"
            >
              {{
                mode === "create"
                  ? "Registrar usuario externo"
                  : "Editar usuario"
              }}
            </h2>

            <div
              class="usermodal-badges"
              aria-label="Tipo y estado de la cuenta"
            >
              <span
                class="usermodal-badge usermodal-badge--neutral"
              >
                {{ tipoUsuarioLabel }}
              </span>

              <span
                class="usermodal-badge"
                :class="estadoBadgeClass"
              >
                {{ estadoLabel }}
              </span>
            </div>
          </div>

          <p
            :id="dialogDescriptionId"
            class="modal__subtitle usermodal-subtitle"
          >
            {{
              mode === "create"
                ? "Complete los datos básicos. La cuenta quedará pendiente hasta que sea activada."
                : descripcionEdicion
            }}
          </p>
        </div>

        <button
          type="button"
          class="btn-cerrar modal__close usermodal-close"
          :disabled="formBusy"
          aria-label="Cerrar ventana"
          title="Cerrar"
          @click="requestClose"
        >
          <span aria-hidden="true">✕</span>
        </button>
      </header>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->
      <form
        class="usermodal-form"
        novalidate
        @submit.prevent="submit"
      >
        <div class="usermodal-scroll">
          <!-- =================================================
               DATOS PERSONALES
          ================================================== -->
          <section
            class="usermodal-section"
            aria-labelledby="usermodal-personal-title"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3
                  id="usermodal-personal-title"
                  class="usermodal-sectiontitle"
                >
                  Datos personales
                </h3>

                <p class="usermodal-sectionsub">
                  Información principal para identificar la cuenta.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <!-- NOMBRES -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-nombres"
                >
                  <span>Nombres</span>

                  <span
                    class="usermodal-required"
                    aria-hidden="true"
                  >
                    *
                  </span>
                </label>

                <input
                  id="usermodal-nombres"
                  v-model="form.nombres"
                  class="field-control usermodal-input"
                  name="nombres"
                  type="text"
                  required
                  maxlength="100"
                  placeholder="Ej.: Andrea Sofía"
                  autocomplete="given-name"
                  :disabled="formBusy"
                />
              </div>

              <!-- APELLIDOS -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-apellidos"
                >
                  <span>Apellidos</span>

                  <span
                    class="usermodal-required"
                    aria-hidden="true"
                  >
                    *
                  </span>
                </label>

                <input
                  id="usermodal-apellidos"
                  v-model="form.apellidos"
                  class="field-control usermodal-input"
                  name="apellidos"
                  type="text"
                  required
                  maxlength="100"
                  placeholder="Ej.: García López"
                  autocomplete="family-name"
                  :disabled="formBusy"
                />
              </div>

              <!-- CORREO -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-email"
                >
                  <span>Correo electrónico</span>

                  <span
                    class="usermodal-required"
                    aria-hidden="true"
                  >
                    *
                  </span>
                </label>

                <input
                  id="usermodal-email"
                  v-model="form.email"
                  class="field-control usermodal-input"
                  :class="{
                    'input-readonly': emailLocked,
                  }"
                  name="email"
                  type="email"
                  required
                  maxlength="150"
                  placeholder="Ej.: usuario@correo.com"
                  autocomplete="email"
                  inputmode="email"
                  :disabled="formBusy || emailLocked"
                  :aria-describedby="
                    emailLocked
                      ? 'usermodal-email-help'
                      : undefined
                  "
                />

                <p
                  v-if="emailLocked"
                  id="usermodal-email-help"
                  class="usermodal-help"
                >
                  El correo de esta cuenta institucional se
                  administra mediante Microsoft 365.
                </p>
              </div>

              <!-- CÉDULA -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label usermodal-label--with-help"
                  for="usermodal-identificacion"
                >
                  <span class="usermodal-label__text">
                    Número de cédula

                    <span
                      v-if="mode === 'create'"
                      class="usermodal-required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </span>

                  <InfoTip title="Número de cédula">
                    Ingrese exactamente 10 dígitos numéricos,
                    sin espacios, letras ni guiones.
                  </InfoTip>
                </label>

                <input
                  id="usermodal-identificacion"
                  v-model="form.identificacion"
                  class="field-control usermodal-input"
                  name="identificacion"
                  type="text"
                  :required="mode === 'create'"
                  minlength="10"
                  maxlength="10"
                  pattern="[0-9]{10}"
                  placeholder="Ej.: 1312345678"
                  autocomplete="off"
                  inputmode="numeric"
                  aria-describedby="usermodal-identificacion-help"
                  :aria-invalid="cedulaTieneError"
                  :disabled="formBusy"
                  @input="sanitizeCedula"
                />

                <p
                  id="usermodal-identificacion-help"
                  class="usermodal-help"
                >
                  Debe contener exactamente 10 números.
                </p>
              </div>
            </div>
          </section>

          <!-- =================================================
               ASIGNACIÓN ACADÉMICA
          ================================================== -->
          <section
            v-if="showAcademicoSection"
            class="usermodal-section"
            aria-labelledby="usermodal-academico-title"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3
                  id="usermodal-academico-title"
                  class="usermodal-sectiontitle"
                >
                  Asignación académica
                </h3>

                <p class="usermodal-sectionsub">
                  Complete o corrija la Facultad y Carrera
                  asignadas al usuario institucional.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <!-- FACULTAD -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-facultad"
                >
                  <span>Facultad</span>

                  <span
                    class="usermodal-required"
                    aria-hidden="true"
                  >
                    *
                  </span>
                </label>

                <select
                  id="usermodal-facultad"
                  v-model="form.facultad"
                  class="field-control usermodal-input"
                  name="facultad"
                  required
                  :disabled="
                    formBusy ||
                    loadingCatalogos
                  "
                  :aria-busy="loadingCatalogos"
                  :aria-describedby="
                    loadingCatalogos
                      ? 'usermodal-facultad-status'
                      : undefined
                  "
                  @change="onFacultadChange"
                >
                  <option value="">
                    Seleccione una Facultad
                  </option>

                  <option
                    v-for="facultad in facultades"
                    :key="facultad.value"
                    :value="facultad.value"
                  >
                    {{ facultad.label }}
                  </option>
                </select>

                <p
                  v-if="loadingCatalogos"
                  id="usermodal-facultad-status"
                  class="usermodal-help"
                  role="status"
                  aria-live="polite"
                >
                  Cargando facultades...
                </p>
              </div>

              <!-- CARRERA -->
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-carrera"
                >
                  <span>Carrera</span>

                  <span
                    class="usermodal-required"
                    aria-hidden="true"
                  >
                    *
                  </span>
                </label>

                <select
                  id="usermodal-carrera"
                  v-model="form.carrera"
                  class="field-control usermodal-input"
                  name="carrera"
                  required
                  :disabled="
                    formBusy ||
                    loadingCatalogos ||
                    loadingCarreras ||
                    !form.facultad
                  "
                  :aria-busy="loadingCarreras"
                  :aria-describedby="
                    loadingCarreras
                      ? 'usermodal-carrera-status'
                      : undefined
                  "
                >
                  <option value="">
                    Seleccione una Carrera
                  </option>

                  <option
                    v-for="carrera in carreras"
                    :key="carrera.value"
                    :value="carrera.value"
                  >
                    {{ carrera.label }}
                  </option>
                </select>

                <p
                  v-if="
                    form.facultad &&
                    loadingCarreras
                  "
                  id="usermodal-carrera-status"
                  class="usermodal-help"
                  role="status"
                  aria-live="polite"
                >
                  Cargando carreras...
                </p>
              </div>
            </div>

            <p
              class="usermodal-note usermodal-note--info"
            >
              La autenticación continúa administrada por
              Microsoft 365. Esta sección únicamente corrige
              la relación académica interna.
            </p>
          </section>

          <!-- =================================================
               INFORMACIÓN PARA CUENTAS NO INSTITUCIONALES
          ================================================== -->
          <section
            v-else-if="mode === 'edit'"
            class="usermodal-section"
            aria-labelledby="usermodal-account-info-title"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3
                  id="usermodal-account-info-title"
                  class="usermodal-sectiontitle"
                >
                  Clasificación de la cuenta
                </h3>

                <p class="usermodal-sectionsub">
                  Esta cuenta no utiliza una asignación académica
                  institucional.
                </p>
              </div>
            </div>

            <p
              v-if="isExterno"
              class="usermodal-note usermodal-note--info"
            >
              Los usuarios externos no registran Facultad ni
              Carrera dentro del sistema.
            </p>

            <p
              v-else
              class="usermodal-note usermodal-note--warn"
            >
              La combinación actual de rol y origen de
              autenticación no corresponde a una cuenta
              institucional ni externa.
            </p>
          </section>

          <!-- =================================================
               CONTROL DE EDICIÓN
          ================================================== -->
          <section
            v-if="mode === 'edit'"
            class="usermodal-section"
            aria-labelledby="usermodal-edit-control-title"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3
                  id="usermodal-edit-control-title"
                  class="usermodal-sectiontitle"
                >
                  Control de edición
                </h3>

                <p class="usermodal-sectionsub">
                  Habilite, extienda o bloquee la edición del
                  perfil del usuario.
                </p>
              </div>

              <InfoTip title="Control de edición">
                Habilitar desbloquea el perfil y reinicia los
                intentos. Extender agrega horas al plazo actual.
                Bloquear impide nuevas modificaciones.
              </InfoTip>
            </div>

            <div
              class="usermodal-status-grid"
              aria-label="Estado de edición del perfil"
            >
              <div class="usermodal-status">
                <span>Bloqueado</span>
                <strong>{{ uiProfileLockedLabel }}</strong>
              </div>

              <div class="usermodal-status">
                <span>Intentos disponibles</span>
                <strong>{{ uiAttemptsLeftLabel }}</strong>
              </div>

              <div class="usermodal-status">
                <span>Límite de edición</span>
                <strong>{{ uiProfileUntilLabel }}</strong>
              </div>
            </div>

            <div class="usermodal-control-grid">
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-extend-hours"
                >
                  Extender edición
                </label>

                <div class="extend-row">
                  <select
                    id="usermodal-extend-hours"
                    v-model="extendHours"
                    class="field-control usermodal-input"
                    name="extend_hours"
                    :disabled="formBusy"
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
                    :disabled="formBusy"
                    @click="handleExtenderEdicion"
                  >
                    {{
                      actionType === "extend"
                        ? "Procesando..."
                        : "Extender"
                    }}
                  </button>
                </div>
              </div>

              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-block-reason"
                >
                  Razón de bloqueo
                </label>

                <input
                  id="usermodal-block-reason"
                  v-model="blockReason"
                  class="field-control usermodal-input"
                  name="block_reason"
                  type="text"
                  maxlength="255"
                  placeholder="Ej.: Validación pendiente"
                  aria-describedby="usermodal-block-reason-help"
                  :disabled="formBusy"
                />

                <p
                  id="usermodal-block-reason-help"
                  class="usermodal-help"
                >
                  El motivo quedará registrado como parte del
                  bloqueo administrativo.
                </p>
              </div>
            </div>

            <div
              class="perfil-actions"
              aria-label="Acciones de control de edición"
            >
              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--primary"
                :disabled="formBusy"
                @click="handleHabilitarEdicion"
              >
                {{
                  actionType === "enable"
                    ? "Procesando..."
                    : "Habilitar edición"
                }}
              </button>

              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--danger"
                :disabled="formBusy"
                @click="handleBloquearEdicion"
              >
                {{
                  actionType === "block"
                    ? "Procesando..."
                    : "Bloquear edición"
                }}
              </button>
            </div>

            <p class="usermodal-help">
              Este control no modifica las credenciales ni el
              estado activo de la cuenta.
            </p>
          </section>

          <!-- =================================================
               PERFIL Y PERMISOS
          ================================================== -->
          <section
            class="usermodal-section"
            aria-labelledby="usermodal-permissions-title"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3
                  id="usermodal-permissions-title"
                  class="usermodal-sectiontitle"
                >
                  Perfil y permisos
                </h3>

                <p class="usermodal-sectionsub">
                  Verifique el tipo de cuenta, su estado y los
                  privilegios administrativos.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-account-type"
                >
                  Tipo de cuenta
                </label>

                <input
                  id="usermodal-account-type"
                  :value="tipoUsuarioLabel"
                  class="field-control usermodal-input input-readonly"
                  type="text"
                  disabled
                />
              </div>

              <div class="usermodal-field">
                <label
                  class="usermodal-label"
                  for="usermodal-account-status"
                >
                  Estado de la cuenta
                </label>

                <input
                  id="usermodal-account-status"
                  :value="estadoLabel"
                  class="field-control usermodal-input input-readonly"
                  type="text"
                  disabled
                />
              </div>
            </div>

            <template v-if="mode === 'edit'">
              <label
                class="usermodal-checkline"
                for="usermodal-is-staff"
              >
                <input
                  id="usermodal-is-staff"
                  v-model="form.is_staff"
                  type="checkbox"
                  :disabled="
                    formBusy ||
                    Boolean(usuario?.is_superuser)
                  "
                />

                <span>
                  <strong>Permisos de administración</strong>

                  <small>
                    Actívelo únicamente si esta persona gestionará
                    usuarios, catálogos o publicaciones globales.
                  </small>

                  <small v-if="usuario?.is_superuser">
                    Los permisos de un superusuario no pueden
                    revocarse desde esta opción.
                  </small>
                </span>
              </label>
            </template>

            <template v-else>
              <p class="usermodal-note usermodal-note--info">
                Los usuarios externos nuevos se crean sin
                privilegios administrativos.
              </p>

              <p class="usermodal-note usermodal-note--warn">
                Al guardar, la cuenta se registrará como
                <strong>Pendiente</strong>. Para habilitar el acceso,
                utilice
                <strong>Pendientes → Activar cuenta</strong>.
              </p>
            </template>
          </section>

          <!-- =================================================
               ERROR
          ================================================== -->
          <div
            v-if="error"
            class="usermodal-alert"
            role="alert"
            aria-live="assertive"
          >
            {{ error }}
          </div>
        </div>

        <!-- ===================================================
             PIE DEL MODAL
        ==================================================== -->
        <footer class="modal__footer usermodal-footer">
          <button
            type="button"
            class="btn-cerrar"
            :disabled="formBusy"
            @click="requestClose"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="btn-guardar"
            :disabled="
              formBusy ||
              loadingCatalogos ||
              loadingCarreras
            "
          >
            {{
              saving
                ? "Guardando..."
                : mode === "create"
                  ? "Registrar usuario"
                  : "Guardar cambios"
            }}
          </button>
        </footer>
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
  reactive,
  ref,
  watch,
} from "vue";

import { adminApi } from "../../scripts/api/adminApi";
import { useNotice } from "../../scripts/composables/useNotice";

import InfoTip from "../../inicio/ui/InfoTip.vue";


const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) =>
      ["create", "edit"].includes(value),
  },

  usuario: {
    type: Object,
    default: null,
  },
});


const emit = defineEmits([
  "close",
  "done",
]);


const { openNotice } = useNotice();


const dialogRef = ref(null);

const saving = ref(false);
const error = ref("");

const actionBusy = ref(false);
const actionType = ref("");

const loadingCatalogos = ref(false);
const loadingCarreras = ref(false);

const facultades = ref([]);
const carreras = ref([]);

const extendHours = ref(24);
const blockReason = ref("");


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


let previouslyFocusedElement = null;
let previousBodyOverflow = "";


const dialogTitleId =
  "usermodal-dialog-title";

const dialogDescriptionId =
  "usermodal-dialog-description";


const ROLE_INSTITUTIONAL = "autor";
const ROLE_EXTERNAL = "autor_externo";

const AUTH_SOURCE_LOCAL = "local";
const AUTH_SOURCE_MICROSOFT = "microsoft";


/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) => {
  return String(value ?? "").trim();
};


const normalizeAccountValue = (value) => {
  return normalizeText(value).toLowerCase();
};


const cleanEmail = (value) => {
  return normalizeText(value).toLowerCase();
};


const sanitizeCedulaValue = (value) => {
  return String(value ?? "")
    .replace(/\D/g, "")
    .slice(0, 10);
};


const toPositiveId = (value) => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  const parsed = Number(value);

  if (
    !Number.isInteger(parsed) ||
    parsed <= 0
  ) {
    return null;
  }

  return parsed;
};


/* ============================================================
   ESTADO DERIVADO
============================================================ */

const formBusy = computed(() => {
  return Boolean(
    saving.value ||
    actionBusy.value
  );
});


const normalizedAuthSource = computed(() => {
  return normalizeAccountValue(
    props.usuario?.auth_source
  );
});


const normalizedRole = computed(() => {
  return normalizeAccountValue(
    props.usuario?.rol ??
    props.usuario?.role
  );
});


const isInstitucional = computed(() => {
  return Boolean(
    props.mode === "edit" &&
    normalizedRole.value ===
      ROLE_INSTITUTIONAL &&
    normalizedAuthSource.value ===
      AUTH_SOURCE_MICROSOFT
  );
});


const isExterno = computed(() => {
  if (props.mode === "create") {
    return true;
  }

  return Boolean(
    normalizedRole.value ===
      ROLE_EXTERNAL &&
    normalizedAuthSource.value ===
      AUTH_SOURCE_LOCAL
  );
});


const isPendiente = computed(() => {
  if (props.mode === "create") {
    return true;
  }

  return props.usuario?.es_pendiente === true;
});


const emailLocked = computed(() => {
  return Boolean(
    props.mode === "edit" &&
    isInstitucional.value
  );
});


const showAcademicoSection = computed(() => {
  return Boolean(
    props.mode === "edit" &&
    isInstitucional.value
  );
});


const tipoUsuarioLabel = computed(() => {
  if (props.mode === "create") {
    return "Cuenta externa";
  }

  if (isInstitucional.value) {
    return "Cuenta institucional";
  }

  if (isExterno.value) {
    return "Cuenta externa";
  }

  return "Cuenta sin clasificación válida";
});


const descripcionEdicion = computed(() => {
  if (isInstitucional.value) {
    return (
      "Actualice los datos personales, la asignación " +
      "académica y los permisos del usuario institucional."
    );
  }

  if (isExterno.value) {
    return (
      "Actualice los datos personales y los permisos " +
      "del usuario externo."
    );
  }

  return (
    "Actualice los datos permitidos y revise la " +
    "clasificación actual de la cuenta."
  );
});


const estadoLabel = computed(() => {
  if (props.mode === "create") {
    return "Pendiente";
  }

  if (isPendiente.value) {
    return "Pendiente";
  }

  return props.usuario?.is_active
    ? "Activo"
    : "Inactivo";
});


const estadoBadgeClass = computed(() => {
  const value = normalizeAccountValue(
    estadoLabel.value
  );

  if (value.includes("pend")) {
    return "usermodal-badge--warn";
  }

  if (value === "inactivo") {
    return "usermodal-badge--off";
  }

  if (value === "activo") {
    return "usermodal-badge--ok";
  }

  return "usermodal-badge--neutral";
});


const cedulaActual = computed(() => {
  return normalizeText(
    form.identificacion
  );
});


const cedulaTieneError = computed(() => {
  if (!cedulaActual.value) {
    return false;
  }

  return !/^\d{10}$/.test(
    cedulaActual.value
  );
});


const uiProfileLockedLabel = computed(() => {
  if (
    profileLocked.value === null ||
    profileLocked.value === undefined
  ) {
    return "—";
  }

  return profileLocked.value
    ? "Sí"
    : "No";
});


const uiAttemptsLeftLabel = computed(() => {
  if (
    attemptsLeft.value === null ||
    attemptsLeft.value === undefined
  ) {
    return "—";
  }

  return String(
    attemptsLeft.value
  );
});


const uiProfileUntilLabel = computed(() => {
  if (!profileUntil.value) {
    return "—";
  }

  try {
    const date = new Date(
      profileUntil.value
    );

    if (Number.isNaN(date.getTime())) {
      return String(
        profileUntil.value
      );
    }

    return new Intl.DateTimeFormat(
      "es-EC",
      {
        dateStyle: "medium",
        timeStyle: "short",
      }
    ).format(date);
  } catch {
    return String(
      profileUntil.value
    );
  }
});


/* ============================================================
   UTILIDADES DE FORMULARIO
============================================================ */

const sanitizeCedula = () => {
  form.identificacion =
    sanitizeCedulaValue(
      form.identificacion
    );
};


const toSelectOptions = (items) => {
  if (!Array.isArray(items)) {
    return [];
  }

  return items
    .map((item) => {
      const value =
        item?.id ??
        item?.value ??
        null;

      const label =
        item?.nombre ??
        item?.label ??
        "";

      return {
        value,
        label: normalizeText(label),
      };
    })
    .filter((item) => {
      return (
        item.value !== null &&
        item.value !== undefined &&
        item.value !== "" &&
        item.label
      );
    });
};


const resolveApiError = (data) => {
  if (!data) {
    return "";
  }

  if (typeof data === "string") {
    return data;
  }

  if (
    typeof data?.detail === "string" &&
    data.detail
  ) {
    return data.detail;
  }

  if (
    Array.isArray(data?.detail) &&
    data.detail[0]
  ) {
    return String(data.detail[0]);
  }

  if (
    typeof data?.error === "string" &&
    data.error
  ) {
    return data.error;
  }

  const priorityKeys = [
    "email",
    "identificacion",
    "nombres",
    "apellidos",
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

    if (
      Array.isArray(value) &&
      value[0]
    ) {
      return String(value[0]);
    }

    if (
      typeof value === "string" &&
      value
    ) {
      return value;
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const nestedMessage =
        resolveApiError(value);

      if (nestedMessage) {
        return nestedMessage;
      }
    }
  }

  for (const value of Object.values(data)) {
    if (
      Array.isArray(value) &&
      value[0]
    ) {
      return String(value[0]);
    }

    if (
      typeof value === "string" &&
      value
    ) {
      return value;
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const nestedMessage =
        resolveApiError(value);

      if (nestedMessage) {
        return nestedMessage;
      }
    }
  }

  return "";
};


/* ============================================================
   ACCESIBILIDAD DEL MODAL
============================================================ */

const requestClose = () => {
  if (formBusy.value) {
    return;
  }

  emit("close");
};


const getFocusableElements = () => {
  const dialog = dialogRef.value;

  if (!dialog) {
    return [];
  }

  const selector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled]):not([type='hidden'])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  return Array.from(
    dialog.querySelectorAll(selector)
  ).filter((element) => {
    return (
      !element.hasAttribute("hidden") &&
      element.getAttribute("aria-hidden") !== "true" &&
      element.getClientRects().length > 0
    );
  });
};


const focusInitialControl = async () => {
  await nextTick();

  const preferredControl =
    dialogRef.value?.querySelector(
      "#usermodal-nombres:not([disabled])"
    );

  if (
    preferredControl instanceof HTMLElement
  ) {
    preferredControl.focus();
    return;
  }

  dialogRef.value?.focus();
};


const handleDialogKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    requestClose();
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getFocusableElements();

  if (!focusableElements.length) {
    event.preventDefault();
    dialogRef.value?.focus();
    return;
  }

  const firstElement =
    focusableElements[0];

  const lastElement =
    focusableElements[
      focusableElements.length - 1
    ];

  const activeElement =
    document.activeElement;

  if (
    event.shiftKey &&
    activeElement === firstElement
  ) {
    event.preventDefault();
    lastElement.focus();
    return;
  }

  if (
    !event.shiftKey &&
    activeElement === lastElement
  ) {
    event.preventDefault();
    firstElement.focus();
  }
};


/* ============================================================
   CATÁLOGOS ACADÉMICOS
============================================================ */

const loadFacultades = async () => {
  loadingCatalogos.value = true;

  try {
    const data =
      await adminApi.selectsFacultades();

    facultades.value =
      toSelectOptions(data);
  } catch (exception) {
    facultades.value = [];

    error.value =
      resolveApiError(
        exception?.response?.data
      ) ||
      "No se pudieron cargar las facultades.";
  } finally {
    loadingCatalogos.value = false;
  }
};


const loadCarreras = async (facultadId) => {
  carreras.value = [];

  const normalizedFacultyId =
    toPositiveId(facultadId);

  if (!normalizedFacultyId) {
    return;
  }

  loadingCarreras.value = true;

  try {
    const data =
      await adminApi.selectsCarrerasByFacultad(
        normalizedFacultyId
      );

    carreras.value =
      toSelectOptions(data);
  } catch (exception) {
    carreras.value = [];

    error.value =
      resolveApiError(
        exception?.response?.data
      ) ||
      "No se pudieron cargar las carreras.";
  } finally {
    loadingCarreras.value = false;
  }
};


const onFacultadChange = async () => {
  form.carrera = "";

  await loadCarreras(
    form.facultad
  );
};


/* ============================================================
   CARGA DEL USUARIO
============================================================ */

const resetForm = () => {
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

  actionType.value = "";
  error.value = "";
};


watch(
  () => [
    props.mode,
    props.usuario,
  ],
  async ([mode, usuario]) => {
    resetForm();

    if (mode === "create") {
      return;
    }

    if (!usuario) {
      return;
    }

    form.id =
      usuario.id ?? null;

    form.nombres =
      usuario.nombres || "";

    form.apellidos =
      usuario.apellidos || "";

    form.email =
      usuario.email || "";

    form.identificacion =
      sanitizeCedulaValue(
        usuario.identificacion || ""
      );

    form.is_staff =
      Boolean(usuario.is_staff);

    profileLocked.value =
      usuario.profile_edit_locked ??
      null;

    attemptsLeft.value =
      usuario.profile_edit_attempts_left ??
      null;

    profileUntil.value =
      usuario.profile_edit_until ??
      null;

    /*
      El serializer administrativo devuelve expresamente:

      facultad_id
      carrera
    */
    if (showAcademicoSection.value) {
      form.facultad =
        usuario.facultad_id ??
        "";

      form.carrera =
        usuario.carrera ??
        usuario.carrera_id ??
        "";

      await loadFacultades();

      if (form.facultad) {
        await loadCarreras(
          form.facultad
        );
      }
    } else {
      form.facultad = "";
      form.carrera = "";
      facultades.value = [];
      carreras.value = [];
    }
  },
  {
    immediate: true,
  }
);


/* ============================================================
   CONTROL DE EDICIÓN
============================================================ */

const handleHabilitarEdicion = async () => {
  if (
    !form.id ||
    formBusy.value
  ) {
    return;
  }

  actionBusy.value = true;
  actionType.value = "enable";

  try {
    const response =
      await adminApi.habilitarEdicionPerfil(
        form.id
      );

    profileLocked.value =
      response?.profile_edit_locked ??
      false;

    attemptsLeft.value =
      response?.profile_edit_attempts_left ??
      3;

    profileUntil.value =
      response?.profile_edit_until ??
      null;

    openNotice({
      title: "Edición habilitada",
      message:
        "El usuario ya puede editar su perfil nuevamente.",
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    openNotice({
      title: "No se pudo habilitar",
      message:
        resolveApiError(data) ||
        "No se pudo habilitar la edición del perfil.",
    });
  } finally {
    actionBusy.value = false;
    actionType.value = "";
  }
};


const handleExtenderEdicion = async () => {
  if (
    !form.id ||
    formBusy.value
  ) {
    return;
  }

  const horas =
    Number(extendHours.value);

  if (
    !Number.isInteger(horas) ||
    horas <= 0
  ) {
    openNotice({
      title: "Horas inválidas",
      message:
        "Seleccione un número válido de horas.",
    });

    return;
  }

  actionBusy.value = true;
  actionType.value = "extend";

  try {
    const response =
      await adminApi.extenderEdicionPerfil(
        form.id,
        horas
      );

    profileUntil.value =
      response?.profile_edit_until ??
      profileUntil.value;

    profileLocked.value =
      response?.profile_edit_locked ??
      false;

    attemptsLeft.value =
      response?.profile_edit_attempts_left ??
      attemptsLeft.value;

    openNotice({
      title: "Edición extendida",
      message:
        `Se extendió el plazo de edición en ${horas} horas.`,
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    openNotice({
      title: "No se pudo extender",
      message:
        resolveApiError(data) ||
        "No se pudo extender la edición del perfil.",
    });
  } finally {
    actionBusy.value = false;
    actionType.value = "";
  }
};


const handleBloquearEdicion = async () => {
  if (
    !form.id ||
    formBusy.value
  ) {
    return;
  }

  openNotice({
    title: "Confirmar bloqueo",
    message:
      "¿Desea bloquear la edición del perfil para este usuario?",
    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, bloquear",

    onConfirm: async () => {
      actionBusy.value = true;
      actionType.value = "block";

      try {
        const response =
          await adminApi.bloquearEdicionPerfil(
            form.id,
            blockReason.value
          );

        profileLocked.value =
          response?.profile_edit_locked ??
          true;

        attemptsLeft.value =
          response?.profile_edit_attempts_left ??
          0;

        profileUntil.value =
          response?.profile_edit_until ??
          null;

        openNotice({
          title: "Edición bloqueada",
          message:
            "El usuario no podrá editar su perfil hasta una nueva habilitación.",
        });
      } catch (exception) {
        const data =
          exception?.response?.data;

        openNotice({
          title: "No se pudo bloquear",
          message:
            resolveApiError(data) ||
            "No se pudo bloquear la edición del perfil.",
        });
      } finally {
        actionBusy.value = false;
        actionType.value = "";
      }
    },
  });
};


/* ============================================================
   VALIDACIÓN Y GUARDADO
============================================================ */

const validateForm = () => {
  const nombres =
    normalizeText(form.nombres);

  const apellidos =
    normalizeText(form.apellidos);

  const email =
    cleanEmail(form.email);

  const identificacion =
    normalizeText(form.identificacion);

  if (
    !nombres ||
    !apellidos ||
    !email
  ) {
    return {
      valid: false,
      message:
        "Complete los campos obligatorios antes de guardar.",
    };
  }

  if (
    props.mode === "create" &&
    !identificacion
  ) {
    return {
      valid: false,
      message:
        "Ingrese el número de cédula del usuario externo.",
    };
  }

  if (
    identificacion &&
    !/^\d{10}$/.test(identificacion)
  ) {
    return {
      valid: false,
      message:
        "La cédula debe contener exactamente 10 dígitos numéricos.",
    };
  }

  if (
    showAcademicoSection.value &&
    (
      !toPositiveId(form.facultad) ||
      !toPositiveId(form.carrera)
    )
  ) {
    return {
      valid: false,
      message:
        "Seleccione la Facultad y la Carrera del usuario institucional.",
    };
  }

  return {
    valid: true,
    nombres,
    apellidos,
    email,
    identificacion:
      identificacion || null,
  };
};


const submit = async () => {
  if (formBusy.value) {
    return;
  }

  error.value = "";

  const validation =
    validateForm();

  if (!validation.valid) {
    error.value =
      validation.message;

    return;
  }

  saving.value = true;

  try {
    if (props.mode === "create") {
      await adminApi.crearUsuario({
        nombres:
          validation.nombres,

        apellidos:
          validation.apellidos,

        email:
          validation.email,

        identificacion:
          validation.identificacion,
      });

      emit("done", {
        title: "Usuario registrado",
        message:
          "La cuenta externa se registró como pendiente. Para permitir el acceso, utilice Pendientes → Activar cuenta.",
      });

      return;
    }

    if (!form.id) {
      throw new Error(
        "No se pudo determinar el usuario que se editará."
      );
    }

    const payload = {
      nombres:
        validation.nombres,

      apellidos:
        validation.apellidos,

      identificacion:
        validation.identificacion,

      /*
        El backend espera is_staff.

        No debe utilizarse el nombre anterior is_staff_set.
      */
      is_staff:
        Boolean(form.is_staff),
    };

    /*
      El correo institucional no puede editarse desde este
      panel porque se administra mediante Microsoft.
    */
    if (!emailLocked.value) {
      payload.email =
        validation.email;
    }

    /*
      Facultad y Carrera solo se envían para una cuenta
      institucional Microsoft.
    */
    if (showAcademicoSection.value) {
      payload.facultad =
        toPositiveId(
          form.facultad
        );

      payload.carrera =
        toPositiveId(
          form.carrera
        );
    }

    await adminApi.editarUsuario(
      form.id,
      payload
    );

    emit("done", {
      title: "Cambios guardados",
      message:
        "Los datos y permisos del usuario se actualizaron correctamente.",
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    error.value =
      resolveApiError(data) ||
      exception?.message ||
      "No se pudo guardar la información.";

    openNotice({
      title: "No se pudo guardar",
      message: error.value,
      details: data || null,
    });
  } finally {
    saving.value = false;
  }
};


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(() => {
  previouslyFocusedElement =
    document.activeElement;

  previousBodyOverflow =
    document.body.style.overflow;

  document.body.style.overflow =
    "hidden";

  focusInitialControl();
});


onBeforeUnmount(() => {
  document.body.style.overflow =
    previousBodyOverflow;

  if (
    previouslyFocusedElement instanceof
    HTMLElement
  ) {
    previouslyFocusedElement.focus();
  }
});
</script>

<style src="../styles/admin-shared.css"></style>
<style
  scoped
  src="./usuario-modal.css"
></style>