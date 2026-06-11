import { describe, expect, it } from "vitest";
import { formatDisplayName } from "../utils/formatDisplayName";

describe("formatDisplayName", () => {
  it("title case em nomes all caps", () => {
    expect(formatDisplayName("GRUPO MAURICEIA - FAZENDAS MF")).toBe(
      "Grupo Mauriceia - Fazendas MF",
    );
    expect(formatDisplayName("GRUPO PRADELLA")).toBe("Grupo Pradella");
  });

  it("preserva nomes já legíveis", () => {
    expect(formatDisplayName("Grupo Pradella")).toBe("Grupo Pradella");
    expect(formatDisplayName("Biview")).toBe("Biview");
  });

  it("mantém siglas comuns", () => {
    expect(formatDisplayName("EMPRESA EXEMPLO SA")).toBe("Empresa Exemplo SA");
    expect(formatDisplayName("CLIENTE LTDA")).toBe("Cliente LTDA");
  });
});
