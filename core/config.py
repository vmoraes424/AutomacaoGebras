"""
Configuração central — lê variáveis do arquivo .env (python-dotenv).
Edite .env na raiz do projeto; config.py expõe as constantes para o resto do código.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_bool(key: str, default: bool = False) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "sim", "on")


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or not raw.strip():
        return default
    return int(raw.strip())


def _env_json(key: str, default):
    raw = os.environ.get(key)
    if raw is None or not raw.strip():
        return default
    return json.loads(raw)


def _env_path(key: str, default: str) -> str:
    raw = _env(key, default)
    path = Path(raw)
    if not path.is_absolute():
        path = _ROOT / path
    return str(path)


def _env_path_with_legacy(key: str, default: str, legacy_default: str) -> str:
    raw = os.environ.get(key)
    if raw and raw.strip():
        return _env_path(key, default)
    legacy_path = _ROOT / legacy_default
    if legacy_path.exists():
        return str(legacy_path)
    return str(_ROOT / default)


# --- Pipedrive ---
PIPEDRIVE_API_TOKEN = _env("PIPEDRIVE_API_TOKEN")

# --- Clicksign (token válido: o que estava em criar_webhook.py) ---
CLICKSIGN_ACCESS_TOKEN = _env("CLICKSIGN_ACCESS_TOKEN")
CLICKSIGN_BASE_URL = _env("CLICKSIGN_BASE_URL", "https://app.clicksign.com/api/v3")
CLICKSIGN_WEBHOOK_URL = _env("CLICKSIGN_WEBHOOK_URL")
CLICKSIGN_RATE_LIMIT_MAX_RETRIES = _env_int("CLICKSIGN_RATE_LIMIT_MAX_RETRIES", 12)
CLICKSIGN_RATE_LIMIT_BUFFER_SEC = _env_int("CLICKSIGN_RATE_LIMIT_BUFFER_SEC", 1)
# Desenvolvimento: não envia contrato à API Clicksign (evita rate limit / espera longa).
DEV_PULAR_CLICKSIGN = _env_bool("DEV_PULAR_CLICKSIGN", False)

# --- Plune ---
PLUNE_BASE_URL = _env("PLUNE_BASE_URL", "https://www-gebras.plune.com.br")
PLUNE_AUTH_TOKEN = _env("PLUNE_AUTH_TOKEN")
PLUNE_COMPANY_ID = _env("PLUNE_COMPANY_ID", "869")
PLUNE_BRANCH_ID = _env("PLUNE_BRANCH_ID", "751")   # Matriz
PLUNE_TIPO_OP_ID = _env("PLUNE_TIPO_OP_ID", "20")  # Tipo de Operação NF (padrão pedidos Sole)
PLUNE_STATUS_PEDIDO = _env("PLUNE_STATUS_PEDIDO", "32")
PLUNE_TIPO_CONTRATO_ID = _env("PLUNE_TIPO_CONTRATO_ID", "3")
PLUNE_CENTRO_CUSTO_ID = _env("PLUNE_CENTRO_CUSTO_ID", "5")
PLUNE_SUBCENTRO_CUSTO_ID = _env("PLUNE_SUBCENTRO_CUSTO_ID")
PLUNE_PRODUTO_SOLE_ID = _env("PLUNE_PRODUTO_SOLE_ID", "5584")
PLUNE_PARCEIRO_TIPO = _env("PLUNE_PARCEIRO_TIPO", "cliente").lower()
PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID = _env("PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID", "31")
PLUNE_STATUS_PEDIDO_RECORRENTE_ID = _env("PLUNE_STATUS_PEDIDO_RECORRENTE_ID", "33")
PLUNE_FRETE_POR_CONTA = _env("PLUNE_FRETE_POR_CONTA", "9")
PLUNE_REGIONAL_SUBCENTRO2_MAP = _env_json("PLUNE_REGIONAL_SUBCENTRO2_MAP", {})
PLUNE_PARAMETRO_CONTABIL_RECORRENTE_ID = _env(
    "PLUNE_PARAMETRO_CONTABIL_RECORRENTE_ID", "1077"
)
PLUNE_PARAMETRO_CONTABIL_IMPLANTACAO_ID = _env(
    "PLUNE_PARAMETRO_CONTABIL_IMPLANTACAO_ID", "1436"
)

# --- Automação ---
INTERVALO_POLLING_SEGUNDOS = _env_int("INTERVALO_POLLING_SEGUNDOS", 30)
MODELO_DOCX = _env_path("MODELO_DOCX", "contrato_padrao.docx")
PASTA_SAIDA = _env_path("PASTA_SAIDA", "contratos")
TESTE_PLUNE_SEM_ASSINATURA = _env_bool("TESTE_PLUNE_SEM_ASSINATURA", True)

# --- Arquivos de estado ---
ARQUIVO_DEALS_PROCESSADOS = _env_path_with_legacy(
    "ARQUIVO_DEALS_PROCESSADOS",
    "runtime/state/deals_processados.txt",
    "deals_processados.txt",
)
ARQUIVO_ENVELOPES_PENDENTES = _env_path_with_legacy(
    "ARQUIVO_ENVELOPES_PENDENTES",
    "runtime/state/envelopes_pendentes.json",
    "envelopes_pendentes.json",
)
ARQUIVO_PEDIDOS_PLUNE_CRIADOS = _env_path_with_legacy(
    "ARQUIVO_PEDIDOS_PLUNE_CRIADOS",
    "runtime/state/pedidos_plune_criados.txt",
    "pedidos_plune_criados.txt",
)
ARQUIVO_AVISOS_APROVACAO_PLUNE = _env_path(
    "ARQUIVO_AVISOS_APROVACAO_PLUNE",
    "runtime/state/avisos_aprovacao_plune.txt",
)
