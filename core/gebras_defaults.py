"""
Configuração fixa Gebras (Plune / Pipedrive) — não vai no .env.

Altere aqui IDs estáveis de negócio. Mapeamentos dinâmicos (subcentros nível 2/3)
e estado da automação ficam no MySQL (database `gebras_automacao`, ver `.env`).
"""

# --- Plune: empresa e URLs ---
PLUNE_BASE_URL = "https://www-gebras.plune.com.br"
PLUNE_COMPANY_ID = "869"

# Filial Pipedrive -> Branch, parâmetros por filial e subcentros: MySQL (gebras_automacao)
# (seed na 1ª conexão em core/database.py; alterações via CLI automacao_db)

# --- Pedido Plune (valores padrão Sole / Gebras) ---
PLUNE_TIPO_OP_ID = "20"
PLUNE_STATUS_PEDIDO = "32"
PLUNE_TIPO_CONTRATO_ID = "3"
PLUNE_CENTRO_CUSTO_ID = "5"
PLUNE_PRODUTO_SOLE_ID = "5584"
PLUNE_PARCEIRO_TIPO = "fornecedor"
PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID = "31"
PLUNE_STATUS_PEDIDO_RECORRENTE_ID = "33"
PLUNE_FRETE_POR_CONTA = "9"

# --- Automação (paths e polling) ---
INTERVALO_POLLING_SEGUNDOS = 30
MODELO_DOCX = "contrato_padrao.docx"
PASTA_SAIDA = "contratos"
ARQUIVO_AVISOS_APROVACAO_PLUNE = "runtime/state/avisos_aprovacao_plune.txt"

# --- Clicksign ---
CLICKSIGN_BASE_URL = "https://app.clicksign.com/api/v3"
CLICKSIGN_RATE_LIMIT_MAX_RETRIES = 12
CLICKSIGN_RATE_LIMIT_BUFFER_SEC = 1
