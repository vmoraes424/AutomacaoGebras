"""Regra: formulário e automação só para deal aberto na etapa Contrato."""

from __future__ import annotations

from core.form_pipe_sync import fetch_deal_for_form
from core.pipedrive_stages import deal_elegivel_formulario_contrato
from portal.domain.formulario.exceptions import (
    DealFormNotFoundError,
    DealNotInContratoStageError,
)


def fetch_deal_eligible_for_form(deal_id: int) -> dict:
    deal = fetch_deal_for_form(deal_id)
    if not deal:
        raise DealFormNotFoundError(deal_id)
    if not deal_elegivel_formulario_contrato(deal):
        raise DealNotInContratoStageError(deal_id)
    return deal
