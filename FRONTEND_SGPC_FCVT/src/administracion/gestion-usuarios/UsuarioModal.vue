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
              <span class="usermodal-badge usermodal-badge--neutral">
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
                : "Actualice los datos personales, la asignación académica y los permisos del usuario."
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

      <form
        class="usermodal-form"
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
                  maxlength="150"
                  placeholder="Ej.: Andrea Sofía"
                  autocomplete="given-name"
                  :disabled="formBusy"
                />
              </div>

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
                  maxlength="150"
                  placeholder="Ej.: García López"
                  autocomplete="family-name"
                  :disabled="formBusy"
                />
              </div>

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
                  :class="{ 'input-readonly': emailLocked }"
                  name="email"
                  type="email"
                  required
                  maxlength="254"
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
                  Cuenta institucional: el correo no se modifica desde
                  este panel.
                </p>
              </div>

              <div class="usermodal-field">
                <label
                  class="usermodal-label usermodal-label--with-help"
                  for="usermodal-identificacion"
                >
                  <span class="usermodal-label__text">
                    Identificación

                    <span
                      v-if="mode === 'create'"
                      class="usermodal-required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </span>

                  <InfoTip title="Identificación">
                    Dato único para evitar duplicados. Debe tener 10
                    dígitos numéricos.
                  </InfoTip>
                </label>

                <input
                  id="usermodal-identificacion"
                  v-model="form.identificacion"
                  class="field-control usermodal-input"
                  name="identificacion"
                  type="text"
                  :required="mode === 'create'"
                  maxlength="10"
                  pattern="[0-9]{10}"
                  placeholder="Ej.: 1312345678"
                  autocomplete="off"
                  inputmode="numeric"
                  aria-describedby="usermodal-identificacion-help"
                  :disabled="formBusy"
                />

                <p
                  id="usermodal-identificacion-help"
                  class="usermodal-help"
                >
                  Solo números, sin espacios ni guiones.
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
                  Complete o corrija la facultad y carrera asignadas al
                  usuario institucional.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
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
                  :disabled="formBusy || loadingCatalogos"
                  :aria-busy="loadingCatalogos"
                  :aria-describedby="
                    loadingCatalogos
                      ? 'usermodal-facultad-status'
                      : undefined
                  "
                  @change="onFacultadChange"
                >
                  <option value="">
                    Seleccione una facultad
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
                    Seleccione una carrera
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
                  v-if="form.facultad && loadingCarreras"
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
              v-if="isInstitucional"
              class="usermodal-note usermodal-note--info"
            >
              La autenticación sigue gestionada por Microsoft. Esta
              asignación solo corrige la relación académica interna.
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
                  Habilite, extienda o bloquee la edición del perfil
                  del usuario.
                </p>
              </div>

              <InfoTip title="Control de edición">
                Habilitar desbloquea y reinicia intentos. Extender suma
                horas al plazo. Bloquear impide editar el perfil.
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
                      actionBusy
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
                  Este motivo quedará asociado al bloqueo cuando el
                  servicio lo admita.
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
                  actionBusy
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
                  actionBusy
                    ? "Procesando..."
                    : "Bloquear edición"
                }}
              </button>
            </div>

            <p class="usermodal-help">
              Este control no modifica credenciales Microsoft ni el
              estado activo o inactivo de la cuenta.
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
                  Verifique el tipo de cuenta, estado y privilegios
                  administrativos.
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
                  :disabled="formBusy"
                />

                <span>
                  <strong>Permisos de administración</strong>

                  <small>
                    Actívelo solo si gestionará usuarios, catálogos o
                    publicaciones globales.
                  </small>
                </span>
              </label>
            </template>

            <template v-else>
              <p class="usermodal-note usermodal-note--info">
                Los usuarios externos nuevos se crean sin privilegios
                administrativos.
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
    validator: (value) => ["create", "edit"].includes(value),
  },
  usuario: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close", "done"]);
const { openNotice } = useNotice();

const dialogRef = ref(null);

const saving = ref(false);
const error = ref("");
const actionBusy = ref(false);

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

const dialogTitleId = "usermodal-dialog-title";
const dialogDescriptionId = "usermodal-dialog-description";

const formBusy = computed(
  () => saving.value || actionBusy.value
);

const normalizedAuthSource = computed(() =>
  String(props.usuario?.auth_source || "")
    .trim()
    .toLowerCase()
);

const normalizedRole = computed(() =>
  String(props.usuario?.rol || "")
    .trim()
    .toLowerCase()
);

const isInstitucional = computed(
  () =>
    props.mode === "edit" &&
    normalizedAuthSource.value === "microsoft"
);

const isExterno = computed(() => {
  if (props.mode === "create") return true;

  return (
    normalizedAuthSource.value === "local" &&
    normalizedRole.value === "autor_externo"
  );
});

const isPendiente = computed(() => {
  if (props.mode === "create") return true;

  return (
    isExterno.value &&
    !props.usuario?.is_active
  );
});

const emailLocked = computed(
  () =>
    props.mode === "edit" &&
    isInstitucional.value
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

  return props.usuario?.is_active
    ? "Activo"
    : "Inactivo";
});

const estadoBadgeClass = computed(() => {
  const value = String(estadoLabel.value || "")
    .toLowerCase()
    .trim();

  if (value.includes("pend")) {
    return "usermodal-badge--warn";
  }

  if (value.includes("inactivo")) {
    return "usermodal-badge--off";
  }

  if (value.includes("activo")) {
    return "usermodal-badge--ok";
  }

  return "usermodal-badge--neutral";
});

const showAcademicoSection = computed(() => {
  if (props.mode !== "edit") return false;

  return !isExterno.value;
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

  return String(attemptsLeft.value);
});

const uiProfileUntilLabel = computed(() => {
  if (!profileUntil.value) return "—";

  try {
    const date = new Date(profileUntil.value);

    if (Number.isNaN(date.getTime())) {
      return String(profileUntil.value);
    }

    return new Intl.DateTimeFormat("es-EC", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  } catch {
    return String(profileUntil.value);
  }
});

const toSelectOptions = (items) => {
  if (!Array.isArray(items)) return [];

  return items.map((item) => ({
    value: item.id ?? item.value,
    label:
      item.nombre ??
      item.label ??
      String(item),
  }));
};

const resolveApiError = (data) => {
  if (!data) return "";

  if (
    typeof data?.detail === "string" &&
    data.detail
  ) {
    return data.detail;
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
  }

  const firstKey = Object.keys(data || {})[0];

  const firstValue = firstKey
    ? data[firstKey]
    : null;

  if (
    Array.isArray(firstValue) &&
    firstValue[0]
  ) {
    return String(firstValue[0]);
  }

  if (
    typeof firstValue === "string" &&
    firstValue
  ) {
    return firstValue;
  }

  return "";
};

/* ============================================================
   ACCESIBILIDAD DEL MODAL
============================================================ */

const requestClose = () => {
  if (formBusy.value) return;

  emit("close");
};

const getFocusableElements = () => {
  const dialog = dialogRef.value;

  if (!dialog) return [];

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
  ).filter(
    (element) =>
      !element.hasAttribute("hidden") &&
      element.getAttribute("aria-hidden") !== "true" &&
      element.getClientRects().length > 0
  );
};

const focusInitialControl = async () => {
  await nextTick();

  const preferredControl =
    dialogRef.value?.querySelector(
      "#usermodal-nombres:not([disabled])"
    );

  if (preferredControl instanceof HTMLElement) {
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

  if (event.key !== "Tab") return;

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
   CATÁLOGOS
============================================================ */

const loadFacultades = async () => {
  loadingCatalogos.value = true;

  try {
    const data =
      await adminApi.selectsFacultades();

    facultades.value =
      toSelectOptions(data);
  } catch {
    facultades.value = [];

    error.value =
      "No se pudieron cargar las facultades.";
  } finally {
    loadingCatalogos.value = false;
  }
};

const loadCarreras = async (facultadId) => {
  carreras.value = [];

  if (!facultadId) return;

  loadingCarreras.value = true;

  try {
    const data =
      await adminApi.selectsCarrerasByFacultad(
        facultadId
      );

    carreras.value =
      toSelectOptions(data);
  } catch {
    carreras.value = [];

    error.value =
      "No se pudieron cargar las carreras.";
  } finally {
    loadingCarreras.value = false;
  }
};

const onFacultadChange = async () => {
  form.carrera = "";

  await loadCarreras(form.facultad);
};

/* ============================================================
   CARGA DEL USUARIO
============================================================ */

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

      return;
    }

    if (!usuario) return;

    form.id = usuario.id;
    form.nombres = usuario.nombres || "";
    form.apellidos = usuario.apellidos || "";
    form.email = usuario.email || "";
    form.identificacion =
      usuario.identificacion || "";
    form.is_staff =
      Boolean(usuario.is_staff);
    form.facultad =
      usuario.facultad ?? "";
    form.carrera =
      usuario.carrera ?? "";

    profileLocked.value =
      usuario.profile_edit_locked ?? null;

    attemptsLeft.value =
      usuario.profile_edit_attempts_left ?? null;

    profileUntil.value =
      usuario.profile_edit_until ?? null;

    extendHours.value = 24;
    blockReason.value = "";

    if (showAcademicoSection.value) {
      await loadFacultades();

      if (form.facultad) {
        await loadCarreras(
          form.facultad
        );
      }
    } else {
      facultades.value = [];
      carreras.value = [];
    }
  },
  {
    immediate: true,
  }
);

/* ============================================================
   CONTROL DE EDICIÓN DEL PERFIL
============================================================ */

const handleHabilitarEdicion = async () => {
  if (
    !form.id ||
    formBusy.value
  ) {
    return;
  }

  actionBusy.value = true;

  try {
    const response =
      await adminApi.habilitarEdicionPerfil(
        form.id
      );

    profileLocked.value =
      response?.profile_edit_locked ?? false;

    attemptsLeft.value =
      response?.profile_edit_attempts_left ?? 3;

    profileUntil.value =
      response?.profile_edit_until ?? null;

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
        "No se pudo habilitar la edición del perfil. Intente nuevamente.",
    });
  } finally {
    actionBusy.value = false;
  }
};

const handleExtenderEdicion = async () => {
  if (
    !form.id ||
    formBusy.value
  ) {
    return;
  }

  actionBusy.value = true;

  try {
    const horas = Number(
      extendHours.value || 24
    );

    const response =
      await adminApi.extenderEdicionPerfil(
        form.id,
        horas
      );

    if (
      response &&
      typeof response === "object"
    ) {
      if (
        "profile_edit_until" in response
      ) {
        profileUntil.value =
          response.profile_edit_until;
      }

      if (
        "profile_edit_locked" in response
      ) {
        profileLocked.value =
          Boolean(
            response.profile_edit_locked
          );
      }

      if (
        "profile_edit_attempts_left" in
        response
      ) {
        attemptsLeft.value =
          response.profile_edit_attempts_left;
      }
    }

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
        "No se pudo extender la edición del perfil. Intente nuevamente.",
    });
  } finally {
    actionBusy.value = false;
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
      "¿Desea bloquear la edición del perfil para este usuario? Podrá habilitarla nuevamente cuando lo necesite.",
    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, bloquear",

    onConfirm: async () => {
      actionBusy.value = true;

      try {
        const response =
          await adminApi.bloquearEdicionPerfil(
            form.id,
            blockReason.value
          );

        profileLocked.value =
          response?.profile_edit_locked ?? true;

        attemptsLeft.value =
          response?.profile_edit_attempts_left ?? 0;

        profileUntil.value =
          response?.profile_edit_until ?? null;

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
            "No se pudo bloquear la edición del perfil. Intente nuevamente.",
        });
      } finally {
        actionBusy.value = false;
      }
    },
  });
};

/* ============================================================
   GUARDADO
============================================================ */

const submit = async () => {
  if (formBusy.value) return;

  error.value = "";
  saving.value = true;

  try {
    const nombres = String(
      form.nombres || ""
    ).trim();

    const apellidos = String(
      form.apellidos || ""
    ).trim();

    const email = String(
      form.email || ""
    )
      .trim()
      .toLowerCase();

    const identificacionRaw = String(
      form.identificacion || ""
    ).trim();

    const identificacion =
      identificacionRaw || null;

    if (
      !nombres ||
      !apellidos ||
      !email
    ) {
      error.value =
        "Complete los campos obligatorios antes de guardar.";

      return;
    }

    if (
      props.mode === "create" &&
      !identificacion
    ) {
      error.value =
        "Ingrese la identificación del usuario externo.";

      return;
    }

    if (
      identificacion &&
      !/^\d+$/.test(identificacion)
    ) {
      error.value =
        "La identificación debe contener solo números.";

      return;
    }

    if (
      identificacion &&
      identificacion.length !== 10
    ) {
      error.value =
        "La identificación debe tener 10 dígitos numéricos.";

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
        message:
          "Se registró correctamente. Para permitir el acceso, utilice Pendientes → Activar cuenta.",
      });

      return;
    }

    if (!form.id) {
      throw new Error(
        "ID faltante en edición."
      );
    }

    const payload = {
      nombres,
      apellidos,
      email,
      identificacion,
      is_staff_set:
        Boolean(form.is_staff),
    };

    if (showAcademicoSection.value) {
      const facultad = form.facultad
        ? Number(form.facultad)
        : null;

      const carrera = form.carrera
        ? Number(form.carrera)
        : null;

      if (
        !facultad ||
        !carrera
      ) {
        error.value =
          "Seleccione facultad y carrera para completar la asignación académica.";

        return;
      }

      payload.facultad = facultad;
      payload.carrera = carrera;
    }

    await adminApi.editarUsuario(
      form.id,
      payload
    );

    emit("done", {
      title: "Cambios guardados",
      message:
        "Los datos del usuario se actualizaron correctamente.",
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    error.value =
      resolveApiError(data) ||
      "No se pudo guardar la información.";

    openNotice({
      title: "No se pudo guardar",
      message: error.value,
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
<style scoped src="./usuario-modal.css"></style>