<template>
  <div
    class="pedit"
    :class="{ 'is-saving': savingLocal }"
  >
    <!-- =====================================================
      MENSAJES
    ====================================================== -->
    <p
      v-if="editMsg"
      :class="['pedit-msg', `is-${editMsgType || 'info'}`]"
      role="status"
      aria-live="polite"
    >
      {{ editMsg }}
    </p>

    <!-- =====================================================
      DATOS GENERALES
    ====================================================== -->
    <section class="pedit-section">
      <header class="pedit-section__head">
        <div class="pedit-section__copy">
          <span class="pedit-section__eyebrow">
            Clasificación institucional
          </span>

          <h2 class="pedit-section__title">
            Datos generales
          </h2>

          <p class="pedit-section__text">
            Actualice la adscripción académica y el proyecto relacionado con
            esta publicación.
          </p>
        </div>

        <div class="pedit-section__meta">
          <span class="pedit-chip">
            {{ tipoLabel }}
          </span>

          <span
            v-if="isAdmin"
            class="pedit-chip pedit-chip--permission"
          >
            Administrador
          </span>

          <span
            v-else-if="canEdit"
            class="pedit-chip pedit-chip--permission"
          >
            Autor vinculado
          </span>
        </div>
      </header>

      <div class="pedit-embed pedit-embed--general">
        <DatosGenerales
          v-model="form.datos_generales"
          :hideUbicacion="!isPonencia"
          :proyectoOpcional="isArticulo || isPonencia"
        />
      </div>
    </section>

    <!-- =====================================================
      INFORMACIÓN GENERAL
    ====================================================== -->
    <section class="pedit-section">
      <header class="pedit-section__head">
        <div class="pedit-section__copy">
          <span class="pedit-section__eyebrow">
            Información temporal
          </span>

          <h2 class="pedit-section__title">
            Información general
          </h2>

          <p class="pedit-section__text">
            Registre la fecha oficial asociada a la publicación.
          </p>
        </div>
      </header>

      <div class="pedit-formGrid">
        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-fecha-publicacion"
          >
            Fecha de publicación
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-fecha-publicacion"
            v-model="form.fecha_publicacion"
            class="pedit-input"
            type="date"
            required
            :disabled="savingLocal || removingPdf"
          />

          <p
            v-if="form.fecha_publicacion"
            class="pedit-help"
          >
            Fecha seleccionada:
            <strong>{{ formatFecha(form.fecha_publicacion) }}</strong>
          </p>
        </div>
      </div>
    </section>

    <!-- =====================================================
      CAMPOS ESPECÍFICOS
    ====================================================== -->
    <section class="pedit-section">
      <header class="pedit-section__head">
        <div class="pedit-section__copy">
          <span class="pedit-section__eyebrow">
            Metadatos especializados
          </span>

          <h2 class="pedit-section__title">
            Campos específicos
          </h2>

          <p class="pedit-section__text">
            Complete la información correspondiente al tipo de publicación.
          </p>
        </div>

        <div class="pedit-section__meta">
          <span class="pedit-chip pedit-chip--type">
            {{ tipoLabel }}
          </span>
        </div>
      </header>

      <!-- Ponencia -->
      <div
        v-if="isPonencia"
        class="pedit-formGrid"
      >
        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-evento"
          >
            Evento
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-evento"
            v-model.trim="form.nombre_evento"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-ponencia"
          >
            Ponencia
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-ponencia"
            v-model.trim="form.nombre_ponencia"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field pedit-field--full">
          <label
            class="pedit-label"
            for="pedit-issn-isbn"
          >
            ISSN o ISBN
          </label>

          <input
            id="pedit-issn-isbn"
            v-model.trim="form.codigo_issn_isbn"
            class="pedit-input"
            type="text"
            :disabled="savingLocal || removingPdf"
          />
        </div>
      </div>

      <!-- Artículo -->
      <div
        v-else-if="isArticulo"
        class="pedit-formGrid"
      >
        <div class="pedit-field pedit-field--full">
          <label
            class="pedit-label"
            for="pedit-nombre-articulo"
          >
            Nombre del artículo
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-nombre-articulo"
            v-model.trim="form.nombre_articulo"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-indexacion"
          >
            Base de datos o indexación
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-indexacion"
            v-model.trim="form.base_datos_indexada"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-revista"
          >
            Nombre de la revista
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-revista"
            v-model.trim="form.nombre_revista"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-doi"
          >
            DOI
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-doi"
            v-model.trim="form.codigo_doi"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-issn"
          >
            ISSN
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-issn"
            v-model.trim="form.codigo_issn"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field pedit-field--full">
          <label
            class="pedit-label"
            for="pedit-link-publicacion"
          >
            Enlace de la publicación
          </label>

          <input
            id="pedit-link-publicacion"
            v-model.trim="form.link_publicacion"
            class="pedit-input"
            type="url"
            placeholder="https://..."
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <template v-if="!isArticuloRegional">
          <div class="pedit-field pedit-field--full">
            <label
              class="pedit-label"
              for="pedit-link-revista"
            >
              Enlace de la revista
            </label>

            <input
              id="pedit-link-revista"
              v-model.trim="form.link_revista"
              class="pedit-input"
              type="url"
              placeholder="https://..."
              :disabled="savingLocal || removingPdf"
            />
          </div>

          <template v-if="isAdmin">
            <div class="pedit-field">
              <label
                class="pedit-label"
                for="pedit-factor-impacto"
              >
                Factor de impacto
              </label>

              <input
                id="pedit-factor-impacto"
                v-model.trim="form.factor_impacto"
                class="pedit-input"
                type="text"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pedit-field">
              <label
                class="pedit-label"
                for="pedit-cuartil"
              >
                Cuartil
              </label>

              <input
                id="pedit-cuartil"
                v-model.trim="form.cuartil"
                class="pedit-input"
                type="text"
                placeholder="Ejemplo: Q1 o Q2"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pedit-field">
              <label
                class="pedit-label"
                for="pedit-sjr"
              >
                SJR
              </label>

              <input
                id="pedit-sjr"
                v-model.trim="form.sjr"
                class="pedit-input"
                type="text"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pedit-field">
              <label
                class="pedit-label"
                for="pedit-numero-revista"
              >
                Número de revista
              </label>

              <input
                id="pedit-numero-revista"
                v-model.trim="form.numero_revista"
                class="pedit-input"
                type="text"
                :disabled="savingLocal || removingPdf"
              />
            </div>
          </template>
        </template>

        <div
          v-if="isArticuloRegional"
          class="pedit-inlineNote"
        >
          Los indicadores avanzados de impacto, cuartil, SJR y número de revista
          no se aplican a los artículos regionales.
        </div>
      </div>

      <!-- Capítulo -->
      <div
        v-else-if="isCapitulo"
        class="pedit-formGrid"
      >
        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-nombre-capitulo"
          >
            Nombre del capítulo
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-nombre-capitulo"
            v-model.trim="form.nombre_capitulo"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-nombre-libro"
          >
            Nombre del libro
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-nombre-libro"
            v-model.trim="form.nombre_libro"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-isbn"
          >
            ISBN
            <span class="pedit-required">*</span>
          </label>

          <input
            id="pedit-isbn"
            v-model.trim="form.codigo_isbn"
            class="pedit-input"
            type="text"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field">
          <label
            class="pedit-label"
            for="pedit-editor"
          >
            Editor o compilador
          </label>

          <input
            id="pedit-editor"
            v-model.trim="form.editor_compilador"
            class="pedit-input"
            type="text"
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pedit-field pedit-field--full">
          <label
            class="pedit-label"
            for="pedit-link-capitulo"
          >
            Enlace del capítulo
          </label>

          <input
            id="pedit-link-capitulo"
            v-model.trim="form.link_capitulo"
            class="pedit-input"
            type="url"
            placeholder="https://..."
            :disabled="savingLocal || removingPdf"
          />
        </div>
      </div>

      <div
        v-else
        class="pedit-empty"
      >
        No existen campos específicos editables para este tipo de publicación.
      </div>
    </section>

    <!-- =====================================================
      AUTORES
    ====================================================== -->
    <section class="pedit-section">
      <header class="pedit-section__head">
        <div class="pedit-section__copy">
          <span class="pedit-section__eyebrow">
            Participación académica
          </span>

          <h2 class="pedit-section__title">
            Autores
          </h2>

          <p class="pedit-section__text">
            Organice el autor principal y los coautores vinculados al registro.
          </p>
        </div>

        <div class="pedit-section__meta">
          <span class="pedit-chip">
            {{ form.autores.length }}
            {{ form.autores.length === 1 ? "autor" : "autores" }}
          </span>
        </div>
      </header>

      <div class="pedit-embed pedit-embed--authors">
        <AutoresSelector v-model="form.autores" />
      </div>
    </section>

    <!-- =====================================================
      ARCHIVO PDF
    ====================================================== -->
    <section class="pedit-section">
      <header class="pedit-section__head">
        <div class="pedit-section__copy">
          <span class="pedit-section__eyebrow">
            Evidencia documental
          </span>

          <h2 class="pedit-section__title">
            Archivo PDF
          </h2>

          <p class="pedit-section__text">
            Consulte, descargue, reemplace o quite el documento principal de la
            publicación.
          </p>
        </div>

        <div class="pedit-section__meta">
          <span
            class="pedit-chip"
            :class="{
              'pedit-chip--available': hasCurrentPdf,
            }"
          >
            {{ hasCurrentPdf ? "PDF disponible" : "Sin PDF" }}
          </span>
        </div>
      </header>

      <div
        v-if="hasCurrentPdf"
        class="pedit-filePanel"
      >
        <div
          class="pedit-filePanel__icon"
          aria-hidden="true"
        >
          PDF
        </div>

        <div class="pedit-filePanel__meta">
          <span class="pedit-filePanel__eyebrow">
            Documento actual
          </span>

          <h3 class="pedit-filePanel__name">
            {{ currentPdfName }}
          </h3>

          <p class="pedit-filePanel__text">
            Puede conservar este archivo, descargarlo o reemplazarlo al guardar
            los cambios.
          </p>
        </div>

        <div class="pedit-filePanel__actions">
          <button
            class="pedit-btn pedit-btn--ghost"
            type="button"
            :disabled="savingLocal || removingPdf"
            @click="openCurrentPdf"
          >
            Ver PDF
          </button>

          <button
            class="pedit-btn pedit-btn--ghost"
            type="button"
            :disabled="savingLocal || removingPdf"
            @click="downloadCurrentPdf"
          >
            Descargar
          </button>

          <button
            v-if="canEdit"
            class="pedit-btn pedit-btn--danger"
            type="button"
            :disabled="savingLocal || removingPdf"
            @click="requestRemovePdf"
          >
            {{ removingPdf ? "Quitando..." : "Quitar PDF" }}
          </button>
        </div>
      </div>

      <div class="pedit-uploader">
        <AdjuntosPdfUploader
          v-model="pdfUploadItems"
          :error="fileError"
          input-id="pub-edit-archivo-pdf"
          title="Actualizar archivo PDF"
          description="Seleccione el PDF principal del registro. Si carga uno nuevo, reemplazará el archivo actual al guardar."
          helper-text="Formato permitido: PDF. Puede arrastrar y soltar un solo archivo."
          :multiple="false"
          :max-files="1"
        />
      </div>
    </section>

    <!-- =====================================================
      ACCIONES
    ====================================================== -->
    <footer
      class="pedit-footer"
      role="group"
      aria-label="Acciones de edición"
    >
      <div class="pedit-footer__copy">
        <strong>Edición de publicación</strong>

        <span>
          Revise los datos antes de guardar los cambios.
        </span>
      </div>

      <div class="pedit-footer__actions">
        <button
          class="pedit-btn pedit-btn--ghost"
          type="button"
          :disabled="savingLocal || removingPdf"
          @click="$emit('cancel')"
        >
          Volver al detalle
        </button>

        <button
          class="pedit-btn pedit-btn--primary"
          type="button"
          :disabled="savingLocal || removingPdf"
          @click="guardar"
        >
          {{ savingLocal ? "Guardando..." : "Guardar cambios" }}
        </button>
      </div>
    </footer>
  </div>

  <!-- =======================================================
    MODAL PARA QUITAR PDF
  ======================================================== -->
  <Teleport to="body">
    <div
      v-if="showRemovePdfModal"
      class="pedit-modalOverlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="pedit-remove-pdf-title"
      @click.self="cancelRemovePdf"
    >
      <section class="pedit-modal">
        <div
          class="pedit-modal__icon"
          aria-hidden="true"
        >
          PDF
        </div>

        <div class="pedit-modal__body">
          <span class="pedit-modal__eyebrow">
            Confirmación requerida
          </span>

          <h2
            id="pedit-remove-pdf-title"
            class="pedit-modal__title"
          >
            Quitar archivo PDF
          </h2>

          <p class="pedit-modal__text">
            Esta acción eliminará el documento actual asociado al registro
            académico.
          </p>

          <p class="pedit-modal__warning">
            Descargue una copia antes de continuar cuando necesite conservar el
            archivo.
          </p>
        </div>

        <div class="pedit-modal__actions">
          <button
            class="pedit-btn pedit-btn--ghost"
            type="button"
            :disabled="removingPdf"
            @click="cancelRemovePdf"
          >
            Cancelar
          </button>

          <button
            class="pedit-btn pedit-btn--danger"
            type="button"
            :disabled="removingPdf"
            @click="removeCurrentPdf"
          >
            {{ removingPdf ? "Quitando..." : "Sí, quitar PDF" }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import {
  computed,
  reactive,
  ref,
  watch,
} from "vue";
import { useRoute } from "vue-router";

import api from "../../scripts/api/axios";

import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";

/* ============================================================
  PROPIEDADES Y EVENTOS
============================================================ */

const props = defineProps({
  detalle: {
    type: Object,
    required: true,
  },

  saving: {
    type: Boolean,
    default: false,
  },

  canEdit: {
    type: Boolean,
    default: false,
  },

  isAdmin: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "saving",
  "updated",
  "cancel",
]);

const route = useRoute();

/* ============================================================
  ESTADOS
============================================================ */

const editMsg = ref("");
const editMsgType = ref("");

const fileError = ref("");
const pdfUploadItems = ref([]);

const removingPdf = ref(false);
const showRemovePdfModal = ref(false);

const preserveFeedbackOnNextDetalle = ref(false);

/* ============================================================
  PROPIEDADES COMPUTADAS
============================================================ */

const savingLocal = computed({
  get: () => props.saving,

  set: (value) => {
    emit("saving", Boolean(value));
  },
});

const canEdit = computed(() => {
  return Boolean(props.canEdit);
});

const isAdmin = computed(() => {
  return Boolean(props.isAdmin);
});

/* ============================================================
  HELPERS
============================================================ */

const firstFilled = (...values) => {
  return (
    values
      .map((value) => {
        return value == null
          ? ""
          : String(value).trim();
      })
      .find(Boolean) || ""
  );
};

const normalizeText = (value) => {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
};

const currentId = computed(() => {
  return firstFilled(
    route.params.id,
    props.detalle?.id
  );
});

const tipoLabel = computed(() => {
  return firstFilled(
    props.detalle?.tipo,
    props.detalle?.tipo_publicacion_final_label,
    props.detalle?.tipo_publicacion_final,
    "Publicación"
  );
});

const tipoStr = computed(() => {
  return String(
    props.detalle?.tipo ||
      props.detalle?.tipo_publicacion_final_label ||
      props.detalle?.tipo_publicacion_final ||
      ""
  );
});

const tipoCodigo = computed(() => {
  return String(
    props.detalle?.tipo_codigo ||
      props.detalle?.tipoCodigo ||
      props.detalle?.tipo_publicacion_final ||
      ""
  );
});

const tipoNormalized = computed(() => {
  return normalizeText(tipoStr.value);
});

const isPonencia = computed(() => {
  return tipoNormalized.value.includes("ponencia");
});

const isArticulo = computed(() => {
  return tipoNormalized.value.includes("articulo");
});

const isCapitulo = computed(() => {
  return tipoNormalized.value.includes("capitulo");
});

const isArticuloRegional = computed(() => {
  const normalizedCode = normalizeText(
    tipoCodigo.value
  );

  if (normalizedCode) {
    return [
      "articulo regional",
      "articulo_regional",
      "ar",
    ].includes(normalizedCode);
  }

  return tipoNormalized.value.includes("regional");
});

/* ============================================================
  FECHA
============================================================ */

const formatFecha = (value) => {
  const fecha = String(value || "").trim();

  if (!fecha) {
    return "";
  }

  try {
    if (/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [year, month, day] = fecha
        .split("-")
        .map(Number);

      const localDate = new Date(
        year,
        month - 1,
        day
      );

      return localDate.toLocaleDateString(
        "es-EC",
        {
          day: "2-digit",
          month: "long",
          year: "numeric",
        }
      );
    }

    const parsed = new Date(fecha);

    if (Number.isNaN(parsed.getTime())) {
      return fecha;
    }

    return parsed.toLocaleDateString(
      "es-EC",
      {
        day: "2-digit",
        month: "long",
        year: "numeric",
      }
    );
  } catch {
    return fecha;
  }
};

/* ============================================================
  ARCHIVO PDF ACTUAL
============================================================ */

const fileNameFromValue = (value) => {
  const raw = String(value || "").trim();

  if (!raw) {
    return "archivo.pdf";
  }

  try {
    const parsed = new URL(
      raw,
      window.location.origin
    );

    const last = parsed.pathname
      .split("/")
      .filter(Boolean)
      .pop();

    return decodeURIComponent(
      last || "archivo.pdf"
    );
  } catch {
    return (
      raw
        .split("/")
        .filter(Boolean)
        .pop() ||
      "archivo.pdf"
    );
  }
};

const getBackendBase = () => {
  const environmentBase =
    firstFilled(
      import.meta.env.VITE_API_URL,
      import.meta.env.VITE_API_BASE_URL,
      import.meta.env.VITE_AXIOS_BASE_URL
    ) || "";

  const axiosBase = firstFilled(
    api?.defaults?.baseURL
  );

  const base =
    environmentBase ||
    axiosBase;

  if (/^https?:\/\//i.test(base)) {
    return base
      .replace(/\/api\/?$/i, "")
      .replace(/\/$/, "");
  }

  return window.location.origin;
};

const resolveFileUrl = (value) => {
  const raw = String(value || "").trim();

  if (!raw) {
    return "";
  }

  if (/^https?:\/\//i.test(raw)) {
    return raw;
  }

  if (
    raw.startsWith("blob:") ||
    raw.startsWith("data:")
  ) {
    return raw;
  }

  const base = getBackendBase();

  const clean = raw.startsWith("/")
    ? raw
    : `/${raw.replace(/^\.?\//, "")}`;

  return `${base}${clean}`;
};

const currentPdfValue = computed(() => {
  return firstFilled(
    props.detalle?.archivo_pdf_url,
    props.detalle?.pdf_url,
    props.detalle?.archivo_pdf,
    props.detalle?.pdf,
    props.detalle?.archivo,
    props.detalle?.archivos?.[0]?.url,
    props.detalle?.archivos?.[0]?.archivo,
    props.detalle?.archivos?.[0]?.archivo_url,
    props.detalle?.adjuntos?.[0]?.url,
    props.detalle?.adjuntos?.[0]?.archivo,
    props.detalle?.adjuntos?.[0]?.archivo_url
  );
});

const hasPdfInPayload = (payload = {}) => {
  if (
    !payload ||
    typeof payload !== "object"
  ) {
    return false;
  }

  return Boolean(
    payload.tiene_pdf ||
      payload.has_pdf ||
      payload.tienePdf ||
      payload.hasPdf ||
      payload.archivo_pdf_url ||
      payload.pdf_url ||
      payload.archivo_pdf ||
      payload.pdf ||
      payload.archivo ||
      payload.archivos?.length ||
      payload.adjuntos?.length
  );
};

const currentPdfHref = computed(() => {
  return resolveFileUrl(
    currentPdfValue.value
  );
});

const hasCurrentPdf = computed(() => {
  return Boolean(
    currentPdfHref.value ||
      hasPdfInPayload(
        props.detalle || {}
      )
  );
});

const currentPdfName = computed(() => {
  const name = fileNameFromValue(
    currentPdfValue.value
  );

  return name && name !== "archivo.pdf"
    ? name
    : "publicacion.pdf";
});

const selectedPdfItem = computed(() => {
  const items = Array.isArray(
    pdfUploadItems.value
  )
    ? pdfUploadItems.value
    : [];

  return (
    items.find((item) => item?.file) ||
    null
  );
});

/* ============================================================
  FORMULARIO
============================================================ */

const form = reactive({
  tipo: "",
  fecha_publicacion: "",

  datos_generales: {
    facultad: null,
    carrera: null,
    proyecto: null,
    area: null,
    subarea: null,
    pais: null,
    ciudad: null,
  },

  nombre_articulo: "",
  base_datos_indexada: "",
  codigo_doi: "",
  codigo_issn: "",
  nombre_revista: "",
  numero_revista: "",
  link_publicacion: "",
  link_revista: "",
  factor_impacto: "",
  cuartil: "",
  sjr: "",

  nombre_evento: "",
  nombre_ponencia: "",
  codigo_issn_isbn: "",

  nombre_capitulo: "",
  nombre_libro: "",
  codigo_isbn: "",
  editor_compilador: "",
  link_capitulo: "",

  autores: [],
});

/* ============================================================
  NORMALIZACIÓN DE AUTORES
============================================================ */

const normalizeAutoresForSelector = (authors) => {
  const base = Array.isArray(authors)
    ? authors
    : [];

  return base
    .map((autor, index) => {
      const autorId =
        autor?.autor_id ??
        autor?.id ??
        autor?.autor?.id ??
        null;

      if (!autorId) {
        return null;
      }

      return {
        autor_id: Number(autorId),

        orden:
          autor?.orden ??
          index + 1,

        rol_autoria:
          autor?.rol_autoria ??
          (index === 0
            ? "principal"
            : "coautor"),

        nombre_completo:
          autor?.nombre_completo ||
          autor?.nombre ||
          "",
      };
    })
    .filter(Boolean)
    .map((item, index) => ({
      ...item,

      orden: index + 1,

      rol_autoria:
        index === 0
          ? "principal"
          : "coautor",
    }));
};

/* ============================================================
  CARGA DEL DETALLE EN EL FORMULARIO
============================================================ */

const mapDetalleToForm = (detalle) => {
  form.tipo =
    detalle?.tipo ||
    "";

  form.fecha_publicacion = String(
    detalle?.fecha_publicacion || ""
  ).substring(0, 10);

  form.datos_generales = {
    facultad:
      detalle?.facultad_id ??
      null,

    carrera:
      detalle?.carrera_id ??
      null,

    proyecto:
      detalle?.proyecto_id ??
      null,

    area:
      detalle?.area_id ??
      null,

    subarea:
      detalle?.subarea_id ??
      null,

    pais:
      detalle?.pais_id ??
      null,

    ciudad:
      detalle?.ciudad_id ??
      null,
  };

  form.autores =
    normalizeAutoresForSelector(
      detalle?.autores
    );

  form.nombre_evento =
    detalle?.nombre_evento || "";

  form.nombre_ponencia =
    detalle?.nombre_ponencia || "";

  form.codigo_issn_isbn =
    detalle?.codigo_issn_isbn || "";

  form.nombre_articulo =
    detalle?.nombre_articulo || "";

  form.base_datos_indexada =
    detalle?.base_datos_indexada || "";

  form.codigo_doi =
    detalle?.codigo_doi || "";

  form.codigo_issn =
    detalle?.codigo_issn || "";

  form.nombre_revista =
    detalle?.nombre_revista || "";

  form.numero_revista =
    detalle?.numero_revista || "";

  form.link_publicacion =
    detalle?.link_publicacion || "";

  form.link_revista =
    detalle?.link_revista || "";

  form.factor_impacto =
    detalle?.factor_impacto || "";

  form.cuartil =
    detalle?.cuartil || "";

  form.sjr =
    detalle?.sjr || "";

  form.nombre_capitulo =
    detalle?.nombre_capitulo || "";

  form.nombre_libro =
    detalle?.nombre_libro || "";

  form.codigo_isbn =
    detalle?.codigo_isbn || "";

  form.editor_compilador =
    detalle?.editor_compilador || "";

  form.link_capitulo =
    detalle?.link_capitulo || "";

  if (isArticuloRegional.value) {
    form.factor_impacto = "";
    form.cuartil = "";
    form.sjr = "";
    form.numero_revista = "";
  }
};

watch(
  () => props.detalle,
  (detalle) => {
    if (!detalle) {
      return;
    }

    pdfUploadItems.value = [];
    fileError.value = "";

    if (
      preserveFeedbackOnNextDetalle.value
    ) {
      preserveFeedbackOnNextDetalle.value =
        false;
    } else {
      editMsg.value = "";
      editMsgType.value = "";
    }

    mapDetalleToForm(detalle);
  },
  {
    immediate: true,
  }
);

/* ============================================================
  ERRORES
============================================================ */

const prettyError = (value) => {
  if (value == null) {
    return "";
  }

  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    return value
      .map(prettyError)
      .join(", ");
  }

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, nested]) => {
        return `${key}: ${prettyError(nested)}`;
      })
      .join(" | ");
  }

  return String(value);
};

/* ============================================================
  PAYLOAD DE AUTORES
============================================================ */

const buildAutoresPayload = () => {
  const raw = Array.isArray(form.autores)
    ? [...form.autores]
    : [];

  return raw
    .map((autor, index) => {
      const autorId =
        autor?.autor_id ??
        autor?.id ??
        autor?.autor?.id ??
        null;

      const numericId = Number(autorId);

      if (
        !Number.isFinite(numericId) ||
        numericId <= 0
      ) {
        return null;
      }

      const orden = index + 1;

      return {
        autor_id: numericId,
        orden,

        rol_autoria:
          orden === 1
            ? "principal"
            : "coautor",
      };
    })
    .filter(Boolean);
};

/* ============================================================
  CAMPOS PERMITIDOS
============================================================ */

const allowedSpecificFields = computed(() => {
  if (isPonencia.value) {
    return [
      "nombre_evento",
      "nombre_ponencia",
      "codigo_issn_isbn",
    ];
  }

  if (isCapitulo.value) {
    return [
      "nombre_capitulo",
      "nombre_libro",
      "codigo_isbn",
      "editor_compilador",
      "link_capitulo",
    ];
  }

  if (isArticulo.value) {
    const base = [
      "nombre_articulo",
      "base_datos_indexada",
      "codigo_doi",
      "codigo_issn",
      "nombre_revista",
      "link_publicacion",
    ];

    if (isArticuloRegional.value) {
      return base;
    }

    const extras = [
      "link_revista",
    ];

    if (isAdmin.value) {
      extras.push(
        "numero_revista",
        "factor_impacto",
        "cuartil",
        "sjr"
      );
    }

    return [
      ...base,
      ...extras,
    ];
  }

  return [];
});

/* ============================================================
  FORMDATA
============================================================ */

const buildFormDataPayload = () => {
  const formData = new FormData();

  Object.entries(
    form.datos_generales || {}
  ).forEach(([key, value]) => {
    if (
      !isPonencia.value &&
      (
        key === "pais" ||
        key === "ciudad"
      )
    ) {
      return;
    }

    if (
      key === "proyecto" &&
      (
        value === "0" ||
        !value
      )
    ) {
      return;
    }

    if (
      value !== null &&
      value !== "" &&
      value !== undefined
    ) {
      formData.append(key, value);
    }
  });

  if (form.fecha_publicacion) {
    formData.append(
      "fecha_publicacion",
      form.fecha_publicacion
    );
  }

  allowedSpecificFields.value.forEach(
    (key) => {
      const value = form[key];

      if (
        value !== null &&
        value !== "" &&
        value !== undefined
      ) {
        formData.append(key, value);
      }
    }
  );

  formData.set(
    "autores",
    JSON.stringify(
      buildAutoresPayload()
    )
  );

  if (selectedPdfItem.value?.file) {
    formData.append(
      "archivo_pdf",
      selectedPdfItem.value.file
    );
  }

  return formData;
};

/* ============================================================
  VALIDACIÓN
============================================================ */

const validarEdicion = () => {
  const autores = buildAutoresPayload();

  if (!autores.length) {
    return "Debe registrar al menos un autor.";
  }

  const datosGenerales =
    form.datos_generales || {};

  const requiredFields = [
    "facultad",
    "carrera",
    "area",
    "subarea",
  ];

  if (
    !isArticulo.value &&
    !isPonencia.value
  ) {
    requiredFields.push("proyecto");
  }

  const missingFields =
    requiredFields.filter((key) => {
      return (
        !datosGenerales[key] ||
        datosGenerales[key] === "0"
      );
    });

  if (missingFields.length) {
    return (
      "Complete todos los campos obligatorios " +
      "de la clasificación institucional."
    );
  }

  if (
    isPonencia.value &&
    (
      !datosGenerales.pais ||
      !datosGenerales.ciudad
    )
  ) {
    return (
      "Debe indicar el país y la ciudad " +
      "de la ponencia."
    );
  }

  if (!form.fecha_publicacion) {
    return (
      "La fecha de publicación es obligatoria."
    );
  }

  if (isArticulo.value) {
    if (!form.nombre_articulo) {
      return (
        "El nombre del artículo es obligatorio."
      );
    }

    if (!form.base_datos_indexada) {
      return (
        "La base de datos o indexación es obligatoria."
      );
    }

    if (!form.nombre_revista) {
      return (
        "El nombre de la revista es obligatorio."
      );
    }

    if (!form.codigo_doi) {
      return "El DOI es obligatorio.";
    }

    if (!form.codigo_issn) {
      return "El ISSN es obligatorio.";
    }
  }

  if (isPonencia.value) {
    if (!form.nombre_evento) {
      return (
        "El nombre del evento es obligatorio."
      );
    }

    if (!form.nombre_ponencia) {
      return (
        "El nombre de la ponencia es obligatorio."
      );
    }
  }

  if (isCapitulo.value) {
    if (!form.nombre_capitulo) {
      return (
        "El nombre del capítulo es obligatorio."
      );
    }

    if (!form.nombre_libro) {
      return (
        "El nombre del libro es obligatorio."
      );
    }

    if (!form.codigo_isbn) {
      return "El ISBN es obligatorio.";
    }
  }

  return "";
};

/* ============================================================
  VISUALIZACIÓN DEL PDF
============================================================ */

const writePdfLoading = (targetWindow) => {
  targetWindow.document.open();

  targetWindow.document.write(`
    <!doctype html>
    <html lang="es">
      <head>
        <title>Cargando PDF...</title>
        <meta charset="utf-8" />
      </head>

      <body
        style="
          margin: 0;
          padding: 32px;
          background: #f2f5fa;
          color: #172033;
          font-family: Arial, sans-serif;
        "
      >
        <p>Cargando PDF...</p>
      </body>
    </html>
  `);

  targetWindow.document.close();
};

const writePdfError = (
  targetWindow,
  message = "No se pudo abrir el PDF."
) => {
  targetWindow.document.open();

  targetWindow.document.write(`
    <!doctype html>
    <html lang="es">
      <head>
        <title>No se pudo abrir el PDF</title>
        <meta charset="utf-8" />
      </head>

      <body
        style="
          margin: 0;
          padding: 32px;
          background: #f2f5fa;
          color: #172033;
          font-family: Arial, sans-serif;
        "
      >
        <h2>${message}</h2>

        <p>
          Verifique que la publicación tenga un archivo PDF asociado.
        </p>
      </body>
    </html>
  `);

  targetWindow.document.close();
};

const writePdfViewer = (
  targetWindow,
  blobUrl
) => {
  targetWindow.document.open();

  targetWindow.document.write(`
    <!doctype html>
    <html lang="es">
      <head>
        <title>Vista previa del PDF</title>
        <meta charset="utf-8" />

        <style>
          html,
          body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #101827;
          }

          iframe {
            width: 100%;
            height: 100%;
            border: 0;
            background: #ffffff;
          }
        </style>
      </head>

      <body>
        <iframe
          src="${blobUrl}"
          title="Vista previa del PDF"
        ></iframe>
      </body>
    </html>
  `);

  targetWindow.document.close();
};

const fetchCurrentPdfBlob = async () => {
  if (!currentId.value) {
    throw new Error(
      "No se pudo determinar el identificador de la publicación."
    );
  }

  const response = await api.get(
    `/publicaciones/${currentId.value}/pdf/`,
    {
      responseType: "blob",

      headers: {
        Accept: "application/pdf",
      },
    }
  );

  const contentType = String(
    response.headers?.["content-type"] || ""
  ).toLowerCase();

  if (
    contentType &&
    !contentType.includes("application/pdf")
  ) {
    throw new Error(
      "La respuesta recibida no es un PDF."
    );
  }

  return new Blob(
    [response.data],
    {
      type: "application/pdf",
    }
  );
};

const openCurrentPdf = async () => {
  if (!currentId.value) {
    return;
  }

  const previewWindow = window.open(
    "about:blank",
    "_blank"
  );

  if (!previewWindow) {
    window.alert(
      "El navegador bloqueó la ventana emergente. " +
      "Permita las ventanas emergentes para visualizar el PDF."
    );

    return;
  }

  writePdfLoading(previewWindow);

  try {
    const blob =
      await fetchCurrentPdfBlob();

    const blobUrl =
      URL.createObjectURL(blob);

    writePdfViewer(
      previewWindow,
      blobUrl
    );

    window.setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 180000);
  } catch (pdfError) {
    console.error(pdfError);

    writePdfError(previewWindow);
  }
};

const downloadCurrentPdf = async () => {
  if (!currentId.value) {
    return;
  }

  try {
    const blob =
      await fetchCurrentPdfBlob();

    const blobUrl =
      URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    link.href = blobUrl;

    link.download =
      currentPdfName.value ||
      "publicacion.pdf";

    document.body.appendChild(link);

    link.click();
    link.remove();

    window.setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 1000);
  } catch (pdfError) {
    console.error(pdfError);

    window.alert(
      "No se pudo descargar el PDF."
    );
  }
};

/* ============================================================
  ELIMINACIÓN DEL PDF
============================================================ */

const requestRemovePdf = () => {
  if (
    !canEdit.value ||
    !hasCurrentPdf.value ||
    savingLocal.value ||
    removingPdf.value
  ) {
    return;
  }

  showRemovePdfModal.value = true;
};

const cancelRemovePdf = () => {
  if (removingPdf.value) {
    return;
  }

  showRemovePdfModal.value = false;
};

const removeCurrentPdf = async () => {
  if (
    !canEdit.value ||
    !hasCurrentPdf.value ||
    savingLocal.value ||
    removingPdf.value
  ) {
    return;
  }

  removingPdf.value = true;

  editMsg.value = "";
  editMsgType.value = "";
  fileError.value = "";

  try {
    if (!currentId.value) {
      editMsg.value =
        "No se pudo determinar el identificador de la publicación.";

      editMsgType.value = "error";

      return;
    }

    await api.patch(
      `/publicaciones/${currentId.value}/`,
      {
        quitar_pdf_actual: true,
      },
      {
        headers: {
          "Content-Type":
            "application/json",
        },
      }
    );

    pdfUploadItems.value = [];
    showRemovePdfModal.value = false;

    editMsg.value =
      "El PDF fue quitado correctamente.";

    editMsgType.value = "success";

    preserveFeedbackOnNextDetalle.value =
      true;

    emit("updated");
  } catch (removeError) {
    console.error(removeError);

    const data =
      removeError?.response?.data;

    if (
      data &&
      typeof data === "object"
    ) {
      const errores = Object.entries(data)
        .map(([campo, detail]) => {
          return (
            `• ${campo}: ` +
            prettyError(detail)
          );
        })
        .join("\n");

      editMsg.value =
        `Error al quitar el PDF:\n${errores}`;
    } else {
      editMsg.value =
        removeError?.response?.data?.detail ||
        removeError?.response?.data?.message ||
        removeError?.response?.data?.error ||
        "No se pudo quitar el PDF de la publicación.";
    }

    editMsgType.value = "error";
  } finally {
    removingPdf.value = false;
  }
};

/* ============================================================
  GUARDADO
============================================================ */

const guardar = async () => {
  savingLocal.value = true;

  editMsg.value = "";
  editMsgType.value = "";
  fileError.value = "";

  try {
    if (!canEdit.value) {
      editMsg.value =
        "No tiene permisos para editar esta publicación.";

      editMsgType.value = "error";

      return;
    }

    if (!currentId.value) {
      editMsg.value =
        "No se pudo determinar el identificador de la publicación.";

      editMsgType.value = "error";

      return;
    }

    const validationMessage =
      validarEdicion();

    if (validationMessage) {
      editMsg.value =
        validationMessage;

      editMsgType.value = "error";

      return;
    }

    const formData =
      buildFormDataPayload();

    await api.put(
      `/publicaciones/${currentId.value}/`,
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      }
    );

    editMsg.value =
      "Los cambios fueron guardados correctamente.";

    editMsgType.value = "success";

    preserveFeedbackOnNextDetalle.value =
      true;

    emit("updated");
  } catch (saveError) {
    console.error(saveError);

    const data =
      saveError?.response?.data;

    if (data?.archivo_pdf) {
      fileError.value =
        prettyError(data.archivo_pdf);
    }

    if (
      data &&
      typeof data === "object"
    ) {
      const errores = Object.entries(data)
        .map(([campo, detail]) => {
          return (
            `• ${campo}: ` +
            prettyError(detail)
          );
        })
        .join("\n");

      editMsg.value =
        `Error al guardar:\n${errores}`;
    } else {
      editMsg.value =
        "No se pudieron guardar los cambios. Intente nuevamente.";
    }

    editMsgType.value = "error";
  } finally {
    savingLocal.value = false;
  }
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
<style src="./editar-publicacion.css"></style>