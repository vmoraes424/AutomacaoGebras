/** Partículas em minúsculo (pt-BR), exceto início do texto. */
const LOWER_PARTICLES = new Set(["de", "da", "do", "dos", "das", "e"]);

/** Siglas comuns em nomes de clientes/contratos Gebras. */
const ACRONYMS = new Set([
  "mf",
  "sa",
  "ltda",
  "me",
  "epp",
  "uc",
  "acl",
  "hub",
  "rs",
  "sc",
  "sp",
  "mg",
  "pr",
  "rj",
  "fv",
  "guf",
  "gml",
  "gqe",
  "sw",
]);

function formatWord(word: string, capitalize: boolean): string {
  const trimmed = word.trim();
  if (!trimmed) return trimmed;

  const lower = trimmed.toLowerCase();
  if (!capitalize && LOWER_PARTICLES.has(lower)) return lower;
  if (ACRONYMS.has(lower)) return lower.toUpperCase();
  if (/^\d+$/.test(trimmed)) return trimmed;

  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

/**
 * Exibe nomes legíveis: "GRUPO MAURICEIA - FAZENDAS MF" → "Grupo Mauriceia - Fazendas MF".
 * Não altera filtros — usar só na UI.
 */
export function formatDisplayName(value: string): string {
  const text = (value ?? "").trim();
  if (!text) return text;

  const tokens = text.split(/(\s+|[-–/])/);
  let wordIndex = 0;

  const out = tokens.map((token) => {
    if (/^[\s\-–/]+$/.test(token)) {
      if (token.trim() === "" && token.includes("\n")) return " ";
      if (/^[-–/]$/.test(token.trim())) return ` ${token.trim()} `;
      return token.includes("\t") ? " " : token;
    }

    const formatted = formatWord(token, wordIndex === 0);
    wordIndex += 1;
    return formatted;
  });

  return out
    .join("")
    .replace(/\s+/g, " ")
    .replace(/\s+([-–/])\s+/g, " $1 ")
    .trim();
}
