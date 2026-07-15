<template>
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
      aria-describedby="activate-dialog-description"
      :aria-busy="saving"
      tabindex="-1"
      @keydown="handleDialogKeydown"
    >
      <!-- =====================================================
           ENCABEZADO
      ====================================================== -->
      <header class="modal__header activate-header">
        <div class="activate-heading">
          <span class="activate-kicker">
            Gestión de usuarios
          </span>

          <h2
            id="activate-dialog-title"
            class="modal__title activate-title"
          >
            Activar cuenta
          </h2>

          <p
            id="activate-dialog-description"
            class="modal__subtitle activate-subtitle"
          >
            Defina las credenciales de acceso para habilitar la cuenta
            del usuario externo.
          </p>
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
                  <span class="activate-user-card__eyebrow">
                    Cuenta seleccionada
                  </span>

                  <h3
                    id="activate-user-title"
                    class="activate-user-card__name"
                  >
                    {{ nombreCompleto }}
                  </h3>
                </div>

                <span class="activate-status">
                  Pendiente
                </span>
              </div>

              <dl class="activate-meta">
                <div class="activate-meta__item">
                  <dt>Identificación</dt>

                  <dd>
                    {{
                      usuario?.identificacion ||
                      "No registrada"
                    }}
                  </dd>
                </div>

                <div class="activate-meta__item">
                  <dt>Tipo de cuenta</dt>
                  <dd>Usuario externo</dd>
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

                <p class="activate-section__subtitle">
                  El correo y la contraseña permitirán que el usuario
                  inicie sesión en el sistema.
                </p>
              </div>
            </div>

            <div class="activate-grid">
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
                  maxlength="254"
                  placeholder="usuario@correo.com"
                  autocomplete="email"
                  inputmode="email"
                  :disabled="saving"
                  :aria-invalid="Boolean(error) && !emailValid"
                  aria-describedby="activate-email-help"
                />

                <p
                  id="activate-email-help"
                  class="activate-help"
                >
                  Se utilizará como identificador para iniciar sesión.
                </p>
              </div>

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
                    :type="showPassword ? 'text' : 'password'"
                    required
                    minlength="8"
                    maxlength="128"
                    placeholder="Mínimo 8 caracteres"
                    autocomplete="new-password"
                    :disabled="saving"
                    :aria-invalid="
                      Boolean(error) &&
                      password.length > 0 &&
                      password.length < 8
                    "
                    aria-describedby="activate-password-help"
                  />

                  <button
                    type="button"
                    class="activate-password__toggle"
                    :disabled="saving"
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
                    @click="showPassword = !showPassword"
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
                    Debe contener al menos 8 caracteres.
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
                La cuenta quedará activa inmediatamente después de
                guardar. Comparta las credenciales únicamente con el
                usuario correspondiente.
              </p>
            </div>
          </section>

          <!-- =================================================
               ERROR
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
              <strong>No se pudo activar la cuenta</strong>
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
            :disabled="saving || !canSubmit"
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
import { useNotice } from "../../scripts/composables/useNotice";

const props = defineProps({
  usuario: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "done"]);

const { openNotice } = useNotice();

const dialogRef = ref(null);
const emailInputRef = ref(null);

const saving = ref(false);
const error = ref("");

const email = ref("");
const password = ref("");
const showPassword = ref(false);

let previouslyFocusedElement = null;
let previousBodyOverflow = "";

const cleanEmail = (value) =>
  String(value || "")
    .trim()
    .toLowerCase();

const nombreCompleto = computed(() => {
  const nombres = String(
    props.usuario?.nombres || ""
  ).trim();

  const apellidos = String(
    props.usuario?.apellidos || ""
  ).trim();

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
    .map((part) => part.charAt(0).toUpperCase())
    .join("");

  return initials || "U";
});

const emailValid = computed(() => {
  const value = cleanEmail(email.value);

  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
});

const passwordStatusLabel = computed(() => {
  const length = String(password.value || "").length;

  if (length === 0) return "";
  if (length < 8) return "Contraseña incompleta";
  if (length < 12) return "Contraseña válida";

  return "Contraseña reforzada";
});

const passwordStatusClass = computed(() => {
  const length = String(password.value || "").length;

  if (length < 8) {
    return "activate-password-status--invalid";
  }

  if (length < 12) {
    return "activate-password-status--valid";
  }

  return "activate-password-status--strong";
});

const canSubmit = computed(() => {
  return (
    Boolean(props.usuario?.id) &&
    emailValid.value &&
    String(password.value || "").length >= 8
  );
});

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

  for (const key of [
    "email",
    "password",
    "non_field_errors",
  ]) {
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

  const firstKey = Object.keys(
    data || {}
  )[0];

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
  if (saving.value) return;

  emit("close");
};

const getFocusableElements = () => {
  if (!dialogRef.value) return [];

  const selector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled]):not([type='hidden'])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  return Array.from(
    dialogRef.value.querySelectorAll(selector)
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

  if (
    emailInputRef.value instanceof HTMLElement
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
   SINCRONIZACIÓN
============================================================ */

watch(
  () => props.usuario,
  (usuario) => {
    error.value = "";
    password.value = "";
    showPassword.value = false;
    email.value = cleanEmail(usuario?.email);
  },
  {
    immediate: true,
  }
);

/* ============================================================
   ACTIVACIÓN
============================================================ */

const activar = async () => {
  if (saving.value) return;

  error.value = "";

  if (!props.usuario?.id) {
    error.value =
      "No se pudo identificar al usuario seleccionado.";

    return;
  }

  const mail = cleanEmail(email.value);
  const pass = String(
    password.value || ""
  ).trim();

  if (!mail || !pass) {
    error.value =
      "Complete el correo electrónico y la contraseña.";

    return;
  }

  if (!emailValid.value) {
    error.value =
      "Ingrese un correo electrónico válido.";

    await nextTick();
    emailInputRef.value?.focus();

    return;
  }

  if (pass.length < 8) {
    error.value =
      "La contraseña debe tener al menos 8 caracteres.";

    return;
  }

  saving.value = true;

  try {
    await adminApi.activarUsuario(
      props.usuario.id,
      {
        email: mail,
        password: pass,
      }
    );

    emit("done", {
      title: "Cuenta activada",
      message:
        `La cuenta de ${nombreCompleto.value} fue activada correctamente.`,
    });
  } catch (exception) {
    const data =
      exception?.response?.data;

    error.value =
      resolveApiError(data) ||
      "No se pudo activar la cuenta. Verifique la información e intente nuevamente.";

    openNotice({
      title: "No se pudo activar",
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
<style scoped src="./activar-usuario-modal.css"></style>