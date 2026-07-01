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
        @submit.prevent="registrarPonencia"
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
              <div id="pn-admin-context-anchor"></div>

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
                  Información institucional y ubicación del evento.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <DatosGenerales
                v-model="form.datos_generales"
                :errors="fieldErrors"
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
                  Relación académica de la ponencia.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="pn-origen_tipo">
                    Origen de la publicación <span class="req">*</span>
                  </label>

                  <select
                    id="pn-origen_tipo"
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
                  <label class="sgpc-label" for="pn-origen_grado">
                    Grado / programa
                    <span v-if="form.origen_tipo === 'tic'" class="req">*</span>
                  </label>

                  <input
                    id="pn-origen_grado"
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

          <section id="sec-evento" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Evento y ponencia</h3>
                <p class="sgpc-card-desc">
                  Datos principales del evento académico y el trabajo presentado.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="pn-nombre_evento">
                    Nombre del evento <span class="req">*</span>
                  </label>

                  <input
                    id="pn-nombre_evento"
                    v-model.trim="form.nombre_evento"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Congreso Internacional de Ciencia"
                  />

                  <p v-if="fieldErrors.nombre_evento" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_evento }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="pn-nombre_ponencia">
                    Nombre de la ponencia <span class="req">*</span>
                  </label>

                  <input
                    id="pn-nombre_ponencia"
                    v-model.trim="form.nombre_ponencia"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Innovación tecnológica en Ecuador"
                  />

                  <p v-if="fieldErrors.nombre_ponencia" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_ponencia }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="pn-fecha_publicacion">
                    Fecha de presentación <span class="req">*</span>
                  </label>

                  <input
                    id="pn-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                    required
                  />

                  <p class="sgpc-hint">
                    Corresponde a la fecha de exposición o presentación del trabajo.
                  </p>

                  <p v-if="fieldErrors.fecha_publicacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="pn-codigo_issn_isbn">
                    Código ISSN / ISBN
                  </label>

                  <input
                    id="pn-codigo_issn_isbn"
                    v-model.trim="form.codigo_issn_isbn"
                    class="sgpc-input"
                    type="text"
                    placeholder="Opcional"
                  />

                  <p class="sgpc-hint">
                    Registre ISSN/ISBN de memorias o actas, si aplica.
                  </p>

                  <p v-if="fieldErrors.codigo_issn_isbn" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_issn_isbn }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="pn-tipo_presentacion">
                    Tipo de presentación
                  </label>

                  <select
                    id="pn-tipo_presentacion"
                    v-model="form.tipo_presentacion"
                    class="sgpc-input"
                  >
                    <option value="">Seleccione...</option>
                    <option value="magistral">Conferencia magistral</option>
                    <option value="oral">Conferencia oral</option>
                    <option value="poster">Poster</option>
                    <option value="otro">Otro</option>
                  </select>

                  <p class="sgpc-hint">
                    Si selecciona “Otro”, deberá escribir el tipo manualmente.
                  </p>

                  <p v-if="fieldErrors.tipo_presentacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.tipo_presentacion }}
                  </p>
                </div>

                <div
                  v-if="form.tipo_presentacion === 'otro'"
                  class="sgpc-field sgpc-col-span-6"
                >
                  <label class="sgpc-label" for="pn-tipo_presentacion_otro">
                    Especifique el tipo de presentación <span class="req">*</span>
                  </label>

                  <input
                    id="pn-tipo_presentacion_otro"
                    v-model.trim="form.tipo_presentacion_otro"
                    class="sgpc-input"
                    type="text"
                    required
                    maxlength="150"
                    placeholder="Ej. Mesa redonda, taller, simposio..."
                  />

                  <p class="sgpc-hint">
                    Este valor se guardará como tipo manual de presentación.
                  </p>

                  <p
                    v-if="fieldErrors.tipo_presentacion_otro"
                    class="sgpc-hint sgpc-hint-error"
                  >
                    {{ fieldErrors.tipo_presentacion_otro }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="pn-link_evento">
                    Link del evento
                  </label>

                  <input
                    id="pn-link_evento"
                    v-model.trim="form.link_evento"
                    class="sgpc-input"
                    type="url"
                    placeholder="https://..."
                  />

                  <p v-if="fieldErrors.link_evento" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.link_evento }}
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
              <div id="pn-autores-anchor"></div>

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
                <h3 class="sgpc-card-title">Adjuntos PDF</h3>
                <p class="sgpc-card-desc">
                  Puede adjuntar evidencia de la ponencia, memorias o soportes complementarios.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="pn-archivo-input"
                title="Agregar archivos PDF"
                description="El primer archivo será el PDF principal de la ponencia. Puede agregar hasta 2 adjuntos adicionales."
                helper-text="PDF principal hasta 5 MB. Adjuntos hasta 3 MB. Máximo 3 archivos."
                :multiple="true"
                :max-files="3"
                :uses-primary-slot="true"
                :primary-max-size-mb="5"
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
                  <span>{{ hasRequiredOrigin ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredOrigin ? "Completo" : "Pendiente" }}</em>
              </button>

              <button
                type="button"
                class="sgpc-status-item"
                :class="{ 'is-ok': hasRequiredEvent }"
                @click="goTo('sec-evento')"
              >
                <div>
                  <strong>Evento y ponencia</strong>
                  <span>{{ hasRequiredEvent ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredEvent ? "Completo" : "Pendiente" }}</em>
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
                  <strong>Adjuntos PDF</strong>
                  <span>{{ hasAdjuntos ? `${form.archivos.length} archivo(s)` : "Opcional" }}</span>
                </div>
                <em>{{ hasAdjuntos ? "Completo" : "Opcional" }}</em>
              </button>
            </div>

            <div class="sgpc-summary-actions">
              <button class="sgpc-btn-primary" :disabled="loading" type="submit">
                <span v-if="loading">{{ submitLoadingText }}</span>
                <span v-else>{{ submitText }}</span>
              </button>

              <button class="sgpc-btn" type="button" :disabled="loading" @click="clearDraft">
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

const BASE_STORAGE_KEY = "sgpc-ponencia-draft:v22";
const STANDARD_CREATE_ENDPOINT = "/ponencias/registrar/";
const ADMIN_CREATE_ENDPOINT = "/admin/publicaciones/ponencias/crear/";

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
  pais: "País",
  ciudad: "Ciudad",
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa",
  nombre_evento: "Nombre del evento",
  nombre_ponencia: "Nombre de la ponencia",
  fecha_publicacion: "Fecha de presentación",
  codigo_issn_isbn: "Código ISSN / ISBN",
  tipo_presentacion: "Tipo de presentación",
  tipo_presentacion_otro: "Tipo de presentación manual",
  link_evento: "Link del evento",
  autores: "Autores",
  archivos: "Adjuntos PDF",
};

function asText(v) {
  if (Array.isArray(v)) return v.map(asText).join(", ");
  if (v != null && typeof v === "object") return Object.values(v).map(asText).join(", ");
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
    "pais",
    "ciudad",
    "origen_tipo",
    "origen_grado",
    "nombre_evento",
    "nombre_ponencia",
    "fecha_publicacion",
    "codigo_issn_isbn",
    "tipo_presentacion",
    "tipo_presentacion_otro",
    "link_evento",
    "autores",
    "archivos",
  ];

  for (const k of order) if (fields?.[k]) return k;
  return Object.keys(fields || {})[0] || null;
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
  name: "PonenciaRegistro",

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
      _draftSuspended: false,

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
        nombre_evento: "",
        nombre_ponencia: "",
        fecha_publicacion: "",
        codigo_issn_isbn: "",
        tipo_presentacion: "",
        tipo_presentacion_otro: "",
        link_evento: "",
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

    draftStorageKey() {
      if (!this.isAdminDelegado) {
        return `${BASE_STORAGE_KEY}:self`;
      }

      const usuarioId =
        this.adminContext.usuarioId ||
        Number(this.$route?.params?.usuarioId || 0) ||
        "sin-usuario";

      return `${BASE_STORAGE_KEY}:admin:${usuarioId}`;
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
        ? "Administración · Ponencias y eventos"
        : "Ponencias y eventos";
    },

    pageTitle() {
      return "Registrar Ponencia";
    },

    pageSubtitle() {
      if (this.isAdminDelegado) {
        return "Registre datos del evento, ponencia, fecha de presentación, autores y adjuntos para el usuario seleccionado. Los campos marcados con * son obligatorios.";
      }

      return "Registre datos del evento, ponencia, fecha de presentación, autores y adjuntos. Los campos marcados con * son obligatorios.";
    },

    submitText() {
      return "Registrar ponencia";
    },

    submitLoadingText() {
      return "Guardando...";
    },

    hasRequiredContext() {
      const dg = this.form.datos_generales || {};
      return !!(
        dg.facultad &&
        dg.carrera &&
        dg.area &&
        dg.subarea &&
        dg.pais &&
        dg.ciudad
      );
    },

    hasRequiredOrigin() {
      if (!this.form.origen_tipo) return false;
      if (this.form.origen_tipo === "tic") {
        return !!String(this.form.origen_grado || "").trim();
      }
      return true;
    },

    hasRequiredEvent() {
      const hasBaseEvent = !!(
        String(this.form.nombre_evento || "").trim() &&
        String(this.form.nombre_ponencia || "").trim() &&
        this.form.fecha_publicacion
      );

      const hasTipoPresentacionOtro =
        this.form.tipo_presentacion !== "otro" ||
        !!String(this.form.tipo_presentacion_otro || "").trim();

      return hasBaseEvent && hasTipoPresentacionOtro;
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
        { key: "evento", done: this.hasRequiredEvent },
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
      return Math.round((this.completedRequiredCount / this.totalRequiredCount) * 100);
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
        if (this._draftSuspended) return;

        clearTimeout(this._draftTimer);
        this._draftTimer = setTimeout(() => {
          const payload = {
            form: {
              datos_generales: val.datos_generales,
              origen_tipo: val.origen_tipo,
              origen_grado: val.origen_grado,
              nombre_evento: val.nombre_evento,
              nombre_ponencia: val.nombre_ponencia,
              fecha_publicacion: val.fecha_publicacion,
              codigo_issn_isbn: val.codigo_issn_isbn,
              tipo_presentacion: val.tipo_presentacion,
              tipo_presentacion_otro: val.tipo_presentacion_otro,
              link_evento: val.link_evento,
              autores: val.autores,
              archivos: serializeDraftArchivos(val.archivos),
            },
            updatedAt: new Date().toISOString(),
          };

          try {
            localStorage.setItem(this.draftStorageKey, JSON.stringify(payload));
          } catch (e) {
            console.warn("No se pudo guardar el borrador.", e);
          }
        }, 250);
      },
    },

    "form.origen_tipo"(v) {
      if (v !== "tic") this.form.origen_grado = "";
    },

    "form.tipo_presentacion"(v) {
      if (v !== "otro") {
        this.form.tipo_presentacion_otro = "";
      }
    },

    "$route.fullPath"() {
      this.handleRouteContextChange();
    },
  },

  methods: {
    hydrateAdminContextFromRoute() {
      const q = this.$route?.query || {};
      const p = this.$route?.params || {};

      const usuarioId = Number(
        p.usuarioId || q.usuario_id || q.usuarioId || q.user_id || 0
      );

      const autorId = Number(
        p.autorId || q.autor_id || q.autorId || q.author_id || 0
      );

      this.adminContext = {
        usuarioId: Number.isFinite(usuarioId) && usuarioId > 0 ? usuarioId : null,
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
      const raw = localStorage.getItem(this.draftStorageKey);
      if (!raw) return;

      try {
        const parsed = JSON.parse(raw);

        this.form = {
          ...this.form,
          ...(parsed.form || parsed),
          datos_generales: {
            ...this.form.datos_generales,
            ...((parsed.form?.datos_generales || parsed.datos_generales) || {}),
          },
          tipo_presentacion_otro:
            parsed.form?.tipo_presentacion_otro ??
            parsed.tipo_presentacion_otro ??
            "",
          autores: Array.isArray(parsed.form?.autores ?? parsed.autores)
            ? (parsed.form?.autores ?? parsed.autores)
            : [],
          archivos: restoreDraftArchivos(parsed.form?.archivos ?? parsed.archivos),
        };

        if (this.form.tipo_presentacion !== "otro") {
          this.form.tipo_presentacion_otro = "";
        }

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

    suspendDraftOnce() {
      this._draftSuspended = true;
      setTimeout(() => {
        this._draftSuspended = false;
      }, 0);
    },

    handleRouteContextChange() {
      this.hydrateAdminContextFromRoute();
      this.suspendDraftOnce();
      this.resetForm();
      this.loadDraft();
    },

    goTo(id) {
      const el = document.getElementById(id);
      el?.scrollIntoView({ behavior: "smooth", block: "start" });
    },

    clearDraft() {
      try {
        localStorage.removeItem(this.draftStorageKey);
      } catch (e) {
        console.warn("No se pudo eliminar el borrador:", e);
      }

      this.suspendDraftOnce();
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
        admin_context: "pn-admin-context-anchor",
        origen_tipo: "pn-origen_tipo",
        origen_grado: "pn-origen_grado",
        nombre_evento: "pn-nombre_evento",
        nombre_ponencia: "pn-nombre_ponencia",
        fecha_publicacion: "pn-fecha_publicacion",
        codigo_issn_isbn: "pn-codigo_issn_isbn",
        tipo_presentacion: "pn-tipo_presentacion",
        tipo_presentacion_otro: "pn-tipo_presentacion_otro",
        link_evento: "pn-link_evento",
        autores: "pn-autores-anchor",
        archivos: "pn-archivo-input",
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
        return "Debe abrir este formulario desde la administración con un usuario objetivo válido.";
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
      if (!dg.pais) fe.pais = "Seleccione un país.";
      if (!dg.ciudad) fe.ciudad = "Seleccione una ciudad.";

      if (!String(this.form.origen_tipo || "").trim()) {
        fe.origen_tipo = "Seleccione el origen de la publicación.";
      }

      if (this.form.origen_tipo === "tic" && !String(this.form.origen_grado || "").trim()) {
        fe.origen_grado = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_evento || "").trim()) {
        fe.nombre_evento = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_ponencia || "").trim()) {
        fe.nombre_ponencia = "Campo obligatorio.";
      }

      if (!this.form.fecha_publicacion) {
        fe.fecha_publicacion = "Campo obligatorio.";
      }

      if (
        this.form.tipo_presentacion === "otro" &&
        !String(this.form.tipo_presentacion_otro || "").trim()
      ) {
        fe.tipo_presentacion_otro =
          "Debe escribir el tipo de presentación cuando seleccione “Otro”.";
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
      if (!this.isAdminDelegado) return STANDARD_CREATE_ENDPOINT;

      const params = new URLSearchParams();

      if (this.adminContext.usuarioId) {
        params.set("usuario_id", String(this.adminContext.usuarioId));
      }

      if (this.adminContext.autorId) {
        params.set("autor_id", String(this.adminContext.autorId));
      }

      const qs = params.toString();
      return qs ? `${ADMIN_CREATE_ENDPOINT}?${qs}` : ADMIN_CREATE_ENDPOINT;
    },

    async registrarPonencia() {
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
        const dg = this.form.datos_generales || {};

        Object.entries(dg).forEach(([k, v]) => {
          appendIfPresent(fd, k, v);
        });

        fd.append("origen_tipo", String(this.form.origen_tipo || "ninguno"));

        if (this.form.origen_tipo === "tic" && String(this.form.origen_grado || "").trim()) {
          fd.append("origen_grado", String(this.form.origen_grado).trim());
        }

        [
          "nombre_evento",
          "nombre_ponencia",
          "fecha_publicacion",
          "codigo_issn_isbn",
          "tipo_presentacion",
          "link_evento",
        ].forEach((key) => {
          appendIfPresent(fd, key, this.form[key]);
        });

        if (
          this.form.tipo_presentacion === "otro" &&
          String(this.form.tipo_presentacion_otro || "").trim()
        ) {
          fd.append(
            "tipo_presentacion_otro",
            String(this.form.tipo_presentacion_otro).trim()
          );
        }

        fd.append("autores", JSON.stringify(autoresPayload));

        if (this.isAdminDelegado && this.adminContext.usuarioId) {
          fd.append("usuario_objetivo_id", String(this.adminContext.usuarioId));

          if (this.adminContext.autorId) {
            fd.append("autor_objetivo_id", String(this.adminContext.autorId));
          }
        }

        appendArchivosToFormData(fd, this.form.archivos, {
          primaryField: "archivo_pdf",
          filesField: "archivos",
          metaField: "archivos_meta",
        });

        await api.post(this.buildCreateUrl(), fd);

        this.suspendDraftOnce();
        localStorage.removeItem(this.draftStorageKey);

        this.mensaje = this.isAdminDelegado
          ? "Ponencia registrada correctamente para el usuario seleccionado."
          : "Ponencia registrada correctamente.";
        this.mensajeTipo = "success";
        this.resetForm();
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
        this.mensaje = normalized.message || "Error al registrar la ponencia.";
        this.mensajeTipo = "error";

        const first = firstErrorField(this.fieldErrors);
        if (first) this.focusField(first);

        console.error("❌ Error ponencia:", data || error);
      } finally {
        this.loading = false;
      }
    },

    resetForm() {
      this.fieldErrors = {};
      this.draftInfo = "";

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
        nombre_evento: "",
        nombre_ponencia: "",
        fecha_publicacion: "",
        codigo_issn_isbn: "",
        tipo_presentacion: "",
        tipo_presentacion_otro: "",
        link_evento: "",
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
  background: color-mix(in srgb, var(--bg-card, #ffffff) 90%, var(--bg-soft, #f4f2ed) 10%);
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