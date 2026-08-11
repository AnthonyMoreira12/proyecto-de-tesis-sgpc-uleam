<template>
  <div class="pdet-page">
    <div class="pdet-wrap">
      <!-- =====================================================
        ESTADO DE CARGA
      ====================================================== -->
      <section
        v-if="loading"
        class="pdet-state pdet-state--loading"
        aria-label="Cargando detalle de publicación"
        aria-live="polite"
      >
        <div class="pdet-skeleton">
          <div class="pdet-sk-topbar"></div>
          <div class="pdet-sk-hero"></div>
          <div class="pdet-sk-section"></div>
          <div class="pdet-sk-section"></div>
          <div class="pdet-sk-section"></div>
        </div>
      </section>

      <!-- =====================================================
        ESTADO DE ERROR
      ====================================================== -->
      <section
        v-else-if="error"
        class="pdet-state pdet-state--error page-stage page-stage-1"
        role="alert"
        aria-live="polite"
      >
        <div class="pdet-error">
          <span class="pdet-error__eyebrow">
            Detalle de publicación
          </span>

          <h1 class="pdet-error__title">
            No se pudo cargar la publicación
          </h1>

          <p class="pdet-error__text">
            {{ error }}
          </p>

          <div class="pdet-error__actions">
            <button
              class="pdet-btn pdet-btn--primary"
              type="button"
              @click="cargarDetalle()"
            >
              Reintentar
            </button>

            <button
              class="pdet-btn pdet-btn--ghost"
              type="button"
              @click="goBack"
            >
              Volver
            </button>
          </div>
        </div>
      </section>

      <!-- =====================================================
        DETALLE PRINCIPAL
      ====================================================== -->
      <article
        v-else-if="detalleNormalizado"
        class="pdet-shell"
      >
        <!-- ===================================================
          MODO LECTURA
        ==================================================== -->
        <template v-if="!editMode">
          <!-- Barra de navegación y acciones -->
          <header
            class="pdet-topbar page-stage page-stage-1"
            aria-label="Acciones del detalle"
          >
            <button
              class="pdet-back"
              type="button"
              @click="goBack"
            >
              <span
                class="pdet-back__icon"
                aria-hidden="true"
              >
                ←
              </span>

              <span>Volver a publicaciones</span>
            </button>

            <div class="pdet-topbar__actions">
              <button
                v-if="hasPdf"
                class="pdet-btn pdet-btn--ghost"
                type="button"
                @click="openPdf"
              >
                Ver PDF
              </button>

              <button
                v-if="canEdit"
                class="pdet-btn pdet-btn--primary"
                type="button"
                @click="openEditMode"
              >
                Editar publicación
              </button>
            </div>
          </header>

          <!-- Encabezado principal -->
          <section
            class="pdet-hero page-stage page-stage-2"
            aria-labelledby="pdet-title"
          >
            <div class="pdet-hero__main">
              <span class="pdet-kicker">
                Producción científica
              </span>

              <div class="pdet-titleRow">
                <h1
                  id="pdet-title"
                  class="pdet-title"
                >
                  {{ detalleNormalizado.titulo }}
                </h1>

                <span
                  class="pdet-badge"
                  :class="toneClass"
                >
                  {{ detalleNormalizado.tipoLabel }}
                </span>
              </div>

              <p class="pdet-subtitle">
                {{ heroIntroText }}
              </p>

              <div
                class="pdet-chipRow"
                aria-label="Información resumida"
              >
                <span
                  v-if="detalleNormalizado.periodoTexto"
                  class="pdet-chip"
                >
                  {{ detalleNormalizado.periodoTexto }}
                </span>

                <span
                  v-if="detalleNormalizado.facultad"
                  class="pdet-chip"
                >
                  {{ detalleNormalizado.facultad }}
                </span>

                <span
                  v-if="detalleNormalizado.carrera"
                  class="pdet-chip"
                >
                  {{ detalleNormalizado.carrera }}
                </span>

                <span
                  v-if="detalleNormalizado.autores.length"
                  class="pdet-chip"
                >
                  {{ detalleNormalizado.autores.length }}
                  {{
                    detalleNormalizado.autores.length === 1
                      ? "autor"
                      : "autores"
                  }}
                </span>

                <span
                  v-if="isAdmin"
                  class="pdet-chip pdet-chip--permission"
                >
                  Administrador
                </span>

                <span
                  v-else-if="canEdit"
                  class="pdet-chip pdet-chip--permission"
                >
                  Puede editar
                </span>
              </div>

              <p
                v-if="detalleNormalizado.proyecto"
                class="pdet-project"
              >
                <span>Proyecto asociado</span>
                <strong>{{ detalleNormalizado.proyecto }}</strong>
              </p>
            </div>

            <aside
              v-if="heroResumen.length"
              class="pdet-hero__panel"
              aria-label="Resumen rápido"
            >
              <header class="pdet-panelHead">
                <span class="pdet-panelEyebrow">
                  Resumen
                </span>

                <h2 class="pdet-panelTitle">
                  Datos principales
                </h2>

                <p class="pdet-panelText">
                  Lectura rápida de la información esencial del registro.
                </p>
              </header>

              <div class="pdet-summaryGrid">
                <article
                  v-for="item in heroResumen"
                  :key="item.label"
                  class="pdet-summaryItem"
                >
                  <span class="k">
                    {{ item.label }}
                  </span>

                  <span class="v">
                    {{ item.value }}
                  </span>
                </article>
              </div>
            </aside>
          </section>

          <!-- =================================================
            CONTENIDO
          ================================================== -->
          <div class="pdet-content page-stage page-stage-3">
            <!-- Información principal -->
            <section
              v-if="
                bloquePrincipal.length ||
                clasificacionInstitucional.length
              "
              class="pdet-section"
            >
              <header class="pdet-sectionHead">
                <div>
                  <span class="pdet-sectionEyebrow">
                    Información académica
                  </span>

                  <h2 class="pdet-h2">
                    {{ bloquePrincipalTitle }}
                  </h2>
                </div>

                <p class="pdet-sectionText">
                  {{ bloquePrincipalText }}
                </p>
              </header>

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
                    <span class="k">
                      {{ campo.label }}
                    </span>

                    <a
                      v-if="campo.href"
                      :href="campo.href"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="pdet-link"
                    >
                      {{ campo.value }}
                    </a>

                    <span
                      v-else
                      class="v"
                    >
                      {{ campo.value }}
                    </span>
                  </article>
                </div>

                <div
                  v-if="clasificacionInstitucional.length"
                  class="pdet-sectionSubgroup"
                >
                  <header class="pdet-subHead">
                    <h3 class="pdet-h3">
                      Clasificación institucional
                    </h3>

                    <p class="pdet-subText">
                      Adscripción y contexto académico de la publicación.
                    </p>
                  </header>

                  <div class="pdet-dataGrid pdet-dataGrid--tri">
                    <article
                      v-for="campo in clasificacionInstitucional"
                      :key="campo.label"
                      class="pdet-dataItem"
                      :class="`span-${campo.span || 4}`"
                    >
                      <span class="k">
                        {{ campo.label }}
                      </span>

                      <span class="v">
                        {{ campo.value }}
                      </span>
                    </article>
                  </div>
                </div>
              </div>
            </section>

            <!-- Autores -->
            <section class="pdet-section">
              <header class="pdet-sectionHead">
                <div>
                  <span class="pdet-sectionEyebrow">
                    Participación
                  </span>

                  <h2 class="pdet-h2">
                    Autores

                    <span
                      v-if="detalleNormalizado.autores.length"
                      class="pdet-count"
                    >
                      {{ detalleNormalizado.autores.length }}
                    </span>
                  </h2>
                </div>

                <p class="pdet-sectionText">
                  Autores vinculados a la publicación en su orden bibliográfico.
                </p>
              </header>

              <div
                v-if="detalleNormalizado.autores.length"
                class="pdet-authorList"
              >
                <article
                  v-for="(autor, index) in detalleNormalizado.autores"
                  :key="autor.id || index"
                  class="pdet-authorRow"
                >
                  <div
                    class="pdet-authorIndex"
                    aria-hidden="true"
                  >
                    {{ index + 1 }}
                  </div>

                  <div class="pdet-authorBody">
                    <h3 class="pdet-authorName">
                      {{ autor.nombre }}
                    </h3>

                    <p class="pdet-authorMeta">
                      Orden bibliográfico {{ autor.orden }}
                    </p>
                  </div>
                </article>
              </div>

              <p
                v-else
                class="pdet-muted"
              >
                No hay autores registrados.
              </p>
            </section>

            <!-- Descripción -->
            <section
              v-if="descripcionTexto"
              class="pdet-section"
            >
              <header class="pdet-sectionHead">
                <div>
                  <span class="pdet-sectionEyebrow">
                    Contenido
                  </span>

                  <h2 class="pdet-h2">
                    Descripción
                  </h2>
                </div>

                <p class="pdet-sectionText">
                  Información complementaria registrada para esta publicación.
                </p>
              </header>

              <div class="pdet-notePanel">
                <p class="pdet-note">
                  {{ descripcionTexto }}
                </p>
              </div>
            </section>

            <!-- PDF -->
            <section
              v-if="hasPdf"
              class="pdet-section"
            >
              <header class="pdet-sectionHead">
                <div>
                  <span class="pdet-sectionEyebrow">
                    Evidencia documental
                  </span>

                  <h2 class="pdet-h2">
                    Archivo PDF
                  </h2>
                </div>

                <p class="pdet-sectionText">
                  Documento asociado al registro de la publicación.
                </p>
              </header>

              <div class="pdet-filePanel">
                <div class="pdet-fileIcon">
                  <span aria-hidden="true">PDF</span>
                </div>

                <div class="pdet-fileMeta">
                  <span class="pdet-fileEyebrow">
                    Documento disponible
                  </span>

                  <h3 class="pdet-fileName">
                    {{ displayPdfName }}
                  </h3>

                  <p class="pdet-fileText">
                    Puede visualizar o descargar el archivo asociado.
                  </p>
                </div>

                <div class="pdet-fileActions">
                  <button
                    class="pdet-btn pdet-btn--ghost"
                    type="button"
                    @click="openPdf"
                  >
                    Ver PDF
                  </button>

                  <button
                    class="pdet-btn pdet-btn--primary"
                    type="button"
                    @click="downloadPdf"
                  >
                    Descargar
                  </button>
                </div>
              </div>
            </section>

            <!-- Identificadores -->
            <section
              v-if="identificadoresAcademicos.length"
              class="pdet-section"
            >
              <header class="pdet-sectionHead">
                <div>
                  <span class="pdet-sectionEyebrow">
                    Referencias académicas
                  </span>

                  <h2 class="pdet-h2">
                    Identificadores
                  </h2>
                </div>

                <p class="pdet-sectionText">
                  Códigos e indicadores técnicos de la publicación.
                </p>
              </header>

              <div class="pdet-dataGrid pdet-dataGrid--tri">
                <article
                  v-for="campo in identificadoresAcademicos"
                  :key="campo.label"
                  class="pdet-dataItem"
                  :class="`span-${campo.span || 4}`"
                >
                  <span class="k">
                    {{ campo.label }}
                  </span>

                  <a
                    v-if="campo.href"
                    :href="campo.href"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="pdet-link"
                  >
                    {{ campo.value }}
                  </a>

                  <span
                    v-else
                    class="v"
                  >
                    {{ campo.value }}
                  </span>
                </article>
              </div>
            </section>
          </div>
        </template>

        <!-- ===================================================
          MODO EDICIÓN
        ==================================================== -->
        <section
          v-else-if="canEdit"
          class="pdet-editShell page-stage page-stage-2"
          aria-label="Edición de publicación"
        >
          <header class="pdet-editHeader">
            <div>
              <span class="pdet-editHeader__eyebrow">
                Gestión del registro
              </span>

              <h1 class="pdet-editHeader__title">
                Editar publicación
              </h1>

              <p class="pdet-editHeader__text">
                Actualice la información académica y documental del registro.
              </p>
            </div>

            <button
              class="pdet-btn pdet-btn--ghost"
              type="button"
              :disabled="saving"
              @click="editMode = false"
            >
              Volver al detalle
            </button>
          </header>

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

/* ============================================================
  NAVEGACIÓN Y SESIÓN
============================================================ */

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

/* ============================================================
  ESTADO PRINCIPAL
============================================================ */

const detalle = ref(null);
const loading = ref(true);
const error = ref("");
const editMode = ref(false);
const saving = ref(false);

let requestSeq = 0;

/* ============================================================
  HELPERS GENERALES
============================================================ */

const toStr = (value) => {
  return value == null
    ? ""
    : String(value).trim();
};

const firstFilled = (...values) => {
  return values
    .map(toStr)
    .find(Boolean) || "";
};

const stripAccents = (value) => {
  return toStr(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
};

const normalizeEmail = (value) => {
  return stripAccents(value)
    .toLowerCase()
    .trim();
};

const toPositiveInt = (value) => {
  const number = Number(value);

  return Number.isFinite(number) && number > 0
    ? number
    : null;
};

const uniqueNumbers = (values = []) => {
  return [
    ...new Set(
      values
        .map(toPositiveInt)
        .filter(Boolean)
    ),
  ];
};

const uniqueStrings = (values = []) => {
  return [
    ...new Set(
      values
        .map((value) => toStr(value))
        .filter(Boolean)
    ),
  ];
};

/* ============================================================
  USUARIO ACTUAL
============================================================ */

const readLocalUser = () => {
  if (typeof window === "undefined") {
    return {};
  }

  try {
    const parsed = JSON.parse(
      localStorage.getItem("user") || "{}"
    );

    return (
      parsed &&
      typeof parsed === "object" &&
      !Array.isArray(parsed)
    )
      ? parsed
      : {};
  } catch {
    return {};
  }
};

const pickFirstObject = (...values) => {
  return (
    values.find(
      (item) =>
        item &&
        typeof item === "object" &&
        !Array.isArray(item)
    ) || {}
  );
};

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
  const user = currentUser.value || {};

  return Boolean(
    userStore?.isAdmin ||
      user?.is_staff ||
      user?.is_superuser ||
      firstFilled(
        user?.rol,
        user?.role
      )
        .toLowerCase()
        .includes("admin")
  );
});

const currentUserIds = computed(() => {
  return uniqueNumbers([
    currentUser.value?.id,
    currentUser.value?.pk,
    currentUser.value?.user_id,
    currentUser.value?.usuario_id,
    currentUser.value?.usuario?.id,
    currentUser.value?.user?.id,
  ]);
});

const currentAuthorIds = computed(() => {
  return uniqueNumbers([
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
  ]);
});

const currentEmails = computed(() => {
  return uniqueStrings([
    normalizeEmail(currentUser.value?.email),
    normalizeEmail(currentUser.value?.correo),
    normalizeEmail(currentUser.value?.mail),
    normalizeEmail(currentUser.value?.usuario?.email),
    normalizeEmail(currentUser.value?.user?.email),
    normalizeEmail(currentUser.value?.profile?.email),
  ]);
});

/* ============================================================
  NORMALIZACIÓN DE TIPO Y PERÍODO
============================================================ */

const normalizeTipo = (tipo) => {
  const normalized = stripAccents(tipo).toLowerCase();

  if (normalized.includes("ponencia")) {
    return "ponencia";
  }

  if (normalized.includes("articulo")) {
    return "articulo";
  }

  if (normalized.includes("capitulo")) {
    return "capitulo";
  }

  if (normalized.includes("libro")) {
    return "libro";
  }

  return "general";
};

const MONTH_NAMES_ES = Object.freeze({
  1: "Enero",
  2: "Febrero",
  3: "Marzo",
  4: "Abril",
  5: "Mayo",
  6: "Junio",
  7: "Julio",
  8: "Agosto",
  9: "Septiembre",
  10: "Octubre",
  11: "Noviembre",
  12: "Diciembre",
});

const formatPublicationPeriod = (
  yearValue,
  monthValue,
  monthLabelValue = ""
) => {
  const year = toPositiveInt(yearValue);

  if (!year) {
    return "";
  }

  const month = toPositiveInt(monthValue);

  if (
    month &&
    month >= 1 &&
    month <= 12
  ) {
    const label =
      firstFilled(
        monthLabelValue,
        MONTH_NAMES_ES[month]
      ) ||
      MONTH_NAMES_ES[month];

    return `${label} de ${year}`;
  }

  return String(year);
};

/* ============================================================
  URLS
============================================================ */

const ensureUrl = (url) => {
  const value = toStr(url);

  if (!value) {
    return "";
  }

  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  if (
    value.startsWith("mailto:") ||
    value.startsWith("tel:")
  ) {
    return value;
  }

  return `https://${value.replace(/^\/+/, "")}`;
};

const doiUrl = (doi) => {
  const value = toStr(doi);

  if (!value) {
    return "";
  }

  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  return `https://doi.org/${value
    .replace(/^doi:\s*/i, "")
    .replace(
      /^https?:\/\/(dx\.)?doi\.org\//i,
      ""
    )}`;
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

const resolvePdfUrl = (url) => {
  const value = toStr(url);

  if (!value) {
    return "";
  }

  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  if (
    value.startsWith("blob:") ||
    value.startsWith("data:")
  ) {
    return value;
  }

  const base = getBackendBase();

  const clean = value.startsWith("/")
    ? value
    : `/${value.replace(/^\.?\//, "")}`;

  return `${base}${clean}`;
};

const fileNameFromUrl = (url) => {
  const value = toStr(url);

  if (!value) {
    return "";
  }

  try {
    const parsed = new URL(
      value,
      window.location.origin
    );

    const last = parsed.pathname
      .split("/")
      .filter(Boolean)
      .pop();

    return decodeURIComponent(last || "");
  } catch {
    return "";
  }
};

/* ============================================================
  CAMPOS
============================================================ */

const buildField = (
  label,
  value,
  extra = {}
) => ({
  label,
  value: toStr(value),
  ...extra,
});

const visibleFields = (fields = []) => {
  return fields.filter(
    (item) =>
      item &&
      toStr(item?.value)
  );
};

/* ============================================================
  AUTORES
============================================================ */

const normalizeAuthors = (authors) => {
  if (!Array.isArray(authors)) {
    return [];
  }

  return authors
    .map((autor, index) => {
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

      const rawOrder =
        Number(
          autor?.orden ??
          autor?.order ??
          index + 1
        );

      const orden = (
        Number.isInteger(rawOrder) &&
        rawOrder > 0
      )
        ? rawOrder
        : index + 1;

      return {
        id:
          autor?.autor_id ??
          autor?.id ??
          autor?.pk ??
          `${index}-${firstFilled(
            autor?.nombre,
            autor?.nombre_completo,
            "autor"
          )}`,

        nombre: firstFilled(
          autor?.nombre,
          autor?.nombre_completo,
          "Autor"
        ),

        orden,
        authorIds,
        userIds,
        emails,
      };
    })
    .filter((autor) => autor.nombre)
    .sort((a, b) => {
      if (a.orden !== b.orden) {
        return a.orden - b.orden;
      }

      return a.nombre.localeCompare(
        b.nombre,
        "es",
        {
          sensitivity: "base",
        }
      );
    });
};

/* ============================================================
  DETALLE NORMALIZADO
============================================================ */

const detalleNormalizado = computed(() => {
  const data = detalle.value || {};

  const tipoLabel = firstFilled(
    data.tipo,
    data.tipo_publicacion,
    data.tipo_publicacion_final_label,
    data.tipo_publicacion_final,
    "Publicación"
  );

  const tipoNorm = normalizeTipo(tipoLabel);

  const titulo = firstFilled(
    data.titulo,
    data.nombre_publicacion,
    data.titulo_publicacion,
    data.nombre_articulo,
    data.nombre_ponencia,
    data.nombre_capitulo,
    data.nombre_libro,
    data.proyecto,
    "Publicación"
  );

  const proyecto = firstFilled(
    data.proyecto,
    data.nombre_proyecto
  );

  const periodoTexto =
    formatPublicationPeriod(
      firstFilled(
        data.anio_publicacion,
        data.year,
        data.anio
      ),
      firstFilled(
        data.mes_publicacion,
        data.month,
        data.mes
      ),
      firstFilled(
        data.mes_publicacion_label,
        data.month_label,
        data.mes_label
      )
    );

  const pais = firstFilled(
    data.pais,
    data.pais_nombre
  );

  const ciudad = firstFilled(
    data.ciudad,
    data.ciudad_nombre
  );

  const archivoPdfUrl = resolvePdfUrl(
    firstFilled(
      data.archivo_pdf_url,
      data.pdf_url,
      data.archivo_pdf,
      data.pdf,
      data.archivo,
      data.archivos?.[0]?.url,
      data.archivos?.[0]?.archivo,
      data.archivos?.[0]?.archivo_url,
      data.adjuntos?.[0]?.url,
      data.adjuntos?.[0]?.archivo,
      data.adjuntos?.[0]?.archivo_url
    )
  );

  return {
    raw: data,
    titulo,
    tipoLabel,
    tipoNorm,

    proyecto:
      proyecto && proyecto !== titulo
        ? proyecto
        : "",

    periodoTexto,

    facultad: firstFilled(
      data.facultad,
      data.facultad_nombre
    ),

    carrera: firstFilled(
      data.carrera,
      data.carrera_nombre
    ),

    area: firstFilled(
      data.area,
      data.area_nombre
    ),

    subarea: firstFilled(
      data.subarea,
      data.subarea_nombre
    ),

    pais,
    ciudad,

    ubicacion: [
      pais,
      ciudad,
    ]
      .filter(Boolean)
      .join(", "),

    archivoPdfUrl,
    autores: normalizeAuthors(data.autores),
  };
});

/* ============================================================
  PDF Y PERMISOS
============================================================ */

const hasPdf = computed(() => {
  const data = detalle.value || {};

  return Boolean(
    detalleNormalizado.value.archivoPdfUrl ||
      data.tiene_pdf ||
      data.has_pdf ||
      data.archivo_pdf_url ||
      data.pdf_url ||
      data.archivo_pdf ||
      data.pdf ||
      data.archivo ||
      data.archivos?.length ||
      data.adjuntos?.length
  );
});

const displayPdfName = computed(() => {
  return (
    fileNameFromUrl(
      detalleNormalizado.value.archivoPdfUrl
    ) ||
    "publicacion.pdf"
  );
});

const userOwnsPublication = computed(() => {
  const authors =
    detalleNormalizado.value.autores || [];

  if (!authors.length) {
    return false;
  }

  const myAuthorIds =
    currentAuthorIds.value;

  const myUserIds =
    currentUserIds.value;

  const myEmails =
    currentEmails.value;

  return authors.some((autor) => {
    const matchesAuthorId =
      myAuthorIds.length > 0 &&
      autor.authorIds.some((id) =>
        myAuthorIds.includes(id)
      );

    const matchesUserId =
      myUserIds.length > 0 &&
      autor.userIds.some((id) =>
        myUserIds.includes(id)
      );

    const matchesEmail =
      myEmails.length > 0 &&
      autor.emails.some((email) =>
        myEmails.includes(email)
      );

    return (
      matchesAuthorId ||
      matchesUserId ||
      matchesEmail
    );
  });
});

const creatorUserId = computed(() => {
  return toPositiveInt(
    detalle.value?.usuario_creador_id ??
      detalle.value?.usuario_creador?.id ??
      detalle.value?.usuario_creador?.pk ??
      null
  );
});

const currentUserIsCreator = computed(() => {
  const creatorId = creatorUserId.value;

  if (!creatorId) {
    return false;
  }

  return currentUserIds.value.includes(creatorId);
});

const canEdit = computed(() => {
  const backendPermission =
    detalle.value?.puede_editar;

  // El backend es la autoridad principal.
  if (typeof backendPermission === "boolean") {
    return backendPermission;
  }

  // Respaldo para respuestas antiguas del API:
  // administrador o usuario que creó la publicación.
  return (
    isAdmin.value ||
    currentUserIsCreator.value
  );
});

/* ============================================================
  TEXTOS Y TONOS
============================================================ */

const heroIntroText = computed(() => {
  if (isAdmin.value) {
    return (
      "Consulte y administre la información académica, " +
      "documental y autoral de esta publicación."
    );
  }

  if (canEdit.value) {
    return (
      "Consulte y actualice la información académica, " +
      "documental y autoral de esta publicación."
    );
  }

  return (
    "Consulte la clasificación, los metadatos, los autores " +
    "y las evidencias disponibles."
  );
});

const toneClass = computed(() => {
  switch (
    detalleNormalizado.value.tipoNorm
  ) {
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
  switch (
    detalleNormalizado.value.tipoNorm
  ) {
    case "ponencia":
      return "Evento y ponencia";

    case "articulo":
      return "Información del artículo";

    case "capitulo":
      return "Capítulo y libro";

    case "libro":
      return "Información del libro";

    default:
      return "Información principal";
  }
});

const bloquePrincipalText = computed(() => {
  switch (
    detalleNormalizado.value.tipoNorm
  ) {
    case "ponencia":
      return (
        "Datos principales del evento y de la " +
        "presentación registrada."
      );

    case "articulo":
      return (
        "Datos editoriales, publicación e indexación " +
        "del artículo."
      );

    case "capitulo":
      return (
        "Datos del capítulo y de la obra académica " +
        "relacionada."
      );

    case "libro":
      return (
        "Datos editoriales y académicos del libro " +
        "registrado."
      );

    default:
      return (
        "Información principal asociada al registro."
      );
  }
});

/* ============================================================
  DESCRIPCIÓN Y RESUMEN
============================================================ */

const descripcionTexto = computed(() => {
  return firstFilled(
    detalle.value?.resumen,
    detalle.value?.descripcion,
    detalle.value?.abstract,
    detalle.value?.detalle
  );
});

const heroResumen = computed(() => {
  const normalized =
    detalleNormalizado.value;

  const totalAutores =
    normalized.autores.length;

  return visibleFields([
    buildField(
      "Tipo",
      normalized.tipoLabel
    ),

    buildField(
      "Período",
      normalized.periodoTexto
    ),

    buildField(
      "Autores",
      totalAutores
        ? `${totalAutores} ${
            totalAutores === 1
              ? "autor"
              : "autores"
          }`
        : ""
    ),

    buildField(
      "Documento",
      hasPdf.value
        ? "Disponible"
        : "Sin PDF"
    ),
  ]);
});

/* ============================================================
  CLASIFICACIÓN
============================================================ */

const clasificacionInstitucional = computed(() => {
  const normalized =
    detalleNormalizado.value;

  const data =
    detalle.value || {};

  return visibleFields([
    buildField(
      "Facultad",
      normalized.facultad,
      { span: 4 }
    ),

    buildField(
      "Carrera",
      normalized.carrera,
      { span: 4 }
    ),

    buildField(
      "Origen",
      firstFilled(
        data.origen_tipo_label,
        data.origen_tipo
      ),
      { span: 4 }
    ),

    buildField(
      "Grado / programa",
      data.origen_grado,
      { span: 4 }
    ),

    buildField(
      "Área del conocimiento",
      normalized.area,
      { span: 4 }
    ),

    buildField(
      "Subárea del conocimiento",
      normalized.subarea,
      { span: 4 }
    ),

    buildField(
      "País",
      normalized.pais,
      { span: 4 }
    ),

    buildField(
      "Ciudad",
      normalized.ciudad,
      { span: 4 }
    ),
  ]);
});

/* ============================================================
  BLOQUE PRINCIPAL POR TIPO
============================================================ */

const bloquePrincipal = computed(() => {
  const data = detalle.value || {};

  const tipo =
    detalleNormalizado.value.tipoNorm;

  const titulo =
    detalleNormalizado.value.titulo;

  if (tipo === "ponencia") {
    const nombrePonencia = firstFilled(
      data.nombre_ponencia,
      data.titulo_ponencia
    );

    return visibleFields([
      buildField(
        "Nombre del evento",
        firstFilled(
          data.nombre_evento,
          data.evento
        ),
        { span: 6 }
      ),

      nombrePonencia &&
      nombrePonencia !== titulo
        ? buildField(
            "Nombre de la ponencia",
            nombrePonencia,
            { span: 6 }
          )
        : null,

      buildField(
        "Período de presentación",
        detalleNormalizado.value.periodoTexto,
        { span: 4 }
      ),

      buildField(
        "Tipo de presentación",
        (
          data.tipo_presentacion === "otro"
            ? firstFilled(
                data.tipo_presentacion_otro,
                "Otro"
              )
            : firstFilled(
                data.tipo_presentacion_label,
                data.tipo_presentacion
              )
        ),
        { span: 4 }
      ),

      buildField(
        "Enlace del evento",
        firstFilled(data.link_evento),
        {
          href: ensureUrl(
            data.link_evento
          ),
          span: 12,
        }
      ),
    ]);
  }

  if (tipo === "articulo") {
    const nombreArticulo = firstFilled(
      data.nombre_articulo,
      data.titulo_articulo
    );

    return visibleFields([
      nombreArticulo &&
      nombreArticulo !== titulo
        ? buildField(
            "Título del artículo",
            nombreArticulo,
            { span: 12 }
          )
        : null,

      buildField(
        "Revista",
        firstFilled(
          data.nombre_revista,
          data.revista
        ),
        { span: 6 }
      ),

      buildField(
        "Base de datos indexada",
        (
          data.base_datos_indexada === "otra"
            ? firstFilled(
                data.base_datos_otra,
                "Otra"
              )
            : firstFilled(
                data.base_datos_indexada_label,
                data.base_datos_indexada,
                data.base_datos,
                data.indexacion
              )
        ),
        { span: 6 }
      ),

      buildField(
        "Enlace del artículo",
        firstFilled(
          data.link_articulo,
          data.link_publicacion,
          data.enlace_articulo
        ),
        {
          href: ensureUrl(
            firstFilled(
              data.link_articulo,
              data.link_publicacion,
              data.enlace_articulo
            )
          ),
          span: 12,
        }
      ),
    ]);
  }

  if (tipo === "capitulo") {
    const nombreCapitulo = firstFilled(
      data.nombre_capitulo,
      data.titulo_capitulo
    );

    return visibleFields([
      nombreCapitulo &&
      nombreCapitulo !== titulo
        ? buildField(
            "Capítulo",
            nombreCapitulo,
            { span: 12 }
          )
        : null,

      buildField(
        "Libro",
        firstFilled(
          data.nombre_libro,
          data.libro
        ),
        { span: 6 }
      ),

      buildField(
        "Editor o compilador",
        firstFilled(
          data.editor_compilador,
          data.editor,
          data.compilador
        ),
        { span: 4 }
      ),

      buildField(
        "Revisor par / arbitraje",
        data.revisor_par_arbitraje,
        { span: 4 }
      ),

      buildField(
        "Período de publicación",
        detalleNormalizado.value.periodoTexto,
        { span: 4 }
      ),

      buildField(
        "Enlace",
        firstFilled(data.link_capitulo),
        {
          href: ensureUrl(
            data.link_capitulo
          ),
          span: 12,
        }
      ),
    ]);
  }

  if (tipo === "libro") {
    const nombreLibro = firstFilled(
      data.nombre_libro,
      data.titulo_libro
    );

    return visibleFields([
      nombreLibro &&
      nombreLibro !== titulo
        ? buildField(
            "Título del libro",
            nombreLibro,
            { span: 12 }
          )
        : null,

      buildField(
        "Editorial / Compilador",
        firstFilled(
          data.editorial_compilador,
          data.editorial
        ),
        { span: 4 }
      ),

      buildField(
        "Revisor par / arbitraje",
        data.revisor_par_arbitraje,
        { span: 4 }
      ),

      buildField(
        "Período de publicación",
        detalleNormalizado.value.periodoTexto,
        { span: 4 }
      ),

      buildField(
        "Enlace",
        firstFilled(data.link_libro),
        {
          href: ensureUrl(
            data.link_libro
          ),
          span: 12,
        }
      ),
    ]);
  }

  return visibleFields([
    buildField(
      "Período de publicación",
      detalleNormalizado.value.periodoTexto,
      { span: 4 }
    ),

    buildField(
      "Ubicación",
      detalleNormalizado.value.ubicacion,
      { span: 8 }
    ),
  ]);
});

/* ============================================================
  IDENTIFICADORES ACADÉMICOS
============================================================ */

const identificadoresAcademicos = computed(() => {
  const data = detalle.value || {};

  const doi = firstFilled(
    data.codigo_doi,
    data.doi
  );

  const factorImpacto = stripAccents(
    firstFilled(
      data.factor_impacto,
      data.factor_impacto_label
    )
  ).toLowerCase();

  const indicadorImpacto = (() => {
    if (factorImpacto === "jcr") {
      return buildField(
        "JCR",
        firstFilled(data.jcr),
        { span: 4 }
      );
    }

    if (factorImpacto === "sjr") {
      return buildField(
        "SJR",
        firstFilled(data.sjr),
        { span: 4 }
      );
    }

    if (firstFilled(data.jcr)) {
      return buildField(
        "JCR",
        firstFilled(data.jcr),
        { span: 4 }
      );
    }

    if (firstFilled(data.sjr)) {
      return buildField(
        "SJR",
        firstFilled(data.sjr),
        { span: 4 }
      );
    }

    return null;
  })();

  return visibleFields([
    buildField(
      "DOI",
      doi,
      {
        href: doiUrl(doi),
        span: 4,
      }
    ),

    buildField(
      "ISSN",
      firstFilled(
        data.codigo_issn,
        data.issn
      ),
      { span: 4 }
    ),

    buildField(
      "ISBN",
      firstFilled(
        data.codigo_isbn,
        data.isbn
      ),
      { span: 4 }
    ),

    buildField(
      "Código ISSN o ISBN",
      firstFilled(
        data.codigo_issn_isbn
      ),
      { span: 4 }
    ),

    buildField(
      "Número de revista",
      firstFilled(data.numero_revista),
      { span: 4 }
    ),

    buildField(
      "Factor de impacto",
      firstFilled(
        data.factor_impacto_label,
        data.factor_impacto
      ),
      { span: 4 }
    ),

    buildField(
      "Cuartil",
      firstFilled(data.cuartil),
      { span: 4 }
    ),

    indicadorImpacto,
  ]);
});

/* ============================================================
  NAVEGACIÓN
============================================================ */

const goBack = () => {
  const from = toStr(
    route.query?.from
  ).toLowerCase();

  if (window.history.length > 1) {
    router.back();
    return;
  }

  if (
    from === "mis-publicaciones" ||
    from === "mias" ||
    from === "mis_publicaciones"
  ) {
    router.push("/mis-publicaciones");
    return;
  }

  router.push("/publicaciones-listado");
};

const openEditMode = () => {
  if (!canEdit.value) {
    return;
  }

  editMode.value = true;
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

const fetchPdfBlob = async (id) => {
  const response = await api.get(
    `/publicaciones/${id}/pdf/`,
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

const openPdf = async () => {
  const id = route.params.id;

  if (!id) {
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
    const blob = await fetchPdfBlob(id);

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

const downloadPdf = async () => {
  const id = route.params.id;

  if (!id) {
    return;
  }

  try {
    const blob = await fetchPdfBlob(id);

    const blobUrl =
      URL.createObjectURL(blob);

    const filename =
      displayPdfName.value ||
      "publicacion.pdf";

    const link =
      document.createElement("a");

    link.href = blobUrl;
    link.download = filename;

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
  CARGA DEL DETALLE
============================================================ */

const cargarDetalle = async (
  forcedId = route.params.id,
  options = {}
) => {
  const id = toStr(forcedId);

  const requestId = ++requestSeq;

  const keepEditMode =
    Boolean(options.keepEditMode);

  const silent =
    Boolean(options.silent);

  if (!id) {
    detalle.value = null;

    error.value =
      "El identificador de la publicación no es válido.";

    loading.value = false;

    return;
  }

  if (!silent) {
    loading.value = true;
  }

  error.value = "";

  if (!keepEditMode) {
    editMode.value = false;
  }

  try {
    const response = await api.get(
      `/publicaciones/${id}/`
    );

    if (requestId !== requestSeq) {
      return;
    }

    detalle.value = response.data;
  } catch (requestError) {
    if (requestId !== requestSeq) {
      return;
    }

    console.error(requestError);

    detalle.value = null;

    error.value =
      requestError?.response?.data?.detail ||
      requestError?.response?.data?.message ||
      "Ocurrió un problema al obtener el detalle de la publicación.";
  } finally {
    if (
      requestId === requestSeq &&
      !silent
    ) {
      loading.value = false;
    }
  }
};

const onUpdated = async () => {
  await cargarDetalle(
    route.params.id,
    {
      keepEditMode: true,
      silent: true,
    }
  );

  editMode.value = false;
};

/* ============================================================
  WATCHERS
============================================================ */

watch(
  () => canEdit.value,
  (allowed) => {
    if (!allowed) {
      editMode.value = false;
    }
  },
  {
    immediate: true,
  }
);

watch(
  () => route.params.id,
  async (newId) => {
    await cargarDetalle(newId);
  },
  {
    immediate: true,
  }
);
</script>

<style src="./detalle-publicacion.css"></style>
