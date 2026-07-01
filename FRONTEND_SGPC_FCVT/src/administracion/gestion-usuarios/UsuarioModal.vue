<template>
  <div class="sgpc-admin-modal modal-overlay" @click.self="emit('close')">
    <div
      class="modal modal--user"
      role="dialog"
      aria-modal="true"
      :aria-label="mode === 'create' ? 'Registrar usuario externo' : 'Editar usuario'"
    >
      <header class="modal__header usermodal-header">
        <div class="usermodal-titlewrap">
          <div class="usermodal-titleline">
            <h2 class="modal__title usermodal-title">
              {{ mode === "create" ? "Registrar usuario externo" : "Editar usuario" }}
            </h2>

            <div class="usermodal-badges" aria-label="Tipo y estado">
              <span class="usermodal-badge usermodal-badge--neutral">
                {{ tipoUsuarioLabel }}
              </span>

              <span class="usermodal-badge" :class="estadoBadgeClass">
                {{ estadoLabel }}
              </span>
            </div>
          </div>

          <p class="modal__subtitle usermodal-subtitle">
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
          :disabled="saving || actionBusy"
          @click="emit('close')"
          aria-label="Cerrar"
          title="Cerrar"
        >
          ✕
        </button>
      </header>

      <form class="usermodal-form" @submit.prevent="submit">
        <div class="usermodal-scroll">
          <section class="usermodal-section" aria-label="Datos personales">
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Datos personales</h3>
                <p class="usermodal-sectionsub">
                  Información principal para identificar la cuenta.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Nombres</label>

                <input
                  v-model="form.nombres"
                  class="field-control usermodal-input"
                  required
                  placeholder="Ej.: Andrea Sofía"
                  autocomplete="given-name"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Apellidos</label>

                <input
                  v-model="form.apellidos"
                  class="field-control usermodal-input"
                  required
                  placeholder="Ej.: García López"
                  autocomplete="family-name"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Correo electrónico</label>

                <input
                  v-model="form.email"
                  class="field-control usermodal-input"
                  required
                  type="email"
                  placeholder="Ej.: usuario@correo.com"
                  :disabled="emailLocked"
                  :class="{ 'input-readonly': emailLocked }"
                  autocomplete="email"
                  inputmode="email"
                />

                <p v-if="emailLocked" class="usermodal-help">
                  Cuenta institucional: el correo no se modifica desde este panel.
                </p>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label usermodal-label--with-help">
                  <span>Identificación</span>

                  <InfoTip title="Identificación">
                    Dato único para evitar duplicados. Debe tener 10 dígitos numéricos.
                  </InfoTip>
                </label>

                <input
                  v-model="form.identificacion"
                  class="field-control usermodal-input"
                  :required="mode === 'create'"
                  placeholder="Ej.: 1312345678"
                  autocomplete="off"
                  inputmode="numeric"
                />

                <p class="usermodal-help">
                  Solo números, sin espacios ni guiones.
                </p>
              </div>
            </div>
          </section>

          <section
            v-if="showAcademicoSection"
            class="usermodal-section"
            aria-label="Asignación académica"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Asignación académica</h3>
                <p class="usermodal-sectionsub">
                  Complete o corrija la facultad y carrera asignadas al usuario institucional.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Facultad</label>

                <select
                  v-model="form.facultad"
                  class="field-control usermodal-input"
                  :disabled="saving || loadingCatalogos"
                  required
                  @change="onFacultadChange"
                >
                  <option value="">Seleccione una facultad</option>

                  <option
                    v-for="f in facultades"
                    :key="f.value"
                    :value="f.value"
                  >
                    {{ f.label }}
                  </option>
                </select>

                <p v-if="loadingCatalogos" class="usermodal-help">
                  Cargando facultades...
                </p>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Carrera</label>

                <select
                  v-model="form.carrera"
                  class="field-control usermodal-input"
                  :disabled="saving || loadingCatalogos || !form.facultad"
                  required
                >
                  <option value="">Seleccione una carrera</option>

                  <option
                    v-for="c in carreras"
                    :key="c.value"
                    :value="c.value"
                  >
                    {{ c.label }}
                  </option>
                </select>

                <p v-if="form.facultad && loadingCarreras" class="usermodal-help">
                  Cargando carreras...
                </p>
              </div>
            </div>

            <p v-if="isInstitucional" class="usermodal-note usermodal-note--info">
              La autenticación sigue gestionada por Microsoft. Esta asignación solo corrige la relación académica interna.
            </p>
          </section>

          <section
            v-if="mode === 'edit'"
            class="usermodal-section"
            aria-label="Control de edición del perfil"
          >
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Control de edición</h3>
                <p class="usermodal-sectionsub">
                  Habilite, extienda o bloquee la edición del perfil del usuario.
                </p>
              </div>

              <InfoTip title="Control de edición">
                Habilitar desbloquea y reinicia intentos. Extender suma horas al plazo. Bloquear impide editar el perfil.
              </InfoTip>
            </div>

            <div class="usermodal-status-grid">
              <div class="usermodal-status">
                <span>Bloqueado</span>
                <strong>{{ uiProfileLockedLabel }}</strong>
              </div>

              <div class="usermodal-status">
                <span>Intentos</span>
                <strong>{{ uiAttemptsLeftLabel }}</strong>
              </div>

              <div class="usermodal-status">
                <span>Límite</span>
                <strong>{{ uiProfileUntilLabel }}</strong>
              </div>
            </div>

            <div class="usermodal-control-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Extender edición</label>

                <div class="extend-row">
                  <select
                    v-model="extendHours"
                    class="field-control usermodal-input"
                    :disabled="saving || actionBusy"
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
                    :disabled="saving || actionBusy"
                    @click="handleExtenderEdicion"
                  >
                    {{ actionBusy ? "Procesando..." : "Extender" }}
                  </button>
                </div>
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Razón de bloqueo</label>

                <input
                  v-model="blockReason"
                  class="field-control usermodal-input"
                  :disabled="saving || actionBusy"
                  maxlength="255"
                  placeholder="Ej.: Validación pendiente"
                />
              </div>
            </div>

            <div class="perfil-actions">
              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--primary"
                :disabled="saving || actionBusy"
                @click="handleHabilitarEdicion"
              >
                {{ actionBusy ? "Procesando..." : "Habilitar edición" }}
              </button>

              <button
                type="button"
                class="usermodal-action-btn usermodal-action-btn--danger"
                :disabled="saving || actionBusy"
                @click="handleBloquearEdicion"
              >
                {{ actionBusy ? "Procesando..." : "Bloquear edición" }}
              </button>
            </div>

            <p class="usermodal-help">
              Este control no modifica credenciales Microsoft ni el estado activo/inactivo de la cuenta.
            </p>
          </section>

          <section class="usermodal-section" aria-label="Perfil y permisos">
            <div class="usermodal-sectionhead">
              <div>
                <h3 class="usermodal-sectiontitle">Perfil y permisos</h3>
                <p class="usermodal-sectionsub">
                  Verifique el tipo de cuenta, estado y privilegios administrativos.
                </p>
              </div>
            </div>

            <div class="usermodal-grid">
              <div class="usermodal-field">
                <label class="usermodal-label">Tipo de cuenta</label>
                <input
                  :value="tipoUsuarioLabel"
                  disabled
                  class="field-control usermodal-input input-readonly"
                />
              </div>

              <div class="usermodal-field">
                <label class="usermodal-label">Estado de la cuenta</label>
                <input
                  :value="estadoLabel"
                  disabled
                  class="field-control usermodal-input input-readonly"
                />
              </div>
            </div>

            <template v-if="mode === 'edit'">
              <label class="usermodal-checkline">
                <input type="checkbox" v-model="form.is_staff" />

                <span>
                  <strong>Permisos de administración</strong>
                  <small>
                    Actívelo solo si gestionará usuarios, catálogos o publicaciones globales.
                  </small>
                </span>
              </label>
            </template>

            <template v-else>
              <p class="usermodal-note usermodal-note--info">
                Los usuarios externos nuevos se crean sin privilegios administrativos.
              </p>

              <p class="usermodal-note usermodal-note--warn">
                Al guardar, la cuenta se registrará como <b>Pendiente</b>. Para habilitar acceso:
                <b>Pendientes → Activar cuenta</b>.
              </p>
            </template>
          </section>

          <div v-if="error" class="usermodal-alert" role="alert" aria-live="polite">
            {{ error }}
          </div>
        </div>

        <footer class="modal__footer usermodal-footer">
          <button
            type="button"
            class="btn-cerrar"
            :disabled="saving || actionBusy"
            @click="emit('close')"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="btn-guardar"
            :disabled="saving || actionBusy"
          >
            {{ saving ? "Guardando..." : mode === "create" ? "Registrar" : "Guardar cambios" }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

import { adminApi } from "../../scripts/api/adminApi";
import { useNotice } from "../../scripts/composables/useNotice";

import InfoTip from "../../inicio/ui/InfoTip.vue";

const props = defineProps({
  mode: { type: String, required: true },
  usuario: { type: Object, default: null },
});

const emit = defineEmits(["close", "done"]);
const { openNotice } = useNotice();

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

const isInstitucional = computed(() => {
  return props.mode === "edit" && props.usuario?.auth_source === "microsoft";
});

const isExterno = computed(() => {
  if (props.mode === "create") return true;

  return (
    props.usuario?.auth_source === "local" &&
    props.usuario?.rol === "autor_externo"
  );
});

const isPendiente = computed(() => {
  if (props.mode === "create") return true;
  return isExterno.value && !props.usuario?.is_active;
});

const emailLocked = computed(() => props.mode === "edit" && isInstitucional.value);

const tipoUsuarioLabel = computed(() => {
  if (props.mode === "create") return "Externo";
  if (isInstitucional.value) return "Institucional";
  if (isExterno.value) return "Externo";
  return "Usuario";
});

const estadoLabel = computed(() => {
  if (props.mode === "create") return "Pendiente";
  if (isPendiente.value) return "Pendiente";
  return props.usuario?.is_active ? "Activo" : "Inactivo";
});

const estadoBadgeClass = computed(() => {
  const value = String(estadoLabel.value || "").toLowerCase().trim();

  if (value.includes("pend")) return "usermodal-badge--warn";
  if (value.includes("inactivo")) return "usermodal-badge--off";
  if (value.includes("activo")) return "usermodal-badge--ok";

  return "usermodal-badge--neutral";
});

const showAcademicoSection = computed(() => {
  if (props.mode !== "edit") return false;
  if (isExterno.value) return false;
  return true;
});

const uiProfileLockedLabel = computed(() => {
  if (profileLocked.value === null || profileLocked.value === undefined) return "—";
  return profileLocked.value ? "Sí" : "No";
});

const uiAttemptsLeftLabel = computed(() => {
  if (attemptsLeft.value === null || attemptsLeft.value === undefined) return "—";
  return String(attemptsLeft.value);
});

const uiProfileUntilLabel = computed(() => {
  if (!profileUntil.value) return "—";

  try {
    const date = new Date(profileUntil.value);
    if (Number.isNaN(date.getTime())) return String(profileUntil.value);
    return date.toLocaleString();
  } catch {
    return String(profileUntil.value);
  }
});

const toSelectOptions = (arr) => {
  if (!Array.isArray(arr)) return [];

  return arr.map((item) => ({
    value: item.id ?? item.value,
    label: item.nombre ?? item.label ?? String(item),
  }));
};

const resolveApiError = (data) => {
  if (!data) return "";

  if (typeof data?.detail === "string" && data.detail) return data.detail;
  if (typeof data?.error === "string" && data.error) return data.error;

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

    if (Array.isArray(value) && value[0]) return String(value[0]);
    if (typeof value === "string" && value) return value;
  }

  const firstKey = Object.keys(data || {})[0];
  const firstValue = firstKey ? data[firstKey] : null;

  if (Array.isArray(firstValue) && firstValue[0]) return String(firstValue[0]);
  if (typeof firstValue === "string" && firstValue) return firstValue;

  return "";
};

const loadFacultades = async () => {
  loadingCatalogos.value = true;

  try {
    const data = await adminApi.selectsFacultades();
    facultades.value = toSelectOptions(data);
  } catch {
    facultades.value = [];
    error.value = "No se pudieron cargar las facultades.";
  } finally {
    loadingCatalogos.value = false;
  }
};

const loadCarreras = async (facultadId) => {
  carreras.value = [];

  if (!facultadId) return;

  loadingCarreras.value = true;

  try {
    const data = await adminApi.selectsCarrerasByFacultad(facultadId);
    carreras.value = toSelectOptions(data);
  } catch {
    carreras.value = [];
    error.value = "No se pudieron cargar las carreras.";
  } finally {
    loadingCarreras.value = false;
  }
};

const onFacultadChange = async () => {
  form.carrera = "";
  await loadCarreras(form.facultad);
};

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
    form.identificacion = usuario.identificacion || "";
    form.is_staff = !!usuario.is_staff;
    form.facultad = usuario.facultad ?? "";
    form.carrera = usuario.carrera ?? "";

    profileLocked.value = usuario.profile_edit_locked ?? null;
    attemptsLeft.value = usuario.profile_edit_attempts_left ?? null;
    profileUntil.value = usuario.profile_edit_until ?? null;

    extendHours.value = 24;
    blockReason.value = "";

    if (showAcademicoSection.value) {
      await loadFacultades();

      if (form.facultad) {
        await loadCarreras(form.facultad);
      }
    } else {
      facultades.value = [];
      carreras.value = [];
    }
  },
  { immediate: true }
);

const handleHabilitarEdicion = async () => {
  if (!form.id) return;

  actionBusy.value = true;

  try {
    const res = await adminApi.habilitarEdicionPerfil(form.id);

    profileLocked.value = res?.profile_edit_locked ?? false;
    attemptsLeft.value = res?.profile_edit_attempts_left ?? 3;
    profileUntil.value = res?.profile_edit_until ?? null;

    openNotice({
      title: "Edición habilitada",
      message: "Listo. El usuario ya puede editar su perfil nuevamente.",
    });
  } catch (e) {
    const data = e?.response?.data;

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
  if (!form.id) return;

  actionBusy.value = true;

  try {
    const horas = Number(extendHours.value || 24);
    const res = await adminApi.extenderEdicionPerfil(form.id, horas);

    if (res && typeof res === "object") {
      if ("profile_edit_until" in res) profileUntil.value = res.profile_edit_until;
      if ("profile_edit_locked" in res) profileLocked.value = !!res.profile_edit_locked;
      if ("profile_edit_attempts_left" in res) {
        attemptsLeft.value = res.profile_edit_attempts_left;
      }
    }

    openNotice({
      title: "Edición extendida",
      message: `Listo. Se extendió el plazo de edición en ${horas} horas.`,
    });
  } catch (e) {
    const data = e?.response?.data;

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
  if (!form.id) return;

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
        const res = await adminApi.bloquearEdicionPerfil(form.id, blockReason.value);

        profileLocked.value = res?.profile_edit_locked ?? true;
        attemptsLeft.value = res?.profile_edit_attempts_left ?? 0;
        profileUntil.value = res?.profile_edit_until ?? null;

        openNotice({
          title: "Edición bloqueada",
          message: "Listo. El usuario no podrá editar su perfil hasta nueva habilitación.",
        });
      } catch (e) {
        const data = e?.response?.data;

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

const submit = async () => {
  error.value = "";
  saving.value = true;

  try {
    const nombres = String(form.nombres || "").trim();
    const apellidos = String(form.apellidos || "").trim();
    const email = String(form.email || "").trim().toLowerCase();
    const identificacionRaw = String(form.identificacion || "").trim();
    const identificacion = identificacionRaw || null;

    if (!nombres || !apellidos || !email) {
      error.value = "Complete los campos obligatorios antes de guardar.";
      return;
    }

    if (props.mode === "create" && !identificacion) {
      error.value = "Ingrese la identificación del usuario externo.";
      return;
    }

    if (identificacion && !/^\d+$/.test(identificacion)) {
      error.value = "La identificación debe contener solo números.";
      return;
    }

    if (identificacion && identificacion.length !== 10) {
      error.value = "La identificación debe tener 10 dígitos numéricos.";
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
        message: "Se registró correctamente. Para permitir acceso: Pendientes → Activar cuenta.",
      });

      return;
    }

    if (!form.id) {
      throw new Error("ID faltante en edición.");
    }

    const payload = {
      nombres,
      apellidos,
      email,
      identificacion,
      is_staff_set: !!form.is_staff,
    };

    if (showAcademicoSection.value) {
      const facultad = form.facultad ? Number(form.facultad) : null;
      const carrera = form.carrera ? Number(form.carrera) : null;

      if (!facultad || !carrera) {
        error.value = "Seleccione facultad y carrera para completar la asignación académica.";
        return;
      }

      payload.facultad = facultad;
      payload.carrera = carrera;
    }

    await adminApi.editarUsuario(form.id, payload);

    emit("done", {
      title: "Cambios guardados",
      message: "Listo. Los datos del usuario se actualizaron correctamente.",
    });
  } catch (e) {
    const data = e?.response?.data;

    error.value = resolveApiError(data) || "No se pudo guardar la información.";

    openNotice({
      title: "No se pudo guardar",
      message: error.value || "Revise los campos e intente nuevamente.",
    });
  } finally {
    saving.value = false;
  }
};
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./usuario-modal.css"></style>