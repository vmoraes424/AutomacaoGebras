import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { CrmDeal } from "../api/types";

export function DealListPage() {
  const { ownerId } = useParams<{ ownerId: string }>();
  const location = useLocation();
  const ownerName = (location.state as { ownerName?: string } | null)?.ownerName ?? "";
  const ownerUserId = Number(ownerId);

  const [deals, setDeals] = useState<CrmDeal[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ownerUserId) return;
    api
      .listDeals(ownerUserId)
      .then(setDeals)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ownerUserId]);

  return (
    <div className="layout">
      <h1>Meus cards — {ownerName || `usuário ${ownerId}`}</h1>
      <p className="muted">
        <Link to="/">← Trocar consultor</Link>
      </p>

      {loading && <p>Carregando cards…</p>}
      {error && <div className="alert error">{error}</div>}

      {!loading && deals.length === 0 && !error && (
        <p className="muted">Nenhum card aberto na etapa Contrato para este dono.</p>
      )}

      {deals.map((deal) => (
        <div key={deal.id} className="card">
          <strong>
            #{deal.id} — {deal.title}
          </strong>
          <div className="muted">Status: {deal.status}</div>
          <Link
            className="button"
            to={`/deals/${ownerId}/${deal.id}/form`}
            state={{ ownerName, dealTitle: deal.title }}
          >
            Preencher formulário
          </Link>
        </div>
      ))}
    </div>
  );
}
