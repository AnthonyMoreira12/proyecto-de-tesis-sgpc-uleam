<template>
  <main class="tipos-container">
    <section
      class="tipos-shell page-stage page-stage-1"
      aria-labelledby="tipos-title"
    >
      <header class="tipos-header">
        <h1
          id="tipos-title"
          class="tipos-header__title"
        >
          Seleccione el tipo de publicación
        </h1>

        <p class="tipos-header__description">
          Elija la categoría de producción científica que desea registrar.
        </p>
      </header>

      <div
        class="tipos-grid page-stage page-main page-stage-2"
        role="list"
        aria-label="Tipos de publicación disponibles"
      >
        <RouterLink
          v-for="tipo in tipos"
          :key="tipo.code"
          :to="tipo.to"
          class="tipo-card"
          :data-tipo="tipo.code"
          :aria-label="`Registrar ${tipo.label}`"
          role="listitem"
        >
          <div class="tipo-card__top">
            <span
              class="tipo-card__icon"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                focusable="false"
              >
                <path
                  :d="tipo.iconPath"
                  fill="currentColor"
                />
              </svg>
            </span>

            <span class="tipo-card__code">
              {{ tipo.code }}
            </span>
          </div>

          <strong class="tipo-card__title">
            {{ tipo.label }}
          </strong>

          <span class="tipo-card__action">
            <span>Registrar</span>

            <svg
              viewBox="0 0 20 20"
              fill="none"
              focusable="false"
              aria-hidden="true"
            >
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
    iconPath:
      "M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5L14 3.5ZM8 12h8v2H8v-2Zm0 4h5v2H8v-2Z",
    to: {
      name: "RegistroArticuloAltoImpacto",
    },
  },
  {
    code: "AR",
    label: "Artículos regionales",
    iconPath:
      "M12 2a10 10 0 1 1 0 20 10 10 0 0 1 0-20Zm0 2c-.74 0-1.82 1.26-2.42 4h4.84C13.82 5.26 12.74 4 12 4ZM7.54 8C7.88 6.37 8.45 5 9.13 4.02A8.05 8.05 0 0 0 4.59 8h2.95Zm8.92 0h2.95a8.05 8.05 0 0 0-4.54-3.98c.68.98 1.25 2.35 1.59 3.98ZM4.07 10a8.4 8.4 0 0 0 0 4h3.18a22.32 22.32 0 0 1 0-4H4.07Zm5.2 0a20.23 20.23 0 0 0 0 4h5.46a20.23 20.23 0 0 0 0-4H9.27Zm7.48 0a22.32 22.32 0 0 1 0 4h3.18a8.4 8.4 0 0 0 0-4h-3.18ZM4.59 16a8.05 8.05 0 0 0 4.54 3.98C8.45 19 7.88 17.63 7.54 16H4.59Zm4.99 0c.6 2.74 1.68 4 2.42 4s1.82-1.26 2.42-4H9.58Zm6.88 0c-.34 1.63-.91 3-1.59 3.98A8.05 8.05 0 0 0 19.41 16h-2.95Z",
    to: {
      name: "RegistroArticuloRegional",
    },
  },
  {
    code: "PON",
    label: "Ponencias",
    iconPath:
      "M4 3h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-6v2h3v2H7v-2h3v-2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm0 2v10h16V5H4Zm3 2h6v2H7V7Zm0 4h10v2H7v-2Z",
    to: {
      name: "RegistroPonencia",
    },
  },
  {
    code: "LIB",
    label: "Libros",
    iconPath:
      "M4 3h6a3 3 0 0 1 3 3v13.08A5.96 5.96 0 0 0 9 17H4V3Zm10 3a3 3 0 0 1 3-3h3v14h-5a5.96 5.96 0 0 0-4 2.08V6a1 1 0 0 1 1-1h2v1Zm3-1a1 1 0 0 0-1 1v9.1c.65-.07 1.32-.1 2-.1V5h-1Z",
    to: {
      name: "RegistroLibro",
    },
  },
  {
    code: "CAP",
    label: "Capítulos de libro",
    iconPath:
      "M6 2h10a2 2 0 0 1 2 2v2h1a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-2H5a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h1Zm0 2H5v12h1V4Zm2 4v12h11V8H8Zm2 3h7v2h-7v-2Zm0 4h7v2h-7v-2Z",
    to: {
      name: "RegistroCapituloLibro",
    },
  },
];
</script>

<style src="./tipos-publicacion.css"></style>
