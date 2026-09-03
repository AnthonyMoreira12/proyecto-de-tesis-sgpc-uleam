<template>
  <main class="solmod-page">
    <section class="solmod-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="solmod-hero">
        <div class="solmod-hero__copy">
          <span>Publicación aprobada</span>

          <h1>Solicitar modificación</h1>

          <p>
            Solicite la corrección de información sensible de una
            publicación aprobada. Los cambios serán revisados por
            un administrador antes de aplicarse.
          </p>
        </div>

        <button
          type="button"
          class="solmod-button solmod-button--secondary"
          :disabled="saving"
          @click="goBack"
        >
          Volver
        </button>
      </header>

      <!-- =====================================================
           CARGA
      ====================================================== -->
      <section
        v-if="loading"
        class="solmod-state solmod-state--loading"
      >
        <span class="solmod-spinner"></span>

        <div>
          <strong>Preparando solicitud</strong>

          <span>
            Consultando los campos que pueden modificarse.
          </span>
        </div>
      </section>

      <!-- =====================================================
           ERROR DE CARGA
      ====================================================== -->
      <p
        v-else-if="error"
        class="solmod-state solmod-state--error"
        role="alert"
      >
        {{ error }}
      </p>

      <!-- =====================================================
           SIN CAMPOS DISPONIBLES
      ====================================================== -->
      <section
        v-else-if="!allowed.length"
        class="solmod-empty"
      >
        <strong>
          No hay campos disponibles para solicitar
        </strong>

        <span>
          Esta publicación no tiene información sensible habilitada
          para modificación en este momento.
        </span>

        <button
          type="button"
          class="solmod-button solmod-button--secondary"
          @click="goBack"
        >
          Volver a la publicación
        </button>
      </section>

      <!-- =====================================================
           FORMULARIO
      ====================================================== -->
      <form
        v-else
        class="solmod-form"
        @submit.prevent="prepareSubmit"
      >
        <!-- ===================================================
             MOTIVO
        ==================================================== -->
        <section class="solmod-panel">
          <header class="solmod-panel__head">
            <div>
              <span>Justificación</span>

              <h2>Motivo de la solicitud</h2>

              <p>
                Explique brevemente por qué la información aprobada
                necesita ser corregida.
              </p>
            </div>
          </header>

          <label class="solmod-textarea-field">
            <span>Motivo</span>

            <textarea
              v-model.trim="motivo"
              rows="5"
              maxlength="4000"
              required
              placeholder="Describa la razón de la modificación solicitada."
            ></textarea>

            <small>
              {{ motivo.length }} / 4000
            </small>
          </label>
        </section>

        <!-- ===================================================
             CAMPOS
        ==================================================== -->
        <section class="solmod-panel">
          <header class="solmod-panel__head">
            <div>
              <span>Información a corregir</span>

              <h2>Campos de la publicación</h2>

              <p>
                Seleccione únicamente los datos que realmente
                necesitan una modificación.
              </p>
            </div>

            <span
              v-if="selected.length"
              class="solmod-count"
            >
              {{ selected.length }}
              {{
                selected.length === 1
                  ? "campo"
                  : "campos"
              }}
            </span>
          </header>

          <div class="solmod-fields">
            <article
              v-for="field in normalFields"
              :key="field"
              class="solmod-field"
              :class="{
                'is-selected':
                  selected.includes(field)
              }"
            >
              <!-- CABECERA DEL CAMPO -->
              <header class="solmod-field__head">
                <label class="solmod-check">
                  <input
                    v-model="selected"
                    type="checkbox"
                    :value="field"
                    @change="onFieldSelection(field)"
                  >

                  <span>
                    {{ label(field) }}
                  </span>
                </label>
              </header>

              <!-- VALOR ACTUAL -->
              <div class="solmod-current">
                <span>Valor actual</span>

                <strong>
                  {{ displayCurrent(field) }}
                </strong>
              </div>

              <!-- NUEVO VALOR -->
              <section
                v-if="selected.includes(field)"
                class="solmod-new-value"
              >
                <span class="solmod-new-value__label">
                  Valor solicitado
                </span>

                <!-- MES -->
                <select
                  v-if="field === 'mes_publicacion'"
                  v-model="values[field]"
                  required
                >
                  <option value="">
                    Seleccione
                  </option>

                  <option
                    v-for="(month, index) in months"
                    :key="month"
                    :value="index + 1"
                  >
                    {{ month }}
                  </option>
                </select>

                <!-- ORIGEN -->
                <select
                  v-else-if="field === 'origen_tipo'"
                  v-model="values[field]"
                  required
                >
                  <option value="ninguno">
                    Ninguno
                  </option>

                  <option value="tic">
                    Trabajo de integración curricular
                  </option>

                  <option value="maestria">
                    Tesis de maestría
                  </option>

                  <option value="doctoral">
                    Tesis doctoral
                  </option>

                  <option value="otro">
                    Otro
                  </option>
                </select>

                <!-- REVISIÓN POR PARES -->
                <select
                  v-else-if="field === 'revisor_par_arbitraje'"
                  v-model="values[field]"
                  required
                >
                  <option value="">
                    Seleccione
                  </option>

                  <option value="si">
                    Sí
                  </option>

                  <option value="no">
                    No
                  </option>
                </select>

                <!-- NUMÉRICOS -->
                <input
                  v-else-if="
                    field === 'anio_publicacion' ||
                    field === 'numero_revista'
                  "
                  v-model="values[field]"
                  type="number"
                  min="1"
                  required
                >

                <!-- URL -->
                <input
                  v-else-if="isUrl(field)"
                  v-model.trim="values[field]"
                  type="url"
                  placeholder="https://..."
                  required
                >

                <!-- TEXTO -->
                <input
                  v-else
                  v-model.trim="values[field]"
                  type="text"
                  :placeholder="
                    `Nuevo valor para ${label(field)}`
                  "
                  required
                >

                <!-- COMPARACIÓN -->
                <div
                  v-if="fieldHasChanged(field)"
                  class="solmod-change-preview"
                >
                  <div>
                    <span>Actual</span>

                    <strong>
                      {{ displayCurrent(field) }}
                    </strong>
                  </div>

                  <span
                    class="solmod-change-preview__arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>

                  <div class="is-new">
                    <span>Solicitado</span>

                    <strong>
                      {{ displayNew(field) }}
                    </strong>
                  </div>
                </div>

                <p
                  v-else
                  class="solmod-nochange"
                >
                  Modifique el valor actual para solicitar un cambio.
                </p>
              </section>
            </article>
          </div>
        </section>

        <!-- ===================================================
             AUTORES
        ==================================================== -->
        <section
          v-if="allowed.includes('autores')"
          class="solmod-panel"
          :class="{
            'solmod-panel--selected':
              selected.includes('autores')
          }"
        >
          <header class="solmod-panel__head">
            <div>
              <span>Autoría</span>

              <h2>Autores y orden bibliográfico</h2>

              <p>
                Active esta opción únicamente si necesita modificar
                autores o su posición en la publicación.
              </p>
            </div>

            <label class="solmod-check">
              <input
                v-model="selected"
                type="checkbox"
                value="autores"
                @change="onAuthorsSelection"
              >

              <span>
                Solicitar cambio
              </span>
            </label>
          </header>

          <template v-if="selected.includes('autores')">
            <section class="solmod-authors-current">
              <span>Autores actuales</span>

              <ol>
                <li
                  v-for="(author, index) in currentAuthors"
                  :key="authorKey(author, index)"
                >
                  {{
                    authorName(
                      author,
                      index
                    )
                  }}
                </li>
              </ol>
            </section>

            <div class="solmod-authors">
              <AutoresSelector
                v-model="authors"
              />
            </div>

            <p
              v-if="!authorsChanged"
              class="solmod-nochange"
            >
              Modifique los autores o su orden para solicitar
              un cambio.
            </p>
          </template>
        </section>

        <!-- ===================================================
             RESUMEN
        ==================================================== -->
        <section
          v-if="selected.length"
          class="solmod-panel solmod-summary"
        >
          <header class="solmod-panel__head">
            <div>
              <span>Revisión previa</span>

              <h2>Resumen de la solicitud</h2>

              <p>
                Revise los cambios antes de enviarlos para
                aprobación administrativa.
              </p>
            </div>
          </header>

          <div
            v-if="realChanges.length"
            class="solmod-summary__changes"
          >
            <article
              v-for="change in realChanges"
              :key="change.field"
            >
              <header>
                <strong>
                  {{ label(change.field) }}
                </strong>
              </header>

              <div class="solmod-summary__comparison">
                <div>
                  <span>Actual</span>

                  <strong>
                    {{ change.before }}
                  </strong>
                </div>

                <span
                  class="solmod-summary__arrow"
                  aria-hidden="true"
                >
                  →
                </span>

                <div class="is-new">
                  <span>Solicitado</span>

                  <strong>
                    {{ change.after }}
                  </strong>
                </div>
              </div>
            </article>
          </div>

          <p
            v-else
            class="solmod-nochange solmod-nochange--summary"
          >
            Ha seleccionado campos, pero todavía no existe ninguna
            modificación real para enviar.
          </p>
        </section>

        <!-- ===================================================
             ERROR DE ENVÍO
        ==================================================== -->
        <p
          v-if="submitError"
          class="solmod-state solmod-state--error"
          role="alert"
        >
          {{ submitError }}
        </p>

        <!-- ===================================================
             ACCIONES
        ==================================================== -->
        <footer class="solmod-actions">
          <button
            type="button"
            class="solmod-button solmod-button--secondary"
            :disabled="saving"
            @click="goBack"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="solmod-button solmod-button--primary"
            :disabled="
              saving ||
              !selected.length ||
              !motivo.trim() ||
              !hasRealChanges
            "
          >
            {{
              saving
                ? "Enviando..."
                : "Enviar solicitud"
            }}
          </button>
        </footer>
      </form>
    </section>

    <!-- =======================================================
         CONFIRMACIÓN
    ======================================================== -->
    <SgpcConfirmDialog
      v-model="confirmOpen"
      eyebrow="Solicitud de modificación"
      title="Enviar solicitud"
      :message="confirmationMessage"
      confirm-label="Enviar"
      :busy="saving"
      @confirm="submit"
    />
  </main>
</template>

<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import AutoresSelector from "../componentes/AutoresSelector.vue";

import SgpcConfirmDialog from "../../inicio/ui/SgpcConfirmDialog.vue";

import {
  configuracionSolicitudModificacion,
  crearSolicitudModificacion,
} from "../../scripts/api/solicitudesModificacionApi";


/* ============================================================
   ROUTER
============================================================ */

const route = useRoute();
const router = useRouter();


/* ============================================================
   ESTADO
============================================================ */

const loading = ref(true);
const saving = ref(false);

const error = ref("");
const submitError = ref("");

const motivo = ref("");

const allowed = ref([]);
const current = ref({});

const selected = ref([]);

const authors = ref([]);

const values = reactive({});

const confirmOpen = ref(false);


/* ============================================================
   CATÁLOGOS
============================================================ */

const months = [
  "Enero",
  "Febrero",
  "Marzo",
  "Abril",
  "Mayo",
  "Junio",
  "Julio",
  "Agosto",
  "Septiembre",
  "Octubre",
  "Noviembre",
  "Diciembre",
];


const labels = {
  anio_publicacion:
    "Año de publicación",

  mes_publicacion:
    "Mes de publicación",

  origen_tipo:
    "Origen",

  origen_grado:
    "Grado o programa",

  nombre_evento:
    "Nombre del evento",

  nombre_ponencia:
    "Nombre de la ponencia",

  codigo_issn_isbn:
    "ISSN / ISBN",

  tipo_presentacion:
    "Tipo de presentación",

  tipo_presentacion_otro:
    "Otro tipo de presentación",

  link_evento:
    "Enlace del evento",

  revisor_par_arbitraje:
    "Revisión por pares",

  nombre_articulo:
    "Nombre del artículo",

  base_datos_indexada:
    "Base de datos indexada",

  base_datos_otra:
    "Otra base de datos",

  codigo_doi:
    "DOI",

  codigo_issn:
    "ISSN",

  nombre_revista:
    "Revista",

  numero_revista:
    "Número de revista",

  link_publicacion:
    "Enlace de publicación",

  link_revista:
    "Enlace de revista",

  factor_impacto:
    "Factor de impacto",

  cuartil:
    "Cuartil",

  sjr:
    "SJR",

  jcr:
    "JCR",

  nombre_libro:
    "Nombre del libro",

  codigo_isbn:
    "ISBN",

  editorial_compilador:
    "Editorial / compilador",

  link_libro:
    "Enlace del libro",

  nombre_capitulo:
    "Nombre del capítulo",

  editor_compilador:
    "Editor / compilador",

  link_capitulo:
    "Enlace del capítulo",

  autores:
    "Autores y orden bibliográfico",
};


/* ============================================================
   COMPUTADOS
============================================================ */

const normalFields = computed(() => (
  allowed.value.filter(
    (field) =>
      field !== "autores"
  )
));


const currentAuthors = computed(() => (
  Array.isArray(current.value?.autores)
    ? current.value.autores
    : []
));


const authorsChanged = computed(() => (
  !authorsEqual(
    currentAuthors.value,
    authors.value
  )
));


const realChanges = computed(() => {
  const changes = [];

  for (const field of selected.value) {
    if (field === "autores") {
      if (authorsChanged.value) {
        changes.push({
          field,
          before:
            authorsDisplay(
              currentAuthors.value
            ),

          after:
            authorsDisplay(
              authors.value
            ),
        });
      }

      continue;
    }

    if (!fieldHasChanged(field)) {
      continue;
    }

    changes.push({
      field,

      before:
        displayCurrent(field),

      after:
        displayNew(field),
    });
  }

  return changes;
});


const hasRealChanges = computed(() => (
  realChanges.value.length > 0
));


const confirmationMessage = computed(() => {
  const total =
    realChanges.value.length;

  if (!total) {
    return (
      "No hay cambios reales para enviar."
    );
  }

  return (
    `Se enviará una solicitud con ${total} ${
      total === 1
        ? "cambio"
        : "cambios"
    }. La publicación no será modificada hasta que un administrador apruebe la solicitud.`
  );
});


/* ============================================================
   ETIQUETAS
============================================================ */

function label(field) {
  return (
    labels[field] ||
    humanize(field)
  );
}


function humanize(value) {
  if (!value) {
    return "";
  }

  const text =
    String(value)
      .replace(/_/g, " ")
      .trim();

  return (
    text.charAt(0).toUpperCase() +
    text.slice(1)
  );
}


function isUrl(field) {
  return (
    String(field)
      .startsWith("link_")
  );
}


/* ============================================================
   VALORES
============================================================ */

function displayCurrent(field) {
  return displayValue(
    field,
    current.value?.[field]
  );
}


function displayNew(field) {
  return displayValue(
    field,
    normalizeValue(field)
  );
}


function displayValue(
  field,
  value
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Sin información";
  }

  if (
    field === "mes_publicacion"
  ) {
    return (
      months[
        Number(value) - 1
      ] ||
      String(value)
    );
  }

  if (
    field === "revisor_par_arbitraje"
  ) {
    const normalized =
      normalizeText(value);

    if (
      normalized === "si" ||
      normalized === "true"
    ) {
      return "Sí";
    }

    if (
      normalized === "no" ||
      normalized === "false"
    ) {
      return "No";
    }
  }

  if (
    field === "origen_tipo"
  ) {
    const origins = {
      ninguno: "Ninguno",

      tic:
        "Trabajo de integración curricular",

      maestria:
        "Tesis de maestría",

      doctoral:
        "Tesis doctoral",

      otro:
        "Otro",
    };

    return (
      origins[value] ||
      String(value)
    );
  }

  if (Array.isArray(value)) {
    return value
      .map(
        (item, index) =>
          objectLabel(
            item,
            index
          )
      )
      .join(", ");
  }

  if (
    typeof value === "object"
  ) {
    return objectLabel(value);
  }

  return String(value);
}


function objectLabel(
  value,
  index = 0
) {
  return (
    value?.nombre ||
    value?.nombre_completo ||
    value?.titulo ||
    value?.label ||
    value?.email ||
    value?.autor_nombre ||
    `Registro ${index + 1}`
  );
}


/* ============================================================
   NORMALIZACIÓN
============================================================ */

function normalizeValue(field) {
  if (field === "autores") {
    return authors.value.map(
      (item, index) => ({
        autor_id:
          Number(
            item.autor_id ??
            item.id
          ),

        orden:
          index + 1,
      })
    );
  }

  const value =
    values[field];

  if (
    field === "anio_publicacion" ||
    field === "mes_publicacion" ||
    field === "numero_revista"
  ) {
    return (
      value === "" ||
      value === null ||
      value === undefined
        ? null
        : Number(value)
    );
  }

  return value;
}


function normalizeComparable(
  field,
  value
) {
  if (
    value === undefined ||
    value === null
  ) {
    return null;
  }

  if (
    field === "anio_publicacion" ||
    field === "mes_publicacion" ||
    field === "numero_revista"
  ) {
    if (value === "") {
      return null;
    }

    return Number(value);
  }

  if (
    typeof value === "string"
  ) {
    return value.trim();
  }

  return value;
}


function normalizeText(value) {
  return String(value)
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    );
}


/* ============================================================
   COMPARACIÓN
============================================================ */

function fieldHasChanged(field) {
  if (field === "autores") {
    return authorsChanged.value;
  }

  const before =
    normalizeComparable(
      field,
      current.value?.[field]
    );

  const after =
    normalizeComparable(
      field,
      normalizeValue(field)
    );

  return (
    JSON.stringify(before) !==
    JSON.stringify(after)
  );
}


function authorsEqual(
  currentList,
  newList
) {
  const currentNormalized =
    normalizeAuthors(
      currentList
    );

  const newNormalized =
    normalizeAuthors(
      newList
    );

  return (
    JSON.stringify(
      currentNormalized
    ) ===
    JSON.stringify(
      newNormalized
    )
  );
}


function normalizeAuthors(list) {
  if (!Array.isArray(list)) {
    return [];
  }

  return list.map(
    (item, index) => ({
      id:
        Number(
          item.autor_id ??
          item.id ??
          item.autor?.id
        ),

      orden:
        Number(
          item.orden ??
          index + 1
        ),
    })
  );
}


/* ============================================================
   AUTORES
============================================================ */

function authorName(
  author,
  index
) {
  return (
    author?.nombre ||
    author?.nombre_completo ||
    author?.autor_nombre ||
    author?.autor?.nombre ||
    author?.autor?.nombre_completo ||
    author?.email ||
    `Autor ${index + 1}`
  );
}


function authorKey(
  author,
  index
) {
  return (
    author?.autor_id ||
    author?.id ||
    author?.autor?.id ||
    index
  );
}


function authorsDisplay(list) {
  if (
    !Array.isArray(list) ||
    !list.length
  ) {
    return "Sin autores";
  }

  return list
    .map(
      (author, index) =>
        `${index + 1}. ${authorName(
          author,
          index
        )}`
    )
    .join(" · ");
}


/* ============================================================
   SELECCIÓN
============================================================ */

function onFieldSelection(field) {
  if (
    selected.value.includes(field)
  ) {
    values[field] =
      current.value?.[field] ??
      "";

    return;
  }

  values[field] =
    current.value?.[field] ??
    "";
}


function onAuthorsSelection() {
  if (
    selected.value.includes(
      "autores"
    )
  ) {
    authors.value =
      cloneAuthors(
        currentAuthors.value
      );
  }
}


function cloneAuthors(list) {
  if (!Array.isArray(list)) {
    return [];
  }

  return list.map(
    (item) => ({
      ...item,

      ...(
        item.autor
          ? {
              autor: {
                ...item.autor,
              },
            }
          : {}
      ),
    })
  );
}


/* ============================================================
   CARGA
============================================================ */

async function load() {
  loading.value = true;

  error.value = "";

  try {
    const payload =
      await configuracionSolicitudModificacion(
        route.params.id
      );

    allowed.value =
      Array.isArray(
        payload?.campos_permitidos
      )
        ? payload.campos_permitidos
        : [];

    current.value =
      payload?.valores_actuales ||
      {};

    selected.value = [];

    for (
      const field of
      allowed.value
    ) {
      if (field === "autores") {
        continue;
      }

      values[field] =
        current.value[field] ??
        "";
    }

    authors.value =
      cloneAuthors(
        currentAuthors.value
      );
  } catch (err) {
    error.value =
      err?.response?.data?.detail ||
      "No fue posible preparar la solicitud de modificación.";
  } finally {
    loading.value = false;
  }
}


/* ============================================================
   VALIDACIÓN
============================================================ */

function validate() {
  if (!motivo.value.trim()) {
    throw new Error(
      "Explique el motivo de la modificación."
    );
  }

  if (!selected.value.length) {
    throw new Error(
      "Seleccione al menos un campo para modificar."
    );
  }

  for (const field of selected.value) {
    if (field === "autores") {
      if (!authors.value.length) {
        throw new Error(
          "La publicación debe conservar al menos un autor."
        );
      }

      continue;
    }

    const value =
      normalizeValue(field);

    if (
      value === "" ||
      value === null ||
      value === undefined
    ) {
      throw new Error(
        `Complete el nuevo valor de ${label(field)}.`
      );
    }
  }

  if (!hasRealChanges.value) {
    throw new Error(
      "Los valores seleccionados son iguales a la información actual. Realice al menos una modificación."
    );
  }
}


/* ============================================================
   PREPARAR ENVÍO
============================================================ */

function prepareSubmit() {
  submitError.value = "";

  try {
    validate();

    confirmOpen.value = true;
  } catch (err) {
    submitError.value =
      err.message;
  }
}


/* ============================================================
   ENVIAR
============================================================ */

async function submit() {
  if (saving.value) {
    return;
  }

  submitError.value = "";

  saving.value = true;

  try {
    validate();

    const cambios = {};

    for (
      const field of
      selected.value
    ) {
      if (!fieldHasChanged(field)) {
        continue;
      }

      cambios[field] =
        normalizeValue(field);
    }

    await crearSolicitudModificacion({
      publicacion:
        Number(route.params.id),

      motivo:
        motivo.value.trim(),

      cambios_solicitados:
        cambios,
    });

    confirmOpen.value =
      false;

    await router.push({
      name:
        "PublicacionDetalle",

      params: {
        id:
          route.params.id,
      },

      query: {
        solicitud:
          "enviada",
      },
    });
  } catch (err) {
    const data =
      err?.response?.data;

    submitError.value =
      (
        data?.detail ||
        data?.non_field_errors?.[0] ||
        firstApiError(data) ||
        (
          err instanceof Error &&
          !err.response
            ? err.message
            : "No fue posible enviar la solicitud."
        )
      );
  } finally {
    saving.value = false;
  }
}


/* ============================================================
   ERROR API
============================================================ */

function firstApiError(data) {
  if (
    !data ||
    typeof data !== "object"
  ) {
    return "";
  }

  for (
    const value of
    Object.values(data)
  ) {
    if (
      Array.isArray(value) &&
      value.length
    ) {
      return String(
        value[0]
      );
    }

    if (
      typeof value === "string"
    ) {
      return value;
    }
  }

  return "";
}


/* ============================================================
   VOLVER
============================================================ */

function goBack() {
  router.push({
    name:
      "PublicacionDetalle",

    params: {
      id:
        route.params.id,
    },
  });
}


/* ============================================================
   INICIO
============================================================ */

onMounted(
  load
);
</script>

<style src="./solicitud-modificacion-publicacion.css"></style>