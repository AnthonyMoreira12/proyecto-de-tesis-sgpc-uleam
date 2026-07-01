<template>
  <div class="sgpc-form-page">
    <div class="sgpc-form-shell">
      <header class="sgpc-form-header page-stage page-header">
        <div class="sgpc-form-heading">
          <p class="sgpc-form-kicker">{{ pageKicker }}</p>

          <h1 class="sgpc-form-title">{{ pageTitle }}</h1>

          <p class="sgpc-form-subtitle">
            {{ pageSubtitle }}
          </p>

          <p v-if="draftInfo" class="sgpc-banner-info">
            {{ draftInfo }}
          </p>
        </div>
      </header>

      <form
        class="sgpc-form sgpc-form--with-aside"
        @submit.prevent="registrarArticuloRegional"
        enctype="multipart/form-data"
      >
        <main class="sgpc-form-main page-stage page-main">
          <section
            v-if="isAdminDelegado"
            id="sec-contexto-admin"
            class="sgpc-card sgpc-card--admin-context"
          >
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Contexto del registro</h3>
                <p class="sgpc-card-desc">
                  Este registro se guardará para el usuario seleccionado.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div id="ar-admin-context-anchor"></div>

              <div class="sgpc-admin-context">
                <article class="sgpc-admin-context__item">
                  <span class="sgpc-admin-context__label">Usuario objetivo</span>
                  <strong class="sgpc-admin-context__value">
                    {{ adminDisplayUsuario }}
                  </strong>
                </article>

                <article
                  v-if="showAutorObjetivo"
                  class="sgpc-admin-context__item"
                >
                  <span class="sgpc-admin-context__label">Autor objetivo</span>
                  <strong class="sgpc-admin-context__value">
                    {{ adminDisplayAutor }}
                  </strong>
                </article>
              </div>

              <p class="sgpc-hint">
                El autor objetivo se agregará automáticamente a la autoría del registro.
              </p>

              <p
                v-if="fieldErrors.admin_context"
                class="sgpc-hint sgpc-hint-error"
              >
                {{ fieldErrors.admin_context }}
              </p>
            </div>
          </section>

          <section id="sec-datos-generales" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Datos generales</h3>
                <p class="sgpc-card-desc">
                  Información institucional para clasificación del registro.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <DatosGenerales
                v-model="formDatos"
                :errors="fieldErrors"
                :hideUbicacion="true"
                :proyectoOpcional="true"
                proyectoLabel="Proyecto de investigación"
                areaLabel="Área del conocimiento (UNESCO)"
                subareaLabel="Subárea del conocimiento (UNESCO)"
              />
            </div>
          </section>

          <section id="sec-origen" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Origen de la publicación</h3>
                <p class="sgpc-card-desc">
                  Indique si el artículo proviene de un trabajo académico o no aplica.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-origen_tipo">
                    Origen <span class="req">*</span>
                  </label>

                  <select
                    id="ar-origen_tipo"
                    v-model="form.origen_tipo"
                    class="sgpc-input"
                    required
                  >
                    <option disabled value="">Seleccione...</option>
                    <option value="ninguno">Ninguno</option>
                    <option value="tic">Trabajo de integración curricular</option>
                    <option value="maestria">Tesis de maestría</option>
                    <option value="doctoral">Tesis doctoral</option>
                  </select>

                  <p v-if="fieldErrors.origen_tipo" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.origen_tipo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-origen_grado">
                    Grado / programa
                    <span v-if="form.origen_tipo === 'tic'" class="req">*</span>
                  </label>

                  <input
                    id="ar-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    :disabled="form.origen_tipo !== 'tic'"
                    :required="form.origen_tipo === 'tic'"
                    placeholder="Ej. Ingeniería de Software / ..."
                  />

                  <p class="sgpc-hint">
                    Se habilita solo cuando el origen es “Trabajo de integración curricular”.
                  </p>

                  <p v-if="fieldErrors.origen_grado" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.origen_grado }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section id="sec-principales" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Datos principales</h3>
                <p class="sgpc-card-desc">
                  Información base del artículo e indexación regional.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-fecha_publicacion">
                    Fecha de publicación <span class="req">*</span>
                  </label>

                  <input
                    id="ar-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    required
                  />

                  <p v-if="fieldErrors.fecha_publicacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-tipo_articulo">
                    Clasificación
                  </label>

                  <input
                    id="ar-tipo_articulo"
                    class="sgpc-input"
                    type="text"
                    value="Regional"
                    disabled
                  />
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="ar-nombre_articulo">
                    Título del artículo <span class="req">*</span>
                  </label>

                  <input
                    id="ar-nombre_articulo"
                    v-model.trim="form.nombre_articulo"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Análisis regional de la producción científica"
                  />

                  <p v-if="fieldErrors.nombre_articulo" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_articulo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-base_datos_indexada">
                    Base de datos / indexación <span class="req">*</span>
                  </label>

                  <select
                    id="ar-base_datos_indexada"
                    v-model="form.base_datos_indexada"
                    class="sgpc-input"
                    required
                  >
                    <option disabled value="">Seleccione una opción</option>
                    <option value="latindex">Latindex</option>
                    <option value="scielo">SciELO</option>
                    <option value="redalyc">Redalyc</option>
                    <option value="dialnet">Dialnet</option>
                    <option value="google_scholar">Google Scholar</option>
                    <option value="otra">Otra</option>
                  </select>

                  <p
                    v-if="fieldErrors.base_datos_indexada"
                    class="sgpc-hint sgpc-hint-error"
                  >
                    {{ fieldErrors.base_datos_indexada }}
                  </p>
                </div>

                <div
                  v-if="form.base_datos_indexada === 'otra'"
                  class="sgpc-field sgpc-col-span-6"
                >
                  <label class="sgpc-label" for="ar-base_datos_otra">
                    Especifique la base de datos <span class="req">*</span>
                  </label>

                  <input
                    id="ar-base_datos_otra"
                    v-model.trim="form.base_datos_otra"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Repositorio institucional / Revista local / ..."
                  />

                  <p v-if="fieldErrors.base_datos_otra" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.base_datos_otra }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section id="sec-revista" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Revista y enlaces</h3>
                <p class="sgpc-card-desc">
                  Identificación formal, metadatos y enlaces de acceso. Los indicadores de impacto no aplican a artículos regionales.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-codigo_issn">
                    Código ISSN <span class="req">*</span>
                  </label>

                  <input
                    id="ar-codigo_issn"
                    v-model.trim="form.codigo_issn"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. 1234-5678"
                  />

                  <p v-if="fieldErrors.codigo_issn" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_issn }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-codigo_doi">Código DOI</label>

                  <input
                    id="ar-codigo_doi"
                    v-model.trim="form.codigo_doi"
                    class="sgpc-input"
                    type="text"
                    placeholder="Ej. 10.1234/abcd.2025"
                  />

                  <p v-if="fieldErrors.codigo_doi" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_doi }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="ar-nombre_revista">
                    Nombre de la revista <span class="req">*</span>
                  </label>

                  <input
                    id="ar-nombre_revista"
                    v-model.trim="form.nombre_revista"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Revista Científica Regional"
                  />

                  <p v-if="fieldErrors.nombre_revista" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-numero_revista">
                    Número de la revista
                  </label>

                  <input
                    id="ar-numero_revista"
                    v-model.number="form.numero_revista"
                    class="sgpc-input"
                    type="number"
                    min="1"
                    step="1"
                    inputmode="numeric"
                    placeholder="Ej. 12"
                  />

                  <p v-if="fieldErrors.numero_revista" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.numero_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-link_revista">Link de la revista</label>

                  <input
                    id="ar-link_revista"
                    v-model.trim="form.link_revista"
                    class="sgpc-input"
                    type="url"
                    placeholder="https://..."
                  />

                  <p v-if="fieldErrors.link_revista" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.link_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ar-link_publicacion">
                    Link de la publicación
                  </label>

                  <input
                    id="ar-link_publicacion"
                    v-model.trim="form.link_publicacion"
                    class="sgpc-input"
                    type="url"
                    placeholder="https://..."
                  />

                  <p v-if="fieldErrors.link_publicacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.link_publicacion }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section id="sec-autores" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Autores</h3>
                <p class="sgpc-card-desc">
                  Seleccione autores, participación y orden de firma.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div id="ar-autores-anchor"></div>

              <AutoresSelector
                v-model="form.autores"
                :error="fieldErrors.autores"
              />

              <p v-if="fieldErrors.autores" class="sgpc-hint sgpc-hint-error">
                {{ fieldErrors.autores }}
              </p>
            </div>
          </section>

          <section id="sec-adjuntos" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Adjuntos</h3>
                <p class="sgpc-card-desc">
                  Suba evidencias del artículo en PDF. Puede asignar un nombre a cada archivo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="ar-archivo-input"
                title="Agregar archivos PDF"
                description="Puede cargar hasta 2 PDF complementarios."
                helper-text="Formato permitido: PDF. Máximo 2 archivos y 3 MB por archivo."
                :multiple="true"
                :max-files="2"
                :uses-primary-slot="false"
                :attachment-max-size-mb="3"
              />
            </div>
          </section>

          <div v-if="successMessage" class="sgpc-alert is-success">
            {{ successMessage }}
          </div>

          <div v-if="errorMessage" class="sgpc-alert is-error">
            {{ errorMessage }}
          </div>
        </main>

        <aside class="sgpc-form-aside page-stage page-aside">
          <div class="sgpc-summary-card">
            <div class="sgpc-summary-head">
              <h3>Resumen del registro</h3>
            </div>

            <div class="sgpc-progress">
              <div class="sgpc-progress-row">
                <span>Completitud</span>
                <strong>{{ progressPercent }}%</strong>
              </div>

              <div class="sgpc-progress-bar">
                <span :style="{ width: `${progressPercent}%` }"></span>
              </div>
            </div>

            <div class="sgpc-status-list">
              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredContext }"
                @click="goTo('sec-datos-generales')"
              >
                <div>
                  <strong>Datos generales</strong>
                  <span>{{ hasRequiredContext ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredContext ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredOrigin }"
                @click="goTo('sec-origen')"
              >
                <div>
                  <strong>Origen</strong>
                  <span>{{ hasRequiredOrigin ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredOrigin ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredMain }"
                @click="goTo('sec-principales')"
              >
                <div>
                  <strong>Datos principales</strong>
                  <span>{{ hasRequiredMain ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredMain ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredJournal }"
                @click="goTo('sec-revista')"
              >
                <div>
                  <strong>Revista y enlaces</strong>
                  <span>{{ hasRequiredJournal ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredJournal ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredAuthors }"
                @click="goTo('sec-autores')"
              >
                <div>
                  <strong>Autores</strong>
                  <span>
                    {{ hasRequiredAuthors ? `${form.autores.length} autor(es)` : "Sin autores" }}
                  </span>
                </div>
                <em>{{ hasRequiredAuthors ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasAdjuntos }"
                @click="goTo('sec-adjuntos')"
              >
                <div>
                  <strong>Adjuntos</strong>
                  <span>
                    {{ hasAdjuntos ? `${form.archivos.length} archivo(s)` : "Opcional" }}
                  </span>
                </div>
                <em>{{ hasAdjuntos ? "Completo" : "Opcional" }}</em>
              </button>
            </div>

            <div class="sgpc-summary-actions">
              <button class="sgpc-btn-primary" :disabled="loading" type="submit">
                <span v-if="loading">{{ submitLoadingText }}</span>
                <span v-else>{{ submitText }}</span>
              </button>

              <button
                class="sgpc-btn"
                type="button"
                :disabled="loading"
                @click="limpiarBorrador"
                title="Borra el cache local del formulario"
              >
                Limpiar borrador
              </button>
            </div>
          </div>
        </aside>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from "vue";
import { useRoute } from "vue-router";
import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";
import api from "../../scripts/api/axios";
import {
  restoreDraftArchivos,
  serializeDraftArchivos,
  appendArchivosToFormData,
} from "../../scripts/utils/adjuntosPdf";

const route = useRoute();

const BASE_DRAFT_KEY = "sgpc:draft:articulo_regional:v22";
const STANDARD_CREATE_ENDPOINT = "/publicaciones/articulos/crear/";
const ADMIN_CREATE_ENDPOINT = "/admin/publicaciones/articulos/crear/";

const ERROR_KEY_ALIASES = {
  meta: "archivos",
  archivos_meta: "archivos",
  files: "archivos",
  archivos: "archivos",
  archivo_pdf: "archivos",
  non_field_errors: "admin_context",
};

const FIELD_LABELS = {
  admin_context: "Usuario objetivo",
  facultad: "Facultad",
  carrera: "Carrera",
  proyecto: "Proyecto de investigación",
  area: "Área del conocimiento (UNESCO)",
  subarea: "Subárea del conocimiento (UNESCO)",
  tipo_codigo: "Tipo de artículo",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa",
  nombre_articulo: "Título del artículo",
  base_datos_indexada: "Base de datos / indexación",
  base_datos_otra: "Base de datos (otra)",
  fecha_publicacion: "Fecha de publicación",
  codigo_issn: "ISSN",
  codigo_doi: "DOI",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_revista: "Link de la revista",
  link_publicacion: "Link de la publicación",
  autores: "Autores",
  archivos: "Adjuntos PDF",
};

function createDefaultFormDatos() {
  return {
    facultad: null,
    carrera: null,
    proyecto: null,
    area: null,
    subarea: null,
    pais: null,
    ciudad: null,
  };
}

function createDefaultForm() {
  return {
    origen_tipo: "",
    origen_grado: "",
    nombre_articulo: "",
    base_datos_indexada: "",
    base_datos_otra: "",
    fecha_publicacion: "",
    codigo_issn: "",
    codigo_doi: "",
    nombre_revista: "",
    numero_revista: null,
    link_revista: "",
    link_publicacion: "",
    autores: [],
    archivos: [],
  };
}

function asText(v) {
  if (Array.isArray(v)) return v.map(asText).join(", ");
  if (v != null && typeof v === "object") {
    return Object.values(v).map(asText).join(", ");
  }
  if (v == null) return "";
  return String(v);
}

function normalizeErrorKey(key) {
  return ERROR_KEY_ALIASES[key] || key;
}

function normalizeDrfErrors(data) {
  if (!data) {
    return {
      fields: {},
      message: "No se pudo guardar. Verifique los campos.",
    };
  }

  const rawErrors =
    data?.errors && typeof data.errors === "object"
      ? data.errors
      : typeof data === "object" && data !== null
        ? data
        : null;

  if (rawErrors && typeof rawErrors === "object") {
    const fields = {};
    let first = null;

    Object.entries(rawErrors).forEach(([k, v]) => {
      if (k === "detail") return;
      const normalizedKey = normalizeErrorKey(k);
      fields[normalizedKey] = asText(v);
      if (!first) first = normalizedKey;
    });

    if (Object.keys(fields).length) {
      let message = "No se pudo registrar. Revise los campos marcados.";

      if (fields.admin_context) {
        message = fields.admin_context;
      } else if (fields.autores) {
        message =
          "Revise la sección de Autores: debe existir al menos un autor y el orden debe ser válido.";
      } else if (fields.archivos) {
        message = "Revise la sección de Adjuntos PDF.";
      } else if (first) {
        const label = FIELD_LABELS[first] || first;
        message = `${label}: ${fields[first]}`;
      }

      return { fields, message };
    }
  }

  if (typeof data?.detail === "string") {
    return { fields: {}, message: data.detail };
  }

  return {
    fields: {},
    message: "No se pudo guardar. Verifique los campos.",
  };
}

function firstErrorField(fields) {
  const order = [
    "admin_context",
    "tipo_codigo",
    "facultad",
    "carrera",
    "proyecto",
    "area",
    "subarea",
    "origen_tipo",
    "origen_grado",
    "fecha_publicacion",
    "nombre_articulo",
    "base_datos_indexada",
    "base_datos_otra",
    "codigo_issn",
    "codigo_doi",
    "nombre_revista",
    "numero_revista",
    "link_revista",
    "link_publicacion",
    "autores",
    "archivos",
  ];

  for (const k of order) if (fields?.[k]) return k;
  return Object.keys(fields || {})[0] || null;
}

function appendFormValue(fd, key, value) {
  if (value === null || value === "" || value === undefined) return;
  if (typeof value === "number" && !Number.isFinite(value)) return;
  fd.append(key, String(value));
}

function normalizeComparableText(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

const adminContext = ref({
  usuarioId: null,
  autorId: null,
  usuarioNombre: "",
  autorNombre: "",
});

const formDatos = ref(createDefaultFormDatos());
const form = ref(createDefaultForm());

const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const fieldErrors = ref({});
const draftInfo = ref("");

let draftTimer = null;
let draftEnabled = true;

const isAdminDelegado = computed(() => {
  const path = String(route.path || "");
  const q = route.query || {};
  const p = route.params || {};

  return Boolean(
    route.meta?.delegatedPublication ||
      path.startsWith("/admin/publicaciones/usuario/") ||
      p.usuarioId ||
      q.modo === "delegado" ||
      q.delegado === "1" ||
      q.admin === "1"
  );
});

const storageKey = computed(() => {
  if (!isAdminDelegado.value) {
    return `${BASE_DRAFT_KEY}:self`;
  }

  const usuarioId =
    adminContext.value.usuarioId ||
    Number(route.params?.usuarioId || 0) ||
    "sin-usuario";

  return `${BASE_DRAFT_KEY}:admin:${usuarioId}`;
});

const adminReady = computed(() => {
  if (!isAdminDelegado.value) return true;
  return Boolean(adminContext.value.usuarioId);
});

const adminDisplayUsuario = computed(() => {
  return (
    adminContext.value.usuarioNombre ||
    `ID ${adminContext.value.usuarioId || "—"}`
  );
});

const adminDisplayAutor = computed(() => {
  if (adminContext.value.autorNombre) return adminContext.value.autorNombre;
  if (adminContext.value.autorId) return `ID ${adminContext.value.autorId}`;
  return "Se resolverá automáticamente";
});

const showAutorObjetivo = computed(() => {
  if (!isAdminDelegado.value) return false;

  const usuarioNombre = normalizeComparableText(adminContext.value.usuarioNombre);
  const autorNombre = normalizeComparableText(adminContext.value.autorNombre);

  if (autorNombre && usuarioNombre && autorNombre !== usuarioNombre) {
    return true;
  }

  if (
    adminContext.value.autorId &&
    adminContext.value.usuarioId &&
    adminContext.value.autorId !== adminContext.value.usuarioId
  ) {
    return true;
  }

  if (adminContext.value.autorId && !adminContext.value.usuarioNombre) {
    return true;
  }

  return false;
});

const pageKicker = computed(() =>
  isAdminDelegado.value ? "Administración · Artículos" : "Artículos"
);

const pageTitle = computed(() => "Registrar Artículo Regional");

const pageSubtitle = computed(() => {
  if (isAdminDelegado.value) {
    return "Registre datos generales, origen, indexación regional, revista, enlaces, autores y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios.";
  }

  return "Registre datos generales, origen, indexación regional, revista, enlaces, autores y adjuntos. Los campos marcados con * son obligatorios.";
});

const submitText = computed(() => "Registrar artículo regional");
const submitLoadingText = computed(() => "Guardando...");

const createEndpoint = computed(() =>
  isAdminDelegado.value ? ADMIN_CREATE_ENDPOINT : STANDARD_CREATE_ENDPOINT
);

const hasRequiredContext = computed(() => {
  const dg = formDatos.value || {};
  return !!(dg.facultad && dg.carrera && dg.area && dg.subarea);
});

const hasRequiredOrigin = computed(() => {
  if (!form.value.origen_tipo) return false;
  if (form.value.origen_tipo === "tic") {
    return !!String(form.value.origen_grado || "").trim();
  }
  return true;
});

const hasRequiredMain = computed(() => {
  if (!form.value.fecha_publicacion) return false;
  if (!String(form.value.nombre_articulo || "").trim()) return false;
  if (!String(form.value.base_datos_indexada || "").trim()) return false;

  if (
    form.value.base_datos_indexada === "otra" &&
    !String(form.value.base_datos_otra || "").trim()
  ) {
    return false;
  }

  return true;
});

const hasRequiredJournal = computed(() => {
  if (!String(form.value.codigo_issn || "").trim()) return false;
  if (!String(form.value.nombre_revista || "").trim()) return false;
  return true;
});

const hasRequiredAuthors = computed(() => {
  return Array.isArray(form.value.autores) && form.value.autores.length > 0;
});

const hasAdjuntos = computed(() => {
  return Array.isArray(form.value.archivos) && form.value.archivos.length > 0;
});

const requiredSections = computed(() => {
  return [
    { key: "datos", done: hasRequiredContext.value },
    { key: "origen", done: hasRequiredOrigin.value },
    { key: "principal", done: hasRequiredMain.value },
    { key: "revista", done: hasRequiredJournal.value },
    { key: "autores", done: hasRequiredAuthors.value },
  ];
});

const completedRequiredCount = computed(() => {
  return requiredSections.value.filter((s) => s.done).length;
});

const totalRequiredCount = computed(() => {
  return requiredSections.value.length;
});

const progressPercent = computed(() => {
  if (!totalRequiredCount.value) return 0;
  return Math.round(
    (completedRequiredCount.value / totalRequiredCount.value) * 100
  );
});

const goTo = (id) => {
  const el = document.getElementById(id);
  el?.scrollIntoView({ behavior: "smooth", block: "start" });
};

function focusField(key) {
  const map = {
    admin_context: "ar-admin-context-anchor",
    origen_tipo: "ar-origen_tipo",
    origen_grado: "ar-origen_grado",
    fecha_publicacion: "ar-fecha_publicacion",
    nombre_articulo: "ar-nombre_articulo",
    base_datos_indexada: "ar-base_datos_indexada",
    base_datos_otra: "ar-base_datos_otra",
    codigo_issn: "ar-codigo_issn",
    codigo_doi: "ar-codigo_doi",
    nombre_revista: "ar-nombre_revista",
    numero_revista: "ar-numero_revista",
    link_revista: "ar-link_revista",
    link_publicacion: "ar-link_publicacion",
    autores: "ar-autores-anchor",
    archivos: "ar-archivo-input",
  };

  const el =
    document.getElementById(`dg-${key}`) ||
    document.getElementById(map[key] || "");

  if (!el) return;

  if (key === "autores" || key === "archivos" || key === "admin_context") {
    el.scrollIntoView?.({ behavior: "smooth", block: "center" });
    return;
  }

  if (typeof el.focus === "function") el.focus({ preventScroll: false });
  else el.scrollIntoView?.({ behavior: "smooth", block: "center" });
}

function hydrateAdminContextFromRoute() {
  const q = route.query || {};
  const p = route.params || {};

  const usuarioId = Number(
    p.usuarioId || q.usuario_id || q.usuarioId || q.user_id || 0
  );

  const autorId = Number(
    p.autorId || q.autor_id || q.autorId || 0
  );

  adminContext.value = {
    usuarioId: Number.isFinite(usuarioId) && usuarioId > 0 ? usuarioId : null,
    autorId: Number.isFinite(autorId) && autorId > 0 ? autorId : null,
    usuarioNombre: String(
      q.usuario_nombre || q.usuarioNombre || q.user_name || ""
    ).trim(),
    autorNombre: String(
      q.autor_nombre || q.autorNombre || q.author_name || ""
    ).trim(),
  };
}

function saveDraft() {
  if (!draftEnabled) return;

  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => {
    try {
      const payload = {
        formDatos: {
          ...formDatos.value,
          pais: null,
          ciudad: null,
        },
        form: {
          origen_tipo: form.value.origen_tipo,
          origen_grado: form.value.origen_grado,
          nombre_articulo: form.value.nombre_articulo,
          base_datos_indexada: form.value.base_datos_indexada,
          base_datos_otra: form.value.base_datos_otra,
          fecha_publicacion: form.value.fecha_publicacion,
          codigo_issn: form.value.codigo_issn,
          codigo_doi: form.value.codigo_doi,
          nombre_revista: form.value.nombre_revista,
          numero_revista: form.value.numero_revista,
          link_revista: form.value.link_revista,
          link_publicacion: form.value.link_publicacion,
          autores: form.value.autores,
          archivos: serializeDraftArchivos(form.value.archivos),
        },
        updatedAt: new Date().toISOString(),
      };

      localStorage.setItem(storageKey.value, JSON.stringify(payload));
    } catch (e) {
      console.warn("No se pudo guardar borrador:", e);
    }
  }, 250);
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(storageKey.value);
    if (!raw) return;

    const parsed = JSON.parse(raw);

    if (parsed?.formDatos) {
      formDatos.value = {
        ...createDefaultFormDatos(),
        ...parsed.formDatos,
        pais: null,
        ciudad: null,
      };
    }

    if (parsed?.form) {
      const incoming = parsed.form || {};

      form.value = {
        ...createDefaultForm(),
        origen_tipo: incoming.origen_tipo || "",
        origen_grado: incoming.origen_grado || "",
        nombre_articulo: incoming.nombre_articulo || "",
        base_datos_indexada: incoming.base_datos_indexada || "",
        base_datos_otra: incoming.base_datos_otra || "",
        fecha_publicacion: incoming.fecha_publicacion || "",
        codigo_issn: incoming.codigo_issn || "",
        codigo_doi: incoming.codigo_doi || "",
        nombre_revista: incoming.nombre_revista || "",
        numero_revista: incoming.numero_revista ?? null,
        link_revista: incoming.link_revista || "",
        link_publicacion: incoming.link_publicacion || "",
        autores: Array.isArray(incoming.autores) ? incoming.autores : [],
        archivos: restoreDraftArchivos(incoming.archivos),
      };
    }

    if (parsed?.updatedAt) {
      const dt = new Date(parsed.updatedAt);
      draftInfo.value = `Se recuperó un borrador guardado (${dt.toLocaleString()}).`;
    } else {
      draftInfo.value = "Se recuperó un borrador guardado.";
    }

    successMessage.value = "";
    errorMessage.value = "";
  } catch (e) {
    console.warn("No se pudo cargar borrador:", e);
  }
}

function clearDraftStorage() {
  try {
    localStorage.removeItem(storageKey.value);
  } catch (e) {
    console.warn("No se pudo limpiar borrador:", e);
  }
}

function disableDraftTemporarily() {
  draftEnabled = false;
  nextTick(() => {
    draftEnabled = true;
  });
}

function buildAutoresPayload() {
  const raw = Array.isArray(form.value.autores) ? form.value.autores : [];

  return raw
    .map((a, index) => {
      const id = Number(a?.autor_id ?? a?.id ?? a?.autor?.id);
      if (!Number.isFinite(id) || id <= 0) return null;

      const orden = index + 1;

      return {
        autor_id: id,
        orden,
        rol_autoria: orden === 1 ? "principal" : "coautor",
      };
    })
    .filter(Boolean);
}

function hasPendingRecoveredFiles() {
  return (Array.isArray(form.value.archivos) ? form.value.archivos : []).some(
    (it) => !it?.file && it?.originalName
  );
}

function validateAdminContext() {
  if (!isAdminDelegado.value) return null;

  if (!adminContext.value.usuarioId) {
    return "Debe llegar al formulario con un usuario objetivo válido.";
  }

  return null;
}

function validateFront() {
  const fe = {};
  const dg = formDatos.value || {};

  if (isAdminDelegado.value && !adminContext.value.usuarioId) {
    fe.admin_context =
      "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
  }

  if (!dg.facultad) fe.facultad = "Seleccione una facultad.";
  if (!dg.carrera) fe.carrera = "Seleccione una carrera.";
  if (!dg.area) fe.area = "Seleccione un área del conocimiento (UNESCO).";
  if (!dg.subarea) fe.subarea = "Seleccione una subárea del conocimiento (UNESCO).";

  if (!String(form.value.origen_tipo || "").trim()) {
    fe.origen_tipo = "Seleccione el origen.";
  }

  if (
    form.value.origen_tipo === "tic" &&
    !String(form.value.origen_grado || "").trim()
  ) {
    fe.origen_grado = "Campo obligatorio.";
  }

  if (!form.value.fecha_publicacion) {
    fe.fecha_publicacion = "Campo obligatorio.";
  }

  if (!String(form.value.nombre_articulo || "").trim()) {
    fe.nombre_articulo = "Campo obligatorio.";
  }

  if (!String(form.value.base_datos_indexada || "").trim()) {
    fe.base_datos_indexada = "Campo obligatorio.";
  }

  if (
    form.value.base_datos_indexada === "otra" &&
    !String(form.value.base_datos_otra || "").trim()
  ) {
    fe.base_datos_otra =
      "Debe especificar la base de datos cuando selecciona “Otra”.";
  }

  if (!String(form.value.codigo_issn || "").trim()) {
    fe.codigo_issn = "Campo obligatorio.";
  }

  if (!String(form.value.nombre_revista || "").trim()) {
    fe.nombre_revista = "Campo obligatorio.";
  }

  if (!Array.isArray(form.value.autores) || form.value.autores.length === 0) {
    fe.autores = "Debe registrar al menos un autor.";
  }

  if (hasPendingRecoveredFiles()) {
    fe.archivos =
      "Hay adjuntos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
  }

  fieldErrors.value = fe;

  if (Object.keys(fe).length) {
    errorMessage.value = "Complete los campos obligatorios antes de guardar.";
    successMessage.value = "";
    const first = firstErrorField(fe);
    if (first) focusField(first);
    return false;
  }

  return true;
}

function resetForm() {
  fieldErrors.value = {};
  draftInfo.value = "";
  successMessage.value = "";
  errorMessage.value = "";

  formDatos.value = createDefaultFormDatos();
  form.value = createDefaultForm();
}

function limpiarBorrador() {
  disableDraftTemporarily();
  clearDraftStorage();
  resetForm();
  successMessage.value = "Borrador eliminado.";
  errorMessage.value = "";
}

function handleRouteContextChange() {
  hydrateAdminContextFromRoute();
  disableDraftTemporarily();
  resetForm();
  loadDraft();
}

async function registrarArticuloRegional() {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";
  fieldErrors.value = {};

  try {
    if (!validateFront()) {
      loading.value = false;
      return;
    }

    const autoresPayload = buildAutoresPayload();
    if (!autoresPayload.length) {
      fieldErrors.value = {
        ...fieldErrors.value,
        autores: "Los autores seleccionados no tienen ID válido.",
      };
      errorMessage.value = "Revise la sección de autores.";
      focusField("autores");
      loading.value = false;
      return;
    }

    const adminValidationError = validateAdminContext();
    if (adminValidationError) {
      fieldErrors.value = {
        ...fieldErrors.value,
        admin_context: adminValidationError,
      };
      errorMessage.value = adminValidationError;
      successMessage.value = "";
      focusField("admin_context");
      loading.value = false;
      return;
    }

    const fd = new FormData();
    fd.append("tipo_codigo", "articulo_regional");

    const dgPayload = {
      ...formDatos.value,
      pais: null,
      ciudad: null,
    };

    Object.entries(dgPayload).forEach(([key, value]) => {
      if (key === "pais" || key === "ciudad") return;
      appendFormValue(fd, key, value);
    });

    appendFormValue(fd, "origen_tipo", form.value.origen_tipo || "ninguno");

    if (form.value.origen_tipo === "tic") {
      appendFormValue(fd, "origen_grado", form.value.origen_grado);
    }

    const campos = [
      "nombre_articulo",
      "base_datos_indexada",
      "base_datos_otra",
      "fecha_publicacion",
      "codigo_issn",
      "codigo_doi",
      "nombre_revista",
      "numero_revista",
      "link_revista",
      "link_publicacion",
    ];

    campos.forEach((key) => {
      if (
        key === "base_datos_otra" &&
        form.value.base_datos_indexada !== "otra"
      ) {
        return;
      }

      appendFormValue(fd, key, form.value[key]);
    });

    fd.append("autores", JSON.stringify(autoresPayload));

    if (isAdminDelegado.value && adminContext.value.usuarioId) {
      fd.append("usuario_objetivo_id", String(adminContext.value.usuarioId));

      if (adminContext.value.autorId) {
        fd.append("autor_objetivo_id", String(adminContext.value.autorId));
      }
    }

    appendArchivosToFormData(fd, form.value.archivos, {
      primaryField: null,
      filesField: "archivos",
      metaField: "archivos_meta",
    });

    await api.post(createEndpoint.value, fd);

    disableDraftTemporarily();
    clearDraftStorage();
    resetForm();

    successMessage.value = isAdminDelegado.value
      ? "Artículo regional registrado correctamente para el usuario seleccionado."
      : "Artículo registrado correctamente.";
    errorMessage.value = "";
  } catch (error) {
    const status = error?.response?.status;
    const data = error?.response?.data;

    if (status === 401) {
      errorMessage.value = "Sesión expirada. Vuelva a iniciar sesión.";
      successMessage.value = "";
      loading.value = false;
      return;
    }

    const normalized = normalizeDrfErrors(data);
    fieldErrors.value = normalized.fields || {};
    errorMessage.value =
      normalized.message || "Error al registrar el artículo. Verifique los campos.";
    successMessage.value = "";

    const first = firstErrorField(fieldErrors.value);
    if (first) focusField(first);

    console.error("❌ Error backend:", data || error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  formDatos.value.pais = null;
  formDatos.value.ciudad = null;
  hydrateAdminContextFromRoute();
  loadDraft();
});

onBeforeUnmount(() => {
  clearTimeout(draftTimer);
});

watch(formDatos, saveDraft, { deep: true });
watch(form, saveDraft, { deep: true });

watch(
  () => route.fullPath,
  () => {
    handleRouteContextChange();
  }
);

watch(
  () => form.value.origen_tipo,
  (v) => {
    if (v !== "tic") form.value.origen_grado = "";
  }
);

watch(
  () => form.value.base_datos_indexada,
  (v) => {
    if (v !== "otra") form.value.base_datos_otra = "";
  }
);
</script>

<style src="../componentes/sgpc-fcvt.css"></style>

<style scoped>
.sgpc-alert {
  white-space: pre-line;
}

.sgpc-card--admin-context {
  border-style: dashed;
}

.sgpc-admin-context {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.sgpc-admin-context__item {
  border: 1px solid var(--border-color, rgba(17, 17, 17, 0.12));
  background: color-mix(
    in srgb,
    var(--bg-card, #ffffff) 90%,
    var(--bg-soft, #f4f2ed) 10%
  );
  border-radius: 18px;
  padding: 14px 16px;
}

.sgpc-admin-context__label {
  display: block;
  font-size: 0.82rem;
  color: var(--text-secondary, #5f5a53);
  margin-bottom: 6px;
}

.sgpc-admin-context__value {
  display: block;
  font-size: 0.98rem;
  color: var(--text-primary, #111111);
}

@media (max-width: 980px) {
  .sgpc-admin-context {
    grid-template-columns: 1fr;
  }
}
</style>