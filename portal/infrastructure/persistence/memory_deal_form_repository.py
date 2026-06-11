from __future__ import annotations

from copy import deepcopy
from typing import Any

from portal.domain.formulario.entities import DealForm
from portal.infrastructure.persistence.deal_form_rules import build_draft, build_submit


class MemoryDealFormRepository:
    """Implementação em memória para testes e dev local."""

    def __init__(self) -> None:
        self._store: dict[str, DealForm] = {}

    def clear(self) -> None:
        self._store.clear()

    @staticmethod
    def _key(deal_id: int, schema_version: str) -> str:
        return f"{deal_id}:{schema_version}"

    def get_by_deal_id(
        self, deal_id: int, *, schema_version: str = "v1"
    ) -> DealForm | None:
        form = self._store.get(self._key(deal_id, schema_version))
        return deepcopy(form) if form else None

    def list_form_status_by_deal_ids(
        self, deal_ids: list[int], *, schema_version: str = "v1"
    ) -> dict[int, str]:
        wanted = {int(d) for d in deal_ids}
        out: dict[int, str] = {}
        for key, form in self._store.items():
            if not key.endswith(f":{schema_version}"):
                continue
            if form.deal_id in wanted:
                out[form.deal_id] = str(form.status)
        return out

    def save_draft(
        self,
        deal_id: int,
        *,
        payload: dict[str, Any],
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
    ) -> DealForm:
        key = self._key(deal_id, schema_version)
        existing = self._store.get(key)
        form = build_draft(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            existing=existing,
        )
        self._store[key] = form
        return deepcopy(form)

    def submit(
        self,
        deal_id: int,
        *,
        payload: dict[str, Any],
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
        validation_errors: dict | None = None,
    ) -> DealForm:
        key = self._key(deal_id, schema_version)
        existing = self._store.get(key)
        form = build_submit(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            existing=existing,
            validation_errors=validation_errors,
        )
        self._store[key] = form
        return deepcopy(form)
