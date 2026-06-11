"""Fase 7 — rollback FORMULARIO_WEB_ENABLED=false em < 5 min (suite + smoke)."""

from __future__ import annotations

import json
import time
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from core.automacao_config import (
    AutomacaoConfig,
    get_automacao_config,
    reset_automacao_config_for_tests,
    save_automacao_config,
)
from core.automacao_contrato import processar_deals_pendentes
from core.form_deal_adapter import DealFormSnapshot, preparar_deal_para_automacao

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def test_rollback_flag_desliga_formulario_web():
    reset_automacao_config_for_tests()
    save_automacao_config(
        AutomacaoConfig(
            dev_pular_clicksign=False,
            teste_plune_sem_assinatura=False,
            dev_hub_sem_aprovacao_plune=False,
            pular_hub=False,
            formulario_web_enabled=False,
        )
    )
    assert get_automacao_config(force_refresh=True).formulario_web_enabled is False


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


@patch(
    "core.automacao_contrato.get_automacao_config",
    return_value=AutomacaoConfig(formulario_web_enabled=False),
)
@patch(
    "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
    return_value=[999001],
)
@patch("core.automacao_contrato.buscar_deal_por_id")
def test_rollback_worker_ignora_fila_form_rapido(_cfg, mock_buscar, _listar):
    started = time.perf_counter()
    processar_deals_pendentes()
    elapsed = time.perf_counter() - started
    mock_buscar.assert_not_called()
    assert elapsed < 300, "rollback smoke deve completar em menos de 5 minutos"
