import api from "../api/axios";
import { isAdminUser as sharedIsAdminUser } from "./auth";

const SEEN_ONCE_PREFIX = "sgpc_uleam_avisos_seen_once";
const SEEN_VERSION_PREFIX = "sgpc_uleam_avisos_seen_version";

export const DEFAULT_AVISOS_CONTENT = Object.freeze({
  eyebrow: "SGPC ULEAM",
  title: "Novedades institucionales",
  text: "Se detectó una actualización en los avisos del sistema. Revise la información antes de continuar.",
  recentLabel: "Actualización reciente",
});

export const DEFAULT_AVISOS_LAYOUT = Object.freeze({
  stageWidth: 1260,
  stageHeight: 640,
  mediaPaneWidth: 806,
  displayMode: "mixed",
});

const STAGE_WIDTH_MIN = 900;
const STAGE_WIDTH_MAX = 1500;
const STAGE_HEIGHT_MIN = 440;
const STAGE_HEIGHT_MAX = 900;
const MEDIA_PANE_WIDTH_MIN = 420;
const ASIDE_WIDTH_MIN = 320;
const SPLITTER_WIDTH = 14;

const DISPLAY_MODE_DEFAULT = "mixed";
const DISPLAY_MODE_ALLOWED = new Set(["mixed", "banner", "text"]);

let avisosConfigCache = {
  ...DEFAULT_AVISOS_CONTENT,
  ...DEFAULT_AVISOS_LAYOUT,
};

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

const safeInt = (value, fallback) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.round(parsed) : Math.round(fallback);
};

const pickFirst = (...values) => {
  for (const value of values) {
    if (value !== undefined && value !== null) return value;
  }
  return undefined;
};

const getMediaPaneWidthMax = (stageWidth) => {
  return Math.max(
    MEDIA_PANE_WIDTH_MIN,
    safeInt(stageWidth, DEFAULT_AVISOS_LAYOUT.stageWidth) -
      ASIDE_WIDTH_MIN -
      SPLITTER_WIDTH
  );
};

const normalizeSingleLine = (value, fallback) => {
  const normalized = String(value ?? "")
    .replace(/\s+/g, " ")
    .trim();

  return normalized || fallback;
};

const normalizeMultiLine = (value, fallback) => {
  const normalized = String(value ?? "")
    .replace(/\r\n/g, "\n")
    .trim();

  return normalized || fallback;
};

const normalizeDisplayMode = (value) => {
  const normalized = String(value ?? "")
    .trim()
    .toLowerCase();

  return DISPLAY_MODE_ALLOWED.has(normalized)
    ? normalized
    : DISPLAY_MODE_DEFAULT;
};

const normalizeAvisosConfig = (value = {}) => {
  const stageWidth = clamp(
    safeInt(
      pickFirst(value?.stageWidth, value?.stage_width),
      DEFAULT_AVISOS_LAYOUT.stageWidth
    ),
    STAGE_WIDTH_MIN,
    STAGE_WIDTH_MAX
  );

  const stageHeight = clamp(
    safeInt(
      pickFirst(value?.stageHeight, value?.stage_height),
      DEFAULT_AVISOS_LAYOUT.stageHeight
    ),
    STAGE_HEIGHT_MIN,
    STAGE_HEIGHT_MAX
  );

  const mediaPaneWidth = clamp(
    safeInt(
      pickFirst(value?.mediaPaneWidth, value?.media_pane_width),
      DEFAULT_AVISOS_LAYOUT.mediaPaneWidth
    ),
    MEDIA_PANE_WIDTH_MIN,
    getMediaPaneWidthMax(stageWidth)
  );

  const displayMode = normalizeDisplayMode(
    pickFirst(value?.displayMode, value?.display_mode)
  );

  return {
    eyebrow: normalizeSingleLine(
      value?.eyebrow,
      DEFAULT_AVISOS_CONTENT.eyebrow
    ),
    title: normalizeSingleLine(value?.title, DEFAULT_AVISOS_CONTENT.title),
    text: normalizeMultiLine(value?.text, DEFAULT_AVISOS_CONTENT.text),
    recentLabel: normalizeSingleLine(
      pickFirst(value?.recentLabel, value?.recent_label),
      DEFAULT_AVISOS_CONTENT.recentLabel
    ),
    stageWidth,
    stageHeight,
    mediaPaneWidth,
    displayMode,
  };
};

const setAvisosConfigCache = (value = {}) => {
  avisosConfigCache = normalizeAvisosConfig(value);
  return { ...avisosConfigCache };
};

const hasOwn = (obj, key) => Object.prototype.hasOwnProperty.call(obj || {}, key);

const buildConfigPatchPayload = (value = {}) => {
  const input = value && typeof value === "object" ? value : {};

  const normalized = normalizeAvisosConfig({
    ...avisosConfigCache,
    ...input,
  });

  const payload = {};

  if (hasOwn(input, "eyebrow")) payload.eyebrow = normalized.eyebrow;
  if (hasOwn(input, "title")) payload.title = normalized.title;
  if (hasOwn(input, "text")) payload.text = normalized.text;

  if (hasOwn(input, "recentLabel") || hasOwn(input, "recent_label")) {
    payload.recentLabel = normalized.recentLabel;
  }

  if (hasOwn(input, "stageWidth") || hasOwn(input, "stage_width")) {
    payload.stageWidth = normalized.stageWidth;
  }

  if (hasOwn(input, "stageHeight") || hasOwn(input, "stage_height")) {
    payload.stageHeight = normalized.stageHeight;
  }

  if (hasOwn(input, "mediaPaneWidth") || hasOwn(input, "media_pane_width")) {
    payload.mediaPaneWidth = normalized.mediaPaneWidth;
  }

  if (hasOwn(input, "displayMode") || hasOwn(input, "display_mode")) {
    payload.displayMode = normalized.displayMode;
  }

  if (!Object.keys(payload).length) {
    payload.eyebrow = normalized.eyebrow;
    payload.title = normalized.title;
    payload.text = normalized.text;
    payload.recentLabel = normalized.recentLabel;
    payload.stageWidth = normalized.stageWidth;
    payload.stageHeight = normalized.stageHeight;
    payload.mediaPaneWidth = normalized.mediaPaneWidth;
    payload.displayMode = normalized.displayMode;
  }

  return payload;
};

const buildContentPatchPayload = (value = {}) => {
  const normalized = normalizeAvisosConfig({
    ...avisosConfigCache,
    ...value,
  });

  return {
    eyebrow: normalized.eyebrow,
    title: normalized.title,
    text: normalized.text,
    recentLabel: normalized.recentLabel,
  };
};

const buildLayoutPatchPayload = (value = {}) => {
  const normalized = normalizeAvisosConfig({
    ...avisosConfigCache,
    ...value,
  });

  return {
    stageWidth: normalized.stageWidth,
    stageHeight: normalized.stageHeight,
    mediaPaneWidth: normalized.mediaPaneWidth,
    displayMode: normalized.displayMode,
  };
};

const resolveUserKey = (user) => {
  if (user?.id) return String(user.id);
  if (user?.email) return String(user.email).toLowerCase();
  return "anonymous";
};

const getSeenOnceKey = (user) => `${SEEN_ONCE_PREFIX}:${resolveUserKey(user)}`;
const getSeenVersionKey = (user) =>
  `${SEEN_VERSION_PREFIX}:${resolveUserKey(user)}`;

const normalizeStatus = (data) => {
  const generalVersion = String(
    pickFirst(data?.version, data?.general_version, "") || ""
  );

  const notifyVersion = String(
    pickFirst(
      data?.notify_version,
      data?.notification_version,
      data?.content_version,
      data?.avisos_version,
      data?.version,
      ""
    ) || ""
  );

  return {
    hasItems: Boolean(pickFirst(data?.has_items, data?.hasItems, false)),
    total: Number(pickFirst(data?.total, 0) || 0),

    // Versión general. Puede cambiar por layout/diseño.
    version: generalVersion,

    // Versión notificable. Solo debe cambiar por imagen o texto de aviso.
    notifyVersion,
  };
};

const is503 = (error) => Number(error?.response?.status) === 503;

const getNoCacheConfig = () => {
  return {
    params: {
      _ts: Date.now(),
    },
  };
};

export const getAvisosCombinedVersion = (baseVersion = "") => {
  return String(baseVersion || "");
};

export const isAdminUser = (user) => sharedIsAdminUser(user);

export const getAvisosContent = () => {
  return {
    eyebrow: avisosConfigCache.eyebrow,
    title: avisosConfigCache.title,
    text: avisosConfigCache.text,
    recentLabel: avisosConfigCache.recentLabel,
  };
};

export const getAvisosLayout = () => {
  return {
    stageWidth: avisosConfigCache.stageWidth,
    stageHeight: avisosConfigCache.stageHeight,
    mediaPaneWidth: avisosConfigCache.mediaPaneWidth,
    displayMode: avisosConfigCache.displayMode,
  };
};

export const getAvisosConfigCached = () => {
  return { ...avisosConfigCache };
};

export const hydrateAvisosConfig = async () => {
  try {
    const { data } = await api.get("banners/config/", getNoCacheConfig());
    return setAvisosConfigCache(data);
  } catch (error) {
    if (is503(error)) {
      return setAvisosConfigCache({
        ...DEFAULT_AVISOS_CONTENT,
        ...DEFAULT_AVISOS_LAYOUT,
      });
    }

    throw error;
  }
};

export const saveAvisosConfig = async (value = {}) => {
  const payload = buildConfigPatchPayload(value);
  const { data } = await api.patch("banners/config/", payload);
  return setAvisosConfigCache(data);
};

export const saveAvisosContent = async (value = {}) => {
  const payload = buildContentPatchPayload(value);
  const { data } = await api.patch("banners/config/", payload);
  return setAvisosConfigCache(data);
};

export const saveAvisosLayout = async (value = {}) => {
  const payload = buildLayoutPatchPayload(value);
  const { data } = await api.patch("banners/config/", payload);
  return setAvisosConfigCache(data);
};

export const resetAvisosContent = async () => {
  return saveAvisosContent(DEFAULT_AVISOS_CONTENT);
};

export const resetAvisosLayout = async () => {
  return saveAvisosLayout(DEFAULT_AVISOS_LAYOUT);
};

export const getAvisosStatus = async () => {
  const { data } = await api.get("banners/status/", getNoCacheConfig());
  return normalizeStatus(data);
};

export const shouldOpenAvisos = async (user, providedStatus = null) => {
  const status = providedStatus || (await getAvisosStatus());

  if (!status.hasItems) {
    return false;
  }

  const seenOnce = localStorage.getItem(getSeenOnceKey(user)) === "1";
  const seenVersion = localStorage.getItem(getSeenVersionKey(user)) || "";
  const currentNotifyVersion = status.notifyVersion || status.version || "";

  if (!seenOnce) {
    return true;
  }

  if (currentNotifyVersion && seenVersion !== currentNotifyVersion) {
    return true;
  }

  return false;
};

export const markAvisosAsSeen = (user, versionOrStatus = "") => {
  localStorage.setItem(getSeenOnceKey(user), "1");

  const version =
    typeof versionOrStatus === "object"
      ? versionOrStatus?.notifyVersion || versionOrStatus?.version || ""
      : versionOrStatus;

  if (version) {
    localStorage.setItem(getSeenVersionKey(user), String(version));
  }
};

export const clearAvisosSeenState = (user) => {
  localStorage.removeItem(getSeenOnceKey(user));
  localStorage.removeItem(getSeenVersionKey(user));
};