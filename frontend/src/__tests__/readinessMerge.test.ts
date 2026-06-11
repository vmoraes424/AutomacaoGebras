import { describe, expect, it } from "vitest";
import type { FormAttachmentsMeta, FormReadiness } from "../api/types";
import { mergeReadinessWithAttachments } from "../utils/readinessMerge";

const baseReadiness: FormReadiness = {
  deal_id: 746,
  ready_to_submit: false,
  summary: { completed: 2, total: 2, percent: 100, validation_error_count: 0 },
  sections: [
    {
      id: "cliente",
      label: "Cliente",
      completed: 2,
      total: 2,
      ready: true,
      items: [],
    },
  ],
  attachments_deferred: true,
  validation_errors: {},
};

const attachments: FormAttachmentsMeta = {
  deal_id: 746,
  proposta_comercial_anexada: true,
  contrato: { source: "padrao", filename: null, label: "Modelo padrão" },
  error: null,
};

describe("mergeReadinessWithAttachments", () => {
  it("mostra chip Anexos loading enquanto Pipe responde", () => {
    const merged = mergeReadinessWithAttachments(baseReadiness, null, true, false);
    const anexos = merged.sections.find((s) => s.id === "anexos");
    expect(anexos?.loading).toBe(true);
    expect(merged.ready_to_submit).toBe(false);
  });

  it("marca proposta ok quando Pipe confirma anexo", () => {
    const merged = mergeReadinessWithAttachments(baseReadiness, attachments, false, false);
    const anexos = merged.sections.find((s) => s.id === "anexos");
    expect(anexos?.ready).toBe(true);
    expect(merged.contrato?.source).toBe("padrao");
    expect(merged.ready_to_submit).toBe(true);
  });
});
