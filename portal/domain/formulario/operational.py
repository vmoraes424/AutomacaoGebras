"""Rótulos operacionais do fluxo portal (Fase 6)."""

from __future__ import annotations

from enum import StrEnum

from portal.domain.formulario.value_objects import FormStatus


class OperationalLabel(StrEnum):
    PENDENTE = "pendente"
    RASCUNHO = "rascunho"
    ERRO = "erro"
    ENVIADO = "enviado"
    PROCESSANDO = "processando"
    PROCESSADO = "processado"


# Etapa Pipe listada no portal (ver core/gebras_defaults.PIPEDRIVE_STAGE_CONTRATO_NOME)
PORTAL_STAGE_NAME = "Contrato"


def operational_label(form_status: str | None) -> OperationalLabel:
    if not form_status:
        return OperationalLabel.PENDENTE
    try:
        status = FormStatus(form_status)
    except ValueError:
        return OperationalLabel.PENDENTE
    if status == FormStatus.DRAFT:
        return OperationalLabel.RASCUNHO
    if status == FormStatus.ERROR:
        return OperationalLabel.ERRO
    if status in (FormStatus.VALIDATED, FormStatus.SUBMITTED):
        return OperationalLabel.ENVIADO
    if status == FormStatus.PROCESSING:
        return OperationalLabel.PROCESSANDO
    if status == FormStatus.PROCESSED:
        return OperationalLabel.PROCESSADO
    return OperationalLabel.PENDENTE


def is_ready_for_form(*, deal_status: str = "open") -> bool:
    """Card aberto na etapa Contrato (já filtrado na listagem)."""
    return deal_status == "open"


def is_ready_for_automation(form_status: str | None) -> bool:
    """Worker processa com FORMULARIO_WEB_ENABLED quando form está validated+."""
    if not form_status:
        return False
    try:
        status = FormStatus(form_status)
    except ValueError:
        return False
    return status in (
        FormStatus.VALIDATED,
        FormStatus.SUBMITTED,
        FormStatus.PROCESSING,
        FormStatus.PROCESSED,
    )
