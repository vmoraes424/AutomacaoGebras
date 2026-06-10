# Fase 1 — API FastAPI

## Execução local

```bash
uvicorn portal.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa: `http://localhost:8000/docs`

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Healthcheck |
| `GET` | `/pipedrive/users` | Usuários ativos (donos de card) |
| `GET` | `/pipedrive/deals?owner_user_id=` | Deals abertos na etapa **Contrato** |
| `GET` | `/forms/{deal_id}` | Recupera rascunho/formulário |
| `GET` | `/forms/{deal_id}/status` | Status e versão do schema |
| `PUT` | `/forms/{deal_id}/draft` | Salva rascunho (`status=draft`) |
| `POST` | `/forms/{deal_id}/submit` | Envia formulário (`submitted` ou `error`) |

## Estrutura (DDD pragmático)

Ver [ddd-pragmatico.md](ddd-pragmatico.md).

```text
portal/
  main.py
  composition.py
  domain/formulario/, domain/crm/
  application/formulario/, application/crm/
  infrastructure/persistence/, infrastructure/pipedrive/
  interfaces/http/routers/, interfaces/http/schemas/
```

## Limites desta fase

- Formulários em **MySQL** (`deal_forms`); memória só com `PORTAL_DEAL_FORM_REPOSITORY=memory`.
- **Sem** integração com worker, Plune, Clicksign ou HUB.
- **Sem** login.
- Pipedrive via API v2 (deals) e v1 (users).

## Testes

```bash
pytest tests/test_form_api_health.py tests/test_form_api_pipedrive.py tests/test_form_api_forms.py
```

Suite completa: +8 testes (248 pass, 3 fails pré-existentes Plune).
