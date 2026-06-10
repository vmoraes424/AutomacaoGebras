from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from portal.domain.formulario.value_objects import FormStatus


@dataclass
class DealForm:
    """Agregado do formulário operacional vinculado a um deal Pipedrive."""

    deal_id: int
    status: FormStatus
    schema_version: str
    payload: dict[str, Any]
    owner_user_id: int | None = None
    owner_name: str = ""
    deal_title: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    submitted_at: datetime | None = None
    validation_errors: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        return {
            "deal_id": self.deal_id,
            "status": str(self.status),
            "schema_version": self.schema_version,
            "payload": self.payload,
            "owner_user_id": self.owner_user_id,
            "owner_name": self.owner_name,
            "deal_title": self.deal_title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "submitted_at": self.submitted_at,
            "validation_errors": self.validation_errors or None,
        }

    def status_snapshot(self) -> dict[str, Any]:
        return {
            "deal_id": self.deal_id,
            "status": str(self.status),
            "schema_version": self.schema_version,
            "updated_at": self.updated_at,
        }
