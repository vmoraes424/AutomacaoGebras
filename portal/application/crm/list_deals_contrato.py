from __future__ import annotations

from portal.domain.crm.entities import CrmDeal
from portal.domain.crm.repositories import CrmReader


class ListDealsContrato:
    def __init__(self, crm_reader: CrmReader) -> None:
        self._crm_reader = crm_reader

    def execute(self, *, owner_user_id: int | None = None) -> list[CrmDeal]:
        return self._crm_reader.list_open_deals_in_contrato_stage(
            owner_user_id=owner_user_id
        )
