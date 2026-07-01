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
        @submit.prevent="registrarCapitulo"
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
              <div id="cl-admin-context-anchor"></div>

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
                  Relación académica del capítulo.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="cl-origen_tipo">
                    Origen de la publicación <span class="req">*</span>
                  </label>

                  <select
                    id="cl-origen_tipo"
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
                  <label class="sgpc-label" for="cl-origen_grado">
                    Grado / programa
                    <span v-if="form.origen_tipo === 'tic'" class="req">*</span>
                  </label>

                  <input
                    id="cl-origen_grado"
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

          <section id="sec-capitulo" class="sgpc-card">
            <div class="sgpc-card-head">
              <div>
                <h3 class="sgpc-card-title">Información del capítulo</h3>
                <p class="sgpc-card-desc">
                  Datos principales del capítulo y su obra.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div class="sgpc-grid">
                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="cl-nombre_capitulo">
                    Nombre del capítulo <span class="req">*</span>
                  </label>

                  <input
                    id="cl-nombre_capitulo"
                    v-model.trim="form.nombre_capitulo"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Tecnologías emergentes en la educación"
                  />

                  <p v-if="fieldErrors.nombre_capitulo" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_capitulo }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="cl-nombre_libro">
                    Nombre del libro <span class="req">*</span>
                  </label>

                  <input
                    id="cl-nombre_libro"
                    v-model.trim="form.nombre_libro"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Innovación y Ciencia en América Latina"
                  />

                  <p v-if="fieldErrors.nombre_libro" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.nombre_libro }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="cl-fecha_publicacion">
                    Fecha de publicación
                  </label>

                  <input
                    id="cl-fecha_publicacion"
                    v-model="form.fecha_publicacion"
                    class="sgpc-input"
                    type="date"
                  />

                  <p v-if="fieldErrors.fecha_publicacion" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.fecha_publicacion }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="cl-codigo_isbn">
                    Código ISBN <span class="req">*</span>
                  </label>

                  <input
                    id="cl-codigo_isbn"
                    v-model.trim="form.codigo_isbn"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. 978-9942-xx-xxxx-x"
                  />

                  <p v-if="fieldErrors.codigo_isbn" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.codigo_isbn }}
                  </p>

                  <p class="sgpc-hint">
                    Registre el ISBN para trazabilidad editorial.
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="cl-editor_compilador">
                    Editor / Compilador <span class="req">*</span>
                  </label>

                  <input
                    id="cl-editor_compilador"
                    v-model.trim="form.editor_compilador"
                    class="sgpc-input"
                    type="text"
                    required
                    placeholder="Ej. Dr. Juan Pérez"
                  />

                  <p
                    v-if="fieldErrors.editor_compilador"
                    class="sgpc-hint sgpc-hint-error"
                  >
                    {{ fieldErrors.editor_compilador }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-6">
                  <label class="sgpc-label" for="cl-revisor_par_arbitraje">
                    Revisor par / arbitraje <span class="req">*</span>
                  </label>

                  <select
                    id="cl-revisor_par_arbitraje"
                    v-model="form.revisor_par_arbitraje"
                    class="sgpc-input"
                    required
                  >
                    <option disabled value="">Seleccione...</option>
                    <option value="si">Sí</option>
                    <option value="no">No</option>
                  </select>

                  <p
                    v-if="fieldErrors.revisor_par_arbitraje"
                    class="sgpc-hint sgpc-hint-error"
                  >
                    {{ fieldErrors.revisor_par_arbitraje }}
                  </p>
                </div>

                <div class="sgpc-field sgpc-col-span-12">
                  <label class="sgpc-label" for="cl-link_capitulo">
                    Link del capítulo <span class="req">*</span>
                  </label>

                  <input
                    id="cl-link_capitulo"
                    v-model.trim="form.link_capitulo"
                    class="sgpc-input"
                    type="url"
                    required
                    placeholder="https://..."
                  />

                  <p v-if="fieldErrors.link_capitulo" class="sgpc-hint sgpc-hint-error">
                    {{ fieldErrors.link_capitulo }}
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
                  Seleccione autores y defina su participación y orden.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <div id="cl-autores-anchor"></div>

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
                  Puede adjuntar el PDF principal del capítulo y soportes complementarios.
                </p>
              </div>
            </div>

            <div class="sgpc-card-body">
              <AdjuntosPdfUploader
                v-model="form.archivos"
                :error="fieldErrors.archivos"
                input-id="cl-archivo-input"
                title="Agregar archivos PDF"
                description="El primer archivo será el PDF principal del capítulo. Puede agregar hasta 2 adjuntos adicionales."
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
                :class="{ 'is-ok': hasRequiredChapter }"
                @click="goTo('sec-capitulo')"
              >
                <div>
                  <strong>Información del capítulo</strong>
                  <span>{{ hasRequiredChapter ? "Completo" : "Campos pendientes" }}</span>
                </div>
                <em>{{ hasRequiredChapter ? "Completo" : "Pendiente" }}</em>
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
              <button class="sgpc-btn-primary" type="submit" :disabled="loading">
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

const BASE_STORAGE_KEY = "sgpc-capitulo-libro-draft:v21";
const STANDARD_CREATE_ENDPOINT = "/capitulos-libro/";
const ADMIN_CREATE_ENDPOINT = "/admin/publicaciones/capitulos-libro/crear/";

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
  origen_tipo: "Origen de la publicación",
  origen_grado: "Grado / programa",
  nombre_capitulo: "Nombre del capítulo",
  nombre_libro: "Nombre del libro",
  fecha_publicacion: "Fecha de publicación",
  codigo_isbn: "Código ISBN",
  editor_compilador: "Editor / Compilador",
  revisor_par_arbitraje: "Revisor par / arbitraje",
  link_capitulo: "Link del capítulo",
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
    return { fields: {}, message: "No se pudo guardar. Verifique los campos." };
  }

  if (typeof data?.detail === "string") {
    return { fields: {}, message: data.detail };
  }

  const rawErrors =
    data?.errors && typeof data.errors === "object"
      ? data.errors
      : data;

  if (typeof rawErrors !== "object" || rawErrors == null) {
    return { fields: {}, message: "No se pudo guardar. Verifique los campos." };
  }

  const fields = {};
  let first = null;

  Object.entries(rawErrors).forEach(([k, v]) => {
    if (k === "detail") return;
    const normalizedKey = normalizeErrorKey(k);
    fields[normalizedKey] = asText(v);
    if (!first) first = normalizedKey;
  });

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

function firstErrorField(fields) {
  const order = [
    "admin_context",
    "facultad",
    "carrera",
    "proyecto",
    "area",
    "subarea",
    "origen_tipo",
    "origen_grado",
    "nombre_capitulo",
    "nombre_libro",
    "fecha_publicacion",
    "codigo_isbn",
    "editor_compilador",
    "revisor_par_arbitraje",
    "link_capitulo",
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
  name: "CapituloLibroRegistro",

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
        nombre_capitulo: "",
        nombre_libro: "",
        fecha_publicacion: "",
        codigo_isbn: "",
        editor_compilador: "",
        revisor_par_arbitraje: "",
        link_capitulo: "",
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
        ? "Administración · Libros y capítulos"
        : "Libros y capítulos";
    },

    pageTitle() {
      return "Registrar Capítulo de Libro";
    },

    pageSubtitle() {
      if (this.isAdminDelegado) {
        return "Registre la información editorial del capítulo para el usuario seleccionado. Los campos marcados con * son obligatorios.";
      }

      return "Registre la información editorial del capítulo. Los campos marcados con * son obligatorios.";
    },

    submitText() {
      return "Registrar capítulo";
    },

    submitLoadingText() {
      return "Guardando...";
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

    hasRequiredChapter() {
      return !!(
        String(this.form.nombre_capitulo || "").trim() &&
        String(this.form.nombre_libro || "").trim() &&
        String(this.form.codigo_isbn || "").trim() &&
        String(this.form.editor_compilador || "").trim() &&
        String(this.form.revisor_par_arbitraje || "").trim() &&
        String(this.form.link_capitulo || "").trim()
      );
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
        { key: "capitulo", done: this.hasRequiredChapter },
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
              datos_generales: {
                ...val.datos_generales,
                pais: null,
                ciudad: null,
              },
              origen_tipo: val.origen_tipo,
              origen_grado: val.origen_grado,
              nombre_capitulo: val.nombre_capitulo,
              nombre_libro: val.nombre_libro,
              fecha_publicacion: val.fecha_publicacion,
              codigo_isbn: val.codigo_isbn,
              editor_compilador: val.editor_compilador,
              revisor_par_arbitraje: val.revisor_par_arbitraje,
              link_capitulo: val.link_capitulo,
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
        p.autorId || q.autor_id || q.autorId || 0
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
            pais: null,
            ciudad: null,
          },
          autores: Array.isArray(parsed.form?.autores ?? parsed.autores)
            ? (parsed.form?.autores ?? parsed.autores)
            : [],
          archivos: restoreDraftArchivos(parsed.form?.archivos ?? parsed.archivos),
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
        admin_context: "cl-admin-context-anchor",
        origen_tipo: "cl-origen_tipo",
        origen_grado: "cl-origen_grado",
        nombre_capitulo: "cl-nombre_capitulo",
        nombre_libro: "cl-nombre_libro",
        fecha_publicacion: "cl-fecha_publicacion",
        codigo_isbn: "cl-codigo_isbn",
        editor_compilador: "cl-editor_compilador",
        revisor_par_arbitraje: "cl-revisor_par_arbitraje",
        link_capitulo: "cl-link_capitulo",
        autores: "cl-autores-anchor",
        archivos: "cl-archivo-input",
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

      if (!String(this.form.origen_tipo || "").trim()) {
        fe.origen_tipo = "Seleccione el origen de la publicación.";
      }

      if (this.form.origen_tipo === "tic" && !String(this.form.origen_grado || "").trim()) {
        fe.origen_grado = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_capitulo || "").trim()) {
        fe.nombre_capitulo = "Campo obligatorio.";
      }

      if (!String(this.form.nombre_libro || "").trim()) {
        fe.nombre_libro = "Campo obligatorio.";
      }

      if (!String(this.form.codigo_isbn || "").trim()) {
        fe.codigo_isbn = "Campo obligatorio.";
      }

      if (!String(this.form.editor_compilador || "").trim()) {
        fe.editor_compilador = "Campo obligatorio.";
      }

      if (!String(this.form.revisor_par_arbitraje || "").trim()) {
        fe.revisor_par_arbitraje = "Seleccione Sí o No.";
      }

      if (!String(this.form.link_capitulo || "").trim()) {
        fe.link_capitulo = "Campo obligatorio.";
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

    async registrarCapitulo() {
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

        Object.entries(this.form.datos_generales).forEach(([k, v]) => {
          if (k === "pais" || k === "ciudad") return;
          appendIfPresent(fd, k, v);
        });

        appendIfPresent(fd, "origen_tipo", this.form.origen_tipo || "ninguno");

        if (this.form.origen_tipo === "tic") {
          appendIfPresent(fd, "origen_grado", this.form.origen_grado);
        }

        const campos = [
          "nombre_capitulo",
          "nombre_libro",
          "fecha_publicacion",
          "codigo_isbn",
          "editor_compilador",
          "revisor_par_arbitraje",
          "link_capitulo",
        ];

        campos.forEach((k) => {
          appendIfPresent(fd, k, this.form[k]);
        });

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

        await api.post(
          this.isAdminDelegado ? ADMIN_CREATE_ENDPOINT : STANDARD_CREATE_ENDPOINT,
          fd
        );

        this.suspendDraftOnce();
        localStorage.removeItem(this.draftStorageKey);

        this.mensaje = this.isAdminDelegado
          ? "Capítulo registrado correctamente para el usuario seleccionado."
          : "Capítulo registrado exitosamente.";
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
        this.mensaje = normalized.message || "Error al registrar el capítulo.";
        this.mensajeTipo = "error";

        const first = firstErrorField(this.fieldErrors);
        if (first) this.focusField(first);

        console.error("❌ Error capítulo:", data || error);
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
        nombre_capitulo: "",
        nombre_libro: "",
        fecha_publicacion: "",
        codigo_isbn: "",
        editor_compilador: "",
        revisor_par_arbitraje: "",
        link_capitulo: "",
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