from __future__ import annotations

from typing import Any, Callable

HubInstalacoesLookup = Callable[[str], Any]


def _default_lookup(codigo_cliente_instalacao: str) -> Any:
    from core.hub_instalacoes import consultar_instalacoes_hub

    return consultar_instalacoes_hub(codigo_cliente_instalacao)


class ListHubInstalacoes:
    """Lista instalações HUB para o código cliente do formulário."""

    def __init__(self, lookup: HubInstalacoesLookup | None = None) -> None:
        self._lookup = lookup or _default_lookup

    def execute(self, codigo_cliente_instalacao: str) -> dict[str, Any]:
        from core.hub_instalacoes import HubInstalacoesError, HubInstalacoesReadError
        from portal.domain.hub.exceptions import HubReadError, HubValidationError

        try:
            return self._lookup(codigo_cliente_instalacao).to_dict()
        except HubInstalacoesError as exc:
            raise HubValidationError(str(exc)) from exc
        except HubInstalacoesReadError as exc:
            raise HubReadError(str(exc)) from exc
