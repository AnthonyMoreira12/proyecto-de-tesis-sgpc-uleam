import { defineStore } from "pinia";
import api from "../api/axios";
import { isAdminUser } from "../utils/auth";
import {
  AUTH_STORAGE_KEYS,
  clearAuthStorage,
  clearPersistedProfileFields,
  getAccessToken,
  getRefreshToken,
  getStorageValue,
  getStoredUser,
  setAccessToken,
  setRefreshToken,
  setStorageValue,
  setStoredUser,
} from "../utils/authStorage";

const STORAGE_KEYS = AUTH_STORAGE_KEYS;

let profileRefreshPromise = null;
let authBootstrapPromise = null;

const AVATAR_KEYS = Object.freeze([
  "avatar_url",
  "avatarUrl",
  "avatar",
  "foto_url",
  "foto",
  "photo_url",
  "photo",
]);

const normalizeNullableString = (value) => {
  const text = String(value ?? "").trim();

  if (!text) return null;

  const lowered = text.toLowerCase();

  if (
    lowered === "null" ||
    lowered === "undefined" ||
    lowered === "none" ||
    lowered === "nan" ||
    lowered === "false"
  ) {
    return null;
  }

  return text;
};

const hasOwn = (obj, key) =>
  Object.prototype.hasOwnProperty.call(obj || {}, key);

const hasAvatarField = (data = {}) => {
  return AVATAR_KEYS.some((key) => hasOwn(data, key));
};

const extractAvatarUrl = (data = {}, fallback = null) => {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return normalizeNullableString(fallback);
  }

  const dataHasAvatarField = hasAvatarField(data);

  if (!dataHasAvatarField) {
    return normalizeNullableString(fallback);
  }

  for (const key of AVATAR_KEYS) {
    const value = normalizeNullableString(data[key]);
    if (value) return value;
  }

  return null;
};

const resolveAutorId = (u = {}) =>
  String(u?.autor_id ?? u?.author_id ?? u?.scholar_profile_id ?? "").trim();

const normalizeUser = (data, fallbackAvatar = null) => {
  if (!data || typeof data !== "object" || Array.isArray(data)) return null;

  const user = { ...data };

  user.is_staff = !!user.is_staff;
  user.is_superuser = !!user.is_superuser;

  user.is_admin = !!(
    user.is_admin ||
    user.es_admin ||
    user.is_staff ||
    user.is_superuser
  );

  user.es_admin = user.is_admin;
  user.avatar_url = extractAvatarUrl(user, fallbackAvatar);

  return user;
};

export const useUserStore = defineStore("user", {
  state: () => {
    const persistedAvatar = normalizeNullableString(
      getStorageValue(STORAGE_KEYS.avatar, "")
    );

    const storedUser = normalizeUser(getStoredUser(null), persistedAvatar);

    return {
      accessToken: getAccessToken(),
      refreshToken: getRefreshToken(),
      user: storedUser,

      nombres: getStorageValue(STORAGE_KEYS.nombres, "") || storedUser?.nombres || "",
      apellidos: getStorageValue(STORAGE_KEYS.apellidos, "") || storedUser?.apellidos || "",
      avatar: normalizeNullableString(persistedAvatar || storedUser?.avatar_url || ""),
      rol: getStorageValue(STORAGE_KEYS.rol, "") || storedUser?.rol || storedUser?.role || "",
      email: getStorageValue(STORAGE_KEYS.email, "") || storedUser?.email || storedUser?.correo || "",
      autorId: getStorageValue(STORAGE_KEYS.autorId, "") || resolveAutorId(storedUser || {}),

      hydrated: false,
      profileRefreshing: false,
    };
  },

  getters: {
    fullName(state) {
      const u = state.user;
      const ms = u?.ms_display_name ? String(u.ms_display_name).trim() : "";

      if (ms) return ms;

      const n = (state.nombres || u?.nombres || "").trim();
      const a = (state.apellidos || u?.apellidos || "").trim();

      return `${n} ${a}`.trim() || "Usuario";
    },

    avatarUrl(state) {
      return normalizeNullableString(
        state.avatar ||
          state.user?.avatar_url ||
          state.user?.avatarUrl ||
          state.user?.avatar ||
          state.user?.foto_url ||
          state.user?.foto ||
          state.user?.photo_url ||
          state.user?.photo ||
          ""
      );
    },

    inicial(state) {
      const n = state.nombres || state.user?.nombres || "";
      const a = state.apellidos || state.user?.apellidos || "";

      return (n.trim()[0] || a.trim()[0] || "U").toUpperCase();
    },

    isAuthenticated(state) {
      return !!state.accessToken && !!state.user;
    },

    isAdmin(state) {
      return isAdminUser(state.user);
    },
  },

  actions: {
    persistTokens() {
      setAccessToken(this.accessToken);
      setRefreshToken(this.refreshToken);
    },

    persistUserFields() {
      setStoredUser(this.user || null);
      setStorageValue(STORAGE_KEYS.nombres, this.nombres || "");
      setStorageValue(STORAGE_KEYS.apellidos, this.apellidos || "");
      setStorageValue(STORAGE_KEYS.avatar, this.avatar || "");
      setStorageValue(STORAGE_KEYS.rol, this.rol || "");
      setStorageValue(STORAGE_KEYS.email, this.email || "");
      setStorageValue(STORAGE_KEYS.autorId, this.autorId || "");
    },

    applyEmptyUserState() {
      this.user = null;
      this.nombres = "";
      this.apellidos = "";
      this.avatar = null;
      this.rol = "";
      this.email = "";
      this.autorId = "";
    },

    applyUserData(data) {
      const fallbackAvatar = normalizeNullableString(
        this.avatar || this.user?.avatar_url || ""
      );

      const normalized = normalizeUser(data, fallbackAvatar);

      if (!normalized) {
        this.applyEmptyUserState();
        return;
      }

      this.user = normalized;
      this.nombres = normalized.nombres || "";
      this.apellidos = normalized.apellidos || "";
      this.avatar = normalizeNullableString(normalized.avatar_url);
      this.rol = normalized.rol || normalized.role || "";
      this.email = normalized.email || normalized.correo || "";
      this.autorId = resolveAutorId(normalized);
    },

    hydrate() {
      this.accessToken = getAccessToken();
      this.refreshToken = getRefreshToken();

      const persistedAvatar = normalizeNullableString(
        getStorageValue(STORAGE_KEYS.avatar, "")
      );

      const persistedUser = normalizeUser(getStoredUser(null), persistedAvatar);

      if (persistedUser) {
        this.applyUserData(persistedUser);
      } else {
        this.user = null;
        this.nombres = getStorageValue(STORAGE_KEYS.nombres, "");
        this.apellidos = getStorageValue(STORAGE_KEYS.apellidos, "");
        this.avatar = normalizeNullableString(getStorageValue(STORAGE_KEYS.avatar, ""));
        this.rol = getStorageValue(STORAGE_KEYS.rol, "");
        this.email = getStorageValue(STORAGE_KEYS.email, "");
        this.autorId = getStorageValue(STORAGE_KEYS.autorId, "");
      }

      this.hydrated = true;
      this.persistUserFields();
    },

    async refreshProfile(options = {}) {
      const { throwOnError = false } = options;

      if (!this.accessToken) return null;

      if (profileRefreshPromise) {
        try {
          return await profileRefreshPromise;
        } catch (error) {
          if (throwOnError) throw error;
          return null;
        }
      }

      this.profileRefreshing = true;

      profileRefreshPromise = (async () => {
        try {
          const { data } = await api.get("auth/profile/");
          this.setUserData(data);
          return data;
        } finally {
          this.profileRefreshing = false;
          profileRefreshPromise = null;
        }
      })();

      try {
        return await profileRefreshPromise;
      } catch (error) {
        if (throwOnError) throw error;
        return null;
      }
    },

    async bootstrapAuth(options = {}) {
      const { force = false } = options;

      if (authBootstrapPromise) {
        return authBootstrapPromise;
      }

      authBootstrapPromise = (async () => {
        if (!this.hydrated || force) {
          this.hydrate();
        }

        if (!this.accessToken) {
          this.clearUser();
          return null;
        }

        /*
          Si ya existe usuario pero no hay avatar, NO devolvemos cache.
          Forzamos auth/profile/ para traer avatar_url desde el backend.
        */
        if (!force && this.user && this.avatarUrl) {
          return this.user;
        }

        try {
          const profile = await this.refreshProfile({ throwOnError: true });

          if (!profile) {
            if (this.user) return this.user;
            this.clearUser();
            return null;
          }

          return this.user;
        } catch {
          if (this.user) return this.user;
          this.clearUser();
          return null;
        }
      })();

      try {
        return await authBootstrapPromise;
      } finally {
        authBootstrapPromise = null;
      }
    },

    hydrateAndRefresh() {
      return this.bootstrapAuth();
    },

    setSession({ access = "", refresh = "", user = null } = {}) {
      this.accessToken = String(access || "").trim();
      this.refreshToken = String(refresh || "").trim();
      this.persistTokens();

      if (user) {
        this.setUserData(user);
      } else {
        this.applyEmptyUserState();
        clearPersistedProfileFields();
      }

      this.hydrated = true;
    },

    setUserData(data) {
      this.applyUserData(data);
      this.persistUserFields();
      this.hydrated = true;
    },

    setAvatar(url) {
      const normalizedUrl = normalizeNullableString(url);

      this.avatar = normalizedUrl;

      if (this.user) {
        this.user.avatar_url = normalizedUrl;
      }

      this.persistUserFields();
    },

    setAutorId(value) {
      this.autorId = String(value || "").trim();

      if (this.user) {
        this.user.autor_id = this.autorId || null;
      }

      this.persistUserFields();
    },

    clearUser() {
      this.accessToken = "";
      this.refreshToken = "";
      this.applyEmptyUserState();
      this.profileRefreshing = false;
      this.hydrated = true;
      clearAuthStorage();
    },
  },
});