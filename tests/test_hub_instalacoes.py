"""Testes: consulta de instalações HUB (core/hub_instalacoes)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.hub_instalacoes import (
    HubInstalacoesError,
    HubInstalacoesReadError,
    consultar_instalacoes_hub,
)
from core.hub_pedido import HubPedidoError


def _mock_hub_rows(rows: list[tuple]) -> MagicMock:
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


def test_consulta_somente_codigo_cliente_lista_todas():
    mock_conn, mock_cursor = _mock_hub_rows(
        [
            (665, 352, "12345648", "UC A", "Pelotas", "RS", "S"),
            (1942, 352, "54195055", "UC B", "Rio Grande", "RS", "S"),
        ]
    )
    with patch("core.hub_instalacoes.hub_conn") as mock_hub:
        mock_hub.return_value.__enter__.return_value = mock_conn
        mock_hub.return_value.__exit__ = MagicMock(return_value=False)
        result = consultar_instalacoes_hub("352")

    assert result.codigo_cliente == 352
    assert result.formato_pipedrive == "352"
    assert result.codigos_instalacao_selecionados == ()
    assert len(result.instalacoes) == 2
    assert result.instalacoes[0].codigo == 665
    assert result.instalacoes[0].selecionada is False
    assert result.codigos_nao_encontrados == ()
    sql, params = mock_cursor.execute.call_args[0]
    assert "COD_CLIENTE" in sql
    assert params == (352,)


def test_consulta_com_instalacoes_marca_selecionadas_e_avisa_inexistentes():
    mock_conn, _ = _mock_hub_rows(
        [
            (665, 352, "12345648", "UC A", "Pelotas", "RS", "S"),
            (1942, 352, "54195055", "UC B", "Rio Grande", "RS", "N"),
        ]
    )
    with patch("core.hub_instalacoes.hub_conn") as mock_hub:
        mock_hub.return_value.__enter__.return_value = mock_conn
        mock_hub.return_value.__exit__ = MagicMock(return_value=False)
        result = consultar_instalacoes_hub("352/665,9999")

    assert result.formato_pipedrive == "352/665,9999"
    assert result.codigos_instalacao_selecionados == (665, 9999)
    assert result.instalacoes[0].selecionada is True
    assert result.instalacoes[1].selecionada is False
    assert result.instalacoes[1].ativo is False
    assert result.codigos_nao_encontrados == (9999,)


def test_consulta_mapeia_ativo_n_como_inativo():
    mock_conn, _ = _mock_hub_rows(
        [
            (2652, 352, "", "UC inativa", "Pelotas", "RS", "N"),
            (4216, 352, "4454554545", "UC ativa", "Pelotas", "RS", "S"),
        ]
    )
    with patch("core.hub_instalacoes.hub_conn") as mock_hub:
        mock_hub.return_value.__enter__.return_value = mock_conn
        mock_hub.return_value.__exit__ = MagicMock(return_value=False)
        result = consultar_instalacoes_hub("352")

    by_codigo = {i.codigo: i.ativo for i in result.instalacoes}
    assert by_codigo[2652] is False
    assert by_codigo[4216] is True


def test_consulta_rejeita_vazio():
    with pytest.raises(HubInstalacoesError, match="Informe o código"):
        consultar_instalacoes_hub("   ")


def test_consulta_rejeita_formato_invalido():
    with pytest.raises(HubInstalacoesError, match="numérico"):
        consultar_instalacoes_hub("352/abc")


def test_consulta_propaga_erro_mysql_como_read_error():
    with patch("core.hub_instalacoes.hub_conn") as mock_hub:
        mock_hub.side_effect = HubPedidoError("MySQL não configurado")
        with pytest.raises(HubInstalacoesReadError, match="MySQL"):
            consultar_instalacoes_hub("352")
