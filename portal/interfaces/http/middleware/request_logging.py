"""Middleware de log estruturado por requisição HTTP."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from portal.infrastructure.structured_logging import configure_portal_logging, log_event
from portal.settings import portal_structured_logs_enabled

_logger = configure_portal_logging(enabled=portal_structured_logs_enabled())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        if portal_structured_logs_enabled():
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            log_event(
                _logger,
                "http_request",
                event="http_request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
        return response
