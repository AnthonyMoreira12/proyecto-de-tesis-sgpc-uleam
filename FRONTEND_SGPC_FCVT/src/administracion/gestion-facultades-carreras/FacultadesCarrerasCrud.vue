<template>
  <div
    class="crud-catalog"
    :class="{ 'crud-catalog--embedded': embedded }"
    :aria-busy="loading ? 'true' : 'false'"
  >
    <!-- =====================================================
         BARRA PRINCIPAL
    ====================================================== -->
    <section
      class="crud-catalog__toolbar adm-surface"
      role="region"
      :aria-labelledby="catalogTitleId"
    >
      <div class="crud-catalog__toolbar-main">
        <div class="crud-catalog__toolbar-copy">
          <span class="adm-kicker">Catálogo académico</span>

          <h2
            :id="catalogTitleId"
            class="crud-catalog__title"
          >
            {{ title }}
          </h2>

          <p class="crud-catalog__subtitle">
            {{ description || defaultDescription }}
          </p>
        </div>

        <div class="crud-catalog__toolbar-actions">
          <button
            class="crud-catalog__btn crud-catalog__btn--secondary"
            type="button"
            :disabled="loading"
            @click="load"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M17.7 6.3A8 8 0 1 0 20 12h-2a6 6 0 1 1-1.8-4.3L13 11h8V3l-3.3 3.3Z"
              />
            </svg>

            {{ loading ? "Actualizando..." : "Actualizar" }}
          </button>

          <button
            class="crud-catalog__btn crud-catalog__btn--primary"
            type="button"
            :aria-expanded="showCreatePanel ? 'true' : 'false'"
            :aria-controls="createPanelId"
            :disabled="loading"
            @click="toggleCreatePanel"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6V5Z"
              />
            </svg>

            {{
              showCreatePanel
                ? "Cerrar formulario"
                : "Nuevo registro"
            }}
          </button>
        </div>
      </div>

      <div class="crud-catalog__toolbar-row">
        <div
          class="crud-catalog__search"
          role="search"
        >
          <label
            class="crud-catalog__sr-only"
            :for="searchInputId"
          >
            Buscar en {{ title }}
          </label>

          <span
            class="crud-catalog__search-icon"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="m20.7 19.3-4.2-4.2a7.5 7.5 0 1 0-1.4 1.4l4.2 4.2a1 1 0 0 0 1.4-1.4ZM5 10.5a5.5 5.5 0 1 1 11 0 5.5 5.5 0 0 1-11 0Z"
              />
            </svg>
          </span>

          <input
            :id="searchInputId"
            v-model="search"
            class="crud-catalog__search-input"
            type="search"
            :placeholder="searchPlaceholder"
            :disabled="loading"
            autocomplete="off"
          />

          <button
            v-if="searchTrim"
            class="crud-catalog__search-clear"
            type="button"
            :disabled="loading"
            aria-label="Limpiar búsqueda"
            title="Limpiar búsqueda"
            @click="clearSearch"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div
          class="crud-catalog__toolbar-meta"
          aria-live="polite"
          aria-atomic="true"
        >
          <span class="crud-catalog__toolbar-count">
            <strong>{{ filteredRows }}</strong>
            de
            <strong>{{ totalRows }}</strong>
            visibles
          </span>

          <span class="crud-catalog__toolbar-status">
            {{ visibleStatusText }}
          </span>
        </div>
      </div>
    </section>

    <!-- =====================================================
         ERROR DE CARGA
    ====================================================== -->
    <div
      v-if="loadError"
      class="crud-catalog__alert crud-catalog__alert--error"
      role="alert"
      aria-live="assertive"
    >
      <span
        class="crud-catalog__alert-icon"
        aria-hidden="true"
      >
        !
      </span>

      <div>
        <strong>No se pudo cargar el catálogo</strong>
        <p>{{ loadError }}</p>
      </div>
    </div>

    <!-- =====================================================
         CONTENIDO
    ====================================================== -->
    <section
      class="crud-catalog__layout"
      :class="{
        'crud-catalog__layout--table-only': !showCreatePanel,
      }"
    >
      <!-- ===================================================
           FORMULARIO DE CREACIÓN
      ==================================================== -->
      <Transition name="catalog-panel">
        <aside
          v-if="showCreatePanel"
          :id="createPanelId"
          class="crud-catalog__aside"
          aria-labelledby="createFormTitleId"
        >
          <section class="crud-catalog__card crud-catalog__card--form adm-surface">
            <div class="crud-catalog__form-head">
              <div>
                <span class="crud-catalog__section-kicker">
                  Nuevo elemento
                </span>

                <h3
                  :id="createFormTitleId"
                  class="crud-catalog__form-title"
                >
                  Registrar en {{ title }}
                </h3>

                <p class="crud-catalog__form-subtitle">
                  Complete los campos obligatorios para agregar el
                  registro al catálogo.
                </p>
              </div>
            </div>

            <form
              class="crud-catalog__form"
              @submit.prevent="create"
            >
              <div
                v-for="field in fields"
                :key="field.key"
                class="crud-catalog__field"
              >
                <div class="crud-catalog__label-row">
                  <label
                    class="crud-catalog__label"
                    :for="fieldControlId('create', field)"
                  >
                    {{ field.label }}

                    <span
                      v-if="field.required"
                      class="crud-catalog__required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </label>

                  <InfoTip
                    v-if="field.help"
                    :title="field.helpTitle || 'Información'"
                  >
                    {{ field.help }}
                  </InfoTip>
                </div>

                <input
                  v-if="field.type !== 'select'"
                  :id="fieldControlId('create', field)"
                  :ref="
                    field.key === firstFieldKey
                      ? setCreateFirstEl
                      : undefined
                  "
                  v-model="createForm[field.key]"
                  class="crud-catalog__control"
                  :name="field.key"
                  :type="field.inputType || 'text'"
                  :placeholder="field.placeholder || ''"
                  :maxlength="field.maxLength || undefined"
                  :required="Boolean(field.required)"
                  :disabled="loading"
                  :autocomplete="field.autocomplete || 'off'"
                  :aria-describedby="
                    field.help
                      ? fieldHelpId('create', field)
                      : undefined
                  "
                />

                <select
                  v-else
                  :id="fieldControlId('create', field)"
                  :ref="
                    field.key === firstFieldKey
                      ? setCreateFirstEl
                      : undefined
                  "
                  v-model="createForm[field.key]"
                  class="crud-catalog__control"
                  :name="field.key"
                  :required="Boolean(field.required)"
                  :disabled="
                    loading ||
                    !(field.options || []).length
                  "
                  :aria-describedby="
                    field.help
                      ? fieldHelpId('create', field)
                      : undefined
                  "
                >
                  <option value="">
                    {{
                      field.placeholder ||
                      "Seleccione una opción"
                    }}
                  </option>

                  <option
                    v-for="option in field.options || []"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>

                <p
                  v-if="field.help"
                  :id="fieldHelpId('create', field)"
                  class="crud-catalog__field-help"
                >
                  {{ field.help }}
                </p>
              </div>

              <div
                v-if="createError"
                class="crud-catalog__form-error"
                role="alert"
                aria-live="assertive"
              >
                {{ createError }}
              </div>

              <div class="crud-catalog__form-actions">
                <button
                  class="crud-catalog__btn crud-catalog__btn--secondary"
                  type="button"
                  :disabled="loading"
                  @click="closeCreatePanel"
                >
                  Cancelar
                </button>

                <button
                  class="crud-catalog__btn crud-catalog__btn--primary"
                  type="submit"
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="crud-catalog__spinner"
                    aria-hidden="true"
                  ></span>

                  {{
                    loading
                      ? "Guardando..."
                      : "Crear registro"
                  }}
                </button>
              </div>
            </form>
          </section>
        </aside>
      </Transition>

      <!-- ===================================================
           TABLA
      ==================================================== -->
      <section class="crud-catalog__card crud-catalog__card--table adm-surface">
        <div class="crud-catalog__table-head">
          <div>
            <span class="crud-catalog__section-kicker">
              Información registrada
            </span>

            <h3 class="crud-catalog__table-title">
              Registros
            </h3>

            <p class="crud-catalog__table-subtitle">
              Consulte, edite o elimine los elementos existentes.
            </p>
          </div>

          <span
            class="crud-catalog__badge"
            aria-live="polite"
          >
            {{ visibleRecordsLabel }}
          </span>
        </div>

        <div
          v-if="loading"
          class="crud-catalog__loading"
          role="status"
          aria-live="polite"
        >
          <span
            class="crud-catalog__spinner crud-catalog__spinner--primary"
            aria-hidden="true"
          ></span>

          Actualizando registros...
        </div>

        <!-- Carga inicial -->
        <div
          v-if="loading && !rows.length"
          class="crud-catalog__skeleton-list"
          aria-hidden="true"
        >
          <div
            v-for="index in 4"
            :key="index"
            class="crud-catalog__skeleton-row"
          >
            <span class="crud-catalog__skeleton crud-catalog__skeleton--main"></span>
            <span class="crud-catalog__skeleton crud-catalog__skeleton--secondary"></span>
            <span class="crud-catalog__skeleton crud-catalog__skeleton--action"></span>
          </div>
        </div>

        <!-- Estado vacío -->
        <div
          v-else-if="!rowsFiltrados.length"
          class="crud-catalog__empty-state"
        >
          <div
            class="crud-catalog__empty-icon"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M4 4h16v16H4V4Zm2 2v12h12V6H6Zm2 3h8v2H8V9Zm0 4h5v2H8v-2Z"
              />
            </svg>
          </div>

          <h4 class="crud-catalog__empty-title">
            {{
              searchTrim
                ? "Sin coincidencias"
                : "Sin registros"
            }}
          </h4>

          <p class="crud-catalog__empty-text">
            {{
              searchTrim
                ? `No se encontraron resultados para “${searchTrim}”.`
                : "Todavía no existen elementos registrados en este catálogo."
            }}
          </p>

          <div class="crud-catalog__empty-actions">
            <button
              v-if="searchTrim"
              class="crud-catalog__btn crud-catalog__btn--secondary"
              type="button"
              @click="clearSearch"
            >
              Limpiar búsqueda
            </button>

            <button
              v-if="!showCreatePanel"
              class="crud-catalog__btn crud-catalog__btn--primary"
              type="button"
              @click="openCreatePanel"
            >
              Nuevo registro
            </button>
          </div>
        </div>

        <!-- Tabla de resultados -->
        <div
          v-else
          class="crud-catalog__table-wrap"
        >
          <table class="crud-catalog__table">
            <caption class="crud-catalog__sr-only">
              Registros del catálogo {{ title }}
            </caption>

            <thead>
              <tr>
                <th
                  v-for="column in columns"
                  :key="column.key"
                  scope="col"
                >
                  {{ column.label }}
                </th>

                <th
                  class="crud-catalog__th-actions"
                  scope="col"
                >
                  Acciones
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="row in rowsFiltrados"
                :key="row.id"
              >
                <td
                  v-for="column in columns"
                  :key="column.key"
                >
                  <span class="crud-catalog__cell-value">
                    {{ rowValue(row, column) }}
                  </span>
                </td>

                <td class="crud-catalog__td-actions">
                  <div class="crud-catalog__actions">
                    <button
                      class="crud-catalog__btn crud-catalog__btn--secondary crud-catalog__btn--sm"
                      type="button"
                      :disabled="loading"
                      :aria-label="`Editar ${resolveRowLabel(row)}`"
                      @click="openEdit(row)"
                    >
                      Editar
                    </button>

                    <button
                      class="crud-catalog__btn crud-catalog__btn--danger crud-catalog__btn--sm"
                      type="button"
                      :disabled="loading"
                      :aria-label="`Eliminar ${resolveRowLabel(row)}`"
                      @click="remove(row)"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>

    <!-- =====================================================
         MODAL DE EDICIÓN
    ====================================================== -->
    <Transition name="catalog-modal">
      <div
        v-if="modal.open"
        class="crud-catalog__modal-shell"
        @click.self="closeModal"
      >
        <div
          ref="modalPanelRef"
          class="crud-catalog__modal-panel"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="modalTitleId"
          :aria-describedby="modalDescriptionId"
          :aria-busy="loading ? 'true' : 'false'"
          tabindex="-1"
          @keydown="handleModalKeydown"
        >
          <form
            class="crud-catalog__modal-form"
            @submit.prevent="saveEdit"
          >
            <header class="crud-catalog__modal-header">
              <div class="crud-catalog__modal-heading">
                <span class="adm-kicker">Edición</span>

                <h2
                  :id="modalTitleId"
                  class="crud-catalog__modal-title"
                >
                  {{ modal.title }}
                </h2>

                <p
                  :id="modalDescriptionId"
                  class="crud-catalog__modal-subtitle"
                >
                  Actualice la información del registro seleccionado.
                </p>
              </div>

              <button
                class="crud-catalog__modal-close"
                type="button"
                :disabled="loading"
                aria-label="Cerrar ventana de edición"
                title="Cerrar"
                @click="closeModal"
              >
                <span aria-hidden="true">×</span>
              </button>
            </header>

            <div class="crud-catalog__modal-scroll">
              <section
                class="crud-catalog__modal-section"
                aria-label="Campos editables"
              >
                <div class="crud-catalog__modal-grid">
                  <div
                    v-for="field in fields"
                    :key="field.key"
                    class="crud-catalog__modal-field"
                  >
                    <div class="crud-catalog__label-row">
                      <label
                        class="crud-catalog__modal-label"
                        :for="fieldControlId('edit', field)"
                      >
                        {{ field.label }}

                        <span
                          v-if="field.required"
                          class="crud-catalog__required"
                          aria-hidden="true"
                        >
                          *
                        </span>
                      </label>

                      <InfoTip
                        v-if="field.help"
                        :title="field.helpTitle || 'Información'"
                      >
                        {{ field.help }}
                      </InfoTip>
                    </div>

                    <input
                      v-if="field.type !== 'select'"
                      :id="fieldControlId('edit', field)"
                      :ref="
                        field.key === firstFieldKey
                          ? setEditFirstEl
                          : undefined
                      "
                      v-model="editForm[field.key]"
                      class="crud-catalog__modal-input"
                      :name="`edit_${field.key}`"
                      :type="field.inputType || 'text'"
                      :placeholder="field.placeholder || ''"
                      :maxlength="field.maxLength || undefined"
                      :required="Boolean(field.required)"
                      :disabled="loading"
                      :autocomplete="field.autocomplete || 'off'"
                      :aria-describedby="
                        field.help
                          ? fieldHelpId('edit', field)
                          : undefined
                      "
                    />

                    <select
                      v-else
                      :id="fieldControlId('edit', field)"
                      :ref="
                        field.key === firstFieldKey
                          ? setEditFirstEl
                          : undefined
                      "
                      v-model="editForm[field.key]"
                      class="crud-catalog__modal-input"
                      :name="`edit_${field.key}`"
                      :required="Boolean(field.required)"
                      :disabled="
                        loading ||
                        !(field.options || []).length
                      "
                      :aria-describedby="
                        field.help
                          ? fieldHelpId('edit', field)
                          : undefined
                      "
                    >
                      <option value="">
                        {{
                          field.placeholder ||
                          "Seleccione una opción"
                        }}
                      </option>

                      <option
                        v-for="option in field.options || []"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>

                    <p
                      v-if="field.help"
                      :id="fieldHelpId('edit', field)"
                      class="crud-catalog__field-help"
                    >
                      {{ field.help }}
                    </p>
                  </div>
                </div>

                <div
                  v-if="editError"
                  class="crud-catalog__form-error"
                  role="alert"
                  aria-live="assertive"
                >
                  {{ editError }}
                </div>
              </section>
            </div>

            <footer class="crud-catalog__modal-footer">
              <button
                class="crud-catalog__btn crud-catalog__btn--secondary"
                type="button"
                :disabled="loading"
                @click="closeModal"
              >
                Cancelar
              </button>

              <button
                class="crud-catalog__btn crud-catalog__btn--primary"
                type="submit"
                :disabled="loading || !editForm.id"
              >
                <span
                  v-if="loading"
                  class="crud-catalog__spinner"
                  aria-hidden="true"
                ></span>

                {{
                  loading
                    ? "Guardando..."
                    : "Guardar cambios"
                }}
              </button>
            </footer>
          </form>
        </div>
      </div>
    </Transition>

    <NoticeDialog
      :model-value="notice"
      @close="closeNotice"
    />
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import { useNotice } from "../../scripts/composables/useNotice";

import InfoTip from "../../inicio/ui/InfoTip.vue";
import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: "",
  },
  fetchRows: {
    type: Function,
    required: true,
  },
  createRow: {
    type: Function,
    required: true,
  },
  updateRow: {
    type: Function,
    required: true,
  },
  deleteRow: {
    type: Function,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  fields: {
    type: Array,
    required: true,
  },
  embedded: {
    type: Boolean,
    default: false,
  },
});

const {
  notice,
  openNotice,
  closeNotice,
} = useNotice();

const rows = ref([]);
const loading = ref(false);
const loadError = ref("");
const createError = ref("");
const editError = ref("");

const showCreatePanel = ref(false);
const search = ref("");

const createFirstEl = ref(null);
const editFirstEl = ref(null);
const modalPanelRef = ref(null);

const createForm = reactive({});
const editForm = reactive({
  id: null,
});

const modal = reactive({
  open: false,
  title: "Editar registro",
});

let modalTriggerElement = null;
let previousBodyOverflow = "";

const normalize = (value) =>
  String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();

const catalogSlug = computed(() => {
  const value = normalize(props.title)
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return value || "catalogo";
});

const catalogTitleId = computed(
  () => `crud-${catalogSlug.value}-title`
);

const searchInputId = computed(
  () => `crud-${catalogSlug.value}-search`
);

const createPanelId = computed(
  () => `crud-${catalogSlug.value}-create-panel`
);

const createFormTitleId = computed(
  () => `crud-${catalogSlug.value}-create-title`
);

const modalTitleId = computed(
  () => `crud-${catalogSlug.value}-modal-title`
);

const modalDescriptionId = computed(
  () => `crud-${catalogSlug.value}-modal-description`
);

const defaultDescription = computed(
  () =>
    "Cree, edite y elimine registros del catálogo."
);

const searchTrim = computed(() =>
  String(search.value || "").trim()
);

const totalRows = computed(
  () => rows.value.length
);

const searchPlaceholder = computed(
  () =>
    `Buscar ${String(props.title || "").toLowerCase()}...`
);

const firstFieldKey = computed(
  () => props.fields?.[0]?.key || null
);

const rowValue = (row, column) => {
  if (typeof column?.map === "function") {
    return column.map(row);
  }

  const value = row?.[column?.key];

  return value === null ||
    value === undefined ||
    value === ""
    ? "—"
    : value;
};

const rowsFiltrados = computed(() => {
  const query = normalize(searchTrim.value);

  if (!query) {
    return rows.value;
  }

  return rows.value.filter((row) =>
    (props.columns || []).some((column) =>
      normalize(
        rowValue(row, column)
      ).includes(query)
    )
  );
});

const filteredRows = computed(
  () => rowsFiltrados.value.length
);

const visibleRecordsLabel = computed(() => {
  const total = filteredRows.value;

  return total === 1
    ? "1 registro visible"
    : `${total} registros visibles`;
});

const visibleStatusText = computed(() => {
  if (loading.value) {
    return "Actualizando catálogo";
  }

  if (!totalRows.value) {
    return "Sin registros";
  }

  if (searchTrim.value) {
    return "Búsqueda aplicada";
  }

  return "Vista completa";
});

const fieldControlId = (scope, field) =>
  `crud-${catalogSlug.value}-${scope}-${field.key}`;

const fieldHelpId = (scope, field) =>
  `crud-${catalogSlug.value}-${scope}-${field.key}-help`;

const setCreateFirstEl = (element) => {
  createFirstEl.value = element || null;
};

const setEditFirstEl = (element) => {
  editFirstEl.value = element || null;
};

const focusCreateFirst = async () => {
  await nextTick();

  createFirstEl.value?.focus?.();
};

const focusEditFirst = async () => {
  await nextTick();

  if (editFirstEl.value?.focus) {
    editFirstEl.value.focus();
    return;
  }

  modalPanelRef.value?.focus();
};

const initForms = () => {
  const validKeys = new Set(
    (props.fields || []).map(
      (field) => field.key
    )
  );

  Object.keys(createForm).forEach((key) => {
    if (!validKeys.has(key)) {
      delete createForm[key];
    }
  });

  Object.keys(editForm).forEach((key) => {
    if (
      key !== "id" &&
      !validKeys.has(key)
    ) {
      delete editForm[key];
    }
  });

  (props.fields || []).forEach((field) => {
    if (!(field.key in createForm)) {
      createForm[field.key] = "";
    }

    if (!(field.key in editForm)) {
      editForm[field.key] = "";
    }
  });
};

const resetCreateForm = () => {
  createError.value = "";

  (props.fields || []).forEach((field) => {
    createForm[field.key] = "";
  });
};

const resetEditForm = () => {
  editForm.id = null;
  editFirstEl.value = null;

  (props.fields || []).forEach((field) => {
    editForm[field.key] = "";
  });
};

const buildPayload = (source) => {
  const payload = {};

  (props.fields || []).forEach((field) => {
    const rawValue = source[field.key];

    payload[field.key] =
      typeof rawValue === "string" &&
      field.type !== "select"
        ? rawValue.trim()
        : rawValue;
  });

  return payload;
};

const validateRequiredFields = (formObject) => {
  const missing = [];

  (props.fields || []).forEach((field) => {
    if (!field.required) {
      return;
    }

    const value = String(
      formObject?.[field.key] ?? ""
    ).trim();

    if (!value) {
      missing.push(
        field.label || field.key
      );
    }
  });

  return missing;
};

const getErrorMessage = (
  error,
  fallback
) => {
  const data = error?.response?.data;

  if (typeof data === "string") {
    return data;
  }

  if (
    typeof data?.detail === "string" &&
    data.detail
  ) {
    return data.detail;
  }

  if (
    typeof data?.error === "string" &&
    data.error
  ) {
    return data.error;
  }

  if (
    data &&
    typeof data === "object"
  ) {
    const firstKey =
      Object.keys(data)[0];

    const firstValue =
      firstKey
        ? data[firstKey]
        : null;

    if (
      Array.isArray(firstValue) &&
      firstValue.length
    ) {
      return firstValue.join(" ");
    }

    if (
      typeof firstValue === "string" &&
      firstValue
    ) {
      return firstValue;
    }
  }

  return error?.message || fallback;
};

const resolveRowLabel = (row) => {
  const firstColumn =
    props.columns?.[0];

  const label = firstColumn
    ? rowValue(row, firstColumn)
    : "";

  return label &&
    label !== "—"
    ? String(label)
    : "este registro";
};

const clearSearch = () => {
  search.value = "";
};

const openCreatePanel = async () => {
  createError.value = "";
  showCreatePanel.value = true;

  await focusCreateFirst();
};

const closeCreatePanel = () => {
  showCreatePanel.value = false;
  resetCreateForm();
};

const toggleCreatePanel = async () => {
  if (showCreatePanel.value) {
    closeCreatePanel();
    return;
  }

  await openCreatePanel();
};

const deferNotice = (payload) => {
  window.setTimeout(() => {
    openNotice(payload);
  }, 0);
};

const load = async () => {
  loading.value = true;
  loadError.value = "";

  try {
    const data =
      await props.fetchRows();

    rows.value =
      Array.isArray(data)
        ? data
        : [];
  } catch (error) {
    console.error(
      "Error cargando catálogo:",
      error
    );

    loadError.value =
      getErrorMessage(
        error,
        "No se pudo cargar el catálogo. Intente nuevamente."
      );

    openNotice({
      title: "No se pudo cargar",
      message: loadError.value,
      details:
        error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const create = async () => {
  if (loading.value) {
    return;
  }

  createError.value = "";

  const missing =
    validateRequiredFields(
      createForm
    );

  if (missing.length) {
    createError.value =
      `Complete: ${missing.join(", ")}.`;

    return;
  }

  loading.value = true;

  try {
    await props.createRow(
      buildPayload(createForm)
    );

    const data =
      await props.fetchRows();

    rows.value =
      Array.isArray(data)
        ? data
        : [];

    closeCreatePanel();

    openNotice({
      title: "Registro creado",
      message:
        "El elemento se agregó correctamente al catálogo.",
    });
  } catch (error) {
    const message =
      getErrorMessage(
        error,
        "No se pudo crear el registro. Verifique la información."
      );

    createError.value = message;

    openNotice({
      title: "No se pudo crear",
      message,
      details:
        error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const lockBodyScroll = () => {
  previousBodyOverflow =
    document.body.style.overflow;

  document.body.style.overflow =
    "hidden";
};

const unlockBodyScroll = () => {
  document.body.style.overflow =
    previousBodyOverflow;
};

const restoreModalTriggerFocus =
  async () => {
    await nextTick();

    if (
      modalTriggerElement instanceof
      HTMLElement
    ) {
      modalTriggerElement.focus();
    }

    modalTriggerElement = null;
  };

const openEdit = async (row) => {
  if (
    loading.value ||
    !row?.id
  ) {
    return;
  }

  editError.value = "";

  modalTriggerElement =
    document.activeElement instanceof
    HTMLElement
      ? document.activeElement
      : null;

  editForm.id = row.id;

  (props.fields || []).forEach((field) => {
    editForm[field.key] =
      row[field.key] ?? "";
  });

  modal.title =
    `Editar ${resolveRowLabel(row)}`;

  modal.open = true;
  lockBodyScroll();

  await focusEditFirst();
};

const closeModal = async (
  force = false
) => {
  if (
    loading.value &&
    !force
  ) {
    return;
  }

  modal.open = false;
  editError.value = "";

  resetEditForm();
  unlockBodyScroll();

  await restoreModalTriggerFocus();
};

const saveEdit = async () => {
  if (
    loading.value ||
    !editForm.id
  ) {
    return;
  }

  editError.value = "";

  const missing =
    validateRequiredFields(
      editForm
    );

  if (missing.length) {
    editError.value =
      `Complete: ${missing.join(", ")}.`;

    return;
  }

  loading.value = true;

  try {
    await props.updateRow(
      editForm.id,
      buildPayload(editForm)
    );

    const data =
      await props.fetchRows();

    rows.value =
      Array.isArray(data)
        ? data
        : [];

    await closeModal(true);

    openNotice({
      title: "Registro actualizado",
      message:
        "Los cambios se guardaron correctamente.",
    });
  } catch (error) {
    const message =
      getErrorMessage(
        error,
        "No se pudo guardar el registro. Verifique la información."
      );

    editError.value = message;

    openNotice({
      title: "No se pudo guardar",
      message,
      details:
        error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const remove = (row) => {
  if (
    loading.value ||
    !row?.id
  ) {
    return;
  }

  const label =
    resolveRowLabel(row);

  openNotice({
    title: "Eliminar registro",
    message:
      `¿Desea eliminar ${label}? Esta acción no se puede deshacer.`,
    confirm: true,
    cancelText: "Cancelar",
    confirmText: "Sí, eliminar",

    onConfirm: async () => {
      loading.value = true;

      try {
        await props.deleteRow(row.id);

        const data =
          await props.fetchRows();

        rows.value =
          Array.isArray(data)
            ? data
            : [];

        deferNotice({
          title: "Registro eliminado",
          message:
            "El elemento se eliminó correctamente del catálogo.",
        });
      } catch (error) {
        const message =
          getErrorMessage(
            error,
            "No se pudo eliminar. Verifique si el registro está relacionado con otros datos."
          );

        deferNotice({
          title: "No se pudo eliminar",
          message,
          details:
            error?.response?.data || null,
        });
      } finally {
        loading.value = false;
      }
    },
  });
};

const getModalFocusableElements = () => {
  if (!modalPanelRef.value) {
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
    modalPanelRef.value.querySelectorAll(
      selector
    )
  ).filter(
    (element) =>
      !element.hasAttribute("hidden") &&
      element.getAttribute(
        "aria-hidden"
      ) !== "true" &&
      element.getClientRects().length > 0
  );
};

const handleModalKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeModal();
    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getModalFocusableElements();

  if (!focusableElements.length) {
    event.preventDefault();
    modalPanelRef.value?.focus();
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

watch(
  () => props.fields,
  () => {
    initForms();
  },
  {
    immediate: true,
    deep: true,
  }
);

onMounted(async () => {
  await load();
});

onBeforeUnmount(() => {
  if (modal.open) {
    unlockBodyScroll();
  }
});
</script>

<style scoped src="./facultades-carreras-crud.css"></style>