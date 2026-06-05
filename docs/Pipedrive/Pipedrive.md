# Pipedrive — API, webhooks e integração Gebras

Documentação prática e de referência para integração com o **Pipedrive** no projeto **AutomacaoGebras**. Cobre autenticação, convenções REST, `GET`, `POST`, `PATCH`/update, `DELETE`, campos customizados, webhooks, payloads e o fluxo local Pipedrive → contrato → Clicksign → Plune.

Para inventário detalhado de rotas por recurso, use também [Pipedrive-endpoints.md](Pipedrive-endpoints.md).

<a id="indice"></a>

## Índice

### Fundamentos

- [Visão geral](#visao-geral)
- [Base URLs e versões](#base-urls-e-versoes)
- [Autenticação](#autenticacao)
- [Formato de resposta, erros e paginação](#resposta-erros-paginacao)
- [Limites, custos e boas práticas](#limites-custos-boas-praticas)

### CRUD e entidades

- [Padrão REST: GET, POST, update e DELETE](#padrao-rest)
- [Deals](#deals)
- [Campos customizados de deals](#campos-customizados)
- [Persons, Organizations e Activities](#contatos-e-atividades)
- [Products, Deal Products, Pipelines e Stages](#produtos-pipelines-stages)
- [Notes, Files, Leads, Users e Search](#outros-recursos)

### Webhooks

- [Webhooks: visão geral](#webhooks-visao-geral)
- [Criar, listar e deletar webhooks](#webhooks-crud)
- [Eventos, objetos e combinações](#webhooks-eventos)
- [Payload v2](#webhooks-payload-v2)
- [Payload v1 legado](#webhooks-payload-v1)
- [Retries, timeout, ban e segurança](#webhooks-entrega)
- [Webhook recomendado para substituir polling](#webhook-recomendado)

### Automação Gebras

- [Fluxo atual no repositório](#fluxo-atual)
- [Campos Pipedrive usados pela automação](#campos-gebras)
- [Checklist de integração](#checklist)
- [Referências oficiais](#referencias)

---

<a id="visao-geral"></a>

## Visão geral

O Pipedrive expõe uma API REST em JSON para ler e modificar dados de CRM: negócios (`deals`), pessoas (`persons`), organizações (`organizations`), atividades (`activities`), produtos (`products`), funis (`pipelines`), etapas (`stages`), notas, arquivos, leads, usuários e campos customizados.

No projeto **AutomacaoGebras**, o Pipedrive é a origem do negócio fechado:

1. O script busca deals ganhos (`status=won`).
2. Os dados do deal e seus campos customizados preenchem o contrato `.docx`.
3. Os e-mails dos signatários vêm de custom fields do deal.
4. O contrato é enviado para Clicksign.
5. Após assinatura, ou em modo de teste, o projeto cria o pedido no Plune.

[↑ Voltar ao índice](#indice)

---

<a id="base-urls-e-versoes"></a>

## Base URLs e versões

### API v2

Use a v2 para novos desenvolvimentos quando o recurso existir nela.

```text
https://api.pipedrive.com/api/v2
```

Exemplo:

```bash
curl --request GET \
  --url "https://api.pipedrive.com/api/v2/deals?status=won&limit=100" \
  --header "x-api-token: <PIPEDRIVE_API_TOKEN>"
```

### API v1

A v1 ainda é necessária para recursos que não existem na v2, por exemplo webhooks gerais e alguns recursos de notas, arquivos e filtros.

```text
https://api.pipedrive.com/v1
```

O código atual também usa URLs no formato:

```text
https://api.pipedrive.com/api/v1/deals/{deal_id}
```

Ao implementar uma rota nova, valide a base URL no ambiente com uma chamada simples (`GET /users/me` ou `GET /deals/{id}`), porque a documentação oficial, exemplos antigos e endpoints por domínio da empresa podem aparecer com pequenas diferenças de prefixo.

### Quando usar v2 ou v1

| Use | Para |
|---|---|
| API v2 | CRUD principal de `deals`, `persons`, `organizations`, `activities`, `products`, `pipelines`, `stages`, fields e search. |
| API v1 | Webhooks gerais, notas, arquivos, filtros, currencies, recents, recursos legados e rotas ainda sem equivalente v2. |

[↑ Voltar ao índice](#indice)

---

<a id="autenticacao"></a>

## Autenticação

### API token

Para integrações internas como esta, use o token do usuário no header:

```http
x-api-token: <PIPEDRIVE_API_TOKEN>
```

Exemplo em Python:

```python
import requests

headers = {"x-api-token": PIPEDRIVE_API_TOKEN}
response = requests.get(
    "https://api.pipedrive.com/api/v2/deals",
    params={"status": "won"},
    headers=headers,
    timeout=30,
)
response.raise_for_status()
```

Observações importantes:

- O token pertence a um usuário e respeita as permissões desse usuário.
- A conta tem apenas um token ativo por usuário; trocar o token quebra integrações antigas.
- Nunca versionar token em Git. Usar `.env` e `.env.example`.
- Para receber todos os eventos por webhook, prefira token/usuário admin ou informe `user_id` de admin ao criar webhook.

### OAuth 2.0

Use OAuth quando a integração for um aplicativo distribuído, Marketplace app ou precisar instalar em várias contas Pipedrive. O fluxo é authorization code com `client_id`, `client_secret`, `redirect_uri`, `access_token`, `refresh_token` e scopes.

Para este repositório, o caminho recomendado é **API token** por ser uma automação interna.

[↑ Voltar ao índice](#indice)

---

<a id="resposta-erros-paginacao"></a>

## Formato de resposta, erros e paginação

### Resposta comum

As APIs geralmente retornam:

```json
{
  "success": true,
  "data": {},
  "additional_data": {}
}
```

Em listas, `data` costuma ser array. Em detalhe ou criação, `data` costuma ser objeto.

### Erros

Formato comum:

```json
{
  "success": false,
  "error": "unauthorized access",
  "errorCode": 401
}
```

Boas práticas:

- Tratar `401` como token inválido, expirado ou ausente.
- Tratar `403` como falta de permissão do usuário/token.
- Tratar `404` como ID inexistente ou invisível para o usuário.
- Tratar `422`/validação como payload inválido, campo obrigatório ausente, tipo incorreto ou custom field mal formatado.
- Usar `timeout` nas chamadas HTTP.
- Logar `status_code` e `response.text` em erro, sem imprimir token.

### Paginação v2

A v2 usa paginação por cursor em várias listas:

```text
GET /deals?limit=100&cursor=<next_cursor>
```

O retorno pode trazer:

```json
{
  "additional_data": {
    "next_cursor": "eyJ..."
  }
}
```

Continue buscando enquanto `next_cursor` existir.

### Paginação v1

Muitas rotas v1 usam `start` e `limit`:

```text
GET /notes?start=0&limit=100
```

O retorno costuma trazer `pagination.more_items_in_collection` e `pagination.next_start`.

[↑ Voltar ao índice](#indice)

---

<a id="limites-custos-boas-praticas"></a>

## Limites, custos e boas práticas

Cada endpoint possui custo de token/rate limit na documentação oficial. Em geral:

- `GET` de detalhe custa menos que listagens amplas.
- `GET` de lista, search e endpoints agregados custam mais.
- Webhooks enviados pelo Pipedrive não contam contra o rate limit da API.
- Evite polling agressivo; prefira webhook para eventos de mudança.
- Em listas v2, use `custom_fields` para trazer somente os campos customizados necessários.
- Use `updated_since`/`updated_until` em sincronizações incrementais.
- Use `ids` quando precisar buscar até 100 registros específicos numa chamada.
- Não use `include_fields` sem necessidade; alguns campos aumentam custo e tamanho do retorno.

[↑ Voltar ao índice](#indice)

---

<a id="padrao-rest"></a>

## Padrão REST: GET, POST, update e DELETE

### GET

Usado para listar ou consultar detalhes.

```http
GET /api/v2/deals?status=won
GET /api/v2/deals/{id}
GET /api/v2/persons/{id}
```

### POST

Usado para criar registros ou executar ações.

```http
POST /api/v2/deals
POST /api/v2/persons
POST /api/v2/deals/{id}/products/bulk
POST /v1/webhooks
```

### Update

Na API v2, updates parciais usam `PATCH`.

```http
PATCH /api/v2/deals/{id}
PATCH /api/v2/persons/{id}
PATCH /api/v2/products/{id}
```

Em endpoints v1 legados, a documentação pode usar `PUT` em alguns recursos. Para código novo neste projeto, prefira a v2 e `PATCH` quando disponível.

### DELETE

Usado para remover ou marcar como deletado.

```http
DELETE /api/v2/deals/{id}
DELETE /api/v2/persons/{id}
DELETE /v1/webhooks/{id}
```

Em várias entidades principais da v2, o delete marca o registro como deletado e há janela de recuperação antes da remoção permanente. Webhook deletado deixa de receber eventos imediatamente.

[↑ Voltar ao índice](#indice)

---

<a id="deals"></a>

## Deals

Deals representam oportunidades/negócios. É a entidade central deste projeto.

### Listar deals

```http
GET /api/v2/deals
```

Filtros úteis:

| Parâmetro | Uso |
|---|---|
| `status` | `open`, `won`, `lost`, `deleted`; aceita múltiplos separados por vírgula. |
| `owner_id` | Filtra por responsável. |
| `person_id` | Filtra por pessoa vinculada. |
| `org_id` | Filtra por organização. |
| `pipeline_id` | Filtra por funil. |
| `stage_id` | Filtra por etapa. |
| `updated_since` / `updated_until` | Sincronização incremental em RFC3339. |
| `sort_by` / `sort_direction` | Ordenação por `id`, `update_time`, `add_time`. |
| `custom_fields` | Lista de hashes de custom fields a incluir, até 15. |
| `include_option_labels` | Retorna labels de option fields. |
| `limit` / `cursor` | Paginação. |

Exemplo usado como base pelo projeto:

```python
requests.get(
    "https://api.pipedrive.com/api/v2/deals",
    params={"status": "won"},
    headers={"x-api-token": PIPEDRIVE_API_TOKEN},
    timeout=30,
)
```

### Consultar um deal

```http
GET /api/v2/deals/{id}
```

O projeto hoje consulta detalhes por:

```http
GET /api/v1/deals/{deal_id}
```

Motivo prático: a função local normaliza custom fields da resposta v1, onde campos customizados podem vir como chaves raiz de 40 caracteres.

### Criar deal

```http
POST /api/v2/deals
Content-Type: application/json
```

Campos comuns:

```json
{
  "title": "Contrato Cliente X",
  "owner_id": 123,
  "person_id": 456,
  "org_id": 789,
  "pipeline_id": 1,
  "stage_id": 2,
  "value": 1000,
  "currency": "BRL",
  "status": "open",
  "custom_fields": {
    "28d491e0263008b437e28fc55bbad8302c4646c8": "Cliente X"
  }
}
```

### Atualizar deal

```http
PATCH /api/v2/deals/{id}
Content-Type: application/json
```

Exemplos:

```json
{
  "status": "won"
}
```

```json
{
  "stage_id": 12,
  "custom_fields": {
    "176d2a0d5167d1edc9b949c75f8b9a7597eabe91": "12.345.678/0001-99"
  }
}
```

Para limpar custom field, envie `null`. Para campo multi-option (`set`), também use `null` para limpar; não use `[]`.

### Deletar deal

```http
DELETE /api/v2/deals/{id}
```

Marca como deletado. Em integrações, evite deletar automaticamente negócio comercial sem confirmação explícita.

### Rotas relacionadas a deals

Rotas importantes na v2:

- `GET /api/v2/deals/archived`
- `GET /api/v2/deals/search`
- `GET /api/v2/deals/products`
- `GET /api/v2/deals/{id}/products`
- `POST /api/v2/deals/{id}/products/bulk`
- `PATCH /api/v2/deals/{id}/products/{product_attachment_id}`
- `DELETE /api/v2/deals/{id}/products/{product_attachment_id}`
- `GET /api/v2/deals/{id}/followers`
- `POST /api/v2/deals/{id}/followers`
- `DELETE /api/v2/deals/{id}/followers/{follower_id}`
- `POST /api/v2/deals/{id}/convert/lead`
- `GET /api/v2/deals/{id}/convert/status/{conversion_id}`

Rotas úteis na v1:

- `GET /v1/deals/summary`
- `GET /v1/deals/timeline`
- `GET /v1/deals/{id}/changelog`
- `POST /v1/deals/{id}/duplicate`
- `GET /v1/deals/{id}/files`
- `GET /v1/deals/{id}/flow`
- `GET /v1/deals/{id}/mailMessages`
- `POST /v1/deals/{id}/merge`
- `GET /v1/deals/{id}/participants`
- `GET /v1/deals/{id}/permittedUsers`

[↑ Voltar ao índice](#indice)

---

<a id="campos-customizados"></a>

## Campos customizados de deals

Custom fields aparecem como hashes de 40 caracteres. Para descobrir nomes, tipos e opções:

```http
GET /api/v2/dealFields
GET /api/v2/dealFields/{field_code}
GET /api/v2/dealFields/{field_code}/options
```

Na resposta de deal, a v2 organiza custom fields em:

```json
{
  "custom_fields": {
    "hash_do_campo": "valor"
  }
}
```

Na v1, alguns custom fields podem vir no nível raiz. O projeto normaliza isso em `pipedrive_fields.buscar_deal_por_id()`.

### Regras de escrita

- Texto: enviar string.
- Numérico/monetário: enviar número quando o tipo aceitar número.
- Data: usar `YYYY-MM-DD`.
- Option/single option: enviar ID da opção, não o label.
- Multi-option/set: enviar IDs conforme formato aceito pelo field; para limpar, enviar `null`.
- Para reduzir payload em listas, usar `custom_fields=hash1,hash2`.

[↑ Voltar ao índice](#indice)

---

<a id="contatos-e-atividades"></a>

## Persons, Organizations e Activities

### Persons

Representam contatos/pessoas.

```http
GET /api/v2/persons
GET /api/v2/persons/{id}
POST /api/v2/persons
PATCH /api/v2/persons/{id}
DELETE /api/v2/persons/{id}
GET /api/v2/persons/search
```

Campos comuns:

```json
{
  "name": "Maria Silva",
  "owner_id": 123,
  "org_id": 789,
  "emails": [{"value": "maria@example.com", "primary": true, "label": "work"}],
  "phones": [{"value": "+55 11 99999-9999", "primary": true, "label": "mobile"}]
}
```

### Organizations

Representam empresas/organizações.

```http
GET /api/v2/organizations
GET /api/v2/organizations/{id}
POST /api/v2/organizations
PATCH /api/v2/organizations/{id}
DELETE /api/v2/organizations/{id}
GET /api/v2/organizations/search
```

Campos comuns:

```json
{
  "name": "Cliente Energia Ltda",
  "owner_id": 123,
  "address": {
    "value": "Rua Exemplo, 123"
  }
}
```

### Activities

Representam tarefas, reuniões, chamadas e compromissos.

```http
GET /api/v2/activities
GET /api/v2/activities/{id}
POST /api/v2/activities
PATCH /api/v2/activities/{id}
DELETE /api/v2/activities/{id}
```

Campos comuns:

```json
{
  "subject": "Follow-up contrato",
  "type": "call",
  "owner_id": 123,
  "deal_id": 456,
  "person_id": 789,
  "due_date": "2026-05-15",
  "due_time": "14:00:00",
  "duration": "00:30:00",
  "done": false
}
```

[↑ Voltar ao índice](#indice)

---

<a id="produtos-pipelines-stages"></a>

## Products, Deal Products, Pipelines e Stages

### Products

```http
GET /api/v2/products
GET /api/v2/products/{id}
POST /api/v2/products
PATCH /api/v2/products/{id}
DELETE /api/v2/products/{id}
GET /api/v2/products/search
```

Também existem variações, imagens e duplicação:

```http
POST /api/v2/products/{id}/duplicate
GET /api/v2/products/{id}/variations
POST /api/v2/products/{id}/variations
PATCH /api/v2/products/{id}/variations/{product_variation_id}
DELETE /api/v2/products/{id}/variations/{product_variation_id}
GET /api/v2/products/{id}/images
POST /api/v2/products/{id}/images
DELETE /api/v2/products/{id}/images
```

### Deal Products

Use para anexar produtos a deals e calcular valor comercial.

```http
GET /api/v2/deals/{id}/products
POST /api/v2/deals/{id}/products
POST /api/v2/deals/{id}/products/bulk
PATCH /api/v2/deals/{id}/products/{product_attachment_id}
DELETE /api/v2/deals/{id}/products/{product_attachment_id}
```

### Pipelines

```http
GET /api/v2/pipelines
GET /api/v2/pipelines/{id}
POST /api/v2/pipelines
PATCH /api/v2/pipelines/{id}
DELETE /api/v2/pipelines/{id}
```

### Stages

```http
GET /api/v2/stages
GET /api/v2/stages/{id}
POST /api/v2/stages
PATCH /api/v2/stages/{id}
DELETE /api/v2/stages/{id}
```

Para detectar mudança de etapa de deal, o webhook deve ser de `deal` com action `change`, não de `stage`. `stage` é a entidade configuração da etapa.

[↑ Voltar ao índice](#indice)

---

<a id="outros-recursos"></a>

## Notes, Files, Leads, Users e Search

### Notes

Notas ainda aparecem principalmente na v1:

```http
GET /v1/notes
POST /v1/notes
GET /v1/notes/{id}
PUT/PATCH /v1/notes/{id}
DELETE /v1/notes/{id}
GET /v1/notes/{id}/comments
POST /v1/notes/{id}/comments
GET /v1/notes/{id}/comments/{commentId}
PUT/PATCH /v1/notes/{id}/comments/{commentId}
DELETE /v1/notes/{id}/comments/{commentId}
```

### Files

```http
GET /v1/files
POST /v1/files
GET /v1/files/{id}
DELETE /v1/files/{id}
GET /v1/files/{id}/download
POST /v1/files/remote
POST /v1/files/remoteLink
```

### Leads

Leads existem na v1 e search/conversões aparecem também no ecossistema v2:

```http
GET /v1/leads
POST /v1/leads
GET /v1/leads/{id}
PATCH /v1/leads/{id}
DELETE /v1/leads/{id}
GET /v1/leads/search
GET /api/v2/leads/search
POST /api/v2/leads/{id}/convert/deal
GET /api/v2/leads/{id}/convert/status/{conversion_id}
```

### Users

```http
GET /v1/users
GET /v1/users/me
GET /v1/users/{id}
GET /v1/users/find
```

Use `GET /users/me` para testar token e descobrir dados do usuário autorizado.

### Search

```http
GET /api/v2/deals/search
GET /api/v2/persons/search
GET /api/v2/organizations/search
GET /api/v2/products/search
GET /api/v2/itemSearch
GET /api/v2/itemSearch/field
```

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-visao-geral"></a>

## Webhooks: visão geral

Webhooks enviam notificações HTTP `POST` para uma URL pública quando dados mudam no Pipedrive. Eles evitam polling constante.

Características principais:

- Limite de 40 webhooks por usuário.
- Endpoint precisa ser URL pública HTTPS válida.
- Endpoint não pode redirecionar.
- Pipedrive aceita qualquer resposta `2XX` como sucesso.
- Timeout de entrega: 10 segundos.
- Webhooks gerais são criados pela API v1 (`/v1/webhooks`), mas podem usar payload versão `2.0`.
- Webhooks v2 são o padrão atual para novos webhooks.

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-crud"></a>

## Criar, listar e deletar webhooks

### Listar webhooks

```http
GET /v1/webhooks
```

Resposta contém dados como:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "event_action": "change",
      "event_object": "deal",
      "subscription_url": "https://example.com/pipedrive/webhook",
      "version": "2.0",
      "is_active": 1,
      "last_delivery_time": "2026-05-15T18:00:00Z",
      "last_http_status": 200,
      "name": "Gebras deal won"
    }
  ]
}
```

### Criar webhook

```http
POST /v1/webhooks
Content-Type: application/json
```

Body:

```json
{
  "subscription_url": "https://seu-dominio.com/webhooks/pipedrive",
  "event_action": "change",
  "event_object": "deal",
  "version": "2.0",
  "name": "Gebras - deal changes",
  "user_id": 123,
  "http_auth_user": "usuario-opcional",
  "http_auth_password": "senha-opcional"
}
```

Campos:

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `subscription_url` | Sim | URL pública que receberá o `POST`. Não pode ser endpoint do próprio Pipedrive nem redirecionar. |
| `event_action` | Sim | `create`, `change`, `delete` ou `*`. |
| `event_object` | Sim | Entidade observada, por exemplo `deal`, `person`, `organization`. |
| `name` | Sim | Nome do webhook. |
| `version` | Não | `2.0` recomendado. Se omitido, v2 é o padrão atual. |
| `user_id` | Não | Usuário cujas permissões autorizam o webhook. |
| `http_auth_user` | Não | Usuário de Basic Auth do endpoint externo. |
| `http_auth_password` | Não | Senha de Basic Auth do endpoint externo. |

### Atualizar webhook

Não há endpoint oficial geral para update de webhook. Para alterar URL, evento, versão ou autenticação:

1. Criar novo webhook com a configuração correta.
2. Testar entrega.
3. Deletar o webhook antigo.

### Deletar webhook

```http
DELETE /v1/webhooks/{id}
```

Resposta:

```json
{
  "success": true,
  "status": "ok"
}
```

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-eventos"></a>

## Eventos, objetos e combinações

### Actions v2

- `create`
- `change`
- `delete`
- `*`

### Objetos v2

- `activity`
- `deal`
- `lead`
- `note`
- `organization`
- `person`
- `pipeline`
- `product`
- `stage`
- `user`
- `project`
- `task`
- `board`
- `phase`
- `deal_installment`
- `deal_product`
- `*`

### Exemplos de combinação

| Evento | Quando usar |
|---|---|
| `create.deal` | Novo deal criado. |
| `change.deal` | Deal alterado; inclui mudança de status, etapa, dono e custom fields. |
| `delete.deal` | Deal removido/deletado. |
| `*.deal` | Qualquer evento de deal. |
| `change.person` | Contato alterado. |
| `change.organization` | Organização alterada. |
| `change.stage` | Configuração da etapa alterada, não movimentação de deal. |
| `*.*` | Tudo que o usuário do webhook puder ver. Usar só para auditoria, pois gera muito tráfego. |

Para a automação Gebras, o evento mais útil é `change.deal`, processando somente quando o status virar `won`.

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-payload-v2"></a>

## Payload v2

Formato geral:

```json
{
  "meta": {
    "action": "change",
    "entity": "deal",
    "company_id": "123",
    "correlation_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "entity_id": "746",
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "is_bulk_edit": false,
    "timestamp": "2026-05-15T18:00:00.000Z",
    "type": "general",
    "user_id": "123",
    "version": "2.0",
    "webhook_id": "456",
    "webhook_owner_id": "123",
    "change_source": "app",
    "attempt": 1,
    "host": "empresa.pipedrive.com",
    "permitted_user_ids": ["123", "456"]
  },
  "data": {
    "id": 746,
    "title": "Biview",
    "status": "won"
  },
  "previous": {
    "status": "open"
  }
}
```

Campos importantes:

| Campo | Uso |
|---|---|
| `meta.action` | `create`, `change`, `delete`. |
| `meta.entity` | Entidade alterada. |
| `meta.entity_id` | ID do registro. |
| `meta.webhook_id` | ID do webhook que disparou. |
| `meta.change_source` | `app` ou `api`. Útil para evitar loops. |
| `meta.attempt` | Número da tentativa de entrega. |
| `data` | Estado atual essencial do objeto. |
| `previous` | Somente campos alterados no update. |

Regra por action:

| Action | `data` | `previous` |
|---|---|---|
| `create` | estado atual | `null` |
| `change` | estado atual | campos anteriores alterados |
| `delete` | `null` | último estado |

Para processar deal ganho com segurança:

1. Verificar `meta.entity == "deal"`.
2. Verificar `meta.action == "change"` ou aceitar `create` se deals puderem nascer como `won`.
3. Verificar `data.status == "won"`.
4. Se `previous.status` existir, garantir que era diferente de `won`.
5. Buscar o deal completo por API (`GET /deals/{id}`) antes de gerar contrato, pois webhook v2 traz dados essenciais, não necessariamente todos os custom fields.
6. Aplicar idempotência usando `deals_processados`.

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-payload-v1"></a>

## Payload v1 legado

Formato v1:

```json
{
  "v": 1,
  "matches_filters": {
    "current": [],
    "previous": []
  },
  "meta": {
    "v": 1,
    "action": "updated",
    "object": "deal",
    "change_source": "app",
    "id": 746,
    "company_id": 123,
    "user_id": 123,
    "host": "empresa.pipedrive.com",
    "timestamp": 1523440213,
    "timestamp_micro": 1523440213384700,
    "trans_pending": false,
    "is_bulk_update": false,
    "webhook_id": 456
  },
  "retry": 0,
  "current": {},
  "previous": {},
  "event": "updated.deal"
}
```

Actions v1:

- `added`
- `updated`
- `deleted`
- `merged`

Objetos v1:

- `activity`
- `activityType`
- `deal`
- `note`
- `organization`
- `person`
- `pipeline`
- `product`
- `stage`
- `user`

Use v2 para novos webhooks, salvo necessidade explícita de compatibilidade.

[↑ Voltar ao índice](#indice)

---

<a id="webhooks-entrega"></a>

## Retries, timeout, ban e segurança

### Regras de entrega

- Sucesso: qualquer HTTP `2XX`.
- Falha: qualquer não-`2XX` ou timeout acima de 10 segundos.
- Retries: 3 tentativas adicionais após aproximadamente 3, 30 e 150 segundos.
- Se não houver entregas bem-sucedidas por 3 dias consecutivos, o webhook pode ser deletado pelo Pipedrive.

### Ban policy

Se a primeira tentativa falhar repetidamente, o contador de ban aumenta. Ao chegar a 10, o webhook fica banido por 30 minutos. Eventos durante ban podem ser perdidos.

### Segurança do endpoint

Recomendações:

- Usar HTTPS com certificado válido.
- Responder rápido (`200`) e processar em fila/background quando possível.
- Validar Basic Auth se configurado em `http_auth_user` e `http_auth_password`.
- Registrar `meta.id`/`correlation_id` para rastreabilidade.
- Usar idempotência por `meta.id` e por `deal_id`.
- Não confiar apenas no payload para dados críticos; buscar o registro completo por API antes de ação irreversível.
- Não expor endpoint que permita criar contratos sem validação de origem/autorização.

[↑ Voltar ao índice](#indice)

---

<a id="webhook-recomendado"></a>

## Webhook recomendado para substituir polling

Configuração sugerida:

```json
{
  "subscription_url": "https://seu-dominio.com/webhooks/pipedrive/deal",
  "event_action": "change",
  "event_object": "deal",
  "version": "2.0",
  "name": "Gebras - deal changed"
}
```

Handler sugerido:

```python
def receber_webhook_pipedrive(payload: dict) -> tuple[dict, int]:
    meta = payload.get("meta") or {}
    data = payload.get("data") or {}
    previous = payload.get("previous") or {}

    if meta.get("entity") != "deal":
        return {"ignored": True, "reason": "not a deal"}, 200

    deal_id = str(meta.get("entity_id") or data.get("id") or "")
    if not deal_id:
        return {"ignored": True, "reason": "missing deal id"}, 200

    became_won = data.get("status") == "won" and previous.get("status") != "won"
    if not became_won:
        return {"ignored": True, "reason": "deal not newly won"}, 200

    # Buscar deal completo e reutilizar a idempotência existente em deals_processados.
    processar_deal_por_id(deal_id)
    return {"ok": True}, 200
```

Esse handler é conceitual. Antes de codificar, adaptar ao servidor HTTP usado no projeto e reaproveitar `buscar_deal_por_id()`, `carregar_deals_processados()` e `salvar_deal_processado()`.

[↑ Voltar ao índice](#indice)

---

<a id="fluxo-atual"></a>

## Fluxo atual no repositório

Arquivos relevantes:

| Arquivo | Papel |
|---|---|
| `core/automacao_contrato.py` | Polling de deals ganhos, geração do contrato e envio Clicksign. |
| `core/pipedrive_fields.py` | Hashes dos custom fields e helpers para extrair dados do deal. |
| `core/envelope_state.py` | Estado local de envelope/deal/pedido Plune. |
| `core/plune_pedido.py` | Criação de pedido Plune a partir de deal Pipedrive. |
| MySQL `gebras_automacao.deals_processed` | Idempotência dos deals já processados. |

Fluxo atual:

1. `buscar_deals_ganhos()` chama `GET /api/v2/deals` com `status=won`.
2. `processar_deals_pendentes()` ignora deals sem `won_time`, já processados ou ganhos antes do início do script.
3. `fill_contract(deal)` monta o `.docx` usando campos do deal.
4. `extrair_signatarios(deal)` monta a sequência de e-mails dos signatários.
5. Clicksign recebe contrato e cria envelope.
6. `salvar_envelope_pendente()` grava o vínculo local.
7. Após assinatura, `criar_pedido_plune(deal_id)` busca deal completo e cria pedido no Plune.

Ponto de atenção: se `GET /api/v2/deals` não trouxer todos os custom fields usados pelo contrato, buscar o deal completo por ID antes de renderizar.

[↑ Voltar ao índice](#indice)

---

<a id="campos-gebras"></a>

## Campos Pipedrive usados pela automação

Definidos em `core/pipedrive_fields.py`.

### Contrato e cliente

| Uso | Hash |
|---|---|
| Notas (códigos instalação / nº contrato) | `14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b` |
| Código Cliente/Código da Instalação | `41a3157128d51e2fc803eeec4b242efafcb55b4e` |
| Nome/razão social do cliente | `28d491e0263008b437e28fc55bbad8302c4646c8` |
| Endereço | `81566ac6e038bb0ba3adfa122c798b3e497b7538` |
| Cidade | `2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5` |
| Documento CPF/CNPJ | `176d2a0d5167d1edc9b949c75f8b9a7597eabe91` |
| Quantidade Sole | `f9923cdce1274da8c10cec1b9ab561e024504620` |
| Valor Recorrência (valor mensal) | `2a331c4b62c9d46aae9451af25eca2d08a3fdf0a` |
| Valor implantação | `015407d5106c321a227f1ca881f920fe2e1042ec` |
| Data implantação | `2b8f62a107891e26390459cfa4048b3eedade11b` |
| Data primeira cobrança | `f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2` |
| Indicadores de qualidade | `ffb2d5aec9acdee5a242ca19683bbf4caa24cd53` |
| Qualidade de energia | `c0a23912d889e00f51ed5bd08a55856a7e5dc930` |
| Contato financeiro | `722da69afe31c1f8fa4f5457a223e2a952ae0978` |
| Contato contratante | `3002b2df87f0577585ebaec394fd09a38ca8778f` |
| Regional (SubCentroCusto2Id) | `14855b5973f28e97dafd4e2abccc539d7461dc24` |
| Consultor (SubCentroCusto3Id) | `60ffe8e9c2aa51f717865559e86e6044bfb335e6` |

### Signatários

| Cargo/nome usado | Hash |
|---|---|
| Consultor GEBRAS | `3bacd163054a20c843e79bc525bebc1285773b17` |
| Coordenador GEBRAS | `3a5c1d1dc1b5f023f57c65b9bf725c27d754d31b` |
| Contato Principal | `a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6` |
| Diretor GEBRAS | `a2eba4ca348f3597d570d84c356aa66e81d762cd` |

Hashes legados removidos do Pipedrive (jun/2026): E-mail Gestor GEBRAS (`ecb0e3a2…`), E-mail Coordenador (`92359b12…`), E-mail Diretor (`35cc64cc…`). O código ainda lê esses valores em deals antigos.

### Recomendações para manter campos

- Ao alterar campos no Pipedrive, atualizar os hashes aqui e em `core/pipedrive_fields.py`.
- Usar `GET /api/v2/dealFields` para conferir nome, tipo e opções.
- Guardar o nome humano do campo junto do hash para reduzir erro operacional.
- Se um campo for obrigatório para contrato, validar antes de enviar Clicksign.

[↑ Voltar ao índice](#indice)

---

<a id="checklist"></a>

## Checklist de integração

### Para leitura de deals ganhos

1. Token em `PIPEDRIVE_API_TOKEN`.
2. Chamar `GET /api/v2/deals?status=won`.
3. Paginar por `next_cursor`.
4. Buscar detalhe por ID quando precisar de custom fields completos.
5. Usar idempotência por `deal_id`.
6. Validar `won_time` e status.

### Para escrita/update no Pipedrive

1. Preferir v2.
2. Usar `POST` para criar, `PATCH` para update parcial, `DELETE` para remover.
3. Enviar JSON com `Content-Type: application/json`.
4. Para custom fields, usar hash correto.
5. Para option fields, enviar ID da opção.
6. Para limpar custom field, enviar `null`.
7. Logar erro e payload sanitizado.

### Para webhooks

1. Criar endpoint público HTTPS.
2. Responder `2XX` em menos de 10 segundos.
3. Criar webhook `change.deal` v2.
4. Validar Basic Auth ou mecanismo equivalente.
5. Buscar deal completo por API antes de gerar contrato.
6. Usar idempotência por `meta.id` e `deal_id`.
7. Monitorar `last_http_status` e `last_delivery_time`.

[↑ Voltar ao índice](#indice)

---

<a id="referencias"></a>

## Referências oficiais

- [Pipedrive API Reference](https://developers.pipedrive.com/docs/api/v1)
- [OpenAPI v1](https://developers.pipedrive.com/docs/api/v1/openapi.yaml)
- [OpenAPI v2](https://developers.pipedrive.com/docs/api/v1/openapi-v2.yaml)
- [Authentication](https://pipedrive.readme.io/docs/core-api-concepts-authentication)
- [Guide for Webhooks v2](https://pipedrive.readme.io/docs/guide-for-webhooks-v2)
- [Guide for Webhooks v1](https://pipedrive.readme.io/docs/guide-for-webhooks)
- [API v2 overview](https://pipedrive.readme.io/docs/pipedrive-api-v2)

---

*Documento criado para o projeto AutomacaoGebras com base na API oficial Pipedrive e no uso local em `core/automacao_contrato.py` e `core/pipedrive_fields.py`.*
