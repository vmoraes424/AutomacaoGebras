"""Testes: endpoint HUB do portal (com mocks)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from core.hub_instalacoes import HubInstalacao, HubInstalacoesResult
from portal.domain.hub.exceptions import HubReadError, HubValidationError
from portal.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_list_instalacoes_ok(client):
    payload = HubInstalacoesResult(
        codigo_cliente=352,
        codigos_instalacao_selecionados=(665,),
        formato_pipedrive="352/665",
        instalacoes=(
            HubInstalacao(
                codigo=665,
                codigo_cliente=352,
                identificacao="12345648",
                razao_social="UC A",
                cidade="Pelotas",
                uf="RS",
                ativo=True,
                selecionada=True,
            ),
        ),
        codigos_nao_encontrados=(),
    )
    with patch(
        "core.hub_instalacoes.consultar_instalacoes_hub",
        return_value=payload,
    ):
        response = client.get("/hub/instalacoes", params={"codigo_cliente_instalacao": "352/665"})

    assert response.status_code == 200
    data = response.json()
    assert data["codigo_cliente"] == 352
    assert data["formato_pipedrive"] == "352/665"
    assert data["instalacoes"][0]["selecionada"] is True


def test_list_instalacoes_400(client):
    with patch(
        "portal.application.hub.list_instalacoes.ListHubInstalacoes.execute",
        side_effect=HubValidationError("inválido"),
    ):
        response = client.get("/hub/instalacoes", params={"codigo_cliente_instalacao": "x"})
    assert response.status_code == 400


def test_list_servicos_ok(client):
    with patch(
        "portal.application.hub.list_servicos.ListHubServicos.execute",
        return_value={
            "servicos": [
                {
                    "codigo_servico": 2,
                    "chave": "sole_web",
                    "nome": "SOLE Web",
                    "sigla": "SW",
                    "nome_pipe": "SOLE WEB",
                    "ordem_form": 1,
                }
            ]
        },
    ):
        response = client.get("/hub/servicos")
    assert response.status_code == 200
    assert response.json()["servicos"][0]["sigla"] == "SW"


def test_list_instalacoes_502(client):
    with patch(
        "portal.application.hub.list_instalacoes.ListHubInstalacoes.execute",
        side_effect=HubReadError("falha hub"),
    ):
        response = client.get("/hub/instalacoes", params={"codigo_cliente_instalacao": "352"})
    assert response.status_code == 502
