## Tipo de anexo (`x1_TipoAnexo`)

É um campo da tabela **[Venda.AnexoPedido] Pedido: Anexos** no schema **[Venda] Vendas**.

Este campo faz referência ao cadastro **[Venda.x1_PedidoTipoAnexo] Pedido: Tipo de Anexo**.

## Detalhes da schema no banco de dados

| Propriedade | Valor |
| --- | --- |
| Assinatura da Classe | `[1] Plune` |
| Schema de Origem | `[Venda] Vendas` |
| Classe/Tabela de Origem | `[Venda.AnexoPedido] Pedido: Anexos` |
| Nome do Campo no RDBMS | `x1_TipoAnexo` |
| Tipo do Campo no RDBMS | `int4` |
| Handler de Input | `Html::input::ForeignKey (padrão)` |
| Descrição do Handler | Handler padrão para campos com chave estrangeira. |
| Tamanho | `21` |
| Casas Decimais | `0` |
| Dimensões/ARRAY | Não ARRAY |
| Classe de Resolução (ResolveFK) | `[Venda.x1_PedidoTipoAnexo] Pedido: Tipo de Anexo` |
| Chave Estrangeira de Resolução | `**ForceFK**Abstract**1732644942**` |
| Classes Referenciadas (FK Naturais) | `[Venda.x1_PedidoTipoAnexo] Pedido: Tipo de Anexo` |
| É Primary Key | Não |
| Aparece na listagem por padrão | `[0] Não por padrão.` |
| É Descrição do Registro | Não |
| Permite Valores Nulos | Sim |
| Sequência SERIAL | Nenhuma |
| Valor Default | Nenhum reconhecido |
| Valor Default no DBMS | Nenhum definido |

### Heranças diretas do handler (`@ISA`)

- `Html::input::Plugin::BrowseUpdatable`
- `Html::input::Plugin`
- `Html::input`
- `Html::Strict`

## Funções disponíveis (listagens e importações)

### Funções de exibição

São funções utilizadas em listagens ou importações de dados, permitindo apresentar os dados do campo de formas alternativas.

| Descrição da função | Handler interno |
| --- | --- |
| Descrição do Registro | `Html::input::Function::ForeignKey::FieldValue` |
| Código do Registro | `Html::input::Function::ForeignKey::FieldID` |
| Código e Descrição do Registro | `Html::input::Function::ForeignKey::FieldIDAndValue` |
| Descrição do Registro (ordenado pelo ID) | `Html::input::Function::ForeignKey::FieldOrderByID` |
| Descrição do Registro como VARCHAR | `Html::input::Function::varchar::FKResolved` |
| Verdadeiro se igual a... | `Html::input::Function::boolean::true_if_like` |
| Concatena com o campo... | `Html::input::Function::varchar::ConcatTT` |
| Exibe TAG colorida na listagem | `Html::input::Function::ForeignKey::Colored` |
| Muda cor de fundo da coluna... | `Html::input::Function::Colored` |

### Funções de agregação

São funções utilizadas unicamente em listagens quando o campo deve ser agregado devido à existência de um agrupamento na consulta (GROUP BY).

| Descrição da função | Handler interno |
| --- | --- |
| Contar registros | `Html::input::Function::Aggregate::integer::count` |
| Contar registros diferentes | `Html::input::Function::Aggregate::integer::count_distinct` |
| Concatena Elementos (alpha - em testes) | `Html::input::Function::Aggregate::ForeignKey::ARRAY::JoinFK` |
| Agregação Nula | `Html::input::Function::Aggregate::varchar::Null` |

## Opções gerais de busca

Para efetuar buscas neste campo, as seguintes expressões são válidas.

| Exemplo | Descrição |
| --- | --- |
| (vazio) | Busca qualquer valor (sem restrição) |
| `!` | Indica negação quando uma expressão inicia por este caracter. Ex.: `!teste` busca valores que **não** contenham `"teste"`. |
| `\nulo` | Apenas valores nulos |
| `[123]` | Busca no **código** do registro, e não no nome (o inverso de `"teste"`). |
| `[123]-[456]` | Faixa de busca no código do registro |
| `[123]-[456],[789],[1234]-[5678]` | Faixas/valores no código (ex.: código entre 123–456 **ou** igual a 789 **ou** entre 1234–5678) |
| `"teste"` | Busca na **descrição** do registro, e não no código (o inverso de `[123]`) |
| `A` | Apenas registros iniciando com `"A"` |
| `>CARLOS` | Apenas registros iniciando com `"BARRA"` |
| `teste` | Apenas registros que contenham a palavra `"teste"` |
| `!teste` | Apenas registros que **não** contenham a palavra `"teste"` |
| `teste ou confirmado` | Contém `"teste"` **ou** `"confirmado"` |
| `teste confirmado` | Contém `"teste"` **ou** `"confirmado"` |
| `teste, confirmado` | Contém `"teste"` **ou** `"confirmado"` (idem ao anterior) |
| `teste e confirmado` | Contém `"teste"` **e** `"confirmado"` |

> Obs.: os filtros são aplicados **antes** das funções de exibição ou agregação.

## Tabela/Classe `Venda.AnexoPedido` (detalhes do Plune)

### Detalhes da schema no banco de dados

| Propriedade | Valor |
| --- | --- |
| Assinatura da Classe | `[1] Plune` |
| Schema Original da Classe | `[Venda] Vendas` |
| Nome Original da Classe | `AnexoPedido` |
| ClassId único | `Venda.AnexoPedido` |
| Pacote de Origem | `[Venda] Vendas` |

### Permissões globais (usuário logado)

| Ação | Permitido |
| --- | --- |
| Consultar | SIM |
| Incluir | SIM |
| Alterar | SIM |
| Excluir | NÃO |

> IMPORTANTE: Permissões Globais referentes **exclusivamente** ao usuário atualmente logado (`biview53@gmail.com`) — demais usuários podem ter permissões diferentes. Permissões de Alteração, Visualização e Exclusão podem sofrer alterações devido ao registro instanciado ou quando subordinados a outra tabela.

### Chaves primárias

| Campo | Descrição |
| --- | --- |
| `[CompanyId]` | Empresa |
| `[BranchId]` | Filial |
| `[PedidoId]` | Pedido |
| `[Id]` | Código |

### Índices (performance)

#### `AnexoPedido_pkey` (UNIQUE KEY)

| Campo | Descrição |
| --- | --- |
| `[CompanyId]` | Empresa |
| `[BranchId]` | Filial |
| `[PedidoId]` | Pedido |
| `[Id]` | Código |

> Importante: os índices de uma tabela servem para aumentar a performance da consulta quando filtros são aplicados. Consultas com filtros em colunas que não possuem índices definidos podem se tornar lentas.

### Campos de descrição de registro

| Campo | Descrição |
| --- | --- |
| `[CompanyId]` | Empresa |
| `[BranchId]` | Filial |
| `[PedidoId]` | Pedido |
| `[Id]` | Código |

### Metadados da classe

| Propriedade | Valor |
| --- | --- |
| Tipo da Classe | `[r]` Mapeamento Objeto-Relacional a uma tabela do DBMS |
| Tipo de Acesso | `hidden` |
| Controla Armazenamento | Não |
| Tipo de Permissionamento | Estático |
| Rastreabilidade | Nenhuma |
| Handler Padrão | `Ultra::Handler::ERP` |
| Diretório para Arquivos Externos | `~/raw (/home/gebras/raw)` |
| Extensão Padrão para Arquivos Externos | `bin` |
| SQL padrão para ORDER BY | (vazio) |

#### Heranças diretas do handler (`@ISA`)

- `Ultra::Plugin::CRUD::Auth::Company`
- `Ultra::Handler::CRUD`
- `Ultra::Handler`
- `Ultra::Class::SQL`
- `Ultra::Class::SQL`

### Referências naturais (chaves estrangeiras)

| Tabela/Classe | Nome das Relações |
| --- | --- |
| Filiais | `Venda_fkey_1391770708` |
| Pedido: Tipo de Anexo | `**ForceFK**Abstract**1732644942**` |
| Pedido | `Venda_fkey_1391770800` |

### Referências inversas (tabelas que referenciam essa)

_(não informado no dump colado)_

### Colunas (campos)

| FieldId | Descrição | Permissões | Tipo | XSchema |
| --- | --- | --- | --- | --- |
| `CompanyId *` | Empresa | Ver / Inc | - | `Company::CompanyId(21) [Company.Company] Minha Empresa` |
| `BranchId *` | Filial | Ver / Inc | - | `int4(21) [Company.Branch] Filiais` |
| `PedidoId *` | Pedido | Ver / Inc | - | `int4(21) [Venda.Pedido] Pedido` |
| `Id *` | Código | Ver / Inc | - | `int4(21) (SERIAL)` |
| `x1_TipoAnexo` | Tipo de anexo | Ver / Inc / Alt | - | `int4(21) [Venda.x1_PedidoTipoAnexo] Pedido: Tipo de Anexo` |
| `x1_ObservacaoAnexo` | Observação do Anexo | Ver / Inc / Alt | - | `text()` |
| `Anexo *` | Anexo | Ver / Inc / Alt | - | `Ultra::external_file(512)` |
| `ExternalFileId` | Código Para Acesso Direto | Ver / Inc / Alt | - | `int4(21)` |
| `ExternalPass` | Senha para acesso Externo | Ver / Inc / Alt | - | `varchar(64)` |
| `ExternalUrl` | URL Externa | Ver | - | `Ultra::URL(1024)` |

## Métodos (API Plune)

As APIs HTTP, JavaScript e HTML/Template::Toolkit oferecem em geral os mesmos métodos de acesso e parâmetros, alterando apenas a sintaxe de chamada conforme o tipo.

Para fins de DEBUG e testes apenas, todas reconhecem o parâmetro `__debug__=1`, o qual retorna o conteúdo estruturado (XML, JSON, etc) de forma identada (pretty print) e adiciona eventuais informações adicionais no parâmetro de retorno `"Warnings"`.

**Não use `__debug__=1` em produção**, pois a performance é degradada.

### Índice de métodos disponíveis

- `Browse`: Listar Registros (múltiplos)
- `Select`: Consultar Registro (único)
- `Update`: Alterar Registro
- `MultiUpdate`: Alterar Múltiplos Registros
- `Insert`: Incluir um ou mais Registro(s)
- `Delete`: Excluir Registro
- `Download`: Baixar conteúdo de Campo/Arquivo
- `Download2`: Baixar conteúdo de Campo/Arquivo (plano)
- `Call`: Invocar Função Exposta
- `AjaxFieldInput`: Construir HTML de um campo (para uso em tela)

### `Browse` — Listar registros (múltiplos)

- **Funcionalidade**: listar registros da tabela, opcionalmente com filtros, colunas, funções, ordenamento, paginação, etc.
- **Nome do Método**: `Browse`
- **Protocolo de Entrada**:
  - `POST/GET` HTTP (REST) (via QueryString simples ou multi-part)
  - Objeto JavaScript (ORM em tela)
  - Objeto HTML/Template::Toolkit (ORM em servidor)

#### Saídas / exemplos de URL

| Saída | Exemplo de URL | Limitações |
| --- | --- | --- |
| JSON | `/JSON/Venda.AnexoPedido/Browse?__debug__=0&...` | Indicado para retornos de 1 registro. |
| JSONL | `/JSONL/Venda.AnexoPedido/Browse?__debug__=0&...` | Indicado para retornos de qualquer tamanho. |
| XML | `/XML/Venda.AnexoPedido/Browse?__debug__=0&...` | Indicado para retornos de 1 registro. |
| TSV | `/TSV/Venda.AnexoPedido/Browse?__debug__=0&...` | Indicado para grandes retornos. |
| TSVX | `/TSVX/Venda.AnexoPedido/Browse?__debug__=0&...` | TSV + 2 colunas (valor resolvido/estendido). |
| BSV | `/BSV/Venda.AnexoPedido/Browse?__debug__=0&...` | Separador ASCII 17, sem resolução/estendido. |
| BSVX | `/BSVX/Venda.AnexoPedido/Browse?__debug__=0&...` | ASCII 17/18 para colunas/sub-colunas. |

#### Exemplo com objetos — JavaScript ORM

```javascript
new Ultra.Class('Venda.AnexoPedido').Browse(
  {
    // Parâmetros da consulta (filtros em colunas ou opções)
    ColunaX: '<filtro>',
    ColunaY: '<filtro>',
    _BrowseSequence: ['ColunaX', 'ColunaY'],
    _BrowseLimit: 15,
    _Order: ['ColunaX', 'ColunaY'],
  },
  {
    // Eventos pós submissão
    onSucces: function () {
      alert(this.data.row.ColunaX.value);
    },
    onError: function (errstr) {
      alert(errstr);
    }, // Erro na consulta (parâmetro inválido, etc)
  }
);
```

#### Exemplo com objetos — HTML/Template::Toolkit ORM

```tt
[%
 SET OBJ = Ultra.Class.Browse( 'Venda.AnexoPedido', {
  'Venda.AnexoPedido.ColunaX'         = '<filtro>'
  'Venda.AnexoPedido.ColunaY'         = '<filtro>'
  '_Venda.AnexoPedido.BrowseSequence' = [ 'ColunaX', 'ColunsY' ]
  '_Venda.AnexoPedido.BrowseLimit'    = 15
  '_Venda.AnexoPedido.Order'          = [ 'ColunaX', 'ColunsY' ]
 } );
 ) %]
<ol>
[% FOREACH ROW IN OBJ.data.row %]
<li>[% ROW.item('ColunaX').value; %]   <!-- Valor nativo do campo -->
<li>[% ROW.item('ColunaX').resolved %] <!-- Resolução do campo, se for uma chave estrangeira -->
<li>[% ROW.item('ColunaX').url %]      <!-- URL para Download, em casos de campos com armazenamento externo - upload -->
<li>[% ROW.item('ColunaX').array;      <!-- Estrutura parseada da array -->
       ROW.item('ColunaX').array.0;    <!-- caso o campo seja uma arry/lista de valores -->
       ROW.item('ColunaX').array.1; %]
[% END %]
</ol>
```

#### Parâmetros suportados (Browse)

| Parâmetro | Ocorrência | Descrição |
| --- | --- | --- |
| `Venda.AnexoPedido.<Nome_do_Campo>=<Expressão_de_Busca>` | `0..N` | Define um filtro de busca para o campo `<Nome_do_Campo>`. |
| `_Venda.AnexoPedido.Order=<Nome_do_Campo1,Nome_do_CampoN,...>` | `0..N` | Define por quais campos a consulta será ordenada. |
| `_Venda.AnexoPedido.OrderDesc=<1\|0,0\|1,...>` | `0..N` | Define se o ordenamento será crescente (`0`) ou decrescente (`1`). |
| `_Venda.AnexoPedido.OrderId=<1\|0>` | `0..N` | Ordenar por código do registro (quando houver FK) em vez da resolução. |
| `_Venda.AnexoPedido.BrowseSequence=<Nome_do_Campo>` | `0..N` | Define quais campos serão consultados (repetindo o parâmetro). |
| `_Venda.AnexoPedido.BrowseSequence=<Campo1>,<Campo2>,...` | `0..1` | Define múltiplos campos de forma alternativa (uma única vez). |
| `_Venda.AnexoPedido.ExportAll=1` | `0..1` | Consulta para exportação (sobrescreve BrowseSequence com todos os campos). |
| `_Venda.AnexoPedido.BrowseLimit=<INTEGER>` | `N` | Nº máximo por página (default `30`; max `1000`). |
| `_Venda.AnexoPedido.Page=<INTEGER>` | `N` | Página a consultar (paginação). |
| `_Venda.AnexoPedido.GroupBy=<Nome_do_Campo>` | `0..1` | Agrupar (`GROUP BY`) por `<Nome_do_Campo>`. |
| `_Venda.AnexoPedido.OK=1` | `0..1` | Relevante na interface HTML: considerar parâmetros enviados. |
| `_Venda.AnexoPedido.<Nome_do_Campo>.Fn=<Nome_da_Função>` | `0..N` | Aplicar função no campo (pode cascatear). |
| `_Venda.AnexoPedido.<Nome_do_Campo>.Fg=<Nome_da_Função>` | `0..N` | Aplicar função para agregação (`GROUP BY`). |

#### Retorno/Saída de dados (exemplo)

```json
{
  "allRows": "198",
  "Method": "Browse",
  "data": {
    "row": [
      {
        "NomeDoCampo": {
          "value": "0",
          "array": ["A", "B"],
          "resolved": "* Produto/Material"
        },
        "StatusId": { "value": "1", "resolved": "Ativo" },
        "_g.canDelete": "1",
        "_g.canUpdate": "1"
      }
    ]
  },
  "rows": 30,
  "ErrorStatus": null,
  "ErrorStatus2": null,
  "canDelete": "1",
  "canUpdate": "1",
  "canInsert": "1",
  "ClassId": "Produto.Produto"
}
```

### `Select` — Consultar registro único

- **Exemplo JSON**: `/JSON/Venda.AnexoPedido/Select?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>`
- **Exemplo XML**: `/XML/Venda.AnexoPedido/Select?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>`

#### Exemplo com objetos — JavaScript ORM

```javascript
new Ultra.Class('Venda.AnexoPedido').Select(
  {
    // Parâmetros da consulta (devem ser especificadas todas as chaves primárias)
    ColunaX: '<Valor>',
    ColunaY: '<Valor>',
  },
  {
    onSucces: function () {
      alert(this.Field.ColunaX.value);
    },
    onError: function (errstr) {
      alert(errstr);
    },
  }
);
```

#### Exemplo com objetos — HTML/Template::Toolkit ORM

```tt
[%
 SET OBJ = Ultra.Class.Browse( 'Venda.AnexoPedido', {
  'Venda.AnexoPedido.ColunaX'         = '<Valor>'
  'Venda.AnexoPedido.ColunaY'         = '<Valor>'
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

#### Parâmetros suportados (Select)

| Parâmetro | Ocorrência | Descrição |
| --- | --- | --- |
| `_Venda.AnexoPedido.IgnoreFields` | `0..1` | Lista de campos ignorados na resposta (ex.: `Campo1,Campo2`). |
| `_Venda.AnexoPedido.FieldSequence` | `0..1` | Lista de campos incluídos na resposta (ex.: `Campo1,Campo2`). |
| `_Venda.AnexoPedido.FormSequence` | `0..1` | Campos exibidos no formulário HTML. |
| `_Venda.AnexoPedido.XMethod` | `0..1` | Invocar método de tabela filha após o método principal. |
| `_Venda.AnexoPedido.XForeignKeyId` | `0..1` | Nome da FK da tabela filha para o `XMethod`. |

#### Retorno/Saída de dados (exemplo)

```json
{
  "Method": "Select",
  "Field": {
    "NomeDoCampo": {
      "value": "0",
      "resolved": "* Produto/Material",
      "array": [],
      "url": "http://..."
    }
  },
  "ErrorStatus": null,
  "ErrorStatus2": null,
  "canDelete": "1",
  "canUpdate": "1",
  "canInsert": "1",
  "ClassId": "Produto.Produto"
}
```

### `Update` — Alterar registro

- **Exemplo JSON**: `/JSON/Venda.AnexoPedido/Update?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>&<NomeDaColuna>=<Valor>&...`
- **Exemplo XML**: `/XML/Venda.AnexoPedido/Update?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>&<NomeDaColuna>=<Valor>&...`

#### Exemplo com objetos — JavaScript ORM

```javascript
new Ultra.Class('Venda.AnexoPedido').Update(
  {
    ColunaX: '<Valor>',
    ColunaY: '<Valor>',
    ColunaZ: '<Valor>',
  },
  {
    onSucces: function () {
      alert(this.Field.ColunaX.value);
    },
    onError: function (errstr) {
      alert(errstr);
    },
  }
);
```

#### Exemplo com objetos — HTML/Template::Toolkit ORM

```tt
[%
 SET OBJ = Ultra.Class.Update( 'Venda.AnexoPedido', {
  'Venda.AnexoPedido.ColunaX'         = '<Valor>'
  'Venda.AnexoPedido.ColunaY'         = '<Valor>'
  'Venda.AnexoPedido.ColunaZ'         = '<Valor>'
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

> Nota sobre Upload de Arquivos: o upload deve ser tratado via submissão `multipart/form-data` (RFC 2388).

### `MultiUpdate` — Alterar múltiplos registros

```javascript
new Ultra.Class('Venda.AnexoPedido').MultiUpdate(
  {
    // Deve ser especificado um _MSelect para cada registro a ser alterado
    _MSelect: 'Id=<Valor>',
    _MSelect: 'Id=<Valor>',
    // E um _doUpdate para cada coluna
    _doUpdate: 'ColunaX=<Valor>',
    _doUpdate: 'ColunaY=<Valor>',
    _doUpdate: 'ColunaZ=<Valor>',
  },
  {
    onSucces: function () {
      alert(this.rows);
    },
    onError: function (errstr) {
      alert(errstr);
    },
  }
);
```

### `Insert` — Incluir registro

```javascript
new Ultra.Class('Venda.AnexoPedido').Insert(
  {
    ColunaX: '<Valor>',
    ColunaY: '<Valor>',
    ColunaZ: '<Valor>',
  },
  {
    onSucces: function () {
      alert(this.Field.ColunaX.value);
    },
    onError: function (errstr) {
      alert(errstr);
    },
  }
);
```

#### MultiInsert (via `XMethod=MultiInsert`)

> Ao adicionar esse parâmetro você poderá enviar múltiplos registros a serem incluídos **dentro da mesma transação**.

### `Delete` — Excluir registro

```javascript
new Ultra.Class('Venda.AnexoPedido').Delete(
  {
    ColunaX: '<Valor>',
    ColunaY: '<Valor>',
    ColunaZ: '<Valor>',
  },
  {
    onSucces: function () {
      alert(this.Field.ColunaX.value);
    },
    onError: function (errstr) {
      alert(errstr);
    },
  }
);
```

### `Download` — Baixar conteúdo de campo/arquivo

- **Exemplo (Class)**: `/Class/Venda.AnexoPedido/Download?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>&_Venda.AnexoPedido.File=<NomeDoCampo>`
- **Exemplo (REST)**: `/REST/Venda.AnexoPedido/Download?__debug__=0&CompanyId=<Valor>&BranchId=<Valor>&PedidoId=<Valor>&Id=<Valor>&_Venda.AnexoPedido.File=<NomeDoCampo>`

### `Download2` — Baixar conteúdo (plano)

Funciona como o `Download`, mas tenta retornar o conteúdo o mais puro possível (ex.: `text/html` ou `text/plain` direto).

### `Call` — Invocar função exposta

- **Exemplo**: `/JSON/Venda.AnexoPedido/Call?__debug__=0&_Venda.AnexoPedido.Function=<NomeDaFunção>&_Venda.AnexoPedido.Params=<Param1>&...`

### `AjaxFieldInput` — Construir HTML de um campo (em tela)

```javascript
new Ultra.Class('Schema.Classe').process(
  'AjaxFieldInput',
  {
    _XMethod: 'NomeDoCampo',
    _FormId: 'FormId',
    Campo1: 'Valor1',
    Campo2: 'Valor2',
    _Instantiate: 1,
  },
  {
    targetElement: elemento,
  }
);
```