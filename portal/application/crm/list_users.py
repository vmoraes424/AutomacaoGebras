from __future__ import annotations

from collections import Counter

from portal.domain.crm.entities import CrmUser
from portal.domain.crm.repositories import CrmReader


class ListCrmUsers:
    """Consultores com pelo menos um deal aberto na etapa Contrato."""

    def __init__(self, crm_reader: CrmReader) -> None:
        self._crm_reader = crm_reader

    def execute(self, *, fresh: bool = False) -> list[CrmUser]:
        deals = self._crm_reader.list_open_deals_in_contrato_stage(fresh=fresh)
        counts = Counter(d.owner_id for d in deals if d.owner_id is not None)
        if not counts:
            return []

        users = self._crm_reader.list_users(fresh=fresh)
        filtered = [u for u in users if u.id in counts]
        filtered.sort(key=lambda u: (u.name or "").casefold())
        return [
            CrmUser(
                id=u.id,
                name=u.name,
                email=u.email,
                deals_contrato_count=counts[u.id],
            )
            for u in filtered
        ]
