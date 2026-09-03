<template>
  <div
    class="notification-live-host"
    aria-live="polite"
    aria-atomic="true"
  >
    <Transition name="notification-live">
      <article
        v-if="visibleNotification"
        :key="toastKey"
        class="notification-live-toast"
        :data-tone="tone"
        role="status"
      >
        <span
          class="notification-live-toast__icon"
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 24 24"
            focusable="false"
          >
            <path
              fill="currentColor"
              :d="iconPath"
            />
          </svg>
        </span>

        <div class="notification-live-toast__content">
          <div
            v-if="dateLabel"
            class="notification-live-toast__topline"
          >
            <time
              :datetime="visibleNotification.created_at || undefined"
            >
              {{ dateLabel }}
            </time>
          </div>

          <strong class="notification-live-toast__title">
            {{ presentation.title }}
          </strong>

          <p class="notification-live-toast__message">
            {{ presentation.message }}
          </p>

          <div class="notification-live-toast__actions">
            <button
              class="notification-live-toast__action"
              type="button"
              @click="openNotification"
            >
              {{ actionLabel }}
            </button>

            <button
              class="notification-live-toast__dismiss"
              type="button"
              aria-label="Cerrar notificación"
              title="Cerrar"
              @click="dismiss"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="m6.4 5 5.6 5.6L17.6 5 19 6.4 13.4 12l5.6 5.6-1.4 1.4-5.6-5.6L6.4 19 5 17.6l5.6-5.6L5 6.4 6.4 5Z"
                />
              </svg>
            </button>
          </div>
        </div>
      </article>
    </Transition>
  </div>
</template>

<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { storeToRefs } from "pinia";
import { useRouter } from "vue-router";

import { useUserStore } from "../../scripts/stores/userStore";
import { useNotificacionesStore } from "../../scripts/stores/notificacionesStore";
import {
  formatNotificationDate,
  notificationIconPath,
  notificationPresentation,
  notificationTone,
} from "../notificacionesUtils";

const TOAST_DURATION_MS = 8_000;

const router = useRouter();
const userStore = useUserStore();
const notificationsStore =
  useNotificacionesStore();

const {
  incomingNotification,
  incomingSequence,
} = storeToRefs(
  notificationsStore
);

const visibleNotification = ref(null);
const toastKey = ref(0);

let dismissTimer = null;

const authenticated = computed(() => {
  return Boolean(
    userStore.isAuthenticated
  );
});

const presentation = computed(() => {
  return notificationPresentation(
    visibleNotification.value || {}
  );
});

const tone = computed(() => {
  return notificationTone(
    visibleNotification.value?.tipo
  );
});

const iconPath = computed(() => {
  return notificationIconPath(
    visibleNotification.value?.tipo
  );
});

const dateLabel = computed(() => {
  return formatNotificationDate(
    visibleNotification.value
      ?.created_at
  );
});

const actionLabel = computed(() => "Ver notificación");

const clearDismissTimer = () => {
  if (!dismissTimer) {
    return;
  }

  window.clearTimeout(
    dismissTimer
  );
  dismissTimer = null;
};

const scheduleDismiss = () => {
  clearDismissTimer();

  dismissTimer = window.setTimeout(
    () => {
      dismiss();
    },
    TOAST_DURATION_MS
  );
};

const dismiss = () => {
  clearDismissTimer();
  visibleNotification.value = null;
  notificationsStore.clearIncoming();
};

const openNotification = async () => {
  const notification =
    visibleNotification.value;

  if (!notification) {
    return;
  }

  clearDismissTimer();

  try {
    if (!notification.leida) {
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

  visibleNotification.value = null;
  notificationsStore.clearIncoming();

  /*
    El aviso lleva a la bandeja sin abrir automáticamente
    ningún modal. El detalle se abre por una acción explícita
    sobre una notificación concreta.
  */
  await router.push("/notificaciones");
};

watch(
  () => authenticated.value,
  (isAuthenticated) => {
    if (isAuthenticated) {
      notificationsStore.startPolling();
      return;
    }

    dismiss();
    notificationsStore.resetLiveState({
      clearItems: true,
    });
  },
  {
    immediate: true,
  }
);

watch(
  () => router.currentRoute.value.path,
  (path) => {
    if (path === "/notificaciones") {
      dismiss();
    }
  }
);

watch(
  () => incomingSequence.value,
  () => {
    if (
      !authenticated.value ||
      !incomingNotification.value
    ) {
      return;
    }

    /*
      Si el usuario ya está dentro de la bandeja de Notificaciones,
      no superponemos un aviso emergente sobre la misma información.
    */
    if (
      router.currentRoute.value.path ===
      "/notificaciones"
    ) {
      visibleNotification.value = null;
      notificationsStore.clearIncoming();
      return;
    }

    visibleNotification.value = {
      ...incomingNotification.value,
    };
    toastKey.value += 1;
    scheduleDismiss();
  }
);

onMounted(() => {
  /*
    El host global es el único propietario del polling.
    El watcher inmediato de `authenticated` inicia o reinicia
    la sincronización cuando corresponde.
  */
  userStore.hydrate?.();
});

onBeforeUnmount(() => {
  clearDismissTimer();

  /*
    Al desmontarse el host global sí corresponde detener
    el polling y retirar sus listeners globales.
  */
  notificationsStore.stopPolling();
});
</script>

<style scoped>
.notification-live-host {
  position: fixed;

  top:
    calc(
      var(--sgpc-nav-offset, var(--nav-offset, 66px))
      + 14px
    );

  right: 16px;

  z-index:
    var(--z-toast, 1500);

  width:
    min(
      400px,
      calc(
        100vw
        - 28px
      )
    );

  pointer-events: none;
}

.notification-live-toast {
  --toast-tone:
    var(--color-primary, #1d4ed8);

  width: 100%;

  display: grid;

  grid-template-columns:
    38px
    minmax(0, 1fr);

  gap: 11px;

  padding: 13px;

  border:
    1px solid
    var(--border-color, #d9e0e8);

  border-radius: 12px;

  background:
    var(--bg-card, #ffffff);

  color:
    var(--text-primary, #172033);

  box-shadow:
    0
    14px
    34px
    rgba(
      15,
      23,
      42,
      0.14
    );

  pointer-events: auto;
}

.notification-live-toast[data-tone="success"] {
  --toast-tone:
    var(--success, #17803d);
}

.notification-live-toast[data-tone="warning"] {
  --toast-tone:
    var(--warning, #9a6700);
}

.notification-live-toast[data-tone="danger"] {
  --toast-tone:
    var(--danger, #b42318);
}

.notification-live-toast__icon {
  width: 38px;
  height: 38px;

  display: grid;
  place-items: center;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--toast-tone) 20%,
      var(--border-color, #d9e0e8)
    );

  border-radius: 9px;

  background:
    var(--bg-soft, #f5f7fb);

  color:
    var(--toast-tone);
}

.notification-live-toast__icon svg {
  width: 18px;
  height: 18px;
}

.notification-live-toast__content {
  min-width: 0;
}

.notification-live-toast__topline {
  display: flex;
  justify-content: flex-end;

  min-height: 15px;

  margin-bottom: 2px;
}

.notification-live-toast__topline time {
  color:
    var(--text-secondary, #667085);

  font-size: 0.64rem;
  font-weight: 500;
}

.notification-live-toast__eyebrow {
  display: none !important;
}

.notification-live-toast__title {
  display: block;

  margin: 0;

  color:
    var(--text-primary, #172033);

  font-size: 0.84rem;
  font-weight: 730;
  line-height: 1.35;
}

.notification-live-toast__message {
  margin: 4px 0 10px;

  color:
    var(--text-secondary, #667085);

  font-size: 0.74rem;
  line-height: 1.45;
}

.notification-live-toast__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 8px;
}

.notification-live-toast__action {
  appearance: none;

  min-height: 38px;

  padding: 0 11px;

  border:
    1px solid
    var(--toast-tone);

  border-radius: 8px;

  background:
    var(--toast-tone);

  color:
    var(--accent-contrast, #ffffff);

  font: inherit;
  font-size: 0.68rem;
  font-weight: 720;

  cursor: pointer;
}

.notification-live-toast__dismiss {
  appearance: none;

  width: 38px;
  height: 38px;

  display: grid;
  place-items: center;

  padding: 0;

  border:
    1px solid
    transparent;

  border-radius: 8px;

  background: transparent;

  color:
    var(--text-secondary, #667085);

  cursor: pointer;
}

.notification-live-toast__dismiss:hover {
  border-color:
    var(--border-color, #d9e0e8);

  background:
    var(--bg-soft, #f5f7fb);

  color:
    var(--text-primary, #172033);
}

.notification-live-toast__dismiss svg {
  width: 16px;
  height: 16px;
}

.notification-live-toast__action:focus-visible,
.notification-live-toast__dismiss:focus-visible {
  outline:
    2px solid
    var(--focus-outline, #2563eb);

  outline-offset: 2px;
}

.notification-live-enter-active,
.notification-live-leave-active {
  transition:
    opacity 160ms ease,
    transform 160ms ease;
}

.notification-live-enter-from,
.notification-live-leave-to {
  opacity: 0;

  transform:
    translateY(-6px);
}

@media (max-width: 640px) {
  .notification-live-host {
    top:
      calc(
        var(--sgpc-nav-offset, var(--nav-offset, 66px))
        + 10px
      );

    right: 10px;

    width:
      calc(
        100vw
        - 20px
      );
  }

  .notification-live-toast {
    grid-template-columns:
      34px
      minmax(0, 1fr);

    padding: 11px;
  }

  .notification-live-toast__icon {
    width: 34px;
    height: 34px;
  }
}

@media (pointer: coarse) {
  .notification-live-toast__action,
  .notification-live-toast__dismiss {
    min-height: 44px;
  }

  .notification-live-toast__dismiss {
    width: 44px;
    height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .notification-live-enter-active,
  .notification-live-leave-active {
    transition: none;
  }

  .notification-live-enter-from,
  .notification-live-leave-to {
    transform: none;
  }
}
</style>
