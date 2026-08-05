import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

import "./assets/styles/theme.css";

import {
  useUserStore,
} from "./scripts/stores/userStore";

import {
  useThemeStore,
} from "./scripts/stores/themeStore";

/* ============================================================
   SGPC ULEAM — ARRANQUE PRINCIPAL
============================================================ */

/*
 * Evita presentar varias alertas simultáneas cuando un mismo
 * error de renderizado se propaga por varios componentes.
 */
let globalErrorAlertVisible = false;

function showGlobalErrorAlert() {
  if (
    globalErrorAlertVisible ||
    typeof window === "undefined"
  ) {
    return;
  }

  globalErrorAlertVisible = true;

  window.setTimeout(() => {
    window.alert(
      "Ups... Ha ocurrido un error inesperado en la interfaz. " +
        "Por favor, recarga la página para continuar."
    );

    globalErrorAlertVisible = false;
  }, 0);
}

/**
 * Inicializa y monta la aplicación una sola vez.
 *
 * Orden:
 *
 * 1. Crear Vue y Pinia.
 * 2. Restaurar el tema antes del primer render.
 * 3. Restaurar la sesión del usuario.
 * 4. Instalar el router.
 * 5. Esperar la navegación inicial.
 * 6. Montar Vue.
 */
async function bootstrap() {
  const mountElement =
    document.getElementById("app");

  if (!mountElement) {
    throw new Error(
      'No se encontró el elemento de montaje "#app" en index.html.'
    );
  }

  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);

  /* =========================================================
     TEMA GLOBAL
  ========================================================= */

  /*
   * El tema se restaura antes de montar App.vue.
   *
   * Esto evita que primero aparezca el tema claro y después
   * cambie al oscuro durante el primer render.
   */
  const themeStore =
    useThemeStore(pinia);

  await Promise.resolve(
    themeStore.init()
  );

  /* =========================================================
     SESIÓN DEL USUARIO
  ========================================================= */

  /*
   * Se hidrata antes de instalar el router porque los guards
   * pueden necesitar conocer el usuario autenticado.
   *
   * Promise.resolve permite que hydrate funcione tanto si es
   * síncrono como si devuelve una promesa.
   */
  const userStore =
    useUserStore(pinia);

  await Promise.resolve(
    userStore.hydrate()
  );

  /* =========================================================
     ROUTER
  ========================================================= */

  app.use(router);

  router.onError((error) => {
    console.error(
      "🚨 [Vue Router Error]:",
      error
    );
  });

  /* =========================================================
     MANEJADOR GLOBAL DE ERRORES
  ========================================================= */

  app.config.errorHandler = (
    error,
    instance,
    info
  ) => {
    console.error(
      "🚨 [Vue Global Error]:",
      error
    );

    console.info(
      "💡 [Información de Vue]:",
      info
    );

    if (instance) {
      console.info(
        "🧩 [Componente afectado]:",
        instance
      );
    }

    showGlobalErrorAlert();
  };

  /*
   * Espera a que Vue Router complete la navegación inicial.
   *
   * Sin esta espera, App.vue puede montarse primero con el
   * RouterView vacío y renderizar la ruta unos milisegundos
   * después, produciendo un destello inicial.
   */
  await router.isReady();

  /*
   * Existe una única llamada a mount.
   */
  app.mount(mountElement);
}

/* ============================================================
   INICIO CONTROLADO
============================================================ */

bootstrap().catch((error) => {
  console.error(
    "🚨 [Error al iniciar SGPC ULEAM]:",
    error
  );

  if (
    typeof window !== "undefined"
  ) {
    window.alert(
      "No fue posible iniciar correctamente el sistema. " +
        "Recarga la página e inténtalo nuevamente."
    );
  }
});