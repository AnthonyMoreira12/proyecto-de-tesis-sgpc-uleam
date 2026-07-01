<template>
  <div class="perfil-container">
    <div v-if="loading" class="perfil-shell perfil-shell--loading">
      <section class="perfil-hero perfil-hero--skeleton">
        <div class="sk-kicker"></div>
        <div class="sk-title"></div>
        <div class="sk-text"></div>

        <div class="sk-pills">
          <div class="sk-pill"></div>
          <div class="sk-pill"></div>
          <div class="sk-pill"></div>
        </div>
      </section>

      <div class="perfil-layout perfil-skeleton">
        <aside class="perfil-sidebar">
          <div class="perfil-sidebar-card">
            <div class="sk-avatar"></div>
            <div class="sk-line w-70"></div>
            <div class="sk-line w-50"></div>

            <div class="sk-tags">
              <div class="sk-pill"></div>
              <div class="sk-pill"></div>
            </div>

            <div class="sk-actions">
              <div class="sk-btn"></div>
              <div class="sk-btn"></div>
            </div>
          </div>
        </aside>

        <main class="perfil-main">
          <div class="sk-card sk-card--notice"></div>
          <div class="sk-card sk-card--panel"></div>
          <div class="sk-card sk-card--panel"></div>
        </main>
      </div>
    </div>

    <div v-else-if="user" class="perfil-shell">
      <header class="perfil-hero page-stage page-hero page-stage-1">
        <div class="perfil-hero__copy">
          <p class="perfil-kicker">Mi cuenta</p>
          <h1 class="perfil-title">Perfil</h1>
          <p class="perfil-subtitle">
            Consulta el estado de tu cuenta y mantén actualizada tu información institucional.
          </p>
        </div>

        <div class="perfil-hero__meta">
          <div class="perfil-head-pills" aria-label="Resumen del perfil">
            <span
              class="head-pill"
              :class="perfilCompletoCalculado ? 'is-ok' : 'is-warn'"
            >
              {{ profileCompletion }}% completo
            </span>

            <span
              class="head-pill"
              :class="canEditProfile ? 'is-ok' : 'is-warn'"
            >
              {{ canEditProfile ? "Edición disponible" : "Edición cerrada" }}
            </span>

            <span class="head-pill">
              {{ user.auth_source === "microsoft" ? "Microsoft 365" : "Cuenta local" }}
            </span>
          </div>

          <button
            class="btn-pill"
            :class="canEditProfile ? 'btn-pill--primary' : 'btn-pill--ghost'"
            type="button"
            :title="canEditProfile ? 'Editar perfil' : editDisabledReason"
            @click="handleEditAction"
          >
            {{ canEditProfile ? "Editar perfil" : "Solicitar edición" }}
          </button>
        </div>
      </header>

      <div class="perfil-layout page-stage page-content page-stage-2">
        <aside class="perfil-sidebar">
          <section class="perfil-sidebar-card">
            <button
              class="perfil-avatar-button"
              type="button"
              :title="avatarButtonLabel"
              :aria-label="avatarButtonLabel"
              @click="openAvatarFlow"
            >
              <img
                v-if="hasAvatar"
                :src="user.avatar_url"
                alt="Foto de perfil"
                class="perfil-avatar"
              />

              <div v-else class="perfil-avatar-placeholder">
                {{ initials }}
              </div>
            </button>

            <div class="perfil-identidad">
              <p class="perfil-eyebrow">Cuenta</p>
              <h2 class="perfil-nombre">{{ displayName }}</h2>
              <p class="perfil-correo">{{ user.email || "Sin correo registrado" }}</p>
            </div>

            <div class="perfil-tags">
              <span class="tag tag-rol">{{ roleLabel }}</span>

              <span v-if="isAdmin" class="tag tag-admin">
                Administrador
              </span>

              <span
                :class="[
                  'tag',
                  perfilCompletoCalculado ? 'tag-ok' : 'tag-warn'
                ]"
              >
                {{ perfilCompletoCalculado ? "Completo" : "Pendiente" }}
              </span>
            </div>

            <div class="sidebar-primary-actions">
              <button
                class="btn-action btn-action--primary"
                type="button"
                @click="openAvatarFlow"
              >
                {{ hasAvatar ? "Actualizar foto" : "Agregar foto" }}
              </button>

              <p class="avatar-help">
                JPG, PNG o WEBP · máximo {{ avatarMaxSizeLabel }}
              </p>
            </div>

            <div class="sidebar-divider"></div>

            <div class="sidebar-actions-block">
              <div class="sidebar-section-title">Acceso</div>

              <div class="sidebar-actions">
                <button
                  v-if="isAdmin"
                  class="btn-action"
                  type="button"
                  @click="irAPanelAdmin"
                >
                  Panel administrativo
                </button>

                <button
                  class="btn-action btn-action--danger"
                  type="button"
                  @click="cerrarSesion"
                >
                  Cerrar sesión
                </button>
              </div>

              <p v-if="user.auth_source === 'microsoft'" class="sidebar-hint">
                Cuenta sincronizada con Microsoft 365.
              </p>
            </div>
          </section>
        </aside>

        <main class="perfil-main">
          <section v-if="showIncompleteBanner" class="perfil-card perfil-notice">
            <div class="perfil-notice__copy">
              <div class="perfil-notice__title">
                Información pendiente
              </div>

              <div class="perfil-notice__text">
                Completa los datos faltantes para mantener actualizado tu perfil institucional.
              </div>

              <div class="perfil-notice__meta">
                <span class="notice-chip">
                  Progreso: <strong>{{ profileCompletion }}%</strong>
                </span>

                <span v-if="missingFields.length" class="notice-chip">
                  Pendiente: <strong>{{ missingFields.join(", ") }}</strong>
                </span>

                <span v-if="tiempoRestante" class="notice-chip">
                  Edición:
                  <strong>{{ tiempoRestante.horas }}h {{ tiempoRestante.minutos }}m</strong>
                </span>
              </div>

              <div class="progress-bar" aria-hidden="true">
                <div
                  class="progress-fill"
                  :style="{ width: profileCompletion + '%' }"
                ></div>
              </div>
            </div>

            <div class="perfil-notice__actions">
              <button
                class="btn-mini btn-mini--primary"
                type="button"
                @click="handleEditAction"
              >
                Completar datos
              </button>

              <button
                class="btn-mini"
                type="button"
                @click="dismissIncompleteBanner"
              >
                Luego
              </button>
            </div>
          </section>

          <section class="perfil-card perfil-card--data">
            <div class="section-head">
              <div>
                <h3 class="section-title">Datos institucionales</h3>
                <p class="section-subtitle">
                  Información principal registrada en el sistema.
                </p>
              </div>

              <span
                class="section-chip"
                :class="perfilCompletoCalculado ? 'chip-ok' : 'chip-warn'"
              >
                {{ perfilCompletoCalculado ? "Completo" : "Pendiente" }}
              </span>
            </div>

            <dl class="perfil-fields">
              <div class="perfil-field perfil-field--wide">
                <dt>{{ correoLabel }}</dt>

                <dd class="dd-row">
                  <span class="mono">{{ user.email || "—" }}</span>

                  <button
                    v-if="user.email"
                    class="icon-btn"
                    type="button"
                    aria-label="Copiar correo"
                    title="Copiar correo"
                    @click="copyText(user.email)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M8 8V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2"
                      />
                      <path
                        d="M6 8h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2Z"
                      />
                    </svg>
                  </button>
                </dd>
              </div>

              <div class="perfil-field">
                <dt>Identificación</dt>

                <dd class="dd-row">
                  <span
                    class="mono"
                    :class="{ 'is-empty': !user.identificacion }"
                  >
                    {{ user.identificacion || "Pendiente" }}
                  </span>

                  <button
                    v-if="user.identificacion"
                    class="icon-btn"
                    type="button"
                    aria-label="Copiar identificación"
                    title="Copiar identificación"
                    @click="copyText(String(user.identificacion))"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M8 8V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2"
                      />
                      <path
                        d="M6 8h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2Z"
                      />
                    </svg>
                  </button>
                </dd>
              </div>

              <div
                v-if="!isExternalAuthor"
                class="perfil-field perfil-field--wide"
              >
                <dt>Facultad</dt>
                <dd :class="{ 'is-empty': !facultadLabel }">
                  {{ facultadLabel || "Pendiente" }}
                </dd>
              </div>

              <div
                v-if="!isExternalAuthor"
                class="perfil-field"
              >
                <dt>Carrera</dt>
                <dd :class="{ 'is-empty': !carreraLabel }">
                  {{ carreraLabel || "Pendiente" }}
                </dd>
              </div>

              <div class="perfil-field">
                <dt>Registro</dt>
                <dd>
                  {{ user.fecha_registro ? formatFecha(user.fecha_registro) : "N/A" }}
                </dd>
              </div>

              <div
                v-if="user.auth_source === 'microsoft'"
                class="perfil-field"
              >
                <dt>Sincronización</dt>
                <dd>
                  {{ user.ms_last_sync ? formatFechaTime(user.ms_last_sync) : "Sin sincronización" }}
                </dd>
              </div>
            </dl>
          </section>

          <section class="perfil-card perfil-card--status">
            <div class="section-head">
              <div>
                <h3 class="section-title">Estado de la cuenta</h3>
                <p class="section-subtitle">
                  Resumen de acceso, permisos y edición.
                </p>
              </div>

              <span class="section-chip">Resumen</span>
            </div>

            <div class="perfil-status-grid">
              <article class="status-item status-item--progress">
                <div class="status-top">
                  <span class="status-kicker">Progreso del perfil</span>

                  <span
                    class="status-pill"
                    :class="perfilCompletoCalculado ? 'status-pill-ok' : 'status-pill-warn'"
                  >
                    {{ profileCompletion }}%
                  </span>
                </div>

                <div class="status-value">
                  {{ perfilCompletoCalculado ? "Información completa" : "Información pendiente" }}
                </div>

                <p class="status-note">
                  {{ perfilCompletoCalculado
                    ? "El perfil tiene los datos requeridos."
                    : "Existen datos requeridos que aún no han sido registrados."
                  }}
                </p>

                <div class="progress-bar progress-bar--status" aria-hidden="true">
                  <div
                    class="progress-fill"
                    :style="{ width: profileCompletion + '%' }"
                  ></div>
                </div>
              </article>

              <article class="status-item">
                <div class="status-top">
                  <span class="status-kicker">Autenticación</span>

                  <span
                    class="status-pill"
                    :class="user.auth_source === 'microsoft' ? 'status-pill-info' : 'status-pill-neutral'"
                  >
                    {{ user.auth_source === "microsoft" ? "Microsoft 365" : "Local" }}
                  </span>
                </div>

                <div class="status-value">
                  {{ user.auth_source === "microsoft" ? "Sincronizada" : "Cuenta local" }}
                </div>

                <p class="status-note">
                  {{ authSourceNote }}
                </p>
              </article>

              <article class="status-item">
                <div class="status-top">
                  <span class="status-kicker">Tipo de cuenta</span>

                  <span class="status-pill status-pill-neutral">
                    {{ isExternalAuthor ? "Externa" : "Institucional" }}
                  </span>
                </div>

                <div class="status-value">
                  {{ roleLabel }}
                </div>

                <p class="status-note">
                  {{ isExternalAuthor ? "Registro externo." : "Cuenta vinculada a la institución." }}
                </p>
              </article>

              <article class="status-item">
                <div class="status-top">
                  <span class="status-kicker">Edición</span>

                  <span
                    class="status-pill"
                    :class="canEditProfile ? 'status-pill-ok' : 'status-pill-warn'"
                  >
                    {{ canEditProfile ? "Disponible" : "Cerrada" }}
                  </span>
                </div>

                <div class="status-value">
                  <template v-if="tiempoRestante">
                    {{ tiempoRestante.horas }}h {{ tiempoRestante.minutos }}m
                  </template>

                  <template v-else>
                    No disponible
                  </template>
                </div>

                <p class="status-note">
                  <template v-if="tiempoRestante">
                    Puedes actualizar tu perfil desde esta vista.
                  </template>

                  <template v-else>
                    Solicita cambios al administrador.
                  </template>
                </p>
              </article>
            </div>
          </section>
        </main>
      </div>
    </div>

    <div v-else class="perfil-shell perfil-shell--error">
      <div class="perfil-error">
        <p>No se pudo cargar el perfil.</p>

        <button
          class="btn-pill btn-pill--primary"
          type="button"
          @click="reloadProfile"
        >
          Reintentar
        </button>
      </div>
    </div>

    <Transition name="modal-fade">
      <div
        v-if="toast.show"
        class="toast"
        :class="toast.type"
        aria-live="polite"
      >
        <span class="toast-text">{{ toast.message }}</span>

        <button
          class="toast-x"
          type="button"
          @click="hideToast"
          aria-label="Cerrar notificación"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M18 6 6 18" />
            <path d="M6 6 18 18" />
          </svg>
        </button>
      </div>
    </Transition>

    <PerfilAvatarModal
      v-model="showAvatarModal"
      :user="user"
      :initials="initials"
      :has-avatar="hasAvatar"
      :max-file-size="MAX_AVATAR_FILE_SIZE"
      :avatar-max-size-label="avatarMaxSizeLabel"
      @updated="handleAvatarUpdated"
      @toast="showToast"
    />

    <Transition name="modal-fade">
      <div
        v-if="showEditModal"
        class="modal-overlay"
        @mousedown.self="closeEditModal"
      >
        <div
          class="edit-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-profile-title"
        >
          <div class="modal-head">
            <div class="modal-head__copy">
              <h3 id="edit-profile-title" class="edit-title">
                Actualizar perfil
              </h3>

              <p class="modal-subtitle">
                Modifica únicamente los datos habilitados para tu cuenta.
              </p>
            </div>

            <button
              class="perfil-modal-close perfil-modal-close--danger"
              type="button"
              @click="closeEditModal"
              aria-label="Cerrar"
              title="Cerrar"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18 6 6 18" />
                <path d="M6 6 18 18" />
              </svg>
            </button>
          </div>

          <div class="edit-body">
            <div class="edit-form">
              <label class="edit-label">
                <span>Identificación</span>

                <input
                  v-model.trim="form.identificacion"
                  class="edit-input"
                  maxlength="10"
                  inputmode="numeric"
                  autocomplete="off"
                  :disabled="!canEditProfile || savingProfile"
                />

                <span class="help">
                  Debe contener exactamente 10 dígitos.
                </span>
              </label>

              <template v-if="!isExternalAuthor">
                <label class="edit-label">
                  <span>Facultad</span>

                  <select
                    v-model="form.facultad_id"
                    class="edit-input"
                    :disabled="!canEditProfile || savingProfile"
                    @change="onFacultadChange"
                  >
                    <option value="">Seleccione facultad</option>

                    <option
                      v-for="f in facultades"
                      :key="f.id"
                      :value="f.id"
                    >
                      {{ f.nombre }}
                    </option>
                  </select>
                </label>

                <label class="edit-label">
                  <span>Carrera</span>

                  <select
                    v-model="form.carrera_id"
                    class="edit-input"
                    :disabled="
                      !canEditProfile ||
                      savingProfile ||
                      loadingCarreras ||
                      !form.facultad_id
                    "
                  >
                    <option value="">Seleccione carrera</option>

                    <option
                      v-for="c in carreras"
                      :key="c.id"
                      :value="c.id"
                    >
                      {{ c.nombre }}
                    </option>
                  </select>

                  <span v-if="loadingCarreras" class="help">
                    Cargando carreras...
                  </span>

                  <span v-else-if="form.facultad_id && !carreras.length" class="help">
                    No hay carreras disponibles para esta facultad.
                  </span>
                </label>
              </template>
            </div>

            <p v-if="editError" class="edit-error">
              {{ editError }}
            </p>
          </div>

          <div class="edit-actions">
            <button
              v-if="canEditProfile"
              class="btn-pill btn-pill--success"
              type="button"
              :disabled="savingProfile"
              @click="saveProfile"
            >
              {{ savingProfile ? "Guardando..." : "Guardar cambios" }}
            </button>

            <button
              class="btn-pill btn-pill--danger"
              type="button"
              :disabled="savingProfile"
              @click="closeEditModal"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";
import PerfilAvatarModal from "./componentes/PerfilAvatarModal.vue";

const router = useRouter();
const userStore = useUserStore();

const MAX_AVATAR_FILE_SIZE = 1 * 1024 * 1024;

const prettyBytes = (bytes) => {
  const size = Number(bytes || 0);
  if (size <= 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  let value = size;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const avatarMaxSizeLabel = prettyBytes(MAX_AVATAR_FILE_SIZE);

const user = ref(null);
const loading = ref(true);
const now = ref(Date.now());
let clockId = null;

const showAvatarModal = ref(false);
const showEditModal = ref(false);
const savingProfile = ref(false);
const editError = ref("");

const facultades = ref([]);
const carreras = ref([]);
const loadingCarreras = ref(false);

const toast = ref({
  show: false,
  type: "info",
  message: "",
  t: null,
});

const form = ref({
  identificacion: "",
  facultad_id: "",
  carrera_id: "",
});

const asArray = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
};

const getUserFacultadLabel = (u) => {
  return u?.facultad_nombre || u?.facultad || "";
};

const getUserCarreraLabel = (u) => {
  return u?.carrera_nombre || u?.carrera || "";
};

const facultadLabel = computed(() => getUserFacultadLabel(user.value));
const carreraLabel = computed(() => getUserCarreraLabel(user.value));

const correoLabel = computed(() => {
  return user.value?.auth_source === "microsoft"
    ? "Correo institucional"
    : "Correo electrónico";
});

const initials = computed(() => {
  const nombres = (user.value?.nombres || "").trim();
  const apellidos = (user.value?.apellidos || "").trim();
  return `${nombres[0] || ""}${apellidos[0] || ""}`.toUpperCase() || "U";
});

const displayName = computed(() => {
  if (user.value?.auth_source === "microsoft" && user.value?.ms_display_name) {
    return user.value.ms_display_name;
  }

  return `${user.value?.nombres || ""} ${user.value?.apellidos || ""}`.trim() || "Usuario";
});

const hasAvatar = computed(() => !!user.value?.avatar_url);

const avatarButtonLabel = computed(() =>
  hasAvatar.value ? "Actualizar foto de perfil" : "Agregar foto de perfil"
);

const isExternalAuthor = computed(
  () => String(user.value?.rol || "").toLowerCase() === "autor_externo"
);

const isAdmin = computed(() =>
  !!(user.value?.is_staff || user.value?.is_superuser || user.value?.es_admin)
);

const roleLabel = computed(() => {
  if (isExternalAuthor.value) return "Autor externo";
  if (String(user.value?.rol || "").toLowerCase() === "autor") return "Autor";
  return "Usuario";
});

const perfilCompletoCalculado = computed(() => {
  const u = user.value;
  if (!u) return false;

  const identOk = !!u.identificacion;
  if (isExternalAuthor.value) return identOk;

  const facOk = !!(u.facultad_id || getUserFacultadLabel(u));
  const carOk = !!(u.carrera_id || getUserCarreraLabel(u));

  return identOk && facOk && carOk;
});

const canEditProfile = computed(() => {
  const u = user.value;
  if (!u) return false;

  if (u.profile_edit_locked) return false;

  if (u.profile_edit_until) {
    const until = new Date(u.profile_edit_until);
    if (!Number.isNaN(until.getTime())) {
      return now.value <= until.getTime();
    }
  }

  if (!u.fecha_registro) return true;

  const created = new Date(u.fecha_registro);
  if (Number.isNaN(created.getTime())) return true;

  const diffHours = (now.value - created.getTime()) / (1000 * 60 * 60);
  return diffHours <= 48;
});

const tiempoRestante = computed(() => {
  const u = user.value;
  if (!u) return null;

  let limiteMs = null;

  if (u.profile_edit_until) {
    const until = new Date(u.profile_edit_until).getTime();
    if (!Number.isNaN(until)) limiteMs = until;
  }

  if (!limiteMs) {
    if (!u.fecha_registro) return null;

    const created = new Date(u.fecha_registro).getTime();
    if (Number.isNaN(created)) return null;

    limiteMs = created + 48 * 60 * 60 * 1000;
  }

  const diff = limiteMs - now.value;
  if (diff <= 0) return null;

  const horas = Math.floor(diff / (1000 * 60 * 60));
  const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return { horas, minutos };
});

const editDisabledReason = computed(() => {
  if (user.value?.profile_edit_locked) {
    return user.value?.profile_edit_lock_reason || "La edición de perfil está bloqueada por el sistema.";
  }

  return "El periodo de edición de perfil ha finalizado. Solicita cambios al administrador.";
});

const showIncompleteBanner = computed(() => {
  const u = user.value;
  if (!u) return false;
  if (perfilCompletoCalculado.value) return false;

  if (u.perfil_banner_snooze_until) {
    const until = new Date(u.perfil_banner_snooze_until);
    if (!Number.isNaN(until.getTime()) && now.value < until.getTime()) return false;
  }

  return canEditProfile.value;
});

const missingFields = computed(() => {
  const u = user.value;
  if (!u) return [];

  const faltantes = [];

  if (!u.identificacion) faltantes.push("Identificación");

  if (!isExternalAuthor.value) {
    if (!(u.facultad_id || getUserFacultadLabel(u))) faltantes.push("Facultad");
    if (!(u.carrera_id || getUserCarreraLabel(u))) faltantes.push("Carrera");
  }

  return faltantes;
});

const profileCompletion = computed(() => {
  const u = user.value;
  if (!u) return 0;

  if (isExternalAuthor.value) return u.identificacion ? 100 : 0;

  let completos = 0;
  if (u.identificacion) completos++;
  if (u.facultad_id || getUserFacultadLabel(u)) completos++;
  if (u.carrera_id || getUserCarreraLabel(u)) completos++;

  return Math.round((completos / 3) * 100);
});

const authSourceNote = computed(() => {
  if (user.value?.auth_source === "microsoft") {
    return "Parte de tus datos puede sincronizarse automáticamente desde Microsoft 365.";
  }

  return "El acceso se administra directamente desde el sistema.";
});

const safeReadStoredUser = () => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

const syncUserState = (data) => {
  user.value = data || null;
  if (!data) return;

  localStorage.setItem("user", JSON.stringify(data));

  if (typeof userStore.setUserData === "function") {
    userStore.setUserData(data);
  }

  if (typeof userStore.setAvatar === "function") {
    userStore.setAvatar(data.avatar_url || null);
  }
};

const resetEditForm = () => {
  form.value.identificacion = user.value?.identificacion || "";
  form.value.facultad_id = user.value?.facultad_id || "";
  form.value.carrera_id = user.value?.carrera_id || "";
};

const showToast = (type, message, ms = 2800) => {
  if (toast.value.t) clearTimeout(toast.value.t);

  toast.value.type = type;
  toast.value.message = message;
  toast.value.show = true;
  toast.value.t = setTimeout(() => {
    toast.value.show = false;
    toast.value.t = null;
  }, ms);
};

const hideToast = () => {
  if (toast.value.t) clearTimeout(toast.value.t);
  toast.value.show = false;
  toast.value.t = null;
};

const copyText = async (txt) => {
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error("Clipboard no soportado");
    }

    await navigator.clipboard.writeText(String(txt ?? ""));
    showToast("success", "Copiado al portapapeles.");
  } catch (error) {
    console.error(error);
    showToast("error", "No se pudo copiar.");
  }
};

const formatFecha = (fecha) => {
  if (!fecha) return "N/A";
  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "N/A";

  return d.toLocaleDateString("es-EC", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
};

const formatFechaTime = (fecha) => {
  if (!fecha) return "N/A";
  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "N/A";

  return d.toLocaleString("es-EC", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const cerrarSesion = () => {
  if (typeof userStore.clearUser === "function") {
    userStore.clearUser();
  }

  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  router.replace("/login");
};

const irAPanelAdmin = () => {
  router.push({ name: "AdminPanel" });
};

const openAvatarFlow = () => {
  showAvatarModal.value = true;
};

const handleAvatarUpdated = (nextUser) => {
  syncUserState(nextUser);
};

const closeAvatarModal = () => {
  showAvatarModal.value = false;
};

const closeEditModal = () => {
  if (savingProfile.value) return;
  showEditModal.value = false;
  editError.value = "";
};

const handleEditAction = async () => {
  if (!canEditProfile.value) {
    showToast("info", editDisabledReason.value, 3800);
    return;
  }

  await openEditProfileModal();
};

const onKeyDown = (e) => {
  if (e.key !== "Escape") return;

  if (showEditModal.value) closeEditModal();
  if (showAvatarModal.value) closeAvatarModal();
};

watch([showAvatarModal, showEditModal], ([avatarOpen, editOpen]) => {
  document.body.style.overflow = avatarOpen || editOpen ? "hidden" : "";
});

const loadFacultades = async () => {
  const resp = await api.get("selects/facultades/");
  facultades.value = asArray(resp.data);
};

const loadCarreras = async (facultadId) => {
  if (!facultadId) {
    carreras.value = [];
    return;
  }

  loadingCarreras.value = true;

  try {
    const resp = await api.get(`selects/carreras/${facultadId}/`);
    carreras.value = asArray(resp.data);
  } finally {
    loadingCarreras.value = false;
  }
};

const onFacultadChange = async () => {
  form.value.carrera_id = "";
  await loadCarreras(form.value.facultad_id);
};

const openEditProfileModal = async () => {
  editError.value = "";
  resetEditForm();
  showEditModal.value = true;

  if (!canEditProfile.value || isExternalAuthor.value) return;

  try {
    await loadFacultades();

    if (form.value.facultad_id) {
      await loadCarreras(form.value.facultad_id);

      const existe = carreras.value.some(
        (c) => String(c.id) === String(form.value.carrera_id)
      );

      if (!existe) form.value.carrera_id = "";
    } else {
      carreras.value = [];
      form.value.carrera_id = "";
    }
  } catch (error) {
    console.error(error);
    editError.value = "No se pudieron cargar facultades y carreras.";
  }
};

const resolveProfileError = (data, fallback) => {
  if (!data) return fallback;

  if (typeof data.detail === "string" && data.detail) return data.detail;
  if (typeof data.error === "string" && data.error) return data.error;

  const keys = [
    "identificacion",
    "facultad_set",
    "carrera_set",
    "non_field_errors",
  ];

  for (const key of keys) {
    const value = data[key];
    if (Array.isArray(value) && value[0]) return String(value[0]);
    if (typeof value === "string" && value) return value;
  }

  return fallback;
};

const normalizeNullableId = (value) => {
  if (value === "" || value === null || value === undefined) return null;

  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
};

const saveProfile = async () => {
  if (savingProfile.value) return;

  if (!canEditProfile.value) {
    editError.value = editDisabledReason.value;
    showToast("error", editError.value);
    return;
  }

  const ident = String(form.value.identificacion || "").trim();

  if (ident && !/^\d{10}$/.test(ident)) {
    editError.value = "La identificación debe tener 10 dígitos numéricos.";
    return;
  }

  const facultadId = normalizeNullableId(form.value.facultad_id);
  const carreraId = normalizeNullableId(form.value.carrera_id);

  if (!isExternalAuthor.value && Boolean(facultadId) !== Boolean(carreraId)) {
    editError.value = "Seleccione facultad y carrera juntas, o deje ambas vacías.";
    return;
  }

  savingProfile.value = true;
  editError.value = "";

  try {
    const payload = isExternalAuthor.value
      ? {
          identificacion: ident || null,
          facultad_set: null,
          carrera_set: null,
        }
      : {
          identificacion: ident || null,
          facultad_set: facultadId,
          carrera_set: carreraId,
        };

    const resp = await api.patch("auth/profile/", payload);
    syncUserState(resp.data);

    showToast("success", "Perfil actualizado.");
    showEditModal.value = false;
  } catch (err) {
    console.error(err);

    const code = err?.response?.status;
    const data = err?.response?.data || {};

    if (code === 403) {
      editError.value = resolveProfileError(data, "Edición bloqueada.");
    } else if (code === 400 || code === 409) {
      editError.value = resolveProfileError(
        data,
        "Datos inválidos. Revisa identificación, facultad y carrera."
      );
    } else {
      editError.value = "No se pudo actualizar el perfil.";
    }

    showToast("error", editError.value);
    await reloadProfile();
  } finally {
    savingProfile.value = false;
  }
};

const dismissIncompleteBanner = async () => {
  try {
    await api.patch("auth/profile/", { snooze_hours: 5 });
    await reloadProfile();
    showToast("info", "Te lo recordaremos más tarde.");
  } catch (error) {
    console.error(error);
    showToast("error", "No se pudo posponer el recordatorio.");
  }
};

const reloadProfile = async () => {
  loading.value = true;

  try {
    const resp = await api.get("auth/profile/");
    syncUserState(resp.data);
  } catch (error) {
    console.error(error);

    const cached = safeReadStoredUser();
    if (cached) {
      syncUserState(cached);
    } else {
      user.value = null;
    }
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  window.addEventListener("keydown", onKeyDown);

  clockId = window.setInterval(() => {
    now.value = Date.now();
  }, 60000);

  const token = localStorage.getItem("access_token");
  if (!token) {
    loading.value = false;
    router.replace("/login");
    return;
  }

  const cached = safeReadStoredUser();
  if (cached) {
    syncUserState(cached);
  }

  await reloadProfile();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeyDown);
  document.body.style.overflow = "";

  if (clockId) {
    clearInterval(clockId);
    clockId = null;
  }

  if (toast.value.t) clearTimeout(toast.value.t);
});
</script>

<style src="./perfil-usuario.css"></style>