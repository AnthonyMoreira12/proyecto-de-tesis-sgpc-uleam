import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

/* ==========================================================
   ESTILOS GLOBALES

   theme.css define los tokens del tema.
   sgpc-content-system.css define la base visual compartida de
   Publicaciones, Mis publicaciones, Proyectos, Perfil académico
   y Notificaciones.

   IMPORTANTE:
   sgpc-content-system.css se importa UNA sola vez aquí. No debe
   volver a cargarse mediante <style src="..."> en los SFC Vue.
========================================================== */
import "./assets/styles/theme.css";
import "./assets/styles/sgpc-content-system.css";

import { useUserStore } from "./scripts/stores/userStore";
import { useThemeStore } from "./scripts/stores/themeStore";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

// Tema global
const themeStore = useThemeStore(pinia);
themeStore.init();

// Usuario
const userStore = useUserStore(pinia);
userStore.hydrate();

app.use(router);
app.mount("#app");
