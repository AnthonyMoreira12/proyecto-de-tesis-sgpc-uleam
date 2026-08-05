/* ============================================================
   SGPC ULEAM
   Tipos de publicación

   Este archivo mantiene dos identificadores:

   - codigo:
     Código visual utilizado por componentes, estilos,
     badges y atributos data-tipo.

   - apiCodigo:
     Código canónico utilizado por el backend en filtros,
     listados y exportaciones.
============================================================ */

/* ============================================================
   NORMALIZACIÓN
============================================================ */

const normalizeText = (value) =>
  String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

/* ============================================================
   CÓDIGOS ADMITIDOS POR LA CAPA VISUAL
============================================================ */

const TIPOS_VALIDOS = Object.freeze([
  "AAI",
  "AR",
  "PON",
  "CAP",
  "LIB",
  "OTRO",
]);

/* ============================================================
   FÁBRICA DE METADATOS
============================================================ */

function createTipoMeta({
  codigo,
  apiCodigo = null,
  label,
  tone,
  aliases = [],
}) {
  const safeTone = tone || "otro";

  const normalizedApiCodigo = apiCodigo
    ? String(apiCodigo).trim().toLowerCase()
    : null;

  return Object.freeze({
    /*
     * Código corto para la interfaz:
     *
     * AAI
     * AR
     * PON
     * CAP
     * LIB
     */
    codigo,

    /*
     * Código oficial enviado al backend:
     *
     * articulo_alto_impacto
     * articulo_regional
     * ponencia
     * capitulo_libro
     * libro
     */
    apiCodigo: normalizedApiCodigo,

    label,
    tone: safeTone,

    color: `var(--pub-${safeTone})`,
    soft: `var(--pub-${safeTone}-soft)`,
    line: `var(--pub-${safeTone}-line)`,
    ink: `var(--pub-${safeTone}-ink)`,

    /*
     * Alias conservados por compatibilidad con componentes
     * anteriores.
     */
    colorVar: `var(--pub-${safeTone})`,
    softVar: `var(--pub-${safeTone}-soft)`,
    lineVar: `var(--pub-${safeTone}-line)`,
    inkVar: `var(--pub-${safeTone}-ink)`,

    /*
     * El atributo data-tipo conserva el código visual para no
     * alterar los selectores CSS existentes.
     */
    dataTipo: codigo,

    cssVars: Object.freeze({
      "--pub-current": `var(--pub-${safeTone})`,
      "--pub-current-soft": `var(--pub-${safeTone}-soft)`,
      "--pub-current-line": `var(--pub-${safeTone}-line)`,
      "--pub-current-ink": `var(--pub-${safeTone}-ink)`,
    }),

    aliases: Object.freeze([
      ...new Set(
        aliases
          .map((alias) => String(alias ?? "").trim())
          .filter(Boolean)
      ),
    ]),
  });
}

/* ============================================================
   TIPO DE RESPALDO
============================================================ */

const META_OTRO = createTipoMeta({
  codigo: "OTRO",
  apiCodigo: null,
  label: "Publicación",
  tone: "otro",
  aliases: [
    "otro",
    "publicacion",
    "publicación",
    "sin clasificar",
    "sin_clasificar",
  ],
});

/* ============================================================
   CATÁLOGO OFICIAL DEL FRONTEND
============================================================ */

export const PUBLICACION_TIPOS = Object.freeze({
  AAI: createTipoMeta({
    codigo: "AAI",
    apiCodigo: "articulo_alto_impacto",
    label: "Artículos de alto impacto",
    tone: "aai",
    aliases: [
      "aai",

      "articulo alto impacto",
      "articulo de alto impacto",
      "articulos de alto impacto",

      "artículo alto impacto",
      "artículo de alto impacto",
      "artículos de alto impacto",

      "alto impacto",
      "alto_impacto",

      "articulo_alto_impacto",

      "articulo alto impacto scopus",
      "articulo alto impacto wos",
      "articulo alto impacto jcr",

      "articulo q1",
      "articulo q2",
      "artículo q1",
      "artículo q2",

      "scopus",
      "wos",
      "jcr",
    ],
  }),

  AR: createTipoMeta({
    codigo: "AR",
    apiCodigo: "articulo_regional",
    label: "Artículos regionales",
    tone: "ar",
    aliases: [
      "ar",

      "articulo regional",
      "articulos regionales",

      "artículo regional",
      "artículos regionales",

      "regional",
      "articulo_regional",

      "latindex",
      "scielo",
      "redalyc",
      "dialnet",
      "google scholar",
      "google_scholar",
    ],
  }),

  PON: createTipoMeta({
    codigo: "PON",
    apiCodigo: "ponencia",
    label: "Ponencias",
    tone: "pon",
    aliases: [
      "pon",
      "ponencia",
      "ponencias",
    ],
  }),

  CAP: createTipoMeta({
    codigo: "CAP",
    apiCodigo: "capitulo_libro",
    label: "Capítulos de libro",
    tone: "cap",
    aliases: [
      "cap",

      "capitulo",
      "capitulos",
      "capítulo",
      "capítulos",

      "capitulo libro",
      "capitulos libro",
      "capítulo libro",
      "capítulos libro",

      "capitulo de libro",
      "capitulos de libro",
      "capítulo de libro",
      "capítulos de libro",

      "capitulo_libro",

      "book chapter",
      "chapter",
    ],
  }),

  LIB: createTipoMeta({
    codigo: "LIB",
    apiCodigo: "libro",
    label: "Libros",
    tone: "lib",
    aliases: [
      "lib",
      "libro",
      "libros",
      "book",
      "books",
    ],
  }),

  OTRO: META_OTRO,
});

/* ============================================================
   OPCIONES PARA DASHBOARD

   Se conservan los códigos visuales para no romper el
   comportamiento existente del dashboard.
============================================================ */

export const TIPO_PUBLICACION_OPTIONS_DASHBOARD = Object.freeze([
  {
    value: PUBLICACION_TIPOS.AAI.codigo,
    apiValue: PUBLICACION_TIPOS.AAI.apiCodigo,
    label: PUBLICACION_TIPOS.AAI.label,
  },
  {
    value: PUBLICACION_TIPOS.AR.codigo,
    apiValue: PUBLICACION_TIPOS.AR.apiCodigo,
    label: PUBLICACION_TIPOS.AR.label,
  },
  {
    value: PUBLICACION_TIPOS.PON.codigo,
    apiValue: PUBLICACION_TIPOS.PON.apiCodigo,
    label: PUBLICACION_TIPOS.PON.label,
  },
  {
    value: PUBLICACION_TIPOS.CAP.codigo,
    apiValue: PUBLICACION_TIPOS.CAP.apiCodigo,
    label: PUBLICACION_TIPOS.CAP.label,
  },
  {
    value: PUBLICACION_TIPOS.LIB.codigo,
    apiValue: PUBLICACION_TIPOS.LIB.apiCodigo,
    label: PUBLICACION_TIPOS.LIB.label,
  },
]);

/* ============================================================
   MAPA DE ALIASES
============================================================ */

const EXACT_ALIAS_TO_CODE = (() => {
  const map = new Map();

  for (
    const [codigo, meta]
    of Object.entries(PUBLICACION_TIPOS)
  ) {
    /*
     * Código corto.
     */
    map.set(
      normalizeText(codigo),
      codigo
    );

    /*
     * Código corto contenido en el objeto.
     */
    map.set(
      normalizeText(meta.codigo),
      codigo
    );

    /*
     * Código canónico del backend.
     */
    if (meta.apiCodigo) {
      map.set(
        normalizeText(meta.apiCodigo),
        codigo
      );
    }

    /*
     * Alias históricos.
     */
    for (const alias of meta.aliases) {
      map.set(
        normalizeText(alias),
        codigo
      );
    }
  }

  return map;
})();

/* ============================================================
   RESOLUCIÓN DEL CÓDIGO VISUAL
============================================================ */

export const resolveTipoPublicacionCodigo = (input) => {
  const raw = normalizeText(input);

  if (!raw) {
    return "OTRO";
  }

  const upperRaw = String(
    input ?? ""
  )
    .trim()
    .toUpperCase();

  if (TIPOS_VALIDOS.includes(upperRaw)) {
    return upperRaw;
  }

  if (EXACT_ALIAS_TO_CODE.has(raw)) {
    return EXACT_ALIAS_TO_CODE.get(raw);
  }

  /*
   * Reconocimiento auxiliar para respuestas antiguas o datos
   * que no contienen un código explícito.
   */

  if (
    raw.includes("alto impacto") ||
    raw.includes("q1") ||
    raw.includes("q2") ||
    raw.includes("scopus") ||
    raw.includes("wos") ||
    raw.includes("jcr")
  ) {
    return "AAI";
  }

  if (
    raw.includes("regional") ||
    raw.includes("latindex") ||
    raw.includes("scielo") ||
    raw.includes("redalyc") ||
    raw.includes("dialnet")
  ) {
    return "AR";
  }

  if (
    raw === "pon" ||
    raw.includes("ponencia")
  ) {
    return "PON";
  }

  if (
    raw.includes("capitulo de libro") ||
    raw.includes("capítulo de libro") ||
    raw.includes("capitulo libro") ||
    raw.includes("capítulo libro") ||
    raw === "capitulo" ||
    raw === "capítulo" ||
    raw === "cap" ||
    raw.includes("book chapter") ||
    raw === "chapter"
  ) {
    return "CAP";
  }

  if (
    raw === "lib" ||
    raw === "libro" ||
    raw === "libros" ||
    raw === "book" ||
    raw === "books"
  ) {
    return "LIB";
  }

  return "OTRO";
};

/* ============================================================
   RESOLUCIÓN DEL CÓDIGO OFICIAL DEL BACKEND
============================================================ */

export const resolveTipoPublicacionApiCodigo = (input) => {
  const codigo = resolveTipoPublicacionCodigo(
    input
  );

  return (
    PUBLICACION_TIPOS[codigo]?.apiCodigo
    || null
  );
};

/* ============================================================
   METADATOS DESDE UN VALOR
============================================================ */

export const getTipoPublicacionMeta = (input) => {
  const codigo = resolveTipoPublicacionCodigo(
    input
  );

  return (
    PUBLICACION_TIPOS[codigo]
    || META_OTRO
  );
};

/* ============================================================
   METADATOS DESDE UNA PUBLICACIÓN
============================================================ */

export const getTipoPublicacionMetaFromItem = (item) => {
  /*
   * La respuesta oficial del backend expone:
   *
   * tipo_publicacion_final
   * tipo_publicacion_final_label
   *
   * Se priorizan estos campos antes de intentar resolver
   * estructuras históricas.
   */

  const directCandidates = [
    item?.tipo_publicacion_final,
    item?.tipo_codigo,
    item?.codigo,
    item?.id,
  ];

  for (const candidate of directCandidates) {
    const code = resolveTipoPublicacionCodigo(
      candidate
    );

    if (code !== "OTRO") {
      return (
        PUBLICACION_TIPOS[code]
        || META_OTRO
      );
    }
  }

  const candidates = [
    item?.tipo_publicacion_final,
    item?.tipo_publicacion_final_label,

    item?.tipo_codigo,
    item?.tipo,

    item?.codigo,
    item?.label,
    item?.nombre,

    item?.subtipo,
    item?.categoria,
    item?.clasificacion,

    item?.base_datos_indexada,
    item?.cuartil,
    item?.revista_indexada,
    item?.indice,
  ];

  for (const candidate of candidates) {
    const codigo = resolveTipoPublicacionCodigo(
      candidate
    );

    if (codigo !== "OTRO") {
      return (
        PUBLICACION_TIPOS[codigo]
        || META_OTRO
      );
    }
  }

  const blob = candidates
    .map((value) => normalizeText(value))
    .filter(Boolean)
    .join(" ");

  const fallbackCode = resolveTipoPublicacionCodigo(
    blob
  );

  return (
    PUBLICACION_TIPOS[fallbackCode]
    || META_OTRO
  );
};

/* ============================================================
   CÓDIGO OFICIAL DESDE UNA PUBLICACIÓN
============================================================ */

export const getTipoPublicacionApiCodigoFromItem = (item) => {
  return (
    getTipoPublicacionMetaFromItem(item)
      .apiCodigo
    || null
  );
};

/* ============================================================
   HELPERS VISUALES
============================================================ */

export const getTipoPublicacionTone = (input) =>
  getTipoPublicacionMeta(input).tone;

export const getTipoPublicacionToneFromItem = (item) =>
  getTipoPublicacionMetaFromItem(item).tone;

export const getTipoPublicacionColor = (input) =>
  getTipoPublicacionMeta(input).color;

export const getTipoPublicacionColorFromItem = (item) =>
  getTipoPublicacionMetaFromItem(item).color;

export const getTipoPublicacionCssVars = (input) =>
  getTipoPublicacionMeta(input).cssVars;

export const getTipoPublicacionCssVarsFromItem = (item) =>
  getTipoPublicacionMetaFromItem(item).cssVars;

export const getTipoPublicacionDataTipo = (input) =>
  getTipoPublicacionMeta(input).dataTipo;

export const getTipoPublicacionDataTipoFromItem = (item) =>
  getTipoPublicacionMetaFromItem(item).dataTipo;

/* ============================================================
   EXPORTACIONES AUXILIARES
============================================================ */

export {
  normalizeText,
};