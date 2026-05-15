# `Venda.Pedido` — Colunas (export Plune)

Catálogo de **FieldId**, descrição de tela, **permissões** (Ver / Inc / Alt) e **tipo / XSchema**, conforme documentação Plune.

- **NN** — coluna **NOT NULL** no banco (asterisco `*` no export).
- **Permissões** — relativas ao **usuário da sessão** no Plune; outros usuários podem diferir. Em alteração/exclusão ou tabelas subordinadas, o registro pode restringir por campo.
- **Tipos PostgreSQL** — ver [documentação de tipos](https://www.postgresql.org/docs/current/datatype.html) (referência moderna; o Plune citava a série 8.2).

Documento irmão: [Pedido.md](Pedido.md) (API, schema, FKs). Âncora no índice principal: [Colunas](Pedido.md#colunas-pedido).

---

## Chaves e cadastro geral

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `CompanyId` | * | Empresa | Ver | Inc | — | `Company::CompanyId(21) [Company.Company] Minha Empresa` |
| `BranchId` | * | Filial | Ver | Inc | — | `int4(21) [Company.Branch] Filiais` |
| `ClienteId` | * | Cliente | Ver | Inc | — | `int4(21) [Parceiro.tbParceiro] Parceiros` |
| `Id` | * | Número | Ver | Inc | — | `int4(21) (SERIAL)` |
| `CalcularImpostos` | * | :Sugerir Valores de Impostos | Ver | Inc | Alt | `bool()` |
| `Encerrado` | * | Geral \| Encerrado | Ver | — | — | `bool()` |
| `Bloqueado` | * | Geral \| Bloqueado | Ver | — | — | `bool()` |
| `Aprovado` | * | Geral \| Aprovado | Ver | — | — | `bool()` |
| `Descricao` | — | Geral \| Descrição | Ver | Inc | Alt | `varchar(128)` |
| `Status` | * | Geral \| Situação | Ver | Inc | Alt | `int4(21) [Venda.StatusPedido] Situação Pedido` |
| `StatusPedido` | — | Geral \| Status | Ver | Inc | Alt | `int4(21) [Venda.StatusLocatarioPedido] Pedido: Status` |
| `ContatoId` | — | Geral \| Contato do Cliente | Ver | Inc | Alt | `int4(21) [Parceiro.tbContatoParceiro] Parceiros:Contatos` |
| `TabelaPrecoId` | — | Geral \| Tabela de Preços | Ver | Inc | Alt | `int4(21) [Venda.TabelaPreco] Tabela de Preços` |
| `RepresentanteId` | — | Geral \| Representante | Ver | Inc | Alt | `int4(21) [Parceiro.tbParceiro] Parceiros` |

---

## Transporte e endereço de entrega

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `TipoTransporteId` | — | Transporte \| Tipo de Transporte | Ver | Inc | Alt | `int4(21) [Venda.TipoTransporte] Tipo de Transporte` |
| `TipoEntregaId` | — | Transporte \| Tipo de Entrega | Ver | Inc | Alt | `int4(21) [Venda.TipoEntrega] Tipos de Entrega` |
| `FreteporConta` | — | Transporte \| Frete por Conta | Ver | Inc | Alt | `int4(21)` |
| `TransportadoraId` | — | Transporte \| Transportadora | Ver | Inc | Alt | `int4(21) [Parceiro.tbParceiro] Parceiros` |
| `CalcularPesoAuto` | — | Transporte \| Calcular peso automaticamente | Ver | Inc | Alt | `bool()` |
| `CEP` | — | Transporte \| Endereço de Entrega CEP | Ver | Inc | Alt | `Ultra::CEP(8)` |
| `CountryId` | — | Transporte \| Endereço de Entrega País | Ver | Inc | Alt | `int4(21) [Util.Country] País` |
| `UF` | — | Transporte \| Endereço de Entrega Estado | Ver | Inc | Alt | `varchar(2) [Util.State] Estado/Província` |
| `CityId` | — | Transporte \| Endereço de Entrega Cidade | Ver | Inc | Alt | `int4(21) [Util.City] Cidade` |
| `Bairro` | — | Transporte \| Endereço de Entrega Bairro | Ver | Inc | Alt | `varchar(72)` |
| `Endereco` | — | Transporte \| Endereço de Entrega Endereço | Ver | Inc | Alt | `varchar(128)` |
| `Numero` | — | Transporte \| Endereço de Entrega Número | Ver | Inc | Alt | `varchar(16)` |
| `Complemento` | — | Transporte \| Endereço de Entrega Complemento | Ver | Inc | Alt | `varchar(60)` |

---

## Cliente (dados gerais, contato e endereço)

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `ClienteNome` | — | Cliente \| Dados Gerais Razão Social | Ver | Inc | Alt | `varchar(60)` |
| `ClienteNumero` | — | Cliente \| Dados Gerais CPF/CNPJ | Ver | Inc | Alt | `Ultra::CNPJ_CPF(15)` |
| `IndicadorIE` | — | Cliente \| Dados Gerais Indicador de IE | Ver | Inc | Alt | `int4(21)` |
| `ClienteInscricao` | — | Cliente \| Dados Gerais Inscrição Estadual | Ver | Inc | Alt | `varchar(64)` |
| `InscricaoMunicipal` | — | Cliente \| Dados Gerais Inscrição Municipal | Ver | Inc | Alt | `varchar(32)` |
| `EMail` | — | Cliente \| E-mail | Ver | Inc | Alt | `Ultra::EmailMulti(512)` |
| `DocumentoEstrangeiro` | — | Cliente \| Documento Estrangeiro | Ver | Inc | Alt | `varchar(14)` |
| `ClienteDDD` | — | Cliente \| DDD | Ver | Inc | Alt | `numeric(3)` |
| `ClienteFone` | — | Cliente \| Fone | Ver | Inc | Alt | `varchar(32)` |
| `IndicativoConsumidorFinal` | — | Cliente \| Operação para Consumidor Final | Ver | Inc | Alt | `bool()` |
| `ClienteCep` | — | Cliente \| Endereço CEP | Ver | Inc | Alt | `Ultra::CEP(8)` |
| `ClienteCountryId` | — | Cliente \| Endereço País | Ver | Inc | Alt | `int2(21) [Util.Country] País` |
| `ClienteStateId` | — | Cliente \| Endereço Estado | Ver | Inc | Alt | `bpchar(2) [Util.State] Estado/Província` |
| `ClienteBairro` | — | Cliente \| Endereço Bairro | Ver | Inc | Alt | `varchar(72)` |
| `ClienteCityId` | — | Cliente \| Endereço Cidade | Ver | Inc | Alt | `int4(21) [Util.City] Cidade` |
| `ClienteEndereco` | — | Cliente \| Endereço Endereço | Ver | Inc | Alt | `varchar(128)` |
| `ClienteCityName` | — | Cliente \| Endereço Nome da Cidade | Ver | Inc | Alt | `varchar(60)` |
| `ClienteEnderecoNumero` | — | Cliente \| Endereço Número | Ver | Inc | Alt | `varchar(16)` |
| `ClienteCityCodigoIBGE` | — | Cliente \| Endereço Código IBGE | Ver | Inc | Alt | `Ultra::NumericZero()` |
| `ClienteComplemento` | — | Cliente \| Endereço Complemento | Ver | Inc | Alt | `varchar(60)` |

---

## Faturamento, NF e centro de custo

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `ModeloId` | — | Faturamento \| Informações para NF Modelo | Ver | Inc | Alt | `varchar(2) [Venda.ModeloDocumentoFiscal] Modelos de Documentos Fiscais` |
| `Serie` | — | Faturamento \| Informações para NF Série | Ver | Inc | Alt | `varchar(5) [Venda.NotaConfig] Config. Nota Fiscal` |
| `TipoOpId` | * | Faturamento \| Informações para NF Operação | Ver | Inc | Alt | `int4(21) [Produto.TipoOp] Tipo de Operação` |
| `CodFiscalId` | — | Faturamento \| Informações para NF CFOP | Ver | Inc | Alt | `int4(21) [Produto.TipoOpCodFiscal] Tipo de Operação: Código Fiscal` |
| `NaturezaOperacaoServicoId` | — | Faturamento \| Informações para NF Natureza da Operação sobre Serviço | Ver | Inc | Alt | `int4(21) [Produto.TipoOpNaturezaOperacaoServico] Tipo de Operação: Natureza da Operação sobre Serviço` |
| `CentroCustoRegiaoId` | — | Faturamento \| Centro de Custo Região | Ver | — | — | `integer() [Util.CentroCustoRegiao] Região` |
| `CentroCustoId` | — | Faturamento \| Centro de Custo Centro | Ver | Inc | Alt | `int4(21) [Company.CentroCusto] Centro de Custo` |
| `SubCentroCustoId` | — | Faturamento \| Centro de Custo Sub Centro | Ver | Inc | Alt | `int4(21) [Company.SubCentroCusto] Sub Centro de Custo` |
| `SubCentroCusto2Id` | — | Faturamento \| Centro de Custo Sub Centro Nível 2 | Ver | Inc | Alt | `int4(21) [Company.SubCentroCustoNivel2] Sub Centro de Custo Nível 2` |
| `SubCentroCusto3Id` | — | Faturamento \| Centro de Custo Sub Centro Nível 3 | Ver | Inc | Alt | `int4(21) [Company.SubCentroCustoNivel3] Sub Centro de Custo Nível 3` |
| `ValorTotalPago` | — | Faturamento \| Dados do Pagamento Valor Pago | Ver | — | — | `Ultra::Money(15,2)` |
| `ValorDevidoPagamento` | — | Faturamento \| Dados do Pagamento Valor Devido | Ver | — | — | `Ultra::Money(15,2)` |
| `ValorTotalNF` | — | Faturamento \| Notas Fiscais Valores Valor Total | Ver | — | — | `Ultra::Money(15,2)` |
| `ValorFaturadoNF` | — | Faturamento \| Valor Faturado | Ver | — | — | `Ultra::Money(15,2)` |
| `ValorSaldoNF` | — | Faturamento \| Saldo | Ver | — | — | `Ultra::Money(15,2)` |
| `DataPagamento` | — | Faturamento \| Pagamentos Pagamento | Ver | — | — | `date()` |
| `DataVencimento` | — | Faturamento \| Pagamentos Vencimento | Ver | — | — | `date()` |
| `ValorPagamento` | — | Faturamento \| Pagamentos Valor | Ver | — | — | `numeric()` |
| `SituacaoPagamento` | — | Faturamento \| Pagamentos Situação | Ver | — | — | `varchar()` |
| `x1_Description` | — | Faturamento \| Pagamentos Descrição | Ver | — | — | `text()` |
| `x1__DataUltimoFat` | — | Faturamento \| Geral Último Faturamento | Ver | Inc | Alt | `date()` |
| `x1__DataUltimoCont` | — | Faturamento \| Geral Último Vencimento | Ver | Inc | Alt | `date()` |

---

## Contrato

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `TipoContratoId` | — | Contrato \| Tipo de Contrato | Ver | Inc | Alt | `int4(21) [Venda.TipoContrato] Tipo de Contrato` |
| `DiaFat` | — | Contrato \| Faturamento Dia do Faturamento | Ver | Inc | Alt | `numeric(2)` |
| `DataFat` | — | Contrato \| Faturamento Último Vencimento | Ver | Inc | Alt | `date(10)` |
| `IntervaloFat` | — | Contrato \| Faturamento Intervalo do Faturamento | Ver | Inc | Alt | `interval(12)` |
| `DataUltimoFaturamento` | — | Contrato \| Data Último Faturamento | Ver | — | — | `date()` |
| `DataProximoVencimento` | — | Contrato \| Faturamento Próxima Data de Vencimento | Ver | Inc | Alt | `date(10)` |
| `DataTermino` | — | Contrato \| Faturamento Data Término Contrato | Ver | Inc | Alt | `date(10)` |
| `QuantidadeParcela` | — | Contrato \| Faturamento Quantidade Parcelas | Ver | Inc | Alt | `int4(21)` |
| `QuantidadeParcelaOcorrida` | — | Contrato \| Faturamento Parcelas já ocorridas | Ver | Inc | Alt | `int4(21)` |
| `MensalidadeOperacaoFinanceiraId` | — | Contrato \| Faturamento Operação Financeira | Ver | Inc | Alt | `int4(21) [Financeiro.tbOperacaoFinanceira] Operação Financeira` |
| `ContratoReajusteIntervalo` | — | Contrato \| Reajuste Reajustar a cada | Ver | Inc | Alt | `interval(12)` |
| `ContratoReajusteIndice` | — | Contrato \| Reajuste Índice de Reajuste | Ver | Inc | Alt | `varchar(16)` |
| `ContratoReajusteUltimo` | — | Contrato \| Reajuste Data do último reajuste | Ver | Inc | Alt | `date(10)` |
| `ContratoReajusteProximo` | — | Contrato \| Reajuste Data do próximo reajuste | Ver | Inc | Alt | `date(10)` |
| `ContratoObs` | — | Contrato \| Observações | Ver | Inc | Alt | `text()` |

---

## Cobrança e parcelamento manual

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `CaixaId` | — | Cobrança \| Caixa | Ver | Inc | Alt | `int4(21) [Financeiro.CaixaCadastro] Caixas` |
| `OperacaoCaixaId` | — | Cobrança \| Operação de Caixa | Ver | Inc | Alt | `int4(21) [Financeiro.CaixaOperacao] Operações de Caixa` |
| `FaturaReceberId` | — | Cobrança \| Fatura Receber | Ver | Inc | Alt | `int4(21) [Financeiro.tbFaturaReceber] Fatura a Receber` |
| `CondicaoPagamentoId` | — | Cobrança \| Condição de Pagamento | Ver | Inc | Alt | `int4(21) [Financeiro.tbCondicaoPagamento] Condições de Pagamento` |
| `x1_PrevisaoCobranca` | — | Cobrança \| Previsão 1ª Cobrança | Ver | Inc | Alt | `date(10)` |
| `AnaliseCreditoId` | — | Cobrança \| Análise de Crédito | Ver | — | — | `_int4() [Credito.BloqueioCreditoTipo] Tipos de Bloqueio de Crédito` |
| `NumeroAutorizacao` | — | Cobrança \| Cartão de Crédito/Débito Número de Autorização | Ver | Inc | Alt | `varchar(20)` |
| `ParcelamentoAutomatico` | * | Cobrança \| Parcelamento Manual Calcular automaticamente os valores do parcelamento manual | Ver | Inc | Alt | `bool()` |
| `OperacaoFinanceiraId` | — | Cobrança \| Parcelamento Manual Operação Financeira | Ver | Inc | Alt | `_int4() [Financeiro.tbOperacaoFinanceira] Operação Financeira` |
| `PagamentoValor` | — | Cobrança \| Parcelamento Manual Valor | Ver | Inc | Alt | `_numeric(10,2)` |
| `PagamentoVencimento` | — | Cobrança \| Parcelamento Manual Vencimento | Ver | Inc | Alt | `_date()` |
| `NumeroAutorizacaoCartao` | — | Cobrança \| Parcelamento Manual Número de Autorização | Ver | Inc | Alt | `_varchar(20)` |
| `FormaEnvioBoletoId` | — | Cobrança \| Parâmetros dos Boletos emitidos pelo Contas a Receber Emitir Boleto | Ver | Inc | Alt | `int4(21) [Financeiro.tbFormaEnvioBoleto] Formas de Gerar/Enviar Boleto` |
| `ValePresenteId` | — | Cobrança \| Vale Crédito Código de Vale-Crédito | Ver | Inc | Alt | `_int4() [Venda.ValePresente] Vale Crédito` |
| `Email` | — | Cobrança \| Parâmetros dos Boletos emitidos pelo Contas a Receber E-mail | Ver | Inc | Alt | `Ultra::Email(64)` |

---

## Impostos e tributos

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `ICMSBase` | — | Impostos \| ICMS Destacado Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSValor` | — | Impostos \| ICMS Destacado Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSValorDeduzir` | — | Impostos \| ICMS Desconto Zona Franca+ Valor do Desconto | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSSubTribBase` | — | Impostos \| ICMS - Substituição Tributaria+ Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSSubTribValor` | — | Impostos \| ICMS - Substituição Tributaria+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSFCPBase` | — | Impostos \| ICMS - Fundo de Combate à Pobreza+ Base de cálculo | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSFCPValor` | — | Impostos \| ICMS - Fundo de Combate à Pobreza+ Valor | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSSTFCPBase` | — | Impostos \| ICMS Subst Trib - Fundo de Combate à Pobreza+ Base de cálculo | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSValorDiferencialAliquota` | — | Impostos \| Diferimento+ Valor Diferimento | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSValorCredPres` | — | Impostos \| Crédito Presumido+ Valor de Crédito Presumido | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSSTFCPValor` | — | Impostos \| ICMS Subst Trib - Fundo de Combate à Pobreza+ Valor | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IPIBase` | — | Impostos \| IPI Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `IPIValor` | — | Impostos \| IPI Valor IPI | Ver | — | — | `Ultra::Money(15,2)` |
| `COFINSBase` | — | Impostos \| COFINS Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `COFINSValor` | — | Impostos \| COFINS Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `COFINSValorDeduzir` | — | Impostos \| COFINS Desconto Zona Franca+ Valor do Desconto | Ver | — | — | `Ultra::Money(15,2)` |
| `COFINSSTValorBaseCalc` | — | Impostos \| COFINS - Substituição Tributaria+ Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `COFINSSTValor` | — | Impostos \| COFINS - Substituição Tributaria+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `ISSQNBase` | — | Impostos \| ISSQN+ Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `ISSQNValor` | — | Impostos \| ISSQN+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `ISSQNSubstituicaoTributaria` | * | Impostos \| ISSQN+ ISSQN por ST | Ver | — | — | `bool()` |
| `IRRFValor` | — | Impostos \| IRRF+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `INSSValor` | — | Impostos \| INSS+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `CSLLBase` | — | Impostos \| CSLL+ Base | Ver | — | — | `Ultra::Money(15,2)` |
| `SeletivoBase` | — | Impostos \| Seletivo+ Base de Cálculo | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `SeletivoValor` | — | Impostos \| Seletivo+ Valor | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `BaseCredPres` | — | Impostos \| IBS CBS Crédito Presumido+ Base de Cálculo | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSCredPresValor` | — | Impostos \| IBS CBS Crédito Presumido+ Valor Total IBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CBSCredPresValor` | — | Impostos \| IBS CBS Crédito Presumido+ Valor Total CBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSCredPresValorSusp` | — | Impostos \| IBS CBS Crédito Presumido+ Valor Total IBS Condição Suspensiva | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CBSCredPresValorSusp` | — | Impostos \| IBS CBS Crédito Presumido+ Valor Total CBS Condição Suspensiva | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CSLLValor` | — | Impostos \| CSLL+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `PISBase` | — | Impostos \| PIS Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `PISValor` | — | Impostos \| PIS Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `PISValorDeduzir` | — | Impostos \| PIS Desconto Zona Franca+ Valor do Desconto | Ver | — | — | `Ultra::Money(15,2)` |
| `PISSTValorBaseCalc` | — | Impostos \| PIS - Substituição Tributaria+ Base de cálculo | Ver | — | — | `Ultra::Money(15,2)` |
| `PISSTValor` | — | Impostos \| PIS - Substituição Tributaria+ Valor | Ver | — | — | `Ultra::Money(15,2)` |
| `ValorTotalImpostos` | — | Impostos \| Total de Impostos Valor Total Impostos | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSPartilhaUFDestinatario` | — | Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de partilha para a UF do destinatário | Ver | — | — | `Ultra::Money(15,2)` |
| `ICMSPartilhaUFEmitente` | — | Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de partilha para a UF do emitente | Ver | — | — | `Ultra::Money(15,2)` |
| `IBSCBSBase` | — | Impostos \| IBS Base de Cálculo IBS e CBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSUFValorDif` | — | Impostos \| IBS Valor Diferimento Estadual | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSUFValorDeson` | — | Impostos \| IBS Valor Desoneração Estadual | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSUFValor` | — | Impostos \| IBS Valor IBS Estadual | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSMunValorDif` | — | Impostos \| IBS Valor Diferimento Municipal | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSMunValorDeson` | — | Impostos \| IBS Valor Desoneração Municipal | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `IBSMunValor` | — | Impostos \| IBS Valor IBS Municipal | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CBSValorDif` | — | Impostos \| CBS+ Valor Diferimento CBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CBSValorDeson` | — | Impostos \| CBS+ Valor Desoneração CBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CBSValor` | — | Impostos \| CBS+ Valor Total CBS | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ICMSValorFCPUFDest` | — | Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de Fundo de Combate à Pobreza | Ver | — | — | `Ultra::Money(15,2)` |

---

## Comissão

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `BaseComissao` | — | Comissão \| Base da Comissão | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ComissaoManual` | * | Comissão \| Informar Comissão Manualmente | Ver | Inc | Alt | `bool()` |
| `PercentualComissao` | — | Comissão \| Percentual da Comissão | Ver | Inc | Alt | `Ultra::Percent(22,8)` |
| `ValorComissao` | — | Comissão \| Valor da Comissão | Ver | Inc | Alt | `Ultra::Money(15,2)` |

---

## Integração

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `PedidoIdMagento` | — | Integração \| Id do Pedido | Ver | Inc | Alt | `varchar(32)` |
| `PedidoIntegracao` | — | Integração \| Pedido Integração | Ver | Inc | Alt | `varchar(200)` |
| `OrigemIntegracaoId` | — | Integração \| Origem da integração | Ver | Inc | Alt | `int4(21)` |

---

## Detalhes (estoque, contábil, moeda, execução, CRM, criação, aprovação)

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `ReservaId` | — | Detalhes \| Estoque Reserva de Estoque | Ver | — | — | `int4(21) [Estoque.Reserva] Reserva de Estoque` |
| `ManutencaoReserva` | * | Detalhes \| Estoque Manutenção das Reservas Automática | Ver | Inc | Alt | `bool()` |
| `EstoqueSuficiente` | * | Detalhes \| Estoque Estoque Suficiente? | Ver | Inc | Alt | `int4(21)` |
| `ParametroContabilId` | — | Detalhes \| Contabilidade Tipo de Lançamento | Ver | Inc | Alt | `int4(21) [Contabilidade.ParametroContabil] Tipo de Lançamento` |
| `MoedaId` | — | Detalhes \| Cotação+ Moeda | Ver | Inc | Alt | `int4(21) [Util.Moeda] Moeda` |
| `DataCotacao` | — | Detalhes \| Cotação+ Data da Cotação | Ver | Inc | Alt | `date(10)` |
| `MoedaFrete` | — | Detalhes \| Frete+ Moeda | Ver | Inc | Alt | `int4(21) [Util.Moeda] Moeda` |
| `Validade` | — | Detalhes \| Outros Validade do Orçamento | Ver | Inc | Alt | `date(10)` |
| `ObjetoRelacionadoId` | — | Detalhes \| Outros Objeto Relacionado | Ver | Inc | Alt | `int4(21) [Parceiro.ObjetoRelacionado] Objeto Relacionado` |
| `x1_TotalDespesaPedido` | — | Detalhes \| Outros Total Despesas do Pedido | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `OrdemCompra` | — | Detalhes \| Outros Ordem de Compra | Ver | Inc | Alt | `varchar(128)` |
| `DataEncerramento` | — | Detalhes \| Outros Data Encerramento | Ver | Inc | Alt | `timestamp(18)` |
| `DataEntrega` | — | Detalhes \| Outros Data de Entrega | Ver | Inc | Alt | `date(10)` |
| `PedidoOriginal` | — | Detalhes \| Outros Pedido Original | Ver | Inc | Alt | `int4(21) [Venda.Pedido] Pedido` |
| `EnderecoPrestacaoServico` | — | Detalhes \| Outros Endereço de Prestação de Serviço | Ver | Inc | Alt | `int4(21)` |
| `AlertaAnaliseCredito` | — | Detalhes \| Analise de Crédito Alerta Análise de Crédito | Ver | — | — | `boolean()` |
| `x1_FaturamentoDireto` | — | Detalhes \| Monetário Faturamento Direto | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `x1_ValorEntrada` | — | Detalhes \| Valor da Entrada | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `x1_ValorPermuta` | — | Detalhes \| Valor da Permuta | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `x1_DataLibExec` | — | Detalhes \| Execução Data de Liberação para Execução | Ver | Inc | Alt | `date(10)` |
| `x1_PercExecAno` | — | Detalhes \| Execução % a Executar no Ano Corrente | Ver | Inc | Alt | `Ultra::Percentual(15,4)` |
| `x1_PrazoExecContrato` | — | Detalhes \| Execução Prazo de Execução do Contrato (meses) | Ver | Inc | Alt | `int4(21)` |
| `x1_DataCancContrato` | — | Detalhes \| Execução Data de Cancelamento do Contrato | Ver | Inc | Alt | `date(10)` |
| `TextoPadrao` | — | Detalhes \| Observações Texto Padrão | Ver | Inc | Alt | `int4(21) [Venda.Texto] Texto Padrão` |
| `Observacao` | — | Detalhes \| Observações Observações | Ver | Inc | Alt | `text()` |
| `ObservacaoNF` | — | Detalhes \| Observações Observações para NF | Ver | Inc | Alt | `text()` |
| `ObservacaoCobranca` | — | Detalhes \| Observações Observações de Cobrança | Ver | Inc | Alt | `text()` |
| `x1_ObservacaoAnexo` | — | Detalhes \| Observações Obs. do Anexo | Ver | Inc | Alt | `text()` |
| `Anexo` | — | Detalhes \| Observações Anexo | Ver | Inc | Alt | `Ultra::external_file(512)` |
| `x1_IntegracaoSIG` | — | Detalhes \| Informações Adicionais Integração SIG | Ver | Inc | Alt | `text()` |
| `MotivoFechamentoId` | — | Detalhes \| CRM Motivo do Fechamento | Ver | Inc | Alt | `int4(21) [CRM2.FatoRelevante] Motivo de Fechamento de Oportunidade` |
| `OportunidadeId` | — | Detalhes \| CRM Oportunidade | Ver | Inc | Alt | `int4(21) [CRM2.tbOportunidade] Oportunidades` |
| `Data` | * | Detalhes \| Criação Data | Ver | — | — | `timestamp(18)` |
| `UserId` | * | Detalhes \| Criação Usuário | Ver | — | — | `varchar(64) [Ultra.Users] Usuários` |
| `x1_RespComercial` | * | Detalhes \| Responsável Comercial Responsável Comercial | Ver | Inc | Alt | `varchar(64) [Ultra.Users] Usuários` |
| `x1_UsouOrcamentista` | * | Detalhes \| Responsável Comercial Usou Orçamentista? | Ver | Inc | Alt | `bool()` |
| `DataAprovacao` | — | Detalhes \| Aprovação Data | Ver | — | — | `timestamp(18)` |
| `UserIdAprovacao` | — | Detalhes \| Aprovação Usuário | Ver | — | — | `varchar(128) [Ultra.Users] Usuários` |

---

## Valores, totais e consistência

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `pseudoValorProduto` | — | Valores Valor dos Produtos/Serviços | Ver | — | — | `numeric(15,4)` |
| `FreteValor` | — | :Valor do Frete | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `CustoTotal` | — | Custo Total | Ver | — | — | `numeric()` |
| `SeguroValor` | — | :Valor do Seguro | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `TotalSaldo` | — | Saldo | Ver | — | — | `numeric(15,4)` |
| `x1_CustoTotalVenda` | — | Custo Atualizado Total | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `DespesaValor` | — | :Outras Despesas | Ver | Inc | Alt | `Ultra::Money(15,2)` |
| `ValorTotal` | * | Valor Total | Ver | — | — | `Ultra::Money(15,2)` |
| `TotalFaturado` | — | :Faturado | Ver | — | — | `numeric(15,4)` |
| `PedidoInconsistencias` | — | Informações que faltam para encerrar o pedido Inconsistências | Ver | — | — | `text()` |

---

## Notas do export Plune

1. **`*` (NN)** — coluna **não pode ser nula** no modelo relacional.
2. **Permissões (`Ver` / `Inc` / `Alt`)** — globais para o usuário da sessão; por registro ou subordinação a outra tabela podem existir restrições adicionais.
3. **Tipos SQL** — detalhes no PostgreSQL: [datatype](https://www.postgresql.org/docs/current/datatype.html).

O sufixo `*` em **Nome da Coluna** no Plune corresponde à coluna **NN** nas tabelas acima.
