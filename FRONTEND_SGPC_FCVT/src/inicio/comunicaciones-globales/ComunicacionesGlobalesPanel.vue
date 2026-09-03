<template>
  <section
    v-if="items.length"
    class="global-comms"
  >
    <article
      v-for="item in items"
      :key="item.id"
      class="global-comms__item"
      :data-kind="item.tipo"
    >
      <div>
        <span>{{ label(item.tipo) }}</span>
        <h2>{{ item.titulo }}</h2>
        <p>{{ item.mensaje }}</p>
      </div>

      <button
        v-if="item.ruta_accion"
        type="button"
        @click="open(item)"
      >
        {{ item.etiqueta_accion || "Revisar" }}
      </button>
    </article>
  </section>
</template>

<script setup>
import {
  onMounted,
  ref,
} from "vue";
import { useRouter } from "vue-router";

import {
  asResults,
  listarComunicaciones,
} from "../../scripts/api/actualizacionesApi";

const router = useRouter();
const items = ref([]);

const label = (value) => ({
  informacion: "Información",
  actualizacion: "Actualización",
  importante: "Importante",
  mantenimiento: "Mantenimiento",
}[value] || "Comunicado");

const shouldHideFromHome = (item) => {
  // Los avisos de actualización de datos se gestionan mediante el modal
  // de inicio de sesión y el centro de notificaciones. No deben ocupar una
  // franja permanente en Inicio, aunque la comunicación haya sido creada
  // manualmente y no tenga una campaña asociada.
  return item?.tipo === "actualizacion";
};

async function load() {
  try {
    const payload =
      await listarComunicaciones();

    const normalized = asResults(payload);

    items.value = normalized.filter(
      (item) => !shouldHideFromHome(item)
    );
  } catch {
    items.value = [];
  }
}

function open(item) {
  const route = String(
    item.ruta_accion || ""
  );

  if (/^https?:\/\//i.test(route)) {
    window.open(
      route,
      "_blank",
      "noopener,noreferrer"
    );
    return;
  }

  router.push(
    route.startsWith("/")
      ? route
      : `/${route}`
  );
}

onMounted(load);
</script>

<style src="./comunicaciones-globales.css"></style>
