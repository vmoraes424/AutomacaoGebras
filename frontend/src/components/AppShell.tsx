import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-brand">
            <h1 className="app-brand-title">Portal de Automação Comercial</h1>
            <p className="app-brand-subtitle">
              Pipedrive <span aria-hidden>·</span> ClickSign <span aria-hidden>·</span> Plune{" "}
              <span aria-hidden>·</span> HUB
            </p>
          </div>
          <nav className="app-header-nav" aria-label="Configurações">
            <NavLink
              to="/config/automacao"
              className={({ isActive }) =>
                `app-header-link${isActive ? " app-header-link--active" : ""}`
              }
            >
              Configs da Automação
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">Desenvolvido pelo time de BI</footer>
    </div>
  );
}
