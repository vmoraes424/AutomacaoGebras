"""Testes: endpoints de formulário (store em memória)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from portal.composition import reset_container
from portal.main import create_app


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


@pytest.fixture(autouse=True)
def _deal_aberto_etapa_contrato():
    """Submit/draft exigem etapa Contrato; testes focam no form, não no Pipe."""
    with patch(
        "portal.application.formulario.deal_eligibility.deal_elegivel_formulario_contrato",
        return_value=True,
    ):
        yield


@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form", return_value=None)
def test_get_form_not_found(_mock_deal, client):
    response = client.get("/forms/746")
    assert response.status_code == 404


@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_get_form_bootstraps_do_pipedrive(mock_buscar, client):
    deal = json.loads(
        (
            Path(__file__).resolve().parent
            / "fixtures"
            / "formulario_v1"
            / "deal_pipe_g1.json"
        ).read_text(encoding="utf-8")
    )
    mock_buscar.return_value = deal
    response = client.get("/forms/999001")
    assert response.status_code == 200
    data = response.json()
    assert data["deal_id"] == 999001
    assert data["status"] == "draft"
    assert data["payload"]["servicos"]["sole_web"] == 4


@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_save_and_get_draft(mock_buscar, client):
    from core.form_uc_hub import normalize_hub_payload

    mock_buscar.return_value = {
        "id": 746,
        "title": "Biview",
        "status": "open",
        "custom_fields": {},
    }
    payload = {
        "schema_version": "v1",
        "cliente": {"contratante": "Teste Ltda"},
    }
    expected_payload = normalize_hub_payload(payload)
    body = {
        "payload": payload,
        "owner_user_id": 24587114,
        "owner_name": "Pedro",
        "deal_title": "Biview",
        "schema_version": "v1",
    }
    put = client.put("/forms/746/draft", json=body)
    assert put.status_code == 200
    saved = put.json()
    assert saved["deal_id"] == 746
    assert saved["status"] == "draft"
    assert saved["payload"]["cliente"]["contratante"] == "Teste Ltda"
    assert saved["owner_user_id"] == 24587114

    get = client.get("/forms/746")
    assert get.status_code == 200
    assert get.json()["payload"] == expected_payload

    status = client.get("/forms/746/status")
    assert status.status_code == 200
    assert status.json()["status"] == "draft"
    assert status.json()["schema_version"] == "v1"


@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_update_draft_preserves_created_at(mock_buscar, client):
    mock_buscar.return_value = {"id": 100, "title": "T", "custom_fields": {}}
    client.put(
        "/forms/100/draft",
        json={"payload": {"a": 1}, "schema_version": "v1"},
    )
    first = client.get("/forms/100").json()
    client.put(
        "/forms/100/draft",
        json={"payload": {"a": 2}, "schema_version": "v1"},
    )
    second = client.get("/forms/100").json()
    assert second["payload"]["a"] == 2
    assert second["created_at"] == first["created_at"]
    assert second["updated_at"] != first["updated_at"]


@patch("core.form_pipe_sync.push_form_to_pipedrive")
@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_submit_incompleto_retorna_error_com_validation_errors(
    mock_buscar, _sync, client
):
    mock_buscar.return_value = {"id": 746, "title": "T", "status": "open", "custom_fields": {}}
    body = {
        "payload": {"cliente": {"contratante": "Enviado"}},
        "schema_version": "v1",
    }
    response = client.post("/forms/746/submit", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["validation_errors"]
    assert data["submitted_at"] is None


def test_submit_g1_validado(client):
    import json
    from pathlib import Path

    fixture = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "formulario_v1"
        / "form_payload_v1_g1.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    body = {"payload": payload, "schema_version": "v1"}
    from unittest.mock import patch

    patches = [
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
        patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True),
        patch("core.pipedrive_validations.resolver_branch_id", return_value="751"),
        patch("core.form_pipe_sync.push_form_to_pipedrive"),
        patch(
            "portal.application.formulario.deal_eligibility.fetch_deal_for_form",
            return_value={"id": 746, "title": "G1", "status": "open", "custom_fields": {}},
        ),
    ]
    for p in patches:
        p.start()
    try:
        response = client.post("/forms/746/submit", json=body)
    finally:
        for p in patches:
            p.stop()
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "validated"
    assert data["submitted_at"] is not None
    assert not data.get("validation_errors")


@patch("core.form_pipe_sync.push_form_to_pipedrive")
@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_draft_after_submit_returns_409(mock_buscar, _sync, client):
    mock_buscar.return_value = {"id": 800, "title": "T", "status": "open", "custom_fields": {}}
    import json
    from pathlib import Path
    from unittest.mock import patch

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
        patch(
            "portal.application.formulario.deal_eligibility.fetch_deal_for_form",
            return_value={"id": 800, "title": "T", "status": "open", "custom_fields": {}},
        ),
    ]
    for p in patches:
        p.start()
    try:
        client.post("/forms/800/submit", json=body)
    finally:
        for p in patches:
            p.stop()
    response = client.put("/forms/800/draft", json=body)
    assert response.status_code == 409


@patch("core.form_pipe_sync.push_form_to_pipedrive")
@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
def test_sync_pipedrive(mock_fetch, mock_push, client):
    mock_fetch.return_value = {"id": 746, "title": "T", "status": "open", "custom_fields": {}}
    body = {
        "payload": {"schema_version": "v1", "cliente": {"contratante": "Sync Teste"}},
        "schema_version": "v1",
    }
    response = client.post("/forms/746/sync-pipedrive", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["deal_id"] == 746
    assert data["synced"] is True
    mock_push.assert_called_once_with(746, body["payload"])


@patch("core.form_pipe_sync.sync_form_field_to_pipedrive", return_value=True)
def test_sync_field_pipedrive(mock_sync_field, client):
    response = client.post(
        "/forms/746/sync-field",
        json={"field_path": "cliente.contratante", "value": "Novo Nome"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["field_path"] == "cliente.contratante"
    assert data["synced"] is True
    mock_sync_field.assert_called_once_with(746, "cliente.contratante", "Novo Nome")


@patch("core.form_readiness_v1.listar_arquivos_deal")
def test_get_form_attachments(mock_listar, client):
    from core.form_readiness_v1 import invalidate_deal_attachments_cache

    invalidate_deal_attachments_cache()
    mock_listar.return_value = [
        {
            "id": 1,
            "file_type": "pdf",
            "name": "Proposta Comercial - Cliente.pdf",
            "add_time": "2026-01-01",
        },
    ]
    response = client.get("/forms/746/attachments")
    assert response.status_code == 200
    data = response.json()
    assert data["deal_id"] == 746
    assert data["proposta_comercial_anexada"] is True
    assert data["contrato"]["source"] == "padrao"


def test_readiness_interactive_nao_bate_pipe_sem_cache(client):
    from core.form_readiness_v1 import invalidate_deal_attachments_cache

    invalidate_deal_attachments_cache()
    body = {
        "payload": {"schema_version": "v1", "cliente": {"contratante": "Teste"}},
        "schema_version": "v1",
    }
    with patch("core.form_readiness_v1.listar_arquivos_deal") as mock_listar:
        response = client.post("/forms/746/readiness", json=body)
        assert response.status_code == 200
        mock_listar.assert_not_called()


@patch("core.form_readiness_v1.listar_arquivos_deal")
def test_readiness_reutiliza_cache_anexos(mock_listar, client):
    from core.form_readiness_v1 import inspect_deal_attachments, invalidate_deal_attachments_cache

    mock_listar.return_value = []
    invalidate_deal_attachments_cache()
    inspect_deal_attachments(746)
    body = {
        "payload": {"schema_version": "v1", "cliente": {"contratante": "Teste"}},
        "schema_version": "v1",
    }
    first = client.post("/forms/746/readiness", json=body)
    second = client.post("/forms/746/readiness", json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    assert mock_listar.call_count == 1

