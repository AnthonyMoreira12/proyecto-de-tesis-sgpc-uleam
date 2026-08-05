import api from "./axios";


/* ==========================================================
   CONFIGURACIÓN
========================================================== */

const PROJECTS_BASE_URL = "proyectos";
const AUTHORS_SELECT_URL = "selects/autores";
const FACULTIES_SELECT_URL = "selects/facultades";
const CAREERS_SELECT_URL = "selects/carreras";


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
  fallback = "No fue posible completar la operación."
) {
  const payload =
    error?.response?.data
    ?? error?.data
    ?? error;

  const visit = (
    value,
    prefix = ""
  ) => {
    if (
      value == null
    ) {
      return [];
    }

    if (
      typeof value
      === "string"
      || typeof value
      === "number"
      || typeof value
      === "boolean"
    ) {
      const message =
        toStr(
          value
        );

      return message
        ? [
            prefix
              ? `${prefix}: ${message}`
              : message,
          ]
        : [];
    }

    if (
      Array.isArray(
        value
      )
    ) {
      return value.flatMap(
        (item) => visit(
          item,
          prefix
        )
      );
    }

    if (
      typeof value
      === "object"
    ) {
      return Object.entries(
        value
      ).flatMap(
        ([
          key,
          childValue,
        ]) => {
          const childPrefix = (
            key === "detail"
            || key === "message"
            || key === "non_field_errors"
              ? prefix
              : (
                prefix
                  ? `${prefix}.${key}`
                  : key
              )
          );

          return visit(
            childValue,
            childPrefix
          );
        }
      );
    }

    return [];
  };

  const messages =
    visit(
      payload
    );

  if (
    messages.length
  ) {
    return [
      ...new Set(
        messages
      ),
    ].join(" | ");
  }

  const nativeMessage =
    toStr(
      error?.message
    );

  return (
    nativeMessage
    || fallback
  );
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

  facultades:
    consultarFacultadesProyecto,

  carreras:
    consultarCarrerasProyecto,

  errorMessage:
    getProyectoApiErrorMessage,
};


export default proyectosApi;