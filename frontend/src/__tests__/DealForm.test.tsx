import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { resetApiClientCachesForTests } from "../api/client";
import { PipeFieldOptionsProvider } from "../hooks/usePipeFieldOptions";
import { DealFormPage } from "../pages/DealFormPage";
import { emptyFormPayloadV1 } from "../schemas/formV1";
import { mockFormRecord } from "../test/mocks";

function fetchUrl(input: RequestInfo | URL): string {
  if (typeof input === "string") return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function renderForm() {
  return render(
    <PipeFieldOptionsProvider>
      <MemoryRouter
        initialEntries={[{ pathname: "/deals/1/746/form", state: { ownerName: "Alice", dealTitle: "Biview" } }]}
      >
        <Routes>
          <Route path="/deals/:ownerId/:dealId/form" element={<DealFormPage />} />
        </Routes>
      </MemoryRouter>
    </PipeFieldOptionsProvider>,
  );
}

describe("DealFormPage", () => {
  let savedBody: unknown;

  beforeEach(() => {
    savedBody = undefined;
    resetApiClientCachesForTests();
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = fetchUrl(input);
        if (url.includes("/deal-field-options")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                fields: {
                  "comercial.filial": [{ id: 1, label: "Matriz" }],
                  "comercial.regional": [{ id: 2, label: "Regional1" }],
                  "comercial.consultor": [{ id: 3, label: "Consultor X" }],
                  "comercial.percentual_exito": [{ id: 4, label: "20%" }],
                  "signatarios.email_consultor_gebras": [{ id: 84, label: "consultor@gebras.com" }],
                  "signatarios.email_coordenador_gebras": [{ id: 81, label: "coordenador@gebras.com" }],
                  "signatarios.email_diretor_gebras": [{ id: 80, label: "diretor@gebras.com" }],
                },
              }),
          });
        }
        if (url.includes("/hub/instalacoes")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                codigo_cliente: 0,
                codigos_instalacao_selecionados: [],
                formato_pipedrive: "",
                instalacoes: [],
                codigos_nao_encontrados: [],
              }),
          });
        }
        if (url.includes("/attachments") && (!init || init.method === undefined)) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                deal_id: 746,
                proposta_comercial_anexada: false,
                contrato: {
                  source: "padrao",
                  filename: null,
                  label: "Contrato a partir do modelo padrão Gebras",
                },
                attachments_error: null,
              }),
          });
        }
        if (url.includes("/readiness") && init?.method === "POST") {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                deal_id: 746,
                ready_to_submit: false,
                attachments_deferred: true,
                summary: { completed: 2, total: 20, percent: 10, validation_error_count: 5 },
                sections: [
                  {
                    id: "cliente",
                    label: "Cliente",
                    completed: 8,
                    total: 9,
                    ready: false,
                    items: [
                      {
                        id: "cliente.notas",
                        label: "Notas",
                        status: "pending",
                        message: null,
                      },
                    ],
                  },
                ],
                validation_errors: {},
              }),
          });
        }
        if (url.includes("/forms/746") && (!init || init.method === undefined)) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve(
                mockFormRecord({
                  payload: {
                    ...emptyFormPayloadV1(),
                    cliente: { ...emptyFormPayloadV1().cliente, contratante: "Salvo" },
                  },
                }),
              ),
          });
        }
        if (url.includes("/draft") && init?.method === "PUT") {
          savedBody = JSON.parse(init.body as string);
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockFormRecord({ status: "draft" })),
          });
        }
        if (url.includes("/submit") && init?.method === "POST") {
          savedBody = JSON.parse(init.body as string);
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve(
                mockFormRecord({
                  status: "error",
                  validation_errors: { "signatarios.email_diretor_gebras": "obrigatório" },
                }),
              ),
          });
        }
        return Promise.reject(new Error(`unexpected ${url} ${init?.method}`));
      }),
    );
  });

  it("carrega rascunho existente", async () => {
    const user = userEvent.setup();
    renderForm();
    expect(await screen.findByDisplayValue("Salvo")).toBeInTheDocument();
    const openBtn = await screen.findByRole("button", {
      name: /Cliente:.*pendentes.*Clique para ver/i,
    });
    await user.click(openBtn);
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("O que falta em Cliente")).toBeInTheDocument();
    expect(within(dialog).getByText("Notas")).toBeInTheDocument();
  });

  it("salva rascunho", async () => {
    const user = userEvent.setup();
    renderForm();
    await screen.findByDisplayValue("Salvo");
    const input = screen.getByLabelText(/^Contratante$/i);
    await user.clear(input);
    await user.type(input, "Novo Cliente");
    await user.click(screen.getByRole("button", { name: /Salvar rascunho/i }));
    await waitFor(() => expect(screen.getByText(/Rascunho salvo/i)).toBeInTheDocument());
    expect(savedBody).toMatchObject({
      schema_version: "v1",
      owner_user_id: 1,
      payload: expect.objectContaining({
        cliente: expect.objectContaining({ contratante: "Novo Cliente" }),
      }),
    });
  });

  it("exibe erros no submit", async () => {
    const user = userEvent.setup();
    renderForm();
    await screen.findByDisplayValue("Salvo");
    await user.click(screen.getByRole("button", { name: /Enviar formulário/i }));
    expect(await screen.findByText(/signatarios.email_diretor_gebras/i)).toBeInTheDocument();
    expect(await screen.findByText("obrigatório")).toBeInTheDocument();
    expect(document.querySelector("input.field-error, select.field-error")).toBeTruthy();
  });
});
