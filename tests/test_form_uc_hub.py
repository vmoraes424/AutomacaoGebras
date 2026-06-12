"""Testes: hub.instalacoes → Observações HUB (pedido_instalacao_extra + servico)."""

from __future__ import annotations

from decimal import Decimal

from core.form_uc_hub import (
    apply_hub_instalacoes,
    build_observacoes_detalhes_hub,
    format_valor_br_hub,
    normalize_hub_payload,
    servico_item_ativo,
    soma_valores_hub,
)
from core.hub_catalogo import servicos_template_hub


def _inst(codigo: int, ident: str, ativos: dict[str, str]) -> dict:
    servicos = servicos_template_hub()
    for item in servicos:
        chave = item["chave"]
        if chave in ativos:
            item["ativo"] = True
            item["valor"] = ativos[chave]
    return {
        "codigo_instalacao": codigo,
        "codigo_cliente": 352,
        "identificacao": ident,
        "servicos": servicos,
    }


def test_servico_item_ativo_somente_por_valor():
    tmpl = servicos_template_hub()[0]
    assert servico_item_ativo({**tmpl, "ativo": True, "valor": ""}) is False
    assert servico_item_ativo({**tmpl, "ativo": False, "valor": "800"}) is True


def test_build_observacoes_soma_valores_por_uc():
    instalacoes = [
        _inst(665, "00665", {"sole_web": "1000", "gestao_acl": "500.50"}),
        _inst(1942, "01942", {"sole_consultoria": "454564"}),
    ]
    texto = build_observacoes_detalhes_hub(instalacoes)
    assert "UC = 00665 - SOLE WEB + ACL = 1.500,50" in texto
    assert "UC = 01942 - Sole Consultoria = 454.564,00" in texto
    assert soma_valores_hub(instalacoes) == Decimal("456064.50")


def test_format_valor_br_hub():
    assert format_valor_br_hub(Decimal("1500.92")) == "1.500,92"
    assert format_valor_br_hub(Decimal("500")) == "500,00"


def test_normalize_migra_uc_linhas_legado():
    payload = {
        "cliente": {"codigo_cliente_instalacao": "352/665"},
        "servicos": {
            "uc_linhas": [
                {
                    "codigo_instalacao": 665,
                    "identificacao": "00665",
                    "servicos": {
                        "sole_web": {"ativo": True, "valor": "800"},
                    },
                }
            ]
        },
        "hub": {},
    }
    out = normalize_hub_payload(payload)
    assert len(out["hub"]["instalacoes"]) == 1
    inst = out["hub"]["instalacoes"][0]
    assert inst["valor_uc"] == "800"
    assert inst["servicos"][0]["codigo_servico"] == 2
    assert "SOLE WEB" in out["hub"]["observacoes_detalhes"]
    assert out["hub"]["valor_total"] == "800"


def test_apply_hub_instalacoes_codigo_pipe():
    payload = {"cliente": {}, "hub": {}}
    inst = _inst(665, "00665", {"sole_web": "100"})
    out = apply_hub_instalacoes(payload, [inst], 352)
    assert out["cliente"]["codigo_cliente_instalacao"] == "352/665"
    assert out["hub"]["valor_total"] == "100"


def test_normalize_sincroniza_codigo_p1_com_matriz_uc():
    """P1 legado no Pipe não pode divergir da matriz hub.instalacoes."""
    payload = {
        "cliente": {"codigo_cliente_instalacao": "222/451, 1629, 1630"},
        "hub": {
            "instalacoes": [
                _inst(451, "451", {"sole_web": "100"}),
                _inst(1629, "1629", {"sole_web": "200"}),
                _inst(1630, "1630", {}),
            ],
            "observacoes_detalhes": (
                "UC = 451 - SOLE WEB = 100,00; UC = 1629 - SOLE WEB = 200,00"
            ),
        },
    }
    out = normalize_hub_payload(payload)
    assert out["cliente"]["codigo_cliente_instalacao"] == "222/451,1629"
    assert out["hub"]["observacoes_detalhes"].count("UC =") == 2


def test_normalize_tres_ucs_ativas_mantem_tres_no_p1():
    payload = {
        "cliente": {"codigo_cliente_instalacao": "222/451, 1629"},
        "hub": {
            "instalacoes": [
                _inst(451, "451", {"sole_web": "100"}),
                _inst(1629, "1629", {"sole_web": "200"}),
                _inst(1630, "1630", {"gestao_acl": "300"}),
            ],
        },
    }
    out = normalize_hub_payload(payload)
    assert out["cliente"]["codigo_cliente_instalacao"] == "222/451,1629,1630"
    assert out["hub"]["observacoes_detalhes"].count("UC =") == 3


def test_validate_nao_acusa_mismatch_quando_matriz_sincroniza_p1():
    from unittest.mock import patch

    from core.form_validation_v1 import validate_form_payload_v1

    payload = {
        "schema_version": "v1",
        "cliente": {"codigo_cliente_instalacao": "222/451, 1629, 1630"},
        "hub": {
            "instalacoes": [
                _inst(451, "451", {"sole_web": "100"}),
                _inst(1629, "1629", {"sole_web": "200"}),
                _inst(1630, "1630", {}),
            ],
        },
        "anexos": {"proposta_comercial_anexada": True},
    }
    patches = (
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
    )
    for p in patches:
        p.start()
    try:
        errors = validate_form_payload_v1(746, payload)
    finally:
        for p in patches:
            p.stop()
    assert not any("Observações (Detalhes)" in msg for msg in errors.values())
    assert "cliente.codigo_cliente_instalacao" not in errors
