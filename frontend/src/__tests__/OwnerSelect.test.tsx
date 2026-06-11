import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { OwnerSelectPage } from "../pages/OwnerSelectPage";

const mockUsers = [
  { id: 1, name: "Alinne", email: "alinne.matos@gebras.com", deals_contrato_count: 4 },
  { id: 2, name: "Elvis Souza", email: "elvis@gebras.com", deals_contrato_count: 2 },
  { id: 3, name: "Karen Oliveira", email: "karen@gebras.com", deals_contrato_count: 7 },
];

describe("OwnerSelectPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          headers: { get: () => "application/json" },
          json: () => Promise.resolve(mockUsers),
        }),
      ),
    );
  });

  it("filtra consultores por nome ou e-mail", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <OwnerSelectPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Alinne")).toBeInTheDocument();
    expect(screen.getByLabelText("4 cards na etapa Contrato")).toHaveTextContent("4");
    expect(screen.getByText("Elvis Souza")).toBeInTheDocument();

    const input = screen.getByPlaceholderText(/Nome ou e-mail/i);
    await user.type(input, "karen");

    expect(screen.getByText("Karen Oliveira")).toBeInTheDocument();
    expect(screen.queryByText("Alinne")).not.toBeInTheDocument();
    expect(screen.getByText(/1 de 3 consultor/i)).toBeInTheDocument();
  });

  it("mostra mensagem quando filtro não encontra ninguém", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <OwnerSelectPage />
      </MemoryRouter>,
    );

    await screen.findByText("Alinne");
    await user.type(screen.getByPlaceholderText(/Nome ou e-mail/i), "xyz inexistente");

    expect(screen.getByText(/Nenhum consultor corresponde/i)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Ver meus cards/i })).not.toBeInTheDocument();
  });
});
