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
3. **Observações (Detalhes)** **obrigatório** no formato `UC = ... = <valor BR>; ...` (ex.: `1.500,92`; UCs separadas por `;`) — ver [Mapeamento-Pipedrive.md](Mapeamento-Pipedrive.md); sem isso o deal é reaberto no ganho; UCs devem coincidir com P1.
4. Pedidos Plune já existem (números para `pedido_plune`).
5. `HUB_CODIGO_USUARIO_SISTEMA` configurado no `.env` (padrão **-3** = usuário `AUTOMACAO` / automação Pipedrive no HUB).

## Ordem dos INSERTs

1. **`pedido`** — cabeçalho (`codigoSituacao=0`, `valorTotal` = valor recorrência).
2. **`pedido_instalacao_extra`** — uma linha por UC do texto em Observações; valor do bloco `= ...`.
3. **`pedido_instalacao_servico`** — serviços listados após `-` em cada bloco UC (nomes validados no catálogo HUB).
4. **`pedido_plune`** — **apenas** ID do pedido Plune **recorrente**.

Implementação: [`core/hub_pedido.py`](../../core/hub_pedido.py) (`criar_pedido_hub`).

## Side effects (desktop)

No C#, após salvar, podem rodar stored procedures:

- `tickets_CriarTicketDePedidoSole_SeInexistente` (serviço 2 — SOLE Web)
- `tickets_CriarTicketDePedidoGQE_SeInexistente` (serviço 6 — GQE)

A automação Python **ainda não** chama essas SPs; tickets podem ser criados manualmente ou em evolução futura.

### Ativação de instalações inativas

Ao **criar** ou **atualizar** pedido (`criar_pedido_hub` / `atualizar_pedido_hub`), cada UC incluída no pedido com `instalacao.Ativo <> 'S'` recebe `UPDATE instalacao SET Ativo = 'S'` na mesma transação do INSERT/UPDATE do pedido.

Implementação: `_ativar_instalacoes_hub_inativas` em [`core/hub_pedido.py`](../../core/hub_pedido.py). O JSON de retorno inclui `instalacoes_ativadas` (lista de `CODIGO` alterados).

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
