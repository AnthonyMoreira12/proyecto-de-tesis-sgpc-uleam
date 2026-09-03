import { onBeforeUnmount, ref, watch } from "vue";

export function useDebouncedSearch(initialValue = "", { delay = 320 } = {}) {
  const search = ref(initialValue);
  const debouncedSearch = ref(initialValue);
  let timer = null;

  watch(search, (value) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      debouncedSearch.value = value;
    }, Math.max(0, Number(delay) || 0));
  });

  onBeforeUnmount(() => {
    if (timer) clearTimeout(timer);
  });

  return {
    search,
    debouncedSearch,
  };
}
