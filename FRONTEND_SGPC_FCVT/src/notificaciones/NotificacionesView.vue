<template>
  <div class="notifications-page">
    <div class="notifications-shell">
      <header
        class="notifications-header page-stage page-stage-1"
        aria-labelledby="notifications-page-title"
      >
        <div class="notifications-header__copy">
          <h1
            id="notifications-page-title"
            class="notifications-title"
          >
            Notificaciones
          </h1>
        </div>
      </header>

      <section
        class="notifications-toolbar page-stage page-stage-2"
        aria-label="Opciones de notificaciones"
      >
        <div
          class="notifications-tabs"
          role="tablist"
          aria-label="Filtrar notificaciones"
        >
          <button
            v-for="tab in tabs"
            :key="tab.value"
            type="button"
            role="tab"
            :aria-selected="filter === tab.value"
            :class="{ 'is-active': filter === tab.value }"
            @click="filter = tab.value"
          >
            {{ tab.label }}

            <span
              v-if="tab.value === 'all' && total > 0"
              class="notifications-tabs__count"
              aria-hidden="true"
            >
              {{ compactCount(total) }}
            </span>

            <span
              v-if="tab.value === 'unread' && unreadCount > 0"
              class="notifications-tabs__count"
              :aria-label="`${unreadCount} sin leer`"
            >
              {{ compactCount(unreadCount) }}
            </span>
          </button>
        </div>

        <div class="notifications-toolbar__actions">
          <div class="notifications-toolbar__search-slot">
            <NotificacionesSearchField
              v-model="query"
              placeholder="Buscar notificaciones"
            />
          </div>

          <button
            class="notifications-icon-btn"
            :class="{ 'is-loading': loadingList }"
            type="button"
            :disabled="loadingList"
            title="Actualizar"
            aria-label="Actualizar notificaciones"
            @click="refresh"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.75 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h8V3l-3.35 3.35Z"
              />
            </svg>
          </button>

          <button
            v-if="unreadCount > 0"
            class="notifications-read-all-btn"
            type="button"
            :disabled="markingAll"
            @click="markAll"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="m9 16.17-3.59-3.58L4 14l5 5L20 8l-1.41-1.42L9 16.17Z"
              />
            </svg>

            {{ markingAll ? "Marcando…" : "Marcar todo como leído" }}
          </button>
        </div>
      </section>

      <section
        class="notifications-content page-stage page-stage-3"
        aria-live="polite"
      >
        <div
          v-if="loadingList && !items.length"
          class="notifications-state"
        >
          <span class="notifications-state__icon is-loading" aria-hidden="true">
            <span class="notifications-spinner"></span>
          </span>
          <strong>Cargando notificaciones…</strong>
        </div>

        <div
          v-else-if="errorList && !items.length"
          class="notifications-state is-error"
        >
          <span class="notifications-state__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M11 17h2v2h-2v-2Zm0-12h2v10h-2V5Zm1-3a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z"
              />
            </svg>
          </span>
          <strong>No pudimos cargar las notificaciones.</strong>
          <p>{{ errorList }}</p>
          <button type="button" @click="refresh">
            Reintentar
          </button>
        </div>

        <div
          v-else-if="!filteredItems.length"
          class="notifications-state"
        >
          <span class="notifications-state__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6v-5a7 7 0 0 0-5.5-6.84V3a1.5 1.5 0 0 0-3 0v1.16A7 7 0 0 0 5 11v5l-2 2v1h18v-1l-2-2Zm-11.59 1L7 16.59V11a5 5 0 0 1 10 0v5.59l-.41.41H7.41Z"
              />
            </svg>
          </span>
          <strong>{{ emptyTitle }}</strong>
          <p>{{ emptyText }}</p>

          <button
            v-if="normalizedQuery"
            type="button"
            @click="query = ''"
          >
            Limpiar búsqueda
          </button>
        </div>

        <template v-else>
          <div class="notifications-results-bar">
            <strong>{{ resultsTitle }}</strong>

            <span class="notifications-results-bar__count">
              {{ filteredItems.length }}
              {{ filteredItems.length === 1 ? "resultado" : "resultados" }}
            </span>
          </div>

          <div class="notifications-groups">
            <section
              v-for="group in groupedItems"
              :key="group.key"
              class="notifications-group"
              :aria-labelledby="`notifications-group-${group.key}`"
            >
              <header class="notifications-group__header">
                <h2 :id="`notifications-group-${group.key}`">
                  {{ group.label }}
                </h2>
              </header>

              <div class="notifications-list">
                <NotificacionItem
                  v-for="notification in group.items"
                  :key="notification.id"
                  :notification="notification"
                  :disabled="actionId === Number(notification.id)"
                  @open="openNotification"
                />
              </div>
            </section>
          </div>
        </template>

        <div v-if="hasMore" class="notifications-load-more">
          <button
            type="button"
            :disabled="loadingMore"
            @click="loadMore"
          >
            <span
              v-if="loadingMore"
              class="notifications-load-more__spinner"
              aria-hidden="true"
            ></span>
            {{ loadingMore ? "Cargando…" : "Mostrar más" }}
          </button>
        </div>
      </section>
    </div>

    <Teleport to="body">
      <div
        v-if="detailDialogOpen"
        class="notification-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="notification-detail-modal-title"
        @click.self="closeNotificationDetail()"
      >
        <section
          ref="detailDialogRef"
          class="notification-detail-modal__card"
          tabindex="-1"
          @keydown.esc="closeNotificationDetail()"
        >
          <header class="notification-detail-modal__header">
            <div>
              <h2 id="notification-detail-modal-title">
                {{ detailPresentation.title || "Notificación" }}
              </h2>
            </div>

            <button
              type="button"
              aria-label="Cerrar detalle"
              title="Cerrar"
              @click="closeNotificationDetail()"
            >
              ×
            </button>
          </header>

          <div
            v-if="detailDialogLoading"
            class="notification-detail-modal__loading"
          >
            <span class="notifications-spinner" aria-hidden="true"></span>
            <span>Cargando detalle…</span>
          </div>

          <div
            v-if="selectedNotification"
            class="notification-detail-modal__body"
          >
            <div class="notification-detail-modal__message">
              <p>
                {{
                  selectedNotification.mensaje ||
                  detailPresentation.message ||
                  "Sin información adicional."
                }}
              </p>
            </div>

            <dl class="notification-detail-modal__facts">
              <div>
                <dt>Fecha</dt>
                <dd>{{ formatExtensionDate(selectedNotification.created_at) }}</dd>
              </div>

              <div v-if="selectedNotification.publicacion_id">
                <dt>Publicación</dt>
                <dd>
                  {{ selectedNotification.publicacion_titulo || "Publicación" }}
                </dd>
              </div>

              <div v-if="selectedNotification.publicacion_tipo">
                <dt>Tipo</dt>
                <dd>{{ selectedNotification.publicacion_tipo }}</dd>
              </div>

              <div
                v-if="
                  isExtensionRequestDetail &&
                  detailPresentation.meta
                "
              >
                <dt>Sección</dt>
                <dd>{{ detailPresentation.meta }}</dd>
              </div>
            </dl>

            <section
              v-if="detailExtensionRequest"
              class="notification-detail-modal__request"
              aria-label="Datos de la solicitud"
            >
              <header>
                <div>
                  <strong>Solicitud de más tiempo</strong>
                </div>
                <span
                  class="notification-detail-modal__status"
                  :data-state="detailExtensionRequest.estado"
                >
                  {{ detailExtensionRequest.estado_label || detailExtensionRequest.estado }}
                </span>
              </header>

              <div class="notification-detail-modal__request-grid">
                <div>
                  <span>Usuario</span>
                  <strong>{{ detailExtensionRequest.usuario_nombre || "Usuario" }}</strong>
                  <small>{{ detailExtensionRequest.usuario_email || "Sin correo" }}</small>
                </div>

                <div>
                  <span>Tiempo solicitado</span>
                  <strong>{{ formatRequestedHours(detailExtensionRequest.horas_solicitadas) }}</strong>
                  <small>
                    Solicitado {{ formatExtensionDate(detailExtensionRequest.solicitada_at) }}
                  </small>
                </div>

                <div>
                  <span>Plazo anterior</span>
                  <strong>{{ formatExtensionDate(detailExtensionRequest.plazo_anterior) }}</strong>
                </div>
              </div>

              <div class="notification-detail-modal__request-reason">
                <span>Motivo</span>
                <p>{{ detailExtensionRequest.motivo || "Sin motivo registrado." }}</p>
              </div>
            </section>

            <p
              v-if="detailDialogError"
              class="notification-detail-modal__error"
            >
              {{ detailDialogError }}
            </p>
          </div>

          <footer class="notification-detail-modal__actions">
            <button
              type="button"
              class="is-secondary"
              @click="closeNotificationDetail()"
            >
              Cerrar
            </button>

            <button
              v-if="detailHasAction"
              type="button"
              class="is-primary"
              @click="handleDetailAction"
            >
              {{ detailActionLabel }}
              <span aria-hidden="true">→</span>
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
  </div>
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
  storeToRefs,
} from "pinia";
import {
  useRouter,
} from "vue-router";

import {
  useUserStore,
} from "../scripts/stores/userStore";
import {
  useNotificacionesStore,
} from "../scripts/stores/notificacionesStore";
import NotificacionItem from "./componentes/NotificacionItem.vue";
import NotificacionesSearchField from "./componentes/NotificacionesSearchField.vue";
import {
  obtenerNotificacion,
} from "../scripts/api/notificacionesApi";
import {
  obtenerSolicitudExtensionPerfil,
} from "../scripts/api/profileExtensionApi";
import {
  notificationActionLabel,
  notificationHasAction,
  notificationPresentation,
  notificationTarget,
} from "./notificacionesUtils";

const router = useRouter();
const userStore = useUserStore();
const notificationsStore =
  useNotificacionesStore();

const {
  items,
  total,
  unreadCount,
  loadingList,
  loadingMore,
  markingAll,
  actionId,
  errorList,
  hasMore,
} = storeToRefs(
  notificationsStore
);

const filter = ref("all");
const query = ref("");

/* ==========================================================
   DETALLE DE NOTIFICACIÓN
========================================================== */
const detailDialogOpen = ref(false);
const detailDialogRef = ref(null);
const detailDialogLoading = ref(false);
const detailDialogError = ref("");
const selectedNotification = ref(null);
const loadedExtensionRequest = ref(null);

const tabs = Object.freeze([
  {
    value: "all",
    label: "Todas",
  },
  {
    value: "unread",
    label: "No leídas",
  },
]);

const compactCount = (
  value
) => {
  const count = Number(value || 0);

  return count > 99
    ? "99+"
    : String(count);
};

const normalizedQuery = computed(
  () =>
    String(query.value || "")
      .trim()
      .toLowerCase()
);

const filteredItems = computed(
  () => {
    const q =
      normalizedQuery.value;

    return items.value.filter(
      (notification) => {
        if (
          filter.value ===
            "unread" &&
          notification?.leida
        ) {
          return false;
        }

        if (!q) {
          return true;
        }

        const presentation =
          notificationPresentation(
            notification
          );

        const metadata =
          notification?.metadata || {};

        const haystack = [
          presentation?.title,
          presentation?.message,
          presentation?.meta,
          notification?.publicacion_titulo,
          notification?.publicacion_tipo,
          notification?.tipo,
          metadata?.usuario_nombre,
          metadata?.usuario_email,
          metadata?.motivo,
          metadata?.horas_solicitadas,
          metadata?.estado_solicitud,
        ]
          .map((value) =>
            String(value || "")
              .toLowerCase()
          )
          .join(" ");

        return haystack.includes(q);
      }
    );
  }
);

const dayStart = (
  value
) => {
  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return null;
  }

  return new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate()
  );
};

const notificationGroupKey = (
  notification
) => {
  const notificationDate =
    dayStart(
      notification?.created_at
    );

  if (!notificationDate) {
    return "previous";
  }

  const today =
    dayStart(new Date());

  const diffDays = Math.floor(
    (
      today.getTime() -
      notificationDate.getTime()
    ) / 86_400_000
  );

  if (diffDays <= 0) {
    return "today";
  }

  if (diffDays === 1) {
    return "yesterday";
  }

  if (diffDays <= 7) {
    return "week";
  }

  return "previous";
};

const GROUPS = Object.freeze([
  {
    key: "today",
    label: "Hoy",
  },
  {
    key: "yesterday",
    label: "Ayer",
  },
  {
    key: "week",
    label: "Esta semana",
  },
  {
    key: "previous",
    label: "Anteriores",
  },
]);

const groupedItems = computed(
  () => {
    const buckets = new Map(
      GROUPS.map((group) => [
        group.key,
        [],
      ])
    );

    filteredItems.value.forEach(
      (notification) => {
        const key =
          notificationGroupKey(
            notification
          );

        buckets.get(key)?.push(
          notification
        );
      }
    );

    return GROUPS
      .map((group) => ({
        ...group,
        items:
          buckets.get(group.key) || [],
      }))
      .filter(
        (group) =>
          group.items.length > 0
      );
  }
);

const emptyTitle = computed(
  () => {
    if (
      normalizedQuery.value
    ) {
      return "No encontramos resultados";
    }

    if (
      filter.value ===
      "unread"
    ) {
      return "Todo al día";
    }

    return "Sin notificaciones";
  }
);

const emptyText = computed(
  () => {
    if (
      normalizedQuery.value
    ) {
      return "No encontramos notificaciones que coincidan con su búsqueda.";
    }

    if (
      filter.value ===
      "unread"
    ) {
      return "No tiene notificaciones pendientes de lectura.";
    }

    return "Las nuevas notificaciones aparecerán aquí.";
  }
);

const resultsTitle = computed(
  () => {
    if (normalizedQuery.value) {
      return `Resultados para “${query.value.trim()}”`;
    }

    if (filter.value === "unread") {
      return "No leídas";
    }

    return "Recientes";
  }
);

const detailPresentation = computed(
  () =>
    notificationPresentation(
      selectedNotification.value || {}
    )
);

const detailActionLabel = computed(() => {
  if (
    Boolean(userStore.isAdmin) &&
    isExtensionRequestDetail.value
  ) {
    return "Revisar solicitud";
  }

  return notificationActionLabel(
    selectedNotification.value || {},
    {
      isAdmin: Boolean(
        userStore.isAdmin
      ),
    }
  );
});

const detailExtensionRequest = computed(() => {
  const notification =
    selectedNotification.value || {};

  const type = String(
    notification?.tipo || ""
  ).toLowerCase();

  if (
    type !== "solicitud_extension_perfil"
  ) {
    return null;
  }

  const metadata =
    notification?.metadata || {};

  const loaded =
    loadedExtensionRequest.value || {};

  return {
    id:
      loaded.id ??
      positiveId(
        metadata.solicitud_extension_id
      ),

    usuario_id:
      loaded.usuario_id ??
      positiveId(
        metadata.usuario_id
      ),

    usuario_nombre:
      loaded.usuario_nombre ||
      metadata.usuario_nombre ||
      "Usuario",

    usuario_email:
      loaded.usuario_email ||
      metadata.usuario_email ||
      "",

    horas_solicitadas:
      loaded.horas_solicitadas ??
      metadata.horas_solicitadas ??
      null,

    horas_aprobadas:
      loaded.horas_aprobadas ??
      metadata.horas_aprobadas ??
      null,

    motivo:
      loaded.motivo ||
      metadata.motivo ||
      "",

    estado:
      loaded.estado ||
      metadata.estado_solicitud ||
      "pendiente",

    estado_label:
      loaded.estado_label ||
      (
        metadata.estado_solicitud ===
        "pendiente"
          ? "Pendiente"
          : metadata.estado_solicitud ||
            "Pendiente"
      ),

    plazo_anterior:
      loaded.plazo_anterior ??
      metadata.plazo_anterior ??
      null,

    nuevo_plazo:
      loaded.nuevo_plazo ??
      metadata.nuevo_plazo ??
      null,

    solicitada_at:
      loaded.solicitada_at ||
      notification.created_at ||
      null,

    motivo_resolucion:
      loaded.motivo_resolucion ||
      metadata.motivo_resolucion ||
      "",
  };
});

const isExtensionRequestDetail = computed(() =>
  String(
    selectedNotification.value?.tipo || ""
  ).toLowerCase() === "solicitud_extension_perfil"
);

const hasUsableExtensionMetadata = (notification) => {
  const metadata =
    notification?.metadata || {};

  return Boolean(
    positiveId(metadata.solicitud_extension_id) ||
    positiveId(metadata.usuario_id) ||
    String(metadata.motivo || "").trim() ||
    Number(metadata.horas_solicitadas) > 0
  );
};

const detailHasAction = computed(() => {
  const notification =
    selectedNotification.value || {};

  if (
    Boolean(userStore.isAdmin) &&
    isExtensionRequestDetail.value
  ) {
    const request =
      detailExtensionRequest.value || {};

    const state = String(
      request?.estado ||
      notification?.metadata?.estado_solicitud ||
      "pendiente"
    ).toLowerCase();

    return (
      state === "pendiente" &&
      Boolean(
        positiveId(request.id) ||
        positiveId(
          notification?.metadata?.solicitud_extension_id
        ) ||
        positiveId(request.usuario_id) ||
        positiveId(notification?.metadata?.usuario_id)
      )
    );
  }

  return notificationHasAction(
    notification
  );
});

const refresh = async () => {
  await notificationsStore.loadList({
    reset: true,
  });
};

const loadMore = async () => {
  await notificationsStore.loadList({
    reset: false,
  });
};

const markAll = async () => {
  try {
    await notificationsStore.markAllRead();
  } catch (error) {
    console.warn(
      "No fue posible marcar todas las notificaciones como leídas.",
      error
    );
  }
};

const notificationId = (notification) => {
  const id = Number(notification?.id);
  return Number.isInteger(id) && id > 0
    ? id
    : null;
};

const positiveId = (value) => {
  const id = Number(value);
  return Number.isInteger(id) && id > 0
    ? id
    : null;
};

const normalizeNotificationDetailError = (error) => {
  const data = error?.response?.data;
  const status = Number(
    error?.response?.status || 0
  );

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para consultar este detalle.";
  }

  if (status >= 500) {
    return "No se pudo actualizar el detalle completo. Intente nuevamente en unos momentos.";
  }

  return String(
    data?.detail ||
    data?.message ||
    "No se pudo cargar el detalle de la notificación."
  ).trim();
};

const loadExtensionDetail = async (notification) => {
  loadedExtensionRequest.value = null;

  if (
    !Boolean(userStore.isAdmin) ||
    String(notification?.tipo || "").toLowerCase() !==
      "solicitud_extension_perfil"
  ) {
    return {
      loaded: false,
      error: null,
    };
  }

  const requestId = positiveId(
    notification?.metadata?.solicitud_extension_id
  );

  if (!requestId) {
    return {
      loaded: false,
      error: null,
    };
  }

  try {
    loadedExtensionRequest.value =
      await obtenerSolicitudExtensionPerfil(
        requestId
      );

    return {
      loaded: Boolean(
        loadedExtensionRequest.value
      ),
      error: null,
    };
  } catch (error) {
    console.warn(
      "No fue posible enriquecer la notificación con el detalle administrativo de la solicitud.",
      error
    );

    return {
      loaded: false,
      error,
    };
  }
};

const openNotificationDetail = async (
  notification
) => {
  if (!notification) {
    return;
  }

  const id = notificationId(notification);

  selectedNotification.value = {
    ...notification,
    metadata: {
      ...(notification?.metadata || {}),
    },
  };

  detailDialogOpen.value = true;
  detailDialogLoading.value = true;
  detailDialogError.value = "";
  loadedExtensionRequest.value = null;

  let notificationFetchError = null;

  if (id) {
    try {
      const fullNotification =
        await obtenerNotificacion(id);

      if (fullNotification) {
        selectedNotification.value = {
          ...selectedNotification.value,
          ...fullNotification,
          metadata: {
            ...(selectedNotification.value?.metadata || {}),
            ...(fullNotification?.metadata || {}),
          },
        };
      }
    } catch (error) {
      notificationFetchError = error;

      console.warn(
        "No fue posible actualizar el detalle completo de la notificación. Se utilizarán los datos ya disponibles.",
        error
      );
    }
  }

  const extensionResult =
    await loadExtensionDetail(
      selectedNotification.value
    );

  const current =
    selectedNotification.value || {};

  if (
    isExtensionRequestDetail.value &&
    !loadedExtensionRequest.value &&
    !hasUsableExtensionMetadata(current)
  ) {
    detailDialogError.value =
      normalizeNotificationDetailError(
        extensionResult?.error ||
        notificationFetchError
      );
  } else if (
    !isExtensionRequestDetail.value &&
    notificationFetchError
  ) {
    detailDialogError.value =
      normalizeNotificationDetailError(
        notificationFetchError
      );
  }

  detailDialogLoading.value = false;
};

const closeNotificationDetail = () => {
  detailDialogOpen.value = false;
  detailDialogLoading.value = false;
  detailDialogError.value = "";
  selectedNotification.value = null;
  loadedExtensionRequest.value = null;
};

const handleDetailAction = async () => {
  const notification =
    selectedNotification.value;

  if (!notification) {
    return;
  }

  const type = String(
    notification?.tipo || ""
  ).toLowerCase();

  if (
    Boolean(userStore.isAdmin) &&
    type === "solicitud_extension_perfil"
  ) {
    const request =
      detailExtensionRequest.value || {};
    const metadata =
      notification?.metadata || {};

    const userId =
      positiveId(request.usuario_id) ||
      positiveId(metadata.usuario_id);
    const requestId =
      positiveId(request.id) ||
      positiveId(metadata.solicitud_extension_id);

    if (!requestId && !userId) {
      detailDialogError.value =
        "La solicitud no contiene información suficiente para abrirla en Administración.";
      return;
    }

    closeNotificationDetail();

    const query = {
      tab: "solicitudes",
    };

    if (requestId) {
      query.solicitud = String(requestId);
    } else {
      query.accion = "extension-perfil";
      query.usuario = String(userId);
    }

    await router.push({
      path: "/admin/usuarios",
      query,
    });
    return;
  }

  const target = notificationTarget(
    notification,
    {
      isAdmin: Boolean(
        userStore.isAdmin
      ),
    }
  );

  closeNotificationDetail();

  if (
    target &&
    target !== "/notificaciones"
  ) {
    await router.push(target);
  }
};

const formatRequestedHours = (value) => {
  const hours = Number(value);

  return Number.isFinite(hours) && hours > 0
    ? `${hours} horas`
    : "No disponible";
};

const formatExtensionDate = (value) => {
  if (!value) return "No disponible";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

let previousBodyOverflow = "";

watch(
  detailDialogOpen,
  async (isOpen) => {
    if (isOpen) {
      previousBodyOverflow =
        document.body.style.overflow;

      document.body.style.overflow =
        "hidden";

      await nextTick();

      detailDialogRef.value?.focus?.();
      return;
    }

    document.body.style.overflow =
      previousBodyOverflow;
  }
);

const openNotification = async (
  notification
) => {
  try {
    if (!notification?.leida) {
      await notificationsStore.markRead(
        notification
      );
    }
  } catch (error) {
    console.warn(
      "No fue posible marcar la notificación como leída.",
      error
    );
  }

  await openNotificationDetail(
    notification
  );
};

onMounted(async () => {
  /* El host global mantiene la sincronización en vivo. */
  await refresh();
});

onBeforeUnmount(() => {
  document.body.style.overflow =
    previousBodyOverflow;
});
</script>

<style src="./notificaciones.css"></style>
