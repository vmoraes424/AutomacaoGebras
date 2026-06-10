from __future__ import annotations

from typing import Any, Callable

from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.repositories import DealFormRepository
from portal.domain.formulario.value_objects import FormStatus

PayloadValidator = Callable[[int, dict[str, Any]], dict[str, str]]
PipeSync = Callable[[int, dict[str, Any]], None]


def _noop_validator(_deal_id: int, _payload: dict[str, Any]) -> dict[str, str]:
    return {}


def _noop_pipe_sync(_deal_id: int, _payload: dict[str, Any]) -> None:
    return None


class SubmitDealForm:
    def __init__(
        self,
        repository: DealFormRepository,
        validator: PayloadValidator | None = None,
        pipe_sync: PipeSync | None = None,
    ) -> None:
        self._repository = repository
        self._validator = validator or _noop_validator
        self._pipe_sync = pipe_sync or _noop_pipe_sync

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
        validation_errors = self._validator(deal_id, payload)
        form = self._repository.submit(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            validation_errors=validation_errors or None,
        )
        if form.status == FormStatus.VALIDATED:
            if self._pipe_sync is not _noop_pipe_sync:
                self._pipe_sync(deal_id, payload)
            else:
                from core.form_pipe_sync import push_form_to_pipedrive

                push_form_to_pipedrive(deal_id, payload)
        return form
