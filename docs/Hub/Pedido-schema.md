# HUB — Schema das tabelas de pedido

Schema obtido do ambiente RDS (`MYSQL_DATABASE_HUB=gebras`). Validar com:

```sql
SHOW CREATE TABLE pedido;
SHOW CREATE TABLE pedido_plune;
SHOW CREATE TABLE pedido_instalacao_servico;
SHOW CREATE TABLE pedido_instalacao_extra;
SELECT * FROM pedido_situacao;
```

## `pedido` (cabeçalho)

| Coluna | Tipo | Notas |
|--------|------|--------|
| `codigo` | int, PK, AUTO_INCREMENT | ID interno HUB (“Código Hub Interno” na UI) |
| `codigoSituacao` | int | FK lógica → `pedido_situacao.codigo` |
| `data` | datetime | Criação |
| `codigoUsuario` | int | Usuário que criou |
| `descricao` | varchar(255) | Título (automação: número contrato `CGRc…`) |
| `observacoes` | text | |
| `dataComercial` | date | |
| `inicioContrato` | date | |
| `vigencia` | int | Meses (automação: 12) |
| `renovarAutomaticamente` | varchar(1) | `S` / `N` |
| `primeiraCobranca` | date | |
| `valorTotal` | decimal(10,2) | Soma das instalações |
| `dataAlteracao` | datetime | Updates manuais |
| `codigoUsuarioAlteracao` | int | |
| `dataAlteracaoAposAprovado` | date | Aditivos pós-conclusão |

## `pedido_situacao`

| codigo | nome |
|--------|------|
| 0 | NOVO |
| 1 | NOVO - Termo Aditivo |
| 2 | NOVO - Pedido Substituto |
| 3 | CANCELADO |
| 4 | CONCLUIDO |
| 5 | LIBERADO |

Automação usa **`codigoSituacao = 0` (NOVO)**.

## `pedido_plune`

| Coluna | Tipo |
|--------|------|
| `codigoPedido` | int |
| `codigoPedidoPlune` | int |

Automação: um registro com o ID do pedido Plune **recorrente** apenas.

## `pedido_instalacao_servico`

| Coluna | Tipo |
|--------|------|
| `codigoPedido` | int |
| `codigoInstalacao` | int |
| `codigoServico` | int |

## `pedido_instalacao_extra`

| Coluna | Tipo |
|--------|------|
| `codigoPedido` | int |
| `codigoInstalacao` | int |
| `valor` | decimal(12,2) |
| `observacoes` | text |
| `temServicoPercNaEconomia` | char(1) (`S`/`N`) |
| `servicoPercNaEconomia` | decimal(4,2) |

## `instalacao` (lookup)

Usada para validar P1/P2:

```sql
SELECT Codigo, cod_cliente, Ref_Cliente, IDENTIFICACAO, NUC
FROM instalacao
WHERE Codigo = ? AND cod_cliente = ?;
```

## Catálogos auxiliares

- `pedido_nome_servico` — nomes dos serviços
- `pedido_servico_preco` — preços por combinação (UI `UC_Instalacao.SugerirValor`)
