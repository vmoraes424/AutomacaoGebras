"""Formulário ↔ estrutura HUB (pedido_instalacao_extra + pedido_instalacao_servico)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from core.hub_catalogo import servico_catalogo_por_chave, servicos_template_hub

# Ordem das colunas no formulário (legado servicos.uc_linhas).
UC_SERVICO_KEYS = (
    "sole_web",
    "sole_consultoria",
    "gestao_acl",
    "gestao_usina_fotovoltaica",
    "gestao_qualidade_energia",
)


def _parse_valor_storage(valor: Any) -> Decimal:
    texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto:
        return Decimal("0")
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation:
        return Decimal("0")


def format_valor_br_hub(valor: Decimal) -> str:
    quantizado = valor.quantize(Decimal("0.01"))
    inteiro, _, frac = f"{quantizado:.2f}".partition(".")
    inteiro_fmt = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro_fmt},{frac}"


def identificacao_uc_hub(identificacao: str, codigo_instalacao: int) -> str:
    ident = (identificacao or "").strip()
    if ident:
        return ident
    return str(codigo_instalacao).zfill(5)


def servico_item_ativo(item: dict[str, Any]) -> bool:
    if not item.get("ativo"):
        return False
    return _parse_valor_storage(item.get("valor")) > 0


def valor_uc_instalacao(instalacao: dict[str, Any]) -> Decimal:
    """Soma dos valores dos serviços ativos → pedido_instalacao_extra.valor."""
    total = Decimal("0")
    for item in instalacao.get("servicos") or []:
        if servico_item_ativo(item):
            total += _parse_valor_storage(item.get("valor"))
    return total.quantize(Decimal("0.01"))


def instalacao_tem_servico(instalacao: dict[str, Any]) -> bool:
    return valor_uc_instalacao(instalacao) > 0


def _valor_decimal_str(valor: Decimal) -> str:
    v = valor.quantize(Decimal("0.01"))
    if v <= 0:
        return ""
    if v == v.to_integral_value():
        return str(int(v))
    return str(v).rstrip("0").rstrip(".")


def compute_valor_uc_str(instalacao: dict[str, Any]) -> str:
    return _valor_decimal_str(valor_uc_instalacao(instalacao))


def build_observacoes_detalhes_hub(instalacoes: list[dict[str, Any]]) -> str:
    blocos: list[str] = []
    for inst in instalacoes:
        if not instalacao_tem_servico(inst):
            continue
        nomes: list[str] = []
        for item in inst.get("servicos") or []:
            if not servico_item_ativo(item):
                continue
            nomes.append(str(item.get("nome_pipe") or item.get("nome") or ""))
        if not nomes:
            continue
        ident = identificacao_uc_hub(
            str(inst.get("identificacao") or ""),
            int(inst.get("codigo_instalacao") or 0),
        )
        blocos.append(
            f"UC = {ident} - {' + '.join(nomes)} = {format_valor_br_hub(valor_uc_instalacao(inst))}"
        )
    return "; ".join(blocos)


def soma_valores_hub(instalacoes: list[dict[str, Any]]) -> Decimal:
    total = Decimal("0")
    for inst in instalacoes:
        total += valor_uc_instalacao(inst)
    return total.quantize(Decimal("0.01"))


def _merge_servicos_instalacao(
    existentes: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    por_chave = {str(s.get("chave")): s for s in (existentes or []) if s.get("chave")}
    merged: list[dict[str, Any]] = []
    for tmpl in servicos_template_hub():
        chave = tmpl["chave"]
        prev = por_chave.get(chave) or {}
        merged.append(
            {
                **tmpl,
                "ativo": bool(prev.get("ativo")),
                "valor": str(prev.get("valor") or ""),
            }
        )
    return merged


def _legacy_uc_linha_para_instalacao(
    linha: dict[str, Any], codigo_cliente: int
) -> dict[str, Any]:
    servicos_dict = linha.get("servicos") or {}
    servicos: list[dict[str, Any]] = []
    catalogo = servico_catalogo_por_chave()
    for chave, cat in catalogo.items():
        raw = servicos_dict.get(chave)
        if isinstance(raw, bool):
            celula = {"ativo": raw, "valor": ""}
        elif isinstance(raw, dict):
            celula = raw
        else:
            celula = {}
        servicos.append(
            {
                "codigo_servico": cat.codigo_servico,
                "chave": chave,
                "nome": cat.nome,
                "sigla": cat.sigla,
                "nome_pipe": cat.nome_pipe,
                "ativo": bool(celula.get("ativo")),
                "valor": str(celula.get("valor") or ""),
            }
        )
    inst = {
        "codigo_instalacao": int(linha.get("codigo_instalacao") or 0),
        "codigo_cliente": codigo_cliente,
        "identificacao": str(linha.get("identificacao") or ""),
        "razao_social": str(linha.get("razao_social") or ""),
        "cidade": str(linha.get("cidade") or ""),
        "uf": str(linha.get("uf") or ""),
        "servicos": servicos,
    }
    inst["valor_uc"] = compute_valor_uc_str(inst)
    return inst


def normalize_hub_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Garante hub.instalacoes[] (estrutura HUB); migra servicos.uc_linhas legado."""
    data = dict(payload or {})
    hub = dict(data.get("hub") or {})
    servicos = data.get("servicos") or {}

    if hub.get("instalacoes"):
        instalacoes = []
        for raw in hub["instalacoes"]:
            inst = dict(raw)
            inst["servicos"] = _merge_servicos_instalacao(inst.get("servicos"))
            inst["valor_uc"] = compute_valor_uc_str(inst)
            instalacoes.append(inst)
        hub["instalacoes"] = instalacoes
    elif servicos.get("uc_linhas"):
        from core.pipedrive_fields import parse_codigo_cliente_instalacao

        codigo_raw = str((data.get("cliente") or {}).get("codigo_cliente_instalacao") or "")
        try:
            codigo_cliente, _ = parse_codigo_cliente_instalacao(codigo_raw)
        except ValueError:
            codigo_cliente = 0
        hub["instalacoes"] = [
            _legacy_uc_linha_para_instalacao(linha, codigo_cliente)
            for linha in servicos["uc_linhas"]
        ]
    else:
        hub.setdefault("instalacoes", [])

    total = soma_valores_hub(hub["instalacoes"])
    hub["valor_total"] = _valor_decimal_str(total) or str(hub.get("valor_total") or "")
    hub["observacoes_detalhes"] = build_observacoes_detalhes_hub(hub["instalacoes"])
    data["hub"] = hub

    cliente = dict(data.get("cliente") or {})
    codigo_raw = str(cliente.get("codigo_cliente_instalacao") or "").strip()
    if codigo_raw and hub["instalacoes"]:
        from core.pipedrive_fields import (
            format_codigo_cliente_instalacao,
            parse_codigo_cliente_instalacao,
        )

        try:
            codigo_cliente, _ = parse_codigo_cliente_instalacao(codigo_raw)
        except ValueError:
            codigo_cliente = 0
        if codigo_cliente > 0:
            codigos = sorted(
                int(i["codigo_instalacao"])
                for i in hub["instalacoes"]
                if i.get("codigo_instalacao") and instalacao_tem_servico(i)
            )
            cliente["codigo_cliente_instalacao"] = format_codigo_cliente_instalacao(
                codigo_cliente, codigos
            )
            data["cliente"] = cliente

    return data


def merge_instalacoes_hub(
    payload: dict[str, Any],
    rows_instalacao: list[dict[str, Any]],
    codigo_cliente: int,
) -> dict[str, Any]:
    data = normalize_hub_payload(payload)
    prev = {
        int(i["codigo_instalacao"]): i
        for i in data.get("hub", {}).get("instalacoes", [])
        if i.get("codigo_instalacao")
    }
    instalacoes: list[dict[str, Any]] = []
    for row in rows_instalacao:
        codigo = int(row["codigo"])
        existente = prev.get(codigo)
        servicos = _merge_servicos_instalacao(
            existente.get("servicos") if existente else None
        )
        inst = {
            "codigo_instalacao": codigo,
            "codigo_cliente": codigo_cliente,
            "identificacao": str(row.get("identificacao") or ""),
            "razao_social": str(row.get("razao_social") or ""),
            "cidade": str(row.get("cidade") or ""),
            "uf": str(row.get("uf") or ""),
            "servicos": servicos,
        }
        inst["valor_uc"] = compute_valor_uc_str(inst)
        instalacoes.append(inst)

    data["hub"] = {
        **(data.get("hub") or {}),
        "instalacoes": instalacoes,
    }
    return apply_hub_instalacoes(data, instalacoes, codigo_cliente)


def apply_hub_instalacoes(
    payload: dict[str, Any],
    instalacoes: list[dict[str, Any]],
    codigo_cliente: int,
) -> dict[str, Any]:
    from core.pipedrive_fields import format_codigo_cliente_instalacao

    data = dict(payload)
    normalized: list[dict[str, Any]] = []
    for inst in instalacoes:
        row = dict(inst)
        row["servicos"] = _merge_servicos_instalacao(row.get("servicos"))
        row["valor_uc"] = compute_valor_uc_str(row)
        row["codigo_cliente"] = codigo_cliente
        normalized.append(row)

    codigos = sorted(
        i["codigo_instalacao"] for i in normalized if instalacao_tem_servico(i)
    )
    total = soma_valores_hub(normalized)
    cliente = dict(data.get("cliente") or {})
    cliente["codigo_cliente_instalacao"] = format_codigo_cliente_instalacao(
        codigo_cliente, codigos
    )
    data["cliente"] = cliente
    data["hub"] = {
        **(data.get("hub") or {}),
        "instalacoes": normalized,
        "observacoes_detalhes": build_observacoes_detalhes_hub(normalized),
        "valor_total": _valor_decimal_str(total),
    }
    return data
