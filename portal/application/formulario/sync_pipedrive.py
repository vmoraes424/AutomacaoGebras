from __future__ import annotations

from typing import Any, Callable

from portal.domain.formulario.repositories import DealFormRepository

PipeSync = Callable[[int, dict[str, Any]], None]
FieldPipeSync = Callable[[int, str, Any], bool]


def _default_pipe_sync(deal_id: int, payload: dict[str, Any]) -> None:
    from core.form_pipe_sync import push_form_to_pipedrive

    push_form_to_pipedrive(deal_id, payload)


def _default_field_pipe_sync(deal_id: int, field_path: str, value: Any) -> bool:
    from core.form_pipe_sync import sync_form_field_to_pipedrive

    return sync_form_field_to_pipedrive(deal_id, field_path, value)


class SyncDealFormToPipedrive:
    """Envia todos os campos migrados do formulário ao Pipedrive."""

    def __init__(self, pipe_sync: PipeSync | None = None) -> None:
        self._pipe_sync = pipe_sync or _default_pipe_sync

    def execute(self, deal_id: int, *, payload: dict[str, Any]) -> dict[str, Any]:
        from portal.application.formulario.deal_eligibility import fetch_deal_eligible_for_form

        fetch_deal_eligible_for_form(deal_id)
        self._pipe_sync(deal_id, payload)
        return {
            "deal_id": deal_id,
            "synced": True,
            "message": "Campos sincronizados no Pipedrive.",
        }


class SyncDealFormFieldToPipedrive:
    """Envia um campo migrado ao Pipedrive (ex.: blur do input)."""

    def __init__(
        self,
        repository: DealFormRepository,
        *,
        field_pipe_sync: FieldPipeSync | None = None,
    ) -> None:
        self._repository = repository
        self._field_pipe_sync = field_pipe_sync or _default_field_pipe_sync

    def sync_field(
        self,
        deal_id: int,
        *,
        field_path: str,
        value: Any,
    ) -> dict[str, Any]:
        synced = self._field_pipe_sync(deal_id, field_path, value)
        return {
            "deal_id": deal_id,
            "field_path": field_path,
            "synced": synced,
            "skipped": not synced,
        }

    def execute(
        self,
        deal_id: int,
        *,
        field_path: str,
        value: Any,
        schema_version: str = "v1",
        owner_user_id: int | None = None,
        owner_name: str = "",
        deal_title: str = "",
    ) -> dict[str, Any]:
        result = self.sync_field(deal_id, field_path=field_path, value=value)
        self.persist_draft_field(
            deal_id,
            field_path,
            value,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
        )
        return result

    def persist_draft_field(
        self,
        deal_id: int,
        field_path: str,
        value: Any,
        *,
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
    ) -> None:
        from core.form_pipe_sync import apply_form_field_value

        existing = self._repository.get_by_deal_id(deal_id, schema_version=schema_version)
        if existing is not None and not existing.status.is_editable():
            return

        base_payload = existing.payload if existing is not None else {"schema_version": schema_version}
        payload = apply_form_field_value(base_payload, field_path, value)
        self._repository.save_draft(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=(
                existing.owner_user_id if existing is not None else owner_user_id
            ),
            owner_name=existing.owner_name if existing is not None else owner_name,
            deal_title=existing.deal_title if existing is not None else deal_title,
        )
