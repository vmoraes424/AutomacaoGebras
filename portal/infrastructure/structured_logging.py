"""Logging estruturado (JSON) para o portal."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_portal_logging(*, enabled: bool = True) -> logging.Logger:
    """Configura logger raiz do portal uma única vez."""
    logger = logging.getLogger("portal")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    if enabled:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, message: str, **fields: Any) -> None:
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "(portal)",
        0,
        message,
        (),
        None,
    )
    record.extra_fields = fields  # type: ignore[attr-defined]
    logger.handle(record)
