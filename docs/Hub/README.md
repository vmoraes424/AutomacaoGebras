# SOLE HUB — pedidos (integração AutomacaoGebras)

Documentação para **criar e remover** pedidos no **SOLE HUB** (ERP Gebras-Faturas), banco MySQL `gebras`, a partir do fluxo Pipedrive → Plune → Clicksign.

## Glossário

| Termo | Significado |
|--------|-------------|
| **HUB** | ERP desktop (`Gebras-Faturas` / `Sole-Hub`); pedidos comerciais com instalações e vínculo Plune |
| **Plune** | ERP fiscal; `Venda.Pedido` (implantação + recorrente por deal) |
| **AutomacaoGebras** | Este repositório; polling Pipedrive e automação |
| **P1 / P2** | Campos Pipedrive: Código da Instalação / Código Cliente (IDs no HUB) |
| **`gebras_automacao`** | MySQL de estado (`MYSQL_DATABASE`) |
| **`gebras`** | MySQL operacional do HUB (`MYSQL_DATABASE_HUB`) |

## Índice

| Documento | Conteúdo |
|-----------|----------|
| [Pedido-criacao.md](Pedido-criacao.md) | INSERTs, validações, serviços, idempotência |
| [Pedido-schema.md](Pedido-schema.md) | Tabelas `pedido_*` (schema validado no RDS) |
| [Mapeamento-Pipedrive.md](Mapeamento-Pipedrive.md) | P1, P2, UCs, datas, Plune |
| [Fluxo-cliente-novo.md](Fluxo-cliente-novo.md) | Parceiro novo no Plune → **não** criar pedido HUB |
| [Integracao-AutomacaoGebras.md](Integracao-AutomacaoGebras.md) | Onde o código chama o HUB; `rm deal` |
| [Referencia-Gebras-Faturas.md](Referencia-Gebras-Faturas.md) | `PedidoServices.Salvar`, forms |

## Código Python neste repo

| Módulo | Função |
|--------|--------|
| [`core/hub_pedido.py`](../../core/hub_pedido.py) | `criar_pedido_hub`, `remover_pedido_hub_por_deal` |
| [`core/database.py`](../../core/database.py) | Flags em `envelopes_pending`; `limpar_estado_deal` |
| [`core/automacao_contrato.py`](../../core/automacao_contrato.py) | Pós-assinatura: `criar_pedido_hub` |

## Variáveis de ambiente

| Variável | Uso |
|----------|-----|
| `MYSQL_DATABASE` | Estado (`gebras_automacao`) |
| `MYSQL_DATABASE_HUB` | HUB (`gebras`) |
| `HUB_CODIGO_USUARIO_SISTEMA` | `codigoUsuario` no INSERT do pedido (padrão **-3**) |

Ver [`.env.example`](../../.env.example).
