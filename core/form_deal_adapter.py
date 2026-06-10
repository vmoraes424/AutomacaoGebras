"""
Adaptador formulario web v1 → deal Pipedrive para o worker.

Precedencia: campos migrados no formulario web sobrescrevem custom_fields do Pipe.
Metadados do card (id, titulo, dono, etapa) permanecem no deal original.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from core.config import FORMULARIO_WEB_ENABLED
from core.form_schema_v1 import form_payload_to_deal_dict, parse_form_payload_v1

# Status prontos para automacao (submit ja validou dominio na Fase 4)
FORM_STATUS_READY_FOR_WORKER = frozenset(
    {"validated", "processing", "processed"}
)


@dataclass(frozen=True)
class DealFormSnapshot:
    deal_id: int
    status: str
    schema_version: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class PrepareDealResult:
    deal: dict[str, Any]
    source: str  # "pipe" | "form_merged"
    skipped_reason: str | None = None
    form_status: str | None = None

    @property
    def uses_formulario_web(self) -> bool:
        return self.source == "form_merged"


def load_deal_form_from_db(
    deal_id: int, *, schema_version: str = "v1"
) -> DealFormSnapshot | None:
    """Leitura MySQL `deal_forms` (sem depender do pacote portal)."""
    from core.database import db_conn

    with db_conn() as conn:
        row = conn.execute(
            """
            SELECT status, schema_version, payload_json
            FROM deal_forms
            WHERE deal_id = %s AND schema_version = %s
            """,
            (deal_id, schema_version),
        ).fetchone()
    if not row:
        return None
    payload = row["payload_json"]
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8")
    if isinstance(payload, str):
        payload = json.loads(payload)
    return DealFormSnapshot(
        deal_id=int(deal_id),
        status=str(row["status"]),
        schema_version=str(row["schema_version"]),
        payload=payload if isinstance(payload, dict) else {},
    )


def merge_form_into_deal(deal_pipe: dict[str, Any], form_payload: dict[str, Any]) -> dict[str, Any]:
    """Mescla payload v1 nos custom_fields do deal (form > Pipe nos campos migrados)."""
    merged = deepcopy(deal_pipe)
    deal_id = int(merged.get("id") or 0)
    parsed = parse_form_payload_v1(form_payload)
    form_deal = form_payload_to_deal_dict(deal_id, parsed)
    cf = dict(merged.get("custom_fields") or {})
    cf.update(form_deal.get("custom_fields") or {})
    merged["custom_fields"] = cf
    return merged


def preparar_deal_para_automacao(
    deal_pipe: dict[str, Any],
    *,
    formulario_web_enabled: bool | None = None,
    form_loader=None,
) -> PrepareDealResult:
    """
    Resolve o deal usado pelo worker.

    - Flag desligada: deal Pipe inalterado (legado).
    - Flag ligada + form validated: merge form > Pipe.
    - Flag ligada + sem form validated: skipped_reason (worker nao processa).
    """
    enabled = FORMULARIO_WEB_ENABLED if formulario_web_enabled is None else formulario_web_enabled
    if not enabled:
        return PrepareDealResult(deal=deepcopy(deal_pipe), source="pipe")

    loader = form_loader or load_deal_form_from_db
    deal_id = int(deal_pipe.get("id") or 0)
    form = loader(deal_id)
    if form is None:
        return PrepareDealResult(
            deal=deepcopy(deal_pipe),
            source="pipe",
            skipped_reason="formulario_web_ausente",
            form_status=None,
        )
    if form.status not in FORM_STATUS_READY_FOR_WORKER:
        return PrepareDealResult(
            deal=deepcopy(deal_pipe),
            source="pipe",
            skipped_reason="formulario_web_nao_validado",
            form_status=form.status,
        )

    merged = merge_form_into_deal(deal_pipe, form.payload)
    return PrepareDealResult(
        deal=merged,
        source="form_merged",
        form_status=form.status,
    )


def deal_para_automacao(deal_pipe: dict[str, Any], **kwargs) -> dict[str, Any]:
    """Atalho: retorna apenas o dict do deal (levanta se deve ignorar)."""
    result = preparar_deal_para_automacao(deal_pipe, **kwargs)
    if result.skipped_reason:
        raise FormDealSkippedError(result.skipped_reason, form_status=result.form_status)
    return result.deal


class FormDealSkippedError(Exception):
    def __init__(self, reason: str, *, form_status: str | None = None) -> None:
        self.reason = reason
        self.form_status = form_status
        super().__init__(reason)
