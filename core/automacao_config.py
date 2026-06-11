"""Flags operacionais da automação — tabela `automacao_config` em MySQL (gebras_automacao)."""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any, Literal

from core.config import MYSQL_DATABASE

_CONFIG_ROW_ID = 1
_LEGACY_META_KEY = "automacao.config"
_CACHE_TTL_SEC = 5.0

_cache_lock = threading.Lock()
_cache: AutomacaoConfig | None = None
_cache_at = 0.0
_memory_store: AutomacaoConfig | None = None

_BOOL_FIELDS = (
    "dev_pular_clicksign",
    "teste_plune_sem_assinatura",
    "dev_hub_sem_aprovacao_plune",
    "pular_hub",
    "formulario_web_enabled",
)

PresetName = Literal["dev", "prod"]


@dataclass(frozen=True)
class AutomacaoConfig:
    """Defaults = produção (1ª linha criada no banco se a tabela estiver vazia)."""

    dev_pular_clicksign: bool = False
    teste_plune_sem_assinatura: bool = False
    dev_hub_sem_aprovacao_plune: bool = False
    pular_hub: bool = False
    formulario_web_enabled: bool = True
    updated_at: str | None = None

    def to_dict(self) -> dict[str, bool]:
        return {name: bool(getattr(self, name)) for name in _BOOL_FIELDS}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> AutomacaoConfig:
        base = cls()
        data = {f.name: getattr(base, f.name) for f in fields(base) if f.name != "updated_at"}
        for name in _BOOL_FIELDS:
            if name in raw:
                data[name] = bool(raw[name])
        updated_at = raw.get("updated_at")
        if updated_at is not None:
            data["updated_at"] = str(updated_at)
        return cls(**data)


# Presets usados pelo portal (/config/automacao) e pelo worker.
PROD_PRESET = AutomacaoConfig(
    dev_pular_clicksign=False,
    teste_plune_sem_assinatura=False,
    dev_hub_sem_aprovacao_plune=False,
    pular_hub=False,
    formulario_web_enabled=True,
)

DEV_PRESET = AutomacaoConfig(
    dev_pular_clicksign=True,
    teste_plune_sem_assinatura=True,
    dev_hub_sem_aprovacao_plune=True,
    pular_hub=True,
    formulario_web_enabled=True,
)

_PRESETS: dict[PresetName, AutomacaoConfig] = {
    "dev": DEV_PRESET,
    "prod": PROD_PRESET,
}


def preset_config(name: PresetName) -> AutomacaoConfig:
    return _PRESETS[name]


def apply_automacao_preset(name: PresetName) -> AutomacaoConfig:
    return save_automacao_config(preset_config(name))


def _use_memory_backend() -> bool:
    """Somente pytest/local sem MySQL; produção usa MYSQL_* do .env."""
    return os.environ.get("AUTOMACAO_CONFIG_BACKEND", "mysql").strip().lower() == "memory"


def mysql_database_name() -> str:
    return MYSQL_DATABASE or "gebras_automacao"


def invalidate_automacao_config_cache() -> None:
    global _cache, _cache_at
    with _cache_lock:
        _cache = None
        _cache_at = 0.0


def reset_automacao_config_for_tests() -> None:
    """Limpa cache e store em memória (pytest)."""
    global _memory_store
    _memory_store = None
    invalidate_automacao_config_cache()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_config(row: dict[str, Any]) -> AutomacaoConfig:
    return AutomacaoConfig(
        dev_pular_clicksign=bool(row.get("dev_pular_clicksign")),
        teste_plune_sem_assinatura=bool(row.get("teste_plune_sem_assinatura")),
        dev_hub_sem_aprovacao_plune=bool(row.get("dev_hub_sem_aprovacao_plune")),
        pular_hub=bool(row.get("pular_hub")),
        formulario_web_enabled=bool(row.get("formulario_web_enabled")),
        updated_at=str(row.get("updated_at") or "") or None,
    )


def _load_legacy_app_meta(conn) -> AutomacaoConfig | None:
    row = conn.execute(
        "SELECT value FROM app_meta WHERE `key` = %s",
        (_LEGACY_META_KEY,),
    ).fetchone()
    if not row:
        return None
    try:
        payload = json.loads(str(row["value"]))
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return AutomacaoConfig.from_dict(payload)


def _load_from_db() -> AutomacaoConfig | None:
    from core.database import db_conn

    try:
        with db_conn() as conn:
            row = conn.execute(
                """
                SELECT dev_pular_clicksign, teste_plune_sem_assinatura,
                       dev_hub_sem_aprovacao_plune, pular_hub, formulario_web_enabled,
                       updated_at
                FROM automacao_config
                WHERE id = %s
                """,
                (_CONFIG_ROW_ID,),
            ).fetchone()
            if row:
                return _row_to_config(row)
            legacy = _load_legacy_app_meta(conn)
            if legacy is not None:
                updated_at = _save_to_db(legacy, conn=conn)
                return AutomacaoConfig(**{**legacy.to_dict(), "updated_at": updated_at})
    except Exception:
        return None
    return None


def _save_to_db(config: AutomacaoConfig, *, conn=None) -> str:
    from core.database import db_conn

    updated_at = _utc_now_iso()
    params = (
        _CONFIG_ROW_ID,
        int(config.dev_pular_clicksign),
        int(config.teste_plune_sem_assinatura),
        int(config.dev_hub_sem_aprovacao_plune),
        int(config.pular_hub),
        int(config.formulario_web_enabled),
        updated_at,
    )
    sql = """
        INSERT INTO automacao_config (
            id, dev_pular_clicksign, teste_plune_sem_assinatura,
            dev_hub_sem_aprovacao_plune, pular_hub, formulario_web_enabled, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            dev_pular_clicksign = VALUES(dev_pular_clicksign),
            teste_plune_sem_assinatura = VALUES(teste_plune_sem_assinatura),
            dev_hub_sem_aprovacao_plune = VALUES(dev_hub_sem_aprovacao_plune),
            pular_hub = VALUES(pular_hub),
            formulario_web_enabled = VALUES(formulario_web_enabled),
            updated_at = VALUES(updated_at)
    """
    if conn is not None:
        conn.execute(sql, params)
    else:
        with db_conn() as owned:
            owned.execute(sql, params)
    return updated_at


def get_automacao_config(*, force_refresh: bool = False) -> AutomacaoConfig:
    global _cache, _cache_at, _memory_store
    now = time.monotonic()
    with _cache_lock:
        if not force_refresh and _cache is not None and now - _cache_at < _CACHE_TTL_SEC:
            return _cache

    if _use_memory_backend():
        cfg = _memory_store or PROD_PRESET
    else:
        cfg = _load_from_db()
        if cfg is None:
            cfg = PROD_PRESET
            try:
                updated_at = _save_to_db(cfg)
                cfg = AutomacaoConfig(**{**cfg.to_dict(), "updated_at": updated_at})
            except Exception:
                pass

    with _cache_lock:
        _cache = cfg
        _cache_at = now
    return cfg


def save_automacao_config(config: AutomacaoConfig) -> AutomacaoConfig:
    global _memory_store
    normalized = AutomacaoConfig.from_dict(config.to_dict())
    if _use_memory_backend():
        stored = AutomacaoConfig(
            **{**normalized.to_dict(), "updated_at": _utc_now_iso()}
        )
        _memory_store = stored
        normalized = stored
    else:
        updated_at = _save_to_db(normalized)
        normalized = AutomacaoConfig(**{**normalized.to_dict(), "updated_at": updated_at})
    invalidate_automacao_config_cache()
    with _cache_lock:
        global _cache, _cache_at
        _cache = normalized
        _cache_at = time.monotonic()
    return normalized
