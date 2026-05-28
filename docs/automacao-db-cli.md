# CLI MySQL `gebras_automacao`

Referência dos comandos para estado e catálogo da automação (dev e produção).

Script: `scripts/automacao_db.py`  
Conexão: variáveis `MYSQL_*` no `.env` (database padrão: `gebras_automacao`)

```powershell
cd "c:\Users\Pedro\Desktop\Gebras\Gebras-Pipe\AutomacaoGebras"
```

```bash
cd /caminho/AutomacaoGebras
```

---

## Visão geral

```bash
python scripts/automacao_db.py status
```

Mostra `MYSQL_HOST:porta/database` e contagens das tabelas.

---

## Consultar um deal

```bash
python scripts/automacao_db.py show 746
```

---

## Listar registros

```bash
python scripts/automacao_db.py list deals
python scripts/automacao_db.py list legado
python scripts/automacao_db.py list envelopes
python scripts/automacao_db.py list pedidos
python scripts/automacao_db.py list pedidos --deal-id 746
python scripts/automacao_db.py list deals --limit 50
```

---

## Remover estado (reprocessar deal)

Não altera catálogo (`pipedrive_filial`, `branch_config`, `plune_subcentro`).

Para cada deal, antes de apagar linhas em `gebras_automacao`, o comando tenta **remover o pedido no HUB** (`MYSQL_DATABASE_HUB`) se `hub_pedido_criado=1` no envelope (pedido criado pela automação). Não remove pedidos no Plune. Ver [`docs/Hub/Integracao-AutomacaoGebras.md`](Hub/Integracao-AutomacaoGebras.md).

```bash
python scripts/automacao_db.py rm deal 746
python scripts/automacao_db.py rm deal 746 -y
python scripts/automacao_db.py rm estado
python scripts/automacao_db.py rm estado -y
```

---

## Catálogo Plune / filiais

```bash
python scripts/automacao_db.py catalogo
```

---

## Sincronizar catálogo (subcentros via API Plune)

```bash
python scripts/automacao_db.py sync
python scripts/automacao_db.py sync --sem-plune
```

Atalho: `python scripts/atualizar_db.py`

---

## Ajuda

```bash
python scripts/automacao_db.py --help
```

---

## Tabelas

| Tabela | Uso |
|--------|-----|
| `deals_processed` | Deal ganho já processado |
| `deals_legacy_block` | Bloqueio formato antigo |
| `envelopes_pending` | Envelope Clicksign / flags Plune |
| `pedidos_plune_keys` | Chaves PedidoIntegracao |
| `pipedrive_filial` | Filial Pipedrive → branch |
| `branch_config` | Parâmetros por filial |
| `plune_subcentro` | Regional / subcentro nível 3 |

Comandos `rm` atuam apenas nas quatro primeiras.

---

## Cuidados

1. Parar o polling antes de `rm` em produção, se possível.
2. Limpar o MySQL não remove pedidos no Plune (`PedidoIntegracao` na API).
3. RDS: Security Group deve liberar porta `3306` para o host da automação.

---

## Exemplo — dev, reprocessar deal 746

```bash
python scripts/automacao_db.py show 746
python scripts/automacao_db.py rm deal 746 -y
python scripts/automacao_db.py status
```
