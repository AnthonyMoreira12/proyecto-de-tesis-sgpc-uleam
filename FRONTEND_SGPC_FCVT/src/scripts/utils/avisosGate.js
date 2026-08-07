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
  displayMode: "banner",
});

export const AVISOS_TEXT_MAX_LENGTH = 700;

export const AVISOS_LAYOUT_LIMITS = Object.freeze({
  stageWidthMin: 900,
  stageWidthMax: 1500,
  stageHeightMin: 440,
  stageHeightMax: 900,
  mediaPaneWidthMin: 420,
  asideWidthMin: 320,
  splitterWidth: 0,
});

export const AVISOS_DISPLAY_MODES = Object.freeze([
  "banner",
]);

const STAGE_WIDTH_MIN = AVISOS_LAYOUT_LIMITS.stageWidthMin;
const STAGE_WIDTH_MAX = AVISOS_LAYOUT_LIMITS.stageWidthMax;
const STAGE_HEIGHT_MIN = AVISOS_LAYOUT_LIMITS.stageHeightMin;
const STAGE_HEIGHT_MAX = AVISOS_LAYOUT_LIMITS.stageHeightMax;
const MEDIA_PANE_WIDTH_MIN = AVISOS_LAYOUT_LIMITS.mediaPaneWidthMin;
const ASIDE_WIDTH_MIN = AVISOS_LAYOUT_LIMITS.asideWidthMin;
const SPLITTER_WIDTH = AVISOS_LAYOUT_LIMITS.splitterWidth;

const DISPLAY_MODE_DEFAULT = "banner";
const DISPLAY_MODE_ALLOWED = new Set(AVISOS_DISPLAY_MODES);

let avisosConfigCache = {
  ...DEFAULT_AVISOS_CONTENT,
  ...DEFAULT_AVISOS_LAYOUT,
};

const clamp = (value, min, max) => {
  return Math.min(
    max,
    Math.max(min, value)
  );
};

const safeInt = (
  value,
  fallback
) => {
  const parsed = Number(value);

  return Number.isFinite(parsed)
    ? Math.round(parsed)
    : Math.round(fallback);
};

const pickFirst = (...values) => {
  for (const value of values) {
    if (
      value !== undefined &&
      value !== null
    ) {
      return value;
    }
  }

  return undefined;
};

const getMediaPaneWidthMax = (
  stageWidth
) => {
  return Math.max(
    MEDIA_PANE_WIDTH_MIN,
    safeInt(
      stageWidth,
      DEFAULT_AVISOS_LAYOUT.stageWidth
    ) -
      ASIDE_WIDTH_MIN -
      SPLITTER_WIDTH
  );
};

const normalizeSingleLine = (
  value,
  fallback
) => {
  const normalized = String(
    value ?? ""
  )
    .replace(/\s+/g, " ")
    .trim();

  return normalized || fallback;
};

const normalizeMultiLine = (
  value,
  fallback
) => {
  const normalized = String(
    value ?? ""
  )
    .replace(/\r\n/g, "\n")
    .trim();

  return normalized || fallback;
};

const normalizeSingleLineForPayload = (
  value,
  maxLength
) => {
  const normalized = String(
    value ?? ""
  )
    .replace(/\s+/g, " ")
    .trim();

  if (
    normalized.length > maxLength
  ) {
    throw new RangeError(
      `El valor no puede superar los ${maxLength} caracteres.`
    );
  }

  return normalized;
};

const normalizeMultiLineForPayload = (
  value,
  maxLength
) => {
  const normalized = String(
    value ?? ""
  )
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .trim();

  if (
    normalized.length > maxLength
  ) {
    throw new RangeError(
      `El mensaje no puede superar los ${maxLength} caracteres.`
    );
  }

  return normalized;
};

const normalizeDisplayMode = (
  value
) => {
  const normalized = String(
    value ?? ""
  )
    .trim()
    .toLowerCase();

  return DISPLAY_MODE_ALLOWED.has(
    normalized
  )
    ? normalized
    : DISPLAY_MODE_DEFAULT;
};

const normalizeAvisosConfig = (
  value = {}
) => {
  const stageWidth = clamp(
    safeInt(
      pickFirst(
        value?.stageWidth,
        value?.stage_width
      ),
      DEFAULT_AVISOS_LAYOUT.stageWidth
    ),
    STAGE_WIDTH_MIN,
    STAGE_WIDTH_MAX
  );

  const stageHeight = clamp(
    safeInt(
      pickFirst(
        value?.stageHeight,
        value?.stage_height
      ),
      DEFAULT_AVISOS_LAYOUT.stageHeight
    ),
    STAGE_HEIGHT_MIN,
    STAGE_HEIGHT_MAX
  );

  const mediaPaneWidth = clamp(
    safeInt(
      pickFirst(
        value?.mediaPaneWidth,
        value?.media_pane_width
      ),
      DEFAULT_AVISOS_LAYOUT.mediaPaneWidth
    ),
    MEDIA_PANE_WIDTH_MIN,
    getMediaPaneWidthMax(stageWidth)
  );

  const displayMode =
    normalizeDisplayMode(
      pickFirst(
        value?.displayMode,
        value?.display_mode
      )
    );

  return {
    eyebrow: normalizeSingleLine(
      value?.eyebrow,
      DEFAULT_AVISOS_CONTENT.eyebrow
    ),

    title: normalizeSingleLine(
      value?.title,
      DEFAULT_AVISOS_CONTENT.title
    ),

    text: normalizeMultiLine(
      value?.text,
      DEFAULT_AVISOS_CONTENT.text
    ),

    recentLabel: normalizeSingleLine(
      pickFirst(
        value?.recentLabel,
        value?.recent_label
      ),
      DEFAULT_AVISOS_CONTENT.recentLabel
    ),

    stageWidth,
    stageHeight,
    mediaPaneWidth,
    displayMode,
  };
};

const setAvisosConfigCache = (
  value = {}
) => {
  avisosConfigCache =
    normalizeAvisosConfig(value);

  return {
    ...avisosConfigCache,
  };
};

const hasOwn = (
  object,
  key
) => {
  return Object.prototype.hasOwnProperty.call(
    object || {},
    key
  );
};

const buildConfigPatchPayload = (
  value = {}
) => {
  const input =
    value &&
    typeof value === "object"
      ? value
      : {};

  const normalized =
    normalizeAvisosConfig({
      ...avisosConfigCache,
      ...input,
    });

  const payload = {};

  if (
    hasOwn(input, "eyebrow")
  ) {
    payload.eyebrow =
      normalizeSingleLineForPayload(
        input.eyebrow,
        60
      );
  }

  if (
    hasOwn(input, "title")
  ) {
    payload.title =
      normalizeSingleLineForPayload(
        input.title,
        220
      );
  }

  if (
    hasOwn(input, "text")
  ) {
    payload.text =
      normalizeMultiLineForPayload(
        input.text,
        AVISOS_TEXT_MAX_LENGTH
      );
  }

  if (
    hasOwn(input, "recentLabel") ||
    hasOwn(input, "recent_label")
  ) {
    payload.recentLabel =
      normalizeSingleLineForPayload(
        pickFirst(
          input.recentLabel,
          input.recent_label
        ),
        60
      );
  }

  if (
    hasOwn(input, "stageWidth") ||
    hasOwn(input, "stage_width")
  ) {
    payload.stageWidth =
      normalized.stageWidth;
  }

  if (
    hasOwn(input, "stageHeight") ||
    hasOwn(input, "stage_height")
  ) {
    payload.stageHeight =
      normalized.stageHeight;
  }

  if (
    hasOwn(input, "mediaPaneWidth") ||
    hasOwn(input, "media_pane_width")
  ) {
    payload.mediaPaneWidth =
      normalized.mediaPaneWidth;
  }

  if (
    hasOwn(input, "displayMode") ||
    hasOwn(input, "display_mode")
  ) {
    payload.displayMode =
      normalized.displayMode;
  }

  if (
    !Object.keys(payload).length
  ) {
    payload.eyebrow =
      avisosConfigCache.eyebrow;

    payload.title =
      avisosConfigCache.title;

    payload.text =
      avisosConfigCache.text;

    payload.recentLabel =
      avisosConfigCache.recentLabel;

    payload.stageWidth =
      normalized.stageWidth;

    payload.stageHeight =
      normalized.stageHeight;

    payload.mediaPaneWidth =
      normalized.mediaPaneWidth;

    payload.displayMode =
      normalized.displayMode;
  }

  return payload;
};

const buildContentPatchPayload = (
  value = {}
) => {
  const input =
    value &&
    typeof value === "object"
      ? value
      : {};

  return {
    eyebrow:
      normalizeSingleLineForPayload(
        pickFirst(
          input.eyebrow,
          avisosConfigCache.eyebrow
        ),
        60
      ),

    title:
      normalizeSingleLineForPayload(
        pickFirst(
          input.title,
          avisosConfigCache.title
        ),
        220
      ),

    text:
      normalizeMultiLineForPayload(
        pickFirst(
          input.text,
          avisosConfigCache.text
        ),
        AVISOS_TEXT_MAX_LENGTH
      ),

    recentLabel:
      normalizeSingleLineForPayload(
        pickFirst(
          input.recentLabel,
          input.recent_label,
          avisosConfigCache.recentLabel
        ),
        60
      ),
  };
};

const buildLayoutPatchPayload = (
  value = {}
) => {
  const normalized =
    normalizeAvisosConfig({
      ...avisosConfigCache,
      ...value,
    });

  return {
    stageWidth:
      normalized.stageWidth,

    stageHeight:
      normalized.stageHeight,

    mediaPaneWidth:
      normalized.mediaPaneWidth,

    displayMode:
      normalized.displayMode,
  };
};

const normalizeUserEmail = (value) => {
  return String(value || "")
    .trim()
    .toLowerCase();
};

const resolveUserKey = (user) => {
  const userId = String(
    user?.id ?? ""
  ).trim();

  if (userId) {
    return `id:${userId}`;
  }

  const email = normalizeUserEmail(
    user?.email
  );

  if (email) {
    return `email:${email}`;
  }

  return null;
};

export const hasAvisosUserIdentity = (
  user
) => {
  return Boolean(resolveUserKey(user));
};

const getSeenOnceKey = (user) => {
  const userKey = resolveUserKey(user);

  return userKey
    ? `${SEEN_ONCE_PREFIX}:${userKey}`
    : null;
};

const getSeenVersionKey = (user) => {
  const userKey = resolveUserKey(user);

  return userKey
    ? `${SEEN_VERSION_PREFIX}:${userKey}`
    : null;
};

const readLocalStorage = (key) => {
  if (!key || typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
};

const writeLocalStorage = (
  key,
  value
) => {
  if (!key || typeof window === "undefined") {
    return false;
  }

  try {
    window.localStorage.setItem(
      key,
      String(value)
    );

    return true;
  } catch {
    return false;
  }
};

const removeLocalStorage = (key) => {
  if (!key || typeof window === "undefined") {
    return false;
  }

  try {
    window.localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
};

const normalizeStatus = (
  data
) => {
  const generalVersion = String(
    pickFirst(
      data?.version,
      data?.general_version,
      ""
    ) || ""
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
    hasItems: Boolean(
      pickFirst(
        data?.has_items,
        data?.hasItems,
        false
      )
    ),

    total: Number(
      pickFirst(
        data?.total,
        0
      ) || 0
    ),

    // Puede cambiar por contenido, imágenes o diseño.
    version: generalVersion,

    // Solo debe cambiar cuando hay novedades notificables.
    notifyVersion,
  };
};

const is503 = (
  error
) => {
  return (
    Number(
      error?.response?.status
    ) === 503
  );
};

const getNoCacheConfig = () => {
  return {
    params: {
      _ts: Date.now(),
    },
  };
};

export const getAvisosCombinedVersion = (
  value = ""
) => {
  if (
    value &&
    typeof value === "object"
  ) {
    return String(
      value.notifyVersion ||
      value.version ||
      ""
    );
  }

  return String(
    value || ""
  );
};

export const isAdminUser = (
  user
) => {
  return sharedIsAdminUser(user);
};

export const getAvisosContent = () => {
  return {
    eyebrow:
      avisosConfigCache.eyebrow,

    title:
      avisosConfigCache.title,

    text:
      avisosConfigCache.text,

    recentLabel:
      avisosConfigCache.recentLabel,
  };
};

export const getAvisosLayout = () => {
  return {
    stageWidth:
      avisosConfigCache.stageWidth,

    stageHeight:
      avisosConfigCache.stageHeight,

    mediaPaneWidth:
      avisosConfigCache.mediaPaneWidth,

    displayMode:
      avisosConfigCache.displayMode,
  };
};

export const getAvisosConfigCached = () => {
  return {
    ...avisosConfigCache,
  };
};

export const hydrateAvisosConfig =
  async () => {
    try {
      const {
        data,
      } = await api.get(
        "banners/config/",
        getNoCacheConfig()
      );

      return setAvisosConfigCache(
        data
      );
    } catch (error) {
      if (
        is503(error)
      ) {
        return setAvisosConfigCache({
          ...DEFAULT_AVISOS_CONTENT,
          ...DEFAULT_AVISOS_LAYOUT,
        });
      }

      throw error;
    }
  };

export const saveAvisosConfig =
  async (
    value = {}
  ) => {
    const payload =
      buildConfigPatchPayload(
        value
      );

    const {
      data,
    } = await api.patch(
      "banners/config/",
      payload
    );

    return setAvisosConfigCache(
      data
    );
  };

export const saveAvisosContent =
  async (
    value = {}
  ) => {
    const payload =
      buildContentPatchPayload(
        value
      );

    const {
      data,
    } = await api.patch(
      "banners/config/",
      payload
    );

    return setAvisosConfigCache(
      data
    );
  };

export const saveAvisosLayout =
  async (
    value = {}
  ) => {
    const payload =
      buildLayoutPatchPayload(
        value
      );

    const {
      data,
    } = await api.patch(
      "banners/config/",
      payload
    );

    return setAvisosConfigCache(
      data
    );
  };

export const resetAvisosContent =
  async () => {
    return saveAvisosContent(
      DEFAULT_AVISOS_CONTENT
    );
  };

export const resetAvisosLayout =
  async () => {
    return saveAvisosLayout(
      DEFAULT_AVISOS_LAYOUT
    );
  };

export const getAvisosStatus =
  async () => {
    const {
      data,
    } = await api.get(
      "banners/status/",
      getNoCacheConfig()
    );

    return normalizeStatus(
      data
    );
  };

export const shouldOpenAvisos =
  async (
    user,
    providedStatus = null
  ) => {
    if (!hasAvisosUserIdentity(user)) {
      return false;
    }

    const avisosStatus =
      providedStatus ||
      await getAvisosStatus();

    if (!avisosStatus.hasItems) {
      return false;
    }

    const currentNotifyVersion =
      getAvisosCombinedVersion(
        avisosStatus
      ).trim();

    // No se abre ni se persiste un aviso cuya versión
    // no haya sido confirmada por el backend.
    if (!currentNotifyVersion) {
      return false;
    }

    const seenOnce =
      readLocalStorage(
        getSeenOnceKey(user)
      ) === "1";

    const seenVersion =
      readLocalStorage(
        getSeenVersionKey(user)
      ) || "";

    if (!seenOnce) {
      return true;
    }

    return (
      seenVersion !==
      currentNotifyVersion
    );
  };

export const markAvisosAsSeen = (
  user,
  versionOrStatus = ""
) => {
  if (!hasAvisosUserIdentity(user)) {
    return false;
  }

  const version =
    getAvisosCombinedVersion(
      versionOrStatus
    ).trim();

  if (!version) {
    return false;
  }

  const onceStored =
    writeLocalStorage(
      getSeenOnceKey(user),
      "1"
    );

  const versionStored =
    writeLocalStorage(
      getSeenVersionKey(user),
      version
    );

  return onceStored && versionStored;
};

export const clearAvisosSeenState = (
  user
) => {
  if (!hasAvisosUserIdentity(user)) {
    return false;
  }

  const onceRemoved =
    removeLocalStorage(
      getSeenOnceKey(user)
    );

  const versionRemoved =
    removeLocalStorage(
      getSeenVersionKey(user)
    );

  return onceRemoved && versionRemoved;
};
