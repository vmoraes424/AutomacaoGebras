# DDD Pragmático — Portal Gebras

Padrão adotado a partir da Fase 1 (refatoração pós-MVP API) para crescer sem acoplar HTTP, Pipe e regras de formulário.

## Princípios (pragmáticos, não dogmáticos)

1. **Bounded contexts explícitos** — cada pasta em `domain/` é um contexto com vocabulário próprio.
2. **Domínio sem framework** — entidades, enums e ports (`Protocol`); sem FastAPI, requests ou MySQL.
3. **Casos de uso finos** — `application/` orquestra domínio + ports; uma classe/função por intenção do usuário.
4. **Infraestrutura substituível** — Pipedrive, MySQL e memória implementam ports; trocar persistência não mexe na API.
5. **Anti-Corruption Layer** — `infrastructure/pipedrive/` traduz API Pipe para entidades `crm`; o domínio não conhece hashes nem REST.
6. **`core/` permanece o contexto de automação** — worker Plune/Clicksign/HUB; integração futura via adaptador (Fase 5), não import direto no portal.

## Bounded contexts do portal

| Contexto | Responsabilidade | Não faz |
|----------|------------------|---------|
| **formulario** | Rascunho/envio/validação do payload por `deal_id` | Chamar Plune, HUB, Clicksign |
| **crm** | Ler donos e cards (etapa Contrato) | Escrever no Pipe, regras de contrato |

Contexto **automacao** (legado): `core/` — processamento pós-formulário validado.

## Camadas

```text
interfaces/http     → FastAPI routers, DTOs, mapeamento HTTP ↔ aplicação
application/        → casos de uso (commands/queries)
domain/             → entidades, value objects, ports (repositories)
infrastructure/     → implementações concretas (Pipe API, MySQL, memória)
composition.py      → injeção de dependências (wire manual, sem framework)
```

Fluxo de uma requisição:

```text
Router → Use Case → Port (interface) → Adapter infra → API/DB
                ↘ Entidade de domínio
```

## Estrutura de pastas

```text
portal/
  main.py
  composition.py
  domain/
    formulario/
      entities.py          # DealForm
      value_objects.py     # FormStatus
      repositories.py        # DealFormRepository (Protocol)
      exceptions.py
    crm/
      entities.py          # CrmUser, CrmDeal
      repositories.py        # CrmReader (Protocol)
      exceptions.py
  application/
    formulario/
      get_deal_form.py
      save_draft.py
      get_status.py
    crm/
      list_users.py
      list_deals_contrato.py
  infrastructure/
    persistence/
      memory_deal_form_repository.py
    pipedrive/
      pipedrive_crm_reader.py
  interfaces/
    http/
      dependencies.py
      routers/
      schemas/
```

## Regras de dependência

| Camada | Pode importar |
|--------|----------------|
| `domain` | só stdlib / typing |
| `application` | `domain` |
| `infrastructure` | `domain`, libs externas, `core.*` só na ACL Pipe |
| `interfaces` | `application`, `domain` (exceções), schemas |
| `composition` | todas (monta o grafo) |

**Proibido** em `domain` e `application`: `fastapi`, `requests`, `core.plune_pedido`, `core.hub_pedido`, `core.automacao_contrato`.

## Evolução por fase

| Fase | Mudança DDD |
|------|-------------|
| 2 | ✅ `MysqlDealFormRepository` implementa `DealFormRepository` (schema v11) |
| 4 | `FormPayloadValidator` em `domain/formulario/` + use case `SubmitDealForm` |
| 5 | `core/form_deal_adapter.py` lê repositório; portal não chama worker |
| 3 React | consome mesmos contratos HTTP; sem lógica de negócio no front |

## Testes alinhados ao DDD

- **Domínio:** entidades e regras puras (`tests/portal/domain/`).
- **Aplicação:** use cases com ports mockados.
- **HTTP:** `test_form_api_*` (contrato da API).
- **Infra:** integração Pipe com `@pytest.mark.integration` (opcional).

## Quando *não* criar mais camadas

- Sem Aggregate Root formal se uma entidade basta (`DealForm`).
- Sem Event Sourcing, CQRS completo ou microsserviços neste estágio.
- Payload JSON v1 permanece `dict` até validação Pydantic na Fase 4 (VOs incrementais).
