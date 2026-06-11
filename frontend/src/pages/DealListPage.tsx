import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { CrmDeal, OperationalLabel } from "../api/types";

const LABEL_TEXT: Record<OperationalLabel, string> = {
  pendente: "Pendente",
  rascunho: "Rascunho",
  erro: "Erro de validação",
  enviado: "Enviado",
  processando: "Processando",
  processado: "Processado",
};

function dealLabel(deal: CrmDeal): OperationalLabel {
  return deal.operational_label ?? "pendente";
}

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
        {" · "}
        Etapa: <strong>Contrato</strong> (abertos)
      </p>

      {loading && <p>Carregando cards…</p>}
      {error && <div className="alert error">{error}</div>}

      {!loading && deals.length === 0 && !error && (
        <p className="muted">Nenhum card aberto na etapa Contrato para este dono.</p>
      )}

      {deals.map((deal) => {
        const label = dealLabel(deal);
        return (
          <div key={deal.id} className="card">
            <div className="card-header">
              <strong>
                #{deal.id} — {deal.title}
              </strong>
              <span className={`badge badge-${label}`}>{LABEL_TEXT[label]}</span>
            </div>
            <div className="muted">
              Status Pipe: {deal.status}
              {deal.ready_for_automation && " · Pronto para automação"}
            </div>
            <Link
              className="button"
              to={`/deals/${ownerId}/${deal.id}/form`}
              state={{ ownerName, dealTitle: deal.title }}
            >
              {label === "enviado" || label === "processando" || label === "processado"
                ? "Ver formulário"
                : "Preencher formulário"}
            </Link>
          </div>
        );
      })}
    </div>
  );
}
