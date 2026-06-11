import { describe, expect, it } from "vitest";
import { formatMoneyBr, moneyToStorage, parseMoneyBr } from "../utils/money";

describe("money utils", () => {
  it("parseia milhar BR", () => {
    expect(parseMoneyBr("1.805")).toBe(1805);
    expect(parseMoneyBr("5.000")).toBe(5000);
  });

  it("parseia decimal BR e prefixo R$", () => {
    expect(parseMoneyBr("1.500,92")).toBe(1500.92);
    expect(parseMoneyBr("R$ 5.000")).toBe(5000);
  });

  it("formata com R$ e separador de milhar", () => {
    expect(formatMoneyBr("1805")).toBe("R$\u00a01.805");
    expect(formatMoneyBr("5000")).toBe("R$\u00a05.000");
  });

  it("armazena valor canônico", () => {
    expect(moneyToStorage("5.000")).toBe("5000");
    expect(moneyToStorage(1805)).toBe("1805");
  });
});
