<template>
  <div class="sgpc-admin-page">
    <div class="adm-panel-shell">
      <section
        class="adm-panel-hero adm-surface adm-hero page-stage page-hero"
        aria-label="Panel administrativo"
      >
        <span class="adm-kicker">Administración</span>

        <h1 class="adm-panel-hero__title adm-title">Panel administrativo</h1>

        <p class="adm-panel-hero__subtitle adm-subtitle">
          Acceda a la gestión de usuarios, publicaciones, catálogos académicos y
          proyectos institucionales desde un solo panel.
        </p>
      </section>

      <section
        class="adm-panel-grid page-stage page-main"
        aria-label="Módulos administrativos"
      >
        <button
          v-for="card in cards"
          :key="card.name"
          class="adm-panel-card adm-surface"
          type="button"
          :aria-label="`Abrir módulo ${card.title}`"
          @click="go(card.name)"
        >
          <div class="adm-panel-card__head">
            <div class="adm-panel-card__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path fill="currentColor" :d="card.iconPath" />
              </svg>
            </div>

            <div class="adm-panel-card__heading">
              <h3 class="adm-panel-card__title">{{ card.title }}</h3>
              <p class="adm-panel-card__text">{{ card.text }}</p>
            </div>
          </div>

          <div class="adm-panel-card__bottom">
            <span class="adm-panel-card__hint">{{ card.hint }}</span>

            <span class="adm-panel-card__cta">
              {{ card.cta }}
              <span class="adm-panel-card__arrow" aria-hidden="true">→</span>
            </span>
          </div>
        </button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const cards = [
  {
    name: "AdminUsuarios",
    title: "Usuarios",
    text: "Gestione cuentas institucionales y externas, active accesos, ajuste permisos y controle el estado de cada usuario.",
    hint: "Cuentas, acceso y estado",
    cta: "Abrir módulo",
    iconPath:
      "M12 12a4 4 0 1 0-4-4a4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z",
  },
  {
    name: "AdminPublicaciones",
    title: "Publicaciones",
    text: "Administre publicaciones institucionales, cree registros de forma delegada en nombre de autores y controle la edición de la producción científica.",
    hint: "Creación, edición y control",
    cta: "Abrir módulo",
    iconPath:
      "M6 2h9l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5M8 12h8M8 16h8M8 20h5",
  },
  {
    name: "GestionFacultadesCarreras",
    title: "Facultades y carreras",
    text: "Administre los catálogos académicos institucionales y mantenga organizada la relación entre facultades y carreras.",
    hint: "Catálogos académicos",
    cta: "Abrir módulo",
    iconPath:
      "M3 3h8v8H3V3Zm10 0h8v8h-8V3ZM3 13h8v8H3v-8Zm10 0h8v8h-8v-8Z",
  },
  {
    name: "ProyectosListado",
    title: "Proyectos",
    text: "Gestione los proyectos registrados en el sistema y su vinculación con la producción científica institucional.",
    hint: "Registro y vinculación",
    cta: "Abrir módulo",
    iconPath:
      "M10 4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6Z",
  },
];

const go = (name) => {
  if (!name) return;
  router.push({ name });
};
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./panel-administracion.css"></style>