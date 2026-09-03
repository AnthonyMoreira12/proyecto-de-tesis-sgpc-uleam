<template>
  <Teleport to="body">
    <Transition name="pav-fade">
      <div
        v-if="modelValue"
        class="pav-overlay"
        @mousedown.self="closeModal"
      >
        <article
          ref="modalRef"
          class="pav-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="pav-title"
          aria-describedby="pav-description"
          :aria-busy="busy"
          tabindex="-1"
          @keydown="handleModalKeydown"
        >
          <!-- =================================================
               ENCABEZADO
          ================================================== -->
          <header class="pav-head">
            <div class="pav-head__copy">
              <span class="pav-kicker">
                Imagen de cuenta
              </span>

              <h3
                id="pav-title"
                class="pav-title"
              >
                Fotografía de perfil
              </h3>

              <p
                id="pav-description"
                class="pav-subtitle"
              >
                Seleccione una imagen JPG, PNG o WEBP.
              </p>
            </div>

            <button
              ref="closeButtonRef"
              class="pav-icon-btn pav-close"
              type="button"
              :disabled="busy"
              aria-label="Cerrar ventana"
              title="Cerrar"
              @click="closeModal"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M18 6 6 18" />
                <path d="M6 6 18 18" />
              </svg>
            </button>
          </header>

          <!-- =================================================
               CONTENIDO
          ================================================== -->
          <div class="pav-body">
            <!-- ===============================================
                 VISTA PREVIA
            ================================================ -->
            <section
              class="pav-preview-card"
              aria-labelledby="pav-preview-title"
            >
              <div class="pav-preview-head">
                <div>
                  <h4
                    id="pav-preview-title"
                    class="pav-section-title"
                  >
                    {{
                      isPreviewMode
                        ? "Vista previa"
                        : hasCurrentAvatar
                          ? "Fotografía actual"
                          : "Vista del perfil"
                    }}
                  </h4>

                  <p class="pav-section-text">
                    La imagen se mostrará con el mismo recorte
                    utilizado en la tarjeta de su perfil.
                  </p>
                </div>

                <span
                  class="pav-state-pill"
                  :class="
                    isPreviewMode
                      ? 'pav-state-pill--new'
                      : 'pav-state-pill--current'
                  "
                >
                  {{
                    isPreviewMode
                      ? "Nueva imagen"
                      : hasCurrentAvatar
                        ? "Actual"
                        : "Iniciales"
                  }}
                </span>
              </div>

              <div class="pav-preview-area">
                <div class="pav-preview-frame">
                  <img
                    v-if="modalImage"
                    :src="modalImage"
                    class="pav-preview-img"
                    alt="Vista previa de la fotografía de perfil"
                    draggable="false"
                    @error="handlePreviewError"
                  />

                  <div
                    v-else
                    class="pav-preview-placeholder"
                    aria-label="Iniciales del usuario"
                  >
                    {{ displayInitials }}
                  </div>
                </div>
              </div>

              <div
                v-if="isPreviewMode"
                class="pav-filemeta"
              >
                <div class="pav-filemeta-row">
                  <span>Archivo</span>

                  <strong>
                    {{ tempFile?.name || "—" }}
                  </strong>
                </div>

                <div class="pav-filemeta-row">
                  <span>Tamaño</span>

                  <strong>
                    {{ selectedFileSizeLabel }}
                  </strong>
                </div>

                <div class="pav-filemeta-row">
                  <span>Dimensiones</span>

                  <strong>
                    {{
                      selectedDimensions
                        ? `${selectedDimensions.width} × ${selectedDimensions.height} px`
                        : "—"
                    }}
                  </strong>
                </div>
              </div>
            </section>

            <!-- ===============================================
                 SELECCIÓN DEL ARCHIVO
            ================================================ -->
            <section
              class="pav-upload-card"
              aria-labelledby="pav-upload-title"
            >
              <div class="pav-upload-copy">
                <h4
                  id="pav-upload-title"
                  class="pav-section-title"
                >
                  {{
                    isPreviewMode
                      ? "Imagen seleccionada"
                      : "Seleccionar imagen"
                  }}
                </h4>

                <p class="pav-section-text">
                  {{ uploadDescription }}
                </p>
              </div>

              <div
                class="pav-dropzone"
                :class="{
                  'is-dragging': isDragging,
                  'is-disabled': busy,
                  'has-file': isPreviewMode,
                }"
                role="button"
                :tabindex="busy ? -1 : 0"
                :aria-disabled="busy"
                aria-describedby="pav-file-rules"
                @click="openFilePicker"
                @keydown.enter.prevent="openFilePicker"
                @keydown.space.prevent="openFilePicker"
                @dragenter.prevent="handleDragEnter"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
              >
                <span
                  class="pav-dropzone__icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M4 7a2 2 0 0 1 2-2h3l1.2-1.5h3.6L15 5h3a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linejoin="round"
                    />

                    <circle
                      cx="12"
                      cy="12"
                      r="3.2"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                    />
                  </svg>
                </span>

                <div class="pav-dropzone__copy">
                  <strong>
                    {{
                      isDragging
                        ? "Suelte la imagen aquí"
                        : isPreviewMode
                          ? "Seleccione otra imagen"
                          : "Arrastre una imagen o selecciónela"
                    }}
                  </strong>

                  <span>
                    Pulse aquí para abrir el explorador de
                    archivos.
                  </span>
                </div>
              </div>

              <input
                ref="fileInputRef"
                class="pav-file-input"
                type="file"
                accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                :disabled="busy"
                @change="handleFileInputChange"
              />

              <div
                id="pav-file-rules"
                class="pav-rules"
              >
                <span>
                  Formatos: JPG, PNG o WEBP
                </span>

                <span>
                  Peso máximo:
                  {{ avatarMaxSizeLabel }}
                </span>

                <span>
                  No se permiten imágenes animadas
                </span>
              </div>

              <div
                v-if="localError"
                class="pav-error"
                role="alert"
                aria-live="assertive"
              >
                <span aria-hidden="true">!</span>

                <p>{{ localError }}</p>
              </div>
            </section>
          </div>

          <!-- =================================================
               PIE DEL MODAL
          ================================================== -->
          <footer class="pav-footer">
            <button
              v-if="hasCurrentAvatar"
              class="pav-btn pav-btn--danger"
              type="button"
              :disabled="busy"
              @click="deleteAvatar"
            >
              <span
                v-if="deleting"
                class="pav-spinner"
                aria-hidden="true"
              ></span>

              <svg
                v-else
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  d="M4.5 6h11M8 6V4.5h4V6m-6 0 .7 10h6.6L14 6M8.5 9v4.5M11.5 9v4.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>

              <span>
                {{
                  deleting
                    ? "Eliminando..."
                    : "Eliminar fotografía"
                }}
              </span>
            </button>

            <button
              v-if="isPreviewMode"
              class="pav-btn pav-btn--ghost"
              type="button"
              :disabled="busy"
              @click="clearSelectedImage"
            >
              Descartar selección
            </button>

            <button
              v-else
              ref="selectActionRef"
              class="pav-btn"
              type="button"
              :disabled="busy"
              @click="openFilePicker"
            >
              Seleccionar imagen
            </button>

            <button
              class="pav-btn pav-btn--ghost"
              type="button"
              :disabled="busy"
              @click="closeModal"
            >
              Cancelar
            </button>

            <button
              class="pav-btn pav-btn--primary"
              type="button"
              :disabled="!isPreviewMode || busy"
              :title="
                !isPreviewMode
                  ? 'Seleccione una imagen antes de guardar.'
                  : 'Guardar la nueva fotografía de perfil.'
              "
              @click="uploadAvatar"
            >
              <span
                v-if="uploading"
                class="pav-spinner"
                aria-hidden="true"
              ></span>

              <svg
                v-else
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

              <span>
                {{
                  uploading
                    ? "Guardando..."
                    : "Guardar fotografía"
                }}
              </span>
            </button>
          </footer>
        </article>
      </div>
    </Transition>
  </Teleport>

  <NoticeDialog
    :modelValue="notice"
    @close="closeNotice"
  />
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";

import api from "../../../scripts/api/axios";
import { useNotice } from "../../../scripts/composables/useNotice";
import NoticeDialog from "../../../inicio/ui/NoticeDialog.vue";

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


/* ============================================================
   REFERENCIAS Y ESTADO
============================================================ */

const modalRef = ref(null);
const closeButtonRef = ref(null);
const selectActionRef = ref(null);
const fileInputRef = ref(null);

const previewImage = ref(null);
const tempFile = ref(null);
const selectedDimensions = ref(null);

const uploading = ref(false);
const deleting = ref(false);
const localError = ref("");

const isDragging = ref(false);
const dragCounter = ref(0);

let previouslyFocusedElement = null;

const {
  notice,
  openNotice,
  closeNotice,
} = useNotice();


const BODY_LOCK_CLASS =
  "pav-scroll-lock";

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

const MAX_IMAGE_WIDTH = 6000;
const MAX_IMAGE_HEIGHT = 6000;
const MAX_IMAGE_PIXELS = 20_000_000;


/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) => {
  return String(
    value ?? ""
  ).trim();
};


const normalizeNullableString = (value) => {
  const text = normalizeText(
    value
  );

  if (!text) {
    return null;
  }

  const lowered =
    text.toLowerCase();

  if (
    lowered === "null" ||
    lowered === "undefined" ||
    lowered === "none"
  ) {
    return null;
  }

  return text;
};


const getFileExtension = (fileName) => {
  const normalizedName =
    normalizeText(fileName)
      .toLowerCase();

  const dotIndex =
    normalizedName.lastIndexOf(".");

  if (dotIndex < 0) {
    return "";
  }

  return normalizedName.slice(
    dotIndex
  );
};


const prettyBytes = (bytes) => {
  const size = Number(
    bytes || 0
  );

  if (
    !Number.isFinite(size) ||
    size <= 0
  ) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let value = size;
  let unitIndex = 0;

  while (
    value >= 1024 &&
    unitIndex < units.length - 1
  ) {
    value /= 1024;
    unitIndex += 1;
  }

  const decimals =
    unitIndex === 0
      ? 0
      : 2;

  return (
    `${value.toFixed(decimals)} ` +
    units[unitIndex]
  );
};


/* ============================================================
   ESTADO DERIVADO
============================================================ */

const busy = computed(() => {
  return Boolean(
    uploading.value ||
    deleting.value
  );
});


const currentAvatarUrl = computed(() => {
  return normalizeNullableString(
    props.user?.avatar_url ??
    props.user?.avatarUrl ??
    props.user?.avatar
  );
});


const hasCurrentAvatar = computed(() => {
  return Boolean(
    currentAvatarUrl.value
  );
});


const displayInitials = computed(() => {
  const normalized =
    normalizeText(
      props.initials
    )
      .replace(/\s+/g, "")
      .slice(0, 2)
      .toUpperCase();

  return normalized || "U";
});


const isPreviewMode = computed(() => {
  return Boolean(
    tempFile.value &&
    previewImage.value
  );
});


const modalImage = computed(() => {
  return (
    previewImage.value ||
    currentAvatarUrl.value ||
    null
  );
});


const selectedFileSizeLabel = computed(() => {
  return prettyBytes(
    tempFile.value?.size
  );
});


const uploadDescription = computed(() => {
  if (isPreviewMode.value) {
    return (
      "Revise la vista previa y guarde la imagen " +
      "cuando esté conforme con el resultado."
    );
  }

  if (hasCurrentAvatar.value) {
    return (
      "Seleccione otra imagen para reemplazar la " +
      "fotografía que utiliza actualmente."
    );
  }

  return (
    "Seleccione una imagen para agregar una " +
    "fotografía a su perfil."
  );
});


/* ============================================================
   URL TEMPORAL
============================================================ */

const revokePreviewUrl = () => {
  if (!previewImage.value) {
    return;
  }

  try {
    URL.revokeObjectURL(
      previewImage.value
    );
  } catch {
    // La URL ya pudo haber sido liberada.
  }

  previewImage.value = null;
};


const clearSelectedImage = () => {
  if (busy.value) {
    return;
  }

  revokePreviewUrl();

  tempFile.value = null;
  selectedDimensions.value = null;
  localError.value = "";

  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
};


/* ============================================================
   VALIDACIÓN DEL ARCHIVO
============================================================ */

const loadImageDimensions = (
  objectUrl
) => {
  return new Promise(
    (resolve, reject) => {
      const image = new Image();

      image.onload = () => {
        resolve({
          width:
            Number(
              image.naturalWidth
            ) || 0,

          height:
            Number(
              image.naturalHeight
            ) || 0,
        });
      };

      image.onerror = () => {
        reject(
          new Error(
            "El archivo no contiene una imagen válida."
          )
        );
      };

      image.src = objectUrl;
    }
  );
};


const validateSelectedFile = async (
  file
) => {
  if (!(file instanceof File)) {
    throw new Error(
      "Seleccione un archivo de imagen válido."
    );
  }

  const fileName =
    normalizeText(
      file.name
    );

  if (!fileName) {
    throw new Error(
      "No fue posible determinar el nombre del archivo."
    );
  }

  const extension =
    getFileExtension(
      fileName
    );

  if (
    !ALLOWED_EXTENSIONS.includes(
      extension
    )
  ) {
    throw new Error(
      "Formato no permitido. Utilice JPG, PNG o WEBP."
    );
  }

  const fileType =
    normalizeText(
      file.type
    ).toLowerCase();

  if (
    fileType &&
    !ALLOWED_TYPES.includes(
      fileType
    )
  ) {
    throw new Error(
      "El tipo de contenido de la imagen no está permitido."
    );
  }

  const fileSize =
    Number(
      file.size
    );

  if (
    !Number.isFinite(fileSize) ||
    fileSize <= 0
  ) {
    throw new Error(
      "La imagen seleccionada está vacía."
    );
  }

  if (
    fileSize >
    Number(props.maxFileSize)
  ) {
    throw new Error(
      (
        "La imagen supera el tamaño máximo " +
        `permitido de ${props.avatarMaxSizeLabel}.`
      )
    );
  }

  const objectUrl =
    URL.createObjectURL(file);

  try {
    const dimensions =
      await loadImageDimensions(
        objectUrl
      );

    if (
      dimensions.width <= 0 ||
      dimensions.height <= 0
    ) {
      throw new Error(
        (
          "No fue posible determinar las " +
          "dimensiones de la imagen."
        )
      );
    }

    if (
      dimensions.width >
        MAX_IMAGE_WIDTH ||
      dimensions.height >
        MAX_IMAGE_HEIGHT
    ) {
      throw new Error(
        (
          "La imagen supera las dimensiones " +
          `máximas de ${MAX_IMAGE_WIDTH} × ` +
          `${MAX_IMAGE_HEIGHT} píxeles.`
        )
      );
    }

    if (
      dimensions.width *
        dimensions.height >
      MAX_IMAGE_PIXELS
    ) {
      throw new Error(
        (
          "La imagen contiene demasiados píxeles. " +
          "Seleccione una imagen de menor resolución."
        )
      );
    }

    return {
      objectUrl,
      dimensions,
    };
  } catch (error) {
    URL.revokeObjectURL(
      objectUrl
    );

    throw error;
  }
};


const selectFile = async (file) => {
  if (busy.value) {
    return;
  }

  localError.value = "";

  try {
    const result =
      await validateSelectedFile(
        file
      );

    revokePreviewUrl();

    tempFile.value = file;

    previewImage.value =
      result.objectUrl;

    selectedDimensions.value =
      result.dimensions;
  } catch (error) {
    localError.value =
      error?.message ||
      "No se pudo procesar la imagen seleccionada.";

    tempFile.value = null;
    selectedDimensions.value = null;
  }
};


/* ============================================================
   SELECTOR DE ARCHIVOS
============================================================ */

const openFilePicker = () => {
  if (busy.value) {
    return;
  }

  fileInputRef.value?.click();
};


const handleFileInputChange = async (
  event
) => {
  const file =
    event?.target?.files?.[0];

  if (file) {
    await selectFile(file);
  }

  /*
    Permite seleccionar nuevamente el mismo archivo después
    de descartarlo o después de una validación fallida.
  */
  if (event?.target) {
    event.target.value = "";
  }
};


/* ============================================================
   ARRASTRAR Y SOLTAR
============================================================ */

const handleDragEnter = () => {
  if (busy.value) {
    return;
  }

  dragCounter.value += 1;
  isDragging.value = true;
};


const handleDragOver = (event) => {
  if (busy.value) {
    return;
  }

  if (event?.dataTransfer) {
    event.dataTransfer.dropEffect =
      "copy";
  }

  isDragging.value = true;
};


const handleDragLeave = () => {
  if (busy.value) {
    return;
  }

  dragCounter.value = Math.max(
    0,
    dragCounter.value - 1
  );

  if (dragCounter.value === 0) {
    isDragging.value = false;
  }
};


const handleDrop = async (event) => {
  if (busy.value) {
    return;
  }

  dragCounter.value = 0;
  isDragging.value = false;

  const files =
    event?.dataTransfer?.files;

  if (!files?.length) {
    localError.value =
      "No se encontró una imagen para procesar.";

    return;
  }

  if (files.length > 1) {
    localError.value =
      "Seleccione una sola imagen.";

    return;
  }

  await selectFile(
    files[0]
  );
};


/* ============================================================
   ERRORES DEL BACKEND
============================================================ */

const resolveApiError = (
  data,
  visited = new Set()
) => {
  if (!data) {
    return "";
  }

  if (typeof data === "string") {
    return data;
  }

  if (
    typeof data !== "object" ||
    visited.has(data)
  ) {
    return "";
  }

  visited.add(data);

  const priorityKeys = [
    "detail",
    "avatar",
    "non_field_errors",
    "error",
  ];

  for (const key of priorityKeys) {
    const value = data?.[key];

    if (
      typeof value === "string" &&
      value
    ) {
      return value;
    }

    if (Array.isArray(value)) {
      for (const item of value) {
        const message =
          resolveApiError(
            item,
            visited
          );

        if (message) {
          return message;
        }
      }
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const message =
        resolveApiError(
          value,
          visited
        );

      if (message) {
        return message;
      }
    }
  }

  for (const value of Object.values(data)) {
    const message =
      resolveApiError(
        value,
        visited
      );

    if (message) {
      return message;
    }
  }

  return "";
};


/* ============================================================
   CACHÉ DEL AVATAR
============================================================ */

const withCacheBust = (url) => {
  const normalizedUrl =
    normalizeNullableString(
      url
    );

  if (!normalizedUrl) {
    return null;
  }

  try {
    const parsedUrl =
      new URL(
        normalizedUrl,
        window.location.origin
      );

    parsedUrl.searchParams.set(
      "avatar_v",
      String(Date.now())
    );

    return parsedUrl.toString();
  } catch {
    const separator =
      normalizedUrl.includes("?")
        ? "&"
        : "?";

    return (
      `${normalizedUrl}${separator}` +
      `avatar_v=${Date.now()}`
    );
  }
};


/* ============================================================
   ACTUALIZAR AVATAR
============================================================ */

const uploadAvatar = async () => {
  if (
    busy.value ||
    !tempFile.value
  ) {
    return;
  }

  uploading.value = true;
  localError.value = "";

  try {
    const formData =
      new FormData();

    formData.append(
      "avatar",
      tempFile.value,
      tempFile.value.name
    );

    /*
      No se establece manualmente Content-Type. El navegador y
      Axios deben agregar el boundary correcto de multipart.
    */
    const response =
      await api.patch(
        "auth/avatar/",
        formData
      );

    const avatarUrl =
      withCacheBust(
        response?.data?.avatar_url
      );

    const updatedUser = {
      ...(props.user || {}),
      avatar_url: avatarUrl,
    };

    emit(
      "updated",
      updatedUser
    );

    emit(
      "toast",
      "success",
      response?.data?.detail ||
        "La fotografía se actualizó correctamente.",
      4200
    );

    clearSelectedImage();

    emit(
      "update:modelValue",
      false
    );
  } catch (error) {
    const data =
      error?.response?.data;

    localError.value =
      resolveApiError(data) ||
      error?.message ||
      (
        "No se pudo actualizar la fotografía. " +
        "Revise la imagen e intente nuevamente."
      );

    emit(
      "toast",
      "error",
      localError.value,
      5200
    );
  } finally {
    uploading.value = false;
  }
};


/* ============================================================
   ELIMINAR AVATAR
============================================================ */

const performDeleteAvatar = async () => {
  deleting.value = true;
  localError.value = "";

  try {
    const response =
      await api.delete(
        "auth/avatar/"
      );

    const updatedUser = {
      ...(props.user || {}),
      avatar_url: null,
    };

    emit(
      "updated",
      updatedUser
    );

    emit(
      "toast",
      "success",
      response?.data?.detail ||
        "La fotografía se eliminó correctamente.",
      4200
    );

    clearSelectedImage();

    emit(
      "update:modelValue",
      false
    );
  } catch (error) {
    const data =
      error?.response?.data;

    localError.value =
      resolveApiError(data) ||
      error?.message ||
      (
        "No se pudo eliminar la fotografía. " +
        "Intente nuevamente."
      );

    emit(
      "toast",
      "error",
      localError.value,
      5200
    );
  } finally {
    deleting.value = false;
  }
};


const deleteAvatar = () => {
  if (
    busy.value ||
    !hasCurrentAvatar.value
  ) {
    return;
  }

  openNotice({
    title: "Eliminar fotografía",
    message:
      "¿Desea eliminar su fotografía de perfil? " +
      "El sistema volverá a mostrar sus iniciales.",
    confirm: true,
    confirmText: "Eliminar fotografía",
    cancelText: "Conservar fotografía",
    onConfirm: performDeleteAvatar,
  });
};


/* ============================================================
   ERROR DE PREVISUALIZACIÓN
============================================================ */

const handlePreviewError = () => {
  if (isPreviewMode.value) {
    localError.value =
      (
        "No fue posible mostrar la imagen seleccionada. " +
        "Seleccione otro archivo."
      );

    clearSelectedImage();
  }
};


/* ============================================================
   MODAL Y ACCESIBILIDAD
============================================================ */

const getFocusableElements = () => {
  if (!modalRef.value) {
    return [];
  }

  const selector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled]):not([type='hidden'])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  return Array.from(
    modalRef.value.querySelectorAll(
      selector
    )
  ).filter((element) => {
    return Boolean(
      !element.hasAttribute("hidden") &&
      element.getAttribute(
        "aria-hidden"
      ) !== "true" &&
      element.getClientRects().length > 0
    );
  });
};


const focusInitialControl = async () => {
  await nextTick();

  if (
    selectActionRef.value instanceof
    HTMLElement &&
    !selectActionRef.value.disabled
  ) {
    selectActionRef.value.focus();
    return;
  }

  if (
    closeButtonRef.value instanceof
    HTMLElement
  ) {
    closeButtonRef.value.focus();
    return;
  }

  modalRef.value?.focus();
};


const closeModal = () => {
  if (busy.value) {
    return;
  }

  emit(
    "update:modelValue",
    false
  );
};


const handleModalKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeModal();
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getFocusableElements();

  if (!focusableElements.length) {
    event.preventDefault();
    modalRef.value?.focus();
    return;
  }

  const firstElement =
    focusableElements[0];

  const lastElement =
    focusableElements[
      focusableElements.length - 1
    ];

  const activeElement =
    document.activeElement;

  if (
    event.shiftKey &&
    activeElement === firstElement
  ) {
    event.preventDefault();
    lastElement.focus();
    return;
  }

  if (
    !event.shiftKey &&
    activeElement === lastElement
  ) {
    event.preventDefault();
    firstElement.focus();
  }
};


/* ============================================================
   REINICIO DEL MODAL
============================================================ */

const resetModalState = () => {
  revokePreviewUrl();

  tempFile.value = null;
  selectedDimensions.value = null;

  localError.value = "";
  isDragging.value = false;
  dragCounter.value = 0;

  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
};


watch(
  () => props.modelValue,
  async (isOpen) => {
    if (isOpen) {
      previouslyFocusedElement =
        document.activeElement;

      document.body.classList.add(
        BODY_LOCK_CLASS
      );

      resetModalState();

      await focusInitialControl();
      return;
    }

    document.body.classList.remove(
      BODY_LOCK_CLASS
    );

    resetModalState();

    if (
      previouslyFocusedElement instanceof
      HTMLElement
    ) {
      window.requestAnimationFrame(
        () => {
          previouslyFocusedElement?.focus?.();
        }
      );
    }
  },
  {
    immediate: true,
  }
);


onBeforeUnmount(() => {
  document.body.classList.remove(
    BODY_LOCK_CLASS
  );

  resetModalState();
});
</script>