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
    sync_form_payload_to_pipedrive,
)
from core.pipedrive_fields import FIELD_QTD_SOLE, get_val

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def test_deal_to_form_carrega_sole_web_do_pipe():
    deal = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    payload = deal_to_form_payload_v1(deal)
    assert payload["servicos"]["sole_web"] == 4
    assert payload["cliente"]["contratante"] == "Empresa Exemplo Gestao Ltda"


def test_roundtrip_form_pipe_custom_fields():
    form = json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))
    cf = form_payload_to_pipe_custom_fields(999001, form)
    assert cf[FIELD_QTD_SOLE] == "4"


def test_hydrate_preenche_vazios_do_pipe():
    deal = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    pipe_payload = deal_to_form_payload_v1(deal)
    sparse = {"schema_version": "v1", "cliente": {"contratante": "Só nome"}}
    merged = hydrate_form_payload_from_pipe(sparse, pipe_payload)
    assert merged["cliente"]["contratante"] == "Só nome"
    assert merged["servicos"]["sole_web"] == 4


@patch("core.form_pipe_sync.requests.patch")
def test_sync_patch_pipedrive(mock_patch):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    form = json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))
    sync_form_payload_to_pipedrive(746, form)
    mock_patch.assert_called_once()
    body = mock_patch.call_args.kwargs["json"]
    assert "custom_fields" in body
    assert body["custom_fields"][FIELD_QTD_SOLE] == "4"


@patch("core.form_pipe_sync.requests.patch")
def test_sync_falha_levanta_erro(mock_patch):
    mock_patch.return_value = MagicMock(ok=False, status_code=400, text="bad")
    with pytest.raises(PipeSyncError):
        sync_form_payload_to_pipedrive(746, {"schema_version": "v1"})
