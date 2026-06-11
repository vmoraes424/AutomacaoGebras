"""Caso de uso: metadados de anexos do deal no Pipedrive (proposta + template contrato)."""

from __future__ import annotations

from core.form_readiness_v1 import get_deal_attachments_meta


class GetDealFormAttachments:
    def execute(self, deal_id: int, *, fresh: bool = False) -> dict:
        return get_deal_attachments_meta(deal_id, fresh=fresh)
