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

Com mais de uma instalação no P1, cada UC deve ter seu bloco em Observações (Detalhes) com serviços e valor próprios.

O número de contrato no Word/Plune usa `CGRc{P1}i{P2}n1r0a{AA}` (`get_numero_contrato`; **P1** = só o **primeiro** código se houver vários separados por vírgula/`;`; `AA` = 2 últimos dígitos do ano, fuso Brasília).

## Serviços e valor por UC (`Observações (Detalhes)`) — **obrigatório**

Campo **obrigatório** para criar pedido no HUB. Sem o formato abaixo, a automação **falha** (deal reaberto no ganho ou erro ao criar pedido HUB).

Formato (um bloco por instalação do P1; vários blocos separados por **`;`**):

**`UC = <código> - <serviço> + <serviço> = <valor BR>`**

Valor **obrigatório** em real brasileiro: ponto de milhar e vírgula decimal com 2 casas (ex.: `1.500,92`, `500,00`). Não use número inteiro sem vírgula (`7897979`).

Texto estruturado em **`FIELD_OBSERVACOES_DETALHES`**:

```text
UC = 00665 - SOLE WEB + Gestão ACL - Mercado Livre de Energia = 1.500,92; UC = 01942 - ACL + Sole Consultoria = 454.564,00
```

| Parte do bloco | Uso no HUB |
|----------------|------------|
| Texto após `UC =` | `instalacao.IDENTIFICACAO` (lookup com P2); grava `codigoInstalacao` = `instalacao.CODIGO` resolvido (deve bater com P1) |
| Trechos entre `-` e `=` separados por `+` | Checkboxes em `pedido_instalacao_servico` |
| Valor após `=` final do bloco (formato BR) | `pedido_instalacao_extra.valor` (gravado como decimal no MySQL) |

Nomes de serviço são resolvidos contra `pedido_nome_servico` no MySQL HUB + aliases (ex.: «ACL» → Gestão Mercado Livre, código **4**). **«SOLE» sozinho é rejeitado** (ambíguo entre Consultoria e Web).

| codigo | Nome no HUB (`pedido_nome_servico`) |
|--------|-------------------------------------|
| 1 | SOLE Consultoria |
| 2 | SOLE Web (com telemetria) |
| 3 | Gestão de Usina Fotovoltaica |
| 4 | Gestão Mercado Livre |
| 5 | Direito de Energia com Comissão de Sucesso |
| 6 | Gestão de Qualidade de Energia |

`pedido.valorTotal` = soma dos valores dos blocos UC.

## Valores e datas

| Campo Pipedrive | Uso no HUB |
|-----------------|------------|
| Valor por UC — bloco em Observações | `pedido_instalacao_extra.valor`; `valorTotal` = soma |
| Data primeira cobrança — `FIELD_DATA_PRIMEIRA_COBRANCA` | `dataComercial`, `inicioContrato`, `primeiraCobranca` |
| Observações — `FIELD_OBSERVACOES_DETALHES` | `observacoes` (+ link do deal) |
| Porcentagem de Êxito — `FIELD_PERCENTUAL_EXITO` | `pedido_instalacao_extra.temServicoPercNaEconomia` (`S` se % > 0) e `servicoPercNaEconomia` (ex.: `15%` → `15.00`) |

Defaults automação: `vigencia=12`, `renovarAutomaticamente=S`, título = número do contrato. Êxito “A definir” ou vazio → flag `N` e percentual `0`.

## Vínculo Plune (`pedido_plune`)

Somente o pedido **recorrente** (`{deal_id}-recorrente`), resolvido por Browse `PedidoIntegracao` em [`obter_numeros_pedidos_plune_deal`](../../core/plune_pedido.py). Implantação **não** é gravada no HUB.
