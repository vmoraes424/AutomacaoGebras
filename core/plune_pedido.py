"""
Card assinado → dados Pipedrive → pedido no Plune.

Um único módulo: cliente Plune, mapeamento de campos e criação do pedido.
"""

from urllib.parse import urlencode

import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .config import (
    ARQUIVO_AVISOS_APROVACAO_PLUNE,
    DEV_PLUNE_APROVADO_NAO,
    DEV_PULAR_CLICKSIGN,
    TESTE_PLUNE_SEM_ASSINATURA,
    PLUNE_AUTH_TOKEN,
    PLUNE_BASE_URL,
    PLUNE_BRANCH_ID,
    PLUNE_COMISSAO_MESES_ANUAL,
    PLUNE_CENTRO_CUSTO_ID,
    PLUNE_COMPANY_ID,
    PLUNE_FRETE_POR_CONTA,
    PLUNE_PARCEIRO_TIPO,
    PLUNE_PEDIDO_MODELO_ID,
    PLUNE_PEDIDO_SERIE,
    PLUNE_PRODUTO_SOLE_ID,
    PLUNE_STATUS_PEDIDO,
    PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID,
    PLUNE_STATUS_PEDIDO_RECORRENTE_ID,
    PLUNE_TIPO_CONTRATO_IMPLANTACAO_ID,
    PLUNE_TIPO_CONTRATO_MERCADO_LIVRE_RECORRENTE_ID,
    PLUNE_TIPO_CONTRATO_QUALIDADE_RECORRENTE_ID,
    PLUNE_TIPO_CONTRATO_SOLE_RECORRENTE_ID,
    PLUNE_TIPO_CONTRATO_USINA_RECORRENTE_ID,
    PLUNE_TIPO_OP_ID,
)
from .envelope_state import (
    carregar_pedidos_plune_criados,
    marcar_pedido_criado,
    salvar_pedido_plune_criado,
)
from .pedido_anexos import (
    CacheAnexosDeal,
    anexar_contrato_pedido,
    anexar_proposta_pedido,
)
from .pipedrive_fields import (
    FIELD_CEP,
    FIELD_CIDADE,
    FIELD_CONTATO_CONTRATANTE,
    FIELD_DATA_IMPLANTACAO,
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_ENDERECO,
    CAMPOS_SERVICO_UC,
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_PERCENTUAL_EXITO,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_QTD_SOLE,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
    resolver_branch_id,
    settings_por_branch,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
    buscar_deal_por_id,
    formatar_data_ptbr,
    formatar_decimal_plune,
    get_documento,
    get_nome_cliente,
    get_numero_contrato,
    get_enum_label,
    get_val,
    normalizar_cep,
    normalizar_documento,
    normalizar_nome,
)


from .plune_errors import PluneApiError, PluneError  # noqa: F401 — reexport


def _plune_aprovado_insert() -> str:
    """
    No ganho, pedido sempre nasce NÃO aprovado.
    Aprovação ocorre apenas após última assinatura (aprovar_pedidos_plune).
    """
    return "0"


# InsertPedidoBase (URLs.cs) — ordem na URL; Aprovado logo após CompanyId
def _insert_pedido_base_url() -> list[tuple[str, str]]:
    return [
        ("Venda.Pedido.CompanyId", PLUNE_COMPANY_ID),
        ("Venda.Pedido.Aprovado", _plune_aprovado_insert()),
        ("Venda.Pedido.Status", "5"),
        ("Venda.Pedido.StatusPedido", PLUNE_STATUS_PEDIDO),
        ("Venda.Pedido.ModeloId", "01"),
        ("Venda.Pedido.NaturezaOperacaoServicoId", "2"),
        ("Venda.Pedido.Serie", PLUNE_PEDIDO_SERIE),
        ("Venda.Pedido.CentroCustoId", PLUNE_CENTRO_CUSTO_ID),
        ("Venda.Pedido.ParcelamentoAutomatico", "1"),
        ("Venda.Pedido.ComissaoManual", "1"),
    ]


_INSERT_BASE_KEYS = {
    "CompanyId",
    "Aprovado",
    "Status",
    "StatusPedido",
    "ModeloId",
    "Serie",
    "NaturezaOperacaoServicoId",
    "TipoContratoId",
    "CentroCustoId",
    "ParcelamentoAutomatico",
    "ComissaoManual",
    "BaseComissao",
    "PercentualComissao",
    "ValorComissao",
}

# Defaults internos (montagem do cabeçalho)
_PEDIDO_DEFAULTS = {
    "CompanyId": PLUNE_COMPANY_ID,
    "Aprovado": "0",
    "Status": "5",
    "StatusPedido": PLUNE_STATUS_PEDIDO,
    "ModeloId": "01",
    "Serie": PLUNE_PEDIDO_SERIE,
    "NaturezaOperacaoServicoId": "2",
    "CentroCustoId": PLUNE_CENTRO_CUSTO_ID,
    "ParcelamentoAutomatico": "1",
    "ComissaoManual": "1",
    "BranchId": PLUNE_BRANCH_ID,
    "TipoOpId": PLUNE_TIPO_OP_ID,
    "FreteporConta": PLUNE_FRETE_POR_CONTA,
}

TIPO_PEDIDO_IMPLANTACAO = "implantacao"
TIPO_PEDIDO_RECORRENTE = "recorrente"

_TIPOS_PEDIDO_PLUNE = (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
)

_PEDIDO_TIPO_CONFIG = {
    TIPO_PEDIDO_IMPLANTACAO: {
        "label": "Implantação",
        "valor_field": FIELD_VALOR_IMPLANTACAO,
        "status_pedido": PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID,
    },
    TIPO_PEDIDO_RECORRENTE: {
        "label": "Recorrente",
        "valor_field": FIELD_VALOR_MENSAL,
        "status_pedido": PLUNE_STATUS_PEDIDO_RECORRENTE_ID,
    },
}


def _pedido_serie(branch_id: str) -> str:
    """0 = NFS-e, 1 = NFSe — por filial (branch_config no MySQL)."""
    cfg = settings_por_branch(branch_id)
    return str(cfg.get("pedido_serie") or PLUNE_PEDIDO_SERIE).strip() or PLUNE_PEDIDO_SERIE


def _pedido_modelo_id(branch_id: str) -> str:
    """Modelo fiscal — deve existir em Venda.NotaConfig para a série da filial."""
    cfg = settings_por_branch(branch_id)
    return (
        str(cfg.get("pedido_modelo_id") or PLUNE_PEDIDO_MODELO_ID).strip()
        or PLUNE_PEDIDO_MODELO_ID
    )


def _parametro_contabil_id(tipo_pedido: str, branch_id: str) -> str:
    cfg = settings_por_branch(branch_id)
    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
        return cfg["parametro_implantacao"]
    return cfg["parametro_recorrente"]


# (rótulo para erro, campo Pipedrive, Venda.TipoContrato.Id)
_TIPO_CONTRATO_RECORRENTE_POR_CAMPO: tuple[tuple[str, str, str], ...] = (
    (
        "Gestão Usina Fotovoltaica",
        FIELD_GESTAO_USINA_FOTOVOLTAICA,
        PLUNE_TIPO_CONTRATO_USINA_RECORRENTE_ID,
    ),
    (
        "Gestão da Qualidade de Energia",
        FIELD_INDICADORES_QUALIDADE,
        PLUNE_TIPO_CONTRATO_QUALIDADE_RECORRENTE_ID,
    ),
    (
        "Gestão ACL - Mercado Livre",
        FIELD_GESTAO_ACL,
        PLUNE_TIPO_CONTRATO_MERCADO_LIVRE_RECORRENTE_ID,
    ),
    ("SOLE Web", FIELD_QTD_SOLE, PLUNE_TIPO_CONTRATO_SOLE_RECORRENTE_ID),
    (
        "Sole Consultoria",
        FIELD_QUALIDADE_ENERGIA,
        PLUNE_TIPO_CONTRATO_SOLE_RECORRENTE_ID,
    ),
)


def _resolver_tipo_contrato_id(deal: dict, tipo_pedido: str) -> str:
    """
    Implantação: IMPLANTAÇÃO (id 1).
    Recorrente: tipo de contrato do serviço com maior quantidade de UCs no Pipedrive.
    Sem fallback: se não houver UC válida no recorrente, levanta PluneError.
    """
    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
        return PLUNE_TIPO_CONTRATO_IMPLANTACAO_ID

    deal_id = str(deal.get("id", ""))
    melhor_id: str | None = None
    melhor_qtd = -1.0
    for _rotulo, campo, tipo_id in _TIPO_CONTRATO_RECORRENTE_POR_CAMPO:
        qtd = _decimal_pipe(get_val(deal, campo))
        if qtd is None or qtd <= 0:
            continue
        if qtd > melhor_qtd:
            melhor_qtd = qtd
            melhor_id = tipo_id

    if not melhor_id:
        servicos = ", ".join(r for r, _, _ in _TIPO_CONTRATO_RECORRENTE_POR_CAMPO)
        raise PluneError(
            f"Deal {deal_id}: pedido recorrente exige ao menos um serviço com "
            f"quantidade de UCs > 0 no Pipedrive ({servicos}). "
            "Preencha os campos no deal antes de ganhar."
        )
    return melhor_id


def _resolver_branch_id(deal: dict) -> str:
    try:
        return resolver_branch_id(deal)
    except ValueError as exc:
        raise PluneError(str(exc)) from exc


def _urlencode_plune(params: list[tuple[str, str]]) -> str:
    """Query string no charset do Plune (ISO-8859-1). UTF-8 quebra acentos na UI."""
    return urlencode(params, doseq=True, encoding="iso-8859-1", errors="replace")


def _plune_get(
    class_id: str, method: str, params: dict | list[tuple[str, str]]
) -> dict:
    if not PLUNE_BASE_URL:
        raise PluneError("PLUNE_BASE_URL não configurado")
    if not PLUNE_AUTH_TOKEN:
        raise PluneError("PLUNE_AUTH_TOKEN não configurado")

    if isinstance(params, dict):
        query: list[tuple[str, str]] = list(params.items())
    else:
        query = list(params)
    query.append(("_AuthToken", PLUNE_AUTH_TOKEN))
    url = (
        f"{PLUNE_BASE_URL.rstrip('/')}/JSON/{class_id}/{method}?"
        f"{_urlencode_plune(query)}"
    )
    response = requests.get(url, timeout=120)
    if not response.ok:
        raise PluneError(f"Plune HTTP {response.status_code}: {response.text[:500]}")
    text = response.text.lstrip()
    if not text.startswith("{"):
        brace = text.find("{")
        if brace == -1:
            raise PluneError(f"Plune resposta inválida: {text[:500]}")
        text = text[brace:]
    payload = json.loads(text)
    error = payload.get("ErrorStatus") or payload.get("ErrorStatus2")
    if error:
        raise PluneApiError(f"Plune ErrorStatus: {error}", str(error))
    return payload


def _field_value(row: dict, field_name: str) -> str:
    item = row.get(field_name) or {}
    if isinstance(item, dict):
        return str(item.get("value", "") or "")
    return str(item or "")


def _field_resolved(row: dict, field_name: str) -> str:
    item = row.get(field_name) or {}
    if isinstance(item, dict):
        resolved = item.get("resolved")
        if resolved not in (None, ""):
            return str(resolved)
        return str(item.get("value", "") or "")
    return str(item or "")


_PARCEIRO_BROWSE_FIELDS = [
    "ParceiroId",
    "NumeroContribuinte",
    "NomRazaoSocial",
    "NomFantasia",
    "ECliente",
    "EFornecedor",
    "EnderecoPrincipal",
    "BairroPrincipal",
    "CidadePrincipalId",
    "CidadePrincipalEx",
    "UFPrincipalId",
    "CEPPrincipal",
    "ContatoNome",
    "EMail",
]


def _tipo_parceiro_flags() -> tuple[str, str]:
    tipo = (PLUNE_PARCEIRO_TIPO or "cliente").strip().lower()
    if tipo in ("fornecedor", "supplier"):
        return "0", "1"
    return "1", "0"


def _campo_tipo_parceiro_browse() -> str:
    e_cliente, e_fornecedor = _tipo_parceiro_flags()
    if e_fornecedor == "1" and e_cliente == "0":
        return "EFornecedor"
    return "ECliente"


def _row_para_parceiro(row: dict) -> dict:
    cidade = _field_resolved(row, "CidadePrincipalId") or _field_value(
        row, "CidadePrincipalEx"
    )
    doc_raw = _field_value(row, "NumeroContribuinte")
    doc_fmt = _field_resolved(row, "NumeroContribuinte") or doc_raw
    return {
        "id": _field_value(row, "ParceiroId"),
        "documento": normalizar_documento(doc_raw),
        "documento_formatado": doc_fmt.strip(),
        "razao_social": _field_value(row, "NomRazaoSocial").strip(),
        "nome_fantasia": _field_value(row, "NomFantasia").strip(),
        "e_cliente": _field_value(row, "ECliente"),
        "e_fornecedor": _field_value(row, "EFornecedor"),
        "endereco": _field_value(row, "EnderecoPrincipal").strip(),
        "bairro": _field_value(row, "BairroPrincipal").strip(),
        "cidade": cidade.strip(),
        "uf": _field_value(row, "UFPrincipalId").strip(),
        "cep": _field_value(row, "CEPPrincipal").strip(),
        "email": _field_value(row, "EMail").strip(),
        "contato": _field_value(row, "ContatoNome").strip(),
    }


def _buscar_parceiro_por_id(parceiro_id: str) -> dict:
    prefix = "Parceiro.tbParceiro."
    params = {
        f"{prefix}EmpresaId": PLUNE_COMPANY_ID,
        f"{prefix}ParceiroId": str(parceiro_id),
    }
    payload = _plune_get("Parceiro.tbParceiro", "Select", params)
    field = payload.get("Field") or {}
    return _row_para_parceiro(field)


def _buscar_parceiros_por_documento(documento: str) -> list[dict]:
    """Browse por CNPJ/CPF — UrlClientes.md."""
    doc_digits = normalizar_documento(documento)
    if not doc_digits:
        return []

    prefix = "Parceiro.tbParceiro."
    params = {
        f"{prefix}Ativo": "1",
        f"{prefix}NumeroContribuinte": doc_digits,
        f"{prefix}{_campo_tipo_parceiro_browse()}": "1",
        "_Parceiro.tbParceiro.BrowseSequence": _PARCEIRO_BROWSE_FIELDS,
        "_Parceiro.tbParceiro.BrowseLimit": "30",
    }
    payload = _plune_get("Parceiro.tbParceiro", "Browse", params)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]

    return [_row_para_parceiro(row) for row in rows]


def _escolher_parceiro_por_documento(
    candidatos: list[dict], documento: str, razao_social_pipe: str = ""
) -> dict | None:
    if not candidatos:
        return None

    doc_digits = normalizar_documento(documento)
    por_doc = [
        c for c in candidatos if c.get("documento") == doc_digits
    ] or candidatos

    if len(por_doc) == 1:
        return por_doc[0]

    nome_alvo = normalizar_nome(razao_social_pipe)
    if nome_alvo:
        por_nome = [
            c for c in por_doc if normalizar_nome(c.get("razao_social", "")) == nome_alvo
        ]
        if len(por_nome) == 1:
            return por_nome[0]
        if len(por_nome) > 1:
            raise PluneError(
                f"Múltiplos parceiros no Plune para {documento}: {por_nome}"
            )

    raise PluneError(
        f"Múltiplos parceiros ativos para {documento}; confira o cadastro no Plune."
    )


def _montar_params_parceiro(deal: dict) -> dict:
    nome = get_nome_cliente(deal).strip()
    documento = normalizar_documento(get_documento(deal))
    endereco = get_val(deal, FIELD_ENDERECO).strip()
    cidade = get_val(deal, FIELD_CIDADE).strip()
    cep = normalizar_cep(get_val(deal, FIELD_CEP))
    contato = get_val(deal, FIELD_CONTATO_CONTRATANTE).strip()

    if not nome:
        raise PluneError("Deal sem razão social/nome do cliente no Pipedrive")
    if not documento:
        raise PluneError("Deal sem CPF/CNPJ no Pipedrive")
    if len(cep) != 8:
        raise PluneError(
            "Deal sem CEP válido no Pipedrive (obrigatório para criar parceiro no Plune; 8 dígitos)"
        )

    e_cliente, e_fornecedor = _tipo_parceiro_flags()
    params = {
        "EmpresaId": PLUNE_COMPANY_ID,
        "NomFantasia": nome[:60],
        "NomRazaoSocial": nome[:60],
        "Ativo": "1",
        "EmProspeccao": "0",
        "EmAprovacao": "0",
        "ECliente": e_cliente,
        "EFornecedor": e_fornecedor,
        "ERepresentante": "0",
        "Transportadora": "0",
        "NumeroContribuinte": documento,
        "RecebeEmala": "0",
        "RecebeMalaCorreio": "0",
        "AcessoWeb": "0",
        "NumeroFiliais": "1",
        "VerificacaoFilial": "0",
        "ConsumidorFinal": "1",
        "ISSQNSubstituicaoTributaria": "0",
        "RegimeTributario": "1",
        "Obs": f"Criado automaticamente via Pipedrive deal {deal.get('id', '')}",
    }
    params["CEPPrincipal"] = cep
    if endereco:
        params["EnderecoPrincipal"] = endereco[:128]
    if cidade:
        params["CidadePrincipalEx"] = cidade[:60]
    if contato:
        params["ContatoNome"] = contato[:100]
    return params


def _criar_parceiro(deal: dict) -> dict:
    params = _montar_params_parceiro(deal)
    prefixed = {
        f"Parceiro.tbParceiro.{key}": value
        for key, value in params.items()
        if value not in (None, "")
    }
    payload = _plune_get("Parceiro.tbParceiro", "Insert", prefixed)
    field = payload.get("Field") or {}
    parceiro_id = _field_value(field, "ParceiroId")
    if not parceiro_id:
        raise PluneError(f"Parceiro criado, mas retorno sem ParceiroId: {payload}")
    return _buscar_parceiro_por_id(parceiro_id)


def buscar_parceiro_plune_por_documento(
    documento: str, razao_social_pipe: str = ""
) -> dict | None:
    """Localiza parceiro ativo no Plune pelo CNPJ/CPF (sem criar)."""
    if not documento:
        return None
    candidatos = _buscar_parceiros_por_documento(documento)
    parceiro = _escolher_parceiro_por_documento(
        candidatos, documento, razao_social_pipe
    )
    if not parceiro:
        return None
    return _buscar_parceiro_por_id(parceiro["id"])


def _resolver_ou_criar_parceiro(deal: dict) -> tuple[dict, bool]:
    """
    CNPJ do Pipedrive só serve para localizar o parceiro no Plune.
    Retorna (dados_parceiro, criado_agora).
    CEP no Pipedrive só é obrigatório quando o parceiro ainda não existe no Plune.
    """
    documento = get_documento(deal)
    if not documento:
        raise PluneError("Deal sem CPF/CNPJ no Pipedrive")

    candidatos = _buscar_parceiros_por_documento(documento)
    parceiro = _escolher_parceiro_por_documento(
        candidatos, documento, get_nome_cliente(deal)
    )
    if parceiro:
        return _buscar_parceiro_por_id(parceiro["id"]), False

    cep = normalizar_cep(get_val(deal, FIELD_CEP))
    if len(cep) != 8:
        from .pipedrive_validations import DealValidationError

        deal_id = str(deal.get("id", ""))
        cep_pipe = get_val(deal, FIELD_CEP)
        raise DealValidationError(
            deal_id,
            [
                "Parceiro não encontrado no Plune para este CNPJ/CPF — será necessário "
                "criar um cadastro novo. Para isso, preencha o campo CEP no Pipedrive "
                f"(8 dígitos, ex.: 01310100 ou 01310-100). Valor atual: {cep_pipe!r}."
            ],
        )

    return _criar_parceiro(deal), True


def _aplicar_dados_cliente_pedido(
    params: dict, parceiro: dict, deal: dict | None = None
) -> None:
    """Preenche cabeçalho do pedido com dados do cadastro Plune."""
    if parceiro.get("razao_social"):
        params["ClienteNome"] = parceiro["razao_social"][:60]
    if parceiro.get("documento"):
        params["ClienteNumero"] = parceiro["documento"]
    if parceiro.get("endereco"):
        params["ClienteEndereco"] = parceiro["endereco"][:128]
    if parceiro.get("bairro"):
        params["ClienteBairro"] = parceiro["bairro"][:72]
    if parceiro.get("cidade"):
        params["ClienteCityName"] = parceiro["cidade"][:60]
    if parceiro.get("uf"):
        params["ClienteStateId"] = parceiro["uf"][:2]
    cep = normalizar_cep(parceiro.get("cep", ""))
    if not cep and deal is not None:
        cep = normalizar_cep(get_val(deal, FIELD_CEP))
    if cep:
        params["ClienteCep"] = cep[:8]


def _valor_ativo(valor: str) -> bool:
    texto = str(valor or "").strip().lower()
    return texto not in (
        "",
        "0",
        "0.0",
        "0,0",
        "0,00",
        "false",
        "nao",
        "não",
        "none",
        "null",
    )


def _decimal_pipe(valor) -> float | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    # Aceita formatos comuns do Pipedrive/BR: 3000, 3000.50, 3.000,50, 3,000.50.
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


def _valor_implantacao_valido_para_pedido(valor) -> bool:
    numero = _decimal_pipe(valor)
    return numero is not None and numero > 1


def _quantidade_observacao(valor) -> str:
    """Quantidade de UCs do Pipedrive para x1_ObservacaoAnexo (não flag 0/1)."""
    numero = _decimal_pipe(valor)
    if numero is None:
        return "0"
    if numero == int(numero):
        return str(int(numero))
    return _formatar_decimal_plune_numero(numero)


def _formatar_moeda_observacao(valor: str) -> str:
    valor_formatado = formatar_decimal_plune(valor)
    if valor_formatado:
        return f"R$ {valor_formatado}"
    return str(valor or "").strip()


def _pedido_integracao_tipo(deal_id: str, tipo_pedido: str) -> str:
    return f"{deal_id}-{tipo_pedido}"


def extrair_numeros_pedidos_plune(result: dict) -> dict[str, str]:
    """Extrai Id (número) dos pedidos implantação/recorrente do retorno de criar_pedido_plune."""
    numeros: dict[str, str] = {}
    for pedido in result.get("pedidos") or []:
        tipo = pedido.get("tipo")
        if tipo not in _TIPOS_PEDIDO_PLUNE:
            continue
        pedido_id = pedido.get("pedido_id")
        if pedido_id not in (None, ""):
            numeros[str(tipo)] = str(pedido_id).strip()
    return numeros


def obter_numeros_pedidos_plune_deal(deal_id: str) -> dict[str, str]:
    """Busca números de pedidos já existentes no Plune (reprocessamento / fill manual)."""
    deal_id = str(deal_id).strip()
    numeros: dict[str, str] = {}
    for tipo_pedido in _TIPOS_PEDIDO_PLUNE:
        chave = _pedido_integracao_tipo(deal_id, tipo_pedido)
        pedido_id = _buscar_pedido_id_por_pedido_integracao(chave)
        if pedido_id:
            numeros[tipo_pedido] = pedido_id
    return numeros


def formatar_linha_pedidos_plune_contrato(numeros: dict[str, str]) -> str:
    partes: list[str] = []
    if numeros.get(TIPO_PEDIDO_IMPLANTACAO):
        partes.append(f"Implantação: {numeros[TIPO_PEDIDO_IMPLANTACAO]}")
    if numeros.get(TIPO_PEDIDO_RECORRENTE):
        partes.append(f"Recorrente: {numeros[TIPO_PEDIDO_RECORRENTE]}")
    return " | ".join(partes) if partes else "—"


def _atualizar_campos_pedido_plune(
    pedido_id: str, cliente_id: str, campos: dict[str, str]
) -> None:
    """Update parcial (ex.: PedidoOriginal em Detalhes | Outros)."""
    if not campos:
        return
    params: list[tuple[str, str]] = [
        ("Venda.Pedido.CompanyId", PLUNE_COMPANY_ID),
        ("Venda.Pedido.ClienteId", str(cliente_id)),
        ("Venda.Pedido.Id", str(pedido_id)),
    ]
    for key, value in campos.items():
        if value not in (None, ""):
            params.append((f"Venda.Pedido.{key}", str(value)))
    _plune_get("Venda.Pedido", "Update", params)


def _buscar_observacao_pedido_plune(pedido_id: str, cliente_id: str) -> str:
    """Lê Observacao atual do pedido para poder complementar sem sobrescrever."""
    prefix = "Venda.Pedido."
    params = {
        f"{prefix}CompanyId": PLUNE_COMPANY_ID,
        f"{prefix}ClienteId": str(cliente_id),
        f"{prefix}Id": str(pedido_id),
        "_Venda.Pedido.BrowseSequence": ["Id", "Observacao"],
        "_Venda.Pedido.BrowseLimit": "2",
    }
    payload = _plune_get("Venda.Pedido", "Browse", params)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]
    if not rows:
        return ""
    return _field_value(rows[0], "Observacao").strip()


def _montar_bloco_pedidos_vinculados(*, id_impl: str, id_rec: str) -> str:
    return "\n".join(
        [
            "PEDIDOS VINCULADOS:",
            f"Implantação: {id_impl}",
            f"Recorrente: {id_rec}",
        ]
    )


def _atualizar_observacao_com_pedidos_vinculados(
    pedido_id: str, cliente_id: str, *, id_impl: str, id_rec: str
) -> None:
    atual = _buscar_observacao_pedido_plune(pedido_id, cliente_id)
    bloco = _montar_bloco_pedidos_vinculados(id_impl=id_impl, id_rec=id_rec)
    if bloco in atual:
        return
    novo = f"{atual}\n\n{bloco}".strip() if atual else bloco
    _atualizar_campos_pedido_plune(pedido_id, cliente_id, {"Observacao": novo})


def vincular_pedidos_plune_implantacao_recorrente(
    resultados: list[dict], *, cliente_id: str
) -> dict[str, str]:
    """
    Preenche Detalhes | Outros | Pedido Original (PedidoOriginal) nos dois sentidos:
    implantação aponta para o nº do recorrente e vice-versa.
    """
    numeros = extrair_numeros_pedidos_plune({"pedidos": resultados})
    id_impl = numeros.get(TIPO_PEDIDO_IMPLANTACAO)
    id_rec = numeros.get(TIPO_PEDIDO_RECORRENTE)
    if not id_impl or not id_rec:
        return numeros

    cliente_id = str(cliente_id).strip()
    _atualizar_campos_pedido_plune(
        id_impl, cliente_id, {"PedidoOriginal": id_rec}
    )
    _atualizar_campos_pedido_plune(
        id_rec, cliente_id, {"PedidoOriginal": id_impl}
    )
    _atualizar_observacao_com_pedidos_vinculados(
        id_impl, cliente_id, id_impl=id_impl, id_rec=id_rec
    )
    _atualizar_observacao_com_pedidos_vinculados(
        id_rec, cliente_id, id_impl=id_impl, id_rec=id_rec
    )
    print(
        f"[*] Pedidos Plune vinculados: implantação {id_impl} ↔ recorrente {id_rec} "
        "(PedidoOriginal)"
    )
    return numeros


def anexar_contrato_local_aos_pedidos_deal(deal_id: str) -> None:
    """Anexa o .docx local aos pedidos após fill_contract (dev / teste sem assinatura)."""
    from .config import DEV_PULAR_CLICKSIGN, TESTE_PLUNE_SEM_ASSINATURA

    if not (TESTE_PLUNE_SEM_ASSINATURA or DEV_PULAR_CLICKSIGN):
        return
    deal_id = str(deal_id).strip()
    cache = CacheAnexosDeal(deal_id, permitir_docx_local=True)
    for tipo_pedido in _TIPOS_PEDIDO_PLUNE:
        chave = _pedido_integracao_tipo(deal_id, tipo_pedido)
        pedido = _buscar_pedido_por_pedido_integracao(chave)
        if not pedido or not pedido.get("id") or not pedido.get("branch_id"):
            continue
        anexar_contrato_pedido(
            deal_id,
            pedido["id"],
            pedido["branch_id"],
            permitir_docx_local=True,
            cache=cache,
        )


def _preco_item_pedido(valor: str) -> str:
    valor_formatado = formatar_decimal_plune(valor)
    return valor_formatado or "0,00"


def _formatar_decimal_plune_numero(valor: float) -> str:
    formatted = f"{valor:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _somar_ucs_pipedrive(deal: dict) -> float:
    return sum(
        (_decimal_pipe(get_val(deal, campo)) or 0.0) for campo in CAMPOS_SERVICO_UC
    )


def _formatar_percentual_comissao_ucs(ucs: float) -> str:
    """Percentual recorrente = somatório das UCs (inteiro sem ,00 quando couber)."""
    if ucs == int(ucs):
        return str(int(ucs))
    return _formatar_decimal_plune_numero(ucs)


def _montar_campos_comissao(
    deal: dict, tipo_pedido: str, valor_pedido: str
) -> dict[str, str]:
    """
    Implantação: BaseComissao = valor do pedido; ValorComissao = valor do pedido;
    PercentualComissao = 0,001.
    Recorrente: BaseComissao = valor do pedido (mensalidade);
    ValorComissao = 12 × valor do pedido; PercentualComissao = somatório das UCs.
    """
    deal_id = str(deal.get("id", ""))
    base_num = _decimal_pipe(valor_pedido)
    if base_num is None or base_num <= 0:
        rotulo_valor = (
            "Valor de Implantação"
            if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO
            else "Valor Recorrência (mensalidade)"
        )
        raise PluneError(
            f"Deal {deal_id}: {rotulo_valor} inválido ou ausente no Pipedrive "
            f"({valor_pedido!r}) — necessário para BaseComissao."
        )

    base_fmt = _formatar_decimal_plune_numero(base_num)
    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
        return {
            "BaseComissao": base_fmt,
            "PercentualComissao": "0,001",
            "ValorComissao": base_fmt,
        }

    ucs = _somar_ucs_pipedrive(deal)
    if ucs <= 0:
        raise PluneError(
            f"Deal {deal_id}: pedido recorrente exige soma de UCs > 0 no Pipedrive "
            "para PercentualComissao (comissão)."
        )
    valor_comissao = base_num * float(PLUNE_COMISSAO_MESES_ANUAL)
    return {
        "BaseComissao": base_fmt,
        "PercentualComissao": _formatar_percentual_comissao_ucs(ucs),
        "ValorComissao": _formatar_decimal_plune_numero(valor_comissao),
    }


def _salvar_aviso_aprovacao_plune(mensagem: str) -> None:
    pasta = os.path.dirname(ARQUIVO_AVISOS_APROVACAO_PLUNE)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(ARQUIVO_AVISOS_APROVACAO_PLUNE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")
        f.flush()
        os.fsync(f.fileno())


def _montar_observacoes_pedido(deal: dict, tipo_pedido: str) -> dict:
    deal_id = str(deal.get("id", ""))
    title = str(deal.get("title", "")).strip()
    valor_mensal = get_val(deal, FIELD_VALOR_MENSAL)
    valor_implantacao = get_val(deal, FIELD_VALOR_IMPLANTACAO)
    qtd_sole = get_val(deal, FIELD_QTD_SOLE)
    sole_consultoria = get_val(deal, FIELD_QUALIDADE_ENERGIA)
    gestao_acl = get_val(deal, FIELD_GESTAO_ACL)
    gestao_usina = get_val(deal, FIELD_GESTAO_USINA_FOTOVOLTAICA)
    qualidade_energia = get_val(deal, FIELD_INDICADORES_QUALIDADE)

    observacao: list[str] = []

    obs_pipe = get_val(deal, FIELD_OBSERVACOES_DETALHES).strip()
    if obs_pipe:
        observacao.append(obs_pipe)

    if tipo_pedido == TIPO_PEDIDO_RECORRENTE and valor_mensal:
        observacao.extend(
            ["", f"MENSALIDADE: {_formatar_moeda_observacao(valor_mensal)}"]
        )

    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO and valor_implantacao:
        observacao.extend(
            ["", f"IMPLANTAÇÃO: {_formatar_moeda_observacao(valor_implantacao)}"]
        )

    percentual_exito = get_enum_label(deal, FIELD_PERCENTUAL_EXITO).strip()
    if percentual_exito:
        observacao.extend(["", f"ÊXITO GEBRAS: {percentual_exito}"])

    observacao.extend(
        [
            "",
            "PROPOSTA COMERCIAL ANEXA.",
            "",
            "PIPEDRIVE:",
            f"https://gebras.pipedrive.com/deal/{deal_id}",
        ]
    )

    unidade_nf = title or get_nome_cliente(deal).strip()
    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
        observacao_nf = "Faturamento referente à implantação de gestão de energia elétrica."
    else:
        observacao_nf = "Faturamento referente a gestão de energia elétrica."
    if unidade_nf:
        if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
            observacao_nf = (
                "Faturamento referente à implantação de gestão de energia elétrica "
                f"da unidade {unidade_nf}."
            )
        else:
            observacao_nf = (
                "Faturamento referente a gestão de energia elétrica "
                f"da unidade {unidade_nf}."
            )

    return {
        "Observacao": "\n".join(observacao).strip(),
        "ObservacaoNF": observacao_nf,
        "x1_ObservacaoAnexo": "\n".join(
            [
                f"Gestão Mercado Livre:{_quantidade_observacao(gestao_acl)};",
                f"SOLE Web (com telemetria):{_quantidade_observacao(qtd_sole)};",
                f"Sole Consultoria:{_quantidade_observacao(sole_consultoria)};",
                f"Gestão de Usina Fotovoltaica:{_quantidade_observacao(gestao_usina)};",
                f"Gestão de Qualidade de Energia:{_quantidade_observacao(qualidade_energia)};",
            ]
        ),
    }


def _descricao_pedido_plune(deal: dict, tipo_pedido: str) -> str:
    """Geral | Descrição: somente código do contrato (CGRc...)."""
    deal_id = str(deal.get("id", ""))
    p1 = get_val(deal, FIELD_NUMERO_CONTRATO_P1).strip()
    p2 = get_val(deal, FIELD_NUMERO_CONTRATO_P2).strip()
    if not p1 or not p2:
        raise PluneError(
            f"Deal {deal_id}: campos de número do contrato (P1/P2) ausentes no Pipedrive "
            "— necessários para Venda.Pedido.Descricao."
        )
    return get_numero_contrato(deal)[:128]


def _montar_params_pedido(deal: dict, parceiro: dict, tipo_pedido: str) -> dict:
    deal_id = str(deal.get("id", ""))
    title = str(deal.get("title", "")).strip()
    tipo_config = _PEDIDO_TIPO_CONFIG[tipo_pedido]
    chave_integracao = _pedido_integracao_tipo(deal_id, tipo_pedido)
    valor_pedido = get_val(deal, tipo_config["valor_field"])
    branch_id = _resolver_branch_id(deal)
    branch_cfg = settings_por_branch(branch_id)

    params = dict(_PEDIDO_DEFAULTS)
    params["Aprovado"] = _plune_aprovado_insert()
    params["BranchId"] = branch_id
    params["Serie"] = _pedido_serie(branch_id)
    params["ModeloId"] = _pedido_modelo_id(branch_id)
    params["StatusPedido"] = tipo_config["status_pedido"]
    params["ClienteId"] = str(parceiro["id"])
    params["Descricao"] = _descricao_pedido_plune(deal, tipo_pedido)
    params["PedidoIntegracao"] = chave_integracao
    # DataEntrega: somente na aprovação pós-Clicksign (última assinatura), ver aprovar_pedidos_plune.
    # ParametroContabilId = «Tipo de Lançamento» (FK _fkey_1364993941 em Pedido.md).
    # Deve ser coerente com o tipo de faturamento do pedido — ver Pedido-colunas.md.
    params["ParametroContabilId"] = _parametro_contabil_id(tipo_pedido, branch_id)
    params["TipoContratoId"] = _resolver_tipo_contrato_id(deal, tipo_pedido)
    params.update(_montar_campos_comissao(deal, tipo_pedido, valor_pedido))
    if branch_cfg["subcentro_custo_id"]:
        params["SubCentroCustoId"] = branch_cfg["subcentro_custo_id"]
    from .plune_catalog import resolver_subcentro

    regional = get_enum_label(deal, FIELD_REGIONAL).strip()
    subcentro2_id = resolver_subcentro(branch_id, 2, regional) or branch_cfg[
        "regional_map"
    ].get(regional)
    if subcentro2_id:
        params["SubCentroCusto2Id"] = str(subcentro2_id)
    subcentro3 = get_enum_label(deal, FIELD_SUBCENTRO_NIVEL_3).strip()
    subcentro3_id = resolver_subcentro(branch_id, 3, subcentro3) or branch_cfg[
        "subcentro3_map"
    ].get(subcentro3)
    if subcentro3_id:
        params["SubCentroCusto3Id"] = str(subcentro3_id)

    _aplicar_dados_cliente_pedido(params, parceiro, deal)

    campo_previsao = (
        FIELD_DATA_IMPLANTACAO
        if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO
        else FIELD_DATA_PRIMEIRA_COBRANCA
    )
    previsao_cobranca = get_val(deal, campo_previsao)
    if previsao_cobranca:
        params["x1_PrevisaoCobranca"] = formatar_data_ptbr(previsao_cobranca)

    # Valor vai no item (PedidoItem.Preco); pseudoValorProduto/ValorTotal são calculados.
    params["_valor_item_preco"] = _preco_item_pedido(valor_pedido)

    params.update(_montar_observacoes_pedido(deal, tipo_pedido))

    return params


def _montar_params_item_pedido(parceiro: dict, preco: str, branch_id: str) -> dict:
    """Linha de Venda.PedidoItem — alimenta Valor dos Produtos/Serviços no cabeçalho."""
    if not PLUNE_PRODUTO_SOLE_ID:
        raise PluneError(
            "PLUNE_PRODUTO_SOLE_ID não configurado (produto SOLE no Plune, ex.: 5584)"
        )
    return {
        "_Venda.Pedido.Slaves": "Venda.PedidoItem",
        "_Venda.Pedido.SlavesSave": "Venda.PedidoItem",
        "_Venda.PedidoItem.isSlave": "PedidoItem_CompanyId_fkey",
        "Venda.PedidoItem.CompanyId": PLUNE_COMPANY_ID,
        "Venda.PedidoItem.BranchId": branch_id,
        "Venda.PedidoItem.ProdutoId": PLUNE_PRODUTO_SOLE_ID,
        "Venda.PedidoItem.Quantidade": "1",
        "Venda.PedidoItem.Preco": preco,
        "Venda.PedidoItem.ClienteId": str(parceiro["id"]),
    }


def _buscar_pedido_id_por_pedido_integracao(deal_id: str) -> str | None:
    """
    Retorna Id do Venda.Pedido já existente com PedidoIntegracao = deal_id (Pipedrive).
    Evita Insert duplicado quando o arquivo de estado local foi perdido ou não foi gravado.
    """
    prefix = "Venda.Pedido."
    params = {
        f"{prefix}CompanyId": PLUNE_COMPANY_ID,
        f"{prefix}PedidoIntegracao": str(deal_id),
        "_Venda.Pedido.BrowseSequence": ["Id"],
        "_Venda.Pedido.BrowseLimit": "15",
    }
    payload = _plune_get("Venda.Pedido", "Browse", params)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]
    if not rows:
        return None
    if len(rows) > 1:
        print(
            f"[!] Aviso: {len(rows)} pedidos no Plune com PedidoIntegracao={deal_id!r}; "
            "tratando como já criado (primeiro registro)."
        )
    pedido_id = _field_value(rows[0], "Id")
    return pedido_id.strip() if pedido_id else None


def _buscar_pedido_por_pedido_integracao(pedido_integracao: str) -> dict | None:
    prefix = "Venda.Pedido."
    params = {
        f"{prefix}CompanyId": PLUNE_COMPANY_ID,
        f"{prefix}PedidoIntegracao": str(pedido_integracao),
        "_Venda.Pedido.BrowseSequence": [
            "Id",
            "ClienteId",
            "BranchId",
            "Aprovado",
            "PedidoIntegracao",
            "StatusPedido",
        ],
        "_Venda.Pedido.BrowseLimit": "15",
    }
    payload = _plune_get("Venda.Pedido", "Browse", params)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]
    if not rows:
        return None
    if len(rows) > 1:
        print(
            f"[!] Aviso: {len(rows)} pedidos no Plune com PedidoIntegracao={pedido_integracao!r}; "
            "usando o primeiro registro para aprovação."
        )
    row = rows[0]
    return {
        "id": _field_value(row, "Id"),
        "cliente_id": _field_value(row, "ClienteId"),
        "branch_id": _field_value(row, "BranchId"),
        "aprovado": _field_value(row, "Aprovado") in ("1", "1.0"),
        "pedido_integracao": _field_value(row, "PedidoIntegracao") or pedido_integracao,
        "status_pedido": _field_value(row, "StatusPedido"),
    }


def _inserir_ou_substituir_param_insert(
    pairs: list[tuple[str, str]], field_key: str, value: str
) -> list[tuple[str, str]]:
    """Substitui param na URL base ou acrescenta (ex.: comissão, TipoContratoId)."""
    target = f"Venda.Pedido.{field_key}"
    valor = str(value)
    substituido = False
    novo: list[tuple[str, str]] = []
    for chave, atual in pairs:
        if chave == target:
            novo.append((chave, valor))
            substituido = True
        else:
            novo.append((chave, atual))
    if not substituido:
        novo.append((target, valor))
    return novo


_INSERT_PARAMS_SUBSTITUIR_OU_ACRESCENTAR = frozenset(
    {
        "StatusPedido",
        "Serie",
        "ModeloId",
        "TipoContratoId",
        "BaseComissao",
        "PercentualComissao",
        "ValorComissao",
    }
)


def _montar_query_insert_pedido(
    deal: dict, parceiro: dict, tipo_pedido: str
) -> list[tuple[str, str]]:
    """Query do Insert na ordem do InsertPedidoBase (C#), sempre com Aprovado=0."""
    params = _montar_params_pedido(deal, parceiro, tipo_pedido)
    branch_id = str(params.get("BranchId") or _resolver_branch_id(deal))
    preco = params.pop("_valor_item_preco", None)

    aprovado_insert = _plune_aprovado_insert()
    pairs = list(_insert_pedido_base_url())
    for key, value in params.items():
        if value in (None, ""):
            continue
        if key in _INSERT_BASE_KEYS:
            if key in _INSERT_PARAMS_SUBSTITUIR_OU_ACRESCENTAR:
                pairs = _inserir_ou_substituir_param_insert(pairs, key, str(value))
            continue
        else:
            pairs.append((f"Venda.Pedido.{key}", str(value)))

    target_aprovado = f"Venda.Pedido.Aprovado"
    if not any(k == target_aprovado and v == aprovado_insert for k, v in pairs):
        pairs.insert(1, (target_aprovado, aprovado_insert))

    if preco:
        for key, value in _montar_params_item_pedido(parceiro, preco, branch_id).items():
            pairs.append((key, str(value)))

    return pairs


def _ordenar_resultados_por_tipo(resultados: list[dict]) -> list[dict]:
    ordem = {tipo: idx for idx, tipo in enumerate(_TIPOS_PEDIDO_PLUNE)}
    return sorted(resultados, key=lambda r: ordem.get(r.get("tipo"), 99))


def _anexar_documentos_pedido_criado(
    deal_id: str,
    pedido_id: str,
    branch_id: str,
    *,
    cache: CacheAnexosDeal | None,
    anexar_contrato_dev: bool,
) -> dict:
    """Proposta e contrato (dev) em paralelo; mesmo arquivo reutilizado via cache."""
    anexos: dict = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futuros = {
            "proposta": executor.submit(
                anexar_proposta_pedido,
                deal_id,
                pedido_id,
                branch_id,
                cache=cache,
            )
        }
        if anexar_contrato_dev:
            futuros["contrato"] = executor.submit(
                anexar_contrato_pedido,
                deal_id,
                pedido_id,
                branch_id,
                permitir_docx_local=True,
                cache=cache,
            )
        for chave, futuro in futuros.items():
            resultado = futuro.result()
            if resultado:
                anexos[chave] = resultado
    return anexos


def _criar_pedido_plune_tipo(
    deal: dict,
    parceiro: dict,
    parceiro_criado: bool,
    tipo_pedido: str,
    *,
    cache: CacheAnexosDeal | None = None,
    anexar_contrato_dev: bool = False,
    criados: set[str] | None = None,
) -> dict:
    deal_id = str(deal.get("id", ""))
    tipo_config = _PEDIDO_TIPO_CONFIG[tipo_pedido]
    chave_integracao = _pedido_integracao_tipo(deal_id, tipo_pedido)
    if criados is None:
        criados = carregar_pedidos_plune_criados()

    if tipo_pedido == TIPO_PEDIDO_IMPLANTACAO:
        valor_implantacao = get_val(deal, FIELD_VALOR_IMPLANTACAO)
        if not _valor_implantacao_valido_para_pedido(valor_implantacao):
            return {
                "status": "skipped",
                "deal_id": deal_id,
                "tipo": tipo_pedido,
                "pedido_integracao": chave_integracao,
                "reason": "valor_implantacao_invalido_ou_menor_igual_1",
                "valor_pipe": valor_implantacao,
            }

    if chave_integracao in criados:
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "reason": "already_in_local_state",
        }

    pedido_existente = _buscar_pedido_id_por_pedido_integracao(chave_integracao)
    if pedido_existente:
        salvar_pedido_plune_criado(chave_integracao)
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "reason": "already_in_plune",
            "pedido_id": pedido_existente,
        }

    branch_id = _resolver_branch_id(deal)
    parametro_contabil = _parametro_contabil_id(tipo_pedido, branch_id)

    query_insert = _montar_query_insert_pedido(deal, parceiro, tipo_pedido)

    payload = _plune_get("Venda.Pedido", "Insert", query_insert)
    field = payload.get("Field") or {}
    pedido_id = _field_value(field, "Id")
    esperado = _plune_aprovado_insert()
    aprovado = _field_value(field, "Aprovado")
    aprovado_insert_ok = aprovado in (esperado, f"{esperado}.0")
    aprovado_flag = aprovado in ("1", "1.0")
    if not aprovado_insert_ok:
        mensagem_aprovacao = (
            "Plune retornou Aprovado inesperado no Insert: "
            f"enviado Venda.Pedido.Aprovado={esperado}, mas o retorno veio Aprovado={aprovado or '0'}. "
            f"PedidoId={pedido_id or '-'}, PedidoIntegracao={chave_integracao}, "
            f"tipo={tipo_pedido}, StatusPedido={tipo_config['status_pedido']}, "
            f"ParametroContabilId={parametro_contabil}. "
            "No fluxo oficial, o pedido deve nascer não aprovado e ser aprovado só após assinatura."
        )
        print(f"[!] {mensagem_aprovacao}")
        _salvar_aviso_aprovacao_plune(mensagem_aprovacao)
    else:
        mensagem_aprovacao = ""

    salvar_pedido_plune_criado(chave_integracao)

    anexos: dict = {}
    if pedido_id:
        anexos = _anexar_documentos_pedido_criado(
            deal_id,
            pedido_id,
            branch_id,
            cache=cache,
            anexar_contrato_dev=anexar_contrato_dev,
        )

    result = {
        "status": "created",
        "deal_id": deal_id,
        "tipo": tipo_pedido,
        "pedido_integracao": chave_integracao,
        "cliente_id": parceiro["id"],
        "cliente_nome": parceiro.get("razao_social"),
        "parceiro_criado": parceiro_criado,
        "pedido_id": pedido_id,
        "aprovado": aprovado_flag,
        "status_pedido": tipo_config["status_pedido"],
        "parametro_contabil_id": parametro_contabil,
    }
    if anexos:
        result["anexos"] = anexos
    if mensagem_aprovacao:
        result["aviso_aprovacao"] = mensagem_aprovacao
    return result


def _aprovar_pedido_plune_tipo(
    deal_id: str,
    tipo_pedido: str,
    *,
    data_entrega: str | None = None,
    cache: CacheAnexosDeal | None = None,
) -> dict:
    chave_integracao = _pedido_integracao_tipo(deal_id, tipo_pedido)
    pedido = _buscar_pedido_por_pedido_integracao(chave_integracao)
    if not pedido:
        return {
            "status": "missing",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "reason": "pedido_nao_encontrado",
        }

    branch_id = str(pedido.get("branch_id") or "").strip()
    if pedido["aprovado"]:
        anexos: dict = {}
        contrato = None
        if branch_id:
            contrato = anexar_contrato_pedido(
                deal_id,
                pedido["id"],
                branch_id,
                permitir_docx_local=False,
                cache=cache,
            )
            if contrato:
                anexos["contrato"] = contrato
        out = {
            "status": "skipped" if contrato else "pending_contract",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "pedido_id": pedido["id"],
            "reason": "already_approved" if contrato else "signed_contract_unavailable",
        }
        if anexos:
            out["anexos"] = anexos
        return out

    # Regra de negócio: nunca aprovar sem contrato assinado disponível para anexar.
    contrato_pre: dict | None = None
    if not branch_id:
        return {
            "status": "pending_contract",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "pedido_id": pedido["id"],
            "aprovado": False,
            "reason": "branch_id_missing_for_contract",
        }
    contrato_pre = anexar_contrato_pedido(
        deal_id,
        pedido["id"],
        branch_id,
        permitir_docx_local=False,
        cache=cache,
    )
    if not contrato_pre:
        return {
            "status": "pending_contract",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "pedido_id": pedido["id"],
            "aprovado": False,
            "reason": "signed_contract_unavailable",
        }
    if contrato_pre.get("erro"):
        return {
            "status": "pending_contract",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "pedido_id": pedido["id"],
            "aprovado": False,
            "reason": "contract_attach_failed",
            "anexos": {"contrato": contrato_pre},
        }

    params = {
        "Venda.Pedido.CompanyId": PLUNE_COMPANY_ID,
        "Venda.Pedido.ClienteId": pedido["cliente_id"],
        "Venda.Pedido.Id": pedido["id"],
        "Venda.Pedido.Aprovado": "1",
    }
    if data_entrega:
        params["Venda.Pedido.DataEntrega"] = data_entrega
    try:
        payload = _plune_get("Venda.Pedido", "Update", params)
    except PluneError as exc:
        erro_plune = getattr(exc, "raw_error", str(exc))
        mensagem = (
            "Plune não aprovou o pedido por Update: "
            f"enviado Venda.Pedido.Aprovado=1, mas a API retornou erro: {exc}. "
            f"PedidoId={pedido['id']}, PedidoIntegracao={chave_integracao}, tipo={tipo_pedido}. "
            "A coluna Aprovado não aparece como alterável na documentação de Venda.Pedido; "
            "validar com Plune qual ação/API deve ser usada para aprovar após assinatura."
        )
        print(f"[!] {mensagem}")
        _salvar_aviso_aprovacao_plune(erro_plune)
        return {
            "status": "not_approved",
            "deal_id": deal_id,
            "tipo": tipo_pedido,
            "pedido_integracao": chave_integracao,
            "pedido_id": pedido["id"],
            "aprovado": False,
            "aviso_aprovacao": mensagem,
            "anexos": {"contrato": contrato_pre},
        }

    field = payload.get("Field") or {}
    aprovado = _field_value(field, "Aprovado")
    aprovado_ok = aprovado in ("1", "1.0")
    if not aprovado_ok:
        mensagem = (
            "Plune não aprovou automaticamente o pedido após Update: "
            f"enviado Venda.Pedido.Aprovado=1, mas o retorno veio Aprovado={aprovado or '0'}. "
            f"PedidoId={pedido['id']}, PedidoIntegracao={chave_integracao}, tipo={tipo_pedido}. "
            "Validar permissão/regra do usuário/token da API para aprovar pedido no cadastro."
        )
        print(f"[!] {mensagem}")
        _salvar_aviso_aprovacao_plune(mensagem)

    anexos: dict = {"contrato": contrato_pre}

    result = {
        "status": "approved" if aprovado_ok else "not_approved",
        "deal_id": deal_id,
        "tipo": tipo_pedido,
        "pedido_integracao": chave_integracao,
        "pedido_id": pedido["id"],
        "aprovado": aprovado_ok,
    }
    if anexos:
        result["anexos"] = anexos
    if data_entrega:
        result["data_entrega"] = data_entrega
    if not aprovado_ok:
        result["aviso_aprovacao"] = mensagem
    return result


def _pedidos_plune_deal_resolvidos(resultados: list[dict]) -> bool:
    return all(
        r.get("status") in ("created", "skipped")
        for r in resultados
    )


def criar_pedido_plune(deal_id: str, *, anexar_contrato: bool | None = None) -> dict:
    """Pega o deal no Pipedrive e cria os pedidos de implantação e recorrência no Plune."""
    if not PLUNE_BRANCH_ID or not PLUNE_TIPO_OP_ID:
        raise PluneError(
            "Configuração Plune incompleta (BranchId / TipoOpId em gebras_defaults.py)"
        )

    deal_id = str(deal_id)
    deal = buscar_deal_por_id(deal_id)
    if not deal:
        raise PluneError(f"Deal {deal_id} não encontrado no Pipedrive")

    cnpj = get_documento(deal)
    if not cnpj:
        raise PluneError(f"Deal {deal_id} sem CNPJ no Pipedrive")

    if anexar_contrato is None:
        anexar_contrato_dev = bool(TESTE_PLUNE_SEM_ASSINATURA or DEV_PULAR_CLICKSIGN)
    else:
        anexar_contrato_dev = anexar_contrato
    cache = CacheAnexosDeal(deal_id, permitir_docx_local=anexar_contrato_dev)
    # Download da proposta (~MB) em paralelo com parceiro + Insert dos pedidos
    cache.iniciar_prefetch_assincrono(
        proposta=True, contrato=anexar_contrato_dev
    )

    parceiro, parceiro_criado = _resolver_ou_criar_parceiro(deal)
    criados = carregar_pedidos_plune_criados()

    resultados: list[dict] = []
    with ThreadPoolExecutor(max_workers=len(_TIPOS_PEDIDO_PLUNE)) as executor:
        futuros = {
            executor.submit(
                _criar_pedido_plune_tipo,
                deal,
                parceiro,
                parceiro_criado,
                tipo_pedido,
                cache=cache,
                anexar_contrato_dev=anexar_contrato_dev,
                criados=criados,
            ): tipo_pedido
            for tipo_pedido in _TIPOS_PEDIDO_PLUNE
        }
        for futuro in as_completed(futuros):
            resultados.append(futuro.result())
    resultados = _ordenar_resultados_por_tipo(resultados)
    vincular_pedidos_plune_implantacao_recorrente(
        resultados, cliente_id=str(parceiro["id"])
    )

    if _pedidos_plune_deal_resolvidos(resultados):
        ids = [
            str(r.get("pedido_id"))
            for r in resultados
            if r.get("pedido_id") not in (None, "")
        ]
        marcar_pedido_criado(deal_id, ",".join(ids) if ids else None)

    if any(r.get("status") == "created" for r in resultados):
        status = "created"
    elif all(r.get("status") == "skipped" for r in resultados):
        status = "skipped"
    else:
        status = "partial"

    return {
        "status": status,
        "deal_id": deal_id,
        "cliente_id": parceiro["id"],
        "cliente_nome": parceiro.get("razao_social"),
        "parceiro_criado": parceiro_criado,
        "pedidos": resultados,
    }


def aprovar_pedidos_plune(
    deal_id: str, *, data_entrega: str | None = None
) -> dict:
    """Após assinatura do contrato, aprova pedidos Plune e define DataEntrega (dd/mm/aaaa)."""
    deal_id = str(deal_id)
    if DEV_PLUNE_APROVADO_NAO:
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "dev_plune_aprovado_nao",
            "pedidos": [
                {
                    "status": "skipped",
                    "deal_id": deal_id,
                    "tipo": tipo,
                    "reason": "dev_plune_aprovado_nao",
                }
                for tipo in _TIPOS_PEDIDO_PLUNE
            ],
        }
    cache = CacheAnexosDeal(deal_id, permitir_docx_local=False)
    cache.iniciar_prefetch_assincrono(proposta=False, contrato=True)

    resultados: list[dict] = []
    with ThreadPoolExecutor(max_workers=len(_TIPOS_PEDIDO_PLUNE)) as executor:
        futuros = {
            executor.submit(
                _aprovar_pedido_plune_tipo,
                deal_id,
                tipo_pedido,
                data_entrega=data_entrega,
                cache=cache,
            ): tipo_pedido
            for tipo_pedido in _TIPOS_PEDIDO_PLUNE
        }
        for futuro in as_completed(futuros):
            resultados.append(futuro.result())
    resultados = _ordenar_resultados_por_tipo(resultados)

    if any(r.get("status") == "pending_contract" for r in resultados):
        status = "pending_contract"
    elif any(r.get("status") == "approved" for r in resultados):
        status = "approved"
    elif all(r.get("status") == "skipped" for r in resultados):
        status = "skipped"
    elif any(r.get("status") == "missing" for r in resultados):
        status = "missing"
    else:
        status = "not_approved"

    out = {
        "status": status,
        "deal_id": deal_id,
        "pedidos": resultados,
    }
    if data_entrega:
        out["data_entrega"] = data_entrega
    return out
