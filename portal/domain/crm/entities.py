from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrmUser:
    id: int
    name: str
    email: str = ""

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}


@dataclass(frozen=True)
class CrmDeal:
    id: int
    title: str
    owner_id: int | None = None
    stage_id: int | None = None
    status: str = ""
    pipeline_id: int | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "owner_id": self.owner_id,
            "stage_id": self.stage_id,
            "status": self.status,
            "pipeline_id": self.pipeline_id,
        }
