# HUB — Criação de pedido (automação)

Guia para o INSERT de pedido no SOLE HUB, espelhando [`PedidoServices.Salvar`](../../../Gebras-Faturas/ModulosGerais/Business/geral/PedidoServices.cs) (ramo insert).

## Quando criar

| Momento | Ação |
|---------|------|
| Ganho Pipedrive | Plune + contrato + Clicksign |
| Ganho + `DEV_HUB_SEM_APROVACAO_PLUNE=true` | **`criar_pedido_hub`** logo após Plune (dev) |
| Envelope `closed` + Plune aprovado (produção) | **`criar_pedido_hub`** se `DEV_HUB_SEM_APROVACAO_PLUNE=false` |
| Parceiro **novo** no Plune no ganho | **Não** criar HUB — ver [Fluxo-cliente-novo.md](Fluxo-cliente-novo.md) |

## Pré-requisitos

1. `parceiro_plune_criado = 0` em `envelopes_pending` (parceiro já existia no Plune no ganho).
2. Pipedrive: **P1** (código instalação) e **P2** (código cliente) numéricos e consistentes com `instalacao`.
3. Ao menos um serviço com UC > 0 no deal (mapeamento em [Mapeamento-Pipedrive.md](Mapeamento-Pipedrive.md)).
4. Pedidos Plune já existem (números para `pedido_plune`).
5. `HUB_CODIGO_USUARIO_SISTEMA` configurado no `.env` (padrão **-3** = usuário `AUTOMACAO` / automação Pipedrive no HUB).

## Ordem dos INSERTs

1. **`pedido`** — cabeçalho (`codigoSituacao=0`, `valorTotal` = valor recorrência).
2. **`pedido_instalacao_extra`** — uma linha por código em P1 (vírgulas = várias instalações); valor repartido entre elas.
3. **`pedido_instalacao_servico`** — mesmos serviços (UC > 0) em cada instalação.
4. **`pedido_plune`** — **apenas** ID do pedido Plune **recorrente**.

Implementação: [`core/hub_pedido.py`](../../core/hub_pedido.py) (`criar_pedido_hub`).

## Side effects (desktop)

No C#, após salvar, podem rodar stored procedures:

- `tickets_CriarTicketDePedidoSole_SeInexistente` (serviço 2 — SOLE Web)
- `tickets_CriarTicketDePedidoGQE_SeInexistente` (serviço 6 — GQE)

A automação Python **ainda não** chama essas SPs; tickets podem ser criados manualmente ou em evolução futura.

## Idempotência

- Se `hub_pedido_criado = 1` no envelope → `skipped` / `hub_pedido_ja_criado`.
- Reprocessar deal: `python scripts/automacao_db.py rm deal <id> -y` remove pedido HUB (se criado pela automação) e estado local — ver [Integracao-AutomacaoGebras.md](Integracao-AutomacaoGebras.md).

## Erros comuns

| Erro | Causa |
|------|--------|
| `parceiro_novo_plune` | Parceiro criado no Plune no ganho |
| Instalação não encontrada | P1/P2 não batem com `instalacao` |
| Sem serviços | Todas as UCs zeradas no Pipedrive |
| Sem pedidos Plune | IDs não encontrados por `PedidoIntegracao` |
| `HUB_CODIGO_USUARIO_SISTEMA` | Variável ausente ou zero |
