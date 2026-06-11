import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DealListPage } from "../pages/DealListPage";
import { mockDeals } from "../test/mocks";

function renderDealList(ownerId = "1") {
  return render(
    <MemoryRouter initialEntries={[`/deals/${ownerId}`]}>
      <Routes>
        <Route path="/deals/:ownerId" element={<DealListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("DealListPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
        if (url.includes("/pipedrive/users")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve([{ id: 1, name: "Karen Oliveira", email: "karen@example.com" }]),
          });
        }
        if (url.includes("/pipedrive/deals")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockDeals),
          });
        }
        return Promise.reject(new Error(`unexpected ${url}`));
      }),
    );
  });

  it("lista cards do dono selecionado", async () => {
    renderDealList("1");
    expect(await screen.findByRole("heading", { name: /Meus cards — Karen Oliveira/i })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Biview" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Outro Deal" })).toBeInTheDocument();
    expect(screen.getByText("Enviado")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining("owner_user_id=1"), expect.anything());
  });

  it("navega para o formulário do deal", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/deals/1"]}>
        <Routes>
          <Route path="/deals/:ownerId" element={<DealListPage />} />
          <Route path="/deals/:ownerId/:dealId/form" element={<div>Formulário aberto</div>} />
        </Routes>
      </MemoryRouter>,
    );
    await screen.findByRole("heading", { name: "Biview" });
    await user.click(screen.getAllByRole("link", { name: /Preencher formulário/i })[0]);
    expect(await screen.findByText("Formulário aberto")).toBeInTheDocument();
  });

  it("filtra cards por id, cliente ou titulo", async () => {
    const user = userEvent.setup();
    renderDealList("1");
    await screen.findByRole("heading", { name: "Biview" });
    expect(screen.getByRole("heading", { name: "Outro Deal" })).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText(/ID, cliente ou nome/i), "999");
    expect(screen.queryByRole("heading", { name: "Biview" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Outro Deal" })).toBeInTheDocument();
    expect(screen.getByText(/1 de 2 card/i)).toBeInTheDocument();
  });
});
