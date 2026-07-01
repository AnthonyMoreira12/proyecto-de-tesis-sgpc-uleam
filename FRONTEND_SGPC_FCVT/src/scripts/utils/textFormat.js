// src/scripts/utils/textFormat.js

/**
 * Normaliza espacios internos y elimina espacios sobrantes.
 * Ejemplo:
 * "  ANTHONY   JOEL   MOREIRA  " => "ANTHONY JOEL MOREIRA"
 */
export const normalizeSpaces = (value = "") => {
  return String(value || "")
    .trim()
    .replace(/\s+/g, " ");
};

/**
 * Convierte una palabra a formato nombre respetando tildes, ñ, guiones y apóstrofes.
 * Ejemplos:
 * "MOREIRA" => "Moreira"
 * "MUÑOZ" => "Muñoz"
 * "MARÍA-JOSÉ" => "María-José"
 */
const capitalizeNameWord = (word = "") => {
  const cleanWord = String(word || "").trim();

  if (!cleanWord) return "";

  return cleanWord
    .toLocaleLowerCase("es-EC")
    .split("-")
    .map((part) => {
      if (!part) return "";

      return part
        .split("'")
        .map((subPart) => {
          if (!subPart) return "";

          return (
            subPart.charAt(0).toLocaleUpperCase("es-EC") +
            subPart.slice(1)
          );
        })
        .join("'");
    })
    .join("-");
};

/**
 * Normaliza nombres de personas que vienen desde Microsoft, backend o formularios.
 *
 * Ejemplos:
 * "ANTHONY JOEL MOREIRA CATAGUA" => "Anthony Joel Moreira Catagua"
 * "LUIS MIGUEL ZAMBRANO CEDEÑO" => "Luis Miguel Zambrano Cedeño"
 * "VALENTINA ISABEL MOREIRA VÉLEZ" => "Valentina Isabel Moreira Vélez"
 */
export const normalizePersonName = (value = "") => {
  const text = normalizeSpaces(value);

  if (!text) return "";

  const lowercaseParticles = new Set([
    "de",
    "del",
    "la",
    "las",
    "los",
    "y",
    "e",
    "da",
    "das",
    "do",
    "dos",
    "van",
    "von",
  ]);

  return text
    .split(" ")
    .map((word, index) => {
      const normalizedWord = capitalizeNameWord(word);
      const lowerWord = normalizedWord.toLocaleLowerCase("es-EC");

      if (index > 0 && lowercaseParticles.has(lowerWord)) {
        return lowerWord;
      }

      return normalizedWord;
    })
    .join(" ");
};

/**
 * Une nombres y apellidos separados y los normaliza.
 */
export const normalizeFullName = (nombres = "", apellidos = "") => {
  return normalizePersonName(`${nombres || ""} ${apellidos || ""}`);
};

/**
 * Normaliza una lista de autores separada por comas.
 *
 * Ejemplo:
 * "ANTHONY MOREIRA, LUIS ZAMBRANO"
 * =>
 * "Anthony Moreira, Luis Zambrano"
 */
export const normalizeAuthorsText = (value = "") => {
  const text = normalizeSpaces(value);

  if (!text) return "";

  return text
    .split(",")
    .map((author) => normalizePersonName(author))
    .filter(Boolean)
    .join(", ");
};