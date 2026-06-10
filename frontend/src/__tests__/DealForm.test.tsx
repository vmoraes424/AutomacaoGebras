import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DealFormPage } from "../pages/DealFormPage";
import { emptyFormPayloadV1 } from "../schemas/formV1";
import { mockFormRecord } from "../test/mocks";

function renderForm() {
  return render(
    <MemoryRouter
      initialEntries={[{ pathname: "/deals/1/746/form", state: { ownerName: "Alice", dealTitle: "Biview" } }]}
    >
      <Routes>
        <Route path="/deals/:ownerId/:dealId/form" element={<DealFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("DealFormPage", () => {
  let savedBody: unknown;

  beforeEach(() => {
    savedBody = undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string, init?: RequestInit) => {
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
    renderForm();
    expect(await screen.findByDisplayValue("Salvo")).toBeInTheDocument();
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
    expect(document.querySelector("input.field-error")).toBeTruthy();
  });
});
