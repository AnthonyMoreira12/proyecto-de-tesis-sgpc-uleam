<template>
  <button
    class="notification-item"
    :class="{
      'is-unread': !notification.leida,
      'is-compact': compact,
    }"
    :data-tone="tone"
    type="button"
    :disabled="disabled"
    @click="$emit('open', notification)"
  >
    <span
      class="notification-item__icon"
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

    <span class="notification-item__content">
      <span class="notification-item__headline">
        <strong>{{ title }}</strong>

        <time
          v-if="dateLabel"
          :datetime="notification.created_at || undefined"
        >
          {{ dateLabel }}
        </time>
      </span>

      <span class="notification-item__message">
        {{ message }}
      </span>
    </span>

    <span
      class="notification-item__rail"
      aria-hidden="true"
    >
      <span
        v-if="!notification.leida"
        class="notification-item__unread"
      ></span>

      <svg
        v-if="!compact"
        class="notification-item__chevron"
        viewBox="0 0 24 24"
        focusable="false"
      >
        <path
          fill="currentColor"
          d="m9.3 5.3 1.4-1.4 8.1 8.1-8.1 8.1-1.4-1.4 6.7-6.7-6.7-6.7Z"
        />
      </svg>
    </span>
  </button>
</template>

<script setup>
import {
  computed,
} from "vue";

import {
  formatNotificationDate,
  notificationIconPath,
  notificationPresentation,
  notificationTone,
  notificationTypeLabel,
} from "../notificacionesUtils";

const props = defineProps({
  notification: {
    type: Object,
    required: true,
  },

  compact: {
    type: Boolean,
    default: false,
  },

  disabled: {
    type: Boolean,
    default: false,
  },

  /*
   * El dropdown ya envía esta prop. Se conserva para evitar
   * que termine como atributo HTML no deseado sobre el botón.
   */
  actionLabel: {
    type: String,
    default: "",
  },
});

defineEmits([
  "open",
]);

const typeLabel = computed(
  () =>
    notificationTypeLabel(
      props.notification
    )
);

const presentation = computed(
  () =>
    notificationPresentation(
      props.notification
    )
);

const title = computed(
  () =>
    presentation.value.title ||
    props.notification.titulo ||
    typeLabel.value
);

const message = computed(
  () =>
    presentation.value.message ||
    props.notification.mensaje ||
    "Sin información adicional."
);

const dateLabel = computed(
  () =>
    formatNotificationDate(
      props.notification?.created_at
    )
);

const tone = computed(
  () =>
    notificationTone(
      props.notification?.tipo
    )
);

const iconPath = computed(
  () =>
    notificationIconPath(
      props.notification?.tipo
    )
);
</script>

<style scoped>
.notification-item,
.notification-item *,
.notification-item *::before,
.notification-item *::after {
  box-sizing: border-box;
}

.notification-item {
  --item-tone: var(--color-primary, #1d4ed8);

  appearance: none;
  position: relative;

  width: 100%;
  min-width: 0;

  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) 22px;
  align-items: start;
  gap: 13px;

  padding: 15px 16px;

  border: 0;
  border-bottom:
    1px solid
    color-mix(
      in srgb,
      var(--border-color, #d9e0e8) 78%,
      transparent
    );

  border-radius: 0;

  background: var(--bg-card, #ffffff);
  color: var(--text-primary, #172033);

  font: inherit;
  text-align: left;

  cursor: pointer;

  transition:
    background 150ms ease,
    box-shadow 150ms ease;
}

.notification-item::before {
  content: "";

  position: absolute;
  top: 11px;
  bottom: 11px;
  left: 0;

  width: 3px;

  border-radius: 0 999px 999px 0;

  background: var(--item-tone);

  opacity: 0;

  transition: opacity 150ms ease;
}

.notification-item:last-child {
  border-bottom: 0;
}

.notification-item[data-tone="success"] {
  --item-tone: var(--success, #17803d);
}

.notification-item[data-tone="warning"] {
  --item-tone: var(--warning, #9a6700);
}

.notification-item[data-tone="danger"] {
  --item-tone: var(--danger, #b42318);
}

.notification-item[data-tone="info"] {
  --item-tone:
    var(
      --color-primary-effective,
      var(--color-primary, #1d4ed8)
    );
}

.notification-item.is-unread {
  background:
    color-mix(
      in srgb,
      var(--item-tone) 4.5%,
      var(--bg-card, #ffffff)
    );
}

.notification-item.is-unread::before {
  opacity: 1;
}

.notification-item:hover:not(:disabled) {
  background:
    color-mix(
      in srgb,
      var(--item-tone) 6%,
      var(--bg-card, #ffffff)
    );
}

.notification-item:focus-visible {
  z-index: 2;

  outline: 0;

  box-shadow:
    inset 0 0 0 2px
    color-mix(
      in srgb,
      var(--item-tone) 70%,
      transparent
    );
}

.notification-item:disabled {
  opacity: 0.58;
  cursor: progress;
}

.notification-item__icon {
  width: 40px;
  height: 40px;

  display: grid;
  place-items: center;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--item-tone) 18%,
      var(--border-color, #d9e0e8)
    );

  border-radius: 10px;

  background:
    color-mix(
      in srgb,
      var(--item-tone) 9%,
      var(--bg-card, #ffffff)
    );

  color: var(--item-tone);
}

.notification-item__icon svg {
  width: 18px;
  height: 18px;
}

.notification-item__content {
  min-width: 0;

  display: grid;
  gap: 5px;

  padding-top: 1px;
}

.notification-item__headline {
  min-width: 0;

  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.notification-item__headline strong {
  min-width: 0;

  overflow: hidden;

  color: var(--text-primary, #172033);

  font-size: 0.85rem;
  font-weight: 680;
  line-height: 1.38;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-item.is-unread
  .notification-item__headline strong {
  font-weight: 770;
}

.notification-item__headline time {
  flex: 0 0 auto;

  padding-top: 1px;

  color: var(--text-secondary, #667085);

  font-size: 0.66rem;
  font-weight: 560;
  line-height: 1.4;

  white-space: nowrap;
}

.notification-item__message {
  display: -webkit-box;

  max-width: 940px;

  overflow: hidden;

  color: var(--text-secondary, #667085);

  font-size: 0.75rem;
  font-weight: 470;
  line-height: 1.5;

  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.notification-item__rail {
  min-height: 40px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;

  color: var(--text-secondary, #667085);
}

.notification-item__unread {
  width: 7px;
  height: 7px;

  flex: 0 0 7px;

  border-radius: 999px;

  background: var(--item-tone);

  box-shadow:
    0 0 0 3px
    color-mix(
      in srgb,
      var(--item-tone) 11%,
      transparent
    );
}

.notification-item__chevron {
  width: 15px;
  height: 15px;

  opacity: 0.42;

  transition:
    opacity 150ms ease,
    transform 150ms ease,
    color 150ms ease;
}

.notification-item:hover:not(:disabled)
  .notification-item__chevron {
  color: var(--item-tone);
  opacity: 0.9;
  transform: translateX(2px);
}

.notification-item.is-compact {
  grid-template-columns: 32px minmax(0, 1fr) 12px;
  gap: 10px;

  padding: 11px 12px;
}

.notification-item.is-compact::before {
  top: 9px;
  bottom: 9px;

  width: 2px;
}

.is-compact .notification-item__icon {
  width: 32px;
  height: 32px;

  border-radius: 9px;
}

.is-compact .notification-item__icon svg {
  width: 15px;
  height: 15px;
}

.is-compact .notification-item__content {
  gap: 3px;

  padding-top: 0;
}

.is-compact .notification-item__headline {
  gap: 8px;
}

.is-compact .notification-item__headline strong {
  font-size: 0.78rem;
}

.is-compact .notification-item__headline time {
  font-size: 0.62rem;
}

.is-compact .notification-item__message {
  font-size: 0.7rem;
  line-height: 1.42;

  -webkit-line-clamp: 2;
}

.is-compact .notification-item__rail {
  min-height: 32px;
}

.is-compact .notification-item__unread {
  width: 6px;
  height: 6px;

  flex-basis: 6px;

  box-shadow: none;
}

@media (max-width: 620px) {
  .notification-item {
    grid-template-columns: 34px minmax(0, 1fr) 16px;
    gap: 10px;

    padding: 13px 12px;
  }

  .notification-item::before {
    top: 10px;
    bottom: 10px;
  }

  .notification-item__icon {
    width: 34px;
    height: 34px;

    border-radius: 9px;
  }

  .notification-item__icon svg {
    width: 16px;
    height: 16px;
  }

  .notification-item__headline {
    flex-direction: column;
    gap: 2px;
  }

  .notification-item__headline strong {
    display: -webkit-box;

    overflow: hidden;

    white-space: normal;

    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .notification-item__message {
    -webkit-line-clamp: 3;
  }

  .notification-item__rail {
    min-height: 34px;
  }

  .notification-item.is-compact {
    grid-template-columns: 30px minmax(0, 1fr) 10px;
    gap: 9px;

    padding: 10px 11px;
  }

  .is-compact .notification-item__icon {
    width: 30px;
    height: 30px;
  }

  .is-compact .notification-item__headline {
    flex-direction: row;
    align-items: flex-start;
    gap: 7px;
  }

  .is-compact .notification-item__headline strong {
    display: block;

    overflow: hidden;

    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .is-compact .notification-item__message {
    -webkit-line-clamp: 2;
  }
}

@media (prefers-reduced-motion: reduce) {
  .notification-item,
  .notification-item::before,
  .notification-item__chevron {
    transition: none;
  }
}
</style>
