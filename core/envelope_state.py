"""
Estado de envelopes e pedidos Plune — persistido em MySQL (core.database).

Mantém API compatível com o restante do projeto.
"""

import re

from .database import (
    buscar_por_deal_id,
    buscar_por_envelope_id,
    carregar_pedidos_plune_criados,
    listar_aguardando_pedido_plune,
    marcar_pedido_criado,
    marcar_pedidos_aprovados,
    limpar_template_local_envelope,
    salvar_envelope_pendente,
    salvar_pedido_plune_key,
)

# Compat: nome antigo do parâmetro (chave PedidoIntegracao, não deal_id)
salvar_pedido_plune_criado = salvar_pedido_plune_key


def extrair_deal_id_do_nome_envelope(envelope_name: str) -> str | None:
    if not envelope_name:
        return None
    match = re.search(r"Contrato Deal (\d+)", envelope_name)
    return match.group(1) if match else None


__all__ = [
    "buscar_por_deal_id",
    "buscar_por_envelope_id",
    "carregar_pedidos_plune_criados",
    "extrair_deal_id_do_nome_envelope",
    "listar_aguardando_pedido_plune",
    "marcar_pedido_criado",
    "marcar_pedidos_aprovados",
    "limpar_template_local_envelope",
    "salvar_envelope_pendente",
    "salvar_pedido_plune_criado",
    "salvar_pedido_plune_key",
]
