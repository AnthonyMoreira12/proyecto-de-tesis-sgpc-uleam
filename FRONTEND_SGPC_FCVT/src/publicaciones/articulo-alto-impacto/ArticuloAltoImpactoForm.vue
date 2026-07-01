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
        @submit.prevent="registrarArticulo"
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
              <div id="ai-admin-context-anchor"></div>

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
                  Clasificación institucional del registro.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <DatosGenerales
                v-model="form.datos_generales"
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
                  Relación académica del artículo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-origen_tipo">
                    Origen de la publicación <span class="req">*</span>
                  </label>

                  <select
                    id="ai-origen_tipo"
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
                  <label class="sgpc-label" for="ai-origen_grado">
                    Grado / programa
                    <span v-if="form.origen_tipo === 'tic'" class="req">*</span>
                  </label>

                  <input
                    id="ai-origen_grado"
                    v-model.trim="form.origen_grado"
                    class="sgpc-input"
                    type="text"
                    :disabled="form.origen_tipo !== 'tic'"
                    :required="form.origen_tipo === 'tic'"
                    placeholder="Ej. Ingeniería en TI / Ingeniería de Software / ..."
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

          <section id="sec-articulo" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Información del artículo</h3>
                <p class="sgpc-card-desc">
                  Datos básicos de la publicación.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="ai-nombre_articulo">
                    Título del artículo <span class="req">*</span>
                  </label>

                  <input
                    id="ai-nombre_articulo"
                    v-model.trim="form.nombre_articulo"
                    class="sgpc-input"
                    type="text"
                    required
                  />

                  <p v-if="fieldErrors.nombre_articulo" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_articulo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-fecha_publicacion">
                    Fecha de publicación <span class="req">*</span>
                  </label>

                  <input
                    id="ai-fecha_publicacion"
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
                  <label class="sgpc-label" for="ai-tipo_articulo">
                    Clasificación
                  </label>

                  <input
                    id="ai-tipo_articulo"
                    class="sgpc-input"
                    type="text"
                    :value="'Alto impacto'"
                    disabled
                  />
                </div>
              </div>
            </div>
          </section>

          <section id="sec-revista" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Revista e indicadores</h3>
                <p class="sgpc-card-desc">
                  Información editorial, enlaces e indicadores de alto impacto.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-nombre_revista">
                    Nombre de la revista <span class="req">*</span>
                  </label>

                  <input
                    id="ai-nombre_revista"
                    v-model.trim="form.nombre_revista"
                    class="sgpc-input"
                    type="text"
                    required
                  />

                  <p v-if="fieldErrors.nombre_revista" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_revista }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-numero_revista">
                    Número de la revista
                  </label>

                  <input
                    id="ai-numero_revista"
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
                  <label class="sgpc-label" for="ai-codigo_doi">
                    Código DOI
                  </label>

                  <input
                    id="ai-codigo_doi"
                    v-model.trim="form.codigo_doi"
                    class="sgpc-input"
                    type="text"
                    placeholder="Ej. 10.1234/xxxxx"
                  />

                  <p v-if="fieldErrors.codigo_doi" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_doi }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-codigo_issn">
                    Código ISSN <span class="req">*</span>
                  </label>

                  <input
                    id="ai-codigo_issn"
                    v-model.trim="form.codigo_issn"
                    class="sgpc-input"
                    type="text"
                    required
                  />

                  <p v-if="fieldErrors.codigo_issn" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_issn }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-link_revista">
                    Link de la revista
                  </label>

                  <input
                    id="ai-link_revista"
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
                  <label class="sgpc-label" for="ai-link_publicacion">
                    Link de la publicación
                  </label>

                  <input
                    id="ai-link_publicacion"
                    v-model.trim="form.link_publicacion"
                    class="sgpc-input"
                    type="url"
                    placeholder="https://..."
                  />

                  <p v-if="fieldErrors.link_publicacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.link_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-factor_impacto">
                    Factor de impacto
                  </label>

                  <select
                    id="ai-factor_impacto"
                    v-model="form.factor_impacto"
                    class="sgpc-input"
                  >
                    <option value="">No aplica / no disponible</option>
                    <option value="sjr">SJR (Scimago Journal Rank)</option>
                    <option value="jcr">JCR (Journal Citation Reports)</option>
                  </select>

                  <p v-if="fieldErrors.factor_impacto" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.factor_impacto }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="ai-cuartil">
                    Cuartil
                  </label>

                  <select id="ai-cuartil" v-model="form.cuartil" class="sgpc-input">
                    <option value="">Seleccione...</option>
                    <option value="q1">Q1</option>
                    <option value="q2">Q2</option>
                    <option value="q3">Q3</option>
                    <option value="q4">Q4</option>
                    <option value="sin_cuartil">Sin cuartil</option>
                  </select>

                  <p v-if="fieldErrors.cuartil" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.cuartil }}
                  </p>
                </div>

                <div
                  v-if="form.factor_impacto === 'sjr'"
                  class="sgpc-field sgpc-col-span-12"
                >
                  <label class="sgpc-label" for="ai-sjr">
                    SJR (valor)
                  </label>

                  <input
                    id="ai-sjr"
                    v-model.trim="form.sjr"
                    class="sgpc-input"
                    type="text"
                    placeholder="Ej. 0.45"
                  />

                  <p v-if="fieldErrors.sjr" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.sjr }}
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
                  Seleccione autores y defina su jerarquía y orden.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div id="ai-autores-anchor"></div>

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
                  Adjunte el PDF principal del artículo, carta de aceptación y soportes relacionados.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="ai-archivo-input"
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

          <div v-if="mensaje" :class="['sgpc-alert', `is-${mensajeTipo}`]">
            {{ mensaje }}
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
                  <span>{{ hasRequiredOrigin ? "Completo" : "Seleccione origen" }}</span>
                </div>
                <em>{{ hasRequiredOrigin ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredArticle }"
                @click="goTo('sec-articulo')"
              >
                <div>
                  <strong>Artículo</strong>
                  <span>{{ hasRequiredArticle ? "Completo" : "Título o fecha pendientes" }}</span>
                </div>
                <em>{{ hasRequiredArticle ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredJournal }"
                @click="goTo('sec-revista')"
              >
                <div>
                  <strong>Revista</strong>
                  <span>{{ hasRequiredJournal ? "Completo" : "Revista o ISSN pendientes" }}</span>
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
                  <span>{{ hasRequiredAuthors ? `${form.autores.length} autor(es)` : "Sin autores" }}</span>
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
                  <span>{{ hasAdjuntos ? `${form.archivos.length} archivo(s)` : "Opcional" }}</span>
                </div>
                <em>{{ hasAdjuntos ? "Completo" : "Opcional" }}</em>
              </button>
            </div>

            <div class="sgpc-summary-actions">
              <button
                class="sgpc-btn-primary"
                type="submit"
                :disabled="loading"
              >
                <span v-if="loading">{{ submitLoadingText }}</span>
                <span v-else>{{ submitText }}</span>
              </button>

              <button
                type="button"
                class="sgpc-btn"
                @click="clearDraft"
                :disabled="loading"
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

<script>
import DatosGenerales from "../componentes/DatosGenerales.vue";
import AutoresSelector from "../componentes/AutoresSelector.vue";
import AdjuntosPdfUploader from "../componentes/AdjuntosPdfUploader.vue";
import api from "../../scripts/api/axios";
import {
  restoreDraftArchivos,
  serializeDraftArchivos,
  appendArchivosToFormData,
} from "../../scripts/utils/adjuntosPdf";

const BASE_STORAGE_KEY = "sgpc-articulo-alto-impacto-draft:v22";

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
  nombre_articulo: "Título del artículo",
  fecha_publicacion: "Fecha de publicación",
  codigo_doi: "DOI",
  codigo_issn: "ISSN",
  nombre_revista: "Nombre de la revista",
  numero_revista: "Número de la revista",
  link_publicacion: "Link de la publicación",
  link_revista: "Link de la revista",
  factor_impacto: "Factor de impacto",
  cuartil: "Cuartil",
  sjr: "SJR",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa",
  autores: "Autores",
  archivos: "Adjuntos PDF",
};

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
    "facultad",
    "carrera",
    "proyecto",
    "area",
    "subarea",
    "tipo_codigo",
    "origen_tipo",
    "origen_grado",
    "nombre_articulo",
    "fecha_publicacion",
    "nombre_revista",
    "numero_revista",
    "codigo_issn",
    "codigo_doi",
    "link_revista",
    "link_publicacion",
    "factor_impacto",
    "cuartil",
    "sjr",
    "autores",
    "archivos",
  ];

  for (const k of order) if (fields?.[k]) return k;
  return Object.keys(fields || {})[0] || null;
}

function normalizeCuartil(value) {
  const raw = String(value ?? "").trim().toLowerCase();

  if (!raw) return "";

  if (["sin cuartil", "sin-cuartil", "sin_cuartil"].includes(raw)) {
    return "sin_cuartil";
  }

  return raw;
}

function appendIfPresent(fd, key, value) {
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

export default {
  name: "ArticuloAltoImpactoRegistro",

  components: {
    DatosGenerales,
    AutoresSelector,
    AdjuntosPdfUploader,
  },

  data() {
    return {
      loading: false,
      mensaje: "",
      mensajeTipo: "",
      fieldErrors: {},
      draftInfo: "",
      _draftTimer: null,
      _draftEnabled: true,

      adminContext: {
        usuarioId: null,
        autorId: null,
        usuarioNombre: "",
        autorNombre: "",
      },

      form: {
        datos_generales: {
          facultad: null,
          carrera: null,
          proyecto: null,
          area: null,
          subarea: null,
          pais: null,
          ciudad: null,
        },

        origen_tipo: "",
        origen_grado: "",

        nombre_articulo: "",
        fecha_publicacion: "",

        codigo_doi: "",
        codigo_issn: "",
        nombre_revista: "",
        numero_revista: null,
        link_revista: "",
        link_publicacion: "",

        factor_impacto: "",
        cuartil: "",
        sjr: "",

        autores: [],
        archivos: [],
      },
    };
  },

  computed: {
    isAdminDelegado() {
      const path = String(this.$route?.path || "");
      const q = this.$route?.query || {};
      const p = this.$route?.params || {};

      return Boolean(
        this.$route?.meta?.delegatedPublication ||
        path.startsWith("/admin/publicaciones/usuario/") ||
        p.usuarioId ||
        q.modo === "delegado" ||
        q.delegado === "1" ||
        q.admin === "1"
      );
    },

    storageKey() {
      if (!this.isAdminDelegado) {
        return `${BASE_STORAGE_KEY}:self`;
      }

      const usuarioId =
        this.adminContext?.usuarioId ||
        Number(this.$route?.params?.usuarioId || 0) ||
        "sin-usuario";

      return `${BASE_STORAGE_KEY}:admin:${usuarioId}`;
    },

    adminReady() {
      if (!this.isAdminDelegado) return true;
      return Boolean(this.adminContext.usuarioId);
    },

    adminDisplayUsuario() {
      return (
        this.adminContext.usuarioNombre ||
        `ID ${this.adminContext.usuarioId || "—"}`
      );
    },

    adminDisplayAutor() {
      if (this.adminContext.autorNombre) return this.adminContext.autorNombre;
      if (this.adminContext.autorId) return `ID ${this.adminContext.autorId}`;
      return "Se resolverá automáticamente";
    },

    showAutorObjetivo() {
      if (!this.isAdminDelegado) return false;

      const usuarioNombre = normalizeComparableText(this.adminContext.usuarioNombre);
      const autorNombre = normalizeComparableText(this.adminContext.autorNombre);

      if (autorNombre && usuarioNombre && autorNombre !== usuarioNombre) {
        return true;
      }

      if (
        this.adminContext.autorId &&
        this.adminContext.usuarioId &&
        this.adminContext.autorId !== this.adminContext.usuarioId
      ) {
        return true;
      }

      if (this.adminContext.autorId && !this.adminContext.usuarioNombre) {
        return true;
      }

      return false;
    },

    pageKicker() {
      return this.isAdminDelegado
        ? "Administración · Artículos"
        : "Artículos";
    },

    pageTitle() {
      return "Registrar Artículo de Alto Impacto";
    },

    pageSubtitle() {
      if (this.isAdminDelegado) {
        return "Registre datos bibliográficos, editoriales, indicadores de alto impacto, autoría y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios.";
      }

      return "Registre datos bibliográficos, editoriales, indicadores de alto impacto, autoría y adjuntos del artículo. Los campos marcados con * son obligatorios.";
    },

    submitText() {
      return "Registrar artículo";
    },

    submitLoadingText() {
      return "Guardando...";
    },

    createEndpoint() {
      return this.isAdminDelegado
        ? ADMIN_CREATE_ENDPOINT
        : STANDARD_CREATE_ENDPOINT;
    },

    hasRequiredContext() {
      const dg = this.form.datos_generales || {};
      return !!(dg.facultad && dg.carrera && dg.area && dg.subarea);
    },

    hasRequiredOrigin() {
      if (!this.form.origen_tipo) return false;
      if (this.form.origen_tipo === "tic") {
        return !!String(this.form.origen_grado || "").trim();
      }
      return true;
    },

    hasRequiredArticle() {
      return !!(
        String(this.form.nombre_articulo || "").trim() &&
        this.form.fecha_publicacion
      );
    },

    hasRequiredJournal() {
      if (!String(this.form.nombre_revista || "").trim()) return false;
      if (!String(this.form.codigo_issn || "").trim()) return false;

      if (
        this.form.factor_impacto === "sjr" &&
        !String(this.form.sjr || "").trim()
      ) {
        return false;
      }

      return true;
    },

    hasRequiredAuthors() {
      return Array.isArray(this.form.autores) && this.form.autores.length > 0;
    },

    hasAdjuntos() {
      return Array.isArray(this.form.archivos) && this.form.archivos.length > 0;
    },

    requiredSections() {
      return [
        { key: "datos", done: this.hasRequiredContext },
        { key: "origen", done: this.hasRequiredOrigin },
        { key: "articulo", done: this.hasRequiredArticle },
        { key: "revista", done: this.hasRequiredJournal },
        { key: "autores", done: this.hasRequiredAuthors },
      ];
    },

    completedRequiredCount() {
      return this.requiredSections.filter((s) => s.done).length;
    },

    totalRequiredCount() {
      return this.requiredSections.length;
    },

    progressPercent() {
      if (!this.totalRequiredCount) return 0;
      return Math.round(
        (this.completedRequiredCount / this.totalRequiredCount) * 100
      );
    },
  },

  created() {
    this.hydrateAdminContextFromRoute();
    this.loadDraft();
  },

  beforeUnmount() {
    clearTimeout(this._draftTimer);
  },

  watch: {
    form: {
      deep: true,
      handler(val) {
        if (!this._draftEnabled) return;

        clearTimeout(this._draftTimer);
        this._draftTimer = setTimeout(() => {
          const payload = {
            form: {
              datos_generales: {
                ...val.datos_generales,
                pais: null,
                ciudad: null,
              },
              origen_tipo: val.origen_tipo,
              origen_grado: val.origen_grado,
              nombre_articulo: val.nombre_articulo,
              fecha_publicacion: val.fecha_publicacion,
              codigo_doi: val.codigo_doi,
              codigo_issn: val.codigo_issn,
              nombre_revista: val.nombre_revista,
              numero_revista: val.numero_revista,
              link_revista: val.link_revista,
              link_publicacion: val.link_publicacion,
              factor_impacto: val.factor_impacto,
              cuartil: normalizeCuartil(val.cuartil),
              sjr: val.sjr,
              autores: val.autores,
              archivos: serializeDraftArchivos(val.archivos),
            },
            updatedAt: new Date().toISOString(),
          };

          try {
            localStorage.setItem(this.storageKey, JSON.stringify(payload));
          } catch (e) {
            console.warn("No se pudo guardar el borrador.", e);
          }
        }, 250);
      },
    },

    "$route.fullPath"() {
      this.handleRouteContextChange();
    },

    "form.origen_tipo"(v) {
      if (v !== "tic") this.form.origen_grado = "";
    },

    "form.factor_impacto"(v) {
      if (v !== "sjr") this.form.sjr = "";
    },

    "form.cuartil"(v) {
      const normalized = normalizeCuartil(v);
      if (normalized !== v) this.form.cuartil = normalized;
    },
  },

  methods: {
    handleRouteContextChange() {
      this.hydrateAdminContextFromRoute();
      this.disableDraftTemporarily();
      this.resetForm();
      this.loadDraft();
    },

    hydrateAdminContextFromRoute() {
      const q = this.$route?.query || {};
      const p = this.$route?.params || {};

      const usuarioId = Number(
        p.usuarioId || q.usuario_id || q.usuarioId || q.user_id || 0
      );

      const autorId = Number(
        p.autorId || q.autor_id || q.autorId || 0
      );

      this.adminContext = {
        usuarioId:
          Number.isFinite(usuarioId) && usuarioId > 0 ? usuarioId : null,
        autorId: Number.isFinite(autorId) && autorId > 0 ? autorId : null,
        usuarioNombre: String(
          q.usuario_nombre || q.usuarioNombre || q.user_name || ""
        ).trim(),
        autorNombre: String(
          q.autor_nombre || q.autorNombre || q.author_name || ""
        ).trim(),
      };
    },

    loadDraft() {
      const raw = localStorage.getItem(this.storageKey);
      if (!raw) return;

      try {
        const parsed = JSON.parse(raw);
        const recovered = parsed.form || parsed;

        this.form = {
          ...this.form,
          ...recovered,
          datos_generales: {
            ...this.form.datos_generales,
            ...(recovered?.datos_generales || {}),
            pais: null,
            ciudad: null,
          },
          cuartil: normalizeCuartil(recovered?.cuartil),
          autores: Array.isArray(recovered?.autores) ? recovered.autores : [],
          archivos: restoreDraftArchivos(recovered?.archivos),
        };

        if (parsed?.updatedAt) {
          const dt = new Date(parsed.updatedAt);
          this.draftInfo = `Se recuperó un borrador guardado (${dt.toLocaleString()}).`;
        } else {
          this.draftInfo = "Se recuperó un borrador guardado.";
        }

        this.mensaje = "Se recuperó un borrador guardado.";
        this.mensajeTipo = "info";
      } catch (e) {
        console.warn("Borrador corrupto, se ignora", e);
      }
    },

    disableDraftTemporarily() {
      this._draftEnabled = false;
      this.$nextTick(() => {
        this._draftEnabled = true;
      });
    },

    goTo(id) {
      const el = document.getElementById(id);
      el?.scrollIntoView({ behavior: "smooth", block: "start" });
    },

    clearDraft() {
      this.disableDraftTemporarily();

      try {
        localStorage.removeItem(this.storageKey);
      } catch (e) {
        console.warn("No se pudo eliminar el borrador.", e);
      }

      this.resetForm();
      this.mensaje = "Borrador eliminado.";
      this.mensajeTipo = "info";
    },

    clearErrors() {
      this.fieldErrors = {};
      this.mensaje = "";
      this.mensajeTipo = "";
    },

    focusField(key) {
      const localIdMap = {
        admin_context: "ai-admin-context-anchor",
        nombre_articulo: "ai-nombre_articulo",
        fecha_publicacion: "ai-fecha_publicacion",
        codigo_doi: "ai-codigo_doi",
        codigo_issn: "ai-codigo_issn",
        nombre_revista: "ai-nombre_revista",
        numero_revista: "ai-numero_revista",
        link_revista: "ai-link_revista",
        link_publicacion: "ai-link_publicacion",
        factor_impacto: "ai-factor_impacto",
        cuartil: "ai-cuartil",
        sjr: "ai-sjr",
        origen_tipo: "ai-origen_tipo",
        origen_grado: "ai-origen_grado",
        autores: "ai-autores-anchor",
        archivos: "ai-archivo-input",
      };

      const el =
        document.getElementById(`dg-${key}`) ||
        document.getElementById(localIdMap[key] || "");

      if (!el) return;

      if (key === "autores" || key === "archivos" || key === "admin_context") {
        el.scrollIntoView?.({ behavior: "smooth", block: "center" });
        return;
      }

      if (typeof el.focus === "function") el.focus({ preventScroll: false });
      else el.scrollIntoView?.({ behavior: "smooth", block: "center" });
    },

    buildAutoresPayload() {
      const raw = Array.isArray(this.form.autores) ? this.form.autores : [];

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
    },

    hasPendingRecoveredFiles() {
      return (Array.isArray(this.form.archivos) ? this.form.archivos : []).some(
        (it) => !it?.file && it?.originalName
      );
    },

    validateAdminContext() {
      if (!this.isAdminDelegado) return null;

      if (!this.adminContext.usuarioId) {
        return "Debe llegar al formulario con un usuario objetivo válido.";
      }

      return null;
    },

    validateFront() {
      const fe = {};
      const dg = this.form.datos_generales || {};

      if (this.isAdminDelegado && !this.adminContext.usuarioId) {
        fe.admin_context =
          "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
      }

      if (!dg.facultad) fe.facultad = "Seleccione una facultad.";
      if (!dg.carrera) fe.carrera = "Seleccione una carrera.";
      if (!dg.area) fe.area = "Seleccione un área del conocimiento (UNESCO).";
      if (!dg.subarea) fe.subarea = "Seleccione una subárea del conocimiento (UNESCO).";

      if (!String(this.form.origen_tipo || "").trim()) {
        fe.origen_tipo = "Seleccione el origen de la publicación.";
      }

      if (
        this.form.origen_tipo === "tic" &&
        !String(this.form.origen_grado || "").trim()
      ) {
        fe.origen_grado = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_articulo || "").trim()) {
        fe.nombre_articulo = "Campo obligatorio.";
      }

      if (!this.form.fecha_publicacion) {
        fe.fecha_publicacion = "Campo obligatorio.";
      }

      if (!String(this.form.codigo_issn || "").trim()) {
        fe.codigo_issn = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_revista || "").trim()) {
        fe.nombre_revista = "Campo obligatorio.";
      }

      if (
        this.form.factor_impacto === "sjr" &&
        String(this.form.sjr || "").trim() === ""
      ) {
        fe.sjr = "Ingrese el valor SJR o seleccione otro factor.";
      }

      if (!Array.isArray(this.form.autores) || this.form.autores.length === 0) {
        fe.autores = "Debe registrar al menos un autor.";
      }

      if (this.hasPendingRecoveredFiles()) {
        fe.archivos =
          "Hay adjuntos recuperados del borrador que deben volver a seleccionarse o eliminarse antes de guardar.";
      }

      this.fieldErrors = fe;

      if (Object.keys(fe).length) {
        const first = firstErrorField(fe);
        this.mensaje = "Complete los campos obligatorios antes de guardar.";
        this.mensajeTipo = "error";
        if (first) this.focusField(first);
        return false;
      }

      return true;
    },

    buildCreateUrl() {
      return this.createEndpoint;
    },

    async registrarArticulo() {
      this.loading = true;
      this.clearErrors();

      try {
        if (!this.validateFront()) {
          this.loading = false;
          return;
        }

        const autoresPayload = this.buildAutoresPayload();
        if (!autoresPayload.length) {
          this.fieldErrors = {
            ...this.fieldErrors,
            autores: "Los autores seleccionados no tienen ID válido.",
          };
          this.mensaje = "Revise la sección de autores.";
          this.mensajeTipo = "error";
          this.focusField("autores");
          this.loading = false;
          return;
        }

        const adminValidationError = this.validateAdminContext();
        if (adminValidationError) {
          this.fieldErrors = {
            ...this.fieldErrors,
            admin_context: adminValidationError,
          };
          this.mensaje = adminValidationError;
          this.mensajeTipo = "error";
          this.focusField("admin_context");
          this.loading = false;
          return;
        }

        const fd = new FormData();

        fd.append("tipo_codigo", "articulo_alto_impacto");

        Object.entries(this.form.datos_generales).forEach(([key, value]) => {
          if (key === "pais" || key === "ciudad") return;
          appendIfPresent(fd, key, value);
        });

        fd.append("origen_tipo", String(this.form.origen_tipo || "ninguno"));

        if (
          this.form.origen_tipo === "tic" &&
          String(this.form.origen_grado || "").trim()
        ) {
          fd.append("origen_grado", String(this.form.origen_grado).trim());
        }

        const campos = [
          "nombre_articulo",
          "fecha_publicacion",
          "codigo_doi",
          "codigo_issn",
          "nombre_revista",
          "numero_revista",
          "link_revista",
          "link_publicacion",
          "factor_impacto",
          "cuartil",
          "sjr",
        ];

        campos.forEach((key) => {
          let value = this.form[key];

          if (key === "cuartil") {
            value = normalizeCuartil(value);
          }

          appendIfPresent(fd, key, value);
        });

        fd.append("autores", JSON.stringify(autoresPayload));

        if (this.isAdminDelegado && this.adminContext.usuarioId) {
          fd.append("usuario_objetivo_id", String(this.adminContext.usuarioId));

          if (this.adminContext.autorId) {
            fd.append("autor_objetivo_id", String(this.adminContext.autorId));
          }
        }

        appendArchivosToFormData(fd, this.form.archivos, {
          primaryField: null,
          filesField: "archivos",
          metaField: "archivos_meta",
        });

        await api.post(this.buildCreateUrl(), fd);

        this.disableDraftTemporarily();
        localStorage.removeItem(this.storageKey);
        this.resetForm();

        this.mensaje = this.isAdminDelegado
          ? "Artículo registrado exitosamente para el usuario seleccionado."
          : "Artículo registrado exitosamente.";
        this.mensajeTipo = "success";
      } catch (error) {
        const status = error?.response?.status;
        const data = error?.response?.data;

        if (status === 401) {
          this.mensaje = "Sesión expirada. Vuelva a iniciar sesión.";
          this.mensajeTipo = "error";
          this.loading = false;
          return;
        }

        const normalized = normalizeDrfErrors(data);
        this.fieldErrors = normalized.fields || {};
        this.mensaje = normalized.message || "No se pudo registrar el artículo.";
        this.mensajeTipo = "error";

        const first = firstErrorField(this.fieldErrors);
        if (first) this.focusField(first);

        console.error("❌ Error backend:", data || error);
      } finally {
        this.loading = false;
      }
    },

    resetForm() {
      this.fieldErrors = {};
      this.draftInfo = "";
      this.mensaje = "";
      this.mensajeTipo = "";

      this.form = {
        datos_generales: {
          facultad: null,
          carrera: null,
          proyecto: null,
          area: null,
          subarea: null,
          pais: null,
          ciudad: null,
        },

        origen_tipo: "",
        origen_grado: "",

        nombre_articulo: "",
        fecha_publicacion: "",

        codigo_doi: "",
        codigo_issn: "",
        nombre_revista: "",
        numero_revista: null,
        link_revista: "",
        link_publicacion: "",

        factor_impacto: "",
        cuartil: "",
        sjr: "",

        autores: [],
        archivos: [],
      };
    },
  },
};
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