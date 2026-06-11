"""Catálogo HUB — pedido_nome_servico (MySQL gebras)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from core.hub_pedido import hub_conn


@dataclass(frozen=True)
class ServicoHubCatalogo:
    codigo_servico: int
    chave: str
    nome: str
    sigla: str
    nome_pipe: str
    ordem_form: int


# Mapeamento estável form ↔ pedido_nome_servico (códigos 1–6 no HUB).
_CHAVE_POR_CODIGO: dict[int, tuple[str, str, int]] = {
    1: ("sole_consultoria", "Sole Consultoria", 2),
    2: ("sole_web", "SOLE WEB", 1),
    3: ("gestao_usina_fotovoltaica", "Gestão de Usina Fotovoltaica", 4),
    4: ("gestao_acl", "ACL", 3),
    6: ("gestao_qualidade_energia", "Gestão de Qualidade de Energia", 5),
}


def _row_para_servico(row: tuple) -> ServicoHubCatalogo | None:
    codigo, nome, _descricao, sigla = row[0], row[1], row[2], row[3] or ""
    mapping = _CHAVE_POR_CODIGO.get(int(codigo))
    if not mapping:
        return None
    chave, nome_pipe, ordem = mapping
    return ServicoHubCatalogo(
        codigo_servico=int(codigo),
        chave=chave,
        nome=str(nome or ""),
        sigla=str(sigla),
        nome_pipe=nome_pipe,
        ordem_form=ordem,
    )


@lru_cache(maxsize=1)
def listar_servicos_hub_catalogo() -> tuple[ServicoHubCatalogo, ...]:
    """Lê pedido_nome_servico; fallback estático se MySQL indisponível."""
    try:
        with hub_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT codigo, nome, descricao, sigla
                    FROM pedido_nome_servico
                    WHERE codigo > 0
                    ORDER BY codigo
                    """
                )
                rows = cur.fetchall()
        catalogo = [s for row in rows if (s := _row_para_servico(row))]
    except Exception:
        catalogo = [
            ServicoHubCatalogo(1, "sole_consultoria", "SOLE Consultoria", "SC", "Sole Consultoria", 2),
            ServicoHubCatalogo(2, "sole_web", "SOLE Web (com telemetria)", "SW", "SOLE WEB", 1),
            ServicoHubCatalogo(4, "gestao_acl", "Gestão Mercado Livre", "GML", "ACL", 3),
            ServicoHubCatalogo(
                3, "gestao_usina_fotovoltaica", "Gestão de Usina Fotovoltaica", "GUF",
                "Gestão de Usina Fotovoltaica", 4,
            ),
            ServicoHubCatalogo(
                6, "gestao_qualidade_energia", "Gestão de Qualidade de Energia", "GQE",
                "Gestão de Qualidade de Energia", 5,
            ),
        ]
    return tuple(sorted(catalogo, key=lambda s: s.ordem_form))


def servico_catalogo_por_chave() -> dict[str, ServicoHubCatalogo]:
    return {s.chave: s for s in listar_servicos_hub_catalogo()}


def servico_item_vazio(catalogo: ServicoHubCatalogo) -> dict[str, Any]:
    return {
        "codigo_servico": catalogo.codigo_servico,
        "chave": catalogo.chave,
        "nome": catalogo.nome,
        "sigla": catalogo.sigla,
        "nome_pipe": catalogo.nome_pipe,
        "ativo": False,
        "valor": "",
    }


def servicos_template_hub() -> list[dict[str, Any]]:
    return [servico_item_vazio(s) for s in listar_servicos_hub_catalogo()]
