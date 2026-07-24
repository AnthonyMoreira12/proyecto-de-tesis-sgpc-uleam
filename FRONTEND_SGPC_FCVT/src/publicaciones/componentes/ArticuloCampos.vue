<template>
  <section
    class="art-campos"
    aria-label="Información del artículo científico"
  >
    <!-- =====================================================
         INFORMACIÓN PRINCIPAL
    ====================================================== -->

    <article class="art-card art-card--main">
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">
            Artículo científico
          </p>

          <h3 class="art-card__title">
            Datos del artículo
          </h3>

          <p class="art-card__desc">
            Complete la información base del artículo, la revista y los enlaces
            de consulta.
          </p>
        </div>

        <span
          class="art-card__badge"
          :data-tipo="tipoVisual"
        >
          {{ tipoLabel }}
        </span>
      </header>

      <div class="art-grid">
        <!-- =================================================
             TÍTULO
        ================================================== -->

        <label
          class="art-field art-field--span-12"
          :class="{
            'art-field--invalid': hasFieldError('nombre_articulo'),
          }"
        >
          <span class="art-label">
            Título del artículo
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <input
            :value="form.nombre_articulo || ''"
            class="art-input"
            type="text"
            maxlength="255"
            placeholder="Ej. Evaluación de la producción científica..."
            :disabled="disabled"
            :aria-invalid="hasFieldError('nombre_articulo')"
            :aria-describedby="
              hasFieldError('nombre_articulo')
                ? fieldErrorId('nombre_articulo')
                : undefined
            "
            required
            @input="
              updateField(
                'nombre_articulo',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('nombre_articulo')"
            :id="fieldErrorId('nombre_articulo')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("nombre_articulo") }}
          </small>
        </label>

        <!-- =================================================
             REVISTA
        ================================================== -->

        <label
          class="art-field art-field--span-6"
          :class="{
            'art-field--invalid': hasFieldError('nombre_revista'),
          }"
        >
          <span class="art-label">
            Nombre de la revista
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <input
            :value="form.nombre_revista || ''"
            class="art-input"
            type="text"
            maxlength="255"
            placeholder="Ej. Revista Científica..."
            :disabled="disabled"
            :aria-invalid="hasFieldError('nombre_revista')"
            :aria-describedby="
              hasFieldError('nombre_revista')
                ? fieldErrorId('nombre_revista')
                : undefined
            "
            required
            @input="
              updateField(
                'nombre_revista',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('nombre_revista')"
            :id="fieldErrorId('nombre_revista')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("nombre_revista") }}
          </small>
        </label>

        <!-- =================================================
             ISSN
        ================================================== -->

        <label
          class="art-field art-field--span-6"
          :class="{
            'art-field--invalid': hasFieldError('codigo_issn'),
          }"
        >
          <span class="art-label">
            Código ISSN
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <input
            :value="form.codigo_issn || ''"
            class="art-input"
            type="text"
            maxlength="100"
            placeholder="Ej. 1234-5678"
            :disabled="disabled"
            :aria-invalid="hasFieldError('codigo_issn')"
            :aria-describedby="
              hasFieldError('codigo_issn')
                ? fieldErrorId('codigo_issn')
                : undefined
            "
            required
            @input="
              updateField(
                'codigo_issn',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('codigo_issn')"
            :id="fieldErrorId('codigo_issn')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("codigo_issn") }}
          </small>
        </label>

        <!-- =================================================
             NÚMERO DE REVISTA
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('numero_revista'),
          }"
        >
          <span class="art-label">
            N.º de revista
          </span>

          <input
            :value="form.numero_revista ?? ''"
            class="art-input"
            type="number"
            min="1"
            step="1"
            inputmode="numeric"
            placeholder="Opcional"
            :disabled="disabled"
            :aria-invalid="hasFieldError('numero_revista')"
            :aria-describedby="
              hasFieldError('numero_revista')
                ? fieldErrorId('numero_revista')
                : undefined
            "
            @input="
              updateField(
                'numero_revista',
                normalizeOptionalNumber($event.target.value)
              )
            "
          />

          <small
            v-if="hasFieldError('numero_revista')"
            :id="fieldErrorId('numero_revista')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("numero_revista") }}
          </small>
        </label>

        <!-- =================================================
             DOI
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('codigo_doi'),
          }"
        >
          <span class="art-label">
            DOI
          </span>

          <input
            :value="form.codigo_doi || ''"
            class="art-input"
            type="text"
            maxlength="150"
            placeholder="10.xxxx/xxxxx"
            :disabled="disabled"
            :aria-invalid="hasFieldError('codigo_doi')"
            :aria-describedby="
              hasFieldError('codigo_doi')
                ? fieldErrorId('codigo_doi')
                : undefined
            "
            @input="
              updateField(
                'codigo_doi',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('codigo_doi')"
            :id="fieldErrorId('codigo_doi')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("codigo_doi") }}
          </small>
        </label>

        <!-- =================================================
             LINK REVISTA
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('link_revista'),
          }"
        >
          <span class="art-label">
            Link de la revista
          </span>

          <input
            :value="form.link_revista || ''"
            class="art-input"
            type="url"
            inputmode="url"
            maxlength="500"
            placeholder="https://..."
            :disabled="disabled"
            :aria-invalid="hasFieldError('link_revista')"
            :aria-describedby="
              hasFieldError('link_revista')
                ? fieldErrorId('link_revista')
                : undefined
            "
            @input="
              updateField(
                'link_revista',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('link_revista')"
            :id="fieldErrorId('link_revista')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("link_revista") }}
          </small>
        </label>

        <!-- =================================================
             LINK PUBLICACIÓN
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('link_publicacion'),
          }"
        >
          <span class="art-label">
            Link de publicación
          </span>

          <input
            :value="form.link_publicacion || ''"
            class="art-input"
            type="url"
            inputmode="url"
            maxlength="500"
            placeholder="https://..."
            :disabled="disabled"
            :aria-invalid="hasFieldError('link_publicacion')"
            :aria-describedby="
              hasFieldError('link_publicacion')
                ? fieldErrorId('link_publicacion')
                : undefined
            "
            @input="
              updateField(
                'link_publicacion',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('link_publicacion')"
            :id="fieldErrorId('link_publicacion')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("link_publicacion") }}
          </small>
        </label>
      </div>
    </article>

    <!-- =====================================================
         ARTÍCULO REGIONAL
    ====================================================== -->

    <article
      v-if="esRegional"
      class="art-card art-card--regional"
    >
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">
            Indexación regional
          </p>

          <h3 class="art-card__title">
            Base de datos / indexación
          </h3>

          <p class="art-card__desc">
            Esta sección aplica únicamente para artículos regionales.
          </p>
        </div>
      </header>

      <div class="art-grid">
        <!-- =================================================
             BASE INDEXADA
        ================================================== -->

        <label
          class="art-field art-field--span-6"
          :class="{
            'art-field--invalid': hasFieldError(
              'base_datos_indexada'
            ),
          }"
        >
          <span class="art-label">
            Base indexada
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <select
            :value="form.base_datos_indexada || ''"
            class="art-input art-select"
            :disabled="disabled"
            :aria-invalid="hasFieldError('base_datos_indexada')"
            :aria-describedby="
              hasFieldError('base_datos_indexada')
                ? fieldErrorId('base_datos_indexada')
                : undefined
            "
            required
            @change="
              updateField(
                'base_datos_indexada',
                $event.target.value
              )
            "
          >
            <option value="">
              Seleccione una base
            </option>

            <option
              v-for="base in basesRegional"
              :key="base.value"
              :value="base.value"
            >
              {{ base.label }}
            </option>
          </select>

          <small
            v-if="hasFieldError('base_datos_indexada')"
            :id="fieldErrorId('base_datos_indexada')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("base_datos_indexada") }}
          </small>
        </label>

        <!-- =================================================
             OTRA BASE
        ================================================== -->

        <label
          v-if="form.base_datos_indexada === 'otra'"
          class="art-field art-field--span-6"
          :class="{
            'art-field--invalid': hasFieldError('base_datos_otra'),
          }"
        >
          <span class="art-label">
            Especifique la base
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <input
            :value="form.base_datos_otra || ''"
            class="art-input"
            type="text"
            maxlength="150"
            placeholder="Nombre de la base o índice"
            :disabled="disabled"
            :aria-invalid="hasFieldError('base_datos_otra')"
            :aria-describedby="
              hasFieldError('base_datos_otra')
                ? fieldErrorId('base_datos_otra')
                : undefined
            "
            required
            @input="
              updateField(
                'base_datos_otra',
                $event.target.value
              )
            "
          />

          <small
            v-if="hasFieldError('base_datos_otra')"
            :id="fieldErrorId('base_datos_otra')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("base_datos_otra") }}
          </small>
        </label>
      </div>
    </article>

    <!-- =====================================================
         ARTÍCULO DE ALTO IMPACTO
    ====================================================== -->

    <article
      v-if="esAltoImpacto"
      class="art-card art-card--impacto"
    >
      <header class="art-card__head">
        <div>
          <p class="art-card__kicker">
            Alto impacto
          </p>

          <h3 class="art-card__title">
            Impacto, cuartil y SJR
          </h3>

          <p class="art-card__desc">
            Esta sección aplica únicamente para artículos de alto impacto.
          </p>
        </div>
      </header>

      <div class="art-grid">
        <!-- =================================================
             FACTOR DE IMPACTO
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('factor_impacto'),
          }"
        >
          <span class="art-label">
            Factor de impacto
          </span>

          <select
            :value="form.factor_impacto || ''"
            class="art-input art-select"
            :disabled="disabled"
            :aria-invalid="hasFieldError('factor_impacto')"
            :aria-describedby="
              hasFieldError('factor_impacto')
                ? fieldErrorId('factor_impacto')
                : undefined
            "
            @change="
              updateField(
                'factor_impacto',
                $event.target.value
              )
            "
          >
            <option value="">
              No aplica / no disponible
            </option>

            <option
              v-for="factor in factoresImpacto"
              :key="factor.value"
              :value="factor.value"
            >
              {{ factor.label }}
            </option>
          </select>

          <small
            v-if="hasFieldError('factor_impacto')"
            :id="fieldErrorId('factor_impacto')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("factor_impacto") }}
          </small>
        </label>

        <!-- =================================================
             CUARTIL
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('cuartil'),
          }"
        >
          <span class="art-label">
            Cuartil
          </span>

          <select
            :value="normalizedQuartile"
            class="art-input art-select"
            :disabled="disabled"
            :aria-invalid="hasFieldError('cuartil')"
            :aria-describedby="
              hasFieldError('cuartil')
                ? fieldErrorId('cuartil')
                : undefined
            "
            @change="
              updateField(
                'cuartil',
                normalizeQuartile($event.target.value)
              )
            "
          >
            <option value="">
              Seleccione un cuartil
            </option>

            <option
              v-for="cuartil in cuartiles"
              :key="cuartil.value"
              :value="cuartil.value"
            >
              {{ cuartil.label }}
            </option>
          </select>

          <small
            v-if="hasFieldError('cuartil')"
            :id="fieldErrorId('cuartil')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("cuartil") }}
          </small>
        </label>

        <!-- =================================================
             SJR
        ================================================== -->

        <label
          class="art-field art-field--span-4"
          :class="{
            'art-field--invalid': hasFieldError('sjr'),
          }"
        >
          <span class="art-label">
            SJR

            <span
              v-if="form.factor_impacto === 'sjr'"
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </span>

          <input
            :value="form.sjr || ''"
            class="art-input"
            type="text"
            inputmode="decimal"
            maxlength="100"
            placeholder="Ej. 0.75"
            :disabled="
              disabled ||
              form.factor_impacto !== 'sjr'
            "
            :required="form.factor_impacto === 'sjr'"
            :aria-invalid="hasFieldError('sjr')"
            :aria-describedby="sjrDescriptionIds"
            @input="
              updateField(
                'sjr',
                $event.target.value
              )
            "
          />

          <small
            :id="`${componentId}-sjr-help`"
            class="art-help"
          >
            Solo se habilita cuando el factor de impacto seleccionado es SJR.
          </small>

          <small
            v-if="hasFieldError('sjr')"
            :id="fieldErrorId('sjr')"
            class="art-error"
            role="alert"
          >
            {{ fieldError("sjr") }}
          </small>
        </label>
      </div>
    </article>
  </section>
</template>

<script setup>
import {
  computed,
  useId,
  watch,
} from "vue";


defineOptions({
  name: "ArticuloCampos",
});


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


const emit = defineEmits([
  "update:modelValue",
  "change",
]);


/* =========================================================
   IDENTIFICADOR ACCESIBLE
========================================================= */

const componentId =
  `articulo-campos-${useId().replaceAll(":", "")}`;


const fieldErrorId = (field) => (
  `${componentId}-${field}-error`
);


/* =========================================================
   LÍMITES DEL BACKEND
========================================================= */

const FIELD_LIMITS = Object.freeze({
  nombre_articulo: 255,
  base_datos_otra: 150,
  codigo_doi: 150,
  codigo_issn: 100,
  nombre_revista: 255,
  link_revista: 500,
  link_publicacion: 500,
  sjr: 100,
});


/* =========================================================
   CATÁLOGOS
========================================================= */

const basesRegional = Object.freeze([
  {
    value: "latindex",
    label: "Latindex",
  },
  {
    value: "scielo",
    label: "SciELO",
  },
  {
    value: "redalyc",
    label: "Redalyc",
  },
  {
    value: "dialnet",
    label: "Dialnet",
  },
  {
    value: "google_scholar",
    label: "Google Scholar",
  },
  {
    value: "otra",
    label: "Otra",
  },
]);


const factoresImpacto = Object.freeze([
  {
    value: "sjr",
    label: "SJR",
  },
  {
    value: "jcr",
    label: "JCR",
  },
]);


const cuartiles = Object.freeze([
  {
    value: "q1",
    label: "Q1",
  },
  {
    value: "q2",
    label: "Q2",
  },
  {
    value: "q3",
    label: "Q3",
  },
  {
    value: "q4",
    label: "Q4",
  },
  {
    value: "sin_cuartil",
    label: "Sin cuartil",
  },
]);


/* =========================================================
   MODELO
========================================================= */

const form = computed(() => (
  props.modelValue &&
  typeof props.modelValue === "object"
    ? props.modelValue
    : {}
));


/* =========================================================
   TIPO DE ARTÍCULO
========================================================= */

const normalizeArticleType = (value) => {
  const normalized = String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");

  if (
    [
      "ar",
      "regional",
      "articulo_regional",
    ].includes(normalized)
  ) {
    return "articulo_regional";
  }

  if (
    [
      "aai",
      "alto_impacto",
      "articulo_alto_impacto",
    ].includes(normalized)
  ) {
    return "articulo_alto_impacto";
  }

  return normalized;
};


const tipoCodigo = computed(() => {
  return normalizeArticleType(
    form.value.tipo_codigo ||
    form.value.tipo_articulo ||
    ""
  );
});


const esRegional = computed(() => (
  tipoCodigo.value ===
  "articulo_regional"
));


const esAltoImpacto = computed(() => (
  tipoCodigo.value ===
  "articulo_alto_impacto"
));


const tipoVisual = computed(() => {
  if (esRegional.value) {
    return "regional";
  }

  if (esAltoImpacto.value) {
    return "alto-impacto";
  }

  return "articulo";
});


const tipoLabel = computed(() => {
  if (esRegional.value) {
    return "Artículo regional";
  }

  if (esAltoImpacto.value) {
    return "Artículo de alto impacto";
  }

  return "Artículo";
});


/* =========================================================
   NORMALIZACIÓN
========================================================= */

const normalizeQuartile = (value) => {
  const normalized = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");

  if (
    [
      "sin_cuartil",
      "sincuartil",
    ].includes(normalized)
  ) {
    return "sin_cuartil";
  }

  return normalized;
};


const normalizedQuartile = computed(() => (
  normalizeQuartile(
    form.value.cuartil
  )
));


const normalizeOptionalNumber = (value) => {
  if (
    value === "" ||
    value === null ||
    value === undefined
  ) {
    return null;
  }

  const number = Number(value);

  if (
    !Number.isFinite(number)
  ) {
    return null;
  }

  return number;
};


/* =========================================================
   ERRORES
========================================================= */

const normalizeError = (value) => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "";
  }

  if (Array.isArray(value)) {
    return value
      .map(normalizeError)
      .filter(Boolean)
      .join(" ");
  }

  if (
    typeof value === "object"
  ) {
    return Object.values(value)
      .map(normalizeError)
      .filter(Boolean)
      .join(" ");
  }

  return String(value).trim();
};


const fieldError = (field) => (
  normalizeError(
    props.errors?.[field]
  )
);


const hasFieldError = (field) => (
  Boolean(
    fieldError(field)
  )
);


const sjrDescriptionIds =
  computed(() => {
    const ids = [
      `${componentId}-sjr-help`,
    ];

    if (
      hasFieldError("sjr")
    ) {
      ids.push(
        fieldErrorId("sjr")
      );
    }

    return ids.join(" ");
  });


/* =========================================================
   ACTUALIZACIÓN DEL MODELO
========================================================= */

const emitPatch = (patch) => {
  const current =
    form.value;

  const hasChanges =
    Object.entries(
      patch
    ).some(
      ([key, value]) => (
        !Object.is(
          current[key],
          value
        )
      )
    );

  if (!hasChanges) {
    return;
  }

  const next = {
    ...current,
    ...patch,
  };

  emit(
    "update:modelValue",
    next
  );

  emit(
    "change",
    next
  );
};


const updateField = (
  field,
  value
) => {
  const patch = {
    [field]: value,
  };

  /* =======================================================
     BASE REGIONAL
  ======================================================== */

  if (
    field ===
      "base_datos_indexada" &&
    value !== "otra"
  ) {
    patch.base_datos_otra =
      "";
  }

  /* =======================================================
     FACTOR DE IMPACTO
  ======================================================== */

  if (
    field ===
      "factor_impacto" &&
    value !== "sjr"
  ) {
    patch.sjr =
      "";
  }

  emitPatch(patch);
};


/* =========================================================
   COHERENCIA ENTRE TIPOS
========================================================= */

watch(
  tipoCodigo,

  (tipo) => {
    /*
     * REGIONAL
     *
     * El backend obliga a eliminar:
     *
     * - factor_impacto
     * - cuartil
     * - sjr
     */
    if (
      tipo ===
      "articulo_regional"
    ) {
      emitPatch({
        tipo_codigo:
          "articulo_regional",

        tipo_articulo:
          "regional",

        factor_impacto:
          "",

        cuartil:
          "",

        sjr:
          "",
      });

      return;
    }

    /*
     * ALTO IMPACTO
     *
     * El backend obliga a eliminar:
     *
     * - base_datos_indexada
     * - base_datos_otra
     */
    if (
      tipo ===
      "articulo_alto_impacto"
    ) {
      emitPatch({
        tipo_codigo:
          "articulo_alto_impacto",

        tipo_articulo:
          "alto_impacto",

        base_datos_indexada:
          "",

        base_datos_otra:
          "",
      });
    }
  },

  {
    immediate: true,
  }
);
</script>

<style
  scoped
  src="./articulo-campos.css"
></style>