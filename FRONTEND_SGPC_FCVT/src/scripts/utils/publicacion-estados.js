/* ==========================================================
   ESTADOS DE PUBLICACIÓN — SGPC ULEAM

   Este archivo concentra únicamente reglas visuales y de
   disponibilidad de acciones del frontend.

   La autorización definitiva siempre corresponde al backend.
========================================================== */

export const ESTADO_PUBLICACION = Object.freeze({
  BORRADOR:
    "borrador",

  EN_REVISION:
    "en_revision",

  OBSERVADA:
    "observada",

  APROBADA:
    "aprobada",

  RECHAZADA:
    "rechazada",
});


export const ESTADOS_PUBLICACION = Object.freeze([
  Object.freeze({
    value:
      ESTADO_PUBLICACION.BORRADOR,

    label:
      "Borrador",

    tone:
      "neutral",

    description:
      "La publicación todavía puede ser corregida antes de enviarse a revisión.",
  }),

  Object.freeze({
    value:
      ESTADO_PUBLICACION.EN_REVISION,

    label:
      "En revisión",

    tone:
      "info",

    description:
      "La publicación está siendo evaluada y permanece bloqueada para edición del autor.",
  }),

  Object.freeze({
    value:
      ESTADO_PUBLICACION.OBSERVADA,

    label:
      "Observada",

    tone:
      "warning",

    description:
      "La publicación requiere correcciones antes de volver a enviarse a revisión.",
  }),

  Object.freeze({
    value:
      ESTADO_PUBLICACION.APROBADA,

    label:
      "Aprobada",

    tone:
      "success",

    description:
      "La publicación superó la revisión administrativa y puede ser visible públicamente.",
  }),

  Object.freeze({
    value:
      ESTADO_PUBLICACION.RECHAZADA,

    label:
      "Rechazada",

    tone:
      "danger",

    description:
      "La publicación recibió una decisión administrativa de rechazo.",
  }),
]);


const ESTADOS_MAP = new Map(
  ESTADOS_PUBLICACION.map(
    (item) => [
      item.value,
      item,
    ]
  )
);


export function normalizarEstadoPublicacion(
  value
) {
  const normalized =
    String(
      value
      ?? ""
    )
      .trim()
      .toLowerCase()
      .replace(
        /\s+/g,
        "_"
      );

  return (
    ESTADOS_MAP.has(
      normalized
    )
      ? normalized
      : ""
  );
}


export function obtenerEstadoPublicacion(
  value
) {
  const normalized =
    normalizarEstadoPublicacion(
      value
    );

  return (
    ESTADOS_MAP.get(
      normalized
    )
    || {
      value:
        normalized,

      label:
        normalized
          ? normalized
              .replace(
                /_/g,
                " "
              )
          : "Sin estado",

      tone:
        "neutral",

      description:
        "",
    }
  );
}


export function estadoPublicacionLabel(
  value
) {
  return obtenerEstadoPublicacion(
    value
  ).label;
}


export function estadoPublicacionTone(
  value
) {
  return obtenerEstadoPublicacion(
    value
  ).tone;
}


export function esPublicacionPublica(
  value
) {
  return (
    normalizarEstadoPublicacion(
      value
    )
    === ESTADO_PUBLICACION.APROBADA
  );
}


export function esEstadoEditable(
  value
) {
  const estado =
    normalizarEstadoPublicacion(
      value
    );

  return (
    estado
    === ESTADO_PUBLICACION.BORRADOR
    || estado
    === ESTADO_PUBLICACION.OBSERVADA
  );
}


export function esEstadoBloqueado(
  value
) {
  const estado =
    normalizarEstadoPublicacion(
      value
    );

  return [
    ESTADO_PUBLICACION.EN_REVISION,
    ESTADO_PUBLICACION.APROBADA,
    ESTADO_PUBLICACION.RECHAZADA,
  ].includes(
    estado
  );
}


export function puedeEnviarRevisionPorEstado(
  value
) {
  return (
    normalizarEstadoPublicacion(
      value
    )
    === ESTADO_PUBLICACION.BORRADOR
  );
}


export function puedeReenviarRevisionPorEstado(
  value
) {
  return (
    normalizarEstadoPublicacion(
      value
    )
    === ESTADO_PUBLICACION.OBSERVADA
  );
}


export function puedeResolverRevisionPorEstado(
  value
) {
  return (
    normalizarEstadoPublicacion(
      value
    )
    === ESTADO_PUBLICACION.EN_REVISION
  );
}


function explicitBoolean(
  value
) {
  return (
    typeof value
    === "boolean"
      ? value
      : null
  );
}


export function puedeEditarPublicacion(
  publicacion
) {
  const explicit =
    explicitBoolean(
      publicacion?.puede_editar
    );

  if (
    explicit !== null
  ) {
    return explicit;
  }

  return esEstadoEditable(
    publicacion?.estado
  );
}


export function puedeEnviarRevision(
  publicacion
) {
  const explicit =
    explicitBoolean(
      publicacion
        ?.puede_enviar_revision
    );

  if (
    explicit !== null
  ) {
    return explicit;
  }

  return puedeEnviarRevisionPorEstado(
    publicacion?.estado
  );
}


export function puedeReenviarRevision(
  publicacion
) {
  const explicit =
    explicitBoolean(
      publicacion
        ?.puede_reenviar_revision
    );

  if (
    explicit !== null
  ) {
    return explicit;
  }

  return puedeReenviarRevisionPorEstado(
    publicacion?.estado
  );
}


export function puedeAdministrarRevision(
  publicacion,
  {
    esAdmin = false,
  } = {}
) {
  return Boolean(
    esAdmin
    && puedeResolverRevisionPorEstado(
      publicacion?.estado
    )
  );
}


export function accionesPublicacion(
  publicacion,
  {
    esAdmin = false,
  } = {}
) {
  if (
    !publicacion
  ) {
    return [];
  }

  const actions = [];

  if (
    puedeEditarPublicacion(
      publicacion
    )
  ) {
    actions.push(
      "editar"
    );
  }

  if (
    puedeEnviarRevision(
      publicacion
    )
  ) {
    actions.push(
      "enviar_revision"
    );
  }

  if (
    puedeReenviarRevision(
      publicacion
    )
  ) {
    actions.push(
      "reenviar_revision"
    );
  }

  if (
    puedeAdministrarRevision(
      publicacion,
      {
        esAdmin,
      }
    )
  ) {
    actions.push(
      "aprobar",
      "observar",
      "rechazar"
    );
  }

  return actions;
}


export default {
  ESTADO_PUBLICACION,
  ESTADOS_PUBLICACION,

  normalizarEstadoPublicacion,
  obtenerEstadoPublicacion,
  estadoPublicacionLabel,
  estadoPublicacionTone,

  esPublicacionPublica,
  esEstadoEditable,
  esEstadoBloqueado,

  puedeEnviarRevisionPorEstado,
  puedeReenviarRevisionPorEstado,
  puedeResolverRevisionPorEstado,

  puedeEditarPublicacion,
  puedeEnviarRevision,
  puedeReenviarRevision,
  puedeAdministrarRevision,

  accionesPublicacion,
};
