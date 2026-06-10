"""Sincronização bidirecional formulário v1 ↔ Pipedrive (campos migrados)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.form_schema_v1 import FORM_PATH_TO_PIPE, form_payload_to_deal_dict, parse_form_payload_v1
from core.pipedrive_fields import get_val

PIPEDRIVE_V2_DEALS = "https://api.pipedrive.com/api/v2/deals"

_SERVICO_KEYS = frozenset(
    {
        "sole_web",
        "sole_consultoria",
        "gestao_acl",
        "gestao_usina_fotovoltaica",
        "gestao_qualidade_energia",
        "quantidade_ucs",
    }
)


class PipeSyncError(RuntimeError):
    pass


def _coerce_servico(value: str) -> int:
    texto = str(value or "").strip()
    if not texto:
        return 0
    try:
        return int(float(texto.replace(",", ".")))
    except ValueError:
        return 0


def _set_nested(payload: dict[str, Any], path: str, value: Any) -> None:
    section, _, field = path.partition(".")
    if section not in payload:
        payload[section] = {}
    payload[section][field] = value


def deal_to_form_payload_v1(deal: dict[str, Any]) -> dict[str, Any]:
    """Lê custom_fields do deal Pipe → payload v1 legível."""
    payload: dict[str, Any] = {"schema_version": "v1"}
    for form_path, pipe_hash in FORM_PATH_TO_PIPE.items():
        raw = get_val(deal, pipe_hash)
        section, _, field = form_path.partition(".")
        if field in _SERVICO_KEYS:
            value: Any = _coerce_servico(raw)
        else:
            value = raw
        _set_nested(payload, form_path, value)
    payload.setdefault("anexos", {})["proposta_comercial_anexada"] = False
    return payload


def _is_empty_form_value(path: str, value: Any) -> bool:
    if path.startswith("servicos."):
        return value is None or value == "" or value == 0
    return value is None or str(value).strip() == ""


def hydrate_form_payload_from_pipe(
    form_payload: dict[str, Any], pipe_payload: dict[str, Any]
) -> dict[str, Any]:
    """Preenche campos vazios do formulário com valores atuais do Pipe."""
    merged = deepcopy(form_payload)
    for form_path in FORM_PATH_TO_PIPE:
        section, _, field = form_path.partition(".")
        current = (merged.get(section) or {}).get(field)
        if not _is_empty_form_value(form_path, current):
            continue
        pipe_val = (pipe_payload.get(section) or {}).get(field)
        if _is_empty_form_value(form_path, pipe_val):
            continue
        _set_nested(merged, form_path, pipe_val)
    merged["schema_version"] = merged.get("schema_version") or "v1"
    return merged


def form_payload_to_pipe_custom_fields(
    deal_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    """Payload v1 → dict de custom_fields (hashes) para PATCH no Pipedrive."""
    parsed = parse_form_payload_v1(payload)
    deal = form_payload_to_deal_dict(deal_id, parsed)
    return deal.get("custom_fields") or {}


def fetch_deal_for_form(deal_id: int) -> dict[str, Any] | None:
    """Busca deal no Pipedrive para bootstrap/hidratação do formulário."""
    from core.pipedrive_fields import buscar_deal_por_id

    return buscar_deal_por_id(str(deal_id))


def push_form_to_pipedrive(deal_id: int, payload: dict[str, Any]) -> None:
    """Alias para injeção no portal (patchável em testes)."""
    sync_form_payload_to_pipedrive(deal_id, payload)


def sync_form_payload_to_pipedrive(deal_id: int, payload: dict[str, Any]) -> None:
    """Grava campos migrados do formulário nos custom_fields do deal (API v2)."""
    if not PIPEDRIVE_API_TOKEN:
        raise PipeSyncError("PIPEDRIVE_API_TOKEN não configurado.")
    custom_fields = form_payload_to_pipe_custom_fields(deal_id, payload)
    response = requests.patch(
        f"{PIPEDRIVE_V2_DEALS}/{int(deal_id)}",
        headers={"x-api-token": PIPEDRIVE_API_TOKEN},
        json={"custom_fields": custom_fields},
        timeout=60,
    )
    if not response.ok:
        raise PipeSyncError(
            f"Pipedrive PATCH deal {deal_id} -> {response.status_code}: "
            f"{response.text[:500]}"
        )
