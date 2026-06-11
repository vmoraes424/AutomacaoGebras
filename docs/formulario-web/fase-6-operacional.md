# Fase 6 — Fluxo operacional

Objetivo: tornar o portal utilizável no dia a dia, com rótulos claros e rastreabilidade no Pipe.

## Etapa no portal

| Regra | Valor |
|-------|-------|
| Etapa Pipe listada | **Contrato** (`PORTAL_STAGE_NAME`) |
| Filtro API | deals **abertos** (`status=open`) do dono selecionado |
| Implementação | `ListDealsContrato` + `deal_esta_em_etapa_contrato` |

O usuário **não precisa abrir o Pipedrive** para preencher: lista cards na etapa Contrato, abre o formulário web e envia.

## Pronto para formulário

Card aparece na listagem quando:

- `deal.status == "open"`
- Etapa = Contrato (já filtrado no backend)

Campo API: `ready_for_form: true`.

## Pronto para automação

Worker com `FORMULARIO_WEB_ENABLED=true` só processa quando `deal_forms.status` ∈ `validated`, `submitted`, `processing`, `processed`.

Campo API: `ready_for_automation: true`.

| `form_status` | Rótulo (`operational_label`) | Automação |
|---------------|------------------------------|-----------|
| *(ausente)* | `pendente` | Não |
| `draft` | `rascunho` | Não |
| `error` | `erro` | Não |
| `validated` / `submitted` | `enviado` | Sim |
| `processing` | `processando` | Sim |
| `processed` | `processado` | Sim |

Módulo: `portal/domain/formulario/operational.py`. Listagem enriquecida: `ListDealsContratoEnriched`.

## Nota no Pipedrive

Após submit **validado**, o portal:

1. Sincroniza campos no deal (`push_form_to_pipedrive`)
2. Cria nota HTML via `notificar_formulario_enviado_pipedrive` → `criar_nota_deal`

Falha na nota **não** impede o submit (best-effort).

## Orientação para usuários

### Fluxo diário

1. Abrir o portal → escolher consultor (dono do card).
2. Na lista, identificar badges: **Pendente**, **Rascunho**, **Enviado**, etc.
3. Clicar em **Preencher formulário** no card desejado.
4. Anexar proposta comercial no **Pipedrive** (campo `anexos.proposta_comercial_anexada` no form).
5. Preencher e **Enviar** — erros aparecem no formulário; sucesso → status **Enviado**.
6. A automação (Plune, contrato, Clicksign, HUB) roda no worker quando o card permanece em Contrato.

### Checklist manual (pendente / enviado / processado)

| Situação | Onde ver | Ação |
|----------|----------|------|
| **Pendente** | Portal: badge cinza; sem linha em `deal_forms` | Preencher formulário |
| **Rascunho** | Portal: badge amarelo; `status=draft` | Continuar e enviar |
| **Erro** | Portal: badge vermelho; mensagens no form | Corrigir campos e reenviar |
| **Enviado** | Portal: badge verde; nota no Pipe | Aguardar worker |
| **Processando** | `deal_forms.status=processing` | Worker em execução |
| **Processado** | `deal_forms.status=processed` | Concluído |

Rollback operacional: `FORMULARIO_WEB_ENABLED=false` — worker ignora portal e usa só Pipe (portal pode ficar fora do ar).

## Testes

```bash
# Unit + API enriquecida + nota no submit
pytest tests/test_form_operational.py tests/test_form_operational_smoke.py -q

# Integração real (dev, manual)
RUN_INTEGRATION=1 INTEGRATION_OWNER_ID=... INTEGRATION_DEAL_ID=... \
  pytest tests/test_form_operational_integration.py -m integration -v
```

Frontend: badges em `DealListPage` — `npm test` em `frontend/`.
