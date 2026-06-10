from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FormDraftIn(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    owner_user_id: int | None = None
    owner_name: str = ""
    deal_title: str = ""
    schema_version: str = "v1"


class FormSubmitIn(FormDraftIn):
    """Mesmo corpo do rascunho; validação de domínio na Fase 4."""


class FormRecordOut(BaseModel):
    deal_id: int
    status: str
    schema_version: str
    payload: dict[str, Any]
    owner_user_id: int | None = None
    owner_name: str = ""
    deal_title: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    submitted_at: datetime | None = None
    validation_errors: dict[str, Any] | None = None
