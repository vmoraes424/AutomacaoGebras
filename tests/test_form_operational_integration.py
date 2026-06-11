"""Fase 6 — fluxo ponta a ponta em dev (opcional, com rede).

Rodar manualmente:

    RUN_INTEGRATION=1 pytest tests/test_form_operational_integration.py -m integration -v

Requer `.env` com Pipedrive, MySQL (`deal_forms`) e flags de dev (`DEV_PULAR_CLICKSIGN`, etc.).
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration

# Rastreável: Fase 7 — teste manual em staging (docs/formulario-web/fase-7-hardening.md)
_requires_integration = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "1",
    reason="defina RUN_INTEGRATION=1 para testes com APIs reais (ver fase-7-hardening.md)",
)


@_requires_integration
def test_fluxo_portal_submit_worker_dev():
    """Smoke documentado: portal -> validated -> worker (dev flags)."""
    from fastapi.testclient import TestClient

    from portal.composition import reset_container
    from portal.main import create_app

    reset_container()
    client = TestClient(create_app())

    owner_id = os.environ.get("INTEGRATION_OWNER_ID")
    deal_id = os.environ.get("INTEGRATION_DEAL_ID")
    if not owner_id or not deal_id:
        pytest.skip("defina INTEGRATION_OWNER_ID e INTEGRATION_DEAL_ID no ambiente")

    owner_id = int(owner_id)
    deal_id = int(deal_id)

    deals = client.get("/pipedrive/deals", params={"owner_user_id": owner_id})
    assert deals.status_code == 200
    ids = {d["id"] for d in deals.json()}
    assert deal_id in ids

    form = client.get(f"/forms/{deal_id}")
    assert form.status_code == 200
    payload = form.json()["payload"]
    payload.setdefault("anexos", {})["proposta_comercial_anexada"] = True

    submit = client.post(
        f"/forms/{deal_id}/submit",
        json={"payload": payload, "schema_version": "v1"},
    )
    assert submit.status_code == 200
    assert submit.json()["status"] in ("validated", "error")
    if submit.json()["status"] == "error":
        pytest.skip(f"form incompleto no deal {deal_id}: {submit.json().get('validation_errors')}")

    from core.automacao_contrato import processar_deals_pendentes

    processar_deals_pendentes()

    status = client.get(f"/forms/{deal_id}/status")
    assert status.status_code == 200
    assert status.json()["status"] in (
        "validated",
        "submitted",
        "processing",
        "processed",
    )


@_requires_integration
def test_sync_todos_campos_mapeados_pipe_v2():
    """Blur/sync de cada campo mapeado no deal de integração (schema v2)."""
    from fastapi.testclient import TestClient

    from core.form_schema_v1 import FORM_PATH_TO_PIPE
    from core.pipe_v2_schema import validate_pipe_custom_field
    from portal.composition import reset_container
    from portal.main import create_app

    deal_id = os.environ.get("INTEGRATION_DEAL_ID")
    if not deal_id:
        pytest.skip("defina INTEGRATION_DEAL_ID no ambiente")

    deal_id = int(deal_id)
    reset_container()
    client = TestClient(create_app())

    form = client.get(f"/forms/{deal_id}")
    assert form.status_code == 200
    payload = form.json()["payload"]

    def _value(path: str) -> object:
        section, _, field = path.partition(".")
        return payload[section][field]

    for field_path, pipe_hash in FORM_PATH_TO_PIPE.items():
        response = client.post(
            f"/forms/{deal_id}/sync-field",
            json={
                "field_path": field_path,
                "value": _value(field_path),
                "schema_version": "v1",
            },
        )
        assert response.status_code == 200, (
            f"sync-field {field_path} -> {response.status_code}: {response.text[:300]}"
        )
        from core.form_pipe_sync import form_field_to_pipe_value

        converted = form_field_to_pipe_value(pipe_hash, field_path, _value(field_path))
        validate_pipe_custom_field(pipe_hash, converted, field_path=field_path)
