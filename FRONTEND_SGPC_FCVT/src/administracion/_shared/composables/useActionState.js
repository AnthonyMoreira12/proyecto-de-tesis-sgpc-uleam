import { computed, ref } from "vue";

export function useActionState() {
  const status = ref("idle");
  const message = ref("");

  const processing = computed(() => status.value === "loading");

  function start(text = "Procesando…") {
    status.value = "loading";
    message.value = text;
  }

  function success(text = "Operación completada correctamente.") {
    status.value = "success";
    message.value = text;
  }

  function fail(text = "No pudimos completar la operación.") {
    status.value = "error";
    message.value = text;
  }

  function reset() {
    status.value = "idle";
    message.value = "";
  }

  return {
    status,
    message,
    processing,
    start,
    success,
    fail,
    reset,
  };
}
