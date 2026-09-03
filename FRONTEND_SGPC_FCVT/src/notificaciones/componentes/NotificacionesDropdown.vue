<template>
  <div
    ref="wrap"
    class="notifications-dropdown"
  >
    <button
      ref="trigger"
      class="sgpc-nav__top-action notifications-dropdown__trigger"
      :class="{
        'is-open': open,
        'has-unread': unreadCount > 0,
      }"
      type="button"
      :aria-label="triggerTitle"
      aria-haspopup="dialog"
      aria-controls="sgpc-notifications-panel"
      :aria-expanded="open ? 'true' : 'false'"
      :title="triggerTitle"
      @click.stop="toggle"
    >
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          fill="currentColor"
          d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-5v-5a7 7 0 0 0-5-6.71V4a2 2 0 1 0-4 0v1.29A7 7 0 0 0 5 12v5l-2 2h18l-2-2Zm-2 0H7v-5a5 5 0 0 1 10 0v5Z"
        />
      </svg>

      <span
        v-if="unreadCount > 0"
        class="notifications-dropdown__badge"
      >
        {{ unreadLabel }}
      </span>
    </button>

    <Transition name="notification-panel">
      <section
        v-if="open"
        id="sgpc-notifications-panel"
        ref="panel"
        class="notifications-dropdown__panel"
        role="dialog"
        aria-modal="false"
        aria-label="Notificaciones"
        tabindex="-1"
        @click.stop
      >
        <header class="notifications-dropdown__head">
          <div class="notifications-dropdown__head-copy">
            <strong>Notificaciones</strong>
            <small>{{ quickSubtitle }}</small>
          </div>

          <div class="notifications-dropdown__head-actions">
            <button
              v-if="unreadCount > 0"
              class="notifications-dropdown__mark-all"
              type="button"
              :disabled="markingAll"
              @click="markAll"
            >
              {{ markingAll ? "Marcando…" : "Marcar leídas" }}
            </button>

            <button
              class="notifications-dropdown__refresh"
              :class="{ 'is-loading': loadingRecent }"
              type="button"
              :disabled="loadingRecent"
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
          </div>
        </header>

        <div class="notifications-dropdown__body">
          <div
            v-if="loadingRecent && !previewItems.length"
            class="notifications-dropdown__state"
          >
            <span class="notifications-dropdown__spinner"></span>
            <span>Cargando…</span>
          </div>

          <div
            v-else-if="errorRecent && !previewItems.length"
            class="notifications-dropdown__state is-error"
          >
            <strong>No se pudieron cargar.</strong>
            <span>{{ errorRecent }}</span>
            <button type="button" @click="refresh">
              Reintentar
            </button>
          </div>

          <div
            v-else-if="!previewItems.length"
            class="notifications-dropdown__state"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-5v-5a7 7 0 0 0-14 0v5l-2 2h18l-2-2Zm-2 0H7v-5a5 5 0 0 1 10 0v5Z"
              />
            </svg>

            <strong>Todo al día</strong>
            <span>No tienes notificaciones recientes.</span>
          </div>

          <div
            v-else
            class="notifications-dropdown__list"
            aria-label="Notificaciones recientes"
          >
            <NotificacionItem
              v-for="notification in previewItems"
              :key="notification.id"
              :notification="notification"
              compact
              :disabled="actionId === Number(notification.id)"
              @open="openNotification"
            />
          </div>
        </div>

        <footer class="notifications-dropdown__foot">
          <button
            type="button"
            @click="goAll"
          >
            Ver todas
            <span aria-hidden="true">→</span>
          </button>
        </footer>
      </section>
    </Transition>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue";

import {
  storeToRefs,
} from "pinia";

import {
  useRouter,
} from "vue-router";

import {
  useNotificacionesStore,
} from "../../scripts/stores/notificacionesStore";

import NotificacionItem from "./NotificacionItem.vue";

const PREVIEW_LIMIT = 5;

const emit = defineEmits([
  "opened",
  "closed",
]);

const router = useRouter();

const notificationsStore =
  useNotificacionesStore();

const {
  recentItems,
  unreadCount,
  unreadLabel,
  loadingRecent,
  errorRecent,
  markingAll,
  actionId,
} = storeToRefs(
  notificationsStore
);

const open = ref(false);
const wrap = ref(null);
const trigger = ref(null);
const panel = ref(null);

const previewItems = computed(() => {
  const items = Array.isArray(
    recentItems.value
  )
    ? recentItems.value
    : [];

  return items.slice(
    0,
    PREVIEW_LIMIT
  );
});

const quickSubtitle = computed(() => {
  if (unreadCount.value > 0) {
    return `${unreadCount.value} sin leer`;
  }

  return "Todo al día";
});

const triggerTitle = computed(
  () =>
    unreadCount.value > 0
      ? `Notificaciones (${unreadCount.value} sin leer)`
      : "Notificaciones"
);

const refresh = async () => {
  await notificationsStore.loadRecent();
};

const show = async () => {
  open.value = true;

  emit("opened");

  await notificationsStore.loadRecent();

  await nextTick();

  panel.value?.focus?.();
};

const close = (
  restoreFocus = false
) => {
  if (!open.value) {
    return;
  }

  open.value = false;

  emit("closed");

  if (restoreFocus) {
    nextTick(() =>
      trigger.value?.focus?.()
    );
  }
};

const toggle = async () => {
  if (open.value) {
    close(true);
    return;
  }

  await show();
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

  close(false);

  /*
    La campana funciona únicamente como vista rápida.
    El detalle completo continúa en /notificaciones.
  */
  await router.push(
    "/notificaciones"
  );
};

const goAll = async () => {
  close(false);

  if (
    router.currentRoute.value.path !==
    "/notificaciones"
  ) {
    await router.push(
      "/notificaciones"
    );
  }
};

const onDocumentClick = (
  event
) => {
  if (
    open.value &&
    wrap.value &&
    !wrap.value.contains(
      event.target
    )
  ) {
    close(false);
  }
};

const onEscape = (
  event
) => {
  if (
    event.key === "Escape" &&
    open.value
  ) {
    close(true);
  }
};

onMounted(() => {
  document.addEventListener(
    "click",
    onDocumentClick
  );

  document.addEventListener(
    "keydown",
    onEscape
  );
});

onBeforeUnmount(() => {
  document.removeEventListener(
    "click",
    onDocumentClick
  );

  document.removeEventListener(
    "keydown",
    onEscape
  );
});

defineExpose({
  close,
  refresh,
});
</script>

<style scoped>
.notifications-dropdown {
  position: relative;
}

.notifications-dropdown__trigger {
  position: relative;
}

.notifications-dropdown__trigger.has-unread {
  color:
    var(--color-primary, #1d4ed8);
}

.notifications-dropdown__badge {
  position: absolute;

  top: -4px;
  right: -5px;

  min-width: 18px;
  height: 18px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  padding: 0 5px;

  border:
    2px solid
    var(--bg-navbar, #ffffff);

  border-radius: 999px;

  background:
    var(--danger, #b42318);

  color:
    var(--danger-contrast, #ffffff);

  font-size: 0.62rem;
  font-weight: 800;
  line-height: 1;
}

.notifications-dropdown__panel {
  position: absolute;

  z-index: 1250;

  top: calc(100% + 10px);
  right: 0;

  width:
    min(
      440px,
      calc(100vw - 24px)
    );

  max-height:
    min(
      560px,
      calc(100dvh - var(--sgpc-nav-offset, 66px) - 22px)
    );

  display: grid;
  grid-template-rows:
    auto
    minmax(0, 1fr)
    auto;

  overflow: hidden;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 82%,
      transparent
    );

  border-radius: 14px;

  background:
    var(--bg-card, #ffffff);

  box-shadow:
    0 18px 44px
    rgba(15, 23, 42, 0.16);
}

.notifications-dropdown__head {
  min-height: 62px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 12px;

  padding: 11px 12px 11px 15px;

  border-bottom:
    1px solid
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 62%,
      transparent
    );
}

.notifications-dropdown__head-copy {
  min-width: 0;

  display: grid;
  gap: 2px;
}

.notifications-dropdown__head strong {
  color:
    var(--text-primary, #172033);

  font-size: 0.9rem;
  font-weight: 760;
  line-height: 1.3;
}

.notifications-dropdown__head small {
  overflow: hidden;

  color:
    var(--text-secondary, #667085);

  font-size: 0.67rem;
  font-weight: 520;
  line-height: 1.35;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.notifications-dropdown__head-actions {
  flex: 0 0 auto;

  display: flex;
  align-items: center;
  justify-content: flex-end;

  gap: 5px;
}

.notifications-dropdown__head-actions button {
  appearance: none;

  font: inherit;

  cursor: pointer;

  transition:
    background 140ms ease,
    border-color 140ms ease,
    color 140ms ease;
}

.notifications-dropdown__mark-all {
  min-height: 34px;

  padding: 0 8px;

  border: 1px solid transparent;
  border-radius: 8px;

  background: transparent;

  color:
    var(
      --link,
      var(--color-primary, #1d4ed8)
    );

  font-size: 0.65rem !important;
  font-weight: 720 !important;
}

.notifications-dropdown__refresh {
  width: 34px;
  min-width: 34px;
  height: 34px;
  min-height: 34px;

  display: grid;
  place-items: center;

  padding: 0;

  border: 1px solid transparent;
  border-radius: 8px;

  background: transparent;

  color:
    var(--text-secondary, #667085);
}

.notifications-dropdown__refresh svg {
  width: 15px;
  height: 15px;
}

.notifications-dropdown__head-actions
  button:hover:not(:disabled) {
  border-color:
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 76%,
      transparent
    );

  background:
    var(--bg-soft, #f5f7fb);

  color:
    var(--text-primary, #172033);
}

.notifications-dropdown__mark-all:hover:not(:disabled) {
  color:
    var(
      --link,
      var(--color-primary, #1d4ed8)
    ) !important;
}

.notifications-dropdown__head-actions
  button:focus-visible,
.notifications-dropdown__state button:focus-visible,
.notifications-dropdown__foot button:focus-visible {
  outline: none;

  box-shadow:
    0 0 0 3px
    color-mix(
      in srgb,
      var(--color-primary, #1d4ed8) 16%,
      transparent
    );
}

.notifications-dropdown__head-actions
  button:disabled {
  opacity: 0.5;
  cursor: wait;
}

.notifications-dropdown__refresh.is-loading svg {
  animation:
    notification-spin
    0.8s
    linear
    infinite;
}

.notifications-dropdown__body {
  min-height: 112px;

  overflow-y: auto;
  overscroll-behavior: contain;

  scrollbar-width: thin;
  scrollbar-color:
    color-mix(
      in srgb,
      var(--text-secondary, #667085) 50%,
      transparent
    )
    transparent;
}

.notifications-dropdown__body::-webkit-scrollbar {
  width: 7px;
}

.notifications-dropdown__body::-webkit-scrollbar-track {
  background: transparent;
}

.notifications-dropdown__body::-webkit-scrollbar-thumb {
  border: 2px solid transparent;
  border-radius: 999px;

  background:
    color-mix(
      in srgb,
      var(--text-secondary, #667085) 42%,
      transparent
    );

  background-clip: padding-box;
}

.notifications-dropdown__list {
  display: grid;
}

.notifications-dropdown__list
  :deep(.notification-item) {
  border-bottom-color:
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 54%,
      transparent
    );
}

.notifications-dropdown__state {
  min-height: 166px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  gap: 7px;

  padding: 22px;

  color:
    var(--text-secondary, #667085);

  text-align: center;
}

.notifications-dropdown__state > svg {
  width: 30px;
  height: 30px;

  color:
    var(--text-disabled, #98a2b3);
}

.notifications-dropdown__state strong {
  color:
    var(--text-primary, #172033);

  font-size: 0.78rem;
}

.notifications-dropdown__state span {
  max-width: 260px;

  font-size: 0.67rem;
  line-height: 1.45;
}

.notifications-dropdown__state button {
  min-height: 36px;

  margin-top: 3px;
  padding: 0 10px;

  border:
    1px solid
    var(--border-color, #d9e0e8);

  border-radius: 8px;

  background:
    var(--bg-card, #ffffff);

  color:
    var(--text-primary, #172033);

  font: inherit;
  font-size: 0.67rem;

  cursor: pointer;
}

.notifications-dropdown__state.is-error {
  color:
    var(--danger, #b42318);
}

.notifications-dropdown__spinner {
  width: 23px;
  height: 23px;

  border:
    2px solid
    var(--border-color, #d9e0e8);

  border-top-color:
    var(--color-primary, #1d4ed8);

  border-radius: 50%;

  animation:
    notification-spin
    0.8s
    linear
    infinite;
}

.notifications-dropdown__foot {
  position: sticky;
  bottom: 0;

  padding: 6px 9px;

  border-top:
    1px solid
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 62%,
      transparent
    );

  background:
    var(--bg-card, #ffffff);
}

.notifications-dropdown__foot button {
  appearance: none;

  width: 100%;
  min-height: 38px;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 6px;

  border: 0;
  border-radius: 8px;

  background: transparent;

  color:
    var(
      --link,
      var(--color-primary, #1d4ed8)
    );

  font: inherit;
  font-size: 0.69rem;
  font-weight: 740;

  cursor: pointer;

  transition:
    background 140ms ease,
    color 140ms ease;
}

.notifications-dropdown__foot button:hover {
  background:
    var(--bg-soft, #f5f7fb);
}

.notification-panel-enter-active,
.notification-panel-leave-active {
  transition:
    opacity 140ms ease,
    transform 140ms ease;
}

.notification-panel-enter-from,
.notification-panel-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

@keyframes notification-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 620px) {
  .notifications-dropdown__panel {
    position: fixed;

    top:
      calc(
        var(--sgpc-nav-offset, 66px)
        + 6px
      );

    right: 10px;
    left: 10px;

    width: auto;

    max-height:
      calc(
        100dvh
        - var(--sgpc-nav-offset, 66px)
        - 16px
      );
  }

  .notifications-dropdown__head {
    min-height: 60px;

    align-items: center;

    padding-left: 13px;
  }

  .notifications-dropdown__mark-all {
    max-width: 94px;

    overflow: hidden;

    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

@media (max-width: 420px) {
  .notifications-dropdown__mark-all {
    display: none;
  }
}

@media (pointer: coarse) {
  .notifications-dropdown__refresh {
    width: 38px;
    min-width: 38px;
    height: 38px;
    min-height: 38px;
  }

  .notifications-dropdown__mark-all,
  .notifications-dropdown__state button,
  .notifications-dropdown__foot button {
    min-height: 42px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .notification-panel-enter-active,
  .notification-panel-leave-active,
  .notifications-dropdown__head-actions button,
  .notifications-dropdown__foot button {
    transition: none;
  }

  .notifications-dropdown__spinner,
  .notifications-dropdown__refresh.is-loading svg {
    animation: none;
  }
}
</style>
