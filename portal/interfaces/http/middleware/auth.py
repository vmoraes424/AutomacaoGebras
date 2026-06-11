"""Proteção mínima por token (Fase 7)."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from portal.settings import portal_api_token

_PUBLIC_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})


def _extract_token(request: Request) -> str | None:
    header = request.headers.get("X-Portal-Token", "").strip()
    if header:
        return header
    auth = request.headers.get("Authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


class PortalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token_required = portal_api_token()
        if not token_required:
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)
        token = _extract_token(request)
        if token != token_required:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token do portal ausente ou inválido"},
            )
        return await call_next(request)
