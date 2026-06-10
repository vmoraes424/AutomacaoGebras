# Fase 4 — Validação de domínio

## Módulos

| Arquivo | Função |
|---------|--------|
| `core/form_schema_v1.py` | Modelos Pydantic v1 + mapa chave legível → hash Pipe |
| `core/form_validation_v1.py` | `validate_form_payload_v1(deal_id, payload)` |

A validação reutiliza `_validar_campo_contrato`, `_implantacao_exige_data_pagamento`, `_validar_mapeamento_plune`, `erros_validacao_observacoes_hub` de `core/pipedrive_validations.py` / `hub_pedido.py` — mesma regra de negócio, entrada convertida de payload v1 para `deal.custom_fields`.

## Submit

- Payload inválido → status `error` + `validation_errors` (chaves `cliente.cep`, `signatarios.email_diretor_gebras`, etc.)
- Payload válido → status `validated` (não mais `submitted`)

## Proposta comercial

No portal, o campo `anexos.proposta_comercial_anexada` confirma que o anexo está no deal Pipe (upload continua no Pipedrive no MVP).

## Testes

```bash
pytest tests/test_form_schema_v1.py tests/test_form_api_forms.py -q
```

Paridade com `tests/test_pipedrive_validations.py` via `TestParidadePipedriveValidations`.
