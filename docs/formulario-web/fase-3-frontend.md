# Fase 3 — Frontend React MVP

## Stack

- Vite + React 19 + TypeScript
- React Router
- Vitest + Testing Library

## Execução

Terminal 1 — API:

```bash
uvicorn portal.main:app --reload --port 8000
```

Terminal 2 — frontend (proxy para API em dev):

```bash
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`

Produção: `npm run build` → `frontend/dist/` (servir via nginx ou estático).

## Telas

| Rota | Função |
|------|--------|
| `/` | Selecionar dono do card (`GET /pipedrive/users`) |
| `/deals/:ownerId` | Meus cards (`GET /pipedrive/deals?owner_user_id=`) |
| `/deals/:ownerId/:dealId/form` | Formulário v1 (GET/PUT/POST forms) |

## Testes frontend

```bash
cd frontend
npm test
```

## Teste de contrato (Python)

```bash
pytest tests/test_form_api_contract.py
```

Valida que `form_payload_v1_g1.json` é aceito pelo backend.

## Variáveis

| Variável | Uso |
|----------|-----|
| `VITE_API_URL` | Base da API (vazio = proxy Vite em dev) |
