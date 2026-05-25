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
# Venda.TipoContrato (Browse) — pedidos automáticos (sem fallback para outro tipo)
PLUNE_TIPO_CONTRATO_IMPLANTACAO_ID = "1"  # IMPLANTAÇÃO
# Recorrente por serviço (maior quantidade de UCs no Pipedrive vence)
PLUNE_TIPO_CONTRATO_USINA_RECORRENTE_ID = "49"  # GESTÃO DE USINA FOTOVOLTAICA recorrente
PLUNE_TIPO_CONTRATO_QUALIDADE_RECORRENTE_ID = "48"  # GESTÃO DA QUALIDADE DE ENERGIA recorrente
PLUNE_TIPO_CONTRATO_MERCADO_LIVRE_RECORRENTE_ID = "41"  # MERCADO LIVRE DE ENERGIA recorrente
PLUNE_TIPO_CONTRATO_SOLE_RECORRENTE_ID = "4"  # SOLE recorrente (SOLE Web / Sole Consultoria)
PLUNE_CENTRO_CUSTO_ID = "5"
PLUNE_PRODUTO_SOLE_ID = "5584"
PLUNE_PARCEIRO_TIPO = "fornecedor"
PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID = "31"
PLUNE_STATUS_PEDIDO_RECORRENTE_ID = "33"
PLUNE_FRETE_POR_CONTA = "9"
# Faturamento | NF Série (Venda.Pedido.Serie): 0 = NFS-e, 1 = NFSe
# Valor por filial em branch_config.pedido_serie (MySQL); fallback global:
PLUNE_PEDIDO_SERIE = "0"
# Modelo fiscal (Venda.Pedido.ModeloId) — par válido com série em Venda.NotaConfig por filial:
# Matriz 751: série 1 + modelo 01 (NFSe); ISM 790: série 0 + modelo 01 (NFS-e).
PLUNE_PEDIDO_MODELO_ID = "01"
# Comissão pedido recorrente: ValorComissao = PLUNE_COMISSAO_MESES_ANUAL × valor do pedido
PLUNE_COMISSAO_MESES_ANUAL = 12

# --- Automação (paths e polling) ---
INTERVALO_POLLING_SEGUNDOS = 30
# Margem antes do arranque: ganhos nesse intervalo ainda entram no corte (evita perder deal ganho segundos antes do script subir)
CORTE_TEMPORAL_GRACE_MINUTOS = 15
MODELO_DOCX = "contrato_padrao.docx"
PASTA_SAIDA = "contratos"
ARQUIVO_AVISOS_APROVACAO_PLUNE = "runtime/state/avisos_aprovacao_plune.txt"

# --- Clicksign ---
CLICKSIGN_BASE_URL = "https://app.clicksign.com/api/v3"
CLICKSIGN_RATE_LIMIT_MAX_RETRIES = 12
CLICKSIGN_RATE_LIMIT_BUFFER_SEC = 1
