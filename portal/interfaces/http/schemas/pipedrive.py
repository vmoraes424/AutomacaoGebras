from __future__ import annotations

from pydantic import BaseModel


class PipedriveUserOut(BaseModel):
    id: int
    name: str
    email: str = ""
    deals_contrato_count: int = 0


class PipedriveDealSummary(BaseModel):
    id: int
    title: str
    cliente: str = ""
    owner_id: int | None = None
    stage_id: int | None = None
    status: str = ""
    pipeline_id: int | None = None
    portal_stage: str = "Contrato"
    form_status: str | None = None
    operational_label: str = "pendente"
    ready_for_form: bool = True
    ready_for_automation: bool = False
