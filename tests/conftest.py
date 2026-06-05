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
# .env local pode ter PULAR_HUB=true; testes de criação HUB precisam dela false
os.environ["PULAR_HUB"] = "false"

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
