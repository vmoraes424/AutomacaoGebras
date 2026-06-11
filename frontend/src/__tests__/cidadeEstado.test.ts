import { describe, expect, it } from "vitest";
import { joinCidadeEstado, splitCidadeEstado } from "../utils/cidadeEstado";

describe("cidadeEstado", () => {
  it("split formato Pipe com país", () => {
    expect(splitCidadeEstado("Pelotas - RS, Brasil")).toEqual({
      municipio: "Pelotas",
      estado: "RS",
    });
  });

  it("split formato barra", () => {
    expect(splitCidadeEstado("Rio grande/RS")).toEqual({
      municipio: "Rio grande",
      estado: "RS",
    });
  });

  it("join formato Pipe", () => {
    expect(joinCidadeEstado("Pelotas", "rs")).toBe("Pelotas - RS, Brasil");
  });

  it("join só município", () => {
    expect(joinCidadeEstado("Curitiba", "")).toBe("Curitiba");
  });
});
