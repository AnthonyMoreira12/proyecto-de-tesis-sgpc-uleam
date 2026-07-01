<template>
  <div class="sgpc-upload" :class="{ 'is-dragover': isDragOver }">
    <div class="sgpc-upload__head">
      <h4 class="sgpc-upload__title">{{ title }}</h4>
      <p class="sgpc-upload__desc">{{ description }}</p>
    </div>

    <div class="sgpc-upload__chips">
      <span class="sgpc-upload__chip">PDF</span>

      <span class="sgpc-upload__chip">
        {{ multiple ? "Múltiples archivos" : "Un solo archivo" }}
      </span>

      <span class="sgpc-upload__chip">
        {{ items.length }}/{{ maxFiles }}
      </span>

      <span v-if="usesPrimarySlot" class="sgpc-upload__chip">
        Principal: ≤ {{ primaryMaxSizeMb }} MB
      </span>

      <span class="sgpc-upload__chip">
        {{ usesPrimarySlot ? "Adjuntos" : "Cada PDF" }}: ≤ {{ attachmentMaxSizeMb }} MB
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
        class="sgpc-upload__native"
        type="file"
        accept="application/pdf,.pdf"
        :multiple="multiple"
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
          {{ multiple ? "Seleccionar uno o varios PDF" : "Seleccionar archivo PDF" }}
        </span>

        <span class="sgpc-upload__trigger-meta">
          {{ multiple ? "También puede arrastrar y soltar varios PDF" : "También puede arrastrar y soltar un PDF" }}
        </span>
      </span>
    </label>

    <div class="sgpc-upload__foot">
      <p class="sgpc-upload__hint">{{ helperText }}</p>

      <p v-if="hasRecoveredItems" class="sgpc-upload__warning">
        Se recuperaron referencias de archivos desde el borrador local.
        Debe volver a seleccionarlos antes de guardar o quitarlos de la lista.
      </p>

      <p
        v-if="localMessage"
        :class="['sgpc-alert', `is-${localMessageType}`]"
      >
        {{ localMessage }}
      </p>

      <p v-if="error" class="sgpc-upload__error">
        {{ error }}
      </p>
    </div>

    <div v-if="items.length" class="sgpc-file-list">
      <article
        v-for="(it, index) in items"
        :key="it.key"
        class="sgpc-file-chip"
        :class="{
          'sgpc-file-chip--cached': isRecovered(it),
          'sgpc-file-chip--warning': isOversize(it, index),
          'is-dragging': draggedIndex === index,
          'is-dragover': dragOverIndex === index && draggedIndex !== index
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
              :aria-label="`Arrastrar ${displayName(it)}`"
              title="Arrastrar para reordenar"
              @dragstart="onDragStart(index, $event)"
              @dragend="onDragEnd"
            >
              ⋮⋮
            </button>

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
                {{ displayName(it) }}
              </div>

              <div class="sgpc-file-chip__meta">
                Tamaño: {{ prettySize(it.file?.size || it.size || 0) }}
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
                  v-if="isRecovered(it)"
                  class="sgpc-file-chip__badge sgpc-file-chip__badge--draft"
                >
                  Re-seleccionar
                </span>

                <span
                  v-if="isOversize(it, index)"
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
              @click="moveUp(index)"
              :disabled="index === 0"
            >
              Subir
            </button>

            <button
              type="button"
              class="sgpc-btn"
              @click="moveDown(index)"
              :disabled="index === items.length - 1"
            >
              Bajar
            </button>

            <button
              type="button"
              class="sgpc-file-chip__remove"
              @click="removeItem(index)"
            >
              Quitar
            </button>
          </div>
        </div>

        <div class="sgpc-file-chip__form">
          <label class="sgpc-label" :for="`${inputId}-nombre-${index}`">
            Nombre personalizado
          </label>

          <input
            :id="`${inputId}-nombre-${index}`"
            class="sgpc-input"
            type="text"
            :value="it.nombre || ''"
            @input="updateName(index, $event.target.value)"
            placeholder="Ej. PDF principal / Carta de aceptación / Evidencia editorial / ..."
          />

          <p class="sgpc-hint">
            <template v-if="isRecovered(it)">
              Este elemento proviene del borrador local. Debe volver a seleccionarlo antes de enviarlo.
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
import { computed, ref } from "vue";
import {
  MAX_ATTACHMENT_PDF_FILE_SIZE,
  MAX_PRIMARY_PDF_FILE_SIZE,
  buildUploadItem,
  isPdfFile,
  makeUploadKey,
  uploadFingerprint,
} from "../../scripts/utils/adjuntosPdf";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  error: { type: String, default: "" },
  inputId: { type: String, required: true },
  title: { type: String, default: "Agregar archivos PDF" },
  description: { type: String, default: "Adjunte evidencias o soportes en PDF." },
  helperText: {
    type: String,
    default: "Formato permitido: PDF.",
  },
  multiple: { type: Boolean, default: true },
  maxFiles: { type: Number, default: 2 },

  usesPrimarySlot: { type: Boolean, default: false },
  primaryMaxSizeMb: {
    type: Number,
    default: Math.round(MAX_PRIMARY_PDF_FILE_SIZE / (1024 * 1024)),
  },
  attachmentMaxSizeMb: {
    type: Number,
    default: Math.round(MAX_ATTACHMENT_PDF_FILE_SIZE / (1024 * 1024)),
  },
});

const emit = defineEmits(["update:modelValue"]);

const isDragOver = ref(false);
const localMessage = ref("");
const localMessageType = ref("info");

const draggedIndex = ref(null);
const dragOverIndex = ref(null);

const bytesPerMb = 1024 * 1024;

const primaryMaxBytes = computed(() =>
  Math.max(1, Number(props.primaryMaxSizeMb || 5)) * bytesPerMb
);

const attachmentMaxBytes = computed(() =>
  Math.max(1, Number(props.attachmentMaxSizeMb || 3)) * bytesPerMb
);

const items = computed(() =>
  (Array.isArray(props.modelValue) ? props.modelValue : []).map((it) => ({
    key: it?.key || makeUploadKey(),
    file: it?.file || null,
    nombre: it?.nombre || "",
    originalName: it?.originalName || it?.file?.name || "",
    size: Number(it?.size || it?.file?.size || 0),
    lastModified: Number(it?.lastModified || it?.file?.lastModified || 0),
  }))
);

const hasRecoveredItems = computed(() =>
  items.value.some((it) => isRecovered(it))
);

function setItems(next) {
  emit("update:modelValue", next);
}

function prettySize(bytes) {
  const n = Number(bytes || 0);
  if (n <= 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let v = n;

  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }

  return `${v.toFixed(i === 0 ? 0 : 2)} ${units[i]}`;
}

function displayName(item) {
  return item?.file?.name || item?.originalName || "Archivo PDF";
}

function isRecovered(item) {
  return !item?.file && !!item?.originalName;
}

function getLimitBytesForIndex(index) {
  if (props.usesPrimarySlot && index === 0) {
    return primaryMaxBytes.value;
  }

  return attachmentMaxBytes.value;
}

function getLimitLabelForIndex(index) {
  if (props.usesPrimarySlot && index === 0) {
    return `PDF principal (máximo ${props.primaryMaxSizeMb} MB)`;
  }

  return `adjunto PDF (máximo ${props.attachmentMaxSizeMb} MB)`;
}

function isOversize(item, index) {
  const size = Number(item?.file?.size || item?.size || 0);
  return size > getLimitBytesForIndex(index);
}

function updateName(index, value) {
  const next = items.value.map((it) => ({ ...it }));
  next[index].nombre = String(value || "").trimStart();
  setItems(next);
}

function removeItem(index) {
  const next = items.value.map((it) => ({ ...it }));
  next.splice(index, 1);
  setItems(next);
  localMessage.value = "Archivo eliminado.";
  localMessageType.value = "info";
}

function validateArrangement(candidate) {
  for (let i = 0; i < candidate.length; i += 1) {
    const fileSize = Number(candidate[i]?.file?.size || candidate[i]?.size || 0);
    const limit = getLimitBytesForIndex(i);

    if (fileSize > limit) {
      localMessage.value = `El archivo "${displayName(candidate[i])}" supera el límite permitido para la posición ${i + 1}.`;
      localMessageType.value = "error";
      return false;
    }
  }

  return true;
}

function moveUp(index) {
  if (index <= 0) return;

  const next = items.value.map((it) => ({ ...it }));
  [next[index - 1], next[index]] = [next[index], next[index - 1]];

  if (!validateArrangement(next)) return;

  setItems(next);
}

function moveDown(index) {
  if (index >= items.value.length - 1) return;

  const next = items.value.map((it) => ({ ...it }));
  [next[index + 1], next[index]] = [next[index], next[index + 1]];

  if (!validateArrangement(next)) return;

  setItems(next);
}

function onInputChange(e) {
  const files = Array.from(e?.target?.files || []);
  e.target.value = "";
  addFiles(files);
}

function onDragOver(e) {
  isDragOver.value = true;
  if (e?.dataTransfer) e.dataTransfer.dropEffect = "copy";
}

function onDragLeave(e) {
  const current = e.currentTarget;
  const related = e.relatedTarget;
  if (current && related && current.contains?.(related)) return;
  isDragOver.value = false;
}

function onDrop(e) {
  isDragOver.value = false;
  const files = Array.from(e?.dataTransfer?.files || []);
  addFiles(files);
}

function findRecoveredMatchIndex(base, file) {
  const normalizedName = String(file?.name || "").trim().toLowerCase();
  const size = Number(file?.size || 0);
  const lastModified = Number(file?.lastModified || 0);

  return base.findIndex(
    (it) =>
      !it?.file &&
      String(it?.originalName || "").trim().toLowerCase() === normalizedName &&
      Number(it?.size || 0) === size &&
      (!Number(it?.lastModified || 0) ||
        Number(it?.lastModified || 0) === lastModified)
  );
}

function addFiles(files = []) {
  let base = props.multiple
    ? items.value.map((it) => ({ ...it }))
    : [];

  let added = 0;
  let invalid = 0;
  let duplicated = 0;
  let oversize = 0;
  let limitReached = false;
  let replacedRecovered = 0;

  for (const file of files) {
    if (!isPdfFile(file)) {
      invalid += 1;
      continue;
    }

    const recoveredIndex = findRecoveredMatchIndex(base, file);
    if (recoveredIndex !== -1) {
      const recoveredLimit = getLimitBytesForIndex(recoveredIndex);

      if (Number(file.size || 0) > recoveredLimit) {
        oversize += 1;
        continue;
      }

      base[recoveredIndex] = {
        ...base[recoveredIndex],
        file,
        originalName: file.name || base[recoveredIndex].originalName || "",
        size: Number(file.size || 0),
        lastModified: Number(file.lastModified || 0),
      };

      replacedRecovered += 1;
      continue;
    }

    const attachedFingerprints = new Set(
      base.filter((it) => it?.file).map((it) => uploadFingerprint(it))
    );

    const fp = uploadFingerprint(file);
    if (attachedFingerprints.has(fp)) {
      duplicated += 1;
      continue;
    }

    if (base.length >= props.maxFiles) {
      limitReached = true;
      break;
    }

    const targetIndex = props.multiple ? base.length : 0;
    const sizeLimit = getLimitBytesForIndex(targetIndex);

    if (Number(file.size || 0) > sizeLimit) {
      oversize += 1;
      continue;
    }

    if (!props.multiple) {
      base = [buildUploadItem(file)];
      added += 1;
      continue;
    }

    base.push(buildUploadItem(file));
    added += 1;
  }

  setItems(base);

  const parts = [];
  if (added) parts.push(added === 1 ? "1 archivo agregado" : `${added} archivos agregados`);
  if (replacedRecovered) {
    parts.push(
      replacedRecovered === 1
        ? "1 archivo recuperado fue re-seleccionado"
        : `${replacedRecovered} archivos recuperados fueron re-seleccionados`
    );
  }
  if (duplicated) parts.push(duplicated === 1 ? "1 duplicado omitido" : `${duplicated} duplicados omitidos`);
  if (invalid) parts.push(invalid === 1 ? "1 archivo inválido" : `${invalid} archivos inválidos`);
  if (oversize) {
    parts.push(
      oversize === 1
        ? "1 archivo supera el límite de tamaño"
        : `${oversize} archivos superan el límite de tamaño`
    );
  }
  if (limitReached) parts.push("se alcanzó el límite permitido");

  localMessage.value = parts.join(" · ") || "Sin cambios.";
  localMessageType.value = invalid || oversize ? "error" : added || replacedRecovered ? "success" : "info";
}

function onDragStart(index, event) {
  draggedIndex.value = index;
  dragOverIndex.value = index;

  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", String(index));
  }
}

function onDragEnd() {
  draggedIndex.value = null;
  dragOverIndex.value = null;
}

function onCardDragOver(index, event) {
  if (draggedIndex.value == null) return;
  dragOverIndex.value = index;
  if (event?.dataTransfer) event.dataTransfer.dropEffect = "move";
}

function onCardDrop(index) {
  if (draggedIndex.value == null) return;

  if (draggedIndex.value === index) {
    onDragEnd();
    return;
  }

  const next = items.value.map((it) => ({ ...it }));
  const [moved] = next.splice(draggedIndex.value, 1);
  next.splice(index, 0, moved);

  if (!validateArrangement(next)) {
    onDragEnd();
    return;
  }

  setItems(next);
  onDragEnd();

  localMessage.value = "Orden de archivos actualizado.";
  localMessageType.value = "info";
}
</script>