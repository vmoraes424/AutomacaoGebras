from __future__ import annotations

from collections import Counter

from portal.domain.crm.entities import CrmUser
from portal.domain.crm.repositories import CrmReader


class ListCrmUsers:
    """Consultores com pelo menos um deal aberto na etapa Contrato."""

    def __init__(self, crm_reader: CrmReader) -> None:
        self._crm_reader = crm_reader

    def execute(self, *, fresh: bool = False) -> list[CrmUser]:
        snapshot = self._crm_reader.get_contrato_snapshot(fresh=fresh)
        counts = Counter(d.owner_id for d in snapshot.deals if d.owner_id is not None)
        if not counts:
            return []

        filtered = [u for u in snapshot.users if u.id in counts]
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
