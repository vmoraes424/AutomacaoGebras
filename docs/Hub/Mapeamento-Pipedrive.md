# HUB — Mapeamento Pipedrive → pedido

Hashes em [`core/pipedrive_fields.py`](../../core/pipedrive_fields.py) e lista em [`docs/Pipedrive/Pipedrive-campos-hashes.md`](../Pipedrive/Pipedrive-campos-hashes.md).

## Identificação HUB

| Campo Pipedrive | Hash | Uso no HUB |
|-----------------|------|------------|
| Código da Instalação | `FIELD_NUMERO_CONTRATO_P1` | `instalacao.Codigo` — **vários** separados por vírgula (`665,1942`) geram uma linha em `pedido_instalacao_extra` / `pedido_instalacao_servico` por instalação |
| Código Cliente | `FIELD_NUMERO_CONTRATO_P2` | `instalacao.cod_cliente` (mesmo cliente para todas) |

Validação (por código de instalação):

```sql
SELECT * FROM instalacao WHERE Codigo = <P1> AND cod_cliente = <P2>;
```

Com mais de uma instalação, o valor recorrência (`FIELD_VALOR_MENSAL`) é **repartido** entre as linhas `pedido_instalacao_extra` e as observações do pedido indicam a quantidade de instalações.

O número de contrato no Word/Plune usa `CGRc{P1}i{P2}n1r0a26` (`get_numero_contrato`).

## Serviços (`pedido_instalacao_servico.codigoServico`)

| codigo | Sigla UI | Campo Pipedrive (UC > 0) |
|--------|----------|---------------------------|
| 1 | SC | Sole Consultoria — `FIELD_QUALIDADE_ENERGIA` |
| 2 | SW | SOLE Web — `FIELD_QTD_SOLE` |
| 3 | GUF | Gestão Usina — `FIELD_GESTAO_USINA_FOTOVOLTAICA` |
| 4 | GML | Gestão ACL — `FIELD_GESTAO_ACL` |
| 6 | GQE | Gestão Qualidade — `FIELD_INDICADORES_QUALIDADE` |

Serviço **5 (DECS)** não é mapeado automaticamente (regra especial na UI).

## Valores e datas

| Campo Pipedrive | Uso no HUB |
|-----------------|------------|
| Valor Recorrência — `FIELD_VALOR_MENSAL` | `valorTotal`, `pedido_instalacao_extra.valor` |
| Data primeira cobrança — `FIELD_DATA_PRIMEIRA_COBRANCA` | `dataComercial`, `inicioContrato`, `primeiraCobranca` |
| Observações — `FIELD_OBSERVACOES_DETALHES` | `observacoes` (+ link do deal) |
| Porcentagem de Êxito — `FIELD_PERCENTUAL_EXITO` | `pedido_instalacao_extra.temServicoPercNaEconomia` (`S` se % > 0) e `servicoPercNaEconomia` (ex.: `15%` → `15.00`) |

Defaults automação: `vigencia=12`, `renovarAutomaticamente=S`, título = número do contrato. Êxito “A definir” ou vazio → flag `N` e percentual `0`.

## Vínculo Plune (`pedido_plune`)

Somente o pedido **recorrente** (`{deal_id}-recorrente`), resolvido por Browse `PedidoIntegracao` em [`obter_numeros_pedidos_plune_deal`](../../core/plune_pedido.py). Implantação **não** é gravada no HUB.
