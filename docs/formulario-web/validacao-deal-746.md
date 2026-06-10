# Validação API Pipedrive — deal 746

Consulta realizada em **10/06/2026** via `GET /api/v1/deals/746` e `GET /api/v2/deals/746` (token do `.env` local).

## Resumo do card

| Campo | Valor |
|-------|-------|
| `id` | 746 |
| `title` | Biview |
| `status` | `open` |
| `pipeline_id` | 1 |
| `stage_id` | 7 |
| Etapa Contrato? | **Sim** (`deal_esta_em_etapa_contrato` = true) |
| `owner_id` (v2) | **24587114** |
| `owner_id` (v1) | `null` ⚠️ |
| Custom fields preenchidos | **30** (todos os slots do Pipe) |

## Conclusões para o portal

1. **Schema v1 cobre os 30 campos** — o deal 746 usa exatamente o conjunto mapeado em `matriz-campos-v1.md` + `Observações (Detalhes)` (opcional no ganho, presente neste deal para HUB).
2. **Filtro por dono:** usar **API v2** (`owner_id`); a resposta v1 deste deal não traz `owner_id`.
3. **Listagem MVP:** deal 746 está em etapa **Contrato** e `open` — alinhado à decisão da Fase 0.
4. **Enums no raw:** hashes podem vir como id (`"56"`, `"50"`) em `custom_fields`; `get_val` / `get_enum_label` resolvem para rótulo (`Iribarrem San Martin`, `20%`). O adaptador form→deal deve gravar no formato que `get_val` já entende.
5. **E-mails signatários set:** no raw, consultor/coordenador/diretor vêm como ids de opção (`87`, `91`, `92`); `get_val` resolve para o e-mail. O formulário web pode usar e-mails diretos; o adaptador deve popular o hash corretamente.

## Amostra de valores (deal 746 — referência estrutural)

Valores reais omitidos onde há PII; estrutura confirmada na API.

| Domínio | Exemplo confirmado |
|---------|-------------------|
| Cliente | Contratante texto, CNPJ 14 dígitos, CEP 8 dígitos, Pelotas/RS |
| Código cliente/inst. | `352/1234,3456` → cliente 352, inst. [1234, 3456] |
| Serviços UC | SOLE Web 4, Consultoria 6, ACL 6, Usina 7, Qualidade 5, Qtd UC's 4 |
| Valores | Recorrência 1800, Implantação 5000 |
| Datas | Implantação 2026-02-24, 1ª cobrança 2026-02-27 |
| Comercial | Filial ISM, Regional1, consultor por nome |
| HUB obs | `UC = … - SOLE WEB + Gestão ACL … = 7.200,00; UC = …` (2 blocos) |

## Compatibilidade com fixtures golden

O fixture `form_payload_v1_g1.json` é **estruturalmente equivalente** ao deal 746 (mesmos grupos de campo e regras), com dados **anonimizados**. Recomendação Fase 5: adicionar fixture opcional `deal_pipe_746_anon.json` derivado desta validação para teste de paridade.

## Script de consulta

`scripts/fetch_deal_pipe.py 746` — imprime resumo na stdout (não grava PII em arquivo).
