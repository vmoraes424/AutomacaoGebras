# Matriz de campos — formulário v1

Mapeamento campo a campo: **origem** (onde o usuário preenche no futuro), **destino** (sistemas que consomem), **obrigatoriedade** e **hash Pipe** legado.

Legenda obrigatoriedade:

- **S** = sempre obrigatório no submit
- **C** = condicional (ver nota)
- **O** = opcional no ganho; pode ser obrigatório em etapa posterior (HUB)
- **P** = permanece só no Pipe (não no formulário)

## Cliente e identificação

| Campo (UI) | Chave JSON v1 | Hash Pipe | Origem MVP | Destino | Obrig. |
|------------|---------------|-----------|------------|---------|--------|
| Contratante | `cliente.contratante` | `28d491e0…` | Formulário | Contrato Word, Plune parceiro | S |
| CPF/CNPJ | `cliente.documento` | `176d2a0d…` | Formulário | Contrato, Plune, validação | S |
| Endereço | `cliente.endereco` | `81566ac6…` | Formulário | Contrato, Plune | S |
| CEP | `cliente.cep` | `6d3373f7…` | Formulário | Contrato, Plune (`CEPPrincipal`) | S |
| Município/Estado | `cliente.municipio_estado` | `2bf3850e…` | Formulário | Contrato (`cidade`/`estado`) | S |
| Inscrição Estadual | `cliente.inscricao_estadual` | `c3e623cf…` | Formulário | Contrato Word | S |
| Inscrição Municipal | `cliente.inscricao_municipal` | `f40caca5…` | Formulário | Contrato Word | S |
| Notas | `cliente.notas` | `14720dca…` | Formulário | Contrato Word (`notas`) | S |
| Código Cliente/Instalação | `cliente.codigo_cliente_instalacao` | `41a31571…` | Formulário | Contrato (`numero_contrato`), HUB P1/P2 | S |

## Serviços (UCs)

| Campo (UI) | Chave JSON v1 | Hash Pipe | Destino | Obrig. |
|------------|---------------|-----------|---------|--------|
| SOLE Web | `servicos.sole_web` | `f9923cdc…` | Contrato, Plune itens, obs Plune | S (≥0) |
| Sole Consultoria | `servicos.sole_consultoria` | `c0a23912…` | Contrato, Plune | S (≥0) |
| Gestão ACL | `servicos.gestao_acl` | `8f998d48…` | Contrato, Plune | S (≥0) |
| Gestão Usina FV | `servicos.gestao_usina_fotovoltaica` | `1ba17944…` | Contrato, Plune | S (≥0) |
| Gestão Qualidade Energia | `servicos.gestao_qualidade_energia` | `ffb2d5ae…` | Contrato, Plune | S (≥0) |
| Quantidade de UC's | `servicos.quantidade_ucs` | `c6d1c300…` | Plune comissão recorrente | S (>0 p/ recorrente) |

Regra global: **pelo menos um** serviço com quantidade **> 0**.

## Valores e datas

| Campo (UI) | Chave JSON v1 | Hash Pipe | Destino | Obrig. |
|------------|---------------|-----------|---------|--------|
| Valor Recorrência | `valores.valor_recorrencia` | `2a331c4b…` | Contrato, Plune recorrente | S (>1) |
| Valor Implantação | `valores.valor_implantacao` | `015407d5…` | Contrato, Plune implantação | S (0 ok) |
| Data Pag. Implantação | `datas.data_pagamento_implantacao` | `2b8f62a1…` | Contrato, Plune `x1_PrevisaoCobranca` | C se impl. >1 |
| Data Primeira Cobrança | `datas.data_primeira_cobranca` | `f5f69ea5…` | Contrato, HUB datas comerciais | S |

## Comercial / Plune

| Campo (UI) | Chave JSON v1 | Hash Pipe | Destino | Obrig. |
|------------|---------------|-----------|---------|--------|
| Filial | `comercial.filial` | `be20f113…` | Plune `BranchId` (MySQL `pipedrive_filial`) | S |
| Regional | `comercial.regional` | `14855b59…` | Plune `SubCentroCusto2Id` | S |
| Consultor | `comercial.consultor` | `60ffe8e9…` | Plune `SubCentroCusto3Id` | S |
| Porcentagem de Êxito | `comercial.percentual_exito` | `225005fe…` | Contrato, HUB `temServicoPercNaEconomia` | S |

## Signatários e contatos

| Campo (UI) | Chave JSON v1 | Hash Pipe | Destino | Obrig. |
|------------|---------------|-----------|---------|--------|
| E-mail Assinante Contrato | `signatarios.email_assinante_contrato` | `a23ea2d2…` | Clicksign grupo 3 | S |
| E-mail Consultor GEBRAS | `signatarios.email_consultor_gebras` | `3bacd163…` | Clicksign g1, cláusula 10.5 | S |
| E-mail Coordenador GEBRAS | `signatarios.email_coordenador_gebras` | `3a5c1d1d…` | Clicksign g2 | S |
| E-mail Diretor GEBRAS | `signatarios.email_diretor_gebras` | `a2eba4ca…` | Clicksign g4 | S |
| Email Financeiro Contratante | `signatarios.email_financeiro_contratante` | `722da69a…` | Contrato Word | S |
| E-mail Gestor Contratante | `signatarios.email_gestor_contratante` | `3002b2df…` | Contrato, Plune `ContatoNome` | S |

Ordem Clicksign: Consultor → Coordenador → Cliente → Diretor (`SIGNER_FIELDS` em `pipedrive_fields.py`).

## HUB

| Campo (UI) | Chave JSON v1 | Hash Pipe | Destino | Obrig. |
|------------|---------------|-----------|---------|--------|
| Observações (Detalhes) | `hub.observacoes_detalhes` | `4fba2f93…` | HUB linhas UC, `pedido.valorTotal` | O no ganho; **S no HUB** |

Instalações HUB vêm de `cliente.codigo_cliente_instalacao` (`352/665,1942`), não de `notas`.

**Portal (matriz HUB):** `servicos.uc_linhas[].servicos.{key}.{ativo,valor}`. Ao editar:
- **Rascunho:** `hub.observacoes_detalhes` — `UC = <IDENTIFICACAO> - SERV1 + SERV2 = <soma R$ UC>;` (worker/HUB no ganho)
- **Pipe em tempo real:** só `cliente.codigo_cliente_instalacao` (`352/665,1942`)
- **Pipe inalterado pela matriz:** `servicos.*`, `quantidade_ucs` (varchar), `valores.valor_recorrencia` — preenchidos como antes

## Somente Pipedrive (não migrar para formulário no MVP)

| Campo | Uso |
|-------|-----|
| `id` | Chave `deal_id` |
| `title` | Título do card |
| `owner_id` | Filtro «meus cards» |
| `stage_id` / pipeline | Etapa Contrato |
| `status` | `open` |
| Anexo Proposta Comercial | Validação `tem_arquivo_proposta_comercial` |
| `update_time` | Polling worker |

## Resumo quantitativo

| Categoria | Campos no formulário v1 |
|-----------|-------------------------|
| Cliente | 9 |
| Serviços | 6 |
| Valores | 2 |
| Datas | 2 |
| Comercial | 4 |
| Signatários | 6 |
| HUB | 1 |
| **Total** | **30** |

Isso libera os 30 custom fields do Pipe para uso comercial residual ou descontinuação gradual; operação passa ao portal.
