"""Configuração do portal (variáveis de ambiente específicas da API)."""

from __future__ import annotations

import os


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_bool(key: str, default: bool = False) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "sim", "on")


def portal_api_token() -> str:
    """Token opcional: vazio = sem autenticação; preenchido = exige header."""
    return _env("PORTAL_API_TOKEN")


def portal_config_password() -> str:
    """Senha opcional para /config/automacao; vazio = tela aberta sem gate."""
    return _env("PORTAL_CONFIG_PASSWORD")


def portal_deal_form_repository() -> str:
    return _env("PORTAL_DEAL_FORM_REPOSITORY", "mysql")


def portal_structured_logs_enabled() -> bool:
    return _env_bool("PORTAL_STRUCTURED_LOGS", True)
