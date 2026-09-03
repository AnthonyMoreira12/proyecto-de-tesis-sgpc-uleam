<template>
  <div class="auth-container auth-container--login">
    <main class="auth-wrapper auth-wrapper--login-scene">
      <div class="login-shell">
        <section
          class="login-panel page-stage page-stage-1"
          aria-labelledby="login-title"
        >
          <!-- =====================================================
               CABECERA
          ====================================================== -->
          <div class="login-panel__topbar">
            <div class="login-panel__brand">
              <img
                src="../../assets/LOGO-ULEAM-VERTICAL.png"
                class="login-panel__brand-logo"
                alt="Logo de la Universidad Laica Eloy Alfaro de Manabí"
              />

              <div class="login-panel__brand-copy">
                <p class="login-panel__brand-kicker">
                  Universidad Laica Eloy Alfaro de Manabí
                </p>

                <p class="login-panel__brand-system">
                  SGPC ULEAM
                </p>
              </div>
            </div>

            <button
              class="login-theme-toggle"
              type="button"
              :aria-label="themeToggleLabel"
              :title="themeToggleLabel"
              :aria-pressed="darkMode ? 'true' : 'false'"
              @click="toggleTheme"
            >
              <!-- SOL -->
              <svg
                v-if="darkMode"
                viewBox="0 0 24 24"
                aria-hidden="true"
                focusable="false"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                />

                <path
                  d="M12 2.5v2M12 19.5v2M4.5 12h-2M21.5 12h-2M5.3 5.3 3.9 3.9M20.1 20.1l-1.4-1.4M18.7 5.3l1.4-1.4M3.9 20.1l1.4-1.4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>

              <!-- LUNA -->
              <svg
                v-else
                viewBox="0 0 24 24"
                aria-hidden="true"
                focusable="false"
              >
                <path
                  d="M21 14.4A8.6 8.6 0 0 1 9.6 3a7.5 7.5 0 1 0 11.4 11.4Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>

              <span class="sr-only">
                {{ themeToggleLabel }}
              </span>
            </button>
          </div>

          <!-- =====================================================
               CONTENIDO
          ====================================================== -->
          <div class="login-panel__content">
            <header class="login-panel__head">
              <h1
                id="login-title"
                class="login-panel__title"
              >
                Iniciar sesión
              </h1>

              <p class="login-panel__subtitle">
                Ingrese con Microsoft 365 o con una cuenta externa registrada.
              </p>
            </header>

            <!-- =================================================
                 MICROSOFT 365
            ================================================== -->
            <section
              class="login-panel__section"
              aria-labelledby="institutional-access-title"
            >
              <h2
                id="institutional-access-title"
                class="sr-only"
              >
                Acceso institucional con Microsoft 365
              </h2>

              <button
                class="btn btn-microsoft btn-microsoft--login"
                type="button"
                :disabled="loadingMS || loadingBD"
                @click="loginMicrosoft"
              >
                <img
                  src="../../assets/icons8-microsoft-365-48.png"
                  alt=""
                  aria-hidden="true"
                  class="ms-logo"
                />

                <span>
                  {{
                    loadingMS
                      ? "Redirigiendo..."
                      : "Continuar con Microsoft 365"
                  }}
                </span>
              </button>

              <p
                v-if="msError"
                class="error-msg login-backend-error"
                aria-live="polite"
                role="alert"
              >
                {{ msError }}
              </p>
            </section>

            <!-- =================================================
                 DIVISOR
            ================================================== -->
            <div
              class="auth-divider auth-divider--login"
              role="separator"
              aria-label="Acceso mediante cuenta externa"
            >
              <span>Cuenta externa</span>
            </div>

            <!-- =================================================
                 LOGIN LOCAL
            ================================================== -->
            <section
              class="login-panel__section"
              aria-labelledby="external-access-title"
            >
              <h2
                id="external-access-title"
                class="sr-only"
              >
                Acceso con cuenta externa
              </h2>

              <form
                class="login-form"
                novalidate
                @submit.prevent="loginBD"
              >
                <!-- CORREO -->
                <div
                  class="input-group login-field"
                  :class="{ invalid: Boolean(errors.email) }"
                >
                  <label
                    class="field-label login-field__label"
                    for="login-email"
                  >
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
                    autocapitalize="none"
                    spellcheck="false"
                    maxlength="150"
                    :disabled="loadingBD || loadingMS"
                    :aria-invalid="Boolean(errors.email)"
                    :aria-describedby="
                      errors.email
                        ? 'login-email-error'
                        : undefined
                    "
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

                <!-- CONTRASEÑA -->
                <div
                  class="input-group login-field"
                  :class="{ invalid: Boolean(errors.password) }"
                >
                  <label
                    class="field-label login-field__label"
                    for="login-password"
                  >
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
                      maxlength="128"
                      :disabled="loadingBD || loadingMS"
                      :aria-invalid="Boolean(errors.password)"
                      :aria-describedby="
                        errors.password
                          ? 'login-password-error'
                          : undefined
                      "
                      @input="clearError('password')"
                    />

                    <button
                      class="toggle-password login-password__toggle"
                      type="button"
                      :disabled="loadingBD || loadingMS"
                      :aria-label="
                        passwordVisible
                          ? 'Ocultar contraseña'
                          : 'Mostrar contraseña'
                      "
                      :aria-pressed="passwordVisible"
                      @click="togglePassword"
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

                <!-- ERROR DEL BACKEND -->
                <p
                  v-if="error"
                  class="error-msg login-backend-error"
                  aria-live="polite"
                  role="alert"
                >
                  {{ error }}
                </p>

                <!-- ACCIONES -->
                <div class="login-actions">
                  <button
                    class="btn btn-primary btn-primary--login"
                    type="submit"
                    :disabled="loadingBD || loadingMS"
                  >
                    {{
                      loadingBD
                        ? "Validando credenciales..."
                        : "Iniciar sesión"
                    }}
                  </button>

                  <button
                    type="button"
                    class="btn-text btn-text--login"
                    :disabled="loadingBD || loadingMS"
                    @click="goForgotPassword"
                  >
                    ¿Olvidó su contraseña?
                  </button>
                </div>
              </form>
            </section>
          </div>
        </section>

        <!-- =====================================================
             PANEL VISUAL
        ====================================================== -->
        <aside
          class="login-visual page-stage page-stage-2"
          aria-hidden="true"
        >
          <span
            class="login-visual__glow login-visual__glow--one"
          ></span>

          <span
            class="login-visual__glow login-visual__glow--two"
          ></span>

          <div class="login-visual__content">
            <div class="login-visual__logo-surface">
              <img
                src="../../assets/LOGO-ULEAM-VERTICAL.png"
                class="login-visual__logo"
                alt=""
              />
            </div>

            <div class="login-visual__copy">
              <h2 class="login-visual__title">
                Sistema de Gestión de Producción Científica
              </h2>

              <p class="login-visual__description">
                Registro, consulta y seguimiento de la producción científica
                institucional.
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
  computed,
  onMounted,
  ref,
} from "vue";

import {
  storeToRefs,
} from "pinia";

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";
import { useThemeStore } from "../../scripts/stores/themeStore";


/* ============================================================
   ROUTER Y STORES
============================================================ */

const router = useRouter();
const route = useRoute();

const userStore = useUserStore();
const themeStore = useThemeStore();

const {
  darkMode,
} = storeToRefs(themeStore);


/* ============================================================
   CONFIGURACIÓN
============================================================ */

const AUTH_HOME_ROUTE = "/home";

const EMAIL_REGEX =
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


/* ============================================================
   ESTADO
============================================================ */

const email = ref("");
const password = ref("");

const passwordVisible = ref(false);

const errors = ref({});

const error = ref("");
const msError = ref("");

const loadingBD = ref(false);
const loadingMS = ref(false);


/* ============================================================
   TEMA
============================================================ */

const themeToggleLabel = computed(() => {
  return darkMode.value
    ? "Activar modo claro"
    : "Activar modo oscuro";
});


const toggleTheme = () => {
  themeStore.toggleTheme();
};


/* ============================================================
   UTILIDADES GENERALES
============================================================ */

const normalizeRouteQueryValue = (value) => {
  if (Array.isArray(value)) {
    return value.length
      ? String(value[0] ?? "").trim()
      : "";
  }

  return String(
    value ?? ""
  ).trim();
};


const isValidEmail = (value = "") => {
  return EMAIL_REGEX.test(
    String(value).trim()
  );
};


const clearObjectField = (
  targetRef,
  field
) => {
  const copy = {
    ...targetRef.value,
  };

  delete copy[field];

  targetRef.value = copy;
};


const resetAuthFeedback = () => {
  error.value = "";
  msError.value = "";
};


const togglePassword = () => {
  passwordVisible.value =
    !passwordVisible.value;
};


/* ============================================================
   VALIDACIÓN LOCAL
============================================================ */

const validateBD = () => {
  const nextErrors = {};

  const trimmedEmail =
    email.value.trim();

  if (!trimmedEmail) {
    nextErrors.email =
      "El correo es obligatorio.";
  } else if (
    !isValidEmail(trimmedEmail)
  ) {
    nextErrors.email =
      "Ingrese un correo válido.";
  }

  if (!password.value) {
    nextErrors.password =
      "La contraseña es obligatoria.";
  }

  errors.value = nextErrors;

  return (
    Object.keys(nextErrors).length === 0
  );
};


const clearError = (field) => {
  clearObjectField(
    errors,
    field
  );

  resetAuthFeedback();
};


/* ============================================================
   SESIÓN
============================================================ */

const saveSession = ({
  access,
  user,
}) => {
  userStore.setSession({
    access,
    user,
  });
};


const ensureAuthenticatedSession = async ({
  access,
  user,
}) => {
  saveSession({
    access,
    user,
  });

  /*
   * Algunos endpoints pueden entregar tokens sin incluir el
   * perfil completo. En ese caso se recupera desde el backend.
   */
  if (
    !userStore.user &&
    typeof userStore.refreshProfile === "function"
  ) {
    await userStore.refreshProfile({
      throwOnError: true,
    });
  }

  return Boolean(
    userStore.isAuthenticated
  );
};


/* ============================================================
   ERRORES DEL BACKEND
============================================================ */

const firstErrorMessage = (value) => {
  if (!value) {
    return "";
  }

  if (
    typeof value === "string"
  ) {
    return value;
  }

  if (
    Array.isArray(value)
  ) {
    for (
      const item of value
    ) {
      const message =
        firstErrorMessage(item);

      if (message) {
        return message;
      }
    }

    return "";
  }

  if (
    typeof value === "object"
  ) {
    for (
      const nestedValue
      of Object.values(value)
    ) {
      const message =
        firstErrorMessage(
          nestedValue
        );

      if (message) {
        return message;
      }
    }
  }

  return "";
};


const parseBackendAuthError = (
  err,
  fallback
) => {
  const data =
    err?.response?.data;

  if (!data) {
    return fallback;
  }

  if (
    typeof data.detail === "string"
    && data.detail.trim()
  ) {
    return data.detail.trim();
  }

  if (
    typeof data.error === "string"
    && data.error.trim()
  ) {
    return data.error.trim();
  }

  const nestedMessage =
    firstErrorMessage(data);

  return (
    nestedMessage
    || fallback
  );
};


/* ============================================================
   NAVEGACIÓN
============================================================ */

const redirectToHome = () => {
  return router.replace(
    AUTH_HOME_ROUTE
  );
};


const goForgotPassword = () => {
  return router.push(
    "/recuperar-contrasena"
  );
};


/* ============================================================
   LOGIN LOCAL
============================================================ */

const loginBD = async () => {
  if (
    loadingBD.value
    || loadingMS.value
  ) {
    return;
  }

  resetAuthFeedback();

  if (!validateBD()) {
    return;
  }

  loadingBD.value = true;

  try {
    const response =
      await api.post(
        "/auth/login/",
        {
          email:
            email.value
              .trim()
              .toLowerCase(),

          password:
            password.value,
        }
      );

    const access =
      response.data?.tokens?.access;

    const user =
      response.data?.user ?? null;

    if (!access) {
      error.value =
        "No se pudo iniciar sesión. Inténtelo nuevamente.";

      return;
    }

    const sessionReady =
      await ensureAuthenticatedSession({
        access,
        user,
      });

    if (!sessionReady) {
      userStore.clearUser();

      error.value =
        "No se pudo completar la sesión. Inténtelo nuevamente.";

      return;
    }

    await redirectToHome();

  } catch (err) {
    userStore.clearUser();

    const statusCode =
      err?.response?.status;

    if (statusCode === 401) {
      error.value =
        "No se pudo iniciar sesión. Verifique su correo y contraseña.";

      return;
    }

    if (statusCode === 403) {
      error.value =
        parseBackendAuthError(
          err,
          "La cuenta está inactiva o no tiene acceso autorizado."
        );

      return;
    }

    if (statusCode === 400) {
      error.value =
        parseBackendAuthError(
          err,
          "Datos inválidos. Verifique los campos."
        );

      return;
    }

    error.value =
      parseBackendAuthError(
        err,
        "No se pudo iniciar sesión en este momento. Inténtelo nuevamente."
      );

  } finally {
    loadingBD.value = false;
  }
};


/* ============================================================
   URL MICROSOFT
============================================================ */

const getApiBaseUrl = () => {
  /*
   * Utilizamos primero el baseURL efectivo de Axios.
   *
   * Esto evita inconsistencias entre:
   *
   * VITE_API_URL
   * y
   * api.defaults.baseURL
   *
   * especialmente cuando axios.js agrega /api.
   */
  const configuredBaseUrl =
    api?.defaults?.baseURL
    || import.meta.env.VITE_API_URL
    || "";

  return String(
    configuredBaseUrl
  )
    .trim()
    .replace(/\/+$/, "");
};


/* ============================================================
   LOGIN MICROSOFT
============================================================ */

const loginMicrosoft = () => {
  if (
    loadingMS.value
    || loadingBD.value
  ) {
    return;
  }

  resetAuthFeedback();

  const baseUrl =
    getApiBaseUrl();

  if (!baseUrl) {
    msError.value =
      "El acceso institucional no está disponible en este momento.";

    return;
  }

  loadingMS.value = true;

  /*
   * El navegador debe navegar directamente hacia Django para
   * iniciar el flujo OAuth.
   *
   * No se utiliza axios porque el backend responde con una
   * redirección hacia Microsoft.
   */
  window.location.assign(
    `${baseUrl}/auth/microsoft/login/`
  );
};


/* ============================================================
   PAYLOAD MICROSOFT
============================================================ */

const extractTokens = (data) => {
  const access =
    data?.tokens?.access
    ?? data?.access
    ?? data?.access_token
    ?? null;

  const user =
    data?.user
    ?? data?.usuario
    ?? data?.data?.user
    ?? null;

  return {
    access,
    user,
  };
};


/* ============================================================
   LIMPIEZA DE URL MICROSOFT
============================================================ */

const clearMsQuery = async () => {
  const cleanQuery = {
    ...route.query,
  };

  /*
   * Flujo actual.
   */
  delete cleanQuery.ms_code;
  delete cleanQuery.ms_error;
  delete cleanQuery.ms_error_code;

  /*
   * Limpieza preventiva de parámetros pertenecientes a flujos
   * OAuth antiguos.
   */
  delete cleanQuery.code;
  delete cleanQuery.state;
  delete cleanQuery.session_state;
  delete cleanQuery.error;
  delete cleanQuery.error_description;

  await router.replace({
    path: route.path,
    query: cleanQuery,
  });
};


/* ============================================================
   FINALIZAR LOGIN MICROSOFT
============================================================ */

const finishMicrosoftLogin =
  async () => {
    const microsoftError =
      normalizeRouteQueryValue(
        route.query.ms_error
      );

    /*
     * El callback de Django redirige los errores utilizando
     * ms_error.
     */
    if (microsoftError) {
      msError.value =
        microsoftError;

      await clearMsQuery();

      return;
    }

    /*
     * El flujo actual utiliza EXCLUSIVAMENTE ms_code.
     *
     * El código OAuth real de Microsoft nunca debe llegar al
     * frontend.
     */
    const code =
      normalizeRouteQueryValue(
        route.query.ms_code
      );

    if (!code) {
      return;
    }

    loadingMS.value = true;

    try {
      /*
       * MicrosoftExchangeView espera solamente:
       *
       * {
       *   code: "..."
       * }
       */
      const response =
        await api.post(
          "/auth/microsoft/exchange/",
          {
            code,
          }
        );

      const {
        access,
        user,
      } = extractTokens(
        response.data
      );

      if (!access) {
        msError.value =
          "No se pudo completar el acceso con Microsoft.";

        await clearMsQuery();

        return;
      }

      const sessionReady =
        await ensureAuthenticatedSession({
          access,
          user,
        });

      if (!sessionReady) {
        userStore.clearUser();

        msError.value =
          "No se pudo completar el acceso con Microsoft.";

        await clearMsQuery();

        return;
      }

      /*
       * Eliminamos el código temporal antes de entrar a la
       * aplicación.
       */
      await clearMsQuery();

      await redirectToHome();

    } catch (err) {
      userStore.clearUser();

      msError.value =
        parseBackendAuthError(
          err,
          "No se pudo completar el acceso con Microsoft."
        );

      await clearMsQuery();

    } finally {
      loadingMS.value = false;
    }
  };


/* ============================================================
   MONTAJE
============================================================ */

onMounted(
  async () => {
    const hasMicrosoftCode =
      Boolean(
        normalizeRouteQueryValue(
          route.query.ms_code
        )
      );

    const hasMicrosoftError =
      Boolean(
        normalizeRouteQueryValue(
          route.query.ms_error
        )
      );

    /*
     * Si regresamos del callback de Microsoft, ese proceso debe
     * resolverse antes de ejecutar bootstrapAuth().
     */
    if (
      hasMicrosoftCode
      || hasMicrosoftError
    ) {
      await finishMicrosoftLogin();

      return;
    }

    /*
     * Sesión existente.
     */
    try {
      await userStore.bootstrapAuth();

      if (
        userStore.isAuthenticated
      ) {
        await redirectToHome();
      }

    } catch {
      /*
       * Si no existe una sesión válida simplemente permanecemos
       * en /login.
       *
       * bootstrapAuth() debe encargarse internamente de limpiar
       * tokens inválidos.
       */
    }
  }
);
</script>

<style src="../auth-base.css"></style>
<style src="./login-view.css"></style>
