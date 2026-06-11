from __future__ import annotations

from fastapi import APIRouter

from core.config import FORMULARIO_WEB_ENABLED
from portal.settings import portal_api_token

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "portal",
        "version": "0.3.0",
        "auth_required": bool(portal_api_token()),
        "formulario_web_enabled": FORMULARIO_WEB_ENABLED,
    }
