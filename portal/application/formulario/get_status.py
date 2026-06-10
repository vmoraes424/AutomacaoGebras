from __future__ import annotations

from typing import Any

class GetDealFormStatus:
    def __init__(self, get_form) -> None:
        self._get_form = get_form

    def execute(
        self,
        deal_id: int,
        *,
        owner_user_id: int | None = None,
        owner_name: str = "",
        deal_title: str = "",
    ) -> dict[str, Any]:
        return self._get_form.execute(
            deal_id,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
        ).status_snapshot()
