from __future__ import annotations

from portal.domain.crm.entities import CrmUser
from portal.domain.crm.repositories import CrmReader


class ListCrmUsers:
    def __init__(self, crm_reader: CrmReader) -> None:
        self._crm_reader = crm_reader

    def execute(self) -> list[CrmUser]:
        return self._crm_reader.list_users()
