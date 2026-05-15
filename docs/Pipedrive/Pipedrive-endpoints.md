# Pipedrive — Inventário de endpoints

Referência rápida de endpoints relevantes para integração. Use este arquivo como mapa de rotas; para detalhes conceituais, payloads e fluxo Gebras, veja [Pipedrive.md](Pipedrive.md).

## Convenções

| Prefixo | Base URL |
|---|---|
| `/api/v2/...` | `https://api.pipedrive.com/api/v2` |
| `/v1/...` | `https://api.pipedrive.com/v1` |

Autenticação padrão:

```http
x-api-token: <PIPEDRIVE_API_TOKEN>
```

Métodos:

- `GET`: listar, buscar detalhe, search ou relatórios.
- `POST`: criar ou executar ação.
- `PATCH`: update parcial na API v2.
- `PUT`: pode existir em recursos legados v1; verificar referência oficial antes de usar.
- `DELETE`: deletar, remover vínculo ou marcar como deletado.

---

## API v2 — recursos principais

### Activities

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/activities` | Lista atividades. |
| `POST` | `/api/v2/activities` | Cria atividade. |
| `GET` | `/api/v2/activities/{id}` | Detalha atividade. |
| `PATCH` | `/api/v2/activities/{id}` | Atualiza atividade. |
| `DELETE` | `/api/v2/activities/{id}` | Deleta atividade. |

### Activity Fields

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/activityFields` | Lista metadados de campos de atividade. |
| `POST` | `/api/v2/activityFields` | Cria campo de atividade. |
| `GET` | `/api/v2/activityFields/{field_code}` | Detalha campo. |
| `PATCH` | `/api/v2/activityFields/{field_code}` | Atualiza campo. |
| `DELETE` | `/api/v2/activityFields/{field_code}` | Remove campo. |

### Deals

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/deals` | Lista deals ativos/não arquivados. |
| `POST` | `/api/v2/deals` | Cria deal. |
| `GET` | `/api/v2/deals/{id}` | Detalha deal. |
| `PATCH` | `/api/v2/deals/{id}` | Atualiza deal. |
| `DELETE` | `/api/v2/deals/{id}` | Marca deal como deletado. |
| `GET` | `/api/v2/deals/archived` | Lista deals arquivados. |
| `GET` | `/api/v2/deals/search` | Pesquisa deals. |
| `GET` | `/api/v2/deals/products` | Lista produtos anexados a vários deals. |
| `GET` | `/api/v2/deals/installments` | Lista parcelas de vários deals. |

### Deal Fields

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/dealFields` | Lista campos de deal, incluindo custom fields. |
| `POST` | `/api/v2/dealFields` | Cria campo de deal. |
| `GET` | `/api/v2/dealFields/{field_code}` | Detalha campo de deal. |
| `PATCH` | `/api/v2/dealFields/{field_code}` | Atualiza campo de deal. |
| `DELETE` | `/api/v2/dealFields/{field_code}` | Remove campo de deal. |
| `POST` | `/api/v2/dealFields/{field_code}/options` | Cria opção de campo. |
| `PATCH` | `/api/v2/dealFields/{field_code}/options` | Atualiza opções de campo. |
| `DELETE` | `/api/v2/dealFields/{field_code}/options` | Remove opção de campo. |

### Deal Followers

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/deals/{id}/followers` | Lista seguidores do deal. |
| `POST` | `/api/v2/deals/{id}/followers` | Adiciona seguidor. |
| `GET` | `/api/v2/deals/{id}/followers/changelog` | Histórico de seguidores. |
| `DELETE` | `/api/v2/deals/{id}/followers/{follower_id}` | Remove seguidor. |

### Deal Products

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/deals/{id}/products` | Lista produtos do deal. |
| `POST` | `/api/v2/deals/{id}/products` | Adiciona produto ao deal. |
| `PATCH` | `/api/v2/deals/{id}/products/{product_attachment_id}` | Atualiza produto anexado. |
| `DELETE` | `/api/v2/deals/{id}/products/{product_attachment_id}` | Remove produto do deal. |
| `POST` | `/api/v2/deals/{id}/products/bulk` | Adiciona até 100 produtos de uma vez. |

### Deal Discounts e Installments

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/deals/{id}/discounts` | Lista descontos do deal. |
| `POST` | `/api/v2/deals/{id}/discounts` | Cria desconto no deal. |
| `PATCH` | `/api/v2/deals/{id}/discounts/{discount_id}` | Atualiza desconto. |
| `DELETE` | `/api/v2/deals/{id}/discounts/{discount_id}` | Remove desconto. |
| `POST` | `/api/v2/deals/{id}/installments` | Cria parcela no deal. |
| `PATCH` | `/api/v2/deals/{id}/installments/{installment_id}` | Atualiza parcela. |
| `DELETE` | `/api/v2/deals/{id}/installments/{installment_id}` | Remove parcela. |

### Deal Conversion

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v2/deals/{id}/convert/lead` | Converte deal para lead. |
| `GET` | `/api/v2/deals/{id}/convert/status/{conversion_id}` | Consulta status da conversão. |

### Persons

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/persons` | Lista pessoas. |
| `POST` | `/api/v2/persons` | Cria pessoa. |
| `GET` | `/api/v2/persons/{id}` | Detalha pessoa. |
| `PATCH` | `/api/v2/persons/{id}` | Atualiza pessoa. |
| `DELETE` | `/api/v2/persons/{id}` | Deleta pessoa. |
| `GET` | `/api/v2/persons/search` | Pesquisa pessoas. |
| `GET` | `/api/v2/persons/{id}/picture` | Busca imagem da pessoa. |

### Person Fields

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/personFields` | Lista campos de pessoa. |
| `POST` | `/api/v2/personFields` | Cria campo de pessoa. |
| `GET` | `/api/v2/personFields/{field_code}` | Detalha campo. |
| `PATCH` | `/api/v2/personFields/{field_code}` | Atualiza campo. |
| `DELETE` | `/api/v2/personFields/{field_code}` | Remove campo. |
| `POST` | `/api/v2/personFields/{field_code}/options` | Cria opção. |
| `PATCH` | `/api/v2/personFields/{field_code}/options` | Atualiza opção. |
| `DELETE` | `/api/v2/personFields/{field_code}/options` | Remove opção. |

### Person Followers

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/persons/{id}/followers` | Lista seguidores. |
| `POST` | `/api/v2/persons/{id}/followers` | Adiciona seguidor. |
| `GET` | `/api/v2/persons/{id}/followers/changelog` | Histórico de seguidores. |
| `DELETE` | `/api/v2/persons/{id}/followers/{follower_id}` | Remove seguidor. |

### Organizations

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/organizations` | Lista organizações. |
| `POST` | `/api/v2/organizations` | Cria organização. |
| `GET` | `/api/v2/organizations/{id}` | Detalha organização. |
| `PATCH` | `/api/v2/organizations/{id}` | Atualiza organização. |
| `DELETE` | `/api/v2/organizations/{id}` | Deleta organização. |
| `GET` | `/api/v2/organizations/search` | Pesquisa organizações. |

### Organization Fields

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/organizationFields` | Lista campos de organização. |
| `POST` | `/api/v2/organizationFields` | Cria campo de organização. |
| `GET` | `/api/v2/organizationFields/{field_code}` | Detalha campo. |
| `PATCH` | `/api/v2/organizationFields/{field_code}` | Atualiza campo. |
| `DELETE` | `/api/v2/organizationFields/{field_code}` | Remove campo. |
| `POST` | `/api/v2/organizationFields/{field_code}/options` | Cria opção. |
| `PATCH` | `/api/v2/organizationFields/{field_code}/options` | Atualiza opção. |
| `DELETE` | `/api/v2/organizationFields/{field_code}/options` | Remove opção. |

### Organization Followers

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/organizations/{id}/followers` | Lista seguidores. |
| `POST` | `/api/v2/organizations/{id}/followers` | Adiciona seguidor. |
| `GET` | `/api/v2/organizations/{id}/followers/changelog` | Histórico de seguidores. |
| `DELETE` | `/api/v2/organizations/{id}/followers/{follower_id}` | Remove seguidor. |

### Products

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/products` | Lista produtos. |
| `POST` | `/api/v2/products` | Cria produto. |
| `GET` | `/api/v2/products/{id}` | Detalha produto. |
| `PATCH` | `/api/v2/products/{id}` | Atualiza produto. |
| `DELETE` | `/api/v2/products/{id}` | Deleta produto. |
| `GET` | `/api/v2/products/search` | Pesquisa produtos. |
| `POST` | `/api/v2/products/{id}/duplicate` | Duplica produto. |
| `GET` | `/api/v2/products/{id}/images` | Busca imagens. |
| `POST` | `/api/v2/products/{id}/images` | Envia imagem. |
| `DELETE` | `/api/v2/products/{id}/images` | Remove imagem. |

### Product Variations

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/products/{id}/variations` | Lista variações do produto. |
| `POST` | `/api/v2/products/{id}/variations` | Cria variação. |
| `PATCH` | `/api/v2/products/{id}/variations/{product_variation_id}` | Atualiza variação. |
| `DELETE` | `/api/v2/products/{id}/variations/{product_variation_id}` | Remove variação. |

### Product Fields

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/productFields` | Lista campos de produto. |
| `POST` | `/api/v2/productFields` | Cria campo de produto. |
| `GET` | `/api/v2/productFields/{field_code}` | Detalha campo. |
| `PATCH` | `/api/v2/productFields/{field_code}` | Atualiza campo. |
| `DELETE` | `/api/v2/productFields/{field_code}` | Remove campo. |
| `POST` | `/api/v2/productFields/{field_code}/options` | Cria opção. |
| `PATCH` | `/api/v2/productFields/{field_code}/options` | Atualiza opção. |
| `DELETE` | `/api/v2/productFields/{field_code}/options` | Remove opção. |

### Product Followers

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/products/{id}/followers` | Lista seguidores. |
| `POST` | `/api/v2/products/{id}/followers` | Adiciona seguidor. |
| `GET` | `/api/v2/products/{id}/followers/changelog` | Histórico de seguidores. |
| `DELETE` | `/api/v2/products/{id}/followers/{follower_id}` | Remove seguidor. |

### Pipelines

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/pipelines` | Lista funis. |
| `POST` | `/api/v2/pipelines` | Cria funil. |
| `GET` | `/api/v2/pipelines/{id}` | Detalha funil. |
| `PATCH` | `/api/v2/pipelines/{id}` | Atualiza funil. |
| `DELETE` | `/api/v2/pipelines/{id}` | Remove funil. |

### Stages

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/stages` | Lista etapas. |
| `POST` | `/api/v2/stages` | Cria etapa. |
| `GET` | `/api/v2/stages/{id}` | Detalha etapa. |
| `PATCH` | `/api/v2/stages/{id}` | Atualiza etapa. |
| `DELETE` | `/api/v2/stages/{id}` | Remove etapa. |

### Search

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/itemSearch` | Pesquisa em múltiplos tipos. |
| `GET` | `/api/v2/itemSearch/field` | Pesquisa por campo específico. |
| `GET` | `/api/v2/deals/search` | Pesquisa deals. |
| `GET` | `/api/v2/persons/search` | Pesquisa pessoas. |
| `GET` | `/api/v2/organizations/search` | Pesquisa organizações. |
| `GET` | `/api/v2/products/search` | Pesquisa produtos. |
| `GET` | `/api/v2/leads/search` | Pesquisa leads. |
| `GET` | `/api/v2/projects/search` | Pesquisa projetos. |

### Leads conversion

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v2/leads/{id}/convert/deal` | Converte lead para deal. |
| `GET` | `/api/v2/leads/{id}/convert/status/{conversion_id}` | Consulta status da conversão. |

### Projects, Tasks, Boards e Phases

Esses recursos podem depender de plano/produto habilitado.

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v2/projectFields` | Lista campos de projeto. |
| `POST` | `/api/v2/projectFields` | Cria campo de projeto. |
| `GET` | `/api/v2/projects` | Lista projetos. |
| `POST` | `/api/v2/projects` | Cria projeto. |
| `GET` | `/api/v2/projects/{id}` | Detalha projeto. |
| `PATCH` | `/api/v2/projects/{id}` | Atualiza projeto. |
| `DELETE` | `/api/v2/projects/{id}` | Remove projeto. |
| `GET` | `/api/v2/projects/archived` | Lista projetos arquivados. |
| `POST` | `/api/v2/projects/{id}/archive` | Arquiva projeto. |
| `GET` | `/api/v2/projectTemplates` | Lista templates de projeto. |
| `GET` | `/api/v2/projectTemplates/{id}` | Detalha template. |
| `GET` | `/api/v2/tasks` | Lista tarefas. |
| `POST` | `/api/v2/tasks` | Cria tarefa. |
| `GET` | `/api/v2/tasks/{id}` | Detalha tarefa. |
| `PATCH` | `/api/v2/tasks/{id}` | Atualiza tarefa. |
| `DELETE` | `/api/v2/tasks/{id}` | Remove tarefa. |
| `GET` | `/api/v2/boards` | Lista boards. |
| `POST` | `/api/v2/boards` | Cria board. |
| `GET` | `/api/v2/boards/{id}` | Detalha board. |
| `PATCH` | `/api/v2/boards/{id}` | Atualiza board. |
| `DELETE` | `/api/v2/boards/{id}` | Remove board. |
| `GET` | `/api/v2/phases` | Lista fases. |
| `POST` | `/api/v2/phases` | Cria fase. |
| `GET` | `/api/v2/phases/{id}` | Detalha fase. |
| `PATCH` | `/api/v2/phases/{id}` | Atualiza fase. |
| `DELETE` | `/api/v2/phases/{id}` | Remove fase. |

---

## API v1 — webhooks e recursos legados úteis

### Webhooks

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/webhooks` | Lista webhooks. |
| `POST` | `/v1/webhooks` | Cria webhook geral. |
| `DELETE` | `/v1/webhooks/{id}` | Deleta webhook. |

Não há update geral de webhook. Criar novo e remover antigo.

### Deals v1 adicionais

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/deals/summary` | Resumo de deals não arquivados. |
| `GET` | `/v1/deals/summary/archived` | Resumo de deals arquivados. |
| `GET` | `/v1/deals/timeline` | Timeline agrupada de deals. |
| `GET` | `/v1/deals/timeline/archived` | Timeline de deals arquivados. |
| `GET` | `/v1/deals/{id}/changelog` | Histórico de mudanças. |
| `POST` | `/v1/deals/{id}/duplicate` | Duplica deal. |
| `GET` | `/v1/deals/{id}/files` | Arquivos do deal. |
| `GET` | `/v1/deals/{id}/flow` | Feed/flow do deal. |
| `GET` | `/v1/deals/{id}/participantsChangelog` | Histórico de participantes. |
| `GET` | `/v1/deals/{id}/mailMessages` | E-mails do deal. |
| `POST` | `/v1/deals/{id}/merge` | Mescla deals. |
| `GET` | `/v1/deals/{id}/participants` | Lista participantes. |
| `POST` | `/v1/deals/{id}/participants` | Adiciona participante. |
| `DELETE` | `/v1/deals/{id}/participants/{deal_participant_id}` | Remove participante. |
| `GET` | `/v1/deals/{id}/permittedUsers` | Usuários com acesso. |

### Notes

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/notes` | Lista notas. |
| `POST` | `/v1/notes` | Cria nota. |
| `GET` | `/v1/notes/{id}` | Detalha nota. |
| `PUT/PATCH` | `/v1/notes/{id}` | Atualiza nota, conforme suporte do endpoint. |
| `DELETE` | `/v1/notes/{id}` | Remove nota. |
| `GET` | `/v1/notes/{id}/comments` | Lista comentários. |
| `POST` | `/v1/notes/{id}/comments` | Cria comentário. |
| `GET` | `/v1/notes/{id}/comments/{commentId}` | Detalha comentário. |
| `PUT/PATCH` | `/v1/notes/{id}/comments/{commentId}` | Atualiza comentário. |
| `DELETE` | `/v1/notes/{id}/comments/{commentId}` | Remove comentário. |

### Files

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/files` | Lista arquivos. |
| `POST` | `/v1/files` | Envia arquivo. |
| `GET` | `/v1/files/{id}` | Detalha arquivo. |
| `DELETE` | `/v1/files/{id}` | Remove arquivo. |
| `GET` | `/v1/files/{id}/download` | Inicializa download. |
| `POST` | `/v1/files/remote` | Cria arquivo remoto e vincula. |
| `POST` | `/v1/files/remoteLink` | Vincula arquivo remoto existente. |

### Leads v1

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/leads` | Lista leads. |
| `POST` | `/v1/leads` | Cria lead. |
| `GET` | `/v1/leads/archived` | Lista leads arquivados. |
| `GET` | `/v1/leads/search` | Pesquisa leads. |
| `GET` | `/v1/leads/{id}` | Detalha lead. |
| `PATCH` | `/v1/leads/{id}` | Atualiza lead. |
| `DELETE` | `/v1/leads/{id}` | Remove lead. |
| `GET` | `/v1/leads/{id}/permittedUsers` | Usuários com acesso. |

### Filters

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/filters` | Lista filtros. |
| `POST` | `/v1/filters` | Cria filtro. |
| `GET` | `/v1/filters/{id}` | Detalha filtro. |
| `PUT/PATCH` | `/v1/filters/{id}` | Atualiza filtro, conforme suporte do endpoint. |
| `DELETE` | `/v1/filters/{id}` | Remove filtro. |
| `GET` | `/v1/filters/helpers` | Helpers para criar filtros. |

### Currencies

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/currencies` | Lista moedas disponíveis. |

### Recents

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/recents` | Lista itens recentes. |

### Users

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/users` | Lista usuários. |
| `GET` | `/v1/users/me` | Usuário autenticado. |
| `GET` | `/v1/users/{id}` | Detalha usuário. |
| `GET` | `/v1/users/find` | Busca usuários por nome. |
| `GET` | `/v1/users/{id}/permissions` | Permissões. |
| `GET` | `/v1/users/{id}/roleAssignments` | Atribuições de role. |
| `GET` | `/v1/users/{id}/roleSettings` | Configurações de role. |

### Campos v1

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/activityFields` | Campos de atividade. |
| `GET` | `/v1/dealFields` | Campos de deal. |
| `GET` | `/v1/personFields` | Campos de pessoa. |
| `GET` | `/v1/organizationFields` | Campos de organização. |
| `GET` | `/v1/productFields` | Campos de produto. |
| `GET` | `/v1/noteFields` | Campos de nota. |
| `GET` | `/v1/leadFields` | Campos de lead. |

### Organization Relationships

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/organizationRelationships` | Lista relacionamentos entre organizações. |
| `POST` | `/v1/organizationRelationships` | Cria relacionamento. |
| `GET` | `/v1/organizationRelationships/{id}` | Detalha relacionamento. |
| `PUT/PATCH` | `/v1/organizationRelationships/{id}` | Atualiza relacionamento. |
| `DELETE` | `/v1/organizationRelationships/{id}` | Remove relacionamento. |

### Mailbox e Meetings

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/v1/mailbox/mailThreads` | Lista threads de e-mail. |
| `GET` | `/v1/mailbox/mailThreads/{id}` | Detalha thread. |
| `GET` | `/v1/mailbox/mailThreads/{id}/mailMessages` | Mensagens da thread. |
| `GET` | `/v1/mailbox/mailMessages/{id}` | Detalha mensagem. |
| `GET` | `/v1/meetings/userProviderLinks` | Links de provedor de reuniões. |
| `DELETE` | `/v1/meetings/userProviderLinks/{id}` | Remove link de provedor. |

---

## Endpoints usados diretamente no AutomacaoGebras

| Uso | Método | Endpoint |
|---|---|---|
| Buscar deals ganhos | `GET` | `/api/v2/deals?status=won` |
| Buscar deal completo por ID | `GET` | `/api/v1/deals/{deal_id}` |
| Descobrir campos customizados de deal | `GET` | `/api/v2/dealFields` ou `/v1/dealFields` |
| Criar webhook para deal ganho | `POST` | `/v1/webhooks` com `event_action=change`, `event_object=deal`, `version=2.0` |
| Listar webhooks cadastrados | `GET` | `/v1/webhooks` |
| Remover webhook antigo | `DELETE` | `/v1/webhooks/{id}` |

---

## Checklist antes de usar uma rota

1. Confirmar se há equivalente v2; preferir v2.
2. Confirmar permissões do token.
3. Confirmar método HTTP exato (`PATCH` v2, `PUT/PATCH` em alguns legados v1).
4. Conferir parâmetros obrigatórios e formato do body na referência oficial.
5. Para lista, implementar paginação.
6. Para escrita, logar resposta e tratar `success=false`.
7. Para deletar, confirmar se é soft delete, remoção de vínculo ou delete definitivo.

---

## Referências

- [Pipedrive API Reference](https://developers.pipedrive.com/docs/api/v1)
- [OpenAPI v2](https://developers.pipedrive.com/docs/api/v1/openapi-v2.yaml)
- [OpenAPI v1](https://developers.pipedrive.com/docs/api/v1/openapi.yaml)
- [Webhooks v2](https://pipedrive.readme.io/docs/guide-for-webhooks-v2)
