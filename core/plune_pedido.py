"""
Card assinado → dados Pipedrive → pedido no Plune.

Um único módulo: cliente Plune, mapeamento de campos e criação do pedido.
"""

from urllib.parse import urlencode

import json
import requests

from .config import (
    PLUNE_AUTH_TOKEN,
    PLUNE_BASE_URL,
    PLUNE_BRANCH_ID,
    PLUNE_CENTRO_CUSTO_ID,
    PLUNE_COMPANY_ID,
    PLUNE_PRODUTO_SOLE_ID,
    PLUNE_STATUS_PEDIDO,
    PLUNE_TIPO_CONTRATO_ID,
    PLUNE_TIPO_OP_ID,
)
from .envelope_state import (
    carregar_pedidos_plune_criados,
    marcar_pedido_criado,
    salvar_pedido_plune_criado,
)
from .pipedrive_fields import (
    FIELD_CIDADE,
    FIELD_CONTATO_CONTRATANTE,
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_ENDERECO,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
    buscar_deal_por_id,
    formatar_data_ptbr,
    formatar_decimal_plune,
    get_documento,
    get_nome_cliente,
    get_numero_contrato,
    get_val,
    normalizar_documento,
    normalizar_nome,
)


class PluneError(RuntimeError):
    pass


# InsertPedidoBase (URLs.cs) — ordem na URL; Aprovado=1 logo após CompanyId
_INSERT_PEDIDO_BASE_URL: list[tuple[str, str]] = [
    ("Venda.Pedido.CompanyId", PLUNE_COMPANY_ID),
    ("Venda.Pedido.Aprovado", "1"),
    ("Venda.Pedido.Status", "5"),
    ("Venda.Pedido.StatusPedido", PLUNE_STATUS_PEDIDO),
    ("Venda.Pedido.ModeloId", "01"),
    ("Venda.Pedido.NaturezaOperacaoServicoId", "2"),
    ("Venda.Pedido.Serie", "1"),
    ("Venda.Pedido.TipoContratoId", PLUNE_TIPO_CONTRATO_ID),
    ("Venda.Pedido.CentroCustoId", PLUNE_CENTRO_CUSTO_ID),
    ("Venda.Pedido.ParcelamentoAutomatico", "1"),
    ("Venda.Pedido.ComissaoManual", "1"),
    ("Venda.Pedido.PercentualComissao", "0,001"),
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
    "PercentualComissao",
}

# Defaults internos (montagem do cabeçalho)
_PEDIDO_DEFAULTS = {
    "CompanyId": PLUNE_COMPANY_ID,
    "Aprovado": "1",
    "Status": "5",
    "StatusPedido": PLUNE_STATUS_PEDIDO,
    "ModeloId": "01",
    "Serie": "1",
    "NaturezaOperacaoServicoId": "2",
    "TipoContratoId": PLUNE_TIPO_CONTRATO_ID,
    "CentroCustoId": PLUNE_CENTRO_CUSTO_ID,
    "ParcelamentoAutomatico": "1",
    "ComissaoManual": "1",
    "PercentualComissao": "0,001",
    "BranchId": PLUNE_BRANCH_ID,
    "TipoOpId": PLUNE_TIPO_OP_ID,
}


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
    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/{class_id}/{method}?{urlencode(query, doseq=True)}"
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
        raise PluneError(f"Plune ErrorStatus: {error}")
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
    "EnderecoPrincipal",
    "BairroPrincipal",
    "CidadePrincipalId",
    "CidadePrincipalEx",
    "UFPrincipalId",
    "CEPPrincipal",
    "ContatoNome",
    "EMail",
]


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
    contato = get_val(deal, FIELD_CONTATO_CONTRATANTE).strip()

    if not nome:
        raise PluneError("Deal sem razão social/nome do cliente no Pipedrive")
    if not documento:
        raise PluneError("Deal sem CPF/CNPJ no Pipedrive")

    params = {
        "EmpresaId": PLUNE_COMPANY_ID,
        "NomFantasia": nome[:60],
        "NomRazaoSocial": nome[:60],
        "Ativo": "1",
        "EmProspeccao": "0",
        "EmAprovacao": "0",
        "ECliente": "1",
        "EFornecedor": "0",
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

    return _criar_parceiro(deal), True


def _aplicar_dados_cliente_pedido(params: dict, parceiro: dict) -> None:
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
    if parceiro.get("cep"):
        params["ClienteCep"] = parceiro["cep"][:8]


def _montar_params_pedido(deal: dict, parceiro: dict) -> dict:
    deal_id = str(deal.get("id", ""))
    title = str(deal.get("title", "")).strip()

    params = dict(_PEDIDO_DEFAULTS)
    params["ClienteId"] = str(parceiro["id"])
    params["Descricao"] = f"Deal {deal_id} - {title}"[:128]
    params["PedidoIntegracao"] = deal_id
    params["DataEntrega"] = formatar_data_ptbr(deal.get("won_time") or deal.get("add_time"))

    _aplicar_dados_cliente_pedido(params, parceiro)

    primeira_cobranca = get_val(deal, FIELD_DATA_PRIMEIRA_COBRANCA)
    if primeira_cobranca:
        params["x1_PrevisaoCobranca"] = formatar_data_ptbr(primeira_cobranca)

    valor_mensal = get_val(deal, FIELD_VALOR_MENSAL)
    valor_implantacao = get_val(deal, FIELD_VALOR_IMPLANTACAO)
    # Valor vai no item (PedidoItem.Preco); pseudoValorProduto/ValorTotal são calculados.
    valor_pedido = valor_implantacao or valor_mensal
    if valor_pedido:
        params["_valor_item_preco"] = formatar_decimal_plune(valor_pedido)

    obs = [
        f"Pipedrive deal_id={deal_id}",
        f"contrato={get_numero_contrato(deal)}",
    ]
    for campo, label in (
        (FIELD_INDICADORES_QUALIDADE, "indicadores"),
        (FIELD_QUALIDADE_ENERGIA, "qualidade_energia"),
    ):
        val = get_val(deal, campo)
        if val:
            obs.append(f"{label}={val}")
    params["Observacao"] = " | ".join(obs)

    return params


def _montar_params_item_pedido(parceiro: dict, preco: str) -> dict:
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
        "Venda.PedidoItem.BranchId": PLUNE_BRANCH_ID,
        "Venda.PedidoItem.ProdutoId": PLUNE_PRODUTO_SOLE_ID,
        "Venda.PedidoItem.Quantidade": "1",
        "Venda.PedidoItem.Preco": preco,
        "Venda.PedidoItem.ClienteId": str(parceiro["id"]),
    }


def _montar_query_insert_pedido(deal: dict, parceiro: dict) -> list[tuple[str, str]]:
    """Query do Insert na ordem do InsertPedidoBase (C#), com Venda.Pedido.Aprovado=1."""
    params = _montar_params_pedido(deal, parceiro)
    preco = params.pop("_valor_item_preco", None)

    pairs = list(_INSERT_PEDIDO_BASE_URL)
    for key, value in params.items():
        if key in _INSERT_BASE_KEYS or value in (None, ""):
            continue
        pairs.append((f"Venda.Pedido.{key}", str(value)))

    if not any(k == "Venda.Pedido.Aprovado" and v == "1" for k, v in pairs):
        pairs.insert(1, ("Venda.Pedido.Aprovado", "1"))

    if preco:
        for key, value in _montar_params_item_pedido(parceiro, preco).items():
            pairs.append((key, str(value)))

    return pairs


def criar_pedido_plune(deal_id: str) -> dict:
    """Pega o deal no Pipedrive e cria Venda.Pedido no Plune."""
    if not PLUNE_BRANCH_ID or not PLUNE_TIPO_OP_ID:
        raise PluneError(
            "Preencha PLUNE_BRANCH_ID e PLUNE_TIPO_OP_ID no .env "
            "(copie de um pedido Sole existente no Plune)"
        )

    deal_id = str(deal_id)
    if deal_id in carregar_pedidos_plune_criados():
        return {"status": "skipped", "deal_id": deal_id}

    deal = buscar_deal_por_id(deal_id)
    if not deal:
        raise PluneError(f"Deal {deal_id} não encontrado no Pipedrive")

    cnpj = get_documento(deal)
    if not cnpj:
        raise PluneError(f"Deal {deal_id} sem CNPJ no Pipedrive")

    parceiro, parceiro_criado = _resolver_ou_criar_parceiro(deal)
    query_insert = _montar_query_insert_pedido(deal, parceiro)

    payload = _plune_get("Venda.Pedido", "Insert", query_insert)
    field = payload.get("Field") or {}
    pedido_id = _field_value(field, "Id")
    aprovado = _field_value(field, "Aprovado")
    if aprovado not in ("1", "1.0"):
        print(
            "[!] Plune retornou Aprovado="
            f"{aprovado or '0'} após Insert (URL enviou Venda.Pedido.Aprovado=1). "
            "O token da API pode não ter permissão de aprovação no cadastro."
        )

    salvar_pedido_plune_criado(deal_id)
    marcar_pedido_criado(deal_id, pedido_id)

    return {
        "status": "created",
        "deal_id": deal_id,
        "cliente_id": parceiro["id"],
        "cliente_nome": parceiro.get("razao_social"),
        "parceiro_criado": parceiro_criado,
        "pedido_id": pedido_id,
        "aprovado": aprovado in ("1", "1.0"),
    }
