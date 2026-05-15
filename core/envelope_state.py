import json
import os
import re
from datetime import datetime, timezone

from .config import ARQUIVO_ENVELOPES_PENDENTES, ARQUIVO_PEDIDOS_PLUNE_CRIADOS


def _load_envelopes() -> list:
    if not os.path.exists(ARQUIVO_ENVELOPES_PENDENTES):
        return []
    with open(ARQUIVO_ENVELOPES_PENDENTES, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []


def _save_envelopes(records: list) -> None:
    pasta_estado = os.path.dirname(ARQUIVO_ENVELOPES_PENDENTES)
    if pasta_estado:
        os.makedirs(pasta_estado, exist_ok=True)
    with open(ARQUIVO_ENVELOPES_PENDENTES, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def salvar_envelope_pendente(deal_id: str, envelope_id: str, envelope_name: str) -> None:
    records = _load_envelopes()
    deal_id = str(deal_id)
    records = [r for r in records if str(r.get("deal_id")) != deal_id]
    records.append(
        {
            "deal_id": deal_id,
            "envelope_id": envelope_id,
            "envelope_name": envelope_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pedido_plune_criado": False,
        }
    )
    _save_envelopes(records)


def buscar_por_envelope_id(envelope_id: str) -> dict | None:
    for record in _load_envelopes():
        if record.get("envelope_id") == envelope_id:
            return record
    return None


def buscar_por_deal_id(deal_id: str) -> dict | None:
    deal_id = str(deal_id)
    for record in _load_envelopes():
        if str(record.get("deal_id")) == deal_id:
            return record
    return None


def marcar_pedido_criado(deal_id: str, pedido_id: str | None = None) -> None:
    records = _load_envelopes()
    deal_id = str(deal_id)
    for record in records:
        if str(record.get("deal_id")) == deal_id:
            record["pedido_plune_criado"] = True
            if pedido_id is not None:
                record["pedido_plune_id"] = str(pedido_id)
    _save_envelopes(records)


def extrair_deal_id_do_nome_envelope(envelope_name: str) -> str | None:
    if not envelope_name:
        return None
    match = re.search(r"Contrato Deal (\d+)", envelope_name)
    return match.group(1) if match else None


def carregar_pedidos_plune_criados() -> set:
    if not os.path.exists(ARQUIVO_PEDIDOS_PLUNE_CRIADOS):
        return set()
    with open(ARQUIVO_PEDIDOS_PLUNE_CRIADOS, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def salvar_pedido_plune_criado(deal_id: str) -> None:
    deal_id = str(deal_id)
    criados = carregar_pedidos_plune_criados()
    if deal_id in criados:
        return
    pasta_estado = os.path.dirname(ARQUIVO_PEDIDOS_PLUNE_CRIADOS)
    if pasta_estado:
        os.makedirs(pasta_estado, exist_ok=True)
    with open(ARQUIVO_PEDIDOS_PLUNE_CRIADOS, "a", encoding="utf-8") as f:
        f.write(f"{deal_id}\n")


def listar_aguardando_pedido_plune() -> list:
    """Envelopes enviados ao Clicksign cujo pedido Plune ainda não foi criado."""
    return [
        r
        for r in _load_envelopes()
        if not r.get("pedido_plune_criado")
        and str(r.get("deal_id")) not in carregar_pedidos_plune_criados()
    ]
