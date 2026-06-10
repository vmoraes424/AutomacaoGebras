from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.value_objects import FormStatus


def _parse_dt(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _parse_json_field(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        return json.loads(value) if value else {}
    return {}


def row_to_deal_form(row: dict[str, Any]) -> DealForm:
    return DealForm(
        deal_id=int(row["deal_id"]),
        status=FormStatus(str(row["status"])),
        schema_version=str(row["schema_version"]),
        payload=_parse_json_field(row.get("payload_json")),
        owner_user_id=(
            int(row["owner_user_id"]) if row.get("owner_user_id") is not None else None
        ),
        owner_name=str(row.get("owner_name") or ""),
        deal_title=str(row.get("deal_title") or ""),
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
        submitted_at=_parse_dt(row.get("submitted_at")),
        validation_errors=_parse_json_field(row.get("validation_errors_json")),
    )


def utc_now_iso() -> str:
    from datetime import timezone

    return datetime.now(timezone.utc).isoformat()
