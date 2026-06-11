import { describe, expect, it } from "vitest";
import type { CrmDeal } from "../api/types";
import { matchesDealFilter } from "../utils/dealFilter";

const deal = (partial: Partial<CrmDeal> & Pick<CrmDeal, "id" | "title">): CrmDeal => ({
  owner_id: 1,
  stage_id: 7,
  status: "open",
  pipeline_id: 1,
  ...partial,
});

describe("matchesDealFilter", () => {
  const sample = deal({
    id: 24593868,
    title: "Contrato Solar ABC",
    cliente: "Empresa Solar ABC Ltda",
  });

  it("filtra por ID", () => {
    expect(matchesDealFilter(sample, "24593868")).toBe(true);
    expect(matchesDealFilter(sample, "9386")).toBe(true);
    expect(matchesDealFilter(sample, "111")).toBe(false);
  });

  it("filtra por nome do card", () => {
    expect(matchesDealFilter(sample, "solar abc")).toBe(true);
    expect(matchesDealFilter(sample, "Contrato")).toBe(true);
  });

  it("filtra por cliente", () => {
    expect(matchesDealFilter(sample, "empresa solar")).toBe(true);
    expect(matchesDealFilter(sample, "Ltda")).toBe(true);
  });
});
