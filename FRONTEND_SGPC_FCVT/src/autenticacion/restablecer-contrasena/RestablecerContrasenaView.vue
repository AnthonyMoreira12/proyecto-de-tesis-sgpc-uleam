<template>
  <div class="auth-container auth-container--reset">
    <main class="auth-wrapper auth-wrapper--reset-scene">
      <div class="reset-shell">
        <section
          class="reset-panel page-stage page-stage-1"
          aria-labelledby="reset-title"
        >
          <div class="reset-panel__brand">
            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              class="reset-panel__brand-logo"
              alt="Logo de la Universidad Laica Eloy Alfaro de Manabí"
            />

            <div class="reset-panel__brand-copy">
              <p class="reset-panel__brand-kicker">
                Universidad Laica Eloy Alfaro de Manabí
              </p>

              <p class="reset-panel__brand-system">
                SGPC ULEAM
              </p>
            </div>
          </div>

          <div class="reset-panel__content">
            <header class="reset-panel__head">
              <h1
                id="reset-title"
                class="reset-panel__title"
              >
                Restablecer contraseña
              </h1>

              <p class="reset-panel__subtitle">
                Cree una nueva contraseña para su cuenta externa.
              </p>
            </header>

            <div
              class="reset-notice"
              role="note"
            >
              <span
                class="reset-notice__icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="9"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />

                  <path
                    d="M12 10.5V16"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />

                  <circle
                    cx="12"
                    cy="7.5"
                    r="1"
                    fill="currentColor"
                  />
                </svg>
              </span>

              <p>
                Las cuentas institucionales ULEAM gestionan su contraseña desde
                Microsoft 365.
              </p>
            </div>

            <section
              v-if="!token"
              class="reset-invalid"
              aria-live="polite"
              role="status"
            >
              <span
                class="reset-invalid__icon"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  focusable="false"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="9"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />

                  <path
                    d="M12 7.5V13"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />

                  <circle
                    cx="12"
                    cy="16.5"
                    r="1"
                    fill="currentColor"
                  />
                </svg>
              </span>

              <div class="reset-invalid__copy">
                <h2>Enlace no válido</h2>

                <p>
                  El enlace de recuperación no fue encontrado o ya no es válido.
                  Solicite uno nuevo para continuar.
                </p>
              </div>

              <div class="reset-invalid__actions">
                <button
                  class="reset-button reset-button--primary"
                  type="button"
                  @click="goRequestRecovery"
                >
                  Solicitar nuevo enlace
                </button>

                <button
                  class="reset-button reset-button--secondary"
                  type="button"
                  @click="goLogin"
                >
                  Volver al inicio de sesión
                </button>
              </div>
            </section>

            <form
              v-else
              class="reset-form"
              novalidate
              @submit.prevent="submitReset"
            >
              <div
                class="input-group reset-field"
                :class="{ invalid: Boolean(errors.new_password) }"
              >
                <label
                  class="reset-field__label"
                  for="reset-new-password"
                >
                  Nueva contraseña
                </label>

                <div class="reset-password-box">
                  <input
                    id="reset-new-password"
                    ref="passwordInputRef"
                    v-model="newPassword"
                    class="reset-field__control"
                    :type="showNewPassword ? 'text' : 'password'"
                    placeholder="Ingrese una nueva contraseña"
                    autocomplete="new-password"
                    :aria-invalid="Boolean(errors.new_password)"
                    :aria-describedby="
                      errors.new_password
                        ? 'reset-new-password-error pw-help'
                        : 'pw-help'
                    "
                    @input="clearError('new_password')"
                  />

                  <button
                    class="reset-password-box__toggle"
                    type="button"
                    :aria-label="
                      showNewPassword
                        ? 'Ocultar nueva contraseña'
                        : 'Mostrar nueva contraseña'
                    "
                    :aria-pressed="showNewPassword"
                    @click="showNewPassword = !showNewPassword"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <path
                        d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="3"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                      />

                      <path
                        v-if="showNewPassword"
                        d="M4 4l16 16"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>

                <div
                  id="pw-help"
                  class="pw-meta"
                >
                  <div
                    class="pw-meter"
                    aria-label="Nivel de seguridad de la contraseña"
                  >
                    <div
                      class="pw-meter__bar"
                      :class="strengthClass"
                      :style="{ width: `${strengthPercentage}%` }"
                    ></div>
                  </div>

                  <p class="pw-meter__text">
                    Seguridad:
                    <strong>{{ strengthLabel }}</strong>
                  </p>
                </div>

                <p
                  v-if="errors.new_password"
                  id="reset-new-password-error"
                  class="reset-field__error"
                  aria-live="polite"
                >
                  {{ errors.new_password }}
                </p>
              </div>

              <div
                class="input-group reset-field"
                :class="{ invalid: Boolean(errors.confirm_password) }"
              >
                <label
                  class="reset-field__label"
                  for="reset-confirm-password"
                >
                  Confirmar contraseña
                </label>

                <div class="reset-password-box">
                  <input
                    id="reset-confirm-password"
                    v-model="confirmPassword"
                    class="reset-field__control"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Repita la nueva contraseña"
                    autocomplete="new-password"
                    :aria-invalid="Boolean(errors.confirm_password)"
                    :aria-describedby="
                      errors.confirm_password
                        ? 'reset-confirm-password-error'
                        : undefined
                    "
                    @input="clearError('confirm_password')"
                  />

                  <button
                    class="reset-password-box__toggle"
                    type="button"
                    :aria-label="
                      showConfirmPassword
                        ? 'Ocultar confirmación de contraseña'
                        : 'Mostrar confirmación de contraseña'
                    "
                    :aria-pressed="showConfirmPassword"
                    @click="showConfirmPassword = !showConfirmPassword"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <path
                        d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="3"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                      />

                      <path
                        v-if="showConfirmPassword"
                        d="M4 4l16 16"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>

                <p
                  v-if="errors.confirm_password"
                  id="reset-confirm-password-error"
                  class="reset-field__error"
                  aria-live="polite"
                >
                  {{ errors.confirm_password }}
                </p>
              </div>

              <div
                class="pw-checklist"
                aria-label="Requisitos de la contraseña"
              >
                <p class="pw-checklist__title">
                  La contraseña debe incluir
                </p>

                <ul class="pw-checklist__grid">
                  <li :class="{ ok: rules.len8 }">
                    8 caracteres o más
                  </li>

                  <li :class="{ ok: rules.letter }">
                    Al menos una letra
                  </li>

                  <li :class="{ ok: rules.number }">
                    Al menos un número
                  </li>

                  <li :class="{ ok: rules.mixed }">
                    Mayúsculas y minúsculas
                  </li>

                  <li :class="{ ok: rules.notCommon }">
                    No ser una contraseña común
                  </li>
                </ul>
              </div>

              <div
                v-if="status.type"
                class="reset-status"
                :class="`is-${status.type}`"
                aria-live="polite"
                role="status"
              >
                {{ status.message }}
              </div>

              <div class="reset-actions">
                <button
                  class="reset-button reset-button--primary"
                  type="submit"
                  :disabled="loading"
                >
                  {{
                    loading
                      ? "Actualizando..."
                      : "Guardar nueva contraseña"
                  }}
                </button>

                <button
                  class="reset-button reset-button--secondary"
                  type="button"
                  :disabled="loading"
                  @click="goLogin"
                >
                  Volver al inicio de sesión
                </button>
              </div>
            </form>
          </div>
        </section>

        <aside
          class="reset-visual page-stage page-stage-2"
          aria-hidden="true"
        >
          <span class="reset-visual__glow reset-visual__glow--one"></span>
          <span class="reset-visual__glow reset-visual__glow--two"></span>

          <div class="reset-visual__content">
            <div class="reset-visual__icon">
              <svg
                viewBox="0 0 24 24"
                focusable="false"
              >
                <path
                  d="M7.5 10V7.8a4.5 4.5 0 0 1 9 0V10"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />

                <rect
                  x="5"
                  y="10"
                  width="14"
                  height="10"
                  rx="2.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />

                <path
                  d="M12 14v2.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
            </div>

            <div class="reset-visual__copy">
              <h2 class="reset-visual__title">
                Proteja su cuenta
              </h2>

              <p class="reset-visual__description">
                Utilice una contraseña segura y diferente de las que emplea en
                otros servicios.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  nextTick,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const token = computed(() => {
  return route.query.token
    ? String(route.query.token)
    : "";
});

const newPassword = ref("");
const confirmPassword = ref("");

const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const errors = ref({});
const loading = ref(false);

const status = ref({
  type: "",
  message: "",
});

const passwordInputRef = ref(null);

const commonPasswords = [
  "123456",
  "12345678",
  "password",
  "qwerty",
  "111111",
  "123123",
  "admin",
  "12345",
  "abc123",
  "password1",
];

const clearObjectField = (targetRef, field) => {
  const copy = { ...targetRef.value };

  delete copy[field];

  targetRef.value = copy;
};

const clearError = (field) => {
  clearObjectField(errors, field);

  status.value = {
    type: "",
    message: "",
  };
};

const rules = computed(() => {
  const password = newPassword.value || "";

  const len8 = password.length >= 8;
  const letter = /[a-zA-Z]/.test(password);
  const number = /\d/.test(password);
  const upper = /[A-Z]/.test(password);
  const lower = /[a-z]/.test(password);
  const mixed = upper && lower;

  const notCommon =
    password.length > 0 &&
    !commonPasswords.includes(password.toLowerCase());

  return {
    len8,
    letter,
    number,
    mixed,
    notCommon,
  };
});

const strengthScore = computed(() => {
  const password = newPassword.value || "";

  if (!password) {
    return 0;
  }

  let score = 0;

  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^a-zA-Z0-9]/.test(password)) score += 1;

  if (
    !commonPasswords.includes(
      password.toLowerCase()
    )
  ) {
    score += 1;
  }

  return Math.min(score, 7);
});

const strengthPercentage = computed(() => {
  return (strengthScore.value / 7) * 100;
});

const strengthLabel = computed(() => {
  const score = strengthScore.value;

  if (score === 0) return "Sin evaluar";
  if (score <= 2) return "Baja";
  if (score <= 4) return "Media";
  if (score <= 6) return "Alta";

  return "Muy alta";
});

const strengthClass = computed(() => {
  const score = strengthScore.value;

  if (score <= 2) return "is-low";
  if (score <= 4) return "is-medium";

  return "is-high";
});

const validate = () => {
  const nextErrors = {};

  const password = newPassword.value;
  const confirmation = confirmPassword.value;

  if (!password) {
    nextErrors.new_password =
      "La nueva contraseña es obligatoria.";
  } else if (password.length < 8) {
    nextErrors.new_password =
      "La contraseña debe tener al menos 8 caracteres.";
  } else if (!/[a-zA-Z]/.test(password)) {
    nextErrors.new_password =
      "La contraseña debe incluir al menos una letra.";
  } else if (!/\d/.test(password)) {
    nextErrors.new_password =
      "La contraseña debe incluir al menos un número.";
  } else if (
    !/[A-Z]/.test(password) ||
    !/[a-z]/.test(password)
  ) {
    nextErrors.new_password =
      "La contraseña debe incluir mayúsculas y minúsculas.";
  } else if (
    commonPasswords.includes(
      password.toLowerCase()
    )
  ) {
    nextErrors.new_password =
      "Elija una contraseña menos común.";
  }

  if (!confirmation) {
    nextErrors.confirm_password =
      "Confirme la nueva contraseña.";
  } else if (confirmation !== password) {
    nextErrors.confirm_password =
      "Las contraseñas no coinciden.";
  }

  errors.value = nextErrors;

  return Object.keys(nextErrors).length === 0;
};

const resolveBackendError = (data) => {
  if (!data) {
    return "";
  }

  if (
    typeof data.detail === "string" &&
    data.detail
  ) {
    return data.detail;
  }

  if (
    typeof data.error === "string" &&
    data.error
  ) {
    return data.error;
  }

  const passwordError = data.new_password;

  if (
    Array.isArray(passwordError) &&
    passwordError[0]
  ) {
    return String(passwordError[0]);
  }

  if (
    typeof passwordError === "string" &&
    passwordError
  ) {
    return passwordError;
  }

  return "";
};

const submitReset = async () => {
  status.value = {
    type: "",
    message: "",
  };

  if (!validate()) {
    return;
  }

  loading.value = true;

  status.value = {
    type: "info",
    message: "Actualizando contraseña...",
  };

  try {
    await api.post(
      "/auth/password-reset/confirm/",
      {
        token: token.value,
        new_password: newPassword.value,
      }
    );

    status.value = {
      type: "success",
      message:
        "Su contraseña fue actualizada correctamente. Ya puede iniciar sesión.",
    };

    newPassword.value = "";
    confirmPassword.value = "";

    showNewPassword.value = false;
    showConfirmPassword.value = false;
  } catch (err) {
    const backendDetail = resolveBackendError(
      err?.response?.data
    );

    const message =
      /token|enlace|expir/i.test(backendDetail)
        ? "El enlace de recuperación no es válido o ya expiró. Solicite uno nuevo."
        : backendDetail ||
          "No se pudo restablecer la contraseña. Verifique el enlace o solicite una nueva recuperación.";

    status.value = {
      type: "error",
      message,
    };
  } finally {
    loading.value = false;
  }
};

const goLogin = () => {
  router.replace("/login");
};

const goRequestRecovery = () => {
  router.replace("/recuperar-contrasena");
};

onMounted(async () => {
  await userStore.bootstrapAuth();

  if (userStore.isAuthenticated) {
    await router.replace("/home");
    return;
  }

  if (token.value) {
    await nextTick();
    passwordInputRef.value?.focus?.();
  }
});
</script>

<style src="../auth-base.css"></style>
<style src="./reset-password.css"></style>