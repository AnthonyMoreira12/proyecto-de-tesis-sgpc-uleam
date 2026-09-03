const LOGIN_MARKER_KEY =
  "sgpc-pending-update-login-marker";

const SEEN_MARKER_KEY =
  "sgpc-pending-update-modal-seen";

const getSessionStorage = () => {
  if (
    typeof window === "undefined" ||
    !window.sessionStorage
  ) {
    return null;
  }

  return window.sessionStorage;
};

const buildMarker = () => {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
};

export const beginPendingUpdateLoginSession = () => {
  const storage = getSessionStorage();

  if (!storage) {
    return "";
  }

  const marker = buildMarker();

  storage.setItem(
    LOGIN_MARKER_KEY,
    marker
  );
  storage.removeItem(
    SEEN_MARKER_KEY
  );

  return marker;
};

export const clearPendingUpdateLoginSession = () => {
  const storage = getSessionStorage();

  if (!storage) {
    return;
  }

  storage.removeItem(
    LOGIN_MARKER_KEY
  );
  storage.removeItem(
    SEEN_MARKER_KEY
  );
};

export const shouldShowPendingUpdateModal = () => {
  const storage = getSessionStorage();

  if (!storage) {
    return false;
  }

  const loginMarker = String(
    storage.getItem(LOGIN_MARKER_KEY) || ""
  ).trim();

  if (!loginMarker) {
    return false;
  }

  const seenMarker = String(
    storage.getItem(SEEN_MARKER_KEY) || ""
  ).trim();

  return seenMarker !== loginMarker;
};

export const markPendingUpdateModalSeen = () => {
  const storage = getSessionStorage();

  if (!storage) {
    return;
  }

  const loginMarker = String(
    storage.getItem(LOGIN_MARKER_KEY) || ""
  ).trim();

  if (!loginMarker) {
    return;
  }

  storage.setItem(
    SEEN_MARKER_KEY,
    loginMarker
  );
};
