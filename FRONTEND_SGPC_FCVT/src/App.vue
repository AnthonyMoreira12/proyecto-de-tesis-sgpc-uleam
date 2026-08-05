<template>
  <div
    class="app-root"
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
        <!--
          Las rutas comparten un escenario estable.

          No se utiliza mode="out-in" ni mode="in-out" porque esos
          modos pueden dejar un fotograma intermedio o prolongar la
          coexistencia de las dos vistas.

          Cuando las animaciones están desactivadas, :css="false"
          hace que Vue cambie la vista de manera inmediata.
        -->
        <div
          class="route-transition-stage"
          :class="{
            'is-public-stage': isPublicLayout,
          }"
        >
          <Transition
            :name="getTransitionName(currentRoute)"
            :css="animations"
            :duration="
              animations
                ? routeTransitionDuration
                : 0
            "
          >
            <div
              v-if="Component"
              :key="getRouteKey(currentRoute)"
              class="route-transition-shell"
              :style="currentRoute.meta?.vars || {}"
            >
              <component :is="Component" />
            </div>
          </Transition>
        </div>
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
import { storeToRefs } from "pinia";
import { useRoute } from "vue-router";

import BarraNavegacion from "./inicio/componentes/BarraNavegacion.vue";
import FooterInstitucional from "./inicio/componentes/FooterInstitucional.vue";
import AvisosGlobalHost from "./inicio/avisos-global-host/AvisosGlobalHost.vue";

import { useThemeStore } from "./scripts/stores/themeStore";

const route = useRoute();
const themeStore = useThemeStore();

const { animations } = storeToRefs(themeStore);

/*
 * Mantiene las clases de entrada el tiempo suficiente para que
 * el indicador superior complete su animación. La salida es
 * inmediata y no deja un fotograma vacío.
 */
const routeTransitionDuration = Object.freeze({
  enter: 220,
  leave: 0,
});

/**
 * Una ruta utiliza el diseño público cuando cualquiera de sus
 * registros coincidentes tiene meta.publicLayout = true.
 */
const isPublicLayout = computed(() => {
  return route.matched.some(
    (record) =>
      record.meta?.publicLayout === true
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

/**
 * Devuelve el nombre de transición definido en la ruta.
 */
function getTransitionName(currentRoute) {
  return (
    currentRoute?.meta?.transitionName ||
    "page-assembly"
  );
}

/**
 * Clave estable para representar la interfaz.
 *
 * Se utiliza path y no fullPath para impedir que un cambio de
 * query string, filtro o hash desmonte toda la vista.
 */
function getRouteKey(currentRoute) {
  const customKey =
    currentRoute?.meta?.transitionKey;

  if (
    customKey !== undefined &&
    customKey !== null
  ) {
    return String(customKey);
  }

  return currentRoute?.path || "/";
}
</script>

<style>
/* =========================================================
   ELEMENTO DE MONTAJE
========================================================= */

/*
 * index.html contiene el único elemento con id="app".
 * La raíz de App.vue usa la clase .app-root para evitar dos
 * identificadores iguales después de app.mount("#app").
 */
#app {
  width: 100%;
  min-width: 0;

  min-height: 100vh;
  min-height: 100dvh;

  margin: 0;

  background:
    var(--bg-main, #f4f6f8);

  color:
    var(--text-primary, #111827);
}

/* =========================================================
   RAÍZ DE LA APLICACIÓN
========================================================= */

.app-root {
  display: flex;
  flex-direction: column;

  width: 100%;
  min-width: 0;

  min-height: 100vh;
  min-height: 100dvh;

  overflow-x: clip;
  overflow-y: visible;

  background:
    var(--bg-main, #f4f6f8);

  color:
    var(--text-primary, #111827);
}

html,
body {
  width: 100%;
  min-width: 0;
  min-height: 100%;

  margin: 0;

  overflow-x: clip;
  overflow-y: visible;

  background:
    var(--bg-main, #f4f6f8);

  color:
    var(--text-primary, #111827);
}

/* =========================================================
   CONTENIDO PRINCIPAL
========================================================= */

.app-main {
  flex: 1 0 auto;

  position: relative;

  width: 100%;
  min-width: 0;

  overflow: visible;

  background:
    var(--bg-main, #f4f6f8);
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

  margin-left:
    var(--sgpc-sidebar-width, 250px);

  padding-top:
    var(--sgpc-nav-offset, 78px);

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
  background:
    var(--bg-main, #f4f6f8);
}

/* =========================================================
   ESCENARIO ESTABLE DE RUTAS
========================================================= */

.route-transition-stage {
  display: grid;

  grid-template-columns:
    minmax(0, 1fr);

  grid-template-rows:
    minmax(
      calc(
        100dvh -
        var(--sgpc-nav-offset, 78px)
      ),
      auto
    );

  align-items: start;

  position: relative;
  isolation: isolate;

  width: 100%;
  min-width: 0;

  min-height: calc(
    100vh - var(--sgpc-nav-offset, 78px)
  );

  min-height: calc(
    100dvh - var(--sgpc-nav-offset, 78px)
  );

  overflow: visible;

  background:
    var(--bg-main, #f4f6f8);

  box-sizing: border-box;
}

.route-transition-stage.is-public-stage {
  grid-template-rows:
    minmax(100dvh, auto);

  min-height: 100vh;
  min-height: 100dvh;
}

/* =========================================================
   CONTENEDOR DE CADA RUTA
========================================================= */

.route-transition-stage
  > .route-transition-shell {
  grid-area: 1 / 1;
  align-self: stretch;
}

.route-transition-shell {
  position: relative;

  width: 100%;
  min-width: 0;

  min-height: calc(
    100vh - var(--sgpc-nav-offset, 78px)
  );

  min-height: calc(
    100dvh - var(--sgpc-nav-offset, 78px)
  );

  overflow: visible;

  background:
    var(--bg-main, #f4f6f8);

  color:
    var(--text-primary, #111827);

  box-sizing: border-box;
}

.route-transition-shell
  > :first-child {
  min-height: inherit;
}

.app-main.is-public
  .route-transition-shell {
  min-height: 100vh;
  min-height: 100dvh;
}

/* =========================================================
   CAPAS DURANTE EL CAMBIO DE RUTA
========================================================= */

.route-transition-stage
  > .page-assembly-enter-active,
.route-transition-stage
  > .page-premium-enter-active {
  z-index: 2;
}

.route-transition-stage
  > .page-assembly-leave-active,
.route-transition-stage
  > .page-premium-leave-active {
  z-index: 1;
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
    100vh - var(--sgpc-nav-offset, 78px)
  ) !important;

  min-height: calc(
    100dvh - var(--sgpc-nav-offset, 78px)
  ) !important;

  margin-left: 0 !important;

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

/* =========================================================
   FORMULARIOS CON RESUMEN STICKY
========================================================= */

.app-main.has-navbar
  .route-transition-shell
  > .sgpc-form-page {
  width: 100%;
  min-width: 0;
  min-height: inherit;

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
      var(--sgpc-nav-offset, 78px);

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
   MOVIMIENTO REDUCIDO
========================================================= */

html.reduced-motion
  .route-transition-stage,
html.reduced-motion
  .route-transition-shell,
html.reduced-motion
  .route-transition-shell
  :is(
    .page-stage,
    .page-stagger > *
  ) {
  opacity: 1 !important;
  visibility: visible !important;

  transform: none !important;
  filter: none !important;

  animation: none !important;
  transition: none !important;
}

@media (prefers-reduced-motion: reduce) {
  .app-main.has-navbar,
  .app-footer-with-navbar,
  .route-transition-stage,
  .route-transition-shell,
  .route-transition-shell
    :is(
      .page-stage,
      .page-stagger > *
    ) {
    opacity: 1 !important;
    visibility: visible !important;

    transform: none !important;
    filter: none !important;

    animation: none !important;
    transition: none !important;
  }
}
</style>
