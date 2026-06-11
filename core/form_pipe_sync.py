"""Sincronização bidirecional formulário v1 ↔ Pipedrive (campos migrados)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.form_schema_v1 import FORM_PATH_TO_PIPE, parse_form_payload_v1
from core.pipedrive_fields import (
    PIPE_FIELDS_ADDRESS,
    PIPE_FIELDS_ENUM,
    PIPE_FIELDS_MONETARY,
    PIPE_FIELDS_NUMERIC,
    PIPE_FIELDS_SET,
    PIPE_FIELDS_TEXT_NUMERIC,
    get_val,
    monetary_value_for_pipe,
    option_id_for_enum_field,
    option_ids_for_set_field,
)

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

_ADDRESS_PIPE_HASHES = PIPE_FIELDS_ADDRESS


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
    from core.pipedrive_fields import warm_deal_field_options_cache

    warm_deal_field_options_cache()
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


def overlay_pipe_mapped_fields_from_pipe(
    form_payload: dict[str, Any], pipe_payload: dict[str, Any]
) -> dict[str, Any]:
    """Sobrescreve campos mapeados do rascunho com valores atuais do Pipe (load/refresh)."""
    merged = deepcopy(form_payload)
    for form_path in FORM_PATH_TO_PIPE:
        section, _, field = form_path.partition(".")
        pipe_val = (pipe_payload.get(section) or {}).get(field)
        if _is_empty_form_value(form_path, pipe_val):
            continue
        _set_nested(merged, form_path, pipe_val)
    merged["schema_version"] = merged.get("schema_version") or "v1"
    return merged


def apply_form_field_value(
    form_payload: dict[str, Any], field_path: str, value: Any
) -> dict[str, Any]:
    """Atualiza um campo no payload do formulário (persistência do rascunho)."""
    merged = deepcopy(form_payload)
    _set_nested(merged, field_path, value)
    merged["schema_version"] = merged.get("schema_version") or "v1"
    return merged


def form_payload_to_pipe_custom_fields(
    deal_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    """Payload v1 → custom_fields no formato PATCH v2 do Pipedrive."""
    parsed = parse_form_payload_v1(payload)
    cf: dict[str, Any] = {}
    for path, pipe_hash in FORM_PATH_TO_PIPE.items():
        section, _, field = path.partition(".")
        value = getattr(getattr(parsed, section), field)
        if isinstance(value, bool):
            continue
        cf[pipe_hash] = form_field_to_pipe_value(pipe_hash, path, value)
    return cf


def fetch_deal_for_form(deal_id: int) -> dict[str, Any] | None:
    """Busca deal no Pipedrive para bootstrap/hidratação do formulário."""
    from core.pipedrive_fields import buscar_deal_por_id

    return buscar_deal_por_id(str(deal_id))


def push_form_to_pipedrive(deal_id: int, payload: dict[str, Any]) -> None:
    """Alias para injeção no portal (patchável em testes)."""
    sync_form_payload_to_pipedrive(deal_id, payload)


_TEXTO_NOTA_FORM_ENVIADO = (
    "<p><strong>Portal Gebras:</strong> formulário web <strong>enviado e validado</strong>. "
    "Os campos operacionais foram sincronizados no deal. "
    "A automação (Plune, contrato, Clicksign) segue quando o card permanece na etapa "
    "<strong>Contrato</strong> e <code>FORMULARIO_WEB_ENABLED=true</code>.</p>"
)


def notificar_formulario_enviado_pipedrive(deal_id: int) -> None:
    """Anotação no deal após submit validado (Fase 6)."""
    from core.pipedrive_validations import criar_nota_deal

    criar_nota_deal(str(deal_id), _TEXTO_NOTA_FORM_ENVIADO)


def sync_form_payload_to_pipedrive(deal_id: int, payload: dict[str, Any]) -> None:
    """Grava campos migrados do formulário nos custom_fields do deal (API v2)."""
    if not PIPEDRIVE_API_TOKEN:
        raise PipeSyncError("PIPEDRIVE_API_TOKEN não configurado.")
    custom_fields = form_payload_to_pipe_custom_fields(deal_id, payload)
    _patch_deal_custom_fields(deal_id, custom_fields)


def form_field_path_is_mapped(field_path: str) -> bool:
    return field_path in FORM_PATH_TO_PIPE


def _normalize_form_field_text(field_path: str, value: Any) -> str:
    section, _, field = field_path.partition(".")
    if section == "servicos" or field in _SERVICO_KEYS:
        if value is None or value == "":
            return "0"
        try:
            return str(int(float(str(value).replace(",", "."))))
        except ValueError:
            return "0"
    return str(value or "").strip()


def form_field_to_pipe_value(pipe_hash: str, field_path: str, value: Any) -> Any:
    """Converte valor do formulário para o tipo esperado pelo PATCH v2 do Pipedrive."""
    text = _normalize_form_field_text(field_path, value)
    if pipe_hash in _ADDRESS_PIPE_HASHES:
        return {"value": text}
    if pipe_hash in PIPE_FIELDS_SET:
        try:
            return option_ids_for_set_field(pipe_hash, text)
        except ValueError as exc:
            raise PipeSyncError(str(exc)) from exc
    if pipe_hash in PIPE_FIELDS_ENUM:
        if not text:
            return None
        opt_id = option_id_for_enum_field(pipe_hash, text)
        if opt_id is None:
            raise PipeSyncError(
                f"Opção «{text}» não encontrada nas opções do campo Pipedrive."
            )
        return opt_id
    if pipe_hash in PIPE_FIELDS_MONETARY:
        try:
            return monetary_value_for_pipe(text)
        except ValueError as exc:
            raise PipeSyncError(str(exc)) from exc
    if pipe_hash in PIPE_FIELDS_TEXT_NUMERIC:
        return text
    if pipe_hash in PIPE_FIELDS_NUMERIC:
        try:
            return int(text)
        except ValueError:
            return 0
    return text


def _pipe_field_text_unchanged(deal: dict[str, Any], pipe_hash: str, field_path: str, value: Any) -> bool:
    current = _normalize_form_field_text(field_path, get_val(deal, pipe_hash))
    new = _normalize_form_field_text(field_path, value)
    return current == new


def sync_form_field_to_pipedrive(deal_id: int, field_path: str, value: Any) -> bool:
    """Grava um único campo migrado no custom_field correspondente do deal.

    Retorna True após PATCH bem-sucedido. O frontend evita chamadas redundantes
    quando o valor não mudou desde o focus (blur guard).
    """
    if not form_field_path_is_mapped(field_path):
        raise PipeSyncError(f"Campo não mapeado para o Pipedrive: {field_path}")
    if not PIPEDRIVE_API_TOKEN:
        raise PipeSyncError("PIPEDRIVE_API_TOKEN não configurado.")
    pipe_hash = FORM_PATH_TO_PIPE[field_path]
    pipe_value = form_field_to_pipe_value(pipe_hash, field_path, value)
    _patch_deal_custom_fields(deal_id, {pipe_hash: pipe_value})
    return True


def _patch_deal_custom_fields(deal_id: int, custom_fields: dict[str, Any]) -> None:
    from core.form_schema_v1 import PIPE_TO_FORM_PATH
    from core.pipe_v2_schema import PipeV2SchemaError, validate_pipe_custom_fields

    try:
        validate_pipe_custom_fields(custom_fields, path_by_hash=PIPE_TO_FORM_PATH)
    except PipeV2SchemaError as exc:
        raise PipeSyncError(str(exc)) from exc

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
