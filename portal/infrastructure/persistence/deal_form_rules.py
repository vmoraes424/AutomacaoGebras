from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.exceptions import DealFormNotEditableError
from portal.domain.formulario.value_objects import FormStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def assert_editable(existing: DealForm | None, deal_id: int) -> None:
    if existing is not None and not existing.status.is_editable():
        raise DealFormNotEditableError(deal_id, str(existing.status))


def build_draft(
    deal_id: int,
    *,
    payload: dict[str, Any],
    schema_version: str,
    owner_user_id: int | None,
    owner_name: str,
    deal_title: str,
    existing: DealForm | None,
) -> DealForm:
    assert_editable(existing, deal_id)
    now = _now()
    return DealForm(
        deal_id=int(deal_id),
        status=FormStatus.DRAFT,
        schema_version=schema_version,
        payload=deepcopy(payload),
        owner_user_id=owner_user_id,
        owner_name=owner_name,
        deal_title=deal_title,
        created_at=existing.created_at if existing else now,
        updated_at=now,
        submitted_at=None,
        validation_errors={},
    )


def build_submit(
    deal_id: int,
    *,
    payload: dict[str, Any],
    schema_version: str,
    owner_user_id: int | None,
    owner_name: str,
    deal_title: str,
    existing: DealForm | None,
    validation_errors: dict | None,
) -> DealForm:
    assert_editable(existing, deal_id)
    now = _now()
    errors = validation_errors or {}
    if errors:
        return DealForm(
            deal_id=int(deal_id),
            status=FormStatus.ERROR,
            schema_version=schema_version,
            payload=deepcopy(payload),
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            submitted_at=None,
            validation_errors=deepcopy(errors),
        )
    return DealForm(
        deal_id=int(deal_id),
        status=FormStatus.VALIDATED,
        schema_version=schema_version,
        payload=deepcopy(payload),
        owner_user_id=owner_user_id,
        owner_name=owner_name,
        deal_title=deal_title,
        created_at=existing.created_at if existing else now,
        updated_at=now,
        submitted_at=now,
        validation_errors={},
    )
