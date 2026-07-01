import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

/* Orden de imports:
   - estilos compartidos de administración
   - tema global al final
*/
import "./assets/styles/theme.css";
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

// ============================================================
// 🛡️ MANEJADOR GLOBAL DE ERRORES (Previene la "pantalla blanca")
// ============================================================
app.config.errorHandler = (err, instance, info) => {
  // 1. Imprimir el error en la consola para los desarrolladores
  console.error("🚨 [Vue Global Error]:", err);
  console.info("💡 [Info de Vue]:", info);

  // 2. Mostrar un mensaje amigable al usuario en lugar de congelar la pantalla
  // (Nota: Si tu proyecto usa una librería de notificaciones como SweetAlert2 o Toastify, 
  // puedes usarla aquí en lugar de un 'alert' normal).
  alert("Ups... Ha ocurrido un error inesperado en la interfaz. Por favor, recarga la página para continuar.");
};

// Finalmente montamos la aplicación
app.mount("#app");