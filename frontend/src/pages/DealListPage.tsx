import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { DealCard } from "../components/DealCard";
import { GebrasLoader } from "../components/GebrasLoader";
import type { CrmDeal } from "../api/types";
import { api } from "../api/client";
import { useCrmSwr } from "../hooks/useCrmSwr";
import { useOwnerName } from "../hooks/useOwnerName";
import { matchesDealFilter } from "../utils/dealFilter";
import { formatDisplayName } from "../utils/formatDisplayName";

export function DealListPage() {
  const { ownerId } = useParams<{ ownerId: string }>();
  const location = useLocation();
  const ownerNameFromNav = (location.state as { ownerName?: string } | null)?.ownerName ?? "";
  const ownerUserId = Number(ownerId);
  const ownerName = useOwnerName(ownerUserId, ownerNameFromNav);

  const dealsCacheKey = ownerUserId ? `/pipedrive/deals?owner_user_id=${ownerUserId}` : "";
  const fetchDeals = useMemo(
    () => (opts?: { fresh?: boolean }) => api.listDeals(ownerUserId, opts),
    [ownerUserId],
  );
  const { data: deals, loading, error } = useCrmSwr<CrmDeal[]>(
    dealsCacheKey,
    fetchDeals,
    [],
  );
  const [filter, setFilter] = useState("");

  const filteredDeals = useMemo(
    () => deals.filter((deal) => matchesDealFilter(deal, filter)),
    [deals, filter],
  );

  const displayOwner = ownerName ? formatDisplayName(ownerName) : `usuário ${ownerId}`;

  if (!ownerUserId) {
    return null;
  }

  return (
    <div className="layout">
      <header className="page-header">
        <h1>Meus cards — {displayOwner}</h1>
        <p className="muted">
          <Link to="/">← Trocar consultor</Link>
          {" · "}
          Etapa: <strong>Contrato</strong> (abertos)
        </p>
      </header>

      {loading && <GebrasLoader variant="cards" label="Carregando cards…" />}
      {error && <div className="alert error">{error}</div>}

      {!loading && deals.length === 0 && !error && (
        <p className="muted">Nenhum card aberto na etapa Contrato para este dono.</p>
      )}

      {!loading && !error && deals.length > 0 && (
        <div className="filter-toolbar">
          <label className="filter-field">
            Filtrar cards
            <input
              type="search"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="ID, cliente ou nome do card…"
              autoComplete="off"
              spellCheck={false}
            />
          </label>
          <p className="filter-meta muted" aria-live="polite">
            {filter
              ? `${filteredDeals.length} de ${deals.length} card(s)`
              : `${deals.length} card(s)`}
          </p>
        </div>
      )}

      {!loading && !error && deals.length > 0 && filteredDeals.length === 0 && (
        <p className="muted">Nenhum card corresponde a «{filter}».</p>
      )}

      {filteredDeals.length > 0 && (
        <div className="card-grid">
          {filteredDeals.map((deal) => (
            <DealCard key={deal.id} deal={deal} ownerId={ownerId!} ownerName={ownerName} />
          ))}
        </div>
      )}
    </div>
  );
}
