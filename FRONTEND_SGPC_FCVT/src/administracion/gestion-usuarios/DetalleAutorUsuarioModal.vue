<template>
  <Teleport to="body" :disabled="embedded">
    <div
      :class="
        embedded
          ? 'authordetail-embedded'
          : 'sgpc-admin-modal modal-overlay'
      "
      @click.self="handleBackdropClick"
    >
      <div
        ref="dialogRef"
        :class="[
          'modal',
          'modal--author-detail',
          {
            'modal--author-detail-embedded': embedded,
          },
        ]"
        :role="embedded ? 'region' : 'dialog'"
        :aria-modal="embedded ? undefined : 'true'"
        aria-labelledby="author-detail-dialog-title"
        tabindex="-1"
        @keydown="handleDialogKeydown"
      >
        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->
        <header class="modal__header authordetail-header">
          <div
            class="authordetail-avatar"
            aria-hidden="true"
          >
            {{ initials }}
          </div>

          <div class="authordetail-headcopy">
            <h2
              id="author-detail-dialog-title"
              class="modal__title authordetail-title"
            >
              {{ fullName }}
            </h2>

          </div>

          <div
            class="authordetail-headmeta"
            aria-label="Clasificación y estado de la cuenta"
          >
            <span
              class="authordetail-badge authordetail-badge--type"
            >
              {{ tipoLabel }}
            </span>

            <span
              class="authordetail-badge"
              :class="statusBadgeClass"
            >
              {{ estadoLabel }}
            </span>

            <span
              v-if="isAdmin"
              class="authordetail-badge authordetail-badge--admin"
            >
              Administrador
            </span>
          </div>

          <button
            v-if="!embedded"
            type="button"
            class="btn-cerrar modal__close authordetail-close"
            aria-label="Cerrar detalle del usuario"
            title="Cerrar"
            @click="requestClose"
          >
            <span aria-hidden="true">✕</span>
          </button>
        </header>

        <!-- =====================================================
             CONTENIDO
        ====================================================== -->
        <div class="modal__body authordetail-body">
          <!-- ===================================================
               DATOS DE LA CUENTA
          ==================================================== -->
          <section
            class="authordetail-section"
            aria-labelledby="author-detail-account-title"
          >
            <div class="authordetail-sectionrow">
              <div>
                <h3
                  id="author-detail-account-title"
                  class="authordetail-sectiontitle"
                >
                  Cuenta
                </h3>
              </div>
            </div>

            <dl class="authordetail-summary">
              <div
                class="authordetail-item authordetail-item--span-2"
              >
                <dt>Correo electrónico</dt>
                <dd>
                  {{
                    usuario?.email ||
                    "No registrado"
                  }}
                </dd>
              </div>

              <div class="authordetail-item">
                <dt>Cédula</dt>
                <dd>
                  {{
                    usuario?.identificacion ||
                    "No registrada"
                  }}
                </dd>
              </div>

              <div class="authordetail-item">
                <dt>Inicio de sesión</dt>
                <dd>{{ authSourceLabel }}</dd>
              </div>

              <div class="authordetail-item">
                <dt>Tipo</dt>
                <dd>{{ tipoLabel }}</dd>
              </div>

              <div class="authordetail-item">
                <dt>Estado</dt>
                <dd>{{ estadoLabel }}</dd>
              </div>

              <div class="authordetail-item">
                <dt>Perfil</dt>
                <dd>
                  {{
                    perfilCompleto
                      ? "Completo"
                      : "Incompleto"
                  }}
                </dd>
              </div>

              <div class="authordetail-item">
                <dt>Acceso</dt>
                <dd>
                  {{
                    isAdmin
                      ? "Administrador"
                      : "Usuario"
                  }}
                </dd>
              </div>
            </dl>

            <div
              v-if="isInstitucional"
              class="authordetail-academic"
            >
              <div class="authordetail-subsectionhead">
                <strong>Información académica</strong>
              </div>

              <dl class="authordetail-academic-grid">
                <div class="authordetail-item">
                  <dt>Sede</dt>
                  <dd>{{ sedeLabel }}</dd>
                </div>

                <div class="authordetail-item">
                  <dt>Facultad</dt>
                  <dd>{{ facultadLabel }}</dd>
                </div>

                <div
                  class="authordetail-item authordetail-item--span-2"
                >
                  <dt>Carrera</dt>
                  <dd>{{ carreraLabel }}</dd>
                </div>
              </dl>
            </div>

            <div
              v-else-if="isExterno"
              class="authordetail-inline-note"
            >
              <strong>Información académica</strong>
              <span>No aplica para usuarios externos.</span>
            </div>

            <div
              v-else
              class="authordetail-inline-note authordetail-inline-note--warn"
            >
              <strong>Información académica</strong>
              <span>Sin información disponible.</span>
            </div>
          </section>

          <!-- ===================================================
               PRODUCCIÓN CIENTÍFICA + PUBLICACIONES
          ==================================================== -->
          <section
            class="authordetail-section"
            aria-labelledby="author-detail-production-title"
          >
            <div class="authordetail-sectionrow">
              <div>
                <h3
                  id="author-detail-production-title"
                  class="authordetail-sectiontitle"
                >
                  Producción científica
                </h3>
              </div>

              <span
                class="authordetail-count"
                aria-live="polite"
              >
                {{ publicationCountLabel }}
              </span>
            </div>

            <div class="authordetail-production-summary">
              <div class="authordetail-author-identity">
                <div
                  class="authordetail-author-icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z"
                    />
                  </svg>
                </div>

                <div class="authordetail-author-copy">
                  <span>Autor</span>
                  <strong>
                    {{
                      usuario?.autor_nombre ||
                      "Sin información de autor"
                    }}
                  </strong>
                </div>
              </div>

              <div class="authordetail-production-stat">
                <span>Publicaciones</span>
                <strong>{{ totalPublicaciones }}</strong>
              </div>
            </div>

            <div class="authordetail-publications-head">
              <strong>Publicaciones</strong>
            </div>

            <!-- SIN PUBLICACIONES -->
            <div
              v-if="!publicaciones.length"
              class="authordetail-empty"
            >
              <div
                class="authordetail-empty__icon"
                aria-hidden="true"
              >
                <svg viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h5M8 13h8M8 17h8"
                  />
                </svg>
              </div>

              <div>
                <strong>Sin publicaciones</strong>
              </div>
            </div>

            <!-- LISTADO DE PUBLICACIONES -->
            <div
              v-else
              class="authordetail-pubs"
              role="list"
              aria-label="Publicaciones"
            >
              <div
                class="authordetail-pubs-header"
                aria-hidden="true"
              >
                <span>Publicación</span>
                <span>Período</span>
                <span>Participación</span>
              </div>

              <article
                v-for="(publication, index) in publicaciones"
                :key="publicationKey(publication, index)"
                class="authordetail-pub"
                role="listitem"
              >
                <div class="authordetail-pubmain">
                  <strong class="authordetail-pubtitle">
                    {{ publicationTitle(publication) }}
                  </strong>

                  <div class="authordetail-pubmeta">
                    <span>
                      {{ publicationType(publication) }}
                    </span>
                  </div>
                </div>

                <div class="authordetail-pubperiod">
                  <span>Período</span>
                  <strong>
                    {{ publicationPeriod(publication) }}
                  </strong>
                </div>

                <div class="authordetail-pubposition">
                  <span>Participación</span>
                  <strong>
                    {{
                      publicationOrder(publication)
                        ? `Autor ${publicationOrder(publication)}`
                        : "—"
                    }}
                  </strong>
                </div>
              </article>
            </div>
          </section>
        </div>

        <!-- =====================================================
             PIE
        ====================================================== -->
        <footer
          v-if="!embedded"
          class="modal__footer authordetail-footer"
        >
          <button
            v-if="showEditAction"
            type="button"
            class="
              authordetail-btn
              authordetail-btn--primary
            "
            @click="emit('edit')"
          >
            Editar usuario
          </button>

          <button
            ref="closeButtonRef"
            type="button"
            class="
              btn-cerrar
              authordetail-btn
              authordetail-btn--secondary
            "
            @click="requestClose"
          >
            Cerrar
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue";

import {
  calculateProfileComplete,
  getAccountTypeLabel,
  getAuthSourceLabel,
  isAdminUser,
  isExternalUser,
  isInstitutionalUser,
} from "../../scripts/utils/auth";


const props = defineProps({
  usuario: {
    type: Object,
    default: null,
  },

  embedded: {
    type: Boolean,
    default: false,
  },

  showEditAction: {
    type: Boolean,
    default: false,
  },
});

const embedded = computed(() =>
  Boolean(props.embedded)
);


const emit = defineEmits([
  "close",
  "edit",
]);


const dialogRef = ref(null);
const closeButtonRef = ref(null);


let previouslyFocusedElement = null;
let previousBodyOverflow = "";


/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) => {
  return String(value ?? "").trim();
};


const normalizeNumber = (
  value,
  fallback = 0
) => {
  const parsed = Number(value);

  if (
    Number.isFinite(parsed) &&
    parsed >= 0
  ) {
    return parsed;
  }

  return fallback;
};


/* ============================================================
   IDENTIDAD DEL USUARIO
============================================================ */

const fullName = computed(() => {
  const nombres = normalizeText(
    props.usuario?.nombres
  );

  const apellidos = normalizeText(
    props.usuario?.apellidos
  );

  return (
    `${nombres} ${apellidos}`.trim() ||
    "Usuario"
  );
});


const initials = computed(() => {
  const value = fullName.value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => {
      return part
        .charAt(0)
        .toUpperCase();
    })
    .join("");

  return value || "U";
});


/* ============================================================
   CLASIFICACIÓN
============================================================ */

const isInstitucional = computed(() => {
  return isInstitutionalUser(
    props.usuario
  );
});


const isExterno = computed(() => {
  return isExternalUser(
    props.usuario
  );
});


const isAdmin = computed(() => {
  return isAdminUser(
    props.usuario
  );
});


const isPending = computed(() => {
  return props.usuario?.es_pendiente === true;
});


const tipoLabel = computed(() => {
  const label = getAccountTypeLabel(
    props.usuario
  );

  if (label === "Cuenta institucional") {
    return "Institucional";
  }

  if (label === "Cuenta externa") {
    return "Externo";
  }

  return "Sin clasificación";
});


const authSourceLabel = computed(() => {
  return getAuthSourceLabel(
    props.usuario
  );
});


const perfilCompleto = computed(() => {
  if (
    typeof props.usuario?.perfil_completo ===
    "boolean"
  ) {
    return props.usuario.perfil_completo;
  }

  return calculateProfileComplete(
    props.usuario
  );
});


/* ============================================================
   ESTADO
============================================================ */

const estadoLabel = computed(() => {
  if (!props.usuario) {
    return "—";
  }

  if (isPending.value) {
    return "Pendiente";
  }

  return props.usuario?.is_active
    ? "Activo"
    : "Inactivo";
});


const statusBadgeClass = computed(() => {
  if (isPending.value) {
    return "authordetail-badge--pending";
  }

  return props.usuario?.is_active
    ? "authordetail-badge--active"
    : "authordetail-badge--inactive";
});


/* ============================================================
   RELACIÓN ACADÉMICA
============================================================ */

const sedeLabel = computed(() => {
  if (!isInstitucional.value) {
    return "No aplica";
  }

  return (
    props.usuario?.sede_nombre ||
    (
      typeof props.usuario?.sede ===
      "object"
        ? props.usuario.sede?.nombre
        : props.usuario?.sede
    ) ||
    "Sin asignar"
  );
});


const facultadLabel = computed(() => {
  if (!isInstitucional.value) {
    return "No aplica";
  }

  return (
    props.usuario?.facultad_nombre ||
    props.usuario?.facultad ||
    "Sin asignar"
  );
});


const carreraLabel = computed(() => {
  if (!isInstitucional.value) {
    return "No aplica";
  }

  return (
    props.usuario?.carrera_nombre ||
    (
      typeof props.usuario?.carrera ===
      "object"
        ? props.usuario.carrera?.nombre
        : null
    ) ||
    "Sin asignar"
  );
});


/* ============================================================
   AUTOR VINCULADO
============================================================ */

/* ============================================================
   PUBLICACIONES
============================================================ */

const publicaciones = computed(() => {
  const value =
    props.usuario?.publicaciones_relacionadas;

  return Array.isArray(value)
    ? value
    : [];
});


const totalPublicaciones = computed(() => {
  const declaredTotal =
    normalizeNumber(
      props.usuario?.total_publicaciones,
      -1
    );

  if (declaredTotal >= 0) {
    return declaredTotal;
  }

  return publicaciones.value.length;
});


const publicationCountLabel = computed(() => {
  const total =
    totalPublicaciones.value;

  return total === 1
    ? "1 publicación"
    : `${total} publicaciones`;
});


const publicationTitle = (publication) => {
  const title = normalizeText(
    publication?.label ||
    publication?.titulo
  );

  if (title) {
    return title;
  }

  const type = publicationType(
    publication
  );

  return type || "Publicación sin título";
};


const publicationType = (publication) => {
  return (
    normalizeText(
      publication?.tipo ||
      publication?.tipo_label ||
      publication?.tipo_codigo
    ) ||
    "Publicación"
  );
};


const MONTH_LABELS = Object.freeze({
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


const publicationPeriod = (publication) => {
  const rawYear =
    publication?.anio_publicacion ??
    publication?.anio ??
    null;

  const rawMonth =
    publication?.mes_publicacion ??
    publication?.mes ??
    null;

  const year = Number(rawYear);
  const month = Number(rawMonth);

  const backendMonthLabel = normalizeText(
    publication?.mes_publicacion_label
  );

  const monthLabel =
    backendMonthLabel ||
    (
      Number.isInteger(month) &&
      month >= 1 &&
      month <= 12
        ? MONTH_LABELS[month]
        : ""
    );

  const hasYear =
    Number.isInteger(year) &&
    year > 0;

  if (
    hasYear &&
    monthLabel
  ) {
    return `${monthLabel} de ${year}`;
  }

  if (hasYear) {
    return String(year);
  }

  if (monthLabel) {
    return monthLabel;
  }

  return "—";
};


const publicationOrder = (publication) => {
  const value = Number(
    publication?.orden
  );

  return (
    Number.isInteger(value) &&
    value > 0
  )
    ? value
    : null;
};


const publicationKey = (
  publication,
  index
) => {
  return [
    publication?.publicacion_id,
    publication?.id,
    publication?.numero,
    publication?.orden,
    publication?.anio_publicacion,
    publication?.mes_publicacion,
    index,
  ]
    .filter((value) => {
      return (
        value !== null &&
        value !== undefined &&
        value !== ""
      );
    })
    .join("-");
};


/* ============================================================
   ACCESIBILIDAD DEL MODAL
============================================================ */

const handleBackdropClick = () => {
  if (!embedded.value) {
    requestClose();
  }
};


const requestClose = () => {
  emit("close");
};


const getFocusableElements = () => {
  if (!dialogRef.value) {
    return [];
  }

  const selector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled]):not([type='hidden'])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  return Array.from(
    dialogRef.value.querySelectorAll(
      selector
    )
  ).filter((element) => {
    return Boolean(
      !element.hasAttribute("hidden") &&
      element.getAttribute("aria-hidden") !==
        "true" &&
      element.getClientRects().length > 0
    );
  });
};


const focusInitialControl = async () => {
  await nextTick();

  if (
    closeButtonRef.value instanceof
    HTMLElement
  ) {
    closeButtonRef.value.focus();
    return;
  }

  dialogRef.value?.focus();
};


const handleDialogKeydown = (event) => {
  if (embedded.value) {
    return;
  }

  if (event.key === "Escape") {
    event.preventDefault();
    requestClose();

    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getFocusableElements();

  if (!focusableElements.length) {
    event.preventDefault();
    dialogRef.value?.focus();

    return;
  }

  const firstElement =
    focusableElements[0];

  const lastElement =
    focusableElements[
      focusableElements.length - 1
    ];

  const activeElement =
    document.activeElement;

  if (
    event.shiftKey &&
    activeElement === firstElement
  ) {
    event.preventDefault();
    lastElement.focus();

    return;
  }

  if (
    !event.shiftKey &&
    activeElement === lastElement
  ) {
    event.preventDefault();
    firstElement.focus();
  }
};


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(() => {
  if (embedded.value) {
    return;
  }

  previouslyFocusedElement =
    document.activeElement;

  previousBodyOverflow =
    document.body.style.overflow;

  document.body.style.overflow =
    "hidden";

  focusInitialControl();
});


onBeforeUnmount(() => {
  if (embedded.value) {
    return;
  }

  document.body.style.overflow =
    previousBodyOverflow;

  if (
    previouslyFocusedElement instanceof
    HTMLElement
  ) {
    previouslyFocusedElement.focus();
  }
});
</script>

<style src="../styles/admin-shared.css"></style>

<style
  scoped
  src="./detalle-autor-usuario-modal.css"
></style>
