import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { GebrasLoader } from "../components/GebrasLoader";
import type { CrmUser } from "../api/types";
import { useCrmQuery } from "../hooks/useCrmQuery";
import { formatDisplayName } from "../utils/formatDisplayName";
import { textIncludesFilter } from "../utils/textFilter";

function matchesConsultorFilter(user: CrmUser, filter: string): boolean {
  if (!filter) return true;
  return (
    textIncludesFilter(user.name, filter) || textIncludesFilter(user.email ?? "", filter)
  );
}

const USERS_CACHE_KEY = "/pipedrive/users";

export function OwnerSelectPage() {
  const fetchUsers = useMemo(() => () => api.listUsers(), []);
  const { data: users, loading, error } = useCrmQuery<CrmUser[]>(USERS_CACHE_KEY, fetchUsers, []);
  const [filter, setFilter] = useState("");

  const filteredUsers = useMemo(
    () => users.filter((user) => matchesConsultorFilter(user, filter)),
    [users, filter],
  );

  return (
    <div className="layout">
      <header className="page-header">
        <h1>Selecione o consultor</h1>
        <p className="muted">
          Apenas consultores com cards abertos na etapa Contrato aparecem aqui.
        </p>
      </header>

      {loading && <GebrasLoader variant="consultants" label="Carregando consultores…" />}
      {error && <div className="alert error">{error}</div>}

      {!loading && !error && users.length === 0 && (
        <p className="muted">Nenhum consultor com cards abertos na etapa Contrato.</p>
      )}

      {!loading && !error && users.length > 0 && (
        <div className="filter-toolbar">
          <label className="filter-field">
            Filtrar consultor
            <input
              type="search"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Nome ou e-mail…"
              autoComplete="off"
              spellCheck={false}
            />
          </label>
          <p className="filter-meta muted" aria-live="polite">
            {filter
              ? `${filteredUsers.length} de ${users.length} consultor(es)`
              : `${users.length} consultor(es)`}
          </p>
        </div>
      )}

      {!loading && !error && users.length > 0 && filteredUsers.length === 0 && (
        <p className="muted">Nenhum consultor corresponde a «{filter}».</p>
      )}

      {!loading && filteredUsers.length > 0 && (
        <div className="card-grid">
          {filteredUsers.map((user) => {
            const count = user.deals_contrato_count ?? 0;
            const countLabel =
              count === 1 ? "1 card na etapa Contrato" : `${count} cards na etapa Contrato`;
            return (
              <div key={user.id} className="card consultant-card">
                <div className="consultant-card-head">
                  <strong>{formatDisplayName(user.name)}</strong>
                  <span className="consultant-card-count" title={countLabel} aria-label={countLabel}>
                    {count}
                  </span>
                </div>
                {user.email && <div className="muted consultant-card-email">{user.email}</div>}
                <Link
                  className="button"
                  to={`/deals/${user.id}`}
                  state={{ ownerName: user.name }}
                >
                  Ver meus cards
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
