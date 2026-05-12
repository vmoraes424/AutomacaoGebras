---
name: gebras-automacao-contratos
description: Orients changes and answers architecture questions for the Gebras contract automation (Pipedrive won deals → docxtpl Word from contrato_padrao.docx → Clicksign API v3 sequential signing). Use when working in AutomacaoGebras, editing automacao_contrato.py or criar_webhook.py, ENTENDIMENTO_SISTEMA.md, contrato_padrao.docx placeholders, deals_processados.txt, contratos/ output, Pipedrive custom field hashes, or Clicksign webhooks and envelopes.
disable-model-invocation: true
---

# Automação Gebras — contratos (Pipedrive → Clicksign)

## Primeiro passo

Para **entendimento do sistema**, **contexto de negócio** e **lista de artefatos**, leia o arquivo na raiz do repositório: [ENTENDIMENTO_SISTEMA.md](../../../ENTENDIMENTO_SISTEMA.md). Este skill resume o que o agente precisa para não quebrar o fluxo; o `.md` é a fonte narrativa completa.

## Contrato mental (o que não confundir)

- **Gatilho**: deal **ganho** no Pipedrive, com `won_time` **posterior** ao instante em que `automacao_contrato.py` foi iniciado (corte em UTC no arranque do script).
- **Estado local**: `deals_processados.txt` evita reprocessar o mesmo deal após envio bem-sucedido ao Clicksign.
- **Modelo**: `contrato_padrao.docx` + **docxtpl**; placeholders devem bater com o dicionário montado em `fill_contract()`.
- **CRM**: mapeamento de dados é por **hash de custom field** do Pipedrive no código — alterar campo no CRM sem atualizar o hash quebra o preenchimento.
- **Assinatura**: signatários vêm de custom fields, em **ordem fixa** (Coordenador Principal → Contato Principal → Gestor Gebras → Diretor Principal). Grupos Clicksign = sequência 1, 2, 3…
- **Sem e-mail de signatário**: contrato pode ser gerado em `contratos/` mas **não** vai ao Clicksign; o deal **não** entra em `deals_processados.txt` (permite nova tentativa após corrigir o CRM).

## Arquivos que costumam mudar juntos

| Objetivo | Onde olhar |
|----------|------------|
| Novo dado no contrato | `fill_contract()` + placeholders em `contrato_padrao.docx` |
| Novo signatário ou ordem | `extrair_signatarios()` + campos no Pipedrive |
| API / envelope / requisitos | `ClicksignClient`, `clicksign_fire_and_forget()` |
| Polling / filtros de deal | `processar_deals_pendentes()`, constantes no topo do script |
| Eventos pós-assinatura (só registro do webhook) | `criar_webhook.py` — processamento do callback não está neste repo |

## Segurança e operação

- Não introduzir **segredos** no repositório; preferir variáveis de ambiente ou cofre. Tratar tokens existentes como sensíveis ao revisar diffs.
- Intervalo real de polling = `INTERVALO_POLLING_SEGUNDOS` (comentários no arquivo podem estar desatualizados).

## Execução (referência rápida)

- Automação contínua: `python automacao_contrato.py`
- Registrar webhook Clicksign: `python criar_webhook.py`

## Atualizar documentação

Se o comportamento do sistema mudar de forma relevante, alinhar **código** e [ENTENDIMENTO_SISTEMA.md](../../../ENTENDIMENTO_SISTEMA.md) para não divergirem.
