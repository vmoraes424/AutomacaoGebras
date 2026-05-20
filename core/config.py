"""
Configuração central.

- Segredos e flags de ambiente: arquivo `.env` na raiz do projeto.
- Constantes de produto/URL: `core/gebras_defaults.py`.
- Filiais, branches, subcentros e estado: MySQL (`gebras_automacao`).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from . import gebras_defaults as G

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
    if raw is None or not str(raw).strip():
        return default
    return int(str(raw).strip())


def _resolve_path(relative: str) -> str:
    path = Path(relative)
    if not path.is_absolute():
        path = _ROOT / path
    return str(path)


def _cfg_filial_padrao() -> dict:
    from .database import branch_config, default_branch_id

    return branch_config(default_branch_id()) or {}


def __getattr__(name: str):
    """Valores por filial padrão vêm do banco (sem duplicar em gebras_defaults)."""
    if name == "PLUNE_BRANCH_ID":
        from .database import default_branch_id

        return default_branch_id()
    if name == "PLUNE_SUBCENTRO_CUSTO_ID":
        return _cfg_filial_padrao().get("subcentro_custo_id", "")
    if name == "PLUNE_PARAMETRO_CONTABIL_RECORRENTE_ID":
        return _cfg_filial_padrao().get("parametro_recorrente", "")
    if name == "PLUNE_PARAMETRO_CONTABIL_IMPLANTACAO_ID":
        return _cfg_filial_padrao().get("parametro_implantacao", "")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# --- MySQL (RDS) ---
MYSQL_HOST = _env("MYSQL_HOST")
MYSQL_PORT = _env_int("MYSQL_PORT", 3306)
MYSQL_USER = _env("MYSQL_USER")
MYSQL_PASSWORD = _env("MYSQL_PASSWORD")
MYSQL_DATABASE = _env("MYSQL_DATABASE", "gebras_automacao")

# --- Segredos e ambiente (.env) ---
PIPEDRIVE_API_TOKEN = _env("PIPEDRIVE_API_TOKEN")
CLICKSIGN_ACCESS_TOKEN = _env("CLICKSIGN_ACCESS_TOKEN")
CLICKSIGN_WEBHOOK_URL = _env("CLICKSIGN_WEBHOOK_URL")
PLUNE_AUTH_TOKEN = _env("PLUNE_AUTH_TOKEN")
DEV_PULAR_CLICKSIGN = _env_bool("DEV_PULAR_CLICKSIGN", False)
TESTE_PLUNE_SEM_ASSINATURA = _env_bool("TESTE_PLUNE_SEM_ASSINATURA", True)
DEV_PLUNE_APROVADO_NAO = _env_bool("DEV_PLUNE_APROVADO_NAO", False)

# --- Negócio (gebras_defaults) ---
PLUNE_BASE_URL = G.PLUNE_BASE_URL
PLUNE_COMPANY_ID = G.PLUNE_COMPANY_ID
PLUNE_TIPO_OP_ID = G.PLUNE_TIPO_OP_ID
PLUNE_STATUS_PEDIDO = G.PLUNE_STATUS_PEDIDO
PLUNE_TIPO_CONTRATO_ID = G.PLUNE_TIPO_CONTRATO_ID
PLUNE_CENTRO_CUSTO_ID = G.PLUNE_CENTRO_CUSTO_ID
PLUNE_PRODUTO_SOLE_ID = G.PLUNE_PRODUTO_SOLE_ID
PLUNE_PARCEIRO_TIPO = G.PLUNE_PARCEIRO_TIPO
PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID = G.PLUNE_STATUS_PEDIDO_IMPLANTACAO_ID
PLUNE_STATUS_PEDIDO_RECORRENTE_ID = G.PLUNE_STATUS_PEDIDO_RECORRENTE_ID
PLUNE_FRETE_POR_CONTA = G.PLUNE_FRETE_POR_CONTA

CLICKSIGN_BASE_URL = G.CLICKSIGN_BASE_URL
CLICKSIGN_RATE_LIMIT_MAX_RETRIES = G.CLICKSIGN_RATE_LIMIT_MAX_RETRIES
CLICKSIGN_RATE_LIMIT_BUFFER_SEC = G.CLICKSIGN_RATE_LIMIT_BUFFER_SEC
INTERVALO_POLLING_SEGUNDOS = G.INTERVALO_POLLING_SEGUNDOS
MODELO_DOCX = _resolve_path(G.MODELO_DOCX)
PASTA_SAIDA = _resolve_path(G.PASTA_SAIDA)
ARQUIVO_AVISOS_APROVACAO_PLUNE = _resolve_path(G.ARQUIVO_AVISOS_APROVACAO_PLUNE)
