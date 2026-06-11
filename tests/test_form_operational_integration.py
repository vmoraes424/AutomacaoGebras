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
