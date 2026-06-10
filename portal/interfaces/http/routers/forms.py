from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from portal.composition import PortalContainer
from portal.domain.formulario.exceptions import (
    DealFormNotEditableError,
    DealFormNotFoundError,
)
from portal.interfaces.http.dependencies import container
from portal.interfaces.http.schemas.forms import FormDraftIn, FormRecordOut, FormSubmitIn

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
