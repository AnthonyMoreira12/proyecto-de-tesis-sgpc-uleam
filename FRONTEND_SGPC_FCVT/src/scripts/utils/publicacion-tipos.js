const normalizeText = (value) =>
  String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

const TIPOS_VALIDOS = ["AAI", "AR", "PON", "CAP", "LIB", "OTRO"];

function createTipoMeta({ codigo, label, tone, aliases = [] }) {
  const safeTone = tone || "otro";

  return Object.freeze({
    codigo,
    label,
    tone: safeTone,

    color: `var(--pub-${safeTone})`,
    soft: `var(--pub-${safeTone}-soft)`,
    line: `var(--pub-${safeTone}-line)`,
    ink: `var(--pub-${safeTone}-ink)`,

    colorVar: `var(--pub-${safeTone})`,
    softVar: `var(--pub-${safeTone}-soft)`,
    lineVar: `var(--pub-${safeTone}-line)`,
    inkVar: `var(--pub-${safeTone}-ink)`,

    dataTipo: codigo,

    cssVars: Object.freeze({
      "--pub-current": `var(--pub-${safeTone})`,
      "--pub-current-soft": `var(--pub-${safeTone}-soft)`,
      "--pub-current-line": `var(--pub-${safeTone}-line)`,
      "--pub-current-ink": `var(--pub-${safeTone}-ink)`,
    }),

    aliases: Object.freeze([...aliases]),
  });
}

const META_OTRO = createTipoMeta({
  codigo: "OTRO",
  label: "Publicación",
  tone: "otro",
  aliases: ["otro", "publicacion", "publicación"],
});

export const PUBLICACION_TIPOS = Object.freeze({
  AAI: createTipoMeta({
    codigo: "AAI",
    label: "Artículos de alto impacto",
    tone: "aai",
    aliases: [
      "aai",
      "articulo alto impacto",
      "articulo de alto impacto",
      "articulos de alto impacto",
      "artículo de alto impacto",
      "artículos de alto impacto",
      "alto impacto",
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
    ],
  }),

  PON: createTipoMeta({
    codigo: "PON",
    label: "Ponencias",
    tone: "pon",
    aliases: ["pon", "ponencia", "ponencias"],
  }),

  CAP: createTipoMeta({
    codigo: "CAP",
    label: "Capítulos de libro",
    tone: "cap",
    aliases: [
      "cap",
      "capitulo",
      "capitulos",
      "capítulo",
      "capítulos",
      "capitulo libro",
      "capítulos libro",
      "capítulo libro",
      "capitulo de libro",
      "capítulos de libro",
      "capítulo de libro",
      "capitulo_libro",
      "book chapter",
      "chapter",
    ],
  }),

  LIB: createTipoMeta({
    codigo: "LIB",
    label: "Libros",
    tone: "lib",
    aliases: ["lib", "libro", "libros", "book", "books"],
  }),

  OTRO: META_OTRO,
});

export const TIPO_PUBLICACION_OPTIONS_DASHBOARD = Object.freeze([
  { value: "AAI", label: PUBLICACION_TIPOS.AAI.label },
  { value: "AR", label: PUBLICACION_TIPOS.AR.label },
  { value: "PON", label: PUBLICACION_TIPOS.PON.label },
  { value: "CAP", label: PUBLICACION_TIPOS.CAP.label },
  { value: "LIB", label: PUBLICACION_TIPOS.LIB.label },
]);

const EXACT_ALIAS_TO_CODE = (() => {
  const map = new Map();

  for (const [codigo, meta] of Object.entries(PUBLICACION_TIPOS)) {
    map.set(normalizeText(codigo), codigo);

    for (const alias of meta.aliases) {
      map.set(normalizeText(alias), codigo);
    }
  }

  return map;
})();

export const resolveTipoPublicacionCodigo = (input) => {
  const raw = normalizeText(input);
  if (!raw) return "OTRO";

  const upperRaw = String(input ?? "").trim().toUpperCase();
  if (TIPOS_VALIDOS.includes(upperRaw)) return upperRaw;

  if (EXACT_ALIAS_TO_CODE.has(raw)) {
    return EXACT_ALIAS_TO_CODE.get(raw);
  }

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

  if (raw.includes("ponencia")) return "PON";

  if (
    raw.includes("capitulo de libro") ||
    raw.includes("capítulo de libro") ||
    raw.includes("capitulo libro") ||
    raw.includes("capítulo libro") ||
    raw.includes("capitulo") ||
    raw.includes("capítulo") ||
    raw.includes("book chapter") ||
    raw.includes("chapter")
  ) {
    return "CAP";
  }

  if (
    raw === "libro" ||
    raw === "libros" ||
    raw === "book" ||
    raw === "books"
  ) {
    return "LIB";
  }

  return "OTRO";
};

export const getTipoPublicacionMeta = (input) =>
  PUBLICACION_TIPOS[resolveTipoPublicacionCodigo(input)] || META_OTRO;

export const getTipoPublicacionMetaFromItem = (item) => {
  const directCode = String(
    item?.tipo_publicacion_final ||
      item?.tipo_codigo ||
      item?.codigo ||
      item?.id ||
      ""
  )
    .trim()
    .toUpperCase();

  if (TIPOS_VALIDOS.includes(directCode)) {
    return PUBLICACION_TIPOS[directCode] || META_OTRO;
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
    const codigo = resolveTipoPublicacionCodigo(candidate);
    if (codigo !== "OTRO") {
      return PUBLICACION_TIPOS[codigo] || META_OTRO;
    }
  }

  const blob = candidates
    .map((value) => normalizeText(value))
    .filter(Boolean)
    .join(" ");

  const fallbackCode = resolveTipoPublicacionCodigo(blob);
  return PUBLICACION_TIPOS[fallbackCode] || META_OTRO;
};

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

export { normalizeText };