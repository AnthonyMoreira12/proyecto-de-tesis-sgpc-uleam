<template>
  <div class="auth-container auth-container--recovery">
    <main class="auth-wrapper auth-wrapper--recovery-scene">
      <div class="recovery-shell">
        <section
          class="recovery-panel page-stage page-stage-1"
          aria-labelledby="recovery-title"
        >
          <div class="recovery-panel__brand">
            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              class="recovery-panel__brand-logo"
              alt="Logo de la Universidad Laica Eloy Alfaro de Manabí"
            />

            <div class="recovery-panel__brand-copy">
              <p class="recovery-panel__brand-kicker">
                Universidad Laica Eloy Alfaro de Manabí
              </p>

              <p class="recovery-panel__brand-system">
                SGPC ULEAM
              </p>
            </div>
          </div>

          <div class="recovery-panel__content">
            <header class="recovery-panel__head">
              <h1
                id="recovery-title"
                class="recovery-panel__title"
              >
                Recuperar contraseña
              </h1>

              <p class="recovery-panel__subtitle">
                Ingrese el correo asociado a su cuenta externa.
              </p>
            </header>

            <div
              class="recovery-notice"
              role="note"
            >
              <span
                class="recovery-notice__icon"
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
                Las cuentas institucionales ULEAM deben recuperar su contraseña
                directamente desde Microsoft 365.
              </p>
            </div>

            <form
              class="recovery-form"
              novalidate
              @submit.prevent="submitRecovery"
            >
              <div
                class="input-group recovery-field"
                :class="{ invalid: Boolean(errors.email) }"
              >
                <label
                  class="recovery-field__label"
                  for="recovery-email"
                >
                  Correo electrónico
                </label>

                <div class="recovery-field__control">
                  <span
                    class="recovery-field__icon"
                    aria-hidden="true"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      focusable="false"
                    >
                      <rect
                        x="3"
                        y="5"
                        width="18"
                        height="14"
                        rx="2.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                      />

                      <path
                        d="m5 8 7 5 7-5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <input
                    id="recovery-email"
                    ref="emailInputRef"
                    v-model="email"
                    class="recovery-field__input"
                    type="email"
                    placeholder="correo@dominio.com"
                    autocomplete="email"
                    inputmode="email"
                    :aria-invalid="Boolean(errors.email)"
                    :aria-describedby="
                      errors.email
                        ? 'recovery-email-error'
                        : undefined
                    "
                    @input="clearEmailError"
                  />
                </div>

                <p
                  v-if="errors.email"
                  id="recovery-email-error"
                  class="recovery-field__error"
                  aria-live="polite"
                >
                  {{ errors.email }}
                </p>
              </div>

              <div
                v-if="status.type"
                class="recovery-status"
                :class="`is-${status.type}`"
                aria-live="polite"
                role="status"
              >
                <span
                  class="recovery-status__icon"
                  aria-hidden="true"
                >
                  <svg
                    v-if="status.type === 'success'"
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
                      d="m8 12 2.6 2.6L16.5 9"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>

                  <svg
                    v-else
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

                <p>
                  {{ status.message }}
                </p>
              </div>

              <div class="recovery-actions">
                <button
                  class="recovery-button recovery-button--primary"
                  type="submit"
                  :disabled="loading"
                >
                  <svg
                    v-if="!loading"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <path
                      d="M4 12 20 4l-5.5 16-3.2-6.3L4 12Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />

                    <path
                      d="m11.3 13.7 4.2-4.2"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                    />
                  </svg>

                  <span
                    v-else
                    class="recovery-button__spinner"
                    aria-hidden="true"
                  ></span>

                  <span>
                    {{ loading ? "Enviando..." : "Enviar enlace" }}
                  </span>
                </button>

                <button
                  class="recovery-button recovery-button--secondary"
                  type="button"
                  :disabled="loading"
                  @click="goLogin"
                >
                  Volver al inicio de sesión
                </button>
              </div>

              <p
                v-if="status.type === 'success'"
                class="recovery-help"
              >
                Revise también la carpeta de correo no deseado o SPAM.
              </p>
            </form>
          </div>
        </section>

        <aside
          class="recovery-visual page-stage page-stage-2"
          aria-hidden="true"
        >
          <span class="recovery-visual__glow recovery-visual__glow--one"></span>
          <span class="recovery-visual__glow recovery-visual__glow--two"></span>

          <div class="recovery-visual__content">
            <div class="recovery-visual__icon">
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

            <div class="recovery-visual__copy">
              <h2 class="recovery-visual__title">
                Recupere el acceso a su cuenta
              </h2>

              <p class="recovery-visual__description">
                Le enviaremos un enlace seguro para crear una nueva contraseña.
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
  onMounted,
  nextTick,
} from "vue";

import { useRouter } from "vue-router";

import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";

const router = useRouter();
const userStore = useUserStore();

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const BLOCKED_DOMAINS = [
  "uleam.edu.ec",
  "live.uleam.edu.ec",
];

const email = ref("");
const errors = ref({});

const loading = ref(false);

const status = ref({
  type: "",
  message: "",
});

const emailInputRef = ref(null);

const isValidEmail = (value = "") => {
  return EMAIL_REGEX.test(String(value).trim());
};

const getDomain = (emailValue) => {
  const parts = String(emailValue || "")
    .trim()
    .toLowerCase()
    .split("@");

  return parts.length === 2
    ? parts[1]
    : "";
};

const isInstitutionalEmail = (emailValue) => {
  const domain = getDomain(emailValue);

  if (!domain) {
    return false;
  }

  return BLOCKED_DOMAINS.some(
    (blockedDomain) =>
      domain === blockedDomain ||
      domain.endsWith(`.${blockedDomain}`)
  );
};

const clearEmailError = () => {
  errors.value = {};
  status.value = {
    type: "",
    message: "",
  };
};

const validate = () => {
  const nextErrors = {};
  const normalizedEmail = email.value.trim();

  if (!normalizedEmail) {
    nextErrors.email =
      "El correo electrónico es obligatorio.";
  } else if (!isValidEmail(normalizedEmail)) {
    nextErrors.email =
      "Ingrese un correo electrónico válido.";
  } else if (isInstitutionalEmail(normalizedEmail)) {
    nextErrors.email =
      "Las cuentas institucionales ULEAM deben recuperar su contraseña desde Microsoft 365.";
  }

  errors.value = nextErrors;

  return Object.keys(nextErrors).length === 0;
};

const resolveBackendError = (err) => {
  const data = err?.response?.data || {};

  if (typeof data.detail === "string" && data.detail) {
    return data.detail;
  }

  if (typeof data.error === "string" && data.error) {
    return data.error;
  }

  return "";
};

const submitRecovery = async () => {
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
    message: "Enviando solicitud de recuperación...",
  };

  try {
    await api.post(
      "/auth/password-reset/request/",
      {
        email: email.value
          .trim()
          .toLowerCase(),
      }
    );

    status.value = {
      type: "success",
      message:
        "Si el correo está registrado como cuenta externa, recibirá un enlace para restablecer su contraseña.",
    };
  } catch (err) {
    status.value = {
      type: "error",
      message:
        resolveBackendError(err) ||
        "No se pudo enviar el enlace. Inténtelo nuevamente.",
    };
  } finally {
    loading.value = false;
  }
};

const goLogin = () => {
  router.replace("/login");
};

onMounted(async () => {
  await userStore.bootstrapAuth();

  if (userStore.isAuthenticated) {
    await router.replace("/home");
    return;
  }

  await nextTick();
  emailInputRef.value?.focus?.();
});
</script>

<style src="../auth-base.css"></style>
<style src="./recuperar-contrasena.css"></style>