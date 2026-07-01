<template>
  <div class="auth-container auth-container--reset">
    <div class="auth-wrapper auth-wrapper--reset-scene">
      <div class="reset-shell">
        <section class="reset-panel page-stage page-stage-1" aria-labelledby="reset-title">
          <div class="reset-panel__brand">
            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              class="reset-panel__brand-logo"
              alt="Logo de la ULEAM"
            />

            <div class="reset-panel__brand-copy">
              <p class="reset-panel__brand-kicker">
                Universidad Laica Eloy Alfaro de Manabí
              </p>
              <p class="reset-panel__brand-system">SGPC ULEAM</p>
            </div>
          </div>

          <div class="reset-panel__content">
            <header class="reset-panel__head">
              <p class="reset-panel__eyebrow">Seguridad de acceso</p>
              <h1 id="reset-title" class="reset-panel__title">Restablecer contraseña</h1>
              <p class="reset-panel__subtitle">
                Actualice el acceso de su <b>cuenta externa</b>.
              </p>
            </header>

            <div class="info-banner info-banner--compact reset-info-banner">
              <b>Importante:</b> si su cuenta es institucional ULEAM, debe gestionar su
              contraseña desde Microsoft 365.
            </div>

            <div
              v-if="!token"
              class="status-box error status-box--tight reset-status-box"
              aria-live="polite"
              role="status"
            >
              El enlace de recuperación no es válido o no fue encontrado. Abra nuevamente el
              enlace enviado a su correo o solicite una nueva recuperación.
            </div>

            <form v-else @submit.prevent="submitReset" class="reset-form" novalidate>
              <div class="input-group reset-field" :class="{ invalid: !!errors.new_password }">
                <label class="field-label reset-field__label" for="reset-new-password">
                  Nueva contraseña
                </label>

                <div class="password-container reset-password-box">
                  <input
                    id="reset-new-password"
                    ref="passwordInputRef"
                    v-model="newPassword"
                    class="input-field reset-field__control"
                    :type="show1 ? 'text' : 'password'"
                    placeholder="Ingrese una nueva contraseña"
                    autocomplete="new-password"
                    :aria-invalid="!!errors.new_password"
                    :aria-describedby="
                      errors.new_password ? 'reset-new-password-error' : 'pw-help'
                    "
                    @input="clearError('new_password')"
                  />

                  <button
                    class="toggle-password reset-password-box__toggle"
                    type="button"
                    @click="show1 = !show1"
                    :aria-label="
                      show1 ? 'Ocultar nueva contraseña' : 'Mostrar nueva contraseña'
                    "
                    :aria-pressed="show1"
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
                        v-if="show1"
                        d="M4 4l16 16"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>

                <div class="pw-meta" id="pw-help">
                  <div class="pw-meter" aria-label="Nivel de seguridad de la contraseña">
                    <div
                      class="pw-meter-bar"
                      :class="strengthClass"
                      :style="{ width: strengthPct + '%' }"
                    ></div>
                  </div>

                  <p class="pw-meter-text">
                    Seguridad: <b>{{ strengthLabel }}</b>
                  </p>
                </div>

                <p
                  v-if="errors.new_password"
                  id="reset-new-password-error"
                  class="error-msg reset-field__error"
                  aria-live="polite"
                >
                  {{ errors.new_password }}
                </p>
              </div>

              <div class="input-group reset-field" :class="{ invalid: !!errors.confirm_password }">
                <label class="field-label reset-field__label" for="reset-confirm-password">
                  Confirmar contraseña
                </label>

                <div class="password-container reset-password-box">
                  <input
                    id="reset-confirm-password"
                    v-model="confirmPassword"
                    class="input-field reset-field__control"
                    :type="show2 ? 'text' : 'password'"
                    placeholder="Repita la nueva contraseña"
                    autocomplete="new-password"
                    :aria-invalid="!!errors.confirm_password"
                    :aria-describedby="
                      errors.confirm_password ? 'reset-confirm-password-error' : undefined
                    "
                    @input="clearError('confirm_password')"
                  />

                  <button
                    class="toggle-password reset-password-box__toggle"
                    type="button"
                    @click="show2 = !show2"
                    :aria-label="
                      show2
                        ? 'Ocultar confirmación de contraseña'
                        : 'Mostrar confirmación de contraseña'
                    "
                    :aria-pressed="show2"
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
                        v-if="show2"
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
                  class="error-msg reset-field__error"
                  aria-live="polite"
                >
                  {{ errors.confirm_password }}
                </p>
              </div>

              <div class="pw-checklist" aria-label="Requisitos de contraseña">
                <p class="pw-checklist-title">Requisitos recomendados</p>

                <ul class="pw-checklist-grid">
                  <li :class="{ ok: rules.len8 }">8 caracteres o más</li>
                  <li :class="{ ok: rules.letter }">Al menos una letra</li>
                  <li :class="{ ok: rules.number }">Al menos un número</li>
                  <li :class="{ ok: rules.mixed }">Mayúsculas y minúsculas</li>
                  <li :class="{ ok: rules.notCommon }">No usar contraseñas comunes</li>
                </ul>
              </div>

              <div
                v-if="status.type"
                class="status-box status-box--tight reset-status-box"
                :class="status.type"
                aria-live="polite"
                role="status"
              >
                {{ status.message }}
              </div>

              <div class="reset-actions">
                <button
                  class="btn btn-primary btn-primary--reset"
                  type="submit"
                  :disabled="loading"
                >
                  {{ loading ? "Actualizando..." : "Guardar nueva contraseña" }}
                </button>

                <button
                  class="btn-text btn-text--reset"
                  type="button"
                  @click="goLogin"
                  :disabled="loading"
                >
                  Volver al inicio de sesión
                </button>
              </div>
            </form>
          </div>

          <div class="reset-panel__footer">
            <p class="reset-panel__footer-text">
              Solo pueden recuperar su acceso usuarios externos autorizados.
            </p>
          </div>
        </section>

        <section class="reset-visual page-stage page-stage-2" aria-hidden="true">
          <div class="reset-visual__topbar">
            <span class="reset-visual__badge">ULEAM</span>
            <span class="reset-visual__badge">Cuenta externa</span>
            <span class="reset-visual__badge">Recuperación</span>
          </div>

          <div class="reset-visual__media">
            <span class="reset-visual__orb reset-visual__orb--one"></span>
            <span class="reset-visual__orb reset-visual__orb--two"></span>
            <span class="reset-visual__orb reset-visual__orb--three"></span>

            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              class="reset-visual__logo"
              alt=""
            />
          </div>

          <div class="reset-visual__caption">
            <p class="reset-visual__eyebrow">Plataforma institucional</p>
            <h2 class="reset-visual__title">Recupere su acceso</h2>
            <p class="reset-visual__text">
              Restablezca la contraseña de su cuenta externa dentro del flujo seguro del sistema.
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../../scripts/api/axios";

const route = useRoute();
const router = useRouter();

const token = computed(() => (route.query.token ? String(route.query.token) : ""));

const newPassword = ref("");
const confirmPassword = ref("");

const show1 = ref(false);
const show2 = ref(false);

const errors = ref({});
const loading = ref(false);
const status = ref({ type: "", message: "" });
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
];

const clearObjectField = (targetRef, field) => {
  const copy = { ...targetRef.value };
  delete copy[field];
  targetRef.value = copy;
};

const clearError = (field) => {
  clearObjectField(errors, field);
  status.value = { type: "", message: "" };
};

const parseJwtPayload = (tokenValue) => {
  try {
    const payload = tokenValue.split(".")[1];
    if (!payload) return null;

    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");

    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
};

const isJwtNotExpired = (tokenValue) => {
  const payload = parseJwtPayload(tokenValue);
  if (!payload?.exp) return false;
  return payload.exp * 1000 > Date.now();
};

const rules = computed(() => {
  const p = newPassword.value || "";
  const len8 = p.length >= 8;
  const letter = /[a-zA-Z]/.test(p);
  const number = /\d/.test(p);
  const upper = /[A-Z]/.test(p);
  const lower = /[a-z]/.test(p);
  const mixed = upper && lower;
  const notCommon = p.length > 0 && !commonPasswords.includes(p.toLowerCase());

  return { len8, letter, number, mixed, notCommon };
});

const strengthScore = computed(() => {
  let score = 0;
  const p = newPassword.value || "";

  if (!p) return 0;
  if (p.length >= 8) score += 1;
  if (p.length >= 12) score += 1;
  if (/[a-z]/.test(p)) score += 1;
  if (/[A-Z]/.test(p)) score += 1;
  if (/\d/.test(p)) score += 1;
  if (/[^a-zA-Z0-9]/.test(p)) score += 1;
  if (!commonPasswords.includes(p.toLowerCase())) score += 1;

  return Math.min(score, 7);
});

const strengthPct = computed(() => (strengthScore.value / 7) * 100);

const strengthLabel = computed(() => {
  const s = strengthScore.value;
  if (s <= 2) return "Baja";
  if (s <= 4) return "Media";
  if (s <= 6) return "Alta";
  return "Muy alta";
});

const strengthClass = computed(() => {
  const s = strengthScore.value;
  if (s <= 2) return "is-low";
  if (s <= 4) return "is-medium";
  return "is-high";
});

const validate = () => {
  const nextErrors = {};

  const p1 = newPassword.value;
  const p2 = confirmPassword.value;

  if (!p1) {
    nextErrors.new_password = "La nueva contraseña es obligatoria.";
  } else if (p1.length < 8) {
    nextErrors.new_password = "La contraseña debe tener al menos 8 caracteres.";
  } else if (!/[a-zA-Z]/.test(p1)) {
    nextErrors.new_password = "La contraseña debe incluir al menos una letra.";
  } else if (!/\d/.test(p1)) {
    nextErrors.new_password = "La contraseña debe incluir al menos un número.";
  } else if (commonPasswords.includes(p1.toLowerCase())) {
    nextErrors.new_password = "Elija una contraseña menos común.";
  }

  if (!p2) {
    nextErrors.confirm_password = "Confirme la nueva contraseña.";
  } else if (p2 !== p1) {
    nextErrors.confirm_password = "Las contraseñas no coinciden.";
  }

  errors.value = nextErrors;
  return Object.keys(nextErrors).length === 0;
};

const resolveBackendError = (data) => {
  if (!data) return "";

  if (typeof data.detail === "string" && data.detail) return data.detail;
  if (typeof data.error === "string" && data.error) return data.error;

  const value = data.new_password;
  if (Array.isArray(value) && value[0]) return String(value[0]);
  if (typeof value === "string" && value) return value;

  return "";
};

const submitReset = async () => {
  status.value = { type: "", message: "" };

  if (!validate()) return;

  loading.value = true;
  status.value = { type: "info", message: "Actualizando contraseña..." };

  try {
    await api.post("/auth/password-reset/confirm/", {
      token: token.value,
      new_password: newPassword.value,
    });

    status.value = {
      type: "success",
      message: "Su contraseña fue actualizada correctamente. Ya puede iniciar sesión.",
    };

    newPassword.value = "";
    confirmPassword.value = "";
    show1.value = false;
    show2.value = false;
  } catch (err) {
    const backendDetail = resolveBackendError(err.response?.data);

    const msg = /token|enlace|expir/i.test(backendDetail)
      ? "El enlace de recuperación no es válido o ya expiró. Solicite uno nuevo."
      : backendDetail ||
        "No se pudo restablecer la contraseña. Verifique el enlace o solicite una nueva recuperación.";

    status.value = { type: "error", message: msg };
  } finally {
    loading.value = false;
  }
};

const goLogin = () => {
  router.replace("/login");
};

onMounted(() => {
  const tokenLocal = localStorage.getItem("access_token");

  if (tokenLocal && isJwtNotExpired(tokenLocal)) {
    router.replace("/home");
    return;
  }

  if (token.value) {
    passwordInputRef.value?.focus?.();
  }
});
</script>

<style src="../auth-base.css"></style>
<style src="./reset-password.css"></style>