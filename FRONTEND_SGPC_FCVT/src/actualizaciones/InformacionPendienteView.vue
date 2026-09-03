<template>
  <main class="pending-page">
    <section class="pending-shell">
      <!-- =====================================================
           CABECERA
      ====================================================== -->
      <header class="pending-hero">
        <div class="pending-hero__copy">
          <span>Actualización de información</span>

          <h1>Información pendiente</h1>

          <p>
            Revise y complete únicamente los datos solicitados
            mediante campañas de actualización vigentes. Las publicaciones
            incluidas en este módulo son únicamente las aprobadas.
          </p>
        </div>

        <button
          type="button"
          :disabled="loading"
          @click="refreshAll"
        >
          {{
            loading
              ? "Actualizando..."
              : "Actualizar"
          }}
        </button>
      </header>

      <!-- =====================================================
           RESUMEN
      ====================================================== -->
      <section
        class="pending-summary"
        aria-label="Resumen de información pendiente"
      >
        <article>
          <span>Campañas activas</span>

          <strong>
            {{ activeCampaigns }}
          </strong>

          <small>
            Periodos de actualización disponibles
          </small>
        </article>

        <article
          :data-state="
            totalRecords
              ? 'warning'
              : 'success'
          "
        >
          <span>Registros pendientes</span>

          <strong>
            {{ totalRecords }}
          </strong>

          <small>
            Perfiles, publicaciones aprobadas o proyectos
          </small>
        </article>

        <article
          :data-state="
            totalFields
              ? 'warning'
              : 'success'
          "
        >
          <span>Campos por completar</span>

          <strong>
            {{ totalFields }}
          </strong>

          <small>
            Datos que todavía requieren atención
          </small>
        </article>
      </section>

      <!-- =====================================================
           ERROR
      ====================================================== -->
      <p
        v-if="error"
        class="pending-alert pending-alert--error"
        role="alert"
      >
        {{ error }}
      </p>

      <!-- =====================================================
           CARGA
      ====================================================== -->
      <section
        v-if="loading && !campaigns.length"
        class="pending-loading"
      >
        <span class="pending-spinner"></span>

        <div>
          <strong>Consultando información</strong>

          <span>
            Revisando campañas y registros pendientes.
          </span>
        </div>
      </section>

      <!-- =====================================================
           TODO AL DÍA
      ====================================================== -->
      <section
        v-else-if="!campaigns.length"
        class="pending-empty pending-empty--success"
      >
        <strong>
          Su información está al día
        </strong>

        <span>
          Actualmente no tiene campañas de actualización activas.
        </span>
      </section>

      <!-- =====================================================
           VISTA ADMINISTRATIVA DE PUBLICACIONES
      ====================================================== -->
      <section
        v-if="showPublicationViewSwitch && campaigns.length"
        class="pending-view-switch"
        aria-label="Vista de publicaciones pendientes"
      >
        <div class="pending-view-switch__copy">
          <strong>Vista de publicaciones</strong>

          <span>
            {{
              publicationView === "mias"
                ? "Mostrando únicamente las publicaciones en las que figuras como autor."
                : "Mostrando todas las publicaciones pendientes disponibles para tu vista administrativa."
            }}
          </span>
        </div>

        <div
          class="pending-view-switch__actions"
          role="group"
          aria-label="Cambiar vista de publicaciones"
        >
          <button
            type="button"
            :class="{ 'is-active': publicationView === 'todas' }"
            :aria-pressed="publicationView === 'todas'"
            @click="publicationView = 'todas'"
          >
            Todas
          </button>

          <button
            type="button"
            :class="{ 'is-active': publicationView === 'mias' }"
            :aria-pressed="publicationView === 'mias'"
            @click="publicationView = 'mias'"
          >
            Mis publicaciones
          </button>
        </div>
      </section>

      <!-- =====================================================
           CAMPAÑAS
      ====================================================== -->
      <section
        v-if="campaigns.length"
        class="pending-campaigns"
      >
        <article
          v-for="item in campaigns"
          :key="item.id"
          class="pending-card"
          :data-state="item.estado"
        >
          <!-- CABECERA CAMPAÑA -->
          <header class="pending-card__head">
            <div class="pending-card__identity">
              <span class="pending-kind">
                {{ typeLabel(item.campania_tipo) }}
              </span>

              <h2>
                {{ item.campania_titulo }}
              </h2>

              <p>
                {{
                  item.campania_fecha_fin
                    ? `Disponible hasta ${formatDate(item.campania_fecha_fin)}`
                    : "Sin fecha límite"
                }}
              </p>
            </div>

            <span
              class="pending-state"
              :data-state="item.estado"
            >
              {{ stateLabel(item.estado) }}
            </span>
          </header>

          <!-- RESUMEN CAMPAÑA -->
          <section class="pending-card__summary">
            <article>
              <span>
                {{ campaignRecordMetricLabel(item) }}
              </span>

              <strong>
                {{ campaignRecordCount(item) }}
              </strong>
            </article>

            <article>
              <span>Campos pendientes</span>

              <strong>
                {{ campaignFieldCount(item) }}
              </strong>
            </article>
          </section>

          <!-- CAMPOS GENERALES -->
          <section
            v-if="
              Array.isArray(item.campos_pendientes) &&
              item.campos_pendientes.length
            "
            class="pending-fields-section"
          >
            <span class="pending-fields-label">
              Información requerida
            </span>

            <div class="pending-fields">
              <span
                v-for="field in item.campos_pendientes"
                :key="field"
              >
                {{ fieldLabel(field) }}
              </span>
            </div>
          </section>

          <!-- =================================================
               PERFIL
          ================================================== -->
          <section
            v-if="item.campania_tipo === 'perfil'"
            class="pending-record pending-record--profile"
          >
            <div class="pending-record__copy">
              <span>Perfil académico</span>

              <strong>Mi perfil</strong>

              <p>
                {{ pendingText(item.campos_pendientes) }}
              </p>
            </div>

            <button
              v-if="item.campos_pendientes?.length"
              type="button"
              :disabled="openingId === item.id"
              @click="openProfile(item)"
            >
              {{
                openingId === item.id
                  ? "Abriendo..."
                  : "Completar información"
              }}
            </button>

            <span
              v-else
              class="pending-complete-badge"
            >
              Completo
            </span>
          </section>

          <!-- =================================================
               PUBLICACIONES / PROYECTOS
          ================================================== -->
          <template v-else>
            <section
              v-if="records(item).length"
              class="pending-records"
            >
              <article
                v-for="record in records(item)"
                :key="record.id"
                class="pending-record"
              >
                <div class="pending-record__copy">
                  <span>
                    {{
                      item.campania_tipo === "publicacion"
                        ? "Publicación aprobada"
                        : "Proyecto"
                    }}
                  </span>

                  <strong
                    :title="recordTitle(item, record)"
                  >
                    {{
                      recordTitle(
                        item,
                        record
                      )
                    }}
                  </strong>

                  <div
                    v-if="
                      item.campania_tipo === 'publicacion' &&
                      (record.tipo || record.anio)
                    "
                    class="pending-record__meta"
                    aria-label="Datos de la publicación"
                  >
                    <span v-if="record.tipo">
                      {{ record.tipo }}
                    </span>

                    <span v-if="record.anio">
                      {{ record.anio }}
                    </span>
                  </div>

                  <p>
                    {{ pendingText(record.campos) }}
                  </p>

                  <div
                    v-if="record.campos?.length"
                    class="pending-record__fields"
                  >
                    <span
                      v-for="field in record.campos"
                      :key="field"
                    >
                      {{ fieldLabel(field) }}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  :disabled="
                    openingId ===
                    `${item.id}:${record.id}`
                  "
                  @click="
                    openRecord(
                      item,
                      record
                    )
                  "
                >
                  {{
                    openingId ===
                    `${item.id}:${record.id}`
                      ? "Abriendo..."
                      : "Completar"
                  }}
                </button>
              </article>
            </section>

            <section
              v-else
              class="pending-complete"
            >
              <strong>
                {{ emptyRecordsTitle(item) }}
              </strong>

              <span>
                {{ emptyRecordsText(item) }}
              </span>
            </section>
          </template>

          <!-- FOOTER -->
          <footer class="pending-card__footer">
            <span>
              {{ summaryLabel(item) }}
            </span>

            <button
              type="button"
              class="pending-link"
              :disabled="
                recalculatingId === item.id
              "
              @click="recalculate(item)"
            >
              {{
                recalculatingId === item.id
                  ? "Revisando..."
                  : "Revisar progreso"
              }}
            </button>
          </footer>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import {
  useRouter,
} from "vue-router";

import {
  apiErrorMessage,
  asResults,
  iniciarMiActualizacion,
  listarMisActualizaciones,
  recalcularMiActualizacion,
} from "../scripts/api/actualizacionesApi";

import {
  useUserStore,
} from "../scripts/stores/userStore";


/* ============================================================
   ESTADO
============================================================ */

const router = useRouter();

const userStore = useUserStore();

const publicationView = ref("todas");

const campaigns = ref([]);

const loading = ref(false);

const error = ref("");

const openingId = ref(null);

const recalculatingId = ref(null);


/* ============================================================
   ETIQUETAS
============================================================ */

const labels = {
  identificacion: "Cédula",
  sede: "Sede",
  carrera: "Carrera",

  area: "Área UNESCO",
  subarea: "Subárea UNESCO",

  pais: "País",
  ciudad: "Ciudad",

  proyecto: "Proyecto asociado",

  descripcion: "Descripción",

  fecha_inicio: "Fecha de inicio",

  fecha_fin_planificada:
    "Fecha de finalización planificada",

  fecha_fin_prorrogada:
    "Fecha de finalización prorrogada",
};


/* ============================================================
   COMPUTADOS
============================================================ */

const isAdmin = computed(() => Boolean(userStore.isAdmin));


const showPublicationViewSwitch = computed(() => (
  isAdmin.value &&
  campaigns.value.some(
    (item) =>
      item.campania_tipo === "publicacion" &&
      rawRecords(item).length
  )
));


const activeCampaigns = computed(() => (
  campaigns.value.filter(
    (item) =>
      item.estado !== "completada"
  ).length
));


const totalRecords = computed(() => (
  campaigns.value.reduce(
    (total, item) => (
      total +
      campaignRecordCount(item)
    ),
    0
  )
));


const totalFields = computed(() => (
  campaigns.value.reduce(
    (total, item) => (
      total +
      campaignFieldCount(item)
    ),
    0
  )
));


/* ============================================================
   FORMATO
============================================================ */

function fieldLabel(value) {
  return (
    labels[value] ||
    humanize(value)
  );
}


function typeLabel(value) {
  const types = {
    perfil: "Perfil",
    publicacion: "Publicaciones",
    proyecto: "Proyectos",
  };

  return (
    types[value] ||
    humanize(value)
  );
}


function stateLabel(value) {
  const states = {
    pendiente: "Pendiente",
    en_progreso: "En progreso",
    completada: "Completada",
    omitida: "Omitida",
  };

  return (
    states[value] ||
    humanize(value)
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


function formatDate(value) {
  if (!value) {
    return "Sin fecha límite";
  }

  const parsed =
    new Date(value);

  if (
    Number.isNaN(
      parsed.getTime()
    )
  ) {
    return String(value);
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      dateStyle: "long",
    }
  ).format(parsed);
}


function rawRecords(item) {
  return Array.isArray(
    item?.resumen_pendientes?.registros
  )
    ? item.resumen_pendientes.registros
    : [];
}


function records(item) {
  const list = rawRecords(item);

  if (
    !isAdmin.value ||
    publicationView.value !== "mias" ||
    item?.campania_tipo !== "publicacion"
  ) {
    return list;
  }

  return list.filter(
    (record) => record?.es_mia === true
  );
}


function pendingText(fields) {
  if (
    !Array.isArray(fields) ||
    !fields.length
  ) {
    return "Información completa";
  }

  return (
    fields.length === 1
      ? `Falta completar ${fieldLabel(fields[0])}.`
      : `Faltan ${fields.length} datos por completar.`
  );
}


function recordTitle(
  campaign,
  record
) {
  const title =
    record.titulo ||
    record.nombre ||
    record.nombre_publicacion ||
    record.nombre_proyecto;

  if (title) {
    return title;
  }

  return (
    campaign.campania_tipo === "publicacion"
      ? "Publicación sin título"
      : "Proyecto sin nombre"
  );
}


/* ============================================================
   CONTADORES
============================================================ */

function campaignRecordCount(item) {
  if (
    item.campania_tipo === "perfil"
  ) {
    return (
      item.campos_pendientes?.length
        ? 1
        : 0
    );
  }

  return records(item).length;
}


function campaignRecordMetricLabel(item) {
  if (item.campania_tipo === "publicacion") {
    if (isAdmin.value && publicationView.value === "mias") {
      return "Mis publicaciones aprobadas por actualizar";
    }

    return "Publicaciones aprobadas por actualizar";
  }

  if (item.campania_tipo === "perfil") {
    return "Perfil pendiente";
  }

  return "Proyectos por actualizar";
}


function campaignFieldCount(item) {
  if (
    item.campania_tipo === "perfil"
  ) {
    return (
      item.campos_pendientes?.length ||
      0
    );
  }

  return records(item).reduce(
    (total, record) => (
      total +
      (
        Array.isArray(record.campos)
          ? record.campos.length
          : 0
      )
    ),
    0
  );
}


function summaryLabel(item) {
  const count =
    campaignRecordCount(item);

  if (
    item.campania_tipo === "perfil"
  ) {
    return count
      ? "Perfil pendiente"
      : "Perfil completo";
  }

  if (
    item.campania_tipo === "publicacion"
  ) {
    if (isAdmin.value && publicationView.value === "mias") {
      return (
        count === 1
          ? "1 publicación propia aprobada pendiente"
          : `${count} publicaciones propias aprobadas pendientes`
      );
    }

    return (
      count === 1
        ? "1 publicación aprobada pendiente"
        : `${count} publicaciones aprobadas pendientes`
    );
  }

  return (
    count === 1
      ? "1 proyecto pendiente"
      : `${count} proyectos pendientes`
  );
}


function emptyRecordsTitle(item) {
  if (
    isAdmin.value &&
    publicationView.value === "mias" &&
    item?.campania_tipo === "publicacion"
  ) {
    return "No tienes publicaciones pendientes";
  }

  return "No quedan registros pendientes";
}


function emptyRecordsText(item) {
  if (
    isAdmin.value &&
    publicationView.value === "mias" &&
    item?.campania_tipo === "publicacion"
  ) {
    return (
      "No se encontraron publicaciones aprobadas pendientes " +
      "en las que figures como autor."
    );
  }

  return (
    "La información correspondiente a esta campaña " +
    "ya está completa."
  );
}


/* ============================================================
   DATOS
============================================================ */

async function load() {
  loading.value = true;

  error.value = "";

  try {
    campaigns.value =
      asResults(
        await listarMisActualizaciones()
      );
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudo consultar su información pendiente."
      );
  } finally {
    loading.value = false;
  }
}


/* ============================================================
   ACTUALIZAR TODO
============================================================ */

async function refreshAll() {
  if (loading.value) {
    return;
  }

  loading.value = true;
  error.value = "";

  try {
    await Promise.all(
      campaigns.value.map(
        (item) =>
          recalcularMiActualizacion(
            item.id
          )
      )
    );

    campaigns.value =
      asResults(
        await listarMisActualizaciones()
      );
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No se pudo actualizar el estado de su información."
      );
  } finally {
    loading.value = false;
  }
}


/* ============================================================
   INICIAR PARTICIPACIÓN
============================================================ */

async function start(item) {
  if (
    item.estado !== "pendiente"
  ) {
    return true;
  }

  try {
    await iniciarMiActualizacion(
      item.id
    );

    item.estado =
      "en_progreso";

    return true;
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible iniciar la actualización."
      );

    return false;
  }
}


/* ============================================================
   PERFIL
============================================================ */

async function openProfile(item) {
  openingId.value =
    item.id;

  try {
    const started =
      await start(item);

    if (!started) {
      return;
    }

    await router.push({
      path:
        "/informacion-pendiente/perfil",

      query: {
        participacion:
          item.id,

        campos:
          (
            item.campos_pendientes ||
            []
          ).join(","),
      },
    });
  } finally {
    openingId.value = null;
  }
}


/* ============================================================
   REGISTROS
============================================================ */

async function openRecord(
  item,
  record
) {
  const key =
    `${item.id}:${record.id}`;

  openingId.value =
    key;

  try {
    const started =
      await start(item);

    if (!started) {
      return;
    }

    const path =
      item.campania_tipo ===
      "publicacion"
        ? `/informacion-pendiente/publicacion/${record.id}`
        : `/informacion-pendiente/proyecto/${record.id}`;

    await router.push({
      path,

      query: {
        participacion:
          item.id,

        campos:
          (
            record.campos ||
            []
          ).join(","),
      },
    });
  } finally {
    openingId.value = null;
  }
}


/* ============================================================
   PROGRESO
============================================================ */

async function recalculate(item) {
  recalculatingId.value =
    item.id;

  error.value = "";

  try {
    await recalcularMiActualizacion(
      item.id
    );

    await load();
  } catch (err) {
    error.value =
      apiErrorMessage(
        err,
        "No fue posible revisar el progreso de la campaña."
      );
  } finally {
    recalculatingId.value =
      null;
  }
}


/* ============================================================
   INICIO
============================================================ */

onMounted(
  load
);
</script>

<style src="./informacion-pendiente.css"></style>