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


const ROLE_INSTITUTIONAL = "autor";
const ROLE_EXTERNAL = "autor_externo";

const AUTH_SOURCE_LOCAL = "local";
const AUTH_SOURCE_MICROSOFT = "microsoft";


/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) => {
  return String(value ?? "").trim();
};


const normalizeAccountValue = (value) => {
  return normalizeText(value).toLowerCase();
};


const normalizeNullableString = (value) => {
  const text = normalizeText(value);

  if (!text) {
    return null;
  }

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


const normalizeBoolean = (
  value,
  fallback = false
) => {
  if (
    value === true ||
    value === 1
  ) {
    return true;
  }

  if (
    value === false ||
    value === 0
  ) {
    return false;
  }

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return Boolean(fallback);
  }

  const normalized =
    normalizeAccountValue(value);

  if (
    normalized === "1" ||
    normalized === "true" ||
    normalized === "yes" ||
    normalized === "y" ||
    normalized === "on" ||
    normalized === "si" ||
    normalized === "sí"
  ) {
    return true;
  }

  if (
    normalized === "0" ||
    normalized === "false" ||
    normalized === "no" ||
    normalized === "n" ||
    normalized === "off"
  ) {
    return false;
  }

  return Boolean(fallback);
};


const hasOwn = (obj, key) => {
  return Object.prototype.hasOwnProperty.call(
    obj || {},
    key
  );
};


const hasAvatarField = (data = {}) => {
  return AVATAR_KEYS.some(
    (key) => hasOwn(data, key)
  );
};


const extractAvatarUrl = (
  data = {},
  fallback = null
) => {
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    return normalizeNullableString(
      fallback
    );
  }

  if (!hasAvatarField(data)) {
    return normalizeNullableString(
      fallback
    );
  }

  for (const key of AVATAR_KEYS) {
    const value =
      normalizeNullableString(
        data[key]
      );

    if (value) {
      return value;
    }
  }

  return null;
};


const resolveAutorId = (user = {}) => {
  return normalizeText(
    user?.autor_id ??
    user?.author_id ??
    user?.scholar_profile_id ??
    ""
  );
};


const isExternalAccount = (user = {}) => {
  return (
    normalizeAccountValue(
      user?.rol ?? user?.role
    ) === ROLE_EXTERNAL &&
    normalizeAccountValue(
      user?.auth_source
    ) === AUTH_SOURCE_LOCAL
  );
};


const isInstitutionalAccount = (
  user = {}
) => {
  return (
    normalizeAccountValue(
      user?.rol ?? user?.role
    ) === ROLE_INSTITUTIONAL &&
    normalizeAccountValue(
      user?.auth_source
    ) === AUTH_SOURCE_MICROSOFT
  );
};


const hasValidCedula = (user = {}) => {
  const cedula = normalizeText(
    user?.identificacion
  );

  return /^\d{10}$/.test(
    cedula
  );
};


const hasCareer = (user = {}) => {
  const careerId =
    user?.carrera_id ??
    (
      typeof user?.carrera === "object"
        ? user.carrera?.id
        : null
    );

  return Boolean(
    careerId
  );
};


const calculateProfileComplete = (
  user = {}
) => {
  if (!hasValidCedula(user)) {
    return false;
  }

  if (isExternalAccount(user)) {
    return true;
  }

  if (isInstitutionalAccount(user)) {
    return hasCareer(user);
  }

  return false;
};


const clearAcademicData = (user) => {
  user.facultad_id = null;
  user.facultad = null;
  user.facultad_nombre = null;

  user.carrera_id = null;
  user.carrera = null;
  user.carrera_nombre = null;

  return user;
};


const normalizeUser = (
  data,
  fallbackAvatar = null
) => {
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    return null;
  }

  const user = {
    ...data,
  };

  user.rol = normalizeAccountValue(
    user.rol ?? user.role
  );

  user.auth_source =
    normalizeAccountValue(
      user.auth_source
    );

  user.email =
    normalizeNullableString(
      user.email ?? user.correo
    );

  user.nombres =
    normalizeText(
      user.nombres
    );

  user.apellidos =
    normalizeText(
      user.apellidos
    );

  user.identificacion =
    normalizeNullableString(
      user.identificacion
    );

  user.is_active =
    normalizeBoolean(
      user.is_active,
      true
    );

  user.is_staff =
    normalizeBoolean(
      user.is_staff,
      false
    );

  user.is_superuser =
    normalizeBoolean(
      user.is_superuser,
      false
    );

  /*
    Los permisos administrativos se calculan exclusivamente
    desde los campos canónicos del modelo.

    No se confía en roles textuales ni en valores antiguos
    almacenados en es_admin o is_admin.
  */
  user.is_admin = Boolean(
    user.is_staff ||
    user.is_superuser
  );

  user.es_admin =
    user.is_admin;

  user.es_externo =
    isExternalAccount(user);

  user.es_institucional =
    isInstitutionalAccount(user);

  if (user.es_externo) {
    user.tipo_cuenta_label =
      "Cuenta externa";
  } else if (
    user.es_institucional
  ) {
    user.tipo_cuenta_label =
      "Cuenta institucional";
  } else {
    user.tipo_cuenta_label =
      "Cuenta sin clasificación válida";
  }

  /*
    Únicamente las cuentas institucionales pueden conservar
    información académica.
  */
  if (!user.es_institucional) {
    clearAcademicData(user);
  }

  user.perfil_completo =
    calculateProfileComplete(user);

  user.avatar_url =
    extractAvatarUrl(
      user,
      fallbackAvatar
    );

  user.autor_id =
    resolveAutorId(user) || null;

  return user;
};


/* ============================================================
   STORE
============================================================ */

export const useUserStore = defineStore(
  "user",
  {
    state: () => {
      const persistedAvatar =
        normalizeNullableString(
          getStorageValue(
            STORAGE_KEYS.avatar,
            ""
          )
        );

      const storedUser =
        normalizeUser(
          getStoredUser(null),
          persistedAvatar
        );

      return {
        accessToken:
          getAccessToken(),

        refreshToken:
          getRefreshToken(),

        user:
          storedUser,

        nombres:
          getStorageValue(
            STORAGE_KEYS.nombres,
            ""
          ) ||
          storedUser?.nombres ||
          "",

        apellidos:
          getStorageValue(
            STORAGE_KEYS.apellidos,
            ""
          ) ||
          storedUser?.apellidos ||
          "",

        avatar:
          normalizeNullableString(
            persistedAvatar ||
            storedUser?.avatar_url ||
            ""
          ),

        rol:
          getStorageValue(
            STORAGE_KEYS.rol,
            ""
          ) ||
          storedUser?.rol ||
          "",

        email:
          getStorageValue(
            STORAGE_KEYS.email,
            ""
          ) ||
          storedUser?.email ||
          "",

        autorId:
          getStorageValue(
            STORAGE_KEYS.autorId,
            ""
          ) ||
          resolveAutorId(
            storedUser || {}
          ),

        hydrated: false,
        profileRefreshing: false,
      };
    },

    getters: {
      fullName(state) {
        const user =
          state.user;

        const microsoftName =
          normalizeText(
            user?.ms_display_name
          );

        if (microsoftName) {
          return microsoftName;
        }

        const nombres =
          normalizeText(
            state.nombres ||
            user?.nombres
          );

        const apellidos =
          normalizeText(
            state.apellidos ||
            user?.apellidos
          );

        return (
          `${nombres} ${apellidos}`.trim() ||
          "Usuario"
        );
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
        const nombres =
          normalizeText(
            state.nombres ||
            state.user?.nombres
          );

        const apellidos =
          normalizeText(
            state.apellidos ||
            state.user?.apellidos
          );

        return (
          nombres.charAt(0) ||
          apellidos.charAt(0) ||
          "U"
        ).toUpperCase();
      },

      isAuthenticated(state) {
        return Boolean(
          state.accessToken &&
          state.user
        );
      },

      isAdmin(state) {
        return isAdminUser(
          state.user
        );
      },

      isExternal(state) {
        return Boolean(
          state.user?.es_externo
        );
      },

      isInstitutional(state) {
        return Boolean(
          state.user?.es_institucional
        );
      },

      accountTypeLabel(state) {
        return (
          state.user?.tipo_cuenta_label ||
          "Cuenta sin clasificación válida"
        );
      },
    },

    actions: {
      /* ======================================================
         PERSISTENCIA
      ====================================================== */

      persistTokens() {
        setAccessToken(
          this.accessToken
        );

        setRefreshToken(
          this.refreshToken
        );
      },

      persistUserFields() {
        setStoredUser(
          this.user || null
        );

        setStorageValue(
          STORAGE_KEYS.nombres,
          this.nombres || ""
        );

        setStorageValue(
          STORAGE_KEYS.apellidos,
          this.apellidos || ""
        );

        setStorageValue(
          STORAGE_KEYS.avatar,
          this.avatar || ""
        );

        setStorageValue(
          STORAGE_KEYS.rol,
          this.rol || ""
        );

        setStorageValue(
          STORAGE_KEYS.email,
          this.email || ""
        );

        setStorageValue(
          STORAGE_KEYS.autorId,
          this.autorId || ""
        );
      },

      /* ======================================================
         ESTADO VACÍO
      ====================================================== */

      applyEmptyUserState() {
        this.user = null;
        this.nombres = "";
        this.apellidos = "";
        this.avatar = null;
        this.rol = "";
        this.email = "";
        this.autorId = "";
      },

      /* ======================================================
         APLICAR DATOS DEL USUARIO
      ====================================================== */

      applyUserData(data) {
        const fallbackAvatar =
          normalizeNullableString(
            this.avatar ||
            this.user?.avatar_url ||
            ""
          );

        const normalized =
          normalizeUser(
            data,
            fallbackAvatar
          );

        if (!normalized) {
          this.applyEmptyUserState();
          return;
        }

        this.user = normalized;

        this.nombres =
          normalized.nombres ||
          "";

        this.apellidos =
          normalized.apellidos ||
          "";

        this.avatar =
          normalizeNullableString(
            normalized.avatar_url
          );

        this.rol =
          normalized.rol ||
          "";

        this.email =
          normalized.email ||
          "";

        this.autorId =
          resolveAutorId(
            normalized
          );
      },

      /* ======================================================
         HIDRATACIÓN LOCAL
      ====================================================== */

      hydrate() {
        this.accessToken =
          getAccessToken();

        this.refreshToken =
          getRefreshToken();

        const persistedAvatar =
          normalizeNullableString(
            getStorageValue(
              STORAGE_KEYS.avatar,
              ""
            )
          );

        const persistedUser =
          normalizeUser(
            getStoredUser(null),
            persistedAvatar
          );

        if (persistedUser) {
          this.applyUserData(
            persistedUser
          );
        } else {
          this.user = null;

          this.nombres =
            getStorageValue(
              STORAGE_KEYS.nombres,
              ""
            );

          this.apellidos =
            getStorageValue(
              STORAGE_KEYS.apellidos,
              ""
            );

          this.avatar =
            normalizeNullableString(
              getStorageValue(
                STORAGE_KEYS.avatar,
                ""
              )
            );

          this.rol =
            getStorageValue(
              STORAGE_KEYS.rol,
              ""
            );

          this.email =
            getStorageValue(
              STORAGE_KEYS.email,
              ""
            );

          this.autorId =
            getStorageValue(
              STORAGE_KEYS.autorId,
              ""
            );
        }

        this.hydrated = true;

        this.persistUserFields();
      },

      /* ======================================================
         ACTUALIZACIÓN DEL PERFIL
      ====================================================== */

      async refreshProfile(
        options = {}
      ) {
        const {
          throwOnError = false,
        } = options;

        if (!this.accessToken) {
          return null;
        }

        if (profileRefreshPromise) {
          try {
            return await profileRefreshPromise;
          } catch (error) {
            if (throwOnError) {
              throw error;
            }

            return null;
          }
        }

        this.profileRefreshing = true;

        profileRefreshPromise =
          (async () => {
            try {
              const { data } =
                await api.get(
                  "auth/profile/"
                );

              this.setUserData(
                data
              );

              return data;
            } finally {
              this.profileRefreshing =
                false;

              profileRefreshPromise =
                null;
            }
          })();

        try {
          return await profileRefreshPromise;
        } catch (error) {
          if (throwOnError) {
            throw error;
          }

          return null;
        }
      },

      /* ======================================================
         INICIALIZACIÓN DE LA AUTENTICACIÓN
      ====================================================== */

      async bootstrapAuth(
        options = {}
      ) {
        const {
          force = false,
        } = options;

        if (authBootstrapPromise) {
          return authBootstrapPromise;
        }

        authBootstrapPromise =
          (async () => {
            if (
              !this.hydrated ||
              force
            ) {
              this.hydrate();
            }

            if (!this.accessToken) {
              this.clearUser();
              return null;
            }

            /*
              La información guardada localmente se utiliza
              únicamente para mostrar datos mientras responde
              el backend.

              Siempre se consulta auth/profile/ para actualizar:

              - is_staff
              - is_superuser
              - es_admin
              - rol
              - auth_source
              - clasificación de cuenta
              - Carrera y Facultad
            */
            try {
              const profile =
                await this.refreshProfile({
                  throwOnError: true,
                });

              if (!profile) {
                this.clearUser();
                return null;
              }

              return this.user;
            } catch (error) {
              const status =
                error?.response?.status;

              /*
                Una respuesta 401 o 403 significa que la sesión
                ya no es válida o que la cuenta perdió acceso.
              */
              if (
                status === 401 ||
                status === 403
              ) {
                this.clearUser();
                return null;
              }

              /*
                Ante una interrupción temporal de red se conserva
                la sesión local como respaldo. El backend seguirá
                protegiendo todas las rutas administrativas.
              */
              if (this.user) {
                return this.user;
              }

              this.clearUser();
              return null;
            }
          })();

        try {
          return await authBootstrapPromise;
        } finally {
          authBootstrapPromise =
            null;
        }
      },

      hydrateAndRefresh() {
        return this.bootstrapAuth();
      },

      /* ======================================================
         ESTABLECER SESIÓN
      ====================================================== */

      setSession({
        access = "",
        refresh = "",
        user = null,
      } = {}) {
        this.accessToken =
          normalizeText(access);

        this.refreshToken =
          normalizeText(refresh);

        this.persistTokens();

        if (user) {
          this.setUserData(
            user
          );
        } else {
          this.applyEmptyUserState();

          clearPersistedProfileFields();
        }

        this.hydrated = true;
      },

      /* ======================================================
         ACTUALIZAR USUARIO
      ====================================================== */

      setUserData(data) {
        this.applyUserData(
          data
        );

        this.persistUserFields();

        this.hydrated = true;
      },

      /* ======================================================
         ACTUALIZAR AVATAR
      ====================================================== */

      setAvatar(url) {
        const normalizedUrl =
          normalizeNullableString(
            url
          );

        this.avatar =
          normalizedUrl;

        if (this.user) {
          this.user.avatar_url =
            normalizedUrl;
        }

        this.persistUserFields();
      },

      /* ======================================================
         ACTUALIZAR AUTOR
      ====================================================== */

      setAutorId(value) {
        this.autorId =
          normalizeText(value);

        if (this.user) {
          this.user.autor_id =
            this.autorId ||
            null;
        }

        this.persistUserFields();
      },

      /* ======================================================
         CERRAR SESIÓN
      ====================================================== */

      clearUser() {
        this.accessToken = "";
        this.refreshToken = "";

        this.applyEmptyUserState();

        this.profileRefreshing =
          false;

        this.hydrated = true;

        clearAuthStorage();
      },
    },
  }
);