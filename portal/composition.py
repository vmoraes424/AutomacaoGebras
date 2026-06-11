"""Composition root — monta casos de uso e adapters (DI manual)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from portal.application.crm.list_deals_contrato import ListDealsContrato
from portal.application.crm.list_deals_enriched import ListDealsContratoEnriched
from portal.application.crm.list_users import ListCrmUsers
from portal.application.hub.list_instalacoes import ListHubInstalacoes
from portal.application.hub.list_servicos import ListHubServicos
from portal.application.formulario.get_deal_form import GetDealForm
from portal.application.formulario.get_status import GetDealFormStatus
from portal.application.formulario.open_deal_form import OpenDealForm
from portal.application.formulario.save_draft import SaveDealFormDraft
from portal.application.formulario.submit import SubmitDealForm
from portal.application.formulario.sync_pipedrive import (
    SyncDealFormFieldToPipedrive,
    SyncDealFormToPipedrive,
)
from portal.domain.formulario.repositories import DealFormRepository
from portal.infrastructure.persistence.memory_deal_form_repository import (
    MemoryDealFormRepository,
)
from portal.infrastructure.persistence.mysql_deal_form_repository import (
    MysqlDealFormRepository,
)
from portal.infrastructure.pipedrive.pipedrive_crm_reader import PipedriveCrmReader

from core.form_pipe_sync import (
    deal_to_form_payload_v1,
    overlay_pipe_mapped_fields_from_pipe,
)
from core.form_validation_v1 import validate_form_payload_v1


def build_deal_form_repository() -> DealFormRepository:
    backend = os.environ.get("PORTAL_DEAL_FORM_REPOSITORY", "mysql").strip().lower()
    if backend == "memory":
        return MemoryDealFormRepository()
    return MysqlDealFormRepository()


@dataclass
class PortalContainer:
    deal_form_repository: DealFormRepository
    crm_reader: PipedriveCrmReader
    get_deal_form: GetDealForm
    open_deal_form: OpenDealForm
    save_deal_form_draft: SaveDealFormDraft
    submit_deal_form: SubmitDealForm
    sync_deal_form_to_pipedrive: SyncDealFormToPipedrive
    sync_deal_form_field_to_pipedrive: SyncDealFormFieldToPipedrive
    get_deal_form_status: GetDealFormStatus
    list_crm_users: ListCrmUsers
    list_deals_contrato: ListDealsContrato
    list_deals_enriched: ListDealsContratoEnriched
    list_hub_instalacoes: ListHubInstalacoes
    list_hub_servicos: ListHubServicos

    def reset_for_tests(self) -> None:
        repo = self.deal_form_repository
        if isinstance(repo, MemoryDealFormRepository):
            repo.clear()


def build_container() -> PortalContainer:
    deal_form_repository = build_deal_form_repository()
    crm_reader = PipedriveCrmReader()
    get_deal_form = GetDealForm(deal_form_repository)
    open_deal_form = OpenDealForm(
        deal_form_repository,
        fetch_deal=None,
        deal_to_form=deal_to_form_payload_v1,
        hydrate=overlay_pipe_mapped_fields_from_pipe,
    )
    return PortalContainer(
        deal_form_repository=deal_form_repository,
        crm_reader=crm_reader,
        get_deal_form=get_deal_form,
        open_deal_form=open_deal_form,
        save_deal_form_draft=SaveDealFormDraft(deal_form_repository),
        submit_deal_form=SubmitDealForm(
            deal_form_repository,
            validator=validate_form_payload_v1,
        ),
        sync_deal_form_to_pipedrive=SyncDealFormToPipedrive(),
        sync_deal_form_field_to_pipedrive=SyncDealFormFieldToPipedrive(deal_form_repository),
        get_deal_form_status=GetDealFormStatus(open_deal_form),
        list_crm_users=ListCrmUsers(crm_reader),
        list_deals_contrato=ListDealsContrato(crm_reader),
        list_deals_enriched=ListDealsContratoEnriched(
            ListDealsContrato(crm_reader),
            deal_form_repository,
        ),
        list_hub_instalacoes=ListHubInstalacoes(),
        list_hub_servicos=ListHubServicos(),
    )


_container: PortalContainer | None = None


def get_container() -> PortalContainer:
    global _container
    if _container is None:
        _container = build_container()
    return _container


def reset_container() -> None:
    """Recria o container (testes)."""
    global _container
    _container = build_container()
