<template>
  <main class="tipos-container">
    <section class="tipos-shell">
      <header class="tipos-hero page-stage page-hero page-stage-1">
        <p class="tipos-kicker">Registro</p>
        <h1 class="tipos-title">Seleccionar tipo de publicación</h1>
      </header>

      <div
        class="tipos-grid page-stage page-main page-stage-2"
        aria-label="Tipos de publicación disponibles"
      >
        <RouterLink
          v-for="tipo in tipos"
          :key="tipo.code"
          :to="tipo.to"
          class="tipo-card"
          :data-tipo="tipo.code"
          :aria-label="`Ir al registro de ${tipo.label}`"
        >
          <span class="tipo-card__topline" aria-hidden="true"></span>

          <div class="tipo-card__head">
            <span class="tipo-card__code">{{ tipo.code }}</span>
          </div>

          <div class="tipo-card__body">
            <h2 class="tipo-card__title">{{ tipo.label }}</h2>
          </div>

          <span class="tipo-card__cta">
            Continuar
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M4.5 10H15.5M15.5 10L10.75 5.25M15.5 10L10.75 14.75"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
        </RouterLink>
      </div>
    </section>
  </main>
</template>

<script setup>
const tipos = [
  {
    code: "AAI",
    label: "Artículos de alto impacto",
    to: { name: "RegistroArticuloAltoImpacto" },
  },
  {
    code: "AR",
    label: "Artículos regionales",
    to: { name: "RegistroArticuloRegional" },
  },
  {
    code: "PON",
    label: "Ponencias",
    to: { name: "RegistroPonencia" },
  },
  {
    code: "LIB",
    label: "Libros",
    to: { name: "RegistroLibro" },
  },
  {
    code: "CAP",
    label: "Capítulos de libro",
    to: { name: "RegistroCapituloLibro" },
  },
];
</script>

<style src="./tipos-publicacion.css"></style>