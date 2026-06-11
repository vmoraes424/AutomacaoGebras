"""Validação de domínio do formulário web v1 — reutiliza regras do worker."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .config import PLUNE_CENTRO_CUSTO_ID
from .form_schema_v1 import (
    PIPE_TO_FORM_PATH,
    FormPayloadV1,
    form_payload_to_deal_dict,
    parse_form_payload_v1,
)
from .form_uc_hub import normalize_hub_payload
from .hub_pedido import erros_validacao_observacoes_hub
from .pipedrive_fields import (
    CAMPOS_CONTRATO_OBRIGATORIOS,
    CAMPOS_CONTRATO_OPCIONAIS,
    CAMPOS_SERVICO_UC,
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_FILIAL,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
    get_enum_label,
    get_val,
    settings_por_branch,
)
from .pipedrive_validations import (
    _decimal_pipe,
    _implantacao_exige_data_pagamento,
    _validar_campo_contrato,
    _validar_mapeamento_plune,
)
from .plune_catalog import resolver_subcentro, sincronizar_subcentros_de_pedidos


def _pydantic_errors(exc: ValidationError) -> dict[str, str]:
    out: dict[str, str] = {}
    for err in exc.errors():
        loc = err.get("loc") or ()
        path = ".".join(str(part) for part in loc if part != "payload")
        if not path:
            path = "_form"
        out[path] = err.get("msg", "valor inválido")
    return out


def _hub_error_path(message: str) -> str:
    lower = message.lower()
    if "observações (detalhes)" in lower or "observacoes (detalhes)" in lower:
        return "servicos.sole_web"
    if "código cliente" in lower or "codigo cliente" in lower:
        return "cliente.codigo_cliente_instalacao"
    if "instalação" in lower or "instalacao" in lower:
        return "servicos.sole_web"
    return "hub.observacoes_detalhes"


def _plune_error_path(message: str) -> str:
    lower = message.lower()
    if "filial" in lower:
        return "comercial.filial"
    if "regional" in lower or "nível 2" in lower or "nivel 2" in lower:
        return "comercial.regional"
    if "nível 3" in lower or "nivel 3" in lower or "consultor" in lower:
        return "comercial.consultor"
    if "plune_centro" in lower or "centro_custo" in lower:
        return "_config"
    return "comercial.filial"


def _validar_servicos_uc(deal: dict) -> str | None:
    if any(
        _decimal_pipe(get_val(deal, campo)) and _decimal_pipe(get_val(deal, campo)) > 0
        for campo in CAMPOS_SERVICO_UC
    ):
        return None
    return (
        "Pelo menos um serviço (UC) deve ter quantidade maior que zero "
        "(SOLE Web, Sole Consultoria, Gestão ACL, Usina ou Gestão da Qualidade de Energia)."
    )


def _validar_plune(deal: dict, errors: dict[str, str], *, interactive: bool = False) -> str:
    plune_msgs: list[str] = []
    branch_id = _validar_mapeamento_plune(deal, plune_msgs)
    for msg in plune_msgs:
        errors[_plune_error_path(msg)] = msg

    if branch_id:
        branch_cfg = settings_por_branch(branch_id)
        if not branch_cfg.get("subcentro_custo_id"):
            msg = (
                f"Configuração Plune ausente para filial BranchId={branch_id}: "
                "subcentro_custo_id (Sub Centro = Gestão de Energia)."
            )
            errors["comercial.filial"] = msg

    if not PLUNE_CENTRO_CUSTO_ID:
        errors["_config"] = (
            "Configuração Plune ausente: PLUNE_CENTRO_CUSTO_ID "
            "(Centro = Contratos Comerciais)."
        )

    regional = get_enum_label(deal, FIELD_REGIONAL).strip()
    branch_settings = settings_por_branch(branch_id) if branch_id else {}
    if regional and branch_id:
        sub2_id = resolver_subcentro(
            branch_id, 2, regional, sync_if_missing=not interactive
        )
        if not sub2_id and not interactive:
            sincronizar_subcentros_de_pedidos(force=True)
            sub2_id = resolver_subcentro(branch_id, 2, regional, sync_if_missing=False)
        if not sub2_id:
            regional_map = branch_settings.get("regional_map", {})
            disponiveis = ", ".join(sorted(regional_map)) or "nenhum (rode sync Plune)"
            errors["comercial.regional"] = (
                "Sub Centro Nível 2 sem mapeamento para SubCentroCusto2Id no Plune. "
                f"Valor recebido: {regional!r}. O catálogo é atualizado via API; "
                f"valores conhecidos na filial: {disponiveis}."
            )

    subcentro3 = get_enum_label(deal, FIELD_SUBCENTRO_NIVEL_3).strip()
    if subcentro3 and branch_id:
        sub3_id = resolver_subcentro(
            branch_id, 3, subcentro3, sync_if_missing=not interactive
        )
        if not sub3_id and not interactive:
            sincronizar_subcentros_de_pedidos(force=True)
            sub3_id = resolver_subcentro(branch_id, 3, subcentro3, sync_if_missing=False)
        if not sub3_id:
            subcentro3_map = branch_settings.get("subcentro3_map", {})
            disponiveis = ", ".join(sorted(subcentro3_map)) or "nenhum (rode sync Plune)"
            errors["comercial.consultor"] = (
                "Sub Centro Nível 3 sem mapeamento para SubCentroCusto3Id no Plune. "
                f"Valor recebido: {subcentro3!r}. O catálogo é atualizado via API; "
                f"valores conhecidos na filial: {disponiveis}."
            )

    return branch_id


def _validar_anexo_proposta(payload: FormPayloadV1, errors: dict[str, str]) -> None:
    if not payload.anexos.proposta_comercial_anexada:
        errors["anexos.proposta_comercial_anexada"] = (
            "Anexo obrigatório ausente: Proposta Comercial. "
            "Confirme que a proposta está anexada no deal do Pipedrive "
            "ou marque como anexada no formulário."
        )


def validate_form_payload_v1(
    deal_id: int,
    payload: dict[str, Any],
    *,
    interactive: bool = False,
) -> dict[str, str]:
    """
    Valida payload do formulário v1.

    Retorna dict vazio se OK; chaves em notação de ponto (ex.: cliente.cep).

    interactive=True (prontidão no portal): só consulta catálogo Plune em cache local,
    sem sync forçado na API Plune a cada keystroke.
    """
    errors: dict[str, str] = {}

    payload = normalize_hub_payload(payload)

    try:
        parsed = parse_form_payload_v1(payload)
    except ValidationError as exc:
        errors.update(_pydantic_errors(exc))
        try:
            parsed = FormPayloadV1.model_construct()
        except Exception:
            return errors

    deal = form_payload_to_deal_dict(deal_id, parsed)

    for label, field_code, tipo in CAMPOS_CONTRATO_OBRIGATORIOS:
        if field_code == FIELD_FILIAL or field_code in CAMPOS_CONTRATO_OPCIONAIS:
            continue
        if (
            field_code == FIELD_DATA_PAGAMENTO_IMPLANTACAO
            and not _implantacao_exige_data_pagamento(deal)
        ):
            continue
        msg = _validar_campo_contrato(deal, label, field_code, tipo)
        if msg:
            form_path = PIPE_TO_FORM_PATH.get(field_code, field_code)
            errors.setdefault(form_path, msg)

    servico_msg = _validar_servicos_uc(deal)
    if servico_msg:
        errors.setdefault("servicos.sole_web", servico_msg)

    if not interactive:
        _validar_plune(deal, errors, interactive=False)

    for msg in erros_validacao_observacoes_hub(deal):
        errors.setdefault(_hub_error_path(msg), msg)

    if not interactive:
        _validar_anexo_proposta(parsed, errors)

    return errors
