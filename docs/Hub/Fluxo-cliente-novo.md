# HUB — Cliente novo no Plune (não criar pedido HUB)

## Regra

Se no **ganho** do deal a automação **criou** o parceiro no Plune (`Parceiro.tbParceiro/Insert`), **não** criar pedido no HUB. O cadastro de cliente/instalação no HUB permanece fluxo manual (ou outro processo).

## Onde a decisão é tomada

[`_resolver_ou_criar_parceiro`](../../core/plune_pedido.py):

- CNPJ/CPF do Pipedrive → Browse parceiro ativo no Plune.
- Encontrou → `(parceiro, criado_agora=False)`.
- Não encontrou + CEP válido → `_criar_parceiro` → `(parceiro, criado_agora=True)`.
- Não encontrou + CEP inválido → `DealValidationError` (deal reaberto no Pipedrive).

`criar_pedido_plune()` retorna `parceiro_criado: true/false` no JSON de resultado.

## Persistência para o pós-assinatura

No ganho, ao salvar envelope Clicksign:

- `salvar_envelope_pendente(..., parceiro_plune_criado=...)`
- Coluna `envelopes_pending.parceiro_plune_criado` em `gebras_automacao`

**Importante:** não dá para decidir no pós-assinatura só “olhando o Plune”, porque o parceiro já terá sido criado no ganho. O critério é o **flag histórico do ganho**.

## Tabela de cenários

| Ganho Plune | `parceiro_plune_criado` | Após assinatura Clicksign |
|-------------|-------------------------|---------------------------|
| Parceiro já existia | 0 | `criar_pedido_hub` (se demais validações OK) |
| Parceiro criado (Insert) | 1 | Skip HUB — `reason: parceiro_novo_plune` |

## Log esperado

```
[*] HUB: ignorado para deal 12345 — parceiro_novo_plune
```

## Regeneração de deal

Se o envelope for recriado, o flag no envelope existente é preservado (`parceiro_plune_criado` do registro anterior ou do novo `criar_pedido_plune`).
