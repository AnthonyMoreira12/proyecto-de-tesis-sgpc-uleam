<template>
  <footer class="sgpc-footer" aria-label="Pie institucional SGPC ULEAM">
    <div class="sgpc-footer__shell">
      <div class="sgpc-footer__main">
        <section class="sgpc-footer__brand" aria-label="Identidad institucional">
          <button
            class="sgpc-footer__brandbox"
            type="button"
            title="Ir al inicio"
            @click="go('/home')"
          >
            <span class="sgpc-footer__logo-wrap" aria-hidden="true">
              <img
                src="../../assets/LOGO-ULEAM-VERTICAL.png"
                alt=""
                class="sgpc-footer__brand-logo"
              />
            </span>

            <span class="sgpc-footer__brand-copy">
              <span class="sgpc-footer__brand-kicker">SGPC ULEAM</span>

              <span class="sgpc-footer__brand-title">
                Sistema de Gestión de Producción Científica
              </span>

              <span class="sgpc-footer__brand-subtitle">
                Universidad Laica Eloy Alfaro de Manabí
              </span>
            </span>
          </button>
        </section>

        <section class="sgpc-footer__support" aria-label="Soporte institucional">
          <div class="sgpc-footer__block-head">
            <span class="sgpc-footer__block-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M12 2a7 7 0 0 0-7 7v3.08A5 5 0 0 0 8 21h2v-2H8a3 3 0 0 1-3-3v-3h3V9a4 4 0 1 1 8 0v4h3v3a3 3 0 0 1-3 3h-2v2h2a5 5 0 0 0 3-8.92V9a7 7 0 0 0-7-7Z"
                />
              </svg>
            </span>

            <div class="sgpc-footer__block-copy">
              <h2 class="sgpc-footer__title">Soporte institucional</h2>
              <p class="sgpc-footer__text">
                Atención para incidencias técnicas de la plataforma.
              </p>
            </div>
          </div>

          <a
            class="sgpc-footer__link-card"
            href="mailto:incidencias.diit@uleam.edu.ec"
            aria-label="Enviar correo a incidencias.diit@uleam.edu.ec"
          >
            <span class="sgpc-footer__link-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M4 5h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Zm0 3.25 8 5.25 8-5.25V7l-8 5.25L4 7v1.25Z"
                />
              </svg>
            </span>

            <span class="sgpc-footer__link-copy">
              <strong>incidencias.diit@uleam.edu.ec</strong>
              <small>Correo de soporte técnico</small>
            </span>
          </a>
        </section>

        <section class="sgpc-footer__location" aria-label="Ubicación institucional">
          <div class="sgpc-footer__block-head">
            <span class="sgpc-footer__block-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5Z"
                />
              </svg>
            </span>

            <div class="sgpc-footer__block-copy">
              <h2 class="sgpc-footer__title">Ubicación</h2>
              <p class="sgpc-footer__text">
                Av. Circunvalación Vía a San Mateo.
              </p>
            </div>
          </div>

          <div class="sgpc-footer__badge-row">
            <span class="sgpc-footer__badge">ULEAM</span>
            <span class="sgpc-footer__badge">SGPC</span>
            <span class="sgpc-footer__badge">Producción científica</span>
          </div>
        </section>
      </div>

      <div class="sgpc-footer__bottom">
        <p class="sgpc-footer__bottom-text">
          <span>© {{ currentYear }} ULEAM.</span>
          <span>Todos los derechos reservados.</span>
          <span>
            Plataforma implementada por la
            <strong>Dirección de Informática e Innovación Tecnológica</strong>.
          </span>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const currentYear = new Date().getFullYear();

const go = (path) => {
  if (router.currentRoute.value.path !== path) {
    router.push(path);
    return;
  }

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};
</script>

<style src="./footer-sgpc.css"></style>