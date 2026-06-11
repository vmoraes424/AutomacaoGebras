import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { AutomacaoConfigPage } from "./pages/AutomacaoConfigPage";
import { DealFormPage } from "./pages/DealFormPage";
import { DealListPage } from "./pages/DealListPage";
import { OwnerSelectPage } from "./pages/OwnerSelectPage";

export function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<OwnerSelectPage />} />
          <Route path="/config/automacao" element={<AutomacaoConfigPage />} />
          <Route path="/deals/:ownerId" element={<DealListPage />} />
          <Route path="/deals/:ownerId/:dealId/form" element={<DealFormPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
