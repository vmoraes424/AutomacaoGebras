"""Testes — limpeza de templates baixados do Pipedrive."""

from __future__ import annotations

import os
from unittest.mock import patch

import core.automacao_contrato as automacao


def _touch(pasta: str, nome: str) -> str:
    caminho = os.path.join(pasta, nome)
    with open(caminho, "wb") as f:
        f.write(b"x")
    return caminho


def test_limpar_templates_locais_deal_mantem_atual(tmp_path, monkeypatch):
    monkeypatch.setattr(automacao, "_PASTA_TEMPLATES_RUNTIME", str(tmp_path))
    atual = _touch(
        str(tmp_path), "template_contrato_padrao_746_2743_44eab0d993.docx"
    )
    antigo = _touch(
        str(tmp_path), "template_contrato_padrao_746_2739_5f62ed2f95.docx"
    )
    outro_deal = _touch(
        str(tmp_path), "template_contrato_padrao_999_1000_abc.docx"
    )

    removidos = automacao.limpar_templates_locais_deal("746", manter=atual)

    assert removidos == 1
    assert os.path.isfile(atual)
    assert not os.path.isfile(antigo)
    assert os.path.isfile(outro_deal)


def test_limpar_templates_orfaos_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(automacao, "_PASTA_TEMPLATES_RUNTIME", str(tmp_path))
    ativo = _touch(str(tmp_path), "template_contrato_padrao_746_2743_a.docx")
    orfao = _touch(str(tmp_path), "template_contrato_padrao_746_2739_b.docx")
    _touch(str(tmp_path), "outro_arquivo.docx")

    class FakeConn:
        def execute(self, *_args, **_kwargs):
            return self

        def fetchall(self):
            return [{"template_local_path": ativo}]

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    with patch("core.database.db_conn", return_value=FakeConn()):
        removidos = automacao.limpar_templates_orfaos_runtime()

    assert removidos == 1
    assert os.path.isfile(ativo)
    assert not os.path.isfile(orfao)
    assert os.path.isfile(os.path.join(str(tmp_path), "outro_arquivo.docx"))
