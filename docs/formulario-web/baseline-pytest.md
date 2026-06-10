# Baseline pytest — Fase 0

Registro da suíte de testes **antes** de qualquer código do portal web. Serve como gate G0 das fases seguintes.

## Execução

```bash
pytest
pytest --co -q          # apenas contagem
pytest -m integration   # APIs externas (opcional, ambiente dev)
```

Configuração: `pytest.ini`, fixtures em `tests/conftest.py`, dependências em `requirements-dev.txt`.

## Resultado em 10/06/2026

| Métrica | Valor |
|---------|-------|
| Testes coletados | **243** |
| Passaram | **240** |
| Falharam | **3** |
| Duração | ~8,3 s |
| Ambiente | Windows, Python local, sem `-m integration` |

### Falhas pré-existentes (não causadas pelo portal)

| Teste | Arquivo | Observação |
|-------|---------|------------|
| `test_monta_insert_com_dados_pipedrive_normalizados` | `test_plune_parceiro_unit.py` | Espera `ECliente == "1"`, código retorna `"0"` |
| `test_insert_parceiro_chama_api_com_prefixo` | `test_plune_parceiro_unit.py` | Mesmo assert `ECliente` |
| `test_comissao_na_url_insert` | `test_plune_pedido_unit.py` | Deal de teste sem `Quantidade de UC's` no payload |

**Ação na Fase 0:** documentar; **não corrigir** nesta task (fora do escopo do portal). Antes da Fase 5, decidir se corrige testes ou código Plune.

**Gate para Fases 1–4:** nenhum teste **adicional** pode falhar; os 3 acima permanecem como débito conhecido até resolução explícita.

**Gate para Fase 5:** idealmente 243/243 verdes; no mínimo 240 pass + 0 regressões novas.

## Mapa de testes por domínio

### Pipedrive / Pipe

| Arquivo | Foco |
|---------|------|
| `test_pipedrive_fields.py` | Hashes, `get_val`, `parse_codigo_cliente_instalacao`, `get_numero_contrato` |
| `test_pipedrive_validations.py` | `validar_deal_para_automacao`, campos obrigatórios, HUB obs |
| `test_pipedrive_stages.py` | Etapas Contrato / Negociação |
| `test_buscar_deals_etapa_contrato.py` | Filtro deals abertos em etapa Contrato |
| `test_pipedrive_files.py` | Anexos do deal |
| `test_pipedrive_files_template.py` | Template Word anexado |
| `test_pipedrive_api_v2_set_fields.py` | Escrita de campos na API v2 |

### Contrato Word / Clicksign

| Arquivo | Foco |
|---------|------|
| `test_fill_contract.py` | Contexto `fill_contract` |
| `test_template_cleanup.py` | Limpeza do template |
| `test_extrair_signatarios.py` | Ordem e deduplicação Clicksign |
| `test_formatar_quantidade_uc.py` | Formatação UCs no Word |
| `test_formatar_data_hora_brasilia.py` | Datas em logs |
| `test_pedidos_plune_contrato.py` | Números Plune no contrato |
| `test_tipo_contrato_pedido.py` | Tipo contrato Plune |

### Plune

| Arquivo | Foco |
|---------|------|
| `test_plune_pedido_unit.py` | Insert/update pedidos, comissão, observações |
| `test_plune_parceiro_unit.py` | Criação parceiro |
| `test_plune_anexo.py` | Anexos Plune |
| `test_plune_errors.py` | Erros Plune |
| `test_aprovar_pedidos_plune.py` | Aprovação pós-assinatura |
| `test_vinculo_pedidos_plune.py` | Vínculo implantação/recorrente |
| `test_comissao_pedido.py` | Campos de comissão |
| `test_pedido_anexos.py` | Anexos em pedidos |

### HUB

| Arquivo | Foco |
|---------|------|
| `test_hub_pedido_unit.py` | P1/P2, observações UC, percentual êxito, criação pedido |

### Orquestração / automação

| Arquivo | Foco |
|---------|------|
| `test_automacao_contrato_unit.py` | Fluxo unitário do worker |
| `test_aviso_comercial.py` | E-mail comercial |

## Testes críticos de regressão (não podem quebrar)

Prioridade máxima ao integrar formulário web:

1. `test_pipedrive_validations.py` — regras de negócio do deal
2. `test_fill_contract.py` — saída do contrato
3. `test_plune_pedido_unit.py` — pedidos Plune
4. `test_hub_pedido_unit.py` — pedido HUB
5. `test_automacao_contrato_unit.py` — orquestração
6. `test_extrair_signatarios.py` — Clicksign
7. `test_buscar_deals_etapa_contrato.py` — gatilho por etapa

## Próximos testes (planejados)

Ver seção 7.4 em `task-decomposition-formulario-web.md`:

- `test_form_api_*`
- `test_form_persistence.py`
- `test_form_schema_v1.py`
- `test_form_deal_adapter.py`
- `test_form_regression_legacy.py`
