<template>
  <main
    class="pdfi-page"
    :aria-busy="diagnosticPending || busy ? 'true' : 'false'"
  >
    <section class="pdfi-shell">
      <header class="pdfi-hero">
        <div class="pdfi-hero__copy">
          <span>Herramientas avanzadas</span>

          <h1>Control de documentos</h1>

          <p>
            Verifique y complete los datos técnicos faltantes de los PDF históricos
            sin modificar la información científica de las publicaciones.
          </p>
        </div>

        <button
          type="button"
          :disabled="diagnosticPending || busy"
          @click="refreshDiagnostic"
        >
          {{ diagnosticPending ? "Actualizando…" : "Actualizar diagnóstico" }}
        </button>
      </header>

      <AdminLoadingState
        v-if="diagnosticVisibleLoading && !diagnosticHasLoaded"
        message="Analizando documentos…"
        description="Estamos verificando los PDF y sus metadatos asociados."
        :skeleton-rows="4"
      />

      <AdminErrorState
        v-else-if="diagnosticError && !diagnosticHasLoaded"
        title="No pudimos cargar el diagnóstico."
        :message="diagnosticError"
        :retrying="diagnosticPending"
        @retry="refreshDiagnostic"
      />

      <template v-else>
        <div class="pdfi-feedback-row">
          <AdminInlineLoader
            v-if="diagnosticVisibleLoading && diagnosticRefreshing"
            message="Actualizando diagnóstico…"
          />

          <AdminActionFeedback
            v-if="actionMessage"
            :status="actionStatus"
            :message="actionMessage"
          />
        </div>

        <p
          v-if="diagnosticError && diagnosticHasLoaded"
          class="pdfi-error"
          role="alert"
        >
          No se pudo actualizar el diagnóstico. Se mantienen los últimos datos disponibles.
          {{ diagnosticError }}
        </p>

        <section
          class="pdfi-metrics"
          aria-label="Estado de los documentos"
        >
          <article>
            <span>Publicaciones con PDF</span>
            <strong>{{ diag.publicaciones_con_pdf || 0 }}</strong>
            <small>Documentos principales encontrados</small>
          </article>

          <article
            :data-state="diag.publicaciones_metadata_incompleta ? 'warning' : 'success'"
          >
            <span>Publicaciones pendientes</span>
            <strong>{{ diag.publicaciones_metadata_incompleta || 0 }}</strong>
            <small>Requieren completar datos del archivo</small>
          </article>

          <article>
            <span>Adjuntos PDF</span>
            <strong>{{ diag.adjuntos_pdf || 0 }}</strong>
            <small>Archivos adicionales encontrados</small>
          </article>

          <article
            :data-state="diag.adjuntos_metadata_incompleta ? 'warning' : 'success'"
          >
            <span>Adjuntos pendientes</span>
            <strong>{{ diag.adjuntos_metadata_incompleta || 0 }}</strong>
            <small>Requieren completar datos del archivo</small>
          </article>
        </section>

        <section class="pdfi-panel pdfi-panel--workflow">
          <header class="pdfi-panel__head">
            <div>
              <span class="pdfi-panel__eyebrow">Proceso seguro</span>
              <h2>Completar datos técnicos</h2>

              <p>
                Primero ejecute una simulación. Solo después de revisar ese resultado
                se habilitará la aplicación real. El proceso no modifica sede, carrera,
                estado, autores ni información bibliográfica.
              </p>
            </div>

            <span
              class="pdfi-readiness"
              :data-ready="simulationReady ? 'true' : 'false'"
            >
              {{ simulationReady ? "Simulación lista" : "Simulación requerida" }}
            </span>
          </header>

          <div class="pdfi-actions">
            <button
              type="button"
              :disabled="busy || diagnosticPending"
              @click="runSimulation"
            >
              {{
                busy && runningMode === "simulation"
                  ? "Simulando…"
                  : "Simular"
              }}
            </button>

            <button
              type="button"
              class="primary"
              :disabled="
                busy ||
                diagnosticPending ||
                nothingPending ||
                !simulationReady
              "
              @click="confirmBackfillOpen = true"
            >
              {{
                busy && runningMode === "backfill"
                  ? "Completando…"
                  : "Completar datos faltantes"
              }}
            </button>
          </div>

          <p
            v-if="nothingPending"
            class="pdfi-ready-message"
          >
            No hay documentos pendientes de normalización técnica.
          </p>
        </section>

        <section
          v-if="result"
          class="pdfi-result"
        >
          <header class="pdfi-result__head">
            <div>
              <span>{{ resultIsSimulation ? "Simulación" : "Proceso finalizado" }}</span>

              <h2>
                {{
                  resultIsSimulation
                    ? "Resultado de la simulación"
                    : "Resultado de la normalización"
                }}
              </h2>
            </div>

            <button
              type="button"
              class="pdfi-result__close"
              aria-label="Cerrar resultado"
              title="Cerrar resultado"
              @click="result = null"
            >
              ×
            </button>
          </header>

          <div
            v-if="resultSummary.length"
            class="pdfi-result__metrics"
          >
            <article
              v-for="item in resultSummary"
              :key="item.key"
            >
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </article>
          </div>

          <p
            v-if="resultMessage"
            class="pdfi-result__message"
          >
            {{ resultMessage }}
          </p>

          <p
            v-if="resultIsSimulation"
            class="pdfi-result__next"
          >
            Revise este resumen. Si los resultados son correctos, puede completar
            los datos faltantes mediante la acción anterior.
          </p>
        </section>
      </template>
    </section>

    <SgpcConfirmDialog
      v-model="confirmBackfillOpen"
      eyebrow="Control de documentos"
      title="Completar datos técnicos"
      message="Se aplicarán únicamente los cambios previamente simulados para completar los datos técnicos faltantes de los PDF. No se modificarán los datos científicos de las publicaciones."
      confirm-label="Completar"
      :busy="busy"
      @confirm="executeBackfill"
    />
  </main>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import SgpcConfirmDialog from "../../inicio/ui/SgpcConfirmDialog.vue";
import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import { useActionState } from "../_shared/composables/useActionState";
import { useAsyncState } from "../_shared/composables/useAsyncState";

import {
  diagnosticoIntegridadDocumental,
  ejecutarBackfillIntegridadDocumental,
} from "../../scripts/api/integridadDocumentalApi";

const diag = ref({});
const result = ref(null);
const busy = ref(false);
const confirmBackfillOpen = ref(false);
const runningMode = ref("");
const resultIsSimulation = ref(false);
const simulationReady = ref(false);

const {
  pending: diagnosticPending,
  visibleLoading: diagnosticVisibleLoading,
  error: diagnosticError,
  hasLoaded: diagnosticHasLoaded,
  refreshing: diagnosticRefreshing,
  begin: beginDiagnostic,
  finish: finishDiagnostic,
  fail: failDiagnostic,
  resetError: resetDiagnosticError,
} = useAsyncState({
  loadingDelay: 220,
});

const {
  status: actionStatus,
  message: actionMessage,
  start: startAction,
  success: actionSuccess,
  fail: actionFail,
} = useActionState();

const nothingPending = computed(() => {
  const publicaciones = Number(diag.value.publicaciones_metadata_incompleta || 0);
  const adjuntos = Number(diag.value.adjuntos_metadata_incompleta || 0);

  return publicaciones === 0 && adjuntos === 0;
});

const resultSummary = computed(() => {
  if (!result.value || typeof result.value !== "object") {
    return [];
  }

  const candidates = [
    {
      keys: ["publicaciones_actualizadas", "publicaciones_procesadas"],
      label: "Publicaciones procesadas",
    },
    {
      keys: ["adjuntos_actualizados", "adjuntos_procesados"],
      label: "Adjuntos procesados",
    },
    {
      keys: ["archivos_actualizados", "actualizados"],
      label: "Archivos actualizados",
    },
    {
      keys: ["omitidos", "saltados"],
      label: "Omitidos",
    },
    {
      keys: ["errores", "errores_total"],
      label: "Errores",
    },
  ];

  return candidates.flatMap((candidate) => {
    const foundKey = candidate.keys.find(
      (key) => result.value[key] !== undefined && result.value[key] !== null
    );

    if (!foundKey) {
      return [];
    }

    const rawValue = result.value[foundKey];

    return [{
      key: foundKey,
      label: candidate.label,
      value: Array.isArray(rawValue) ? rawValue.length : rawValue,
    }];
  });
});

const resultMessage = computed(() => {
  if (!result.value) {
    return "";
  }

  return (
    result.value.message ||
    result.value.mensaje ||
    (
      resultIsSimulation.value
        ? "La simulación terminó sin modificar la base de datos."
        : "La normalización técnica finalizó correctamente."
    )
  );
});

async function loadDiagnostic({ invalidateSimulation = false } = {}) {
  if (diagnosticPending.value) {
    return;
  }

  beginDiagnostic();

  try {
    const nextDiagnostic = await diagnosticoIntegridadDocumental();
    diag.value = nextDiagnostic || {};
    resetDiagnosticError();

    if (invalidateSimulation) {
      simulationReady.value = false;
    }

    finishDiagnostic({ loaded: true });
  } catch (err) {
    failDiagnostic(
      getErrorMessage(
        err,
        "No fue posible obtener el diagnóstico."
      )
    );

    finishDiagnostic({
      loaded: diagnosticHasLoaded.value,
    });
  }
}

function refreshDiagnostic() {
  return loadDiagnostic({
    invalidateSimulation: true,
  });
}

async function runSimulation() {
  if (busy.value || diagnosticPending.value) {
    return;
  }

  busy.value = true;
  runningMode.value = "simulation";
  simulationReady.value = false;
  startAction("Simulando la normalización de documentos…");

  try {
    result.value = await ejecutarBackfillIntegridadDocumental({
      dry_run: true,
    });

    resultIsSimulation.value = true;
    simulationReady.value = true;
    actionSuccess(
      "Simulación completada. Revise el resultado antes de aplicar cambios."
    );

    await loadDiagnostic();
  } catch (err) {
    const message = getErrorMessage(
      err,
      "No fue posible ejecutar la simulación."
    );

    actionFail(message);
  } finally {
    busy.value = false;
    runningMode.value = "";
  }
}

async function executeBackfill() {
  if (
    busy.value ||
    diagnosticPending.value ||
    !simulationReady.value ||
    nothingPending.value
  ) {
    return;
  }

  busy.value = true;
  runningMode.value = "backfill";
  startAction("Completando los datos técnicos faltantes…");

  try {
    result.value = await ejecutarBackfillIntegridadDocumental({
      dry_run: false,
    });

    resultIsSimulation.value = false;
    simulationReady.value = false;
    confirmBackfillOpen.value = false;
    actionSuccess("Datos técnicos completados correctamente.");

    try {
      await loadDiagnostic();
    } catch {
      // loadDiagnostic ya gestiona su propio feedback.
    }
  } catch (err) {
    actionFail(
      getErrorMessage(
        err,
        "No fue posible completar los datos técnicos."
      )
    );
  } finally {
    busy.value = false;
    runningMode.value = "";
  }
}

function getErrorMessage(err, fallback) {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}

onMounted(
  loadDiagnostic
);
</script>

<style src="./admin-integridad-documental.css"></style>
<style src="./admin-integridad-documental-stage7.css"></style>
