from __future__ import annotations


class CrmDomainError(Exception):
    """Erro base do contexto CRM (leitura Pipe)."""


class CrmReadError(CrmDomainError):
    pass
