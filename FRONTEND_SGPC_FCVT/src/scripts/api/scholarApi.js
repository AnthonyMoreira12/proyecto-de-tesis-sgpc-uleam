import api from "./axios";


const toStr = (value) => (
  value == null
    ? ""
    : String(value)
);


const cleanParams = (
  object = {}
) => {
  const output = {};

  Object.entries(
    object
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
        const trimmedValue =
          value.trim();

        if (
          !trimmedValue
        ) {
          return;
        }

        output[key] =
          trimmedValue;

        return;
      }

      output[key] =
        value;
    }
  );

  return output;
};


const unwrap = (
  response
) => (
  response?.data
  ?? response
);


export async function scholarSuggest(
  {
    q = "",
    limit = 8,
    signal,
  } = {}
) {
  const query =
    toStr(q).trim();

  if (
    !query
  ) {
    return {
      suggestions: [],
      results: [],
    };
  }

  const response =
    await api.get(
      "scholar/suggest/",
      {
        params: cleanParams({
          q: query,
          limit,
        }),
        signal,
      }
    );

  return unwrap(
    response
  );
}


export async function searchScholarPublications(
  {
    q = "",
    year = "",
    month = "",
    type = "",
    sort = "relevance",
    facets = "1",
    lang = "all",
    author_id = "",
    has_pdf = "",
    page = 1,
    page_size,
  } = {},
  {
    signal,
  } = {}
) {
  const response =
    await api.get(
      "busqueda/publicaciones/",
      {
        params: cleanParams({
          q,
          year,
          month,
          type,
          sort,
          facets,
          lang,
          author_id,
          has_pdf,
          page,
          page_size,
        }),
        signal,
      }
    );

  return unwrap(
    response
  );
}


export async function listScholarProfiles(
  {
    q = "",
    preload = "0",
    page = 1,
    page_size = 10,
  } = {},
  {
    signal,
  } = {}
) {
  const query =
    toStr(q).trim();

  const shouldPreload =
    !query
    && toStr(
      preload
    ).trim() === "1";

  const response =
    await api.get(
      "scholar/perfiles/",
      {
        params: cleanParams({
          q: (
            query
            || undefined
          ),
          preload: (
            shouldPreload
              ? "1"
              : undefined
          ),
          page,
          page_size,
        }),
        signal,
      }
    );

  return unwrap(
    response
  );
}


export async function getScholarProfileDetail(
  id,
  {
    signal,
  } = {}
) {
  const authorId =
    toStr(id).trim();

  if (
    !authorId
  ) {
    throw new Error(
      "Identificador de perfil no válido."
    );
  }

  const path = (
    authorId === "me"
      ? "scholar/perfiles/me/"
      : `scholar/perfiles/${authorId}/`
  );

  const response =
    await api.get(
      path,
      {
        signal,
      }
    );

  return unwrap(
    response
  );
}


export async function getScholarMyProfile(
  {
    signal,
  } = {}
) {
  return getScholarProfileDetail(
    "me",
    {
      signal,
    }
  );
}


export async function updateScholarMyProfile(
  payload = {},
  {
    signal,
  } = {}
) {
  const allowedFields = [
    "orcid",
    "registro_senescyt",
    "google_scholar",
    "scopus_id",
  ];

  const body = {};

  allowedFields.forEach(
    (field) => {
      if (
        Object.prototype.hasOwnProperty.call(
          payload || {},
          field
        )
      ) {
        body[field] =
          payload[field];
      }
    }
  );

  const response =
    await api.patch(
      "scholar/perfiles/me/",
      body,
      {
        signal,
      }
    );

  return unwrap(
    response
  );
}
