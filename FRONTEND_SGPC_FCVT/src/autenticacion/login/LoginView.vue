<template>
  <div class="auth-container auth-container--login">
    <div class="auth-wrapper auth-wrapper--login-scene">
      <div class="login-shell">
        <section
          class="login-panel page-stage page-stage-1"
          aria-labelledby="login-title"
        >
          <div class="login-panel__brand">
            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              class="login-panel__brand-logo"
              alt="Logo de la ULEAM"
            />

            <div class="login-panel__brand-copy">
              <p class="login-panel__brand-kicker">
                Universidad Laica Eloy Alfaro de Manabí
              </p>
              <p class="login-panel__brand-system">SGPC ULEAM</p>
            </div>
          </div>

          <div class="login-panel__content">
            <header class="login-panel__head">
              <p class="login-panel__eyebrow">Acceso seguro</p>
              <h1 id="login-title" class="login-panel__title">Iniciar sesión</h1>
              <p class="login-panel__subtitle">
                Ingrese con su cuenta institucional de Microsoft 365 o con una cuenta
                externa registrada.
              </p>
            </header>

            <section
              class="login-panel__section"
              aria-labelledby="institutional-access-title"
            >
              <h2 id="institutional-access-title" class="sr-only">
                Acceso institucional
              </h2>

              <button
                class="btn btn-microsoft btn-microsoft--login"
                type="button"
                @click="loginMicrosoft"
                :disabled="loadingMS || loadingBD"
              >
                <img
                  src="../../assets/icons8-microsoft-365-48.png"
                  alt=""
                  aria-hidden="true"
                  class="ms-logo"
                />
                <span>
                  {{ loadingMS ? "Redirigiendo..." : "Continuar con Microsoft 365" }}
                </span>
              </button>

              <p
                v-if="msError"
                class="error-msg backend-error login-backend-error"
                aria-live="polite"
                role="status"
              >
                {{ msError }}
              </p>

              <p class="login-panel__hint">
                Para cuentas institucionales ULEAM y personal autorizado.
              </p>
            </section>

            <div
              class="auth-divider auth-divider--login"
              role="separator"
              aria-label="Separador de accesos"
            >
              <span>o continúe con</span>
            </div>

            <section
              class="login-panel__section"
              aria-labelledby="external-access-title"
            >
              <h2 id="external-access-title" class="sr-only">
                Acceso con cuenta externa
              </h2>

              <form @submit.prevent="loginBD" class="login-form" novalidate>
                <div class="input-group login-field" :class="{ invalid: !!errors.email }">
                  <label class="field-label login-field__label" for="login-email">
                    Correo electrónico
                  </label>

                  <input
                    id="login-email"
                    v-model="email"
                    class="input-field login-field__control"
                    type="email"
                    placeholder="correo@dominio.com"
                    autocomplete="username"
                    inputmode="email"
                    :aria-invalid="!!errors.email"
                    :aria-describedby="errors.email ? 'login-email-error' : undefined"
                    @input="clearError('email')"
                  />

                  <p
                    v-if="errors.email"
                    id="login-email-error"
                    class="error-msg login-field__error"
                    aria-live="polite"
                  >
                    {{ errors.email }}
                  </p>
                </div>

                <div
                  class="input-group login-field"
                  :class="{ invalid: !!errors.password }"
                >
                  <label class="field-label login-field__label" for="login-password">
                    Contraseña
                  </label>

                  <div class="password-container login-password">
                    <input
                      id="login-password"
                      v-model="password"
                      class="input-field login-field__control"
                      :type="passwordVisible ? 'text' : 'password'"
                      placeholder="Ingrese su contraseña"
                      autocomplete="current-password"
                      :aria-invalid="!!errors.password"
                      :aria-describedby="
                        errors.password ? 'login-password-error' : undefined
                      "
                      @input="clearError('password')"
                    />

                    <button
                      class="toggle-password login-password__toggle"
                      type="button"
                      @click="togglePassword"
                      :aria-label="
                        passwordVisible ? 'Ocultar contraseña' : 'Mostrar contraseña'
                      "
                      :aria-pressed="passwordVisible"
                    >
                      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
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
                          v-if="passwordVisible"
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
                    v-if="errors.password"
                    id="login-password-error"
                    class="error-msg login-field__error"
                    aria-live="polite"
                  >
                    {{ errors.password }}
                  </p>
                </div>

                <p
                  v-if="error"
                  class="error-msg backend-error login-backend-error"
                  aria-live="polite"
                  role="status"
                >
                  {{ error }}
                </p>

                <div class="login-actions">
                  <button
                    class="btn btn-primary btn-primary--login"
                    type="submit"
                    :disabled="loadingBD || loadingMS"
                  >
                    {{ loadingBD ? "Validando..." : "Iniciar sesión" }}
                  </button>

                  <button
                    v-if="allowExternalRecovery"
                    type="button"
                    class="btn-text btn-text--login"
                    @click="openForgot"
                    :disabled="loadingBD || loadingMS"
                    title="Disponible solo para cuentas externas"
                  >
                    ¿Olvidó su contraseña?
                  </button>
                </div>
              </form>
            </section>
          </div>

          <div class="login-panel__footer">
            <p class="login-panel__footer-text">
              Solo pueden ingresar usuarios autorizados.
            </p>
          </div>
        </section>

        <section class="login-visual page-stage page-stage-2" aria-hidden="true">
          <div class="login-visual__media">
            <span class="login-visual__orb login-visual__orb--one"></span>
            <span class="login-visual__orb login-visual__orb--two"></span>
            <span class="login-visual__orb login-visual__orb--three"></span>

            <div class="login-visual__logo-frame">
              <img
                src="../../assets/LOGO-ULEAM-VERTICAL.png"
                class="login-visual__logo"
                alt=""
              />
            </div>
          </div>

          <div class="login-visual__caption">
            <p class="login-visual__eyebrow">Plataforma institucional</p>
            <h2 class="login-visual__title">
              Sistema de Gestión de Producción Científica
            </h2>
          </div>
        </section>
      </div>
    </div>

    <teleport to="body">
      <div
        v-if="forgotOpen"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="forgot-modal-title"
        aria-describedby="forgot-modal-desc"
        @click.self="closeForgot"
      >
        <div ref="modalCardRef" class="modal-card login-modal-card" tabindex="-1">
          <div class="modal-head">
            <div class="modal-head-copy">
              <h3 id="forgot-modal-title" class="modal-title">Recuperar contraseña</h3>
              <p id="forgot-modal-desc" class="modal-subtitle">
                Esta opción está disponible solo para cuentas externas.
              </p>
            </div>

            <button
              class="modal-close"
              type="button"
              @click="closeForgot"
              aria-label="Cerrar ventana de recuperación"
            >
              <svg
                class="modal-close-icon"
                viewBox="0 0 24 24"
                aria-hidden="true"
                focusable="false"
              >
                <path d="M6 6L18 18" />
                <path d="M18 6L6 18" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="submitForgot" class="modal-body" novalidate>
            <div class="info-banner info-banner--compact">
              Si usa una cuenta institucional ULEAM, recupere su contraseña desde
              Microsoft 365.
            </div>

            <div class="input-group" :class="{ invalid: !!forgotErrors.email }">
              <label class="field-label" for="forgot-email">Correo electrónico</label>

              <input
                id="forgot-email"
                ref="forgotInputRef"
                v-model="forgotEmail"
                class="input-field"
                type="email"
                placeholder="correo@dominio.com"
                autocomplete="email"
                inputmode="email"
                :aria-invalid="!!forgotErrors.email"
                :aria-describedby="forgotErrors.email ? 'forgot-email-error' : undefined"
                @input="clearForgotError"
              />

              <p
                v-if="forgotErrors.email"
                id="forgot-email-error"
                class="error-msg"
                aria-live="polite"
              >
                {{ forgotErrors.email }}
              </p>
            </div>

            <div
              v-if="forgotStatus.type"
              class="status-box status-box--tight"
              :class="forgotStatus.type"
              aria-live="polite"
              role="status"
            >
              {{ forgotStatus.message }}
            </div>

            <div class="modal-actions">
              <button
                type="button"
                class="btn btn-secondary"
                @click="closeForgot"
                :disabled="forgotLoading"
              >
                Cancelar
              </button>

              <button type="submit" class="btn btn-solid" :disabled="forgotLoading">
                {{ forgotLoading ? "Enviando..." : "Enviar instrucciones" }}
              </button>
            </div>

            <p class="modal-help">
              Si no recibe el correo, revise SPAM o contacte a un administrador.
            </p>
          </form>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const AUTH_HOME_ROUTE = "/home";
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const BLOCKED_DOMAINS = ["uleam.edu.ec", "live.uleam.edu.ec"];
const allowExternalRecovery = true;

const email = ref("");
const password = ref("");
const passwordVisible = ref(false);

const errors = ref({});
const error = ref("");
const msError = ref("");

const loadingBD = ref(false);
const loadingMS = ref(false);

const forgotOpen = ref(false);
const forgotEmail = ref("");
const forgotErrors = ref({});
const forgotLoading = ref(false);
const forgotStatus = ref({ type: "", message: "" });
const forgotInputRef = ref(null);
const modalCardRef = ref(null);
const forgotRequestId = ref(0);
const isUnmounted = ref(false);

const isValidEmail = (value = "") => EMAIL_REGEX.test(String(value).trim());

const clearObjectField = (targetRef, field) => {
  const copy = { ...targetRef.value };
  delete copy[field];
  targetRef.value = copy;
};

const resetAuthFeedback = () => {
  error.value = "";
  msError.value = "";
};

const resetForgotState = () => {
  forgotErrors.value = {};
  forgotStatus.value = { type: "", message: "" };
};

const togglePassword = () => {
  passwordVisible.value = !passwordVisible.value;
};

const validateBD = () => {
  const nextErrors = {};
  const trimmedEmail = email.value.trim();

  if (!trimmedEmail) {
    nextErrors.email = "El correo es obligatorio.";
  } else if (!isValidEmail(trimmedEmail)) {
    nextErrors.email = "Ingrese un correo válido.";
  }

  if (!password.value) {
    nextErrors.password = "La contraseña es obligatoria.";
  }

  errors.value = nextErrors;
  return Object.keys(nextErrors).length === 0;
};

const clearError = (field) => {
  clearObjectField(errors, field);
  resetAuthFeedback();
};

const saveSession = ({ access, refresh, user }) => {
  userStore.setSession({ access, refresh, user });
};

const ensureAuthenticatedSession = async ({ access, refresh, user }) => {
  saveSession({ access, refresh, user });

  if (!userStore.user && typeof userStore.refreshProfile === "function") {
    await userStore.refreshProfile({ throwOnError: true });
  }

  return userStore.isAuthenticated;
};

const parseBackendAuthError = (err, fallback) => {
  const data = err?.response?.data || {};

  if (typeof data.detail === "string" && data.detail) return data.detail;
  if (typeof data.error === "string" && data.error) return data.error;

  return fallback;
};

const redirectToHome = () => {
  return router.replace(AUTH_HOME_ROUTE);
};

const loginBD = async () => {
  resetAuthFeedback();

  if (!validateBD()) return;

  loadingBD.value = true;

  try {
    const res = await api.post("/auth/login/", {
      email: email.value.trim().toLowerCase(),
      password: password.value,
    });

    const access = res.data?.tokens?.access;
    const refresh = res.data?.tokens?.refresh;
    const user = res.data?.user || null;

    if (!access || !refresh) {
      error.value = "No se pudo iniciar sesión. Inténtelo nuevamente.";
      return;
    }

    const sessionReady = await ensureAuthenticatedSession({
      access,
      refresh,
      user,
    });

    if (!sessionReady) {
      userStore.clearUser();
      error.value = "No se pudo completar la sesión. Inténtelo nuevamente.";
      return;
    }

    await redirectToHome();
  } catch (err) {
    userStore.clearUser();

    if (err?.response?.status === 401) {
      error.value =
        "No se pudo iniciar sesión. Verifique su correo y contraseña.";
    } else if (err?.response?.status === 403) {
      error.value = parseBackendAuthError(
        err,
        "La cuenta está inactiva o no tiene acceso autorizado."
      );
    } else if (err?.response?.status === 400) {
      error.value = "Datos inválidos. Verifique los campos.";
    } else {
      error.value = parseBackendAuthError(
        err,
        "No se pudo iniciar sesión en este momento. Inténtelo nuevamente."
      );
    }
  } finally {
    loadingBD.value = false;
  }
};

const loginMicrosoft = () => {
  resetAuthFeedback();
  loadingMS.value = true;

  const baseUrl = import.meta.env.VITE_API_URL;

  if (!baseUrl) {
    msError.value = "El acceso institucional no está disponible en este momento.";
    loadingMS.value = false;
    return;
  }

  window.location.assign(`${String(baseUrl).replace(/\/$/, "")}/auth/microsoft/login/`);
};

const extractTokens = (data) => {
  const access =
    data?.access ||
    data?.access_token ||
    data?.tokens?.access ||
    data?.tokens?.access_token ||
    null;

  const refresh =
    data?.refresh ||
    data?.refresh_token ||
    data?.tokens?.refresh ||
    data?.tokens?.refresh_token ||
    null;

  const user = data?.user || data?.usuario || data?.data?.user || null;

  return { access, refresh, user };
};

const safeDecode = (value) => {
  try {
    return decodeURIComponent(String(value));
  } catch {
    return String(value);
  }
};

const clearMsQuery = () => {
  const cleanQuery = { ...route.query };
  delete cleanQuery.ms_code;
  delete cleanQuery.ms_error;
  delete cleanQuery.code;
  delete cleanQuery.state;

  return router.replace({ path: route.path, query: cleanQuery });
};

const finishMicrosoftLogin = async () => {
  const msErr = route.query.ms_error;

  if (msErr) {
    msError.value = safeDecode(msErr);
    await clearMsQuery();
    return;
  }

  const code = route.query.ms_code || route.query.code;
  const state = route.query.state;

  if (!code) return;

  loadingMS.value = true;

  try {
    const payload = state
      ? { code: String(code), state: String(state) }
      : { code: String(code) };

    const res = await api.post("/auth/microsoft/exchange/", payload);
    const { access, refresh, user } = extractTokens(res.data);

    if (!access || !refresh) {
      msError.value = "No se pudo completar el acceso con Microsoft.";
      await clearMsQuery();
      return;
    }

    const sessionReady = await ensureAuthenticatedSession({
      access,
      refresh,
      user,
    });

    if (!sessionReady) {
      userStore.clearUser();
      msError.value = "No se pudo completar el acceso con Microsoft.";
      await clearMsQuery();
      return;
    }

    await clearMsQuery();
    await redirectToHome();
  } catch (err) {
    userStore.clearUser();
    msError.value = parseBackendAuthError(
      err,
      "No se pudo completar el acceso con Microsoft."
    );
    await clearMsQuery();
  } finally {
    loadingMS.value = false;
  }
};

const getDomain = (emailStr) => {
  const parts = String(emailStr || "").trim().toLowerCase().split("@");
  return parts.length === 2 ? parts[1] : "";
};

const isBlockedInstitutionalEmail = (emailStr) => {
  const domain = getDomain(emailStr);
  if (!domain) return false;

  return BLOCKED_DOMAINS.some(
    (blocked) => domain === blocked || domain.endsWith(`.${blocked}`)
  );
};

const validateForgot = () => {
  const nextErrors = {};
  const value = forgotEmail.value.trim();

  if (!value) {
    nextErrors.email = "El correo es obligatorio.";
  } else if (!isValidEmail(value)) {
    nextErrors.email = "Ingrese un correo válido.";
  } else if (isBlockedInstitutionalEmail(value)) {
    nextErrors.email =
      "La recuperación solo está disponible para cuentas externas. Para cuentas ULEAM use Microsoft 365.";
  }

  forgotErrors.value = nextErrors;
  return Object.keys(nextErrors).length === 0;
};

const clearForgotError = () => {
  resetForgotState();
};

const openForgot = async () => {
  if (!allowExternalRecovery) return;

  forgotOpen.value = true;
  forgotEmail.value = "";
  forgotLoading.value = false;
  resetForgotState();

  await nextTick();
  forgotInputRef.value?.focus?.();
};

const closeForgot = () => {
  forgotOpen.value = false;
  forgotLoading.value = false;
  resetForgotState();
};

const submitForgot = async () => {
  resetForgotState();

  if (!validateForgot()) return;

  forgotLoading.value = true;
  forgotStatus.value = { type: "info", message: "Procesando solicitud..." };

  const requestId = ++forgotRequestId.value;

  try {
    await api.post("/auth/password-reset/request/", {
      email: forgotEmail.value.trim().toLowerCase(),
    });

    if (
      isUnmounted.value ||
      !forgotOpen.value ||
      requestId !== forgotRequestId.value
    ) {
      return;
    }

    forgotStatus.value = {
      type: "success",
      message:
        "Si el correo está registrado como usuario externo, recibirá instrucciones para restablecer su contraseña.",
    };
  } catch (err) {
    if (
      isUnmounted.value ||
      !forgotOpen.value ||
      requestId !== forgotRequestId.value
    ) {
      return;
    }

    const msg =
      err.response?.data?.detail ||
      err.response?.data?.error ||
      "No se pudo procesar la solicitud. Inténtelo nuevamente.";

    forgotStatus.value = { type: "error", message: msg };
  } finally {
    if (!isUnmounted.value && requestId === forgotRequestId.value) {
      forgotLoading.value = false;
    }
  }
};

const trapFocus = (e) => {
  if (!forgotOpen.value || e.key !== "Tab" || !modalCardRef.value) return;

  const focusable = modalCardRef.value.querySelectorAll(
    'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
  );

  if (!focusable.length) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    first.focus();
  }
};

const onKeyDown = (e) => {
  if (e.key === "Escape" && forgotOpen.value) {
    closeForgot();
    return;
  }

  trapFocus(e);
};

onMounted(async () => {
  window.addEventListener("keydown", onKeyDown);

  const returningFromMicrosoft =
    !!route.query.ms_code || !!route.query.code || !!route.query.ms_error;

  if (returningFromMicrosoft) {
    await finishMicrosoftLogin();
    return;
  }

  await userStore.bootstrapAuth();

  if (userStore.isAuthenticated) {
    await redirectToHome();
  }
});

onBeforeUnmount(() => {
  isUnmounted.value = true;
  window.removeEventListener("keydown", onKeyDown);
});
</script>

<style src="../auth-base.css"></style>
<style src="./login-view.css"></style>