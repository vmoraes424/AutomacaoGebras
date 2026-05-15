# `Parceiro.tbParceiro` — Colunas (export Plune)

Catálogo de **FieldId**, descrição de tela, **permissões** (Ver / Inc / Alt) e **tipo / XSchema**, conforme documentação Plune.

- **NN** — coluna **NOT NULL** no banco (asterisco `*` no export).
- **Permissões** — relativas ao **usuário da sessão** no Plune; outros usuários podem diferir. Em alteração/exclusão ou tabelas subordinadas, o registro pode restringir por campo.
- **Tipos PostgreSQL** — ver [documentação de tipos](https://www.postgresql.org/docs/current/datatype.html) (referência moderna; o Plune citava a série 8.2).

Documento irmão: [Clientes.md](Clientes.md) (API Browse, schema, integração Pipedrive).

**Campos usados na automação** (Browse / pedido): `Ativo`, `NumeroContribuinte`, `ParceiroId`, `NomRazaoSocial` — ver [Browse](Clientes.md#browse).

---

## Chaves

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `EmpresaId` | * | Empresa | Ver | Inc | — | `Company::CompanyId(21) [Company.Company] Minha Empresa` |
| `ParceiroId` | — | Código | Ver | Inc | — | `int4(6)` |

---

## Principal

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `NomFantasia` | * | Principal \| Nome Fantasia | Ver | Inc | Alt | `varchar(60)` |
| `NomRazaoSocial` | * | Principal \| Razão Social | Ver | Inc | Alt | `varchar(60)` |
| `Ativo` | * | Principal \| Situação Ativo | Ver | Inc | Alt | `bool()` |
| `EmProspeccao` | * | Principal \| Em prospecção? | Ver | Inc | Alt | `bool()` |
| `EmAprovacao` | * | Principal \| Em aprovação? | Ver | Inc | Alt | `bool()` |
| `Tipo` | — | Principal \| Tipo de parceiro \| Tipo do Parceiro | Ver | Inc | Alt | `int4(21) [Parceiro.Tipo] Tipo de Parceiros` |
| `ECliente` | * | Principal \| É Cliente? | Ver | Inc | Alt | `bool()` |
| `EFornecedor` | * | Principal \| É Fornecedor? | Ver | Inc | Alt | `bool()` |
| `ERepresentante` | * | Principal \| É Representante? | Ver | Inc | Alt | `bool()` |
| `Transportadora` | * | Principal \| É Transportadora? | Ver | Inc | Alt | `bool()` |
| `ECondutor` | — | Principal \| Condutor? | — | Inc | Alt | `bool()` |

---

## Cadastro

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `TipoContribuinteId` | — | Cadastro \| Tipo de Contribuinte | Ver | Inc | Alt | `varchar(8) [Parceiro.tbTipoContribuinte] Tipo de Contribuinte` |
| `NumeroContribuinte` | — | Cadastro \| Número do CNPJ / CPF | Ver | Inc | Alt | `Ultra::CNPJ_CPF(15)` |
| `IndicadorIE` | — | Cadastro \| Indicador da IE | Ver | Inc | Alt | `int4(21)` |
| `NumeroInscricao` | — | Cadastro \| Inscrição Estadual | Ver | Inc | Alt | `varchar(32)` |
| `InscricaoMunicipal` | — | Cadastro \| Inscrição Municipal | Ver | Inc | Alt | `varchar(32)` |
| `DocumentoEstrangeiro` | — | Cadastro \| Documento Estrangeiro | Ver | Inc | Alt | `varchar(14)` |
| `CodigoCnae` | — | Cadastro \| CNAE \| Código do Cnae | Ver | Inc | Alt | `Ultra::NumericZeroUnformated(128)` |
| `RamoAtividadeSecaoId` | — | Cadastro \| Ramo de Atividade | Ver | Inc | Alt | `int4(21) [Parceiro.tbRamoAtividadeSecao] CNAE (Seção)` |
| `RamoAtividadeDivisaoId` | — | Cadastro \| Sub-ramo de Atividade | Ver | Inc | Alt | `int4(21) [Parceiro.tbRamoAtividadeDivisao] CNAE (Divisão)` |

---

## Endereço principal

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `CEPPrincipal` | — | Endereço Principal \| CEP | Ver | Inc | Alt | `Ultra::CEP(8)` |
| `PaisPrincipalId` | — | Endereço Principal \| País | Ver | Inc | Alt | `int2(21) [Util.Country] País` |
| `UFPrincipalId` | — | Endereço Principal \| Estado | Ver | Inc | Alt | `bpchar(2) [Util.State] Estado/Província` |
| `UFPrincipalEx` | — | Endereço Principal \| Estado: Exterior | Ver | Inc | Alt | `bpchar(60)` |
| `CidadePrincipalId` | — | Endereço Principal \| Cidade | Ver | Inc | Alt | `int4(21) [Util.City] Cidade` |
| `CidadePrincipalEx` | — | Endereço Principal \| Cidade: Exterior | Ver | Inc | Alt | `varchar(60)` |
| `BairroPrincipal` | — | Endereço Principal \| Bairro | Ver | Inc | Alt | `varchar(72)` |
| `EnderecoPrincipal` | — | Endereço Principal \| Endereço | Ver | Inc | Alt | `varchar(128)` |
| `NumeroPrincipal` | — | Endereço Principal \| Número | Ver | Inc | Alt | `varchar(16)` |
| `ComplementoPrincipal` | — | Endereço Principal \| Complemento | Ver | Inc | Alt | `varchar(60)` |

---

## Contato

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `DDDTelefone` | — | Contato \| Empresa \| Telefone: DDD | Ver | Inc | Alt | `numeric(3)` |
| `Telefone` | — | Contato \| Telefone: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `TelefoneRamal` | — | Contato \| Telefone: Ramal | Ver | Inc | Alt | `int4(21)` |
| `DDDFax` | — | Contato \| Fax: DDD | Ver | Inc | Alt | `numeric(3)` |
| `Fax` | — | Contato \| Fax: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `HomePage` | — | Contato \| Site | Ver | Inc | Alt | `Ultra::URL(1024)` |
| `ContatoNome` | — | Contato \| Contato Principal \| Nome do Contato | Ver | Inc | Alt | `varchar(100)` |
| `Tratamento` | — | Contato \| Tratamento | Ver | Inc | Alt | `varchar(32)` |
| `ContatoRG` | — | Contato \| CIN (RG) | Ver | Inc | Alt | `varchar(11)` |
| `CPFContato` | — | Contato \| CPF | Ver | Inc | Alt | `Ultra::CPF(11)` |
| `Cargo` | — | Contato \| Cargo / Função | Ver | Inc | Alt | `varchar(128)` |
| `ContatoDDD` | — | Contato \| Telefone: DDD | Ver | Inc | Alt | `numeric(3)` |
| `ContatoTelefone` | — | Contato \| Telefone: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `ContatoTelefoneRamal` | — | Contato \| Telefone: Ramal | Ver | Inc | Alt | `int4(21)` |
| `DDDCelular` | — | Contato \| Celular: DDD | Ver | Inc | Alt | `numeric(3)` |
| `Celular` | — | Contato \| Celular: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `DDDCelular2` | — | Contato \| Celular 2: DDD | Ver | Inc | Alt | `numeric(3)` |
| `Celular2` | — | Contato \| Celular 2: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `ContatoDDDFax` | — | Contato \| Fax: DDD | Ver | Inc | Alt | `numeric(3)` |
| `ContatoFAX` | — | Contato \| FAX: Número | Ver | Inc | Alt | `Ultra::PhoneNumber(20)` |
| `EMail` | — | Contato \| E-mail | Ver | Inc | Alt | `Ultra::EmailMulti(512)` |
| `VoIP` | — | Contato \| Skype | Ver | Inc | Alt | `Ultra::URL(1024)` |
| `OrigemId` | — | Contato \| Origem | Ver | Inc | Alt | `int4(21) [CRM2.tbOrigem] Origem Prospect` |
| `FotoContatoPrincipal` | — | Contato \| Foto | Ver | Inc | Alt | `Ultra::external_file(512)` |

---

## CRM

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `GrupoParceiroId` | — | CRM \| Informações \| Grupo do Parceiro | Ver | Inc | Alt | `int4(21) [Parceiro.tbGrupo] Grupo de Parceiros` |
| `EMailCopiaAtividade` | — | CRM \| Informações \| E-Mail para Atividade | Ver | Inc | Alt | `Ultra::Email(64)` |
| `RecebeEmala` | * | CRM \| Aceita receber e-mail | Ver | Inc | Alt | `bool()` |
| `RecebeMalaCorreio` | * | CRM \| Recebe Mala Direta (Correio) | Ver | Inc | Alt | `bool()` |
| `ParceiroArea` | — | CRM \| Área \| Área de Vendas ou Atuação | Ver | Inc | — | `int4(21) [Parceiro.Area] Áreas` |
| `ParceiroAreaUserId` | — | CRM \| Área \| Responsável ou Vendedor | Ver | Inc | — | `int4(21) [Parceiro.AreaUser] Áreas: Usuários / Vendedores` |
| `AcessoWeb` | * | CRM \| Acesso Web \| Acessa via Web | Ver | Inc | Alt | `bool()` |
| `Senha` | — | CRM \| Senha | Ver | Inc | Alt | `Ultra::password(128)` |
| `NumColaboradores` | — | CRM \| Pessoa Jurídica \| Número de colaboradores | Ver | Inc | Alt | `int4(21)` |
| `NumeroFiliais` | * | CRM \| Número de Filiais | Ver | Inc | Alt | `int4(21)` |
| `Faturamento` | — | CRM \| Faturamento | Ver | Inc | Alt | `numeric(10,2)` |
| `DataFundacao` | — | CRM \| Pessoa Física \| Data de Nascimento | Ver | Inc | Alt | `date(10)` |
| `ColaboradorId` | — | CRM \| Pessoa Física \| Colaborador | Ver | Inc | Alt | `int4(21)` |

---

## Mais (auditoria e crédito)

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `VerificacaoFilial` | * | Mais \| Análise de Crédito \| Consolidar (somar) as informações de crédito pelo CNPJ (8 dígitos)? | Ver | Inc | Alt | `bool()` |
| `NumeroInterno` | — | Mais \| Detalhes \| Número Interno | Ver | Inc | Alt | `varchar(255)` |
| `DataUltimoContato` | — | Mais \| Data do último contato | Ver | Inc | Alt | `timestamp(18)` |
| `Cadastro` | * | Mais \| Data de Cadastro | Ver | — | — | `timestamp(18)` |
| `UserId` | * | Mais \| Criado por | Ver | — | — | `varchar(128) [Ultra.Users] Usuários` |
| `UltimaAlteracao` | — | Mais \| Última Alteração | Ver | — | — | `timestamp(18)` |
| `UltimaCompra` | — | Mais \| Última Compra | Ver | — | — | `date()` |
| `UltimaVenda` | — | Mais \| Última Venda | Ver | — | — | `date()` |
| `RegiaoCentroCustoId` | — | Mais \| Região | Ver | Inc | Alt | `int4(21) [Util.CentroCustoRegiao] Região` |
| `Obs` | — | Mais \| Observações | Ver | Inc | Alt | `text()` |

---

## Classificação

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `CategoriaId` | — | Classificação \| Categoria | Ver | Inc | Alt | `int4(21) [Parceiro.Categoria] Categoria` |
| `SubCategoriaId` | — | Classificação \| Sub Categoria | Ver | Inc | Alt | `int4(21) [Parceiro.SubCategoria] Sub Categoria` |
| `GrupoId` | — | Classificação \| Grupo | Ver | Inc | Alt | `int4(21) [Parceiro.Grupo] Grupo` |
| `SubGrupoId` | — | Classificação \| Sub Grupo | Ver | Inc | Alt | `int4(21) [Parceiro.SubGrupo] Sub Grupo` |

---

## NF (pedidos e notas)

| Campo | NN | Descrição (Plune) | Ver | Inc | Alt | Tipo / XSchema |
|------:|:--:|-------------------|:---:|:---:|:---:|----------------|
| `TipoTransporteId` | — | NF \| Informações Padrões para Pedidos e Notas Fiscais de Emissão Própria \| Tipo de Transporte | Ver | Inc | Alt | `int4(21) [Venda.TipoTransporte] Tipo de Transporte` |
| `ConsumidorFinal` | * | NF \| Tipo Aplicação ICMS | Ver | Inc | Alt | `int4(21) [Produto.TipoAplicacaoICMS] Tipo Aplicação ICMS` |
| `ISSQNSubstituicaoTributaria` | * | NF \| ISSQN por ST | Ver | Inc | Alt | `bool()` |
| `IndicativoConsumidorFinal` | — | NF \| Operação com Consumidor Final | Ver | Inc | Alt | `bool()` |
| `EmailNFe` | — | NF \| E-Mail para envio de Notas | Ver | Inc | Alt | `Ultra::EmailMulti(512)` |
| `GrupoTributacaoId` | — | NF \| Grupo de Tributação | Ver | Inc | Alt | `int4(21) [Parceiro.GrupoTributacao] Grupo de Tributação` |
| `RegimeTributario` | * | NF \| Informação para NF de Entrada (Terceiros) \| Regime Tributário | Ver | Inc | Alt | `varchar(1) [Produto.RegimeTributario] Regime Tributário` |
| `SituacaoEspecialTomador` | — | NF \| NF de Serviço \| Situação Especial | Ver | Inc | Alt | `int4(21)` |

---

## Notas do export Plune

O sufixo `*` em **Nome da Coluna** no Plune corresponde à coluna **NN** nas tabelas acima.

*Documento gerado a partir do export de colunas Plune `Parceiro.tbParceiro`.*
