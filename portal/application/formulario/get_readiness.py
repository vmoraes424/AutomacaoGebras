"""Caso de uso: prontidão do formulário (checklist + anexos Pipe)."""

from __future__ import annotations

from typing import Any

from core.form_readiness_v1 import build_form_readiness


class GetDealFormReadiness:
    def execute(self, deal_id: int, *, payload: dict[str, Any]) -> dict[str, Any]:
        return build_form_readiness(deal_id, payload)
