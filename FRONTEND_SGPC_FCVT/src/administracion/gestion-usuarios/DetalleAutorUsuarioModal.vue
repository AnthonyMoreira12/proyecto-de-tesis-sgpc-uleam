<template>
  <div class="sgpc-admin-modal modal-overlay" @click.self="emit('close')">
    <div
      class="modal modal--author-detail"
      role="dialog"
      aria-modal="true"
      aria-label="Detalle del usuario"
    >
      <header class="modal__header authordetail-header">
        <div class="authordetail-headcopy">
          <div class="authordetail-topline">
            <span class="authordetail-kicker">Detalle</span>

            <span
              v-if="usuario?.creado_desde_selector"
              class="authordetail-badge"
            >
              Creado desde selector
            </span>
          </div>

          <h2 class="modal__title authordetail-title">
            {{ fullName }}
          </h2>

          <p class="authordetail-subtitle">
            Relación del usuario con el autor y sus publicaciones enlazadas.
          </p>
        </div>

        <button
          type="button"
          class="modal__close authordetail-close"
          @click="emit('close')"
          aria-label="Cerrar"
          title="Cerrar"
        >
          ✕
        </button>
      </header>

      <div class="modal__body authordetail-body">
        <section class="authordetail-section">
          <h3 class="authordetail-sectiontitle">Resumen</h3>

          <div class="authordetail-summary">
            <div class="authordetail-item">
              <span>Correo</span>
              <strong>{{ usuario?.email || "—" }}</strong>
            </div>

            <div class="authordetail-item">
              <span>Identificación</span>
              <strong>{{ usuario?.identificacion || "—" }}</strong>
            </div>

            <div class="authordetail-item">
              <span>Estado</span>
              <strong>{{ estadoLabel }}</strong>
            </div>

            <div class="authordetail-item">
              <span>Tipo</span>
              <strong>{{ tipoLabel }}</strong>
            </div>

            <div class="authordetail-item authordetail-item--wide">
              <span>Autor vinculado</span>
              <strong>{{ usuario?.autor_nombre || "Sin autor vinculado" }}</strong>
            </div>

            <div class="authordetail-item">
              <span>Publicaciones</span>
              <strong>{{ usuario?.total_publicaciones || 0 }}</strong>
            </div>
          </div>
        </section>

        <section class="authordetail-section">
          <div class="authordetail-sectionrow">
            <h3 class="authordetail-sectiontitle">Publicaciones relacionadas</h3>

            <span class="authordetail-count">
              {{ publicaciones.length }} registro(s)
            </span>
          </div>

          <div v-if="!publicaciones.length" class="authordetail-empty">
            Este autor no tiene publicaciones enlazadas.
          </div>

          <div v-else class="authordetail-pubs">
            <article
              v-for="pub in publicaciones"
              :key="`${pub.publicacion_id}-${pub.orden}-${pub.rol_autoria}`"
              class="authordetail-pub"
            >
              <div class="authordetail-pubmain">
                <strong>{{ pub.label }}</strong>

                <div class="authordetail-pubmeta">
                  <span>{{ pub.tipo || "Publicación" }}</span>
                  <span>Año: {{ pub.anio_publicacion || "—" }}</span>
                  <span>Orden: {{ pub.orden || "—" }}</span>
                </div>
              </div>

              <span class="authordetail-pill">
                {{ pub.rol_label }}
              </span>
            </article>
          </div>
        </section>
      </div>

      <footer class="modal__footer authordetail-footer">
        <button
          type="button"
          class="authordetail-btn"
          @click="emit('close')"
        >
          Cerrar
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  usuario: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);

const fullName = computed(() => {
  const nombres = String(props.usuario?.nombres || "").trim();
  const apellidos = String(props.usuario?.apellidos || "").trim();
  return `${nombres} ${apellidos}`.trim() || "Usuario";
});

const publicaciones = computed(() => {
  return Array.isArray(props.usuario?.publicaciones_relacionadas)
    ? props.usuario.publicaciones_relacionadas
    : [];
});

const estadoLabel = computed(() => {
  if (!props.usuario) return "—";

  if (
    String(props.usuario?.rol || "").toLowerCase() === "autor_externo" &&
    String(props.usuario?.auth_source || "").toLowerCase() === "local" &&
    !props.usuario?.is_active
  ) {
    return "Pendiente";
  }

  return props.usuario?.is_active ? "Activo" : "Inactivo";
});

const tipoLabel = computed(() => {
  if (!props.usuario) return "—";

  if (String(props.usuario?.auth_source || "").toLowerCase() === "microsoft") {
    return "Institucional";
  }

  if (String(props.usuario?.rol || "").toLowerCase() === "autor_externo") {
    return "Externo";
  }

  return "Usuario";
});
</script>

<style src="../styles/admin-shared.css"></style>
<style scoped src="./detalle-autor-usuario-modal.css"></style>