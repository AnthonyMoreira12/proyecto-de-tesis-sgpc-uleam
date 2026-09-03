<template>
  <Teleport to="body">
    <div
      class="profile-request-modal__backdrop"
    role="presentation"
    @click.self="handleClose"
  >
    <section
      class="profile-request-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="profile-request-modal-title"
      :aria-busy="busy"
    >
      <header class="profile-request-modal__header">
        <div class="profile-request-modal__heading">
          <h2
            id="profile-request-modal-title"
            class="profile-request-modal__title"
          >
            Solicitud de edición de perfil
          </h2>

          <p class="profile-request-modal__subtitle">
            Revise la solicitud antes de tomar una decisión.
          </p>
        </div>

        <button
          class="profile-request-modal__close"
          type="button"
          :disabled="busy"
          aria-label="Cerrar"
          title="Cerrar"
          @click="handleClose"
        >
          ×
        </button>
      </header>

      <div class="profile-request-modal__body">
        <template v-if="!resolvedState">
          <section class="profile-request-modal__identity">
            <div>
              <strong class="profile-request-modal__user-name">
                {{ userName }}
              </strong>
              <span class="profile-request-modal__user-email">
                {{ userEmail }}
              </span>
            </div>

            <span class="profile-request-modal__pending-badge">
              Pendiente
            </span>
          </section>

          <section class="profile-request-modal__summary">
            <div class="profile-request-modal__summary-item">
              <span>Tiempo solicitado</span>
              <strong>{{ requestedHoursLabel }}</strong>
            </div>

            <div class="profile-request-modal__summary-item">
              <span>Fecha de solicitud</span>
              <strong>{{ requestedAtLabel }}</strong>
            </div>

            <div class="profile-request-modal__summary-item">
              <span>Plazo anterior</span>
              <strong>{{ previousDeadlineLabel }}</strong>
            </div>
          </section>

          <section class="profile-request-modal__reason">
            <h3>Motivo de la solicitud</h3>
            <p>
              {{ requestReason }}
            </p>
          </section>

          <div
            v-if="errorMessage"
            class="profile-request-modal__alert profile-request-modal__alert--error"
            role="alert"
            aria-live="assertive"
          >
            {{ errorMessage }}
          </div>

          <section
            v-if="decisionMode !== 'reject'"
            class="profile-request-modal__decision"
            aria-labelledby="profile-request-approve-title"
          >
            <div class="profile-request-modal__decision-copy">
              <h3 id="profile-request-approve-title">
                Aprobar solicitud
              </h3>
              <p>
                Seleccione el tiempo que tendrá disponible para editar el perfil.
              </p>
            </div>

            <label class="profile-request-modal__field">
              <span>Tiempo que se concederá</span>
              <select
                v-model.number="approvedHours"
                :disabled="busy"
              >
                <option
                  v-for="hours in availableHours"
                  :key="hours"
                  :value="hours"
                >
                  {{ hours }} horas
                </option>
              </select>
            </label>
          </section>

          <section
            v-else
            class="profile-request-modal__decision profile-request-modal__decision--reject"
            aria-labelledby="profile-request-reject-title"
          >
            <div class="profile-request-modal__decision-copy">
              <h3 id="profile-request-reject-title">
                Rechazar solicitud
              </h3>
              <p>
                Indique brevemente por qué no se concederá el tiempo solicitado.
              </p>
            </div>

            <label class="profile-request-modal__field">
              <span>Motivo del rechazo</span>
              <textarea
                ref="rejectReasonRef"
                v-model="rejectionReason"
                rows="4"
                maxlength="1000"
                :disabled="busy"
                placeholder="Escriba el motivo del rechazo"
              ></textarea>
              <small>
                Mínimo 10 caracteres.
              </small>
            </label>
          </section>
        </template>

        <section
          v-else
          class="profile-request-modal__resolved"
          aria-live="polite"
        >
          <span
            class="profile-request-modal__resolved-status"
            :class="
              resolvedState.decision === 'aprobar'
                ? 'is-approved'
                : 'is-rejected'
            "
          >
            {{
              resolvedState.decision === "aprobar"
                ? "Solicitud aprobada"
                : "Solicitud rechazada"
            }}
          </span>

          <h3>
            {{ resolvedTitle }}
          </h3>

          <p>
            {{ resolvedMessage }}
          </p>
        </section>
      </div>

      <footer class="profile-request-modal__footer">
        <template v-if="!resolvedState">
          <button
            v-if="decisionMode !== 'reject'"
            class="profile-request-modal__btn profile-request-modal__btn--secondary"
            type="button"
            :disabled="busy"
            @click="openRejectMode"
          >
            Rechazar
          </button>

          <button
            v-else
            class="profile-request-modal__btn profile-request-modal__btn--secondary"
            type="button"
            :disabled="busy"
            @click="cancelRejectMode"
          >
            Volver
          </button>

          <button
            v-if="decisionMode !== 'reject'"
            class="profile-request-modal__btn profile-request-modal__btn--primary"
            type="button"
            :disabled="busy"
            @click="approveRequest"
          >
            {{ busy ? "Procesando…" : "Aprobar solicitud" }}
          </button>

          <button
            v-else
            class="profile-request-modal__btn profile-request-modal__btn--danger"
            type="button"
            :disabled="busy || rejectionReasonTrim.length < 10"
            @click="rejectRequest"
          >
            {{ busy ? "Procesando…" : "Confirmar rechazo" }}
          </button>
        </template>

        <button
          v-else
          class="profile-request-modal__btn profile-request-modal__btn--primary"
          type="button"
          @click="handleClose"
        >
          Volver a solicitudes
        </button>
      </footer>
      </section>
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
  watch,
} from "vue";

import {
  resolverSolicitudExtensionPerfil,
} from "../../scripts/api/profileExtensionApi";


const props = defineProps({
  solicitud: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits([
  "close",
  "resolved",
]);

const availableHours = Object.freeze([
  6,
  12,
  24,
  48,
  72,
]);

const approvedHours = ref(24);
const decisionMode = ref("review");
const rejectionReason = ref("");
const rejectReasonRef = ref(null);
const busy = ref(false);
const errorMessage = ref("");
const resolvedState = ref(null);


const normalizeText = (value) => {
  return String(value ?? "").trim();
};


const normalizeApprovedHours = (value) => {
  const parsed = Number(value);

  if (availableHours.includes(parsed)) {
    return parsed;
  }

  const requested = Number(
    props.solicitud?.horas_solicitadas
  );

  if (availableHours.includes(requested)) {
    return requested;
  }

  return 24;
};


const userName = computed(() => {
  return (
    normalizeText(props.solicitud?.usuario_nombre) ||
    "Usuario"
  );
});


const userEmail = computed(() => {
  return (
    normalizeText(props.solicitud?.usuario_email) ||
    "Correo no disponible"
  );
});


const requestReason = computed(() => {
  return (
    normalizeText(props.solicitud?.motivo) ||
    "No se registró un motivo."
  );
});


const requestedHoursLabel = computed(() => {
  const hours = Number(
    props.solicitud?.horas_solicitadas
  );

  return Number.isFinite(hours) && hours > 0
    ? `${hours} horas`
    : "No disponible";
});


const formatDateTime = (value) => {
  if (!value) {
    return "No disponible";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};


const requestedAtLabel = computed(() => {
  return formatDateTime(
    props.solicitud?.solicitada_at
  );
});


const previousDeadlineLabel = computed(() => {
  return formatDateTime(
    props.solicitud?.plazo_anterior
  );
});


const rejectionReasonTrim = computed(() => {
  return normalizeText(
    rejectionReason.value
  );
});


const resolvedTitle = computed(() => {
  if (!resolvedState.value) {
    return "";
  }

  if (resolvedState.value.decision === "aprobar") {
    return `${userName.value} ya puede editar su perfil.`;
  }

  return "La decisión fue registrada correctamente.";
});


const resolvedMessage = computed(() => {
  const state = resolvedState.value;

  if (!state) {
    return "";
  }

  if (state.decision === "aprobar") {
    const hours = Number(
      state?.solicitud?.horas_aprobadas ||
      approvedHours.value
    );
    const deadline = formatDateTime(
      state?.solicitud?.nuevo_plazo
    );

    return (
      `Se concedieron ${hours} horas adicionales. ` +
      `El nuevo plazo finaliza el ${deadline}.`
    );
  }

  return (
    "La solicitud salió de la cola pendiente y el usuario continuará " +
    "sin permiso de edición hasta que exista una nueva autorización."
  );
});


const resetState = () => {
  approvedHours.value = normalizeApprovedHours(
    props.solicitud?.horas_solicitadas
  );
  decisionMode.value = "review";
  rejectionReason.value = "";
  errorMessage.value = "";
  resolvedState.value = null;
};


const resolveApiError = (error, fallback) => {
  const data = error?.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  const fields = [
    "decision",
    "horas_aprobadas",
    "motivo_resolucion",
  ];

  for (const field of fields) {
    const value = data?.[field];

    if (Array.isArray(value) && value[0]) {
      return String(value[0]);
    }

    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return fallback;
};


const processDecision = async (
  decision,
  payload = {}
) => {
  if (busy.value) {
    return;
  }

  const requestId = Number(
    props.solicitud?.id
  );

  if (!Number.isInteger(requestId) || requestId < 1) {
    errorMessage.value =
      "La solicitud seleccionada no tiene un identificador válido.";
    return;
  }

  busy.value = true;
  errorMessage.value = "";

  try {
    const result =
      await resolverSolicitudExtensionPerfil(
        requestId,
        {
          decision,
          ...payload,
        }
      );

    const solicitud =
      result?.solicitud ||
      props.solicitud;

    resolvedState.value = {
      decision,
      solicitud,
    };

    emit("resolved", {
      decision,
      solicitud,
    });
  } catch (error) {
    const responseData =
      error?.response?.data || {};
    const resolvedRequest =
      responseData?.solicitud || null;
    const resolvedRequestState = normalizeText(
      resolvedRequest?.estado
    ).toLowerCase();

    /*
     * Si otro administrador resolvió la misma solicitud unos instantes
     * antes, el backend responde 409 con la solicitud actual. En lugar de
     * dejar una fila obsoleta como si siguiera pendiente, sincronizamos la
     * decisión real y retiramos la solicitud de la cola.
     */
    if (
      Number(error?.response?.status) === 409 &&
      resolvedRequest &&
      ["aprobada", "rechazada"].includes(
        resolvedRequestState
      )
    ) {
      const actualDecision =
        resolvedRequestState === "aprobada"
          ? "aprobar"
          : "rechazar";

      resolvedState.value = {
        decision: actualDecision,
        solicitud: resolvedRequest,
      };

      emit("resolved", {
        decision: actualDecision,
        solicitud: resolvedRequest,
        stale: true,
      });

      return;
    }

    errorMessage.value = resolveApiError(
      error,
      decision === "aprobar"
        ? "No se pudo aprobar la solicitud. Intente nuevamente."
        : "No se pudo rechazar la solicitud. Intente nuevamente."
    );
  } finally {
    busy.value = false;
  }
};


const approveRequest = async () => {
  await processDecision(
    "aprobar",
    {
      horas_aprobadas:
        normalizeApprovedHours(
          approvedHours.value
        ),
      motivo_resolucion: "",
    }
  );
};


const rejectRequest = async () => {
  if (rejectionReasonTrim.value.length < 10) {
    errorMessage.value =
      "Indique un motivo de rechazo de al menos 10 caracteres.";
    await nextTick();
    rejectReasonRef.value?.focus?.();
    return;
  }

  await processDecision(
    "rechazar",
    {
      horas_aprobadas: null,
      motivo_resolucion:
        rejectionReasonTrim.value,
    }
  );
};


const openRejectMode = async () => {
  decisionMode.value = "reject";
  errorMessage.value = "";

  await nextTick();
  rejectReasonRef.value?.focus?.();
};


const cancelRejectMode = () => {
  decisionMode.value = "review";
  rejectionReason.value = "";
  errorMessage.value = "";
};


const handleClose = () => {
  if (busy.value) {
    return;
  }

  emit("close");
};


const handleKeydown = (event) => {
  if (event.key === "Escape") {
    handleClose();
  }
};


watch(
  () => props.solicitud,
  () => {
    resetState();
  },
  {
    immediate: true,
    deep: true,
  }
);

onMounted(() => {
  window.addEventListener(
    "keydown",
    handleKeydown
  );
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    handleKeydown
  );
});
</script>

<style
  scoped
  src="./solicitud-edicion-perfil-modal.css"
></style>
