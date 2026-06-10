"""ACL: API Pipedrive → entidades do contexto CRM."""

from __future__ import annotations

from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.pipedrive_stages import deal_esta_em_etapa_contrato
from portal.domain.crm.entities import CrmDeal, CrmUser
from portal.domain.crm.exceptions import CrmReadError

PIPEDRIVE_V2_BASE = "https://api.pipedrive.com/api/v2"
PIPEDRIVE_V1_BASE = "https://api.pipedrive.com/v1"


class PipedriveCrmReader:
    def __init__(self, api_token: str | None = None) -> None:
        self._token = (api_token or PIPEDRIVE_API_TOKEN).strip()
        if not self._token:
            raise CrmReadError("PIPEDRIVE_API_TOKEN não configurado.")

    def _headers(self) -> dict[str, str]:
        return {"x-api-token": self._token}

    def list_users(self) -> list[CrmUser]:
        response = requests.get(
            f"{PIPEDRIVE_V1_BASE}/users",
            headers=self._headers(),
            params={"limit": 500},
            timeout=60,
        )
        if not response.ok:
            raise CrmReadError(
                f"Pipedrive users -> {response.status_code}: {response.text[:500]}"
            )
        users = response.json().get("data") or []
        return [
            CrmUser(
                id=int(u["id"]),
                name=str(u.get("name") or "").strip(),
                email=str(u.get("email") or "").strip(),
            )
            for u in users
            if u.get("id") is not None and u.get("active_flag") is not False
        ]

    def list_open_deals_in_contrato_stage(
        self, *, owner_user_id: int | None = None
    ) -> list[CrmDeal]:
        deals: list[CrmDeal] = []
        cursor: str | None = None

        while True:
            params: dict[str, Any] = {"status": "open", "limit": 500}
            if owner_user_id is not None:
                params["owner_id"] = owner_user_id
            if cursor:
                params["cursor"] = cursor

            response = requests.get(
                f"{PIPEDRIVE_V2_BASE}/deals",
                headers=self._headers(),
                params=params,
                timeout=60,
            )
            if not response.ok:
                raise CrmReadError(
                    f"Pipedrive deals -> {response.status_code}: {response.text[:500]}"
                )

            body = response.json()
            page = body.get("data") or []
            if isinstance(page, dict):
                page = [page]

            for deal in page:
                if deal_esta_em_etapa_contrato(deal):
                    deals.append(self._to_crm_deal(deal))

            cursor = (body.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break

        return deals

    @staticmethod
    def _to_crm_deal(deal: dict[str, Any]) -> CrmDeal:
        owner = deal.get("owner_id")
        return CrmDeal(
            id=int(deal["id"]),
            title=str(deal.get("title") or "").strip(),
            owner_id=int(owner) if owner is not None else None,
            stage_id=int(deal["stage_id"]) if deal.get("stage_id") is not None else None,
            status=str(deal.get("status") or ""),
            pipeline_id=(
                int(deal["pipeline_id"]) if deal.get("pipeline_id") is not None else None
            ),
        )
