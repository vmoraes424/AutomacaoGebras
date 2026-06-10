# Fase 5 — Integração controlada com o worker

## Fluxo operacional (form ↔ Pipe)

| Momento | O que acontece |
|---------|----------------|
| **Abrir formulário** | `GET /forms/{deal_id}` busca o deal no Pipe; se não há rascunho, cria um com os valores do Pipe; se há rascunho, preenche campos vazios com o Pipe |
| **Enviar (validated)** | Salva em `deal_forms` + `PATCH` no Pipedrive (campos migrados) |
| **Worker** | Com flag ligada, mescla form validated > Pipe e segue Plune/contrato/HUB |

Módulo: `core/form_pipe_sync.py` (`deal_to_form_payload_v1`, `push_form_to_pipedrive`).

## Flag

| Variável | Default recomendado | Efeito |
|----------|---------------------|--------|
| `FORMULARIO_WEB_ENABLED` | `true` | Worker exige form `validated` e usa payload web |

Rollback: `FORMULARIO_WEB_ENABLED=false` — worker ignora portal e usa só Pipe.

## Adaptador (`core/form_deal_adapter.py`)

| Função | Uso |
|--------|-----|
| `load_deal_form_from_db(deal_id)` | SELECT em `deal_forms` |
| `merge_form_into_deal(pipe, payload)` | form > Pipe nos `custom_fields` migrados |
| `preparar_deal_para_automacao(deal)` | Resolve deal + `skipped_reason` |

## Worker (`automacao_contrato.py`)

1. `preparar_deal_para_automacao` antes do processamento.
2. Se `skipped_reason` → ignora deal (sem Plune/contrato/HUB).
3. Se `form_merged` → pula `validar_deal_para_automacao` (já validado no portal).
4. Flag desligada → fluxo inalterado.

## Testes

```bash
pytest tests/test_form_pipe_sync.py tests/test_form_deal_adapter.py tests/test_form_worker_integration.py tests/test_form_regression_legacy.py -q
```
