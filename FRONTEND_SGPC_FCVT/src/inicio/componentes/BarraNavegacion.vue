<template>
  <div
    class="sgpc-nav"
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
      @click="closePanelsFromOverlay"
    ></div>

    <aside
      class="sgpc-nav__drawer"
      :class="{ 'is-open': drawerOpen }"
      aria-label="Menú de navegación"
    >
      <div class="sgpc-nav__drawer-head">
        <button
          class="sgpc-nav__iconbtn"
          type="button"
          aria-label="Cerrar menú"
          @click="closeDrawer"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              d="M18 6 6 18M6 6l12 12"
            />
          </svg>
        </button>

        <div class="sgpc-nav__drawer-title">SGPC ULEAM</div>
      </div>

      <nav class="sgpc-nav__drawer-nav" aria-label="Opciones del sistema">
        <div class="sgpc-nav__drawer-section-title">Principal</div>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/home', '/inicio') }"
          @click="goHomeFromLogo"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M12 3l9 8h-3v10h-5v-6H11v6H6V11H3l9-8z" />
          </svg>
          Inicio
        </button>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/tipos-publicacion') }"
          @click="go('/tipos-publicacion')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M19 11H13V5h-2v6H5v2h6v6h2v-6h6v-2z" />
          </svg>
          Registrar publicación
        </button>

        <button
          type="button"
          :class="{ 'is-active': isAvisosRouteActive }"
          @click="goAvisos"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4V5Zm2 0v10.17L8.28 14H18V5H6Zm2 2h8v2H8V7Zm0 4h6v2H8v-2Z"
            />
          </svg>
          Avisos
        </button>

        <div class="sgpc-nav__drawer-section-title">Académico</div>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/perfil/me') }"
          @click="goMyScholarProfile"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z"
            />
          </svg>
          Mi perfil académico
        </button>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/proyectos-listado') }"
          @click="go('/proyectos-listado')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z"
            />
          </svg>
          Proyectos
        </button>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/mis-publicaciones') }"
          @click="go('/mis-publicaciones')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2V5Zm2 0v14h10V5H6Z"
            />
          </svg>
          Mis publicaciones
        </button>

        <button
          type="button"
          :class="{ 'is-active': isRouteActive('/publicaciones-listado') }"
          @click="go('/publicaciones-listado')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M3 5h18v2H3V5Zm0 6h18v2H3v-2Zm0 6h18v2H3v-2Z" />
          </svg>
          {{ publicationsListLabel }}
        </button>
      </nav>
    </aside>

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
            placeholder="Buscar"
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
              <span class="sgpc-nav__command-item-title">Buscar “{{ queryLocal.trim() }}”</span>
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

    <header
      ref="headerEl"
      class="sgpc-nav__header"
      :class="{
        'is-loaded': loaded,
        'is-scrolled': isScrolled,
        'has-open-panel': drawerOpen || searchPanelOpen || accountOpen
      }"
    >
      <div class="sgpc-nav__left">
        <button
          class="sgpc-nav__iconbtn sgpc-nav__surface-btn"
          type="button"
          aria-label="Abrir menú"
          @click="openDrawer"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
            <path fill="currentColor" d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z" />
          </svg>
        </button>

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

          <div class="sgpc-nav__brand-text">
            <div class="sgpc-nav__brand-title">
              <span class="sgpc-nav__brand-highlight">SGPC</span> ULEAM
            </div>
          </div>
        </button>
      </div>

      <div class="sgpc-nav__right">
        <div class="sgpc-nav__search-wrap">
          <button
            ref="searchTrigger"
            class="sgpc-nav__search-trigger"
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
            <span class="sgpc-nav__search-trigger-text">Buscar</span>
            <span class="sgpc-nav__search-trigger-shortcut" aria-hidden="true">Ctrl K</span>
          </button>
        </div>

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
                <div class="sgpc-nav__account-links">
                  <button
                    class="sgpc-nav__account-link"
                    :class="{ 'is-active': isRouteActive('/profile') }"
                    type="button"
                    @click="goMyAccount"
                  >
                    <span class="sgpc-nav__account-link-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.97 0-9 2.24-9 5v1h18v-1c0-2.76-4.03-5-9-5Z"
                        />
                      </svg>
                    </span>
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
                    <span class="sgpc-nav__account-link-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M19.14 12.94a7.43 7.43 0 0 0 .05-.94 7.43 7.43 0 0 0-.05-.94l2.11-1.65a.5.5 0 0 0 .12-.64l-2-3.46a.5.5 0 0 0-.6-.22l-2.49 1a7.28 7.28 0 0 0-1.63-.94l-.38-2.65A.5.5 0 0 0 13.8 1h-4a.5.5 0 0 0-.49.42l-.38 2.65a7.28 7.28 0 0 0-1.63.94l-2.49-1a.5.5 0 0 0-.6.22l-2 3.46a.5.5 0 0 0 .12.64L4.46 11.06a7.43 7.43 0 0 0-.05.94 7.43 7.43 0 0 0 .05.94l-2.11 1.65a.5.5 0 0 0-.12.64l2 3.46a.5.5 0 0 0 .6.22l2.49-1a7.28 7.28 0 0 0 1.63.94l.38 2.65a.5.5 0 0 0 .49.42h4a.5.5 0 0 0 .49-.42l.38-2.65a7.28 7.28 0 0 0 1.63-.94l2.49 1a.5.5 0 0 0 .6-.22l2-3.46a.5.5 0 0 0-.12-.64Zm-7.14 2.56A3.5 3.5 0 1 1 15.5 12a3.5 3.5 0 0 1-3.5 3.5Z"
                        />
                      </svg>
                    </span>
                    <span>Preferencias de interfaz</span>
                  </button>

                  <button
                    v-if="isAdmin"
                    class="sgpc-nav__account-link"
                    :class="{ 'is-active': isRouteActive('/admin', '/admin/panel', '/admin-panel') }"
                    type="button"
                    @click="goAdminPanel"
                  >
                    <span class="sgpc-nav__account-link-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M12 2 3 6v6c0 5 3.84 9.74 9 11 5.16-1.26 9-6 9-11V6l-9-4Zm0 2.18 7 3.11V12c0 4.02-2.93 7.95-7 9.01C7.93 19.95 5 16.02 5 12V7.29l7-3.11Zm-1 4.82v6l5-3-5-3Z"
                        />
                      </svg>
                    </span>
                    <span>Panel administrativo</span>
                  </button>
                </div>

                <div class="sgpc-nav__account-theme-row">
                  <span class="sgpc-nav__account-theme-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M21 14.32A8.5 8.5 0 0 1 9.68 3a7.2 7.2 0 1 0 11.32 11.32Z"
                      />
                    </svg>
                  </span>

                  <div class="sgpc-nav__account-theme-text">
                    <div class="sgpc-nav__account-theme-title">Modo oscuro</div>
                    <div class="sgpc-nav__account-theme-sub">
                      Aplicado a toda la plataforma
                    </div>
                  </div>

                  <label class="sgpc-nav__switch" aria-label="Modo oscuro">
                    <input v-model="uiDarkMode" type="checkbox" />
                    <span class="sgpc-nav__track" aria-hidden="true">
                      <span class="sgpc-nav__thumb"></span>
                    </span>
                  </label>
                </div>

                <button
                  class="sgpc-nav__account-btn sgpc-nav__account-btn--danger"
                  type="button"
                  @click="logout"
                >
                  <span class="sgpc-nav__account-btn-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M10 3h9a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-9v-2h9V5h-9V3Zm1.59 5.59 1.41-1.42L17.83 12 13 16.83l-1.41-1.42L14 13H3v-2h11l-2.41-2.41Z"
                      />
                    </svg>
                  </span>
                  <span>Cerrar sesión</span>
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </header>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useThemeStore } from "../../scripts/stores/themeStore";
import { useRouter, useRoute } from "vue-router";
import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";
import { useScholarStore } from "../../scripts/stores/scholarStore";

const themeStore = useThemeStore();
const { darkMode } = storeToRefs(themeStore);

const uiDarkMode = computed({
  get: () => darkMode.value,
  set: (value) => themeStore.setDark(value),
});

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

const navOffset = ref(78);

const accountWrap = ref(null);
const accountTrigger = ref(null);
const accountCard = ref(null);
const searchTrigger = ref(null);
const searchPanel = ref(null);
const searchInput = ref(null);
const headerEl = ref(null);

const queryLocal = ref("");

const resolvedAvatar = ref("");
const avatarRefreshAttempted = ref(false);
const avatarRequestId = ref(0);

let headerResizeObserver = null;

const isAuthenticated = computed(() => !!userStore.isAuthenticated);
const userName = computed(() => userStore.fullName || "Usuario");
const userInitial = computed(() => userStore.inicial || "U");
const isAdmin = computed(() => !!userStore.isAdmin);

const suggestLoading = computed(() => !!scholarStore.suggestLoading);
const panelBackdropVisible = computed(
  () => drawerOpen.value || searchPanelOpen.value || accountOpen.value
);
const shouldLockScroll = computed(
  () => drawerOpen.value || searchPanelOpen.value || accountOpen.value
);
const publicationsListLabel = computed(() =>
  isAdmin.value ? "Gestión de publicaciones" : "Ver publicaciones"
);

const isAvisosRouteActive = computed(() => {
  return String(route.query?.modal || "").trim().toLowerCase() === "avisos";
});

const resolveAssetUrl = (value) => {
  const raw = String(value ?? "").trim();
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

const storedUserAvatar = computed(() => {
  return resolveAssetUrl(userStore.avatarUrl || "");
});

const userAvatar = computed(() => {
  return resolvedAvatar.value || null;
});

const preloadImage = (src) => {
  return new Promise((resolve, reject) => {
    if (!src) {
      resolve("");
      return;
    }

    const img = new Image();
    img.decoding = "async";

    img.onload = () => resolve(src);
    img.onerror = reject;
    img.src = src;

    if (img.complete) {
      resolve(src);
    }
  });
};

const syncResolvedAvatar = async (src) => {
  const requestId = ++avatarRequestId.value;

  if (!src) {
    resolvedAvatar.value = "";
    return;
  }

  try {
    await preloadImage(src);

    if (requestId === avatarRequestId.value) {
      resolvedAvatar.value = src;
    }
  } catch {
    if (requestId === avatarRequestId.value) {
      resolvedAvatar.value = "";
    }
  }
};

const ensureAvatarReady = async () => {
  if (!isAuthenticated.value) {
    avatarRefreshAttempted.value = false;
    await syncResolvedAvatar("");
    return;
  }

  if (!storedUserAvatar.value && !avatarRefreshAttempted.value) {
    avatarRefreshAttempted.value = true;
    await userStore.refreshProfile?.().catch(() => null);
  }

  await syncResolvedAvatar(resolveAssetUrl(userStore.avatarUrl || ""));
};

const setGlobalNavOffset = () => {
  if (typeof document === "undefined") return;
  document.documentElement.style.setProperty("--sgpc-nav-offset", `${navOffset.value}px`);
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

const syncNavOffset = () => {
  if (!headerEl.value) return;
  navOffset.value = Math.ceil(headerEl.value.offsetHeight || 78);
  setGlobalNavOffset();
};

const updateNavbarState = () => {
  if (typeof window === "undefined") return;
  const currentY = Math.max(window.scrollY || 0, 0);
  isScrolled.value = currentY > 10;
};

const navigateTo = (target, replace = false) => {
  closeAllPanels();

  const resolved = router.resolve(target);
  if (resolved.fullPath === route.fullPath) return;

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
  drawerOpen.value = false;
  closeSearchPanel(false);

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
  closeAccount();
  closeSearchPanel(false);
};

const closePanelsFromOverlay = () => {
  closeAllPanels();
};

const go = (path) => navigateTo(path);

const isRouteActive = (...paths) =>
  paths.some((path) => route.path === path || route.path.startsWith(`${path}/`));

const goHomeFromLogo = () => {
  navigateTo(isAuthenticated.value ? "/home" : "/login");
};

const goAvisos = () => {
  navigateTo({
    path: "/home",
    query: {
      modal: "avisos",
      ts: Date.now().toString(),
    },
  });
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

const hardLogout = async () => {
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

const logout = async () => {
  closeAllPanels();
  await hardLogout();
};

const openSearchPanel = async () => {
  const q = queryLocal.value.trim();

  searchPanelOpen.value = true;
  activeIndex.value = -1;
  accountOpen.value = false;
  drawerOpen.value = false;

  await nextTick();
  searchInput.value?.focus?.();

  if (q.length >= 2) {
    await scholarStore.suggestSmart(q);
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

  await scholarStore.suggestSmart(q);
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

const acceptActive = () => {
  const list = normalizedSuggestions.value;

  if (!list.length) {
    submitSearch();
    return;
  }

  const idx = activeIndex.value;
  if (idx >= 0 && idx < list.length) {
    applySuggestion(list[idx]);
    return;
  }

  submitSearch();
};

const kindLabel = (kind) => {
  if (kind === "publication") return "Publicación";
  if (kind === "profile") return "Investigador";
  if (kind === "project") return "Proyecto";
  if (kind === "keyword") return "Tema";
  return "Sugerencia";
};

const kindIconPath = (kind) => {
  if (kind === "publication") {
    return "M6 3h8l4 4v14H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm7 1.5V8h3.5L13 4.5ZM8 11h8v1.8H8V11Zm0 4h8v1.8H8V15Z";
  }

  if (kind === "profile") {
    return "M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z";
  }

  if (kind === "project") {
    return "M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z";
  }

  if (kind === "keyword") {
    return "M10.59 13.41a1.996 1.996 0 0 1 0-2.82l4-4a1.996 1.996 0 1 1 2.82 2.82l-4 4a1.996 1.996 0 0 1-2.82 0ZM6.59 17.41a1.996 1.996 0 0 1 0-2.82l4-4a1.996 1.996 0 1 1 2.82 2.82l-4 4a1.996 1.996 0 0 1-2.82 0Z";
  }

  return "M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z";
};

const buildSuggestionSubtitle = (suggestion) => {
  const kind = kindLabel(suggestion?.kind);
  const extra = String(suggestion?.extra || "").trim();
  return extra ? `${kind} · ${extra}` : kind;
};

const applySuggestion = (suggestion) => {
  if (!suggestion) return;

  closeAllPanels();

  if (suggestion.kind === "publication" && suggestion.id) {
    router.push(`/publicacion/${suggestion.id}`);
    return;
  }

  if (suggestion.kind === "profile" && suggestion.id) {
    const sid = String(suggestion.id).trim();

    if (userStore.autorId && sid === String(userStore.autorId).trim()) {
      router.push("/perfil/me");
      return;
    }

    const q = queryLocal.value.trim();
    router.push({
      path: `/perfil/${sid}`,
      query: q ? { q } : {},
    });
    return;
  }

  if (suggestion.kind === "project" && suggestion.id) {
    router.push({
      path: "/proyectos-listado",
      query: { q: (suggestion.label || "").trim() || undefined },
    });
    return;
  }

  queryLocal.value = (suggestion.label || queryLocal.value).trim();

  navigateTo({
    path: "/scholar",
    query: {
      q: queryLocal.value,
      scope: "pubs",
    },
  });
};

const submitSearch = async () => {
  const q = queryLocal.value.trim();

  if (!q) return;

  navigateTo({
    path: "/scholar",
    query: {
      q,
      scope: "pubs",
    },
  });
};

const escapeRegExp = (value) =>
  String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const highlight = (text, q) => {
  const source = String(text || "");
  const search = String(q || "").trim();

  if (!search || search.length < 2) return escapeHtml(source);

  const regex = new RegExp(`(${escapeRegExp(search)})`, "ig");

  return source
    .split(regex)
    .map((part, index) =>
      index % 2 === 1
        ? `<mark>${escapeHtml(part)}</mark>`
        : escapeHtml(part)
    )
    .join("");
};

const onClickOutside = (event) => {
  if (accountOpen.value) {
    const insideAcc = accountWrap.value?.contains(event.target);
    if (!insideAcc) closeAccount();
  }

  if (searchPanelOpen.value) {
    const insideSearchPanel = searchPanel.value?.contains(event.target);
    const insideSearchTrigger = searchTrigger.value?.contains(event.target);

    if (!insideSearchPanel && !insideSearchTrigger) {
      closeSearchPanel(false);
    }
  }
};

const onEsc = (event) => {
  if (event.key !== "Escape") return;

  if (drawerOpen.value) {
    closeDrawer();
    return;
  }

  if (accountOpen.value) {
    closeAccount(true);
    return;
  }

  if (searchPanelOpen.value) {
    closeSearchPanel(true);
  }
};

const onGlobalShortcut = async (event) => {
  const isModifier = event.ctrlKey || event.metaKey;
  const key = String(event.key || "").toLowerCase();

  if (!isModifier || key !== "k") return;

  event.preventDefault();
  event.stopPropagation();

  if (!searchPanelOpen.value) {
    await openSearchPanel();
    return;
  }

  searchInput.value?.focus?.();
};

watch(
  () => route.fullPath,
  async () => {
    closeDrawer();
    closeAccount();
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
  () => isAuthenticated.value,
  async (value) => {
    if (!value) {
      avatarRefreshAttempted.value = false;
      await syncResolvedAvatar("");
      return;
    }

    if (!storedUserAvatar.value && !avatarRefreshAttempted.value) {
      avatarRefreshAttempted.value = true;
      await userStore.refreshProfile?.().catch(() => null);
    }
  },
  { immediate: true }
);

watch(
  () => storedUserAvatar.value,
  async (value) => {
    await syncResolvedAvatar(value || "");
  },
  { immediate: true }
);

onMounted(async () => {
  loaded.value = true;
  queryLocal.value = String(route.query?.q || "");

  await nextTick();
  syncNavOffset();
  updateNavbarState();

  if (typeof window !== "undefined") {
    window.addEventListener("scroll", updateNavbarState, { passive: true });
    window.addEventListener("keydown", onGlobalShortcut);
    window.addEventListener("resize", syncNavOffset, { passive: true });
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
    await userStore.bootstrapAuth();
  } else {
    await userStore.hydrate?.();
  }

  await ensureAvatarReady();

  await nextTick();
  syncNavOffset();

  if (!userStore.isAuthenticated) return;

  if (!String(userStore.autorId || "").trim()) {
    try {
      const { data } = await api.get("/scholar/perfiles/me/");
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
    document.body.classList.remove("sgpc-nav-lock");
    document.removeEventListener("click", onClickOutside);
    document.removeEventListener("keydown", onEsc);
    document.documentElement.style.removeProperty("--sgpc-nav-offset");
  }

  if (typeof window !== "undefined") {
    window.removeEventListener("scroll", updateNavbarState);
    window.removeEventListener("keydown", onGlobalShortcut);
    window.removeEventListener("resize", syncNavOffset);
  }

  if (headerResizeObserver) {
    headerResizeObserver.disconnect();
    headerResizeObserver = null;
  }
});
</script>

<style src="./barra-navegacion.css"></style>