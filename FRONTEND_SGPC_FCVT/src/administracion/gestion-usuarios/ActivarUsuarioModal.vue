<template>
  <Teleport to="body">
    <div
      class="sgpc-admin-modal modal-overlay"
      @click.self="requestClose"
    >
      <div
        ref="dialogRef"
        class="modal modal--activate"
        role="dialog"
        aria-modal="true"
        aria-labelledby="activate-dialog-title"
                :aria-busy="saving"
        tabindex="-1"
        @keydown="handleDialogKeydown"
      >
        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->
        <header class="modal__header activate-header">
          <div class="activate-heading">
            <h2
              id="activate-dialog-title"
              class="modal__title activate-title"
            >
              Activar cuenta
            </h2>

          </div>

          <button
            type="button"
            class="btn-cerrar modal__close activate-close"
            :disabled="saving"
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
          class="activate-form"
          novalidate
          @submit.prevent="activar"
        >
          <div class="activate-body">
            <!-- =================================================
                 RESUMEN DEL USUARIO
            ================================================== -->
            <section
              class="activate-user-card"
              aria-labelledby="activate-user-title"
            >
              <div
                class="activate-user-card__avatar"
                aria-hidden="true"
              >
                {{ userInitials }}
              </div>

              <div class="activate-user-card__content">
                <div class="activate-user-card__heading">
                  <div>
                    <h3
                      id="activate-user-title"
                      class="activate-user-card__name"
                    >
                      {{ nombreCompleto }}
                    </h3>
                  </div>

                  <span
                    class="activate-status"
                    :class="{
                      'activate-status--invalid':
                        Boolean(targetValidationMessage),
                    }"
                  >
                    {{ estadoCuentaLabel }}
                  </span>
                </div>

                <dl class="activate-meta">
                  <div class="activate-meta__item">
                    <dt>Cédula</dt>

                    <dd>
                      {{
                        usuario?.identificacion ||
                        "No registrada"
                      }}
                    </dd>
                  </div>

                  <div class="activate-meta__item">
                    <dt>Tipo</dt>

                    <dd>{{ tipoCuentaLabel }}</dd>
                  </div>

                  <div class="activate-meta__item">
                    <dt>Correo actual</dt>

                    <dd>
                      {{
                        usuario?.email ||
                        "No registrado"
                      }}
                    </dd>
                  </div>
                </dl>
              </div>
            </section>

            <!-- =================================================
                 INCONSISTENCIA DE LA CUENTA
            ================================================== -->
            <div
              v-if="targetValidationMessage"
              class="activate-error"
              role="alert"
              aria-live="assertive"
            >
              <span
                class="activate-error__icon"
                aria-hidden="true"
              >
                !
              </span>

              <div>
                <strong>
                  La cuenta no puede activarse
                </strong>

                <p>
                  {{ targetValidationMessage }}
                </p>
              </div>
            </div>

            <!-- =================================================
                 CREDENCIALES
            ================================================== -->
            <section
              class="activate-section"
              aria-labelledby="activate-access-title"
            >
              <div class="activate-section__head">
                <div>
                  <h3
                    id="activate-access-title"
                    class="activate-section__title"
                  >
                    Datos de acceso
                  </h3>

                </div>
              </div>

              <div class="activate-grid">
                <!-- CORREO -->
                <div class="activate-field">
                  <label
                    for="activate-email"
                    class="activate-label"
                  >
                    <span>Correo electrónico</span>

                    <span
                      class="activate-required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <input
                    id="activate-email"
                    ref="emailInputRef"
                    v-model="email"
                    class="field-control activate-input"
                    name="email"
                    type="email"
                    required
                    maxlength="150"
                    placeholder="usuario@correo.com"
                    autocomplete="email"
                    inputmode="email"
                    :disabled="
                      saving ||
                      Boolean(targetValidationMessage)
                    "
                    :aria-invalid="
                      Boolean(email) &&
                      !emailValid
                    "
                  />

                </div>

                <!-- CONTRASEÑA -->
                <div class="activate-field">
                  <label
                    for="activate-password"
                    class="activate-label"
                  >
                    <span>Contraseña temporal</span>

                    <span
                      class="activate-required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <div class="activate-password">
                    <input
                      id="activate-password"
                      v-model="password"
                      class="field-control activate-input activate-password__input"
                      name="password"
                      :type="
                        showPassword
                          ? 'text'
                          : 'password'
                      "
                      required
                      minlength="8"
                      maxlength="128"
                      placeholder="Mínimo 8 caracteres"
                      autocomplete="new-password"
                      :disabled="
                        saving ||
                        Boolean(targetValidationMessage)
                      "
                      :aria-invalid="
                        Boolean(password) &&
                        !passwordValid
                      "
                      aria-describedby="activate-password-help"
                    />

                    <button
                      type="button"
                      class="activate-password__toggle"
                      :disabled="
                        saving ||
                        Boolean(targetValidationMessage)
                      "
                      :aria-label="
                        showPassword
                          ? 'Ocultar contraseña'
                          : 'Mostrar contraseña'
                      "
                      :title="
                        showPassword
                          ? 'Ocultar contraseña'
                          : 'Mostrar contraseña'
                      "
                      @click="
                        showPassword = !showPassword
                      "
                    >
                      <svg
                        v-if="!showPassword"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path
                          fill="currentColor"
                          d="M12 5c5.5 0 9.5 5.2 9.7 5.4a1 1 0 0 1 0 1.2C21.5 11.8 17.5 17 12 17S2.5 11.8 2.3 11.6a1 1 0 0 1 0-1.2C2.5 10.2 6.5 5 12 5Zm0 2c-3.6 0-6.6 3-7.6 4 1 1 4 4 7.6 4s6.6-3 7.6-4c-1-1-4-4-7.6-4Zm0 1.5A2.5 2.5 0 1 1 9.5 11 2.5 2.5 0 0 1 12 8.5Z"
                        />
                      </svg>

                      <svg
                        v-else
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path
                          fill="currentColor"
                          d="m3.7 2.3 18 18-1.4 1.4-3.1-3.1A11.7 11.7 0 0 1 12 20c-5.5 0-9.5-5.2-9.7-5.4a1 1 0 0 1 0-1.2 19 19 0 0 1 4-3.8L2.3 3.7 3.7 2.3Zm4 8.7a14.8 14.8 0 0 0-3.3 3c1 1 4 4 7.6 4a9.8 9.8 0 0 0 3.7-.8l-1.6-1.6a4 4 0 0 1-5.7-5.7L7.7 11Zm4.1-5c5.5 0 9.5 5.2 9.7 5.4a1 1 0 0 1 0 1.2 18.3 18.3 0 0 1-2.6 2.8l-1.4-1.4a15.7 15.7 0 0 0 1.9-2c-1-1-4-4-7.6-4a9.4 9.4 0 0 0-1.9.2L8.3 6.6A11.8 11.8 0 0 1 11.8 6Zm.2 4a2 2 0 0 1 2 2v.3l-2.3-2.3h.3Z"
                        />
                      </svg>
                    </button>
                  </div>

                  <div
                    id="activate-password-help"
                    class="activate-password-help"
                  >
                    <p class="activate-help">
                      8–128 caracteres.
                    </p>

                    <span
                      v-if="password"
                      class="activate-password-status"
                      :class="passwordStatusClass"
                      aria-live="polite"
                    >
                      {{ passwordStatusLabel }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="activate-note">
                <span
                  class="activate-note__icon"
                  aria-hidden="true"
                >
                  i
                </span>

                <p>
                  Comparta las credenciales únicamente con este usuario.
                </p>
              </div>
            </section>

            <!-- =================================================
                 ERROR DEL SERVIDOR
            ================================================== -->
            <div
              v-if="error"
              class="activate-error"
              role="alert"
              aria-live="assertive"
            >
              <span
                class="activate-error__icon"
                aria-hidden="true"
              >
                !
              </span>

              <div>
                <strong>
                  No se pudo activar la cuenta
                </strong>

                <p>{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- ===================================================
               PIE
          ==================================================== -->
          <footer class="modal__footer activate-footer">
            <button
              type="button"
              class="btn-cerrar activate-cancel"
              :disabled="saving"
              @click="requestClose"
            >
              Cancelar
            </button>

            <button
              type="submit"
              class="btn-primary activate-submit"
              :disabled="
                saving ||
                !canSubmit
              "
            >
              <span
                v-if="saving"
                class="activate-spinner"
                aria-hidden="true"
              ></span>

              {{
                saving
                  ? "Activando..."
                  : "Activar cuenta"
              }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

import { adminApi } from "../../scripts/api/adminApi";


const props = defineProps({
  usuario: {
    type: Object,
    required: true,
  },
});


const emit = defineEmits([
  "close",
  "done",
]);




const dialogRef = ref(null);
const emailInputRef = ref(null);

const saving = ref(false);
const error = ref("");

const email = ref("");
const password = ref("");
const showPassword = ref(false);


let previouslyFocusedElement = null;
let previousBodyOverflow = "";


const ROLE_EXTERNAL = "autor_externo";
const AUTH_SOURCE_LOCAL = "local";


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


const hasValidCedula = (value) => {
  return /^\d{10}$/.test(
    normalizeText(value)
  );
};


/* ============================================================
   INFORMACIÓN DEL USUARIO
============================================================ */

const nombreCompleto = computed(() => {
  const nombres = normalizeText(
    props.usuario?.nombres
  );

  const apellidos = normalizeText(
    props.usuario?.apellidos
  );

  return (
    `${nombres} ${apellidos}`.trim() ||
    "Usuario externo"
  );
});


const userInitials = computed(() => {
  const initials = nombreCompleto.value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => {
      return part
        .charAt(0)
        .toUpperCase();
    })
    .join("");

  return initials || "U";
});


const isExternalAccount = computed(() => {
  const role = normalizeAccountValue(
    props.usuario?.rol
  );

  const authSource = normalizeAccountValue(
    props.usuario?.auth_source
  );

  return Boolean(
    role === ROLE_EXTERNAL &&
    authSource === AUTH_SOURCE_LOCAL
  );
});


const isPendingAccount = computed(() => {
  return Boolean(
    isExternalAccount.value &&
    !props.usuario?.is_active
  );
});


const tipoCuentaLabel = computed(() => {
  if (isExternalAccount.value) {
    return "Cuenta externa";
  }

  return "Cuenta con clasificación incompatible";
});


const estadoCuentaLabel = computed(() => {
  if (isPendingAccount.value) {
    return "Pendiente";
  }

  if (props.usuario?.is_active) {
    return "Activa";
  }

  return "No disponible";
});


const targetValidationMessage = computed(() => {
  if (!props.usuario?.id) {
    return (
      "No se pudo determinar el usuario seleccionado."
    );
  }

  if (!isExternalAccount.value) {
    return (
      "Solo las cuentas externas pendientes pueden activarse desde aquí."
    );
  }

  if (props.usuario?.is_active) {
    return (
      "La cuenta seleccionada ya se encuentra activa."
    );
  }

  if (
    !hasValidCedula(
      props.usuario?.identificacion
    )
  ) {
    return (
      "La cuenta debe tener un número de cédula válido de " +
      "exactamente 10 dígitos antes de ser activada."
    );
  }

  return "";
});


/* ============================================================
   VALIDACIÓN DEL FORMULARIO
============================================================ */

const emailValid = computed(() => {
  const value = cleanEmail(
    email.value
  );

  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    value
  );
});


const passwordValid = computed(() => {
  const value = String(
    password.value ?? ""
  );

  return Boolean(
    value.length >= 8 &&
    value.length <= 128 &&
    value.trim().length > 0
  );
});


const passwordStatusLabel = computed(() => {
  const value = String(
    password.value ?? ""
  );

  const length = value.length;

  if (length === 0) {
    return "";
  }

  if (
    length < 8 ||
    value.trim().length === 0
  ) {
    return "Contraseña incompleta";
  }

  if (length < 12) {
    return "Longitud válida";
  }

  return "Longitud reforzada";
});


const passwordStatusClass = computed(() => {
  if (!passwordValid.value) {
    return (
      "activate-password-status--invalid"
    );
  }

  if (
    String(password.value ?? "").length < 12
  ) {
    return (
      "activate-password-status--valid"
    );
  }

  return (
    "activate-password-status--strong"
  );
});


const canSubmit = computed(() => {
  return Boolean(
    !targetValidationMessage.value &&
    emailValid.value &&
    passwordValid.value
  );
});


/* ============================================================
   ERRORES DEL BACKEND
============================================================ */


const sanitizeApiMessage = (value) => {
  const message = String(value ?? "").trim();

  if (!message) {
    return "";
  }

  const technicalPattern =
    /(backend|endpoint|serializer|queryset|traceback|exception|jwt|token|sql|database|constraint|http\s*\d{3}|api\/)/i;

  return technicalPattern.test(message)
    ? ""
    : message;
};

const resolveApiError = (
  data,
  visited = new Set()
) => {
  if (!data) {
    return "";
  }

  if (typeof data === "string") {
    return sanitizeApiMessage(data);
  }

  if (
    typeof data !== "object" ||
    visited.has(data)
  ) {
    return "";
  }

  visited.add(data);

  const priorityKeys = [
    "detail",
    "email",
    "password",
    "identificacion",
    "non_field_errors",
    "error",
  ];

  for (const key of priorityKeys) {
    const value = data?.[key];

    if (
      typeof value === "string" &&
      value
    ) {
      return sanitizeApiMessage(value);
    }

    if (
      Array.isArray(value) &&
      value.length
    ) {
      for (const item of value) {
        const message =
          resolveApiError(
            item,
            visited
          );

        if (message) {
          return message;
        }
      }
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const message =
        resolveApiError(
          value,
          visited
        );

      if (message) {
        return message;
      }
    }
  }

  for (const value of Object.values(data)) {
    const message =
      resolveApiError(
        value,
        visited
      );

    if (message) {
      return message;
    }
  }

  return "";
};


/* ============================================================
   ACCESIBILIDAD DEL MODAL
============================================================ */

const requestClose = () => {
  if (saving.value) {
    return;
  }

  emit("close");
};


const getFocusableElements = () => {
  if (!dialogRef.value) {
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
    dialogRef.value.querySelectorAll(
      selector
    )
  ).filter((element) => {
    return Boolean(
      !element.hasAttribute("hidden") &&
      element.getAttribute("aria-hidden") !== "true" &&
      element.getClientRects().length > 0
    );
  });
};


const focusInitialControl = async () => {
  await nextTick();

  if (
    emailInputRef.value instanceof
    HTMLElement &&
    !emailInputRef.value.disabled
  ) {
    emailInputRef.value.focus();
    emailInputRef.value.select();

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
   SINCRONIZACIÓN DEL USUARIO
============================================================ */

watch(
  () => props.usuario,
  async (usuario) => {
    error.value = "";
    password.value = "";
    showPassword.value = false;

    email.value = cleanEmail(
      usuario?.email
    );

    await focusInitialControl();
  },
  {
    immediate: true,
  }
);


/* ============================================================
   ACTIVACIÓN
============================================================ */

const activar = async () => {
  if (saving.value) {
    return;
  }

  error.value = "";

  if (targetValidationMessage.value) {
    error.value =
      targetValidationMessage.value;

    return;
  }

  const normalizedEmail = cleanEmail(
    email.value
  );

  /*
    La contraseña no debe normalizarse con trim(), porque eso
    modificaría el valor que el administrador escribió.
  */
  const rawPassword = String(
    password.value ?? ""
  );

  if (!emailValid.value) {
    error.value =
      "Ingrese un correo electrónico válido.";

    await nextTick();
    emailInputRef.value?.focus();

    return;
  }

  if (!passwordValid.value) {
    error.value =
      "La contraseña debe contener entre 8 y 128 caracteres y no puede estar vacía.";

    return;
  }

  saving.value = true;

  try {
    const updatedUser =
      await adminApi.activarUsuario(
        props.usuario.id,
        {
          email: normalizedEmail,
          password: rawPassword,
        }
      );

    emit("done", {
      title: "Cuenta activada",
      message:
        `La cuenta de ${nombreCompleto.value} fue activada correctamente.`,
      usuario: updatedUser,
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    error.value =
      resolveApiError(data) ||
      (
        "No pudimos activar la cuenta. " +
        "Revise la información e intente nuevamente."
      );

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
  src="./activar-usuario-modal.css"
></style>