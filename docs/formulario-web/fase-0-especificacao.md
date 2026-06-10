# Fase 0 — Especificação antes de código

Documento de saída da Fase 0 do portal web. Nenhum código de produção do portal foi alterado; apenas especificação, fixtures e baseline de testes.

## 1. Resumo das decisões

| Tema | Decisão |
|------|---------|
| Interface do usuário | Portal React; usuário **não** entra no Pipe para preencher |
| Backend | FastAPI reutilizando módulos `core/*` |
| Login MVP | Sem login nominal; ambiente controlado (rede interna / token depois) |
| Fonte dos dados operacionais | Formulário web (`deal_forms.payload_json`) |
| Pipe no MVP | Metadados do card: `id`, `title`, `owner_id`, `stage_id`, `status`, anexo Proposta Comercial |
| Listagem no portal | Deals **abertos** na etapa **Contrato**, filtrados por `owner_id` |
| Worker | Continua em loop; consome formulário quando `FORMULARIO_WEB_ENABLED=true` |
| Rollback | Flag desligada = comportamento atual (dados só no Pipe) |

## 2. Schema do formulário v1

Versão: `schema_version: "v1"`.

O payload usa **chaves legíveis** (snake_case). O adaptador na Fase 5 converte para o formato `deal` com `custom_fields` (hashes) que o `core` já entende.

### 2.1 Estrutura JSON

```json
{
  "schema_version": "v1",
  "cliente": { },
  "servicos": { },
  "valores": { },
  "datas": { },
  "comercial": { },
  "signatarios": { },
  "hub": { },
  "anexos": { }
}
```

### 2.2 Seções e campos

#### `cliente`

| Campo JSON | Tipo | Obrigatório | Equivalente Pipe |
|------------|------|-------------|------------------|
| `contratante` | string | sim | Contratante |
| `documento` | string | sim | CPF/CNPJ |
| `endereco` | string | sim | Endereço |
| `cep` | string | sim | CEP (8 dígitos) |
| `municipio_estado` | string | sim | Município/Estado |
| `inscricao_estadual` | string | sim | Inscrição Estadual |
| `inscricao_municipal` | string | sim | Inscrição Municipal |
| `notas` | string | sim | Notas |
| `codigo_cliente_instalacao` | string | sim | Código Cliente/Código da Instalação |

#### `servicos` (quantidades UC; 0 se não contratar)

| Campo JSON | Tipo | Obrigatório | Equivalente Pipe |
|------------|------|-------------|------------------|
| `sole_web` | number | sim | SOLE Web |
| `sole_consultoria` | number | sim | Sole Consultoria |
| `gestao_acl` | number | sim | Gestão ACL |
| `gestao_usina_fotovoltaica` | number | sim | Gestão Usina Fotovoltaica |
| `gestao_qualidade_energia` | number | sim | Gestão da Qualidade de Energia |
| `quantidade_ucs` | number | sim | Quantidade de UC's |

Regra: pelo menos um serviço com quantidade **> 0** (mesma regra de `validar_deal_para_automacao`).

#### `valores`

| Campo JSON | Tipo | Obrigatório | Equivalente Pipe |
|------------|------|-------------|------------------|
| `valor_recorrencia` | string/number | sim | Valor Recorrência (> 1) |
| `valor_implantacao` | string/number | sim | Valor de Implantação (0 permitido) |

#### `datas`

| Campo JSON | Tipo | Obrigatório | Condição |
|------------|------|-------------|----------|
| `data_pagamento_implantacao` | date (ISO ou BR) | condicional | Obrigatório se `valor_implantacao` > 1 |
| `data_primeira_cobranca` | date | sim | Data primeira cobrança mensal |

#### `comercial`

| Campo JSON | Tipo | Obrigatório | Equivalente Pipe |
|------------|------|-------------|------------------|
| `filial` | string (rótulo enum) | sim | Filial → BranchId Plune |
| `regional` | string | sim | Regional → SubCentro 2 |
| `consultor` | string | sim | Consultor → SubCentro 3 |
| `percentual_exito` | string | sim | Porcentagem de Exito |

#### `signatarios`

| Campo JSON | Tipo | Obrigatório | Papel Clicksign |
|------------|------|-------------|-----------------|
| `email_assinante_contrato` | email | sim | Cliente (grupo 3) |
| `email_consultor_gebras` | email | sim | Consultor (grupo 1) |
| `email_coordenador_gebras` | email | sim | Coordenador (grupo 2) |
| `email_diretor_gebras` | email | sim | Diretor (grupo 4) |
| `email_financeiro_contratante` | email | sim | Contrato (contato financeiro) |
| `email_gestor_contratante` | email | sim | Plune parceiro / contrato |

#### `hub`

| Campo JSON | Tipo | Obrigatório | Uso |
|------------|------|-------------|-----|
| `observacoes_detalhes` | string | não no submit inicial* | Blocos `UC = ...` para HUB |

\* Opcional na validação do ganho (`CAMPOS_CONTRATO_OPCIONAIS`), **obrigatório** para criar pedido HUB se parceiro já existia no Plune. O portal deve orientar o usuário a preencher quando HUB for esperado.

Formato dos blocos (ver `docs/Hub/Mapeamento-Pipedrive.md`):

```text
UC = 00665 - SOLE WEB + Gestão ACL - Mercado Livre de Energia = 1.500,92; UC = 01942 - ACL + Sole Consultoria = 454.564,00
```

#### `anexos`

| Campo JSON | Tipo | Obrigatório | Observação |
|------------|------|-------------|------------|
| `proposta_comercial_anexada` | boolean | informativo | Anexo continua no **deal do Pipe** no MVP; portal só indica se existe |

No MVP o upload da Proposta Comercial **não** migra para o portal; o worker continua verificando anexo no Pipe (`tem_arquivo_proposta_comercial`). Evolução futura: upload via API Pipe pelo backend do portal.

### 2.3 Campos que permanecem só no Pipedrive

| Campo / dado | Motivo |
|--------------|--------|
| `id`, `title` | Identidade do card |
| `owner_id` | Dono do card (filtro no portal) |
| `pipeline_id`, `stage_id`, `status` | Funil e etapa |
| `update_time` | Polling do worker |
| Arquivo **Proposta Comercial** | Anexo nativo do CRM no MVP |
| `won_time` | Preenchido pela automação pós-assinatura |

## 3. Status do formulário e gatilho do worker

### 3.1 Máquina de estados

```text
draft → submitted → validated → processing → processed
                    ↘ error ↗
```

| Status | Significado |
|--------|-------------|
| `draft` | Rascunho editável no portal |
| `submitted` | Usuário enviou; API validando |
| `validated` | Passou validação backend; **worker pode processar** |
| `processing` | Worker assumiu o deal |
| `processed` | Plune/contrato/Clicksign/HUB concluídos (ou fluxo dev equivalente) |
| `error` | Validação ou processamento falhou; mensagens em `validation_errors_json` |

### 3.2 Quando o worker processa

| Modo | Condição |
|------|----------|
| **Legado** (`FORMULARIO_WEB_ENABLED=false`) | Deal aberto em etapa Contrato + `validar_deal_para_automacao(deal)` OK + demais regras atuais |
| **Portal** (`FORMULARIO_WEB_ENABLED=true`) | Mesmas condições de etapa/status do deal **e** formulário com status `validated` **e** adaptador monta `deal` equivalente ao validado |

Deal **sem** formulário `validated` não avança para Plune/contrato/HUB no modo portal.

### 3.3 Listagem no portal (MVP)

- **Etapa:** somente **Contrato** (`deal_esta_em_etapa_contrato`), alinhado a `buscar_deals_etapa_contrato()`.
- **Status do deal:** `open`.
- **Filtro:** `owner_id` selecionado na UI (sem login: dropdown de usuários Pipe).
- **Não listar** no MVP: Negociação, ganhos, perdidos (evita escopo e confusão).

## 4. Limites de alteração no `core` (antes da Fase 5)

### 4.1 Não alterar na Fase 1–4

- `core/automacao_contrato.py` — loop principal
- `core/plune_pedido.py` — regras de pedido
- `core/hub_pedido.py` — regras HUB
- `core/pipedrive_validations.py` — lógica de validação (extrair funções compartilhadas na Fase 4 se necessário, sem mudar comportamento)

### 4.2 Alterações permitidas na Fase 5 (mínimas)

| Arquivo | Alteração |
|---------|-----------|
| Novo `core/form_deal_adapter.py` | Lê `deal_forms`, merge com deal Pipe, expõe `deal` unificado |
| `core/automacao_contrato.py` | Pontos de leitura de deal: chamar adaptador se flag ligada; **sem** reescrever loop |
| `core/config.py` | `FORMULARIO_WEB_ENABLED` |
| `core/database.py` | Funções CRUD `deal_forms` (ou módulo `core/form_persistence.py`) |

### 4.3 Contrato do adaptador (Fase 5)

```python
def deal_para_automacao(deal_id: str, deal_pipe: dict) -> dict:
    """
    Se FORMULARIO_WEB_ENABLED e form validated: merge campos migrados do payload v1
    sobre custom_fields do deal_pipe.
    Senão: retorna deal_pipe inalterado.
    """
```

Precedência: **formulário web > Pipedrive** para campos migrados; metadados do card sempre do Pipe.

## 5. Critérios de aceite da Fase 0

| Critério | Artefato |
|----------|----------|
| Documento de campos v1 | Este arquivo + [matriz-campos-v1.md](matriz-campos-v1.md) |
| Origem, destino, obrigatoriedade | Matriz |
| Limite no `core` | Seção 4 acima |
| Baseline pytest | [baseline-pytest.md](baseline-pytest.md) |
| Cenários golden | [cenarios-golden.md](cenarios-golden.md) + `tests/fixtures/formulario_v1/` |

## 6. Próximo passo

**Fase 1:** backend FastAPI mínimo (`GET /health`, listagem Pipe, CRUD rascunho) **sem** tocar no worker.
