"""
Regressão: automação (Plune → contrato/Clicksign → HUB) compatível com formulário web.

Garante que merge form → deal produz os mesmos insumos que o worker usava
com dados só no Pipedrive, e que os dois fluxos do worker continuam íntegros:
  - processar_deals_pendentes (pós-submit)
  - processar_contratos_assinados (pós-assinatura)

Rodar localmente:
  python scripts/validate_automacao_regression.py
  pytest tests/test_automacao_regression_form.py -q
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.automacao_config import AutomacaoConfig
from core.automacao_contrato import fill_contract, processar_contratos_assinados
from core.form_deal_adapter import merge_form_into_deal, preparar_deal_para_automacao
from core.form_uc_hub import build_observacoes_detalhes_hub, normalize_hub_payload
from core.hub_catalogo import servicos_template_hub
from core.hub_pedido import _montar_dados_pedido_hub_deal, erros_validacao_observacoes_hub
from core.pipedrive_fields import (
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_NOME_CLIENTE,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_QTD_SOLE,
    extrair_signatarios,
    get_numero_contrato,
    get_val,
)

pytestmark = pytest.mark.automation_regression

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _merged_g1() -> dict:
    return merge_form_into_deal(_load("deal_pipe_g1.json"), _load("form_payload_v1_g1.json"))


class TestAutomacaoInputsPosForm:
    """Deal merged deve alimentar Plune, contrato, Clicksign e HUB como antes."""

    def test_g1_hub_observacoes_validas(self):
        merged = _merged_g1()
        assert erros_validacao_observacoes_hub(merged) == []
        obs = get_val(merged, FIELD_OBSERVACOES_DETALHES)
        assert "UC =" in obs
        assert "1.500,92" in obs

    def test_g1_signatarios_ordem_legacy(self):
        merged = _merged_g1()
        expected = _load("expected_g1.json")
        signatarios = extrair_signatarios(merged)
        assert len(signatarios) == expected["signatarios_count"]
        assert [s["papel"] for s in signatarios] == expected["signatarios_ordem"]

    def test_g1_numero_contrato_e_cliente(self):
        merged = _merged_g1()
        expected = _load("expected_g1.json")
        assert get_numero_contrato(merged).startswith(expected["numero_contrato_pattern"])
        assert get_val(merged, FIELD_NOME_CLIENTE) == "Empresa Exemplo Gestao Ltda"

    @patch("core.automacao_contrato.get_enum_label", return_value="15%")
    @patch("core.automacao_contrato.buscar_parceiro_plune_por_documento", return_value=None)
    @patch("core.automacao_contrato.DocxTemplate")
    @patch("core.automacao_contrato.os.path.exists", return_value=True)
    def test_g1_fill_contract_aceita_deal_merged(
        self, _exists, mock_docx_cls, _parceiro, _enum
    ):
        merged = _merged_g1()
        doc = MagicMock()
        mock_docx_cls.return_value = doc
        fill_contract(merged)
        contexto = doc.render.call_args[0][0]
        assert contexto["sole_web"] == "4"
        assert contexto["nome_cliente"]

    def test_g1_montar_pedido_hub(self):
        merged = _merged_g1()
        with (
            patch("core.hub_pedido._validar_instalacoes_hub"),
            patch("core.hub_pedido._id_plune_recorrente_para_hub", return_value=777001),
            patch("core.hub_pedido.get_enum_label", return_value="15%"),
            patch("core.hub_pedido._catalogo_servicos_hub", new=_mock_catalogo_hub),
        ):
            dados = _montar_dados_pedido_hub_deal("999001", merged)
        assert dados["codigo_cliente"] == 352
        assert dados["codigos_instalacao"] == [665, 1942]
        assert len(dados["linhas_obs"]) == 2

    def test_flag_off_mantem_pipe_puro(self):
        """Rollback: sem form, worker usa deal Pipe inalterado."""
        pipe = _load("deal_pipe_g1.json")
        form = _load("form_payload_v1_g1.json")
        from core.form_deal_adapter import DealFormSnapshot

        result = preparar_deal_para_automacao(
            deepcopy(pipe),
            formulario_web_enabled=False,
            form_loader=lambda _id: DealFormSnapshot(999001, "validated", "v1", form),
        )
        assert result.source == "pipe"
        assert result.deal == pipe


class TestUcMatrixCompatibilidadeAutomacao:
    """Matriz UC (valor > 0) gera observações HUB válidas para pedido."""

    def test_valor_sem_checkbox_ativo_gera_observacoes(self):
        servicos = servicos_template_hub()
        for item in servicos:
            if item["chave"] == "sole_web":
                item["valor"] = "45"
                item["ativo"] = False

        payload = normalize_hub_payload(
            {
                "schema_version": "v1",
                "cliente": {"codigo_cliente_instalacao": "352/665"},
                "hub": {
                    "instalacoes": [
                        {
                            "codigo_instalacao": 665,
                            "codigo_cliente": 352,
                            "identificacao": "12345648",
                            "razao_social": "",
                            "cidade": "Pelotas",
                            "uf": "RS",
                            "valor_uc": "",
                            "servicos": servicos,
                        }
                    ]
                },
            }
        )
        obs = build_observacoes_detalhes_hub(payload["hub"]["instalacoes"])
        assert "SOLE WEB" in obs
        assert "45,00" in obs

        merged = merge_form_into_deal(_load("deal_pipe_g1.json"), payload)
        assert erros_validacao_observacoes_hub(merged) == []
        assert get_val(merged, FIELD_CODIGO_CLIENTE_INSTALACAO) == "352/665"


class TestWorkerPosAssinatura:
    """processar_contratos_assinados — cadeia Plune aprova → ganho → HUB."""

    @patch("core.hub_pedido.tentar_criar_pedido_hub_deal")
    @patch("core.automacao_contrato.marcar_deal_como_ganho")
    @patch("core.automacao_contrato.marcar_pedidos_aprovados")
    @patch(
        "core.automacao_contrato.aprovar_pedidos_plune",
        return_value={"status": "approved"},
    )
    @patch("core.automacao_contrato.buscar_por_deal_id", return_value={"parceiro_plune_criado": 0})
    @patch("core.automacao_contrato.limpar_template_local_envelope")
    @patch("core.automacao_contrato.limpar_templates_locais_deal")
    @patch("core.automacao_contrato._remover_arquivo_template_local")
    @patch("core.automacao_contrato.carregar_pedidos_plune_criados", return_value=[])
    @patch("core.automacao_contrato.listar_aguardando_pedido_plune")
    @patch("core.automacao_contrato.get_automacao_config")
    def test_fluxo_fechado_aprova_ganha_hub(
        self,
        mock_cfg,
        mock_listar,
        _carregar,
        _rm,
        _limpar_deal,
        _limpar_env,
        _buscar_env,
        mock_aprovar,
        mock_marcar_aprov,
        mock_ganho,
        mock_hub,
    ):
        mock_cfg.return_value = AutomacaoConfig(teste_plune_sem_assinatura=False)
        mock_listar.return_value = [
            {"deal_id": "746", "envelope_id": "env-1", "template_local_path": ""}
        ]

        with patch("core.automacao_contrato.ClicksignClient") as mock_cs_cls:
            cs = mock_cs_cls.return_value
            cs.get_envelope_status.return_value = "closed"
            cs.get_ultima_assinatura_data_ptbr.return_value = "01/06/2026"
            processar_contratos_assinados()

        mock_aprovar.assert_called_once_with("746", data_entrega="01/06/2026")
        mock_marcar_aprov.assert_called_once_with("746")
        mock_ganho.assert_called_once_with("746")
        mock_hub.assert_called_once()
        assert mock_hub.call_args.kwargs.get("parceiro_plune_criado") is False

    @patch("core.hub_pedido.tentar_criar_pedido_hub_deal")
    @patch("core.automacao_contrato.marcar_deal_como_ganho")
    @patch("core.automacao_contrato.marcar_pedidos_aprovados")
    @patch(
        "core.automacao_contrato.aprovar_pedidos_plune",
        return_value={"status": "approved"},
    )
    @patch(
        "core.automacao_contrato.buscar_por_deal_id",
        return_value={"parceiro_plune_criado": 1},
    )
    @patch("core.automacao_contrato.limpar_template_local_envelope")
    @patch("core.automacao_contrato.limpar_templates_locais_deal")
    @patch("core.automacao_contrato._remover_arquivo_template_local")
    @patch("core.automacao_contrato.carregar_pedidos_plune_criados", return_value=[])
    @patch("core.automacao_contrato.listar_aguardando_pedido_plune")
    @patch("core.automacao_contrato.get_automacao_config")
    def test_parceiro_novo_ainda_cria_hub_se_flag_zero(
        self,
        mock_cfg,
        mock_listar,
        _carregar,
        _rm,
        _limpar_deal,
        _limpar_env,
        _buscar_env,
        _aprovar,
        _marcar_aprov,
        _ganho,
        mock_hub,
    ):
        """HUB skip só quando parceiro_plune_criado=1 no registro do envelope."""
        mock_cfg.return_value = AutomacaoConfig(teste_plune_sem_assinatura=False)
        mock_listar.return_value = [
            {"deal_id": "746", "envelope_id": "env-1", "template_local_path": ""}
        ]
        with patch("core.automacao_contrato.ClicksignClient") as mock_cs_cls:
            cs = mock_cs_cls.return_value
            cs.get_envelope_status.return_value = "closed"
            cs.get_ultima_assinatura_data_ptbr.return_value = "01/06/2026"
            processar_contratos_assinados()
        mock_hub.assert_called_once()
        assert mock_hub.call_args.kwargs.get("parceiro_plune_criado") is True


class TestValidacaoLegacyVsForm:
    """Deal merged G1 alimenta validações HUB (observações) como antes."""

    def test_g1_merged_observacoes_obrigatorias_para_hub(self):
        merged = _merged_g1()
        obs = get_val(merged, FIELD_OBSERVACOES_DETALHES)
        assert "UC =" in obs
        assert erros_validacao_observacoes_hub(merged) == []


def _mock_catalogo_hub():
    from core.hub_pedido import _ServicoCatalogoHub

    return (
        _ServicoCatalogoHub(1, "SOLE Consultoria", "sole consultoria", "sole consultoria", "sc"),
        _ServicoCatalogoHub(
            2, "SOLE Web (com telemetria)", "sole web (com telemetria)",
            "sole web (com telemetria)", "sw",
        ),
        _ServicoCatalogoHub(
            3, "Gestão de Usina Fotovoltaica", "gestao de usina fotovoltaica",
            "gestao de usina fotovoltaica", "guf",
        ),
        _ServicoCatalogoHub(
            4, "Gestão Mercado Livre", "gestao mercado livre",
            "gestao mercado livre", "gml",
        ),
        _ServicoCatalogoHub(5, "DECS", "decs", "decs", "decs"),
        _ServicoCatalogoHub(
            6, "Gestão de Qualidade de Energia", "gestao de qualidade de energia",
            "gestao de qualidade de energia", "gqe",
        ),
    )
