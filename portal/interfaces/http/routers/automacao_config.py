from __future__ import annotations

from fastapi import APIRouter, Depends

from core.automacao_config import (
    AutomacaoConfig,
    apply_automacao_preset,
    get_automacao_config,
    mysql_database_name,
    save_automacao_config,
)
from portal.interfaces.http.deps.config_auth import require_config_password
from portal.interfaces.http.schemas.automacao_config import (
    AutomacaoConfigBody,
    AutomacaoConfigResponse,
    ConfigAccessResponse,
)
from portal.settings import portal_config_password

router = APIRouter(prefix="/config", tags=["config"])


def _to_response(cfg: AutomacaoConfig) -> AutomacaoConfigResponse:
    return AutomacaoConfigResponse(
        **cfg.to_dict(),
        updated_at=cfg.updated_at,
        mysql_database=mysql_database_name(),
    )


@router.get("/automacao/access", response_model=ConfigAccessResponse)
def get_config_access() -> ConfigAccessResponse:
    return ConfigAccessResponse(password_required=bool(portal_config_password()))


@router.get(
    "/automacao",
    response_model=AutomacaoConfigResponse,
    dependencies=[Depends(require_config_password)],
)
def get_config_automacao() -> AutomacaoConfigResponse:
    return _to_response(get_automacao_config())


@router.put(
    "/automacao",
    response_model=AutomacaoConfigResponse,
    dependencies=[Depends(require_config_password)],
)
def update_config_automacao(body: AutomacaoConfigBody) -> AutomacaoConfigResponse:
    cfg = save_automacao_config(AutomacaoConfig.from_dict(body.model_dump()))
    return _to_response(cfg)


@router.post(
    "/automacao/preset/dev",
    response_model=AutomacaoConfigResponse,
    dependencies=[Depends(require_config_password)],
)
def apply_dev_preset() -> AutomacaoConfigResponse:
    return _to_response(apply_automacao_preset("dev"))


@router.post(
    "/automacao/preset/prod",
    response_model=AutomacaoConfigResponse,
    dependencies=[Depends(require_config_password)],
)
def apply_prod_preset() -> AutomacaoConfigResponse:
    return _to_response(apply_automacao_preset("prod"))
