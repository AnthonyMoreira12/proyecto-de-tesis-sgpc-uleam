<template>
  <main
    class="prep-page"
    :aria-busy="diagnosticPending || busy ? 'true' : 'false'"
  >
    <section class="prep-shell">

      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="prep-hero">
        <div class="prep-hero__copy">
          <span>Herramientas avanzadas</span>

          <h1>Preparación de actualización</h1>

          <p>
            Revise el estado de los datos históricos, simule los ajustes seguros
            y verifique su conservación antes de habilitar una nueva versión del SGPC.
          </p>
        </div>

        <button
          type="button"
          :disabled="busy || diagnosticPending"
          @click="refreshDiagnostic"
        >
          {{
            diagnosticPending
              ? "Actualizando…"
              : "Actualizar diagnóstico"
          }}
        </button>
      </header>

      <AdminLoadingState
        v-if="diagnosticVisibleLoading && !diagnosticHasLoaded"
        message="Analizando preparación…"
        description="Estamos revisando la estructura académica y los registros históricos."
        :skeleton-rows="4"
      />

      <AdminErrorState
        v-else-if="diagnosticError && !diagnosticHasLoaded"
        title="No pudimos cargar el diagnóstico."
        :message="diagnosticError"
        :retrying="diagnosticPending"
        @retry="refreshDiagnostic"
      />

      <div class="prep-feedback-row">
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
        class="prep-message is-error"
        role="alert"
      >
        No se pudo actualizar el diagnóstico. Se mantienen los últimos datos disponibles.
        {{ diagnosticError }}
      </p>

      <!-- =====================================================
           MENSAJES
      ====================================================== -->
      <p
        v-if="error"
        class="prep-message is-error"
        role="alert"
      >
        {{ error }}
      </p>


      <!-- =====================================================
           ESTADO GENERAL
      ====================================================== -->
      <section
        v-if="diagnostic"
        class="prep-status"
        :class="{
          'is-blocked':
            !diagnostic.listo_para_abrir
        }"
      >
        <div class="prep-status__marker"></div>

        <div class="prep-status__body">
          <strong>
            {{
              diagnostic.listo_para_abrir
                ? "Sin bloqueos estructurales"
                : "Hay bloqueos que deben resolverse"
            }}
          </strong>

          <span>
            {{
              diagnostic.listo_para_abrir
                ? "Puede continuar con la simulación y revisar los registros pendientes antes de aplicar cambios."
                : "No habilite la nueva versión para los usuarios hasta resolver los bloqueos identificados."
            }}
          </span>
        </div>
      </section>

      <!-- =====================================================
           MÉTRICAS
      ====================================================== -->
      <section
        v-if="diagnostic"
        class="prep-metrics"
        aria-label="Resumen de preparación"
      >
        <article
          :data-state="
            diagnostic.usuarios?.sin_sede
              ? 'warning'
              : 'success'
          "
        >
          <span>Usuarios institucionales</span>

          <strong>
            {{ diagnostic.usuarios?.institucionales || 0 }}
          </strong>

          <small>
            {{ diagnostic.usuarios?.sin_sede || 0 }}
            sin sede
          </small>
        </article>

        <article
          :data-state="
            diagnostic.publicaciones?.sin_sede
              ? 'warning'
              : 'success'
          "
        >
          <span>Publicaciones</span>

          <strong>
            {{ diagnostic.publicaciones?.total || 0 }}
          </strong>

          <small>
            {{ diagnostic.publicaciones?.sin_sede || 0 }}
            sin sede
          </small>
        </article>

        <article
          :data-state="
            diagnostic.proyectos?.sin_sede
              ? 'warning'
              : 'success'
          "
        >
          <span>Proyectos</span>

          <strong>
            {{ diagnostic.proyectos?.total || 0 }}
          </strong>

          <small>
            {{ diagnostic.proyectos?.sin_sede || 0 }}
            sin sede
          </small>
        </article>

        <article>
          <span>Relaciones Carrera–Sede</span>

          <strong>
            {{
              diagnostic.catalogos
                ?.carreras_sedes_activas || 0
            }}
          </strong>

          <small>
            Relaciones activas
          </small>
        </article>
      </section>

      <!-- =====================================================
           BLOQUEOS / ADVERTENCIAS
      ====================================================== -->
      <section
        v-if="
          diagnostic?.bloqueos?.length ||
          diagnostic?.advertencias?.length
        "
        class="prep-grid"
      >
        <article
          v-if="diagnostic?.bloqueos?.length"
          class="prep-panel prep-panel--danger"
        >
          <header class="prep-panel-head">
            <div>
              <span>Requiere intervención</span>
              <h2>Bloqueos</h2>
            </div>

            <strong class="prep-panel-count">
              {{ diagnostic.bloqueos.length }}
            </strong>
          </header>

          <ul class="prep-issue-list">
            <li
              v-for="item in diagnostic.bloqueos"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>

          <RouterLink
            class="prep-link"
            to="/admin/estructura/facultades"
          >
            Revisar estructura académica
          </RouterLink>
        </article>

        <article
          v-if="diagnostic?.advertencias?.length"
          class="prep-panel prep-panel--warning"
        >
          <header class="prep-panel-head">
            <div>
              <span>Revisión recomendada</span>
              <h2>Advertencias</h2>
            </div>

            <strong class="prep-panel-count">
              {{ diagnostic.advertencias.length }}
            </strong>
          </header>

          <ul class="prep-issue-list">
            <li
              v-for="item in diagnostic.advertencias"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>

          <RouterLink
            class="prep-link"
            to="/admin/actualizaciones"
          >
            Gestionar campañas de actualización
          </RouterLink>
        </article>
      </section>

      <!-- =====================================================
           NORMALIZACIÓN
      ====================================================== -->
      <section
        v-if="diagnosticHasLoaded"
        class="prep-panel prep-normalize"
      >
        <header class="prep-panel-head">
          <div>
            <span>Proceso controlado</span>

            <h2>Normalización segura</h2>

            <p>
              Primero realice una simulación. La sede predeterminada
              únicamente se asignará cuando exista una relación
              Carrera–Sede activa y compatible. Si no existe evidencia
              suficiente, el registro permanecerá pendiente.
            </p>
          </div>
        </header>

        <div class="prep-form-row">
          <label class="prep-field">
            <span>Sede predeterminada</span>

            <select
              v-model="defaultSedeId"
              :disabled="busy"
            >
              <option value="">
                Sin sede predeterminada
              </option>

              <option
                v-for="sede in sedes"
                :key="sede.id"
                :value="String(sede.id)"
              >
                {{
                  sede.nombre ||
                  sede.label ||
                  sede.descripcion ||
                  `Sede ${sede.id}`
                }}
              </option>
            </select>
          </label>

          <label
            class="prep-check"
            :class="{
              'is-disabled': !defaultSedeId
            }"
          >
            <input
              v-model="useDefaultSede"
              type="checkbox"
              :disabled="
                !defaultSedeId ||
                busy
              "
            >

            <span>
              Usar esta sede como respaldo para
              registros históricos compatibles
            </span>
          </label>
        </div>

        <p
          v-if="simulationStale"
          class="prep-inline-warning"
        >
          La configuración cambió después de la última simulación.
          Debe simular nuevamente antes de aplicar.
        </p>

        <div class="prep-actions">
          <button
            type="button"
            :disabled="busy"
            @click="simulate"
          >
            {{
              simulationLoading
                ? "Simulando…"
                : "1. Simular normalización"
            }}
          </button>

          <button
            type="button"
            class="primary"
            :disabled="
              busy ||
              !simulation ||
              simulationStale
            "
            @click="applyNormalization"
          >
            {{
              busy && operationStage === "applying"
                ? "Aplicando…"
                : "2. Aplicar normalización"
            }}
          </button>
        </div>
      </section>

      <!-- =====================================================
           RESULTADO DE SIMULACIÓN
      ====================================================== -->
      <section
        v-if="simulation"
        class="prep-panel prep-simulation"
      >
        <header class="prep-panel-head">
          <div>
            <span>Vista previa</span>

            <h2>Resultado de la simulación</h2>

            <p>
              Estos son los cambios que el sistema puede realizar
              sin modificar todavía la base de datos.
            </p>
          </div>

          <span
            class="prep-chip"
            :class="{
              'is-warning': simulationStale
            }"
          >
            {{
              simulationStale
                ? "Debe repetir la simulación"
                : "Simulación vigente"
            }}
          </span>
        </header>

        <div class="prep-simulation-grid">
          <article>
            <span>Usuarios con sede</span>

            <strong>
              {{
                simulation.resumen
                  ?.usuarios_sede || 0
              }}
            </strong>
          </article>

          <article>
            <span>Publicaciones con sede</span>

            <strong>
              {{
                simulation.resumen
                  ?.publicaciones_sede || 0
              }}
            </strong>
          </article>

          <article>
            <span>Proyectos con sede</span>

            <strong>
              {{
                simulation.resumen
                  ?.proyectos_sede || 0
              }}
            </strong>
          </article>

          <article>
            <span>Perfiles recalculados</span>

            <strong>
              {{
                simulation.resumen
                  ?.perfiles_recalculados || 0
              }}
            </strong>
          </article>
        </div>

        <section class="prep-pending">
          <header>
            <h3>Seguirán pendientes</h3>

            <p>
              Estos registros necesitan intervención adicional
              o una campaña de actualización.
            </p>
          </header>

          <div class="prep-pending-grid">
            <article>
              <span>Usuarios</span>

              <strong>
                {{
                  simulation.pendientes
                    ?.usuarios_sin_sede
                    ?.length || 0
                }}
              </strong>
            </article>

            <article>
              <span>Publicaciones</span>

              <strong>
                {{
                  simulation.pendientes
                    ?.publicaciones_sin_sede
                    ?.length || 0
                }}
              </strong>
            </article>

            <article>
              <span>Proyectos</span>

              <strong>
                {{
                  simulation.pendientes
                    ?.proyectos_sin_sede
                    ?.length || 0
                }}
              </strong>
            </article>

            <article>
              <span>Relaciones inconsistentes</span>

              <strong>
                {{
                  simulation.pendientes
                    ?.relaciones_invalidas
                    ?.length || 0
                }}
              </strong>
            </article>
          </div>
        </section>
      </section>

      <!-- =====================================================
           VERIFICACIÓN
      ====================================================== -->
      <section
        v-if="verification"
        class="prep-panel"
      >
        <header class="prep-panel-head">
          <div>
            <span>Protección de datos</span>

            <h2>Verificación de conservación</h2>

            <p
              :class="
                verification.perdida_detectada
                  ? 'danger-text'
                  : 'ok-text'
              "
            >
              {{
                verification.perdida_detectada
                  ? "Se detectó una reducción en los conteos críticos. No continúe con el despliegue."
                  : "Los conteos críticos se conservaron correctamente."
              }}
            </p>
          </div>

          <span
            class="prep-chip"
            :class="{
              'is-danger':
                verification.perdida_detectada
            }"
          >
            {{
              verification.perdida_detectada
                ? "Revisión necesaria"
                : "Conservación correcta"
            }}
          </span>
        </header>

        <div class="prep-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Entidad</th>
                <th>Antes</th>
                <th>Después</th>
                <th>Diferencia</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="
                  (row, key)
                  in verification.diferencias
                "
                :key="key"
              >
                <td>
                  {{ labelEntity(key) }}
                </td>

                <td>
                  {{ row.antes }}
                </td>

                <td>
                  {{ row.despues }}
                </td>

                <td>
                  <strong
                    :class="{
                      'danger-text':
                        Number(row.delta) < 0,
                      'ok-text':
                        Number(row.delta) === 0
                    }"
                  >
                    {{ formatDelta(row.delta) }}
                  </strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- =====================================================
           DATOS NUEVOS
      ====================================================== -->
      <section
        v-if="diagnostic"
        class="prep-panel"
      >
        <header class="prep-panel-head">
          <div>
            <span>Seguimiento</span>

            <h2>Estado de los datos nuevos</h2>

            <p>
              Resumen de los campos incorporados por la nueva
              versión y la acción recomendada para completarlos.
            </p>
          </div>
        </header>

        <div class="prep-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Control</th>
                <th>Cantidad</th>
                <th>Acción recomendada</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>Usuarios sin sede</td>

                <td>
                  {{ diagnostic.usuarios?.sin_sede || 0 }}
                </td>

                <td>
                  Normalización o campaña de perfil
                </td>
              </tr>

              <tr>
                <td>Usuarios sin carrera</td>

                <td>
                  {{ diagnostic.usuarios?.sin_carrera || 0 }}
                </td>

                <td>
                  Campaña de perfil
                </td>
              </tr>

              <tr>
                <td>Perfil desincronizado</td>

                <td>
                  {{
                    diagnostic.usuarios
                      ?.perfil_completo_desincronizado || 0
                  }}
                </td>

                <td>
                  Se recalcula automáticamente
                </td>
              </tr>

              <tr>
                <td>Publicaciones sin sede</td>

                <td>
                  {{
                    diagnostic.publicaciones
                      ?.sin_sede || 0
                  }}
                </td>

                <td>
                  Inferencia segura o campaña
                </td>
              </tr>

              <tr>
                <td>Proyectos sin sede</td>

                <td>
                  {{
                    diagnostic.proyectos
                      ?.sin_sede || 0
                  }}
                </td>

                <td>
                  Inferencia segura o campaña
                </td>
              </tr>

              <tr>
                <td>
                  PDF de publicación con metadatos incompletos
                </td>

                <td>
                  {{
                    diagnostic.integridad_documental
                      ?.publicaciones_metadata_incompleta || 0
                  }}
                </td>

                <td>
                  <RouterLink
                    class="prep-link"
                    to="/admin/integridad-documental"
                  >
                    Control de documentos
                  </RouterLink>
                </td>
              </tr>

              <tr>
                <td>
                  Usuarios con Carrera–Sede inválida
                </td>

                <td>
                  {{
                    diagnostic.usuarios
                      ?.relacion_sede_carrera_invalida || 0
                  }}
                </td>

                <td>
                  Corregir estructura o usuario
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>

    <!-- =======================================================
         CONFIRMACIÓN
    ======================================================== -->
    <SgpcConfirmDialog
      v-model="confirmNormalizationOpen"
      eyebrow="Preparación de actualización"
      title="Aplicar normalización"
      message="Se aplicarán únicamente las asignaciones seguras mostradas en la simulación y se recalculará el estado del perfil. No se eliminarán registros."
      confirm-label="Aplicar"
      :busy="busy"
      @confirm="executeNormalization"
    />
  </main>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  RouterLink,
} from "vue-router";

import SgpcConfirmDialog from "../../inicio/ui/SgpcConfirmDialog.vue";
import AdminActionFeedback from "../_shared/components/feedback/AdminActionFeedback.vue";
import AdminErrorState from "../_shared/components/feedback/AdminErrorState.vue";
import AdminInlineLoader from "../_shared/components/feedback/AdminInlineLoader.vue";
import AdminLoadingState from "../_shared/components/feedback/AdminLoadingState.vue";
import { useActionState } from "../_shared/composables/useActionState";
import { useAsyncState } from "../_shared/composables/useAsyncState";

import {
  getAdminSedes,
} from "../_shared/utils/adminCatalogCache";

import {
  diagnosticarPreparacionProduccion,
  normalizarPreparacionProduccion,
  verificarPreparacionProduccion,
} from "../../scripts/api/preparacionProduccionApi";


/* ============================================================
   ESTADO
============================================================ */

const diagnostic = ref(null);

const simulation = ref(null);
const verification = ref(null);

const baseline = ref(null);

const sedes = ref([]);

const defaultSedeId = ref("");
const useDefaultSede = ref(false);

const busy = ref(false);
const simulationLoading = ref(false);
const operationStage = ref("");

const error = ref("");

const confirmNormalizationOpen = ref(false);

const simulationConfiguration = ref(null);

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


/* ============================================================
   COMPUTADOS
============================================================ */

const currentConfiguration = computed(() => ({
  sedeId:
    defaultSedeId.value || "",

  useDefault:
    Boolean(
      useDefaultSede.value &&
      defaultSedeId.value
    ),
}));


const simulationStale = computed(() => {
  if (!simulation.value) {
    return false;
  }

  if (!simulationConfiguration.value) {
    return true;
  }

  return (
    JSON.stringify(
      simulationConfiguration.value
    ) !==
    JSON.stringify(
      currentConfiguration.value
    )
  );
});


/* ============================================================
   UTILIDADES
============================================================ */

function listOf(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}


function labelEntity(key) {
  const labels = {
    usuarios: "Usuarios",
    autores: "Autores",
    publicaciones: "Publicaciones",
    proyectos: "Proyectos",
  };

  return labels[key] || key;
}


function formatDelta(value) {
  const number =
    Number(value || 0);

  if (number > 0) {
    return `+${number}`;
  }

  return String(number);
}


function getErrorMessage(
  err,
  fallback
) {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}


/* ============================================================
   DIAGNÓSTICO
============================================================ */

async function loadDiagnostic() {
  if (diagnosticPending.value) {
    return;
  }

  beginDiagnostic();

  try {
    const nextDiagnostic =
      await diagnosticarPreparacionProduccion();

    diagnostic.value = nextDiagnostic;
    resetDiagnosticError();

    if (!baseline.value) {
      baseline.value =
        nextDiagnostic?.snapshot ||
        null;
    }

    finishDiagnostic({ loaded: true });
  } catch (err) {
    failDiagnostic(
      getErrorMessage(
        err,
        "No fue posible obtener el diagnóstico de preparación."
      )
    );

    finishDiagnostic({
      loaded: diagnosticHasLoaded.value,
    });
  }
}


function refreshDiagnostic() {
  simulation.value = null;
  simulationConfiguration.value = null;
  verification.value = null;

  return loadDiagnostic();
}


/* ============================================================
   SEDES
============================================================ */

async function loadSedes() {
  try {
    sedes.value =
      listOf(
        await getAdminSedes()
      );
  } catch {
    if (!sedes.value.length) {
      sedes.value = [];
    }
  }
}


/* ============================================================
   NORMALIZACIÓN
============================================================ */

function normalizationPayload(
  dryRun
) {
  return {
    dry_run: dryRun,

    sede_predeterminada_id:
      defaultSedeId.value ||
      null,

    usar_sede_predeterminada:
      Boolean(
        useDefaultSede.value &&
        defaultSedeId.value
      ),

    ...(
      dryRun
        ? {}
        : {
            confirmacion:
              "NORMALIZAR_PRODUCCION",
          }
    ),
  };
}


async function simulate() {
  if (busy.value) {
    return;
  }

  busy.value = true;
  simulationLoading.value = true;
  operationStage.value = "simulating";

  error.value = "";
  verification.value = null;
  startAction("Simulando la normalización segura…");

  try {
    simulation.value =
      await normalizarPreparacionProduccion(
        normalizationPayload(true)
      );

    simulationConfiguration.value = {
      ...currentConfiguration.value,
    };

    actionSuccess(
      "Simulación completada. Revise los cambios propuestos y los registros que seguirán pendientes."
    );
  } catch (err) {
    actionFail(
      getErrorMessage(
        err,
        "No fue posible simular la normalización."
      )
    );
  } finally {
    simulationLoading.value = false;
    operationStage.value = "";
    busy.value = false;
  }
}


function applyNormalization() {
  if (
    !simulation.value ||
    simulationStale.value
  ) {
    return;
  }

  confirmNormalizationOpen.value = true;
}


async function executeNormalization() {
  if (
    busy.value ||
    !simulation.value ||
    simulationStale.value
  ) {
    return;
  }

  busy.value = true;
  error.value = "";
  operationStage.value = "applying";
  startAction("Aplicando las asignaciones seguras simuladas…");

  let result = null;

  try {
    result =
      await normalizarPreparacionProduccion(
        normalizationPayload(false)
      );
  } catch (err) {
    actionFail(
      getErrorMessage(
        err,
        "No fue posible aplicar la normalización."
      )
    );
    operationStage.value = "";
    busy.value = false;
    return;
  }

  /*
   * Conservamos la última simulación visible como referencia, pero la
   * invalidamos después de aplicar para impedir una segunda ejecución
   * sin volver a simular sobre el estado actualizado de la base.
   */
  simulationConfiguration.value = null;
  confirmNormalizationOpen.value = false;

  let verificationIssue = "";
  let diagnosticIssue = "";

  if (baseline.value) {
    operationStage.value = "verifying";
    startAction("Normalización aplicada. Verificando conservación de datos…");

    try {
      verification.value =
        await verificarPreparacionProduccion(
          baseline.value
        );
    } catch (err) {
      verificationIssue = getErrorMessage(
        err,
        "No fue posible completar la verificación de conservación."
      );
    }
  }

  operationStage.value = "refreshing";
  startAction("Normalización aplicada. Actualizando el diagnóstico…");

  try {
    diagnostic.value =
      result?.diagnostico_despues ||
      await diagnosticarPreparacionProduccion();
  } catch (err) {
    diagnosticIssue = getErrorMessage(
      err,
      "No fue posible actualizar el diagnóstico posterior."
    );
  }

  operationStage.value = "";
  busy.value = false;

  if (verificationIssue || diagnosticIssue) {
    error.value = [
      "La normalización ya fue aplicada correctamente, pero quedó pendiente una comprobación posterior.",
      verificationIssue,
      diagnosticIssue,
      "Actualice el diagnóstico y verifique la conservación antes del despliegue.",
    ]
      .filter(Boolean)
      .join(" ");

    actionSuccess("Normalización aplicada. Verificación posterior pendiente.");
    return;
  }

  if (verification.value?.perdida_detectada) {
    error.value =
      "La normalización fue aplicada, pero la verificación detectó una reducción en los conteos críticos. No continúe con el despliegue hasta revisar el resultado.";

    actionSuccess(
      "Normalización aplicada. La verificación requiere revisión obligatoria."
    );
    return;
  }

  actionSuccess(
    "Normalización aplicada y verificación posterior completada correctamente."
  );
}


/* ============================================================
   WATCHERS
============================================================ */

watch(
  defaultSedeId,
  (value) => {
    if (!value) {
      useDefaultSede.value = false;
    }
  }
);


/* ============================================================
   INICIO
============================================================ */

onMounted(
  async () => {
    await Promise.all([
      loadDiagnostic(),
      loadSedes(),
    ]);
  }
);
</script>

<style src="./admin-preparacion-produccion.css"></style>
<style src="./admin-preparacion-produccion-stage7.css"></style>