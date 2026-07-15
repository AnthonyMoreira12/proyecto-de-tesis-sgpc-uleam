<template>
  <Teleport to="body">
    <Transition name="pav-fade">
      <div
        v-if="modelValue"
        class="pav-overlay"
        @click.self="closeModal"
      >
        <article
          ref="modalRef"
          class="pav-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="pav-title"
          aria-describedby="pav-description"
          tabindex="-1"
        >
          <header class="pav-head">
            <div class="pav-head__identity">
              <span class="pav-head__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path
                    d="M4 7a3 3 0 0 1 3-3h2l1.2-1.5h3.6L15 4h2a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linejoin="round"
                  />

                  <circle
                    cx="12"
                    cy="12"
                    r="3.7"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />
                </svg>
              </span>

              <div class="pav-head__copy">
                <span class="pav-kicker">
                  Foto de perfil
                </span>

                <h2 id="pav-title" class="pav-title">
                  Actualizar fotografía
                </h2>

                <p id="pav-description" class="pav-subtitle">
                  Seleccione una imagen que permita identificar su cuenta dentro
                  de SGPC ULEAM.
                </p>
              </div>
            </div>

            <button
              class="pav-icon-btn"
              type="button"
              :disabled="uploading"
              aria-label="Cerrar ventana"
              title="Cerrar"
              @click="closeModal"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18 6 6 18" />
                <path d="M6 6 18 18" />
              </svg>
            </button>
          </header>

          <div class="pav-body">
            <section
              class="pav-preview-panel"
              aria-labelledby="pav-preview-title"
            >
              <header class="pav-section-head">
                <div>
                  <span class="pav-section-label">
                    Resultado
                  </span>

                  <h3 id="pav-preview-title" class="pav-section-title">
                    {{ isPreviewMode ? "Vista previa" : "Foto actual" }}
                  </h3>
                </div>

                <span
                  class="pav-state-pill"
                  :class="{
                    'is-new': isPreviewMode,
                    'is-current': !isPreviewMode,
                  }"
                >
                  {{
                    isPreviewMode
                      ? "Nueva imagen"
                      : hasAvatar
                        ? "Actual"
                        : "Iniciales"
                  }}
                </span>
              </header>

              <div class="pav-preview-area">
                <div class="pav-preview-ring">
                  <img
                    v-if="modalImage"
                    :src="modalImage"
                    class="pav-preview-img"
                    alt=""
                    draggable="false"
                  />

                  <div
                    v-else
                    class="pav-preview-placeholder"
                    aria-hidden="true"
                  >
                    {{ initials }}
                  </div>
                </div>

                <div class="pav-preview-mini">
                  <div class="pav-preview-mini__avatar">
                    <img
                      v-if="modalImage"
                      :src="modalImage"
                      alt=""
                      draggable="false"
                    />

                    <span v-else>
                      {{ initials }}
                    </span>
                  </div>

                  <div class="pav-preview-mini__lines">
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>

              <dl
                v-if="isPreviewMode"
                class="pav-filemeta"
              >
                <div>
                  <dt>Archivo</dt>
                  <dd>{{ tempFile?.name || "—" }}</dd>
                </div>

                <div>
                  <dt>Tamaño</dt>
                  <dd>{{ tempFileSizeLabel }}</dd>
                </div>

                <div>
                  <dt>Formato</dt>
                  <dd>{{ selectedFileFormat }}</dd>
                </div>
              </dl>

              <p v-else class="pav-preview-note">
                {{
                  hasAvatar
                    ? "La fotografía actual será reemplazada únicamente después de guardar."
                    : "Mientras no cargue una fotografía, el sistema mostrará sus iniciales."
                }}
              </p>
            </section>

            <section
              class="pav-upload-panel"
              aria-labelledby="pav-upload-title"
            >
              <header class="pav-section-head">
                <div>
                  <span class="pav-section-label">
                    Selección
                  </span>

                  <h3 id="pav-upload-title" class="pav-section-title">
                    {{
                      isPreviewMode
                        ? "Imagen seleccionada"
                        : "Seleccione una imagen"
                    }}
                  </h3>

                  <p class="pav-section-text">
                    {{ uploadDescription }}
                  </p>
                </div>
              </header>

              <input
                ref="fileInput"
                class="pav-sr-only"
                type="file"
                accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
                @change="handleImageSelected"
              />

              <button
                ref="selectActionRef"
                class="pav-dropzone"
                :class="{
                  'is-dragging': isDragging,
                  'has-file': isPreviewMode,
                }"
                type="button"
                :disabled="uploading"
                :aria-label="
                  isPreviewMode
                    ? 'Seleccionar otra imagen'
                    : 'Seleccionar imagen de perfil'
                "
                @dragenter.prevent="onDragEnter"
                @dragover.prevent="onDragOver"
                @dragleave.prevent="onDragLeave"
                @drop.prevent="onDrop"
                @click="openFilePicker"
              >
                <span class="pav-dropzone-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 16V4" />
                    <path d="m7 9 5-5 5 5" />
                    <path
                      d="M20 16.5V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-1.5"
                    />
                  </svg>
                </span>

                <strong class="pav-dropzone-title">
                  {{
                    isPreviewMode
                      ? "Cambiar imagen"
                      : "Elegir imagen"
                  }}
                </strong>

                <span class="pav-dropzone-text">
                  Haga clic o arrastre el archivo hasta esta zona.
                </span>

                <span class="pav-dropzone-action">
                  Examinar archivos
                </span>
              </button>

              <div
                class="pav-requirements"
                aria-label="Requisitos de la fotografía"
              >
                <div class="pav-requirement">
                  <span class="pav-requirement__icon" aria-hidden="true">
                    <svg viewBox="0 0 20 20">
                      <path
                        d="m5 10 3 3 7-7"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <span>JPG, PNG o WEBP</span>
                </div>

                <div class="pav-requirement">
                  <span class="pav-requirement__icon" aria-hidden="true">
                    <svg viewBox="0 0 20 20">
                      <path
                        d="m5 10 3 3 7-7"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <span>Máximo {{ avatarMaxSizeLabel }}</span>
                </div>

                <div class="pav-requirement">
                  <span class="pav-requirement__icon" aria-hidden="true">
                    <svg viewBox="0 0 20 20">
                      <path
                        d="m5 10 3 3 7-7"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <span>Imagen cuadrada recomendada</span>
                </div>

                <div class="pav-requirement">
                  <span class="pav-requirement__icon" aria-hidden="true">
                    <svg viewBox="0 0 20 20">
                      <path
                        d="m5 10 3 3 7-7"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <span>Rostro centrado y visible</span>
                </div>
              </div>

              <p
                v-if="localError"
                class="pav-error"
                role="alert"
                aria-live="polite"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />

                  <path
                    d="M10 5.8v5M10 14.3h.01"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />
                </svg>

                <span>{{ localError }}</span>
              </p>
            </section>
          </div>

          <footer class="pav-actions">
            <button
              class="pav-btn pav-btn--secondary"
              type="button"
              :disabled="uploading"
              @click="closeModal"
            >
              Cancelar
            </button>

            <button
              v-if="isPreviewMode"
              class="pav-btn pav-btn--ghost"
              type="button"
              :disabled="uploading"
              @click="clearSelectedImage"
            >
              Descartar selección
            </button>

            <button
              class="pav-btn pav-btn--primary"
              type="button"
              :disabled="!isPreviewMode || uploading"
              :title="
                !isPreviewMode
                  ? 'Seleccione una imagen antes de guardar.'
                  : 'Guardar nueva fotografía.'
              "
              @click="uploadAvatar"
            >
              <svg
                v-if="!uploading"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  d="m5 10 3 3 7-7"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>

              <span class="pav-spinner" v-else aria-hidden="true"></span>

              <span>
                {{ uploading ? "Guardando..." : "Guardar fotografía" }}
              </span>
            </button>
          </footer>
        </article>
      </div>
    </Transition>
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

import api from "../../../scripts/api/axios";
import "./perfil-avatar-modal.css";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },

  user: {
    type: Object,
    default: null,
  },

  initials: {
    type: String,
    default: "U",
  },

  hasAvatar: {
    type: Boolean,
    default: false,
  },

  maxFileSize: {
    type: Number,
    default: 1024 * 1024,
  },

  avatarMaxSizeLabel: {
    type: String,
    default: "1 MB",
  },
});

const emit = defineEmits([
  "update:modelValue",
  "updated",
  "toast",
]);

const modalRef = ref(null);
const fileInput = ref(null);
const selectActionRef = ref(null);

const previewImage = ref(null);
const tempFile = ref(null);
const uploading = ref(false);
const localError = ref("");

const isDragging = ref(false);
const dragCounter = ref(0);

let previouslyFocusedElement = null;

const BODY_LOCK_CLASS = "pav-scroll-lock";

const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
];

const ALLOWED_EXTENSIONS = [
  ".jpg",
  ".jpeg",
  ".png",
  ".webp",
];

const prettyBytes = (bytes) => {
  const size = Number(bytes || 0);

  if (size <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];

  let value = size;
  let index = 0;

  while (
    value >= 1024 &&
    index < units.length - 1
  ) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const isPreviewMode = computed(() => {
  return Boolean(tempFile.value);
});

const modalImage = computed(() => {
  if (previewImage.value) {
    return previewImage.value;
  }

  return (
    props.user?.avatar_url ||
    props.user?.avatar ||
    null
  );
});

const tempFileSizeLabel = computed(() => {
  if (!tempFile.value) {
    return "—";
  }

  return prettyBytes(tempFile.value.size);
});

const selectedFileFormat = computed(() => {
  if (!tempFile.value) {
    return "—";
  }

  const extension = getFileExtension(
    tempFile.value
  )
    .replace(".", "")
    .toUpperCase();

  return extension || "Imagen";
});

const uploadDescription = computed(() => {
  if (isPreviewMode.value) {
    return "Revise la vista previa y guarde la imagen cuando esté conforme.";
  }

  if (props.hasAvatar) {
    return "Puede reemplazar la fotografía actual seleccionando una imagen nueva.";
  }

  return "Agregue una fotografía para facilitar la identificación de su cuenta.";
});

const setDocumentScrollLock = (locked) => {
  if (typeof document === "undefined") {
    return;
  }

  document.documentElement.classList.toggle(
    BODY_LOCK_CLASS,
    Boolean(locked)
  );

  document.body.classList.toggle(
    BODY_LOCK_CLASS,
    Boolean(locked)
  );
};

const notify = (type, message) => {
  emit("toast", type, message);
};

const cleanupPreviewUrl = () => {
  if (previewImage.value) {
    URL.revokeObjectURL(previewImage.value);
  }

  previewImage.value = null;
};

const resetState = () => {
  cleanupPreviewUrl();

  tempFile.value = null;
  localError.value = "";
  isDragging.value = false;
  dragCounter.value = 0;

  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const closeModal = () => {
  if (uploading.value) {
    return;
  }

  emit("update:modelValue", false);
};

const openFilePicker = () => {
  if (uploading.value) {
    return;
  }

  localError.value = "";

  if (fileInput.value) {
    fileInput.value.value = "";
    fileInput.value.click();
  }
};

const getFileExtension = (file) => {
  const name = String(file?.name || "")
    .trim()
    .toLowerCase();

  const index = name.lastIndexOf(".");

  return index >= 0
    ? name.slice(index)
    : "";
};

const setValidationError = (message) => {
  localError.value = message;
  notify("error", message);
};

const validateImage = (file) => {
  localError.value = "";

  if (!file) {
    return false;
  }

  const extension = getFileExtension(file);

  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    setValidationError(
      "Formato no permitido. Utilice una imagen JPG, PNG o WEBP."
    );

    return false;
  }

  if (
    file.type &&
    !ALLOWED_TYPES.includes(file.type)
  ) {
    setValidationError(
      "El tipo del archivo seleccionado no corresponde a una imagen permitida."
    );

    return false;
  }

  if (
    Number(file.size || 0) >
    props.maxFileSize
  ) {
    setValidationError(
      `La imagen supera el tamaño máximo permitido de ${props.avatarMaxSizeLabel}.`
    );

    return false;
  }

  return true;
};

const setPreviewFromFile = (file) => {
  cleanupPreviewUrl();

  tempFile.value = file;
  previewImage.value = URL.createObjectURL(file);
  localError.value = "";
};

const handleImageSelected = (event) => {
  const file = event.target.files?.[0];

  if (!file) {
    return;
  }

  if (!validateImage(file)) {
    event.target.value = "";
    return;
  }

  setPreviewFromFile(file);
  event.target.value = "";
};

const clearSelectedImage = async () => {
  resetState();

  await nextTick();

  selectActionRef.value?.focus?.({
    preventScroll: true,
  });
};

const sendAvatarRequest = async (formData) => {
  const config = {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  };

  try {
    return await api.patch(
      "auth/avatar/",
      formData,
      config
    );
  } catch (error) {
    const status = error?.response?.status;

    if (
      status === 405 ||
      status === 415
    ) {
      return api.post(
        "auth/avatar/",
        formData,
        config
      );
    }

    throw error;
  }
};

const resolveUploadError = (data) => {
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

  if (
    Array.isArray(data.avatar) &&
    data.avatar[0]
  ) {
    return String(data.avatar[0]);
  }

  if (
    typeof data.avatar === "string" &&
    data.avatar
  ) {
    return data.avatar;
  }

  if (
    Array.isArray(data.file) &&
    data.file[0]
  ) {
    return String(data.file[0]);
  }

  if (
    typeof data.file === "string" &&
    data.file
  ) {
    return data.file;
  }

  return "";
};

const buildUpdatedUser = (responseData) => {
  const data = responseData || {};

  const nestedUser =
    data.user ||
    data.usuario ||
    null;

  const avatarUrl =
    data.avatar_url ||
    data.avatar ||
    nestedUser?.avatar_url ||
    props.user?.avatar_url ||
    null;

  if (
    nestedUser &&
    typeof nestedUser === "object"
  ) {
    return {
      ...(props.user || {}),
      ...nestedUser,
      avatar_url: avatarUrl,
    };
  }

  return {
    ...(props.user || {}),
    ...data,
    avatar_url: avatarUrl,
  };
};

const uploadAvatar = async () => {
  if (
    !tempFile.value ||
    uploading.value
  ) {
    return;
  }

  uploading.value = true;
  localError.value = "";

  try {
    const formData = new FormData();

    formData.append(
      "avatar",
      tempFile.value
    );

    const response =
      await sendAvatarRequest(formData);

    const nextUser =
      buildUpdatedUser(response.data);

    emit("updated", nextUser);

    notify(
      "success",
      "La fotografía se actualizó correctamente."
    );

    emit("update:modelValue", false);
  } catch (error) {
    console.error(
      "Error al subir avatar:",
      error?.response?.data || error
    );

    const message =
      resolveUploadError(
        error?.response?.data
      ) ||
      "No se pudo actualizar la fotografía.";

    localError.value = message;
    notify("error", message);
  } finally {
    uploading.value = false;
  }
};

const onDragEnter = () => {
  if (uploading.value) {
    return;
  }

  dragCounter.value += 1;
  isDragging.value = true;
};

const onDragOver = () => {
  if (uploading.value) {
    return;
  }

  isDragging.value = true;
};

const onDragLeave = () => {
  if (uploading.value) {
    return;
  }

  dragCounter.value -= 1;

  if (dragCounter.value <= 0) {
    dragCounter.value = 0;
    isDragging.value = false;
  }
};

const onDrop = (event) => {
  if (uploading.value) {
    return;
  }

  dragCounter.value = 0;
  isDragging.value = false;

  const file =
    event.dataTransfer?.files?.[0];

  if (!file) {
    return;
  }

  if (!validateImage(file)) {
    return;
  }

  setPreviewFromFile(file);
};

const getFocusableElements = () => {
  if (!modalRef.value) {
    return [];
  }

  return Array.from(
    modalRef.value.querySelectorAll(
      [
        "button:not([disabled])",
        "input:not([disabled])",
        "select:not([disabled])",
        "textarea:not([disabled])",
        "[href]",
        '[tabindex]:not([tabindex="-1"])',
      ].join(",")
    )
  );
};

const trapFocus = (event) => {
  const elements = getFocusableElements();

  if (!elements.length) {
    event.preventDefault();
    modalRef.value?.focus?.();
    return;
  }

  const first = elements[0];
  const last = elements[elements.length - 1];

  if (
    event.shiftKey &&
    document.activeElement === first
  ) {
    event.preventDefault();
    last.focus();
    return;
  }

  if (
    !event.shiftKey &&
    document.activeElement === last
  ) {
    event.preventDefault();
    first.focus();
  }
};

const onKeydown = (event) => {
  if (!props.modelValue) {
    return;
  }

  if (event.key === "Escape") {
    closeModal();
    return;
  }

  if (event.key === "Tab") {
    trapFocus(event);
  }
};

watch(
  () => props.modelValue,
  async (isOpen) => {
    setDocumentScrollLock(isOpen);

    if (isOpen) {
      previouslyFocusedElement =
        document.activeElement;

      resetState();

      await nextTick();

      selectActionRef.value?.focus?.({
        preventScroll: true,
      });

      return;
    }

    resetState();

    await nextTick();

    previouslyFocusedElement?.focus?.({
      preventScroll: true,
    });

    previouslyFocusedElement = null;
  },
  {
    immediate: true,
  }
);

onMounted(() => {
  window.addEventListener(
    "keydown",
    onKeydown
  );
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    onKeydown
  );

  setDocumentScrollLock(false);
  resetState();
});
</script>