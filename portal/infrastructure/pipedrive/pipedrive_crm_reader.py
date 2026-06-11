"""ACL: API Pipedrive → entidades do contexto CRM."""

from __future__ import annotations

from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.pipedrive_stages import deal_esta_em_etapa_contrato
from portal.domain.crm.entities import CrmDeal, CrmUser
from portal.domain.crm.exceptions import CrmReadError
from portal.infrastructure.cache.ttl_singleflight import TtlSingleflightCache

PIPEDRIVE_V2_BASE = "https://api.pipedrive.com/api/v2"
PIPEDRIVE_V1_BASE = "https://api.pipedrive.com/v1"

# Snapshot compartilhado: consultores + cards por dono na mesma leitura do Pipe.
_CONTRATO_DEALS_CACHE: TtlSingleflightCache[list[CrmDeal]] = TtlSingleflightCache(ttl_seconds=15.0)
_USERS_CACHE: TtlSingleflightCache[list[CrmUser]] = TtlSingleflightCache(ttl_seconds=15.0)


class PipedriveCrmReader:
    def __init__(self, api_token: str | None = None) -> None:
        self._token = (api_token or PIPEDRIVE_API_TOKEN).strip()
        if not self._token:
            raise CrmReadError("PIPEDRIVE_API_TOKEN não configurado.")

    def _headers(self) -> dict[str, str]:
        return {"x-api-token": self._token}

    @staticmethod
    def invalidate_crm_cache() -> None:
        _CONTRATO_DEALS_CACHE.invalidate()
        _USERS_CACHE.invalidate()

    def list_users(self, *, fresh: bool = False) -> list[CrmUser]:
        return _USERS_CACHE.get_or_fetch(
            fresh=fresh,
            fetcher=self._fetch_users,
        )

    def list_open_deals_in_contrato_stage(
        self,
        *,
        owner_user_id: int | None = None,
        fresh: bool = False,
    ) -> list[CrmDeal]:
        all_deals = _CONTRATO_DEALS_CACHE.get_or_fetch(
            fresh=fresh,
            fetcher=self._fetch_all_contrato_deals,
        )
        if owner_user_id is None:
            return all_deals
        return [d for d in all_deals if d.owner_id == owner_user_id]

    def _fetch_users(self) -> list[CrmUser]:
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

    def _fetch_all_contrato_deals(self) -> list[CrmDeal]:
        raw_deals: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            params: dict[str, Any] = {"status": "open", "limit": 500}
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
                    raw_deals.append(deal)

            cursor = (body.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break

        org_ids = {
            int(d["org_id"])
            for d in raw_deals
            if d.get("org_id") is not None
        }
        org_names = self._fetch_org_names(org_ids)
        return [self._to_crm_deal(deal, org_names) for deal in raw_deals]

    def _fetch_org_names(self, org_ids: set[int]) -> dict[int, str]:
        names: dict[int, str] = {}
        for org_id in sorted(org_ids):
            response = requests.get(
                f"{PIPEDRIVE_V2_BASE}/organizations/{org_id}",
                headers=self._headers(),
                timeout=30,
            )
            if not response.ok:
                continue
            data = response.json().get("data") or {}
            names[org_id] = str(data.get("name") or "").strip()
        return names

    @staticmethod
    def _resolve_owner_id(deal: dict[str, Any]) -> int | None:
        for key in ("owner_id", "user_id"):
            raw = deal.get(key)
            if raw is None:
                continue
            if isinstance(raw, dict):
                nested = raw.get("id") if raw.get("id") is not None else raw.get("value")
                if nested is not None:
                    return int(nested)
                continue
            try:
                return int(raw)
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _to_crm_deal(
        deal: dict[str, Any],
        org_names: dict[int, str] | None = None,
    ) -> CrmDeal:
        owner_id = PipedriveCrmReader._resolve_owner_id(deal)
        org_raw = deal.get("org_id")
        org_id = int(org_raw) if org_raw is not None else None
        org_name = (org_names or {}).get(org_id, "") if org_id else ""
        return CrmDeal(
            id=int(deal["id"]),
            title=str(deal.get("title") or "").strip(),
            owner_id=owner_id,
            stage_id=int(deal["stage_id"]) if deal.get("stage_id") is not None else None,
            status=str(deal.get("status") or ""),
            pipeline_id=(
                int(deal["pipeline_id"]) if deal.get("pipeline_id") is not None else None
            ),
            org_id=org_id,
            org_name=org_name,
        )
