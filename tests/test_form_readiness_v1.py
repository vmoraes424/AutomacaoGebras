"""Testes form_readiness_v1."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.form_readiness_v1 import (
    build_form_readiness,
    inspect_deal_attachments,
    invalidate_deal_attachments_cache,
)


@pytest.fixture
def payload_minimo():
    return {
        "schema_version": "v1",
        "cliente": {"contratante": "Teste"},
        "anexos": {"proposta_comercial_anexada": False},
    }


def test_build_readiness_retorna_secoes(payload_minimo):
    out = build_form_readiness(746, payload_minimo)

    assert out["deal_id"] == 746
    assert "sections" in out
    assert out["summary"]["total"] > 0
    assert out.get("attachments_deferred") is True
    assert "contrato" not in out
    section_ids = {s["id"] for s in out["sections"]}
    assert "cliente" in section_ids
    assert "anexos" not in section_ids


def test_proposta_pipe_marca_anexo_ok(payload_minimo):
    pipe_attachments = {
        "proposta_comercial_anexada": True,
        "contrato_template": {"source": "padrao", "filename": None},
        "attachments_error": None,
    }
    with patch("core.form_readiness_v1.inspect_deal_attachments", return_value=pipe_attachments):
        out = build_form_readiness(746, payload_minimo, interactive=False)

    anexos = next(s for s in out["sections"] if s["id"] == "anexos")
    proposta = next(i for i in anexos["items"] if i["id"] == "anexos.proposta_comercial_anexada")
    assert proposta["status"] == "ok"


def test_readiness_interativo_exclui_anexos(payload_minimo):
    with patch("core.form_readiness_v1.inspect_deal_attachments") as mock_att:
        out = build_form_readiness(746, payload_minimo, interactive=True)
        mock_att.assert_not_called()

    assert out.get("attachments_deferred") is True
    assert "contrato" not in out
    section_ids = {s["id"] for s in out["sections"]}
    assert "anexos" not in section_ids


def test_hub_section_com_matriz_uc(payload_minimo):
    payload = {
        **payload_minimo,
        "cliente": {
            **payload_minimo.get("cliente", {}),
            "codigo_cliente_instalacao": "352/665",
        },
        "hub": {
            "instalacoes": [
                {
                    "codigo_instalacao": 665,
                    "codigo_cliente": 352,
                    "identificacao": "00665",
                    "servicos": [
                        {
                            "chave": "sole_web",
                            "nome": "SOLE Web",
                            "nome_pipe": "SOLE WEB",
                            "ativo": True,
                            "valor": "100",
                        }
                    ],
                }
            ],
            "observacoes_detalhes": "",
        },
    }
    with patch("core.form_readiness_v1.inspect_deal_attachments") as mock_att, patch(
        "core.form_readiness_v1.validate_form_payload_v1", return_value={}
    ):
        mock_att.return_value = {
            "proposta_comercial_anexada": False,
            "contrato_template": {"source": "padrao", "filename": None},
            "attachments_error": None,
        }
        out = build_form_readiness(746, payload)

    hub = next(s for s in out["sections"] if s["id"] == "hub")
    assert hub["total"] == 1
    assert hub["completed"] == 1
    assert hub["items"][0]["id"] == "_hub_uc_matrix"
    assert hub["items"][0]["status"] == "ok"


def test_hub_section_legacy_observacoes(payload_minimo):
    payload = {
        **payload_minimo,
        "hub": {"observacoes_detalhes": "UC = 00665 - SOLE WEB = 100,00"},
    }
    with patch("core.form_readiness_v1.inspect_deal_attachments") as mock_att:
        mock_att.return_value = {
            "proposta_comercial_anexada": False,
            "contrato_template": {"source": "padrao", "filename": None},
            "attachments_error": None,
        }
        out = build_form_readiness(746, payload)

    hub = next(s for s in out["sections"] if s["id"] == "hub")
    assert hub["total"] == 1
    assert hub["items"][0]["id"] == "hub.observacoes_detalhes"


def test_interactive_pula_validacao_plune(payload_minimo):
    with patch("core.form_validation_v1._validar_plune") as mock_plune:
        from core.form_validation_v1 import validate_form_payload_v1

        validate_form_payload_v1(746, payload_minimo, interactive=True)
        mock_plune.assert_not_called()


def test_interactive_nao_forca_sync_plune():
    from core.form_schema_v1 import form_payload_to_deal_dict, parse_form_payload_v1
    from core.form_validation_v1 import _validar_plune

    payload = {
        "schema_version": "v1",
        "comercial": {"filial": "Matriz", "regional": "Regional 1", "consultor": "Consultor X"},
    }
    parsed = parse_form_payload_v1(payload)
    deal = form_payload_to_deal_dict(746, parsed)

    with patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos") as mock_sync:
        mock_sync.return_value = 0
        with patch("core.form_validation_v1.resolver_subcentro", return_value="99"):
            _validar_plune(deal, {}, interactive=True)
        mock_sync.assert_not_called()


def test_attachments_cache_reutiliza():
    invalidate_deal_attachments_cache()
    with patch("core.form_readiness_v1.listar_arquivos_deal") as mock_list:
        mock_list.return_value = []
        inspect_deal_attachments(746)
        inspect_deal_attachments(746)
        assert mock_list.call_count == 1


def test_contrato_custom_quando_template_no_pipe():
    invalidate_deal_attachments_cache()
    with patch("core.form_readiness_v1.listar_arquivos_deal") as mock_list:
        mock_list.return_value = [
            {"id": 1, "file_type": "docx", "name": "contrato_padrao - Cliente X.docx", "add_time": "2026-01-01"},
        ]
        att = inspect_deal_attachments(746)

    assert att["contrato_template"]["source"] == "custom"
    assert "contrato_padrao" in (att["contrato_template"]["filename"] or "")
