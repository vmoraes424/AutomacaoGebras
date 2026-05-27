# Campos Plune — FieldId e nomes

Gerado em **18/05/2026 18:02** a partir dos exports de colunas do Plune no repositório.

No Plune, o identificador de campo na API é o **FieldId** no formato `Schema.Tabela.Campo` (ex.: `Venda.Pedido.ClienteId`). Não há hashes de 40 caracteres como no Pipedrive.

## Índice

- [Pedido (`Venda.Pedido`)](#vendapedido)
- [Parceiro / Cliente (`Parceiro.tbParceiro`)](#parceirotbparceiro)
- [Pedido — Itens (`Venda.PedidoItem`)](#vendapedidoitem)
- [Usados pela automação (resumo)](#usados-pela-automação-resumo)

**Total catalogado:** 295 campos em pedido e parceiro, + 6 campos de item usados na automação.

## Pedido (`Venda.Pedido`)

**ClassId:** `Venda.Pedido` · **Fonte:** [docs/Plune/Pedidos/Pedido-colunas.md](docs/Plune/Pedidos/Pedido-colunas.md) · **Campos:** 205

| Descrição (Plune) | Campo | FieldId API | Tipo | NN | Uso automação |
|---|---|---|:---:|:---:|---|
| Detalhes \| Analise de Crédito Alerta Análise de Crédito | `AlertaAnaliseCredito` | `Venda.Pedido.AlertaAnaliseCredito` | boolean() | Não |  |
| Cobrança \| Análise de Crédito | `AnaliseCreditoId` | `Venda.Pedido.AnaliseCreditoId` | _int4() [Credito.BloqueioCreditoTipo] Tipos de Bloqueio de Crédito | Não |  |
| Detalhes \| Observações Anexo | `Anexo` | `Venda.Pedido.Anexo` | Ultra::external_file(512) | Não |  |
| Geral \| Aprovado | `Aprovado` | `Venda.Pedido.Aprovado` | bool() | Sim | Insert + aprovação pós-insert |
| Transporte \| Endereço de Entrega Bairro | `Bairro` | `Venda.Pedido.Bairro` | varchar(72) | Não |  |
| Comissão \| Base da Comissão | `BaseComissao` | `Venda.Pedido.BaseComissao` | Ultra::Money(15,2) | Não | Insert |
| Impostos \| IBS CBS Crédito Presumido+ Base de Cálculo | `BaseCredPres` | `Venda.Pedido.BaseCredPres` | Ultra::Money(15,2) | Não |  |
| Geral \| Bloqueado | `Bloqueado` | `Venda.Pedido.Bloqueado` | bool() | Sim |  |
| Filial | `BranchId` | `Venda.Pedido.BranchId` | int4(21) [Company.Branch] Filiais | Sim | Defaults |
| Cobrança \| Caixa | `CaixaId` | `Venda.Pedido.CaixaId` | int4(21) [Financeiro.CaixaCadastro] Caixas | Não |  |
| :Sugerir Valores de Impostos | `CalcularImpostos` | `Venda.Pedido.CalcularImpostos` | bool() | Sim |  |
| Transporte \| Calcular peso automaticamente | `CalcularPesoAuto` | `Venda.Pedido.CalcularPesoAuto` | bool() | Não |  |
| Impostos \| IBS CBS Crédito Presumido+ Valor Total CBS | `CBSCredPresValor` | `Venda.Pedido.CBSCredPresValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS CBS Crédito Presumido+ Valor Total CBS Condição Suspensiva | `CBSCredPresValorSusp` | `Venda.Pedido.CBSCredPresValorSusp` | Ultra::Money(15,2) | Não |  |
| Impostos \| CBS+ Valor Total CBS | `CBSValor` | `Venda.Pedido.CBSValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| CBS+ Valor Desoneração CBS | `CBSValorDeson` | `Venda.Pedido.CBSValorDeson` | Ultra::Money(15,2) | Não |  |
| Impostos \| CBS+ Valor Diferimento CBS | `CBSValorDif` | `Venda.Pedido.CBSValorDif` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Centro de Custo Centro | `CentroCustoId` | `Venda.Pedido.CentroCustoId` | int4(21) [Company.CentroCusto] Centro de Custo | Não | Insert base |
| Faturamento \| Centro de Custo Região | `CentroCustoRegiaoId` | `Venda.Pedido.CentroCustoRegiaoId` | integer() [Util.CentroCustoRegiao] Região | Não |  |
| Transporte \| Endereço de Entrega CEP | `CEP` | `Venda.Pedido.CEP` | Ultra::CEP(8) | Não |  |
| Transporte \| Endereço de Entrega Cidade | `CityId` | `Venda.Pedido.CityId` | int4(21) [Util.City] Cidade | Não |  |
| Cliente \| Endereço Bairro | `ClienteBairro` | `Venda.Pedido.ClienteBairro` | varchar(72) | Não | Insert |
| Cliente \| Endereço CEP | `ClienteCep` | `Venda.Pedido.ClienteCep` | Ultra::CEP(8) | Não | Insert |
| Cliente \| Endereço Código IBGE | `ClienteCityCodigoIBGE` | `Venda.Pedido.ClienteCityCodigoIBGE` | Ultra::NumericZero() | Não |  |
| Cliente \| Endereço Cidade | `ClienteCityId` | `Venda.Pedido.ClienteCityId` | int4(21) [Util.City] Cidade | Não |  |
| Cliente \| Endereço Nome da Cidade | `ClienteCityName` | `Venda.Pedido.ClienteCityName` | varchar(60) | Não | Insert |
| Cliente \| Endereço Complemento | `ClienteComplemento` | `Venda.Pedido.ClienteComplemento` | varchar(60) | Não |  |
| Cliente \| Endereço País | `ClienteCountryId` | `Venda.Pedido.ClienteCountryId` | int2(21) [Util.Country] País | Não |  |
| Cliente \| DDD | `ClienteDDD` | `Venda.Pedido.ClienteDDD` | numeric(3) | Não |  |
| Cliente \| Endereço Endereço | `ClienteEndereco` | `Venda.Pedido.ClienteEndereco` | varchar(128) | Não | Insert |
| Cliente \| Endereço Número | `ClienteEnderecoNumero` | `Venda.Pedido.ClienteEnderecoNumero` | varchar(16) | Não |  |
| Cliente \| Fone | `ClienteFone` | `Venda.Pedido.ClienteFone` | varchar(32) | Não |  |
| Cliente | `ClienteId` | `Venda.Pedido.ClienteId` | int4(21) [Parceiro.tbParceiro] Parceiros | Sim | Insert (parceiro resolvido) |
| Cliente \| Dados Gerais Inscrição Estadual | `ClienteInscricao` | `Venda.Pedido.ClienteInscricao` | varchar(64) | Não |  |
| Cliente \| Dados Gerais Razão Social | `ClienteNome` | `Venda.Pedido.ClienteNome` | varchar(60) | Não | Insert (cadastro Plune) |
| Cliente \| Dados Gerais CPF/CNPJ | `ClienteNumero` | `Venda.Pedido.ClienteNumero` | Ultra::CNPJ_CPF(15) | Não | Insert |
| Cliente \| Endereço Estado | `ClienteStateId` | `Venda.Pedido.ClienteStateId` | bpchar(2) [Util.State] Estado/Província | Não | Insert |
| Faturamento \| Informações para NF CFOP | `CodFiscalId` | `Venda.Pedido.CodFiscalId` | int4(21) [Produto.TipoOpCodFiscal] Tipo de Operação: Código Fiscal | Não |  |
| Impostos \| COFINS Base de cálculo | `COFINSBase` | `Venda.Pedido.COFINSBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| COFINS - Substituição Tributaria+ Valor | `COFINSSTValor` | `Venda.Pedido.COFINSSTValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| COFINS - Substituição Tributaria+ Base de cálculo | `COFINSSTValorBaseCalc` | `Venda.Pedido.COFINSSTValorBaseCalc` | Ultra::Money(15,2) | Não |  |
| Impostos \| COFINS Valor | `COFINSValor` | `Venda.Pedido.COFINSValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| COFINS Desconto Zona Franca+ Valor do Desconto | `COFINSValorDeduzir` | `Venda.Pedido.COFINSValorDeduzir` | Ultra::Money(15,2) | Não |  |
| Comissão \| Informar Comissão Manualmente | `ComissaoManual` | `Venda.Pedido.ComissaoManual` | bool() | Sim | Insert base |
| Empresa | `CompanyId` | `Venda.Pedido.CompanyId` | Company::CompanyId(21) [Company.Company] Minha Empresa | Sim | Insert base / defaults |
| Transporte \| Endereço de Entrega Complemento | `Complemento` | `Venda.Pedido.Complemento` | varchar(60) | Não |  |
| Cobrança \| Condição de Pagamento | `CondicaoPagamentoId` | `Venda.Pedido.CondicaoPagamentoId` | int4(21) [Financeiro.tbCondicaoPagamento] Condições de Pagamento | Não |  |
| Geral \| Contato do Cliente | `ContatoId` | `Venda.Pedido.ContatoId` | int4(21) [Parceiro.tbContatoParceiro] Parceiros:Contatos | Não |  |
| Contrato \| Observações | `ContratoObs` | `Venda.Pedido.ContratoObs` | text() | Não |  |
| Contrato \| Reajuste Índice de Reajuste | `ContratoReajusteIndice` | `Venda.Pedido.ContratoReajusteIndice` | varchar(16) | Não |  |
| Contrato \| Reajuste Reajustar a cada | `ContratoReajusteIntervalo` | `Venda.Pedido.ContratoReajusteIntervalo` | interval(12) | Não |  |
| Contrato \| Reajuste Data do próximo reajuste | `ContratoReajusteProximo` | `Venda.Pedido.ContratoReajusteProximo` | date(10) | Não |  |
| Contrato \| Reajuste Data do último reajuste | `ContratoReajusteUltimo` | `Venda.Pedido.ContratoReajusteUltimo` | date(10) | Não |  |
| Transporte \| Endereço de Entrega País | `CountryId` | `Venda.Pedido.CountryId` | int4(21) [Util.Country] País | Não |  |
| Impostos \| CSLL+ Base | `CSLLBase` | `Venda.Pedido.CSLLBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| CSLL+ Valor | `CSLLValor` | `Venda.Pedido.CSLLValor` | Ultra::Money(15,2) | Não |  |
| Custo Total | `CustoTotal` | `Venda.Pedido.CustoTotal` | numeric() | Não |  |
| Detalhes \| Criação Data | `Data` | `Venda.Pedido.Data` | timestamp(18) | Sim |  |
| Detalhes \| Aprovação Data | `DataAprovacao` | `Venda.Pedido.DataAprovacao` | timestamp(18) | Não |  |
| Detalhes \| Cotação+ Data da Cotação | `DataCotacao` | `Venda.Pedido.DataCotacao` | date(10) | Não |  |
| Detalhes \| Outros Data Encerramento | `DataEncerramento` | `Venda.Pedido.DataEncerramento` | timestamp(18) | Não |  |
| Detalhes \| Outros Data de Entrega | `DataEntrega` | `Venda.Pedido.DataEntrega` | date(10) | Não | Insert |
| Contrato \| Faturamento Último Vencimento | `DataFat` | `Venda.Pedido.DataFat` | date(10) | Não |  |
| Faturamento \| Pagamentos Pagamento | `DataPagamento` | `Venda.Pedido.DataPagamento` | date() | Não |  |
| Contrato \| Faturamento Próxima Data de Vencimento | `DataProximoVencimento` | `Venda.Pedido.DataProximoVencimento` | date(10) | Não |  |
| Contrato \| Faturamento Data Término Contrato | `DataTermino` | `Venda.Pedido.DataTermino` | date(10) | Não |  |
| Contrato \| Data Último Faturamento | `DataUltimoFaturamento` | `Venda.Pedido.DataUltimoFaturamento` | date() | Não |  |
| Faturamento \| Pagamentos Vencimento | `DataVencimento` | `Venda.Pedido.DataVencimento` | date() | Não |  |
| Geral \| Descrição | `Descricao` | `Venda.Pedido.Descricao` | varchar(128) | Não | Insert |
| :Outras Despesas | `DespesaValor` | `Venda.Pedido.DespesaValor` | Ultra::Money(15,2) | Não |  |
| Contrato \| Faturamento Dia do Faturamento | `DiaFat` | `Venda.Pedido.DiaFat` | numeric(2) | Não |  |
| Cliente \| Documento Estrangeiro | `DocumentoEstrangeiro` | `Venda.Pedido.DocumentoEstrangeiro` | varchar(14) | Não |  |
| Cliente \| E-mail | `EMail` | `Venda.Pedido.EMail` | Ultra::EmailMulti(512) | Não |  |
| Cobrança \| Parâmetros dos Boletos emitidos pelo Contas a Receber E-mail | `Email` | `Venda.Pedido.Email` | Ultra::Email(64) | Não |  |
| Geral \| Encerrado | `Encerrado` | `Venda.Pedido.Encerrado` | bool() | Sim |  |
| Transporte \| Endereço de Entrega Endereço | `Endereco` | `Venda.Pedido.Endereco` | varchar(128) | Não |  |
| Detalhes \| Outros Endereço de Prestação de Serviço | `EnderecoPrestacaoServico` | `Venda.Pedido.EnderecoPrestacaoServico` | int4(21) | Não |  |
| Detalhes \| Estoque Estoque Suficiente? | `EstoqueSuficiente` | `Venda.Pedido.EstoqueSuficiente` | int4(21) | Sim |  |
| Cobrança \| Fatura Receber | `FaturaReceberId` | `Venda.Pedido.FaturaReceberId` | int4(21) [Financeiro.tbFaturaReceber] Fatura a Receber | Não |  |
| Cobrança \| Parâmetros dos Boletos emitidos pelo Contas a Receber Emitir Boleto | `FormaEnvioBoletoId` | `Venda.Pedido.FormaEnvioBoletoId` | int4(21) [Financeiro.tbFormaEnvioBoleto] Formas de Gerar/Enviar Boleto | Não |  |
| Transporte \| Frete por Conta | `FreteporConta` | `Venda.Pedido.FreteporConta` | int4(21) | Não | Defaults |
| :Valor do Frete | `FreteValor` | `Venda.Pedido.FreteValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Base de Cálculo IBS e CBS | `IBSCBSBase` | `Venda.Pedido.IBSCBSBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS CBS Crédito Presumido+ Valor Total IBS | `IBSCredPresValor` | `Venda.Pedido.IBSCredPresValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS CBS Crédito Presumido+ Valor Total IBS Condição Suspensiva | `IBSCredPresValorSusp` | `Venda.Pedido.IBSCredPresValorSusp` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor IBS Municipal | `IBSMunValor` | `Venda.Pedido.IBSMunValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor Desoneração Municipal | `IBSMunValorDeson` | `Venda.Pedido.IBSMunValorDeson` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor Diferimento Municipal | `IBSMunValorDif` | `Venda.Pedido.IBSMunValorDif` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor IBS Estadual | `IBSUFValor` | `Venda.Pedido.IBSUFValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor Desoneração Estadual | `IBSUFValorDeson` | `Venda.Pedido.IBSUFValorDeson` | Ultra::Money(15,2) | Não |  |
| Impostos \| IBS Valor Diferimento Estadual | `IBSUFValorDif` | `Venda.Pedido.IBSUFValorDif` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Destacado Base de cálculo | `ICMSBase` | `Venda.Pedido.ICMSBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS - Fundo de Combate à Pobreza+ Base de cálculo | `ICMSFCPBase` | `Venda.Pedido.ICMSFCPBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS - Fundo de Combate à Pobreza+ Valor | `ICMSFCPValor` | `Venda.Pedido.ICMSFCPValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de partilha para a UF do destinatário | `ICMSPartilhaUFDestinatario` | `Venda.Pedido.ICMSPartilhaUFDestinatario` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de partilha para a UF do emitente | `ICMSPartilhaUFEmitente` | `Venda.Pedido.ICMSPartilhaUFEmitente` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Subst Trib - Fundo de Combate à Pobreza+ Base de cálculo | `ICMSSTFCPBase` | `Venda.Pedido.ICMSSTFCPBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Subst Trib - Fundo de Combate à Pobreza+ Valor | `ICMSSTFCPValor` | `Venda.Pedido.ICMSSTFCPValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS - Substituição Tributaria+ Base de cálculo | `ICMSSubTribBase` | `Venda.Pedido.ICMSSubTribBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS - Substituição Tributaria+ Valor | `ICMSSubTribValor` | `Venda.Pedido.ICMSSubTribValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Destacado Valor | `ICMSValor` | `Venda.Pedido.ICMSValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| Crédito Presumido+ Valor de Crédito Presumido | `ICMSValorCredPres` | `Venda.Pedido.ICMSValorCredPres` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Desconto Zona Franca+ Valor do Desconto | `ICMSValorDeduzir` | `Venda.Pedido.ICMSValorDeduzir` | Ultra::Money(15,2) | Não |  |
| Impostos \| Diferimento+ Valor Diferimento | `ICMSValorDiferencialAliquota` | `Venda.Pedido.ICMSValorDiferencialAliquota` | Ultra::Money(15,2) | Não |  |
| Impostos \| ICMS Partilha em Operações interestaduais+ ICMS de Fundo de Combate à Pobreza | `ICMSValorFCPUFDest` | `Venda.Pedido.ICMSValorFCPUFDest` | Ultra::Money(15,2) | Não |  |
| Número | `Id` | `Venda.Pedido.Id` | int4(21) (SERIAL) | Sim | Browse / aprovação |
| Cliente \| Dados Gerais Indicador de IE | `IndicadorIE` | `Venda.Pedido.IndicadorIE` | int4(21) | Não |  |
| Cliente \| Operação para Consumidor Final | `IndicativoConsumidorFinal` | `Venda.Pedido.IndicativoConsumidorFinal` | bool() | Não |  |
| Cliente \| Dados Gerais Inscrição Municipal | `InscricaoMunicipal` | `Venda.Pedido.InscricaoMunicipal` | varchar(32) | Não |  |
| Impostos \| INSS+ Valor | `INSSValor` | `Venda.Pedido.INSSValor` | Ultra::Money(15,2) | Não |  |
| Contrato \| Faturamento Intervalo do Faturamento | `IntervaloFat` | `Venda.Pedido.IntervaloFat` | interval(12) | Não |  |
| Impostos \| IPI Base de cálculo | `IPIBase` | `Venda.Pedido.IPIBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| IPI Valor IPI | `IPIValor` | `Venda.Pedido.IPIValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| IRRF+ Valor | `IRRFValor` | `Venda.Pedido.IRRFValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| ISSQN+ Base de cálculo | `ISSQNBase` | `Venda.Pedido.ISSQNBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| ISSQN+ ISSQN por ST | `ISSQNSubstituicaoTributaria` | `Venda.Pedido.ISSQNSubstituicaoTributaria` | bool() | Sim |  |
| Impostos \| ISSQN+ Valor | `ISSQNValor` | `Venda.Pedido.ISSQNValor` | Ultra::Money(15,2) | Não |  |
| Detalhes \| Estoque Manutenção das Reservas Automática | `ManutencaoReserva` | `Venda.Pedido.ManutencaoReserva` | bool() | Sim |  |
| Contrato \| Faturamento Operação Financeira | `MensalidadeOperacaoFinanceiraId` | `Venda.Pedido.MensalidadeOperacaoFinanceiraId` | int4(21) [Financeiro.tbOperacaoFinanceira] Operação Financeira | Não |  |
| Faturamento \| Informações para NF Modelo | `ModeloId` | `Venda.Pedido.ModeloId` | varchar(2) [Venda.ModeloDocumentoFiscal] Modelos de Documentos Fiscais | Não | Insert base |
| Detalhes \| Frete+ Moeda | `MoedaFrete` | `Venda.Pedido.MoedaFrete` | int4(21) [Util.Moeda] Moeda | Não |  |
| Detalhes \| Cotação+ Moeda | `MoedaId` | `Venda.Pedido.MoedaId` | int4(21) [Util.Moeda] Moeda | Não |  |
| Detalhes \| CRM Motivo do Fechamento | `MotivoFechamentoId` | `Venda.Pedido.MotivoFechamentoId` | int4(21) [CRM2.FatoRelevante] Motivo de Fechamento de Oportunidade | Não |  |
| Faturamento \| Informações para NF Natureza da Operação sobre Serviço | `NaturezaOperacaoServicoId` | `Venda.Pedido.NaturezaOperacaoServicoId` | int4(21) [Produto.TipoOpNaturezaOperacaoServico] Tipo de Operação: Natureza da Operação sobre Serviço | Não | Insert base |
| Transporte \| Endereço de Entrega Número | `Numero` | `Venda.Pedido.Numero` | varchar(16) | Não |  |
| Cobrança \| Cartão de Crédito/Débito Número de Autorização | `NumeroAutorizacao` | `Venda.Pedido.NumeroAutorizacao` | varchar(20) | Não |  |
| Cobrança \| Parcelamento Manual Número de Autorização | `NumeroAutorizacaoCartao` | `Venda.Pedido.NumeroAutorizacaoCartao` | _varchar(20) | Não |  |
| Detalhes \| Outros Objeto Relacionado | `ObjetoRelacionadoId` | `Venda.Pedido.ObjetoRelacionadoId` | int4(21) [Parceiro.ObjetoRelacionado] Objeto Relacionado | Não |  |
| Detalhes \| Observações Observações | `Observacao` | `Venda.Pedido.Observacao` | text() | Não | Insert |
| Detalhes \| Observações Observações de Cobrança | `ObservacaoCobranca` | `Venda.Pedido.ObservacaoCobranca` | text() | Não |  |
| Detalhes \| Observações Observações para NF | `ObservacaoNF` | `Venda.Pedido.ObservacaoNF` | text() | Não | Insert |
| Cobrança \| Operação de Caixa | `OperacaoCaixaId` | `Venda.Pedido.OperacaoCaixaId` | int4(21) [Financeiro.CaixaOperacao] Operações de Caixa | Não |  |
| Cobrança \| Parcelamento Manual Operação Financeira | `OperacaoFinanceiraId` | `Venda.Pedido.OperacaoFinanceiraId` | _int4() [Financeiro.tbOperacaoFinanceira] Operação Financeira | Não |  |
| Detalhes \| CRM Oportunidade | `OportunidadeId` | `Venda.Pedido.OportunidadeId` | int4(21) [CRM2.tbOportunidade] Oportunidades | Não |  |
| Detalhes \| Outros Ordem de Compra | `OrdemCompra` | `Venda.Pedido.OrdemCompra` | varchar(128) | Não |  |
| Integração \| Origem da integração | `OrigemIntegracaoId` | `Venda.Pedido.OrigemIntegracaoId` | int4(21) | Não |  |
| Cobrança \| Parcelamento Manual Valor | `PagamentoValor` | `Venda.Pedido.PagamentoValor` | _numeric(10,2) | Não |  |
| Cobrança \| Parcelamento Manual Vencimento | `PagamentoVencimento` | `Venda.Pedido.PagamentoVencimento` | _date() | Não |  |
| Detalhes \| Contabilidade Tipo de Lançamento | `ParametroContabilId` | `Venda.Pedido.ParametroContabilId` | int4(21) [Contabilidade.ParametroContabil] Tipo de Lançamento | Não | Insert (implantação vs recorrente) |
| Cobrança \| Parcelamento Manual Calcular automaticamente os valores do parcelamento manual | `ParcelamentoAutomatico` | `Venda.Pedido.ParcelamentoAutomatico` | bool() | Sim | Insert base |
| Integração \| Id do Pedido | `PedidoIdMagento` | `Venda.Pedido.PedidoIdMagento` | varchar(32) | Não |  |
| Informações que faltam para encerrar o pedido Inconsistências | `PedidoInconsistencias` | `Venda.Pedido.PedidoInconsistencias` | text() | Não |  |
| Integração \| Pedido Integração | `PedidoIntegracao` | `Venda.Pedido.PedidoIntegracao` | varchar(200) | Não | Insert + idempotência Browse |
| Detalhes \| Outros Pedido Original | `PedidoOriginal` | `Venda.Pedido.PedidoOriginal` | int4(21) [Venda.Pedido] Pedido | Não | Update pós-Insert (vínculo implantação ↔ recorrente) |
| Comissão \| Percentual da Comissão | `PercentualComissao` | `Venda.Pedido.PercentualComissao` | Ultra::Percent(22,8) | Não | Insert (UCs Pipedrive / implantação) |
| Impostos \| PIS Base de cálculo | `PISBase` | `Venda.Pedido.PISBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| PIS - Substituição Tributaria+ Valor | `PISSTValor` | `Venda.Pedido.PISSTValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| PIS - Substituição Tributaria+ Base de cálculo | `PISSTValorBaseCalc` | `Venda.Pedido.PISSTValorBaseCalc` | Ultra::Money(15,2) | Não |  |
| Impostos \| PIS Valor | `PISValor` | `Venda.Pedido.PISValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| PIS Desconto Zona Franca+ Valor do Desconto | `PISValorDeduzir` | `Venda.Pedido.PISValorDeduzir` | Ultra::Money(15,2) | Não |  |
| Valores Valor dos Produtos/Serviços | `pseudoValorProduto` | `Venda.Pedido.pseudoValorProduto` | numeric(15,4) | Não |  |
| Contrato \| Faturamento Quantidade Parcelas | `QuantidadeParcela` | `Venda.Pedido.QuantidadeParcela` | int4(21) | Não |  |
| Contrato \| Faturamento Parcelas já ocorridas | `QuantidadeParcelaOcorrida` | `Venda.Pedido.QuantidadeParcelaOcorrida` | int4(21) | Não |  |
| Geral \| Representante | `RepresentanteId` | `Venda.Pedido.RepresentanteId` | int4(21) [Parceiro.tbParceiro] Parceiros | Não |  |
| Detalhes \| Estoque Reserva de Estoque | `ReservaId` | `Venda.Pedido.ReservaId` | int4(21) [Estoque.Reserva] Reserva de Estoque | Não |  |
| :Valor do Seguro | `SeguroValor` | `Venda.Pedido.SeguroValor` | Ultra::Money(15,2) | Não |  |
| Impostos \| Seletivo+ Base de Cálculo | `SeletivoBase` | `Venda.Pedido.SeletivoBase` | Ultra::Money(15,2) | Não |  |
| Impostos \| Seletivo+ Valor | `SeletivoValor` | `Venda.Pedido.SeletivoValor` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Informações para NF Série | `Serie` | `Venda.Pedido.Serie` | varchar(5) [Venda.NotaConfig] Config. Nota Fiscal | Não | Insert base |
| Faturamento \| Pagamentos Situação | `SituacaoPagamento` | `Venda.Pedido.SituacaoPagamento` | varchar() | Não |  |
| Geral \| Situação | `Status` | `Venda.Pedido.Status` | int4(21) [Venda.StatusPedido] Situação Pedido | Sim | Insert base |
| Geral \| Status | `StatusPedido` | `Venda.Pedido.StatusPedido` | int4(21) [Venda.StatusLocatarioPedido] Pedido: Status | Não | Insert (implantação vs recorrente) |
| Faturamento \| Centro de Custo Sub Centro Nível 2 | `SubCentroCusto2Id` | `Venda.Pedido.SubCentroCusto2Id` | int4(21) [Company.SubCentroCustoNivel2] Sub Centro de Custo Nível 2 | Não | Insert (regional Pipedrive) |
| Faturamento \| Centro de Custo Sub Centro Nível 3 | `SubCentroCusto3Id` | `Venda.Pedido.SubCentroCusto3Id` | int4(21) [Company.SubCentroCustoNivel3] Sub Centro de Custo Nível 3 | Não |  |
| Faturamento \| Centro de Custo Sub Centro | `SubCentroCustoId` | `Venda.Pedido.SubCentroCustoId` | int4(21) [Company.SubCentroCusto] Sub Centro de Custo | Não | Insert (env PLUNE_SUBCENTRO_CUSTO_ID) |
| Geral \| Tabela de Preços | `TabelaPrecoId` | `Venda.Pedido.TabelaPrecoId` | int4(21) [Venda.TabelaPreco] Tabela de Preços | Não |  |
| Detalhes \| Observações Texto Padrão | `TextoPadrao` | `Venda.Pedido.TextoPadrao` | int4(21) [Venda.Texto] Texto Padrão | Não |  |
| Contrato \| Tipo de Contrato | `TipoContratoId` | `Venda.Pedido.TipoContratoId` | int4(21) [Venda.TipoContrato] Tipo de Contrato | Não | Insert base |
| Transporte \| Tipo de Entrega | `TipoEntregaId` | `Venda.Pedido.TipoEntregaId` | int4(21) [Venda.TipoEntrega] Tipos de Entrega | Não |  |
| Faturamento \| Informações para NF Operação | `TipoOpId` | `Venda.Pedido.TipoOpId` | int4(21) [Produto.TipoOp] Tipo de Operação | Sim | Defaults |
| Transporte \| Tipo de Transporte | `TipoTransporteId` | `Venda.Pedido.TipoTransporteId` | int4(21) [Venda.TipoTransporte] Tipo de Transporte | Não |  |
| :Faturado | `TotalFaturado` | `Venda.Pedido.TotalFaturado` | numeric(15,4) | Não |  |
| Saldo | `TotalSaldo` | `Venda.Pedido.TotalSaldo` | numeric(15,4) | Não |  |
| Transporte \| Transportadora | `TransportadoraId` | `Venda.Pedido.TransportadoraId` | int4(21) [Parceiro.tbParceiro] Parceiros | Não |  |
| Transporte \| Endereço de Entrega Estado | `UF` | `Venda.Pedido.UF` | varchar(2) [Util.State] Estado/Província | Não |  |
| Detalhes \| Criação Usuário | `UserId` | `Venda.Pedido.UserId` | varchar(64) [Ultra.Users] Usuários | Sim |  |
| Detalhes \| Aprovação Usuário | `UserIdAprovacao` | `Venda.Pedido.UserIdAprovacao` | varchar(128) [Ultra.Users] Usuários | Não |  |
| Cobrança \| Vale Crédito Código de Vale-Crédito | `ValePresenteId` | `Venda.Pedido.ValePresenteId` | _int4() [Venda.ValePresente] Vale Crédito | Não |  |
| Detalhes \| Outros Validade do Orçamento | `Validade` | `Venda.Pedido.Validade` | date(10) | Não |  |
| Comissão \| Valor da Comissão | `ValorComissao` | `Venda.Pedido.ValorComissao` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Dados do Pagamento Valor Devido | `ValorDevidoPagamento` | `Venda.Pedido.ValorDevidoPagamento` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Valor Faturado | `ValorFaturadoNF` | `Venda.Pedido.ValorFaturadoNF` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Pagamentos Valor | `ValorPagamento` | `Venda.Pedido.ValorPagamento` | numeric() | Não |  |
| Faturamento \| Saldo | `ValorSaldoNF` | `Venda.Pedido.ValorSaldoNF` | Ultra::Money(15,2) | Não |  |
| Valor Total | `ValorTotal` | `Venda.Pedido.ValorTotal` | Ultra::Money(15,2) | Sim |  |
| Impostos \| Total de Impostos Valor Total Impostos | `ValorTotalImpostos` | `Venda.Pedido.ValorTotalImpostos` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Notas Fiscais Valores Valor Total | `ValorTotalNF` | `Venda.Pedido.ValorTotalNF` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Dados do Pagamento Valor Pago | `ValorTotalPago` | `Venda.Pedido.ValorTotalPago` | Ultra::Money(15,2) | Não |  |
| Faturamento \| Geral Último Vencimento | `x1__DataUltimoCont` | `Venda.Pedido.x1__DataUltimoCont` | date() | Não |  |
| Faturamento \| Geral Último Faturamento | `x1__DataUltimoFat` | `Venda.Pedido.x1__DataUltimoFat` | date() | Não |  |
| Custo Atualizado Total | `x1_CustoTotalVenda` | `Venda.Pedido.x1_CustoTotalVenda` | Ultra::Money(15,2) | Não |  |
| Detalhes \| Execução Data de Cancelamento do Contrato | `x1_DataCancContrato` | `Venda.Pedido.x1_DataCancContrato` | date(10) | Não |  |
| Detalhes \| Execução Data de Liberação para Execução | `x1_DataLibExec` | `Venda.Pedido.x1_DataLibExec` | date(10) | Não |  |
| Faturamento \| Pagamentos Descrição | `x1_Description` | `Venda.Pedido.x1_Description` | text() | Não |  |
| Detalhes \| Monetário Faturamento Direto | `x1_FaturamentoDireto` | `Venda.Pedido.x1_FaturamentoDireto` | Ultra::Money(15,2) | Não |  |
| Detalhes \| Informações Adicionais Integração SIG | `x1_IntegracaoSIG` | `Venda.Pedido.x1_IntegracaoSIG` | text() | Não |  |
| Detalhes \| Observações Obs. do Anexo | `x1_ObservacaoAnexo` | `Venda.Pedido.x1_ObservacaoAnexo` | text() | Não | Insert |
| Detalhes \| Execução % a Executar no Ano Corrente | `x1_PercExecAno` | `Venda.Pedido.x1_PercExecAno` | Ultra::Percentual(15,4) | Não |  |
| Detalhes \| Execução Prazo de Execução do Contrato (meses) | `x1_PrazoExecContrato` | `Venda.Pedido.x1_PrazoExecContrato` | int4(21) | Não |  |
| Cobrança \| Previsão 1ª Cobrança | `x1_PrevisaoCobranca` | `Venda.Pedido.x1_PrevisaoCobranca` | date(10) | Não | Insert (datas Pipedrive) |
| Detalhes \| Responsável Comercial Responsável Comercial | `x1_RespComercial` | `Venda.Pedido.x1_RespComercial` | varchar(64) [Ultra.Users] Usuários | Sim |  |
| Detalhes \| Outros Total Despesas do Pedido | `x1_TotalDespesaPedido` | `Venda.Pedido.x1_TotalDespesaPedido` | Ultra::Money(15,2) | Não |  |
| Detalhes \| Responsável Comercial Usou Orçamentista? | `x1_UsouOrcamentista` | `Venda.Pedido.x1_UsouOrcamentista` | bool() | Sim |  |
| Detalhes \| Valor da Entrada | `x1_ValorEntrada` | `Venda.Pedido.x1_ValorEntrada` | Ultra::Money(15,2) | Não |  |
| Detalhes \| Valor da Permuta | `x1_ValorPermuta` | `Venda.Pedido.x1_ValorPermuta` | Ultra::Money(15,2) | Não |  |

## Parceiro / Cliente (`Parceiro.tbParceiro`)

**ClassId:** `Parceiro.tbParceiro` · **Fonte:** [docs/Plune/Clientes/Clientes-colunas.md](docs/Plune/Clientes/Clientes-colunas.md) · **Campos:** 90

| Descrição (Plune) | Campo | FieldId API | Tipo | NN | Uso automação |
|---|---|---|:---:|:---:|---|
| CRM \| Acesso Web \| Acessa via Web | `AcessoWeb` | `Parceiro.tbParceiro.AcessoWeb` | bool() | Sim | Insert |
| Principal \| Situação Ativo | `Ativo` | `Parceiro.tbParceiro.Ativo` | bool() | Sim | Browse filtro |
| Endereço Principal \| Bairro | `BairroPrincipal` | `Parceiro.tbParceiro.BairroPrincipal` | varchar(72) | Não | Browse |
| Mais \| Data de Cadastro | `Cadastro` | `Parceiro.tbParceiro.Cadastro` | timestamp(18) | Sim |  |
| Contato \| Cargo / Função | `Cargo` | `Parceiro.tbParceiro.Cargo` | varchar(128) | Não |  |
| Classificação \| Categoria | `CategoriaId` | `Parceiro.tbParceiro.CategoriaId` | int4(21) [Parceiro.Categoria] Categoria | Não |  |
| Contato \| Celular: Número | `Celular` | `Parceiro.tbParceiro.Celular` | Ultra::PhoneNumber(20) | Não |  |
| Contato \| Celular 2: Número | `Celular2` | `Parceiro.tbParceiro.Celular2` | Ultra::PhoneNumber(20) | Não |  |
| Endereço Principal \| CEP | `CEPPrincipal` | `Parceiro.tbParceiro.CEPPrincipal` | Ultra::CEP(8) | Não | Browse |
| Endereço Principal \| Cidade: Exterior | `CidadePrincipalEx` | `Parceiro.tbParceiro.CidadePrincipalEx` | varchar(60) | Não | Browse + Insert |
| Endereço Principal \| Cidade | `CidadePrincipalId` | `Parceiro.tbParceiro.CidadePrincipalId` | int4(21) [Util.City] Cidade | Não | Browse |
| Cadastro \| CNAE \| Código do Cnae | `CodigoCnae` | `Parceiro.tbParceiro.CodigoCnae` | Ultra::NumericZeroUnformated(128) | Não |  |
| CRM \| Pessoa Física \| Colaborador | `ColaboradorId` | `Parceiro.tbParceiro.ColaboradorId` | int4(21) | Não |  |
| Endereço Principal \| Complemento | `ComplementoPrincipal` | `Parceiro.tbParceiro.ComplementoPrincipal` | varchar(60) | Não |  |
| NF \| Tipo Aplicação ICMS | `ConsumidorFinal` | `Parceiro.tbParceiro.ConsumidorFinal` | int4(21) [Produto.TipoAplicacaoICMS] Tipo Aplicação ICMS | Sim | Insert |
| Contato \| Telefone: DDD | `ContatoDDD` | `Parceiro.tbParceiro.ContatoDDD` | numeric(3) | Não |  |
| Contato \| Fax: DDD | `ContatoDDDFax` | `Parceiro.tbParceiro.ContatoDDDFax` | numeric(3) | Não |  |
| Contato \| FAX: Número | `ContatoFAX` | `Parceiro.tbParceiro.ContatoFAX` | Ultra::PhoneNumber(20) | Não |  |
| Contato \| Contato Principal \| Nome do Contato | `ContatoNome` | `Parceiro.tbParceiro.ContatoNome` | varchar(100) | Não | Browse + Insert (Pipedrive) |
| Contato \| CIN (RG) | `ContatoRG` | `Parceiro.tbParceiro.ContatoRG` | varchar(11) | Não |  |
| Contato \| Telefone: Número | `ContatoTelefone` | `Parceiro.tbParceiro.ContatoTelefone` | Ultra::PhoneNumber(20) | Não |  |
| Contato \| Telefone: Ramal | `ContatoTelefoneRamal` | `Parceiro.tbParceiro.ContatoTelefoneRamal` | int4(21) | Não |  |
| Contato \| CPF | `CPFContato` | `Parceiro.tbParceiro.CPFContato` | Ultra::CPF(11) | Não |  |
| CRM \| Pessoa Física \| Data de Nascimento | `DataFundacao` | `Parceiro.tbParceiro.DataFundacao` | date(10) | Não |  |
| Mais \| Data do último contato | `DataUltimoContato` | `Parceiro.tbParceiro.DataUltimoContato` | timestamp(18) | Não |  |
| Contato \| Celular: DDD | `DDDCelular` | `Parceiro.tbParceiro.DDDCelular` | numeric(3) | Não |  |
| Contato \| Celular 2: DDD | `DDDCelular2` | `Parceiro.tbParceiro.DDDCelular2` | numeric(3) | Não |  |
| Contato \| Fax: DDD | `DDDFax` | `Parceiro.tbParceiro.DDDFax` | numeric(3) | Não |  |
| Contato \| Empresa \| Telefone: DDD | `DDDTelefone` | `Parceiro.tbParceiro.DDDTelefone` | numeric(3) | Não |  |
| Cadastro \| Documento Estrangeiro | `DocumentoEstrangeiro` | `Parceiro.tbParceiro.DocumentoEstrangeiro` | varchar(14) | Não |  |
| Principal \| É Cliente? | `ECliente` | `Parceiro.tbParceiro.ECliente` | bool() | Sim | Browse filtro + Insert |
| Principal \| É Fornecedor? | `EFornecedor` | `Parceiro.tbParceiro.EFornecedor` | bool() | Sim | Browse filtro + Insert |
| Contato \| E-mail | `EMail` | `Parceiro.tbParceiro.EMail` | Ultra::EmailMulti(512) | Não | Browse |
| CRM \| Informações \| E-Mail para Atividade | `EMailCopiaAtividade` | `Parceiro.tbParceiro.EMailCopiaAtividade` | Ultra::Email(64) | Não |  |
| NF \| E-Mail para envio de Notas | `EmailNFe` | `Parceiro.tbParceiro.EmailNFe` | Ultra::EmailMulti(512) | Não |  |
| Principal \| Em aprovação? | `EmAprovacao` | `Parceiro.tbParceiro.EmAprovacao` | bool() | Sim | Insert |
| Empresa | `EmpresaId` | `Parceiro.tbParceiro.EmpresaId` | Company::CompanyId(21) [Company.Company] Minha Empresa | Sim | Insert / Select / Browse filtro |
| Principal \| Em prospecção? | `EmProspeccao` | `Parceiro.tbParceiro.EmProspeccao` | bool() | Sim | Insert |
| Endereço Principal \| Endereço | `EnderecoPrincipal` | `Parceiro.tbParceiro.EnderecoPrincipal` | varchar(128) | Não | Browse + Insert |
| Principal \| É Representante? | `ERepresentante` | `Parceiro.tbParceiro.ERepresentante` | bool() | Sim | Insert |
| CRM \| Faturamento | `Faturamento` | `Parceiro.tbParceiro.Faturamento` | numeric(10,2) | Não |  |
| Contato \| Fax: Número | `Fax` | `Parceiro.tbParceiro.Fax` | Ultra::PhoneNumber(20) | Não |  |
| Contato \| Foto | `FotoContatoPrincipal` | `Parceiro.tbParceiro.FotoContatoPrincipal` | Ultra::external_file(512) | Não |  |
| Classificação \| Grupo | `GrupoId` | `Parceiro.tbParceiro.GrupoId` | int4(21) [Parceiro.Grupo] Grupo | Não |  |
| CRM \| Informações \| Grupo do Parceiro | `GrupoParceiroId` | `Parceiro.tbParceiro.GrupoParceiroId` | int4(21) [Parceiro.tbGrupo] Grupo de Parceiros | Não |  |
| NF \| Grupo de Tributação | `GrupoTributacaoId` | `Parceiro.tbParceiro.GrupoTributacaoId` | int4(21) [Parceiro.GrupoTributacao] Grupo de Tributação | Não |  |
| Contato \| Site | `HomePage` | `Parceiro.tbParceiro.HomePage` | Ultra::URL(1024) | Não |  |
| Cadastro \| Indicador da IE | `IndicadorIE` | `Parceiro.tbParceiro.IndicadorIE` | int4(21) | Não |  |
| NF \| Operação com Consumidor Final | `IndicativoConsumidorFinal` | `Parceiro.tbParceiro.IndicativoConsumidorFinal` | bool() | Não |  |
| Cadastro \| Inscrição Municipal | `InscricaoMunicipal` | `Parceiro.tbParceiro.InscricaoMunicipal` | varchar(32) | Não |  |
| NF \| ISSQN por ST | `ISSQNSubstituicaoTributaria` | `Parceiro.tbParceiro.ISSQNSubstituicaoTributaria` | bool() | Sim | Insert |
| Principal \| Nome Fantasia | `NomFantasia` | `Parceiro.tbParceiro.NomFantasia` | varchar(60) | Sim | Browse + Insert |
| Principal \| Razão Social | `NomRazaoSocial` | `Parceiro.tbParceiro.NomRazaoSocial` | varchar(60) | Sim | Browse + Insert |
| CRM \| Pessoa Jurídica \| Número de colaboradores | `NumColaboradores` | `Parceiro.tbParceiro.NumColaboradores` | int4(21) | Não |  |
| Cadastro \| Número do CNPJ / CPF | `NumeroContribuinte` | `Parceiro.tbParceiro.NumeroContribuinte` | Ultra::CNPJ_CPF(15) | Não | Browse filtro + Insert |
| CRM \| Número de Filiais | `NumeroFiliais` | `Parceiro.tbParceiro.NumeroFiliais` | int4(21) | Sim | Insert |
| Cadastro \| Inscrição Estadual | `NumeroInscricao` | `Parceiro.tbParceiro.NumeroInscricao` | varchar(32) | Não |  |
| Mais \| Detalhes \| Número Interno | `NumeroInterno` | `Parceiro.tbParceiro.NumeroInterno` | varchar(255) | Não |  |
| Endereço Principal \| Número | `NumeroPrincipal` | `Parceiro.tbParceiro.NumeroPrincipal` | varchar(16) | Não |  |
| Mais \| Observações | `Obs` | `Parceiro.tbParceiro.Obs` | text() | Não | Insert |
| Contato \| Origem | `OrigemId` | `Parceiro.tbParceiro.OrigemId` | int4(21) [CRM2.tbOrigem] Origem Prospect | Não |  |
| Endereço Principal \| País | `PaisPrincipalId` | `Parceiro.tbParceiro.PaisPrincipalId` | int2(21) [Util.Country] País | Não |  |
| CRM \| Área \| Área de Vendas ou Atuação | `ParceiroArea` | `Parceiro.tbParceiro.ParceiroArea` | int4(21) [Parceiro.Area] Áreas | Não |  |
| CRM \| Área \| Responsável ou Vendedor | `ParceiroAreaUserId` | `Parceiro.tbParceiro.ParceiroAreaUserId` | int4(21) [Parceiro.AreaUser] Áreas: Usuários / Vendedores | Não |  |
| Código | `ParceiroId` | `Parceiro.tbParceiro.ParceiroId` | int4(6) | Não | Browse / Select |
| Cadastro \| Sub-ramo de Atividade | `RamoAtividadeDivisaoId` | `Parceiro.tbParceiro.RamoAtividadeDivisaoId` | int4(21) [Parceiro.tbRamoAtividadeDivisao] CNAE (Divisão) | Não |  |
| Cadastro \| Ramo de Atividade | `RamoAtividadeSecaoId` | `Parceiro.tbParceiro.RamoAtividadeSecaoId` | int4(21) [Parceiro.tbRamoAtividadeSecao] CNAE (Seção) | Não |  |
| CRM \| Aceita receber e-mail | `RecebeEmala` | `Parceiro.tbParceiro.RecebeEmala` | bool() | Sim | Insert |
| CRM \| Recebe Mala Direta (Correio) | `RecebeMalaCorreio` | `Parceiro.tbParceiro.RecebeMalaCorreio` | bool() | Sim | Insert |
| Mais \| Região | `RegiaoCentroCustoId` | `Parceiro.tbParceiro.RegiaoCentroCustoId` | int4(21) [Util.CentroCustoRegiao] Região | Não |  |
| NF \| Informação para NF de Entrada (Terceiros) \| Regime Tributário | `RegimeTributario` | `Parceiro.tbParceiro.RegimeTributario` | varchar(1) [Produto.RegimeTributario] Regime Tributário | Sim | Insert |
| CRM \| Senha | `Senha` | `Parceiro.tbParceiro.Senha` | Ultra::password(128) | Não |  |
| NF \| NF de Serviço \| Situação Especial | `SituacaoEspecialTomador` | `Parceiro.tbParceiro.SituacaoEspecialTomador` | int4(21) | Não |  |
| Classificação \| Sub Categoria | `SubCategoriaId` | `Parceiro.tbParceiro.SubCategoriaId` | int4(21) [Parceiro.SubCategoria] Sub Categoria | Não |  |
| Classificação \| Sub Grupo | `SubGrupoId` | `Parceiro.tbParceiro.SubGrupoId` | int4(21) [Parceiro.SubGrupo] Sub Grupo | Não |  |
| Contato \| Telefone: Número | `Telefone` | `Parceiro.tbParceiro.Telefone` | Ultra::PhoneNumber(20) | Não |  |
| Contato \| Telefone: Ramal | `TelefoneRamal` | `Parceiro.tbParceiro.TelefoneRamal` | int4(21) | Não |  |
| Principal \| Tipo de parceiro \| Tipo do Parceiro | `Tipo` | `Parceiro.tbParceiro.Tipo` | int4(21) [Parceiro.Tipo] Tipo de Parceiros | Não |  |
| Cadastro \| Tipo de Contribuinte | `TipoContribuinteId` | `Parceiro.tbParceiro.TipoContribuinteId` | varchar(8) [Parceiro.tbTipoContribuinte] Tipo de Contribuinte | Não |  |
| NF \| Informações Padrões para Pedidos e Notas Fiscais de Emissão Própria \| Tipo de Transporte | `TipoTransporteId` | `Parceiro.tbParceiro.TipoTransporteId` | int4(21) [Venda.TipoTransporte] Tipo de Transporte | Não |  |
| Principal \| É Transportadora? | `Transportadora` | `Parceiro.tbParceiro.Transportadora` | bool() | Sim | Insert |
| Contato \| Tratamento | `Tratamento` | `Parceiro.tbParceiro.Tratamento` | varchar(32) | Não |  |
| Endereço Principal \| Estado: Exterior | `UFPrincipalEx` | `Parceiro.tbParceiro.UFPrincipalEx` | bpchar(60) | Não |  |
| Endereço Principal \| Estado | `UFPrincipalId` | `Parceiro.tbParceiro.UFPrincipalId` | bpchar(2) [Util.State] Estado/Província | Não | Browse |
| Mais \| Última Alteração | `UltimaAlteracao` | `Parceiro.tbParceiro.UltimaAlteracao` | timestamp(18) | Não |  |
| Mais \| Última Compra | `UltimaCompra` | `Parceiro.tbParceiro.UltimaCompra` | date() | Não |  |
| Mais \| Última Venda | `UltimaVenda` | `Parceiro.tbParceiro.UltimaVenda` | date() | Não |  |
| Mais \| Criado por | `UserId` | `Parceiro.tbParceiro.UserId` | varchar(128) [Ultra.Users] Usuários | Sim |  |
| Mais \| Análise de Crédito \| Consolidar (somar) as informações de crédito pelo CNPJ (8 dígitos)? | `VerificacaoFilial` | `Parceiro.tbParceiro.VerificacaoFilial` | bool() | Sim | Insert |
| Contato \| Skype | `VoIP` | `Parceiro.tbParceiro.VoIP` | Ultra::URL(1024) | Não |  |

## Pedido — Itens (`Venda.PedidoItem`)

Tabela embutida no Insert do pedido. Não há export de colunas no repositório; lista abaixo = campos usados pela automação em `core/plune_pedido.py`.

| Campo | FieldId API | Uso automação |
|---|---|---|
| `BranchId` | `Venda.PedidoItem.BranchId` | Insert item |
| `ClienteId` | `Venda.PedidoItem.ClienteId` | Insert item |
| `CompanyId` | `Venda.PedidoItem.CompanyId` | Insert item (slave) |
| `Preco` | `Venda.PedidoItem.Preco` | Insert item (valor deal) |
| `ProdutoId` | `Venda.PedidoItem.ProdutoId` | Insert item (PLUNE_PRODUTO_SOLE_ID) |
| `Quantidade` | `Venda.PedidoItem.Quantidade` | Insert item |

## Usados pela automação (resumo)

Referência rápida dos FieldIds enviados pelo fluxo Pipedrive → Plune.

### `Venda.Pedido`

| Campo | FieldId API | Papel |
|---|---|---|
| `Aprovado` | `Venda.Pedido.Aprovado` | Insert + aprovação pós-insert |
| `BaseComissao` | `Venda.Pedido.BaseComissao` | Insert |
| `BranchId` | `Venda.Pedido.BranchId` | Defaults |
| `CentroCustoId` | `Venda.Pedido.CentroCustoId` | Insert base |
| `ClienteBairro` | `Venda.Pedido.ClienteBairro` | Insert |
| `ClienteCep` | `Venda.Pedido.ClienteCep` | Insert |
| `ClienteCityName` | `Venda.Pedido.ClienteCityName` | Insert |
| `ClienteEndereco` | `Venda.Pedido.ClienteEndereco` | Insert |
| `ClienteId` | `Venda.Pedido.ClienteId` | Insert (parceiro resolvido) |
| `ClienteNome` | `Venda.Pedido.ClienteNome` | Insert (cadastro Plune) |
| `ClienteNumero` | `Venda.Pedido.ClienteNumero` | Insert |
| `ClienteStateId` | `Venda.Pedido.ClienteStateId` | Insert |
| `ComissaoManual` | `Venda.Pedido.ComissaoManual` | Insert base |
| `CompanyId` | `Venda.Pedido.CompanyId` | Insert base / defaults |
| `DataEntrega` | `Venda.Pedido.DataEntrega` | Insert |
| `Descricao` | `Venda.Pedido.Descricao` | Insert |
| `FreteporConta` | `Venda.Pedido.FreteporConta` | Defaults |
| `Id` | `Venda.Pedido.Id` | Browse / aprovação |
| `ModeloId` | `Venda.Pedido.ModeloId` | Insert base |
| `NaturezaOperacaoServicoId` | `Venda.Pedido.NaturezaOperacaoServicoId` | Insert base |
| `Observacao` | `Venda.Pedido.Observacao` | Insert |
| `ObservacaoNF` | `Venda.Pedido.ObservacaoNF` | Insert |
| `ParametroContabilId` | `Venda.Pedido.ParametroContabilId` | Insert (implantação vs recorrente) |
| `ParcelamentoAutomatico` | `Venda.Pedido.ParcelamentoAutomatico` | Insert base |
| `PedidoIntegracao` | `Venda.Pedido.PedidoIntegracao` | Insert + idempotência Browse |
| `PercentualComissao` | `Venda.Pedido.PercentualComissao` | Insert (UCs Pipedrive / implantação) |
| `Serie` | `Venda.Pedido.Serie` | Insert base |
| `Status` | `Venda.Pedido.Status` | Insert base |
| `StatusPedido` | `Venda.Pedido.StatusPedido` | Insert (implantação vs recorrente) |
| `SubCentroCusto2Id` | `Venda.Pedido.SubCentroCusto2Id` | Insert (regional Pipedrive) |
| `SubCentroCustoId` | `Venda.Pedido.SubCentroCustoId` | Insert (env PLUNE_SUBCENTRO_CUSTO_ID) |
| `TipoContratoId` | `Venda.Pedido.TipoContratoId` | Insert base |
| `TipoOpId` | `Venda.Pedido.TipoOpId` | Defaults |
| `x1_ObservacaoAnexo` | `Venda.Pedido.x1_ObservacaoAnexo` | Insert |
| `x1_PrevisaoCobranca` | `Venda.Pedido.x1_PrevisaoCobranca` | Insert (datas Pipedrive) |

### `Venda.PedidoItem`

| Campo | FieldId API | Papel |
|---|---|---|
| `BranchId` | `Venda.PedidoItem.BranchId` | Insert item |
| `ClienteId` | `Venda.PedidoItem.ClienteId` | Insert item |
| `CompanyId` | `Venda.PedidoItem.CompanyId` | Insert item (slave) |
| `Preco` | `Venda.PedidoItem.Preco` | Insert item (valor deal) |
| `ProdutoId` | `Venda.PedidoItem.ProdutoId` | Insert item (PLUNE_PRODUTO_SOLE_ID) |
| `Quantidade` | `Venda.PedidoItem.Quantidade` | Insert item |

### `Parceiro.tbParceiro`

| Campo | FieldId API | Papel |
|---|---|---|
| `AcessoWeb` | `Parceiro.tbParceiro.AcessoWeb` | Insert |
| `Ativo` | `Parceiro.tbParceiro.Ativo` | Browse filtro |
| `BairroPrincipal` | `Parceiro.tbParceiro.BairroPrincipal` | Browse |
| `CEPPrincipal` | `Parceiro.tbParceiro.CEPPrincipal` | Browse |
| `CidadePrincipalEx` | `Parceiro.tbParceiro.CidadePrincipalEx` | Browse + Insert |
| `CidadePrincipalId` | `Parceiro.tbParceiro.CidadePrincipalId` | Browse |
| `ConsumidorFinal` | `Parceiro.tbParceiro.ConsumidorFinal` | Insert |
| `ContatoNome` | `Parceiro.tbParceiro.ContatoNome` | Browse + Insert (Pipedrive) |
| `ECliente` | `Parceiro.tbParceiro.ECliente` | Browse filtro + Insert |
| `EFornecedor` | `Parceiro.tbParceiro.EFornecedor` | Browse filtro + Insert |
| `EMail` | `Parceiro.tbParceiro.EMail` | Browse |
| `EmAprovacao` | `Parceiro.tbParceiro.EmAprovacao` | Insert |
| `EmpresaId` | `Parceiro.tbParceiro.EmpresaId` | Insert / Select / Browse filtro |
| `EmProspeccao` | `Parceiro.tbParceiro.EmProspeccao` | Insert |
| `EnderecoPrincipal` | `Parceiro.tbParceiro.EnderecoPrincipal` | Browse + Insert |
| `ERepresentante` | `Parceiro.tbParceiro.ERepresentante` | Insert |
| `ISSQNSubstituicaoTributaria` | `Parceiro.tbParceiro.ISSQNSubstituicaoTributaria` | Insert |
| `NomFantasia` | `Parceiro.tbParceiro.NomFantasia` | Browse + Insert |
| `NomRazaoSocial` | `Parceiro.tbParceiro.NomRazaoSocial` | Browse + Insert |
| `NumeroContribuinte` | `Parceiro.tbParceiro.NumeroContribuinte` | Browse filtro + Insert |
| `NumeroFiliais` | `Parceiro.tbParceiro.NumeroFiliais` | Insert |
| `Obs` | `Parceiro.tbParceiro.Obs` | Insert |
| `ParceiroId` | `Parceiro.tbParceiro.ParceiroId` | Browse / Select |
| `RecebeEmala` | `Parceiro.tbParceiro.RecebeEmala` | Insert |
| `RecebeMalaCorreio` | `Parceiro.tbParceiro.RecebeMalaCorreio` | Insert |
| `RegimeTributario` | `Parceiro.tbParceiro.RegimeTributario` | Insert |
| `Transportadora` | `Parceiro.tbParceiro.Transportadora` | Insert |
| `UFPrincipalId` | `Parceiro.tbParceiro.UFPrincipalId` | Browse |
| `VerificacaoFilial` | `Parceiro.tbParceiro.VerificacaoFilial` | Insert |
