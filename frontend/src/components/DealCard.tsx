import { Link } from "react-router-dom";
import type { CrmDeal } from "../api/types";
import {
  DEAL_LABEL_TEXT,
  dealDisplayCliente,
  dealDisplayTitle,
  dealFormButtonLabel,
  dealOperationalLabel,
} from "../utils/dealCard";

type DealCardProps = {
  deal: CrmDeal;
  ownerId: string;
  ownerName: string;
};

export function DealCard({ deal, ownerId, ownerName }: DealCardProps) {
  const label = dealOperationalLabel(deal);
  const displayTitle = dealDisplayTitle(deal);
  const displayCliente = dealDisplayCliente(deal);

  return (
    <article className={`deal-card deal-card--${label}`}>
      <div className="deal-card-top">
        <span className="deal-card-id">#{deal.id}</span>
        <span className={`badge badge-${label}`}>{DEAL_LABEL_TEXT[label]}</span>
      </div>

      <h2 className="deal-card-title">{displayTitle}</h2>

      {displayCliente && (
        <p className="deal-card-cliente">
          <span className="deal-card-cliente-label">Cliente</span>
          {displayCliente}
        </p>
      )}

      <div className="deal-card-meta">
        {deal.ready_for_automation && (
          <span className="deal-card-chip deal-card-chip--ok">Pronto para automação</span>
        )}
        {label === "erro" && (
          <span className="deal-card-chip deal-card-chip--warn">Revisar validação</span>
        )}
      </div>

      <Link
        className="button deal-card-action"
        to={`/deals/${ownerId}/${deal.id}/form`}
        state={{ ownerName, dealTitle: deal.title }}
      >
        {dealFormButtonLabel(label)}
      </Link>
    </article>
  );
}
