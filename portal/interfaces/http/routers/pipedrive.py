from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from portal.composition import PortalContainer
from portal.domain.crm.exceptions import CrmReadError
from portal.interfaces.http.dependencies import container
from portal.interfaces.http.schemas.pipedrive import PipedriveDealSummary, PipedriveUserOut

router = APIRouter(prefix="/pipedrive", tags=["pipedrive"])


@router.get("/users", response_model=list[PipedriveUserOut])
def list_users(
    c: PortalContainer = Depends(container),
    x_portal_fresh: str | None = Header(default=None, alias="X-Portal-Fresh"),
) -> list[dict]:
    try:
        fresh = x_portal_fresh == "1"
        return [user.to_dict() for user in c.list_crm_users.execute(fresh=fresh)]
    except CrmReadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/deals", response_model=list[PipedriveDealSummary])
def list_deals(
    owner_user_id: int | None = Query(default=None, description="ID do dono do card"),
    c: PortalContainer = Depends(container),
    x_portal_fresh: str | None = Header(default=None, alias="X-Portal-Fresh"),
) -> list[dict]:
    try:
        fresh = x_portal_fresh == "1"
        return c.list_deals_enriched.execute(owner_user_id=owner_user_id, fresh=fresh)
    except CrmReadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
