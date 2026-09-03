<template>
  <div
    class="sgpc-upload"
    :class="{ 'is-dragover': isDragOver }"
  >
    <div class="sgpc-upload__head">
      <h4 class="sgpc-upload__title">
        {{ title }}
      </h4>

      <p class="sgpc-upload__desc">
        {{ description }}
      </p>
    </div>

    <div
      class="sgpc-upload__summary"
      aria-label="Condiciones de los archivos"
    >
      <span>PDF</span>
      <span aria-hidden="true">·</span>
      <span>
        Máximo {{ effectiveMaxFiles }}
        {{ effectiveMaxFiles === 1 ? "archivo" : "archivos" }}
      </span>

      <template v-if="usesPrimarySlot">
        <span aria-hidden="true">·</span>
        <span>Principal: {{ primaryMaxSizeMb }} MB</span>
        <span aria-hidden="true">·</span>
        <span>Adicionales: {{ attachmentMaxSizeMb }} MB</span>
      </template>

      <template v-else>
        <span aria-hidden="true">·</span>
        <span>Hasta {{ attachmentMaxSizeMb }} MB por archivo</span>
      </template>
    </div>

    <label
      class="sgpc-upload__trigger"
      :class="{ 'is-dragover': isDragOver }"
      :for="inputId"
      @dragenter.prevent="isDragOver = true"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
    >
      <input
        :id="inputId"
        ref="fileInput"
        class="sgpc-upload__native"
        type="file"
        accept=".pdf,application/pdf,application/x-pdf"
        :multiple="multiple"
        :aria-describedby="describedByIds"
        :aria-invalid="Boolean(error || localMessageType === 'error')"
        @change="onInputChange"
      />

      <span class="sgpc-upload__trigger-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
          <path
            d="M12 16V8M8 12h8"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
          <path
            d="M7 4.75h7.586a2 2 0 0 1 1.414.586l2.664 2.664A2 2 0 0 1 19.25 9.414V18A2.25 2.25 0 0 1 17 20.25H7A2.25 2.25 0 0 1 4.75 18V7A2.25 2.25 0 0 1 7 4.75Z"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linejoin="round"
          />
        </svg>
      </span>

      <span class="sgpc-upload__trigger-copy">
        <span class="sgpc-upload__trigger-title">
          {{ multiple ? "Seleccionar archivos" : "Seleccionar archivo" }}
        </span>
        <span class="sgpc-upload__trigger-meta">
          {{ multiple ? "o arrástrelos aquí" : "o arrástrelo aquí" }}
        </span>
      </span>
    </label>

    <div class="sgpc-upload__foot">
      <p
        v-if="helperText"
        :id="helperId"
        class="sgpc-upload__hint"
      >
        {{ helperText }}
      </p>

      <p
        v-if="isRestoringFiles"
        class="sgpc-upload__hint"
        role="status"
        aria-live="polite"
      >
        Recuperando archivos del borrador...
      </p>

      <p
        v-if="hasRecoveredItems && !isRestoringFiles"
        :id="recoveredWarningId"
        class="sgpc-upload__warning"
      >
        Algunos archivos del borrador deben seleccionarse nuevamente.
      </p>

      <p
        v-if="localMessage"
        :id="localMessageId"
        :class="['sgpc-alert', `is-${localMessageType}`]"
        :role="localMessageType === 'error' ? 'alert' : 'status'"
        :aria-live="localMessageType === 'error' ? 'assertive' : 'polite'"
      >
        {{ localMessage }}
      </p>

      <p
        v-if="error"
        :id="externalErrorId"
        class="sgpc-upload__error"
        role="alert"
        aria-live="assertive"
      >
        {{ error }}
      </p>
    </div>

    <div
      v-if="items.length"
      class="sgpc-file-list"
      aria-label="Archivos seleccionados"
    >
      <article
        v-for="(item, index) in items"
        :key="item.key"
        class="sgpc-file-chip"
        :class="{
          'sgpc-file-chip--cached': isRecovered(item),
          'sgpc-file-chip--warning': isOversize(item, index),
        }"
      >
        <div class="sgpc-file-chip__top">
          <div class="sgpc-file-chip__main">
            <div class="sgpc-file-chip__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
                <path
                  d="M7 3.75h7.2a2 2 0 0 1 1.414.586l2.05 2.05a2 2 0 0 1 .586 1.414V19A2.25 2.25 0 0 1 16 21.25H8A2.25 2.25 0 0 1 5.75 19V6A2.25 2.25 0 0 1 8 3.75Z"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linejoin="round"
                />
                <path
                  d="M9 12.25h6M9 15.75h6M9 8.75h3.5"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </div>

            <div class="sgpc-file-chip__body">
              <div class="sgpc-file-chip__name">
                {{ displayName(item) }}
              </div>
              <div class="sgpc-file-chip__meta">
                {{ prettySize(item.file?.size || item.size || 0) }}
              </div>

              <div
                v-if="
                  (usesPrimarySlot && index === 0) ||
                  isRecovered(item) ||
                  isOversize(item, index)
                "
                class="sgpc-file-chip__badges"
              >
                <span
                  v-if="usesPrimarySlot && index === 0"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--ok"
                >
                  Documento principal
                </span>
                <span
                  v-if="isRecovered(item)"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--draft"
                >
                  Debe seleccionarse nuevamente
                </span>
                <span
                  v-if="isOversize(item, index)"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--warning"
                >
                  Supera el tamaño permitido
                </span>
              </div>
            </div>
          </div>

          <div class="sgpc-file-chip__actions">
            <button
              type="button"
              class="sgpc-btn sgpc-file-chip__order-btn"
              :disabled="index === 0"
              :aria-label="`Subir ${displayName(item)} una posición`"
              @click="moveUp(index)"
            >
              <span aria-hidden="true">↑</span>
              Subir
            </button>

            <button
              type="button"
              class="sgpc-btn sgpc-file-chip__order-btn"
              :disabled="index === items.length - 1"
              :aria-label="`Bajar ${displayName(item)} una posición`"
              @click="moveDown(index)"
            >
              <span aria-hidden="true">↓</span>
              Bajar
            </button>

            <button
              type="button"
              class="sgpc-file-chip__remove"
              :aria-label="`Quitar ${displayName(item)}`"
              @click="removeItem(index)"
            >
              Quitar
            </button>
          </div>
        </div>

        <div class="sgpc-file-chip__form">
          <label
            class="sgpc-label"
            :for="`${inputId}-nombre-${index}`"
          >
            Descripción del documento
            <span class="sgpc-file-chip__optional">(opcional)</span>
          </label>

          <input
            :id="`${inputId}-nombre-${index}`"
            class="sgpc-input"
            type="text"
            :value="item.nombre || ''"
            :maxlength="MAX_ATTACHMENT_NAME_LENGTH"
            placeholder="Ej. Carta de aceptación"
            @input="updateName(index, $event.target.value)"
          />

          <p class="sgpc-hint">
            <template v-if="isRecovered(item)">
              Este archivo no pudo recuperarse del borrador.
              Selecciónelo nuevamente.
            </template>
            <template v-else>
              Use una descripción breve solo si necesita identificar este archivo.
            </template>
          </p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  MAX_ATTACHMENT_FILES,
  MAX_ATTACHMENT_NAME_LENGTH,
  MAX_ATTACHMENT_PDF_FILE_SIZE,
  MAX_FILES_WITH_PRIMARY,
  MAX_PRIMARY_PDF_FILE_SIZE,
  buildUploadItem,
  cacheUploadFile,
  deleteCachedUploadFile,
  loadCachedUploadFile,
  makeUploadKey,
  pruneCachedUploadFiles,
  uploadFingerprint,
  validatePdfFile,
} from "../../scripts/utils/adjuntosPdf";

defineOptions({
  name: "AdjuntosPdfUploader",
});

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },

  error: {
    type: String,
    default: "",
  },

  inputId: {
    type: String,
    required: true,
  },

  title: {
    type: String,
    default: "Documentos",
  },

  description: {
    type: String,
    default:
      "Adjunte el documento de la publicación y, si corresponde, archivos adicionales.",
  },

  helperText: {
    type: String,
    default: "",
  },

  multiple: {
    type: Boolean,
    default: true,
  },

  maxFiles: {
    type: Number,
    default: 2,
  },

  usesPrimarySlot: {
    type: Boolean,
    default: false,
  },

  primaryMaxSizeMb: {
    type: Number,
    default: Math.round(
      MAX_PRIMARY_PDF_FILE_SIZE /
        (1024 * 1024)
    ),
  },

  attachmentMaxSizeMb: {
    type: Number,
    default: Math.round(
      MAX_ATTACHMENT_PDF_FILE_SIZE /
        (1024 * 1024)
    ),
  },
});

const emit = defineEmits([
  "update:modelValue",
]);

const fileInput = ref(null);

const isDragOver = ref(false);

const localMessage = ref("");

const localMessageType = ref(
  "info"
);

const draggedIndex = ref(null);

const dragOverIndex = ref(null);

const isRestoringFiles = ref(
  false
);

const bytesPerMb = 1024 * 1024;

const generatedKeys =
  new Map();

let hydrationPromise = null;

// ============================================================
// CONFIGURACIÓN
// ============================================================

const positiveNumber = (
  value,
  fallback
) => {
  const parsed =
    Number(value);

  if (
    !Number.isFinite(parsed) ||
    parsed <= 0
  ) {
    return fallback;
  }

  return parsed;
};

const effectiveMaxFiles =
  computed(() => {
    if (!props.multiple) {
      return 1;
    }

    const requested =
      Math.max(
        1,
        Math.trunc(
          positiveNumber(
            props.maxFiles,
            1
          )
        )
      );

    const backendMaximum =
      props.usesPrimarySlot
        ? MAX_FILES_WITH_PRIMARY
        : MAX_ATTACHMENT_FILES;

    return Math.min(
      requested,
      backendMaximum
    );
  });

const primaryMaxBytes =
  computed(() => {
    return (
      Math.min(
        positiveNumber(
          props.primaryMaxSizeMb,
          5
        ),
        MAX_PRIMARY_PDF_FILE_SIZE /
          bytesPerMb
      ) * bytesPerMb
    );
  });

const attachmentMaxBytes =
  computed(() => {
    return (
      Math.min(
        positiveNumber(
          props.attachmentMaxSizeMb,
          3
        ),
        MAX_ATTACHMENT_PDF_FILE_SIZE /
          bytesPerMb
      ) * bytesPerMb
    );
  });

// ============================================================
// IDS
// ============================================================

const helperId = computed(
  () =>
    `${props.inputId}-helper`
);

const recoveredWarningId =
  computed(
    () =>
      `${props.inputId}-recovered-warning`
  );

const localMessageId =
  computed(
    () =>
      `${props.inputId}-local-message`
  );

const externalErrorId =
  computed(
    () =>
      `${props.inputId}-error`
  );

const describedByIds =
  computed(() => {
    const ids = [];

    if (props.helperText) {
      ids.push(
        helperId.value
      );
    }

    if (
      hasRecoveredItems.value
    ) {
      ids.push(
        recoveredWarningId.value
      );
    }

    if (localMessage.value) {
      ids.push(
        localMessageId.value
      );
    }

    if (props.error) {
      ids.push(
        externalErrorId.value
      );
    }

    return ids.join(" ");
  });

// ============================================================
// NORMALIZACIÓN
// ============================================================

const resolveGeneratedKey = (
  item,
  index
) => {
  if (item?.key) {
    return item.key;
  }

  const signature = [
    item?.file?.name ||
      item?.originalName ||
      "archivo",

    item?.file?.size ??
      item?.size ??
      0,

    item?.file?.lastModified ??
      item?.lastModified ??
      0,

    index,
  ].join("::");

  if (
    !generatedKeys.has(
      signature
    )
  ) {
    generatedKeys.set(
      signature,
      makeUploadKey()
    );
  }

  return generatedKeys.get(
    signature
  );
};

const normalizeItem = (
  item,
  index
) => ({
  key:
    resolveGeneratedKey(
      item,
      index
    ),

  file:
    item?.file || null,

  nombre: String(
    item?.nombre || ""
  ).slice(
    0,
    MAX_ATTACHMENT_NAME_LENGTH
  ),

  originalName: String(
    item?.file?.name ||
      item?.originalName ||
      ""
  ),

  size: Number(
    item?.file?.size ??
      item?.size ??
      0
  ),

  lastModified: Number(
    item?.file?.lastModified ??
      item?.lastModified ??
      0
  ),
});

const items = computed(
  () =>
    (
      Array.isArray(
        props.modelValue
      )
        ? props.modelValue
        : []
    ).map(
      normalizeItem
    )
);

// ============================================================
// ESTADOS
// ============================================================

function isRecovered(item) {
  return Boolean(
    !item?.file &&
      item?.originalName
  );
}

const hasRecoveredItems =
  computed(() =>
    items.value.some(
      isRecovered
    )
  );

// ============================================================
// WATCH
// ============================================================

watch(
  () => props.error,
  (value) => {
    if (value) {
      localMessage.value = "";
      localMessageType.value =
        "info";
    }
  }
);

watch(
  () => props.modelValue,
  async (nextValue, previousValue) => {
    const next =
      (
        Array.isArray(nextValue)
          ? nextValue
          : []
      ).map(normalizeItem);

    const previous =
      (
        Array.isArray(previousValue)
          ? previousValue
          : []
      ).map(normalizeItem);

    // --------------------------------------------------------
    // Si un elemento desapareció del modelValue, eliminamos
    // también su File almacenado en IndexedDB.
    // --------------------------------------------------------

    const nextKeys =
      new Set(
        next
          .map(
            (item) =>
              item?.key
          )
          .filter(Boolean)
      );

    const removedKeys =
      previous
        .map(
          (item) =>
            item?.key
        )
        .filter(
          (key) =>
            key &&
            !nextKeys.has(key)
        );

    if (removedKeys.length) {
      await Promise.all(
        removedKeys.map(
          (key) =>
            deleteCachedUploadFile(
              key
            )
        )
      );
    }

    // --------------------------------------------------------
    // Si existe File real, aseguramos que quede guardado.
    // --------------------------------------------------------

    await persistFilesInCache(
      next
    );

    // --------------------------------------------------------
    // Si tenemos placeholders recuperados, intentamos
    // reconstruirlos automáticamente.
    // --------------------------------------------------------

    if (
      next.some(isRecovered)
    ) {
      await hydrateRecoveredFiles();
    }
  },
  {
    deep: true,
  }
);

// ============================================================
// EMIT
// ============================================================

function setItems(next) {
  emit(
    "update:modelValue",

    next
      .map(
        (item, index) =>
          normalizeItem(
            item,
            index
          )
      )
      .slice(
        0,
        effectiveMaxFiles.value
      )
  );
}

// ============================================================
// CACHE
// ============================================================

async function persistFilesInCache(
  source = []
) {
  const liveFiles =
    (
      Array.isArray(source)
        ? source
        : []
    ).filter(
      (item) =>
        item?.key &&
        item?.file
    );

  if (!liveFiles.length) {
    return {
      total: 0,
      saved: 0,
    };
  }

  const results =
    await Promise.all(
      liveFiles.map(
        (item) =>
          cacheUploadFile(
            item
          )
      )
    );

  return {
    total:
      liveFiles.length,

    saved:
      results.filter(Boolean)
        .length,
  };
}

async function hydrateRecoveredFiles() {
  if (hydrationPromise) {
    return hydrationPromise;
  }

  const recovered =
    items.value.filter(
      isRecovered
    );

  if (!recovered.length) {
    return;
  }

  hydrationPromise =
    (async () => {
      isRestoringFiles.value =
        true;

      try {
        const next =
          items.value.map(
            (item) => ({
              ...item,
            })
          );

        let restoredCount = 0;

        for (
          let index = 0;
          index < next.length;
          index += 1
        ) {
          const item =
            next[index];

          if (
            !isRecovered(item) ||
            !item?.key
          ) {
            continue;
          }

          const file =
            await loadCachedUploadFile(
              item.key,
              item
            );

          if (!file) {
            continue;
          }

          const validation =
            await validatePdfFile(
              file,
              {
                maxBytes:
                  getLimitBytesForIndex(
                    index
                  ),

                validateSignature:
                  false,
              }
            );

          if (
            !validation.valid
          ) {
            await deleteCachedUploadFile(
              item.key
            );

            continue;
          }

          next[index] = {
            ...item,

            file,

            originalName:
              file.name ||
              item.originalName ||
              "",

            size:
              Number(
                file.size || 0
              ),

            lastModified:
              Number(
                file.lastModified ||
                  0
              ),
          };

          restoredCount += 1;
        }

        if (restoredCount) {
          setItems(next);

          setLocalMessage(
            restoredCount === 1
              ? "Se recuperó 1 archivo del borrador."
              : `${restoredCount} archivos fueron recuperados del borrador.`,
            "success"
          );
        }
      } finally {
        isRestoringFiles.value =
          false;

        hydrationPromise = null;
      }
    })();

  return hydrationPromise;
}

// ============================================================
// MENSAJES
// ============================================================

function clearLocalMessage() {
  localMessage.value = "";
  localMessageType.value =
    "info";
}

function setLocalMessage(
  message,
  type = "info"
) {
  localMessage.value =
    message;

  localMessageType.value =
    type;
}

// ============================================================
// FORMATO
// ============================================================

function prettySize(bytes) {
  const size =
    Number(bytes || 0);

  if (size <= 0) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let unitIndex = 0;
  let normalizedSize = size;

  while (
    normalizedSize >= 1024 &&
    unitIndex <
      units.length - 1
  ) {
    normalizedSize /= 1024;
    unitIndex += 1;
  }

  return `${normalizedSize.toFixed(
    unitIndex === 0
      ? 0
      : 2
  )} ${units[unitIndex]}`;
}

function displayName(item) {
  return (
    item?.file?.name ||
    item?.originalName ||
    "Archivo PDF"
  );
}

// ============================================================
// LÍMITES
// ============================================================

function getLimitBytesForIndex(
  index
) {
  if (
    props.usesPrimarySlot &&
    index === 0
  ) {
    return primaryMaxBytes.value;
  }

  return attachmentMaxBytes.value;
}

function isOversize(
  item,
  index
) {
  const size =
    Number(
      item?.file?.size ??
        item?.size ??
        0
    );

  return (
    size >
    getLimitBytesForIndex(
      index
    )
  );
}

// ============================================================
// NOMBRE PERSONALIZADO
// ============================================================

function updateName(
  index,
  value
) {
  const next =
    items.value.map(
      (item) => ({
        ...item,
      })
    );

  if (!next[index]) {
    return;
  }

  next[index].nombre =
    String(value || "")
      .trimStart()
      .slice(
        0,
        MAX_ATTACHMENT_NAME_LENGTH
      );

  setItems(next);
}

// ============================================================
// QUITAR
// ============================================================

async function removeItem(
  index
) {
  const next =
    items.value.map(
      (item) => ({
        ...item,
      })
    );

  if (!next[index]) {
    return;
  }

  const removed =
    next[index];

  const removedName =
    displayName(removed);

  if (removed?.key) {
    await deleteCachedUploadFile(
      removed.key
    );
  }

  next.splice(
    index,
    1
  );

  setItems(next);

  setLocalMessage(
    `Se quitó "${removedName}".`,
    "info"
  );
}

// ============================================================
// VALIDAR ORDEN
// ============================================================

function validateArrangement(
  candidate
) {
  if (
    candidate.length >
    effectiveMaxFiles.value
  ) {
    setLocalMessage(
      `Puede agregar como máximo ${effectiveMaxFiles.value} ${effectiveMaxFiles.value === 1 ? "archivo" : "archivos"}.`,
      "error"
    );

    return false;
  }

  for (
    let index = 0;
    index <
    candidate.length;
    index += 1
  ) {
    if (
      isRecovered(
        candidate[index]
      )
    ) {
      continue;
    }

    const fileSize =
      Number(
        candidate[index]
          ?.file?.size ??
          candidate[index]
            ?.size ??
          0
      );

    if (fileSize <= 0) {
      setLocalMessage(
        `El archivo "${displayName(
          candidate[index]
        )}" está vacío.`,
        "error"
      );

      return false;
    }

    const limit =
      getLimitBytesForIndex(
        index
      );

    if (
      fileSize > limit
    ) {
      setLocalMessage(
        `El archivo "${displayName(
          candidate[index]
        )}" supera el límite permitido para la posición ${index + 1}.`,
        "error"
      );

      return false;
    }
  }

  return true;
}

// ============================================================
// REORDENAR
// ============================================================

function moveUp(index) {
  if (index <= 0) {
    return;
  }

  const next =
    items.value.map(
      (item) => ({
        ...item,
      })
    );

  [
    next[index - 1],
    next[index],
  ] = [
    next[index],
    next[index - 1],
  ];

  if (
    !validateArrangement(
      next
    )
  ) {
    return;
  }

  setItems(next);

  setLocalMessage(
    "Orden de archivos actualizado.",
    "info"
  );
}

function moveDown(index) {
  if (
    index >=
    items.value.length - 1
  ) {
    return;
  }

  const next =
    items.value.map(
      (item) => ({
        ...item,
      })
    );

  [
    next[index + 1],
    next[index],
  ] = [
    next[index],
    next[index + 1],
  ];

  if (
    !validateArrangement(
      next
    )
  ) {
    return;
  }

  setItems(next);

  setLocalMessage(
    "Orden de archivos actualizado.",
    "info"
  );
}

// ============================================================
// INPUT
// ============================================================

async function onInputChange(
  event
) {
  const files =
    Array.from(
      event?.target?.files ||
        []
    );

  if (event?.target) {
    event.target.value =
      "";
  }

  await addFiles(files);
}

// ============================================================
// DRAG GENERAL
// ============================================================

function onDragOver(event) {
  isDragOver.value = true;

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer.dropEffect =
      "copy";
  }
}

function onDragLeave(event) {
  const current =
    event.currentTarget;

  const related =
    event.relatedTarget;

  if (
    current &&
    related &&
    current.contains?.(
      related
    )
  ) {
    return;
  }

  isDragOver.value =
    false;
}

async function onDrop(event) {
  isDragOver.value =
    false;

  const files =
    Array.from(
      event?.dataTransfer?.files ||
        []
    );

  await addFiles(files);
}

// ============================================================
// ENCONTRAR PLACEHOLDER
// ============================================================

function findRecoveredMatchIndex(
  base,
  file
) {
  const normalizedName =
    String(
      file?.name || ""
    )
      .trim()
      .toLowerCase();

  const size =
    Number(
      file?.size || 0
    );

  const lastModified =
    Number(
      file?.lastModified || 0
    );

  return base.findIndex(
    (item) =>
      !item?.file &&
      String(
        item?.originalName ||
          ""
      )
        .trim()
        .toLowerCase() ===
        normalizedName &&
      Number(
        item?.size || 0
      ) === size &&
      (
        !Number(
          item?.lastModified ||
            0
        ) ||
        Number(
          item?.lastModified ||
            0
        ) === lastModified
      )
  );
}

function fingerprintFromItem(
  item
) {
  if (item?.file) {
    return uploadFingerprint(
      item.file
    );
  }

  return [
    String(
      item?.originalName ||
        ""
    )
      .trim()
      .toLowerCase(),

    Number(
      item?.size || 0
    ),

    Number(
      item?.lastModified ||
        0
    ),
  ].join("::");
}

// ============================================================
// AGREGAR ARCHIVOS
// ============================================================

async function addFiles(
  files = []
) {
  clearLocalMessage();

  if (!files.length) {
    setLocalMessage(
      "No se seleccionaron archivos.",
      "info"
    );

    return;
  }

  let base =
    props.multiple
      ? items.value.map(
          (item) => ({
            ...item,
          })
        )
      : [];

  const fingerprints =
    new Set(
      base
        .filter(
          (item) =>
            item?.file
        )
        .map(
          fingerprintFromItem
        )
    );

  let added = 0;
  let replacedRecovered = 0;
  let duplicated = 0;

  let invalidExtension = 0;
  let invalidMime = 0;
  let emptyFiles = 0;
  let oversize = 0;

  let limitReached = false;

  const countValidationFailure =
    (reason) => {
      if (
        reason ===
        "extension"
      ) {
        invalidExtension += 1;
      } else if (
        reason === "mime"
      ) {
        invalidMime += 1;
      } else if (
        reason === "empty"
      ) {
        emptyFiles += 1;
      } else if (
        reason === "size"
      ) {
        oversize += 1;
      }
    };

  for (const file of files) {
    const fingerprint =
      uploadFingerprint(
        file
      );

    if (
      fingerprints.has(
        fingerprint
      )
    ) {
      duplicated += 1;
      continue;
    }

    const recoveredIndex =
      findRecoveredMatchIndex(
        base,
        file
      );

    // --------------------------------------------------------
    // REEMPLAZAR PLACEHOLDER
    // --------------------------------------------------------

    if (
      recoveredIndex !== -1
    ) {
      const validation =
        await validatePdfFile(
          file,
          {
            maxBytes:
              getLimitBytesForIndex(
                recoveredIndex
              ),

            validateSignature:
              false,
          }
        );

      if (
        !validation.valid
      ) {
        countValidationFailure(
          validation.reason
        );

        continue;
      }

      base[recoveredIndex] = {
        ...base[
          recoveredIndex
        ],

        file,

        originalName:
          file.name ||
          base[
            recoveredIndex
          ].originalName ||
          "",

        size:
          Number(
            file.size || 0
          ),

        lastModified:
          Number(
            file.lastModified ||
              0
          ),
      };

      fingerprints.add(
        fingerprint
      );

      replacedRecovered += 1;

      if (!props.multiple) {
        break;
      }

      continue;
    }

    // --------------------------------------------------------
    // LÍMITE
    // --------------------------------------------------------

    if (
      base.length >=
      effectiveMaxFiles.value
    ) {
      limitReached = true;
      break;
    }

    const targetIndex =
      props.multiple
        ? base.length
        : 0;

    // --------------------------------------------------------
    // VALIDACIÓN
    // --------------------------------------------------------

    const validation =
      await validatePdfFile(
        file,
        {
          maxBytes:
            getLimitBytesForIndex(
              targetIndex
            ),

          validateSignature:
            false,
        }
      );

    if (
      !validation.valid
    ) {
      countValidationFailure(
        validation.reason
      );

      continue;
    }

    const uploadItem =
      buildUploadItem(
        file
      );

    if (!props.multiple) {
      base = [
        uploadItem,
      ];

      fingerprints.add(
        fingerprint
      );

      added += 1;
      break;
    }

    base.push(
      uploadItem
    );

    fingerprints.add(
      fingerprint
    );

    added += 1;
  }

  // ==========================================================
  // MUY IMPORTANTE:
  // Guardamos el File real ANTES de actualizar el v-model.
  // Así reducimos el riesgo de que el usuario recargue antes
  // de que el PDF haya sido persistido.
  // ==========================================================

  const cacheResult =
    await persistFilesInCache(
      base
    );

  setItems(base);

  const parts = [];

  if (added) {
    parts.push(
      added === 1
        ? "1 archivo agregado"
        : `${added} archivos agregados`
    );
  }

  if (
    replacedRecovered
  ) {
    parts.push(
      replacedRecovered === 1
        ? "1 archivo del borrador fue seleccionado nuevamente"
        : `${replacedRecovered} archivos del borrador fueron seleccionados nuevamente`
    );
  }

  if (duplicated) {
    parts.push(
      duplicated === 1
        ? "1 archivo ya estaba agregado"
        : `${duplicated} archivos ya estaban agregados`
    );
  }

  if (
    invalidExtension
  ) {
    parts.push(
      invalidExtension === 1
        ? "1 archivo no tiene extensión PDF"
        : `${invalidExtension} archivos no tienen extensión PDF`
    );
  }

  if (invalidMime) {
    parts.push(
      invalidMime === 1
        ? "1 archivo no es un PDF válido"
        : `${invalidMime} archivos no son PDF válidos`
    );
  }

  if (emptyFiles) {
    parts.push(
      emptyFiles === 1
        ? "1 archivo está vacío"
        : `${emptyFiles} archivos están vacíos`
    );
  }

  if (oversize) {
    parts.push(
      oversize === 1
        ? "1 archivo supera el límite de tamaño"
        : `${oversize} archivos superan el límite de tamaño`
    );
  }

  if (limitReached) {
    parts.push(
      `se alcanzó el máximo de ${effectiveMaxFiles.value} ${effectiveMaxFiles.value === 1 ? "archivo" : "archivos"}`
    );
  }

  if (
    cacheResult.total > 0 &&
    cacheResult.saved <
      cacheResult.total
  ) {
    parts.push(
      "algunos archivos podrían necesitar seleccionarse nuevamente al volver a este borrador"
    );
  }

  const hasErrors =
    Boolean(
      invalidExtension ||
        invalidMime ||
        emptyFiles ||
        oversize
    );

  const hasSuccess =
    Boolean(
      added ||
        replacedRecovered
    );

  setLocalMessage(
    parts.join(" · ") ||
      "Sin cambios.",

    hasErrors
      ? "error"
      : hasSuccess
        ? "success"
        : "info"
  );
}

// ============================================================
// DRAG / REORDENAR
// ============================================================

function onDragStart(
  index,
  event
) {
  draggedIndex.value =
    index;

  dragOverIndex.value =
    index;

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer.effectAllowed =
      "move";

    event.dataTransfer.setData(
      "text/plain",
      String(index)
    );
  }
}

function onDragEnd() {
  draggedIndex.value =
    null;

  dragOverIndex.value =
    null;
}

function onCardDragOver(
  index,
  event
) {
  if (
    draggedIndex.value ==
    null
  ) {
    return;
  }

  dragOverIndex.value =
    index;

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer.dropEffect =
      "move";
  }
}

function onCardDrop(index) {
  if (
    draggedIndex.value ==
    null
  ) {
    return;
  }

  if (
    draggedIndex.value ===
    index
  ) {
    onDragEnd();
    return;
  }

  const next =
    items.value.map(
      (item) => ({
        ...item,
      })
    );

  const [moved] =
    next.splice(
      draggedIndex.value,
      1
    );

  next.splice(
    index,
    0,
    moved
  );

  if (
    !validateArrangement(
      next
    )
  ) {
    onDragEnd();
    return;
  }

  setItems(next);

  onDragEnd();

  setLocalMessage(
    "Orden de archivos actualizado.",
    "info"
  );
}

// ============================================================
// INICIALIZACIÓN
// ============================================================

onMounted(async () => {
  // Elimina PDF de borradores antiguos.
  await pruneCachedUploadFiles();

  // Primero aseguramos cualquier File que ya exista.
  await persistFilesInCache(
    items.value
  );

  // Después buscamos automáticamente los archivos que vinieron
  // restaurados únicamente como metadata desde localStorage.
  if (
    hasRecoveredItems.value
  ) {
    await hydrateRecoveredFiles();
  }
});
</script>

<style
  scoped
  src="./adjuntos-pdf.css"
></style>