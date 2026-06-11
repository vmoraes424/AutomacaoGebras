from __future__ import annotations

from typing import Protocol

from portal.domain.crm.entities import ContratoSnapshot, CrmDeal, CrmUser


class CrmReader(Protocol):
    def get_contrato_snapshot(self, *, fresh: bool = False) -> ContratoSnapshot: ...

    def list_users(self, *, fresh: bool = False) -> list[CrmUser]: ...

    def list_open_deals_in_contrato_stage(
        self,
        *,
        owner_user_id: int | None = None,
        fresh: bool = False,
    ) -> list[CrmDeal]: ...
