"""Integração form → deal → pedido HUB (mock MySQL + staging opcional).

Rodar unitários (CI/local, sem MySQL):

    pytest tests/test_form_hub_pedido_integration.py -v

Rodar contra MySQL gebras (staging/manual):

    RUN_HUB_MYSQL=1 pytest tests/test_form_hub_pedido_integration.py -m hub_mysql -v

Variáveis opcionais para staging (defaults = pedido 841 de referência):

    HUB_TEST_CODIGO_CLIENTE=352
    HUB_TEST_CODIGO_INSTALACAO=12108
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.automacao_config import AutomacaoConfig
from core.form_deal_adapter import merge_form_into_deal
from core.form_schema_v1 import parse_form_payload_v1
from core.form_uc_hub import apply_hub_instalacoes
from core.hub_catalogo import servicos_template_hub
from core.hub_pedido import (
    HubPedidoError,
    _inserir_filhos_pedido_hub,
    _montar_dados_pedido_hub_deal,
    criar_pedido_hub,
    hub_conn,
    remover_pedido_hub,
)
from core.pipedrive_fields import (
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_OBSERVACOES_DETALHES,
    get_val,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"

pytestmark_hub_mysql = pytest.mark.hub_mysql

_requires_hub_mysql = pytest.mark.skipif(
    os.environ.get("RUN_HUB_MYSQL") != "1",
    reason="defina RUN_HUB_MYSQL=1 para INSERT real no MySQL gebras",
)


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _ativar_servicos_por_chave(
    servicos: list[dict], valores: dict[str, str]
) -> list[dict]:
    out = []
    for item in servicos:
        row = dict(item)
        if row["chave"] in valores:
            row["ativo"] = True
            row["valor"] = valores[row["chave"]]
        out.append(row)
    return out


def _buscar_identificacao_hub(codigo_instalacao: int, codigo_cliente: int) -> str:
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(IDENTIFICACAO, '')
                FROM instalacao
                WHERE CODIGO = %s AND COD_CLIENTE = %s
                LIMIT 1
                """,
                (codigo_instalacao, codigo_cliente),
            )
            row = cur.fetchone()
    if not row:
        return str(codigo_instalacao).zfill(5)
    ident = str(row[0] or "").strip()
    return ident or str(codigo_instalacao).zfill(5)


def _resolver_par_teste_mysql() -> tuple[int, int, str]:
    """Par cliente/instalação existente no HUB (env ou auto-descoberta)."""
    from core.hub_pedido import _validar_instalacao_hub

    env_cliente = os.environ.get("HUB_TEST_CODIGO_CLIENTE")
    env_inst = os.environ.get("HUB_TEST_CODIGO_INSTALACAO")
    if env_cliente and env_inst:
        codigo_cliente = int(env_cliente)
        codigo_instalacao = int(env_inst)
        try:
            _validar_instalacao_hub(codigo_instalacao, codigo_cliente)
        except HubPedidoError as exc:
            pytest.skip(str(exc))
        return (
            codigo_cliente,
            codigo_instalacao,
            _buscar_identificacao_hub(codigo_instalacao, codigo_cliente),
        )

    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COD_CLIENTE, CODIGO, COALESCE(IDENTIFICACAO, '')
                FROM instalacao
                ORDER BY CODIGO DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()
    if not row:
        pytest.skip("tabela instalacao vazia no HUB")
    codigo_cliente = int(row[0])
    codigo_instalacao = int(row[1])
    ident = str(row[2] or "").strip() or str(codigo_instalacao).zfill(5)
    return codigo_cliente, codigo_instalacao, ident


def form_payload_para_instalacao(
    codigo_cliente: int,
    codigo_instalacao: int,
    identificacao: str,
) -> dict:
    servicos = _ativar_servicos_por_chave(
        servicos_template_hub(),
        {
            "sole_consultoria": "650",
            "sole_web": "650",
            "gestao_usina_fotovoltaica": "650",
        },
    )
    instalacao = {
        "codigo_instalacao": codigo_instalacao,
        "codigo_cliente": codigo_cliente,
        "identificacao": identificacao,
        "razao_social": "UC Teste Integração",
        "cidade": "Pelotas",
        "uf": "RS",
        "valor_uc": "",
        "servicos": servicos,
    }
    base = _load("form_payload_v1_g1.json")
    base["cliente"]["codigo_cliente_instalacao"] = f"{codigo_cliente}/{codigo_instalacao}"
    base["hub"] = {"instalacoes": [], "observacoes_detalhes": "", "valor_total": ""}
    return apply_hub_instalacoes(base, [instalacao], codigo_cliente)


def form_payload_estilo_pedido_841() -> dict:
    """Matriz hub.instalacoes — referência pedido 841 (UC 12108, SC+SW+GUF = 1.950)."""
    return form_payload_para_instalacao(352, 12108, "625700568")


def deal_pipe_base(deal_id: int = 888001) -> dict:
    deal = _load("deal_pipe_g1.json")
    deal = deepcopy(deal)
    deal["id"] = deal_id
    deal["title"] = "Contrato Integração HUB Teste"
    return deal


def deal_merged_do_form(form: dict | None = None, deal_id: int = 888001) -> dict:
    form = form or form_payload_estilo_pedido_841()
    return merge_form_into_deal(deal_pipe_base(deal_id), form)


class RecordingCursor:
    """Captura SQL executado (mock hub_conn)."""

    def __init__(self, *, lastrowid: int = 9001, fetchall_rows: list[tuple] | None = None) -> None:
        self.executions: list[tuple[str, tuple]] = []
        self.lastrowid = lastrowid
        self.fetchall_rows = list(fetchall_rows or [])

    def execute(self, sql: str, params=None) -> None:
        self.executions.append((sql.strip(), params or ()))

    def fetchall(self) -> list[tuple]:
        return list(self.fetchall_rows)

    def __enter__(self):
        return self

    def __exit__(self, *args) -> bool:
        return False


def _hub_patches(*, deal: dict, cursor: RecordingCursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    return (
        patch(
            "core.hub_pedido.get_automacao_config",
            return_value=AutomacaoConfig(pular_hub=False),
        ),
        patch("core.hub_pedido.HUB_CODIGO_USUARIO_SISTEMA", -3),
        patch("core.hub_pedido.buscar_por_deal_id", return_value={}),
        patch("core.hub_pedido.buscar_deal_por_id", return_value=deal),
        patch("core.hub_pedido._validar_instalacoes_hub"),
        patch("core.hub_pedido._id_plune_recorrente_para_hub", return_value=777001),
        patch("core.hub_pedido.get_enum_label", return_value="15%"),
        patch("core.hub_pedido.marcar_hub_pedido_criado"),
        patch("core.hub_pedido.hub_conn", return_value=mock_conn),
        patch("core.hub_pedido._catalogo_servicos_hub", new=_mock_catalogo_hub),
    )


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


def _sqls(cursor: RecordingCursor) -> list[str]:
    return [sql for sql, _ in cursor.executions]


def _params_por_tabela(cursor: RecordingCursor, fragmento: str) -> list[tuple]:
    return [params for sql, params in cursor.executions if fragmento in sql]


class TestFormParaMontarPedidoHub:
    """form → merge → observacoes matriz → _montar_dados_pedido_hub_deal."""

    def test_parse_form_normaliza_hub_instalacoes(self):
        raw = form_payload_estilo_pedido_841()
        parsed = parse_form_payload_v1(raw)
        assert len(parsed.hub.instalacoes) == 1
        inst = parsed.hub.instalacoes[0]
        assert inst.codigo_instalacao == 12108
        assert inst.valor_uc == "1950"
        ativos = [s for s in inst.servicos if s.ativo]
        assert len(ativos) == 3
        assert parsed.hub.valor_total == "1950"

    def test_merge_form_gera_observacoes_detalhes(self):
        form = form_payload_estilo_pedido_841()
        merged = deal_merged_do_form(form)
        obs = get_val(merged, FIELD_OBSERVACOES_DETALHES)
        assert "625700568" in obs
        assert "SOLE WEB" in obs
        assert "1.950,00" in obs
        assert get_val(merged, FIELD_CODIGO_CLIENTE_INSTALACAO) == "352/12108"

    def test_montar_dados_linhas_servico_e_valor(self):
        merged = deal_merged_do_form()
        patches = _hub_patches(deal=merged, cursor=RecordingCursor())
        for p in patches:
            p.start()
        try:
            dados = _montar_dados_pedido_hub_deal("888001", merged)
        finally:
            for p in patches:
                p.stop()

        assert dados["codigo_cliente"] == 352
        assert dados["codigos_instalacao"] == [12108]
        assert dados["valor_decimal"] == Decimal("1950.00")
        assert len(dados["linhas_obs"]) == 1
        linha = dados["linhas_obs"][0]
        assert linha.codigo_instalacao == 12108
        assert linha.identificacao == "625700568"
        assert set(linha.servicos) == {1, 2, 3}
        assert linha.valor == Decimal("1950.00")


class TestCriarPedidoHubComDealDoForm:
    """criar_pedido_hub com deal montado a partir do form — INSERT mockado."""

    def test_criar_pedido_hub_inserts_pedido_extra_servico(self):
        merged = deal_merged_do_form()
        cursor = RecordingCursor(lastrowid=9001)
        patches = _hub_patches(deal=merged, cursor=cursor)
        for p in patches:
            p.start()
        try:
            out = criar_pedido_hub("888001", parceiro_plune_criado=False)
        finally:
            for p in patches:
                p.stop()

        assert out["status"] == "created"
        assert out["pedido_hub_id"] == 9001
        assert out["codigo_cliente"] == 352
        assert out["codigos_instalacao"] == [12108]
        assert set(out["instalacoes_obs"][0]["servicos"]) == {1, 2, 3}
        assert out["instalacoes_obs"][0]["valor"] == "1950.00"
        assert out["instalacoes_ativadas"] == []

        sqls = _sqls(cursor)
        assert any("INSERT INTO pedido" in s for s in sqls)
        assert any("SELECT CODIGO" in s and "instalacao" in s for s in sqls)
        assert any("INSERT INTO pedido_instalacao_extra" in s for s in sqls)
        assert any("INSERT INTO pedido_instalacao_servico" in s for s in sqls)
        assert any("INSERT INTO pedido_plune" in s for s in sqls)

        pedido_params = _params_por_tabela(cursor, "INSERT INTO pedido")[0]
        assert pedido_params[-1] == Decimal("1950.00")

        extra_params = _params_por_tabela(cursor, "pedido_instalacao_extra")[0]
        assert extra_params[0] == 9001
        assert extra_params[1] == 12108
        assert extra_params[3] == Decimal("1950.00")

        svc_params = _params_por_tabela(cursor, "pedido_instalacao_servico")
        assert len(svc_params) == 3
        assert {(p[0], p[1], p[2]) for p in svc_params} == {
            (9001, 12108, 1),
            (9001, 12108, 2),
            (9001, 12108, 3),
        }

    def test_inserir_filhos_pedido_hub_isolado(self):
        merged = deal_merged_do_form()
        patches = (
            patch("core.hub_pedido._validar_instalacoes_hub"),
            patch("core.hub_pedido._id_plune_recorrente_para_hub", return_value=777001),
            patch("core.hub_pedido.get_enum_label", return_value="15%"),
            patch("core.hub_pedido._catalogo_servicos_hub", new=_mock_catalogo_hub),
        )
        for p in patches:
            p.start()
        try:
            dados = _montar_dados_pedido_hub_deal("888001", merged)
        finally:
            for p in patches:
                p.stop()

        cursor = RecordingCursor()
        _inserir_filhos_pedido_hub(
            cursor,
            9002,
            dados["linhas_obs"],
            tem_perc_economia=True,
            perc_economia=Decimal("15.00"),
            codigo_plune_recorrente=777001,
        )
        extras = _params_por_tabela(cursor, "pedido_instalacao_extra")
        servicos = _params_por_tabela(cursor, "pedido_instalacao_servico")
        assert len(extras) == 1
        assert extras[0][3] == Decimal("1950.00")
        assert len(servicos) == 3


@_requires_hub_mysql
@pytest.mark.integration
@pytestmark_hub_mysql
class TestCriarPedidoHubMysqlStaging:
    """INSERT real no MySQL gebras — só staging/manual (limpa pedido ao final)."""

    def test_criar_e_verificar_pedido_mysql(self):
        from core.config import MYSQL_HOST, MYSQL_USER

        if not MYSQL_HOST or not MYSQL_USER:
            pytest.skip("MYSQL_HOST/MYSQL_USER não configurados no .env")

        codigo_cliente, codigo_instalacao, identificacao = _resolver_par_teste_mysql()
        deal_id = os.environ.get("HUB_TEST_DEAL_ID", "888001")

        form = form_payload_para_instalacao(
            codigo_cliente, codigo_instalacao, identificacao
        )
        merged = merge_form_into_deal(deal_pipe_base(int(deal_id)), form)

        codigo_pedido: int | None = None
        patches = (
            patch(
            "core.hub_pedido.get_automacao_config",
            return_value=AutomacaoConfig(pular_hub=False),
        ),
            patch("core.hub_pedido.HUB_CODIGO_USUARIO_SISTEMA", -3),
            patch("core.hub_pedido.buscar_por_deal_id", return_value={}),
            patch("core.hub_pedido.buscar_deal_por_id", return_value=merged),
            patch("core.hub_pedido._id_plune_recorrente_para_hub", return_value=777001),
            patch("core.hub_pedido.get_enum_label", return_value="15%"),
            patch("core.hub_pedido.marcar_hub_pedido_criado"),
            patch("core.hub_pedido._catalogo_servicos_hub", new=_mock_catalogo_hub),
        )
        for p in patches:
            p.start()
        try:
            out = criar_pedido_hub(deal_id, parceiro_plune_criado=False)
            assert out["status"] == "created", out
            codigo_pedido = int(out["pedido_hub_id"])
        finally:
            for p in patches:
                p.stop()

        try:
            with hub_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT valorTotal FROM pedido WHERE codigo = %s",
                        (codigo_pedido,),
                    )
                    row = cur.fetchone()
                    assert row is not None
                    assert Decimal(str(row[0])) == Decimal("1950.00")

                    cur.execute(
                        """
                        SELECT codigoInstalacao, valor
                        FROM pedido_instalacao_extra
                        WHERE codigoPedido = %s
                        """,
                        (codigo_pedido,),
                    )
                    extras = cur.fetchall()
                    assert len(extras) == 1
                    assert extras[0][0] == codigo_instalacao
                    assert Decimal(str(extras[0][1])) == Decimal("1950.00")

                    cur.execute(
                        """
                        SELECT codigoServico
                        FROM pedido_instalacao_servico
                        WHERE codigoPedido = %s AND codigoInstalacao = %s
                        ORDER BY codigoServico
                        """,
                        (codigo_pedido, codigo_instalacao),
                    )
                    servicos_db = [r[0] for r in cur.fetchall()]
                    assert servicos_db == [1, 2, 3]
        finally:
            if codigo_pedido:
                remover_pedido_hub(codigo_pedido)

    def test_instalacao_inexistente_falha_validacao(self):
        from core.config import MYSQL_HOST

        if not MYSQL_HOST:
            pytest.skip("MYSQL não configurado")

        merged = deal_merged_do_form()
        cf = merged.setdefault("custom_fields", {})
        cf[FIELD_CODIGO_CLIENTE_INSTALACAO] = "352/999999999"

        with pytest.raises(HubPedidoError, match="não encontrada"):
            _montar_dados_pedido_hub_deal("888001", merged)
