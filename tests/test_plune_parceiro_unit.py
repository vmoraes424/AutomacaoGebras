"""Testes unitários: criação e resolução de parceiro/cliente Plune (Parceiro.tbParceiro).

Fluxo documentado em docs/Plune/Clientes/Clientes.md — deal ganho no Pipedrive,
Browse por CNPJ; se não existir, Insert com dados do pipe (CEP obrigatório).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.pipedrive_fields import (
    FIELD_CEP,
    FIELD_CIDADE,
    FIELD_CONTATO_CONTRATANTE,
    FIELD_DOCUMENTO,
    FIELD_ENDERECO,
    FIELD_NOME_CLIENTE,
)
from core.pipedrive_validations import DealValidationError
from core.plune_pedido import (
    PluneError,
    _buscar_parceiros_por_documento,
    _campo_tipo_parceiro_browse,
    _criar_parceiro,
    _escolher_parceiro_por_documento,
    _montar_params_parceiro,
    _normalizar_uf_plune,
    _resolver_ou_criar_parceiro,
    _tipo_parceiro_flags,
)


def _deal_novo_cliente(*, deal_id: int = 746) -> dict:
    """Deal Pipedrive com campos mínimos para Insert de parceiro novo."""
    return {
        "id": deal_id,
        "title": "BIView Ltda",
        "custom_fields": {
            FIELD_NOME_CLIENTE: "BIView Gestão de Energia Ltda",
            FIELD_DOCUMENTO: "07.936.028/0001-84",
            FIELD_ENDERECO: "Rua Exemplo, 100",
            FIELD_CIDADE: "Pelotas/RS",
            FIELD_CEP: "96015-560",
            FIELD_CONTATO_CONTRATANTE: "contato@biview.com.br",
        },
    }


def _parceiro_plune_row(
    *,
    parceiro_id: str = "5001",
    documento: str = "07936028000184",
    razao: str = "BIView Gestão de Energia Ltda",
) -> dict:
    return {
        "id": parceiro_id,
        "documento": documento,
        "documento_formatado": "07.936.028/0001-84",
        "razao_social": razao,
        "nome_fantasia": razao,
        "e_cliente": "1",
        "e_fornecedor": "0",
        "endereco": "Rua Exemplo, 100",
        "bairro": "",
        "cidade": "Pelotas",
        "uf": "RS",
        "cep": "96015560",
        "email": "",
        "contato": "",
    }


class TestNormalizarUfPlune:
    @pytest.mark.parametrize(
        "entrada,esperado",
        [
            ("RS", "RS"),
            ("sp", "SP"),
            ("RS - Rio Grande do Sul", "RS"),
            ("SP - São Paulo", "SP"),
            ("Rio Grande do Sul", "RS"),
            ("Santa Catarina", "SC"),
            ("São Paulo", "SP"),
            ("Minas Gerais", "MG"),
            ("Rio de Janeiro", "RJ"),
            ("Mato Grosso do Sul", "MS"),
            ("Distrito Federal", "DF"),
            ("", ""),
            ("Texto inválido", ""),
        ],
    )
    def test_converte_formatos_comuns(self, entrada, esperado):
        assert _normalizar_uf_plune(entrada) == esperado


class TestTipoParceiroFlags:
    def test_padrao_cliente(self):
        with patch("core.plune_pedido.PLUNE_PARCEIRO_TIPO", "cliente"):
            assert _tipo_parceiro_flags() == ("1", "0")
            assert _campo_tipo_parceiro_browse() == "ECliente"

    def test_fornecedor(self):
        with patch("core.plune_pedido.PLUNE_PARCEIRO_TIPO", "fornecedor"):
            assert _tipo_parceiro_flags() == ("0", "1")
            assert _campo_tipo_parceiro_browse() == "EFornecedor"


class TestMontarParamsParceiro:
    def test_monta_insert_com_dados_pipedrive_normalizados(self):
        params = _montar_params_parceiro(_deal_novo_cliente())

        assert params["NomRazaoSocial"] == "BIView Gestão de Energia Ltda"
        assert params["NomFantasia"] == "BIView Gestão de Energia Ltda"
        assert params["NumeroContribuinte"] == "07936028000184"
        assert params["CEPPrincipal"] == "96015560"
        assert params["EnderecoPrincipal"] == "Rua Exemplo, 100"
        assert params["CidadePrincipalEx"] == "Pelotas/RS"
        assert params["ContatoNome"] == "contato@biview.com.br"
        assert params["ECliente"] == "1"
        assert params["EFornecedor"] == "0"
        assert params["Ativo"] == "1"
        assert "746" in params["Obs"]

    def test_sem_nome_levanta_plune_error(self):
        deal = _deal_novo_cliente()
        deal["custom_fields"][FIELD_NOME_CLIENTE] = ""
        with pytest.raises(PluneError, match="razão social"):
            _montar_params_parceiro(deal)

    def test_sem_documento_levanta_plune_error(self):
        deal = _deal_novo_cliente()
        deal["custom_fields"][FIELD_DOCUMENTO] = ""
        with pytest.raises(PluneError, match="CPF/CNPJ"):
            _montar_params_parceiro(deal)

    def test_cep_invalido_levanta_plune_error(self):
        deal = _deal_novo_cliente()
        deal["custom_fields"][FIELD_CEP] = "123"
        with pytest.raises(PluneError, match="CEP válido"):
            _montar_params_parceiro(deal)


class TestCriarParceiro:
    @patch("core.plune_pedido._buscar_parceiro_por_id")
    @patch("core.plune_pedido._plune_get")
    def test_insert_parceiro_chama_api_com_prefixo(self, mock_plune, mock_select):
        mock_plune.return_value = {
            "Field": {"ParceiroId": {"value": "5001"}},
        }
        mock_select.return_value = _parceiro_plune_row()

        parceiro = _criar_parceiro(_deal_novo_cliente())

        mock_plune.assert_called_once()
        class_id, method, params = mock_plune.call_args.args
        assert class_id == "Parceiro.tbParceiro"
        assert method == "Insert"
        assert params["Parceiro.tbParceiro.NumeroContribuinte"] == "07936028000184"
        assert params["Parceiro.tbParceiro.ECliente"] == "1"
        assert params["Parceiro.tbParceiro.CEPPrincipal"] == "96015560"
        mock_select.assert_called_once_with("5001")
        assert parceiro["id"] == "5001"

    @patch("core.plune_pedido._plune_get")
    def test_insert_sem_parceiro_id_levanta_erro(self, mock_plune):
        mock_plune.return_value = {"Field": {}}
        with pytest.raises(PluneError, match="sem ParceiroId"):
            _criar_parceiro(_deal_novo_cliente())


class TestEscolherParceiroPorDocumento:
    def test_retorna_unico_candidato(self):
        candidato = _parceiro_plune_row()
        escolhido = _escolher_parceiro_por_documento(
            [candidato], "07.936.028/0001-84", "BIView"
        )
        assert escolhido is candidato

    def test_desambigua_por_razao_social(self):
        a = _parceiro_plune_row(parceiro_id="1", razao="Empresa A Ltda")
        b = _parceiro_plune_row(parceiro_id="2", razao="Empresa B Ltda")
        escolhido = _escolher_parceiro_por_documento(
            [a, b],
            "07936028000184",
            "Empresa B Ltda",
        )
        assert escolhido["id"] == "2"

    def test_multiplos_sem_razao_levanta_erro(self):
        a = _parceiro_plune_row(parceiro_id="1")
        b = _parceiro_plune_row(parceiro_id="2")
        with pytest.raises(PluneError, match="Múltiplos parceiros"):
            _escolher_parceiro_por_documento([a, b], "07936028000184", "")


class TestResolverOuCriarParceiro:
    @patch("core.plune_pedido._buscar_parceiro_por_id")
    @patch("core.plune_pedido._buscar_parceiros_por_documento")
    def test_reutiliza_parceiro_existente(self, mock_browse, mock_select):
        existente = {"id": "100", "documento": "07936028000184", "razao_social": "BIView"}
        mock_browse.return_value = [existente]
        mock_select.return_value = _parceiro_plune_row(parceiro_id="100")

        parceiro, criado = _resolver_ou_criar_parceiro(_deal_novo_cliente())

        assert criado is False
        assert parceiro["id"] == "100"
        mock_select.assert_called_once_with("100")

    @patch("core.plune_pedido._criar_parceiro")
    @patch("core.plune_pedido._buscar_parceiros_por_documento", return_value=[])
    def test_cria_parceiro_quando_nao_existe_no_plune(self, _browse, mock_criar):
        mock_criar.return_value = _parceiro_plune_row()

        parceiro, criado = _resolver_ou_criar_parceiro(_deal_novo_cliente())

        assert criado is True
        mock_criar.assert_called_once()
        assert parceiro["documento"] == "07936028000184"

    @patch("core.plune_pedido._buscar_parceiros_por_documento", return_value=[])
    def test_sem_cep_reabre_deal_quando_precisa_criar(self, _browse):
        deal = _deal_novo_cliente()
        deal["custom_fields"][FIELD_CEP] = ""

        with pytest.raises(DealValidationError) as exc:
            _resolver_ou_criar_parceiro(deal)

        assert exc.value.deal_id == "746"
        assert any("CEP" in msg for msg in exc.value.mensagens)
        assert any("criar um cadastro novo" in msg for msg in exc.value.mensagens)

    def test_sem_documento_no_deal_levanta_plune_error(self):
        deal = _deal_novo_cliente()
        deal["custom_fields"][FIELD_DOCUMENTO] = ""
        with pytest.raises(PluneError, match="CPF/CNPJ"):
            _resolver_ou_criar_parceiro(deal)


class TestBuscarParceirosPorDocumento:
    @patch("core.plune_pedido._plune_get")
    def test_browse_filtra_por_eciente(self, mock_plune):
        mock_plune.return_value = {
            "data": {
                "row": [
                    {
                        "ParceiroId": {"value": "5001"},
                        "NumeroContribuinte": {
                            "value": "07936028000184",
                            "resolved": "07.936.028/0001-84",
                        },
                        "NomRazaoSocial": {"value": "BIView"},
                        "NomFantasia": {"value": ""},
                        "ECliente": {"value": "1"},
                        "EFornecedor": {"value": "0"},
                        "EnderecoPrincipal": {"value": ""},
                        "BairroPrincipal": {"value": ""},
                        "CidadePrincipalEx": {"value": "Pelotas"},
                        "UFPrincipalId": {"value": "RS"},
                        "CEPPrincipal": {"value": "96015560"},
                        "ContatoNome": {"value": ""},
                        "EMail": {"value": ""},
                    }
                ]
            }
        }

        with patch("core.plune_pedido.PLUNE_PARCEIRO_TIPO", "cliente"):
            parceiros = _buscar_parceiros_por_documento("07.936.028/0001-84")

        _, _, params = mock_plune.call_args.args
        assert params["Parceiro.tbParceiro.ECliente"] == "1"
        assert params["Parceiro.tbParceiro.NumeroContribuinte"] == "07936028000184"
        assert len(parceiros) == 1
        assert parceiros[0]["documento"] == "07936028000184"

    @patch("core.plune_pedido._plune_get")
    def test_browse_uf_apenas_em_resolved(self, mock_plune):
        mock_plune.return_value = {
            "data": {
                "row": [
                    {
                        "ParceiroId": {"value": "5001"},
                        "NumeroContribuinte": {"value": "07936028000184"},
                        "NomRazaoSocial": {"value": "BIView"},
                        "NomFantasia": {"value": ""},
                        "ECliente": {"value": "1"},
                        "EFornecedor": {"value": "0"},
                        "EnderecoPrincipal": {"value": ""},
                        "BairroPrincipal": {"value": ""},
                        "CidadePrincipalId": {
                            "value": "1234",
                            "resolved": "Pelotas",
                        },
                        "UFPrincipalId": {
                            "value": "",
                            "resolved": "RS - Rio Grande do Sul",
                        },
                        "CEPPrincipal": {"value": ""},
                        "ContatoNome": {"value": ""},
                        "EMail": {"value": ""},
                    }
                ]
            }
        }

        parceiros = _buscar_parceiros_por_documento("07.936.028/0001-84")

        assert parceiros[0]["cidade"] == "Pelotas"
        assert parceiros[0]["uf"] == "RS"

    @patch("core.plune_pedido._plune_get")
    def test_browse_uf_value_e_resolved_nome_completo(self, mock_plune):
        """Select/Browse pode trazer value=RS e resolved=Rio Grande do Sul — usar o código."""
        mock_plune.return_value = {
            "data": {
                "row": [
                    {
                        "ParceiroId": {"value": "12057"},
                        "NumeroContribuinte": {"value": "52398605000186"},
                        "NomRazaoSocial": {"value": "BIView"},
                        "NomFantasia": {"value": ""},
                        "ECliente": {"value": "0"},
                        "EFornecedor": {"value": "1"},
                        "EnderecoPrincipal": {"value": ""},
                        "BairroPrincipal": {"value": ""},
                        "CidadePrincipalId": {
                            "value": "7965",
                            "resolved": "Pelotas",
                        },
                        "UFPrincipalId": {
                            "value": "RS",
                            "resolved": "Rio Grande do Sul",
                        },
                        "CEPPrincipal": {"value": ""},
                        "ContatoNome": {"value": ""},
                        "EMail": {"value": ""},
                    }
                ]
            }
        }

        parceiros = _buscar_parceiros_por_documento("52398605000186")

        assert parceiros[0]["uf"] == "RS"

    @patch("core.plune_pedido._plune_get")
    def test_browse_uf_apenas_nome_completo_em_resolved(self, mock_plune):
        """Sem value — só nome do estado no resolved (ex.: Santa Catarina → SC)."""
        mock_plune.return_value = {
            "data": {
                "row": [
                    {
                        "ParceiroId": {"value": "9001"},
                        "NumeroContribuinte": {"value": "12345678000199"},
                        "NomRazaoSocial": {"value": "Cliente SC"},
                        "NomFantasia": {"value": ""},
                        "ECliente": {"value": "1"},
                        "EFornecedor": {"value": "0"},
                        "EnderecoPrincipal": {"value": ""},
                        "BairroPrincipal": {"value": ""},
                        "CidadePrincipalEx": {"value": "Florianópolis"},
                        "UFPrincipalId": {
                            "value": "",
                            "resolved": "Santa Catarina",
                        },
                        "CEPPrincipal": {"value": ""},
                        "ContatoNome": {"value": ""},
                        "EMail": {"value": ""},
                    }
                ]
            }
        }

        parceiros = _buscar_parceiros_por_documento("12345678000199")

        assert parceiros[0]["uf"] == "SC"
