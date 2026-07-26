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

// ============================================================
// CACHE LOCAL DE ARCHIVOS PDF
// IndexedDB permite conservar el File/Blob real entre recargas.
// ============================================================

const UPLOAD_CACHE_DB_NAME = "sgpc-uleam-upload-cache";
const UPLOAD_CACHE_DB_VERSION = 1;
const UPLOAD_CACHE_STORE = "publication-pdf-files";

// Conservamos los PDF de borrador durante un máximo de 7 días.
export const UPLOAD_CACHE_MAX_AGE_MS =
  7 * 24 * 60 * 60 * 1000;

let uploadCacheDbPromise = null;

export const ALLOWED_PDF_MIME_TYPES = Object.freeze([
  "application/pdf",
  "application/x-pdf",
]);

const normalizeFileName = (value) =>
  String(value ?? "").trim();

const normalizeMimeType = (value) =>
  String(value ?? "")
    .trim()
    .toLowerCase();

// ============================================================
// CLAVES
// ============================================================

export function makeUploadKey() {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()
    .toString(16)
    .slice(2)}`;
}

// ============================================================
// INDEXEDDB
// ============================================================

function canUseIndexedDb() {
  return (
    typeof window !== "undefined" &&
    typeof window.indexedDB !== "undefined"
  );
}

function waitForTransaction(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => {
      resolve();
    };

    transaction.onerror = () => {
      reject(
        transaction.error ||
          new Error(
            "No se pudo completar la operación de almacenamiento."
          )
      );
    };

    transaction.onabort = () => {
      reject(
        transaction.error ||
          new Error(
            "La operación de almacenamiento fue cancelada."
          )
      );
    };
  });
}

function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => {
      resolve(request.result);
    };

    request.onerror = () => {
      reject(
        request.error ||
          new Error(
            "No se pudo completar la consulta en IndexedDB."
          )
      );
    };
  });
}

async function openUploadCacheDb() {
  if (!canUseIndexedDb()) {
    return null;
  }

  if (uploadCacheDbPromise) {
    return uploadCacheDbPromise;
  }

  uploadCacheDbPromise = new Promise(
    (resolve, reject) => {
      const request = window.indexedDB.open(
        UPLOAD_CACHE_DB_NAME,
        UPLOAD_CACHE_DB_VERSION
      );

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        if (
          !db.objectStoreNames.contains(
            UPLOAD_CACHE_STORE
          )
        ) {
          const store = db.createObjectStore(
            UPLOAD_CACHE_STORE,
            {
              keyPath: "key",
            }
          );

          store.createIndex(
            "savedAt",
            "savedAt",
            {
              unique: false,
            }
          );
        }
      };

      request.onsuccess = () => {
        const db = request.result;

        db.onversionchange = () => {
          db.close();
          uploadCacheDbPromise = null;
        };

        resolve(db);
      };

      request.onerror = () => {
        uploadCacheDbPromise = null;
        reject(
          request.error ||
            new Error(
              "No se pudo abrir el almacenamiento local de archivos."
            )
        );
      };

      request.onblocked = () => {
        console.warn(
          "IndexedDB está bloqueado por otra pestaña de SGPC ULEAM."
        );
      };
    }
  );

  try {
    return await uploadCacheDbPromise;
  } catch (error) {
    console.warn(
      "SGPC ULEAM no pudo inicializar la caché de archivos PDF.",
      error
    );

    uploadCacheDbPromise = null;
    return null;
  }
}

// ============================================================
// GUARDAR ARCHIVO REAL EN INDEXEDDB
// ============================================================

export async function cacheUploadFile(
  itemOrKey,
  explicitFile = null
) {
  const key =
    typeof itemOrKey === "string"
      ? itemOrKey
      : itemOrKey?.key;

  const file =
    explicitFile ||
    (
      typeof itemOrKey === "object"
        ? itemOrKey?.file
        : null
    );

  if (!key || !file) {
    return false;
  }

  const db = await openUploadCacheDb();

  if (!db) {
    return false;
  }

  try {
    const transaction = db.transaction(
      UPLOAD_CACHE_STORE,
      "readwrite"
    );

    const store = transaction.objectStore(
      UPLOAD_CACHE_STORE
    );

    store.put({
      key,
      file,
      name: normalizeFileName(file.name),
      size: Number(file.size || 0),
      lastModified: Number(
        file.lastModified || 0
      ),
      type:
        normalizeMimeType(file.type) ||
        "application/pdf",
      savedAt: Date.now(),
    });

    await waitForTransaction(transaction);

    return true;
  } catch (error) {
    console.warn(
      `No se pudo guardar temporalmente el PDF "${file?.name || ""}".`,
      error
    );

    return false;
  }
}

// ============================================================
// RECUPERAR ARCHIVO REAL DESDE INDEXEDDB
// ============================================================

export async function loadCachedUploadFile(
  key,
  expected = {}
) {
  if (!key) {
    return null;
  }

  const db = await openUploadCacheDb();

  if (!db) {
    return null;
  }

  try {
    const transaction = db.transaction(
      UPLOAD_CACHE_STORE,
      "readonly"
    );

    const store = transaction.objectStore(
      UPLOAD_CACHE_STORE
    );

    const request = store.get(key);

    const record = await requestToPromise(
      request
    );

    await waitForTransaction(transaction);

    if (!record?.file) {
      return null;
    }

    const now = Date.now();

    if (
      Number(record.savedAt || 0) > 0 &&
      now - Number(record.savedAt) >
        UPLOAD_CACHE_MAX_AGE_MS
    ) {
      await deleteCachedUploadFile(key);
      return null;
    }

    const expectedName = normalizeFileName(
      expected?.originalName ||
        expected?.file?.name ||
        ""
    ).toLowerCase();

    const expectedSize = Number(
      expected?.size ||
        expected?.file?.size ||
        0
    );

    const expectedLastModified = Number(
      expected?.lastModified ||
        expected?.file?.lastModified ||
        0
    );

    const cachedName = normalizeFileName(
      record.name || record.file?.name || ""
    ).toLowerCase();

    const cachedSize = Number(
      record.size ||
        record.file?.size ||
        0
    );

    const cachedLastModified = Number(
      record.lastModified ||
        record.file?.lastModified ||
        0
    );

    if (
      expectedName &&
      cachedName &&
      expectedName !== cachedName
    ) {
      await deleteCachedUploadFile(key);
      return null;
    }

    if (
      expectedSize > 0 &&
      cachedSize > 0 &&
      expectedSize !== cachedSize
    ) {
      await deleteCachedUploadFile(key);
      return null;
    }

    if (
      expectedLastModified > 0 &&
      cachedLastModified > 0 &&
      expectedLastModified !==
        cachedLastModified
    ) {
      await deleteCachedUploadFile(key);
      return null;
    }

    if (
      typeof File !== "undefined" &&
      record.file instanceof File
    ) {
      return record.file;
    }

    if (
      typeof File !== "undefined" &&
      record.file instanceof Blob
    ) {
      return new File(
        [record.file],
        record.name ||
          expected?.originalName ||
          "archivo.pdf",
        {
          type:
            record.type ||
            record.file.type ||
            "application/pdf",

          lastModified:
            Number(
              record.lastModified || 0
            ) || Date.now(),
        }
      );
    }

    return null;
  } catch (error) {
    console.warn(
      "No se pudo recuperar un archivo PDF desde IndexedDB.",
      error
    );

    return null;
  }
}

// ============================================================
// ELIMINAR UN ARCHIVO DE LA CACHE
// ============================================================

export async function deleteCachedUploadFile(
  key
) {
  if (!key) {
    return false;
  }

  const db = await openUploadCacheDb();

  if (!db) {
    return false;
  }

  try {
    const transaction = db.transaction(
      UPLOAD_CACHE_STORE,
      "readwrite"
    );

    transaction
      .objectStore(UPLOAD_CACHE_STORE)
      .delete(key);

    await waitForTransaction(transaction);

    return true;
  } catch (error) {
    console.warn(
      "No se pudo eliminar el archivo PDF de la caché.",
      error
    );

    return false;
  }
}

// ============================================================
// ELIMINAR VARIOS ARCHIVOS DE LA CACHE
// ============================================================

export async function deleteCachedUploadFiles(
  keys = []
) {
  const source = Array.isArray(keys)
    ? keys.filter(Boolean)
    : [];

  if (!source.length) {
    return 0;
  }

  const results = await Promise.all(
    source.map((key) =>
      deleteCachedUploadFile(key)
    )
  );

  return results.filter(Boolean).length;
}

// ============================================================
// LIMPIAR TODA LA CACHE DE PDF
// ============================================================

export async function clearUploadFileCache() {
  const db = await openUploadCacheDb();

  if (!db) {
    return false;
  }

  try {
    const transaction = db.transaction(
      UPLOAD_CACHE_STORE,
      "readwrite"
    );

    transaction
      .objectStore(UPLOAD_CACHE_STORE)
      .clear();

    await waitForTransaction(transaction);

    return true;
  } catch (error) {
    console.warn(
      "No se pudo limpiar la caché local de archivos PDF.",
      error
    );

    return false;
  }
}

// ============================================================
// ELIMINAR ARCHIVOS ANTIGUOS
// ============================================================

export async function pruneCachedUploadFiles(
  maxAgeMs = UPLOAD_CACHE_MAX_AGE_MS
) {
  const db = await openUploadCacheDb();

  if (!db) {
    return 0;
  }

  try {
    const readTransaction =
      db.transaction(
        UPLOAD_CACHE_STORE,
        "readonly"
      );

    const records =
      await requestToPromise(
        readTransaction
          .objectStore(UPLOAD_CACHE_STORE)
          .getAll()
      );

    await waitForTransaction(
      readTransaction
    );

    const now = Date.now();

    const expiredKeys = (
      Array.isArray(records)
        ? records
        : []
    )
      .filter((record) => {
        const savedAt = Number(
          record?.savedAt || 0
        );

        if (!savedAt) {
          return true;
        }

        return (
          now - savedAt >
          Number(maxAgeMs)
        );
      })
      .map((record) => record.key)
      .filter(Boolean);

    if (!expiredKeys.length) {
      return 0;
    }

    return await deleteCachedUploadFiles(
      expiredKeys
    );
  } catch (error) {
    console.warn(
      "No se pudo depurar la caché de archivos PDF.",
      error
    );

    return 0;
  }
}

// ============================================================
// NOMBRE DEL ARCHIVO
// ============================================================

export function getPdfBaseName(fileName) {
  const normalized =
    normalizeFileName(fileName);

  if (!normalized) {
    return "Archivo PDF";
  }

  const safeName = normalized
    .replace(/^.*[\\/]/, "")
    .trim();

  const withoutExtension = safeName
    .replace(/\.pdf$/i, "")
    .trim();

  return (
    withoutExtension ||
    safeName ||
    "Archivo PDF"
  );
}

export function normalizeAttachmentName(
  value,
  fileName = ""
) {
  const custom = String(
    value ?? ""
  ).trim();

  const fallback =
    getPdfBaseName(fileName);

  return (
    custom ||
    fallback ||
    "Archivo PDF"
  )
    .slice(
      0,
      MAX_ATTACHMENT_NAME_LENGTH
    )
    .trim();
}

// ============================================================
// VALIDACIONES PDF
// ============================================================

export function hasPdfExtension(
  fileOrName
) {
  const name =
    typeof fileOrName === "string"
      ? fileOrName
      : fileOrName?.name;

  return /\.pdf$/i.test(
    normalizeFileName(name)
  );
}

export function hasAllowedPdfMime(file) {
  if (!file) {
    return false;
  }

  const mime = normalizeMimeType(
    file?.type
  );

  // Algunos navegadores no informan MIME.
  // La validación definitiva continúa en Django.
  if (!mime) {
    return true;
  }

  return ALLOWED_PDF_MIME_TYPES.includes(
    mime
  );
}

export function isPdfFile(file) {
  if (!file) {
    return false;
  }

  return (
    hasPdfExtension(file) &&
    hasAllowedPdfMime(file)
  );
}

// ============================================================
// FIRMA PDF
// ============================================================

export async function hasPdfSignature(file) {
  if (
    !file ||
    typeof file.slice !== "function"
  ) {
    return false;
  }

  try {
    const buffer = await file
      .slice(
        0,
        PDF_SIGNATURE_SCAN_BYTES
      )
      .arrayBuffer();

    const bytes =
      new Uint8Array(buffer);

    const signature = [
      0x25,
      0x50,
      0x44,
      0x46,
      0x2d,
    ]; // %PDF-

    for (
      let i = 0;
      i <=
      bytes.length -
        signature.length;
      i += 1
    ) {
      let matches = true;

      for (
        let j = 0;
        j < signature.length;
        j += 1
      ) {
        if (
          bytes[i + j] !==
          signature[j]
        ) {
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
    console.warn(
      "No se pudo comprobar la firma PDF en el navegador.",
      error
    );

    return false;
  }
}

export function isPdfSizeValid(
  file,
  maxBytes
) {
  if (!file) {
    return false;
  }

  const size = Number(
    file?.size || 0
  );

  const limit = Number(
    maxBytes || 0
  );

  return (
    Number.isFinite(size) &&
    size > 0 &&
    Number.isFinite(limit) &&
    limit > 0 &&
    size <= limit
  );
}

// ============================================================
// VALIDACIÓN GENERAL
// ============================================================

export async function validatePdfFile(
  file,
  {
    maxBytes =
      MAX_ATTACHMENT_PDF_FILE_SIZE,

    validateSignature = false,
  } = {}
) {
  if (!file) {
    return {
      valid: false,
      reason: "missing",
      message:
        "No se seleccionó ningún archivo.",
    };
  }

  if (!hasPdfExtension(file)) {
    return {
      valid: false,
      reason: "extension",
      message:
        "Solo se permiten archivos con extensión PDF.",
    };
  }

  if (!hasAllowedPdfMime(file)) {
    return {
      valid: false,
      reason: "mime",
      message:
        "El tipo de contenido del archivo no corresponde a un PDF.",
    };
  }

  const size = Number(
    file?.size || 0
  );

  if (
    !Number.isFinite(size) ||
    size <= 0
  ) {
    return {
      valid: false,
      reason: "empty",
      message:
        "El archivo PDF está vacío.",
    };
  }

  if (
    size >
    Number(maxBytes)
  ) {
    return {
      valid: false,
      reason: "size",
      message:
        `El archivo supera el tamaño máximo permitido de ${formatBytes(
          maxBytes
        )}.`,
    };
  }

  if (validateSignature) {
    const signatureValid =
      await hasPdfSignature(file);

    if (!signatureValid) {
      return {
        valid: false,
        reason: "signature",
        message:
          "El archivo no contiene una firma PDF reconocible.",
      };
    }
  }

  return {
    valid: true,
    reason: null,
    message: "",
  };
}

// ============================================================
// FORMATO
// ============================================================

export function formatBytes(bytes) {
  const value = Number(
    bytes || 0
  );

  if (
    !Number.isFinite(value) ||
    value <= 0
  ) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let size = value;
  let unitIndex = 0;

  while (
    size >= 1024 &&
    unitIndex <
      units.length - 1
  ) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(
    unitIndex === 0 ? 0 : 2
  )} ${units[unitIndex]}`;
}

// ============================================================
// CONSTRUCCIÓN DE ELEMENTOS
// ============================================================

export function buildUploadItem(file) {
  return {
    key: makeUploadKey(),

    file: file || null,

    nombre: "",

    originalName:
      normalizeFileName(
        file?.name || ""
      ),

    size: Number(
      file?.size || 0
    ),

    lastModified: Number(
      file?.lastModified || 0
    ),
  };
}

// ============================================================
// SERIALIZACIÓN PARA BORRADOR
//
// IMPORTANTE:
// El File real NO se mete en localStorage.
// El archivo real queda almacenado en IndexedDB usando "key".
// ============================================================

export function serializeDraftArchivos(
  items = []
) {
  const source =
    Array.isArray(items)
      ? items
      : [];

  return source.map((item) => ({
    key:
      item?.key ||
      makeUploadKey(),

    nombre: String(
      item?.nombre || ""
    )
      .trim()
      .slice(
        0,
        MAX_ATTACHMENT_NAME_LENGTH
      ),

    originalName:
      normalizeFileName(
        item?.file?.name ||
          item?.originalName ||
          ""
      ),

    size: Number(
      item?.file?.size ??
        item?.size ??
        0
    ),

    lastModified: Number(
      item?.file?.lastModified ??
        item?.lastModified ??
        0
    ),
  }));
}

// ============================================================
// RESTAURACIÓN INICIAL DEL BORRADOR
//
// Inicialmente se crea el placeholder.
// AdjuntosPdfUploader buscará automáticamente el File en IndexedDB.
// ============================================================

export function restoreDraftArchivos(
  items = []
) {
  const source =
    Array.isArray(items)
      ? items
      : [];

  return source.map((item) => ({
    key:
      item?.key ||
      makeUploadKey(),

    file: null,

    nombre: String(
      item?.nombre || ""
    )
      .trim()
      .slice(
        0,
        MAX_ATTACHMENT_NAME_LENGTH
      ),

    originalName:
      normalizeFileName(
        item?.originalName || ""
      ),

    size: Number(
      item?.size || 0
    ),

    lastModified: Number(
      item?.lastModified || 0
    ),
  }));
}

// ============================================================
// RESTAURACIÓN COMPLETA DESDE INDEXEDDB
// Puede utilizarse también desde otras vistas.
// ============================================================

export async function rehydrateDraftArchivos(
  items = []
) {
  const restored =
    restoreDraftArchivos(items);

  return Promise.all(
    restored.map(
      async (item) => {
        if (!item?.key) {
          return item;
        }

        const file =
          await loadCachedUploadFile(
            item.key,
            item
          );

        if (!file) {
          return item;
        }

        return {
          ...item,
          file,

          originalName:
            normalizeFileName(
              file.name ||
                item.originalName ||
                ""
            ),

          size: Number(
            file.size || 0
          ),

          lastModified: Number(
            file.lastModified || 0
          ),
        };
      }
    )
  );
}

// ============================================================
// HUELLA DEL ARCHIVO
// ============================================================

export function uploadFingerprint(
  itemOrFile
) {
  const file =
    itemOrFile?.file ||
    itemOrFile;

  const name =
    normalizeFileName(
      file?.name ||
        itemOrFile?.originalName ||
        ""
    ).toLowerCase();

  const size = Number(
    file?.size ||
      itemOrFile?.size ||
      0
  );

  const lastModified =
    Number(
      file?.lastModified ||
        itemOrFile?.lastModified ||
        0
    );

  return `${name}::${size}::${lastModified}`;
}

// ============================================================
// VALIDACIÓN FINAL ANTES DE FORM DATA
// ============================================================

function assertUploadFile(
  file,
  {
    maxBytes,
    label,
  }
) {
  if (!file) {
    throw new Error(
      `${label}: archivo no disponible.`
    );
  }

  if (!hasPdfExtension(file)) {
    throw new Error(
      `${label}: solo se permiten archivos con extensión PDF.`
    );
  }

  if (!hasAllowedPdfMime(file)) {
    throw new Error(
      `${label}: el tipo de contenido no corresponde a un PDF.`
    );
  }

  const size = Number(
    file?.size || 0
  );

  if (
    !Number.isFinite(size) ||
    size <= 0
  ) {
    throw new Error(
      `${label}: el archivo PDF está vacío.`
    );
  }

  if (size > maxBytes) {
    throw new Error(
      `${label}: supera el tamaño máximo de ${formatBytes(
        maxBytes
      )}.`
    );
  }
}

// ============================================================
// FORM DATA
// ============================================================

export function appendArchivosToFormData(
  formData,
  items = [],
  {
    primaryField = null,
    filesField = "archivos",
    metaField = "archivos_meta",
  } = {}
) {
  if (
    !formData ||
    typeof formData.append !==
      "function"
  ) {
    throw new TypeError(
      "appendArchivosToFormData requiere una instancia válida de FormData."
    );
  }

  const source =
    Array.isArray(items)
      ? items
      : [];

  const valid = source.filter(
    (item) => item?.file
  );

  if (!valid.length) {
    return {
      primary: null,
      attachments: 0,
      total: 0,

      skippedRecovered:
        source.filter(
          (item) =>
            !item?.file &&
            item?.originalName
        ).length,
    };
  }

  let primary = null;
  let attachments = valid;

  if (primaryField) {
    primary = valid[0];

    assertUploadFile(
      primary.file,
      {
        maxBytes:
          MAX_PRIMARY_PDF_FILE_SIZE,

        label:
          "PDF principal",
      }
    );

    formData.append(
      primaryField,
      primary.file
    );

    attachments =
      valid.slice(1);
  }

  if (
    attachments.length >
    MAX_ATTACHMENT_FILES
  ) {
    throw new Error(
      `Solo se permiten hasta ${MAX_ATTACHMENT_FILES} archivos PDF adjuntos por publicación.`
    );
  }

  if (attachments.length) {
    const metadata = [];

    attachments.forEach(
      (item, index) => {
        const attachmentNumber =
          index + 1;

        assertUploadFile(
          item.file,
          {
            maxBytes:
              MAX_ATTACHMENT_PDF_FILE_SIZE,

            label:
              `Adjunto #${attachmentNumber}`,
          }
        );

        formData.append(
          filesField,
          item.file
        );

        metadata.push({
          nombre:
            normalizeAttachmentName(
              item?.nombre,
              item?.file?.name ||
                item?.originalName
            ),

          orden:
            attachmentNumber,
        });
      }
    );

    formData.append(
      metaField,
      JSON.stringify(metadata)
    );
  }

  return {
    primary,

    attachments:
      attachments.length,

    total:
      valid.length,

    skippedRecovered:
      source.filter(
        (item) =>
          !item?.file &&
          item?.originalName
      ).length,
  };
}