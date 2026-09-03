export function buildAdminPublicacionTargetQuery(target = {}) {
  const query = {};

  const usuarioId = String(target?.usuarioId || "").trim();
  const autorId = String(target?.autorId || "").trim();

  if (usuarioId) {
    query.usuario_objetivo_id = usuarioId;

    // Compatibilidad con formularios anteriores.
    query.usuario_id = usuarioId;
  }

  if (autorId) {
    query.autor_objetivo_id = autorId;

    // Compatibilidad con formularios anteriores.
    query.autor_id = autorId;
  }

  if (target?.usuarioNombre) {
    query.usuario_nombre = String(target.usuarioNombre);
  }

  if (target?.autorNombre) {
    query.autor_nombre = String(target.autorNombre);
  }

  query.modo = "delegado";
  query.admin = "1";

  return query;
}

export function buildAdminPublicacionLinks(target = {}) {
  const usuarioId = String(target?.usuarioId || "").trim();
  const query = buildAdminPublicacionTargetQuery(target);

  if (!usuarioId) {
    return {
      panel: {
        name: "AdminPublicaciones",
      },

      articuloAltoImpacto: null,
      articuloRegional: null,
      ponencia: null,
      libro: null,
      capitulo: null,
    };
  }

  return {
    panel: {
      name: "AdminPublicacionesUsuario",
      params: {
        usuarioId,
      },
      query,
    },

    articuloAltoImpacto: {
      name: "AdminRegistroArticuloAltoImpactoUsuario",
      params: {
        usuarioId,
      },
      query,
    },

    articuloRegional: {
      name: "AdminRegistroArticuloRegionalUsuario",
      params: {
        usuarioId,
      },
      query,
    },

    ponencia: {
      name: "AdminRegistroPonenciaUsuario",
      params: {
        usuarioId,
      },
      query,
    },

    libro: {
      name: "AdminRegistroLibroUsuario",
      params: {
        usuarioId,
      },
      query,
    },

    capitulo: {
      name: "AdminRegistroCapituloLibroUsuario",
      params: {
        usuarioId,
      },
      query,
    },
  };
}