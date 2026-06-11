from __future__ import annotations

from fastapi import APIRouter

from core.automacao_config import get_automacao_config
from portal.settings import portal_api_token

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "portal",
        "version": "0.3.0",
        "auth_required": bool(portal_api_token()),
        "formulario_web_enabled": get_automacao_config().formulario_web_enabled,
    }
