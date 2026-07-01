import {
  isPdfFile,
  MAX_ATTACHMENT_PDF_FILE_SIZE,
} from "./adjuntosPdf";

const BYTES_PER_MB = 1024 * 1024;
const DEFAULT_MAX_SIZE_MB = Math.round(
  MAX_ATTACHMENT_PDF_FILE_SIZE / BYTES_PER_MB
);

const normalizeAllowedTypes = (allowedTypes = []) => {
  if (Array.isArray(allowedTypes)) return allowedTypes;
  return [allowedTypes];
};

const expectsPdfValidation = (allowedTypes = []) => {
  const normalized = normalizeAllowedTypes(allowedTypes);
  return normalized.includes("application/pdf");
};

export function validateFile(
  file,
  allowedTypes = ["application/pdf"],
  maxSizeMB = DEFAULT_MAX_SIZE_MB
) {
  if (!file) {
    return {
      valid: false,
      error: "No se seleccionó ningún archivo.",
    };
  }

  const normalizedAllowedTypes = normalizeAllowedTypes(allowedTypes);
  const maxSizeValue = Number(maxSizeMB);
  const safeMaxSizeMB = Number.isFinite(maxSizeValue) && maxSizeValue > 0
    ? maxSizeValue
    : DEFAULT_MAX_SIZE_MB;

  const maxSizeBytes = safeMaxSizeMB * BYTES_PER_MB;

  let isValidType = false;

  if (expectsPdfValidation(normalizedAllowedTypes)) {
    isValidType = isPdfFile(file);
  } else if (!normalizedAllowedTypes.length) {
    isValidType = true;
  } else {
    isValidType = normalizedAllowedTypes.includes(
      String(file?.type || "").trim()
    );
  }

  if (!isValidType) {
    return {
      valid: false,
      error: expectsPdfValidation(normalizedAllowedTypes)
        ? "Formato no permitido. Solo se aceptan archivos PDF."
        : "Formato no permitido.",
    };
  }

  if (Number(file.size || 0) > maxSizeBytes) {
    return {
      valid: false,
      error: `El archivo supera el límite de ${safeMaxSizeMB} MB.`,
    };
  }

  return {
    valid: true,
    error: null,
  };
}