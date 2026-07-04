<template>
  <div class="pub-edit" :class="{ 'is-saving': savingLocal }">
    <p v-if="editMsg" :class="['pub-msg', editMsgType]">
      {{ editMsg }}
    </p>

    <section class="pub-section">
      <div class="pub-embed pub-embed--context pub-embed--plain">
        <DatosGenerales
          v-model="form.datos_generales"
          :hideUbicacion="!isPonencia"
          :proyectoOpcional="isArticulo || isPonencia"
        />
      </div>
    </section>

    <section class="pub-section">
      <div class="pub-section__head pub-section__head--compact">
        <div>
          <h3 class="pub-h2">Información general</h3>
        </div>

        <div class="pub-section__meta">
          <span class="pub-chip">{{ tipoLabel }}</span>
          <span v-if="isAdmin" class="pub-chip">Administrador</span>
          <span v-else-if="canEdit" class="pub-chip">Autor vinculado</span>
        </div>
      </div>

      <div class="pub-form-grid">
        <div class="pub-field">
          <label class="pub-label">
            Fecha de publicación
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            type="date"
            v-model="form.fecha_publicacion"
            required
            :disabled="savingLocal || removingPdf"
          />
          <p v-if="form.fecha_publicacion" class="pub-help">
            {{ formatFecha(form.fecha_publicacion) }}
          </p>
        </div>
      </div>
    </section>

    <section class="pub-section">
      <div class="pub-section__head pub-section__head--compact">
        <div>
          <h3 class="pub-h2">Campos específicos</h3>
        </div>

        <div class="pub-section__meta">
          <span class="pub-chip">{{ tipoLabel }}</span>
        </div>
      </div>

      <div v-if="isPonencia" class="pub-form-grid">
        <div class="pub-field">
          <label class="pub-label">
            Evento
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_evento"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            Ponencia
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_ponencia"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field full">
          <label class="pub-label">ISSN / ISBN</label>
          <input
            class="pub-input"
            v-model.trim="form.codigo_issn_isbn"
            :disabled="savingLocal || removingPdf"
          />
        </div>
      </div>

      <div v-else-if="isArticulo" class="pub-form-grid">
        <div class="pub-field full">
          <label class="pub-label">
            Nombre del artículo
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_articulo"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            Base de datos / indexación
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.base_datos_indexada"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            Nombre de la revista
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_revista"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            DOI
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.codigo_doi"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            ISSN
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.codigo_issn"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field full">
          <label class="pub-label">Enlace de la publicación</label>
          <input
            class="pub-input"
            v-model.trim="form.link_publicacion"
            type="url"
            placeholder="https://..."
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <template v-if="!isArticuloRegional">
          <div class="pub-field full">
            <label class="pub-label">Enlace de la revista</label>
            <input
              class="pub-input"
              v-model.trim="form.link_revista"
              type="url"
              placeholder="https://..."
              :disabled="savingLocal || removingPdf"
            />
          </div>

          <template v-if="isAdmin">
            <div class="pub-field">
              <label class="pub-label">Factor de impacto</label>
              <input
                class="pub-input"
                v-model.trim="form.factor_impacto"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pub-field">
              <label class="pub-label">Cuartil</label>
              <input
                class="pub-input"
                v-model.trim="form.cuartil"
                placeholder="Ej. Q1, Q2"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pub-field">
              <label class="pub-label">SJR</label>
              <input
                class="pub-input"
                v-model.trim="form.sjr"
                :disabled="savingLocal || removingPdf"
              />
            </div>

            <div class="pub-field">
              <label class="pub-label">Número de revista</label>
              <input
                class="pub-input"
                v-model.trim="form.numero_revista"
                :disabled="savingLocal || removingPdf"
              />
            </div>
          </template>
        </template>

        <div v-if="isArticuloRegional" class="pub-inlineNote">
          Artículo regional: los indicadores avanzados no aplican.
        </div>
      </div>

      <div v-else-if="isCapitulo" class="pub-form-grid">
        <div class="pub-field">
          <label class="pub-label">
            Nombre del capítulo
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_capitulo"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            Nombre del libro
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.nombre_libro"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">
            ISBN
            <span class="req">*</span>
          </label>
          <input
            class="pub-input"
            v-model.trim="form.codigo_isbn"
            required
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field">
          <label class="pub-label">Editor / Compilador</label>
          <input
            class="pub-input"
            v-model.trim="form.editor_compilador"
            :disabled="savingLocal || removingPdf"
          />
        </div>

        <div class="pub-field full">
          <label class="pub-label">Enlace</label>
          <input
            class="pub-input"
            v-model.trim="form.link_capitulo"
            type="url"
            placeholder="https://..."
            :disabled="savingLocal || removingPdf"
          />
        </div>
      </div>

      <div v-else class="pub-muted">
        No hay campos editables para este tipo.
      </div>
    </section>

    <section class="pub-section">
      <div class="pub-section__head pub-section__head--compact">
        <div>
          <h3 class="pub-h2">Autores</h3>
        </div>
      </div>

      <div class="pub-embed pub-embed--authors">
        <AutoresSelector v-model="form.autores" />
      </div>
    </section>

    <section class="pub-section">
      <div class="pub-section__head pub-section__head--compact">
        <div>
          <h3 class="pub-h2">Archivo PDF</h3>
          <p class="pub-section__text">
            Desde esta sección puedes consultar, reemplazar o quitar el PDF de la publicación.
          </p>
        </div>
      </div>

      <div v-if="hasCurrentPdf" class="pub-filePanel">
        <div class="pub-filePanel__meta">
          <span class="pub-filePanel__eyebrow">Documento actual</span>
          <h4 class="pub-filePanel__name">
            {{ currentPdfName }}
          </h4>
          <p class="pub-filePanel__text">
            Puedes conservar este archivo, reemplazarlo por uno nuevo o quitarlo del registro.
          </p>
        </div>

        <div class="pub-filePanel__actions">
          <button
            class="pub-btn pub-btn--ghost"
            type="button"
            @click="openCurrentPdf"
            :disabled="savingLocal || removingPdf"
          >
            Ver PDF actual
          </button>

          <button
            class="pub-btn pub-btn--ghost"
            type="button"
            @click="downloadCurrentPdf"
            :disabled="savingLocal || removingPdf"
          >
            Descargar PDF actual
          </button>

          <button
            v-if="canEdit"
            class="pub-btn pub-btn--danger"
            type="button"
            @click="requestRemovePdf"
            :disabled="savingLocal || removingPdf"
          >
            {{ removingPdf ? "Quitando..." : "Quitar PDF" }}
          </button>
        </div>
      </div>

      <AdjuntosPdfUploader
        v-model="pdfUploadItems"
        :error="fileError"
        input-id="pub-edit-archivo-pdf"
        title="Actualizar archivo PDF"
        description="Seleccione el PDF principal del registro. Si carga uno nuevo, reemplazará el actual al guardar."
        helper-text="Formato permitido: PDF. Puede arrastrar y soltar un solo archivo."
        :multiple="false"
        :max-files="1"
      />
    </section>

    <div class="pub-footer" role="group" aria-label="Acciones de edición">
      <button
        class="pub-btn pub-btn--primary"
        type="button"
        @click="guardar"
        :disabled="savingLocal || removingPdf"
      >
        {{ savingLocal ? "Guardando..." : "Guardar cambios" }}
      </button>

      <button
        class="pub-btn pub-btn--ghost"
        type="button"
        @click="$emit('cancel')"
        :disabled="savingLocal || removingPdf"
      >
        Volver al detalle
      </button>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="showRemovePdfModal"
      class="pub-modalOverlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="pub-remove-pdf-title"
      @click.self="cancelRemovePdf"
    >
      <section class="pub-modal">
        <div class="pub-modal__icon">
          PDF
        </div>

        <div class="pub-modal__body">
          <p class="pub-modal__eyebrow">
            Confirmación requerida
          </p>

          <h2 id="pub-remove-pdf-title" class="pub-modal__title">
            Quitar archivo PDF
          </h2>

          <p class="pub-modal__text">
            Estás por quitar el PDF asociado a esta publicación. Esta acción
            eliminará el documento actual del registro académico.
          </p>

          <p class="pub-modal__warning">
            Si necesitas conservar una copia, descarga el archivo antes de continuar.
          </p>
        </div>

        <div class="pub-modal__actions">
          <button
            class="pub-btn pub-btn--ghost"
            type="button"
            :disabled="removingPdf"
            @click="cancelRemovePdf"
          >
            Cancelar
          </button>

          <button
            class="pub-btn pub-btn--danger"
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
import { ref, reactive, computed, watch } from "vue";
import { useRoute } from "vue-router";
import api from "../../scripts/api/axios";

import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";

const props = defineProps({
  detalle: { type: Object, required: true },
  saving: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  isAdmin: { type: Boolean, default: false },
});

const emit = defineEmits(["saving", "updated", "cancel"]);

const route = useRoute();

const editMsg = ref("");
const editMsgType = ref("");
const fileError = ref("");
const pdfUploadItems = ref([]);
const removingPdf = ref(false);
const showRemovePdfModal = ref(false);
const preserveFeedbackOnNextDetalle = ref(false);

const savingLocal = computed({
  get: () => props.saving,
  set: (value) => emit("saving", !!value),
});

const canEdit = computed(() => !!props.canEdit);
const isAdmin = computed(() => !!props.isAdmin);

const firstFilled = (...values) =>
  values
    .map((value) => (value == null ? "" : String(value).trim()))
    .find(Boolean) || "";

const normalizeText = (value) =>
  String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

const currentId = computed(() => firstFilled(route.params.id, props.detalle?.id));
const tipoLabel = computed(() => firstFilled(props.detalle?.tipo, "Publicación"));

const tipoStr = computed(() => String(props.detalle?.tipo || ""));
const tipoCodigo = computed(() =>
  String(props.detalle?.tipo_codigo || props.detalle?.tipoCodigo || "")
);
const tipoNormalized = computed(() => normalizeText(tipoStr.value));

const isPonencia = computed(() => tipoNormalized.value.includes("ponencia"));
const isArticulo = computed(() => tipoNormalized.value.includes("articulo"));
const isCapitulo = computed(() => tipoNormalized.value.includes("capitulo"));

const isArticuloRegional = computed(() => {
  const tc = normalizeText(tipoCodigo.value);
  if (tc) return tc === "articulo_regional";
  return tipoNormalized.value.includes("regional");
});

const formatFecha = (value) => {
  const fecha = String(value || "").trim();
  if (!fecha) return "";

  try {
    if (/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [year, month, day] = fecha.split("-").map(Number);
      const localDate = new Date(year, month - 1, day);
      return localDate.toLocaleDateString("es-EC", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    }

    const parsed = new Date(fecha);
    if (Number.isNaN(parsed.getTime())) return fecha;

    return parsed.toLocaleDateString("es-EC", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return fecha;
  }
};

const fileNameFromValue = (value) => {
  const raw = String(value || "").trim();
  if (!raw) return "archivo.pdf";

  try {
    const parsed = new URL(raw, window.location.origin);
    const last = parsed.pathname.split("/").filter(Boolean).pop();
    return decodeURIComponent(last || "archivo.pdf");
  } catch {
    return raw.split("/").filter(Boolean).pop() || "archivo.pdf";
  }
};

const getBackendBase = () => {
  const envBase =
    firstFilled(
      import.meta.env.VITE_API_URL,
      import.meta.env.VITE_API_BASE_URL,
      import.meta.env.VITE_AXIOS_BASE_URL
    ) || "";

  const axiosBase = firstFilled(api?.defaults?.baseURL);
  const base = envBase || axiosBase;

  if (/^https?:\/\//i.test(base)) {
    return base.replace(/\/api\/?$/i, "").replace(/\/$/, "");
  }

  return window.location.origin;
};

const resolveFileUrl = (value) => {
  const raw = String(value || "").trim();
  if (!raw) return "";

  if (/^https?:\/\//i.test(raw)) return raw;
  if (raw.startsWith("blob:") || raw.startsWith("data:")) return raw;

  const base = getBackendBase();
  const clean = raw.startsWith("/") ? raw : `/${raw.replace(/^\.?\//, "")}`;
  return `${base}${clean}`;
};

const currentPdfValue = computed(() =>
  firstFilled(
    props.detalle?.archivo_pdf_url,
    props.detalle?.archivo_pdf,
    props.detalle?.pdf,
    props.detalle?.archivo,
    props.detalle?.archivos?.[0]?.url,
    props.detalle?.archivos?.[0]?.archivo,
    props.detalle?.archivos?.[0]?.archivo_url,
    props.detalle?.adjuntos?.[0]?.url,
    props.detalle?.adjuntos?.[0]?.archivo,
    props.detalle?.adjuntos?.[0]?.archivo_url
  )
);

const currentPdfHref = computed(() => resolveFileUrl(currentPdfValue.value));
const hasCurrentPdf = computed(() => Boolean(currentPdfHref.value));
const currentPdfName = computed(() => fileNameFromValue(currentPdfValue.value));

const selectedPdfItem = computed(() => {
  const items = Array.isArray(pdfUploadItems.value) ? pdfUploadItems.value : [];
  return items.find((it) => it?.file) || null;
});

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

const normalizeAutoresForSelector = (arr) => {
  const base = Array.isArray(arr) ? arr : [];

  return base
    .map((autor, index) => {
      const autorId = autor?.autor_id ?? autor?.id ?? null;
      if (!autorId) return null;

      return {
        autor_id: Number(autorId),
        orden: autor?.orden ?? index + 1,
        rol_autoria: autor?.rol_autoria ?? (index === 0 ? "principal" : "coautor"),
        nombre_completo: autor?.nombre_completo || autor?.nombre || "",
      };
    })
    .filter(Boolean)
    .map((item, index) => ({
      ...item,
      orden: index + 1,
      rol_autoria: index === 0 ? "principal" : "coautor",
    }));
};

const mapDetalleToForm = (detalle) => {
  form.tipo = detalle?.tipo || "";
  form.fecha_publicacion = String(detalle?.fecha_publicacion || "").substring(0, 10);

  form.datos_generales = {
    facultad: detalle?.facultad_id ?? null,
    carrera: detalle?.carrera_id ?? null,
    proyecto: detalle?.proyecto_id ?? null,
    area: detalle?.area_id ?? null,
    subarea: detalle?.subarea_id ?? null,
    pais: detalle?.pais_id ?? null,
    ciudad: detalle?.ciudad_id ?? null,
  };

  form.autores = normalizeAutoresForSelector(detalle?.autores);

  form.nombre_evento = detalle?.nombre_evento || "";
  form.nombre_ponencia = detalle?.nombre_ponencia || "";
  form.codigo_issn_isbn = detalle?.codigo_issn_isbn || "";

  form.nombre_articulo = detalle?.nombre_articulo || "";
  form.base_datos_indexada = detalle?.base_datos_indexada || "";
  form.codigo_doi = detalle?.codigo_doi || "";
  form.codigo_issn = detalle?.codigo_issn || "";
  form.nombre_revista = detalle?.nombre_revista || "";
  form.numero_revista = detalle?.numero_revista || "";
  form.link_publicacion = detalle?.link_publicacion || "";
  form.link_revista = detalle?.link_revista || "";
  form.factor_impacto = detalle?.factor_impacto || "";
  form.cuartil = detalle?.cuartil || "";
  form.sjr = detalle?.sjr || "";

  form.nombre_capitulo = detalle?.nombre_capitulo || "";
  form.nombre_libro = detalle?.nombre_libro || "";
  form.codigo_isbn = detalle?.codigo_isbn || "";
  form.editor_compilador = detalle?.editor_compilador || "";
  form.link_capitulo = detalle?.link_capitulo || "";

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
    if (!detalle) return;

    pdfUploadItems.value = [];
    fileError.value = "";

    if (preserveFeedbackOnNextDetalle.value) {
      preserveFeedbackOnNextDetalle.value = false;
    } else {
      editMsg.value = "";
      editMsgType.value = "";
    }

    mapDetalleToForm(detalle);
  },
  { immediate: true }
);

const prettyError = (value) => {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(prettyError).join(", ");
  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, nested]) => `${key}: ${prettyError(nested)}`)
      .join(" | ");
  }
  return String(value);
};

const buildAutoresPayload = () => {
  const raw = Array.isArray(form.autores) ? [...form.autores] : [];

  return raw
    .map((autor, index) => {
      const autorId = autor?.autor_id ?? autor?.id ?? autor?.autor?.id ?? null;
      const numericId = Number(autorId);

      if (!Number.isFinite(numericId) || numericId <= 0) return null;

      const orden = index + 1;

      return {
        autor_id: numericId,
        orden,
        rol_autoria: orden === 1 ? "principal" : "coautor",
      };
    })
    .filter(Boolean);
};

const allowedSpecificFields = computed(() => {
  if (isPonencia.value) {
    return ["nombre_evento", "nombre_ponencia", "codigo_issn_isbn"];
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

    if (isArticuloRegional.value) return base;

    const extras = ["link_revista"];
    if (isAdmin.value) extras.push("numero_revista", "factor_impacto", "cuartil", "sjr");

    return [...base, ...extras];
  }

  return [];
});

const buildFormDataPayload = () => {
  const fd = new FormData();

  Object.entries(form.datos_generales || {}).forEach(([key, value]) => {
    if (!isPonencia.value && (key === "pais" || key === "ciudad")) return;
    if (key === "proyecto" && (value === "0" || !value)) return;

    if (value !== null && value !== "" && value !== undefined) {
      fd.append(key, value);
    }
  });

  if (form.fecha_publicacion) {
    fd.append("fecha_publicacion", form.fecha_publicacion);
  }

  allowedSpecificFields.value.forEach((key) => {
    const value = form[key];
    if (value !== null && value !== "" && value !== undefined) {
      fd.append(key, value);
    }
  });

  fd.set("autores", JSON.stringify(buildAutoresPayload()));

  if (selectedPdfItem.value?.file) {
    fd.append("archivo_pdf", selectedPdfItem.value.file);
  }

  return fd;
};

const validarEdicion = () => {
  const autores = buildAutoresPayload();
  if (!autores.length) return "Debe registrar al menos un autor.";

  const dg = form.datos_generales || {};
  const obligatorios = ["facultad", "carrera", "area", "subarea"];

  if (!isArticulo.value && !isPonencia.value) {
    obligatorios.push("proyecto");
  }

  const faltan = obligatorios.filter((key) => !dg[key] || dg[key] === "0");
  if (faltan.length) return "Faltan campos obligatorios.";

  if (isPonencia.value && (!dg.pais || !dg.ciudad)) {
    return "Debe indicar país y ciudad.";
  }

  if (!form.fecha_publicacion) {
    return "La fecha de publicación es obligatoria.";
  }

  if (isArticulo.value) {
    if (!form.nombre_articulo) return "El nombre del artículo es obligatorio.";
    if (!form.base_datos_indexada) return "La base de datos / indexación es obligatoria.";
    if (!form.nombre_revista) return "El nombre de la revista es obligatoria.";
    if (!form.codigo_doi) return "El DOI es obligatorio.";
    if (!form.codigo_issn) return "El ISSN es obligatorio.";
  }

  if (isPonencia.value) {
    if (!form.nombre_evento) return "El nombre del evento es obligatorio.";
    if (!form.nombre_ponencia) return "El nombre de la ponencia es obligatorio.";
  }

  if (isCapitulo.value) {
    if (!form.nombre_capitulo) return "El nombre del capítulo es obligatorio.";
    if (!form.nombre_libro) return "El nombre del libro es obligatorio.";
    if (!form.codigo_isbn) return "El ISBN es obligatorio.";
  }

  return "";
};

const openCurrentPdf = async () => {
  if (!currentId.value) return;

  const previewWindow = window.open("", "_blank");

  if (!previewWindow) {
    alert(
      "El navegador bloqueó la ventana emergente. Permite ventanas emergentes para ver el PDF."
    );
    return;
  }

  previewWindow.document.write(`
    <html>
      <head>
        <title>Cargando PDF...</title>
      </head>
      <body style="font-family: Arial, sans-serif; padding: 24px;">
        <p>Cargando PDF...</p>
      </body>
    </html>
  `);

  try {
    const response = await api.get(`/publicaciones/${currentId.value}/pdf/`, {
      responseType: "blob",
      headers: {
        Accept: "application/pdf",
      },
    });

    const blob = new Blob([response.data], {
      type: "application/pdf",
    });

    const blobUrl = URL.createObjectURL(blob);

    previewWindow.location.href = blobUrl;

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 120000);
  } catch (err) {
    console.error(err);

    previewWindow.document.body.innerHTML = `
      <p>No se pudo abrir el PDF.</p>
      <p>Verifica que la publicación tenga un archivo PDF asociado.</p>
    `;
  }
};

const downloadCurrentPdf = async () => {
  if (!currentId.value) return;

  try {
    const response = await api.get(`/publicaciones/${currentId.value}/pdf/`, {
      responseType: "blob",
      headers: {
        Accept: "application/pdf",
      },
    });

    const blob = new Blob([response.data], {
      type: "application/pdf",
    });

    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = currentPdfName.value || "publicacion.pdf";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 1000);
  } catch (err) {
    console.error(err);
    alert("No se pudo descargar el PDF.");
  }
};

const requestRemovePdf = () => {
  if (!canEdit.value || !hasCurrentPdf.value || savingLocal.value || removingPdf.value) {
    return;
  }

  showRemovePdfModal.value = true;
};

const cancelRemovePdf = () => {
  if (removingPdf.value) return;
  showRemovePdfModal.value = false;
};

const removeCurrentPdf = async () => {
  if (!canEdit.value || !hasCurrentPdf.value || savingLocal.value || removingPdf.value) {
    return;
  }

  removingPdf.value = true;
  editMsg.value = "";
  editMsgType.value = "";
  fileError.value = "";

  try {
    if (!currentId.value) {
      editMsg.value = "No se pudo determinar el identificador de la publicación.";
      editMsgType.value = "error";
      return;
    }

    const formData = new FormData();
    formData.append("quitar_pdf_actual", "true");

    await api.patch(`/publicaciones/${currentId.value}/`, formData);

    pdfUploadItems.value = [];
    showRemovePdfModal.value = false;
    editMsg.value = "PDF quitado correctamente.";
    editMsgType.value = "success";

    preserveFeedbackOnNextDetalle.value = true;
    emit("updated");
  } catch (err) {
    console.error(err);

    const data = err?.response?.data;

    if (data && typeof data === "object") {
      const errores = Object.entries(data)
        .map(([campo, detalle]) => `• ${campo}: ${prettyError(detalle)}`)
        .join("\n");

      editMsg.value = `Error al quitar el PDF:\n${errores}`;
    } else {
      editMsg.value =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.response?.data?.error ||
        "No se pudo quitar el PDF de la publicación.";
    }

    editMsgType.value = "error";
  } finally {
    removingPdf.value = false;
  }
};

const guardar = async () => {
  savingLocal.value = true;
  editMsg.value = "";
  editMsgType.value = "";
  fileError.value = "";

  try {
    if (!canEdit.value) {
      editMsg.value = "No tienes permisos para editar esta publicación.";
      editMsgType.value = "error";
      savingLocal.value = false;
      return;
    }

    if (!currentId.value) {
      editMsg.value = "No se pudo determinar el identificador de la publicación.";
      editMsgType.value = "error";
      savingLocal.value = false;
      return;
    }

    const validationMessage = validarEdicion();
    if (validationMessage) {
      editMsg.value = validationMessage;
      editMsgType.value = "error";
      savingLocal.value = false;
      return;
    }

    const formData = buildFormDataPayload();

    await api.put(`/publicaciones/${currentId.value}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    editMsg.value = "Cambios guardados correctamente.";
    editMsgType.value = "success";

    preserveFeedbackOnNextDetalle.value = true;
    emit("updated");
  } catch (err) {
    console.error(err);
    const data = err?.response?.data;

    if (data?.archivo_pdf) {
      fileError.value = prettyError(data.archivo_pdf);
    }

    if (data && typeof data === "object") {
      const errores = Object.entries(data)
        .map(([campo, detalle]) => `• ${campo}: ${prettyError(detalle)}`)
        .join("\n");

      editMsg.value = `Error al guardar:\n${errores}`;
    } else {
      editMsg.value = "No se pudieron guardar los cambios. Intenta nuevamente.";
    }

    editMsgType.value = "error";
  } finally {
    savingLocal.value = false;
  }
};
</script>

<style src="../componentes/sgpc-fcvt.css"></style>
<style src="./editar-publicacion.css"></style>

