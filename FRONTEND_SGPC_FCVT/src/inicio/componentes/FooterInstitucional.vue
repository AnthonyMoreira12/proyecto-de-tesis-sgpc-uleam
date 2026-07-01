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
            <img
              src="../../assets/LOGO-ULEAM-VERTICAL.png"
              alt="Logo ULEAM"
              class="sgpc-footer__brand-logo"
            />

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

        <section class="sgpc-footer__contact" aria-label="Información de contacto">
          <h2 class="sgpc-footer__title">Contacto institucional</h2>

          <div class="sgpc-footer__contact-list">
            <p class="sgpc-footer__contact-item">
              <span class="sgpc-footer__contact-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
                  <path
                    d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linejoin="round"
                  />
                  <circle
                    cx="12"
                    cy="10"
                    r="2.4"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />
                </svg>
              </span>

              <span class="sgpc-footer__contact-text">
                Av. Circunvalación Vía a San Mateo
              </span>
            </p>

            <a
              class="sgpc-footer__contact-item sgpc-footer__contact-link"
              href="mailto:incidencias.diit@uleam.edu.ec"
            >
              <span class="sgpc-footer__contact-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
                  <path
                    d="M4 6h16v12H4z"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M4 7l8 6 8-6"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <span class="sgpc-footer__contact-text">
                incidencias.diit@uleam.edu.ec
              </span>
            </a>
          </div>
        </section>
      </div>

      <div class="sgpc-footer__bottom">
        <div class="sgpc-footer__bottom-copy">
          <p class="sgpc-footer__bottom-text">
            <span>Copyright © {{ currentYear }}, todos los derechos reservados</span>

            <span class="sgpc-footer__bottom-sep" aria-hidden="true">|</span>

            <span>
              <strong class="sgpc-footer__bottom-strong">ULEAM</strong>
            </span>

            <span class="sgpc-footer__bottom-sep" aria-hidden="true">|</span>

            <span>
              Plataforma implementada por la
              <strong class="sgpc-footer__bottom-strong">
                Dirección de Informática e Innovación Tecnológica
              </strong>
            </span>
          </p>
        </div>
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

  window.scrollTo({ top: 0, behavior: "smooth" });
};
</script>

<style src="./footer-sgpc.css"></style>