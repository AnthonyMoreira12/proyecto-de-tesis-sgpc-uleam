<template>
  <div
    id="app"
    :class="{
      'app-has-navbar': showNavbar,
      'app-public-layout': isPublicLayout,
    }"
  >
    <!-- Navegación privada del sistema -->
    <BarraNavegacion v-if="showNavbar" />

    <!-- Contenido de la ruta -->
    <main
      class="app-main"
      :class="{
        'has-navbar': showNavbar,
        'is-public': isPublicLayout,
      }"
    >
      <RouterView v-slot="{ Component, route: currentRoute }">
        <Transition
          :name="currentRoute.meta?.transitionName || 'page-assembly'"
          mode="out-in"
          appear
        >
          <div
            :key="currentRoute.fullPath"
            class="route-transition-shell"
            :style="currentRoute.meta?.vars || {}"
          >
            <component :is="Component" />
          </div>
        </Transition>
      </RouterView>
    </main>

    <!-- Pie institucional solo en interfaces privadas -->
    <FooterInstitucional
      v-if="showFooter"
      :class="{
        'app-footer-with-navbar': showNavbar,
      }"
    />

    <!-- Una sola instancia global del sistema de avisos -->
    <AvisosGlobalHost v-if="showGlobalAvisos" />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import BarraNavegacion from "./inicio/componentes/BarraNavegacion.vue";
import FooterInstitucional from "./inicio/componentes/FooterInstitucional.vue";
import AvisosGlobalHost from "./inicio/avisos-global-host/AvisosGlobalHost.vue";

const route = useRoute();

/**
 * Una ruta utiliza el diseño público cuando cualquiera de sus
 * registros coincidentes tiene meta.publicLayout = true.
 *
 * Esto funciona también con alias como:
 * /reset-password
 */
const isPublicLayout = computed(() => {
  return route.matched.some(
    (record) => record.meta?.publicLayout === true
  );
});

const showNavbar = computed(() => {
  return !isPublicLayout.value;
});

const showFooter = computed(() => {
  return !isPublicLayout.value;
});

const showGlobalAvisos = computed(() => {
  return !isPublicLayout.value;
});
</script>

<style>
#app {
  display: flex;
  flex-direction: column;

  width: 100%;
  min-width: 0;

  min-height: 100vh;
  min-height: 100dvh;

  /*
   * clip evita el desbordamiento horizontal sin crear
   * un contenedor de desplazamiento que bloquee sticky.
   */
  overflow-x: clip;
  overflow-y: visible;

  background: var(--bg-main, #f4f2ed);
}

html,
body {
  min-width: 0;
  min-height: 100%;

  margin: 0;

  /*
   * No usar hidden aquí. hidden puede crear un ancestro
   * de desplazamiento para position: sticky.
   */
  overflow-x: clip;
  overflow-y: visible;
}

/* =========================================================
   CONTENIDO PRINCIPAL
========================================================= */

.app-main {
  flex: 1 0 auto;

  position: relative;

  width: 100%;
  min-width: 0;

  /*
   * El contenido debe permitir que los componentes sticky
   * utilicen el desplazamiento principal de la ventana.
   */
  overflow: visible;
}

/* =========================================================
   DISEÑO PRIVADO CON NAVEGACIÓN
========================================================= */

.app-main.has-navbar {
  width: calc(
    100vw - var(--sgpc-sidebar-width, 250px)
  );

  max-width: calc(
    100vw - var(--sgpc-sidebar-width, 250px)
  );

  min-height: 100vh;
  min-height: 100dvh;

  margin-left: var(--sgpc-sidebar-width, 250px);

  padding-top: var(--sgpc-nav-offset, 66px);

  /*
   * clip controla únicamente el exceso horizontal.
   * visible mantiene funcional position: sticky.
   */
  overflow-x: clip;
  overflow-y: visible;

  box-sizing: border-box;

  transition:
    margin-left 190ms ease,
    width 190ms ease,
    max-width 190ms ease;
}

/* =========================================================
   DISEÑO PÚBLICO DE AUTENTICACIÓN
========================================================= */

.app-main.is-public {
  width: 100%;
  max-width: 100vw;

  min-height: 100vh;
  min-height: 100dvh;

  margin-left: 0;
  padding-top: 0;

  overflow-x: clip;
  overflow-y: visible;
}

.app-public-layout {
  background: var(--bg-main, #f4f2ed);
}

/* =========================================================
   TRANSICIÓN DE RUTAS
========================================================= */

.route-transition-shell {
  position: relative;

  width: 100%;
  min-width: 0;

  min-height: inherit;

  /*
   * No debe convertirse en un contenedor de scroll.
   */
  overflow: visible;

  box-sizing: border-box;
}

/* =========================================================
   EVITAR DOBLE DESPLAZAMIENTO
========================================================= */

.app-main.has-navbar
  .route-transition-shell
  > :is(
    .ivbi-page,
    .page-with-navbar-offset,
    .main-with-navbar-offset
  ) {
  width: 100% !important;
  max-width: 100% !important;

  min-height: calc(
    100vh - var(--sgpc-nav-offset, 66px)
  ) !important;

  min-height: calc(
    100dvh - var(--sgpc-nav-offset, 66px)
  ) !important;

  margin-left: 0 !important;

  /*
   * clip no crea el ancestro de scroll que bloqueaba sticky.
   */
  overflow-x: clip !important;
  overflow-y: visible !important;

  box-sizing: border-box !important;
}

.app-main.has-navbar
  .route-transition-shell
  > .ivbi-page {
  padding-top: 24px !important;

  padding-right:
    clamp(18px, 2vw, 34px) !important;

  padding-bottom:
    34px !important;

  padding-left:
    clamp(18px, 2vw, 34px) !important;
}

.app-main.has-navbar
  .route-transition-shell
  > :is(
    .page-with-navbar-offset,
    .main-with-navbar-offset
  ) {
  padding-top: 24px !important;
}

/* Las interfaces públicas controlan su propio espaciado */
.app-main.is-public
  .route-transition-shell {
  min-height: 100vh;
  min-height: 100dvh;

  overflow-x: clip;
  overflow-y: visible;
}

/* =========================================================
   FORMULARIOS CON RESUMEN STICKY
========================================================= */

.app-main.has-navbar
  .route-transition-shell
  > .sgpc-form-page {
  width: 100%;
  min-width: 0;

  overflow: visible !important;
}

.app-main.has-navbar
  .sgpc-form-page
  .sgpc-form-shell,
.app-main.has-navbar
  .sgpc-form-page
  .sgpc-form,
.app-main.has-navbar
  .sgpc-form-page
  .sgpc-form--with-aside {
  overflow: visible !important;
}

/* =========================================================
   FOOTER PRIVADO
========================================================= */

.app-footer-with-navbar {
  width: calc(
    100vw - var(--sgpc-sidebar-width, 250px)
  );

  max-width: calc(
    100vw - var(--sgpc-sidebar-width, 250px)
  );

  margin-left:
    var(--sgpc-sidebar-width, 250px);

  box-sizing: border-box;

  transition:
    margin-left 190ms ease,
    width 190ms ease,
    max-width 190ms ease;
}

/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 980px) {
  .app-main.has-navbar {
    width: 100%;
    max-width: 100vw;

    margin-left: 0;

    padding-top:
      var(--sgpc-nav-offset, 66px);

    overflow-x: clip;
    overflow-y: visible;
  }

  .app-footer-with-navbar {
    width: 100%;
    max-width: 100vw;

    margin-left: 0;
  }

  .app-main.has-navbar
    .route-transition-shell
    > :is(
      .ivbi-page,
      .page-with-navbar-offset,
      .main-with-navbar-offset
    ) {
    width: 100% !important;
    max-width: 100vw !important;

    margin-left: 0 !important;

    overflow-x: clip !important;
    overflow-y: visible !important;
  }

  .app-main.has-navbar
    .route-transition-shell
    > .ivbi-page {
    padding-top: 16px !important;
    padding-right: 14px !important;
    padding-left: 14px !important;
  }
}

@media (max-width: 560px) {
  .app-main.has-navbar
    .route-transition-shell
    > .ivbi-page {
    padding-right: 10px !important;
    padding-left: 10px !important;
  }
}

/* =========================================================
   ACCESIBILIDAD
========================================================= */

@media (prefers-reduced-motion: reduce) {
  .app-main.has-navbar,
  .app-footer-with-navbar,
  .route-transition-shell {
    animation: none !important;
    transition: none !important;
  }
}
</style>  