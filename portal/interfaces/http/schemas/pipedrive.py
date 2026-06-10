from __future__ import annotations

from pydantic import BaseModel


class PipedriveUserOut(BaseModel):
    id: int
    name: str
    email: str = ""


class PipedriveDealSummary(BaseModel):
    id: int
    title: str
    owner_id: int | None = None
    stage_id: int | None = None
    status: str = ""
    pipeline_id: int | None = None
