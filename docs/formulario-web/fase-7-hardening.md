# Fase 7 — Hardening e produção

Objetivo: observabilidade, proteção mínima, CI e rollback documentado.

## Proteção de acesso

| Variável | Default | Comportamento |
|----------|---------|---------------|
| `PORTAL_API_TOKEN` | *(vazio)* | Vazio = API aberta (dev/rede interna). Preenchido = exige token em todas as rotas exceto `/health` e OpenAPI. |

Headers aceitos:

- `Authorization: Bearer <token>`
- `X-Portal-Token: <token>`

Recomendação produção: token forte + reverse proxy (VPN/rede interna). Middleware: `portal/interfaces/http/middleware/auth.py`.

## Logs estruturados

| Variável | Default | Comportamento |
|----------|---------|---------------|
| `PORTAL_STRUCTURED_LOGS` | `true` | JSON em stdout por requisição (`event=http_request`, method, path, status, duration_ms). |

Módulo: `portal/infrastructure/structured_logging.py`.

## Variáveis de ambiente — portal

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `PORTAL_API_TOKEN` | Não | Token de acesso à API |
| `PORTAL_DEAL_FORM_REPOSITORY` | Não | `mysql` (prod) ou `memory` (testes) |
| `PORTAL_STRUCTURED_LOGS` | Não | `true`/`false` — logs JSON |
| `FORMULARIO_WEB_ENABLED` | Não | `false` = worker legado Pipe-only; `true` = exige form validated |

Demais variáveis (MySQL, Pipedrive, Plune, Clicksign): ver `.env.example` e `core/config.py`.

## Rollback

**Problema:** portal ou integração com problemas em produção.

**Ação (< 5 min):**

1. Definir `FORMULARIO_WEB_ENABLED=false` no `.env` do worker.
2. Reiniciar apenas o worker (`automacao_contrato.py`) — **não** é necessário apagar `deal_forms`.
3. Confirmar smoke:

```bash
pytest tests/test_form_rollback.py tests/test_form_operational_smoke.py -q
```

**Efeito:** `processar_deals_pendentes()` retorna imediatamente (não consome a fila `deal_forms`). O adaptador também ignora merge do portal. Portal pode ficar fora do ar sem impacto na automação.

**Reversão:** `FORMULARIO_WEB_ENABLED=true` após correção.

## Resiliência

| Cenário | Comportamento |
|---------|---------------|
| Portal fora do ar | Worker legado com flag `false` continua |
| Pipe indisponível | Formulário salvo em `deal_forms` continua acessível via `GET /forms/{id}` |
| Falha na nota Pipe pós-submit | Submit validado não é revertido (best-effort) |

## CI (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

| Job | Gate | Conteúdo |
|-----|------|----------|
| `pytest-portal` | **Obrigatório** | Testes portal/form + cobertura ≥ 75% (`.coveragerc`) |
| `pytest-full` | Informativo | Suite completa `-m "not integration"` (débito Plune documentado em `baseline-pytest.md`) |
| `frontend` | Obrigatório | `npm test` Vitest |

PR não deve mergear com `pytest-portal` ou `frontend` vermelhos.

## Cobertura

Áreas críticas monitoradas:

- `portal/` (API, casos de uso, persistência)
- `core/form_deal_adapter.py`
- `core/form_validation_v1.py`
- `core/form_schema_v1.py`
- `core/form_pipe_sync.py`

```bash
pytest tests/test_form_*.py tests/test_portal_*.py -m "not integration" --cov --cov-report=term-missing
```

Meta mínima: **75%** (`fail_under` em `.coveragerc`). Baseline local portal/form: ~88%.

## Smoke pós-deploy

```bash
# API
curl -s http://localhost:8000/health | jq .
curl -s "http://localhost:8000/pipedrive/users" -H "X-Portal-Token: $PORTAL_API_TOKEN"

# Testes automatizados
pytest tests/test_form_hardening_smoke.py -q
```

## Integração em staging

Antes de produção, rodar uma vez:

```bash
RUN_INTEGRATION=1 INTEGRATION_OWNER_ID=<id> INTEGRATION_DEAL_ID=<id> \
  pytest tests/test_form_operational_integration.py -m integration -v
```

Skip documentado em `tests/test_form_operational_integration.py` (exige `RUN_INTEGRATION=1`).

## Skips rastreáveis

| Teste | Motivo |
|-------|--------|
| `test_form_operational_integration.py` | Rede/API real; manual em staging (`RUN_INTEGRATION=1`) |

Nenhum outro `@pytest.mark.skip` no escopo portal/form.
