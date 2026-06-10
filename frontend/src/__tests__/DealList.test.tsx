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
      vi.fn((url: string) => {
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
    expect(await screen.findByText(/Biview/)).toBeInTheDocument();
    expect(screen.getByText(/Outro deal/)).toBeInTheDocument();
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
    await screen.findByText(/Biview/);
    await user.click(screen.getAllByRole("link", { name: /Preencher formulário/i })[0]);
    expect(await screen.findByText("Formulário aberto")).toBeInTheDocument();
  });
});
