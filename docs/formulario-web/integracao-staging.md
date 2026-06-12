# Integração em staging / dev (API real)

Runbook para validar o portal ponta a ponta com Pipedrive, MySQL (`deal_forms`) e worker — **antes de produção**.

Referência de deal: [validacao-deal-746.md](validacao-deal-746.md) (`INTEGRATION_DEAL_ID=746`, owner `24587114`).

## Pré-requisitos

| Item | Variável / nota |
|------|-----------------|
| `.env` com token Pipedrive válido | `PIPEDRIVE_API_TOKEN` |
| MySQL com `deal_forms` | `MYSQL_*`, schema aplicado |
| Portal | `PORTAL_DEAL_FORM_REPOSITORY=mysql` |
| Worker flags dev | `DEV_PULAR_CLICKSIGN=true` (recomendado) |
| Formulário web ligado | `FORMULARIO_WEB_ENABLED=true` |

Subir API:

```bash
uvicorn portal.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (opcional, mesmo fluxo via curl):

```bash
cd frontend && npm run dev
```

## 1. Smoke HTTP

```bash
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/pipedrive/deal-field-options | jq '.fields | keys'
curl -s "http://localhost:8000/pipedrive/users" | jq 'length'
curl -s "http://localhost:8000/pipedrive/deals?owner_user_id=24587114" | jq 'map(.id)'
```

Esperado: health `200` com `"capabilities": {"deal_field_options": true}`; deal-field-options lista 7 chaves (comercial.* + signatários Gebras); users > 0; lista contém deal `746` se ainda em Contrato.

Se `deal-field-options` retornar **404**, o backend está **desatualizado** ou o `uvicorn` não foi reiniciado após `git pull`.

## 2. Testes automatizados com rede

```bash
# PowerShell
$env:RUN_INTEGRATION="1"
$env:INTEGRATION_OWNER_ID="24587114"
$env:INTEGRATION_DEAL_ID="746"
pytest tests/test_form_operational_integration.py -m integration -v
```

| Teste | O que valida |
|-------|----------------|
| `test_fluxo_portal_submit_worker_dev` | Listagem → GET form → submit → worker |
| `test_sync_todos_campos_mapeados_pipe_v2` | `POST /sync-field` nos **30 campos** mapeados (schema v2) |

Sem `RUN_INTEGRATION=1` os testes são **skipped** (não falham no CI).

## 3. Checklist manual (deal 746)

1. Abrir `/deals/24587114/746/form` no frontend.
2. Confirmar overlay Pipe → rascunho (valores do card, não só MySQL antigo).
3. Editar um campo texto → blur → pulse verde (sync-field).
4. Editar valor monetário (`R$ …`) e serviço UC → blur sem erro 502.
5. **Atualizar Pipedrive** (sync completo) → mensagem de sucesso.
6. **Salvar rascunho** → recarregar página → valor persiste.
7. **Enviar formulário** → status `validated` ou erros estruturados.
8. No Pipedrive: conferir 1–2 custom fields alterados no passo 3.

## 4. Worker pós-submit (opcional em dev)

Com `FORMULARIO_WEB_ENABLED=true` e flags de dev:

```bash
python -m core.automacao_contrato
# ou o entrypoint que chama processar_deals_pendentes()
```

Esperado: deal 746 na fila `deal_forms` → status `processing` / `processed`; Plune/Clicksign conforme flags.

## 5. Rollback

Se algo falhar em staging:

```bash
# .env do worker
FORMULARIO_WEB_ENABLED=false
```

Rodar regressão rápida:

```bash
pytest tests/test_form_rollback.py tests/test_form_regression_legacy.py -q
```

## 6. Registro de execução

Preencher após cada rodada em staging:

| Data | Executor | Deal | sync-field 30/30 | submit | worker | Observação |
|------|----------|------|------------------|--------|--------|------------|
| | | 746 | | | | |
