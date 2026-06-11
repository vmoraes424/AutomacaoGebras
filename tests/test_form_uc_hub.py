"""Testes: hub.instalacoes → Observações HUB (pedido_instalacao_extra + servico)."""

from __future__ import annotations

from decimal import Decimal

from core.form_uc_hub import (
    apply_hub_instalacoes,
    build_observacoes_detalhes_hub,
    format_valor_br_hub,
    normalize_hub_payload,
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
