<template>
  <div
    class="sgpc-admin-modal modal-overlay"
    @click.self="requestClose"
  >
    <div
      ref="dialogRef"
      class="modal modal--author-detail"
      role="dialog"
      aria-modal="true"
      aria-labelledby="author-detail-dialog-title"
      aria-describedby="author-detail-dialog-description"
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
          <div class="authordetail-topline">
            <span class="authordetail-kicker">
              Detalle de usuario
            </span>

            <span
              class="authordetail-badge"
              :class="statusBadgeClass"
            >
              {{ estadoLabel }}
            </span>

            <span
              class="authordetail-badge authordetail-badge--type"
            >
              {{ tipoLabel }}
            </span>

            <span
              v-if="isAdmin"
              class="authordetail-badge authordetail-badge--admin"
            >
              Administrador
            </span>

            <span
              v-if="usuario?.creado_desde_selector"
              class="authordetail-badge authordetail-badge--neutral"
            >
              Creado desde selector
            </span>
          </div>

          <h2
            id="author-detail-dialog-title"
            class="modal__title authordetail-title"
          >
            {{ fullName }}
          </h2>

          <p
            id="author-detail-dialog-description"
            class="authordetail-subtitle"
          >
            Información de la cuenta, autor vinculado y producción
            científica relacionada.
          </p>
        </div>

        <button
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
             INFORMACIÓN DE LA CUENTA
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
                Información de la cuenta
              </h3>

              <p class="authordetail-sectionsub">
                Datos de identificación, acceso y clasificación
                del usuario.
              </p>
            </div>
          </div>

          <dl class="authordetail-summary">
            <div
              class="authordetail-item authordetail-item--wide"
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
              <dt>Número de cédula</dt>

              <dd>
                {{
                  usuario?.identificacion ||
                  "No registrada"
                }}
              </dd>
            </div>

            <div class="authordetail-item">
              <dt>Tipo de cuenta</dt>

              <dd>{{ tipoLabel }}</dd>
            </div>

            <div class="authordetail-item">
              <dt>Estado</dt>

              <dd>{{ estadoLabel }}</dd>
            </div>

            <div class="authordetail-item">
              <dt>Autenticación</dt>

              <dd>{{ authSourceLabel }}</dd>
            </div>

            <div class="authordetail-item">
              <dt>Perfil completo</dt>

              <dd>
                {{
                  perfilCompleto
                    ? "Sí"
                    : "No"
                }}
              </dd>
            </div>

            <div
              class="authordetail-item authordetail-item--wide"
            >
              <dt>Facultad</dt>

              <dd>
                {{ facultadLabel }}
              </dd>
            </div>

            <div
              class="authordetail-item authordetail-item--wide"
            >
              <dt>Carrera</dt>

              <dd>
                {{ carreraLabel }}
              </dd>
            </div>
          </dl>

          <p
            v-if="isExterno"
            class="authordetail-sectionsub"
          >
            Las cuentas externas no registran Facultad ni Carrera.
          </p>

          <p
            v-else-if="!isInstitucional"
            class="authordetail-sectionsub"
          >
            La combinación actual de rol y autenticación no
            corresponde a una cuenta institucional ni externa.
          </p>
        </section>

        <!-- ===================================================
             RELACIÓN CON AUTOR
        ==================================================== -->
        <section
          class="authordetail-section"
          aria-labelledby="author-detail-author-title"
        >
          <div class="authordetail-sectionrow">
            <div>
              <h3
                id="author-detail-author-title"
                class="authordetail-sectiontitle"
              >
                Autor vinculado
              </h3>

              <p class="authordetail-sectionsub">
                Relación utilizada para asociar la producción
                científica con esta cuenta.
              </p>
            </div>

            <span
              class="authordetail-count"
              :class="{
                'authordetail-count--muted':
                  !hasLinkedAuthor,
              }"
            >
              {{
                hasLinkedAuthor
                  ? "Vinculado"
                  : "Sin vínculo"
              }}
            </span>
          </div>

          <div class="authordetail-author-card">
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
              <span>Nombre del autor</span>

              <strong>
                {{
                  usuario?.autor_nombre ||
                  "Sin autor vinculado"
                }}
              </strong>
            </div>

            <div class="authordetail-author-total">
              <span>Publicaciones</span>

              <strong>
                {{ totalPublicaciones }}
              </strong>
            </div>
          </div>
        </section>

        <!-- ===================================================
             PUBLICACIONES
        ==================================================== -->
        <section
          class="authordetail-section"
          aria-labelledby="author-detail-publications-title"
        >
          <div class="authordetail-sectionrow">
            <div>
              <h3
                id="author-detail-publications-title"
                class="authordetail-sectiontitle"
              >
                Publicaciones relacionadas
              </h3>

              <p class="authordetail-sectionsub">
                Registros donde el autor participa como autor
                principal o coautor.
              </p>
            </div>

            <span
              class="authordetail-count"
              aria-live="polite"
            >
              {{ publicationCountLabel }}
            </span>
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
              <strong>
                Sin publicaciones relacionadas
              </strong>

              <p>
                El autor vinculado todavía no participa en
                publicaciones registradas en el sistema.
              </p>
            </div>
          </div>

          <!-- LISTADO DE PUBLICACIONES -->
          <div
            v-else
            class="authordetail-pubs"
            role="list"
            aria-label="Publicaciones relacionadas"
          >
            <article
              v-for="(publication, index) in publicaciones"
              :key="publicationKey(publication, index)"
              class="authordetail-pub"
              role="listitem"
            >
              <div class="authordetail-pubindex">
                {{ index + 1 }}
              </div>

              <div class="authordetail-pubmain">
                <strong class="authordetail-pubtitle">
                  {{ publicationTitle(publication) }}
                </strong>

                <div class="authordetail-pubmeta">
                  <span>
                    {{ publicationType(publication) }}
                  </span>

                  <span aria-hidden="true">·</span>

                  <span>
                    Año:
                    {{ publicationYear(publication) }}
                  </span>

                  <template
                    v-if="
                      publication.orden !== null &&
                      publication.orden !== undefined
                    "
                  >
                    <span aria-hidden="true">·</span>

                    <span>
                      Orden:
                      {{ publication.orden }}
                    </span>
                  </template>

                  <template
                    v-if="publication.numero"
                  >
                    <span aria-hidden="true">·</span>

                    <span>
                      N.º {{ publication.numero }}
                    </span>
                  </template>
                </div>
              </div>

              <span class="authordetail-pill">
                {{ publicationRole(publication) }}
              </span>
            </article>
          </div>
        </section>
      </div>

      <!-- =====================================================
           PIE
      ====================================================== -->
      <footer class="modal__footer authordetail-footer">
        <button
          ref="closeButtonRef"
          type="button"
          class="btn-cerrar authordetail-btn"
          @click="requestClose"
        >
          Cerrar
        </button>
      </footer>
    </div>
  </div>
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
});


const emit = defineEmits([
  "close",
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

const hasLinkedAuthor = computed(() => {
  return Boolean(
    props.usuario?.tiene_autor ||
    props.usuario?.autor_id ||
    props.usuario?.autor_nombre
  );
});


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

  const number = publication?.numero;

  if (
    number !== null &&
    number !== undefined &&
    number !== ""
  ) {
    return `${type} N.º ${number}`;
  }

  return "Publicación sin título";
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


const publicationYear = (publication) => {
  return (
    publication?.anio_publicacion ||
    publication?.anio ||
    "—"
  );
};


const publicationRole = (publication) => {
  const roleLabel = normalizeText(
    publication?.rol_label
  );

  if (roleLabel) {
    return roleLabel;
  }

  const role = normalizeText(
    publication?.rol_autoria
  ).toLowerCase();

  if (
    role === "principal" ||
    publication?.orden === 1
  ) {
    return "Principal";
  }

  if (publication?.orden) {
    return `Coautor #${publication.orden}`;
  }

  return "Coautor";
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
    publication?.rol_autoria,
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
  previouslyFocusedElement =
    document.activeElement;

  previousBodyOverflow =
    document.body.style.overflow;

  document.body.style.overflow =
    "hidden";

  focusInitialControl();
});


onBeforeUnmount(() => {
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