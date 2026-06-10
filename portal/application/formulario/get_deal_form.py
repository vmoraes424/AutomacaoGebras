from __future__ import annotations

from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.exceptions import DealFormNotFoundError
from portal.domain.formulario.repositories import DealFormRepository


class GetDealForm:
    def __init__(self, repository: DealFormRepository) -> None:
        self._repository = repository

    def execute(self, deal_id: int) -> DealForm:
        form = self._repository.get_by_deal_id(deal_id)
        if form is None:
            raise DealFormNotFoundError(deal_id)
        return form
