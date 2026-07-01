export const MAX_PRIMARY_PDF_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
export const MAX_ATTACHMENT_PDF_FILE_SIZE = 3 * 1024 * 1024; // 3 MB
export const MAX_RECOMMENDED_FILE_SIZE = MAX_ATTACHMENT_PDF_FILE_SIZE;

const normalizeFileName = (value) => String(value ?? "").trim();

export function makeUploadKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function isPdfFile(file) {
  if (!file) return false;

  const mime = String(file?.type || "").trim().toLowerCase();
  const name = normalizeFileName(file?.name || "").toLowerCase();

  return mime === "application/pdf" || /\.pdf$/i.test(name);
}

export function buildUploadItem(file) {
  return {
    key: makeUploadKey(),
    file,
    nombre: "",
    originalName: normalizeFileName(file?.name || ""),
    size: Number(file?.size || 0),
    lastModified: Number(file?.lastModified || 0),
  };
}

export function serializeDraftArchivos(items = []) {
  return (Array.isArray(items) ? items : []).map((it) => ({
    key: it?.key || makeUploadKey(),
    nombre: String(it?.nombre || "").trim(),
    originalName: it?.file?.name || it?.originalName || "",
    size: Number(it?.file?.size || it?.size || 0),
    lastModified: Number(it?.file?.lastModified || it?.lastModified || 0),
  }));
}

export function restoreDraftArchivos(items = []) {
  return (Array.isArray(items) ? items : []).map((it) => ({
    key: it?.key || makeUploadKey(),
    file: null,
    nombre: String(it?.nombre || "").trim(),
    originalName: it?.originalName || "",
    size: Number(it?.size || 0),
    lastModified: Number(it?.lastModified || 0),
  }));
}

export function uploadFingerprint(itemOrFile) {
  const file = itemOrFile?.file || itemOrFile;
  const name = file?.name || itemOrFile?.originalName || "";
  const size = Number(file?.size || itemOrFile?.size || 0);
  const lastModified = Number(file?.lastModified || itemOrFile?.lastModified || 0);

  return `${String(name).toLowerCase()}::${size}::${lastModified}`;
}

export function appendArchivosToFormData(
  fd,
  items = [],
  {
    primaryField = null,
    filesField = "archivos",
    metaField = "archivos_meta",
  } = {}
) {
  const valid = (Array.isArray(items) ? items : []).filter((it) => it?.file);

  if (!valid.length) {
    return { primary: null, attachments: 0 };
  }

  let attachments = valid;

  if (primaryField) {
    fd.append(primaryField, valid[0].file);
    attachments = valid.slice(1);
  }

  if (attachments.length) {
    attachments.forEach((it) => {
      fd.append(filesField, it.file);
    });

    fd.append(
      metaField,
      JSON.stringify(
        attachments.map((it, index) => ({
          nombre: String(it?.nombre || "").trim(),
          orden: index + 1,
        }))
      )
    );
  }

  return {
    primary: primaryField ? valid[0] : null,
    attachments: attachments.length,
  };
}