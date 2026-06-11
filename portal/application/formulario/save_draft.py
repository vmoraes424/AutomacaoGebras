from __future__ import annotations

from typing import Any

from portal.application.formulario.deal_eligibility import fetch_deal_eligible_for_form
from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.repositories import DealFormRepository


class SaveDealFormDraft:
    def __init__(self, repository: DealFormRepository) -> None:
        self._repository = repository

    def execute(
        self,
        deal_id: int,
        *,
        payload: dict[str, Any],
        schema_version: str = "v1",
        owner_user_id: int | None = None,
        owner_name: str = "",
        deal_title: str = "",
    ) -> DealForm:
        fetch_deal_eligible_for_form(deal_id)
        return self._repository.save_draft(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
        )
