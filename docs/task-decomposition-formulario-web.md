# Task Decomposition - Portal Web de Preenchimento Gebras

## 1. Contexto

O projeto atual usa o Pipedrive como origem principal dos dados do contrato, Plune e HUB. O limite de campos personalizados do Pipe passou a bloquear a evolução do fluxo, porque muitos dados operacionais nao pertencem ao CRM em si: sao dados de contrato, Plune, HUB, instalacoes, valores e regras de processamento.

O pivot definido e criar um portal web proprio para o preenchimento dessas informacoes. O usuario deve operar pelo formulario, sem precisar entrar no Pipedrive. O Pipe continua existindo como backend de CRM e fonte de cards/deals, mas deixa de ser a interface principal do usuario.

Esta task nao implementa codigo. Ela define a decomposicao, fronteiras, riscos e ordem sugerida de execucao.

## 2. Objetivo

Criar uma base de trabalho para implementar um portal com:

- Frontend em React para o usuario listar cards e preencher informacoes.
- Backend em FastAPI para expor endpoints, validar dados e reaproveitar o que ja existe em Python.
- Banco proprio para armazenar o payload completo do formulario por deal.
- Integracao segura com o worker atual, minimizando alteracoes no `core` da automacao.

## 3. Decisoes Iniciais

- **Arquitetura do portal:** DDD pragmático (bounded contexts `formulario` + `crm`). Ver [`docs/formulario-web/ddd-pragmatico.md`](formulario-web/ddd-pragmatico.md).
- A abordagem escolhida e a opcao 2: frontend separado + backend API.
- O backend deve ser Python/FastAPI para reaproveitar os modulos atuais.
- O frontend deve ser React, inicialmente simples, sem framework pesado se nao houver necessidade.
- Nao havera login nominal no MVP.
- O uso sem login pressupoe ambiente controlado. Se a pagina ficar exposta fora da rede/ambiente interno, deve existir ao menos protecao por token, proxy, VPN ou regra equivalente antes de producao.
- O Pipe sera usado via API para cards, donos, etapas e status.
- O formulario web sera a fonte oficial dos dados ricos de contrato, Plune e HUB.
- O worker atual deve continuar existindo, mas passara a consumir dados do banco do formulario quando disponiveis.
- **Testes sao obrigatorios em cada fase**, nao apenas no final. Nenhuma fase avanca sem a suíte existente passando e sem testes novos cobrindo o que foi adicionado.

## 4. Arquitetura Alvo

```text
Usuario
  -> Portal React
  -> API FastAPI
  -> Banco AutomacaoGebras
  -> Pipedrive API
  -> Worker atual
  -> Plune
  -> Contrato / Clicksign
  -> HUB
```

Separacao de responsabilidades:

- React: telas, formulario, experiencia do usuario.
- FastAPI: endpoints, validacao, leitura do Pipe, persistencia do formulario.
- Banco: estado do formulario e payload operacional.
- Pipedrive: cards/deals, dono do card, etapa/status e rastreabilidade comercial.
- Worker atual: processamento de Plune, contrato, Clicksign e HUB.

## 5. Fronteiras Da Primeira Entrega

Entra no MVP:

- Listar cards/deals do Pipedrive por dono do card.
- Permitir selecionar um card.
- Exibir formulario web para preenchimento dos dados operacionais.
- Salvar rascunho e envio final do formulario.
- Validar obrigatorios no backend.
- Registrar status do formulario por deal.
- Preparar contrato de integracao para o worker consumir os dados depois.

Nao entra no MVP:

- Login completo com usuario/senha.
- Permissoes avancadas por perfil.
- Criacao completa de card no Pipedrive pelo portal.
- Reescrita do worker atual.
- Reescrita das regras Plune/HUB.
- Substituicao imediata de todos os campos customizados do Pipe.
- Form builder dinamico/generico.

## 6. Modelo Conceitual De Dados

Tabela sugerida: `deal_forms`.

Campos conceituais:

- `id`: identificador interno.
- `deal_id`: id do deal/card no Pipedrive.
- `owner_user_id`: id do dono do card no Pipe.
- `owner_name`: nome do dono no momento do preenchimento, para auditoria simples.
- `deal_title`: titulo do deal no momento do preenchimento.
- `status`: `draft`, `submitted`, `validated`, `processing`, `processed`, `error`.
- `schema_version`: versao do formulario, iniciando em `v1`.
- `payload_json`: dados completos preenchidos no portal.
- `validation_errors_json`: erros estruturados quando houver.
- `created_at`, `updated_at`, `submitted_at`.

Regra central:

- O `deal_id` e a chave de integracao entre Pipe, formulario e worker.

## 7. Estrategia De Testes

O repositorio ja possui suíte pytest em `tests/` com `conftest.py`, mocks de banco/API e marker `@pytest.mark.integration` para testes com rede. O portal **nao pode degradar** esse baseline.

### 7.1 Principio: Nada Quebra

Antes de qualquer merge ou deploy de uma fase:

1. Rodar `pytest` completo (sem `-m integration` por padrao).
2. Confirmar que **todos os testes existentes** continuam verdes.
3. Adicionar testes novos **na mesma fase** da funcionalidade, nao depois.
4. So integrar com o `core` quando existir teste de regressao com flag desligada **e** ligada.

Comando de referencia:

```bash
pytest
pytest -m integration   # somente quando ambiente de dev/staging permitir APIs reais
```

### 7.2 Camadas De Teste

| Camada | O que cobre | Quando roda | Ferramenta |
|--------|-------------|-------------|------------|
| **Regressao legado** | Worker, Plune, HUB, contrato, validacoes Pipe | Toda fase, obrigatorio | `pytest` (suite atual) |
| **Unitario API** | Endpoints FastAPI, schemas Pydantic, servicos | Fases 1, 2, 4 | `pytest` + `TestClient` |
| **Unitario persistencia** | `deal_forms`, draft/submit, unicidade | Fase 2 | `pytest` + DB mock ou SQLite de teste |
| **Unitario adaptador** | Merge formulario + deal Pipe, precedencia de campos | Fase 5 | `pytest` + fixtures |
| **Contrato API** | Payload request/response estavel entre React e FastAPI | Fases 1, 3, 4 | `pytest` + snapshots JSON ou schemas compartilhados |
| **Frontend** | Fluxos criticos do formulario (salvar, enviar, erros) | Fase 3+ | Vitest + Testing Library (minimo) |
| **Integracao controlada** | Fluxo portal -> banco -> worker (dev flags) | Fase 5, 6 | `@pytest.mark.integration` + env dev |
| **Smoke pos-deploy** | Health, listagem, um deal de teste | Fase 7 | script manual ou CI |

### 7.3 Baseline De Regressao (nao pode falhar)

Estes modulos ja tem cobertura e representam o coracao da automacao. Qualquer alteracao no `core` exige que continuem passando:

- `tests/test_automacao_contrato_unit.py`
- `tests/test_pipedrive_validations.py`
- `tests/test_pipedrive_fields.py`
- `tests/test_pipedrive_stages.py`
- `tests/test_plune_pedido_unit.py`
- `tests/test_hub_pedido_unit.py`
- `tests/test_fill_contract.py`
- `tests/test_extrair_signatarios.py`
- `tests/test_buscar_deals_etapa_contrato.py`

**Regra:** ao tocar `core/automacao_contrato.py`, `core/pipedrive_validations.py` ou adaptadores, adicionar pelo menos um teste que prova comportamento identico com `FORMULARIO_WEB_ENABLED=false`.

### 7.4 Novos Arquivos De Teste Sugeridos

Criar conforme as fases avancam (nomes indicativos):

- `tests/test_form_api_health.py` — healthcheck e bootstrap da API.
- `tests/test_form_api_pipedrive.py` — listagem de users/deals com mocks.
- `tests/test_form_persistence.py` — CRUD `deal_forms`, status, unicidade.
- `tests/test_form_schema_v1.py` — validacao Pydantic do payload `v1`.
- `tests/test_form_deal_adapter.py` — merge formulario web + deal Pipe.
- `tests/test_form_worker_integration.py` — worker com flag on/off (unitario, sem rede).
- `tests/test_form_regression_legacy.py` — cenarios golden: mesmo deal processado via Pipe-only vs formulario-web.

Frontend (quando existir `frontend/`):

- `frontend/src/__tests__/DealForm.test.tsx` — salvar rascunho, submit, exibir erros.
- `frontend/src/__tests__/DealList.test.tsx` — filtro por dono.

### 7.5 Fixtures E Mocks

Reaproveitar padroes de `tests/conftest.py`:

- `deal_minimo` e fixtures existentes para deals.
- Novas fixtures: `form_payload_v1_minimo`, `form_payload_v1_completo`, `deal_form_record_draft`, `deal_form_record_submitted`.
- Mock de Pipedrive API nos testes de listagem (sem rede).
- Mock de `deal_forms` no adaptador ate a Fase 2 estar pronta.
- Nunca chamar Plune, Clicksign ou HUB em testes unitarios da API do formulario.

### 7.6 Cenarios Golden (obrigatorios na Fase 5)

Antes de ligar `FORMULARIO_WEB_ENABLED` em qualquer ambiente:

1. Capturar um deal de referencia (fixture JSON anonimizado) com payload Pipe completo.
2. Montar payload equivalente no formulario web `v1`.
3. Assertar que o **mesmo contexto** de contrato, signatarios, Plune e HUB e produzido pelo adaptador.
4. Assertar que com flag desligada o worker usa apenas Pipe (comportamento atual).
5. Assertar que deal sem formulario `validated` nao dispara processamento.

### 7.7 Gate De Qualidade Por Fase

Nenhuma fase e considerada concluida sem:

| Gate | Criterio |
|------|----------|
| G0 | Baseline `pytest` verde antes de comecar a fase |
| G1 | Testes novos da fase escritos e verdes |
| G2 | Baseline `pytest` verde depois da fase |
| G3 | Nenhum teste existente removido ou desabilitado sem justificativa documentada |
| G4 | Alteracao no `core` tem teste de flag off + flag on |

### 7.8 CI (quando existir pipeline)

Minimo desejavel:

- Job `pytest` em todo PR que toque `core/`, `tests/` ou codigo do portal.
- Falha do job bloqueia merge.
- Testes `@pytest.mark.integration` em job separado, manual ou nightly, nao no caminho critico do PR.

## 8. Decomposicao Hierarquica

Cada fase inclui bloco **Testes** obrigatorio. Ver secao 7 para camadas, gates e baseline.

### Fase 0 - Especificacao Antes De Codigo ✅ CONCLUÍDA

Objetivo: reduzir risco antes de tocar no `core`.

**Entregáveis:** [`docs/formulario-web/`](formulario-web/README.md) (especificação, matriz, baseline pytest, cenários golden, `schema-v1-map.json`, fixtures em `tests/fixtures/formulario_v1/`).

Tarefas:

- Mapear quais campos continuam no Pipedrive e quais migram para o formulario.
- Definir o schema `v1` do formulario.
- Separar campos por dominio: contrato, cliente, unidades/instalacoes, Plune, HUB, signatarios e observacoes.
- Definir status do formulario e quando o worker pode processar.
- Definir se o MVP lista somente deals em etapa Contrato ou tambem outras etapas.

Testes:

- Rodar `pytest` e registrar baseline verde (screenshot/log de contagem de testes).
- Listar quais testes existentes cobrem cada dominio (contrato, Plune, HUB, Pipe).
- Definir cenarios golden e fixtures JSON anonimizados para a Fase 5.
- Documentar matriz campo a campo: origem Pipe vs formulario vs destino (contrato/Plune/HUB).

Criterios de aceite:

- Existe um documento de campos do formulario `v1`.
- Cada campo tem origem, destino e obrigatoriedade.
- O limite de alteracao no `core` esta descrito antes da implementacao.
- Baseline `pytest` documentado e verde.

### Fase 1 - Backend FastAPI Minimo ✅ CONCLUÍDA

Objetivo: criar a camada web sem mexer no worker.

**Entregáveis:** pacote `portal/` (`main.py`, routers, services, schemas), store em memória, testes `test_form_api_*`. Execução: `uvicorn portal.main:app --reload`.

Tarefas:

- Criar estrutura da API FastAPI.
- Criar endpoint de healthcheck.
- Criar servico de leitura do Pipedrive encapsulado.
- Criar endpoint para listar donos/usuarios do Pipe, se a API atual permitir.
- Criar endpoint para listar cards por `owner_user_id`.
- Criar endpoints para salvar e buscar formulario por `deal_id`.

Testes:

- `tests/test_form_api_health.py`: `GET /health` retorna 200.
- `tests/test_form_api_pipedrive.py`: listagem de users/deals com mock, filtro por `owner_user_id`.
- Testes de endpoints de formulario com mock de persistencia (antes da Fase 2 real).
- Assertar que nenhum endpoint importa ou chama `plune_pedido`, `hub_pedido`, `ClicksignClient`.
- Gate G0 + G1 + G2 da secao 7.7.

Criterios de aceite:

- API sobe localmente.
- API lista cards filtrados por dono.
- API salva e recupera payload de formulario sem acionar Plune, Clicksign ou HUB.
- Testes novos da API passam; suite legada continua verde.

### Fase 2 - Banco Do Formulario ✅ CONCLUÍDA

Objetivo: persistir o estado operacional fora do Pipe.

**Entregáveis:** tabela `deal_forms` (schema v11), `MysqlDealFormRepository`, `POST /forms/{id}/submit`, testes `test_form_persistence.py`. Ver [`fase-2-persistencia.md`](formulario-web/fase-2-persistencia.md).

Tarefas:

- Criar migration ou script controlado para tabela `deal_forms`.
- Garantir unicidade por `deal_id` e `schema_version`, ou regra equivalente.
- Salvar rascunho com status `draft`.
- Salvar envio final com status `submitted`.
- Registrar erros de validacao no banco quando houver.

Testes:

- `tests/test_form_persistence.py`: insert/update draft, submit, unicidade `deal_id` + `schema_version`.
- Teste de transicao de status: `draft` -> `submitted` (e bloqueio de edicao apos submit, se regra assim definir).
- Teste de `validation_errors_json` persistido em envio invalido.
- Fixtures em `conftest.py`: `form_payload_v1_minimo`, `deal_form_record_draft`.
- Gate G0 + G1 + G2.

Criterios de aceite:

- Um deal tem no maximo um formulario ativo por versao.
- O payload pode ser editado enquanto estiver em `draft`.
- O payload enviado fica rastreavel por timestamps.
- Persistencia coberta por testes unitarios sem depender de MySQL real (mock ou DB de teste).

### Fase 3 - Frontend React MVP ✅ CONCLUÍDA

Objetivo: dar ao usuario uma interface que substitua a entrada no Pipe para preenchimento.

**Entregáveis:** `frontend/` (Vite+React), telas dono/cards/formulário, Vitest, `test_form_api_contract.py`. Ver [`fase-3-frontend.md`](formulario-web/fase-3-frontend.md).

Tarefas:

- Criar tela inicial com selecao de dono do card.
- Criar tela "Meus Cards" filtrando por dono.
- Criar tela do formulario do deal.
- Permitir salvar rascunho.
- Permitir enviar formulario.
- Exibir validacoes retornadas pelo backend.

Testes:

- Vitest + Testing Library: listagem filtrada por dono, abertura de formulario, salvar rascunho, submit com sucesso e submit com erro.
- Mock da API no frontend; nao depender de backend rodando nos testes unitarios de UI.
- Teste de contrato: payloads enviados pelo frontend batem com schema esperado pelo backend (JSON fixture compartilhado ou validacao cruzada em `pytest`).
- Gate G2 na suite Python (frontend nao pode ter quebrado nada no back).

Criterios de aceite:

- Usuario escolhe dono e ve somente os cards daquele dono.
- Usuario abre um card e preenche os dados.
- Usuario salva e retoma um rascunho.
- Usuario envia o formulario e recebe feedback claro.
- Testes de UI cobrem os quatro fluxos acima.

### Fase 4 - Validacao De Dominio ✅ CONCLUÍDA

Objetivo: mover as validacoes obrigatorias para perto do backend, sem duplicar regra de forma descontrolada.

Tarefas:

- Criar schema Pydantic do formulario `v1`.
- Validar obrigatorios por tipo de servico.
- Validar dados necessarios para contrato.
- Validar dados necessarios para Plune.
- Validar dados necessarios para HUB.
- Reaproveitar validacoes existentes quando fizer sentido, sem acoplar endpoint web diretamente ao loop do worker.

Testes:

- `tests/test_form_schema_v1.py`: obrigatorios, tipos, regras por servico (SOLE Web, ACL, usina, etc.).
- Reutilizar ou espelhar casos de `tests/test_pipedrive_validations.py` para o payload do formulario — mesma regra de negocio, entrada diferente.
- Teste: envio incompleto retorna 422 (ou equivalente) com `validation_errors_json` estruturado.
- Teste: payload completo valido transiciona para `validated`.
- Nao duplicar logica: preferir funcoes compartilhadas testadas uma vez, consumidas pela API e pelo worker.
- Gate G0 + G1 + G2.

Criterios de aceite:

- O backend rejeita envio incompleto com erros estruturados.
- O frontend consegue destacar campos com erro.
- O worker nao precisa lidar com formulario obviamente incompleto.
- Validacoes do formulario tem paridade testada com regras ja cobertas em `test_pipedrive_validations`.

### Fase 5 - Integracao Controlada Com O Worker ✅ CONCLUÍDA

Objetivo: fazer o worker consumir dados do formulario com o menor risco possivel.

Tarefas:

- Criar uma funcao/adaptador de leitura do formulario por `deal_id`.
- Definir precedencia: formulario web > Pipedrive para campos migrados.
- Manter Pipedrive como origem para dados do card, dono, etapa e identificadores.
- Alterar o worker apenas nos pontos onde monta contexto/validacoes.
- Proteger a integracao com flag de ambiente, por exemplo `FORMULARIO_WEB_ENABLED`.
- Nao remover campos antigos do Pipedrive nesta fase.

Testes (fase mais critica — maximo cuidado):

- `tests/test_form_deal_adapter.py`: merge formulario + deal, precedencia web > Pipe para campos migrados.
- `tests/test_form_worker_integration.py`: worker com `FORMULARIO_WEB_ENABLED=false` — comportamento identico ao atual (regressao).
- Mesmo arquivo: worker com `FORMULARIO_WEB_ENABLED=true` e formulario `validated` — usa payload web.
- `tests/test_form_regression_legacy.py`: cenarios golden da secao 7.6.
- Assertar idempotencia: deal ja em `deals_processed` nao reprocessa.
- Assertar que deal sem formulario `validated` nao chama Plune/contrato/HUB.
- Rodar suite completa `pytest` duas vezes: flag off e flag on (via `monkeypatch`/`patch` em env).
- Gate G4 obrigatorio antes de qualquer teste em ambiente compartilhado.

Criterios de aceite:

- Com a flag desligada, o worker se comporta como antes.
- Com a flag ligada, o worker busca payload do formulario para campos migrados.
- Deal sem formulario validado nao avanca para Plune/contrato/HUB.
- Erros sao registrados sem duplicar processamento.
- **100% dos testes legados passam com flag desligada.**
- Cenarios golden passam com flag ligada.

### Fase 6 - Fluxo Operacional

Objetivo: tornar o processo utilizavel no dia a dia.

Tarefas:

- Definir qual etapa do Pipe aparece no portal.
- Definir quando um card esta "pronto para formulario".
- Definir quando um card esta "pronto para automacao".
- Registrar no Pipe uma nota ou status minimo indicando que o formulario foi enviado, se necessario.
- Criar orientacao operacional para usuarios.

Testes:

- `@pytest.mark.integration`: fluxo ponta a ponta em dev — selecionar dono, preencher formulario, submit, worker processa com flags de dev (`DEV_PULAR_CLICKSIGN`, etc.).
- Checklist manual documentado: cards pendentes vs enviados vs processados.
- Smoke: portal fora do ar nao impede worker legado de rodar (flag off).

Criterios de aceite:

- Usuario nao precisa abrir o Pipe para preencher dados.
- Time consegue identificar cards pendentes e enviados.
- Automacao so processa cards prontos.
- Pelo menos um teste de integracao documentado (mesmo que rode so em dev).

### Fase 7 - Hardening E Producao

Objetivo: preparar para producao sem expandir demais o escopo. Testes unitarios ja devem existir das fases anteriores; aqui consolidamos observabilidade, CI e rollback.

Tarefas:

- Definir protecao minima de acesso ao portal.
- Adicionar logs estruturados no backend.
- Configurar CI: `pytest` obrigatorio em PR.
- Documentar rollback (`FORMULARIO_WEB_ENABLED=false`).
- Documentar variaveis de ambiente novas.
- Opcional: `pytest-cov` com meta minima nas areas novas (API, adaptador, persistencia).

Testes:

- Smoke pos-deploy: health, listagem, um deal de teste.
- Teste de rollback: desligar flag e confirmar regressao em menos de 5 min (suite + smoke).
- Revisar que nenhum teste foi `@pytest.mark.skip` sem issue rastreavel.
- Rodar `pytest -m integration` uma vez em staging antes de producao.

Criterios de aceite:

- Falha no portal nao quebra worker legado.
- Falha no Pipe nao apaga formularios.
- Rollback volta o worker para comportamento anterior via flag.
- CI bloqueia merge com testes vermelhos.
- Cobertura documentada das areas criticas (adaptador + validacao + persistencia).

## 9. Grafo De Dependencias

```text
Fase 0
  -> Fase 1
  -> Fase 2
  -> Fase 3
  -> Fase 4
  -> Fase 5
  -> Fase 6
  -> Fase 7
```

Paralelizavel depois da Fase 0:

- Backend FastAPI e frontend React podem evoluir em paralelo depois dos contratos de API.
- Schema do formulario e layout visual podem evoluir em paralelo, desde que a versao `v1` seja respeitada.
- Hardening pode comecar antes da integracao final, mas nao deve bloquear o prototipo local.
- **Testes de cada fase sao prerequisito da fase seguinte** (gate G2).

## 10. Pontos De Cuidado No `core`

O `core` atual concentra regras sensiveis da automacao. A implementacao deve evitar alteracoes amplas e diretas.

Regras de seguranca tecnica:

- Nao reescrever `core/automacao_contrato.py` de uma vez.
- Criar adaptadores pequenos para ler dados do formulario.
- Manter compatibilidade por flag ate o fluxo novo estar validado.
- Preservar idempotencia de `deals_processed` e `envelopes_pending`.
- Nao acionar Plune, Clicksign ou HUB a partir do frontend.
- Nao colocar regra de negocio critica somente no React.
- Validacao decisiva deve ficar no backend/worker.
- **Toda alteracao no `core` exige teste de regressao com flag off antes do merge.**

## 11. Contrato Inicial De API

Endpoints conceituais para o MVP:

- `GET /health`: verifica se a API esta online.
- `GET /pipedrive/users`: lista donos disponiveis para filtro.
- `GET /pipedrive/deals?owner_user_id={id}`: lista cards do dono.
- `GET /forms/{deal_id}`: recupera formulario salvo.
- `PUT /forms/{deal_id}/draft`: salva rascunho.
- `POST /forms/{deal_id}/submit`: envia formulario para validacao.
- `GET /forms/{deal_id}/status`: consulta status do formulario.

Esses nomes podem mudar na implementacao, mas o contrato funcional deve permanecer simples.

Cada endpoint deve ter pelo menos um teste em `tests/test_form_api_*.py` antes de ser considerado estavel.

## 12. Agentes E Skills Sugeridos Para Execucao Futura

Nao criar agentes ou skills nesta task. Por enquanto, este arquivo e suficiente.

Se a implementacao for dividida entre agentes depois, a sugestao e:

- Agente de contexto readonly: mapear os pontos exatos do `core` que montam dados do contrato, Plune e HUB.
- Agente backend: criar FastAPI, endpoints e persistencia.
- Agente frontend: criar React MVP.
- Agente de integracao: conectar worker ao payload do formulario com flag.
- Agente de revisao: revisar riscos de idempotencia, seguranca e regressao no `core`.
- Agente de testes: garantir gates G0–G4 e cenarios golden antes de merge na Fase 5.

Uma skill local so deve ser criada depois que o fluxo estiver estavel e repetivel, por exemplo `gebras-formulario-web`, documentando como trabalhar no portal sem quebrar o worker e como rodar a suíte de regressao.

## 13. Ordem Recomendada Das Proximas Tasks

1. Rodar `pytest` e documentar baseline verde (Fase 0).
2. Criar documento de campos do formulario `v1` + fixtures golden.
3. Criar desenho de endpoints e payloads.
4. Implementar backend FastAPI minimo + `test_form_api_*`.
5. Implementar banco do formulario + `test_form_persistence`.
6. Implementar frontend React MVP + testes Vitest.
7. Adicionar validacoes backend + `test_form_schema_v1` (paridade com `test_pipedrive_validations`).
8. Integrar worker por adaptador e flag + `test_form_deal_adapter` + `test_form_regression_legacy`.
9. Teste de integracao em dev (`@pytest.mark.integration`).
10. CI com `pytest` obrigatorio em PR.
11. Decidir estrategia de protecao de acesso antes de producao.

## 14. Definicao De Pronto Da Iniciativa

A iniciativa pode ser considerada pronta quando:

- O usuario preenche os dados pelo portal sem entrar no Pipe.
- Cards sao filtrados por dono.
- O formulario salva rascunho e envio final.
- O backend valida dados obrigatorios.
- O worker processa usando dados do formulario quando a flag esta ligada.
- O fluxo antigo ainda pode ser usado como rollback.
- Plune, contrato, Clicksign e HUB nao sao acionados de forma duplicada.
- **Suite `pytest` legada 100% verde com `FORMULARIO_WEB_ENABLED=false`.**
- **Cenarios golden passam com flag ligada.**
- **Todo endpoint e adaptador novo tem teste unitario.**
- **CI bloqueia merge com regressao.**

