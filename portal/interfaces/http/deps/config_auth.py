"""Senha opcional para rotas /config/automacao (PORTAL_CONFIG_PASSWORD no .env)."""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException

from portal.settings import portal_config_password


def require_config_password(
    x_portal_config_password: str | None = Header(default=None, alias="X-Portal-Config-Password"),
) -> None:
    expected = portal_config_password()
    if not expected:
        return
    provided = (x_portal_config_password or "").strip()
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Senha de configuração inválida ou ausente")
