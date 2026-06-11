"""Sincronização form v1 ↔ Pipedrive."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.form_pipe_sync import (
    PipeSyncError,
    deal_to_form_payload_v1,
    form_payload_to_pipe_custom_fields,
    hydrate_form_payload_from_pipe,
    overlay_pipe_mapped_fields_from_pipe,
    sync_form_field_to_pipedrive,
    sync_form_payload_to_pipedrive,
)
from core.pipedrive_fields import (
    DEFAULT_PIPE_CURRENCY,
    FIELD_CIDADE,
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_GEBRAS,
    FIELD_EMAIL_DIRETOR_GEBRAS,
    FIELD_FILIAL,
    FIELD_NOME_CLIENTE,
    FIELD_PERCENTUAL_EXITO,
    FIELD_QTD_SOLE,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
    get_val,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"

G1_PIPE_FIELD_OPTIONS = {
    FIELD_FILIAL: {"1": "Matriz"},
    FIELD_REGIONAL: {"2": "Sul"},
    FIELD_SUBCENTRO_NIVEL_3: {"3": "Consultor Teste"},
    FIELD_PERCENTUAL_EXITO: {"4": "15%"},
    FIELD_EMAIL_CONSULTOR_GEBRAS: {"10": "consultor@gebras.com.br"},
    FIELD_EMAIL_COORDENADOR_GEBRAS: {"11": "coordenador@gebras.com.br"},
    FIELD_EMAIL_DIRETOR_GEBRAS: {"12": "diretor@gebras.com.br"},
}


def _mock_g1_pipe_options(field_code: str) -> dict[str, str]:
    return G1_PIPE_FIELD_OPTIONS.get(field_code, {})


def test_deal_to_form_carrega_sole_web_do_pipe():
    deal = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    payload = deal_to_form_payload_v1(deal)
    assert payload["servicos"]["sole_web"] == 4
    assert payload["cliente"]["contratante"] == "Empresa Exemplo Gestao Ltda"


def test_roundtrip_form_pipe_custom_fields():
    form = json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))
    with patch(
        "core.pipedrive_fields._enum_option_labels_for_field",
        side_effect=_mock_g1_pipe_options,
    ):
        cf = form_payload_to_pipe_custom_fields(999001, form)
    assert cf[FIELD_QTD_SOLE] == 4
    assert cf[FIELD_FILIAL] == 1
    assert cf[FIELD_EMAIL_COORDENADOR_GEBRAS] == [11]
    assert cf[FIELD_VALOR_MENSAL] == {
        "value": 1500.0,
        "currency": DEFAULT_PIPE_CURRENCY,
    }
    assert cf[FIELD_VALOR_IMPLANTACAO] == {
        "value": 7000.0,
        "currency": DEFAULT_PIPE_CURRENCY,
    }


def test_hydrate_preenche_vazios_do_pipe():
    deal = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    pipe_payload = deal_to_form_payload_v1(deal)
    sparse = {"schema_version": "v1", "cliente": {"contratante": "Só nome"}}
    merged = hydrate_form_payload_from_pipe(sparse, pipe_payload)
    assert merged["cliente"]["contratante"] == "Só nome"
    assert merged["servicos"]["sole_web"] == 4


def test_overlay_sobrescreve_rascunho_com_pipe():
    deal = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    pipe_payload = deal_to_form_payload_v1(deal)
    stale = {
        "schema_version": "v1",
        "cliente": {"contratante": "Teste testando"},
    }
    merged = overlay_pipe_mapped_fields_from_pipe(stale, pipe_payload)
    assert merged["cliente"]["contratante"] == "Empresa Exemplo Gestao Ltda"


@patch("core.form_pipe_sync.requests.patch")
@patch("core.pipedrive_fields._enum_option_labels_for_field")
def test_sync_patch_pipedrive(mock_labels, mock_patch):
    mock_labels.side_effect = _mock_g1_pipe_options
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    form = json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))
    sync_form_payload_to_pipedrive(746, form)
    mock_patch.assert_called_once()
    body = mock_patch.call_args.kwargs["json"]
    assert "custom_fields" in body
    assert body["custom_fields"][FIELD_QTD_SOLE] == 4


@patch("core.form_pipe_sync.requests.patch")
def test_sync_falha_levanta_erro(mock_patch):
    mock_patch.return_value = MagicMock(ok=False, status_code=400, text="bad")
    with pytest.raises(PipeSyncError):
        sync_form_payload_to_pipedrive(746, {"schema_version": "v1"})


@patch("core.form_pipe_sync.requests.patch")
def test_sync_campo_unico(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    assert sync_form_field_to_pipedrive(746, "cliente.contratante", "Acme Ltda") is True
    mock_patch.assert_called_once()
    body = mock_patch.call_args.kwargs["json"]
    assert body["custom_fields"][FIELD_NOME_CLIENTE] == "Acme Ltda"


@patch("core.form_pipe_sync.requests.patch")
def test_sync_campo_servico_envia_numero(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    sync_form_field_to_pipedrive(746, "servicos.gestao_qualidade_energia", 9)
    body = mock_patch.call_args.kwargs["json"]
    from core.pipedrive_fields import FIELD_INDICADORES_QUALIDADE

    assert body["custom_fields"][FIELD_INDICADORES_QUALIDADE] == 9
    assert isinstance(body["custom_fields"][FIELD_INDICADORES_QUALIDADE], int)


@patch("core.form_pipe_sync.requests.patch")
def test_sync_quantidade_ucs_envia_string_varchar(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    from core.pipedrive_fields import FIELD_QUANTIDADE_UCS

    sync_form_field_to_pipedrive(746, "servicos.quantidade_ucs", 2)
    body = mock_patch.call_args.kwargs["json"]
    assert body["custom_fields"][FIELD_QUANTIDADE_UCS] == "2"
    assert isinstance(body["custom_fields"][FIELD_QUANTIDADE_UCS], str)


@patch("core.form_pipe_sync.requests.patch")
def test_sync_campo_monetary_envia_objeto(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    sync_form_field_to_pipedrive(746, "valores.valor_recorrencia", "1.805")
    body = mock_patch.call_args.kwargs["json"]
    assert body["custom_fields"][FIELD_VALOR_MENSAL] == {
        "value": 1805.0,
        "currency": DEFAULT_PIPE_CURRENCY,
    }


@patch("core.form_pipe_sync.requests.patch")
def test_sync_campo_address_envia_objeto(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    sync_form_field_to_pipedrive(746, "cliente.municipio_estado", "Pelotas - RS, Brasil")
    body = mock_patch.call_args.kwargs["json"]
    assert body["custom_fields"][FIELD_CIDADE] == {"value": "Pelotas - RS, Brasil"}


def test_sync_campo_nao_mapeado():
    with pytest.raises(PipeSyncError, match="não mapeado"):
        sync_form_field_to_pipedrive(746, "anexos.proposta", True)


@patch("core.form_pipe_sync.requests.patch")
@patch("core.pipedrive_fields._enum_option_labels_for_field")
def test_sync_campo_set_email_gebras(mock_labels, mock_patch):
    mock_labels.return_value = {
        "91": "vinicius.bederode@gebras.com",
    }
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    sync_form_field_to_pipedrive(
        746,
        "signatarios.email_coordenador_gebras",
        "vinicius.bederode@gebras.com",
    )
    body = mock_patch.call_args.kwargs["json"]
    assert body["custom_fields"][FIELD_EMAIL_COORDENADOR_GEBRAS] == [91]
