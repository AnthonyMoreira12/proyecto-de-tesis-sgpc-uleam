import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      "@": fileURLToPath(
        new URL(
          "./src",
          import.meta.url
        )
      ),
    },
  },

  server: {
    port: 5173,

    /*
     * El proxy se conserva como respaldo para módulos que puedan
     * utilizar rutas relativas /api durante desarrollo.
     *
     * Se usa "localhost" también en Django para no mezclar
     * localhost y 127.0.0.1 dentro del flujo de autenticación.
     */
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },

      "/media": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
