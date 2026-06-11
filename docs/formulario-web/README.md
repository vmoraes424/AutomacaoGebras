# Portal Web — Formulário Gebras

Documentação da iniciativa de substituir o preenchimento no Pipedrive por um portal React + API FastAPI.

## Índice

| Documento | Conteúdo |
|-----------|----------|
| [fase-0-especificacao.md](fase-0-especificacao.md) | Decisões da Fase 0: schema v1, status, etapas Pipe, limites no `core` |
| [matriz-campos-v1.md](matriz-campos-v1.md) | Matriz campo a campo: origem, destino, obrigatoriedade |
| [baseline-pytest.md](baseline-pytest.md) | Baseline da suíte de testes antes de implementar o portal |
| [cenarios-golden.md](cenarios-golden.md) | Cenários golden para regressão na Fase 5 |
| [schema-v1-map.json](schema-v1-map.json) | Mapa chave JSON v1 → hash Pipedrive (adaptador Fase 5) |
| [validacao-deal-746.md](validacao-deal-746.md) | GET API real no deal 746 (validação Fase 0) |
| [ddd-pragmatico.md](ddd-pragmatico.md) | Arquitetura DDD pragmática do portal |
| [../task-decomposition-formulario-web.md](../task-decomposition-formulario-web.md) | Decomposição completa do projeto |

## Fixtures

Fixtures JSON anonimizadas em [`tests/fixtures/formulario_v1/`](../../tests/fixtures/formulario_v1/).

## Status

| Fase | Status |
|------|--------|
| 0 — Especificação | ✅ Concluída |
| 1 — API FastAPI | ✅ Concluída — ver [fase-1-api.md](fase-1-api.md) |
| 2 — Banco `deal_forms` | ✅ Concluída — ver [fase-2-persistencia.md](fase-2-persistencia.md) |
| 3 — Frontend React | ✅ Concluída — ver [fase-3-frontend.md](fase-3-frontend.md) |
| 4 — Validação de domínio | ✅ Concluída — ver [fase-4-validacao.md](fase-4-validacao.md) |
| 5 — Integração worker | ✅ Concluída — ver [fase-5-integracao-worker.md](fase-5-integracao-worker.md) |
| 6 — Fluxo operacional | ✅ Concluída — ver [fase-6-operacional.md](fase-6-operacional.md) |
| 7 — Hardening e produção | ✅ Concluída — ver [fase-7-hardening.md](fase-7-hardening.md) |
