# Automacao Gebras

## Docker (worker continuo)

Build da imagem:

```bash
docker build -t automacao-gebras .
```

Execucao local com variaveis do arquivo `.env`:

```bash
docker run --rm --env-file .env automacao-gebras
```

O container inicia o worker principal com:

```bash
python -m core.automacao_contrato
```

## Portal API (FastAPI)

API do formulário web (Fase 1), separada do worker:

```bash
pip install -r requirements.txt
uvicorn portal.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints principais: `GET /health`, `GET /pipedrive/users`, `GET /pipedrive/deals?owner_user_id=`, `GET /forms/{deal_id}`, `PUT /forms/{deal_id}/draft`, `POST /forms/{deal_id}/submit`.

## Portal frontend (React)

```bash
cd frontend && npm install && npm run dev
```

Requer API em `http://localhost:8000` (proxy Vite em dev). Ver `docs/formulario-web/fase-3-frontend.md`.
