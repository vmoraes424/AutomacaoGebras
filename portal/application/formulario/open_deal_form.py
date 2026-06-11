from __future__ import annotations

from typing import Callable

from portal.application.formulario.deal_eligibility import fetch_deal_eligible_for_form
from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.exceptions import DealFormNotFoundError
from portal.domain.formulario.repositories import DealFormRepository

DealFetcher = Callable[[int], dict | None]
DealToForm = Callable[[dict], dict]
FormHydrator = Callable[[dict, dict], dict]


class OpenDealForm:
    """
    Abre o formulário do deal: rascunho salvo ou bootstrap a partir do Pipedrive.

    Campos mapeados no rascunho são atualizados com valores atuais do Pipe ao abrir.
    """

    def __init__(
        self,
        repository: DealFormRepository,
        *,
        fetch_deal: DealFetcher | None = None,
        deal_to_form: DealToForm,
        hydrate: FormHydrator,
    ) -> None:
        self._repository = repository
        self._fetch_deal = fetch_deal
        self._deal_to_form = deal_to_form
        self._hydrate = hydrate

    def execute(
        self,
        deal_id: int,
        *,
        owner_user_id: int | None = None,
        owner_name: str = "",
        deal_title: str = "",
        schema_version: str = "v1",
    ) -> DealForm:
        existing = self._repository.get_by_deal_id(deal_id, schema_version=schema_version)
        if existing is not None and not existing.status.is_editable():
            return existing

        if existing is not None:
            from core.form_pipe_sync import fetch_deal_for_form

            fetch_pipe = self._fetch_deal or fetch_deal_for_form
            deal_pipe = fetch_pipe(deal_id)
            if not deal_pipe:
                return existing
            pipe_payload = self._deal_to_form(deal_pipe)
            if existing.status.is_editable():
                hydrated = self._hydrate(existing.payload, pipe_payload)
                if hydrated != existing.payload:
                    return self._repository.save_draft(
                        deal_id,
                        payload=hydrated,
                        schema_version=schema_version,
                        owner_user_id=existing.owner_user_id or owner_user_id,
                        owner_name=existing.owner_name or owner_name,
                        deal_title=existing.deal_title or deal_title,
                    )
            return existing

        fetch = self._fetch_deal or fetch_deal_eligible_for_form
        deal_pipe = fetch(deal_id)
        if not deal_pipe:
            raise DealFormNotFoundError(deal_id)

        pipe_payload = self._deal_to_form(deal_pipe)
        return self._repository.save_draft(
            deal_id,
            payload=pipe_payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title or str(deal_pipe.get("title") or ""),
        )
