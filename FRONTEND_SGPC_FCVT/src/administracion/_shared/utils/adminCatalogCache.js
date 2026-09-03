import adminApi from "../../../scripts/api/adminApi";

const DEFAULT_TTL = 2 * 60 * 1000;

const cache = new Map();

function now() {
  return Date.now();
}

function normalizeId(value) {
  const text = String(value ?? "").trim();
  return text || "all";
}

function careersKey(params = {}) {
  return [
    "carreras",
    normalizeId(params.sedeId),
    normalizeId(params.facultadId),
  ].join(":");
}

async function cachedRequest(key, loader, options = {}) {
  const ttl = Number(options.ttl ?? DEFAULT_TTL);
  const force = Boolean(options.force);
  const current = cache.get(key);

  if (!force && current?.value !== undefined && current.expiresAt > now()) {
    return current.value;
  }

  if (!force && current?.promise) {
    return current.promise;
  }

  const previousValue = current?.value;
  const promise = Promise.resolve()
    .then(loader)
    .then((value) => {
      cache.set(key, {
        value,
        expiresAt: now() + Math.max(0, ttl),
        promise: null,
      });
      return value;
    })
    .catch((error) => {
      if (previousValue !== undefined) {
        cache.set(key, {
          value: previousValue,
          expiresAt: 0,
          promise: null,
        });
      } else {
        cache.delete(key);
      }
      throw error;
    });

  cache.set(key, {
    value: previousValue,
    expiresAt: current?.expiresAt || 0,
    promise,
  });

  return promise;
}

export function getAdminSedes(options = {}) {
  return cachedRequest(
    "sedes",
    () => adminApi.selectsSedes(),
    options,
  );
}

export function getAdminFacultades(options = {}) {
  return cachedRequest(
    "facultades",
    () => adminApi.selectsFacultades(),
    options,
  );
}

export function getAdminCarreras(params = {}, options = {}) {
  const normalizedParams = {
    sedeId: params.sedeId || null,
    facultadId: params.facultadId || null,
  };

  return cachedRequest(
    careersKey(normalizedParams),
    () => adminApi.selectsCarreras(normalizedParams),
    options,
  );
}

export function invalidateAdminCatalogCache(scope = "all") {
  if (scope === "all") {
    cache.clear();
    return;
  }

  const prefixes = Array.isArray(scope)
    ? scope
    : [scope];

  for (const key of [...cache.keys()]) {
    if (
      prefixes.some((prefix) =>
        key === prefix || key.startsWith(`${prefix}:`)
      )
    ) {
      cache.delete(key);
    }
  }
}
