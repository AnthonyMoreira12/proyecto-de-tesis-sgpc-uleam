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
      class="sgpc-upload__chips"
      aria-label="Restricciones de archivos"
    >
      <span class="sgpc-upload__chip">
        PDF
      </span>

      <span class="sgpc-upload__chip">
        {{ multiple ? "Múltiples archivos" : "Un solo archivo" }}
      </span>

      <span class="sgpc-upload__chip">
        {{ items.length }}/{{ effectiveMaxFiles }}
      </span>

      <span
        v-if="usesPrimarySlot"
        class="sgpc-upload__chip"
      >
        Principal: ≤ {{ primaryMaxSizeMb }} MB
      </span>

      <span class="sgpc-upload__chip">
        {{ usesPrimarySlot ? "Adjuntos" : "Cada PDF" }}:
        ≤ {{ attachmentMaxSizeMb }} MB
      </span>
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
        accept="application/pdf,.pdf"
        :multiple="multiple"
        :aria-describedby="describedByIds"
        :aria-invalid="Boolean(error || localMessageType === 'error')"
        @change="onInputChange"
      />

      <span
        class="sgpc-upload__trigger-icon"
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 24 24"
          width="22"
          height="22"
          fill="none"
        >
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
          {{
            multiple
              ? "Seleccionar uno o varios PDF"
              : "Seleccionar archivo PDF"
          }}
        </span>

        <span class="sgpc-upload__trigger-meta">
          {{
            multiple
              ? "También puede arrastrar y soltar varios PDF"
              : "También puede arrastrar y soltar un PDF"
          }}
        </span>
      </span>
    </label>

    <div class="sgpc-upload__foot">
      <p
        :id="helperId"
        class="sgpc-upload__hint"
      >
        {{ helperText }}
      </p>

      <p
        v-if="hasRecoveredItems"
        :id="recoveredWarningId"
        class="sgpc-upload__warning"
      >
        Se recuperaron referencias de archivos desde el borrador local.
        Debe volver a seleccionarlos antes de guardar o quitarlos de la lista.
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
      aria-label="Archivos PDF seleccionados"
    >
      <article
        v-for="(item, index) in items"
        :key="item.key"
        class="sgpc-file-chip"
        :class="{
          'sgpc-file-chip--cached': isRecovered(item),
          'sgpc-file-chip--warning': isOversize(item, index),
          'is-dragging': draggedIndex === index,
          'is-dragover':
            dragOverIndex === index && draggedIndex !== index,
        }"
        @dragover.prevent="onCardDragOver(index, $event)"
        @drop.prevent="onCardDrop(index)"
      >
        <div class="sgpc-file-chip__top">
          <div class="sgpc-file-chip__main">
            <button
              type="button"
              class="sgpc-file-chip__move"
              draggable="true"
              :aria-label="`Arrastrar ${displayName(item)}`"
              title="Arrastrar para reordenar"
              @dragstart="onDragStart(index, $event)"
              @dragend="onDragEnd"
            >
              ⋮⋮
            </button>

            <div
              class="sgpc-file-chip__icon"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                width="20"
                height="20"
                fill="none"
              >
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
                Tamaño: {{ prettySize(item.file?.size || item.size || 0) }}
              </div>

              <div class="sgpc-file-chip__badges">
                <span class="sgpc-file-chip__badge">
                  #{{ index + 1 }}
                </span>

                <span
                  v-if="usesPrimarySlot && index === 0"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--ok"
                >
                  Principal
                </span>

                <span
                  v-else
                  class="sgpc-file-chip__badge"
                >
                  Adjunto
                </span>

                <span
                  v-if="isRecovered(item)"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--draft"
                >
                  Re-seleccionar
                </span>

                <span
                  v-if="isOversize(item, index)"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--warning"
                >
                  Supera límite
                </span>
              </div>
            </div>
          </div>

          <div class="sgpc-file-chip__actions">
            <button
              type="button"
              class="sgpc-btn"
              :disabled="index === 0"
              :aria-label="`Subir ${displayName(item)} una posición`"
              @click="moveUp(index)"
            >
              Subir
            </button>

            <button
              type="button"
              class="sgpc-btn"
              :disabled="index === items.length - 1"
              :aria-label="`Bajar ${displayName(item)} una posición`"
              @click="moveDown(index)"
            >
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
            Nombre personalizado
          </label>

          <input
            :id="`${inputId}-nombre-${index}`"
            class="sgpc-input"
            type="text"
            :value="item.nombre || ''"
            maxlength="180"
            placeholder="Ej. PDF principal / Carta de aceptación / Evidencia editorial / ..."
            @input="updateName(index, $event.target.value)"
          />

          <p class="sgpc-hint">
            <template v-if="isRecovered(item)">
              Este elemento proviene del borrador local. Debe volver a
              seleccionarlo antes de enviarlo.
            </template>

            <template v-else>
              Este nombre se enviará junto al archivo para organizarlo mejor.
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
  ref,
  watch,
} from "vue";

import {
  MAX_ATTACHMENT_PDF_FILE_SIZE,
  MAX_PRIMARY_PDF_FILE_SIZE,
  buildUploadItem,
  isPdfFile,
  makeUploadKey,
  uploadFingerprint,
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
    default: "Agregar archivos PDF",
  },

  description: {
    type: String,
    default: "Adjunte evidencias o soportes en PDF.",
  },

  helperText: {
    type: String,
    default: "Formato permitido: PDF.",
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
const localMessageType = ref("info");
const draggedIndex = ref(null);
const dragOverIndex = ref(null);

const bytesPerMb = 1024 * 1024;
const generatedKeys = new Map();

const positiveNumber = (
  value,
  fallback
) => {
  const parsed = Number(value);

  if (
    !Number.isFinite(parsed) ||
    parsed <= 0
  ) {
    return fallback;
  }

  return parsed;
};

const effectiveMaxFiles = computed(() => {
  if (!props.multiple) {
    return 1;
  }

  return Math.max(
    1,
    Math.trunc(
      positiveNumber(
        props.maxFiles,
        1
      )
    )
  );
});

const primaryMaxBytes = computed(() => (
  positiveNumber(
    props.primaryMaxSizeMb,
    5
  ) * bytesPerMb
));

const attachmentMaxBytes = computed(() => (
  positiveNumber(
    props.attachmentMaxSizeMb,
    3
  ) * bytesPerMb
));

const helperId = computed(() => (
  `${props.inputId}-helper`
));

const recoveredWarningId = computed(() => (
  `${props.inputId}-recovered-warning`
));

const localMessageId = computed(() => (
  `${props.inputId}-local-message`
));

const externalErrorId = computed(() => (
  `${props.inputId}-error`
));

const describedByIds = computed(() => {
  const ids = [helperId.value];

  if (hasRecoveredItems.value) {
    ids.push(recoveredWarningId.value);
  }

  if (localMessage.value) {
    ids.push(localMessageId.value);
  }

  if (props.error) {
    ids.push(externalErrorId.value);
  }

  return ids.join(" ");
});

const resolveGeneratedKey = (
  item,
  index
) => {
  if (item?.key) {
    return item.key;
  }

  const signature = [
    item?.file?.name || item?.originalName || "archivo",
    item?.file?.size || item?.size || 0,
    item?.file?.lastModified || item?.lastModified || 0,
    index,
  ].join("::");

  if (!generatedKeys.has(signature)) {
    generatedKeys.set(
      signature,
      makeUploadKey()
    );
  }

  return generatedKeys.get(signature);
};

const normalizeItem = (
  item,
  index
) => ({
  key: resolveGeneratedKey(item, index),
  file: item?.file || null,
  nombre: String(item?.nombre || ""),
  originalName: String(
    item?.originalName ||
    item?.file?.name ||
    ""
  ),
  size: Number(
    item?.size ||
    item?.file?.size ||
    0
  ),
  lastModified: Number(
    item?.lastModified ||
    item?.file?.lastModified ||
    0
  ),
});

const items = computed(() => (
  (
    Array.isArray(props.modelValue)
      ? props.modelValue
      : []
  ).map(normalizeItem)
));

const hasRecoveredItems = computed(() => (
  items.value.some(isRecovered)
));

watch(
  () => props.error,
  (value) => {
    if (value) {
      localMessage.value = "";
      localMessageType.value = "info";
    }
  }
);

function setItems(next) {
  emit(
    "update:modelValue",
    next.map((item, index) => (
      normalizeItem(item, index)
    ))
  );
}

function clearLocalMessage() {
  localMessage.value = "";
  localMessageType.value = "info";
}

function setLocalMessage(
  message,
  type = "info"
) {
  localMessage.value = message;
  localMessageType.value = type;
}

function prettySize(bytes) {
  const size = Number(bytes || 0);

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
    unitIndex < units.length - 1
  ) {
    normalizedSize /= 1024;
    unitIndex += 1;
  }

  return `${normalizedSize.toFixed(
    unitIndex === 0 ? 0 : 2
  )} ${units[unitIndex]}`;
}

function displayName(item) {
  return (
    item?.file?.name ||
    item?.originalName ||
    "Archivo PDF"
  );
}

function isRecovered(item) {
  return Boolean(
    !item?.file &&
    item?.originalName
  );
}

function getLimitBytesForIndex(index) {
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
  const size = Number(
    item?.file?.size ||
    item?.size ||
    0
  );

  return (
    size >
    getLimitBytesForIndex(index)
  );
}

function updateName(
  index,
  value
) {
  const next = items.value.map((item) => ({
    ...item,
  }));

  if (!next[index]) {
    return;
  }

  next[index].nombre = String(
    value || ""
  ).trimStart();

  setItems(next);
}

function removeItem(index) {
  const next = items.value.map((item) => ({
    ...item,
  }));

  if (!next[index]) {
    return;
  }

  const removedName = displayName(
    next[index]
  );

  next.splice(index, 1);
  setItems(next);

  setLocalMessage(
    `Se quitó "${removedName}".`,
    "info"
  );
}

function validateArrangement(candidate) {
  for (
    let index = 0;
    index < candidate.length;
    index += 1
  ) {
    const fileSize = Number(
      candidate[index]?.file?.size ||
      candidate[index]?.size ||
      0
    );

    const limit = getLimitBytesForIndex(
      index
    );

    if (fileSize > limit) {
      setLocalMessage(
        `El archivo "${displayName(candidate[index])}" supera el límite permitido para la posición ${index + 1}.`,
        "error"
      );

      return false;
    }
  }

  return true;
}

function moveUp(index) {
  if (index <= 0) {
    return;
  }

  const next = items.value.map((item) => ({
    ...item,
  }));

  [
    next[index - 1],
    next[index],
  ] = [
    next[index],
    next[index - 1],
  ];

  if (!validateArrangement(next)) {
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

  const next = items.value.map((item) => ({
    ...item,
  }));

  [
    next[index + 1],
    next[index],
  ] = [
    next[index],
    next[index + 1],
  ];

  if (!validateArrangement(next)) {
    return;
  }

  setItems(next);
  setLocalMessage(
    "Orden de archivos actualizado.",
    "info"
  );
}

function onInputChange(event) {
  const files = Array.from(
    event?.target?.files || []
  );

  if (event?.target) {
    event.target.value = "";
  }

  addFiles(files);
}

function onDragOver(event) {
  isDragOver.value = true;

  if (event?.dataTransfer) {
    event.dataTransfer.dropEffect = "copy";
  }
}

function onDragLeave(event) {
  const current = event.currentTarget;
  const related = event.relatedTarget;

  if (
    current &&
    related &&
    current.contains?.(related)
  ) {
    return;
  }

  isDragOver.value = false;
}

function onDrop(event) {
  isDragOver.value = false;

  const files = Array.from(
    event?.dataTransfer?.files || []
  );

  addFiles(files);
}

function findRecoveredMatchIndex(
  base,
  file
) {
  const normalizedName = String(
    file?.name || ""
  )
    .trim()
    .toLowerCase();

  const size = Number(
    file?.size || 0
  );

  const lastModified = Number(
    file?.lastModified || 0
  );

  return base.findIndex((item) => (
    !item?.file &&
    String(item?.originalName || "")
      .trim()
      .toLowerCase() === normalizedName &&
    Number(item?.size || 0) === size &&
    (
      !Number(item?.lastModified || 0) ||
      Number(item?.lastModified || 0) === lastModified
    )
  ));
}

function fingerprintFromItem(item) {
  if (item?.file) {
    return uploadFingerprint(item.file);
  }

  return [
    String(item?.originalName || "")
      .trim()
      .toLowerCase(),
    Number(item?.size || 0),
    Number(item?.lastModified || 0),
  ].join("::");
}

function addFiles(files = []) {
  clearLocalMessage();

  if (!files.length) {
    setLocalMessage(
      "No se seleccionaron archivos.",
      "info"
    );

    return;
  }

  let base = props.multiple
    ? items.value.map((item) => ({
        ...item,
      }))
    : [];

  const fingerprints = new Set(
    base
      .filter((item) => item?.file)
      .map(fingerprintFromItem)
  );

  let added = 0;
  let invalid = 0;
  let duplicated = 0;
  let oversize = 0;
  let replacedRecovered = 0;
  let limitReached = false;

  for (const file of files) {
    if (!isPdfFile(file)) {
      invalid += 1;
      continue;
    }

    const recoveredIndex = findRecoveredMatchIndex(
      base,
      file
    );

    if (recoveredIndex !== -1) {
      const recoveredLimit = getLimitBytesForIndex(
        recoveredIndex
      );

      if (
        Number(file.size || 0) >
        recoveredLimit
      ) {
        oversize += 1;
        continue;
      }

      base[recoveredIndex] = {
        ...base[recoveredIndex],
        file,
        originalName:
          file.name ||
          base[recoveredIndex].originalName ||
          "",
        size: Number(file.size || 0),
        lastModified: Number(
          file.lastModified || 0
        ),
      };

      fingerprints.add(
        uploadFingerprint(file)
      );

      replacedRecovered += 1;

      if (!props.multiple) {
        break;
      }

      continue;
    }

    const fingerprint = uploadFingerprint(
      file
    );

    if (fingerprints.has(fingerprint)) {
      duplicated += 1;
      continue;
    }

    if (
      base.length >=
      effectiveMaxFiles.value
    ) {
      limitReached = true;
      break;
    }

    const targetIndex = props.multiple
      ? base.length
      : 0;

    const sizeLimit = getLimitBytesForIndex(
      targetIndex
    );

    if (
      Number(file.size || 0) >
      sizeLimit
    ) {
      oversize += 1;
      continue;
    }

    const uploadItem = buildUploadItem(
      file
    );

    if (!props.multiple) {
      base = [uploadItem];
      added += 1;
      fingerprints.add(fingerprint);
      break;
    }

    base.push(uploadItem);
    fingerprints.add(fingerprint);
    added += 1;
  }

  setItems(base);

  const parts = [];

  if (added) {
    parts.push(
      added === 1
        ? "1 archivo agregado"
        : `${added} archivos agregados`
    );
  }

  if (replacedRecovered) {
    parts.push(
      replacedRecovered === 1
        ? "1 archivo recuperado fue re-seleccionado"
        : `${replacedRecovered} archivos recuperados fueron re-seleccionados`
    );
  }

  if (duplicated) {
    parts.push(
      duplicated === 1
        ? "1 duplicado omitido"
        : `${duplicated} duplicados omitidos`
    );
  }

  if (invalid) {
    parts.push(
      invalid === 1
        ? "1 archivo inválido"
        : `${invalid} archivos inválidos`
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
      "se alcanzó el límite permitido"
    );
  }

  const hasErrors = Boolean(
    invalid ||
    oversize
  );

  const hasSuccess = Boolean(
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

function onDragStart(
  index,
  event
) {
  draggedIndex.value = index;
  dragOverIndex.value = index;

  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData(
      "text/plain",
      String(index)
    );
  }
}

function onDragEnd() {
  draggedIndex.value = null;
  dragOverIndex.value = null;
}

function onCardDragOver(
  index,
  event
) {
  if (draggedIndex.value == null) {
    return;
  }

  dragOverIndex.value = index;

  if (event?.dataTransfer) {
    event.dataTransfer.dropEffect = "move";
  }
}

function onCardDrop(index) {
  if (draggedIndex.value == null) {
    return;
  }

  if (draggedIndex.value === index) {
    onDragEnd();
    return;
  }

  const next = items.value.map((item) => ({
    ...item,
  }));

  const [moved] = next.splice(
    draggedIndex.value,
    1
  );

  next.splice(
    index,
    0,
    moved
  );

  if (!validateArrangement(next)) {
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
</script>

<style scoped src="./adjuntos-pdf.css"></style>
