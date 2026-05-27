# Plune — Criação de pedido novo (do zero)

Guia prático para **incluir** um registro em `Venda.Pedido` via API (`Insert`), incluindo **itens** na mesma transação quando necessário. Complementa [Pedido.md](Pedido.md) (método **Insert**, tabelas embutidas) e o catálogo de campos [Pedido-colunas.md](Pedido-colunas.md).

---

## Quando usar

| Cenário | Método |
|--------|--------|
| Pedido **ainda não existe** no Plune | **`Venda.Pedido/Insert`** |
| Pedido **já existe** e só altera cabeçalho / regras de negócio permitem | **`Venda.Pedido/Update`** — ver [Pedido.md § Update](Pedido.md#3-update) |

Este documento cobre o primeiro caso (**criação do zero**).

---

## Endpoint e formato

| Item | Valor |
|------|--------|
| Método HTTP | Em geral **GET** ou **POST** com query string (padrão do projeto: GET) |
| URL | `https://<host>/JSON/Venda.Pedido/Insert?...` |
| Autenticação | Token de sessão (ex.: `_AuthToken=...`) conforme ambiente |
| Valores | **Formato de tela (pt-BR)** para o pedido: datas `dd/mm/aaaa`, decimais com vírgula onde o Plune esperar formato de tela — ver [Pedido.md § Insert](Pedido.md#5-insert) |

**Permissões:** as operações respeitam o **usuário da sessão**; é preciso permissão de **Inclusão** em `Venda.Pedido` e, se houver itens embutidos ou insert posterior em `Venda.PedidoItem`, permissão (e regras por registro) em **Pedido: Itens**.

---

## Chaves e obrigatoriedade (cabeçalho)

Conforme [Pedido.md — schema](Pedido.md#schema-banco) e [Pedido-colunas.md](Pedido-colunas.md) (**NN = \***):

| Campo | Papel no Insert |
|-------|------------------|
| `CompanyId` | Empresa (fixo no ambiente Gebras, ex.: **869**) |
| `BranchId` | **Filial** — NOT NULL no cadastro; necessária também em muitos fluxos de **item** (cálculo de custo do produto) |
| `ClienteId` | Cliente (parceiro) do pedido |
| `Id` | Em **Insert**, em geral **omitido** ou preenchido por sequência/trigger do banco; após gravar, o retorno traz o `Id` gerado |

Outros campos marcados como NOT NULL no export (`CalcularImpostos`, `Encerrado`, `Bloqueado`, `Aprovado`, `Status`, `TipoOpId`, etc.) devem ser informados conforme a política do cadastro no Plune ou assumem default/trigger — validar no ambiente.

---

## Padrão Gebras no repositório (referência)

O projeto monta um **Insert** com parâmetros fixos de negócio Gebras e anexa parâmetros dinâmicos (`{0}`):

**Arquivo:** `ModulosGerais/Business/plune/URLs.cs` — constante `InsertPedidoBase`.

Valores fixos ilustrativos (podem mudar com o tempo no código):

| Parâmetro (exemplo) | Valor típico |
|---------------------|--------------|
| `Venda.Pedido.CompanyId` | `869` |
| `Venda.Pedido.Aprovado` | `1` |
| `Venda.Pedido.Status` | `5` |
| `Venda.Pedido.StatusPedido` | `31` (no comentário do código: executado/FIN para fluxo Hub) |
| `Venda.Pedido.ModeloId` | Por filial em `branch_config.pedido_modelo_id` (ambas `01`) — deve casar com `Venda.NotaConfig` |
| `Venda.Pedido.NaturezaOperacaoServicoId` | `2` |
| `Venda.Pedido.Serie` | Por filial em `branch_config.pedido_serie`: **Matriz `1` (NFSe)**, **ISM `0` (NFS-e)** — o código `0`/`1` só faz sentido junto com o modelo cadastrado na filial |
| `Venda.Pedido.TipoContratoId` | Implantação: `1` (IMPLANTAÇÃO). Recorrente: serviço com **maior UC** no Pipedrive (ex.: Usina `49`, Qualidade `48`, Mercado Livre `41`, SOLE `4`). **Sem fallback** — sem UC válida o Insert falha. |
| `Venda.Pedido.CentroCustoId` | `5` |
| `Venda.Pedido.ParcelamentoAutomatico` | `1` |
| `Venda.Pedido.ComissaoManual` | `1` |
| `Venda.Pedido.BaseComissao` / `ValorComissao` / `PercentualComissao` | Implantação: base = valor do pedido, `ValorComissao` = **valor do pedido**, `PercentualComissao` = **0,001**. Recorrente: base = mensalidade, `ValorComissao` = **12 × valor do pedido**, `PercentualComissao` = **total de UCs**. |

**Depois** concatenam-se os campos variáveis (ex.: `Descricao`, `DataEntrega`, `BranchId`, `ClienteId`, centros de custo, `TipoOpId`, `Observacao`, colunas customizadas `*_COL`, etc.) — ver implementação em `TicketServices.MontarQueryStringVendaPedidoInsertRessarcimento` (ramo **não** atualizar pedido pai).

> Para um **pedido completamente novo** fora desse fluxo, use a mesma ideia: **defaults fixos** + **campos obrigatórios do seu negócio** + `_AuthToken`.

---

## Incluir itens na mesma requisição (tabela embutida)

Para criar o pedido **e** linhas de `Venda.PedidoItem` em uma única transação, use os parâmetros documentados em [Pedido.md — PedidoItem](Pedido.md#embutida-item):

| Parâmetro | Valor |
|-----------|--------|
| `_Venda.Pedido.Slaves` | `Venda.PedidoItem` |
| `_Venda.Pedido.SlavesSave` | `Venda.PedidoItem` |
| `_Venda.PedidoItem.isSlave` | `PedidoItem_CompanyId_fkey` |
| `Venda.PedidoItem.<Campo>` | Repetir para cada linha (produto, quantidade, preço, etc.) |

**Boas práticas no ambiente Gebras:**

1. Informar **`Venda.PedidoItem.BranchId`** alinhado à filial do pedido quando o produto exigir filial para **custo** (evita erros do tipo “informar a Filial”).
2. Garantir **`ClienteId`** / vínculo com o pai coerente com a PK do item, se o Plune exigir na API direta `Venda.PedidoItem/Insert` (ver constante `InsertPedidoItemRessarcimento` no código).

Regras de **pareamento** de várias linhas: todos os campos da embutida repetidos **N** vezes na mesma ordem — ver [Pedido.md — visão geral embutidas](Pedido.md#embutidas-visao-geral).

---

## Checklist mínimo sugerido (novo pedido com itens)

1. **Autenticação** válida (`_AuthToken`).
2. **CompanyId**, **BranchId**, **ClienteId** corretos.
3. Campos de **situação** exigidos pelo cadastro (`Status`, `StatusPedido`, `Aprovado`, …) — ver [Pedido-colunas.md — chaves e cadastro geral](Pedido-colunas.md#chaves-e-cadastro-geral).
4. **Faturamento / NF** mínimos se aplicável: `TipoOpId` (NN), `ModeloId`, `Serie`, `NaturezaOperacaoServicoId`, `CentroCustoId` / subcentros — ver [Pedido-colunas.md — faturamento](Pedido-colunas.md#faturamento-nf-e-centro-de-custo).
5. **Contrato** se o tipo de pedido depender: `TipoContratoId` — ver [Pedido-colunas.md — contrato](Pedido-colunas.md#contrato).
6. **Descrição / datas** úteis operacionalmente: `Descricao` no Insert; **`DataEntrega`** (Detalhes \| Outros) **somente na aprovação** pós-Clicksign — data da última assinatura do envelope (`Venda.Pedido.Update` com `Aprovado=1`). No Insert o pedido fica não aprovado e sem data de entrega. Ver [Pedido-colunas.md](Pedido-colunas.md).
7. **Vínculo implantação ↔ recorrente** (após os dois Inserts): `Venda.Pedido.PedidoOriginal` = Id do outro pedido — recorrente recebe o nº da implantação e implantação recebe o nº do recorrente (`vincular_pedidos_plune_implantacao_recorrente` em `core/plune_pedido.py`).
7. **Itens:** `Slaves` / `SlavesSave` / `isSlave` + produto, quantidade, preço, **filial no item** se necessário.

### Centro de custo Gebras (Regional do Pipe)

Para o fluxo de contratos, a hierarquia do pedido deve ser preenchida nesta ordem:

1. `Venda.Pedido.CentroCustoId` = Centro **CONTRATOS COMERCIAIS** (`PLUNE_CENTRO_CUSTO_ID` em `core/gebras_defaults.py`).
2. `Venda.Pedido.SubCentroCustoId` = Sub Centro **GESTÃO DE ENERGIA** (por filial em `PLUNE_BRANCH_SETTINGS`).
3. `Venda.Pedido.SubCentroCusto2Id` = Sub Centro Nível 2 do Pipedrive (`regional_subcentro2_map` em `PLUNE_BRANCH_SETTINGS`).
4. `Venda.Pedido.SubCentroCusto3Id` = Sub Centro Nível 3 do Pipedrive (`FIELD_SUBCENTRO_NIVEL_3` / catálogo `plune_subcentro`).

O token atual pode não ter permissão para listar `Company.CentroCusto`, `Company.SubCentroCusto`, `Company.SubCentroCustoNivel2` e `Company.SubCentroCustoNivel3`; nesse caso os IDs devem ser obtidos pela tela do Plune e configurados em `core/gebras_defaults.py`.

---

## Colunas úteis para integração (referência rápida)

| Campo | Onde detalhar |
|-------|----------------|
| `pseudoValorProduto` | [Valores, totais e consistência](Pedido-colunas.md#valores-totais-e-consistência) |
| `ValorTotal`, totais de NF/pagamento | [Faturamento](Pedido-colunas.md#faturamento-nf-e-centro-de-custo) e [Valores](Pedido-colunas.md#valores-totais-e-consistência) |
| Transporte / endereço de entrega | [Pedido-colunas.md — transporte](Pedido-colunas.md#transporte-e-endereço-de-entrega) |

Para a lista completa por grupo (cliente, impostos, comissão, integração, etc.), use sempre **Pedido-colunas.md**.

---

## Retorno e pós-inclusão

- O retorno do **Insert** equivale, em sucesso, a um **Select** do registro gravado (valores finais após triggers) — [Pedido.md § Retorno Insert](Pedido.md#retorno-insert).
- Em erro, verificar `ErrorStatus` / mensagem textual e **não** assumir `NextMethod` aplicado.

---

## Documentação relacionada

| Documento | Conteúdo |
|-----------|----------|
| [Pedido.md](Pedido.md) | API completa (Browse, Select, Update, **Insert**, Delete, schema, FKs) |
| [Pedido-colunas.md](Pedido-colunas.md) | FieldId, NN, permissões Ver/Inc/Alt, tipos |
| `ModulosGerais/Business/plune/URLs.cs` | URLs e defaults `InsertPedidoBase` / exemplos Browse |

---

*Guia derivado da documentação interna `Venda.Pedido` e do uso no repositório Gebras-Faturas; validar ids de domínio (status, centro de custo, tipo de contrato) no Plune da empresa.*
