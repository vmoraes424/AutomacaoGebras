"""Testes: flags operacionais da automação (tabela automacao_config / memória pytest)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from core.automacao_config import (
    DEV_PRESET,
    PROD_PRESET,
    AutomacaoConfig,
    apply_automacao_preset,
    get_automacao_config,
    reset_automacao_config_for_tests,
    save_automacao_config,
)
from portal.composition import reset_container
from portal.main import create_app


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


@pytest.fixture(autouse=True)
def _clean_config_cache():
    reset_automacao_config_for_tests()
    yield
    reset_automacao_config_for_tests()


def test_prod_defaults_when_memory_empty():
    cfg = get_automacao_config(force_refresh=True)
    assert cfg.to_dict() == PROD_PRESET.to_dict()


def test_save_and_load_memory_backend():
    cfg = DEV_PRESET
    save_automacao_config(cfg)
    loaded = get_automacao_config(force_refresh=True)
    assert loaded.to_dict() == cfg.to_dict()


def test_apply_presets_memory():
    apply_automacao_preset("dev")
    assert get_automacao_config(force_refresh=True).to_dict() == DEV_PRESET.to_dict()
    apply_automacao_preset("prod")
    assert get_automacao_config(force_refresh=True).to_dict() == PROD_PRESET.to_dict()


def test_get_config_api(client):
    response = client.get("/config/automacao/access")
    assert response.status_code == 200
    assert response.json()["password_required"] is False

    response = client.get("/config/automacao")
    assert response.status_code == 200
    data = response.json()
    assert "dev_pular_clicksign" in data
    assert data.get("mysql_database")


def test_config_password_required(monkeypatch, client):
    monkeypatch.setenv("PORTAL_CONFIG_PASSWORD", "secret-config")
    reset_container()
    c = TestClient(create_app())
    try:
        assert c.get("/config/automacao/access").json()["password_required"] is True
        assert c.get("/config/automacao").status_code == 401
        ok = c.get(
            "/config/automacao",
            headers={"X-Portal-Config-Password": "secret-config"},
        )
        assert ok.status_code == 200
        bad = c.get(
            "/config/automacao",
            headers={"X-Portal-Config-Password": "wrong"},
        )
        assert bad.status_code == 401
    finally:
        reset_container()


def test_put_config_api(client):
    body = {
        "dev_pular_clicksign": True,
        "teste_plune_sem_assinatura": False,
        "dev_hub_sem_aprovacao_plune": False,
        "pular_hub": True,
        "formulario_web_enabled": True,
    }
    response = client.put("/config/automacao", json=body)
    assert response.status_code == 200
    assert response.json()["pular_hub"] is True


def test_preset_dev_api(client):
    response = client.post("/config/automacao/preset/dev")
    assert response.status_code == 200
    data = response.json()
    assert data["dev_pular_clicksign"] is True
    assert data["pular_hub"] is True


def test_preset_prod_api(client):
    client.post("/config/automacao/preset/dev")
    response = client.post("/config/automacao/preset/prod")
    assert response.status_code == 200
    data = response.json()
    assert data["dev_pular_clicksign"] is False
    assert data["teste_plune_sem_assinatura"] is False
    assert data["pular_hub"] is False


def test_save_persists_to_automacao_config_table(monkeypatch):
    monkeypatch.setenv("AUTOMACAO_CONFIG_BACKEND", "mysql")
    saved: dict | None = None

    class FakeConn:
        def execute(self, sql, params=()):
            nonlocal saved
            if "INSERT INTO automacao_config" in sql:
                saved = {"sql": sql, "params": params}
            return self

        def fetchone(self):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("core.database.db_conn", return_value=FakeConn()):
        reset_automacao_config_for_tests()
        result = save_automacao_config(AutomacaoConfig(pular_hub=True))
    assert saved is not None
    assert saved["params"][0] == 1
    assert saved["params"][4] == 1
    assert result.updated_at
