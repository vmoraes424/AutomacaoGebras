# Plune — API `Venda.Pedido`

Documentação da classe **Pedido** do pacote **Venda**, schema **Venda** (Vendas). A classe expõe operações via **WebServices SOA** (HTTP REST, JavaScript ORM e HTML/Template::Toolkit).

<a id="indice"></a>

## Índice

### Visão geral e convenções

- [Visão geral da classe](#visão-geral-da-classe)
- [Convenções comuns (debug, protocolos)](#convenções-comuns-debug-protocolos)

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
| 8 | [Download2](#8-download2) | Baixar conteúdo de campo/arquivo (plano) |
| 9 | [Call](#9-call) | Invocar função exposta |
| 10 | [AjaxFieldInput](#10-ajaxfieldinput) | Construir HTML de campo (tela / Ajax) |

### Inserção com tabelas embutidas (Insert)

- [Visão geral — tabelas embutidas](#embutidas-visao-geral)
- [PedidoContratoParcela](#embutida-parcela)
- [PedidoItem](#embutida-item)

### Metadados e banco de dados

- [Detalhes do schema (Plune / banco)](#schema-banco)
- [Colunas — FieldId, permissões e tipos](Pedido-colunas.md) (`Pedido-colunas.md`)

---

## Visão geral da classe

**Pedido** é uma classe do pacote **[Venda]** na schema **[Venda]** (Vendas).

O acesso ocorre por API, permitindo integração com outros sistemas. Os métodos listados no [índice](#indice) compartilham, em geral, os **mesmos parâmetros conceituais**; muda apenas a **sintaxe** (query string, objeto JavaScript ou Template::Toolkit).

[↑ Voltar ao índice](#indice)

---

## Convenções comuns (debug, protocolos)

As APIs **HTTP**, **JavaScript** e **HTML/Template::Toolkit** reconhecem, para **debug e testes**, o parâmetro `__debug__=1`:

- Retorno estruturado (XML, JSON, etc.) **indentado** (pretty print).
- Pode incluir informações extras no retorno, por exemplo em **Warnings**.

**Não use `__debug__=1` em produção** — a performance é degradada.

**Protocolos de entrada** (quando aplicável ao método):

- POST/GET HTTP (REST), query string simples ou multi-part.
- Objeto JavaScript (ORM em tela).
- Objeto HTML/Template::Toolkit (ORM no servidor).

As chamadas respeitam as **permissões do usuário logado**, não as do autor do script/template.

[↑ Voltar ao índice](#indice)

---

## 1. Browse

**Listar registros (múltiplos)**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Listar registros da tabela, com filtros, colunas, funções, ordenação, paginação, etc. |
| **Nome do método** | `Browse` |

### URLs de exemplo (GET/POST)

| Saída | Exemplo de URL | Limitações |
|-------|----------------|------------|
| JSON | `/JSON/Venda.Pedido/Browse?__debug__=0&...` | Indicado para retornos de **1** registro. |
| JSONL | `/JSONL/Venda.Pedido/Browse?__debug__=0&...` | Qualquer tamanho; 1ª linha = meta-dados; demais = registros. |
| XML | `/XML/Venda.Pedido/Browse?__debug__=0&...` | Indicado para retornos de **1** registro. |
| TSV | `/TSV/Venda.Pedido/Browse?__debug__=0&...` | Grandes retornos; TAB/quebras viram espaços; última coluna = paginação/status (QueryString). Ver **ErrorStatus**. |
| TSVX | `/TSVX/Venda.Pedido/Browse?__debug__=0&...` | Como TSV + colunas de valor exibido e valor estendido (ou nulo, mantendo 3 posições por campo). |
| BSV | `/BSV/Venda.Pedido/Browse?__debug__=0&...` | Como TSV, sem exibição estendida; separador ASCII **17** entre colunas. |
| BSVX | `/BSVX/Venda.Pedido/Browse?__debug__=0&...` | Como TSVX; separador colunas ASCII **17**; subcolunas ASCII **18**. |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').Browse( {
 // Parâmetros da consulta (filtros em colunas ou opções)
 ColunaX:         '<filtro>'
 ColunaY:         '<filtro>'
 _BrowseSequence: ['ColunaX', 'ColunaY']
 _BrowseLimit:    15
 _Order:          ['ColunaX', 'ColunaY']
}, {
 // Eventos pós submissão
 onSucces:  function () { alert( this.data.row.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); }, // Erro na consulta (parâmetro inválido, etc)
} );
```

### Exemplo HTML/Template::Toolkit (ORM)

```html
[%
 SET OBJ = Ultra.Class.Browse( 'Venda.Pedido', {
  'Venda.Pedido.ColunaX'         = '<filtro>'
  'Venda.Pedido.ColunaY'         = '<filtro>'
  '_Venda.Pedido.BrowseSequence' = [ 'ColunaX', 'ColunaY' ]
  '_Venda.Pedido.BrowseLimit'    = 15
  '_Venda.Pedido.Order'          = [ 'ColunaX', 'ColunaY' ]
 } );
) %]
<ol>
[% FOREACH ROW IN OBJ.data.row %]
<li>[% ROW.item('ColunaX').value; %]   <!-- Valor nativo do campo -->
<li>[% ROW.item('ColunaX').resolved %] <!-- Resolução do campo, se for uma chave estrangeira -->
<li>[% ROW.item('ColunaX').url %]      <!-- URL para Download, em casos de campos com armazenamento externo - upload -->
<li>[% ROW.item('ColunaX').array;      <!-- Estrutura parseada da array -->
       ROW.item('ColunaX').array.0;    <!-- caso o campo seja uma array/lista de valores -->
       ROW.item('ColunaX').array.1; %]
[% END %]
</ol>
```

### Parâmetros suportados (Browse)

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `Venda.Pedido.<Nome_do_Campo>=<Expressão_de_Busca>` | 0..N | Filtro no campo. Expressões como nos formulários de listagem HTML. |
| `_Venda.Pedido.Order=<Nome1,Nome2,...>` | 0..N | Ordenação; vários campos separados por vírgula. |
| `_Venda.Pedido.OrderDesc=<1\|0,...>` | 0..N | 0 = crescente, 1 = decrescente (por campo ordenado). |
| `_Venda.Pedido.OrderId=<1\|0>` | 0..N | Com FK: 1 = ordenar pelo **código** do registro, não pela resolução. |
| `_Venda.Pedido.BrowseSequence=<Nome_do_Campo>` | 0..N | Campos a retornar (pode repetir o parâmetro). |
| `_Venda.Pedido.BrowseSequence=<Nome1>,<Nome2>,...` | 0..1 | Lista de campos em um único parâmetro. |
| Prefixo `x99<NUM>_<Nome do Campo>` | — | Mesmo campo mais de uma vez com funções diferentes (ex.: `x991_Nome`, `x992_Nome`). |
| `_Venda.Pedido.ExportAll=1` | 0\|1 | Exportação: força todos os campos (sobrescreve BrowseSequence). |
| `_Venda.Pedido.BrowseLimit=<INTEGER>` | N | Registros por página (default **30**, máx. **1000**). |
| `_Venda.Pedido.Page=<INTEGER>` | N | Página da consulta. |
| `_Venda.Pedido.GroupBy=<Nome_do_Campo>` | 0..1 | Agrupamento (GROUP BY). |
| `_Venda.Pedido.OK=1` | 0\|1 | Interface HTML (Class.cgi): 1 = submissão de listagem válida. |
| `_Venda.Pedido.<Nome_do_Campo>.Fn=<Função>` | 0..N | Função no campo. Cascatear repetindo o parâmetro. Parâmetros da função: `/Valor` após o nome. Ex.: `Html::input::Funcion::numeric::soma_campo/ValorTotal`. |
| `_Venda.Pedido.<Nome_do_Campo>.Fg=<Função>` | 0..N | Função de **agregação** (com GROUP BY). |

### Retorno (Browse)

```json
{
 "allRows" : "198",
 "Method"  : "Browse",
 "data" : {
  "row" : [
           {
            "NomeDoCampo" : {
               "value"    : "0",
               "array"    : ["A","B"],
               "resolved" : "* Produto/Material"
            },
            "StatusId" : {
               "value"    : "1",
               "resolved" : "Ativo"
            },
            "_g.canDelete" : "1",
            "_g.canUpdate" : "1"
       }
      ]
 },
 "rows"         : 30,
 "ErrorStatus"  : null,
 "ErrorStatus2" : null,
 "canDelete"    : "1",
 "canUpdate"    : "1",
 "canInsert"    : "1",
 "ClassId"      : "Produto.Produto"
}
```

[↑ Voltar ao índice](#indice)

---

## 2. Select

**Consultar registro único**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Consultar todas as colunas de **um** registro. |
| **Nome do método** | `Select` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Venda.Pedido/Select?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>` |
| XML | `/XML/Venda.Pedido/Select?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>` |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').Select( {
 // Parâmetros da consulta (devem ser especificadas todas as chaves primárias)
 ColunaX:         '<Valor>'
 ColunaY:         '<Valor>'
}, {
 onSucces:  function () { alert( this.Field.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Exemplo Template::Toolkit (ORM)

> **Nota:** Na documentação original do Plune, o exemplo abaixo usa `Ultra.Class.Browse`; para **Select**, o equivalente esperado é `Ultra.Class.Select` com os mesmos parâmetros de chave.

```html
[%
 SET OBJ = Ultra.Class.Select( 'Venda.Pedido', {
  'Venda.Pedido.ColunaX'         = '<Valor>'
  'Venda.Pedido.ColunaY'         = '<Valor>'
 } );
) %]
[% IF OBJ.ErrorStatus %]
 ERRO:[% OBJ.ErrorStatus %]
[% ELSE %]
 <ol>
  <li>[% OBJ.Field.item('ColunaX').value %]
  <li>[% OBJ.Field.item('ColunaY').value %]
 </ol>
[% END %]
```

### Parâmetros suportados (Select)

**Obrigatório:** todos os pares nome/valor da **chave primária** (ou chave única alternativa, se existir).

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `_Venda.Pedido.IgnoreFields` | 0..1 | Campos a omitir na resposta (ex.: `Campo1,Campo2`). Também usado após **Insert**/**Update** (redirecionam para Select). |
| `_Venda.Pedido.FieldSequence` | 0..1 | Apenas estes campos na resposta (oposto de IgnoreFields). |
| `_Venda.Pedido.FormSequence` | 0..1 | Campos no formulário HTML. |
| `_Venda.Pedido.XMethod` | 0..1 | Método de tabela **filha** após o principal (ex.: Browse da filha). |
| `_Venda.Pedido.XForeignKeyId` | 0..1 | Nome da FK da filha para o XMethod (ex.: `Schema_TabelaX_fkey1`). |

### Retorno (Select)

```json
{
 "Method"  : "Select",
 "Field" : {
            "NomeDoCampo" : {
               "value"    : "0",
               "resolved" : "* Produto/Material",
               "array"    : [ "..." ],
               "url"      : "http://..."
            },
            "StatusId" : {
               "value"    : "1",
               "resolved" : "Ativo"
            }
 },
 "ErrorStatus"  : null,
 "ErrorStatus2" : null,
 "canDelete"    : "1",
 "canUpdate"    : "1",
 "canInsert"    : "1",
 "ClassId"      : "Produto.Produto"
}
```

[↑ Voltar ao índice](#indice)

---

## 3. Update

**Alterar registro**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Alterar uma ou mais colunas de **um** registro. |
| **Nome do método** | `Update` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Venda.Pedido/Update?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&<NomeDaColuna>=<Valor>&...` |
| XML | `/XML/Venda.Pedido/Update?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&<NomeDaColuna>=<Valor>&...` |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').Update( {
 // Chaves primárias do registro + campos a alterar
 ColunaX:         '<Valor>'
 ColunaY:         '<Valor>'
 ColunaZ:         '<Valor>'
}, {
 // Retorno bem-sucedido equivale ao Select
 onSucces:  function () { alert( this.Field.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Exemplo Template::Toolkit (ORM)

```html
[%
 SET OBJ = Ultra.Class.Update( 'Venda.Pedido', {
  'Venda.Pedido.ColunaX'         = '<Valor>'
  'Venda.Pedido.ColunaY'         = '<Valor>'
  'Venda.Pedido.ColunaZ'         = '<Valor>'
 } );
) %]
[% IF OBJ.ErrorStatus %]
 ERRO:[% OBJ.ErrorStatus %]
[% ELSE %]
 <ol>
  <li>[% OBJ.Field.item('ColunaX').value %]
  <li>[% OBJ.Field.item('ColunaY').value %]
 </ol>
[% END %]
```

### Parâmetros suportados (Update)

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `_Venda.Pedido.OK=1` | 0\|1 | HTML: 1 = submissão para gravação. |
| `Venda.Pedido.<NomeDoCampo>=<Valor>` | 0..N | Valores no formato de **tela** (pt-BR: datas `dd/mm/aaaa`, números `1.213,45`). Arrays: repetir o mesmo par nome=valor na query string. |
| `_Venda.Pedido.NextMethod=<Method>` | 0..1 | Saída alternativa após gravar (default: **Select**). Pode ser Browse, Download, etc. Em tela: Update, Insert, InsertSelect. Se houver erro, não aplica NextMethod — veja **ErrorStatus**. |
| `_Venda.Pedido.NextQuery=<QueryString>` | 0..1 | Com `NextMethod=Browse`, parâmetros da listagem (RFC 3986, 2396, 3875). Ex.: `_BrowseSequence=Campo1,Campo2&Campo1=100&Campo3=>0`. |
| `_Venda.Pedido.FormSequence` | 0..1 | Campos do formulário HTML. |

**Upload:** usar `multipart/form-data` (RFC 2388).

**Chave e valores:**

- Informar **todos** os campos da **PK** (ou chave única).
- Informar **pelo menos um** campo a alterar.
- Campo **omitido** na query → mantém valor anterior.
- Campo presente **sem valor** → **NULL**.
- Campo com valor → substitui o anterior.

**Triggers / permissões:** o retorno é como **Select** (estado real após gatilhos).

### Retorno (Update)

Igual ao **Select** — reconsulta o registro após a gravação.

[↑ Voltar ao índice](#indice)

---

## 4. MultiUpdate

**Alterar múltiplos registros**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Alterar colunas em **um ou mais** registros. |
| **Nome do método** | `MultiUpdate` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Venda.Pedido/MultiUpdate?__debug__=0&_Venda.Pedido.MSelect=<IdentificadorDoRegistro>&Venda.Pedido.doUpdate=<NomeDaColuna>%3D<valor>...` |
| XML | `/XML/Venda.Pedido/MultiUpdate?__debug__=0&_Venda.Pedido.MSelect=<IdentificadorDoRegistro>&Venda.Pedido.doUpdate=<NomeDaColuna>%3D<valor>...` |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').MultiUpdate( {
 '_MSelect':  'Id=<Valor>'
 '_MSelect':  'Id=<Valor>'
 '_doUpdate': 'ColunaX=<Valor>'
 '_doUpdate': 'ColunaY=<Valor>'
 '_doUpdate': 'ColunaZ=<Valor>'
}, {
 onSucces:  function () { alert( this.rows ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Parâmetros suportados (MultiUpdate)

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `_Venda.Pedido.MSelect=<Campo1=Valor&...>` | 0..N | Identificação do registro (QueryString). Um `_MSelect` por registro. |
| `_Venda.Pedido.doUpdate=<CampoX=Valor>` | 0..N | Coluna e novo valor (QueryString). **Exceção:** valor no formato do **banco** (americano), não o de tela. |

### Retorno (MultiUpdate)

Indica erro (se houver) e quantidade de registros afetados em **`rows`** (não é o mesmo retorno detalhado do Select).

[↑ Voltar ao índice](#indice)

---

## 5. Insert

**Incluir registro**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Incluir novo registro. Tabelas embutidas podem ser incluídas na **mesma transação**. |
| **Nome do método** | `Insert` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Venda.Pedido/Insert?__debug__=0&<NomeDaColuna>=<Valor>&...` |
| XML | `/XML/Venda.Pedido/Insert?__debug__=0&<NomeDaColuna>=<Valor>&...` |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').Insert( {
 ColunaX:         '<Valor>'
 ColunaY:         '<Valor>'
 ColunaZ:         '<Valor>'
}, {
 onSucces:  function () { alert( this.Field.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Exemplo Template::Toolkit (ORM)

```html
[%
 SET OBJ = Ultra.Class.Insert( 'Venda.Pedido', {
  'Venda.Pedido.ColunaX'         = '<Valor>'
  'Venda.Pedido.ColunaY'         = '<Valor>'
  'Venda.Pedido.ColunaZ'         = '<Valor>'
 } );
) %]
[% IF OBJ.ErrorStatus %]
 ERRO:[% OBJ.ErrorStatus %]
[% ELSE %]
 <ol>
  <li>[% OBJ.Field.item('ColunaX').value %]
  <li>[% OBJ.Field.item('ColunaY').value %]
 </ol>
[% END %]
```

### Parâmetros suportados (Insert)

| Parâmetro | Ocorrência | Descrição |
|-----------|------------|-----------|
| `_Venda.Pedido.OK=1` | 0\|1 | HTML: 1 = submissão para gravação. |
| `Venda.Pedido.<NomeDoCampo>=<Valor>` | 0..N | Formato de tela (pt-BR). Arrays: repetir par nome=valor. |
| `_Venda.Pedido.NextMethod` / `NextQuery` / `FormSequence` | — | Mesmo conceito que em **Update** (saída após inclusão; default **Select**). |
| `_Venda.Pedido.XMethod=MultiInsert` | 0..1 | Vários registros na mesma transação; repetir campos na query. Falha em um → rollback; **ErrorAtIndex** aponta o primeiro com erro. **Limitações:** sem ARRAY, upload ou tabelas embutidas. Exige permissão de inclusão múltipla na tabela. |

**Notas de valores (trecho genérico da doc Plune):** omitir campo → default do BD ou NULL; campo vazio → NULL; PK pode vir de serial/trigger; triggers podem alterar o resultado — retorno pós-gravação como **Select**.

**Tabelas 1:1:** esta tabela **não** possui 1:1 documentadas aqui.

<a id="embutidas-visao-geral"></a>

### Tabelas embutidas (visão geral)

Permitem inserir registros filhos na mesma transação do pai.

**Regras:**

- Repetir os campos da tabela embutida na URL: cada repetição alinha um **novo** registro filho.
- Se **N** filhos, **todos** os campos enviados devem ter **N** valores (mesmo nulos), na **mesma ordem**, para pareamento.
- Incluir parâmetros `Slaves`, `SlavesSave` e `isSlave` conforme cada tabela (ver abaixo).

Exemplo genérico (conceito):

`Venda.Pedido.ColunaA=1&Venda.Pedido.ColunaB=2&TabelaEmbutida1.ColunaC=3&TabelaEmbutida1.ColunaD=4&TabelaEmbutida1.ColunaC=5&TabelaEmbutida1.ColunaD=6`

→ 1 pedido (A=1, B=2) e 2 linhas na embutida.

Transação: **BEGIN/COMMIT**; falha → **ROLLBACK** e erro na resposta.

<a id="embutida-parcela"></a>

### Tabela embutida: `Venda.PedidoContratoParcela`

**Pedido: Parcelas do Contrato**

| Parâmetro | Valor / uso | Descrição |
|-----------|-------------|-----------|
| `_Venda.Pedido.Slaves` | `Venda.PedidoContratoParcela` | Tabela presente na submissão (obrigatório). |
| `_Venda.Pedido.SlavesSave` | `Venda.PedidoContratoParcela` | Salvar a tabela (obrigatório). |
| `_Venda.PedidoContratoParcela.isSlave` | `Venda_fkey_1365535661` | Nome da FK pai-filho (obrigatório). |
| `Venda.PedidoContratoParcela.<Campo>` | valor 1..N | Dados; repetir parâmetros para múltiplas linhas. |

**URL exemplo:**

```text
/JSON/Venda.Pedido/Insert?
Venda.Pedido.ColunaA=1&Venda.Pedido.ColunaB=2&
_Venda.Pedido.Slaves=Venda.PedidoContratoParcela&_Venda.Pedido.SlavesSave=Venda.PedidoContratoParcela&_Venda.PedidoContratoParcela.isSlave=Venda_fkey_1365535661&
Venda.PedidoContratoParcela.ColunaC=3&Venda.PedidoContratoParcela.ColunaD=4&
Venda.PedidoContratoParcela.ColunaC=5&Venda.PedidoContratoParcela.ColunaD=6
```

<a id="embutida-item"></a>

### Tabela embutida: `Venda.PedidoItem`

**Pedido: Itens**

| Parâmetro | Valor / uso | Descrição |
|-----------|-------------|-----------|
| `_Venda.Pedido.Slaves` | `Venda.PedidoItem` | Tabela presente (obrigatório). |
| `_Venda.Pedido.SlavesSave` | `Venda.PedidoItem` | Salvar (obrigatório). |
| `_Venda.PedidoItem.isSlave` | `PedidoItem_CompanyId_fkey` | FK (obrigatório). |
| `Venda.PedidoItem.<Campo>` | valor 1..N | Dados; repetir para várias linhas. |

**URL exemplo:**

```text
/JSON/Venda.Pedido/Insert?
Venda.Pedido.ColunaA=1&Venda.Pedido.ColunaB=2&
_Venda.Pedido.Slaves=Venda.PedidoItem&_Venda.Pedido.SlavesSave=Venda.PedidoItem&_Venda.PedidoItem.isSlave=PedidoItem_CompanyId_fkey&
Venda.PedidoItem.ColunaC=3&Venda.PedidoItem.ColunaD=4&
Venda.PedidoItem.ColunaC=5&Venda.PedidoItem.ColunaD=6
```

### Retorno (Insert)

Igual a **Select** (ou **Browse** em inclusão múltipla), refletindo o que foi gravado após triggers.

[↑ Voltar ao índice](#indice)

---

## 6. Delete

**Excluir registro**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Remove o registro (irreversível). |
| **Nome do método** | `Delete` |

### URLs de exemplo

| | |
|--|--|
| JSON | `/JSON/Venda.Pedido/Delete?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>` |
| XML | `/XML/Venda.Pedido/Delete?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>` |

### Exemplo JavaScript (ORM)

```javascript
new Ultra.Class('Venda.Pedido').Delete( {
 ColunaX:         '<Valor>'
 ColunaY:         '<Valor>'
 ColunaZ:         '<Valor>'
}, {
 onSucces:  function () { alert( this.Field.ColunaX.value ); },
 onError:   function (errstr) { alert(errstr); },
} );
```

### Exemplo Template::Toolkit (ORM)

```html
[%
 SET OBJ = Ultra.Class.Delete( 'Venda.Pedido', {
  'Venda.Pedido.ColunaX'         = '<Valor>'
  'Venda.Pedido.ColunaY'         = '<Valor>'
  'Venda.Pedido.ColunaZ'         = '<Valor>'
 } );
) %]
[% IF OBJ.ErrorStatus %]
 ERRO:[% OBJ.ErrorStatus %]
[% ELSE %]
 SUCESSO NA EXCLUSÃO!
[% END %]
```

### Parâmetros e retorno (Delete)

**Obrigatório:** todos os campos da **chave primária**.

```json
{
 "Method"       : "Delete",
 "ErrorStatus"  : null,
 "ErrorStatus2" : null,
 "canDelete"    : "1",
 "canUpdate"    : "1",
 "canInsert"    : "1",
 "ClassId"      : "Produto.Produto"
}
```

[↑ Voltar ao índice](#indice)

---

## 7. Download

**Baixar conteúdo de campo/arquivo**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Baixar conteúdo completo de campos com armazenamento externo (ex.: `Ultra.external_file`). Em Browse/Select, o campo traz `.url` apontando para este endpoint. |
| **Nome do método** | `Download` |

### URLs de exemplo

| Saída | URL |
|-------|-----|
| Binária ou HTML | `/Class/Venda.Pedido/Download?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&_Venda.Pedido.File=<NomeDoCampo>` |
| Binária ou texto plano | `/REST/Venda.Pedido/Download?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&_Venda.Pedido.File=<NomeDoCampo>` |

### Parâmetros

**Obrigatório:** PK completa + `_Venda.Pedido.File=<NomeDoCampo>`.

### Retorno

MIME conforme o arquivo (imagem, octet-stream, XML, etc.). Em campo “normal”, pode retornar HTML.

- **`/Class/...`:** tende a envolver em HTML / opções de exportação (uso humano na plataforma).
- **`/REST/...`:** arquivo **puro** (melhor para API máquina-máquina).

[↑ Voltar ao índice](#indice)

---

## 8. Download2

**Baixar conteúdo de campo/arquivo (plano)**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Igual ao Download; em campos HTML/TEXT, **Download2** evita o envelope HTML extra do Download. Com saída **REST** no Download, o comportamento aproxima-se do Download2. |
| **Nome do método** | `Download2` |

### URLs de exemplo

| Saída | URL |
|-------|-----|
| Binária ou texto | `/Class/Venda.Pedido/Download2?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&_Venda.Pedido.File=<NomeDoCampo>` |
| Binária ou texto | `/REST/Venda.Pedido/Download2?__debug__=0&CompanyId=<Valor>&ClienteId=<Valor>&Id=<Valor>&_Venda.Pedido.File=<NomeDoCampo>` |

[↑ Voltar ao índice](#indice)

---

## 9. Call

**Invocar função exposta**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Chamar funções de BD expostas na API para quem tem acesso à tabela. |
| **Nome do método** | `Call` |

### URL de exemplo

`/JSON/Venda.Pedido/Call?__debug__=0&_Venda.Pedido.Function=<NomeDaFunção>&_Venda.Pedido.Params=<Param1>&_Venda.Pedido.Params=<Param2>&...`

### Parâmetros

- `_Venda.Pedido.Function` — nome da função.
- `_Venda.Pedido.Params` — repetir na ordem dos argumentos da função.

### Retorno

```json
{
 "Method"       : "Call",
 "ErrorStatus"  : null,
 "ErrorStatus2" : null,
 "ClassId"      : "Produto.Produto",
 "data"         : { "row": [ ["..."], ["..."], ["..."] ] }
}
```

[↑ Voltar ao índice](#indice)

---

## 10. AjaxFieldInput

**Construir HTML de um campo (tela)**

### Resumo

| | |
|--|--|
| **Funcionalidade** | Uso em **tela**, via JavaScript: HTML do campo como em formulário Insert/Update. |
| **Nome do método** | `AjaxFieldInput` |

### Exemplo JavaScript

```javascript
new Ultra.Class( 'Schema.Classe' ).process(
 'AjaxFieldInput',
 {
  _XMethod: 'NomeDoCampo',
  _FormId:  'FormId',
  Campo1:   'Valor1',
  Campo2:   'Valor2',
  _Instantiate: 1,
 },
 {
  targetElement: elemento
 }
);
```

### Retorno

HTML do controle (ex.: `<input name='...' value='...'>`).

[↑ Voltar ao índice](#indice)

---

<a id="schema-banco"></a>

## Detalhes do schema (Plune / banco de dados)

Metadados exportados do Plune para a classe **`Venda.Pedido`**. Útil para montar **Select** / **Update** / **Delete** (chaves), entender **FKs** e **índices**.

### Identificação da classe

| Propriedade | Valor |
|-------------|-------|
| Assinatura da classe | [1] Plune |
| Schema original | [Venda] Vendas |
| Nome original da classe | Pedido |
| **ClassId** | `Venda.Pedido` |
| Pacote de origem | [Venda] Vendas |

### Permissões globais

Valores abaixo referem-se ao **usuário da sessão** no momento da exportação no Plune; **outros usuários** podem ter permissões diferentes. Permissões por registro podem ainda depender de relacionamentos com outras tabelas.

| Consultar | Incluir | Alterar | Excluir |
|:---------:|:-------:|:-------:|:-------:|
| SIM | SIM | SIM | SIM |

### Chaves primárias

| Campo | Rótulo |
|-------|--------|
| `CompanyId` | Empresa |
| `ClienteId` | Cliente |
| `Id` | Número |

Para chamadas HTTP/API, em geral é necessário informar **os três** campos na chave composta.

### Chaves únicas

| Nome | Colunas |
|------|---------|
| **Pedido_FilialSemCliente_UK** | `CompanyId`, `BranchId`, `Id` |
| **Pedido_Filial_UK** | `CompanyId`, `BranchId`, `ClienteId`, `Id` |
| **Pedido_CompanyId_key1** | `CompanyId`, `Id` |

### Índices (performance)

| Índice | Tipo | Colunas / campos |
|--------|------|------------------|
| `Pedido_pkey` | UNIQUE KEY | `CompanyId`, `ClienteId`, `Id` |
| `Pedido_Filial_UK` | INDEX | `CompanyId`, `BranchId`, `ClienteId`, `Id` |
| `Pedido_FilialSemCliente_UK` | INDEX | `CompanyId`, `BranchId`, `Id` |
| `Pedido_9382294430_idx` | INDEX | `CompanyId`, `ClienteId`, `Data` (*Criação*) |
| `Pedido_CompanyId_key1` | INDEX | `CompanyId`, `Id` |
| `ix_PedidoMRP` | INDEX | `CompanyId`, `BranchId`, `ClienteId`, `Id`, `Aprovado`, `Data` (*Criação*), `Encerrado` |
| `Pedido_DataCriacao_idx` | INDEX | `Data` (*Criação*) |

Filtros em colunas **sem** índice adequado podem degradar performance em volumes grandes.

### Campos de descrição de registro

| Campo | Caminho / rótulo |
|-------|------------------|
| `Id` | Número |
| `Descricao` | /1/Geral/Descrição |

### Comportamento da classe (Plune)

| Propriedade | Valor |
|-------------|-------|
| Tipo da classe | [r] Mapeamento objeto-relacional a uma tabela do DBMS |
| Tipo de acesso | `public` |
| Controla armazenamento | Não |
| Tipo de permissionamento | Estático |
| Rastreabilidade | Nenhuma |
| Handler padrão | `Ultra::Handler::ERP` |

**Heranças diretas do handler (@ISA):**

- `Ultra::Plugin::CRUD::Auth::Company`
- `Ultra::Handler::CRUD`
- `Ultra::Handler`
- `Ultra::Class::SQL` (duas entradas na exportação original)

### Arquivos externos

| Propriedade | Valor |
|-------------|-------|
| Diretório | `~/raw` (`/home/gebras/raw`) |
| Extensão padrão | `bin` |

### SQL padrão para `ORDER BY`

```sql
%SELF%."CompanyId", %SELF%."ClienteId", %SELF%."Data" desc,
%SELF%."OrdemCompra" desc, %SELF%."Id" desc
```

### Referências naturais (FK — esta classe → outras)

| Tabela / classe (referência) | Nome da relação (FK) |
|------------------------------|----------------------|
| Sub Centro de Custo Nível 3 | `Venda_fkey_1342463335` |
| Tipo de Lançamento | `_fkey_1364993941` |
| Condições de Pagamento | `1261499090` |
| Tipo de Operação | `Pedido_TipoOpId_TipoOp_fkey4783` |
| Contas e Caixas de Movimento | — |
| Tabela de Preços | `Pedido_CompanyId_fkey3` |
| Centro de Custo | `Venda_Pedido_fkey_1246622269` |
| Fatura a Receber | `Venda_Pedido_fkey_1275336974` |
| Pedido: Status | `Venda_Pedido_fkey_1259585303` |
| Config. Nota Fiscal | `**ForceFK**Abstract**1275311935**` |
| Tipos de Bloqueio de Crédito | `**ForceFK**Abstract**1297855024**` |
| Filiais | `Pedido_BranchId_Branch_fkey14271` |
| Tipo de Operação: Código Fiscal | `Venda_Pedido_fkey_1247248100` |
| Moeda | `_fkey_1366728048` |
| Moeda (frete) | `Venda_fkey_MoedaFrete` |
| Operações de Caixa | `Venda_Pedido_fkey_1275423063` |
| Tipos de Entrega | `Venda_Pedido_fkey_1268756882` |
| Tipo de Operação: Natureza da Operação sobre Serviço | `Venda_Pedido_fkey_1307554999` |
| Sub Centro de Custo Nível 2 | `Venda_fkey_1342463292` |
| Situação Pedido | `Pedido_Status_StatusPedido_fkey93699` |
| Tipo de Transporte | `Venda_fkey_1559047918` |
| Reserva de Estoque | `Pedido_CompanyId_fkey4` |
| Usuários | `Pedido_CompanyId_fkey2` |
| — | `x1_Venda_fkey_1369144109` |
| — | `Venda_Pedido_fkey_1252496048` |
| Estado/Província | `Venda_fkey_1531255085` |
| — | `Venda_Pedido_fkey_1246277049` |
| Tipo de Contrato | `Venda_Pedido_fkey_1247501308` |
| Vale Crédito | `**ForceFK**Abstract**1572030967**` |
| Sub Centro de Custo | `Venda_Pedido_fkey_1246622345` |
| País | `Venda_Pedido_fkey_1265910037` |
| — | `Venda_Pedido_fkey_1531252270` |
| Oportunidades | `Venda_Pedido_fkey_1283533163` |
| Representante | `**ForceFK**Abstract**1665**` |
| Região | `**ForceFK**Abstract**1274382923**` |
| Formas de Gerar/Enviar Boleto | `Venda_Pedido_fkey_1298016017` |
| Parceiros | `Pedido_TransportadoraId_tbParceiro_fkey16117` |
| — | `Venda_Pedido_fkey_1301379834` |
| Caixas | `Venda_Pedido_fkey_1275423010` |
| Objeto Relacionado | `Venda_fkey_1325077082` |
| Parceiros: Contatos | `Venda_fkey_1326913025` |
| Motivo de Fechamento de Oportunidade | `Venda_Pedido_fkey_1283533462` |
| Pedido (auto) | `Venda_fkey_1379343028` |
| Operação Financeira | `Venda_Pedido_fkey_1275073932` |
| — | `**ForceFK**Abstract**1260894983**` |
| Texto Padrão | `_fkey_1363870099` |
| Cidade | `Venda_Pedido_fkey_1531255570` |
| — | `Venda_Pedido_fkey_1246276967` |

### Referências inversas (outras tabelas → `Venda.Pedido`)

| Tabela / classe | Nome da relação (FK) |
|-----------------|----------------------|
| Pedido: Calcular Contrato | `Venda_fkey_1366031192` |
| Pedido: Magento Pagamento | `Venda_fkey_1422379865` |
| Movimentação Contábil | `Contabilidade_fkey_1394192200` |
| Lançamento de Comissões | `Financeiro_tbLancamentoComissao_fkey_1296027690` |
| Fatura a Receber | `**ForceFK**Abstract**1735298755**` |
| Fatura a Receber | `Financeiro_tbFaturaReceber_fkey_1278100640` |
| Previsão de Consumo | `**ForceFK**Abstract**1325067536**` |
| Solicitação | `Compra_fkey_1346096692` |
| Pedido: Reservar Estoque | `Venda_PedidoReserva_fkey_1293432011` |
| Conferência Cega | `Produto_fkey_1439385482` |
| Desaprovar Pedido | `Venda_DesaprovarPedido_fkey_1246298983` |
| Desencerrar Pedido | `Venda_DesencerrarPedido_fkey_1270466661` |
| Contas a Receber: Informações de Contratos | `Financeiro_fkey_1463700494` |
| Pedido: Parcelas do Contrato | `Venda_fkey_1365535661` |
| Prévia de Rateio Despesa/Receita | `Financeiro_fkey_1330461472` |
| Orçamento | `**ForceFK**Abstract**1759**` |
| Ordem de Produção | `PCP_OrdemProducaoItem_fkey_1243424403` |
| Ordem de Produção: Produção | `**ForceFK**Abstract**1267554739**` |
| Pedido: Aprovar Preço dos Itens | `Venda_AprovarPrecoItemPedido_fkey_1300346474` |
| Pedido: Reavaliar Crédito | `Venda_ReavaliarCreditoPedido_fkey_1305546700` |
| Veículo | `Venda_fkey_1358251752` |
| Pedido: Incluir NF: Itens | `Venda_IncluirNFSaidaItem_fkey_1279027480` |
| Pedido: Excluir Contas a Receber | `Venda_ExcluirContaReceberPedido_fkey_1275483420` |
| Pedidos da Loja | `Company_fkey_1698529791` |
| Nota Fiscal | `**ForceFK**Abstract**1278697343**` |
| Lançar Comissão | `Financeiro_LancarComissaoPedido_fkey_1296458792` |
| Despesas do Pedido | `PedidoDespesa_PedidoId_Pedido_fkey88976` |
| Reavaliar Estoque | `Venda_ReavaliarEstoque_fkey_1300710831` |
| Sincronizar E-Commerce | `Venda_fkey_1418835200` |
| Pedido: Criar Nota desvinculada: Itens | `Venda_fkey_1548786174` |
| Pedido: Aprovar Crédito | `Venda_AprovarCreditoPedido_fkey_1266599571` |
| Pedido: Emitir OP | `PedidoProduz_CompanyId_fkey1` |
| Recalcular Impostos | `Venda_fkey_1445944452` |
| Representantes Comissionados | `Financeiro_ComissaoRepresentante_fkey_1246992522` |
| Pedido: Gerar Ordens de Produção: Itens | `Venda_fkey_1580387116` |
| Pedidos da Loja: Importar agora | `Company_fkey_1698529642` |
| Pedido: Gerar Mensalidade | `Venda_GerarMensalidade_fkey_1272647393` |
| Pedido: Relatório Lucratividade | `**ForceFK**Abstract**1249408055**` |
| Pedido: Aditivos Contratuais | `Venda_fkey_1319216386` |
| Transporte Volume Pedido | `Venda_fkey_1359633115` |
| Contas a Receber | `**ForceFK**Abstract**1735299170**` |
| Contas a Receber | `Financeiro_fkey_1578939627` |
| Contas a Receber | `Financeiro_tbContaReceber_fkey_1278101022` |
| Cancelar Saldo do Pedido | `Venda_fkey_1324316397` |
| Pedido: Gerar Contas a Receber | `Venda_GerarContaReceber_fkey_1275339172` |
| MRP | `PCP_fkey_1704288877` |
| Pedido: Anexos | `Venda_fkey_1391770800` |
| Pedido: Itens | `PedidoItem_CompanyId_fkey` |
| Pedido: Itens: Composição | `Venda_PedidoItemComposicao_fkey_1280324800` |
| Grupo de Produtos do Pedido | `ProdutoGrupo_PedidoId_Pedido_fkey44823` |
| Pedido: Recalcular Pedido | `Venda_fkey_1445362330` |
| Nota Fiscal: Itens | `Venda_NotaItem_fkey_1278695996` |
| Calcula Markup | `Venda_fkey_1373984175` |
| Pedido | `Venda_fkey_1379343028` |
| Processo de Importação | `Compra_fkey_1346163671` |
| Agenda de Atividades | `CRM2_tbProspectsAcoes_fkey_1283519771` |

[↑ Voltar ao índice](#indice)

---

<a id="colunas-pedido"></a>

## Colunas (`Venda.Pedido`)

Listagem de **FieldId**, descrição de tela, **Ver / Inc / Alt** e **tipo / XSchema** exportada do Plune, agrupada por área (cadastro, transporte, cliente, faturamento, contrato, cobrança, impostos, comissão, integração, detalhes, valores).

**Documento completo:** [Pedido-colunas.md](Pedido-colunas.md).

**Chaves:** a PK documentada no [schema](#schema-banco) é `CompanyId`, `ClienteId`, `Id`. No export de colunas, `BranchId` também é **NOT NULL**; use [Pedido-colunas.md](Pedido-colunas.md) para todos os campos com **NN = \***.

[↑ Voltar ao índice](#indice)

---

## Referência rápida de caminhos

| Operação | Padrão JSON (exemplo) |
|----------|------------------------|
| Browse | `/JSON/Venda.Pedido/Browse?...` |
| Select | `/JSON/Venda.Pedido/Select?...` |
| Update | `/JSON/Venda.Pedido/Update?...` |
| MultiUpdate | `/JSON/Venda.Pedido/MultiUpdate?...` |
| Insert | `/JSON/Venda.Pedido/Insert?...` |
| Delete | `/JSON/Venda.Pedido/Delete?...` |
| Call | `/JSON/Venda.Pedido/Call?...` |
| Download | `/REST/Venda.Pedido/Download?...` ou `/Class/...` |
| Download2 | `/REST/Venda.Pedido/Download2?...` ou `/Class/...` |

---

*Documento reformulado a partir da documentação Plune da classe `Venda.Pedido`, incluindo metadados de schema/banco e referência à listagem de colunas em [Pedido-colunas.md](Pedido-colunas.md); estrutura e índice para navegação no repositório.*
