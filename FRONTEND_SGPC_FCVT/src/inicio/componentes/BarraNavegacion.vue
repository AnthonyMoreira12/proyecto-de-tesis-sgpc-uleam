<template>
  <div
    class="sgpc-nav"
    :class="{ 'is-sidebar-collapsed': sidebarCollapsed }"
    :style="{ '--sgpc-nav-offset': `${navOffset}px` }"
  >
    <div
      class="sgpc-nav__overlay"
      :class="{
        'is-visible': panelBackdropVisible,
        'is-drawer-open': drawerOpen,
        'is-search-open': searchPanelOpen,
        'is-account-open': accountOpen
      }"
      aria-hidden="true"
      @click="closeAllPanels"
    ></div>

    <aside
      class="sgpc-nav__sidebar"
      :class="{ 'is-open': drawerOpen }"
      aria-label="Menú de navegación"
    >
      <div class="sgpc-nav__brand-panel">
        <button
          class="sgpc-nav__brand"
          type="button"
          title="Sistema de Gestión de Producción Científica ULEAM"
          aria-label="Ir al inicio de SGPC ULEAM"
          @click="goHomeFromLogo"
        >
          <img
            src="../../assets/LOGO-ULEAM-VERTICAL.png"
            alt="Logo ULEAM"
            class="sgpc-nav__brand-logo"
          />

          <span class="sgpc-nav__brand-copy">
            <strong><span>SGPC</span> ULEAM</strong>
            <small>Producción científica</small>
          </span>
        </button>

        <button
          class="sgpc-nav__close-drawer"
          type="button"
          aria-label="Cerrar menú"
          @click="closeDrawer"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              d="M18 6 6 18M6 6l12 12"
            />
          </svg>
        </button>

        <button
          class="sgpc-nav__collapse-toggle"
          type="button"
          :aria-label="sidebarToggleTitle"
          :title="sidebarToggleTitle"
          @click.stop="toggleSidebarCollapse"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
              :d="sidebarCollapsed ? 'M9 5l7 7-7 7' : 'M15 5l-7 7 7 7'"
            />
          </svg>
        </button>
      </div>

      <nav class="sgpc-nav__menu" aria-label="Opciones del sistema">
        <div class="sgpc-nav__section-title">Principal</div>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/home', '/inicio') }"
          title="Dashboard"
          @click="goHomeFromLogo"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M12 3l9 8h-3v10h-5v-6H11v6H6V11H3l9-8z" />
            </svg>
          </span>
          <span>Dashboard</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/tipos-publicacion') }"
          title="Registrar publicación"
          @click="go('/tipos-publicacion')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M19 11H13V5h-2v6H5v2h6v6h2v-6h6v-2z" />
            </svg>
          </span>
          <span>Registrar publicación</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isAvisosRouteActive }"
          title="Avisos"
          @click="goAvisos"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4V5Zm2 0v10.17L8.28 14H18V5H6Zm2 2h8v2H8V7Zm0 4h6v2H8v-2Z"
              />
            </svg>
          </span>
          <span>Avisos</span>
        </button>

        <div class="sgpc-nav__section-title">Académico</div>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/perfil/me', '/perfil-academico/me') }"
          title="Mi perfil académico"
          @click="goMyScholarProfile"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z"
              />
            </svg>
          </span>
          <span>Mi perfil académico</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/proyectos-listado') }"
          title="Proyectos"
          @click="go('/proyectos-listado')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z"
              />
            </svg>
          </span>
          <span>Proyectos</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/mis-publicaciones') }"
          title="Mis publicaciones"
          @click="go('/mis-publicaciones')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2V5Zm2 0v14h10V5H6Z"
              />
            </svg>
          </span>
          <span>Mis publicaciones</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/publicaciones-listado') }"
          :title="publicationsListLabel"
          @click="go('/publicaciones-listado')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M3 5h18v2H3V5Zm0 6h18v2H3v-2Zm0 6h18v2H3v-2Z" />
            </svg>
          </span>
          <span>{{ publicationsMenuLabel }}</span>
        </button>

        <template v-if="isAdmin">
          <div class="sgpc-nav__section-title">Administración</div>

          <button
            type="button"
            class="sgpc-nav__menu-item"
            :class="{ 'is-active': isRouteActive('/admin', '/admin/panel', '/admin-panel') }"
            title="Panel administrativo"
            @click="goAdminPanel"
          >
            <span class="sgpc-nav__menu-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M12 2 3 6v6c0 5 3.84 9.74 9 11 5.16-1.26 9-6 9-11V6l-9-4Zm0 2.18 7 3.11V12c0 4.02-2.93 7.95-7 9.01C7.93 19.95 5 16.02 5 12V7.29l7-3.11Z"
                />
              </svg>
            </span>
            <span>Panel administrativo</span>
          </button>
        </template>
      </nav>
    </aside>

    <header
      ref="headerEl"
      class="sgpc-nav__topbar"
      :class="{
        'is-loaded': loaded,
        'is-scrolled': isScrolled,
        'has-open-panel': drawerOpen || searchPanelOpen || accountOpen
      }"
    >
      <div class="sgpc-nav__topbar-left">
        <button
          class="sgpc-nav__menu-toggle"
          type="button"
          aria-label="Abrir menú"
          @click="openDrawer"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z" />
          </svg>
        </button>

        <div class="sgpc-nav__page-title">
          <strong>{{ pageTitle }}</strong>
          <small>{{ pageSubtitle }}</small>
        </div>
      </div>

      <div class="sgpc-nav__topbar-right">
        <button
          ref="searchTrigger"
          class="sgpc-nav__top-action sgpc-nav__top-search"
          :class="{ 'is-open': searchPanelOpen }"
          type="button"
          aria-label="Abrir búsqueda global"
          :aria-expanded="searchPanelOpen ? 'true' : 'false'"
          aria-haspopup="dialog"
          title="Buscar (Ctrl + K)"
          @click.stop="toggleSearch"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
            />
          </svg>
          <span>Buscar</span>
          <kbd>Ctrl K</kbd>
        </button>

        <button
          class="sgpc-nav__top-action sgpc-nav__theme-top-btn"
          :class="{ 'is-active': uiDarkMode }"
          type="button"
          :aria-label="themeToggleTitle"
          :title="themeToggleTitle"
          :aria-pressed="uiDarkMode ? 'true' : 'false'"
          @click.stop="toggleDarkMode"
        >
          <svg v-if="uiDarkMode" viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm-1-14h2v3h-2V2Zm0 17h2v3h-2v-3ZM4.22 5.64l1.42-1.42 2.12 2.12-1.42 1.42-2.12-2.12Zm12.02 12.02 1.42-1.42 2.12 2.12-1.42 1.42-2.12-2.12ZM2 11h3v2H2v-2Zm17 0h3v2h-3v-2ZM4.22 18.36l2.12-2.12 1.42 1.42-2.12 2.12-1.42-1.42ZM16.24 6.34l2.12-2.12 1.42 1.42-2.12 2.12-1.42-1.42Z"
            />
          </svg>

          <svg v-else viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M21 14.56A8.8 8.8 0 0 1 9.44 3a7.15 7.15 0 1 0 11.56 11.56Z"
            />
          </svg>
        </button>

        <template v-if="!isAuthenticated">
          <button class="sgpc-nav__login-btn" type="button" @click="go('/login')">
            Iniciar sesión
          </button>
        </template>

        <template v-else>
          <div class="sgpc-nav__account-wrap" ref="accountWrap">
            <button
              ref="accountTrigger"
              class="sgpc-nav__account-trigger"
              :class="{ 'is-open': accountOpen }"
              type="button"
              aria-label="Cuenta"
              aria-haspopup="dialog"
              aria-controls="sgpc-nav-account-card"
              :aria-expanded="accountOpen ? 'true' : 'false'"
              @click.stop="toggleAccount"
            >
              <span class="sgpc-nav__avatar-btn" aria-hidden="true">
                <img
                  v-if="userAvatar"
                  :src="userAvatar"
                  class="sgpc-nav__avatar-img"
                  alt=""
                  loading="eager"
                  decoding="async"
                  fetchpriority="high"
                  @error="handleAvatarImgError"
                />
                <span v-else class="sgpc-nav__avatar-initial">{{ userInitial }}</span>
              </span>

              <span class="sgpc-nav__account-name">{{ userName }}</span>
            </button>

            <div
              id="sgpc-nav-account-card"
              ref="accountCard"
              class="sgpc-nav__account-card"
              :class="{ 'is-open': accountOpen }"
              role="dialog"
              aria-modal="false"
              aria-label="Panel de cuenta"
              tabindex="-1"
              @click.stop
            >
              <div class="sgpc-nav__account-top">
                <div class="sgpc-nav__account-photo" aria-hidden="true">
                  <img
                    v-if="userAvatar"
                    :src="userAvatar"
                    class="sgpc-nav__account-photo-img"
                    alt=""
                    loading="eager"
                    decoding="async"
                    fetchpriority="high"
                    @error="handleAvatarImgError"
                  />
                  <div v-else class="sgpc-nav__account-photo-inner">{{ userInitial }}</div>
                </div>

                <div class="sgpc-nav__account-meta">
                  <p class="sgpc-nav__account-user">{{ userName }}</p>
                  <p class="sgpc-nav__account-email">{{ userStore.email || "" }}</p>
                  <p v-if="isAdmin" class="sgpc-nav__account-role">Administrador</p>
                </div>
              </div>

              <div class="sgpc-nav__divider"></div>

              <div class="sgpc-nav__account-body">
                <button
                  class="sgpc-nav__account-link"
                  :class="{ 'is-active': isRouteActive('/profile') }"
                  type="button"
                  @click="goMyAccount"
                >
                  <span>Mi cuenta</span>
                </button>

                <button
                  class="sgpc-nav__account-link"
                  :class="{
                    'is-active': isRouteActive(
                      '/preferencias',
                      '/preferencias-interfaz',
                      '/configuraciones'
                    )
                  }"
                  type="button"
                  @click="goConfig"
                >
                  <span>Preferencias de interfaz</span>
                </button>

                <button
                  v-if="isAdmin"
                  class="sgpc-nav__account-link"
                  :class="{ 'is-active': isRouteActive('/admin', '/admin/panel', '/admin-panel') }"
                  type="button"
                  @click="goAdminPanel"
                >
                  <span>Panel administrativo</span>
                </button>

                <button
                  class="sgpc-nav__account-btn sgpc-nav__account-btn--danger"
                  type="button"
                  @click="logout"
                >
                  <span>Cerrar sesión</span>
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </header>

    <Transition name="sgpc-nav-command-fade">
      <div
        v-if="searchPanelOpen"
        ref="searchPanel"
        class="sgpc-nav__command"
        :class="{
          'is-idle': !showCommandBody,
          'has-body': showCommandBody
        }"
        role="dialog"
        aria-modal="true"
        aria-label="Búsqueda global"
        @click.stop
      >
        <div class="sgpc-nav__command-head">
          <span class="sgpc-nav__command-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
              />
            </svg>
          </span>

          <input
            ref="searchInput"
            v-model="queryLocal"
            type="search"
            class="sgpc-nav__command-input"
            placeholder="Buscar publicaciones, autores o proyectos"
            title="Buscar"
            role="combobox"
            aria-autocomplete="list"
            aria-label="Buscar"
            :aria-expanded="showCommandBody ? 'true' : 'false'"
            :aria-controls="showCommandBody ? 'sgpc-nav-command-listbox' : undefined"
            :aria-activedescendant="activeDescendantId || undefined"
            @input="onInput"
            @keydown.down.prevent="move(1)"
            @keydown.up.prevent="move(-1)"
            @keydown.enter.prevent="acceptActive"
            @keydown.esc.prevent="closeSearchPanel(true)"
          />
        </div>

        <div
          v-if="showCommandBody"
          id="sgpc-nav-command-listbox"
          class="sgpc-nav__command-body"
          role="listbox"
          aria-label="Resultados de búsqueda"
        >
          <button
            v-if="queryLocal.trim()"
            class="sgpc-nav__command-action"
            type="button"
            @click="submitSearch"
          >
            <span class="sgpc-nav__command-item-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
                />
              </svg>
            </span>

            <span class="sgpc-nav__command-item-copy">
              <span class="sgpc-nav__command-item-title">
                Buscar “{{ queryLocal.trim() }}”
              </span>
              <small class="sgpc-nav__command-item-subtitle">
                Ir al índice académico
              </small>
            </span>
          </button>

          <div v-if="suggestLoading" class="sgpc-nav__loading">
            <span class="sgpc-nav__dot"></span>
            <span class="sgpc-nav__dot"></span>
            <span class="sgpc-nav__dot"></span>
            <span class="sgpc-nav__loading-text">Buscando sugerencias…</span>
          </div>

          <template v-else>
            <template v-if="normalizedSuggestions.length">
              <button
                v-for="s in normalizedSuggestions"
                :id="s._optionId"
                :key="s._key"
                type="button"
                class="sgpc-nav__command-item"
                :class="{ 'is-active': activeIndex === s._flatIndex }"
                role="option"
                :aria-selected="activeIndex === s._flatIndex ? 'true' : 'false'"
                @mousemove="activeIndex = s._flatIndex"
                @click="applySuggestion(s)"
              >
                <span class="sgpc-nav__command-item-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path :d="kindIconPath(s.kind)" fill="currentColor" />
                  </svg>
                </span>

                <span class="sgpc-nav__command-item-copy">
                  <span
                    class="sgpc-nav__command-item-title"
                    v-html="highlight(s.label, queryLocal)"
                  ></span>
                  <small class="sgpc-nav__command-item-subtitle">
                    {{ buildSuggestionSubtitle(s) }}
                  </small>
                </span>
              </button>
            </template>

            <p v-else class="sgpc-nav__no-results">
              Sin coincidencias directas. Presiona <b>Enter</b> para buscar en el índice académico.
            </p>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useRouter, useRoute } from "vue-router";
import { useThemeStore } from "../../scripts/stores/themeStore";
import { useUserStore } from "../../scripts/stores/userStore";
import { useScholarStore } from "../../scripts/stores/scholarStore";

const themeStore = useThemeStore();
const { darkMode } = storeToRefs(themeStore);

const userStore = useUserStore();
const scholarStore = useScholarStore();
const router = useRouter();
const route = useRoute();

const loaded = ref(false);
const isScrolled = ref(false);
const drawerOpen = ref(false);
const accountOpen = ref(false);
const searchPanelOpen = ref(false);
const activeIndex = ref(-1);
const navOffset = ref(66);
const sidebarCollapsed = ref(false);
const avatarBroken = ref(false);

const accountWrap = ref(null);
const accountTrigger = ref(null);
const accountCard = ref(null);
const searchTrigger = ref(null);
const searchPanel = ref(null);
const searchInput = ref(null);
const headerEl = ref(null);

const queryLocal = ref("");

let headerResizeObserver = null;

const SIDEBAR_COLLAPSE_STORAGE_KEY = "sgpc_sidebar_collapsed";

const uiDarkMode = computed({
  get: () => !!darkMode.value,
  set: (value) => themeStore.setDark?.(!!value),
});

const isAuthenticated = computed(() => !!userStore.isAuthenticated);
const userName = computed(() => userStore.fullName || "Usuario");
const userInitial = computed(() => userStore.inicial || "U");
const isAdmin = computed(() => !!userStore.isAdmin);
const suggestLoading = computed(() => !!scholarStore.suggestLoading);

const sidebarToggleTitle = computed(() =>
  sidebarCollapsed.value ? "Expandir menú" : "Ocultar menú"
);

const themeToggleTitle = computed(() =>
  uiDarkMode.value ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
);

const panelBackdropVisible = computed(
  () => drawerOpen.value || searchPanelOpen.value || accountOpen.value
);

const shouldLockScroll = computed(
  () => drawerOpen.value || searchPanelOpen.value || accountOpen.value
);

const publicationsListLabel = computed(() =>
  isAdmin.value ? "Gestión de publicaciones" : "Ver publicaciones"
);

const publicationsMenuLabel = computed(() => "Publicaciones");

const isAvisosRouteActive = computed(() => {
  return String(route.query?.modal || "").trim().toLowerCase() === "avisos";
});

const pageTitle = computed(() => {
  const path = route.path;

  if (path.startsWith("/admin")) return "Administración";
  if (path.startsWith("/publicacion")) return "Publicación";
  if (path.startsWith("/publicaciones-listado")) return publicationsListLabel.value;
  if (path.startsWith("/mis-publicaciones")) return "Mis publicaciones";
  if (path.startsWith("/proyectos-listado")) return "Proyectos";
  if (path.startsWith("/perfil") || path.startsWith("/perfil-academico")) return "Perfil académico";
  if (path.startsWith("/profile")) return "Mi cuenta";
  if (path.startsWith("/preferencias")) return "Preferencias";
  if (path.startsWith("/tipos-publicacion")) return "Registrar publicación";
  if (path.startsWith("/busqueda")) return "Búsqueda académica";

  return "Dashboard";
});

const pageSubtitle = computed(() => {
  if (isAdmin.value) return "Panel institucional SGPC ULEAM";
  return "Sistema de Gestión de Producción Científica";
});

const normalizeNullableString = (value) => {
  const text = String(value ?? "").trim();
  if (!text) return "";

  const lowered = text.toLowerCase();

  if (
    lowered === "null" ||
    lowered === "undefined" ||
    lowered === "none" ||
    lowered === "nan" ||
    lowered === "false"
  ) {
    return "";
  }

  return text;
};

const firstFilled = (...values) => {
  return values.map(normalizeNullableString).find(Boolean) || "";
};

const readStoredUser = () => {
  if (typeof window === "undefined") return {};

  try {
    const parsed = JSON.parse(localStorage.getItem("user") || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
};

const resolveAssetUrl = (value) => {
  const raw = normalizeNullableString(value);
  if (!raw) return "";

  if (/^(https?:|data:|blob:)/i.test(raw)) {
    return raw;
  }

  const apiBase = String(import.meta.env.VITE_API_URL || "").trim();

  try {
    if (apiBase) {
      const baseUrl = new URL(apiBase, window.location.origin);
      const origin = `${baseUrl.origin}/`;
      return new URL(raw.startsWith("/") ? raw.slice(1) : raw, origin).toString();
    }
  } catch {
    //
  }

  try {
    return new URL(raw, window.location.origin).toString();
  } catch {
    return raw;
  }
};

const userAvatar = computed(() => {
  if (avatarBroken.value) return null;

  const cached = readStoredUser();

  return (
    resolveAssetUrl(
      firstFilled(
        userStore.avatarUrl,
        userStore.avatar,
        userStore.user?.avatar_url,
        userStore.user?.avatarUrl,
        userStore.user?.avatar,
        userStore.user?.foto_url,
        userStore.user?.foto,
        cached.avatar_url,
        cached.avatarUrl,
        cached.avatar,
        cached.foto_url,
        cached.foto
      )
    ) || null
  );
});

const handleAvatarImgError = async () => {
  avatarBroken.value = true;

  try {
    await userStore.refreshProfile?.();
    avatarBroken.value = false;
  } catch {
    avatarBroken.value = true;
  }
};

const isDesktopViewport = () => {
  if (typeof window === "undefined") return true;
  return window.matchMedia?.("(min-width: 981px)")?.matches ?? true;
};

const applySidebarCollapseState = () => {
  if (typeof document === "undefined") return;

  document.documentElement.classList.toggle(
    "sgpc-sidebar-collapsed",
    sidebarCollapsed.value && isDesktopViewport()
  );
};

const loadSidebarCollapsePreference = () => {
  sidebarCollapsed.value = false;

  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(SIDEBAR_COLLAPSE_STORAGE_KEY);
  } catch {
    //
  }
};

const saveSidebarCollapsePreference = () => {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(SIDEBAR_COLLAPSE_STORAGE_KEY);
  } catch {
    //
  }
};

const handleSidebarViewportChange = () => {
  applySidebarCollapseState();
  nextTick(() => syncNavOffset());
};

const toggleSidebarCollapse = () => {
  if (!isDesktopViewport()) {
    openDrawer();
    return;
  }

  sidebarCollapsed.value = !sidebarCollapsed.value;
  saveSidebarCollapsePreference();
  applySidebarCollapseState();

  nextTick(() => {
    syncNavOffset();
  });
};

const setGlobalNavOffset = () => {
  if (typeof document === "undefined") return;
  document.documentElement.style.setProperty("--sgpc-nav-offset", `${navOffset.value}px`);
};

const syncNavOffset = () => {
  if (!headerEl.value) return;
  navOffset.value = Math.ceil(headerEl.value.offsetHeight || 66);
  setGlobalNavOffset();
};

const updateNavbarState = () => {
  if (typeof window === "undefined") return;
  const currentY = Math.max(window.scrollY || 0, 0);
  isScrolled.value = currentY > 8;
};

const navigateTo = (target, replace = false) => {
  closeAllPanels();

  const resolved = router.resolve(target);
  if (resolved.fullPath === route.fullPath) return null;

  return replace ? router.replace(target) : router.push(target);
};

const openDrawer = () => {
  drawerOpen.value = true;
  accountOpen.value = false;
  closeSearchPanel(false);
};

const closeDrawer = () => {
  drawerOpen.value = false;
};

const toggleAccount = async () => {
  if (accountOpen.value) {
    closeAccount(true);
    return;
  }

  accountOpen.value = true;
  closeSearchPanel(false);

  if (typeof window !== "undefined" && window.matchMedia?.("(max-width: 980px)")?.matches) {
    drawerOpen.value = false;
  }

  await nextTick();
  accountCard.value?.focus?.();
};

const closeAccount = (restoreFocus = false) => {
  accountOpen.value = false;

  if (restoreFocus) {
    nextTick(() => {
      accountTrigger.value?.focus?.();
    });
  }
};

const closeSearchPanel = (restoreFocus = false) => {
  searchPanelOpen.value = false;
  activeIndex.value = -1;
  scholarStore.clearSuggestions?.();

  if (restoreFocus) {
    nextTick(() => {
      searchTrigger.value?.focus?.();
    });
  }
};

const closeAllPanels = () => {
  closeDrawer();
  closeAccount(false);
  closeSearchPanel(false);
};

const toggleDarkMode = () => {
  uiDarkMode.value = !uiDarkMode.value;
};

const go = (path) => navigateTo(path);

const isRouteActive = (...paths) =>
  paths.some((path) => route.path === path || route.path.startsWith(`${path}/`));

const goHomeFromLogo = () => {
  navigateTo(isAuthenticated.value ? "/home" : "/login");
};

const goAvisos = () => {
  /*
   * Los avisos se controlan desde AvisosGlobalHost.
   * No se modifica la ruta ni se agrega ?modal=avisos,
   * porque eso puede activar nuevamente observadores de Home
   * y abrir una segunda instancia del overlay.
   */
  closeAllPanels();

  if (typeof window === "undefined") return;

  window.dispatchEvent(
    new CustomEvent("sgpc:open-avisos", {
      detail: {
        mode: "viewer",
      },
    })
  );
};

const goMyScholarProfile = () => {
  navigateTo("/perfil/me");
};

const goMyAccount = () => {
  navigateTo("/profile");
};

const goConfig = () => {
  navigateTo("/preferencias");
};

const goAdminPanel = () => {
  navigateTo("/admin/panel");
};

const logout = async () => {
  closeAllPanels();

  try {
    await userStore.logout?.();
  } catch {
    //
  }

  userStore.clearUser?.();
  scholarStore.clearAll?.();

  if (route.path !== "/login") {
    await router.replace("/login");
  }
};

const normalizeSuggestionKind = (kind) => {
  const value = String(kind || "").trim().toLowerCase();

  if (
    value.includes("profile") ||
    value.includes("perfil") ||
    value.includes("author") ||
    value.includes("autor") ||
    value.includes("investigador")
  ) {
    return "profile";
  }

  if (
    value.includes("publication") ||
    value.includes("publicacion") ||
    value.includes("paper") ||
    value.includes("article") ||
    value.includes("articulo") ||
    value.includes("work")
  ) {
    return "publication";
  }

  if (value.includes("project") || value.includes("proyecto")) {
    return "project";
  }

  if (
    value.includes("keyword") ||
    value.includes("topic") ||
    value.includes("tema") ||
    value.includes("tag")
  ) {
    return "keyword";
  }

  return "suggestion";
};

const normalizedSuggestions = computed(() => {
  const raw = Array.isArray(scholarStore.suggestions) ? scholarStore.suggestions : [];

  return raw
    .map((item, index) => {
      const label = String(item?.label || "").trim();
      if (!label) return null;

      const kind = normalizeSuggestionKind(item?.kind);

      return {
        ...item,
        kind,
        label,
        extra: String(item?.extra || "").trim(),
        _flatIndex: index,
        _key: `${kind}:${item?.id ?? label}:${index}`,
        _optionId: `sgpc-nav-option-${index}`,
      };
    })
    .filter(Boolean);
});

const showCommandBody = computed(() => {
  const q = queryLocal.value.trim();
  return suggestLoading.value || normalizedSuggestions.value.length > 0 || q.length >= 2;
});

const activeDescendantId = computed(() => {
  const item = normalizedSuggestions.value[activeIndex.value];
  return item?._optionId || "";
});

const openSearchPanel = async () => {
  const q = queryLocal.value.trim();

  searchPanelOpen.value = true;
  activeIndex.value = -1;
  accountOpen.value = false;

  if (typeof window !== "undefined" && window.matchMedia?.("(max-width: 980px)")?.matches) {
    drawerOpen.value = false;
  }

  await nextTick();
  searchInput.value?.focus?.();

  if (q.length >= 2) {
    await scholarStore.suggestSmart?.(q);
  } else {
    scholarStore.clearSuggestions?.();
  }
};

const toggleSearch = async () => {
  if (searchPanelOpen.value) {
    closeSearchPanel(true);
    return;
  }

  await openSearchPanel();
};

const scrollActiveIntoView = async () => {
  await nextTick();

  const id = activeDescendantId.value;
  if (!id || typeof document === "undefined") return;

  const node = document.getElementById(id);
  node?.scrollIntoView?.({
    block: "nearest",
    inline: "nearest",
  });
};

const onInput = async () => {
  const q = queryLocal.value.trim();

  activeIndex.value = -1;

  if (q.length < 2) {
    scholarStore.clearSuggestions?.();
    return;
  }

  await scholarStore.suggestSmart?.(q);
};

const move = async (dir) => {
  const max = normalizedSuggestions.value.length - 1;
  if (max < 0) return;

  const next = activeIndex.value + dir;

  if (next < 0) activeIndex.value = max;
  else if (next > max) activeIndex.value = 0;
  else activeIndex.value = next;

  await scrollActiveIntoView();
};

const submitSearch = () => {
  const q = queryLocal.value.trim();

  if (!q) {
    closeSearchPanel(true);
    return;
  }

  navigateTo({
    path: "/busqueda",
    query: { q },
  });
};

const applySuggestion = (suggestion) => {
  if (!suggestion) return;

  const id = suggestion.id ?? suggestion.value ?? suggestion.pk ?? "";
  const label = String(suggestion.label || "").trim();
  const q = label || queryLocal.value.trim();

  if (suggestion.kind === "publication" && id) {
    navigateTo(`/publicacion/${id}`);
    return;
  }

  if (suggestion.kind === "profile" && id) {
    navigateTo(`/perfil/${id}`);
    return;
  }

  if (suggestion.kind === "project") {
    navigateTo({
      path: "/proyectos-listado",
      query: q ? { q } : {},
    });
    return;
  }

  navigateTo({
    path: "/busqueda",
    query: q ? { q } : {},
  });
};

const acceptActive = () => {
  const item = normalizedSuggestions.value[activeIndex.value];

  if (item) {
    applySuggestion(item);
    return;
  }

  submitSearch();
};

const buildSuggestionSubtitle = (suggestion) => {
  const extra = String(suggestion?.extra || "").trim();

  if (extra) return extra;

  if (suggestion.kind === "publication") return "Publicación científica";
  if (suggestion.kind === "profile") return "Perfil académico";
  if (suggestion.kind === "project") return "Proyecto";
  if (suggestion.kind === "keyword") return "Tema de búsqueda";

  return "Sugerencia";
};

const kindIconPath = (kind) => {
  if (kind === "profile") {
    return "M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z";
  }

  if (kind === "publication") {
    return "M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5L14 3.5ZM8 12h8v2H8v-2Zm0 4h8v2H8v-2Z";
  }

  if (kind === "project") {
    return "M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z";
  }

  return "M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z";
};

const escapeHtml = (value) =>
  String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

const escapeRegExp = (value) =>
  String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const highlight = (label, query) => {
  const safeLabel = escapeHtml(label);
  const q = String(query || "").trim();

  if (!q) return safeLabel;

  try {
    const regex = new RegExp(`(${escapeRegExp(q)})`, "ig");
    return safeLabel.replace(regex, "<mark>$1</mark>");
  } catch {
    return safeLabel;
  }
};

const onClickOutside = (event) => {
  const target = event.target;

  if (
    accountOpen.value &&
    accountWrap.value &&
    !accountWrap.value.contains(target)
  ) {
    closeAccount(false);
  }

  if (
    searchPanelOpen.value &&
    searchPanel.value &&
    searchTrigger.value &&
    !searchPanel.value.contains(target) &&
    !searchTrigger.value.contains(target)
  ) {
    closeSearchPanel(false);
  }
};

const onEsc = (event) => {
  if (event.key !== "Escape") return;
  closeAllPanels();
};

const onGlobalShortcut = (event) => {
  const key = String(event.key || "").toLowerCase();

  if ((event.ctrlKey || event.metaKey) && key === "k") {
    event.preventDefault();
    toggleSearch();
  }
};

watch(
  () => route.fullPath,
  async () => {
    closeDrawer();
    closeAccount(false);
    closeSearchPanel(false);

    queryLocal.value = String(route.query?.q || "");

    await nextTick();
    syncNavOffset();
    updateNavbarState();
  }
);

watch(
  () => shouldLockScroll.value,
  (value) => {
    if (typeof document === "undefined") return;
    document.documentElement.classList.toggle("sgpc-nav-lock", value);
    document.body.classList.toggle("sgpc-nav-lock", value);
  }
);

watch(
  () => userAvatar.value,
  () => {
    avatarBroken.value = false;
  }
);

onMounted(async () => {
  loaded.value = true;
  queryLocal.value = String(route.query?.q || "");

  loadSidebarCollapsePreference();
  applySidebarCollapseState();

  await nextTick();
  syncNavOffset();
  updateNavbarState();

  if (typeof window !== "undefined") {
    window.addEventListener("scroll", updateNavbarState, { passive: true });
    window.addEventListener("keydown", onGlobalShortcut);
    window.addEventListener("resize", syncNavOffset, { passive: true });
    window.addEventListener("resize", handleSidebarViewportChange, { passive: true });
  }

  if (typeof ResizeObserver !== "undefined" && headerEl.value) {
    headerResizeObserver = new ResizeObserver(() => {
      syncNavOffset();
    });
    headerResizeObserver.observe(headerEl.value);
  }

  if (typeof document !== "undefined") {
    document.addEventListener("click", onClickOutside);
    document.addEventListener("keydown", onEsc);
    setGlobalNavOffset();
  }

  if (typeof userStore.bootstrapAuth === "function") {
    await userStore.bootstrapAuth({ force: true });
  } else {
    await userStore.hydrate?.();
    await userStore.refreshProfile?.().catch(() => null);
  }

  if (userStore.isAuthenticated && !String(userStore.autorId || "").trim()) {
    try {
      const { data } = await import("../../scripts/api/axios").then((mod) =>
        mod.default.get("/scholar/perfiles/me/")
      );

      const authorId = data?.id;

      if (authorId != null) {
        userStore.setAutorId?.(authorId);
      }
    } catch {
      //
    }
  }

  await nextTick();
  syncNavOffset();
});

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.documentElement.classList.remove("sgpc-nav-lock");
    document.documentElement.classList.remove("sgpc-sidebar-collapsed");
    document.body.classList.remove("sgpc-nav-lock");
    document.removeEventListener("click", onClickOutside);
    document.removeEventListener("keydown", onEsc);
    document.documentElement.style.removeProperty("--sgpc-nav-offset");
  }

  if (typeof window !== "undefined") {
    window.removeEventListener("scroll", updateNavbarState);
    window.removeEventListener("keydown", onGlobalShortcut);
    window.removeEventListener("resize", syncNavOffset);
    window.removeEventListener("resize", handleSidebarViewportChange);
  }

  if (headerResizeObserver) {
    headerResizeObserver.disconnect();
    headerResizeObserver = null;
  }
});
</script>

<style src="./barra-navegacion.css"></style>