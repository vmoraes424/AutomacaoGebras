"""Fase 7 — proteção mínima por token."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from portal.composition import reset_container
from portal.main import create_app


@pytest.fixture
def client_no_auth(monkeypatch):
    monkeypatch.setenv("PORTAL_API_TOKEN", "")
    reset_container()
    yield TestClient(create_app())
    reset_container()


@pytest.fixture
def client_with_auth(monkeypatch):
    monkeypatch.setenv("PORTAL_API_TOKEN", "secret-test-token")
    reset_container()
    yield TestClient(create_app())
    reset_container()


def test_health_publico_sem_token(client_with_auth):
    response = client_with_auth.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["auth_required"] is True


def test_rota_protegida_sem_token_retorna_401(client_with_auth):
    response = client_with_auth.get("/pipedrive/users")
    assert response.status_code == 401


def test_rota_protegida_com_bearer(client_with_auth):
    with (
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_users",
            return_value=[],
        ),
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_open_deals_in_contrato_stage",
            return_value=[],
        ),
    ):
        response = client_with_auth.get(
            "/pipedrive/users",
            headers={"Authorization": "Bearer secret-test-token"},
        )
    assert response.status_code == 200


def test_rota_protegida_com_header_x_portal_token(client_with_auth):
    with (
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_users",
            return_value=[],
        ),
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_open_deals_in_contrato_stage",
            return_value=[],
        ),
    ):
        response = client_with_auth.get(
            "/pipedrive/users",
            headers={"X-Portal-Token": "secret-test-token"},
        )
    assert response.status_code == 200


def test_sem_portal_api_token_liberado(client_no_auth):
    with (
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_users",
            return_value=[],
        ),
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_open_deals_in_contrato_stage",
            return_value=[],
        ),
    ):
        response = client_no_auth.get("/pipedrive/users")
    assert response.status_code == 200
    assert client_no_auth.get("/health").json()["auth_required"] is False
