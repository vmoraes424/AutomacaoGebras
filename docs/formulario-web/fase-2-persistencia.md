# Fase 2 — Persistência MySQL `deal_forms`

## Tabela

Criada em `gebras_automacao` via `core/database.py` (schema v11).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `deal_id` | INT | PK composta |
| `schema_version` | VARCHAR(16) | PK composta (default `v1`) |
| `owner_user_id` | INT NULL | Dono do card no Pipe |
| `owner_name` | VARCHAR | Auditoria |
| `deal_title` | VARCHAR | Título do deal |
| `status` | VARCHAR | `draft`, `submitted`, `error`, … |
| `payload_json` | JSON | Formulário v1 |
| `validation_errors_json` | JSON NULL | Erros no envio inválido |
| `created_at` | VARCHAR(64) | ISO UTC |
| `updated_at` | VARCHAR(64) | ISO UTC |
| `submitted_at` | VARCHAR(64) NULL | Preenchido em `submitted` |

Unicidade: `(deal_id, schema_version)`.

## Repositório

- **Produção:** `MysqlDealFormRepository` (`portal/infrastructure/persistence/`)
- **Testes:** `PORTAL_DEAL_FORM_REPOSITORY=memory` (definido em `tests/conftest.py`)

## Endpoints novos

| Método | Rota | Comportamento |
|--------|------|----------------|
| `POST` | `/forms/{deal_id}/submit` | `submitted` se válido; `error` + `validation_errors` se inválido |

Regras:

- Só `draft` é editável (`PUT .../draft`).
- Após `submitted`, rascunho retorna **409**.

## Migração

Ao subir a API ou o worker com MySQL configurado, `_init_schema` / `_migrate_schema` cria a tabela automaticamente.

Verificar:

```bash
python scripts/automacao_db.py status
```

## Testes

```bash
pytest tests/test_form_persistence.py tests/test_form_api_forms.py
```
