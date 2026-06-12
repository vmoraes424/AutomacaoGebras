from __future__ import annotations

from typing import Any, Callable


def _default_lookup() -> dict[str, list[dict[str, Any]]]:
    from core.form_schema_v1 import list_form_enum_field_options

    return list_form_enum_field_options()


class ListPipedriveDealFieldOptions:
    """Opções dos campos enum do formulário (dealFields v2)."""

    def __init__(
        self,
        lookup: Callable[[], dict[str, list[dict[str, Any]]]] | None = None,
    ) -> None:
        self._lookup = lookup or _default_lookup

    def execute(self) -> dict[str, Any]:
        return {"fields": self._lookup()}
