import re

import requests

from .config import PIPEDRIVE_API_TOKEN, PLUNE_CENTRO_CUSTO_ID
from .database import default_branch_id, filial_tem_mapeamento
from .pipedrive_fields import (
    CAMPOS_CONTRATO_OBRIGATORIOS,
    CAMPOS_CONTRATO_OPCIONAIS,
    CAMPOS_SERVICO_UC,
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_DOCUMENTO,
    FIELD_FILIAL,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
    FIELD_VALOR_IMPLANTACAO,
    get_enum_label,
    get_filial_chaves,
    get_filial_label,
    get_val,
    normalizar_cep,
    resolver_branch_id,
    settings_por_branch,
)
from .hub_pedido import erros_validacao_observacoes_hub
from .pipedrive_files import listar_arquivos_deal, tem_arquivo_proposta_comercial
from .plune_catalog import resolver_subcentro, sincronizar_subcentros_de_pedidos


class DealValidationError(RuntimeError):
    def __init__(self, deal_id: str, mensagens: list[str]):
        self.deal_id = str(deal_id)
        self.mensagens = mensagens
        super().__init__("; ".join(mensagens))


def _decimal_pipe(valor) -> float | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    normalizado = texto.replace("R$", "").replace(" ", "")
    if "," in normalizado and "." in normalizado:
        if normalizado.rfind(",") > normalizado.rfind("."):
            normalizado = normalizado.replace(".", "").replace(",", ".")
        else:
            normalizado = normalizado.replace(",", "")
    elif "," in normalizado:
        normalizado = normalizado.replace(".", "").replace(",", ".")
    try:
        return float(normalizado)
    except ValueError:
        return None


def _valor_numero_maior_que_um(valor) -> bool:
    numero = _decimal_pipe(valor)
    return numero is not None and numero > 1


def _implantacao_exige_data_pagamento(deal: dict) -> bool:
    """Mesmo critério do pedido Plune implantação: só com valor > 1."""
    return _valor_numero_maior_que_um(get_val(deal, FIELD_VALOR_IMPLANTACAO))


def _documento_valido(valor: str) -> bool:
    digits = re.sub(r"\D", "", valor or "")
    return len(digits) in (11, 14)


def _email_valido(valor: str) -> bool:
    texto = (valor or "").strip()
    return bool(texto) and "@" in texto and "." in texto.split("@")[-1]


def _campo_presente_no_deal(deal: dict, field_code: str) -> bool:
    cf = deal.get("custom_fields") or {}
    if field_code in cf:
        raw = cf[field_code]
        return raw is not None and raw != ""
    return field_code in deal and deal[field_code] not in (None, "")


def _validar_campo_contrato(deal: dict, label: str, field_code: str, tipo: str) -> str | None:
    if tipo == "enum":
        valor = get_enum_label(deal, field_code).strip()
        if not valor:
            return (
                f"Campo obrigatório ausente: {label}. "
                f"Selecione uma opção na seção Contrato do deal."
            )
        return None

    if tipo == "documento":
        valor = get_val(deal, field_code).strip()
        if not _documento_valido(valor):
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe CPF (11 dígitos) ou CNPJ (14 dígitos). Valor recebido: {valor!r}."
            )
        return None

    if tipo == "cep":
        valor = get_val(deal, field_code)
        cep = normalizar_cep(valor)
        if len(cep) != 8:
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe CEP com 8 dígitos. Valor recebido: {valor!r}."
            )
        return None

    if tipo == "email":
        valor = get_val(deal, field_code).strip()
        if not _email_valido(valor):
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe um e-mail válido. Valor recebido: {valor!r}."
            )
        return None

    if tipo == "uc":
        if not _campo_presente_no_deal(deal, field_code):
            return (
                f"Campo obrigatório ausente: {label}. "
                f"Informe a quantidade de UCs (use 0 se não contratar o serviço)."
            )
        if _decimal_pipe(get_val(deal, field_code)) is None:
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe um número. Valor recebido: {get_val(deal, field_code)!r}."
            )
        return None

    if tipo == "money_mensal":
        valor = get_val(deal, field_code)
        if not _valor_numero_maior_que_um(valor):
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe um valor maior que 1. Valor recebido: {valor!r}."
            )
        return None

    if tipo == "money_implantacao":
        if not _campo_presente_no_deal(deal, field_code):
            return (
                f"Campo obrigatório ausente: {label}. "
                f"Informe o valor (use 0 se não houver implantação)."
            )
        if _decimal_pipe(get_val(deal, field_code)) is None:
            return (
                f"Campo obrigatório inválido: {label}. "
                f"Informe um valor numérico (0 se não houver implantação). "
                f"Valor recebido: {get_val(deal, field_code)!r}."
            )
        return None

    if tipo == "date":
        valor = get_val(deal, field_code).strip()
        if not valor:
            return (
                f"Campo obrigatório ausente: {label}. "
                f"Informe a data na seção Contrato do deal."
            )
        return None

    # text e demais
    valor = get_val(deal, field_code).strip()
    if not valor:
        return (
            f"Campo obrigatório ausente: {label}. "
            f"Preencha o campo na seção Contrato do deal."
        )
    return None


def _validar_mapeamento_plune(deal: dict, erros: list[str]) -> str:
    """Retorna branch_id resolvido ou '' se já registrou erro."""
    label_filial, id_filial = get_filial_chaves(deal)
    if not label_filial and not id_filial:
        erros.append(
            "Campo obrigatório inválido: Filial. "
            "Selecione a filial no deal (Matriz ou Iribarrem San Martin)."
        )
        return ""
    if not filial_tem_mapeamento(label_filial, id_filial):
        erros.append(
            "Filial sem mapeamento para BranchId no Plune. "
            f"Valor no Pipedrive: {get_filial_label(deal) or id_filial!r}. "
            "Cadastre em pipedrive_filial (MySQL)."
        )
        return ""
    try:
        return resolver_branch_id(deal)
    except ValueError as exc:
        erros.append(str(exc))
        return ""


def validar_deal_para_automacao(deal: dict) -> None:
    deal_id = str(deal.get("id", ""))
    erros: list[str] = []

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
            erros.append(msg)

    branch_id = _validar_mapeamento_plune(deal, erros)
    if branch_id:
        branch_cfg = settings_por_branch(branch_id)
        if not branch_cfg["subcentro_custo_id"]:
            erros.append(
                f"Configuração Plune ausente para filial BranchId={branch_id}: "
                "subcentro_custo_id (Sub Centro = Gestão de Energia)."
            )

    if not PLUNE_CENTRO_CUSTO_ID:
        erros.append(
            "Configuração Plune ausente: PLUNE_CENTRO_CUSTO_ID (Centro = Contratos Comerciais)."
        )

    regional = get_enum_label(deal, FIELD_REGIONAL).strip()
    branch_settings = settings_por_branch(branch_id) if branch_id else {}
    if regional and branch_id:
        sub2_id = resolver_subcentro(branch_id, 2, regional)
        if not sub2_id:
            sincronizar_subcentros_de_pedidos(force=True)
            sub2_id = resolver_subcentro(branch_id, 2, regional, sync_if_missing=False)
        if not sub2_id:
            regional_map = branch_settings.get("regional_map", {})
            disponiveis = ", ".join(sorted(regional_map)) or "nenhum (rode sync Plune)"
            erros.append(
                "Sub Centro Nível 2 sem mapeamento para SubCentroCusto2Id no Plune. "
                f"Valor recebido: {regional!r}. O catálogo é atualizado via API; "
                f"valores conhecidos na filial: {disponiveis}."
            )

    subcentro3 = get_enum_label(deal, FIELD_SUBCENTRO_NIVEL_3).strip()
    if subcentro3 and branch_id:
        sub3_id = resolver_subcentro(branch_id, 3, subcentro3)
        if not sub3_id:
            sincronizar_subcentros_de_pedidos(force=True)
            sub3_id = resolver_subcentro(branch_id, 3, subcentro3, sync_if_missing=False)
        if not sub3_id:
            subcentro3_map = branch_settings.get("subcentro3_map", {})
            disponiveis = ", ".join(sorted(subcentro3_map)) or "nenhum (rode sync Plune)"
            erros.append(
                "Sub Centro Nível 3 sem mapeamento para SubCentroCusto3Id no Plune. "
                f"Valor recebido: {subcentro3!r}. O catálogo é atualizado via API; "
                f"valores conhecidos na filial: {disponiveis}."
            )

    if not any(_decimal_pipe(get_val(deal, campo)) and _decimal_pipe(get_val(deal, campo)) > 0 for campo in CAMPOS_SERVICO_UC):
        erros.append(
            "Pelo menos um serviço (UC) deve ter quantidade maior que zero "
            "(SOLE Web, Sole Consultoria, Gestão ACL, Usina ou Gestão da Qualidade de Energia)."
        )

    erros.extend(erros_validacao_observacoes_hub(deal))

    try:
        arquivos = listar_arquivos_deal(deal_id)
        if not tem_arquivo_proposta_comercial(arquivos):
            erros.append(
                "Anexo obrigatório ausente: Proposta Comercial. "
                "Anexe um arquivo cujo nome contenha «Proposta Comercial» no deal."
            )
    except RuntimeError as exc:
        erros.append(
            f"Não foi possível verificar anexos do deal (Proposta Comercial): {exc}"
        )

    if erros:
        raise DealValidationError(deal_id, erros)


def _pipedrive_headers() -> dict:
    return {"x-api-token": PIPEDRIVE_API_TOKEN}


def criar_nota_deal(deal_id: str, texto: str) -> None:
    payload = {"deal_id": int(deal_id), "content": texto}
    response = requests.post(
        "https://api.pipedrive.com/v1/notes",
        json=payload,
        headers=_pipedrive_headers(),
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive notes -> {response.status_code}: {response.text[:500]}"
        )


def reabrir_deal(deal_id: str) -> None:
    response = requests.put(
        f"https://api.pipedrive.com/v1/deals/{deal_id}",
        params={"api_token": PIPEDRIVE_API_TOKEN},
        json={"status": "open"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive reopen deal -> {response.status_code}: {response.text[:500]}"
        )
    data = response.json().get("data") or {}
    status = data.get("status")
    if status != "open":
        raise RuntimeError(
            f"Pipedrive reopen deal não confirmou status=open; status retornado={status!r}"
        )


def reabrir_deal_com_erros(deal_id: str, erros: list[str]) -> None:
    itens = "".join(f"<li>{erro}</li>" for erro in erros)
    nota = (
        "<p><strong>Automação Gebras:</strong> o card foi reaberto porque há "
        "campos obrigatórios inválidos ou ausentes na seção <strong>Contrato</strong> "
        "(exceto Observações), "
        "ou falta o anexo <strong>Proposta Comercial</strong>.</p>"
        f"<ul>{itens}</ul>"
        "<p>Corrija os campos e marque o card como ganho novamente.</p>"
    )
    criar_nota_deal(deal_id, nota)
    reabrir_deal(deal_id)
