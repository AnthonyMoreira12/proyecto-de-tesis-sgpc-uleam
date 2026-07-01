<template>
  <div class="sgpc-admin-modal modal-overlay" @click.self="emitClose">
    <div
      class="modal modal--activate"
      role="dialog"
      aria-modal="true"
      :aria-busy="saving ? 'true' : 'false'"
      aria-label="Activar cuenta"
    >
      <header class="modal__header activate-header">
        <div class="activate-heading">
          <span class="activate-kicker">Usuarios</span>

          <h2 class="modal__title activate-title">Activar cuenta</h2>

          <p class="activate-subtitle">
            Defina un correo y una contraseña válida para habilitar el acceso del usuario.
          </p>

          <dl class="activate-meta" aria-label="Resumen del usuario">
            <div class="activate-meta__item">
              <dt>Usuario</dt>
              <dd>{{ nombreCompleto || "Usuario" }}</dd>
            </div>

            <div class="activate-meta__item">
              <dt>Estado</dt>
              <dd>Pendiente</dd>
            </div>
          </dl>
        </div>

        <button
          type="button"
          class="activate-close modal__close"
          :disabled="saving"
          @click="emitClose"
          aria-label="Cerrar"
          title="Cerrar"
        >
          ✕
        </button>
      </header>

      <form class="modal__body activate-body" @submit.prevent="activar">
        <section class="activate-section" aria-label="Datos de acceso">
          <div class="activate-grid">
            <div class="activate-field">
              <label for="activate-email" class="activate-label">
                Correo electrónico
              </label>

              <input
                id="activate-email"
                v-model="email"
                class="field-control activate-input"
                type="email"
                placeholder="usuario@correo.com"
                autocomplete="email"
                inputmode="email"
                :disabled="saving"
                required
              />
            </div>

            <div class="activate-field">
              <label for="activate-password" class="activate-label">
                Contraseña
              </label>

              <input
                id="activate-password"
                v-model="password"
                class="field-control activate-input"
                type="password"
                placeholder="Mínimo 8 caracteres"
                autocomplete="new-password"
                :disabled="saving"
                required
              />
            </div>
          </div>

          <p class="activate-note">
            La cuenta quedará habilitada inmediatamente después de guardar.
          </p>
        </section>

        <div
          v-if="error"
          class="alerta error activate-error"
          role="alert"
          aria-live="polite"
        >
          {{ error }}
        </div>

        <footer class="modal__footer activate-footer">
          <button
            type="button"
            class="activate-cancel"
            :disabled="saving"
            @click="emitClose"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="activate-submit"
            :disabled="saving"
          >
            {{ saving ? "Activando..." : "Activar cuenta" }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
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

const saving = ref(false);
const error = ref("");

const email = ref("");
const password = ref("");

const emitClose = () => emit("close");

const cleanEmail = (value) => (value || "").trim().toLowerCase();

const resolveApiError = (data) => {
  if (!data) return "";
  if (typeof data?.detail === "string" && data.detail) return data.detail;
  if (typeof data?.error === "string" && data.error) return data.error;

  for (const key of ["email", "password", "non_field_errors"]) {
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

const nombreCompleto = computed(() => {
  const nombres = (props.usuario?.nombres || "").trim();
  const apellidos = (props.usuario?.apellidos || "").trim();
  return `${nombres} ${apellidos}`.trim();
});

watch(
  () => props.usuario,
  (usuario) => {
    error.value = "";
    password.value = "";
    email.value = cleanEmail(usuario?.email);
  },
  { immediate: true }
);

const activar = async () => {
  error.value = "";

  if (!props.usuario?.id) return;

  const mail = cleanEmail(email.value);
  const pass = (password.value || "").trim();

  if (!mail || !pass) {
    error.value = "Complete los campos obligatorios.";
    return;
  }

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail);
  if (!emailOk) {
    error.value = "Ingrese un correo válido.";
    return;
  }

  if (pass.length < 8) {
    error.value = "La contraseña debe tener al menos 8 caracteres.";
    return;
  }

  saving.value = true;

  try {
    await adminApi.activarUsuario(props.usuario.id, {
      email: mail,
      password: pass,
    });

    emit("done", {
      title: "Cuenta activada",
      message: `La cuenta de ${nombreCompleto.value || "este usuario"} fue activada correctamente.`,
    });
  } catch (e) {
    const data = e?.response?.data;
    const resolved = resolveApiError(data);

    error.value =
      resolved || "No se pudo activar la cuenta. Verifique la información e intente nuevamente.";

    openNotice({
      title: "No se pudo activar",
      message: error.value,
      details: data || null,
    });
  } finally {
    saving.value = false;
  }
};
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./activar-usuario-modal.css"></style>