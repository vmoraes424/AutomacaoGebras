"""Prontidão do formulário v1 — checklist alinhado a validate_form_payload_v1 + anexos Pipe."""

from __future__ import annotations

import threading
import time
from typing import Any, Literal

from .form_schema_v1 import (
    FORM_PATH_TO_PIPE,
    FormPayloadV1,
    form_payload_to_deal_dict,
    parse_form_payload_v1,
)
from .form_uc_hub import instalacao_tem_servico, normalize_hub_payload
from .form_validation_v1 import validate_form_payload_v1
from .pipedrive_fields import (
    CAMPOS_CONTRATO_OBRIGATORIOS,
    CAMPOS_CONTRATO_OPCIONAIS,
)
from .pipedrive_files import (
    escolher_docx_contrato_padrao,
    listar_arquivos_deal,
    tem_arquivo_proposta_comercial,
)
from .pipedrive_validations import _implantacao_exige_data_pagamento

_ATTACHMENTS_TTL_SEC = 60.0
_attachments_cache: dict[int, tuple[float, dict[str, Any]]] = {}
_attachments_lock = threading.Lock()

ItemStatus = Literal["ok", "pending", "error", "info"]

READINESS_SECTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "cliente",
        "Cliente",
        (
            "cliente.contratante",
            "cliente.documento",
            "cliente.endereco",
            "cliente.cep",
            "cliente.municipio_estado",
            "cliente.inscricao_estadual",
            "cliente.inscricao_municipal",
            "cliente.notas",
            "cliente.codigo_cliente_instalacao",
        ),
    ),
    ("servicos", "Serviços UC", ("_servicos_uc",)),
    (
        "valores_datas",
        "Valores e datas",
        (
            "valores.valor_recorrencia",
            "valores.valor_implantacao",
            "datas.data_pagamento_implantacao",
            "datas.data_primeira_cobranca",
        ),
    ),
    (
        "comercial",
        "Comercial",
        (
            "comercial.filial",
            "comercial.regional",
            "comercial.consultor",
            "comercial.percentual_exito",
        ),
    ),
    (
        "signatarios",
        "Signatários",
        (
            "signatarios.email_assinante_contrato",
            "signatarios.email_financeiro_contratante",
            "signatarios.email_gestor_contratante",
            "signatarios.email_consultor_gebras",
            "signatarios.email_coordenador_gebras",
            "signatarios.email_diretor_gebras",
        ),
    ),
    ("hub", "HUB", ("hub.observacoes_detalhes",)),
    ("anexos", "Anexos", ("anexos.proposta_comercial_anexada",)),
)

FIELD_LABELS: dict[str, str] = {
    "_servicos_uc": "Pelo menos um serviço UC",
    "anexos.proposta_comercial_anexada": "Proposta comercial (Pipedrive)",
}

for _label, _code, _tipo in CAMPOS_CONTRATO_OBRIGATORIOS:
    from .form_schema_v1 import PIPE_TO_FORM_PATH

    _path = PIPE_TO_FORM_PATH.get(_code)
    if _path:
        FIELD_LABELS[_path] = _label

FIELD_LABELS["_hub_uc_matrix"] = "Matriz UC × serviço × valor"
FIELD_LABELS["hub.observacoes_detalhes"] = "HUB — Observações (detalhes)"


def _get_path_value(parsed: FormPayloadV1, path: str) -> Any:
    section, _, field = path.partition(".")
    return getattr(getattr(parsed, section), field)


def _path_filled(parsed: FormPayloadV1, path: str) -> bool:
    value = _get_path_value(parsed, path)
    if path.startswith("servicos."):
        return isinstance(value, int) and value > 0
    if path == "anexos.proposta_comercial_anexada":
        return bool(value)
    return bool(str(value or "").strip())


def _skip_path(deal: dict, path: str, parsed: FormPayloadV1 | None = None) -> bool:
    if path in {
        "hub.observacoes_detalhes",
        "_servicos_uc",
        "_hub_uc_matrix",
        "anexos.proposta_comercial_anexada",
    }:
        return False
    pipe_hash = FORM_PATH_TO_PIPE.get(path)
    if pipe_hash in CAMPOS_CONTRATO_OPCIONAIS:
        return True
    if path == "datas.data_pagamento_implantacao" and not _implantacao_exige_data_pagamento(deal):
        return True
    return False


def _fetch_deal_attachments(deal_id: int) -> dict[str, Any]:
    """Anexos do deal no Pipedrive: proposta comercial e template contrato_padrao."""
    out: dict[str, Any] = {
        "proposta_comercial_anexada": False,
        "contrato_template": {
            "source": "padrao",
            "filename": None,
        },
        "attachments_error": None,
    }
    try:
        arquivos = listar_arquivos_deal(str(deal_id))
    except RuntimeError as exc:
        out["attachments_error"] = str(exc)
        return out

    out["proposta_comercial_anexada"] = tem_arquivo_proposta_comercial(arquivos)
    tpl = escolher_docx_contrato_padrao(arquivos)
    if tpl:
        out["contrato_template"] = {
            "source": "custom",
            "filename": str(tpl.get("name") or "").strip() or None,
        }
    return out


def inspect_deal_attachments(deal_id: int, *, fresh: bool = False) -> dict[str, Any]:
    now = time.monotonic()
    if not fresh:
        with _attachments_lock:
            cached = _attachments_cache.get(deal_id)
            if cached and now - cached[0] < _ATTACHMENTS_TTL_SEC:
                return cached[1]
    result = _fetch_deal_attachments(deal_id)
    with _attachments_lock:
        _attachments_cache[deal_id] = (now, result)
    return result


def invalidate_deal_attachments_cache(deal_id: int | None = None) -> None:
    with _attachments_lock:
        if deal_id is None:
            _attachments_cache.clear()
        else:
            _attachments_cache.pop(deal_id, None)


def _peek_attachments_cache(deal_id: int) -> dict[str, Any] | None:
    now = time.monotonic()
    with _attachments_lock:
        cached = _attachments_cache.get(deal_id)
        if cached and now - cached[0] < _ATTACHMENTS_TTL_SEC:
            return cached[1]
    return None


def get_deal_attachments_meta(deal_id: int, *, fresh: bool = False) -> dict[str, Any]:
    """Resposta estável para GET /forms/{id}/attachments."""
    meta = inspect_deal_attachments(deal_id, fresh=fresh)
    tpl = meta.get("contrato_template") or {}
    tpl_source = tpl.get("source") or "padrao"
    return {
        "deal_id": deal_id,
        "proposta_comercial_anexada": meta.get("proposta_comercial_anexada") is True,
        "contrato": {
            "source": tpl_source,
            "filename": tpl.get("filename"),
            "label": (
                f"Contrato a partir do arquivo enviado ({tpl.get('filename')})"
                if tpl_source == "custom" and tpl.get("filename")
                else "Contrato a partir do modelo padrão Gebras"
            ),
        },
        "error": meta.get("attachments_error"),
    }


def warmup_deal_attachments_cache(deal_id: int) -> None:
    """Pré-carrega anexos do Pipe (opcional — frontend usa GET /attachments)."""
    if _peek_attachments_cache(deal_id) is not None:
        return
    inspect_deal_attachments(deal_id, fresh=False)


def _instalacao_ativa(inst: Any) -> bool:
    if hasattr(inst, "model_dump"):
        data = inst.model_dump()
    elif isinstance(inst, dict):
        data = inst
    else:
        data = dict(inst)
    return instalacao_tem_servico(data)


def _hub_section_paths(parsed: FormPayloadV1) -> tuple[str, ...]:
    if parsed.hub.instalacoes:
        return ("_hub_uc_matrix",)
    return ("hub.observacoes_detalhes",)


def build_form_readiness(
    deal_id: int,
    payload: dict[str, Any],
    *,
    interactive: bool = True,
) -> dict[str, Any]:
    """
    Retorna prontidão para envio: seções, itens, resumo.

    interactive=True (portal): só payload local — anexos Pipe vão em GET /attachments.
    """
    include_attachments = not interactive
    payload = normalize_hub_payload(payload)
    try:
        parsed = parse_form_payload_v1(payload)
    except Exception:
        parsed = FormPayloadV1.model_construct()

    errors = validate_form_payload_v1(deal_id, payload, interactive=interactive)
    attachments: dict[str, Any] | None = None
    if include_attachments:
        attachments = inspect_deal_attachments(deal_id, fresh=True)

    deal = form_payload_to_deal_dict(deal_id, parsed)
    proposta_pipe = (
        attachments.get("proposta_comercial_anexada") is True if attachments else False
    )

    sections_out: list[dict[str, Any]] = []
    total_items = 0
    ok_items = 0

    for section_id, section_label, paths in READINESS_SECTIONS:
        if section_id == "hub":
            paths = _hub_section_paths(parsed)
        if interactive and section_id == "anexos":
            continue
        items: list[dict[str, Any]] = []
        for path in paths:
            if path != "_servicos_uc" and path != "anexos.proposta_comercial_anexada":
                if _skip_path(deal, path, parsed):
                    continue

            label = FIELD_LABELS.get(path, path)
            message = errors.get(path)

            if path == "_servicos_uc":
                servico_err = errors.get("servicos.sole_web")
                status: ItemStatus = "ok" if not servico_err else ("error" if servico_err else "pending")
                filled = status == "ok"
                if servico_err:
                    message = servico_err
            elif path == "_hub_uc_matrix":
                hub_err = errors.get("hub.observacoes_detalhes")
                filled = any(
                    _instalacao_ativa(inst)
                    for inst in (parsed.hub.instalacoes or [])
                )
                if hub_err:
                    status = "error"
                    message = hub_err
                elif filled:
                    status = "ok"
                else:
                    status = "pending"
            elif path == "anexos.proposta_comercial_anexada":
                filled = proposta_pipe or _path_filled(parsed, path)
                if message and proposta_pipe:
                    message = None
                if proposta_pipe or filled:
                    status = "ok"
                elif message:
                    status = "error"
                else:
                    status = "pending"
            else:
                filled = _path_filled(parsed, path)
                if message:
                    status = "error"
                elif filled:
                    status = "ok"
                else:
                    status = "pending"

            total_items += 1
            if status == "ok":
                ok_items += 1

            items.append(
                {
                    "id": path,
                    "label": label,
                    "status": status,
                    "message": message,
                }
            )

        section_ok = sum(1 for i in items if i["status"] == "ok")
        sections_out.append(
            {
                "id": section_id,
                "label": section_label,
                "completed": section_ok,
                "total": len(items),
                "ready": section_ok == len(items) and len(items) > 0,
                "items": items,
            }
        )

    tpl = (attachments or {}).get("contrato_template") or {}
    tpl_source = tpl.get("source") or "padrao"
    contrato_info: dict[str, Any] | None = None
    attachments_out: dict[str, Any] | None = None
    if include_attachments:
        contrato_info = {
            "source": tpl_source,
            "filename": tpl.get("filename"),
            "label": (
                f"Contrato a partir do arquivo enviado ({tpl.get('filename')})"
                if tpl_source == "custom" and tpl.get("filename")
                else "Contrato a partir do modelo padrão Gebras"
            ),
        }
        attachments_out = {
            "proposta_comercial_anexada": proposta_pipe,
            "error": attachments.get("attachments_error") if attachments else None,
        }

    percent = round((ok_items / total_items) * 100) if total_items else 0

    effective_errors = dict(errors)
    if proposta_pipe:
        effective_errors.pop("anexos.proposta_comercial_anexada", None)

    out: dict[str, Any] = {
        "deal_id": deal_id,
        "ready_to_submit": len(effective_errors) == 0,
        "summary": {
            "completed": ok_items,
            "total": total_items,
            "percent": percent,
            "validation_error_count": len(errors),
        },
        "sections": sections_out,
        "validation_errors": errors,
    }
    if interactive:
        out["attachments_deferred"] = True
    if contrato_info is not None:
        out["contrato"] = contrato_info
    if attachments_out is not None:
        out["attachments"] = attachments_out
    return out
