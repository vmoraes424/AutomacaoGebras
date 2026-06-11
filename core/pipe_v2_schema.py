"""Validação de custom_fields para PATCH Pipedrive API v2."""

from __future__ import annotations

import re
from typing import Any

from core.pipedrive_fields import (
    DEFAULT_PIPE_CURRENCY,
    PIPE_FIELDS_ADDRESS,
    PIPE_FIELDS_DATE,
    PIPE_FIELDS_ENUM,
    PIPE_FIELDS_MONETARY,
    PIPE_FIELDS_NUMERIC,
    PIPE_FIELDS_SET,
)

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class PipeV2SchemaError(ValueError):
    """Valor incompatível com o schema v2 do Pipedrive."""


def validate_pipe_custom_field(
    pipe_hash: str,
    value: Any,
    *,
    field_path: str = "",
) -> None:
    """Garante tipo/estrutura aceitos pelo PATCH v2 (evita 400 na API)."""
    label = field_path or pipe_hash

    if pipe_hash in PIPE_FIELDS_ADDRESS:
        if not isinstance(value, dict):
            raise PipeV2SchemaError(
                f"{label}: campo address deve ser objeto {{'value': str}}, recebeu {type(value).__name__}"
            )
        if "value" not in value or not isinstance(value["value"], str):
            raise PipeV2SchemaError(f"{label}: address.value deve ser string")
        return

    if pipe_hash in PIPE_FIELDS_SET:
        if not isinstance(value, list):
            raise PipeV2SchemaError(
                f"{label}: campo set deve ser lista de int, recebeu {type(value).__name__}"
            )
        if not value or not all(type(x) is int for x in value):
            raise PipeV2SchemaError(f"{label}: set deve ser lista não vazia de int")
        return

    if pipe_hash in PIPE_FIELDS_ENUM:
        if type(value) is not int:
            raise PipeV2SchemaError(
                f"{label}: campo enum deve ser int (option_id), recebeu {type(value).__name__}"
            )
        return

    if pipe_hash in PIPE_FIELDS_MONETARY:
        if not isinstance(value, dict):
            raise PipeV2SchemaError(
                f"{label}: campo monetary deve ser objeto, recebeu {type(value).__name__}"
            )
        raw = value.get("value")
        if not isinstance(raw, (int, float)):
            raise PipeV2SchemaError(f"{label}: monetary.value deve ser número")
        if value.get("currency") != DEFAULT_PIPE_CURRENCY:
            raise PipeV2SchemaError(
                f"{label}: monetary.currency deve ser {DEFAULT_PIPE_CURRENCY!r}"
            )
        return

    if pipe_hash in PIPE_FIELDS_NUMERIC:
        if type(value) is not int:
            raise PipeV2SchemaError(
                f"{label}: campo numérico deve ser int, recebeu {type(value).__name__} ({value!r})"
            )
        return

    if pipe_hash in PIPE_FIELDS_DATE:
        if not isinstance(value, str) or not _ISO_DATE.match(value):
            raise PipeV2SchemaError(
                f"{label}: campo date deve ser string ISO YYYY-MM-DD, recebeu {value!r}"
            )
        return

    if not isinstance(value, str):
        raise PipeV2SchemaError(
            f"{label}: campo texto deve ser string, recebeu {type(value).__name__}"
        )


def validate_pipe_custom_fields(
    custom_fields: dict[str, Any],
    *,
    path_by_hash: dict[str, str] | None = None,
) -> None:
    for pipe_hash, value in custom_fields.items():
        validate_pipe_custom_field(
            pipe_hash,
            value,
            field_path=(path_by_hash or {}).get(pipe_hash, ""),
        )
