<template>
  <div id="app">
    <BarraNavegacion v-if="showNavbar" />

    <div
      v-if="showNavbar"
      class="app-navbar-spacer"
      aria-hidden="true"
    ></div>

    <main class="app-main">
      <RouterView v-slot="{ Component, route }">
        <Transition
          :name="route.meta?.transitionName || 'page-assembly'"
          mode="out-in"
          appear
        >
          <div
            :key="route.fullPath"
            class="route-transition-shell"
            :style="route.meta?.vars || {}"
          >
            <component :is="Component" />
          </div>
        </Transition>
      </RouterView>
    </main>

    <FooterInstitucional v-if="showFooter" />

    <AvisosGlobalHost />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import BarraNavegacion from "./inicio/componentes/BarraNavegacion.vue";
import FooterInstitucional from "./inicio/componentes/FooterInstitucional.vue";
import AvisosGlobalHost from "./inicio/avisos-global-host/AvisosGlobalHost.vue";

const route = useRoute();

const HIDE_NAVBAR_PATHS = ["/login", "/reset-password"];
const HIDE_FOOTER_PATHS = ["/login"];

const showNavbar = computed(() => !HIDE_NAVBAR_PATHS.includes(route.path));
const showFooter = computed(() => !HIDE_FOOTER_PATHS.includes(route.path));
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-navbar-spacer {
  flex: 0 0 auto;
  height: 72px;
}

.app-main {
  flex: 1 0 auto;
  min-width: 0;
}

.route-transition-shell {
  min-width: 0;
  width: 100%;
}

@media (max-width: 860px) {
  .app-navbar-spacer {
    height: 126px;
  }
}

@media (max-width: 560px) {
  .app-navbar-spacer {
    height: 122px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .route-transition-shell {
    animation: none !important;
    transition: none !important;
  }
}
</style>