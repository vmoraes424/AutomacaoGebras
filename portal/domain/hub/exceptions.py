from __future__ import annotations


class HubDomainError(Exception):
    """Erro base do contexto HUB (leitura instalações)."""


class HubValidationError(HubDomainError):
    pass


class HubReadError(HubDomainError):
    pass
