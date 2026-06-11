from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from core.form_pipe_sync import PipeSyncError
from portal.composition import PortalContainer
from portal.domain.formulario.exceptions import (
    DealFormNotEditableError,
    DealFormNotFoundError,
    DealNotInContratoStageError,
)
from portal.interfaces.http.dependencies import container
from portal.interfaces.http.schemas.forms import (
    FormDraftIn,
    FormRecordOut,
    FormSubmitIn,
    FormSyncFieldIn,
)

router = APIRouter(prefix="/forms", tags=["forms"])


@router.get("/{deal_id}", response_model=FormRecordOut)
def get_form(
    deal_id: int,
    owner_user_id: int | None = None,
    owner_name: str = "",
    deal_title: str = "",
    c: PortalContainer = Depends(container),
) -> dict:
    try:
        return c.open_deal_form.execute(
            deal_id,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
        ).to_record()
    except DealFormNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{deal_id}/status")
def get_form_status(
    deal_id: int,
    owner_user_id: int | None = None,
    owner_name: str = "",
    deal_title: str = "",
    c: PortalContainer = Depends(container),
) -> dict:
    try:
        return c.get_deal_form_status.execute(
            deal_id,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
        )
    except DealFormNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.put("/{deal_id}/draft", response_model=FormRecordOut)
def save_draft(
    deal_id: int,
    body: FormDraftIn,
    c: PortalContainer = Depends(container),
) -> dict:
    try:
        form = c.save_deal_form_draft.execute(
            deal_id,
            payload=body.payload,
            schema_version=body.schema_version,
            owner_user_id=body.owner_user_id,
            owner_name=body.owner_name,
            deal_title=body.deal_title,
        )
        return form.to_record()
    except DealFormNotEditableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{deal_id}/sync-pipedrive")
def sync_pipedrive(
    deal_id: int,
    body: FormDraftIn,
    c: PortalContainer = Depends(container),
) -> dict:
    """PATCH de todos os campos migrados no deal Pipedrive (sem enviar formulário)."""
    try:
        return c.sync_deal_form_to_pipedrive.execute(
            deal_id,
            payload=body.payload,
        )
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PipeSyncError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/{deal_id}/sync-field")
def sync_field_pipedrive(
    deal_id: int,
    body: FormSyncFieldIn,
    background_tasks: BackgroundTasks,
    c: PortalContainer = Depends(container),
) -> dict:
    """PATCH de um campo migrado no deal Pipedrive (blur do input)."""
    try:
        result = c.sync_deal_form_field_to_pipedrive.sync_field(
            deal_id,
            field_path=body.field_path,
            value=body.value,
        )
        background_tasks.add_task(
            c.sync_deal_form_field_to_pipedrive.persist_draft_field,
            deal_id,
            field_path=body.field_path,
            value=body.value,
            schema_version=body.schema_version,
            owner_user_id=body.owner_user_id,
            owner_name=body.owner_name,
            deal_title=body.deal_title,
        )
        return result
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PipeSyncError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/{deal_id}/submit", response_model=FormRecordOut)
def submit_form(
    deal_id: int,
    body: FormSubmitIn,
    c: PortalContainer = Depends(container),
) -> dict:
    try:
        form = c.submit_deal_form.execute(
            deal_id,
            payload=body.payload,
            schema_version=body.schema_version,
            owner_user_id=body.owner_user_id,
            owner_name=body.owner_name,
            deal_title=body.deal_title,
        )
        return form.to_record()
    except DealFormNotEditableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DealNotInContratoStageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
