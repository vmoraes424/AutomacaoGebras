/** Interpreta valor monetário em notação BR (1.805,50 / 5.000 / 1805). */
export function parseMoneyBr(raw: string): number | null {
  let texto = raw.replace(/R\$\s?/gi, "").trim();
  if (!texto) return null;

  if (texto.includes(",") && texto.includes(".")) {
    if (texto.lastIndexOf(",") > texto.lastIndexOf(".")) {
      texto = texto.replace(/\./g, "").replace(",", ".");
    } else {
      texto = texto.replace(/,/g, "");
    }
  } else if (texto.includes(",")) {
    texto = texto.replace(/\./g, "").replace(",", ".");
  } else if (texto.includes(".")) {
    const partes = texto.split(".");
    if (partes.length > 1 && partes.every((p) => /^\d+$/.test(p)) && partes[partes.length - 1].length === 3) {
      texto = partes.join("");
    }
  }

  const n = Number(texto);
  return Number.isFinite(n) ? n : null;
}

/** Valor canônico no payload (sem separador de milhar). */
export function moneyToStorage(value: string | number): string {
  const n = typeof value === "number" ? value : parseMoneyBr(String(value));
  if (n === null) return "";
  if (Number.isInteger(n)) return String(Math.trunc(n));
  return String(n);
}

/** Exibição pt-BR com R$ e separador de milhar. */
export function formatMoneyBr(value: string | number): string {
  const n = typeof value === "number" ? value : parseMoneyBr(String(value));
  if (n === null) return "";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(n);
}
