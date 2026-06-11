"""Fase 6 — rótulos operacionais e listagem enriquecida."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from portal.application.crm.list_deals_contrato import ListDealsContrato
from portal.application.crm.list_deals_enriched import ListDealsContratoEnriched
from portal.composition import reset_container
from portal.domain.crm.entities import CrmDeal
from portal.domain.formulario.operational import (
    OperationalLabel,
    is_ready_for_automation,
    is_ready_for_form,
    operational_label,
)
from portal.domain.formulario.value_objects import FormStatus
from portal.infrastructure.persistence.memory_deal_form_repository import (
    MemoryDealFormRepository,
)
from portal.main import create_app


class TestOperationalLabels:
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (None, OperationalLabel.PENDENTE),
            ("draft", OperationalLabel.RASCUNHO),
            ("error", OperationalLabel.ERRO),
            ("validated", OperationalLabel.ENVIADO),
            ("submitted", OperationalLabel.ENVIADO),
            ("processing", OperationalLabel.PROCESSANDO),
            ("processed", OperationalLabel.PROCESSADO),
            ("unknown", OperationalLabel.PENDENTE),
        ],
    )
    def test_operational_label(self, status, expected):
        assert operational_label(status) == expected

    def test_ready_for_form_open_only(self):
        assert is_ready_for_form(deal_status="open") is True
        assert is_ready_for_form(deal_status="won") is False

    @pytest.mark.parametrize(
        "status",
        [None, "draft", "error"],
    )
    def test_not_ready_for_automation(self, status):
        assert is_ready_for_automation(status) is False

    @pytest.mark.parametrize(
        "status",
        [
            FormStatus.VALIDATED,
            FormStatus.SUBMITTED,
            FormStatus.PROCESSING,
            FormStatus.PROCESSED,
        ],
    )
    def test_ready_for_automation(self, status):
        assert is_ready_for_automation(str(status)) is True


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.deal_esta_em_etapa_contrato")
@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
def test_list_deals_enriched_com_status_form(mock_get, mock_em_contrato, client):
    mock_em_contrato.side_effect = lambda d: d.get("id") in (746, 999)

    page = MagicMock()
    page.ok = True
    page.status_code = 200
    page.json.return_value = {
        "data": [
            {
                "id": 746,
                "title": "Biview",
                "owner_id": 1,
                "stage_id": 7,
                "status": "open",
                "pipeline_id": 1,
            },
            {
                "id": 999,
                "title": "Outro",
                "owner_id": 1,
                "stage_id": 7,
                "status": "open",
                "pipeline_id": 1,
            },
        ],
        "additional_data": {},
    }
    mock_get.return_value = page

    fixture = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "formulario_v1"
        / "form_payload_v1_g1.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    body = {"payload": payload, "schema_version": "v1"}
    patches = [
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
        patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True),
        patch("core.pipedrive_validations.resolver_branch_id", return_value="751"),
        patch("core.form_pipe_sync.push_form_to_pipedrive"),
        patch("core.form_pipe_sync.notificar_formulario_enviado_pipedrive"),
    ]
    for p in patches:
        p.start()
    try:
        client.post("/forms/746/submit", json=body)
    finally:
        for p in patches:
            p.stop()

    response = client.get("/pipedrive/deals", params={"owner_user_id": 1})
    assert response.status_code == 200
    data = {d["id"]: d for d in response.json()}
    assert len(data) == 2

    biview = data[746]
    assert biview["portal_stage"] == "Contrato"
    assert biview["form_status"] == "validated"
    assert biview["operational_label"] == "enviado"
    assert biview["ready_for_form"] is True
    assert biview["ready_for_automation"] is True

    outro = data[999]
    assert outro["operational_label"] == "pendente"
    assert outro["form_status"] is None
    assert outro["ready_for_automation"] is False


@patch("core.form_pipe_sync.notificar_formulario_enviado_pipedrive")
@patch("core.form_pipe_sync.push_form_to_pipedrive")
def test_submit_validado_cria_nota_pipe(_sync, mock_nota, client):
    fixture = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "formulario_v1"
        / "form_payload_v1_g1.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    body = {"payload": payload, "schema_version": "v1"}
    patches = [
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
        patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True),
        patch("core.pipedrive_validations.resolver_branch_id", return_value="751"),
    ]
    for p in patches:
        p.start()
    try:
        response = client.post("/forms/900/submit", json=body)
    finally:
        for p in patches:
            p.stop()
    assert response.status_code == 200
    assert response.json()["status"] == "validated"
    mock_nota.assert_called_once_with(900)


def test_list_deals_enriched_use_case():
    deals = [
        CrmDeal(id=1, title="A", owner_id=10, stage_id=7, status="open", pipeline_id=1),
        CrmDeal(id=2, title="B", owner_id=10, stage_id=7, status="won", pipeline_id=1),
    ]
    list_mock = MagicMock(spec=ListDealsContrato)
    list_mock.execute.return_value = deals
    repo = MemoryDealFormRepository()
    repo.save_draft(
        1,
        payload={"x": 1},
        schema_version="v1",
        owner_user_id=10,
        owner_name="U",
        deal_title="A",
    )
    enriched = ListDealsContratoEnriched(list_mock, repo).execute(owner_user_id=10)
    assert enriched[0]["operational_label"] == "rascunho"
    assert enriched[0]["ready_for_automation"] is False
    assert enriched[1]["ready_for_form"] is False
    assert enriched[1]["operational_label"] == "pendente"
