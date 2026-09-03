import { defineStore } from "pinia";

import {
  listarNotificaciones,
  marcarNotificacionLeida,
  marcarTodasNotificacionesLeidas,
  obtenerResumenNotificaciones,
} from "../api/notificacionesApi";

import {
  installNotificationSoundUnlock,
  playNotificationSound,
} from "../utils/notificationSound";

const SOUND_STORAGE_KEY =
  "sgpc-notifications-sound-enabled";
const SOUND_VOLUME_STORAGE_KEY =
  "sgpc-notifications-sound-volume";

/*
 * Se consulta únicamente un resumen ligero en cada ciclo.
 * La lista reciente solo se vuelve a pedir cuando cambia el contador,
 * al iniciar el host o cuando el usuario la solicita expresamente.
 */
const REFRESH_INTERVAL_MS = 10_000;
const RECENT_LIMIT = 12;
const DEFAULT_SOUND_VOLUME = 0.82;

const clamp = (
  value,
  min,
  max
) => Math.min(
  max,
  Math.max(min, value)
);

const readStoredBoolean = (
  key,
  fallback
) => {
  if (typeof window === "undefined") {
    return fallback;
  }

  const value =
    window.localStorage.getItem(
      key
    );

  if (value === null) {
    return fallback;
  }

  return value !== "false";
};

const persistBoolean = (
  key,
  value
) => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(
    key,
    value ? "true" : "false"
  );
};

const readStoredNumber = (
  key,
  fallback
) => {
  if (typeof window === "undefined") {
    return fallback;
  }

  const raw = Number(
    window.localStorage.getItem(key)
  );

  return Number.isFinite(raw)
    ? raw
    : fallback;
};

const persistNumber = (
  key,
  value
) => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(
    key,
    String(value)
  );
};

const extractItems = (
  payload
) => {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
};

const extractTotal = (
  payload,
  fallback = 0
) => {
  const raw =
    payload?.count ??
    payload?.total ??
    fallback;

  const parsed = Number(raw);

  return Number.isFinite(parsed)
    ? parsed
    : fallback;
};

const notificationId = (
  notification
) => {
  const id = Number(
    notification?.id
  );

  return Number.isInteger(id) && id > 0
    ? id
    : null;
};

const buildIdSet = (
  items = []
) => new Set(
  items
    .map(notificationId)
    .filter(Boolean)
);

const findIncomingNotification = (
  items,
  previousIds
) => {
  const normalized = Array.isArray(items)
    ? items
    : [];

  return (
    normalized.find((item) => {
      const id = notificationId(item);

      return (
        id &&
        !item?.leida &&
        !previousIds.has(id)
      );
    }) ||
    normalized.find(
      (item) => !item?.leida
    ) ||
    null
  );
};

const TECHNICAL_ERROR_PATTERN =
  /(?:backend|endpoint|serializer|queryset|jwt|token|sql|postgres|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|stack|http\s*\d{3}|request\b|response\b)/i;

const safeErrorText = (
  value
) => {
  const text =
    typeof value === "string"
      ? value.trim()
      : "";

  if (
    !text ||
    TECHNICAL_ERROR_PATTERN.test(text)
  ) {
    return "";
  }

  return text;
};

const normalizeError = (
  error,
  fallback
) => {
  const status = Number(
    error?.response?.status
  );

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para consultar las notificaciones.";
  }

  if (status === 429) {
    return "Se realizaron demasiadas solicitudes. Intente nuevamente en unos minutos.";
  }

  if (status >= 500) {
    return fallback;
  }

  const payload =
    error?.response?.data;

  const candidates = [
    typeof payload === "string"
      ? payload
      : "",
    payload?.detail,
    payload?.message,
  ];

  for (const candidate of candidates) {
    const safe =
      safeErrorText(candidate);

    if (safe) {
      return safe;
    }
  }

  return fallback;
};

export const useNotificacionesStore =
  defineStore(
    "notificaciones",
    {
      state: () => ({
        recentItems: [],
        items: [],

        total: 0,
        unreadCount: 0,

        loadingRecent: false,
        loadingList: false,
        loadingMore: false,
        markingAll: false,
        actionId: null,

        errorRecent: "",
        errorList: "",

        page: 1,
        hasMore: false,

        soundEnabled:
          readStoredBoolean(
            SOUND_STORAGE_KEY,
            true
          ),

        soundVolume:
          clamp(
            readStoredNumber(
              SOUND_VOLUME_STORAGE_KEY,
              DEFAULT_SOUND_VOLUME
            ),
            0,
            1
          ),

        summaryInitialized: false,
        lastUnreadCount: null,

        /*
         * La notificación entrante alimenta el aviso emergente global.
         * `incomingSequence` permite detectar dos eventos consecutivos
         * aunque tengan el mismo contenido visible.
         */
        incomingNotification: null,
        incomingSequence: 0,

        pollingTimer: null,
        pollingInFlight: false,
        visibilityHandler: null,
        focusHandler: null,
      }),

      getters: {
        unreadLabel: (
          state
        ) => (
          state.unreadCount > 99
            ? "99+"
            : String(
                state.unreadCount
              )
        ),

        panelSubtitle: (
          state
        ) => {
          if (state.unreadCount > 0) {
            return `${state.unreadCount} sin leer · ${state.total} recientes`;
          }

          if (state.total > 0) {
            return `${state.total} recientes · Todas leídas`;
          }

          return "Sin novedades";
        },

        soundVolumePercent: (
          state
        ) => Math.round(
          state.soundVolume * 100
        ),
      },

      actions: {
        setSoundEnabled(
          value
        ) {
          this.soundEnabled =
            Boolean(value);

          persistBoolean(
            SOUND_STORAGE_KEY,
            this.soundEnabled
          );
        },

        setSoundVolume(
          value
        ) {
          const normalized = clamp(
            Number(value),
            0,
            1
          );

          this.soundVolume =
            Number.isFinite(normalized)
              ? normalized
              : DEFAULT_SOUND_VOLUME;

          persistNumber(
            SOUND_VOLUME_STORAGE_KEY,
            this.soundVolume
          );
        },

        resetPreferences() {
          this.setSoundEnabled(true);
          this.setSoundVolume(
            DEFAULT_SOUND_VOLUME
          );
        },

        async testSound() {
          installNotificationSoundUnlock();

          return playNotificationSound({
            force: true,
            volume: this.soundVolume,
          });
        },

        publishIncoming(
          notification
        ) {
          if (!notification) {
            return;
          }

          this.incomingNotification =
            notification;
          this.incomingSequence += 1;
        },

        clearIncoming() {
          this.incomingNotification = null;
        },

        async refreshSummary({
          notify = true,
        } = {}) {
          try {
            const summary =
              await obtenerResumenNotificaciones();

            const nextUnread = Math.max(
              0,
              Number(
                summary?.no_leidas || 0
              )
            );

            const nextTotal = Math.max(
              0,
              Number(
                summary?.total || 0
              )
            );

            const previousUnread =
              this.lastUnreadCount;
            const wasInitialized =
              this.summaryInitialized;

            const increased = Boolean(
              wasInitialized &&
              previousUnread !== null &&
              nextUnread > previousUnread
            );

            this.unreadCount =
              nextUnread;
            this.total = nextTotal;
            this.lastUnreadCount =
              nextUnread;
            this.summaryInitialized = true;

            if (
              increased &&
              notify &&
              this.soundEnabled
            ) {
              await playNotificationSound({
                volume: this.soundVolume,
              });
            }

            return {
              ...summary,
              increased,
              wasInitialized,
            };
          } catch (error) {
            console.warn(
              "No fue posible actualizar el resumen de notificaciones.",
              error
            );

            return null;
          }
        },

        async loadRecent({
          silent = false,
          syncSummary = true,
          notify = false,
        } = {}) {
          if (!silent) {
            this.loadingRecent = true;
          }

          this.errorRecent = "";

          try {
            const previousIds =
              buildIdSet(
                this.recentItems
              );

            const payload =
              await listarNotificaciones({
                page_size:
                  RECENT_LIMIT,
              });

            this.recentItems =
              extractItems(payload).slice(
                0,
                RECENT_LIMIT
              );

            this.total = Math.max(
              this.total,
              extractTotal(
                payload,
                this.recentItems.length
              )
            );

            if (syncSummary) {
              const summary =
                await this.refreshSummary({
                  notify: false,
                });

              if (summary?.increased) {
                const incoming =
                  findIncomingNotification(
                    this.recentItems,
                    previousIds
                  );

                this.publishIncoming(
                  incoming
                );

                if (
                  notify &&
                  this.soundEnabled
                ) {
                  await playNotificationSound({
                    volume:
                      this.soundVolume,
                  });
                }
              }
            }

            return this.recentItems;
          } catch (error) {
            this.errorRecent =
              normalizeError(
                error,
                "No pudimos cargar las notificaciones. Intente nuevamente."
              );

            return [];
          } finally {
            if (!silent) {
              this.loadingRecent = false;
            }
          }
        },

        async syncLive({
          notify = true,
          forceRecent = false,
        } = {}) {
          if (this.pollingInFlight) {
            return null;
          }

          this.pollingInFlight = true;

          try {
            const previousIds =
              buildIdSet(
                this.recentItems
              );

            const summary =
              await this.refreshSummary({
                notify: false,
              });

            if (!summary) {
              return null;
            }

            const shouldRefreshRecent =
              forceRecent ||
              !this.recentItems.length ||
              summary.increased;

            if (shouldRefreshRecent) {
              await this.loadRecent({
                silent: true,
                syncSummary: false,
              });
            }

            if (summary.increased) {
              const incoming =
                findIncomingNotification(
                  this.recentItems,
                  previousIds
                );

              this.publishIncoming(
                incoming
              );

              if (
                notify &&
                this.soundEnabled
              ) {
                await playNotificationSound({
                  volume:
                    this.soundVolume,
                });
              }
            }

            return summary;
          } finally {
            this.pollingInFlight = false;
          }
        },

        async loadList({
          reset = true,
        } = {}) {
          if (reset) {
            this.loadingList = true;
            this.page = 1;
            this.errorList = "";
          } else {
            this.loadingMore = true;
          }

          const targetPage = reset
            ? 1
            : this.page + 1;

          try {
            const payload =
              await listarNotificaciones({
                page: targetPage,
                page_size: 30,
              });

            const nextItems =
              extractItems(payload);

            this.items = reset
              ? nextItems
              : [
                  ...this.items,
                  ...nextItems.filter(
                    (candidate) =>
                      !this.items.some(
                        (current) =>
                          Number(
                            current?.id
                          ) ===
                          Number(
                            candidate?.id
                          )
                      )
                  ),
                ];

            this.page = targetPage;
            this.hasMore = Boolean(
              payload?.next
            );

            this.total = Math.max(
              this.total,
              extractTotal(
                payload,
                this.items.length
              )
            );

            await this.refreshSummary({
              notify: false,
            });

            return this.items;
          } catch (error) {
            this.errorList =
              normalizeError(
                error,
                "No pudimos cargar las notificaciones. Intente nuevamente."
              );

            return this.items;
          } finally {
            this.loadingList = false;
            this.loadingMore = false;
          }
        },

        async markRead(
          notification
        ) {
          const id = Number(
            notification?.id
          );

          if (
            !Number.isInteger(id) ||
            id < 1 ||
            notification?.leida
          ) {
            return notification;
          }

          this.actionId = id;

          try {
            const updated =
              await marcarNotificacionLeida(
                id
              );

            const applyUpdate = (
              item
            ) => (
              Number(item?.id) === id
                ? {
                    ...item,
                    ...(updated &&
                    typeof updated ===
                      "object"
                      ? updated
                      : {}),
                    leida: true,
                  }
                : item
            );

            this.recentItems =
              this.recentItems.map(
                applyUpdate
              );

            this.items =
              this.items.map(
                applyUpdate
              );

            this.unreadCount = Math.max(
              0,
              this.unreadCount - 1
            );

            this.lastUnreadCount =
              this.unreadCount;

            return updated || {
              ...notification,
              leida: true,
            };
          } finally {
            this.actionId = null;
          }
        },

        async markAllRead() {
          if (
            this.unreadCount < 1 ||
            this.markingAll
          ) {
            return null;
          }

          this.markingAll = true;

          try {
            const result =
              await marcarTodasNotificacionesLeidas();

            const mark = (
              item
            ) => ({
              ...item,
              leida: true,
            });

            this.recentItems =
              this.recentItems.map(mark);
            this.items =
              this.items.map(mark);
            this.unreadCount = 0;
            this.lastUnreadCount = 0;

            return result;
          } finally {
            this.markingAll = false;
          }
        },

        startPolling() {
          if (typeof window === "undefined") {
            return;
          }

          installNotificationSoundUnlock();

          if (this.pollingTimer) {
            return;
          }

          /*
           * La primera sincronización establece la línea base y carga
           * la campana sin reproducir sonidos de notificaciones antiguas.
           */
          this.syncLive({
            notify: false,
            forceRecent: true,
          });

          this.visibilityHandler = () => {
            if (
              document.visibilityState ===
              "visible"
            ) {
              this.syncLive({
                notify: true,
              });
            }
          };

          this.focusHandler = () => {
            this.syncLive({
              notify: true,
            });
          };

          document.addEventListener(
            "visibilitychange",
            this.visibilityHandler
          );
          window.addEventListener(
            "focus",
            this.focusHandler
          );

          this.pollingTimer =
            window.setInterval(
              () => {
                if (
                  typeof document !==
                    "undefined" &&
                  document.visibilityState !==
                    "visible"
                ) {
                  return;
                }

                this.syncLive({
                  notify: true,
                });
              },
              REFRESH_INTERVAL_MS
            );
        },

        stopPolling() {
          if (typeof window === "undefined") {
            return;
          }

          if (this.pollingTimer) {
            window.clearInterval(
              this.pollingTimer
            );
            this.pollingTimer = null;
          }

          if (this.visibilityHandler) {
            document.removeEventListener(
              "visibilitychange",
              this.visibilityHandler
            );
            this.visibilityHandler = null;
          }

          if (this.focusHandler) {
            window.removeEventListener(
              "focus",
              this.focusHandler
            );
            this.focusHandler = null;
          }
        },

        resetLiveState({
          clearItems = false,
        } = {}) {
          this.stopPolling();

          this.summaryInitialized = false;
          this.lastUnreadCount = null;
          this.incomingNotification = null;
          this.incomingSequence = 0;
          this.pollingInFlight = false;
          this.unreadCount = 0;
          this.total = 0;

          if (clearItems) {
            this.recentItems = [];
            this.items = [];
            this.page = 1;
            this.hasMore = false;
          }
        },
      },
    }
  );

export default useNotificacionesStore;
