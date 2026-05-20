# Plune — API `Parceiro.tbParceiro` (clientes / parceiros)

Documentação da classe **Parceiro** do pacote **[Parceiro]**, schema **[Parceiro]**. No ERP Plune da Gebras, **clientes** usados em pedidos (`Venda.Pedido.ClienteId`) são registros desta tabela — o **ClassId** exposto na API é `Parceiro.tbParceiro`.

<a id="indice"></a>

## Índice

### Visão geral e integração

- [Papel na automação Gebras](#automacao)
- [Visão geral da classe](#visao-geral)
- [Convenções comuns (debug, protocolos)](#convencoes)
- [Resolução de `ClienteId` (Pipedrive → Plune)](#resolucao-cliente-id)
- [Mapeamento Pipedrive](#mapeamento-pipedrive)

### Métodos da API

| # | Método | Descrição |
|---|--------|-----------|
| 1 | [Browse](#1-browse) | Listar registros (múltiplos) |
| 2 | [Select](#2-select) | Consultar registro (único) |
| 3 | [Update](#3-update) | Alterar registro |
| 4 | [MultiUpdate](#4-multiupdate) | Alterar múltiplos registros |
| 5 | [Insert](#5-insert) | Incluir registro(s) |
| 6 | [Delete](#6-delete) | Excluir registro |
| 7 | [Download](#7-download) | Baixar conteúdo de campo/arquivo |
| 8 | [Download2](#8-download2) | Baixar conteúdo (plano) |
| 9 | [Call](#9-call) | Invocar função exposta |
| 10 | [AjaxFieldInput](#10-ajaxfieldinput) | Construir HTML de campo (tela / Ajax) |

### Metadados e banco

- [Detalhes do schema (Plune / banco)](#schema-banco)
- [Colunas — FieldId, permissões e tipos](Clientes-colunas.md) (`Clientes-colunas.md`)
- [Referências cruzadas](#referencias)
- [Testes e arquivos no repositório](#testes)

---

<a id="automacao"></a>

## Papel na automação Gebras

Fluxo relevante para **clientes**:

1. Deal **ganho** no Pipedrive → contrato (Word) → Clicksign.
2. Após assinatura (ou em modo teste), `plune_pedido.criar_pedido_plune()` cria `Venda.Pedido`.
3. Antes do **Insert** do pedido, o sistema localiza um registro **ativo** em `Parceiro.tbParceiro` pelo **CPF/CNPJ** (`NumeroContribuinte`) e, se necessário, desambigua pela **razão social** vinda do Pipedrive.
4. Se não houver parceiro por documento nem por razão social exata, cria um novo `Parceiro.tbParceiro`.
5. O `ParceiroId` encontrado ou criado vira `ClienteId` no pedido.

Implementação: `plune_pedido.py` (`_buscar_parceiros_por_documento`, `_buscar_parceiros_por_razao_social`, `_resolver_ou_criar_cliente_id`). URLs de exemplo históricas: `UrlClientes.md` (raiz do repo).

[↑ Voltar ao índice](#indice)

---

<a id="visao-geral"></a>

## Visão geral da classe

| Propriedade | Valor |
|-------------|-------|
| Assinatura | [1] Plune |
| Schema | [Parceiro] Parceiro |
| Tabela | `tbParceiro` |
| **ClassId** | `Parceiro.tbParceiro` |
| Descrição de registro | `NomRazaoSocial` (/1/Principal/Razão Social) |
| Tipo | [r] ORM → tabela DBMS |
| Acesso | `public` |
| Handler | `Ultra::Handler::ERP` |

Operações na API SOA: **Browse**, **Select**, **Insert**, **Update**, **Delete**, etc. — detalhes em [Métodos da API](#indice). **Este projeto** usa sobretudo **Browse** para localizar o parceiro antes do pedido.

[↑ Voltar ao índice](#indice)

---

<a id="convencoes"></a>

## Convenções comuns (debug, protocolos)

As APIs **HTTP**, **JavaScript** e **HTML/Template::Toolkit** oferecem em geral os **mesmos métodos e parâmetros**, mudando apenas a **sintaxe** da chamada.

Para **debug e testes**, todas reconhecem `__debug__=1`:

- Retorno estruturado (XML, JSON, etc.) **indentado** (pretty print).
- Pode incluir informações extras em **Warnings**.

**Não use `__debug__=1` em produção** — a performance é degradada.

**Protocolos de entrada** (quando aplicável):

- POST/GET HTTP (REST), query string simples ou multi-part.
- Objeto JavaScript (ORM em tela).
- Objeto HTML/Template::Toolkit (ORM no servidor).

As chamadas respeitam as **permissões do usuário logado**, não as do autor do script/template.

**Base URL (Gebras):** `{PLUNE_BASE_URL}/JSON/Parceiro.tbParceiro/{Método}?...` + `_AuthToken` (ver `.env` / `config.py`).

[↑ Voltar ao índice](#indice)

---

<a id="resolucao-cliente-id"></a>

## Resolução de `ClienteId` (Pipedrive → Plune)

Algoritmo em `_resolver_ou_criar_cliente_id(deal)`:

1. **Browse** com `Ativo=1` e `NumeroContribuinte` normalizado (só dígitos).
2. Filtra candidatos com documento igual ao do deal.
3. Se houver **razão social** no Pipedrive, compara nome normalizado (`normalizar_nome`):
   - **1** match por nome → usa esse `ParceiroId`.
   - **>1** match por nome → erro de ambiguidade.
4. Se **1** candidato por documento → usa esse `ParceiroId`.
5. Se **>1** candidato por documento e nome não resolve → erro pedindo conferência da razão social.
6. Se não houver candidato por documento, faz Browse por `NomRazaoSocial`.
7. Se houver **1** match exato por razão social → usa esse `ParceiroId` para não duplicar parceiro.
8. Se também não houver match por razão social, cria um novo `Parceiro.tbParceiro` e usa o `ParceiroId` retornado.

O pedido ainda envia cópia textual dos dados do cliente (`ClienteNome`, `ClienteNumero`, endereço, etc.) em `Venda.Pedido.Insert` — ver [Pedido-colunas.md](../Pedidos/Pedido-colunas.md) (seção Cliente).

[↑ Voltar ao índice](#indice)

---

<a id="mapeamento-pipedrive"></a>

## Mapeamento Pipedrive

Campos do deal usados na etapa de cliente/pedido (`pipedrive_fields.py`):

| Uso | Campo Pipedrive (custom field hash) | Plune / pedido |
|-----|-------------------------------------|----------------|
| Documento (busca Browse) | `FIELD_DOCUMENTO` | `NumeroContribuinte` → `ClienteId` |
| Razão social (desambiguação + pedido) | `FIELD_NOME_CLIENTE` | `NomRazaoSocial` → `ClienteNome` |
| Endereço | `FIELD_ENDERECO` | `EnderecoPrincipal` → `ClienteEndereco` |
| CEP (obrigatório só ao **criar** parceiro novo) | `FIELD_CEP` | `CEPPrincipal` → `ClienteCep` |
| Cidade | `FIELD_CIDADE` | `CidadePrincipalEx` → `ClienteCityName` |

[↑ Voltar ao índice](#indice)

---

## 1. Browse

<a id="1-browse"></a>

**Listar registros (múltiplos)**

| | |
|--|--|
| **Funcionalidade** | Listar registros da tabela, com filtros, colunas, funções, ordenação, paginação, etc. |
| **Nome do método** | `Browse` |

### URLs de exemplo (GET/POST)

| Saída | Exemplo de URL | Limitações |
|-------|----------------|------------|
| JSON | `/JSON/Parceiro.tbParceiro/Browse?__debug__=0&...` | Indicado para retornos de **1** registro. |
| JSONL | `/JSONL/Parceiro.tbParceiro/Browse?__debug__=0&...` | Qualquer tamanho; 1ª linha = meta-dados; demais = registros. |
| XML | `/XML/Parceiro.tbParceiro/Browse?__debug__=0&...` | Indicado para retornos de **1** registro. |
| TSV | `/TSV/Parceiro.tbParceiro/Browse?__debug__=0&...` | Grandes retornos; TAB/quebras viram espaços; última coluna = paginação/status. Ver **ErrorStatus**. |
| TSVX | `/TSVX/Parceiro.tbParceiro/Browse?__debug__=0&...` | Como TSV + colunas de valor exibido e valor estendido. |
| BSV | `/BSV/Parceiro.tbParceiro/Browse?__debug__=0&...` | Como TSV, sem exibição estendida; separador ASCII **17** entre colunas. |
| BSVX | `/BSVX/Parceiro.tbParceiro/Browse?__debug__=0&...` | Como TSVX; separador colunas ASCII **17**; subcolunas ASCII **18**. |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Parceiro.tbParceiro').Browse( {
 ColunaX:         '<filtro>'
 ColunaY:         '<filtro>'
 _BrowseSequence: ['ColunaX', 'ColunaY']
 _BrowseLimit:    15
 _Order:          ['ColunaX', 'ColunaY']
}, {
 onSucces:  function () { alert( this.data.row.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Exemplo HTML/Template::Toolkit (ORM)

```html
[%
 SET OBJ = Ultra.Class.Browse( 'Parceiro.tbParceiro', {
  'Parceiro.tbParceiro.ColunaX'         = '<filtro>'
  'Parceiro.tbParceiro.ColunaY'         = '<filtro>'
  '_Parceiro.tbParceiro.BrowseSequence' = [ 'ColunaX', 'ColunaY' ]
  '_Parceiro.tbParceiro.BrowseLimit'    = 15
  '_Parceiro.tbParceiro.Order'          = [ 'ColunaX', 'ColunaY' ]
 } );
) %]
```

### Parâmetros suportados (Browse)

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `Parceiro.tbParceiro.<Nome_do_Campo>=<Expressão_de_Busca>` | 0..N | Filtro no campo (expressões como na listagem HTML). |
| `_Parceiro.tbParceiro.Order=<Nome1,Nome2,...>` | 0..N | Ordenação. |
| `_Parceiro.tbParceiro.OrderDesc=<1\|0,...>` | 0..N | 0 = crescente, 1 = decrescente. |
| `_Parceiro.tbParceiro.OrderId=<1\|0>` | 0..N | Com FK: ordenar pelo **código** do registro. |
| `_Parceiro.tbParceiro.BrowseSequence=<Nome_do_Campo>` | 0..N | Campos a retornar. |
| `_Parceiro.tbParceiro.BrowseSequence=<Nome1>,<Nome2>,...` | 0..1 | Lista de campos em um parâmetro. |
| Prefixo `x99<NUM>_<Nome do Campo>` | — | Mesmo campo com funções diferentes (ex.: `x991_Nome`). |
| `_Parceiro.tbParceiro.ExportAll=1` | 0\|1 | Exportação: todos os campos. |
| `_Parceiro.tbParceiro.BrowseLimit=<INTEGER>` | N | Registros por página (default **30**, máx. **1000**). |
| `_Parceiro.tbParceiro.Page=<INTEGER>` | N | Página da consulta. |
| `_Parceiro.tbParceiro.GroupBy=<Nome_do_Campo>` | 0..1 | GROUP BY. |
| `_Parceiro.tbParceiro.OK=1` | 0\|1 | Interface HTML: submissão de listagem. |
| `_Parceiro.tbParceiro.<Campo>.Fn=<Função>` | 0..N | Função no campo (cascatear repetindo). |
| `_Parceiro.tbParceiro.<Campo>.Fg=<Função>` | 0..N | Função de agregação (GROUP BY). |

### Retorno (Browse)

```json
{
 "allRows" : "198",
 "Method"  : "Browse",
 "data" : { "row" : [ { "NomeDoCampo" : { "value": "0", "resolved": "..." } } ] },
 "rows"         : 30,
 "ErrorStatus"  : null,
 "ErrorStatus2" : null,
 "canDelete"    : "1",
 "canUpdate"    : "1",
 "canInsert"    : "1",
 "ClassId"      : "Parceiro.tbParceiro"
}
```

### Uso na automação Gebras

Implementação em `plune_pedido._buscar_parceiros_por_documento()`:

| Parâmetro | Valor |
|-----------|-------|
| `Parceiro.tbParceiro.Ativo` | `1` |
| `Parceiro.tbParceiro.NumeroContribuinte` | CPF/CNPJ só dígitos |
| `_Parceiro.tbParceiro.BrowseSequence` | `ParceiroId`, `NumeroContribuinte`, `NomRazaoSocial` |
| `_Parceiro.tbParceiro.BrowseLimit` | `30` |

Exemplos de URL: `UrlClientes.md` na raiz do repositório. Host: `https://www-gebras.plune.com.br`.

[↑ Voltar ao índice](#indice)

---

## 2. Select

<a id="2-select"></a>

**Consultar registro único**

| | |
|--|--|
| **Funcionalidade** | Consultar todas as colunas de **um** registro. |
| **Nome do método** | `Select` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/Select?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>` |
| XML | `/XML/Parceiro.tbParceiro/Select?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>` |

### Parâmetros suportados (Select)

**Obrigatório:** todos os campos da **chave primária** (`EmpresaId`, `ParceiroId`) ou chave única alternativa.

| Parâmetro | Descrição |
|-----------|-----------|
| `_Parceiro.tbParceiro.IgnoreFields` | Campos a omitir na resposta (`Campo1,Campo2`). |
| `_Parceiro.tbParceiro.FieldSequence` | Apenas estes campos na resposta. |
| `_Parceiro.tbParceiro.FormSequence` | Campos no formulário HTML. |
| `_Parceiro.tbParceiro.XMethod` | Método de tabela filha após o principal. |
| `_Parceiro.tbParceiro.XForeignKeyId` | FK da tabela filha (com `XMethod`). |

Retorno: objeto `Field` com `value`, `resolved`, `array`, `url` por campo — estrutura análoga ao [Select em Pedido](../Pedidos/Pedido.md#2-select).

[↑ Voltar ao índice](#indice)

---

## 3. Update

<a id="3-update"></a>

**Alterar registro**

| | |
|--|--|
| **Funcionalidade** | Alterar uma ou mais colunas de um único registro. |
| **Nome do método** | `Update` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/Update?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>&<Coluna>=<Valor>&...` |
| XML | `/XML/Parceiro.tbParceiro/Update?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>&<Coluna>=<Valor>&...` |

### Regras de valores

- **PK obrigatória** para identificar o registro.
- Campo **omitido** → mantém valor antigo.
- Campo **presente sem valor** → **NULL**.
- Campo **com valor** → substitui o antigo.
- Valores em formato de **tela** (BR): datas `dd/mm/aaaa`, números `1.213,45`.
- Campos **ARRAY**: repetir `A.B.C=1&A.B.C=2` na query string.
- Retorno igual ao **Select** (reconsulta pós-triggers).

Parâmetros úteis: `_Parceiro.tbParceiro.OK=1` (HTML), `NextMethod`, `NextQuery`, `FormSequence`. Upload: `multipart/form-data` (RFC 2388).

[↑ Voltar ao índice](#indice)

---

## 4. MultiUpdate

<a id="4-multiupdate"></a>

**Alterar múltiplos registros**

| | |
|--|--|
| **Funcionalidade** | Alterar colunas em um ou mais registros. |
| **Nome do método** | `MultiUpdate` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/MultiUpdate?__debug__=0&_Parceiro.tbParceiro.MSelect=<QueryString>&Parceiro.tbParceiro.doUpdate=<Coluna>%3D<valor>...` |

| Parâmetro | Descrição |
|-----------|-----------|
| `_Parceiro.tbParceiro.MSelect=<Campo=Valor&...>` | Um registro alvo por ocorrência (QueryString da PK). |
| `_Parceiro.tbParceiro.doUpdate=<Campo=Valor>` | Coluna e novo valor (formato **banco**, americano). |

Retorno: `rows` (registros afetados) e `ErrorStatus` se houver falha.

[↑ Voltar ao índice](#indice)

---

## 5. Insert

<a id="5-insert"></a>

**Incluir registro**

| | |
|--|--|
| **Funcionalidade** | Incluir novo registro; suporta tabelas **1:1** e **embutidas** na mesma transação. |
| **Nome do método** | `Insert` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/Insert?__debug__=0&Parceiro.tbParceiro.<Coluna>=<Valor>&...` |
| XML | `/XML/Parceiro.tbParceiro/Insert?__debug__=0&Parceiro.tbParceiro.<Coluna>=<Valor>&...` |

> **Automação Gebras:** o fluxo chama Insert nesta tabela somente quando não encontra parceiro ativo por CPF/CNPJ nem por razão social exata.

### Regras de valores

- Campo omitido → default do BD ou NULL.
- Campo vazio na query → NULL.
- PK pode vir de serial/trigger; não é obrigatório informar todas as PKs.
- Retorno igual ao **Select** (ou **Browse** em inclusão múltipla).

Parâmetros: `NextMethod`, `NextQuery`, `FormSequence`, `XMethod=MultiInsert` (vários registros na mesma transação; ver doc Plune).

### Tabelas 1:1 (Insert na mesma transação)

| Tabela | `Slaves` / `SlavesSave` | `isSlave` (FK) |
|--------|-------------------------|----------------|
| `Parceiro.tbCliente` | `Parceiro.tbCliente` | `tbCliente_TransportadoraId_tbParceiro_fkey60549` |
| `Parceiro.tbTransportadora` | `Parceiro.tbTransportadora` | `Parceiro_tbTransportadora_fkey_1319116416` |
| `Parceiro.tbFornecedor` | `Parceiro.tbFornecedor` | `tbFornecedor_EmpresaId_fkey` |
| `Parceiro.tbRepresentante` | `Parceiro.tbRepresentante` | `tbRepresentante_EmpresaId_fkey` |

Para cada tabela 1:1: `_Parceiro.tbParceiro.Slaves`, `_Parceiro.tbParceiro.SlavesSave`, `<Tabela>.isSlave`, e `Parceiro.<Tabela>.<Campo>=<Valor>`.

### Tabelas embutidas (1:N)

Repetir campos da tabela filha na query string (cada repetição = novo registro). Exigir `Slaves`, `SlavesSave` e `isSlave` na request real. Todos os INSERTs na mesma transação (rollback se um falhar).

[↑ Voltar ao índice](#indice)

---

## 6. Delete

<a id="6-delete"></a>

**Excluir registro**

| | |
|--|--|
| **Funcionalidade** | Exclui o registro (irreversível). |
| **Nome do método** | `Delete` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/Delete?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>` |
| XML | `/XML/Parceiro.tbParceiro/Delete?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>` |

**Obrigatório:** toda a chave primária. Permissão global de exclusão nesta classe: **NÃO** (exportação original) — pode variar por usuário/registro.

Retorno: `Method`, `ErrorStatus`, `ErrorStatus2`, `canDelete`, `canUpdate`, `canInsert`, `ClassId`.

[↑ Voltar ao índice](#indice)

---

## 7. Download

<a id="7-download"></a>

**Baixar conteúdo de campo/arquivo**

Campos `Ultra::external_file` (ex.: `FotoContatoPrincipal`) exigem Download para o binário completo. Browse/Select expõem `url` apontando para este método.

| Saída | URL |
|-------|-----|
| Binária ou HTML | `/Class/Parceiro.tbParceiro/Download?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>&_Parceiro.tbParceiro.File=<Campo>` |
| Binária ou texto | `/REST/Parceiro.tbParceiro/Download?__debug__=0&EmpresaId=<Valor>&ParceiroId=<Valor>&_Parceiro.tbParceiro.File=<Campo>` |

**Obrigatório:** PK + `_Parceiro.tbParceiro.File`. `/Class` tende a envelope HTML; `/REST` retorna arquivo puro (preferível M2M).

[↑ Voltar ao índice](#indice)

---

## 8. Download2

<a id="8-download2"></a>

**Baixar conteúdo (plano)**

Comportamento como **Download**, porém em HTML/TEXT evita envelope com menu PDF/DOC — conteúdo mais puro. Equivalente a **Download** via saída **REST** em muitos casos.

| | |
|--|--|
| Class | `/Class/Parceiro.tbParceiro/Download2?...` |
| REST | `/REST/Parceiro.tbParceiro/Download2?...` |

[↑ Voltar ao índice](#indice)

---

## 9. Call

<a id="9-call"></a>

**Invocar função exposta**

Funções de banco expostas pela tabela (auxiliares de tela/API).

| | |
|--|--|
| JSON | `/JSON/Parceiro.tbParceiro/Call?__debug__=0&_Parceiro.tbParceiro.Function=<Nome>&_Parceiro.tbParceiro.Params=<P1>&_Parceiro.tbParceiro.Params=<P2>...` |

Retorno: `data.row` como **array de arrays** (SET OF).

[↑ Voltar ao índice](#indice)

---

## 10. AjaxFieldInput

<a id="10-ajaxfieldinput"></a>

**Construir HTML de campo (tela / Ajax)**

Uso **exclusivo em tela** (JavaScript), retorna HTML do campo como no formulário Insert/Update.

```javascript
new Ultra.Class( 'Parceiro.tbParceiro' ).process(
 'AjaxFieldInput',
 {
  _XMethod: 'NomeDoCampo',
  _FormId:  'FormId',
  Campo1:   'Valor1',
  _Instantiate: 1,
 },
 { targetElement: elemento }
);
```

[↑ Voltar ao índice](#indice)

---

## Referência rápida de caminhos

| Operação | Padrão JSON |
|----------|-------------|
| Browse | `/JSON/Parceiro.tbParceiro/Browse?...` |
| Select | `/JSON/Parceiro.tbParceiro/Select?...` |
| Update | `/JSON/Parceiro.tbParceiro/Update?...` |
| MultiUpdate | `/JSON/Parceiro.tbParceiro/MultiUpdate?...` |
| Insert | `/JSON/Parceiro.tbParceiro/Insert?...` |
| Delete | `/JSON/Parceiro.tbParceiro/Delete?...` |
| Call | `/JSON/Parceiro.tbParceiro/Call?...` |
| Download | `/REST/Parceiro.tbParceiro/Download?...` ou `/Class/...` |
| Download2 | `/REST/Parceiro.tbParceiro/Download2?...` ou `/Class/...` |

---

<a id="schema-banco"></a>

## Detalhes do schema (Plune / banco de dados)

Metadados exportados do Plune para **`Parceiro.tbParceiro`**.

### Identificação

| Propriedade | Valor |
|-------------|-------|
| Nome original da classe | `tbParceiro` |
| **ClassId** | `Parceiro.tbParceiro` |
| Pacote de origem | [Parceiro] Parceiro |

### Permissões globais

Referem-se ao **usuário logado no momento da exportação** (`biview53@gmail.com` na exportação original). Outros usuários podem diferir. Alterar/visualizar/excluir pode ainda depender do registro ou de tabelas subordinadas.

| Consultar | Incluir | Alterar | Excluir |
|:---------:|:-------:|:-------:|:-------:|
| SIM | SIM | SIM | **NÃO** |

### Chaves primárias

| Campo | Rótulo |
|-------|--------|
| `EmpresaId` | Empresa |
| `ParceiroId` | Código |

Na API Gebras, `EmpresaId` alinha-se a `CompanyId` / `PLUNE_COMPANY_ID` (ex.: `869`).

### Chaves únicas

*(nenhuma listada na exportação)*

### Índices (performance)

| Índice | Tipo | Colunas |
|--------|------|---------|
| `tbParceiro_pkey` | UNIQUE KEY | `EmpresaId`, `ParceiroId` |
| `Parceiro_NumeroContribuinte_idx` | INDEX | `NumeroContribuinte` (/1/Cadastro/Número do CNPJ / CPF) |
| `tbParceiro_Empresa_UFCity_ix` | INDEX | `EmpresaId`, `UFPrincipalId`, `CidadePrincipalId` |

A busca por **CPF/CNPJ** no projeto usa coluna indexada (`NumeroContribuinte`).

### Campos de descrição de registro

| Campo | Caminho |
|-------|---------|
| `NomRazaoSocial` | /1/Principal/Razão Social |

### Comportamento da classe

| Propriedade | Valor |
|-------------|-------|
| Controla armazenamento | Sim |
| Tipo de permissionamento | Estático |
| Rastreabilidade | Nenhuma |
| SQL padrão ORDER BY | `%SELF%."NomRazaoSocial"` |

**Handler @ISA:** `Ultra::Plugin::CRUD::Auth::Company`, `Ultra::Handler::CRUD`, `Ultra::Handler`, `Ultra::Class::SQL`.

**Arquivos externos:** diretório `~/raw` (`/home/gebras/raw`), extensão padrão `bin`.

### Referências naturais (FK — esta tabela referencia)

| Tabela / classe | Relação (nome na exportação) |
|-----------------|------------------------------|
| Minha Empresa | `tbParceiro_EmpresaId_fkey` |
| País | `Parceiro_tbParceiro_fkey_1265909179` |
| Estado/Província | `Parceiro_tbParceiro_fkey_1265909150` |
| Cidade | `tbParceiro_PaisPrincipalId_fkey` |
| Tipo de Parceiros | `tbParceiro_Tipo_Tipo_fkey17969` |
| Tipo de Contribuinte | `Parceiro_tbParceiro_fkey_1265919443` |
| Regime Tributário | `Parceiro_tbParceiro_fkey_1289911204` |
| Grupo / Sub Grupo / Categoria / Sub Categoria | várias `Parceiro_tbParceiro_fkey_*` |
| CNAE (Divisão) | `tbParceiroRamoAtividadeDivisao_fk` |
| Bancos, Usuários, Áreas, Região, etc. | ver exportação completa no Plune |

### Referências inversas (outras tabelas referenciam `tbParceiro`)

A tabela é hub do cadastro comercial. Destaques para a automação e vendas:

| Tabela / classe | Uso |
|-----------------|-----|
| **Pedido** (`Venda.Pedido`) | `ClienteId`, `TransportadoraId` → FK para `tbParceiro` |
| **Cliente** (`tbCliente`) | extensão/cadastro de cliente ligado ao parceiro |
| **Parceiros:Contatos** (`tbContatoParceiro`) | contatos do parceiro |
| Nota Fiscal, Contas a Receber, Contratos, Cotação, Ordem de Compra, etc. | dezenas de FKs (exportação Plune lista completa) |

Para colunas do pedido que espelham dados do cliente, ver [Pedido-colunas.md](../Pedidos/Pedido-colunas.md). Catálogo completo desta tabela: [Clientes-colunas.md](Clientes-colunas.md).

[↑ Voltar ao índice](#indice)

---

<a id="referencias"></a>

## Referências cruzadas

| Documento | Conteúdo |
|-----------|----------|
| [Pedido.md](../Pedidos/Pedido.md) | API `Venda.Pedido` (Insert após assinatura) |
| [Clientes-colunas.md](Clientes-colunas.md) | FieldId, permissões e tipos de `Parceiro.tbParceiro` |
| [Pedido-colunas.md](../Pedidos/Pedido-colunas.md) | `ClienteId`, `ClienteNome`, `ClienteNumero`, endereço |
| `UrlClientes.md` | URLs Browse copiadas do navegador |
| `ENTENDIMENTO_SISTEMA.md` | Fluxo Pipedrive → Clicksign → Plune |

[↑ Voltar ao índice](#indice)

---

<a id="testes"></a>

## Testes e arquivos no repositório

```bash
# Browse por documento (e opcionalmente razão social)
python tests/test_plune_browse_cliente.py 35969644072
python tests/test_plune_browse_cliente.py 359.696.440-72 "Razao Social"

# Pedido completo a partir de deal_id
python tests/test_plune_insert_pedido.py <deal_id>
```

| Arquivo | Função |
|---------|--------|
| `plune_pedido.py` | Browse parceiro + Insert pedido |
| `pipedrive_fields.py` | Hashes dos campos do deal |
| `config.py` / `.env` | `PLUNE_BASE_URL`, `PLUNE_AUTH_TOKEN`, `PLUNE_COMPANY_ID` |

**Regra operacional:** a automação evita duplicidade buscando antes por CPF/CNPJ e razão social. Se nenhum parceiro ativo for encontrado, cria `Parceiro.tbParceiro` com cadastro mínimo e usa o `ParceiroId` retornado no pedido.

[↑ Voltar ao índice](#indice)

---

*Documento alinhado à documentação Plune da classe `Parceiro.tbParceiro`, export de schema/colunas e uso em `plune_pedido.py` no repositório AutomacaoGebras.*
