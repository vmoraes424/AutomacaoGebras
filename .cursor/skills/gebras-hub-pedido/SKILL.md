---
name: gebras-hub-pedido
description: Guides HUB (SOLE Hub / MySQL gebras) pedido creation after Clicksign signature, P1/P2 mapping, parceiro novo Plune gate, rm deal cleanup, and docs/Hub. Use when working on core/hub_pedido.py, MYSQL_DATABASE_HUB, pedido_plune, envelopes_pending hub flags, or integrating pedido HUB after Plune approval.
---

# Automação Gebras — pedido HUB

## Primeiro passo

Leia [`docs/Hub/README.md`](../../../docs/Hub/README.md) e [`docs/Hub/Integracao-AutomacaoGebras.md`](../../../docs/Hub/Integracao-AutomacaoGebras.md).

## Regras que não quebrar

1. **Dois bancos:** `MYSQL_DATABASE` = estado (`gebras_automacao`); `MYSQL_DATABASE_HUB` = pedido (`gebras`).
2. **Cliente novo Plune:** se `parceiro_plune_criado` no ganho → **não** criar pedido HUB ([Fluxo-cliente-novo.md](../../../docs/Hub/Fluxo-cliente-novo.md)).
3. **Timing:** produção — HUB após envelope fechado e `aprovar_pedidos_plune`. Dev: `DEV_HUB_SEM_APROVACAO_PLUNE=true` dispara HUB no ganho (após Plune).
4. **P1/P2:** Código instalação + código cliente no Pipedrive devem existir em `instalacao`.
5. **`rm deal`:** remove pedido HUB criado pela automação (`hub_pedido_criado`) antes de limpar `envelopes_pending`.
6. **Segredos:** não commitar `.env`; usar `HUB_CODIGO_USUARIO_SISTEMA`.

## Arquivos que mudam juntos

| Objetivo | Onde |
|----------|------|
| Criar/remover pedido HUB | `core/hub_pedido.py` |
| Flags deal/envelope | `core/database.py` (`envelopes_pending`) |
| Ganho / pós-assinatura | `core/automacao_contrato.py` |
| CLI reprocessar | `scripts/automacao_db.py`, `docs/automacao-db-cli.md` |
| Documentação | `docs/Hub/*` |

## Referência legado

Insert espelha `PedidoServices.Salvar` em Gebras-Faturas — ver [`docs/Hub/Referencia-Gebras-Faturas.md`](../../../docs/Hub/Referencia-Gebras-Faturas.md).

## Skill relacionada

Contratos/Pipedrive/Plune/Clicksign: [`gebras-automacao-contratos`](../gebras-automacao-contratos/SKILL.md) + [`ENTENDIMENTO_SISTEMA.md`](../../../ENTENDIMENTO_SISTEMA.md).
