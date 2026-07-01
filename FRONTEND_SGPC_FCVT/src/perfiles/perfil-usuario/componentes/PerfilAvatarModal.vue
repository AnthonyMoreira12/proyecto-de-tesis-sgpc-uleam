<template>
  <Transition name="pav-fade">
    <div
      v-if="modelValue"
      class="pav-overlay"
      @mousedown.self="closeModal"
    >
      <article
        class="pav-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pav-title"
        aria-describedby="pav-description"
      >
        <header class="pav-head">
          <div class="pav-head__copy">
            <span class="pav-kicker">Foto de perfil</span>

            <h3 id="pav-title" class="pav-title">
              Actualizar foto
            </h3>

            <p id="pav-description" class="pav-subtitle">
              Selecciona una imagen clara para identificar tu cuenta dentro del sistema.
            </p>
          </div>

          <button
            ref="closeButtonRef"
            class="pav-icon-btn pav-close"
            type="button"
            :disabled="uploading"
            aria-label="Cerrar"
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
          <section class="pav-preview-card" aria-label="Vista previa de la foto">
            <div class="pav-preview-head">
              <div>
                <h4 class="pav-section-title">
                  {{ isPreviewMode ? "Vista previa" : "Foto actual" }}
                </h4>

                <p class="pav-section-text">
                  Se mostrará en formato circular dentro de tu perfil.
                </p>
              </div>

              <span
                class="pav-state-pill"
                :class="isPreviewMode ? 'pav-state-pill--new' : 'pav-state-pill--current'"
              >
                {{ isPreviewMode ? "Nueva imagen" : hasAvatar ? "Actual" : "Iniciales" }}
              </span>
            </div>

            <div class="pav-preview-area">
              <div class="pav-preview-frame" aria-hidden="true">
                <img
                  v-if="modalImage"
                  :src="modalImage"
                  alt=""
                  class="pav-preview-img"
                  draggable="false"
                />

                <div v-else class="pav-preview-placeholder">
                  {{ initials }}
                </div>
              </div>
            </div>

            <div v-if="isPreviewMode" class="pav-filemeta">
              <div class="pav-filemeta-row">
                <span>Archivo</span>
                <strong>{{ tempFile?.name || "—" }}</strong>
              </div>

              <div class="pav-filemeta-row">
                <span>Tamaño</span>
                <strong>{{ tempFileSizeLabel }}</strong>
              </div>
            </div>
          </section>

          <section class="pav-upload-card" aria-label="Seleccionar imagen">
            <div class="pav-upload-copy">
              <h4 class="pav-section-title">
                {{ isPreviewMode ? "Imagen seleccionada" : "Seleccionar imagen" }}
              </h4>

              <p class="pav-section-text">
                {{ uploadDescription }}
              </p>
            </div>

            <input
              ref="fileInput"
              type="file"
              accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
              class="pav-sr-only"
              @change="handleImageSelected"
            />

            <button
              ref="selectActionRef"
              class="pav-dropzone"
              :class="{ 'is-dragging': isDragging }"
              type="button"
              :disabled="uploading"
              :aria-label="isPreviewMode ? 'Cambiar imagen seleccionada' : 'Seleccionar imagen de perfil'"
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
                  <path d="M20 16.5V18a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-1.5" />
                </svg>
              </span>

              <span class="pav-dropzone-main">
                {{ isPreviewMode ? "Cambiar imagen" : "Elegir imagen" }}
              </span>

              <span class="pav-dropzone-meta">
                Haz clic o arrastra una imagen aquí.
              </span>
            </button>

            <div class="pav-rules" aria-label="Requisitos de imagen">
              <div class="pav-rule">
                <span class="pav-rule__dot"></span>
                JPG, PNG o WEBP
              </div>

              <div class="pav-rule">
                <span class="pav-rule__dot"></span>
                Máximo {{ avatarMaxSizeLabel }}
              </div>

              <div class="pav-rule">
                <span class="pav-rule__dot"></span>
                Rostro centrado recomendado
              </div>
            </div>

            <p v-if="localError" class="pav-error" role="alert" aria-live="polite">
              {{ localError }}
            </p>
          </section>
        </div>

        <footer class="pav-actions">
          <button
            class="pav-btn pav-btn--primary"
            type="button"
            :disabled="!isPreviewMode || uploading"
            :title="!isPreviewMode ? 'Selecciona una imagen antes de guardar.' : 'Guardar nueva foto de perfil.'"
            @click="uploadAvatar"
          >
            {{ uploading ? "Guardando..." : "Guardar foto" }}
          </button>

          <button
            v-if="isPreviewMode"
            class="pav-btn"
            type="button"
            :disabled="uploading"
            @click="openFilePicker"
          >
            Cambiar
          </button>

          <button
            v-if="isPreviewMode"
            class="pav-btn pav-btn--ghost"
            type="button"
            :disabled="uploading"
            @click="clearSelectedImage"
          >
            Descartar
          </button>

          <button
            class="pav-btn pav-btn--danger"
            type="button"
            :disabled="uploading"
            @click="closeModal"
          >
            Cancelar
          </button>
        </footer>
      </article>
    </div>
  </Transition>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
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

const emit = defineEmits(["update:modelValue", "updated", "toast"]);

const fileInput = ref(null);
const closeButtonRef = ref(null);
const selectActionRef = ref(null);

const previewImage = ref(null);
const tempFile = ref(null);
const uploading = ref(false);
const localError = ref("");

const isDragging = ref(false);
const dragCounter = ref(0);

const BODY_LOCK_CLASS = "pav-scroll-lock";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"];

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

const isPreviewMode = computed(() => !!tempFile.value);

const modalImage = computed(() => {
  if (previewImage.value) return previewImage.value;
  return props.user?.avatar_url || null;
});

const tempFileSizeLabel = computed(() => {
  if (!tempFile.value) return "—";
  return prettyBytes(tempFile.value.size);
});

const uploadDescription = computed(() => {
  if (isPreviewMode.value) {
    return "Revisa la vista previa antes de guardar la nueva foto.";
  }

  if (props.hasAvatar) {
    return "Puedes reemplazar la imagen actual por una nueva fotografía.";
  }

  return "Agrega una imagen para identificar mejor tu cuenta.";
});

const setDocumentScrollLock = (locked) => {
  if (typeof document === "undefined") return;

  document.body.classList.toggle(BODY_LOCK_CLASS, Boolean(locked));
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
  if (uploading.value) return;

  emit("update:modelValue", false);
  resetState();
};

const openFilePicker = () => {
  if (uploading.value) return;

  localError.value = "";

  if (fileInput.value) {
    fileInput.value.value = "";
    fileInput.value.click();
  }
};

const getFileExtension = (file) => {
  const name = String(file?.name || "").toLowerCase();
  const dot = name.lastIndexOf(".");
  return dot >= 0 ? name.slice(dot) : "";
};

const setValidationError = (message) => {
  localError.value = message;
  notify("error", message);
};

const validateImage = (file) => {
  localError.value = "";

  if (!file) return false;

  const ext = getFileExtension(file);

  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    setValidationError("Formato no permitido. Use JPG, PNG o WEBP.");
    return false;
  }

  if (file.type && !ALLOWED_TYPES.includes(file.type)) {
    setValidationError("Formato no permitido. Use JPG, PNG o WEBP.");
    return false;
  }

  if (Number(file.size || 0) > props.maxFileSize) {
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

  if (!file) return;

  if (!validateImage(file)) {
    event.target.value = "";
    return;
  }

  setPreviewFromFile(file);
  event.target.value = "";
};

const clearSelectedImage = () => {
  resetState();

  nextTick(() => {
    selectActionRef.value?.focus?.({ preventScroll: true });
  });
};

const sendAvatarRequest = async (formData) => {
  const config = {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  };

  try {
    return await api.patch("auth/avatar/", formData, config);
  } catch (error) {
    const status = error?.response?.status;

    if (status === 405 || status === 415) {
      return await api.post("auth/avatar/", formData, config);
    }

    throw error;
  }
};

const resolveUploadError = (data) => {
  if (!data) return "";

  if (typeof data.detail === "string" && data.detail) return data.detail;
  if (typeof data.error === "string" && data.error) return data.error;

  if (Array.isArray(data.avatar) && data.avatar[0]) return String(data.avatar[0]);
  if (typeof data.avatar === "string" && data.avatar) return data.avatar;

  if (Array.isArray(data.file) && data.file[0]) return String(data.file[0]);
  if (typeof data.file === "string" && data.file) return data.file;

  return "";
};

const buildUpdatedUser = (responseData) => {
  const data = responseData || {};
  const nestedUser = data.user || data.usuario || null;

  const avatarUrl =
    data.avatar_url ||
    data.avatar ||
    nestedUser?.avatar_url ||
    props.user?.avatar_url ||
    null;

  if (nestedUser && typeof nestedUser === "object") {
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
  if (!tempFile.value || uploading.value) return;

  uploading.value = true;
  localError.value = "";

  try {
    const formData = new FormData();
    formData.append("avatar", tempFile.value);

    const resp = await sendAvatarRequest(formData);
    const nextUser = buildUpdatedUser(resp.data);

    emit("updated", nextUser);
    notify("success", "Foto actualizada correctamente.");
    emit("update:modelValue", false);

    resetState();
  } catch (error) {
    console.error("Error al subir avatar:", error?.response?.data || error);

    const message =
      resolveUploadError(error?.response?.data) ||
      "No se pudo actualizar la foto.";

    localError.value = message;
    notify("error", message);
  } finally {
    uploading.value = false;
  }
};

const onDragEnter = () => {
  if (uploading.value) return;

  dragCounter.value += 1;
  isDragging.value = true;
};

const onDragOver = () => {
  if (uploading.value) return;

  isDragging.value = true;
};

const onDragLeave = () => {
  if (uploading.value) return;

  dragCounter.value -= 1;

  if (dragCounter.value <= 0) {
    dragCounter.value = 0;
    isDragging.value = false;
  }
};

const onDrop = (event) => {
  if (uploading.value) return;

  dragCounter.value = 0;
  isDragging.value = false;

  const file = event.dataTransfer?.files?.[0];

  if (!file) return;
  if (!validateImage(file)) return;

  setPreviewFromFile(file);
};

const onKeydown = (event) => {
  if (event.key === "Escape" && props.modelValue) {
    closeModal();
  }
};

watch(
  () => props.modelValue,
  async (isOpen) => {
    setDocumentScrollLock(isOpen);

    if (isOpen) {
      resetState();

      await nextTick();

      selectActionRef.value?.focus?.({ preventScroll: true });
      return;
    }

    resetState();
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
  setDocumentScrollLock(false);
  resetState();
});
</script>