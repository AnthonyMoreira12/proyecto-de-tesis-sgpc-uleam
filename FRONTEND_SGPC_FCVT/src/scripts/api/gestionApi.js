import api from "./axios";


/* ==========================================================
   ENDPOINTS
========================================================== */

const DASHBOARD_GESTION_URL =
  "/dashboard/gestion/";

const REPORTE_GESTION_PREVIEW_URL =
  "/reportes/gestion/preview/";

const REPORTE_GESTION_EXCEL_URL =
  "/reportes/gestion/excel/";

const REPORTE_PRODUCCION_PREVIEW_URL =
  "/reportes/produccion/preview/";

const REPORTE_PRODUCCION_EXCEL_URL =
  "/reportes/produccion/excel/";

const MI_REPORTE_PRODUCCION_PREVIEW_URL =
  "/reportes/mios/preview/";

const MI_REPORTE_PRODUCCION_EXCEL_URL =
  "/reportes/mios/excel/";

const MI_REPORTE_PRODUCCION_PDF_URL =
  "/reportes/mios/pdf/";


/* ==========================================================
   UTILIDADES
========================================================== */

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


function filenameFromDisposition(
  disposition
) {
  const value =
    String(
      disposition
      || ""
    ).trim();

  if (
    !value
  ) {
    return "";
  }

  const utfMatch =
    value.match(
      /filename\*=UTF-8''([^;]+)/i
    );

  if (
    utfMatch?.[1]
  ) {
    try {
      return decodeURIComponent(
        utfMatch[1]
          .replace(
            /^["']|["']$/g,
            ""
          )
      );
    } catch {
      return utfMatch[1]
        .replace(
          /^["']|["']$/g,
          ""
        );
    }
  }

  const regularMatch =
    value.match(
      /filename\s*=\s*"?([^";]+)"?/i
    );

  return (
    regularMatch?.[1]
      ? regularMatch[1].trim()
      : ""
  );
}


async function getPayload(
  url,
  params = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      url,
      {
        params:
          cleanParams(
            params
          ),
        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  return unwrap(
    response
  );
}


async function getFile(
  url,
  params = {},
  {
    signal,
  } = {},
  fallbackFilename = "reporte_sgpc.xlsx",
  fallbackContentType = "application/octet-stream"
) {
  const response =
    await api.get(
      url,
      {
        params:
          cleanParams(
            params
          ),

        responseType:
          "blob",

        ...(signal
          ? {
              signal,
            }
          : {}),
      }
    );

  const disposition =
    response?.headers?.[
      "content-disposition"
    ]
    || "";

  const filename =
    filenameFromDisposition(
      disposition
    )
    || fallbackFilename;

  return {
    blob:
      response?.data
      ?? null,

    filename,

    contentType:
      response?.headers?.[
        "content-type"
      ]
      || fallbackContentType,

    contentLength:
      Number(
        response?.headers?.[
          "content-length"
        ]
        || 0
      ),
  };
}


/* ==========================================================
   DASHBOARD DE GESTIÓN
========================================================== */

export async function obtenerDashboardGestion(
  params = {},
  options = {}
) {
  return getPayload(
    DASHBOARD_GESTION_URL,
    params,
    options
  );
}


/* ==========================================================
   REPORTE ADMINISTRATIVO DE GESTIÓN (COMPATIBILIDAD)
========================================================== */

export async function obtenerVistaPreviaReporteGestion(
  params = {},
  options = {}
) {
  return getPayload(
    REPORTE_GESTION_PREVIEW_URL,
    params,
    options
  );
}


export async function descargarReporteGestionExcel(
  params = {},
  options = {}
) {
  return getFile(
    REPORTE_GESTION_EXCEL_URL,
    params,
    options,
    "reporte_gestion_sgpc.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
}


/* ==========================================================
   PRODUCCIÓN CIENTÍFICA INSTITUCIONAL - ADMIN
========================================================== */

export async function obtenerReporteProduccionAdmin(
  params = {},
  options = {}
) {
  return getPayload(
    REPORTE_PRODUCCION_PREVIEW_URL,
    params,
    options
  );
}


export async function descargarReporteProduccionAdminExcel(
  params = {},
  options = {}
) {
  return getFile(
    REPORTE_PRODUCCION_EXCEL_URL,
    params,
    options,
    "reporte_produccion_institucional.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
}


/* ==========================================================
   PRODUCCIÓN CIENTÍFICA PERSONAL
========================================================== */

export async function obtenerMiReporteProduccion(
  params = {},
  options = {}
) {
  return getPayload(
    MI_REPORTE_PRODUCCION_PREVIEW_URL,
    params,
    options
  );
}


export async function descargarMiReporteProduccionExcel(
  params = {},
  options = {}
) {
  return getFile(
    MI_REPORTE_PRODUCCION_EXCEL_URL,
    params,
    options,
    "mi_produccion_cientifica.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
}


export async function descargarMiReporteProduccionPdf(
  params = {},
  options = {}
) {
  return getFile(
    MI_REPORTE_PRODUCCION_PDF_URL,
    params,
    options,
    "mi_produccion_cientifica.pdf",
    "application/pdf"
  );
}


/* ==========================================================
   DESCARGA EN NAVEGADOR
========================================================== */

export function guardarBlobEnNavegador(
  blob,
  filename
) {
  if (
    typeof window
    === "undefined"
    || typeof document
    === "undefined"
  ) {
    return false;
  }

  if (
    !(blob instanceof Blob)
  ) {
    throw new TypeError(
      "El contenido recibido no es un archivo descargable."
    );
  }

  const safeFilename =
    String(
      filename
      || "reporte_sgpc.xlsx"
    ).trim()
    || "reporte_sgpc.xlsx";

  const url =
    window.URL.createObjectURL(
      blob
    );

  const anchor =
    document.createElement(
      "a"
    );

  try {
    anchor.href = url;
    anchor.download =
      safeFilename;

    document.body.appendChild(
      anchor
    );

    anchor.click();
  } finally {
    anchor.remove();

    window.setTimeout(
      () => {
        window.URL.revokeObjectURL(
          url
        );
      },
      0
    );
  }

  return true;
}


/* ==========================================================
   OBJETO COMPATIBLE
========================================================== */

export const gestionApi = {
  dashboard:
    obtenerDashboardGestion,

  previewReporte:
    obtenerVistaPreviaReporteGestion,

  descargarExcel:
    descargarReporteGestionExcel,

  reporteProduccionAdmin:
    obtenerReporteProduccionAdmin,

  descargarProduccionAdmin:
    descargarReporteProduccionAdminExcel,

  miReporteProduccion:
    obtenerMiReporteProduccion,

  descargarMiProduccion:
    descargarMiReporteProduccionExcel,

  descargarMiProduccionPdf:
    descargarMiReporteProduccionPdf,

  guardarBlob:
    guardarBlobEnNavegador,
};


export default gestionApi;
