"""ACL: API Pipedrive → snapshot Contrato (deals + users), cacheado no portal."""

from __future__ import annotations

from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.pipedrive_stages import list_stage_ids_etapa_contrato
from portal.domain.crm.entities import ContratoSnapshot, CrmDeal, CrmUser
from portal.domain.crm.exceptions import CrmReadError
from portal.infrastructure.cache.ttl_singleflight import TtlSingleflightCache

PIPEDRIVE_V2_BASE = "https://api.pipedrive.com/api/v2"
PIPEDRIVE_V1_BASE = "https://api.pipedrive.com/api/v1"

# Uma leitura Pipe serve /pipedrive/users e /pipedrive/deals.
_SNAPSHOT_CACHE: TtlSingleflightCache[ContratoSnapshot] = TtlSingleflightCache(ttl_seconds=30.0)
_ORG_IDS_CHUNK = 100


class PipedriveCrmReader:
    def __init__(self, api_token: str | None = None) -> None:
        self._token = (api_token or PIPEDRIVE_API_TOKEN).strip()
        if not self._token:
            raise CrmReadError("PIPEDRIVE_API_TOKEN não configurado.")

    def _headers(self) -> dict[str, str]:
        return {"x-api-token": self._token}

    @staticmethod
    def invalidate_crm_cache() -> None:
        _SNAPSHOT_CACHE.invalidate()

    def get_contrato_snapshot(self, *, fresh: bool = False) -> ContratoSnapshot:
        return _SNAPSHOT_CACHE.get_or_fetch(
            fresh=fresh,
            fetcher=self._fetch_contrato_snapshot,
        )

    def list_users(self, *, fresh: bool = False) -> list[CrmUser]:
        return list(self.get_contrato_snapshot(fresh=fresh).users)

    def list_open_deals_in_contrato_stage(
        self,
        *,
        owner_user_id: int | None = None,
        fresh: bool = False,
    ) -> list[CrmDeal]:
        deals = list(self.get_contrato_snapshot(fresh=fresh).deals)
        if owner_user_id is None:
            return deals
        return [d for d in deals if d.owner_id == owner_user_id]

    def _fetch_contrato_snapshot(self) -> ContratoSnapshot:
        users = self._fetch_users()
        deals = self._fetch_contrato_deals()
        return ContratoSnapshot(deals=tuple(deals), users=tuple(users))

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

    def _fetch_deals_open_in_stage(self, stage_id: int) -> list[dict[str, Any]]:
        raw_deals: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            params: dict[str, Any] = {
                "status": "open",
                "stage_id": stage_id,
                "limit": 500,
            }
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
                    f"Pipedrive deals stage={stage_id} -> "
                    f"{response.status_code}: {response.text[:500]}"
                )

            body = response.json()
            page = body.get("data") or []
            if isinstance(page, dict):
                page = [page]
            raw_deals.extend(page)

            cursor = (body.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break

        return raw_deals

    def _fetch_contrato_deals(self) -> list[CrmDeal]:
        stage_ids = list_stage_ids_etapa_contrato()
        if not stage_ids:
            return []

        raw_deals: list[dict[str, Any]] = []
        seen_ids: set[int] = set()

        for stage_id in stage_ids:
            for deal in self._fetch_deals_open_in_stage(stage_id):
                deal_id = deal.get("id")
                if deal_id is None:
                    continue
                deal_id_int = int(deal_id)
                if deal_id_int in seen_ids:
                    continue
                seen_ids.add(deal_id_int)
                raw_deals.append(deal)

        org_ids = {
            int(d["org_id"])
            for d in raw_deals
            if d.get("org_id") is not None
        }
        org_names = self._fetch_org_names(org_ids)
        return [self._to_crm_deal(deal, org_names) for deal in raw_deals]

    def _fetch_org_names(self, org_ids: set[int]) -> dict[int, str]:
        if not org_ids:
            return {}

        names: dict[int, str] = {}
        sorted_ids = sorted(org_ids)

        for offset in range(0, len(sorted_ids), _ORG_IDS_CHUNK):
            chunk = sorted_ids[offset : offset + _ORG_IDS_CHUNK]
            response = requests.get(
                f"{PIPEDRIVE_V2_BASE}/organizations",
                headers=self._headers(),
                params={"ids": ",".join(str(i) for i in chunk), "limit": 500},
                timeout=30,
            )
            if not response.ok:
                continue
            for org in response.json().get("data") or []:
                org_id = org.get("id")
                if org_id is None:
                    continue
                name = str(org.get("name") or "").strip()
                if name:
                    names[int(org_id)] = name

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
