from __future__ import annotations

from portal.application.crm.list_deals_contrato import ListDealsContrato
from portal.domain.crm.entities import CrmDeal
from portal.domain.formulario.operational import (
    PORTAL_STAGE_NAME,
    is_ready_for_automation,
    is_ready_for_form,
    operational_label,
)
from portal.domain.formulario.repositories import DealFormRepository


class ListDealsContratoEnriched:
    """Deals na etapa Contrato + status do formulário web."""

    def __init__(
        self,
        list_deals: ListDealsContrato,
        form_repository: DealFormRepository,
    ) -> None:
        self._list_deals = list_deals
        self._form_repository = form_repository

    def execute(self, *, owner_user_id: int | None = None, fresh: bool = False) -> list[dict]:
        deals = self._list_deals.execute(owner_user_id=owner_user_id, fresh=fresh)
        if not deals:
            return []
        deal_ids = [d.id for d in deals]
        status_map = self._form_repository.list_form_status_by_deal_ids(deal_ids)
        return [self._enrich(deal, status_map.get(deal.id)) for deal in deals]

    def _enrich(self, deal: CrmDeal, form_status: str | None) -> dict:
        label = operational_label(form_status)
        data = deal.to_dict()
        data.update(
            {
                "portal_stage": PORTAL_STAGE_NAME,
                "form_status": form_status,
                "operational_label": str(label),
                "ready_for_form": is_ready_for_form(deal_status=deal.status),
                "ready_for_automation": is_ready_for_automation(form_status),
            }
        )
        return data
