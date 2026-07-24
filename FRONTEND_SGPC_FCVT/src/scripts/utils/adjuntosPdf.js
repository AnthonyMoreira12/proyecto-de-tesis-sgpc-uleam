// ============================================================
// SGPC ULEAM
// Utilidades compartidas para archivos PDF de publicaciones
// ============================================================

export const MAX_PRIMARY_PDF_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
export const MAX_ATTACHMENT_PDF_FILE_SIZE = 3 * 1024 * 1024; // 3 MB
export const MAX_RECOMMENDED_FILE_SIZE = MAX_ATTACHMENT_PDF_FILE_SIZE;

export const MAX_ATTACHMENT_NAME_LENGTH = 150;
export const MAX_ATTACHMENT_FILES = 2;
export const MAX_FILES_WITH_PRIMARY = 1 + MAX_ATTACHMENT_FILES;

export const PDF_SIGNATURE_SCAN_BYTES = 1024;

export const ALLOWED_PDF_MIME_TYPES = Object.freeze([
  "application/pdf",
  "application/x-pdf",
]);

const normalizeFileName = (value) => String(value ?? "").trim();
const normalizeMimeType = (value) =>
  String(value ?? "")
    .trim()
    .toLowerCase();

export function makeUploadKey() {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function getPdfBaseName(fileName) {
  const normalized = normalizeFileName(fileName);

  if (!normalized) {
    return "Archivo PDF";
  }

  const safeName = normalized.replace(/^.*[\\/]/, "").trim();
  const withoutExtension = safeName.replace(/\.pdf$/i, "").trim();

  return withoutExtension || safeName || "Archivo PDF";
}

export function normalizeAttachmentName(value, fileName = "") {
  const custom = String(value ?? "").trim();
  const fallback = getPdfBaseName(fileName);

  return (custom || fallback || "Archivo PDF")
    .slice(0, MAX_ATTACHMENT_NAME_LENGTH)
    .trim();
}

export function hasPdfExtension(fileOrName) {
  const name =
    typeof fileOrName === "string"
      ? fileOrName
      : fileOrName?.name;

  return /\.pdf$/i.test(normalizeFileName(name));
}

export function hasAllowedPdfMime(file) {
  if (!file) {
    return false;
  }

  const mime = normalizeMimeType(file?.type);

  // Algunos navegadores no informan MIME. En ese caso la
  // validación definitiva queda a cargo de Django.
  if (!mime) {
    return true;
  }

  return ALLOWED_PDF_MIME_TYPES.includes(mime);
}

export function isPdfFile(file) {
  if (!file) {
    return false;
  }

  return hasPdfExtension(file) && hasAllowedPdfMime(file);
}

// Comprobación auxiliar tolerante. Busca %PDF- dentro de los
// primeros 1024 bytes en vez de exigirlo exactamente en byte 0.
export async function hasPdfSignature(file) {
  if (!file || typeof file.slice !== "function") {
    return false;
  }

  try {
    const buffer = await file
      .slice(0, PDF_SIGNATURE_SCAN_BYTES)
      .arrayBuffer();

    const bytes = new Uint8Array(buffer);
    const signature = [0x25, 0x50, 0x44, 0x46, 0x2d]; // %PDF-

    for (
      let i = 0;
      i <= bytes.length - signature.length;
      i += 1
    ) {
      let matches = true;

      for (let j = 0; j < signature.length; j += 1) {
        if (bytes[i + j] !== signature[j]) {
          matches = false;
          break;
        }
      }

      if (matches) {
        return true;
      }
    }

    return false;
  } catch (error) {
    console.warn("No se pudo comprobar la firma PDF en el navegador.", error);
    return false;
  }
}

export function isPdfSizeValid(file, maxBytes) {
  if (!file) {
    return false;
  }

  const size = Number(file?.size || 0);
  const limit = Number(maxBytes || 0);

  return (
    Number.isFinite(size) &&
    size > 0 &&
    Number.isFinite(limit) &&
    limit > 0 &&
    size <= limit
  );
}

// La firma binaria no es bloqueante por defecto en el frontend.
// Django conserva la validación de seguridad definitiva.
export async function validatePdfFile(
  file,
  {
    maxBytes = MAX_ATTACHMENT_PDF_FILE_SIZE,
    validateSignature = false,
  } = {}
) {
  if (!file) {
    return {
      valid: false,
      reason: "missing",
      message: "No se seleccionó ningún archivo.",
    };
  }

  if (!hasPdfExtension(file)) {
    return {
      valid: false,
      reason: "extension",
      message: "Solo se permiten archivos con extensión PDF.",
    };
  }

  if (!hasAllowedPdfMime(file)) {
    return {
      valid: false,
      reason: "mime",
      message: "El tipo de contenido del archivo no corresponde a un PDF.",
    };
  }

  const size = Number(file?.size || 0);

  if (!Number.isFinite(size) || size <= 0) {
    return {
      valid: false,
      reason: "empty",
      message: "El archivo PDF está vacío.",
    };
  }

  if (size > Number(maxBytes)) {
    return {
      valid: false,
      reason: "size",
      message: `El archivo supera el tamaño máximo permitido de ${formatBytes(
        maxBytes
      )}.`,
    };
  }

  if (validateSignature) {
    const signatureValid = await hasPdfSignature(file);

    if (!signatureValid) {
      return {
        valid: false,
        reason: "signature",
        message: "El archivo no contiene una firma PDF reconocible.",
      };
    }
  }

  return {
    valid: true,
    reason: null,
    message: "",
  };
}

export function formatBytes(bytes) {
  const value = Number(bytes || 0);

  if (!Number.isFinite(value) || value <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 2)} ${units[unitIndex]}`;
}

export function buildUploadItem(file) {
  return {
    key: makeUploadKey(),
    file: file || null,
    nombre: "",
    originalName: normalizeFileName(file?.name || ""),
    size: Number(file?.size || 0),
    lastModified: Number(file?.lastModified || 0),
  };
}

export function serializeDraftArchivos(items = []) {
  const source = Array.isArray(items) ? items : [];

  return source.map((item) => ({
    key: item?.key || makeUploadKey(),
    nombre: String(item?.nombre || "")
      .trim()
      .slice(0, MAX_ATTACHMENT_NAME_LENGTH),
    originalName: normalizeFileName(
      item?.file?.name || item?.originalName || ""
    ),
    size: Number(item?.file?.size || item?.size || 0),
    lastModified: Number(
      item?.file?.lastModified || item?.lastModified || 0
    ),
  }));
}

export function restoreDraftArchivos(items = []) {
  const source = Array.isArray(items) ? items : [];

  return source.map((item) => ({
    key: item?.key || makeUploadKey(),
    file: null,
    nombre: String(item?.nombre || "")
      .trim()
      .slice(0, MAX_ATTACHMENT_NAME_LENGTH),
    originalName: normalizeFileName(item?.originalName || ""),
    size: Number(item?.size || 0),
    lastModified: Number(item?.lastModified || 0),
  }));
}

export function uploadFingerprint(itemOrFile) {
  const file = itemOrFile?.file || itemOrFile;
  const name = normalizeFileName(
    file?.name || itemOrFile?.originalName || ""
  ).toLowerCase();
  const size = Number(file?.size || itemOrFile?.size || 0);
  const lastModified = Number(
    file?.lastModified || itemOrFile?.lastModified || 0
  );

  return `${name}::${size}::${lastModified}`;
}

function assertUploadFile(file, { maxBytes, label }) {
  if (!file) {
    throw new Error(`${label}: archivo no disponible.`);
  }

  if (!hasPdfExtension(file)) {
    throw new Error(`${label}: solo se permiten archivos con extensión PDF.`);
  }

  if (!hasAllowedPdfMime(file)) {
    throw new Error(
      `${label}: el tipo de contenido no corresponde a un PDF.`
    );
  }

  const size = Number(file?.size || 0);

  if (!Number.isFinite(size) || size <= 0) {
    throw new Error(`${label}: el archivo PDF está vacío.`);
  }

  if (size > maxBytes) {
    throw new Error(
      `${label}: supera el tamaño máximo de ${formatBytes(maxBytes)}.`
    );
  }
}

export function appendArchivosToFormData(
  formData,
  items = [],
  {
    primaryField = null,
    filesField = "archivos",
    metaField = "archivos_meta",
  } = {}
) {
  if (!formData || typeof formData.append !== "function") {
    throw new TypeError(
      "appendArchivosToFormData requiere una instancia válida de FormData."
    );
  }

  const source = Array.isArray(items) ? items : [];
  const valid = source.filter((item) => item?.file);

  if (!valid.length) {
    return {
      primary: null,
      attachments: 0,
      total: 0,
      skippedRecovered: source.filter(
        (item) => !item?.file && item?.originalName
      ).length,
    };
  }

  let primary = null;
  let attachments = valid;

  if (primaryField) {
    primary = valid[0];

    assertUploadFile(primary.file, {
      maxBytes: MAX_PRIMARY_PDF_FILE_SIZE,
      label: "PDF principal",
    });

    formData.append(primaryField, primary.file);
    attachments = valid.slice(1);
  }

  if (attachments.length > MAX_ATTACHMENT_FILES) {
    throw new Error(
      `Solo se permiten hasta ${MAX_ATTACHMENT_FILES} archivos PDF adjuntos por publicación.`
    );
  }

  if (attachments.length) {
    const metadata = [];

    attachments.forEach((item, index) => {
      const attachmentNumber = index + 1;

      assertUploadFile(item.file, {
        maxBytes: MAX_ATTACHMENT_PDF_FILE_SIZE,
        label: `Adjunto #${attachmentNumber}`,
      });

      formData.append(filesField, item.file);

      metadata.push({
        nombre: normalizeAttachmentName(
          item?.nombre,
          item?.file?.name || item?.originalName
        ),
        orden: attachmentNumber,
      });
    });

    formData.append(metaField, JSON.stringify(metadata));
  }

  return {
    primary,
    attachments: attachments.length,
    total: valid.length,
    skippedRecovered: source.filter(
      (item) => !item?.file && item?.originalName
    ).length,
  };
}
