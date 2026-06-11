from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from portal.composition import PortalContainer
from portal.domain.hub.exceptions import HubReadError, HubValidationError
from portal.interfaces.http.dependencies import container
from portal.interfaces.http.schemas.hub import HubInstalacoesOut, HubServicosOut

router = APIRouter(prefix="/hub", tags=["hub"])


@router.get("/servicos", response_model=HubServicosOut)
def list_servicos(c: PortalContainer = Depends(container)) -> dict:
    return c.list_hub_servicos.execute()


@router.get("/instalacoes", response_model=HubInstalacoesOut)
def list_instalacoes(
    codigo_cliente_instalacao: str = Query(
        ...,
        min_length=1,
        description=(
            "Mesmo formato do campo Pipedrive: «352» ou «352/1234,3456». "
            "No Pipe o valor continua sendo enviado neste formato."
        ),
    ),
    c: PortalContainer = Depends(container),
) -> dict:
    try:
        return c.list_hub_instalacoes.execute(codigo_cliente_instalacao.strip())
    except HubValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HubReadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
