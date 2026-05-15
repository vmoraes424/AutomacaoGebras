# Entendimento do sistema — Automação Gebras (contratos)

## O que é

Este repositório contém uma **automação em Python** que liga o **Pipedrive** (CRM) ao **Clicksign** (assinatura eletrônica). Quando um negócio é marcado como **ganho** no Pipedrive, o sistema **gera um contrato em Word** a partir de um modelo e **abre um envelope de assinatura** no Clicksign, com **ordem sequencial** de signatários definida pelos dados do próprio deal.

Há também um script auxiliar para **registrar um webhook** na API do Clicksign (por exemplo, para receber eventos de assinatura ou de fechamento do envelope em um endpoint HTTP).

## Sobre o que é (domínio de negócio)

O foco é o **fluxo comercial pós-venda**: formalizar contratos da **Gebras** com clientes (ex.: produtos/serviços relacionados a indicadores, energia e gestão, conforme campos preenchidos no Pipedrive). O texto legal e variáveis do contrato vivem no modelo Word (`contrato_padrao.docx`); os valores (cliente, valores, datas, contatos, quantidades etc.) vêm dos **campos customizados** e metadados do deal no Pipedrive.

Arquivos gerados na pasta `contratos/` seguem o padrão `Contrato_{id_do_deal}_{título_do_deal}.docx` — por exemplo contratos associados a deals específicos do CRM.

## Componentes principais

| Artefato | Função |
|----------|--------|
| `automacao_contrato.py` | Loop principal: consulta deals ganhos, gera `.docx`, envia ao Clicksign. |
| `contrato_padrao.docx` | Modelo Word com placeholders consumidos pela biblioteca **docxtpl** (sintaxe tipo Jinja2). |
| `contratos/` | Saída dos contratos preenchidos antes do envio à assinatura. |
| `deals_processados.txt` | Registro local dos IDs de deal já processados (evita reprocessar o mesmo ganho). |
| `criar_webhook.py` | Cria webhook na API v3 do Clicksign (eventos como assinatura e fechamento automático do envelope). |

## Fluxo resumido (`automacao_contrato.py`)

1. **Início do script**: é gravada a data/hora UTC de arranque. Só entram deals **ganhos depois** desse instante (evita processar histórico antigo ao subir o processo).
2. **Polling**: a cada intervalo configurável, chama a API do Pipedrive (`/api/v2/deals`, `status=won`).
3. **Filtro**: ignora deals sem `won_time`, já listados em `deals_processados.txt`, ou com data de vitória anterior ao início do script.
4. **Geração**: monta o contexto a partir dos **hashes dos custom fields** do Pipedrive (cada hash corresponde a um campo do formulário do deal), formata moeda e datas em padrão brasileiro, gera número de contrato e texto de unidades por extenso quando aplicável, e grava o `.docx` em `contratos/`.
5. **Signatários**: lê e-mails dos custom fields em **ordem fixa** (Coordenador Principal → Contato Principal → Gestor Gebras → Diretor Principal). Envelope no Clicksign só é criado se houver pelo menos um signatário com e-mail **e** `DEV_PULAR_CLICKSIGN` estiver desligado; com `DEV_PULAR_CLICKSIGN=true`, o envio ao Clicksign é ignorado (não exige signatários para concluir o fluxo de geração do arquivo e registro do deal).
6. **Clicksign (API v3)** *(omitido se `DEV_PULAR_CLICKSIGN=true` no `.env`)*: cria envelope, envia o documento em Base64, etc. Em **desenvolvimento**, ativar `DEV_PULAR_CLICKSIGN` evita chamadas à API (e rate limit): o `.docx` continua sendo gerado em `contratos/`; combine com `TESTE_PLUNE_SEM_ASSINATURA=true` para ainda criar o pedido no Plune.
7. **Plune**: ao liberar o pedido (em teste logo após o contrato, ou em produção após assinatura), o sistema cria dois `Venda.Pedido` por deal: `implantacao` (`PedidoIntegracao=<deal_id>-implantacao`, `StatusPedido=31`) e `recorrente` (`PedidoIntegracao=<deal_id>-recorrente`, `StatusPedido=33`). Ambos nascem com `FreteporConta=9` (`Sem Frete`). O `ParametroContabilId` depende da filial: Matriz (`BranchId=751`) usa recorrente `1077` e implantação `1440`; ISM (`BranchId=790`) usa recorrente `1102` e implantação `1436`.

## Variável `DEV_PULAR_CLICKSIGN` (desenvolvimento)

| Valor | Efeito |
|-------|--------|
| `false` (padrão) | Fluxo normal: envia o contrato ao Clicksign após gerar o Word. |
| `true` | **Não** chama a API Clicksign (nenhum upload, envelope ou assinatura). O arquivo `contratos/Contrato_….docx` é gerado e o deal pode ser marcado em `deals_processados`; não há linha nova em `envelopes_pendentes.json` para esse fluxo. Para testar **Plune** sem Clicksign, use também `TESTE_PLUNE_SEM_ASSINATURA=true`. Em produção, mantenha `false`. |

## Script de webhook (`criar_webhook.py`)

Registra na Clicksign um endpoint HTTP (`URL_WEBHOOK`) para eventos como `sign` e `auto_close` (envelope concluído quando todos assinam). Serve para integrações posteriores (atualizar CRM, arquivar PDF, etc.) — o processamento desses callbacks não está implementado neste repositório, apenas a **criação** do webhook.

## Dependências e execução

- **Python** com `requests` e `docxtpl`.
- Execução típica: `python automacao_contrato.py` (processo contínuo até interrupção manual).
- Webhook: `python criar_webhook.py` (execução pontual).

## Observações de operação e segurança

- **Tokens** de Pipedrive e Clicksign estão hoje **fixos no código**; em ambiente de produção o recomendável é usar **variáveis de ambiente** ou um cofre de segredos e **não** versionar chaves.
- Se nenhum signatário tiver e-mail, o contrato é gerado mas **não** é enviado ao Clicksign; o deal **não** é marcado como processado nesse caso, permitindo nova tentativa após correção dos dados no CRM.
- O comentário no código sobre intervalo de polling pode divergir do valor numérico da constante — o comportamento efetivo é o definido pela variável `INTERVALO_POLLING_SEGUNDOS`.

## Em uma frase

**Sistema de automação que, ao ganhar um deal no Pipedrive, preenche o contrato padrão em Word e inicia a assinatura eletrônica sequencial no Clicksign**, com opção de configurar webhooks para acompanhar eventos de assinatura.

## Referências — documentação Pipedrive

- [Referência da API Pipedrive (portal v1)](https://developers.pipedrive.com/docs/api/v1) — índice geral da API REST (OpenAPI, endpoints, webhooks, etc.).
- [Deals (inclui endpoints `/api/v2/deals`)](https://developers.pipedrive.com/docs/api/v1/Deals) — alinhado ao uso deste projeto (`GET /api/v2/deals`, `status=won`).

Página principal de developers: [developers.pipedrive.com](https://developers.pipedrive.com/).
