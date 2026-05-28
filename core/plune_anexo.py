"""
Anexos de pedido Plune (Venda.AnexoPedido).
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from .config import PLUNE_AUTH_TOKEN, PLUNE_BASE_URL, PLUNE_COMPANY_ID
from .plune_errors import PluneApiError, PluneError

_TIPO_ANEXO_CACHE: dict[str, str] = {}


def _parse_plune_json(text: str) -> dict:
    text = text.lstrip()
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


def _field_value(item: object) -> str:
    """Extrai value de payloads Plune {value: ...} ou retorna str simples."""
    if item is None:
        return ""
    if isinstance(item, dict):
        return str(item.get("value") or item.get("Value") or "").strip()
    return str(item).strip()


def _row_get(row: dict, *keys: str) -> str:
    for key in keys:
        if key in row:
            val = row.get(key)
            if isinstance(val, dict):
                return _field_value(val)
            return str(val or "").strip()
    return ""


def listar_anexos_pedido(*, pedido_id: str, branch_id: str) -> list[dict]:
    """
    Lista anexos do pedido no Plune (Venda.AnexoPedido/Browse).
    Retorna lista de dicts normalizados: {anexo_id, nome_arquivo, pedido_id, branch_id}.
    """
    if not PLUNE_BASE_URL or not PLUNE_AUTH_TOKEN:
        raise PluneError("Plune não configurado (PLUNE_BASE_URL / PLUNE_AUTH_TOKEN)")
    pedido_id = str(pedido_id).strip()
    branch_id = str(branch_id).strip()
    if not pedido_id or not branch_id:
        raise PluneError("pedido_id e branch_id obrigatórios para listar anexo Plune")

    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/Venda.AnexoPedido/Browse"
    params = {
        "Venda.AnexoPedido.CompanyId": PLUNE_COMPANY_ID,
        "Venda.AnexoPedido.BranchId": branch_id,
        "Venda.AnexoPedido.PedidoId": pedido_id,
        "_AuthToken": PLUNE_AUTH_TOKEN,
        # Tenta trazer também Tipo/Observação para nossas regras de limpeza.
        "_Venda.AnexoPedido.BrowseSequence": [
            "Id",
            "NomeArquivo",
            "x1_TipoAnexo",
            "TipoAnexo",
            "TipoAnexoId",
            "x1_ObservacaoAnexo",
            "Observacao",
            "ObservacaoAnexo",
        ],
        "_Venda.AnexoPedido.BrowseLimit": "200",
    }
    response = requests.get(url, params=params, timeout=60)
    if not response.ok:
        raise PluneError(
            f"Plune AnexoPedido Browse HTTP {response.status_code}: {response.text[:500]}"
        )
    payload = _parse_plune_json(response.text)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]
    out: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        anexo_id = _row_get(row, "Id", "id")
        nome = _row_get(row, "NomeArquivo", "Nome", "Arquivo", "Anexo", "FileName", "filename")
        if not nome:
            # alguns payloads vêm com chave "AnexoNome"
            nome = _row_get(row, "AnexoNome", "anexo_nome")
        tipo = _row_get(
            row,
            "x1_TipoAnexo",
            "TipoAnexoId",
            "TipoAnexo",
            "Tipo",
            "tipo_anexo",
        )
        obs = _row_get(
            row,
            "x1_ObservacaoAnexo",
            "Observacao",
            "ObservacaoAnexo",
            "Obs",
            "observacao",
            "observacao_anexo",
        )
        out.append(
            {
                "anexo_id": anexo_id,
                "nome_arquivo": nome,
                "tipo_anexo": tipo,
                "observacao": obs,
                "pedido_id": pedido_id,
                "branch_id": branch_id,
            }
        )
    return out


def remover_anexo_pedido(*, pedido_id: str, branch_id: str, anexo_id: str) -> None:
    """Remove um anexo específico do pedido (Venda.AnexoPedido/Delete)."""
    if not PLUNE_BASE_URL or not PLUNE_AUTH_TOKEN:
        raise PluneError("Plune não configurado (PLUNE_BASE_URL / PLUNE_AUTH_TOKEN)")
    pedido_id = str(pedido_id).strip()
    branch_id = str(branch_id).strip()
    anexo_id = str(anexo_id).strip()
    if not pedido_id or not branch_id or not anexo_id:
        raise PluneError("pedido_id, branch_id e anexo_id obrigatórios para remover anexo")

    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/Venda.AnexoPedido/Delete"
    params = {
        "Venda.AnexoPedido.CompanyId": PLUNE_COMPANY_ID,
        "Venda.AnexoPedido.BranchId": branch_id,
        "Venda.AnexoPedido.PedidoId": pedido_id,
        "Venda.AnexoPedido.Id": anexo_id,
        "_AuthToken": PLUNE_AUTH_TOKEN,
        "_Venda.AnexoPedido.OK": "1",
    }
    response = requests.get(url, params=params, timeout=60)
    if not response.ok:
        raise PluneError(
            f"Plune AnexoPedido Delete HTTP {response.status_code}: {response.text[:500]}"
        )
    _parse_plune_json(response.text)


def remover_todos_anexos_pedido(*, pedido_id: str, branch_id: str) -> dict:
    """
    Remove TODOS os anexos do pedido antes de anexar novamente (proposta/contrato).
    Best-effort: retorna contagem e nomes removidos (erros são propagados).
    """
    anexos = listar_anexos_pedido(pedido_id=pedido_id, branch_id=branch_id)
    removidos: list[str] = []
    for a in anexos:
        anexo_id = str(a.get("anexo_id") or "").strip()
        if not anexo_id:
            continue
        nome = str(a.get("nome_arquivo") or "").strip()
        remover_anexo_pedido(pedido_id=pedido_id, branch_id=branch_id, anexo_id=anexo_id)
        removidos.append(nome or anexo_id)
    return {"removidos": removidos, "total": len(removidos)}


def remover_contratos_pedido(
    *,
    pedido_id: str,
    branch_id: str,
    tipo_anexo_contrato_id: str | None = None,
    observacao_prefix: str | None = None,
) -> dict:
    """
    Remove SOMENTE anexos de contrato.
    Preferência:
    - se tipo_anexo_contrato_id vier: remove anexos com x1_TipoAnexo == esse id
    - se observacao_prefix vier: remove anexos cuja x1_ObservacaoAnexo começa com o prefixo
    - fallback: nome do arquivo contém "contrato"
    """
    anexos = listar_anexos_pedido(pedido_id=pedido_id, branch_id=branch_id)
    removidos: list[str] = []
    for a in anexos:
        anexo_id = str(a.get("anexo_id") or "").strip()
        if not anexo_id:
            continue
        nome = str(a.get("nome_arquivo") or "").strip()
        tipo = str(a.get("tipo_anexo") or "").strip()
        obs = str(a.get("observacao") or "").strip()

        is_contrato = False
        if tipo_anexo_contrato_id and tipo == str(tipo_anexo_contrato_id).strip():
            is_contrato = True
        elif observacao_prefix and obs.upper().startswith(str(observacao_prefix).strip().upper()):
            is_contrato = True
        elif "contrato" in nome.lower():
            is_contrato = True

        if not is_contrato:
            continue

        remover_anexo_pedido(pedido_id=pedido_id, branch_id=branch_id, anexo_id=anexo_id)
        removidos.append(nome or anexo_id)
    return {"removidos": removidos, "total": len(removidos)}


def remover_anexos_automacao(
    *,
    pedido_id: str,
    branch_id: str,
    tipo_anexo_id: str | None,
    observacao_prefix: str | None,
) -> dict:
    """
    Remove anexos criados pela automação para um tipo específico.
    Critérios (OR):
    - tipo_anexo_id: x1_TipoAnexo == tipo_anexo_id
    - observacao_prefix: x1_ObservacaoAnexo começa com observacao_prefix
    """
    anexos = listar_anexos_pedido(pedido_id=pedido_id, branch_id=branch_id)
    removidos: list[str] = []
    for a in anexos:
        anexo_id = str(a.get("anexo_id") or "").strip()
        if not anexo_id:
            continue
        nome = str(a.get("nome_arquivo") or "").strip()
        tipo = str(a.get("tipo_anexo") or "").strip()
        obs = str(a.get("observacao") or "").strip()
        if tipo_anexo_id and tipo == str(tipo_anexo_id).strip():
            pass
        elif observacao_prefix and obs.upper().startswith(str(observacao_prefix).strip().upper()):
            pass
        else:
            continue
        remover_anexo_pedido(pedido_id=pedido_id, branch_id=branch_id, anexo_id=anexo_id)
        removidos.append(nome or anexo_id)
    return {"removidos": removidos, "total": len(removidos)}


def inserir_anexo_pedido(
    *,
    pedido_id: str,
    branch_id: str,
    nome_arquivo: str,
    conteudo: bytes,
    content_type: str = "application/pdf",
    tipo_anexo: str | None = None,
    observacao: str | None = None,
) -> dict:
    """
    Insere linha em Venda.AnexoPedido (Pedido: Anexos) com upload multipart.
    """
    if not PLUNE_BASE_URL or not PLUNE_AUTH_TOKEN:
        raise PluneError("Plune não configurado (PLUNE_BASE_URL / PLUNE_AUTH_TOKEN)")
    pedido_id = str(pedido_id).strip()
    branch_id = str(branch_id).strip()
    if not pedido_id or not branch_id:
        raise PluneError("pedido_id e branch_id obrigatórios para anexo Plune")
    if not conteudo:
        raise PluneError(f"Arquivo vazio: {nome_arquivo!r}")

    nome_arquivo = Path(nome_arquivo).name or "anexo.pdf"
    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/Venda.AnexoPedido/Insert"
    data = {
        "Venda.AnexoPedido.CompanyId": PLUNE_COMPANY_ID,
        "Venda.AnexoPedido.BranchId": branch_id,
        "Venda.AnexoPedido.PedidoId": pedido_id,
        "_AuthToken": PLUNE_AUTH_TOKEN,
        "_Venda.AnexoPedido.OK": "1",
    }
    # Campos opcionais (tela do Plune: "Tipo de anexo" e "Observação do Anexo").
    # Mantemos ambos como string por compatibilidade com o que o Plune costuma aceitar em Insert.
    if tipo_anexo:
        # Doc: campo FK chama x1_TipoAnexo na tabela Venda.AnexoPedido.
        # Em alguns ambientes o Plune também aceita/expõe alias "TipoAnexo".
        val = str(tipo_anexo).strip()
        data["Venda.AnexoPedido.x1_TipoAnexo"] = val
        data["Venda.AnexoPedido.TipoAnexo"] = val
    if observacao:
        val = str(observacao).strip()
        # Doc: campo chama x1_ObservacaoAnexo.
        data["Venda.AnexoPedido.x1_ObservacaoAnexo"] = val
    files = {
        "Venda.AnexoPedido.Anexo": (nome_arquivo, conteudo, content_type),
    }
    response = requests.post(url, data=data, files=files, timeout=180)
    if not response.ok:
        raise PluneError(
            f"Plune AnexoPedido Insert HTTP {response.status_code}: {response.text[:500]}"
        )
    payload = _parse_plune_json(response.text)
    field = payload.get("Field") or {}
    anexo_id = ""
    if isinstance(field, dict):
        item = field.get("Id") or {}
        if isinstance(item, dict):
            anexo_id = str(item.get("value") or "")
        else:
            anexo_id = str(item or "")
    return {
        "anexo_id": anexo_id,
        "nome_arquivo": nome_arquivo,
        "pedido_id": pedido_id,
        "branch_id": branch_id,
    }


def resolver_tipo_anexo_id(label: str) -> str:
    """
    Resolve o ID (int4) do cadastro `Venda.x1_PedidoTipoAnexo` pelo rótulo (ex.: "CONTRATO").
    Necessário porque `Venda.AnexoPedido.x1_TipoAnexo` é FK (int), não texto.
    """
    label = str(label or "").strip()
    if not label:
        return ""
    key = label.upper()
    if key in _TIPO_ANEXO_CACHE:
        return _TIPO_ANEXO_CACHE[key]
    if not PLUNE_BASE_URL or not PLUNE_AUTH_TOKEN:
        return ""

    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/Venda.x1_PedidoTipoAnexo/Browse"
    params = {
        "_AuthToken": PLUNE_AUTH_TOKEN,
        "_Venda.x1_PedidoTipoAnexo.BrowseLimit": "200",
        "_Venda.x1_PedidoTipoAnexo.BrowseSequence": ["Id", "Descricao", "Nome"],
        # Alguns ambientes exigem CompanyId no cadastro
        "Venda.x1_PedidoTipoAnexo.CompanyId": PLUNE_COMPANY_ID,
    }
    response = requests.get(url, params=params, timeout=60)
    if not response.ok:
        return ""
    payload = _parse_plune_json(response.text)
    rows = payload.get("data", {}).get("row", []) or []
    if isinstance(rows, dict):
        rows = [rows]
    for row in rows:
        if not isinstance(row, dict):
            continue
        desc = _row_get(row, "Descricao", "Nome", "descricao", "nome")
        if desc.strip().upper() == key:
            tipo_id = _row_get(row, "Id", "id")
            if tipo_id:
                _TIPO_ANEXO_CACHE[key] = tipo_id
                return tipo_id
    return ""
