<template>
  <SgpcConfirmDialog
    v-model="open"
    eyebrow="Actualización de información"
    title="Información pendiente por completar"
    :message="message"
    confirm-label="Revisar información"
    cancel-label="Recordarme después"
    tone="primary"
    @confirm="goToPendingInformation"
    @cancel="closeForThisLogin"
  >
    <div
      v-if="summaryRows.length"
      class="pending-login-summary"
      aria-label="Resumen de información pendiente"
    >
      <div
        v-for="row in summaryRows"
        :key="row.key"
        class="pending-login-summary__row"
      >
        <span class="pending-login-summary__label">
          {{ row.label }}
        </span>
        <span class="pending-login-summary__value">
          {{ row.text }}
        </span>
      </div>
    </div>

    <p class="pending-login-summary__hint">
      El aviso permanecerá disponible en Notificaciones y se enviarán
      recordatorios mientras exista información obligatoria pendiente.
    </p>
  </SgpcConfirmDialog>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { useRouter } from "vue-router";

import SgpcConfirmDialog from "../../inicio/ui/SgpcConfirmDialog.vue";
import { sincronizarAvisoMisActualizaciones } from "../../scripts/api/actualizacionesApi";
import { useNotificacionesStore } from "../../scripts/stores/notificacionesStore";
import {
  markPendingUpdateModalSeen,
  shouldShowPendingUpdateModal,
} from "../../scripts/utils/actualizacionesSession";

const emit = defineEmits([
  "visibility-change",
]);

const router = useRouter();
const notificacionesStore = useNotificacionesStore();

const open = ref(false);
const summary = ref(null);
let syncTimer = null;

const BACKGROUND_SYNC_MS = 30 * 60 * 1000;

const numberValue = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0
    ? parsed
    : 0;
};

const plural = (
  value,
  singular,
  pluralForm
) => `${value} ${value === 1 ? singular : pluralForm}`;

const summaryRows = computed(() => {
  const buckets = summary.value?.por_tipo || {};

  const config = [
    ["perfil", "Perfil"],
    ["publicacion", "Publicaciones"],
    ["proyecto", "Proyectos"],
  ];

  return config.flatMap(([key, label]) => {
    const bucket = buckets?.[key] || {};
    const fields = numberValue(bucket.campos);
    const records = numberValue(bucket.registros);

    if (!fields && !records) {
      return [];
    }

    const parts = [];

    if (records) {
      parts.push(
        plural(
          records,
          "registro",
          "registros"
        )
      );
    }

    if (fields) {
      parts.push(
        plural(
          fields,
          "campo",
          "campos"
        )
      );
    }

    return [{
      key,
      label,
      text: parts.join(" · "),
    }];
  });
});

const message = computed(() => {
  const fields = numberValue(
    summary.value?.total_campos_pendientes
  );
  const records = numberValue(
    summary.value?.total_registros_pendientes
  );

  if (fields && records) {
    return (
      `Tienes ${plural(fields, "campo obligatorio pendiente", "campos obligatorios pendientes")} ` +
      `en ${plural(records, "registro", "registros")}. ` +
      "Puedes completarlos ahora o continuar y revisarlos después desde Notificaciones."
    );
  }

  return "Tienes información obligatoria pendiente de completar. Puedes revisarla ahora o hacerlo posteriormente desde Notificaciones.";
});

const refreshNotifications = async (
  payload
) => {
  const created =
    numberValue(payload?.notificaciones_creadas) > 0;

  if (!created) {
    return;
  }

  await notificacionesStore.syncLive({
    notify: false,
    forceRecent: true,
  });
};

const synchronize = async ({
  allowModal = false,
} = {}) => {
  try {
    const payload =
      await sincronizarAvisoMisActualizaciones();

    summary.value = payload || null;

    await refreshNotifications(payload);

    if (
      allowModal &&
      payload?.requiere_actualizacion === true &&
      shouldShowPendingUpdateModal()
    ) {
      markPendingUpdateModalSeen();
      open.value = true;
    }
  } catch (error) {
    const status = Number(
      error?.response?.status
    );

    if (status !== 401) {
      console.warn(
        "No se pudo sincronizar el aviso de información pendiente.",
        error
      );
    }
  }
};

const closeForThisLogin = () => {
  open.value = false;
};

const goToPendingInformation = async () => {
  open.value = false;
  await router.push("/informacion-pendiente");
};

watch(
  open,
  (value) => {
    emit(
      "visibility-change",
      Boolean(value)
    );
  },
  { immediate: true }
);

onMounted(async () => {
  await synchronize({
    allowModal: true,
  });

  syncTimer = window.setInterval(
    () => {
      if (
        typeof document !== "undefined" &&
        document.visibilityState !== "visible"
      ) {
        return;
      }

      synchronize({
        allowModal: false,
      });
    },
    BACKGROUND_SYNC_MS
  );
});

onBeforeUnmount(() => {
  if (syncTimer) {
    window.clearInterval(syncTimer);
    syncTimer = null;
  }

  emit(
    "visibility-change",
    false
  );
});
</script>

<style scoped>
.pending-login-summary {
  display: grid;
  gap: 0;
  margin-top: 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-card);
}

.pending-login-summary__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
}

.pending-login-summary__row:last-child {
  border-bottom: 0;
}

.pending-login-summary__label {
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 720;
}

.pending-login-summary__value {
  color: var(--text-secondary);
  font-size: 0.76rem;
  text-align: right;
}

.pending-login-summary__hint {
  margin-top: 14px !important;
  color: var(--text-secondary);
  font-size: 0.74rem !important;
  line-height: 1.55 !important;
}

@media (max-width: 520px) {
  .pending-login-summary__row {
    align-items: flex-start;
    flex-direction: column;
    gap: 3px;
  }

  .pending-login-summary__value {
    text-align: left;
  }
}
</style>
