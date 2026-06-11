"""Fixtures e variáveis de ambiente para testes (sem rede por padrão)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Evita falha de import por .env vazio em CI/local de teste
os.environ.setdefault("PIPEDRIVE_API_TOKEN", "pytest-pipedrive-token")
os.environ.setdefault("CLICKSIGN_ACCESS_TOKEN", "pytest-clicksign-token")
os.environ.setdefault("CLICKSIGN_BASE_URL", "https://sandbox.clicksign.com/api/v3")
os.environ.setdefault("PLUNE_BASE_URL", "https://plune.test.example")
os.environ.setdefault("PLUNE_AUTH_TOKEN", "pytest-plune-token")
os.environ.setdefault("PORTAL_API_TOKEN", "")
os.environ.setdefault("PORTAL_STRUCTURED_LOGS", "false")
# pytest: tela de configs aberta (testes de senha sobrescrevem via monkeypatch)
os.environ["PORTAL_CONFIG_PASSWORD"] = ""

# Portal: testes usam repositório em memória (sem MySQL real)
os.environ["PORTAL_DEAL_FORM_REPOSITORY"] = "memory"
# Config da automação: pytest usa memória; produção usa tabela automacao_config no MySQL
os.environ["AUTOMACAO_CONFIG_BACKEND"] = "memory"

# config.PLUNE_BRANCH_ID consulta MySQL no import de plune_pedido — mock antes de qualquer import core.*
_FAKE_FILIAL = {
    "subcentro_custo_id": "100",
    "parametro_recorrente": "200",
    "parametro_implantacao": "300",
}


def _fake_branch_config(branch_id: str) -> dict:
    faturamento = (
        {"pedido_serie": "1", "pedido_modelo_id": "01"}
        if str(branch_id) == "751"
        else {"pedido_serie": "0", "pedido_modelo_id": "01"}
    )
    return {**_FAKE_FILIAL, **faturamento, "branch_id": branch_id}


_DB_PATCHES = [
    patch("core.database.default_branch_id", return_value="751"),
    patch("core.database.branch_config", side_effect=_fake_branch_config),
    patch("core.database.db_conn"),
]
for _p in _DB_PATCHES:
    _p.start()

import pytest  # noqa: E402


@pytest.fixture
def deal_minimo() -> dict:
    return {
        "id": 999,
        "title": "Cliente Teste Ltda",
        "org_name": "Cliente Teste Ltda",
    }


@pytest.fixture
def parceiro_minimo() -> dict:
    return {
        "id": "1001",
        "razao_social": "Cliente Teste Ltda",
        "documento": "52398605000186",
    }


@pytest.fixture
def pdf_bytes() -> bytes:
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


@pytest.fixture
def form_payload_v1_minimo() -> dict:
    return {
        "schema_version": "v1",
        "cliente": {"contratante": "Cliente Teste Ltda", "documento": "11222333000144"},
        "servicos": {"sole_web": 1, "quantidade_ucs": 1},
    }


@pytest.fixture
def eligible_pipe_deal() -> dict:
    """Deal aberto em Contrato para submit/open (sem rede)."""
    deal = {
        "id": 746,
        "title": "Biview",
        "status": "open",
        "stage_id": 7,
        "pipeline_id": 1,
        "custom_fields": {},
    }
    with (
        patch(
            "portal.application.formulario.deal_eligibility.fetch_deal_for_form",
            return_value=deal,
        ),
        patch(
            "portal.application.formulario.deal_eligibility.deal_elegivel_formulario_contrato",
            return_value=True,
        ),
    ):
        yield deal


@pytest.fixture
def deal_form_record_draft(form_payload_v1_minimo: dict) -> dict:
    return {
        "deal_id": 746,
        "status": "draft",
        "schema_version": "v1",
        "payload": form_payload_v1_minimo,
        "owner_user_id": 24587114,
        "owner_name": "Consultor Teste",
        "deal_title": "Biview",
    }
