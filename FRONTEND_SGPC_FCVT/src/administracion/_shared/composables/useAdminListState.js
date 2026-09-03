import { computed, reactive, ref } from "vue";
import { useAsyncState } from "./useAsyncState";

export function useAdminListState({ initialFilters = {}, loadingDelay = 220 } = {}) {
  const items = ref([]);
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    count: 0,
  });
  const filters = reactive({ ...initialFilters });

  const asyncState = useAsyncState({ loadingDelay });

  const isEmpty = computed(
    () => asyncState.hasLoaded.value && !asyncState.pending.value && items.value.length === 0,
  );

  function setItems(payload, { page, pageSize, count } = {}) {
    items.value = Array.isArray(payload) ? payload : [];
    if (Number.isFinite(Number(page))) pagination.page = Number(page);
    if (Number.isFinite(Number(pageSize))) pagination.pageSize = Number(pageSize);
    if (Number.isFinite(Number(count))) pagination.count = Number(count);
  }

  function resetFilters() {
    Object.keys(filters).forEach((key) => {
      filters[key] = initialFilters[key] ?? "";
    });
  }

  return {
    items,
    pagination,
    filters,
    isEmpty,
    setItems,
    resetFilters,
    ...asyncState,
  };
}
