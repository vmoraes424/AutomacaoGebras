"""Fase 7 — rollback FORMULARIO_WEB_ENABLED=false em < 5 min (suite + smoke)."""

from __future__ import annotations

import json
import time
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from core.automacao_contrato import processar_deals_pendentes
from core.config import _env_bool
from core.form_deal_adapter import DealFormSnapshot, preparar_deal_para_automacao

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def test_rollback_flag_lida_do_ambiente(monkeypatch):
    monkeypatch.setenv("FORMULARIO_WEB_ENABLED", "false")
    assert _env_bool("FORMULARIO_WEB_ENABLED", True) is False


def test_rollback_adaptador_ignora_form():
    deal_pipe = json.loads((FIXTURES / "deal_pipe_g1.json").read_text(encoding="utf-8"))
    form = json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))
    pipe = deepcopy(deal_pipe)
    result = preparar_deal_para_automacao(
        pipe,
        formulario_web_enabled=False,
        form_loader=lambda _id: DealFormSnapshot(999001, "validated", "v1", form),
    )
    assert result.source == "pipe"
    assert result.deal == pipe


@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", False)
@patch(
    "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
    return_value=[999001],
)
@patch("core.automacao_contrato.buscar_deal_por_id")
def test_rollback_worker_ignora_fila_form_rapido(mock_buscar, _listar):
    started = time.perf_counter()
    processar_deals_pendentes()
    elapsed = time.perf_counter() - started
    mock_buscar.assert_not_called()
    assert elapsed < 300, "rollback smoke deve completar em menos de 5 minutos"
