# Cenários golden — Fase 0

Casos de referência para a Fase 5 (`test_form_regression_legacy.py`). Cada cenário define entradas e **saídas esperadas** que o adaptador form→deal deve preservar.

Fixtures JSON: [`tests/fixtures/formulario_v1/`](../../tests/fixtures/formulario_v1/).

## G1 — Deal completo com HUB (referência principal)

**Arquivos:** `deal_pipe_g1.json`, `form_payload_v1_g1.json`, `expected_g1.json`

**Perfil:** Cliente existente no Plune (`parceiro_plune_criado=0`), múltiplas UCs, observações HUB com dois blocos, implantação e recorrência.

**Assertivas (Fase 5):**

| Função | Esperado |
|--------|----------|
| `get_numero_contrato` | `CGRc665i352n1r0a26` (ano conforme fixture) |
| `parse_codigo_cliente_instalacao` | cliente `352`, instalações `[665, 1942]` |
| `extrair_signatarios` | 4 signatários, ordem Consultor→Coordenador→Cliente→Diretor |
| `validar_deal_para_automacao` | sem `DealValidationError` (com mocks de anexo e catálogo Plune) |
| `erros_validacao_observacoes_hub` | lista vazia |
| Contexto `fill_contract` | `sole_web=4`, `valor_mensal` formatado, `notas` preenchido |
| Adaptador | `deal` mesclado ≡ deal_pipe original nos `custom_fields` |

## G2 — Implantação zero (sem data pagamento impl.)

**Arquivos:** `form_payload_v1_g2_implantacao_zero.json`

**Perfil:** `valor_implantacao=0`, `data_pagamento_implantacao` ausente.

**Assertivas:**

- `_implantacao_exige_data_pagamento(deal)` → `False`
- Validação não exige data de implantação
- Plune: pedido implantação omitido ou valor zero (comportamento atual)

## G3 — Sem observações HUB (parceiro novo Plune)

**Perfil:** `hub.observacoes_detalhes` vazio; `parceiro_plune_criado=1` no fluxo.

**Assertivas:**

- `validar_deal_para_automacao` → OK (obs opcional)
- `criar_pedido_hub` → não chamado / skip
- Formulário pode estar `validated` sem blocos UC

## G4 — Flag desligada (regressão legado)

**Entrada:** mesmo `deal_pipe_g1.json`, `FORMULARIO_WEB_ENABLED=false`, sem registro em `deal_forms`.

**Assertivas:**

- Adaptador retorna `deal_pipe` **inalterado**
- Worker segue caminho atual; nenhuma leitura de `deal_forms`
- Todos os testes em `baseline-pytest.md` continuam passando (sem novas falhas)

## G5 — Formulário incompleto

**Arquivo:** `form_payload_v1_incompleto.json`

**Perfil:** falta `signatarios.email_diretor_gebras`, `servicos` todos zero.

**Assertivas:**

- Submit → status permanece `submitted` ou vai para `error`
- Não transiciona para `validated`
- Worker não processa deal

## G6 — Precedência form > Pipe

**Perfil:** `deal_pipe` com `sole_web=1` no hash; formulário com `sole_web=4`.

**Assertivas:**

- Com flag ligada e form `validated`: `get_val(deal_merged, FIELD_QTD_SOLE)` → `"4"`
- Com flag desligada: → `"1"`

## Como usar na implementação

```python
# Esboço Fase 5 — não implementado na Fase 0
@pytest.mark.parametrize("fixture", ["g1", "g2", "g5"])
def test_adaptador_golden(fixture, load_golden):
    deal_pipe, form_payload, expected = load_golden(fixture)
    merged = deal_para_automacao(deal_pipe["id"], deal_pipe)
    assert get_val(merged, FIELD_QTD_SOLE) == expected["sole_web"]
```

## Dados anonimizados

Fixtures usam CNPJ, nomes e e-mails fictícios. Não commitar deals reais de produção.
