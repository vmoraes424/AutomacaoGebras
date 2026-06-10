from __future__ import annotations

from enum import StrEnum


class FormStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

    def is_editable(self) -> bool:
        return self in (FormStatus.DRAFT, FormStatus.ERROR)
