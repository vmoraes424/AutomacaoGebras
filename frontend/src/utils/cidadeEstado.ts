/** Espelha core.pipedrive_fields.split_cidade_estado / formato Pipe address. */

export function splitCidadeEstado(texto: string): { municipio: string; estado: string } {
  const text = (texto ?? "").trim();
  if (!text) return { municipio: "", estado: "" };

  if (text.includes("-")) {
    const [cidade, resto] = text.split("-", 2);
    let estado = resto.trim();
    if (estado.includes(",")) {
      estado = estado.split(",", 1)[0]?.trim() ?? estado;
    }
    return { municipio: cidade.trim(), estado };
  }

  if (text.includes("/")) {
    const idx = text.lastIndexOf("/");
    return {
      municipio: text.slice(0, idx).trim(),
      estado: text.slice(idx + 1).trim(),
    };
  }

  return { municipio: text, estado: "" };
}

/** Formato esperado pelo campo address do Pipedrive (ex.: Pelotas - RS, Brasil). */
export function joinCidadeEstado(municipio: string, estado: string): string {
  const m = municipio.trim();
  const e = estado.trim().toUpperCase();
  if (!m && !e) return "";
  if (!e) return m;
  if (!m) return e;
  return `${m} - ${e}, Brasil`;
}
