<template>
  <div class="crud-catalog" :class="{ 'crud-catalog--embedded': embedded }">
    <section
      class="crud-catalog__toolbar adm-surface"
      role="region"
      :aria-label="`Control de ${title}`"
    >
      <div class="crud-catalog__toolbar-main">
        <div class="crud-catalog__toolbar-copy">
          <span class="adm-kicker">Catálogo</span>

          <h2 class="crud-catalog__title">
            {{ title }}
          </h2>

          <p class="crud-catalog__subtitle">
            {{ description || defaultDescription }}
          </p>
        </div>

        <div class="crud-catalog__toolbar-actions">
          <button
            class="crud-catalog__btn crud-catalog__btn--ghost btn-soft"
            type="button"
            @click="load"
            :disabled="loading"
          >
            {{ loading ? "Actualizando..." : "Refrescar" }}
          </button>

          <button
            class="crud-catalog__btn crud-catalog__btn--primary btn-primary"
            type="button"
            @click="toggleCreatePanel"
            :disabled="loading"
          >
            {{ showCreatePanel ? "Ocultar formulario" : "Nuevo registro" }}
          </button>
        </div>
      </div>

      <div class="crud-catalog__toolbar-row">
        <div class="crud-catalog__search adm-search">
          <span class="crud-catalog__search-icon adm-search__icon" aria-hidden="true">
            ⌕
          </span>

          <input
            v-model="search"
            class="crud-catalog__search-input adm-search__input"
            :placeholder="searchPlaceholder"
            :disabled="loading"
            autocomplete="off"
            type="search"
          />

          <button
            v-if="searchTrim"
            class="crud-catalog__search-clear adm-search__clear"
            type="button"
            @click="clearSearch"
            :disabled="loading"
            aria-label="Limpiar búsqueda"
            title="Limpiar búsqueda"
          >
            ×
          </button>
        </div>

        <div class="crud-catalog__toolbar-meta" aria-live="polite">
          <span class="crud-catalog__toolbar-count">
            Mostrando <strong>{{ filteredRows }}</strong> de
            <strong>{{ totalRows }}</strong>
          </span>

          <span class="crud-catalog__toolbar-status">
            {{ visibleStatusText }}
          </span>
        </div>
      </div>
    </section>

    <div v-if="loadError" class="crud-catalog__alert adm-alert adm-alert--error">
      {{ loadError }}
    </div>

    <section
      class="crud-catalog__layout"
      :class="{ 'crud-catalog__layout--table-only': !showCreatePanel }"
    >
      <aside
        v-if="showCreatePanel"
        class="crud-catalog__aside"
        aria-label="Nuevo registro"
      >
        <section class="crud-catalog__card crud-catalog__card--form adm-surface">
          <div class="crud-catalog__form-head">
            <div>
              <h3 class="crud-catalog__form-title">Nuevo registro</h3>
              <p class="crud-catalog__form-subtitle">
                Complete los campos requeridos.
              </p>
            </div>
          </div>

          <form class="crud-catalog__form" @submit.prevent="create">
            <template v-for="field in fields" :key="field.key">
              <div class="crud-catalog__field">
                <label class="crud-catalog__label">
                  <span class="crud-catalog__label-text">
                    {{ field.label }}
                    <span
                      v-if="field.required"
                      class="crud-catalog__required"
                      aria-hidden="true"
                    >
                      *
                    </span>
                  </span>

                  <InfoTip v-if="field.help" :title="field.helpTitle || 'Información'">
                    {{ field.help }}
                  </InfoTip>
                </label>

                <input
                  v-if="field.type !== 'select'"
                  :ref="field.key === firstFieldKey ? setCreateFirstEl : undefined"
                  v-model="createForm[field.key]"
                  class="crud-catalog__control"
                  :placeholder="field.placeholder || ''"
                  :maxlength="field.maxLength || undefined"
                  :required="!!field.required"
                  :disabled="loading"
                  autocomplete="off"
                />

                <select
                  v-else
                  :ref="field.key === firstFieldKey ? setCreateFirstEl : undefined"
                  v-model="createForm[field.key]"
                  class="crud-catalog__control"
                  :required="!!field.required"
                  :disabled="loading || !(field.options || []).length"
                >
                  <option value="">
                    {{ field.placeholder || "Seleccione una opción" }}
                  </option>

                  <option
                    v-for="option in field.options || []"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </template>

            <div v-if="createError" class="crud-catalog__alert adm-alert adm-alert--error">
              {{ createError }}
            </div>

            <div class="crud-catalog__form-actions">
              <button
                class="crud-catalog__btn crud-catalog__btn--ghost btn-soft"
                type="button"
                @click="resetCreateForm"
                :disabled="loading"
              >
                Limpiar
              </button>

              <button
                class="crud-catalog__btn crud-catalog__btn--primary btn-primary"
                type="submit"
                :disabled="loading"
              >
                {{ loading ? "Guardando..." : "Crear registro" }}
              </button>
            </div>
          </form>
        </section>
      </aside>

      <section class="crud-catalog__card crud-catalog__card--table adm-surface">
        <div class="crud-catalog__table-head">
          <div>
            <h3 class="crud-catalog__table-title">Registros</h3>
            <p class="crud-catalog__table-subtitle">
              Edite o elimine los elementos del catálogo.
            </p>
          </div>

          <span class="crud-catalog__badge">
            {{ filteredRows }} visible(s)
          </span>
        </div>

        <div v-if="!loading && !rowsFiltrados.length" class="crud-catalog__empty-state">
          <h4 class="crud-catalog__empty-title">
            {{ searchTrim ? "Sin coincidencias" : "Sin registros" }}
          </h4>

          <p class="crud-catalog__empty-text">
            {{
              searchTrim
                ? "No existen registros que coincidan con la búsqueda actual."
                : "Todavía no existen registros creados para este catálogo."
            }}
          </p>

          <div class="crud-catalog__empty-actions">
            <button
              v-if="searchTrim"
              class="crud-catalog__btn crud-catalog__btn--ghost btn-soft"
              type="button"
              @click="clearSearch"
            >
              Limpiar búsqueda
            </button>

            <button
              v-if="!showCreatePanel"
              class="crud-catalog__btn crud-catalog__btn--primary btn-primary"
              type="button"
              @click="openCreatePanel"
            >
              Nuevo registro
            </button>
          </div>
        </div>

        <div v-else class="crud-catalog__table-wrap">
          <table class="crud-catalog__table">
            <thead>
              <tr>
                <th
                  v-for="column in columns"
                  :key="column.key"
                  scope="col"
                >
                  {{ column.label }}
                </th>

                <th class="crud-catalog__th-actions" scope="col">
                  Acciones
                </th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="row in rowsFiltrados" :key="row.id">
                <td v-for="column in columns" :key="column.key">
                  {{ rowValue(row, column) }}
                </td>

                <td class="crud-catalog__td-actions">
                  <div class="crud-catalog__actions">
                    <button
                      class="crud-catalog__btn crud-catalog__btn--secondary crud-catalog__btn--sm"
                      type="button"
                      @click="openEdit(row)"
                      :disabled="loading"
                    >
                      Editar
                    </button>

                    <button
                      class="crud-catalog__btn crud-catalog__btn--danger crud-catalog__btn--sm"
                      type="button"
                      @click="remove(row)"
                      :disabled="loading"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="loading && !rowsFiltrados.length">
                <td class="crud-catalog__empty-row" :colspan="columns.length + 1">
                  Cargando registros...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>

    <Transition name="modal-fade">
      <div
        v-if="modal.open"
        class="crud-catalog__modal-shell"
        role="presentation"
        @click.self="closeModal"
      >
        <div
          class="crud-catalog__modal-panel adm-surface"
          role="dialog"
          aria-modal="true"
          :aria-label="modal.title"
        >
          <form class="crud-catalog__modal-form" @submit.prevent="saveEdit">
            <header class="crud-catalog__modal-header">
              <div class="crud-catalog__modal-titleline">
                <div>
                  <span class="adm-kicker">Edición</span>

                  <h2 class="crud-catalog__modal-title">
                    {{ modal.title }}
                  </h2>

                  <p class="crud-catalog__modal-subtitle">
                    Actualice la información del registro seleccionado.
                  </p>
                </div>

                <button
                  class="crud-catalog__modal-close"
                  type="button"
                  aria-label="Cerrar edición"
                  @click="closeModal"
                >
                  ×
                </button>
              </div>
            </header>

            <div class="crud-catalog__modal-scroll">
              <section class="crud-catalog__modal-section">
                <div class="crud-catalog__modal-grid">
                  <template v-for="field in fields" :key="field.key">
                    <div class="crud-catalog__modal-field">
                      <label class="crud-catalog__modal-label">
                        <span>
                          {{ field.label }}
                          <span
                            v-if="field.required"
                            class="crud-catalog__required"
                            aria-hidden="true"
                          >
                            *
                          </span>
                        </span>

                        <InfoTip v-if="field.help" :title="field.helpTitle || 'Información'">
                          {{ field.help }}
                        </InfoTip>
                      </label>

                      <input
                        v-if="field.type !== 'select'"
                        :ref="field.key === firstFieldKey ? setEditFirstEl : undefined"
                        v-model="editForm[field.key]"
                        class="crud-catalog__modal-input"
                        :placeholder="field.placeholder || ''"
                        :maxlength="field.maxLength || undefined"
                        :required="!!field.required"
                        :disabled="loading"
                        autocomplete="off"
                      />

                      <select
                        v-else
                        :ref="field.key === firstFieldKey ? setEditFirstEl : undefined"
                        v-model="editForm[field.key]"
                        class="crud-catalog__modal-input"
                        :required="!!field.required"
                        :disabled="loading || !(field.options || []).length"
                      >
                        <option value="">
                          {{ field.placeholder || "Seleccione una opción" }}
                        </option>

                        <option
                          v-for="option in field.options || []"
                          :key="option.value"
                          :value="option.value"
                        >
                          {{ option.label }}
                        </option>
                      </select>
                    </div>
                  </template>
                </div>

                <div v-if="editError" class="crud-catalog__modal-alert">
                  {{ editError }}
                </div>
              </section>
            </div>

            <footer class="crud-catalog__modal-footer">
              <button
                class="crud-catalog__modal-btn crud-catalog__modal-btn--ghost"
                type="button"
                :disabled="loading"
                @click="closeModal"
              >
                Cancelar
              </button>

              <button
                class="crud-catalog__modal-btn crud-catalog__modal-btn--primary"
                type="submit"
                :disabled="loading || !editForm.id"
              >
                {{ loading ? "Guardando..." : "Guardar cambios" }}
              </button>
            </footer>
          </form>
        </div>
      </div>
    </Transition>

    <NoticeDialog :modelValue="notice" @close="closeNotice" />
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

import NoticeDialog from "../../inicio/ui/NoticeDialog.vue";
import InfoTip from "../../inicio/ui/InfoTip.vue";

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  fetchRows: { type: Function, required: true },
  createRow: { type: Function, required: true },
  updateRow: { type: Function, required: true },
  deleteRow: { type: Function, required: true },
  columns: { type: Array, required: true },
  fields: { type: Array, required: true },
  embedded: { type: Boolean, default: false },
});

const { notice, openNotice, closeNotice } = useNotice();

const rows = ref([]);
const loading = ref(false);
const loadError = ref("");
const createError = ref("");
const editError = ref("");

const showCreatePanel = ref(false);
const search = ref("");
const createFirstEl = ref(null);
const editFirstEl = ref(null);

const createForm = reactive({});
const editForm = reactive({ id: null });

const modal = reactive({
  open: false,
  title: "Editar registro",
});

const searchTrim = computed(() => String(search.value || "").trim());
const totalRows = computed(() => rows.value.length);
const filteredRows = computed(() => rowsFiltrados.value.length);

const defaultDescription = computed(() => {
  return "Cree, edite y elimine registros del catálogo.";
});

const searchPlaceholder = computed(() => {
  return `Buscar ${String(props.title || "").toLowerCase()}...`;
});

const visibleStatusText = computed(() => {
  if (loading.value) return "Actualizando catálogo";
  if (!totalRows.value) return "Sin registros";
  if (searchTrim.value) return "Filtro aplicado";
  return "Vista completa";
});

const firstFieldKey = computed(() => props.fields?.[0]?.key || null);

const setCreateFirstEl = (el) => {
  if (el) createFirstEl.value = el;
};

const setEditFirstEl = (el) => {
  if (el) editFirstEl.value = el;
};

const focusCreateFirst = async () => {
  await nextTick();
  createFirstEl.value?.focus?.();
};

const focusEditFirst = async () => {
  await nextTick();
  editFirstEl.value?.focus?.();
};

const openCreatePanel = async () => {
  createError.value = "";
  showCreatePanel.value = true;
  await focusCreateFirst();
};

const closeCreatePanel = () => {
  showCreatePanel.value = false;
  createError.value = "";
};

const toggleCreatePanel = async () => {
  if (showCreatePanel.value) {
    closeCreatePanel();
    return;
  }

  await openCreatePanel();
};

const rowValue = (row, column) => {
  if (typeof column.map === "function") return column.map(row);
  return row?.[column.key] ?? "-";
};

const normalize = (value) =>
  String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim();

const rowsFiltrados = computed(() => {
  const query = normalize(searchTrim.value);
  if (!query) return rows.value;

  return rows.value.filter((row) =>
    (props.columns || []).some((column) =>
      normalize(rowValue(row, column)).includes(query)
    )
  );
});

const initForms = () => {
  (props.fields || []).forEach((field) => {
    if (!(field.key in createForm)) createForm[field.key] = "";
    if (!(field.key in editForm)) editForm[field.key] = "";
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
    const raw = source[field.key];

    payload[field.key] =
      typeof raw === "string" && field.type !== "select" ? raw.trim() : raw;
  });

  return payload;
};

const validateRequiredFields = (formObj) => {
  const missing = [];

  (props.fields || []).forEach((field) => {
    if (!field.required) return;

    const value = String(formObj?.[field.key] ?? "").trim();

    if (!value) {
      missing.push(field.label || field.key);
    }
  });

  return missing;
};

const getErrorMessage = (error, fallback) => {
  const data = error?.response?.data;

  if (typeof data === "string") return data;
  if (data?.detail) return data.detail;
  if (data?.error) return data.error;

  if (data && typeof data === "object") {
    const firstKey = Object.keys(data)[0];
    const firstValue = data[firstKey];

    if (Array.isArray(firstValue)) return firstValue.join(" ");
    if (typeof firstValue === "string") return firstValue;
  }

  return error?.message || fallback;
};

const resolveRowLabel = (row) => {
  const firstColumn = props.columns?.[0];
  const label = firstColumn ? rowValue(row, firstColumn) : "";

  return label && label !== "-" ? label : "este registro";
};

const clearSearch = () => {
  search.value = "";
};

const load = async () => {
  loading.value = true;
  loadError.value = "";

  try {
    const data = await props.fetchRows();
    rows.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error(error);

    loadError.value = "No se pudo cargar el catálogo.";

    openNotice({
      title: "Error",
      message: "No se pudo cargar el catálogo.",
    });
  } finally {
    loading.value = false;
  }
};

const create = async () => {
  createError.value = "";

  const missing = validateRequiredFields(createForm);

  if (missing.length) {
    createError.value = `Complete: ${missing.join(", ")}.`;
    return;
  }

  loading.value = true;

  try {
    await props.createRow(buildPayload(createForm));
    resetCreateForm();
    await load();
    closeCreatePanel();

    openNotice({
      title: "Creado",
      message: "El registro se creó correctamente.",
    });
  } catch (error) {
    const msg = getErrorMessage(
      error,
      "No se pudo crear. Verifique la información."
    );

    createError.value = msg;

    openNotice({
      title: "No se pudo crear",
      message: msg,
      details: error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const openEdit = async (row) => {
  editError.value = "";
  editForm.id = row.id;

  (props.fields || []).forEach((field) => {
    editForm[field.key] = row[field.key] ?? "";
  });

  modal.title = `Editar ${resolveRowLabel(row)}`;
  modal.open = true;

  await focusEditFirst();
};

const saveEdit = async () => {
  editError.value = "";

  if (!editForm.id) return;

  const missing = validateRequiredFields(editForm);

  if (missing.length) {
    editError.value = `Complete: ${missing.join(", ")}.`;
    return;
  }

  loading.value = true;

  try {
    await props.updateRow(editForm.id, buildPayload(editForm));

    modal.open = false;
    await load();
    resetEditForm();

    openNotice({
      title: "Actualizado",
      message: "El registro se actualizó correctamente.",
    });
  } catch (error) {
    const msg = getErrorMessage(
      error,
      "No se pudo guardar. Verifique la información."
    );

    editError.value = msg;

    openNotice({
      title: "No se pudo guardar",
      message: msg,
      details: error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const closeModal = () => {
  modal.open = false;
  editError.value = "";
  resetEditForm();
};

const remove = async (row) => {
  const label = resolveRowLabel(row);

  const confirmed = window.confirm(
    `¿Eliminar ${label}? Esta acción no se puede deshacer.`
  );

  if (!confirmed) return;

  loading.value = true;

  try {
    await props.deleteRow(row.id);
    await load();

    openNotice({
      title: "Eliminado",
      message: "El registro se eliminó correctamente.",
    });
  } catch (error) {
    const msg = getErrorMessage(
      error,
      "No se pudo eliminar. Verifique si el registro está relacionado con otros datos."
    );

    openNotice({
      title: "No se pudo eliminar",
      message: msg,
      details: error?.response?.data || null,
    });
  } finally {
    loading.value = false;
  }
};

const onEsc = (event) => {
  if (event.key !== "Escape") return;

  if (modal.open) {
    closeModal();
  }
};

watch(
  () => props.fields,
  () => {
    initForms();
  },
  { immediate: true, deep: true }
);

onMounted(async () => {
  document.addEventListener("keydown", onEsc);
  await load();
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", onEsc);
});
</script>

<style scoped src="./facultades-carreras-crud.css"></style>