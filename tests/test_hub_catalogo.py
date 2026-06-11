"""Catálogo pedido_nome_servico."""

from __future__ import annotations

from core.hub_catalogo import listar_servicos_hub_catalogo, servicos_template_hub


def test_catalogo_tem_cinco_servicos_form():
    cats = listar_servicos_hub_catalogo()
    assert len(cats) == 5
    chaves = {c.chave for c in cats}
    assert "sole_web" in chaves
    assert "gestao_acl" in chaves


def test_template_alinhado_catalogo():
    tmpl = servicos_template_hub()
    cats = listar_servicos_hub_catalogo()
    assert len(tmpl) == len(cats)
    assert tmpl[0]["codigo_servico"] == cats[0].codigo_servico
