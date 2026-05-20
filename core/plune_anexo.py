"""
Anexos de pedido Plune (Venda.AnexoPedido).
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from .config import PLUNE_AUTH_TOKEN, PLUNE_BASE_URL, PLUNE_COMPANY_ID
from .plune_errors import PluneApiError, PluneError


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


def inserir_anexo_pedido(
    *,
    pedido_id: str,
    branch_id: str,
    nome_arquivo: str,
    conteudo: bytes,
    content_type: str = "application/pdf",
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
