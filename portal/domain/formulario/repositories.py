from __future__ import annotations

from typing import Protocol

from portal.domain.formulario.entities import DealForm


class DealFormRepository(Protocol):
    def get_by_deal_id(
        self, deal_id: int, *, schema_version: str = "v1"
    ) -> DealForm | None: ...

    def save_draft(
        self,
        deal_id: int,
        *,
        payload: dict,
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
    ) -> DealForm: ...

    def submit(
        self,
        deal_id: int,
        *,
        payload: dict,
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
        validation_errors: dict | None = None,
    ) -> DealForm: ...
