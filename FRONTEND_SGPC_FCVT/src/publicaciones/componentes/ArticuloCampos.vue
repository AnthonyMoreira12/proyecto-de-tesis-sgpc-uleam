<template>
  <section class="art-campos">
    <article class="art-card art-card--main">
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">Artículo científico</p>
          <h3 class="art-card__title">Datos del artículo</h3>
          <p class="art-card__desc">
            Complete la información base del artículo, la revista y los enlaces de consulta.
          </p>
        </div>

        <span class="art-card__badge" :data-tipo="tipoVisual">
          {{ tipoLabel }}
        </span>
      </header>

      <div class="art-grid">
        <label class="art-field art-field--span-12">
          <span class="art-label">Título del artículo</span>
          <input
            :value="form.nombre_articulo"
            class="art-input"
            type="text"
            placeholder="Ej. Evaluación de la producción científica..."
            :disabled="disabled"
            @input="updateField('nombre_articulo', $event.target.value)"
          />
          <small v-if="fieldError('nombre_articulo')" class="art-error">
            {{ fieldError("nombre_articulo") }}
          </small>
        </label>

        <label class="art-field art-field--span-6">
          <span class="art-label">Nombre de la revista</span>
          <input
            :value="form.nombre_revista"
            class="art-input"
            type="text"
            placeholder="Nombre oficial de la revista"
            :disabled="disabled"
            @input="updateField('nombre_revista', $event.target.value)"
          />
          <small v-if="fieldError('nombre_revista')" class="art-error">
            {{ fieldError("nombre_revista") }}
          </small>
        </label>

        <label class="art-field art-field--span-3">
          <span class="art-label">ISSN</span>
          <input
            :value="form.codigo_issn"
            class="art-input"
            type="text"
            placeholder="0000-0000"
            :disabled="disabled"
            @input="updateField('codigo_issn', $event.target.value)"
          />
          <small v-if="fieldError('codigo_issn')" class="art-error">
            {{ fieldError("codigo_issn") }}
          </small>
        </label>

        <label class="art-field art-field--span-3">
          <span class="art-label">N.º revista</span>
          <input
            :value="form.numero_revista"
            class="art-input"
            type="number"
            min="1"
            placeholder="Opcional"
            :disabled="disabled"
            @input="updateField('numero_revista', $event.target.value)"
          />
          <small v-if="fieldError('numero_revista')" class="art-error">
            {{ fieldError("numero_revista") }}
          </small>
        </label>

        <label class="art-field art-field--span-4">
          <span class="art-label">DOI</span>
          <input
            :value="form.codigo_doi"
            class="art-input"
            type="text"
            placeholder="10.xxxx/xxxxx"
            :disabled="disabled"
            @input="updateField('codigo_doi', $event.target.value)"
          />
          <small v-if="fieldError('codigo_doi')" class="art-error">
            {{ fieldError("codigo_doi") }}
          </small>
        </label>

        <label class="art-field art-field--span-4">
          <span class="art-label">Link de la revista</span>
          <input
            :value="form.link_revista"
            class="art-input"
            type="url"
            placeholder="https://..."
            :disabled="disabled"
            @input="updateField('link_revista', $event.target.value)"
          />
          <small v-if="fieldError('link_revista')" class="art-error">
            {{ fieldError("link_revista") }}
          </small>
        </label>

        <label class="art-field art-field--span-4">
          <span class="art-label">Link de publicación</span>
          <input
            :value="form.link_publicacion"
            class="art-input"
            type="url"
            placeholder="https://..."
            :disabled="disabled"
            @input="updateField('link_publicacion', $event.target.value)"
          />
          <small v-if="fieldError('link_publicacion')" class="art-error">
            {{ fieldError("link_publicacion") }}
          </small>
        </label>
      </div>
    </article>

    <article
      v-if="esRegional"
      class="art-card art-card--regional"
    >
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">Indexación regional</p>
          <h3 class="art-card__title">Base de datos / indexación</h3>
          <p class="art-card__desc">
            Esta sección aplica únicamente para artículos regionales.
          </p>
        </div>
      </header>

      <div class="art-grid">
        <label class="art-field art-field--span-6">
          <span class="art-label">Base indexada</span>
          <select
            :value="form.base_datos_indexada"
            class="art-input art-select"
            :disabled="disabled"
            @change="updateField('base_datos_indexada', $event.target.value)"
          >
            <option value="">Seleccione una base</option>
            <option
              v-for="base in basesRegional"
              :key="base.value"
              :value="base.value"
            >
              {{ base.label }}
            </option>
          </select>
          <small v-if="fieldError('base_datos_indexada')" class="art-error">
            {{ fieldError("base_datos_indexada") }}
          </small>
        </label>

        <label
          v-if="form.base_datos_indexada === 'otra'"
          class="art-field art-field--span-6"
        >
          <span class="art-label">Especifique la base</span>
          <input
            :value="form.base_datos_otra"
            class="art-input"
            type="text"
            placeholder="Nombre de la base o índice"
            :disabled="disabled"
            @input="updateField('base_datos_otra', $event.target.value)"
          />
          <small v-if="fieldError('base_datos_otra')" class="art-error">
            {{ fieldError("base_datos_otra") }}
          </small>
        </label>
      </div>
    </article>

    <article
      v-if="esAltoImpacto"
      class="art-card art-card--impacto"
    >
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">Alto impacto</p>
          <h3 class="art-card__title">Impacto, cuartil y SJR</h3>
          <p class="art-card__desc">
            Esta sección aplica únicamente para artículos de alto impacto.
          </p>
        </div>
      </header>

      <div class="art-grid">
        <label class="art-field art-field--span-4">
          <span class="art-label">Factor de impacto</span>
          <select
            :value="form.factor_impacto"
            class="art-input art-select"
            :disabled="disabled"
            @change="updateField('factor_impacto', $event.target.value)"
          >
            <option value="">Sin factor registrado</option>
            <option
              v-for="factor in factoresImpacto"
              :key="factor.value"
              :value="factor.value"
            >
              {{ factor.label }}
            </option>
          </select>
          <small v-if="fieldError('factor_impacto')" class="art-error">
            {{ fieldError("factor_impacto") }}
          </small>
        </label>

        <label class="art-field art-field--span-4">
          <span class="art-label">Cuartil</span>
          <select
            :value="form.cuartil"
            class="art-input art-select"
            :disabled="disabled"
            @change="updateField('cuartil', $event.target.value)"
          >
            <option value="">Seleccione un cuartil</option>
            <option
              v-for="cuartil in cuartiles"
              :key="cuartil.value"
              :value="cuartil.value"
            >
              {{ cuartil.label }}
            </option>
          </select>
          <small v-if="fieldError('cuartil')" class="art-error">
            {{ fieldError("cuartil") }}
          </small>
        </label>

        <label class="art-field art-field--span-4">
          <span class="art-label">SJR</span>
          <input
            :value="form.sjr"
            class="art-input"
            type="text"
            placeholder="Ej. 0.75"
            :disabled="disabled || form.factor_impacto !== 'sjr'"
            @input="updateField('sjr', $event.target.value)"
          />
          <small class="art-help">
            Solo requerido cuando el factor de impacto sea SJR.
          </small>
          <small v-if="fieldError('sjr')" class="art-error">
            {{ fieldError("sjr") }}
          </small>
        </label>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, watch } from "vue";
import "./articulo-campos.css";

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "change"]);

const basesRegional = [
  { value: "latindex", label: "Latindex" },
  { value: "scielo", label: "SciELO" },
  { value: "redalyc", label: "Redalyc" },
  { value: "dialnet", label: "Dialnet" },
  { value: "google_scholar", label: "Google Scholar" },
  { value: "otra", label: "Otra" },
];

const factoresImpacto = [
  { value: "sjr", label: "SJR" },
  { value: "jcr", label: "JCR" },
];

const cuartiles = [
  { value: "q1", label: "Q1" },
  { value: "q2", label: "Q2" },
  { value: "q3", label: "Q3" },
  { value: "q4", label: "Q4" },
  { value: "sin_cuartil", label: "Sin cuartil" },
];

const form = computed(() => props.modelValue || {});

const tipoCodigo = computed(() => {
  const value = String(form.value.tipo_codigo || form.value.tipo_articulo || "").trim().toLowerCase();

  if (value === "regional") return "articulo_regional";
  if (value === "alto_impacto") return "articulo_alto_impacto";

  return value;
});

const esRegional = computed(() => tipoCodigo.value === "articulo_regional");
const esAltoImpacto = computed(() => tipoCodigo.value === "articulo_alto_impacto");

const tipoVisual = computed(() => {
  if (esRegional.value) return "regional";
  if (esAltoImpacto.value) return "alto-impacto";
  return "articulo";
});

const tipoLabel = computed(() => {
  if (esRegional.value) return "Artículo regional";
  if (esAltoImpacto.value) return "Artículo de alto impacto";
  return "Artículo";
});

function normalizeError(value) {
  if (!value) return "";

  if (Array.isArray(value)) {
    return value.filter(Boolean).join(" ");
  }

  if (typeof value === "object") {
    return Object.values(value).flat().filter(Boolean).join(" ");
  }

  return String(value);
}

function fieldError(field) {
  return normalizeError(props.errors?.[field]);
}

function emitPatch(patch) {
  const next = {
    ...form.value,
    ...patch,
  };

  emit("update:modelValue", next);
  emit("change", next);
}

function updateField(field, value) {
  const patch = {
    [field]: value,
  };

  if (field === "base_datos_indexada" && value !== "otra") {
    patch.base_datos_otra = "";
  }

  if (field === "factor_impacto" && value !== "sjr") {
    patch.sjr = "";
  }

  emitPatch(patch);
}

watch(
  tipoCodigo,
  (tipo) => {
    if (!tipo) return;

    if (tipo === "articulo_regional") {
      emitPatch({
        tipo_codigo: "articulo_regional",
        tipo_articulo: "regional",
        factor_impacto: "",
        cuartil: "",
        sjr: "",
      });
      return;
    }

    if (tipo === "articulo_alto_impacto") {
      emitPatch({
        tipo_codigo: "articulo_alto_impacto",
        tipo_articulo: "alto_impacto",
        base_datos_indexada: "",
        base_datos_otra: "",
      });
    }
  },
  { immediate: true },
);
</script>