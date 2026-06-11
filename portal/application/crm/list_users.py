from __future__ import annotations

from portal.domain.crm.entities import CrmUser
from portal.domain.crm.repositories import CrmReader


class ListCrmUsers:
    """Consultores com pelo menos um deal aberto na etapa Contrato."""

    def __init__(self, crm_reader: CrmReader) -> None:
        self._crm_reader = crm_reader

    def execute(self) -> list[CrmUser]:
        deals = self._crm_reader.list_open_deals_in_contrato_stage()
        owner_ids = {d.owner_id for d in deals if d.owner_id is not None}
        if not owner_ids:
            return []

        users = self._crm_reader.list_users()
        filtered = [u for u in users if u.id in owner_ids]
        filtered.sort(key=lambda u: (u.name or "").casefold())
        return filtered
