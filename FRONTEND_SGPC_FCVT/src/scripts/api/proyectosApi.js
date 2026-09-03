import api from "./axios";


/* ==========================================================
   CONFIGURACIÓN
========================================================== */

const PROJECTS_BASE_URL = "proyectos";
const AUTHORS_SELECT_URL = "selects/autores";
const FACULTIES_SELECT_URL = "selects/facultades";
const SITES_SELECT_URL = "selects/sedes";
const CAREERS_SELECT_URL = "selects/carreras";
const CAREERS_BY_SITE_SELECT_URL = "selects/carreras/sede";


/* ==========================================================
   UTILIDADES
========================================================== */

const toStr = (
  value
) => (
  value == null
    ? ""
    : String(value).trim()
);

const ensurePositiveInteger = (
  value,
  fieldName = "id"
) => {
  if (
    typeof value === "boolean"
  ) {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  const parsedValue =
    Number.parseInt(
      String(value ?? ""),
      10
    );

  if (
    !Number.isInteger(
      parsedValue
    )
    || parsedValue < 1
  ) {
    throw new TypeError(
      `${fieldName} debe ser un entero positivo.`
    );
  }

  return parsedValue;
};

const cleanParams = (
  params = {}
) => {
  const cleaned = {};

  Object.entries(
    params
  ).forEach(
    ([
      key,
      value,
    ]) => {
      if (
        value == null
      ) {
        return;
      }

      if (
        typeof value
        === "string"
      ) {
        const normalized =
          value.trim();

        if (
          !normalized
        ) {
          return;
        }

        cleaned[key] =
          normalized;

        return;
      }

      cleaned[key] =
        value;
    }
  );

  return cleaned;
};

const unwrap = (
  response
) => (
  response?.data
  ?? response
  ?? null
);

const requestConfig = ({
  params,
  signal,
  headers,
  ...rest
} = {}) => ({
  ...rest,

  ...(params
    ? {
        params:
          cleanParams(
            params
          ),
      }
    : {}),

  ...(signal
    ? {
        signal,
      }
    : {}),

  ...(headers
    ? {
        headers,
      }
    : {}),
});


/* ==========================================================
   ERRORES
========================================================== */

export function getProyectoApiErrorMessage(
  error,
  fallback = "No pudimos completar la acción. Intente nuevamente."
) {
  const status =
    Number(
      error?.response?.status
      ?? error?.status
      ?? 0
    ) || 0;

  if (status === 401) {
    return "Su sesión ha vencido. Inicie sesión nuevamente.";
  }

  if (status === 403) {
    return "No tiene permisos para realizar esta acción.";
  }

  if (status === 404) {
    return "No encontramos la información solicitada.";
  }

  if (status === 429) {
    return "Se realizaron demasiadas solicitudes. Intente nuevamente en unos minutos.";
  }

  if (status >= 500) {
    return fallback;
  }

  const payload =
    error?.response?.data
    ?? error?.data
    ?? null;

  const FIELD_LABELS = {
    nombre: "Nombre",
    descripcion: "Descripción",
    sede: "Sede",
    facultad: "Facultad",
    carrera: "Carrera",
    estado: "Estado",
    anio_inicio: "Año de inicio",
    anio_fin: "Año de finalización",
    fecha_inicio: "Fecha de inicio",
    fecha_fin_planificada: "Fecha de finalización prevista",
    fecha_fin_prorrogada: "Nueva fecha de finalización",
    fecha_cierre: "Fecha de cierre",
    archivo_pdf: "Documento PDF",
    autores: "Profesores",
    profesores: "Profesores",
  };

  const TECHNICAL_PATTERN =
    /\b(?:api|backend|endpoint|serializer|queryset|jwt|token|sql|postgres(?:ql)?|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|stack\s*trace|http\s*\d{3}|request|response)\b/i;

  const normalizeMessage = (
    value
  ) => {
    const message =
      toStr(value)
        .replace(/\s+/g, " ")
        .trim();

    if (
      !message
      || TECHNICAL_PATTERN.test(message)
    ) {
      return "";
    }

    return message;
  };

  const collect = (
    value,
    field = ""
  ) => {
    if (value == null) {
      return [];
    }

    if (
      typeof value === "string"
      || typeof value === "number"
      || typeof value === "boolean"
    ) {
      const message =
        normalizeMessage(value);

      if (!message) {
        return [];
      }

      const label =
        FIELD_LABELS[field] || "";

      return [
        label
          ? `${label}: ${message}`
          : message,
      ];
    }

    if (Array.isArray(value)) {
      return value.flatMap(
        (item) => collect(item, field)
      );
    }

    if (typeof value === "object") {
      return Object.entries(value).flatMap(
        ([key, child]) => {
          if (
            key === "detail"
            || key === "message"
            || key === "non_field_errors"
            || key === "error"
          ) {
            return collect(child, field);
          }

          return collect(child, key);
        }
      );
    }

    return [];
  };

  const messages = [
    ...new Set(
      collect(payload)
    ),
  ];

  if (messages.length) {
    return messages.join(" · ");
  }

  return fallback;
}


/* ==========================================================
   PROYECTOS
========================================================== */

export async function listarProyectos(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/`,
      requestConfig({
        params,
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function obtenerProyecto(
  proyectoId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/${id}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function crearProyecto(
  payload,
  {
    signal,
  } = {}
) {
  const response =
    await api.post(
      `${PROJECTS_BASE_URL}/`,
      payload,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function actualizarProyecto(
  proyectoId,
  payload,
  {
    signal,
    partial = true,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const method = (
    partial
      ? "patch"
      : "put"
  );

  const response =
    await api[
      method
    ](
      `${PROJECTS_BASE_URL}/${id}/`,
      payload,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function eliminarProyecto(
  proyectoId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const response =
    await api.delete(
      `${PROJECTS_BASE_URL}/${id}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   PRODUCCIÓN CIENTÍFICA
========================================================== */

export async function obtenerProduccionProyecto(
  proyectoId,
  params = {},
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/${id}/produccion/`,
      requestConfig({
        params,
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function compararProduccionProyectos(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/comparativa-produccion/`,
      requestConfig({
        params,
        signal,
      })
    );

  return unwrap(
    response
  );
}



/* ==========================================================
   AÑOS Y ESTADO
========================================================== */

export async function consultarAniosProyectos(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/anios/`,
      requestConfig({
        params,
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function cambiarEstadoProyecto(
  proyectoId,
  estado = "",
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const payload =
    toStr(
      estado
    )
      ? {
          estado:
            toStr(
              estado
            ),
        }
      : {};

  const response =
    await api.patch(
      `${PROJECTS_BASE_URL}/${id}/cambiar_estado/`,
      payload,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function extenderFechaProyecto(
  proyectoId,
  fechaFinProrrogada,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const date =
    toStr(
      fechaFinProrrogada
    );

  if (
    !date
  ) {
    throw new TypeError(
      "Debe indicar la nueva fecha de finalización."
    );
  }

  const response =
    await api.patch(
      `${PROJECTS_BASE_URL}/${id}/extender_fecha/`,
      {
        fecha_fin_prorrogada:
          date,
      },
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   EQUIPO INVESTIGADOR
========================================================== */

export async function consultarAutoresProyecto(
  proyectoId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const response =
    await api.get(
      `${PROJECTS_BASE_URL}/${id}/autores/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function actualizarAutoresProyecto(
  proyectoId,
  autores,
  {
    signal,
    partial = false,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      proyectoId,
      "proyectoId"
    );

  const method = (
    partial
      ? "patch"
      : "put"
  );

  const response =
    await api[
      method
    ](
      `${PROJECTS_BASE_URL}/${id}/autores/`,
      {
        autores_data:
          autores,
      },
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   SELECTORES DEL FORMULARIO
========================================================== */

export async function buscarAutoresProyecto(
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${AUTHORS_SELECT_URL}/`,
      requestConfig({
        params,
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function consultarSedesProyecto(
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${SITES_SELECT_URL}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function consultarCarrerasPorSedeProyecto(
  sedeId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      sedeId,
      "sedeId"
    );

  const response =
    await api.get(
      `${CAREERS_BY_SITE_SELECT_URL}/${id}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}



export async function consultarFacultadesProyecto(
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      `${FACULTIES_SELECT_URL}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


export async function consultarCarrerasProyecto(
  facultadId,
  {
    signal,
  } = {}
) {
  const id =
    ensurePositiveInteger(
      facultadId,
      "facultadId"
    );

  const response =
    await api.get(
      `${CAREERS_SELECT_URL}/${id}/`,
      requestConfig({
        signal,
      })
    );

  return unwrap(
    response
  );
}


/* ==========================================================
   OBJETO COMPATIBLE
========================================================== */

export const proyectosApi = {
  listar:
    listarProyectos,

  obtener:
    obtenerProyecto,

  crear:
    crearProyecto,

  actualizar:
    actualizarProyecto,

  eliminar:
    eliminarProyecto,

  anios:
    consultarAniosProyectos,

  produccion:
    obtenerProduccionProyecto,

  comparativaProduccion:
    compararProduccionProyectos,

  cambiarEstado:
    cambiarEstadoProyecto,

  extenderFecha:
    extenderFechaProyecto,

  consultarAutores:
    consultarAutoresProyecto,

  actualizarAutores:
    actualizarAutoresProyecto,

  buscarAutores:
    buscarAutoresProyecto,

  sedes:
    consultarSedesProyecto,

  facultades:
    consultarFacultadesProyecto,

  carreras:
    consultarCarrerasProyecto,

  carrerasPorSede:
    consultarCarrerasPorSedeProyecto,

  errorMessage:
    getProyectoApiErrorMessage,
};


export default proyectosApi;
