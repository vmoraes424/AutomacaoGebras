from __future__ import annotations

from typing import Any, Callable


def _default_lookup() -> list[dict[str, Any]]:
    from core.hub_catalogo import listar_servicos_hub_catalogo

    return [
        {
            "codigo_servico": s.codigo_servico,
            "chave": s.chave,
            "nome": s.nome,
            "sigla": s.sigla,
            "nome_pipe": s.nome_pipe,
            "ordem_form": s.ordem_form,
        }
        for s in listar_servicos_hub_catalogo()
    ]


class ListHubServicos:
    """Catálogo pedido_nome_servico para colunas da matriz UC × serviço."""

    def __init__(self, lookup: Callable[[], list[dict[str, Any]]] | None = None) -> None:
        self._lookup = lookup or _default_lookup

    def execute(self) -> dict[str, Any]:
        servicos = self._lookup()
        return {"servicos": servicos}
