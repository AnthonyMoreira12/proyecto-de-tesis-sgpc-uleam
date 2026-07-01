<template>
  <div class="pdet-page">
    <div class="pdet-wrap">
      <!-- LOADING -->
      <div
        v-if="loading"
        class="pdet-state pdet-state--loading"
        aria-label="Cargando detalle de publicación"
      >
        <div class="pdet-skeleton">
          <div class="pdet-sk-topbar"></div>
          <div class="pdet-sk-hero"></div>
          <div class="pdet-sk-section"></div>
          <div class="pdet-sk-section"></div>
          <div class="pdet-sk-section"></div>
        </div>
      </div>

      <!-- ERROR -->
      <section
        v-else-if="error"
        class="pdet-state pdet-state--error"
        role="alert"
        aria-live="polite"
      >
        <div class="pdet-error">
          <p class="pdet-error__eyebrow">Detalle de publicación</p>
          <h1 class="pdet-error__title">No se pudo cargar la publicación</h1>
          <p class="pdet-error__text">{{ error }}</p>

          <div class="pdet-error__actions">
            <button
              class="pdet-btn pdet-btn--primary"
              type="button"
              @click="cargarDetalle()"
            >
              Reintentar
            </button>

            <button class="pdet-btn" type="button" @click="goBack">
              Volver
            </button>
          </div>
        </div>
      </section>

      <!-- DETALLE -->
      <article v-else-if="detalleNormalizado" class="pdet-shell page-stagger">
        <!-- SOLO EN LECTURA -->
        <template v-if="!editMode">
          <header class="pdet-topbar page-stage page-stage-1">
            <button class="pdet-linkbtn" type="button" @click="goBack">
              Volver a publicaciones
            </button>

            <div class="pdet-topbar__actions">
              <button
                v-if="hasPdf"
                class="pdet-btn"
                type="button"
                @click="openPdf"
              >
                Ver PDF
              </button>

              <template v-if="canEdit">
                <button
                  class="pdet-btn pdet-btn--primary"
                  type="button"
                  @click="openEditMode"
                >
                  Editar publicación
                </button>
              </template>
            </div>
          </header>

          <section class="pdet-hero page-stage page-stage-2">
            <div class="pdet-hero__main">
              <p class="pdet-kicker">Detalle de publicación</p>

              <div class="pdet-titleRow">
                <h1 class="pdet-title">{{ detalleNormalizado.titulo }}</h1>

                <span class="pdet-badge" :class="toneClass">
                  {{ detalleNormalizado.tipoLabel }}
                </span>
              </div>

              <p class="pdet-subtitle">
                {{ heroIntroText }}
              </p>

              <div class="pdet-chipRow">
                <span v-if="detalleNormalizado.fechaTexto" class="pdet-chip">
                  {{ detalleNormalizado.fechaTexto }}
                </span>

                <span v-if="detalleNormalizado.facultad" class="pdet-chip">
                  {{ detalleNormalizado.facultad }}
                </span>

                <span v-if="detalleNormalizado.carrera" class="pdet-chip">
                  {{ detalleNormalizado.carrera }}
                </span>

                <span v-if="detalleNormalizado.autores.length" class="pdet-chip">
                  {{ detalleNormalizado.autores.length }}
                  {{ detalleNormalizado.autores.length === 1 ? "autor" : "autores" }}
                </span>

                <span v-if="isAdmin" class="pdet-chip">
                  Administrador
                </span>

                <span v-else-if="userOwnsPublication" class="pdet-chip">
                  Autor vinculado
                </span>
              </div>

              <p v-if="detalleNormalizado.proyecto" class="pdet-project">
                <strong>Proyecto:</strong> {{ detalleNormalizado.proyecto }}
              </p>
            </div>

            <aside
              v-if="heroResumen.length"
              class="pdet-hero__panel"
              aria-label="Resumen rápido"
            >
              <div class="pdet-panelHead">
                <h2 class="pdet-panelTitle">Resumen rápido</h2>
                <p class="pdet-panelText">
                  Lectura breve de los datos principales del registro.
                </p>
              </div>

              <div class="pdet-summaryGrid">
                <article
                  v-for="item in heroResumen"
                  :key="item.label"
                  class="pdet-summaryItem"
                >
                  <span class="k">{{ item.label }}</span>
                  <span class="v">{{ item.value }}</span>
                </article>
              </div>
            </aside>
          </section>
        </template>

        <!-- MODO LECTURA -->
        <template v-if="!editMode">
          <div class="pdet-content page-stage page-stage-3">
            <section
              v-if="bloquePrincipal.length || clasificacionInstitucional.length"
              class="pdet-section"
            >
              <div class="pdet-sectionHead">
                <h2 class="pdet-h2">{{ bloquePrincipalTitle }}</h2>
                <p class="pdet-sectionText">
                  {{ bloquePrincipalText }}
                </p>
              </div>

              <div class="pdet-sectionBody">
                <div
                  v-if="bloquePrincipal.length"
                  class="pdet-dataGrid pdet-dataGrid--duo"
                >
                  <article
                    v-for="campo in bloquePrincipal"
                    :key="campo.label"
                    class="pdet-dataItem"
                    :class="`span-${campo.span || 4}`"
                  >
                    <span class="k">{{ campo.label }}</span>

                    <template v-if="campo.href">
                      <a
                        :href="campo.href"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="pdet-link"
                      >
                        {{ campo.value }}
                      </a>
                    </template>

                    <template v-else>
                      <span class="v">{{ campo.value }}</span>
                    </template>
                  </article>
                </div>

                <div
                  v-if="clasificacionInstitucional.length"
                  class="pdet-sectionSubgroup"
                >
                  <div class="pdet-subHead">
                    <h3 class="pdet-h3">Clasificación institucional</h3>
                    <p class="pdet-subText">
                      Adscripción y contexto académico del registro.
                    </p>
                  </div>

                  <div class="pdet-dataGrid pdet-dataGrid--tri">
                    <article
                      v-for="campo in clasificacionInstitucional"
                      :key="campo.label"
                      class="pdet-dataItem"
                      :class="`span-${campo.span || 4}`"
                    >
                      <span class="k">{{ campo.label }}</span>
                      <span class="v">{{ campo.value }}</span>
                    </article>
                  </div>
                </div>
              </div>
            </section>

            <section class="pdet-section">
              <div class="pdet-sectionHead">
                <h2 class="pdet-h2">
                  Autores
                  <span v-if="detalleNormalizado.autores.length" class="pdet-count">
                    ({{ detalleNormalizado.autores.length }})
                  </span>
                </h2>
                <p class="pdet-sectionText">
                  Autor principal y coautores registrados.
                </p>
              </div>

              <div v-if="detalleNormalizado.autores.length" class="pdet-authorList">
                <article
                  v-for="(autor, index) in detalleNormalizado.autores"
                  :key="autor.id || index"
                  class="pdet-authorRow"
                >
                  <div class="pdet-authorIndex">{{ index + 1 }}</div>

                  <div class="pdet-authorBody">
                    <h3 class="pdet-authorName">{{ autor.nombre }}</h3>
                    <p class="pdet-authorMeta">{{ autor.rol }}</p>
                  </div>
                </article>
              </div>

              <p v-else class="pdet-muted">
                No hay autores registrados.
              </p>
            </section>

            <section v-if="descripcionTexto" class="pdet-section">
              <div class="pdet-sectionHead">
                <h2 class="pdet-h2">Descripción</h2>
                <p class="pdet-sectionText">
                  Información complementaria del registro.
                </p>
              </div>

              <div class="pdet-notePanel">
                <div class="pdet-note">
                  {{ descripcionTexto }}
                </div>
              </div>
            </section>

            <section v-if="hasPdf" class="pdet-section">
              <div class="pdet-sectionHead">
                <h2 class="pdet-h2">Adjuntos</h2>
                <p class="pdet-sectionText">
                  Archivo asociado a la publicación.
                </p>
              </div>

              <div class="pdet-filePanel">
                <div class="pdet-fileMeta">
                  <span class="pdet-fileEyebrow">Documento</span>
                  <h3 class="pdet-fileName">
                    {{ fileNameFromUrl(detalleNormalizado.archivoPdfUrl) }}
                  </h3>
                  <p class="pdet-fileText">
                    PDF adjunto al registro.
                  </p>
                </div>

                <div class="pdet-fileActions">
                  <button class="pdet-btn" type="button" @click="openPdf">
                    Ver PDF
                  </button>

                  <button
                    class="pdet-btn pdet-btn--primary"
                    type="button"
                    @click="downloadPdf"
                  >
                    Descargar PDF
                  </button>
                </div>
              </div>
            </section>

            <section v-if="identificadoresAcademicos.length" class="pdet-section">
              <div class="pdet-sectionHead">
                <h2 class="pdet-h2">Identificadores</h2>
                <p class="pdet-sectionText">
                  Datos técnicos y académicos del registro.
                </p>
              </div>

              <div class="pdet-dataGrid pdet-dataGrid--tri">
                <article
                  v-for="campo in identificadoresAcademicos"
                  :key="campo.label"
                  class="pdet-dataItem"
                  :class="`span-${campo.span || 4}`"
                >
                  <span class="k">{{ campo.label }}</span>

                  <template v-if="campo.href">
                    <a
                      :href="campo.href"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="pdet-link"
                    >
                      {{ campo.value }}
                    </a>
                  </template>

                  <template v-else>
                    <span class="v">{{ campo.value }}</span>
                  </template>
                </article>
              </div>
            </section>
          </div>
        </template>

        <!-- MODO EDICIÓN -->
        <section v-else-if="canEdit" class="pdet-editShell page-stage page-stage-3">
          <PublicacionEditForm
            :detalle="detalle"
            :saving="saving"
            :can-edit="canEdit"
            :is-admin="isAdmin"
            @saving="saving = $event"
            @updated="onUpdated"
            @cancel="editMode = false"
          />
        </section>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";
import PublicacionEditForm from "./EditarPublicacionView.vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const detalle = ref(null);
const loading = ref(true);
const error = ref("");
const editMode = ref(false);
const saving = ref(false);

let requestSeq = 0;

const toStr = (value) => (value == null ? "" : String(value).trim());

const firstFilled = (...values) => values.map(toStr).find(Boolean) || "";

const stripAccents = (value) =>
  toStr(value).normalize("NFD").replace(/[\u0300-\u036f]/g, "");

const normalizeEmail = (value) => stripAccents(value).toLowerCase().trim();

const toPositiveInt = (value) => {
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : null;
};

const uniqueNumbers = (values = []) => [...new Set(values.map(toPositiveInt).filter(Boolean))];

const uniqueStrings = (values = []) =>
  [...new Set(values.map((v) => toStr(v)).filter(Boolean))];

const readLocalUser = () => {
  if (typeof window === "undefined") return {};

  try {
    const parsed = JSON.parse(localStorage.getItem("user") || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
};

const pickFirstObject = (...values) =>
  values.find((item) => item && typeof item === "object" && !Array.isArray(item)) || {};

const currentUser = computed(() => {
  const fromStore = pickFirstObject(
    userStore?.user,
    userStore?.profile,
    userStore?.me,
    userStore?.currentUser,
    userStore?.usuario,
    userStore?.$state?.user,
    userStore?.$state?.profile,
    userStore?.$state?.me,
    userStore?.$state?.currentUser,
    userStore?.$state?.usuario
  );

  const fromLocal = readLocalUser();

  return {
    ...fromLocal,
    ...fromStore,
  };
});

const isAdmin = computed(() => {
  const u = currentUser.value || {};

  return !!(
    userStore?.isAdmin ||
    u?.is_staff ||
    u?.is_superuser ||
    firstFilled(u?.rol, u?.role).toLowerCase().includes("admin")
  );
});

const currentUserIds = computed(() =>
  uniqueNumbers([
    currentUser.value?.id,
    currentUser.value?.pk,
    currentUser.value?.user_id,
    currentUser.value?.usuario_id,
    currentUser.value?.usuario?.id,
    currentUser.value?.user?.id,
  ])
);

const currentAuthorIds = computed(() =>
  uniqueNumbers([
    currentUser.value?.autor_id,
    currentUser.value?.autorId,
    currentUser.value?.author_id,
    currentUser.value?.authorId,
    currentUser.value?.autor?.id,
    currentUser.value?.autor?.autor_id,
    currentUser.value?.autor_vinculado_id,
    currentUser.value?.autorVinculadoId,
    currentUser.value?.perfil?.autor_id,
    currentUser.value?.profile?.autor_id,
    userStore?.autor_id,
    userStore?.autorId,
    userStore?.user?.autor_id,
    userStore?.user?.autorId,
    userStore?.profile?.autor_id,
  ])
);

const currentEmails = computed(() =>
  uniqueStrings([
    normalizeEmail(currentUser.value?.email),
    normalizeEmail(currentUser.value?.correo),
    normalizeEmail(currentUser.value?.mail),
    normalizeEmail(currentUser.value?.usuario?.email),
    normalizeEmail(currentUser.value?.user?.email),
    normalizeEmail(currentUser.value?.profile?.email),
  ])
);

const normalizeTipo = (tipo) => {
  const t = stripAccents(tipo).toLowerCase();

  if (t.includes("ponencia")) return "ponencia";
  if (t.includes("articulo")) return "articulo";
  if (t.includes("capitulo")) return "capitulo";
  if (t.includes("libro")) return "libro";

  return "general";
};

const formatFecha = (fecha) => {
  const value = toStr(fecha);
  if (!value) return "";

  try {
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      const [y, m, d] = value.split("-").map(Number);
      const localDate = new Date(y, m - 1, d);

      return localDate.toLocaleDateString("es-EC", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    }

    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;

    return parsed.toLocaleDateString("es-EC", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return value;
  }
};

const ensureUrl = (url) => {
  const value = toStr(url);
  if (!value) return "";

  if (/^https?:\/\//i.test(value)) return value;
  if (value.startsWith("mailto:") || value.startsWith("tel:")) return value;

  return `https://${value.replace(/^\/+/, "")}`;
};

const doiUrl = (doi) => {
  const value = toStr(doi);
  if (!value) return "";

  if (/^https?:\/\//i.test(value)) return value;

  return `https://doi.org/${value
    .replace(/^doi:\s*/i, "")
    .replace(/^https?:\/\/(dx\.)?doi\.org\//i, "")}`;
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

const resolvePdfUrl = (url) => {
  const value = toStr(url);
  if (!value) return "";

  if (/^https?:\/\//i.test(value)) return value;
  if (value.startsWith("blob:") || value.startsWith("data:")) return value;

  const base = getBackendBase();
  const clean = value.startsWith("/") ? value : `/${value.replace(/^\.?\//, "")}`;

  return `${base}${clean}`;
};

const fileNameFromUrl = (url) => {
  const value = toStr(url);
  if (!value) return "archivo.pdf";

  try {
    const parsed = new URL(value, window.location.origin);
    const last = parsed.pathname.split("/").filter(Boolean).pop();
    return decodeURIComponent(last || "archivo.pdf");
  } catch {
    return "archivo.pdf";
  }
};

const buildField = (label, value, extra = {}) => ({
  label,
  value: toStr(value),
  ...extra,
});

const visibleFields = (fields = []) =>
  fields.filter((item) => item && toStr(item?.value));

const normalizeAuthors = (authors) => {
  if (!Array.isArray(authors)) return [];

  return authors
    .map((autor, index) => {
      const rolRaw = firstFilled(
        autor?.rol_autoria,
        autor?.tipo_participacion,
        autor?.rol
      );
      const rolNorm = stripAccents(rolRaw).toLowerCase();

      let rol = "Autor";
      if (rolNorm.includes("principal")) rol = "Autor principal";
      else if (rolNorm.includes("coautor")) rol = "Coautor";
      else if (rolRaw) rol = rolRaw;

      const authorIds = uniqueNumbers([
        autor?.autor_id,
        autor?.autorId,
        autor?.autor?.id,
        autor?.id,
        autor?.pk,
      ]);

      const userIds = uniqueNumbers([
        autor?.usuario_id,
        autor?.user_id,
        autor?.usuario?.id,
        autor?.user?.id,
        autor?.usuario?.pk,
        autor?.user?.pk,
      ]);

      const emails = uniqueStrings([
        normalizeEmail(autor?.correo),
        normalizeEmail(autor?.email),
        normalizeEmail(autor?.usuario?.email),
        normalizeEmail(autor?.user?.email),
        normalizeEmail(autor?.usuario?.correo),
      ]);

      return {
        id:
          autor?.id ??
          autor?.autor_id ??
          autor?.pk ??
          `${index}-${firstFilled(autor?.nombre, autor?.nombre_completo, "autor")}`,
        nombre: firstFilled(autor?.nombre, autor?.nombre_completo, "Autor"),
        rol,
        authorIds,
        userIds,
        emails,
      };
    })
    .filter((autor) => autor.nombre);
};

const detalleNormalizado = computed(() => {
  const d = detalle.value || {};

  const tipoLabel = firstFilled(
    d.tipo,
    d.tipo_publicacion,
    d.tipo_publicacion_final,
    "Publicación"
  );

  const tipoNorm = normalizeTipo(tipoLabel);

  const titulo = firstFilled(
    d.titulo,
    d.nombre_publicacion,
    d.titulo_publicacion,
    d.nombre_articulo,
    d.nombre_ponencia,
    d.nombre_capitulo,
    d.nombre_libro,
    d.proyecto,
    "Publicación"
  );

  const proyecto = firstFilled(d.proyecto, d.nombre_proyecto);
  const fechaTexto = formatFecha(d.fecha_publicacion);

  const pais = firstFilled(d.pais, d.pais_nombre);
  const ciudad = firstFilled(d.ciudad, d.ciudad_nombre);

  return {
    raw: d,
    titulo,
    tipoLabel,
    tipoNorm,
    proyecto: proyecto && proyecto !== titulo ? proyecto : "",
    fechaTexto,
    facultad: firstFilled(d.facultad, d.facultad_nombre),
    carrera: firstFilled(d.carrera, d.carrera_nombre),
    area: firstFilled(d.area, d.area_nombre),
    subarea: firstFilled(d.subarea, d.subarea_nombre),
    pais,
    ciudad,
    ubicacion: [pais, ciudad].filter(Boolean).join(", "),
    archivoPdfUrl: resolvePdfUrl(
      firstFilled(d.archivo_pdf_url, d.archivo_pdf, d.pdf, d.archivo)
    ),
    autores: normalizeAuthors(d.autores),
  };
});

const userOwnsPublication = computed(() => {
  const authors = detalleNormalizado.value.autores || [];
  if (!authors.length) return false;

  const myAuthorIds = currentAuthorIds.value;
  const myUserIds = currentUserIds.value;
  const myEmails = currentEmails.value;

  return authors.some((autor) => {
    const matchAuthorId =
      myAuthorIds.length > 0 &&
      autor.authorIds.some((id) => myAuthorIds.includes(id));

    const matchUserId =
      myUserIds.length > 0 &&
      autor.userIds.some((id) => myUserIds.includes(id));

    const matchEmail =
      myEmails.length > 0 &&
      autor.emails.some((email) => myEmails.includes(email));

    return matchAuthorId || matchUserId || matchEmail;
  });
});

const canEdit = computed(() => isAdmin.value || userOwnsPublication.value);

const hasPdf = computed(() => Boolean(detalleNormalizado.value.archivoPdfUrl));

const heroIntroText = computed(() => {
  if (isAdmin.value) {
    return "Consulta y administra esta publicación con acceso completo.";
  }

  if (userOwnsPublication.value) {
    return "Consulta y edita esta publicación porque estás vinculado como autor.";
  }

  return "Consulta su clasificación, metadatos, autores y evidencias disponibles.";
});

const toneClass = computed(() => {
  switch (detalleNormalizado.value.tipoNorm) {
    case "articulo":
      return "is-primary";
    case "ponencia":
      return "is-warning";
    case "capitulo":
      return "is-success";
    case "libro":
      return "is-neutral";
    default:
      return "";
  }
});

const bloquePrincipalTitle = computed(() => {
  switch (detalleNormalizado.value.tipoNorm) {
    case "ponencia":
      return "Evento y ponencia";
    case "articulo":
      return "Artículo";
    case "capitulo":
      return "Capítulo y libro";
    case "libro":
      return "Libro";
    default:
      return "Detalle de publicación";
  }
});

const bloquePrincipalText = computed(() => {
  switch (detalleNormalizado.value.tipoNorm) {
    case "ponencia":
      return "Información principal del evento y de la presentación.";
    case "articulo":
      return "Información principal del artículo y de su indexación.";
    case "capitulo":
      return "Información principal del capítulo y de la obra relacionada.";
    case "libro":
      return "Información principal del libro registrado.";
    default:
      return "Información principal del registro.";
  }
});

const descripcionTexto = computed(() =>
  firstFilled(
    detalle.value?.resumen,
    detalle.value?.descripcion,
    detalle.value?.abstract,
    detalle.value?.detalle
  )
);

const heroResumen = computed(() => {
  const d = detalleNormalizado.value;
  const totalAutores = d.autores.length;

  return visibleFields([
    buildField("Tipo", d.tipoLabel),
    buildField("Fecha", d.fechaTexto),
    buildField(
      "Autores",
      totalAutores ? `${totalAutores} ${totalAutores === 1 ? "autor" : "autores"}` : ""
    ),
    buildField("Documento", hasPdf.value ? "Disponible" : "Sin PDF"),
  ]);
});

const clasificacionInstitucional = computed(() => {
  const d = detalleNormalizado.value;

  return visibleFields([
    buildField("Facultad", d.facultad, { span: 4 }),
    buildField("Carrera", d.carrera, { span: 4 }),
    buildField("Área del conocimiento", d.area, { span: 4 }),
    buildField("Subárea del conocimiento", d.subarea, { span: 4 }),
    buildField("País", d.pais, { span: 4 }),
    buildField("Ciudad", d.ciudad, { span: 4 }),
  ]);
});

const bloquePrincipal = computed(() => {
  const d = detalle.value || {};
  const tipo = detalleNormalizado.value.tipoNorm;
  const titulo = detalleNormalizado.value.titulo;

  if (tipo === "ponencia") {
    const nombrePonencia = firstFilled(d.nombre_ponencia, d.titulo_ponencia);

    return visibleFields([
      buildField("Nombre del evento", firstFilled(d.nombre_evento, d.evento), { span: 6 }),
      nombrePonencia && nombrePonencia !== titulo
        ? buildField("Nombre de la ponencia", nombrePonencia, { span: 6 })
        : null,
      buildField("Fecha de presentación", formatFecha(d.fecha_publicacion), { span: 4 }),
      buildField("Tipo de presentación", firstFilled(d.tipo_presentacion), { span: 4 }),
      buildField("Enlace del evento", firstFilled(d.link_evento), {
        href: ensureUrl(d.link_evento),
        span: 12,
      }),
    ]);
  }

  if (tipo === "articulo") {
    const nombreArticulo = firstFilled(d.nombre_articulo, d.titulo_articulo);

    return visibleFields([
      nombreArticulo && nombreArticulo !== titulo
        ? buildField("Título del artículo", nombreArticulo, { span: 12 })
        : null,
      buildField("Revista", firstFilled(d.nombre_revista, d.revista), { span: 6 }),
      buildField(
        "Base de datos indexada",
        firstFilled(d.base_datos_indexada, d.base_datos, d.indexacion),
        { span: 6 }
      ),
      buildField(
        "Enlace del artículo",
        firstFilled(d.link_articulo, d.link_publicacion, d.enlace_articulo),
        {
          href: ensureUrl(
            firstFilled(d.link_articulo, d.link_publicacion, d.enlace_articulo)
          ),
          span: 12,
        }
      ),
    ]);
  }

  if (tipo === "capitulo") {
    const nombreCapitulo = firstFilled(d.nombre_capitulo, d.titulo_capitulo);

    return visibleFields([
      nombreCapitulo && nombreCapitulo !== titulo
        ? buildField("Capítulo", nombreCapitulo, { span: 12 })
        : null,
      buildField("Libro", firstFilled(d.nombre_libro, d.libro), { span: 6 }),
      buildField(
        "Editor / Compilador",
        firstFilled(d.editor_compilador, d.editor, d.compilador),
        { span: 6 }
      ),
      buildField("Enlace", firstFilled(d.link_capitulo), {
        href: ensureUrl(d.link_capitulo),
        span: 12,
      }),
    ]);
  }

  if (tipo === "libro") {
    const nombreLibro = firstFilled(d.nombre_libro, d.titulo_libro);

    return visibleFields([
      nombreLibro && nombreLibro !== titulo
        ? buildField("Título del libro", nombreLibro, { span: 12 })
        : null,
      buildField("Editorial", firstFilled(d.editorial), { span: 4 }),
      buildField("Edición", firstFilled(d.edicion), { span: 4 }),
      buildField("Fecha de publicación", formatFecha(d.fecha_publicacion), { span: 4 }),
      buildField("Enlace", firstFilled(d.link_libro), {
        href: ensureUrl(d.link_libro),
        span: 12,
      }),
    ]);
  }

  return visibleFields([
    buildField("Fecha de publicación", formatFecha(d.fecha_publicacion), { span: 4 }),
    buildField("Ubicación", detalleNormalizado.value.ubicacion, { span: 8 }),
  ]);
});

const identificadoresAcademicos = computed(() => {
  const d = detalle.value || {};
  const doi = firstFilled(d.codigo_doi, d.doi);

  return visibleFields([
    buildField("DOI", doi, { href: doiUrl(doi), span: 4 }),
    buildField("ISSN", firstFilled(d.codigo_issn, d.issn), { span: 4 }),
    buildField("ISBN", firstFilled(d.codigo_isbn, d.isbn), { span: 4 }),
    buildField("Código ISSN / ISBN", firstFilled(d.codigo_issn_isbn), { span: 4 }),
    buildField("Cuartil", firstFilled(d.cuartil), { span: 4 }),
    buildField("SJR", firstFilled(d.sjr), { span: 4 }),
  ]);
});

const goBack = () => {
  const from = toStr(route.query?.from).toLowerCase();

  if (window.history.length > 1) {
    router.back();
    return;
  }

  if (from === "mis-publicaciones" || from === "mias" || from === "mis_publicaciones") {
    router.push("/mis-publicaciones");
    return;
  }

  router.push("/publicaciones-listado");
};

const openEditMode = () => {
  if (!canEdit.value) return;
  editMode.value = true;
};

const openPdf = () => {
  const url = detalleNormalizado.value.archivoPdfUrl;
  if (!url) return;

  window.open(url, "_blank", "noopener,noreferrer");
};

const downloadPdf = () => {
  const url = detalleNormalizado.value.archivoPdfUrl;
  if (!url) return;

  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.download = fileNameFromUrl(url);

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const cargarDetalle = async (forcedId = route.params.id) => {
  const id = toStr(forcedId);
  const requestId = ++requestSeq;

  if (!id) {
    detalle.value = null;
    error.value = "El identificador de la publicación no es válido.";
    loading.value = false;
    return;
  }

  loading.value = true;
  error.value = "";
  editMode.value = false;

  try {
    const response = await api.get(`/publicaciones/${id}/`);

    if (requestId !== requestSeq) return;
    detalle.value = response.data;
  } catch (err) {
    if (requestId !== requestSeq) return;

    console.error(err);
    detalle.value = null;
    error.value =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      "Ocurrió un problema al obtener el detalle de la publicación.";
  } finally {
    if (requestId === requestSeq) {
      loading.value = false;
    }
  }
};

const onUpdated = async () => {
  await cargarDetalle(route.params.id);
  editMode.value = false;
};

watch(
  () => canEdit.value,
  (allowed) => {
    if (!allowed) {
      editMode.value = false;
    }
  },
  { immediate: true }
);

watch(
  () => route.params.id,
  async (newId) => {
    await cargarDetalle(newId);
  },
  { immediate: true }
);
</script>

<style src="./detalle-publicacion.css"></style>